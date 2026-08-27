"""Geometri yardımcıları — PostGIS ile okuma/yazma."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

SRID = 4326


def nokta(enlem: float, boylam: float):
    """PostGIS POINT üretir. Dikkat: ST_MakePoint(boylam, enlem) sırası."""
    return func.ST_SetSRID(func.ST_MakePoint(boylam, enlem), SRID)


def poligon(noktalar: list[tuple[float, float]]):
    """Kapalı POLYGON üretir. Girdi: [(enlem, boylam), ...]"""
    kapali = list(noktalar)
    if kapali[0] != kapali[-1]:
        kapali.append(kapali[0])
    wkt = ", ".join(f"{b} {e}" for e, b in kapali)
    return func.ST_SetSRID(func.ST_GeomFromText(f"POLYGON(({wkt}))"), SRID)


async def nokta_oku(db: AsyncSession, sutun, kayit_id_kosulu) -> dict | None:
    """POINT sütununu {enlem, boylam} olarak okur."""
    y = await db.execute(
        select(func.ST_Y(sutun), func.ST_X(sutun)).where(kayit_id_kosulu)
    )
    satir = y.first()
    if not satir or satir[0] is None:
        return None
    return {"enlem": satir[0], "boylam": satir[1]}


async def poligon_oku(db: AsyncSession, sutun, kayit_id_kosulu) -> list[dict] | None:
    """POLYGON dış halkasını [{enlem, boylam}, ...] olarak okur."""
    y = await db.execute(
        select(func.ST_AsText(func.ST_ExteriorRing(sutun))).where(kayit_id_kosulu)
    )
    satir = y.scalar_one_or_none()
    if not satir:
        return None
    icerik = satir[satir.find("(") + 1: satir.rfind(")")]
    noktalar = []
    for ikili in icerik.split(","):
        parcalar = ikili.strip().split()
        if len(parcalar) == 2:
            noktalar.append({"enlem": float(parcalar[1]), "boylam": float(parcalar[0])})
    return noktalar or None
