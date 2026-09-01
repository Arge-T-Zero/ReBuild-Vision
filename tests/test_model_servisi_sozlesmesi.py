"""Sahte ve gerçek model servisleri AYNI sözleşmeyi konuşmalıdır.

`api/` iki servisi ayırt etmez; aralarındaki geçiş tek bir ortam
değişkenidir (`MODEL_SERVICE_URL`). Alan adları ayrışırsa arayüz
SESSİZCE bozulur: `detections` yerine `tespitler` dönen bir servis
hiçbir hata vermeden boş kutu listesi üretir.

Bu test, gerçek servis ağırlıksız çalıştırılabildiği için ağırlık
gerektirmez — sözleşmenin biçimini denetler, çıkarımın kendisini değil.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

DEPO_KOKU = Path(__file__).resolve().parents[1]


def _uygulama_yukle(ad: str, yol: Path):
    """Aynı adı taşıyan iki `app.py` dosyasını ayrı modül olarak yükler."""
    spec = importlib.util.spec_from_file_location(ad, yol)
    assert spec and spec.loader
    modul = importlib.util.module_from_spec(spec)
    sys.modules[ad] = modul
    spec.loader.exec_module(modul)
    return modul.app


@pytest.fixture(scope="module")
def sahte() -> TestClient:
    return TestClient(_uygulama_yukle(
        "model_mock_app", DEPO_KOKU / "model-mock/app.py"))


@pytest.fixture(scope="module")
def gercek() -> TestClient:
    return TestClient(_uygulama_yukle(
        "model_service_app", DEPO_KOKU / "model-service/app.py"))


# `api/app/services/model_client.py` ve arayüzün okuduğu alanlar.
SAGLIK_ALANLARI = {"durum", "sahte", "model", "model_license", "sinif_sayisi"}
TAHMIN_ALANLARI = {
    "sahte", "image_id", "image_width", "image_height", "processed_at",
    "model", "model_license", "review_threshold", "detections",
}


def test_saglik_ayni_alanlari_doner(sahte, gercek):
    s = sahte.get("/health").json()
    g = gercek.get("/health").json()
    assert SAGLIK_ALANLARI <= s.keys(), f"sahte serviste eksik: {SAGLIK_ALANLARI - s.keys()}"
    assert SAGLIK_ALANLARI <= g.keys(), f"gerçek serviste eksik: {SAGLIK_ALANLARI - g.keys()}"


def test_sahte_bayragi_dogru(sahte, gercek):
    """Arayüzdeki 'SAHTE MODEL SERVİSİ' rozeti bu alana bakar."""
    assert sahte.get("/health").json()["sahte"] is True
    assert gercek.get("/health").json()["sahte"] is False, (
        "Gerçek servis kendini sahte ilan ederse rozet yanlış çıkar; "
        "tersi çok daha kötü — sahtelik gizlenmiş olur."
    )


def test_siniflar_uc_noktasi_ayni_veriyi_doner(sahte, gercek):
    assert sahte.get("/siniflar").json() == gercek.get("/siniflar").json()


def test_agirliksiz_gercek_servis_sahte_veri_URETMEZ(gercek):
    """Ağırlık yokken 503 döner; uydurma tespit listesi DÖNMEZ.

    Sessizce boş liste dönmek de kabul edilemez: çağıran taraf bunu
    "görüntüde malzeme yok" diye okur.
    """
    y = gercek.get("/health").json()
    if y["agirlik_yuklendi"]:
        pytest.skip("Ağırlık yüklü — bu test ağırlıksız durumu sınar")

    yanit = gercek.post(
        "/predict", files={"file": ("a.jpg", b"sahte-icerik", "image/jpeg")})
    assert yanit.status_code == 503, (
        f"Ağırlık yokken {yanit.status_code} döndü. Çıkarım yapılamıyorsa "
        f"bu açıkça söylenmeli; boş ya da uydurma sonuç dönülmemeli."
    )


def test_gercek_servis_agpl_beyanini_gizlemez(gercek):
    lisans = gercek.get("/health").json()["model_license"]
    assert "AGPL" in lisans.upper(), (
        "Ultralytics AGPL-3.0'dır ve bu beyan gizlenemez "
        "(docs/lisans-analizi.md Bölüm 3)."
    )


def test_sahte_servis_tahmin_sozlesmesi(sahte):
    """Sahte servis üzerinden tahmin gövdesinin biçimi sabitlenir."""
    from PIL import Image
    import io as _io

    tampon = _io.BytesIO()
    Image.new("RGB", (640, 480), (128, 128, 128)).save(tampon, format="JPEG")
    y = sahte.post(
        "/predict",
        files={"file": ("t.jpg", tampon.getvalue(), "image/jpeg")},
    ).json()

    assert TAHMIN_ALANLARI <= y.keys(), f"eksik: {TAHMIN_ALANLARI - y.keys()}"
    assert y["detections"], "sahte servis en az bir tespit üretmeli"
    for t in y["detections"]:
        assert {"class_id", "class_name", "confidence", "bbox",
                "bbox_format", "needs_review"} <= t.keys()
        assert {"x", "y", "w", "h"} == t["bbox"].keys()
        # Arayüz YALNIZCA bu biçimi çizer; başkası sessizce atlanır
        # (web/src/bilesenler/TespitKutulari.tsx).
        assert t["bbox_format"] == "pixel_absolute_original"


def test_bilinmeyen_sinif_idsi_sessizce_gecilmez():
    """Eğitimdeki sınıf sırası kayarsa istek REDDEDİLİR.

    Bu, bu projedeki en sinsi hata türüdür: model 80 sınıflı bir ağırlıkla
    (ya da sırası kaymış bir `data.yaml` ile) çalıştırılırsa arayüz
    "ahşap" yerine "metal" gösterir ve hiçbir yerde hata görünmez.
    Miktar hesabı da yanlış malzemenin katsayısıyla yapılır.
    """
    import importlib.util
    from fastapi import HTTPException

    spec = importlib.util.spec_from_file_location(
        "model_service_guard", DEPO_KOKU / "model-service/app.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)

    # siniflar.json 0-9 tanımlıyor; 42 COCO ağırlığından gelebilecek bir id.
    with pytest.raises(HTTPException) as h:
        modul._sinif_adi(42)
    assert h.value.status_code == 500
    assert "siniflar.json" in h.value.detail
    assert "data.yaml" in h.value.detail, (
        "Hata mesajı sorunun NEREDE çözüleceğini söylemeli")

    # Geçerli id'ler sorunsuz çevrilmeli.
    assert modul._sinif_adi(0) == "beton"
    assert modul._sinif_adi(9) == "konteyner"


def test_iki_servis_ayni_esik_alanini_kullanir(sahte, gercek):
    """`review_threshold` adı ayrışırsa inceleme kuyruğu bozulur."""
    from PIL import Image
    import io as _io

    tampon = _io.BytesIO()
    Image.new("RGB", (320, 240), (10, 10, 10)).save(tampon, format="JPEG")
    s = sahte.post(
        "/predict", files={"file": ("t.jpg", tampon.getvalue(), "image/jpeg")},
    ).json()
    assert isinstance(s["review_threshold"], (int, float))
    assert isinstance(gercek.get("/health").json()["review_threshold"], (int, float))
