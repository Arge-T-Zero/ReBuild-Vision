"""Uzman doğrulama ve inceleme kuyruğu."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import siniflar
from ..core.permissions import DOGRULAYABILIR
from ..db import oturum
from ..deps import aktif_kullanici
from ..models import DogrulamaDurumu, Kullanici, Tespit
from ..schemas import DogrulamaIstek, TespitCikti
from ..deps import rol_gerekli

router = APIRouter(prefix="/tespit", tags=["doğrulama"])


@router.get("/inceleme-kuyrugu", response_model=list[TespitCikti])
async def inceleme_kuyrugu(
    _: Kullanici = Depends(rol_gerekli(DOGRULAYABILIR)),
    db: AsyncSession = Depends(oturum),
):
    """Uzman incelemesi bekleyen tespitler.

    Düşük güvenli kayıtlar buraya OTOMATİK düşer (ana talimat Bölüm 7.3).
    Kullanıcının kuyruğa ekleme yapması gerekmez.
    """
    y = await db.execute(
        select(Tespit)
        .where(Tespit.inceleme_gerekli.is_(True))
        .where(Tespit.dogrulama_durumu == DogrulamaDurumu.BEKLEMEDE)
        .order_by(Tespit.guven_skoru.asc())
    )
    return [TespitCikti.model_validate(t) for t in y.scalars()]


@router.post("/{tespit_id}/dogrula", response_model=TespitCikti)
async def dogrula(
    tespit_id: int,
    istek: DogrulamaIstek,
    k: Kullanici = Depends(rol_gerekli(DOGRULAYABILIR)),
    db: AsyncSession = Depends(oturum),
):
    """Onayla / düzelt / belirsiz işaretle.

    'reddet' aksiyonu yoktur (docs/karar-kaydi.md K-004). Bir tespiti
    reddetmek kaydın bilgi değerini yok eder; 'belirsiz' kaydı izlenebilir
    tutarak ikinci incelemeye açık bırakır.

    Değişiklik islem_gecmisi'ne otomatik düşer (Rapor Bölüm 6).
    """
    t = await db.get(Tespit, tespit_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tespit bulunamadı")

    if istek.durum == DogrulamaDurumu.BEKLEMEDE:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Doğrulama sonucu 'beklemede' olamaz",
        )

    if istek.durum == DogrulamaDurumu.DUZELTILDI:
        if not istek.duzeltilen_sinif:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Düzeltme için yeni sınıf belirtilmelidir",
            )
        gecerli = {s["ad"] for s in siniflar()["siniflar"]}
        if istek.duzeltilen_sinif not in gecerli:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Geçersiz sınıf: {istek.duzeltilen_sinif}",
            )
        # Eski sınıf silinmez; islem_gecmisi'nde eski/yeni birlikte durur.
        t.duzeltilen_sinif = istek.duzeltilen_sinif

    t.dogrulama_durumu = istek.durum
    t.dogrulayan_id = k.id
    t.dogrulama_tarihi = datetime.now(timezone.utc)

    # İnceleme tamamlandı; kayıt kuyruktan çıkar.
    t.inceleme_gerekli = False

    await db.commit()
    await db.refresh(t)
    return TespitCikti.model_validate(t)


@router.get("/{tespit_id}", response_model=TespitCikti)
async def getir(
    tespit_id: int,
    _: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    t = await db.get(Tespit, tespit_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tespit bulunamadı")
    return TespitCikti.model_validate(t)
