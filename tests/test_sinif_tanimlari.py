"""Sınıf tanımları — siniflar.json tek doğruluk kaynağıdır."""
from __future__ import annotations

import json
from pathlib import Path

from api.app.core.config import malzeme_siniflari, siniflar

DEPO_KOKU = Path(__file__).resolve().parents[1]


def test_siniflar_json_ile_belge_ayni_sayida():
    d = siniflar()
    assert len(d["siniflar"]) == 10


def test_konteyner_malzeme_degil():
    """K-007: hurda konteyneri atık malzeme değildir."""
    d = {s["ad"]: s for s in siniflar()["siniflar"]}
    assert d["konteyner"]["malzeme_mi"] is False
    assert "konteyner" not in malzeme_siniflari()
    assert len(malzeme_siniflari()) == 9


def test_kapsanmayan_gruplar_beyan_edilmis():
    """Cam ve seramik eğitim verisinde yok — gizlenmiyor."""
    adlar = {g["ad"] for g in siniflar()["kapsanmayan_gruplar"]}
    assert "cam" in adlar
    assert "seramik" in adlar
    for g in siniflar()["kapsanmayan_gruplar"]:
        assert g["not"], f"{g['ad']} için gerekçe yazılmalı"


def test_sinif_adlari_benzersiz_ve_kimlikler_sirali():
    s = siniflar()["siniflar"]
    assert len({x["ad"] for x in s}) == len(s)
    assert [x["id"] for x in s] == list(range(len(s)))


def test_her_sinifin_rengi_var():
    """Renk tek başına anlam taşımaz ama her sınıfın bir rengi olmalı."""
    for s in siniflar()["siniflar"]:
        assert s["renk"].startswith("#") and len(s["renk"]) == 7
        assert s["gorunen_ad"]


def test_katsayilar_dogrulanmamis_olarak_isaretli():
    """Bölüm 14: kaynak girilmeden katsayı kullanılmaz."""
    k = json.loads((DEPO_KOKU / "katsayilar.json").read_text(encoding="utf-8"))
    for x in k["katsayilar"]:
        if x["dogrulandi"]:
            assert x["kaynak"], f"{x['sinif']} doğrulandı ama kaynağı yok"
            assert x["alt"] is not None and x["ust"] is not None
            assert x["alt"] < x["ust"], "Katsayı da aralık olmalı"


def test_katsayi_tablosunda_malzeme_olmayan_sinif_yok():
    k = json.loads((DEPO_KOKU / "katsayilar.json").read_text(encoding="utf-8"))
    adlar = {x["sinif"] for x in k["katsayilar"]}
    assert "konteyner" not in adlar
    assert adlar == set(malzeme_siniflari())


# --- Eğitim veri setinin sınıf sırası (Madde 10.5) -------------------------

DATA_YAML = DEPO_KOKU / "model-service/data.yaml"


def _data_yaml_siniflari() -> list[str]:
    """`model-service/data.yaml` içindeki `names` listesini SIRASIYLA verir.

    PyYAML bilinçli olarak kullanılmıyor: sunucu bağımlılıklarında yok ve
    yalnız bu test için eklenmesi gerekirdi. `pytest.importorskip` ile
    geçmek ise daha kötü olurdu — koruma CI'da sessizce kapanırdı, ki bu
    testin varlık sebebi tam da o sessizliği önlemek. Ultralytics
    data.yaml'ı düz bir biçim; `names` satırı tek başına okunabilir.
    """
    satirlar = DATA_YAML.read_text(encoding="utf-8").splitlines()
    for i, satir in enumerate(satirlar):
        if not satir.startswith("names:"):
            continue

        # Tek satır biçimi:  names: ['ahsap', 'metal']
        kuyruk = satir.split(":", 1)[1].strip()
        if kuyruk.startswith("["):
            icerik = kuyruk.strip("[]")
            return [ad.strip().strip("'\"") for ad in icerik.split(",") if ad.strip()]

        # Blok biçimi:  "  - ahsap"  ya da  "  0: ahsap"
        adlar = []
        for alt in satirlar[i + 1:]:
            if alt.strip() and not alt.startswith((" ", "\t", "-")):
                break
            girdi = alt.strip()
            if not girdi:
                continue
            if girdi.startswith("-"):
                adlar.append(girdi.lstrip("- ").strip("'\""))
            elif ":" in girdi:
                adlar.append(girdi.split(":", 1)[1].strip().strip("'\""))
        return adlar

    raise AssertionError(f"{DATA_YAML} içinde `names` alanı yok")


def test_data_yaml_depoda_duruyor():
    """Madde 10.5: eğitim veri kaynağı beyanının kanıtı depoda olmalı."""
    assert DATA_YAML.exists(), (
        "model-service/data.yaml eksik. Ağırlık büyük olduğu için depoya "
        "girmez ama sınıf sırası girer: modelin ne öğrendiğini gösteren "
        "tek küçük kanıt budur."
    )


def test_data_yaml_sinif_sayisi_siniflar_json_ile_ayni():
    assert len(_data_yaml_siniflari()) == len(siniflar()["siniflar"])


def test_data_yaml_sinif_sirasi_siniflar_json_ile_ayni():
    """Eğitimdeki sıra kayarsa arayüz YANLIŞ MALZEME gösterir.

    `model-service/app.py` sınıf adını modelden değil siniflar.json'dan
    alır (`_sinif_adi`). Oradaki koruma yalnız BİLİNMEYEN id'yi yakalar:
    model 0-9 arası geçerli bir id döndürdüğü sürece istisna atılmaz ve
    tespit sessizce yanlış etiketlenir — "cam" olan kutu "ahsap" diye
    kaydedilir, oradan miktar hesabına ve rapora geçer.

    Bu testin işi o sessizliği bozmaktır.
    """
    beklenen = [s["ad"] for s in siniflar()["siniflar"]]
    gercek = _data_yaml_siniflari()
    assert gercek == beklenen, (
        "Eğitim veri setinin sınıf sırası siniflar.json ile uyuşmuyor.\n"
        f"  data.yaml     : {gercek}\n"
        f"  siniflar.json : {beklenen}\n"
        "Ya model bu sıraya göre yeniden eğitilmeli ya da siniflar.json "
        "(ve ona bağlı katsayilar.json, docs/siniflar.md, arayüz) "
        "eğitilen sıraya göre güncellenmeli. İkisi ayrı kaldığı sürece "
        "servis her tespiti yanlış adla döndürür."
    )
