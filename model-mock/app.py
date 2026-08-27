"""SAHTE model servisi.

Gerçek YOLO11 servisinin yerine geçen, gerçek bir HTTP uç noktası.
Sahtelik hiçbir yerde gizlenmez (ana talimat Bölüm 9.5).
"""
from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
import io

MODEL_ADI = "yolo11-rebuild-SAHTE"
BBOX_FORMAT = "pixel_absolute_original"
INCELEME_ESIGI = 0.50  # ölçülmüş değer değil, yer tutucu (results/model-metrikleri.md)

SINIFLAR_YOLU = Path(__file__).resolve().parent.parent / "siniflar.json"
SINIFLAR = json.loads(SINIFLAR_YOLU.read_text(encoding="utf-8"))

app = FastAPI(
    title="ReBuild Vision — SAHTE model servisi",
    description="Gerçek model değildir. Çıktılar uydurmadır.",
    version="0.1.0-SAHTE",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "durum": "calisiyor",
        "sahte": True,
        "model": MODEL_ADI,
        "model_license": "YOK - SAHTE SERVIS",
        "uyari": "Bu servis gercek bir model calistirmaz. Ciktilar uydurmadir.",
        "sinif_sayisi": len(SINIFLAR["siniflar"]),
    }


@app.get("/siniflar")
def siniflar() -> dict:
    return SINIFLAR


def _boyut_oku(icerik: bytes) -> tuple[int, int]:
    try:
        with Image.open(io.BytesIO(icerik)) as im:
            return im.width, im.height
    except (UnidentifiedImageError, OSError):
        # Görüntü çözülemezse sabit bir boyut varsayılır; sahte serviste
        # akışı durdurmaya gerek yok.
        return 4000, 3000


def _tespit_uret(rnd: random.Random, g: int, y: int, sinif: dict,
                 dusuk_guven: bool) -> dict:
    if dusuk_guven:
        guven = round(rnd.uniform(0.28, INCELEME_ESIGI - 0.01), 2)
    else:
        guven = round(rnd.uniform(INCELEME_ESIGI + 0.05, 0.97), 2)

    w = rnd.randint(int(g * 0.05), int(g * 0.30))
    h = rnd.randint(int(y * 0.05), int(y * 0.30))
    x = rnd.randint(0, max(0, g - w))
    yy = rnd.randint(0, max(0, y - h))

    return {
        "class_id": sinif["id"],
        "class_name": sinif["ad"],
        "confidence": guven,
        "bbox": {"x": x, "y": yy, "w": w, "h": h},
        "bbox_format": BBOX_FORMAT,
        "needs_review": guven < INCELEME_ESIGI,
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict:
    icerik = await file.read()
    ozet = hashlib.sha256(icerik).hexdigest()
    rnd = random.Random(int(ozet[:16], 16))  # aynı görüntü → aynı sonuç

    g, y = _boyut_oku(icerik)
    havuz = SINIFLAR["siniflar"]

    # En az biri düşük güvenli olacak biçimde 3-6 tespit üretilir.
    adet = rnd.randint(3, 6)
    secimler = [rnd.choice(havuz) for _ in range(adet)]
    dusuk_indeks = rnd.randrange(adet)

    tespitler = [
        _tespit_uret(rnd, g, y, sinif, dusuk_guven=(i == dusuk_indeks))
        for i, sinif in enumerate(secimler)
    ]

    return {
        "sahte": True,
        "uyari": "SAHTE SERVIS - bu sonuclar gercek bir modelden gelmemistir",
        "image_id": ozet[:12],
        "image_width": g,
        "image_height": y,
        "processed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": MODEL_ADI,
        "model_license": "YOK - SAHTE SERVIS",
        "review_threshold": INCELEME_ESIGI,
        "detections": tespitler,
    }
