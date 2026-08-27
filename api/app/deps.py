"""FastAPI bağımlılıkları — kimlik ve yetki.

Yetki kontrolü API katmanındadır. Arayüzde gizleme yeterli değildir
(ana talimat Bölüm 5).
"""
from __future__ import annotations

from collections.abc import Callable, Iterable

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .core.permissions import OnayDurumu, Rol
from .core.security import jeton_coz
from .db import oturum
from .models import Kullanici
from .services.denetim import aktif_kullanici_id


async def aktif_kullanici(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(oturum),
) -> Kullanici:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Oturum açılmamış")

    yuk = jeton_coz(authorization.split(" ", 1)[1])
    if not yuk:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Jeton geçersiz veya süresi dolmuş")

    k = await db.get(Kullanici, int(yuk["sub"]))
    if not k:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Kullanıcı bulunamadı")

    if k.onay_durumu != OnayDurumu.ONAYLANDI:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Hesabınız henüz yönetici tarafından onaylanmadı",
        )

    # İşlem geçmişi kayıtları bu kullanıcıya bağlanır.
    aktif_kullanici_id.set(k.id)
    return k


def rol_gerekli(roller: Iterable[Rol]) -> Callable:
    """Belirtilen rollerden birine sahip olmayı zorunlu kılar."""
    izinli = set(roller)

    async def kontrol(k: Kullanici = Depends(aktif_kullanici)) -> Kullanici:
        if k.rol not in izinli:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Bu işlem için yetkiniz yok",
            )
        return k

    return kontrol
