#!/usr/bin/env python3
"""Demo verisi — şartname Madde 10.7.

"Demo ortamlarında anonimleştirilmiş, sentetik veya maskeleme uygulanmış
veri kullanılması esastır."

Gerçek e-posta adresi hiçbir yerde kullanılmaz; tüm hesaplar @demo.local
alan adındadır ve gerçek bir posta kutusuna karşılık gelmez.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

DEPO_KOKU = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPO_KOKU))

from sqlalchemy import select  # noqa: E402

from api.app.core.permissions import OnayDurumu, Rol  # noqa: E402
from api.app.core.security import parola_ozetle  # noqa: E402
from api.app.db import OturumUret  # noqa: E402
from api.app.geo import nokta, poligon  # noqa: E402
from api.app.models import EnkazAlani, Kullanici  # noqa: E402

DEMO_PAROLA = "demo1234"

HESAPLAR = [
    ("yonetici@demo.local", "Demo Yönetici",        Rol.YONETICI),
    ("saha@demo.local",     "Demo Saha Personeli",  Rol.SAHA),
    ("uzman@demo.local",    "Demo Doğrulayıcı Uzman", Rol.UZMAN),
    ("belediye@demo.local", "Demo Belediye Yetkilisi", Rol.BELEDIYE),
    ("afad@demo.local",     "Demo AFAD Yetkilisi",  Rol.AFAD),
    ("yikim@demo.local",    "Demo Yıkım Firması",   Rol.YIKIM),
    ("tesis@demo.local",    "Demo Tesis Operatörü", Rol.TESIS),
]

# Sentetik konum — gerçek bir enkaz sahası değildir.
DEMO_ALAN = {
    "ad": "Demo Sahası A (sentetik)",
    "konum": (40.9862, 40.5219),  # Rize merkez civarı, örnek koordinat
    "sinir": [
        (40.9872, 40.5205), (40.9872, 40.5233),
        (40.9852, 40.5233), (40.9852, 40.5205),
    ],
}


async def main() -> None:
    async with OturumUret() as db:
        eklenen = []
        for eposta, ad, rol in HESAPLAR:
            var = await db.scalar(select(Kullanici).where(Kullanici.eposta == eposta))
            if var:
                continue
            db.add(Kullanici(
                eposta=eposta,
                sifre_hash=parola_ozetle(DEMO_PAROLA),
                ad=ad,
                rol=rol,
                onay_durumu=OnayDurumu.ONAYLANDI,
            ))
            eklenen.append(eposta)
        await db.commit()

        # Rol onay akışını demoda gösterebilmek için onay bekleyen bir hesap.
        bekleyen = "yeni.kullanici@demo.local"
        if not await db.scalar(select(Kullanici).where(Kullanici.eposta == bekleyen)):
            db.add(Kullanici(
                eposta=bekleyen,
                sifre_hash=parola_ozetle(DEMO_PAROLA),
                ad="Demo Onay Bekleyen",
                rol=None,
                onay_durumu=OnayDurumu.BEKLEMEDE,
            ))
            await db.commit()
            eklenen.append(f"{bekleyen} (onay bekliyor)")

        belediye = await db.scalar(
            select(Kullanici).where(Kullanici.eposta == "belediye@demo.local")
        )
        if not await db.scalar(
            select(EnkazAlani).where(EnkazAlani.ad == DEMO_ALAN["ad"])
        ):
            a = EnkazAlani(
                ad=DEMO_ALAN["ad"],
                sorumlu="Demo Belediye",
                olusturan_id=belediye.id,
            )
            a.konum = nokta(*DEMO_ALAN["konum"])
            a.sinir = poligon(DEMO_ALAN["sinir"])
            db.add(a)
            await db.commit()
            eklenen.append(DEMO_ALAN["ad"])

    print("Demo verisi hazır.")
    for e in eklenen:
        print(f"  + {e}")
    if not eklenen:
        print("  (her şey zaten mevcuttu)")
    print(f"\nTüm demo hesaplarının parolası: {DEMO_PAROLA}")
    print("Madde 10.7: bu hesaplar sentetiktir, gerçek posta kutusu yoktur.")


if __name__ == "__main__":
    asyncio.run(main())
