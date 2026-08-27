"""Model servisi istemcisi — AGPL SINIRI BURADADIR.

Bu dosya, `api/` ile model çıkarım servisi arasındaki TEK temas noktasıdır.

KURAL: Bu dosya (ve `api/` altındaki hiçbir dosya) `ultralytics` paketini
import ETMEZ. Model ayrı bir süreçte çalışır ve yalnızca HTTP ile çağrılır.
Sahte servis ile gerçek servis arasındaki geçiş tek bir ortam değişkenidir:
`MODEL_SERVICE_URL`.

Gerekçe: docs/lisans-analizi.md Bölüm 3.4
"""
from __future__ import annotations

import httpx

from ..core.config import ayarlar

ZAMAN_ASIMI = 60.0


class ModelServisiHatasi(RuntimeError):
    pass


async def saglik() -> dict:
    """Servisin durumu. `sahte: true` ise arayüz uyarı rozeti gösterir."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            y = await c.get(f"{ayarlar().model_service_url}/health")
            y.raise_for_status()
            return y.json()
    except httpx.HTTPError as e:
        raise ModelServisiHatasi(f"Model servisine ulaşılamadı: {e}") from e


async def tahmin_et(dosya_adi: str, icerik: bytes, mime: str) -> dict:
    """Görüntüyü model servisine gönderir ve ham tahmin çıktısını döner.

    Dönen çıktı 'ön tahmin'dir. Doğrulanmadan miktar, ekonomik değer veya
    yönlendirme hesaplarına GİRMEZ (ana talimat Bölüm 1.4).
    """
    try:
        async with httpx.AsyncClient(timeout=ZAMAN_ASIMI) as c:
            y = await c.post(
                f"{ayarlar().model_service_url}/predict",
                files={"file": (dosya_adi, icerik, mime)},
            )
            y.raise_for_status()
            return y.json()
    except httpx.HTTPError as e:
        raise ModelServisiHatasi(f"Tahmin isteği başarısız: {e}") from e
