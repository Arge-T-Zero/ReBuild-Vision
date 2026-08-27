"""Enkaz alanları."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.permissions import SAHA_OLUSTURABILIR
from ..db import oturum
from ..deps import aktif_kullanici, rol_gerekli
from ..geo import nokta, nokta_oku, poligon, poligon_oku
from ..models import EnkazAlani, Goruntu, Kullanici
from ..schemas import EnkazAlaniCikti, EnkazAlaniIstek
from ..services.queries import gorulebilir_alanlar

router = APIRouter(prefix="/enkaz-alani", tags=["enkaz alanı"])


async def _ciktiya_cevir(db: AsyncSession, a: EnkazAlani) -> EnkazAlaniCikti:
    sayi = await db.scalar(
        select(func.count(Goruntu.id)).where(Goruntu.enkaz_alani_id == a.id)
    )
    return EnkazAlaniCikti(
        id=a.id,
        ad=a.ad,
        konum=await nokta_oku(db, EnkazAlani.konum, EnkazAlani.id == a.id),
        sinir=await poligon_oku(db, EnkazAlani.sinir, EnkazAlani.id == a.id),
        erisim_durumu=a.erisim_durumu,
        sorumlu=a.sorumlu,
        inceleme_tarihi=a.inceleme_tarihi,
        olusturan_id=a.olusturan_id,
        olusturma_tarihi=a.olusturma_tarihi,
        goruntu_sayisi=sayi or 0,
    )


@router.post("", response_model=EnkazAlaniCikti, status_code=status.HTTP_201_CREATED)
async def olustur(
    istek: EnkazAlaniIstek,
    k: Kullanici = Depends(rol_gerekli(SAHA_OLUSTURABILIR)),
    db: AsyncSession = Depends(oturum),
):
    a = EnkazAlani(
        ad=istek.ad,
        erisim_durumu=istek.erisim_durumu,
        sorumlu=istek.sorumlu,
        inceleme_tarihi=istek.inceleme_tarihi,
        olusturan_id=k.id,
    )
    if istek.konum:
        a.konum = nokta(istek.konum.enlem, istek.konum.boylam)
    if istek.sinir:
        a.sinir = poligon([(n.enlem, n.boylam) for n in istek.sinir])

    db.add(a)
    await db.commit()
    await db.refresh(a)
    return await _ciktiya_cevir(db, a)


@router.get("", response_model=list[EnkazAlaniCikti])
async def listele(
    k: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    """Rolün görebildiği alanlar. Filtre veri katmanındadır (Bölüm 5)."""
    y = await db.execute(gorulebilir_alanlar(k.rol, k.id).order_by(EnkazAlani.id.desc()))
    return [await _ciktiya_cevir(db, a) for a in y.scalars()]


@router.get("/{alan_id}", response_model=EnkazAlaniCikti)
async def getir(
    alan_id: int,
    k: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    sorgu = gorulebilir_alanlar(k.rol, k.id).where(EnkazAlani.id == alan_id)
    a = (await db.execute(sorgu)).scalar_one_or_none()
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enkaz alanı bulunamadı")
    return await _ciktiya_cevir(db, a)
