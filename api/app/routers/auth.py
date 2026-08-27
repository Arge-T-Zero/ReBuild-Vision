"""Kimlik doğrulama — kayıt, giriş, rol atama."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.permissions import ROL_ATAYABILIR, OnayDurumu
from ..core.security import jeton_uret, parola_dogrula, parola_ozetle
from ..db import oturum
from ..deps import aktif_kullanici, rol_gerekli
from ..models import Kullanici
from ..schemas import (
    GirisIstek,
    JetonCikti,
    KayitIstek,
    KullaniciCikti,
    RolAtaIstek,
)

router = APIRouter(prefix="/auth", tags=["kimlik"])


@router.post("/kayit", response_model=KullaniciCikti,
             status_code=status.HTTP_201_CREATED)
async def kayit(istek: KayitIstek, db: AsyncSession = Depends(oturum)):
    """Yeni kullanıcı kaydı.

    Kullanıcı kendi rolünü SEÇEMEZ (Brief Bölüm 3). Kayıt
    onay_durumu=beklemede ve rol=None ile başlar; rolü yönetici atar.
    Bu, kamu sistemi mantığının göstergesidir.
    """
    var = await db.scalar(select(Kullanici).where(Kullanici.eposta == istek.eposta))
    if var:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bu e-posta zaten kayıtlı")

    k = Kullanici(
        eposta=istek.eposta,
        sifre_hash=parola_ozetle(istek.parola),
        ad=istek.ad,
        rol=None,
        onay_durumu=OnayDurumu.BEKLEMEDE,
    )
    db.add(k)
    await db.commit()
    await db.refresh(k)
    return k


@router.post("/giris", response_model=JetonCikti)
async def giris(istek: GirisIstek, db: AsyncSession = Depends(oturum)):
    k = await db.scalar(select(Kullanici).where(Kullanici.eposta == istek.eposta))
    if not k or not parola_dogrula(istek.parola, k.sifre_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-posta veya parola hatalı")

    if k.onay_durumu != OnayDurumu.ONAYLANDI:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Hesabınız henüz yönetici tarafından onaylanmadı. "
            "Rol atandıktan sonra giriş yapabilirsiniz.",
        )

    return JetonCikti(jeton=jeton_uret(k.id, k.rol.value), kullanici=k)


@router.get("/ben", response_model=KullaniciCikti)
async def ben(k: Kullanici = Depends(aktif_kullanici)):
    return k


@router.get("/bekleyenler", response_model=list[KullaniciCikti])
async def bekleyenler(
    _: Kullanici = Depends(rol_gerekli(ROL_ATAYABILIR)),
    db: AsyncSession = Depends(oturum),
):
    """Rol ataması bekleyen kullanıcılar (yalnızca yönetici)."""
    y = await db.execute(
        select(Kullanici).where(Kullanici.onay_durumu == OnayDurumu.BEKLEMEDE)
    )
    return list(y.scalars())


@router.post("/kullanici/{kullanici_id}/rol", response_model=KullaniciCikti)
async def rol_ata(
    kullanici_id: int,
    istek: RolAtaIstek,
    _: Kullanici = Depends(rol_gerekli(ROL_ATAYABILIR)),
    db: AsyncSession = Depends(oturum),
):
    """Rol atama — yalnızca yönetici. İşlem geçmişine otomatik düşer."""
    k = await db.get(Kullanici, kullanici_id)
    if not k:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Kullanıcı bulunamadı")
    k.rol = istek.rol
    k.onay_durumu = istek.onay_durumu
    await db.commit()
    await db.refresh(k)
    return k
