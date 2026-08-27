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
