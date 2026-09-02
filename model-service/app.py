"""GERÇEK model servisi — YOLO11 çıkarımı.

⚠️ AGPL-3.0 SINIRI BU DİZİNDEDİR.

`ultralytics` AGPL-3.0 lisanslıdır ve `api/` içine GİREMEZ. Bu servis
ayrı bir süreçte çalışır; `api/` ona yalnızca HTTP ile erişir
(`api/app/services/model_client.py`). Sınır bir yorumla değil,
`tests/test_agpl_siniri.py` içindeki beş testle korunur.
Gerekçe: docs/lisans-analizi.md Bölüm 3.4.

SÖZLEŞME
`model-mock/app.py` ile BİREBİR aynı yanıt biçimini üretir. İki servis
arasında geçiş tek bir ortam değişkenidir (`MODEL_SERVICE_URL`); alan
adları ayrışırsa arayüz sessizce bozulur. Sözleşme
`tests/test_model_servisi_sozlesmesi.py` ile doğrulanır.

AĞIRLIK YOKSA NE OLUR
Servis sahte veri ÜRETMEZ ve sessizce mock'a düşmez. `/health`
`agirlik_yuklendi: false` döner, `/predict` 503 verir. Bu bilinçlidir:
bu projede en pahalı arıza, uydurma bir çıktının gerçek sanılmasıdır
(ana talimat Bölüm 9.5).
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

DEPO_KOKU = Path(__file__).resolve().parent.parent
SINIFLAR = json.loads((DEPO_KOKU / "siniflar.json").read_text(encoding="utf-8"))

# Mock ile aynı olmak ZORUNDA: arayüz kutuları bu biçime göre çiziyor
# (web/src/bilesenler/TespitKutulari.tsx yalnızca bu değeri kabul eder).
BBOX_FORMAT = "pixel_absolute_original"

# Uzman incelemesi eşiği.
#
# ⚠️ BU HÂLÂ ÖLÇÜLMÜŞ BİR DEĞER DEĞİL — ama sebebi değişti.
#
# Eski gerekçe "model henüz ölçülmedi" idi; model 01.09.2026'da eğitildi
# ve ölçüldü (results/model-metrikleri.md). Yine de eşik türetilemiyor:
# eşiği doğru seçmek için precision ve recall'un GÜVENE GÖRE değişimi
# gerekir, elimizdeki `results/egitim/metrikler.json` ise her sınıf için
# tek bir çalışma noktası veriyor. Eğriler yalnızca PNG olarak var
# (`gorseller/*_BoxF1_curve.png`); bir görselden sayı okumak ölçüm
# değildir ve bu depoda ölçülmemiş sayı yazılmaz (Bölüm 14).
#
# Türetmek için gereken: eğitim ortamında `model.val()` çıktısının ham
# p/r/f1-conf dizileri (ya da eşiği tarayan bir koşu). O gelene kadar
# 0,50 bir mühendislik varsayımıdır ve ortam değişkeniyle
# değiştirilebilir tutuluyor ki kod değişikliği gerekmesin.
#
# Pratik etkisi kayıtlıdır: modelin genel precision'ı val'de 0,53,
# yani bu eşiğin üstünde kalan tespitlerin azımsanmayacak kısmı da
# yanlıştır. Sistemin cevabı eşiği yükseltmek değil, DOĞRULAMA
# KAPISIDIR: doğrulanmamış hiçbir tespit miktara, haritaya ya da rapora
# girmez (Bölüm 1.4).
INCELEME_ESIGI = float(os.getenv("INCELEME_ESIGI", "0.50"))

AGIRLIK_YOLU = os.getenv("MODEL_AGIRLIK", str(DEPO_KOKU / "model-service/agirliklar/best.pt"))

app = FastAPI(
    title="ReBuild Vision — model servisi",
    description="YOLO11 çıkarımı. Çıktılar ÖN TAHMİNDİR.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class _Model:
    """Ağırlığı bir kez yükler ve bellekte tutar.

    Yükleme uygulama açılışında DEĞİL, ilk istekte yapılır: ağırlık
    dosyası yoksa servis yine de ayağa kalkmalı ve `/health` üzerinden
    durumu söyleyebilmelidir. Açılışta çökerse `api/` yalnızca "model
    servisine ulaşılamıyor" der ve nedeni hiçbir yerde görünmez.
    """

    def __init__(self) -> None:
        self._model = None
        self._hata: str | None = None
        self._denendi = False

    @property
    def hazir(self) -> bool:
        self._yukle()
        return self._model is not None

    @property
    def hata(self) -> str | None:
        self._yukle()
        return self._hata

    def _yukle(self) -> None:
        if self._denendi:
            return
        self._denendi = True

        yol = Path(AGIRLIK_YOLU)
        if not yol.is_file():
            self._hata = (
                f"Ağırlık dosyası bulunamadı: {yol}. "
                "MODEL_AGIRLIK ortam değişkeniyle yol verilebilir."
            )
            return
        try:
            # İçe aktarma FONKSİYON İÇİNDE: ultralytics kurulu değilse
            # servis yine de ayağa kalkar ve nedenini `/health` ile söyler.
            from ultralytics import YOLO  # noqa: PLC0415

            self._model = YOLO(str(yol))
        except Exception as e:  # noqa: BLE001 — nedeni ekranda görünmeli
            self._hata = f"Ağırlık yüklenemedi: {type(e).__name__}: {e}"

    def isim(self) -> str:
        return Path(AGIRLIK_YOLU).stem if self.hazir else "yüklenmedi"

    def tahmin(self, icerik: bytes) -> list[dict]:
        assert self._model is not None
        with Image.open(io.BytesIO(icerik)) as im:
            goruntu = im.convert("RGB")
            sonuc = self._model.predict(goruntu, verbose=False)[0]

        tespitler: list[dict] = []
        kutular = getattr(sonuc, "boxes", None)
        if kutular is None:
            return tespitler

        for kutu in kutular:
            sinif_id = int(kutu.cls.item())
            guven = float(kutu.conf.item())
            x1, y1, x2, y2 = (float(v) for v in kutu.xyxy[0].tolist())

            tespitler.append({
                "class_id": sinif_id,
                # Sınıf adı MODELDEN değil, siniflar.json'dan alınır.
                # Model kendi `names` sözlüğünü taşır; eğitimdeki sıra
                # kayarsa arayüz yanlış malzeme gösterir. Tek kaynak
                # siniflar.json'dur ve uyuşmazlık aşağıda yakalanır.
                "class_name": _sinif_adi(sinif_id),
                # Güven skoru YUVARLANMAZ (ana talimat Bölüm 9.2).
                "confidence": guven,
                "bbox": {
                    "x": int(round(x1)),
                    "y": int(round(y1)),
                    "w": int(round(x2 - x1)),
                    "h": int(round(y2 - y1)),
                },
                "bbox_format": BBOX_FORMAT,
                "needs_review": guven < INCELEME_ESIGI,
            })
        return tespitler


_ID_ADI = {s["id"]: s["ad"] for s in SINIFLAR["siniflar"]}


def _sinif_adi(sinif_id: int) -> str:
    """Sınıf id'sini `siniflar.json`'daki ada çevirir.

    ⚠️ BİLİNMEYEN ID SESSİZCE GEÇİLMEZ. Model, `siniflar.json`'da
    olmayan bir id dönerse eğitim veri setinin sınıf sırası bu depoyla
    uyuşmuyor demektir — ve bu, arayüzün "ahşap" yerine "metal"
    göstermesi anlamına gelir. Hata vermeden geçilirse kimse fark etmez.
    """
    ad = _ID_ADI.get(sinif_id)
    if ad is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Model, siniflar.json'da bulunmayan bir sınıf id'si döndü: "
            f"{sinif_id}. Beklenen id aralığı 0-{max(_ID_ADI)}. "
            f"Eğitimdeki data.yaml sınıf sırası siniflar.json ile "
            f"eşleşmiyor olabilir.",
        )
    return ad


model = _Model()


@app.get("/health")
def health() -> dict:
    hazir = model.hazir
    return {
        "durum": "calisiyor" if hazir else "agirlik_yok",
        # Arayüzdeki "SAHTE MODEL SERVİSİ" rozeti buna bakar. Gerçek
        # serviste her zaman False — sahte servisle karıştırılamaz.
        "sahte": False,
        "agirlik_yuklendi": hazir,
        "model": model.isim(),
        # AGPL-3.0 beyanı gizlenmez; jüri lisans sorusunu buradan da
        # doğrulayabilmelidir (docs/lisans-analizi.md Bölüm 3).
        "model_license": "AGPL-3.0 (ultralytics)",
        "sinif_sayisi": len(SINIFLAR["siniflar"]),
        "review_threshold": INCELEME_ESIGI,
        **({"hata": model.hata} if not hazir and model.hata else {}),
    }


@app.get("/siniflar")
def siniflar() -> dict:
    return SINIFLAR


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict:
    if not model.hazir:
        # Ağırlık yoksa UYDURMA ÜRETİLMEZ. Sahte servise düşmek de
        # seçenek değildir: çağıran taraf gerçek model çalıştığını sanır.
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            model.hata or "Model ağırlığı yüklü değil; çıkarım yapılamaz.",
        )

    icerik = await file.read()
    try:
        with Image.open(io.BytesIO(icerik)) as im:
            g, y = im.width, im.height
    except (UnidentifiedImageError, OSError) as e:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Görüntü çözülemedi: {e}",
        ) from e

    return {
        "sahte": False,
        "image_id": hashlib.sha256(icerik).hexdigest()[:12],
        "image_width": g,
        "image_height": y,
        "processed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": model.isim(),
        "model_license": "AGPL-3.0 (ultralytics)",
        "review_threshold": INCELEME_ESIGI,
        "detections": model.tahmin(icerik),
    }
