"""OGC API - Features — açık coğrafi standart (Şartname Madde 10.8).

Bu testlerin asıl işi bir kaçamağı engellemek: standart bir uç nokta
açmak, kural süzgecini atlamanın yolu OLMAMALIDIR. Coğrafi bir serviste
bu, doğrulanmamış bir ön tahminin kamu haritasına düşmesi demektir.

Uç nokta sorguyu yeniden yazmaz; `rapor.py` içindeki ortak sorguyu
kullanır. Aşağıdaki testler bunun böyle kaldığını doğrular.
"""
from __future__ import annotations

import json

import pytest_asyncio

import api.app.db as db_modulu
from api.app.geo import nokta
from api.app.models import EnkazAlani, Goruntu, Tespit

# Ankara yakını — Türkiye sınırları içinde, koordinat sırası testi için.
TEST_ENLEM = 39.9334
TEST_BOYLAM = 32.8597


@pytest_asyncio.fixture
async def konumlu_tespit(kullanicilar):
    """Alan → görüntü → tespit zinciri kurar; alanın KONUMU vardır.

    `conftest.tespit_kur` konumsuz alan üretiyor ve coğrafi uç nokta
    konumsuz kaydı (doğru biçimde) eliyor. OGC testleri konuma ihtiyaç
    duyduğu için bu yardımcı ayrı duruyor; `conftest` değiştirilmedi.
    """
    async def kur(sinif: str = "beton", dogrulama: str = "beklemede") -> int:
        async with db_modulu.OturumUret() as db:
            a = EnkazAlani(ad="OGC Test Alan",
                           olusturan_id=kullanicilar["belediye"],
                           konum=nokta(TEST_ENLEM, TEST_BOYLAM))
            db.add(a)
            await db.flush()
            g = Goruntu(enkaz_alani_id=a.id, dosya_yolu="t.jpg",
                        genislik=1000, yukseklik=800,
                        yukleyen_id=kullanicilar["saha"])
            db.add(g)
            await db.flush()
            t = Tespit(goruntu_id=g.id, sinif=sinif, guven_skoru=0.9,
                       bbox={"x": 1, "y": 1, "w": 10, "h": 10},
                       bbox_format="pixel_absolute_original",
                       inceleme_gerekli=False,
                       dogrulama_durumu=dogrulama)
            db.add(t)
            await db.commit()
            return t.id
    return kur


async def _hazirla(istemci, jeton, konumlu_tespit):
    """Bir doğrulanmış, bir doğrulanmamış, bir konteyner kaydı kurar."""
    onayli = await konumlu_tespit("metal")
    await istemci.post(f"/tespit/{onayli}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})
    beklemede = await konumlu_tespit("ahsap")
    konteyner = await konumlu_tespit("konteyner")
    await istemci.post(f"/tespit/{konteyner}/dogrula",
                       headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})
    return onayli, beklemede, konteyner


# --- Standart uyumu ---------------------------------------------------

async def test_karsilama_sayfasi_baglantilari_verir(istemci):
    d = json.loads((await istemci.get("/ogc")).text)
    iliskiler = {b["rel"] for b in d["links"]}
    # OGC API - Features Core: karşılama sayfası bu üçünü göstermeli.
    assert {"self", "conformance", "data"} <= iliskiler


async def test_uygunluk_yalnizca_karsilanan_siniflari_beyan_eder(istemci):
    d = json.loads((await istemci.get("/ogc/conformance")).text)
    assert any("conf/core" in u for u in d["conformsTo"])
    assert any("conf/geojson" in u for u in d["conformsTo"])
    # oas30 BEYAN EDİLMEZ: sistem OpenAPI 3.1 üretir, 3.0 değil.
    # Karşılanmayan bir uygunluk sınıfını beyan etmek yanlış beyandır.
    assert not any("oas30" in u for u in d["conformsTo"]), (
        "Karşılanmayan uygunluk sınıfı beyan edilmiş"
    )


async def test_koleksiyon_crs_ve_baglantilari(istemci):
    d = json.loads((await istemci.get("/ogc/collections/tespit")).text)
    assert d["id"] == "tespit"
    assert d["itemType"] == "feature"
    # Veri tabanında EPSG:4326 saklanıyor; dönüşüm yapılmıyor.
    assert "CRS84" in d["crs"][0]


async def test_bilinmeyen_koleksiyon_404(istemci, jeton):
    for yol in ("/ogc/collections/yok",
                "/ogc/collections/yok/items"):
        y = await istemci.get(yol, headers=await jeton("belediye"))
        assert y.status_code == 404, yol


# --- KURAL SÜZGECİ — asıl korunan şey --------------------------------

async def test_dogrulanmamis_kayit_ogc_uzerinden_sizmaz(
        istemci, jeton, konumlu_tespit):
    onayli, beklemede, _ = await _hazirla(istemci, jeton, konumlu_tespit)
    d = json.loads((await istemci.get(
        "/ogc/collections/tespit/items?limit=1000",
        headers=await jeton("belediye"))).text)

    kimlikler = [f["id"] for f in d["features"]]
    assert onayli in kimlikler
    assert beklemede not in kimlikler, (
        "Doğrulanmamış ön tahmin coğrafi servise sızdı — kamu haritasına "
        "düşebilirdi"
    )


async def test_konteyner_ogc_uzerinden_sizmaz(istemci, jeton, konumlu_tespit):
    _, _, konteyner = await _hazirla(istemci, jeton, konumlu_tespit)
    d = json.loads((await istemci.get(
        "/ogc/collections/tespit/items?limit=1000",
        headers=await jeton("belediye"))).text)

    assert konteyner not in [f["id"] for f in d["features"]]
    assert "konteyner" not in {f["properties"]["sinif"] for f in d["features"]}


async def test_tek_kayit_ucu_de_kural_suzgecinden_gecer(
        istemci, jeton, konumlu_tespit):
    """id ile doğrudan erişim, doğrulama kuralını atlamanın yolu olamaz."""
    _, beklemede, _ = await _hazirla(istemci, jeton, konumlu_tespit)
    y = await istemci.get(f"/ogc/collections/tespit/items/{beklemede}",
                          headers=await jeton("belediye"))
    assert y.status_code == 404, (
        "Doğrulanmamış kayda id ile ulaşıldı — süzgeç atlanmış"
    )


async def test_ogc_ve_rapor_ayni_kayitlari_verir(istemci, jeton, konumlu_tespit):
    """İki uç nokta ayrışırsa biri kuralı atlıyor demektir."""
    await _hazirla(istemci, jeton, konumlu_tespit)
    basliklar = await jeton("belediye")

    ogc = json.loads((await istemci.get(
        "/ogc/collections/tespit/items?limit=1000", headers=basliklar)).text)
    rapor = json.loads((await istemci.get(
        "/rapor/geojson", headers=basliklar)).text)

    assert ([f["id"] for f in ogc["features"]]
            == [f["properties"]["tespit_id"] for f in rapor["features"]])


async def test_yetkisiz_istek_reddedilir(istemci):
    y = await istemci.get("/ogc/collections/tespit/items")
    assert y.status_code == 401


# --- GeoJSON biçimi ---------------------------------------------------

async def test_koordinat_sirasi_boylam_enlem(istemci, jeton, konumlu_tespit):
    """RFC 7946: önce boylam, sonra enlem. Ters yazmak en sık hatadır."""
    await _hazirla(istemci, jeton, konumlu_tespit)
    d = json.loads((await istemci.get(
        "/ogc/collections/tespit/items", headers=await jeton("belediye"))).text)

    boylam, enlem = d["features"][0]["geometry"]["coordinates"]
    # Demo veri Türkiye'de: boylam 25-45, enlem 35-43.
    assert 25 <= boylam <= 45, f"boylam beklenen aralıkta değil: {boylam}"
    assert 35 <= enlem <= 43, f"enlem beklenen aralıkta değil: {enlem}"


async def test_sayfalama_alanlari_dogru(istemci, jeton, konumlu_tespit):
    await _hazirla(istemci, jeton, konumlu_tespit)
    d = json.loads((await istemci.get(
        "/ogc/collections/tespit/items?limit=1",
        headers=await jeton("belediye"))).text)

    assert d["type"] == "FeatureCollection"
    assert d["numberReturned"] == len(d["features"]) == 1
    assert d["numberMatched"] >= d["numberReturned"]


async def test_bozuk_bbox_400_doner(istemci, jeton):
    y = await istemci.get("/ogc/collections/tespit/items?bbox=bozuk",
                          headers=await jeton("belediye"))
    assert y.status_code == 400


async def test_kapsam_uyarisi_ogc_ciktisinda_da_var(
        istemci, jeton, konumlu_tespit):
    """QGIS'ten bağlanan biri README okumaz; uyarı veriyle gelmeli."""
    await _hazirla(istemci, jeton, konumlu_tespit)
    d = json.loads((await istemci.get(
        "/ogc/collections/tespit/items", headers=await jeton("belediye"))).text)

    assert "kunye" in d
    assert d["kunye"]["kapsam_uyarisi"]
    assert "görünür yüzey" in d["kunye"]["kapsam_uyarisi"]
