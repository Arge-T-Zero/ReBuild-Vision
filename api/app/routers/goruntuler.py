"""Görüntü yükleme ve model çıkarımı."""
from __future__ import annotations

import io
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import ayarlar
from ..core.permissions import GORUNTU_YUKLEYEBILIR
from ..db import oturum
from ..deps import aktif_kullanici, rol_gerekli
from ..geo import nokta
from ..models import EnkazAlani, Goruntu, Kullanici, Tespit
from ..schemas import GoruntuCikti, TespitCikti, YuklemeCikti
from ..services import model_client
from ..services.queries import gorulebilir_alanlar

router = APIRouter(prefix="/goruntu", tags=["görüntü"])

IZINLI_TURLER = {"image/jpeg", "image/png", "image/webp"}

# ⚠️ YÜKLEME BOYUT SINIRI YOKTU.
#
# Bu uç nokta `list[UploadFile]` alıyor ve her dosyayı `await
# dosya.read()` ile TÜMÜYLE belleğe okuyordu. Dosya sayısı ve boyutu
# sınırsızdı. Tek koruma `docker/nginx.conf` içindeki
# `client_max_body_size 64m` idi ve o da yalnız konteyner yolunda
# geçerli: yerel geliştirme (Vite → uvicorn), Render ve MOBİL UYGULAMA
# doğrudan API'ye gidiyor. Yani tek bir istekle sunucunun belleği
# tüketilebiliyordu.
#
# Sınırlar nginx'inkiyle uyumlu seçildi: dosya başına 32 MB (modern bir
# telefon kamerası ~8-12 MB üretir; 32 MB rahat bir tavan), istek başına
# 10 dosya ve toplam 64 MB. Vekil arkasındayken nginx zaten 64 MB'ta
# keser; bu sınırlar vekilsiz yolları da kapatır.
DOSYA_BASI_SINIR = 32 * 1024 * 1024
ISTEK_BASI_DOSYA_SINIRI = 10
ISTEK_BASI_TOPLAM_SINIR = 64 * 1024 * 1024


def _tespit_ciktisi(t: Tespit) -> TespitCikti:
    return TespitCikti.model_validate(t)


@router.post("/yukle/{alan_id}", response_model=YuklemeCikti,
             status_code=status.HTTP_201_CREATED)
async def yukle(
    alan_id: int,
    dosyalar: list[UploadFile] = File(...),
    enlem: float | None = None,
    boylam: float | None = None,
    k: Kullanici = Depends(rol_gerekli(GORUNTU_YUKLEYEBILIR)),
    db: AsyncSession = Depends(oturum),
):
    """Toplu görüntü yükleme ve model çıkarımı.

    Düşük güvenli tespitler OTOMATİK olarak uzman inceleme kuyruğuna
    düşer; kullanıcının bir şey yapmasına gerek yoktur
    (ana talimat Bölüm 7.3, demo 4. adım).
    """
    alan = (await db.execute(
        gorulebilir_alanlar(k.rol, k.id).where(EnkazAlani.id == alan_id)
    )).scalar_one_or_none()
    if not alan:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enkaz alanı bulunamadı")

    # Sayı denetimi model servisine gitmeden ÖNCE: reddedilecek bir
    # istek için çıkarım servisini hiç meşgul etmemek gerekir.
    if len(dosyalar) > ISTEK_BASI_DOSYA_SINIRI:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"Tek istekte en çok {ISTEK_BASI_DOSYA_SINIRI} görüntü "
            f"yüklenebilir; {len(dosyalar)} gönderildi.",
        )

    saglik = await model_client.saglik()
    sahte = bool(saglik.get("sahte"))

    klasor = ayarlar().yukleme_yolu
    ciktilar: list[GoruntuCikti] = []
    kuyruga_dusen = 0
    toplam_bayt = 0

    for dosya in dosyalar:
        if dosya.content_type not in IZINLI_TURLER:
            raise HTTPException(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                f"Desteklenmeyen dosya türü: {dosya.content_type}",
            )
        icerik = await dosya.read()

        # Boyut denetimi okumadan SONRA: Starlette büyük gövdeyi zaten
        # diske alıyor (SpooledTemporaryFile), yani bellekte tutulan şey
        # bir dosyalık. Asıl korunan, on beş dosyanın aynı anda belleğe
        # açılması ve diskin dolması.
        if len(icerik) > DOSYA_BASI_SINIR:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                f"Görüntü çok büyük ({len(icerik) // (1024 * 1024)} MB): "
                f"{dosya.filename}. Dosya başına sınır "
                f"{DOSYA_BASI_SINIR // (1024 * 1024)} MB.",
            )
        toplam_bayt += len(icerik)
        if toplam_bayt > ISTEK_BASI_TOPLAM_SINIR:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                f"İstek toplamı çok büyük; sınır "
                f"{ISTEK_BASI_TOPLAM_SINIR // (1024 * 1024)} MB.",
            )

        try:
            with Image.open(io.BytesIO(icerik)) as im:
                genislik, yukseklik = im.width, im.height
        except (UnidentifiedImageError, OSError):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Görüntü çözümlenemedi: {dosya.filename}",
            )

        ad = f"{datetime.now(timezone.utc):%Y%m%d}_{secrets.token_hex(8)}"
        uzanti = (dosya.filename or "").rsplit(".", 1)[-1].lower() or "jpg"
        yol = klasor / f"{ad}.{uzanti}"
        yol.write_bytes(icerik)

        g = Goruntu(
            enkaz_alani_id=alan_id,
            dosya_yolu=yol.name,
            cekim_tarihi=datetime.now(timezone.utc),
            cihaz=None,
            genislik=genislik,
            yukseklik=yukseklik,
            yukleyen_id=k.id,
        )
        if enlem is not None and boylam is not None:
            g.konum = nokta(enlem, boylam)
        db.add(g)
        await db.flush()

        sonuc = await model_client.tahmin_et(
            dosya.filename or yol.name, icerik, dosya.content_type
        )

        tespitler: list[Tespit] = []
        for d in sonuc.get("detections", []):
            t = Tespit(
                goruntu_id=g.id,
                sinif=d["class_name"],
                guven_skoru=float(d["confidence"]),
                bbox=d.get("bbox"),
                # Bölüm 4.3: bu alan asla boş bırakılmaz.
                bbox_format=d["bbox_format"],
                inceleme_gerekli=bool(d.get("needs_review")),
            )
            if t.inceleme_gerekli:
                kuyruga_dusen += 1
            db.add(t)
            tespitler.append(t)

        await db.flush()
        ciktilar.append(GoruntuCikti(
            id=g.id,
            enkaz_alani_id=g.enkaz_alani_id,
            dosya_yolu=g.dosya_yolu,
            genislik=g.genislik,
            yukseklik=g.yukseklik,
            cekim_tarihi=g.cekim_tarihi,
            cihaz=g.cihaz,
            yukleyen_id=g.yukleyen_id,
            olusturma_tarihi=datetime.now(timezone.utc),
            tespitler=[_tespit_ciktisi(t) for t in tespitler],
        ))

    await db.commit()
    return YuklemeCikti(
        goruntuler=ciktilar,
        sahte_model_servisi=sahte,
        inceleme_kuyruguna_dusen=kuyruga_dusen,
    )


@router.get("/alan/{alan_id}", response_model=list[GoruntuCikti])
async def alan_goruntuleri(
    alan_id: int,
    k: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    alan = (await db.execute(
        gorulebilir_alanlar(k.rol, k.id).where(EnkazAlani.id == alan_id)
    )).scalar_one_or_none()
    if not alan:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enkaz alanı bulunamadı")

    y = await db.execute(
        select(Goruntu).where(Goruntu.enkaz_alani_id == alan_id)
        .order_by(Goruntu.id.desc())
    )
    cikti = []
    for g in y.scalars():
        ts = await db.execute(select(Tespit).where(Tespit.goruntu_id == g.id))
        cikti.append(GoruntuCikti(
            id=g.id, enkaz_alani_id=g.enkaz_alani_id, dosya_yolu=g.dosya_yolu,
            genislik=g.genislik, yukseklik=g.yukseklik,
            cekim_tarihi=g.cekim_tarihi, cihaz=g.cihaz,
            yukleyen_id=g.yukleyen_id, olusturma_tarihi=g.olusturma_tarihi,
            tespitler=[_tespit_ciktisi(t) for t in ts.scalars()],
        ))
    return cikti
