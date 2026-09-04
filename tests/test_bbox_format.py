"""bbox_format — brief'in en sık hata kaynağı olarak işaretlediği alan.

Ana talimat Bölüm 4.3: kutuların hangi koordinat uzayında verildiği
belirsiz bırakılmaz.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text

import api.app.db as db_modulu


async def test_bbox_format_bos_gecilemez():
    """NOT NULL kısıtı — uygulama katmanı atlansa bile veri tabanı yakalar."""
    async with db_modulu.OturumUret() as db:
        with pytest.raises(Exception) as h:
            await db.execute(text(
                "INSERT INTO tespit (goruntu_id, sinif, guven_skoru) "
                "VALUES (1, 'tugla', 0.8)"
            ))
            await db.commit()
    assert "bbox_format" in str(h.value)


async def test_bos_metin_bbox_format_reddedilir():
    async with db_modulu.OturumUret() as db:
        with pytest.raises(Exception) as h:
            await db.execute(text(
                "INSERT INTO tespit (goruntu_id, sinif, guven_skoru, bbox_format) "
                "VALUES (1, 'tugla', 0.8, '')"
            ))
            await db.commit()
    assert "ck_tespit_bbox_format_dolu" in str(h.value)


async def test_api_yanitinda_bbox_format_her_zaman_dolu(
    istemci, jeton, tespit_kur
):
    tid = await tespit_kur()
    d = (await istemci.get(f"/tespit/{tid}", headers=await jeton("uzman"))).json()
    assert d["bbox_format"]
    assert d["bbox_format"] == "pixel_absolute_original"


async def test_guven_skoru_araligi_zorlanir():
    """0-1 dışındaki güven skoru kabul edilmez."""
    async with db_modulu.OturumUret() as db:
        with pytest.raises(Exception) as h:
            await db.execute(text(
                "INSERT INTO tespit (goruntu_id, sinif, guven_skoru, bbox_format) "
                "VALUES (1, 'tugla', 1.5, 'pixel_absolute_original')"
            ))
            await db.commit()
    assert "ck_tespit_guven_araligi" in str(h.value)
