"""Ortam yapılandırması."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

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

    `konteyner` (skip bin) bir malzeme değildir; miktar hesabına ve
    Malzeme Kaynak Haritası'na girmez. Bkz. docs/karar-kaydi.md K-007.
    """
    return frozenset(
        s["ad"] for s in siniflar()["siniflar"] if s["malzeme_mi"]
    )
