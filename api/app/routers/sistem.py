"""Sistem durumu, sınıflar, harita ve işlem geçmişi."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import siniflar as sinif_tanimlari
from ..db import oturum
from ..deps import aktif_kullanici
from ..models import Goruntu, IslemGecmisi, Kullanici, Tespit
from ..schemas import IslemGecmisiCikti
from ..services import model_client
from ..services.queries import hesaba_girebilir

router = APIRouter(tags=["sistem"])

# Ana talimat Bölüm 1.3 — bu metin arayüzde sonuç ekranında ve harita
# lejandında YAZILI olarak görünür.
KAPSAM_UYARISI = (
    "Sistem yalnızca görünür yüzeye ilişkin ön değerlendirme yapar; "
    "enkaz altı içerik değerlendirilmez."
)


@router.get("/sistem/durum")
async def durum():
    """Servis durumu.

    `sahte_model_servisi: true` ise arayüz kalıcı 'SAHTE MODEL SERVİSİ'
    rozeti gösterir (ana talimat Bölüm 9.5) — demo sırasında yanlışlıkla
    'gerçek model çalışıyor' izlenimi verilmesin.
    """
    try:
        saglik = await model_client.saglik()
        model_durumu = {
            "ulasilabilir": True,
            "sahte": bool(saglik.get("sahte")),
            "model": saglik.get("model"),
            "lisans": saglik.get("model_license"),
        }
    except model_client.ModelServisiHatasi as e:
        model_durumu = {"ulasilabilir": False, "sahte": None, "hata": str(e)}

    return {
        "model_servisi": model_durumu,
        "kapsam_uyarisi": KAPSAM_UYARISI,
        "model_metrikleri": "henüz ölçülmedi — results/model-metrikleri.md",
    }


@router.get("/sistem/siniflar")
async def siniflar():
    """Sınıf tanımları. Arayüz renk ve etiketleri buradan alır.

    `kapsanmayan_gruplar` da döner: cam ve seramik eğitim verisinde
    bulunmadığı için model bu grupları tanımaz. Arayüz bunu görünür kılar —
    bir sınıfın yokluğu 'o malzeme sahada yok' anlamına gelmez.
    """
    return sinif_tanimlari()


@router.get("/harita")
async def harita(
    k: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    """Malzeme Kaynak Haritası verisi.

    Yalnızca DOĞRULANMIŞ ve MALZEME olan tespitler döner — filtre veri
    katmanındadır (ana talimat Bölüm 1.4, docs/karar-kaydi.md K-007).
    """
    sorgu = hesaba_girebilir(
        select(Tespit.sinif, func.count(Tespit.id))
        .join(Goruntu, Tespit.goruntu_id == Goruntu.id)
    ).group_by(Tespit.sinif)

    y = await db.execute(sorgu)
    return {
        "kapsam_uyarisi": KAPSAM_UYARISI,
        "not": (
            "Yalnızca uzman tarafından doğrulanmış kayıtlar gösterilir. "
            "Doğrulanmamış ön tahminler haritada yer almaz."
        ),
        "malzeme_dagilimi": [{"sinif": s, "adet": n} for s, n in y.all()],
    }


@router.get("/gecmis", response_model=list[IslemGecmisiCikti])
async def gecmis(
    kayit_tipi: str | None = None,
    kayit_id: int | None = None,
    limit: int = 50,
    _: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    """İşlem geçmişi — kim, ne zaman, neyi değiştirdi.

    Rapor Bölüm 6, dördüncü yenilikçi yön. Arayüzde de görünür olmalıdır,
    yalnızca veri tabanında durmamalıdır.
    """
    sorgu = select(IslemGecmisi).order_by(IslemGecmisi.id.desc()).limit(min(limit, 200))
    if kayit_tipi:
        sorgu = sorgu.where(IslemGecmisi.kayit_tipi == kayit_tipi)
    if kayit_id is not None:
        sorgu = sorgu.where(IslemGecmisi.kayit_id == kayit_id)
    y = await db.execute(sorgu)
    return list(y.scalars())
