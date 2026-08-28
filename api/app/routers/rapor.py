"""Rapor indirme — JSON, GeoJSON ve CSV.

Ana talimat Bölüm 10 (P3). Jürinin ve kurumların veriyi kendi
araçlarında (QGIS, Excel) açabilmesi için.

⚠️ RAPORLARIN TAŞIDIĞI KURALLAR — ekrandakiyle aynıdır, istisnasız:

1. Yalnızca **doğrulanmış** tespitler dışa aktarılır. Doğrulanmamış ön
   tahminler rapora girmez (ana talimat Bölüm 1.4). Ekranda gizlenip
   dosyada verilseydi kural anlamsız olurdu.
2. Uzman düzeltmesi modelin tahminini geçersiz kılar; raporda **geçerli
   sınıf** yazar, ham tahmin ayrı bir sütunda izlenebilirlik için durur.
3. `konteyner` gibi malzeme olmayan sınıflar dışarıda kalır (K-007).
4. **Miktar hesaplanmamışsa alan boştur.** CSV'de sıfır değil, boş
   hücre; JSON'da `null`. Elektronik tabloda 0 gören biri "ölçüm sıfır"
   sanardı — oysa ölçüm yapılmamıştır (Bölüm 1.1).
5. Her dosyanın başında kapsam uyarısı bulunur: sistem yalnızca görünür
   yüzeyi değerlendirir ve tehlikeli madde teşhisi yapmaz.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import siniflar as sinif_tanimlari
from ..core.permissions import RAPOR_ALABILIR
from ..db import oturum
from ..deps import rol_gerekli
from ..models import EnkazAlani, Goruntu, Kullanici, MiktarHesabi, Tespit
from ..services.queries import gecerli_sinif, gorulebilir_alanlar, hesaba_girebilir

router = APIRouter(prefix="/rapor", tags=["rapor"])

KAPSAM_UYARISI = (
    "Sistem yalnızca görünür yüzeye ilişkin ön değerlendirme yapar; enkaz "
    "altı içerik değerlendirilmez. Sistem tehlikeli madde teşhisi yapmaz. "
    "Bu dosya yalnızca uzman tarafından doğrulanmış kayıtları içerir."
)

MIKTAR_NOTU = (
    "Miktar alanı boşsa ölçüm girilmediği için hesaplanmamıştır; sıfır "
    "anlamına GELMEZ. Miktar hesaplandığında tek bir kesin değer değil, "
    "alt ve üst sınırdan oluşan belirsizlik aralığı verilir."
)


async def _satirlar(db: AsyncSession, k: Kullanici, alan_id: int | None):
    """Rapora girecek kayıtlar — ekrandaki filtrelerin aynısı."""
    gorulebilir = gorulebilir_alanlar(k.rol, k.id).subquery()

    sorgu = hesaba_girebilir(
        select(
            Tespit.id,
            gecerli_sinif().label("sinif"),
            Tespit.sinif.label("model_tahmini"),
            Tespit.duzeltilen_sinif,
            Tespit.guven_skoru,
            Tespit.dogrulama_durumu,
            Tespit.dogrulama_tarihi,
            EnkazAlani.id.label("alan_id"),
            EnkazAlani.ad.label("alan_adi"),
            func.ST_Y(EnkazAlani.konum).label("enlem"),
            func.ST_X(EnkazAlani.konum).label("boylam"),
            MiktarHesabi.deger_alt,
            MiktarHesabi.deger_ust,
            MiktarHesabi.birim,
            MiktarHesabi.yontem,
            MiktarHesabi.katsayi_kaynagi,
        )
        .join(Goruntu, Tespit.goruntu_id == Goruntu.id)
        .join(EnkazAlani, Goruntu.enkaz_alani_id == EnkazAlani.id)
        .join(MiktarHesabi, MiktarHesabi.tespit_id == Tespit.id, isouter=True)
        .join(gorulebilir, gorulebilir.c.id == EnkazAlani.id)
    ).order_by(EnkazAlani.id, Tespit.id)

    if alan_id is not None:
        sorgu = sorgu.where(EnkazAlani.id == alan_id)

    return (await db.execute(sorgu)).mappings().all()


def _kunye() -> dict:
    return {
        "uretilme_tarihi": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kaynak": "ReBuild Vision",
        "kapsam_uyarisi": KAPSAM_UYARISI,
        "miktar_notu": MIKTAR_NOTU,
        "model_metrikleri": "henüz ölçülmedi — results/model-metrikleri.md",
    }


def _gorunen_ad(sinif: str) -> str:
    for s in sinif_tanimlari()["siniflar"]:
        if s["ad"] == sinif:
            return s["gorunen_ad"]
    return sinif


@router.get("/json")
async def json_rapor(
    alan_id: int | None = None,
    k: Kullanici = Depends(rol_gerekli(RAPOR_ALABILIR)),
    db: AsyncSession = Depends(oturum),
):
    satirlar = await _satirlar(db, k, alan_id)
    govde = {
        **_kunye(),
        "kayit_sayisi": len(satirlar),
        "kayitlar": [
            {
                "tespit_id": r["id"],
                "enkaz_alani": {"id": r["alan_id"], "ad": r["alan_adi"]},
                "sinif": r["sinif"],
                "sinif_gorunen_ad": _gorunen_ad(r["sinif"]),
                "model_tahmini": r["model_tahmini"],
                "uzman_duzeltmesi": r["duzeltilen_sinif"],
                "model_guveni": r["guven_skoru"],
                "dogrulama_durumu": r["dogrulama_durumu"].value,
                "dogrulama_tarihi": (
                    r["dogrulama_tarihi"].isoformat()
                    if r["dogrulama_tarihi"] else None
                ),
                # Hesaplanmadıysa null — sıfır DEĞİL.
                "miktar": (
                    {
                        "alt": r["deger_alt"], "ust": r["deger_ust"],
                        "birim": r["birim"], "yontem": r["yontem"],
                        "katsayi_kaynagi": r["katsayi_kaynagi"],
                    }
                    if r["deger_alt"] is not None else None
                ),
            }
            for r in satirlar
        ],
    }
    return Response(
        content=json.dumps(govde, ensure_ascii=False, indent=2),
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition":
                 'attachment; filename="rebuild-vision-rapor.json"'},
    )


@router.get("/geojson")
async def geojson_rapor(
    alan_id: int | None = None,
    k: Kullanici = Depends(rol_gerekli(RAPOR_ALABILIR)),
    db: AsyncSession = Depends(oturum),
):
    """QGIS ve benzeri araçlarda doğrudan açılabilen coğrafi çıktı."""
    satirlar = await _satirlar(db, k, alan_id)

    ozellikler = []
    for r in satirlar:
        if r["enlem"] is None or r["boylam"] is None:
            continue  # konumsuz kayıt haritaya konamaz
        ozellikler.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r["boylam"], r["enlem"]],  # GeoJSON: boylam önce
            },
            "properties": {
                "tespit_id": r["id"],
                "alan_adi": r["alan_adi"],
                "sinif": r["sinif"],
                "sinif_gorunen_ad": _gorunen_ad(r["sinif"]),
                "model_guveni": r["guven_skoru"],
                "dogrulama_durumu": r["dogrulama_durumu"].value,
                "miktar_alt": r["deger_alt"],
                "miktar_ust": r["deger_ust"],
                "miktar_birim": r["birim"],
            },
        })

    return Response(
        content=json.dumps({
            "type": "FeatureCollection",
            # Kapsam uyarısı dosyanın içinde kalsın: QGIS'te açan biri de görsün.
            "kunye": _kunye(),
            "features": ozellikler,
        }, ensure_ascii=False, indent=2),
        media_type="application/geo+json; charset=utf-8",
        headers={"Content-Disposition":
                 'attachment; filename="rebuild-vision-rapor.geojson"'},
    )


@router.get("/csv")
async def csv_rapor(
    alan_id: int | None = None,
    k: Kullanici = Depends(rol_gerekli(RAPOR_ALABILIR)),
    db: AsyncSession = Depends(oturum),
):
    satirlar = await _satirlar(db, k, alan_id)

    tampon = io.StringIO()
    # Excel Türkçe yerelde ';' bekler; ',' kullanılırsa sütunlar birleşir.
    yazici = csv.writer(tampon, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    yazici.writerow([f"# {KAPSAM_UYARISI}"])
    yazici.writerow([f"# {MIKTAR_NOTU}"])
    yazici.writerow([f"# Üretilme: {_kunye()['uretilme_tarihi']}"])
    yazici.writerow([])
    yazici.writerow([
        "tespit_id", "enkaz_alani", "sinif", "sinif_gorunen_ad",
        "model_tahmini", "uzman_duzeltmesi", "model_guveni",
        "dogrulama_durumu", "dogrulama_tarihi",
        "miktar_alt", "miktar_ust", "miktar_birim", "miktar_yontemi",
    ])
    for r in satirlar:
        yazici.writerow([
            r["id"], r["alan_adi"], r["sinif"], _gorunen_ad(r["sinif"]),
            r["model_tahmini"], r["duzeltilen_sinif"] or "",
            r["guven_skoru"], r["dogrulama_durumu"].value,
            r["dogrulama_tarihi"].isoformat() if r["dogrulama_tarihi"] else "",
            # Hesaplanmadıysa BOŞ hücre — 0 yazılsaydı "ölçüm sıfır" sanılırdı.
            r["deger_alt"] if r["deger_alt"] is not None else "",
            r["deger_ust"] if r["deger_ust"] is not None else "",
            r["birim"] or "", r["yontem"] or "",
        ])

    # Excel'in UTF-8'i tanıması için BOM gerekir; yoksa Türkçe harfler bozulur.
    return Response(
        content="﻿" + tampon.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition":
                 'attachment; filename="rebuild-vision-rapor.csv"'},
    )
