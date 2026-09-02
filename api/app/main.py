"""ReBuild Vision — API girişi."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import ayarlar
from .routers import (
    alanlar, auth, dogrulama, esitleme, goruntuler,
    ogc, olcumler, rapor,
    sistem, tehlikeli,
)
from .services import denetim  # noqa: F401 — olay dinleyicisini kaydeder

app = FastAPI(
    title="ReBuild Vision API",
    description=(
        "Afet sonrası enkaz malzemelerinin görüntü tabanlı ön "
        "sınıflandırması. Model çıktıları ÖN TAHMİNDİR; nihai kararı "
        "yetkili kurum ve uzmanlar verir."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ayarlar().kaynak_listesi,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(alanlar.router)
app.include_router(goruntuler.router)
app.include_router(dogrulama.router)
app.include_router(olcumler.router)
app.include_router(esitleme.router)
app.include_router(tehlikeli.router)
app.include_router(rapor.router)
app.include_router(ogc.router)
app.include_router(sistem.router)

app.mount(
    "/dosya",
    StaticFiles(directory=str(ayarlar().yukleme_yolu)),
    name="dosya",
)


@app.get("/", tags=["sistem"])
async def kok():
    return {
        "ad": "ReBuild Vision API",
        "surum": "0.1.0",
        "dokumantasyon": "/docs",
        "uyari": (
            "Model çıktıları ön tahmindir. Sistem tehlikeli madde teşhisi "
            "yapmaz ve enkaz altı içeriği değerlendirmez."
        ),
    }
