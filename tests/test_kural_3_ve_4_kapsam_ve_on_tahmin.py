"""KURAL 3 ve 4 — Enkaz altı görülmez · Nihai kararı sistem vermez.

Rapor 12: "Sistemin yalnızca görünür yüzeye ilişkin ön değerlendirme
yaptığının açıkça belirtilmesi."
Rapor 12 / 3.7: model çıktıları "ön tahmin" olarak gösterilir; doğrulanmamış
kayıtlar hesaplara girmez.
"""
from __future__ import annotations

import pytest

import api.app.db as db_modulu
from api.app.models import DogrulamaDurumu

pytestmark = pytest.mark.kural


# --- KURAL 3: kapsam uyarısı ------------------------------------------------

async def test_kapsam_uyarisi_sistem_durumunda_bulunur(istemci):
    d = (await istemci.get("/sistem/durum")).json()
    u = d["kapsam_uyarisi"]
    assert "görünür yüzey" in u
    assert "enkaz altı" in u


async def test_kapsam_uyarisi_harita_yanitinda_bulunur(istemci, jeton, kullanicilar):
    d = (await istemci.get("/harita", headers=await jeton("belediye"))).json()
    assert "görünür yüzey" in d["kapsam_uyarisi"]


async def test_toplam_enkaz_iddiasi_uretilmez(istemci, jeton, kullanicilar):
    """Harita yanıtı toplam enkaz içeriği iddiası içermez."""
    d = (await istemci.get("/harita", headers=await jeton("belediye"))).json()
    assert "toplam_enkaz" not in d
    assert "toplam_tonaj" not in d
    assert "tahmini_toplam" not in d


# --- KURAL 4: ön tahmin ve doğrulama filtresi -------------------------------

async def test_her_tespit_on_tahmin_etiketi_tasir(istemci, jeton, tespit_kur):
    tid = await tespit_kur()
    d = (await istemci.get(f"/tespit/{tid}", headers=await jeton("uzman"))).json()
    assert d["etiket"] == "ön tahmin"


async def test_dogrulanmamis_kayit_haritaya_girmez(
    istemci, jeton, tespit_kur
):
    """Beklemedeki kayıt hesaba girmez — bu bir veri katmanı kuralıdır."""
    await tespit_kur("metal")
    d = (await istemci.get("/harita", headers=await jeton("belediye"))).json()
    assert d["malzeme_dagilimi"] == []


async def test_belirsiz_isaretlenen_kayit_haritaya_girmez(
    istemci, jeton, tespit_kur
):
    """'Belirsiz' = uzman karar veremedi; hesaba katılmaz."""
    tid = await tespit_kur("metal")
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "belirsiz"})
    d = (await istemci.get("/harita", headers=await jeton("belediye"))).json()
    assert d["malzeme_dagilimi"] == []


async def test_onaylanan_kayit_haritaya_girer(istemci, jeton, tespit_kur):
    tid = await tespit_kur("metal")
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})
    d = (await istemci.get("/harita", headers=await jeton("belediye"))).json()
    assert d["malzeme_dagilimi"] == [{"sinif": "metal", "adet": 1}]


async def test_uzman_duzeltmesi_model_tahminini_gecersiz_kilar(
    istemci, jeton, tespit_kur
):
    """İnsan denetimli yapay zekâ iddiasının kod karşılığı."""
    tid = await tespit_kur("sert_plastik")
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "duzeltildi", "duzeltilen_sinif": "metal"})

    d = (await istemci.get("/harita", headers=await jeton("belediye"))).json()
    assert d["malzeme_dagilimi"] == [{"sinif": "metal", "adet": 1}], (
        "Harita uzmanın düzelttiği sınıfı göstermeli, modelin tahminini değil"
    )

    # Ham tahmin izlenebilirlik için korunur.
    t = (await istemci.get(f"/tespit/{tid}", headers=await jeton("uzman"))).json()
    assert t["sinif"] == "sert_plastik"
    assert t["duzeltilen_sinif"] == "metal"


async def test_konteynere_duzeltilen_kayit_hesaptan_cikar(
    istemci, jeton, tespit_kur
):
    """K-007: malzeme olmayan sınıf haritaya ve miktara girmez."""
    tid = await tespit_kur("metal")
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "duzeltildi", "duzeltilen_sinif": "konteyner"})
    d = (await istemci.get("/harita", headers=await jeton("belediye"))).json()
    assert d["malzeme_dagilimi"] == []


async def test_reddet_aksiyonu_yoktur():
    """K-004: rapor gövde metni üç aksiyon tanımlar."""
    degerler = {d.value for d in DogrulamaDurumu}
    assert degerler == {"beklemede", "onaylandi", "duzeltildi", "belirsiz"}
    assert "reddedildi" not in degerler
    assert "reddet" not in degerler


async def test_reddet_istegi_semaca_reddedilir(istemci, jeton, tespit_kur):
    tid = await tespit_kur()
    y = await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                           json={"durum": "reddedildi"})
    assert y.status_code == 422


async def test_beklemede_durumu_dogrulama_sonucu_olamaz(
    istemci, jeton, tespit_kur
):
    tid = await tespit_kur()
    y = await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                           json={"durum": "beklemede"})
    assert y.status_code == 400


async def test_duzeltme_yeni_sinif_olmadan_kabul_edilmez(
    istemci, jeton, tespit_kur
):
    tid = await tespit_kur()
    y = await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                           json={"durum": "duzeltildi"})
    assert y.status_code == 400


async def test_gecersiz_sinifa_duzeltilemez(istemci, jeton, tespit_kur):
    tid = await tespit_kur()
    y = await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                           json={"durum": "duzeltildi", "duzeltilen_sinif": "altin"})
    assert y.status_code == 400
