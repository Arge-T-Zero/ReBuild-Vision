"""Çevrimdışı eşitleme — mobil kuyruğun sunucu tarafı.

Rapor Bölüm 12: "Mobil kayıtların cihazda şifreli olarak geçici biçimde
saklanması ve bağlantı sağlandığında eşitlenmesi."
"""
from __future__ import annotations

import pytest

from api.app.core.config import ayarlar  # noqa: F401


async def test_kuyruk_toplu_yazilir(istemci, jeton, tespit_kur):
    tid = await tespit_kur()
    y = await istemci.post("/esitleme/olcum", headers=await jeton("saha"), json={
        "kayitlar": [
            {"yerel_kimlik": "cihaz-a-0001", "tespit_id": tid, "tur": "agirlik",
             "deger": 3.5, "birim": "ton", "yontem": "Saha kantarı"},
            {"yerel_kimlik": "cihaz-a-0002", "tespit_id": tid, "tur": "hacim",
             "deger": 12.0, "birim": "m3", "yontem": "Şerit metre"},
        ],
    })
    assert y.status_code == 200
    d = y.json()
    assert d["yazilan"] == 2 and d["yinelenen"] == 0 and d["hatali"] == 0

    olcumler = (await istemci.get(f"/olcum/tespit/{tid}",
                                  headers=await jeton("saha"))).json()
    assert len(olcumler) == 2


async def test_ayni_kayit_iki_kez_yazilmaz(istemci, jeton, tespit_kur):
    """Ağ koptuğunda istemci isteği tekrarlar ama sonucu bilemez.

    Bu koruma olmadan tek bir zayıf bağlantı ölçümleri ikiye katlardı ve
    miktar hesabı bozulurdu.
    """
    tid = await tespit_kur()
    govde = {"kayitlar": [
        {"yerel_kimlik": "cihaz-b-0001", "tespit_id": tid, "tur": "agirlik",
         "deger": 4.0, "birim": "ton", "yontem": "Kantar"},
    ]}
    baslik = await jeton("saha")

    ilk = (await istemci.post("/esitleme/olcum", headers=baslik, json=govde)).json()
    assert ilk["yazilan"] == 1

    # İstemci aynı isteği tekrarlıyor
    ikinci = (await istemci.post("/esitleme/olcum", headers=baslik, json=govde)).json()
    assert ikinci["yazilan"] == 0
    assert ikinci["yinelenen"] == 1

    olcumler = (await istemci.get(f"/olcum/tespit/{tid}", headers=baslik)).json()
    assert len(olcumler) == 1, "Ölçüm iki kez yazılmamalı"


async def test_kismi_basari_digerlerini_engellemez(istemci, jeton, tespit_kur):
    """Bir satır hatalıysa diğerleri yine de yazılır.

    Tümünü reddetmek, saha personelini bağlantısı olmayan bir yerde
    çözemeyeceği bir hatayla baş başa bırakırdı.
    """
    tid = await tespit_kur()
    d = (await istemci.post("/esitleme/olcum", headers=await jeton("saha"), json={
        "kayitlar": [
            {"yerel_kimlik": "cihaz-c-0001", "tespit_id": tid, "tur": "agirlik",
             "deger": 2.0, "birim": "ton", "yontem": "Kantar"},
            {"yerel_kimlik": "cihaz-c-0002", "tespit_id": 999999, "tur": "agirlik",
             "deger": 2.0, "birim": "ton", "yontem": "Kantar"},
            {"yerel_kimlik": "cihaz-c-0003", "tespit_id": tid, "tur": "hacim",
             "deger": 8.0, "birim": "m3", "yontem": "Metre"},
        ],
    })).json()

    assert d["yazilan"] == 2
    assert d["hatali"] == 1
    hatali = [s for s in d["satirlar"] if s["durum"] == "hata"]
    assert hatali[0]["yerel_kimlik"] == "cihaz-c-0002"
    assert "bulunamadı" in hatali[0]["aciklama"]


async def test_esitleme_de_yetki_ister(istemci, jeton, tespit_kur):
    """Toplu giriş, tekil girişin yetki kontrolünü atlamaz."""
    tid = await tespit_kur()
    govde = {"kayitlar": [
        {"yerel_kimlik": "cihaz-d-0001", "tespit_id": tid, "tur": "agirlik",
         "deger": 1.0, "birim": "ton", "yontem": "x"},
    ]}
    for rol in ("yikim", "tesis", "belediye", "afad"):
        y = await istemci.post("/esitleme/olcum", headers=await jeton(rol), json=govde)
        assert y.status_code == 403, f"{rol} ölçüm eşitleyememeli"


async def test_esitleme_dogrulamayi_atlamaz(istemci, jeton, tespit_kur):
    """Sıfır ya da negatif ölçüm toplu girişte de reddedilir."""
    tid = await tespit_kur()
    y = await istemci.post("/esitleme/olcum", headers=await jeton("saha"), json={
        "kayitlar": [
            {"yerel_kimlik": "cihaz-e-0001", "tespit_id": tid, "tur": "agirlik",
             "deger": 0, "birim": "ton", "yontem": "x"},
        ],
    })
    assert y.status_code == 422


async def test_esitlenen_olcum_miktar_hesabina_girer(istemci, jeton, tespit_kur):
    """Çevrimdışı gelen ölçüm de miktarı açar — Bölüm 1.1 aynen işler."""
    tid = await tespit_kur()
    d = (await istemci.get(f"/miktar/{tid}", headers=await jeton("saha"))).json()
    assert d["hesaplandi"] is False

    await istemci.post("/esitleme/olcum", headers=await jeton("saha"), json={
        "kayitlar": [
            {"yerel_kimlik": "cihaz-f-0001", "tespit_id": tid, "tur": "agirlik",
             "deger": 9.0, "birim": "ton", "yontem": "Saha kantarı"},
        ],
    })

    d = (await istemci.get(f"/miktar/{tid}", headers=await jeton("saha"))).json()
    assert d["hesaplandi"] is True
    assert d["deger_alt"] < d["deger_ust"], "Tek kesin değer değil, aralık"


async def test_esitleme_islem_gecmisine_duser(istemci, jeton, tespit_kur):
    tid = await tespit_kur()
    baslik = await jeton("saha")
    await istemci.post("/esitleme/olcum", headers=baslik, json={
        "kayitlar": [
            {"yerel_kimlik": "cihaz-g-0001", "tespit_id": tid, "tur": "agirlik",
             "deger": 5.0, "birim": "ton", "yontem": "Kantar"},
        ],
    })
    g = (await istemci.get("/gecmis?kayit_tipi=olcum", headers=baslik)).json()
    assert len(g) == 1
    assert g[0]["kayit_id"] is not None
