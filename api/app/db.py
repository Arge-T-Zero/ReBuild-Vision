"""Veri tabanı oturumu — SQLAlchemy 2.0 async + asyncpg."""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .core.config import ayarlar


class Temel(DeclarativeBase):
    pass


motor = create_async_engine(ayarlar().veritabani_url, echo=False, future=True)
OturumUret = async_sessionmaker(motor, expire_on_commit=False, class_=AsyncSession)


async def oturum() -> AsyncIterator[AsyncSession]:
    async with OturumUret() as s:
        yield s
