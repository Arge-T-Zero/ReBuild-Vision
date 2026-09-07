"""Model servisi istemcisi — AGPL SINIRI BURADADIR.

Bu dosya, `api/` ile model çıkarım servisi arasındaki TEK temas noktasıdır.

KURAL: Bu dosya (ve `api/` altındaki hiçbir dosya) `ultralytics` paketini
import ETMEZ. Model ayrı bir süreçte çalışır ve yalnızca HTTP ile çağrılır.
Sahte servis ile gerçek servis arasındaki geçiş tek bir ortam değişkenidir:
`MODEL_SERVICE_URL`.

Gerekçe: docs/lisans-analizi.md Bölüm 3.4
"""
from __future__ import annotations

import time

import httpx

from ..core.config import ayarlar

ZAMAN_ASIMI = 60.0

# --- Sağlık yanıtı önbelleği ---------------------------------------------
#
# ⚠️ BU ÖNBELLEK 06.09.2026'DA BİR CANLI ARIZASINDAN SONRA EKLENDİ.
#
# Yükleme sayfasında şu hata görünüyordu:
#
#   Model servisine ulaşılamadı: Client error '429 Too Many Requests'
#   for url 'https://rebuild-vision-model.onrender.com/health'
#
# Model servisi ÇALIŞIYORDU — aynı adres curl ile
# `{"durum":"calisiyor","sahte":false,"agirlik_yuklendi":true}` dönüyordu.
# Sorun servisin kendisi değil, `/health`'in çok sık çağrılmasıydı:
# `/sistem/durum` kimlik istemez ve arayüz onu HER SAYFA YÜKLEMESİNDE
# çağırır; ayrıca her görüntü yüklemesi önce bir sağlık sorgusu yapar.
# Render'ın ücretsiz katmanı bu trafiği hız sınırına takıyordu.
#
# Önbellek, aynı cevabı saniyeler içinde defalarca sormayı keser.
# Süre bilinçli olarak KISA: model servisi ayağa kalktığında ya da
# düştüğünde arayüz bunu bir dakika içinde öğrenmelidir; sahte/gerçek
# ayrımı gizlenemez (ana talimat Bölüm 9.5), yalnızca gecikebilir.
SAGLIK_ONBELLEK_SANIYE = 45.0

# Hata da önbelleklenir, ama çok daha kısa süreyle: servis geri geldiğinde
# arayüz "model yok" demeye devam etmemeli. Hata önbelleği olmadan,
# servisin düştüğü anlarda her sayfa yüklemesi 5 saniye bekleyip yeni bir
# istek daha üretir ve hız sınırı derinleşir.
SAGLIK_HATA_ONBELLEK_SANIYE = 10.0

# 429 geldiğinde sunucu `Retry-After` verebilir. Ona uyulur ama üst sınırla:
# çok uzun bir değer arayüzü gereksiz yere kör bırakır.
EN_UZUN_BEKLEME_SANIYE = 120.0

_onbellek: tuple[float, dict | None, "ModelServisiHatasi | None"] | None = None


class ModelServisiHatasi(RuntimeError):
    """Model servisine ulaşılamadı ya da servis hata döndü.

    `durum_kodu` ve `hiz_siniri` ALANLARININ VARLIK SEBEBİ:
    "429 Too Many Requests" ile "servis yok" AYNI ŞEY DEĞİLDİR. 429,
    servisin çalıştığını ama şu an cevap vermediğini söyler; arayüzde
    "MODEL YOK" diye göstermek yanlış beyandır. Bunun tersi de yanlış
    olurdu: 429 alındığında "model çalışıyor, sahte değil" demek de
    bilinmeyen bir şeyi bilinir gibi göstermek olurdu. Doğru cevap
    üçüncü bir durumdur: **şu an okunamıyor.**
    """

    def __init__(self, mesaj: str, *, durum_kodu: int | None = None,
                 tekrar_dene_saniye: float | None = None):
        super().__init__(mesaj)
        self.durum_kodu = durum_kodu
        self.tekrar_dene_saniye = tekrar_dene_saniye

    @property
    def hiz_siniri(self) -> bool:
        """429 — servis meşgul/hız sınırı. 'Ağırlık yüklü değil' DEĞİL."""
        return self.durum_kodu == 429


def onbellegi_temizle() -> None:
    """Sağlık önbelleğini boşaltır (testler ve elle tetikleme için)."""
    global _onbellek
    _onbellek = None


def _bekleme_suresi(yanit: httpx.Response) -> float:
    """`Retry-After` başlığını saniyeye çevirir; yoksa varsayılan."""
    ham = yanit.headers.get("retry-after", "")
    try:
        saniye = float(ham)
    except ValueError:
        return SAGLIK_HATA_ONBELLEK_SANIYE
    return max(1.0, min(saniye, EN_UZUN_BEKLEME_SANIYE))


async def saglik() -> dict:
    """Servisin durumu. `sahte: true` ise arayüz uyarı rozeti gösterir.

    Sonuç kısa süreli önbelleklenir; gerekçe dosyanın başındadır.
    """
    global _onbellek

    simdi = time.monotonic()
    if _onbellek is not None:
        son_kullanma, yanit, hata = _onbellek
        if simdi < son_kullanma:
            if hata is not None:
                raise hata
            return yanit

    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            y = await c.get(f"{ayarlar().model_service_url}/health")
            y.raise_for_status()
            sonuc = y.json()
    except httpx.HTTPStatusError as e:
        bekleme = (_bekleme_suresi(e.response)
                   if e.response.status_code == 429
                   else SAGLIK_HATA_ONBELLEK_SANIYE)
        hata = ModelServisiHatasi(
            f"Model servisine ulaşılamadı: {e}",
            durum_kodu=e.response.status_code,
            tekrar_dene_saniye=bekleme,
        )
        _onbellek = (simdi + bekleme, None, hata)
        raise hata from e
    except httpx.HTTPError as e:
        hata = ModelServisiHatasi(f"Model servisine ulaşılamadı: {e}")
        _onbellek = (simdi + SAGLIK_HATA_ONBELLEK_SANIYE, None, hata)
        raise hata from e

    _onbellek = (simdi + SAGLIK_ONBELLEK_SANIYE, sonuc, None)
    return sonuc


async def tahmin_et(dosya_adi: str, icerik: bytes, mime: str) -> dict:
    """Görüntüyü model servisine gönderir ve ham tahmin çıktısını döner.

    Dönen çıktı 'ön tahmin'dir. Doğrulanmadan miktar, ekonomik değer veya
    yönlendirme hesaplarına GİRMEZ (ana talimat Bölüm 1.4).

    Tahmin ÖNBELLEKLENMEZ: her görüntü ayrı bir istektir ve sonuç
    saklanamaz.
    """
    try:
        async with httpx.AsyncClient(timeout=ZAMAN_ASIMI) as c:
            y = await c.post(
                f"{ayarlar().model_service_url}/predict",
                files={"file": (dosya_adi, icerik, mime)},
            )
            y.raise_for_status()
            return y.json()
    except httpx.HTTPStatusError as e:
        raise ModelServisiHatasi(
            f"Tahmin isteği başarısız: {e}",
            durum_kodu=e.response.status_code,
            tekrar_dene_saniye=(_bekleme_suresi(e.response)
                                if e.response.status_code == 429 else None),
        ) from e
    except httpx.HTTPError as e:
        raise ModelServisiHatasi(f"Tahmin isteği başarısız: {e}") from e
