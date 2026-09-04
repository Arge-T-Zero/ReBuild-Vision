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
    await tespit_kur("beton", inceleme=True)

    uzman = (await istemci.get("/enkaz-alani", headers=await jeton("uzman"))).json()
    assert len(uzman) == 1, "Uzman inceleme bekleyen sahayı görmeli"


async def test_uzman_isi_olmayan_sahayi_gormez(istemci, jeton, tespit_kur,
                                               kullanicilar):
    """Görünürlük iş üzerinden türetilir; her saha açılmaz."""
    tid = await tespit_kur("beton")
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
    await tespit_kur("beton")
    alanlar = (await istemci.get("/enkaz-alani",
                                 headers=await jeton("saha"))).json()
    assert len(alanlar) == 1, "Saha personeli tanımlı sahayı görmeli"


async def test_dis_taraflar_atanmamis_sahayi_gormez(istemci, jeton, tespit_kur):
    """Yıkım firması ve geri kazanım tesisi dış taraftır.

    Atama akışı gelene kadar boş liste görmeleri DOĞRU davranıştır;
    saha personeline tanınan genişletme bu rollere tanınmaz.
    """
    await tespit_kur("beton")
    for rol in ("yikim", "tesis"):
        y = (await istemci.get("/enkaz-alani", headers=await jeton(rol))).json()
        assert y == [], f"{rol} atanmamış sahayı görmemeli"


async def test_harita_rol_kapsamiyla_sinirli(istemci, jeton, tespit_kur):
    """K-017 — harita dağılımı da rolün gördüğü sahalarla sınırlıdır.

    Önceden hiçbir saha göremeyen bir rol, haritada "0 enkaz alanı"
    yazarken yanında sistemin TAMAMINA ait malzeme kırılımını okuyordu.
    """
    tid = await tespit_kur("tugla")
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
    tid = await tespit_kur("beton")

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
    tid = await tespit_kur("beton")
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})

    y = (await istemci.get(f"/gecmis?kayit_tipi=tespit&kayit_id={tid}",
                           headers=await jeton("uzman"))).json()
    guncelleme = [k for k in y if k["islem"] == "guncelleme"]
    assert guncelleme, "Doğrulama geçmişe düşmeli"
    assert guncelleme[0]["kullanici_ad"], "Kullanıcı adı dönmeli, yalnızca id değil"


# --- Nesne düzeyi yetkilendirme (02.09.2026 denetimi) ---------------------


async def test_gormedigi_sahanin_tespitini_id_ile_okuyamaz(
    istemci, jeton, tespit_kur
):
    """⚠️ BU AÇIK 02.09.2026 DENETİMİNDE BULUNDU.

    Yetki kontrolü EYLEM üzerinden yapılıyordu ("bu rol okuyabilir mi?"),
    NESNE üzerinden unutulmuştu ("bu rol BU KAYDI okuyabilir mi?").

    `gorulebilir_alanlar()` süzgeci liste uçlarında uygulanıyordu: `yikim`
    rolü `/enkaz-alani`'nda boş liste, `/harita`'da boş dağılım görüyordu.
    Ama TEKİL kayıt uçları yalnızca "giriş yapmış mı" diye bakıyordu.

    Sonuç: dış taraf bir rol, id'leri sırayla gezerek göremediği
    sahaların tespitlerini, malzeme sınıflarını ve **hesaplanmış
    tonajını** okuyabiliyordu. Liste ucunda kapatılan kapı tekil uçta
    açıktı.

    Bu test dört ucu birden tutar; biri gevşerse kırılır.
    """
    tid = await tespit_kur("tugla", dogrulama="onaylandi")
    yikim = await jeton("yikim")

    # Önce kapsamın gerçekten dışında olduğunu doğrula — testin
    # varsayımı çürükse geri kalanı anlamsız olurdu.
    alanlar = (await istemci.get("/enkaz-alani", headers=yikim)).json()
    assert alanlar == [], "Test kurgusu bozuk: yikim bu sahayı görüyor"

    # 1) Tespitin kendisi
    y = await istemci.get(f"/tespit/{tid}", headers=yikim)
    assert y.status_code == 404, (
        f"Görülmeyen sahanın tespiti okunabildi: {y.status_code} {y.text[:200]}"
    )

    # 2) Miktar — en pahalı sızıntı: hesaplanmış tonaj
    y = await istemci.get(f"/miktar/{tid}", headers=yikim)
    assert y.status_code == 404, f"Miktar sızdı: {y.status_code}"

    # 3) Ölçümler — tonaj hesabının girdisi
    y = await istemci.get(f"/olcum/tespit/{tid}", headers=yikim)
    assert y.status_code == 200 and y.json() == [], (
        f"Ölçümler sızdı: {y.text[:200]}"
    )

    # 4) Tehlikeli madde kayıtları
    y = await istemci.get(f"/tehlikeli/tespit/{tid}", headers=yikim)
    assert y.status_code == 200
    d = y.json()
    assert d["kayitlar"] == [], "Tehlikeli madde kaydı sızdı"
    # Yokluk açıklaması yine verilmeli: "kayıt yok" ile "göremiyorsun"
    # aynı biçimde yanıtlanır, ve yokluk her iki durumda da güvenlik
    # anlamına gelmez (ana talimat Bölüm 1.2).
    assert d["aciklama"], "Yokluk açıklaması kapsam dışında da verilmeli"


async def test_gormedigi_sahanin_tespitine_olcum_giremez(
    istemci, jeton, tespit_kur
):
    """Yazma tarafı da aynı süzgeçten geçer.

    `saha` rolü ölçüm girebilir (eylem yetkisi var) ama yalnızca
    görebildiği sahalarda (nesne yetkisi). İkisi ayrı sorulardır.
    """
    tid = await tespit_kur("tugla", dogrulama="onaylandi")

    y = await istemci.post("/olcum", headers=await jeton("yikim"), json={
        "tespit_id": tid, "tur": "hacim", "deger": 10.0,
        "birim": "m3", "yontem": "Test",
    })
    # `yikim` ölçüm giremez (eylem yetkisi yok) — 403.
    assert y.status_code == 403


async def test_kapsamindaki_tespiti_okuyabilir(istemci, jeton, tespit_kur):
    """Süzgeç fazla dar olmamalı: yetkili rol kaydı GÖREBİLMELİ.

    Bir yetki düzeltmesinin en sık yan etkisi, kapıyı herkese kapatmak ve
    bunu fark etmemektir. Bu test o yönü tutar.

    `TUM_SAHALARI_GORUR` = {yonetici, afad}. `belediye` kendi oluşturduğu
    sahaları görür ve `conftest.tespit_kur` sahayı belediye adına kurar.
    """
    tid = await tespit_kur("tugla", dogrulama="onaylandi")
    for rol in ("belediye", "afad", "yonetici"):
        y = await istemci.get(f"/tespit/{tid}", headers=await jeton(rol))
        assert y.status_code == 200, (
            f"{rol} kapsamındaki tespiti göremiyor: {y.status_code}"
        )


async def test_uzman_inceleme_bekleyen_tespiti_okuyabilir(
    istemci, jeton, tespit_kur
):
    """Uzmanın görünürlüğü İŞ ÜZERİNDEN türetilir (K-014).

    Uzmana saha atama akışı henüz yok; `gorulebilir_alanlar()` uzmana
    "inceleme bekleyen ya da kendisinin doğruladığı tespiti içeren"
    sahaları verir. Kuyruktan bir kaydı açan uzman onu görebilmelidir —
    demo akışının 5. adımı tam olarak budur.

    ⚠️ Bunun DİĞER YÜZÜ de bilinçlidir ve altta sınanıyor: başka bir
    uzmanın doğruladığı, kapsamında iş bırakmayan bir kaydı göremez.
    Bu bir gerileme değil, liste ucundaki davranışın tekil uca
    uygulanmasıdır — `/enkaz-alani` o sahayı zaten döndürmüyordu.
    """
    tid = await tespit_kur("tugla", inceleme=True)
    y = await istemci.get(f"/tespit/{tid}", headers=await jeton("uzman"))
    assert y.status_code == 200, (
        "Uzman kuyruktaki kaydı açamıyor — doğrulama akışı kırılırdı"
    )


async def test_uzman_isi_olmayan_sahanin_tespitini_okuyamaz(
    istemci, jeton, tespit_kur
):
    """Yukarıdaki kuralın simetrik yüzü.

    Kayıt başka bir uzmanca doğrulanmış ve sahada bekleyen iş yok:
    bu uzmanın kapsamı dışındadır. Liste ucu bu sahayı zaten
    döndürmüyordu; tekil uç 02.09.2026'ya kadar döndürüyordu.
    """
    tid = await tespit_kur("tugla", dogrulama="onaylandi")
    alanlar = (await istemci.get(
        "/enkaz-alani", headers=await jeton("uzman"))).json()
    assert alanlar == [], "Test kurgusu bozuk: uzman bu sahayı listede görüyor"

    y = await istemci.get(f"/tespit/{tid}", headers=await jeton("uzman"))
    assert y.status_code == 404, (
        "Liste ucu sahayı gizlerken tekil uç tespiti veriyor — "
        "iki uç aynı kuralı uygulamalı"
    )
