"""Çevrimdışı eşitleme — mobil uygulamanın kuyruğunu boşalttığı uç nokta.

Rapor Bölüm 12 (risk tablosu):

    "Mobil kayıtların cihazda şifreli olarak geçici biçimde saklanması ve
     bağlantı sağlandığında eşitlenmesi."

Saha personeli çoğu zaman bağlantısız çalışır. Kayıtlar cihazda şifreli
bir kuyrukta birikir; bağlantı gelince buradan toplu gönderilir.

TASARIM KARARLARI

1. **Aynı kayıt iki kez gönderilirse iki kez yazılmaz.** Mobil taraf her
   kayda cihazda üretilen bir `yerel_kimlik` verir. Ağ koptuğunda
   istemci isteği tekrarlar ama sonucu bilemez; sunucu bu kimliğe bakıp
   yinelenen kaydı atlar. Bu olmadan tek bir zayıf bağlantı ölçümleri
   ikiye katlardı.

2. **Kısmi başarı normaldir.** Yirmi kayıttan üçü geçersizse diğer on
   yedisi yazılır; istemci yalnızca başarısızları kuyruğunda tutar.
   Tümünü reddetmek, saha personelini bağlantısı olmayan bir yerde
   çözemeyeceği bir hatayla baş başa bırakırdı.

3. **Bölüm 1'in kuralları burada da geçerlidir.** Toplu giriş, tekil
   girişin doğrulamalarını atlamaz.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.permissions import OLCUM_GIREBILIR
from ..db import oturum
from ..deps import rol_gerekli
from ..models import Kullanici, Olcum, Tespit
from ..schemas import (
    EsitlemeIstek, EsitlemeSonucu, EsitlemeSatirSonucu, olcum_kusuru,
)

router = APIRouter(prefix="/esitleme", tags=["çevrimdışı eşitleme"])


@router.post("/olcum", response_model=EsitlemeSonucu,
             status_code=status.HTTP_200_OK)
async def olcum_esitle(
    istek: EsitlemeIstek,
    k: Kullanici = Depends(rol_gerekli(OLCUM_GIREBILIR)),
    db: AsyncSession = Depends(oturum),
):
    """Çevrimdışı biriken ölçümleri toplu olarak yazar.

    Yanıt her satır için ayrı sonuç döner; istemci yalnızca `durum` alanı
    `hata` olanları kuyruğunda tutar, gerisini siler.
    """
    # Bu cihazdan daha önce gelmiş kayıtlar — yinelenenleri ayıklamak için.
    gelen_kimlikler = [s.yerel_kimlik for s in istek.kayitlar]
    var_olanlar = set((await db.execute(
        select(Olcum.yerel_kimlik).where(Olcum.yerel_kimlik.in_(gelen_kimlikler))
    )).scalars())

    sonuclar: list[EsitlemeSatirSonucu] = []
    yazilacak: list[Olcum] = []

    for satir in istek.kayitlar:
        if satir.yerel_kimlik in var_olanlar:
            sonuclar.append(EsitlemeSatirSonucu(
                yerel_kimlik=satir.yerel_kimlik,
                durum="yinelenen",
                aciklama="Bu kayıt daha önce eşitlenmiş; tekrar yazılmadı.",
            ))
            continue

        # Birim/üst sınır kuralı burada, SATIR DÜZEYİNDE uygulanır.
        # Şemada uygulanırsa (eskiden öyleydi) tek bozuk satır bütün
        # partiyi 422 ile düşürür ve sağlam ölçümler de yazılmaz —
        # gerekçenin tamamı schemas.EsitlemeSatiri docstring'inde.
        kusur = olcum_kusuru(satir.tur, satir.birim, satir.deger)
        if kusur:
            sonuclar.append(EsitlemeSatirSonucu(
                yerel_kimlik=satir.yerel_kimlik,
                durum="hata",
                aciklama=kusur,
            ))
            continue

        tespit = await db.get(Tespit, satir.tespit_id)
        if not tespit:
            sonuclar.append(EsitlemeSatirSonucu(
                yerel_kimlik=satir.yerel_kimlik,
                durum="hata",
                aciklama=f"Tespit bulunamadı (id {satir.tespit_id}).",
            ))
            continue

        yazilacak.append(Olcum(
            tespit_id=satir.tespit_id,
            tur=satir.tur,
            deger=satir.deger,
            birim=satir.birim,
            yontem=satir.yontem,
            giren_id=k.id,
            yerel_kimlik=satir.yerel_kimlik,
        ))
        sonuclar.append(EsitlemeSatirSonucu(
            yerel_kimlik=satir.yerel_kimlik, durum="yazildi",
        ))

    if yazilacak:
        db.add_all(yazilacak)
        await db.commit()

    return EsitlemeSonucu(
        yazilan=sum(1 for s in sonuclar if s.durum == "yazildi"),
        yinelenen=sum(1 for s in sonuclar if s.durum == "yinelenen"),
        hatali=sum(1 for s in sonuclar if s.durum == "hata"),
        satirlar=sonuclar,
    )
