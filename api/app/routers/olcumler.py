"""Saha ölçümü ve miktar hesabı."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.permissions import OLCUM_GIREBILIR
from ..db import oturum
from ..deps import aktif_kullanici, rol_gerekli
from ..models import Kullanici, MiktarHesabi, Olcum, Tespit
from ..schemas import MiktarCikti, OlcumCikti, OlcumIstek
from ..services import miktar as miktar_servisi

router = APIRouter(tags=["ölçüm ve miktar"])


@router.post("/olcum", response_model=OlcumCikti, status_code=status.HTTP_201_CREATED)
async def olcum_ekle(
    istek: OlcumIstek,
    k: Kullanici = Depends(rol_gerekli(OLCUM_GIREBILIR)),
    db: AsyncSession = Depends(oturum),
):
    t = await db.get(Tespit, istek.tespit_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tespit bulunamadı")

    o = Olcum(
        tespit_id=istek.tespit_id,
        tur=istek.tur,
        deger=istek.deger,
        birim=istek.birim,
        yontem=istek.yontem,
        giren_id=k.id,
    )
    db.add(o)
    await db.commit()
    await db.refresh(o)
    return o


@router.get("/olcum/tespit/{tespit_id}", response_model=list[OlcumCikti])
async def olcumler(
    tespit_id: int,
    _: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    y = await db.execute(select(Olcum).where(Olcum.tespit_id == tespit_id))
    return list(y.scalars())


@router.get("/miktar/{tespit_id}", response_model=MiktarCikti)
async def miktar(
    tespit_id: int,
    _: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    """Bir tespitin miktarı.

    ÖLÇÜM YOKSA SAYI DÖNMEZ. `hesaplandi=False` gelir ve `aciklama` alanı
    nedenini söyler. Varsayılan değer, "≈0" veya "hesaplanıyor"
    DÖNDÜRÜLMEZ (ana talimat Bölüm 1.1). Bu, final demosunun 7. adımıdır.
    """
    t = await db.get(Tespit, tespit_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tespit bulunamadı")

    kayitli = await db.scalar(
        select(MiktarHesabi).where(MiktarHesabi.tespit_id == tespit_id)
    )
    if kayitli:
        return MiktarCikti(
            tespit_id=tespit_id,
            hesaplandi=True,
            deger_alt=kayitli.deger_alt,
            deger_ust=kayitli.deger_ust,
            birim=kayitli.birim,
            kullanilan_katsayi=kayitli.kullanilan_katsayi,
            katsayi_kaynagi=kayitli.katsayi_kaynagi,
            yontem=kayitli.yontem,
        )

    y = await db.execute(select(Olcum).where(Olcum.tespit_id == tespit_id))
    # Uzman düzeltmesi varsa katsayı ve malzeme kontrolü DÜZELTİLEN sınıfa
    # göre yapılır — insanın kararı modelinkini geçersiz kılar.
    sonuc = miktar_servisi.hesapla(t.duzeltilen_sinif or t.sinif, list(y.scalars()))

    if not sonuc.hesaplandi:
        # Satır YAZILMAZ. Sıfır yazılmaz, NULL yazılmaz — satır yoktur.
        return MiktarCikti(
            tespit_id=tespit_id,
            hesaplandi=False,
            aciklama=miktar_servisi.NEDEN_METNI.get(sonuc.neden, "Miktar hesaplanmadı"),
        )

    m = MiktarHesabi(
        tespit_id=tespit_id,
        deger_alt=sonuc.deger_alt,
        deger_ust=sonuc.deger_ust,
        birim=sonuc.birim,
        kullanilan_katsayi=sonuc.kullanilan_katsayi,
        katsayi_kaynagi=sonuc.katsayi_kaynagi,
        yontem=sonuc.yontem,
    )
    db.add(m)
    await db.commit()

    return MiktarCikti(
        tespit_id=tespit_id,
        hesaplandi=True,
        deger_alt=sonuc.deger_alt,
        deger_ust=sonuc.deger_ust,
        birim=sonuc.birim,
        kullanilan_katsayi=sonuc.kullanilan_katsayi,
        katsayi_kaynagi=sonuc.katsayi_kaynagi,
        yontem=sonuc.yontem,
    )
