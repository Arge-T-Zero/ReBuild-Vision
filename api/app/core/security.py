"""Parola özeti ve JWT — tamamen yerel (docs/karar-kaydi.md K-005)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import ayarlar

ALGORITMA = "HS256"


def parola_ozetle(parola: str) -> str:
    return bcrypt.hashpw(parola.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def parola_dogrula(parola: str, ozet: str) -> bool:
    try:
        return bcrypt.checkpw(parola.encode("utf-8"), ozet.encode("utf-8"))
    except ValueError:
        return False


def jeton_uret(kullanici_id: int, rol: str) -> str:
    a = ayarlar()
    simdi = datetime.now(timezone.utc)
    yuk = {
        "sub": str(kullanici_id),
        "rol": rol,
        "iat": simdi,
        "exp": simdi + timedelta(minutes=a.jwt_gecerlilik_dakika),
    }
    return jwt.encode(yuk, a.jwt_gizli_anahtar, algorithm=ALGORITMA)


def jeton_coz(jeton: str) -> dict | None:
    try:
        return jwt.decode(
            jeton, ayarlar().jwt_gizli_anahtar, algorithms=[ALGORITMA]
        )
    except jwt.PyJWTError:
        return None
