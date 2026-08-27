"""Tehlikeli madde yönlendirme akışı — teşhis değil, yönlendirme.

Ana talimat Bölüm 1.2 / Rapor 3.5 ve 12.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.kural


async def test_kayit_yokken_guvenli_denmez(istemci, jeton, tespit_kur):
    """Yokluk, güvenlik anlamına GELMEZ — yanıt bunu açıkça söyler."""
    tid = await tespit_kur()
    d = (await istemci.get(f"/tehlikeli/tespit/{tid}",
                           headers=await jeton("belediye"))).json()

    assert d["kayitlar"] == []
    assert d["degerlendirme"] == "degerlendirilmedi"
    assert d["degerlendirme"] != "guvenli"
    assert "GELMEZ" in d["aciklama"]
    assert "teşhisi yapmaz" in d["aciklama"]


async def test_yonlendirme_kaydi_acilabilir(istemci, jeton, tespit_kur):
    tid = await tespit_kur()
    y = await istemci.post("/tehlikeli", headers=await jeton("saha"), json={
        "tespit_id": tid, "durum": "incelemeye_yonlendirildi",
    })
    assert y.status_code == 201
    assert y.json()["durum"] == "incelemeye_yonlendirildi"

    d = (await istemci.get(f"/tehlikeli/tespit/{tid}",
                           headers=await jeton("saha"))).json()
    assert len(d["kayitlar"]) == 1
    assert d["aciklama"] is None


async def test_guvenli_durumu_semaca_reddedilir(istemci, jeton, tespit_kur):
    """Şema yalnızca iki değer kabul eder."""
    tid = await tespit_kur()
    for yasakli in ("guvenli", "tehlikesiz", "temiz", "dusuk_risk"):
        y = await istemci.post("/tehlikeli", headers=await jeton("uzman"),
                               json={"tespit_id": tid, "durum": yasakli})
        assert y.status_code == 422, f"'{yasakli}' kabul edilmemeli"


async def test_lab_sonucunu_yalnizca_uzman_girer(istemci, jeton, tespit_kur):
    """Sonucu model değil, yetkili insan girer."""
    tid = await tespit_kur()
    govde = {
        "tespit_id": tid, "durum": "lab_sonucu_var",
        "lab_sonucu_notu": "Numunede asbest tespit edilmedi (rapor no 123).",
    }

    y = await istemci.post("/tehlikeli", headers=await jeton("saha"), json=govde)
    assert y.status_code == 403, "Saha personeli laboratuvar sonucu giremez"

    y = await istemci.post("/tehlikeli", headers=await jeton("uzman"), json=govde)
    assert y.status_code == 201


async def test_lab_sonucu_notsuz_kabul_edilmez(istemci, jeton, tespit_kur):
    """Sonuç var deniyorsa dayanağı yazılmalı."""
    tid = await tespit_kur()
    y = await istemci.post("/tehlikeli", headers=await jeton("uzman"), json={
        "tespit_id": tid, "durum": "lab_sonucu_var", "lab_sonucu_notu": "  ",
    })
    assert y.status_code == 400


async def test_salt_okunur_roller_yonlendiremez(istemci, jeton, tespit_kur):
    tid = await tespit_kur()
    for rol in ("yikim", "tesis"):
        y = await istemci.post("/tehlikeli", headers=await jeton(rol), json={
            "tespit_id": tid, "durum": "incelemeye_yonlendirildi",
        })
        assert y.status_code == 403


async def test_yanit_semasinda_olasilik_alani_yok(istemci, jeton, tespit_kur):
    """Yanıt hiçbir tahmin alanı içermez."""
    tid = await tespit_kur()
    await istemci.post("/tehlikeli", headers=await jeton("uzman"), json={
        "tespit_id": tid, "durum": "incelemeye_yonlendirildi",
    })
    d = (await istemci.get(f"/tehlikeli/tespit/{tid}",
                           headers=await jeton("uzman"))).json()

    kayit = d["kayitlar"][0]
    for yasakli in ("olasilik", "guven_skoru", "risk_seviyesi",
                    "madde_adi", "tehlike_puani"):
        assert yasakli not in kayit


async def test_yonlendirme_islem_gecmisine_duser(istemci, jeton, tespit_kur):
    tid = await tespit_kur()
    await istemci.post("/tehlikeli", headers=await jeton("uzman"), json={
        "tespit_id": tid, "durum": "incelemeye_yonlendirildi",
    })
    g = (await istemci.get("/gecmis?kayit_tipi=tehlikeli_kayit",
                           headers=await jeton("uzman"))).json()
    assert len(g) == 1
    assert g[0]["islem"] == "olusturma"
    assert g[0]["kayit_id"] is not None
