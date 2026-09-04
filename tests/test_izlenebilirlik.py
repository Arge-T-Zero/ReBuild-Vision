"""İzlenebilirlik — işlem geçmişi otomatik ve eksiksiz.

Rapor Bölüm 6 (dördüncü yenilikçi yön): "Her kayıt için oluşturan kullanıcı,
tarih, doğrulama durumu ve değişiklik geçmişi saklanarak izlenebilirlik
sağlanacaktır."

Kayıtlar elle yazılmaz; olay dinleyicisi yazar. Bu testler dinleyicinin
sessizce devre dışı kalmasını engeller.
"""
from __future__ import annotations

from sqlalchemy import select

import api.app.db as db_modulu
from api.app.models import IslemGecmisi


async def _gecmis(istemci, baslik, **p):
    q = "&".join(f"{a}={b}" for a, b in p.items())
    y = await istemci.get(f"/gecmis?{q}", headers=baslik)
    assert y.status_code == 200
    return y.json()


async def test_alan_olusturma_gecmise_dusuyor(istemci, jeton):
    b = await jeton("belediye")
    await istemci.post("/enkaz-alani", headers=b,
                       json={"ad": "Kayıtlı alan", "erisim_durumu": "acik"})

    kayitlar = await _gecmis(istemci, b, kayit_tipi="enkaz_alani")
    assert len(kayitlar) == 1
    k = kayitlar[0]
    assert k["islem"] == "olusturma"
    assert k["yeni_deger"]["ad"] == "Kayıtlı alan"


async def test_olusturma_kaydinda_kayit_id_dolu(istemci, jeton):
    """before_flush kullanılsaydı id atanmamış olurdu — regresyon testi."""
    b = await jeton("belediye")
    y = await istemci.post("/enkaz-alani", headers=b,
                           json={"ad": "Kimlikli alan", "erisim_durumu": "acik"})
    alan_id = y.json()["id"]

    kayitlar = await _gecmis(istemci, b, kayit_tipi="enkaz_alani")
    assert kayitlar[0]["kayit_id"] == alan_id, (
        "Oluşturma kaydı ilgili satıra bağlanamıyor"
    )


async def test_dogrulama_eski_ve_yeni_degeri_saklar(istemci, jeton, tespit_kur):
    tid = await tespit_kur("ahsap")
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "duzeltildi", "duzeltilen_sinif": "tugla"})

    kayitlar = await _gecmis(istemci, await jeton("uzman"),
                             kayit_tipi="tespit", kayit_id=tid)
    guncelleme = next(k for k in kayitlar if k["islem"] == "guncelleme")

    assert guncelleme["eski_deger"]["dogrulama_durumu"] == "beklemede"
    assert guncelleme["yeni_deger"]["dogrulama_durumu"] == "duzeltildi"
    assert guncelleme["yeni_deger"]["duzeltilen_sinif"] == "tugla"


async def test_gecmis_kimin_yaptigini_kaydeder(istemci, jeton, kullanicilar,
                                               tespit_kur):
    tid = await tespit_kur()
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})

    kayitlar = await _gecmis(istemci, await jeton("uzman"),
                             kayit_tipi="tespit", kayit_id=tid)
    guncelleme = next(k for k in kayitlar if k["islem"] == "guncelleme")
    assert guncelleme["kullanici_id"] == kullanicilar["uzman"]


async def test_parola_ozeti_gecmise_yazilmaz(istemci, jeton):
    """Gizli alanlar denetim kaydına sızmamalı."""
    await istemci.post("/auth/kayit", json={
        "eposta": "gizli@test.local", "parola": "parola12345", "ad": "Gizli",
    })
    async with db_modulu.OturumUret() as db:
        y = await db.execute(select(IslemGecmisi))
        for k in y.scalars():
            assert "sifre_hash" not in (k.yeni_deger or {})
            assert "sifre_hash" not in (k.eski_deger or {})


async def test_olcum_girisi_gecmise_dusuyor(istemci, jeton, tespit_kur):
    tid = await tespit_kur()
    await istemci.post("/olcum", headers=await jeton("saha"), json={
        "tespit_id": tid, "tur": "agirlik", "deger": 3.2,
        "birim": "ton", "yontem": "Kantar",
    })
    # Sistem geneli dökümü GECMIS_GORUR rolleri okur; burada sınanan
    # ölçümün geçmişe DÜŞMESİ, saha personelinin okuma yetkisi değil.
    kayitlar = await _gecmis(istemci, await jeton("uzman"), kayit_tipi="olcum")
    assert len(kayitlar) == 1
    assert kayitlar[0]["yeni_deger"]["yontem"] == "Kantar"


async def test_gecmis_tablosu_kendini_kaydetmez(istemci, jeton):
    """Sonsuz döngü olmamalı."""
    await istemci.post("/enkaz-alani", headers=await jeton("belediye"),
                       json={"ad": "x", "erisim_durumu": "acik"})
    kayitlar = await _gecmis(istemci, await jeton("belediye"),
                             kayit_tipi="islem_gecmisi")
    assert kayitlar == []
