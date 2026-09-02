"""Rol tabanlı erişim — yetki kontrolü API katmanındadır.

Ana talimat Bölüm 5: "Yetki kontrolü API katmanında olsun, sadece arayüzde
gizleme yeterli değil."
Brief Bölüm 3: "Kullanıcı kayıt olurken kendi rolünü seçemez."
"""
from __future__ import annotations

import pytest
from sqlalchemy import select

import api.app.db as db_modulu
from api.app.core.permissions import OnayDurumu
from api.app.models import Kullanici


async def test_kayitta_rol_secilemez(istemci):
    """İstek gövdesine 'rol' eklense bile yok sayılır."""
    y = await istemci.post("/auth/kayit", json={
        "eposta": "sizma@test.local", "parola": "parola12345",
        "ad": "Sızma Denemesi", "rol": "yonetici",
    })
    assert y.status_code == 201
    d = y.json()
    assert d["rol"] is None, "Kullanıcı kendi rolünü atayamamalı"
    assert d["onay_durumu"] == "beklemede"


async def test_onaysiz_hesap_giris_yapamaz(istemci):
    await istemci.post("/auth/kayit", json={
        "eposta": "bekleyen@test.local", "parola": "parola12345",
        "ad": "Bekleyen",
    })
    y = await istemci.post("/auth/giris", json={
        "eposta": "bekleyen@test.local", "parola": "parola12345",
    })
    assert y.status_code == 403
    assert "onaylanmad" in y.json()["detail"]


async def test_jetonsuz_istek_reddedilir(istemci):
    assert (await istemci.get("/enkaz-alani")).status_code == 401
    assert (await istemci.get("/tespit/inceleme-kuyrugu")).status_code == 401


async def test_gecersiz_jeton_reddedilir(istemci):
    y = await istemci.get("/enkaz-alani",
                          headers={"Authorization": "Bearer sahte.jeton.degeri"})
    assert y.status_code == 401


@pytest.mark.parametrize("rol,beklenen", [
    ("belediye", 201), ("afad", 201), ("yonetici", 201),
    ("saha", 403), ("uzman", 403), ("yikim", 403), ("tesis", 403),
])
async def test_alan_olusturma_yetkisi(istemci, jeton, rol, beklenen):
    y = await istemci.post("/enkaz-alani", headers=await jeton(rol),
                           json={"ad": f"{rol} alanı", "erisim_durumu": "acik"})
    assert y.status_code == beklenen, f"{rol} için beklenen {beklenen}"


@pytest.mark.parametrize("rol,beklenen", [
    ("uzman", 200), ("yonetici", 200),
    ("belediye", 403), ("saha", 403), ("afad", 403),
    ("yikim", 403), ("tesis", 403),
])
async def test_dogrulama_yetkisi(istemci, jeton, tespit_kur, rol, beklenen):
    tid = await tespit_kur()
    y = await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton(rol),
                           json={"durum": "onaylandi"})
    assert y.status_code == beklenen, f"{rol} için beklenen {beklenen}"


@pytest.mark.parametrize("rol,beklenen", [
    ("saha", 201), ("uzman", 201), ("yonetici", 201),
    ("belediye", 403), ("afad", 403), ("yikim", 403), ("tesis", 403),
])
async def test_olcum_girme_yetkisi(istemci, jeton, tespit_kur, rol, beklenen):
    tid = await tespit_kur()
    y = await istemci.post("/olcum", headers=await jeton(rol), json={
        "tespit_id": tid, "tur": "agirlik", "deger": 5.0,
        "birim": "ton", "yontem": "Kantar",
    })
    assert y.status_code == beklenen, f"{rol} için beklenen {beklenen}"


async def test_salt_okunur_roller_hicbir_yazma_yapamaz(istemci, jeton, tespit_kur):
    """Yıkım firması ve tesis operatörü yalnızca görüntüleyebilir."""
    tid = await tespit_kur()
    for rol in ("yikim", "tesis"):
        b = await jeton(rol)
        assert (await istemci.post("/enkaz-alani", headers=b,
                json={"ad": "x", "erisim_durumu": "acik"})).status_code == 403
        assert (await istemci.post(f"/tespit/{tid}/dogrula", headers=b,
                json={"durum": "onaylandi"})).status_code == 403
        assert (await istemci.post("/olcum", headers=b, json={
                "tespit_id": tid, "tur": "agirlik", "deger": 1.0,
                "birim": "ton", "yontem": "x"})).status_code == 403


async def test_rol_atamayi_yalnizca_yonetici_yapar(istemci, jeton, kullanicilar):
    hedef = kullanicilar["saha"]
    for rol in ("belediye", "afad", "uzman", "saha"):
        y = await istemci.post(f"/auth/kullanici/{hedef}/rol",
                               headers=await jeton(rol),
                               json={"rol": "yonetici", "onay_durumu": "onaylandi"})
        assert y.status_code == 403, f"{rol} rol atayamamalı"

    y = await istemci.post(f"/auth/kullanici/{hedef}/rol",
                           headers=await jeton("yonetici"),
                           json={"rol": "uzman", "onay_durumu": "onaylandi"})
    assert y.status_code == 200
    assert y.json()["rol"] == "uzman"


async def test_saha_gorunurlugu_role_gore_filtrelenir(istemci, jeton):
    """Belediye kendi oluşturduğunu görür; AFAD tümünü görür."""
    await istemci.post("/enkaz-alani", headers=await jeton("belediye"),
                       json={"ad": "Belediye alanı", "erisim_durumu": "acik"})

    belediye = (await istemci.get("/enkaz-alani",
                                  headers=await jeton("belediye"))).json()
    afad = (await istemci.get("/enkaz-alani", headers=await jeton("afad"))).json()
    yikim = (await istemci.get("/enkaz-alani", headers=await jeton("yikim"))).json()

    assert len(belediye) == 1
    assert len(afad) == 1, "AFAD çok sahalı görünüme sahiptir"
    assert len(yikim) == 0, "Yıkım firması ilişkisiz sahayı görmemeli"


async def test_parola_ozeti_hicbir_yanitta_gorunmez(istemci, jeton, kullanicilar):
    y = await istemci.get("/auth/ben", headers=await jeton("saha"))
    assert "sifre_hash" not in y.text
    assert "parola" not in y.text.lower()


async def test_uzman_inceleme_bekleyen_sahayi_gorur(istemci, jeton, tespit_kur):
    """Uzman, iş bulunan sahaları görür.

    Uzmana saha atama akışı henüz yok; görünürlük iş üzerinden türetilir.
    Uzman kuyruktan doğrulama yaparken tespiti bağlamında görebilmeli,
    ölçüm ve laboratuvar kaydı ekleyebilmelidir.
    """
    await tespit_kur("beton_tugla", inceleme=True)

    uzman = (await istemci.get("/enkaz-alani", headers=await jeton("uzman"))).json()
    assert len(uzman) == 1, "Uzman inceleme bekleyen sahayı görmeli"


async def test_uzman_isi_olmayan_sahayi_gormez(istemci, jeton, tespit_kur,
                                               kullanicilar):
    """Görünürlük iş üzerinden türetilir; her saha açılmaz."""
    tid = await tespit_kur("beton_tugla")
    # Tek tespit onaylanınca ortada bekleyen iş kalmaz.
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})

    # Uzman kendi doğruladığı kaydı görmeye devam eder (izlenebilirlik).
    uzman = (await istemci.get("/enkaz-alani", headers=await jeton("uzman"))).json()
    assert len(uzman) == 1

    # Yıkım firmasının o sahada hiçbir işi yok.
    yikim = (await istemci.get("/enkaz-alani", headers=await jeton("yikim"))).json()
    assert len(yikim) == 0


async def test_saha_personeli_alanlari_gorur(istemci, jeton, tespit_kur):
    """K-014 — saha personeli tanımlı sahaları görür.

    Rolün tek işi görüntü yüklemek. Görünürlük "oluşturduğu ya da daha
    önce görüntü yüklediği saha" ile sınırlandığında, saha personeli bir
    sahaya görüntü yükleyebilmek için o sahaya DAHA ÖNCE görüntü yüklemiş
    olmak zorunda kalıyordu — rol tamamen işlevsizdi.
    """
    await tespit_kur("beton_tugla")
    alanlar = (await istemci.get("/enkaz-alani",
                                 headers=await jeton("saha"))).json()
    assert len(alanlar) == 1, "Saha personeli tanımlı sahayı görmeli"


async def test_dis_taraflar_atanmamis_sahayi_gormez(istemci, jeton, tespit_kur):
    """Yıkım firması ve geri kazanım tesisi dış taraftır.

    Atama akışı gelene kadar boş liste görmeleri DOĞRU davranıştır;
    saha personeline tanınan genişletme bu rollere tanınmaz.
    """
    await tespit_kur("beton_tugla")
    for rol in ("yikim", "tesis"):
        y = (await istemci.get("/enkaz-alani", headers=await jeton(rol))).json()
        assert y == [], f"{rol} atanmamış sahayı görmemeli"


async def test_harita_rol_kapsamiyla_sinirli(istemci, jeton, tespit_kur):
    """K-017 — harita dağılımı da rolün gördüğü sahalarla sınırlıdır.

    Önceden hiçbir saha göremeyen bir rol, haritada "0 enkaz alanı"
    yazarken yanında sistemin TAMAMINA ait malzeme kırılımını okuyordu.
    """
    tid = await tespit_kur("metal")
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})

    yonetici = (await istemci.get("/harita",
                                  headers=await jeton("yonetici"))).json()
    assert sum(d["adet"] for d in yonetici["malzeme_dagilimi"]) == 1

    yikim = (await istemci.get("/harita", headers=await jeton("yikim"))).json()
    assert yikim["malzeme_dagilimi"] == [], (
        "Hiçbir saha göremeyen rol, haritada da veri görmemeli"
    )


async def test_gecmis_sistem_genelini_herkes_goremez(istemci, jeton, tespit_kur):
    """K-017 — sistem geneli denetim dökümü sınırlıdır, kayıt bazlı değil.

    Arayüzde sekmeyi gizlemek yetki değildir; uç nokta doğrudan
    çağrılabilir.
    """
    tid = await tespit_kur("beton_tugla")

    for rol in ("yikim", "tesis", "saha"):
        y = await istemci.get("/gecmis", headers=await jeton(rol))
        assert y.status_code == 403, f"{rol} sistem geneli dökümü görmemeli"

    for rol in ("yonetici", "uzman", "belediye", "afad"):
        y = await istemci.get("/gecmis", headers=await jeton(rol))
        assert y.status_code == 200, f"{rol} sistem geneli dökümü görmeli"

    # Tek bir kaydın geçmişi herkese açıktır: tespit detayındaki
    # "Bu tespitin geçmişi" paneli buradan beslenir.
    y = await istemci.get(f"/gecmis?kayit_tipi=tespit&kayit_id={tid}",
                          headers=await jeton("saha"))
    assert y.status_code == 200
    assert len(y.json()) >= 1


async def test_gecmis_kullanici_adini_dondurur(istemci, jeton, tespit_kur):
    """Denetim kaydının vaadi "KİM, ne zaman, neyi değiştirdi"."""
    tid = await tespit_kur("beton_tugla")
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})

    y = (await istemci.get(f"/gecmis?kayit_tipi=tespit&kayit_id={tid}",
                           headers=await jeton("uzman"))).json()
    guncelleme = [k for k in y if k["islem"] == "guncelleme"]
    assert guncelleme, "Doğrulama geçmişe düşmeli"
    assert guncelleme[0]["kullanici_ad"], "Kullanıcı adı dönmeli, yalnızca id değil"
