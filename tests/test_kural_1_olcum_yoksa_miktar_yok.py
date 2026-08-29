"""KURAL 1 — Ölçüm yoksa miktar üretilmez.

Rapor 3.6: "Yeterli ölçüm bulunmayan alanlar için tonaj tahmini
oluşturulmayacaktır."
Rapor 4: miktar tek kesin değer değil, belirsizlik aralığı olarak verilir.

Bu dosyadaki testler final demosunun 6. ve 7. adımlarını korur.
"""
from __future__ import annotations

import pytest
from sqlalchemy import select, text

import api.app.db as db_modulu
from api.app.models import DogrulamaDurumu, MiktarHesabi, Olcum, Tespit
from api.app.services import miktar as miktar_servisi

pytestmark = pytest.mark.kural


async def test_olcum_yokken_api_sayi_dondurmez(istemci, jeton, tespit_kur):
    """Ölçüm yoksa hiçbir sayı alanı dolu gelmez — demo 7. adım."""
    tid = await tespit_kur(dogrulama="onaylandi")
    y = await istemci.get(f"/miktar/{tid}", headers=await jeton("belediye"))
    assert y.status_code == 200
    d = y.json()

    assert d["hesaplandi"] is False
    assert d["deger_alt"] is None
    assert d["deger_ust"] is None
    assert d["birim"] is None
    assert d["aciklama"] == "Ölçüm girilmediği için miktar hesaplanmadı"

    # Yer tutucu metin sızmamalı: "0", "≈0", "hesaplanıyor" olmamalı.
    assert "0" not in (d["aciklama"] or "")
    assert "hesaplan" in (d["aciklama"] or "").lower()


async def test_olcum_yokken_veri_tabaninda_satir_olusmaz(
    istemci, jeton, tespit_kur
):
    """Satır YOK — 0 da değil, NULL da değil."""
    tid = await tespit_kur(dogrulama="onaylandi")
    await istemci.get(f"/miktar/{tid}", headers=await jeton("belediye"))

    async with db_modulu.OturumUret() as db:
        satir = await db.scalar(
            select(MiktarHesabi).where(MiktarHesabi.tespit_id == tid)
        )
    assert satir is None, "Ölçüm yokken miktar_hesabi satırı oluşturulmamalı"


async def test_agirlik_olcumu_araligi_uretir(istemci, jeton, tespit_kur):
    """Ölçüm girilince miktar ARALIK olarak gelir — demo 6. adım."""
    tid = await tespit_kur(dogrulama="onaylandi")
    e = await istemci.post("/olcum", headers=await jeton("saha"), json={
        "tespit_id": tid, "tur": "agirlik", "deger": 12.4,
        "birim": "ton", "yontem": "Saha kantar ölçümü",
    })
    assert e.status_code == 201, e.text

    d = (await istemci.get(f"/miktar/{tid}", headers=await jeton("belediye"))).json()
    assert d["hesaplandi"] is True
    assert d["deger_alt"] < d["deger_ust"], "Tek kesin değer üretilmemeli"
    assert d["birim"] == "ton"
    assert d["yontem"], "Kullanılan yöntem her zaman belirtilmeli"
    assert d["katsayi_kaynagi"], "Katsayı kaynağı her zaman belirtilmeli"


async def test_tek_degerli_miktar_veri_tabaninca_reddedilir():
    """CHECK kısıtı: alt = üst yazılamaz.

    Belirsizlik aralığı taahhüdü şema seviyesinde zorlanır; bir hata
    uygulama katmanını atlarsa veri tabanı yakalar.
    """
    async with db_modulu.OturumUret() as db:
        with pytest.raises(Exception) as h:
            await db.execute(text("""
                INSERT INTO miktar_hesabi
                  (tespit_id, deger_alt, deger_ust, birim,
                   kullanilan_katsayi, katsayi_kaynagi, yontem)
                VALUES (1, 12.5, 12.5, 'ton', 1, 'k', 'y')
            """))
            await db.commit()
    assert "ck_miktar_araliksiz_degil" in str(h.value)


async def test_yalnizca_alan_olcumu_miktar_uretmez(istemci, jeton, tespit_kur):
    """Derinlik bilinmeden alan ölçümü hacme çevrilemez."""
    tid = await tespit_kur(dogrulama="onaylandi")
    await istemci.post("/olcum", headers=await jeton("saha"), json={
        "tespit_id": tid, "tur": "alan", "deger": 40.0,
        "birim": "m2", "yontem": "Şerit metre",
    })
    d = (await istemci.get(f"/miktar/{tid}", headers=await jeton("belediye"))).json()
    assert d["hesaplandi"] is False
    assert d["deger_alt"] is None
    assert "derinlik" in d["aciklama"].lower()


async def test_dogrulanmamis_katsayiyla_miktar_uretilmez(
    istemci, jeton, tespit_kur
):
    """Bölüm 14: dayanağı doğrulanmamış katsayıyla sayı üretilmez."""
    tid = await tespit_kur("beton", dogrulama="onaylandi")
    await istemci.post("/olcum", headers=await jeton("saha"), json={
        "tespit_id": tid, "tur": "hacim", "deger": 30.0,
        "birim": "m3", "yontem": "Saha tahmini",
    })
    d = (await istemci.get(f"/miktar/{tid}", headers=await jeton("belediye"))).json()

    # katsayilar.json'daki tüm katsayılar şu an dogrulandi:false
    assert d["hesaplandi"] is False
    assert d["deger_alt"] is None
    assert "katsayı" in d["aciklama"].lower()


async def test_malzeme_olmayan_sinif_miktara_girmez(istemci, jeton, tespit_kur):
    """K-007: konteyner bir atık malzeme değildir."""
    tid = await tespit_kur("konteyner", dogrulama="onaylandi")
    await istemci.post("/olcum", headers=await jeton("saha"), json={
        "tespit_id": tid, "tur": "agirlik", "deger": 500.0,
        "birim": "ton", "yontem": "Kantar",
    })
    d = (await istemci.get(f"/miktar/{tid}", headers=await jeton("belediye"))).json()
    assert d["hesaplandi"] is False
    assert "malzeme değildir" in d["aciklama"]


def test_servis_katmani_olcumsuz_hesap_yapmaz():
    """Servis katmanı doğrudan sınanır — HTTP olmadan."""
    t = Tespit(sinif="beton", dogrulama_durumu=DogrulamaDurumu.ONAYLANDI)
    s = miktar_servisi.hesapla(t, [])
    assert s.hesaplandi is False
    assert s.neden == miktar_servisi.OLCUM_YOK
    assert s.deger_alt is None and s.deger_ust is None


async def test_dogrulanmamis_tespit_miktara_girmez(istemci, jeton, tespit_kur):
    """Bölüm 1.4 — doğrulanmamış kayıt miktar hesabına GİRMEZ.

    "Bu bir arayüz kuralı değil, veri katmanı kuralıdır." Ölçüm girilmiş
    olsa bile, uzman onayı yoksa sayı üretilmez ve satır yazılmaz.
    """
    tid = await tespit_kur()  # varsayılan: beklemede
    e = await istemci.post("/olcum", headers=await jeton("saha"), json={
        "tespit_id": tid, "tur": "agirlik", "deger": 12.4,
        "birim": "ton", "yontem": "Saha kantar ölçümü",
    })
    assert e.status_code == 201, e.text

    d = (await istemci.get(f"/miktar/{tid}", headers=await jeton("belediye"))).json()
    assert d["hesaplandi"] is False
    assert d["deger_alt"] is None and d["deger_ust"] is None
    assert "doğrulanmadığı" in d["aciklama"]

    async with db_modulu.OturumUret() as db:
        satir = await db.scalar(
            select(MiktarHesabi).where(MiktarHesabi.tespit_id == tid)
        )
    assert satir is None, "Doğrulanmamış tespit için miktar satırı yazılmamalı"


async def test_belirsiz_isaretlenen_tespit_de_miktara_girmez(
    istemci, jeton, tespit_kur
):
    """`belirsiz`, uzmanın karar veremediği kayıttır — onay değildir."""
    tid = await tespit_kur(dogrulama="belirsiz")
    await istemci.post("/olcum", headers=await jeton("saha"), json={
        "tespit_id": tid, "tur": "agirlik", "deger": 12.4,
        "birim": "ton", "yontem": "Saha kantar ölçümü",
    })
    d = (await istemci.get(f"/miktar/{tid}", headers=await jeton("belediye"))).json()
    assert d["hesaplandi"] is False


async def test_sacma_yuksek_olcum_reddedilir(istemci, jeton, tespit_kur):
    """Tek tespit için 10⁹ ton kabul edilmez — yazım hatası kalkanı.

    Sessizce kırpılmaz, istek reddedilir: kullanıcının girdiği sayıyı
    değiştirip kaydetmek ölçümü uydurmak olurdu.
    """
    tid = await tespit_kur(dogrulama="onaylandi")
    y = await istemci.post("/olcum", headers=await jeton("saha"), json={
        "tespit_id": tid, "tur": "agirlik", "deger": 1_000_000_000,
        "birim": "ton", "yontem": "Kantar",
    })
    assert y.status_code == 422


async def test_olcum_birimi_turune_uymazsa_reddedilir(
    istemci, jeton, tespit_kur
):
    """Ağırlık ölçümü m³ birimiyle gelemez.

    Kabul edilseydi hacim değeri ağırlık sanılıp katsayısız hesaba girerdi.
    """
    tid = await tespit_kur(dogrulama="onaylandi")
    y = await istemci.post("/olcum", headers=await jeton("saha"), json={
        "tespit_id": tid, "tur": "agirlik", "deger": 12.4,
        "birim": "m3", "yontem": "Kantar",
    })
    assert y.status_code == 422
