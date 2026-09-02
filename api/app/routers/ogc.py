"""OGC API - Features · Part 1: Core — coğrafi veri için açık standart.

Şartname **Madde 10.8**:

> "Kamu sistemlerine entegrasyon potansiyeli bulunan projelerde açık
>  standartlara, REST API/OGC API benzeri servis yaklaşımına ve
>  taşınabilir veri formatlarına öncelik verilmesi beklenir."

Sistem GeoJSON dışa aktarımı zaten yapıyordu, ama o bir **dosya
indirmedir**: QGIS'te açmak için önce indirmek gerekir ve veri o anda
donar. OGC API - Features ise **canlı bir servistir** — QGIS, ArcGIS ve
kamu coğrafi bilgi sistemleri katmanı doğrudan adresten bağlar,
`bbox` ile ekrandaki alanı ister ve veri güncellendiğinde kendiliğinden
tazelenir. Kamu entegrasyonunda beklenen budur.

⚠️ BU UÇ NOKTA YENİ BİR SORGU YOLU AÇMAZ.

Kayıtlar `rapor.py` içindeki `_satirlar()` üzerinden gelir; yani rapor
ve harita ile **birebir aynı** kural süzgecinden geçer:

  - yalnızca **doğrulanmış** tespitler (`sadece_dogrulanmis`)
  - `malzeme_mi: false` işaretli sınıflar **hariç** (`sadece_malzeme`)
  - uzman düzeltmesi model tahminini **geçersiz kılar** (`gecerli_sinif`)
  - rolün göremediği saha **hiç dönmez** (`gorulebilir_alanlar`)

Sorguyu burada yeniden yazmak, bu dört kuralın birinin sessizce
atlanması demek olurdu — ve coğrafi bir uç noktada bu, doğrulanmamış
bir ön tahminin kamu haritasına düşmesi anlamına gelir.

Uygunluk beyanı: yalnızca `core` ve `geojson` uygunluk sınıfları beyan
edilir. `oas30` beyan EDİLMEZ; sistem OpenAPI 3.1 üretir, 3.0 değil —
karşılanmayan bir uygunluk sınıfı beyan etmek yanlış beyandır.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.permissions import RAPOR_ALABILIR
from ..db import oturum
from ..deps import rol_gerekli
from ..models import Kullanici
from .rapor import _gorunen_ad, _kunye, _satirlar

router = APIRouter(prefix="/ogc", tags=["OGC API - Features"])

GEOJSON = "application/geo+json"

# Yalnızca gerçekten karşılanan uygunluk sınıfları.
UYGUNLUK = [
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
]

KOLEKSIYON = "tespit"
VARSAYILAN_LIMIT = 100
EN_FAZLA_LIMIT = 1000


def _baglanti(istek: Request, yol: str, iliski: str, tur: str,
              baslik: str) -> dict:
    return {
        "href": f"{str(istek.base_url).rstrip('/')}{yol}",
        "rel": iliski,
        "type": tur,
        "title": baslik,
    }


@router.get("", summary="OGC API karşılama sayfası")
def karsilama(istek: Request) -> JSONResponse:
    return JSONResponse({
        "title": "ReBuild Vision — enkaz malzemesi tespitleri",
        "description": (
            "Doğrulanmış malzeme tespitlerinin coğrafi servisi. "
            "Her kayıt bir uzman tarafından doğrulanmıştır; "
            "doğrulanmamış ön tahminler bu serviste YER ALMAZ."
        ),
        "links": [
            _baglanti(istek, "/ogc", "self", "application/json",
                      "Bu belge"),
            _baglanti(istek, "/ogc/conformance", "conformance",
                      "application/json", "Uygunluk beyanı"),
            _baglanti(istek, "/ogc/collections", "data",
                      "application/json", "Koleksiyonlar"),
            _baglanti(istek, "/openapi.json", "service-desc",
                      "application/vnd.oai.openapi+json;version=3.1",
                      "OpenAPI tanımı"),
        ],
    })


@router.get("/conformance", summary="Uygunluk sınıfları")
def uygunluk() -> JSONResponse:
    return JSONResponse({"conformsTo": UYGUNLUK})


def _koleksiyon_tanimi(istek: Request) -> dict:
    return {
        "id": KOLEKSIYON,
        "title": "Doğrulanmış malzeme tespitleri",
        "description": (
            "Enkaz sahalarındaki görünür malzeme tespitleri. "
            "Yalnızca uzman doğrulamasından geçmiş kayıtlar; malzeme "
            "olmayan sınıflar hariç. Uzman düzeltmesi modelin ilk "
            "tahminini geçersiz kılar."
        ),
        "itemType": "feature",
        # Tek koordinat referans sistemi: WGS 84. Veri tabanında da
        # EPSG:4326 saklanıyor, dönüşüm yapılmıyor.
        "crs": ["http://www.opengis.net/def/crs/OGC/1.3/CRS84"],
        "extent": {
            # Türkiye sınırlarını kapsayan kaba kutu. Gerçek veri kapsamı
            # role göre değiştiği için sabit bir kutu veriliyor; kullanıcıya
            # göre değişen bir "extent" bilgi sızdırırdı.
            "spatial": {
                "bbox": [[25.0, 35.0, 45.0, 43.0]],
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
            },
        },
        "links": [
            _baglanti(istek, f"/ogc/collections/{KOLEKSIYON}", "self",
                      "application/json", "Koleksiyon tanımı"),
            _baglanti(istek, f"/ogc/collections/{KOLEKSIYON}/items", "items",
                      GEOJSON, "Kayıtlar"),
        ],
    }


@router.get("/collections", summary="Koleksiyonlar")
def koleksiyonlar(istek: Request) -> JSONResponse:
    return JSONResponse({
        "collections": [_koleksiyon_tanimi(istek)],
        "links": [
            _baglanti(istek, "/ogc/collections", "self",
                      "application/json", "Bu belge"),
        ],
    })


@router.get("/collections/{koleksiyon_id}", summary="Koleksiyon tanımı")
def koleksiyon(koleksiyon_id: str, istek: Request) -> JSONResponse:
    if koleksiyon_id != KOLEKSIYON:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            f"Koleksiyon bulunamadı: {koleksiyon_id}")
    return JSONResponse(_koleksiyon_tanimi(istek))


def _ozellik(r) -> dict:
    """Bir tespit kaydını GeoJSON Feature'a çevirir."""
    return {
        "type": "Feature",
        "id": r["id"],
        "geometry": {
            "type": "Point",
            # GeoJSON (RFC 7946): boylam önce, enlem sonra.
            "coordinates": [r["boylam"], r["enlem"]],
        },
        "properties": {
            "alan_id": r["alan_id"],
            "alan_adi": r["alan_adi"],
            "sinif": r["sinif"],
            "sinif_gorunen_ad": _gorunen_ad(r["sinif"]),
            # Modelin ilk tahmini de taşınır: uzman düzelttiyse ikisi
            # farklıdır ve fark izlenebilir kalmalıdır.
            "model_tahmini": r["model_tahmini"],
            "uzman_duzeltmesi": r["duzeltilen_sinif"],
            "model_guveni": r["guven_skoru"],
            "dogrulama_durumu": r["dogrulama_durumu"].value,
            "miktar_alt": r["deger_alt"],
            "miktar_ust": r["deger_ust"],
            "miktar_birim": r["birim"],
            "miktar_yontemi": r["yontem"],
            "katsayi_kaynagi": r["katsayi_kaynagi"],
        },
    }


@router.get("/collections/{koleksiyon_id}/items", summary="Kayıtlar")
async def kayitlar(
    koleksiyon_id: str,
    istek: Request,
    bbox: str | None = Query(
        None,
        description="Sınırlayıcı kutu: boylam_min,enlem_min,boylam_max,enlem_max",
    ),
    limit: int = Query(VARSAYILAN_LIMIT, ge=1, le=EN_FAZLA_LIMIT),
    offset: int = Query(0, ge=0),
    alan_id: int | None = None,
    k: Kullanici = Depends(rol_gerekli(RAPOR_ALABILIR)),
    db: AsyncSession = Depends(oturum),
) -> JSONResponse:
    if koleksiyon_id != KOLEKSIYON:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            f"Koleksiyon bulunamadı: {koleksiyon_id}")

    # Kural süzgeci burada değil, ortak sorguda. Bkz. dosya başlığı.
    satirlar = [r for r in await _satirlar(db, k, alan_id)
                if r["enlem"] is not None and r["boylam"] is not None]

    if bbox:
        try:
            b = [float(p) for p in bbox.split(",")]
            if len(b) != 4:
                raise ValueError
        except ValueError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "bbox biçimi: boylam_min,enlem_min,boylam_max,enlem_max",
            ) from None
        satirlar = [r for r in satirlar
                    if b[0] <= r["boylam"] <= b[2]
                    and b[1] <= r["enlem"] <= b[3]]

    toplam = len(satirlar)
    sayfa = satirlar[offset:offset + limit]

    baglantilar = [
        _baglanti(istek, f"/ogc/collections/{KOLEKSIYON}/items", "self",
                  GEOJSON, "Bu sayfa"),
        _baglanti(istek, f"/ogc/collections/{KOLEKSIYON}", "collection",
                  "application/json", "Koleksiyon tanımı"),
    ]
    if offset + limit < toplam:
        baglantilar.append({
            "href": (f"{str(istek.base_url).rstrip('/')}"
                     f"/ogc/collections/{KOLEKSIYON}/items"
                     f"?limit={limit}&offset={offset + limit}"),
            "rel": "next", "type": GEOJSON, "title": "Sonraki sayfa",
        })

    return JSONResponse(
        {
            "type": "FeatureCollection",
            "features": [_ozellik(r) for r in sayfa],
            "numberMatched": toplam,
            "numberReturned": len(sayfa),
            "timeStamp": _kunye()["uretilme_tarihi"],
            # Kapsam uyarısı burada da taşınır: QGIS'ten bağlanan biri
            # README'yi okumaz, veriyi olduğu gibi alır.
            "kunye": _kunye(),
            "links": baglantilar,
        },
        media_type=GEOJSON,
    )


@router.get("/collections/{koleksiyon_id}/items/{kayit_id}",
            summary="Tek kayıt")
async def kayit(
    koleksiyon_id: str,
    kayit_id: int,
    istek: Request,
    k: Kullanici = Depends(rol_gerekli(RAPOR_ALABILIR)),
    db: AsyncSession = Depends(oturum),
) -> JSONResponse:
    if koleksiyon_id != KOLEKSIYON:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            f"Koleksiyon bulunamadı: {koleksiyon_id}")

    # Tek kayıt da aynı süzgeçten geçer: id ile doğrudan erişim,
    # rol kapsamını ya da doğrulama kuralını atlamanın yolu OLAMAZ.
    for r in await _satirlar(db, k, None):
        if r["id"] == kayit_id:
            if r["enlem"] is None or r["boylam"] is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    "Kaydın konumu yok")
            ozellik = _ozellik(r)
            ozellik["links"] = [
                _baglanti(istek,
                          f"/ogc/collections/{KOLEKSIYON}/items/{kayit_id}",
                          "self", GEOJSON, "Bu kayıt"),
                _baglanti(istek, f"/ogc/collections/{KOLEKSIYON}",
                          "collection", "application/json",
                          "Koleksiyon tanımı"),
            ]
            return JSONResponse(ozellik, media_type=GEOJSON)

    raise HTTPException(status.HTTP_404_NOT_FOUND,
                        f"Kayıt bulunamadı: {kayit_id}")
