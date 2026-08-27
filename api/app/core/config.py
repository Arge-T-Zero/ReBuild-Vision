"""Ortam yapılandırması."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DEPO_KOKU = Path(__file__).resolve().parents[3]


class Ayarlar(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DEPO_KOKU / ".env", extra="ignore"
    )

    veritabani_url: str = (
        "postgresql+asyncpg://localhost:5433/rebuild_vision"
    )
    model_service_url: str = "http://localhost:8090"
    jwt_gizli_anahtar: str = "gelistirme-icin-guvensiz-anahtar-DEGISTIRIN"
    jwt_gecerlilik_dakika: int = 480
    yukleme_klasoru: str = "api/yuklenenler"
    izin_verilen_kaynaklar: str = "http://localhost:5173"

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
