"""Ortam yapılandırması."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEPO_KOKU = Path(__file__).resolve().parents[3]

# Bu değer depoda açıkça yazılıdır ve herkese açıktır. Üretimde kullanılması
# engellenir (bkz. Ayarlar.model_post_init).
GUVENSIZ_VARSAYILAN_ANAHTAR = "gelistirme-icin-guvensiz-anahtar-DEGISTIRIN"


class Ayarlar(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DEPO_KOKU / ".env", extra="ignore"
    )

    veritabani_url: str = (
        "postgresql+asyncpg://localhost:5433/rebuild_vision"
    )
    model_service_url: str = "http://localhost:8090"
    jwt_gizli_anahtar: str = GUVENSIZ_VARSAYILAN_ANAHTAR
    jwt_gecerlilik_dakika: int = 480
    yukleme_klasoru: str = "api/yuklenenler"
    izin_verilen_kaynaklar: str = "http://localhost:5173"

    @field_validator("*", mode="before")
    @classmethod
    def _bosluk_kirp(cls, deger):
        """Ortam değişkenlerinin başındaki/sonundaki boşluğu temizler.

        Yayın panellerine (Render, Vercel) değer yapıştırırken sona bir
        satır sonu karışması çok kolaydır ve verdiği hata insanı yanlış
        yere götürür:

            asyncpg.exceptions.InvalidCatalogNameError:
            database "postgres\\n" does not exist

        Dize doğrudur, sonundaki görünmez karakter yüzünden reddedilir.
        Bu yüzden bütün metin ayarları okunurken kırpılır.
        """
        return deger.strip() if isinstance(deger, str) else deger

    # 'gelistirme' | 'uretim'. Üretimde güvensiz varsayılanlar reddedilir.
    ortam: str = "gelistirme"

    def model_post_init(self, __context) -> None:
        """Güvensiz varsayılan anahtarla ÜRETİME ÇIKILAMAZ.

        Depo herkese açık olduğunda bu anahtarın değeri de herkese açıktır;
        onunla imzalanan jetonlar taklit edilebilir ve herhangi biri kendine
        yönetici jetonu üretebilir. Bu yüzden hata bir uyarı değil, açılışı
        durduran bir hatadır.
        """
        if self.jwt_gizli_anahtar != GUVENSIZ_VARSAYILAN_ANAHTAR:
            return

        if self.ortam == "gelistirme":
            print(
                "\n  UYARI: JWT_GIZLI_ANAHTAR varsayılan (güvensiz) değerde.\n"
                "  Bu değer depoda açıkça yazılıdır. Yalnızca yerel geliştirme\n"
                "  için kabul edilir; yayına almadan önce mutlaka değiştirin:\n"
                "    python3 -c \"import secrets; print(secrets.token_urlsafe(48))\"\n",
                flush=True,
            )
            return

        raise RuntimeError(
            "JWT_GIZLI_ANAHTAR varsayılan (güvensiz) değerde ve ORTAM='uretim'. "
            "Bu anahtar depoda açıkça yazılıdır; onunla imzalanan jetonlar "
            "taklit edilebilir. Yeni bir anahtar üretip ortam değişkeni olarak "
            "verin:  python3 -c \"import secrets; print(secrets.token_urlsafe(48))\""
        )

    @property
    def kaynak_listesi(self) -> list[str]:
        return [k.strip() for k in self.izin_verilen_kaynaklar.split(",") if k.strip()]

    @property
    def yukleme_yolu(self) -> Path:
        y = DEPO_KOKU / self.yukleme_klasoru
        y.mkdir(parents=True, exist_ok=True)
        return y


@lru_cache
def ayarlar() -> Ayarlar:
    return Ayarlar()


@lru_cache
def siniflar() -> dict:
    """siniflar.json — sınıf listesinin tek doğruluk kaynağı.

    Sınıf adları kodda elle yazılmaz; bkz. docs/siniflar.md.
    """
    return json.loads((DEPO_KOKU / "siniflar.json").read_text(encoding="utf-8"))


@lru_cache
def malzeme_siniflari() -> frozenset[str]:
    """Yalnızca gerçek malzeme olan sınıflar.

    Atığın içinde bulunduğu kap ya da zemin bir malzeme değildir; miktar
    hesabına ve Malzeme Kaynak Haritası'na girmez. Ayrım sınıf adına
    değil `siniflar.json` → `malzeme_mi` alanına bakar, böylece sınıf
    listesi değiştiğinde kural elle güncellenmek zorunda kalmaz.
    Bkz. docs/karar-kaydi.md K-007.
    """
    return frozenset(
        s["ad"] for s in siniflar()["siniflar"] if s["malzeme_mi"]
    )


# --- Model başarım özeti (Madde 10.5 · ana talimat Bölüm 14) -------------

@lru_cache
def model_metrik_ozeti() -> str:
    """Arayüzün altbilgisinde görünen tek satırlık başarım özeti.

    ⚠️ BU METİN İKİ YERDE ELLE YAZILIYDU ve ikisi de "henüz ölçülmedi"
    diyordu. Model 01.09.2026'da eğitilip ölçüldükten sonra da öyle
    demeye devam etti — yani arayüz, jüriye ölçüm olmadığını söylerken
    depoda ölçüm duruyordu. Sabit metnin sorunu yanlış olması değil,
    yanlış OLABİLMESİDİR.

    Bu yüzden özet artık ölçümün kendisinden üretilir: sayı
    `results/egitim/metrikler.json` dosyasından okunur. Dosya yoksa
    "ölçülmedi" denir — uydurulmaz.
    """
    yol = DEPO_KOKU / "results/egitim/metrikler.json"
    if not yol.is_file():
        return "henüz ölçülmedi — results/model-metrikleri.md"
    try:
        kayitlar = json.loads(yol.read_text(encoding="utf-8"))
        ozet = next(k for k in kayitlar if k["sinif"] == "TÜM SINIFLAR")
        map50, bolme = ozet["mAP50"], ozet["split"]
    except (json.JSONDecodeError, KeyError, StopIteration):
        return "henüz ölçülmedi — results/model-metrikleri.md"

    # ⚠️ BÖLME ADI DA DOSYADAN GELİR, SABİT DEĞİL.
    #
    # Eskiden metin "test mAP50 = ..." diye sabitti ve yalnızca `test`
    # bölmesini arıyordu. v2'de test kümesi ÖLÇÜLMEDİ; elimizde val var.
    # Sabit metin kalsaydı iki kötü seçenek doğardı: ya val sayısını
    # "test" diye beyan edecektik (yanlış beyan), ya da özet "ölçülmedi"
    # diyecekti (elde ölçüm dururken yalan). Bölmeyi dosyadan okumak
    # ikisini de ortadan kaldırır.
    #
    # Model adı da aynı sebeple sabit değil: v1 YOLO11m, v2 YOLO11s.
    # Sabit bir "YOLO11m" ilk model değişiminde sessizce yanlışa döner.
    model = ozet.get("model", "model")
    sinif_sayisi = len(siniflar()["siniflar"])
    return (
        f"{bolme} mAP50 = {map50:.4f} ({sinif_sayisi} sınıf, {model}) — "
        "sınıf bazlı sonuçlar ve bilinen zayıflıklar: "
        "results/model-metrikleri.md"
    ).replace(f"{map50:.4f}", f"{map50:.4f}".replace(".", ","))
