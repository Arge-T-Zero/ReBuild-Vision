"""KURAL 2 — Tehlikeli madde teşhisi yapılmaz.

Rapor 3.5: "Asbest ve benzeri tehlikeli maddeler görüntü üzerinden teşhis
edilmeyecek."
Rapor 12: Analiz sonucu bulunmayan alan için "güvenli" değerlendirmesi de
yapılmaz — yokluk, güvenlik anlamına gelmez.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text

import api.app.db as db_modulu
from api.app.models import TehlikeliDurum

pytestmark = pytest.mark.kural


def test_enum_yalnizca_iki_deger_icerir():
    """Değer kümesinde 'guvenli' veya risk seviyesi YOKTUR."""
    degerler = {d.value for d in TehlikeliDurum}
    assert degerler == {"incelemeye_yonlendirildi", "lab_sonucu_var"}

    yasakli = {"guvenli", "tehlikesiz", "temiz", "risk_yok", "dusuk_risk"}
    assert not (degerler & yasakli)


async def test_guvenli_degeri_veri_tabaninca_reddedilir():
    """Bir hata uygulama katmanını atlarsa veri tabanı yakalar."""
    async with db_modulu.OturumUret() as db:
        with pytest.raises(Exception) as h:
            await db.execute(text(
                "INSERT INTO tehlikeli_kayit (tespit_id, durum, giren_id) "
                "VALUES (1, 'guvenli', 1)"
            ))
            await db.commit()
    assert "tehlikeli_durum_turu" in str(h.value)


async def test_tabloda_olasilik_veya_risk_alani_yok():
    """Şemada tahmin üretebilecek hiçbir alan bulunmamalı."""
    async with db_modulu.OturumUret() as db:
        y = await db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'tehlikeli_kayit'"
        ))
        sutunlar = {s[0] for s in y}

    yasakli = {
        "olasilik", "guven_skoru", "risk_seviyesi", "madde_adi",
        "madde_tahmini", "guvenli", "tehlike_puani",
    }
    assert not (sutunlar & yasakli), (
        f"Tehlikeli madde tahmini üretebilecek alan bulundu: {sutunlar & yasakli}"
    )


async def test_model_ciktisinda_tehlikeli_madde_sinifi_yok():
    """Sınıf listesi hiçbir tehlikeli madde sınıfı içermez."""
    from api.app.core.config import siniflar

    adlar = {s["ad"] for s in siniflar()["siniflar"]}
    yasakli = {"asbest", "asbestos", "tehlikeli", "kimyasal", "zehirli"}
    assert not (adlar & yasakli)
    for ad in adlar:
        assert "asbest" not in ad.lower()


async def test_api_hicbir_yerde_guvenli_degerlendirmesi_dondurmez(
    istemci, jeton, tespit_kur
):
    """Uç nokta yanıtlarında 'güvenli' ima eden alan bulunmaz."""
    tid = await tespit_kur()
    baslik = await jeton("belediye")

    for yol in [f"/tespit/{tid}", f"/miktar/{tid}", "/harita", "/sistem/durum"]:
        y = await istemci.get(yol, headers=baslik)
        assert y.status_code == 200, yol
        metin = y.text.lower()
        for sozcuk in ["güvenli", "guvenli", "tehlikesiz", "risk yok"]:
            assert sozcuk not in metin, f"{yol} yanıtında '{sozcuk}' geçiyor"
