"""Alembic ortamı — async motor ile."""
from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

DEPO_KOKU = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(DEPO_KOKU))

from api.app.core.config import ayarlar  # noqa: E402
from api.app.db import Temel  # noqa: E402
from api.app import models  # noqa: E402,F401 — tablolar kaydedilsin

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

hedef_metadata = Temel.metadata


def _dahil_mi(nesne, ad, tur, yansitiliyor, karsilastirilan):
    """Göçe girmeyecek nesneler.

    1. PostGIS'in kendi tabloları.
    2. Geometri sütunlarının uzamsal indeksleri: GeoAlchemy2 bunları kendi
       DDL olaylarıyla zaten oluşturur. Göçe de yazılırsa aynı indeks iki
       kez oluşturulmaya çalışılır ve DuplicateTableError alınır.
    """
    if tur == "table" and ad in {"spatial_ref_sys"}:
        return False
    if tur == "index" and any(
        s.type.__class__.__name__ == "Geometry"
        for s in getattr(nesne, "columns", [])
    ):
        return False
    return True


def cevrimdisi() -> None:
    context.configure(
        url=ayarlar().veritabani_url,
        target_metadata=hedef_metadata,
        literal_binds=True,
        include_object=_dahil_mi,
    )
    with context.begin_transaction():
        context.run_migrations()


def _calistir(baglanti) -> None:
    context.configure(
        connection=baglanti,
        target_metadata=hedef_metadata,
        include_object=_dahil_mi,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def _cevrimici() -> None:
    motor = create_async_engine(ayarlar().veritabani_url, future=True)
    async with motor.connect() as baglanti:
        await baglanti.run_sync(_calistir)
    await motor.dispose()


if context.is_offline_mode():
    cevrimdisi()
else:
    asyncio.run(_cevrimici())
