"""AGPL-3.0 sınırı — api/ hiçbir zaman ultralytics'e bağlanmaz.

docs/lisans-analizi.md Bölüm 3.4:
Model çıkarımı ayrı bir süreçte çalışır; `api/` onu yalnızca HTTP ile
çağırır. Bu sınır bir yorum satırıyla değil, testle korunur — aksi halde
bir sonraki "hızlı çözüm" sırasında sessizce kaybolabilir.
"""
from __future__ import annotations

import re
from pathlib import Path

DEPO_KOKU = Path(__file__).resolve().parents[1]

# AGPL-3.0 veya benzeri güçlü kopyaleft taşıyan, api/ içine girmemesi
# gereken paketler.
YASAKLI_PAKETLER = ("ultralytics", "yolov5", "yolov8")


def _yorumsuz_satirlar(yol: Path) -> list[str]:
    return [
        s.strip() for s in yol.read_text(encoding="utf-8").splitlines()
        if s.strip() and not s.strip().startswith("#")
    ]


def test_api_bagimliliklarinda_agpl_paketi_yok():
    """requirements.txt'te yorum dışında yasaklı paket bulunmamalı."""
    satirlar = _yorumsuz_satirlar(DEPO_KOKU / "api/requirements.txt")
    for satir in satirlar:
        ad = re.split(r"[=<>\[;]", satir)[0].strip().lower()
        assert ad not in YASAKLI_PAKETLER, (
            f"api/requirements.txt içinde '{ad}' var. Model kütüphanesi "
            f"api/'ye BAĞLANAMAZ — ayrı serviste çalışmalıdır. "
            f"Bkz. docs/lisans-analizi.md Bölüm 3.4"
        )


def test_api_kodunda_model_kutuphanesi_import_edilmiyor():
    """api/ altındaki hiçbir dosya yasaklı paketi import etmemeli."""
    ihlaller: list[str] = []
    for dosya in (DEPO_KOKU / "api/app").rglob("*.py"):
        icerik = dosya.read_text(encoding="utf-8")
        for paket in YASAKLI_PAKETLER:
            desen = rf"^\s*(import\s+{paket}|from\s+{paket}[\s.])"
            if re.search(desen, icerik, re.MULTILINE):
                ihlaller.append(f"{dosya.relative_to(DEPO_KOKU)} -> {paket}")
    assert not ihlaller, (
        "Model kütüphanesi api/ içinde import edilmiş: " + ", ".join(ihlaller)
    )


def test_model_erisimi_tek_dosyadan_gecer():
    """Model servisiyle HTTP teması yalnızca model_client.py üzerinden.

    `core/config.py` ayarı yalnızca TANIMLAR (Pydantic alanı); model
    servisine erişmez. Sınırın anlamı "adresi kullanan tek yer" olmasıdır,
    "adı hiçbir yerde geçmesin" değil.
    """
    izinli = {
        DEPO_KOKU / "api/app/services/model_client.py",
        DEPO_KOKU / "api/app/core/config.py",  # ayarın tanım yeri
    }

    ihlaller: list[str] = []
    for dosya in (DEPO_KOKU / "api/app").rglob("*.py"):
        if dosya in izinli:
            continue
        icerik = dosya.read_text(encoding="utf-8")
        if "model_service_url" in icerik.lower():
            ihlaller.append(str(dosya.relative_to(DEPO_KOKU)))
    assert not ihlaller, (
        "Model servisinin adresi yalnızca model_client.py içinde "
        "kullanılmalı; şu dosyalarda da geçiyor: " + ", ".join(ihlaller)
    )


def test_model_istemcisi_disinda_httpx_kullanilmiyor():
    """Model servisine ikinci bir HTTP yolu açılmamalı."""
    izinli = DEPO_KOKU / "api/app/services/model_client.py"
    ihlaller: list[str] = []
    for dosya in (DEPO_KOKU / "api/app").rglob("*.py"):
        if dosya == izinli:
            continue
        icerik = dosya.read_text(encoding="utf-8")
        if re.search(r"^\s*import httpx|^\s*from httpx", icerik, re.MULTILINE):
            ihlaller.append(str(dosya.relative_to(DEPO_KOKU)))
    assert not ihlaller, (
        "httpx yalnızca model_client.py içinde kullanılmalı: "
        + ", ".join(ihlaller)
    )


def test_docker_imajinda_model_kutuphanesi_yok():
    """API imajı model kütüphanesini kurmamalı."""
    icerik = (DEPO_KOKU / "docker/api.Dockerfile").read_text(encoding="utf-8")
    kod_satirlari = [
        s for s in icerik.splitlines() if not s.strip().startswith("#")
    ]
    for paket in YASAKLI_PAKETLER:
        assert not any(paket in s for s in kod_satirlari), (
            f"docker/api.Dockerfile içinde '{paket}' geçiyor"
        )
