"""Miktar hesabı — ana talimat Bölüm 1.1'in kod karşılığı.

İki kural, ikisi de burada zorlanır:

1. ÖLÇÜM YOKSA MİKTAR ÜRETİLMEZ.
   Varsayılan değer, tahmini değer, yer tutucu sayı, "≈0" veya
   "hesaplanıyor" yazılmaz. Hesap yapılamıyorsa satır OLUŞTURULMAZ —
   sıfır yazılmaz, NULL yazılmaz, satır yoktur.

2. MİKTAR TEK BİR KESİN DEĞER OLARAK ÜRETİLMEZ.
   Belirsizlik aralığı ve kullanılan yöntem birlikte döner
   (Rapor Bölüm 4, üçüncü yenilikçi yön).

3. DOĞRULANMAMIŞ KAYIT MİKTAR HESABINA GİRMEZ (Bölüm 1.4).
   "Bu bir arayüz kuralı değil, veri katmanı kuralıdır." Kural bu yüzden
   burada, hesabın kendisinde durur: `hesapla` tespiti bütün olarak alır
   ve doğrulama durumuna bakar. Router'a bırakılsaydı yeni bir çağıran
   kontrolü atlayabilirdi; buradan atlanamaz.

Ek olarak: dayanağı doğrulanmamış bir katsayı ile hesap yapılmaz
(Bölüm 14). Bu da 'hesaplanamadı' sonucunu verir.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache

from ..core.config import DEPO_KOKU, malzeme_siniflari
from ..models import DogrulamaDurumu, Olcum, OlcumTuru, Tespit


@lru_cache
def katsayilar() -> dict[str, dict]:
    ham = json.loads((DEPO_KOKU / "katsayilar.json").read_text(encoding="utf-8"))
    return {k["sinif"]: k for k in ham["katsayilar"]}


class HesaplanamazNedeni(str):
    pass


OLCUM_YOK = "olcum_yok"
MALZEME_DEGIL = "malzeme_degil"
KATSAYI_YOK = "katsayi_dogrulanmadi"
UYGUN_OLCUM_YOK = "uygun_olcum_turu_yok"
DOGRULANMADI = "dogrulanmadi"

# Uzmanın onayladığı sayılan durumlar. `beklemede` ve `belirsiz` yoktur:
# belirsiz, uzmanın karar veremediği kayıttır ve hesaba katılmaz.
# services/queries.py DOGRULANMIS ile aynı küme.
DOGRULANMIS = (DogrulamaDurumu.ONAYLANDI, DogrulamaDurumu.DUZELTILDI)


@dataclass(frozen=True)
class Sonuc:
    """Hesap sonucu.

    `hesaplandi=False` ise hiçbir sayı alanı doldurulmaz. Çağıran taraf
    veri tabanına satır YAZMAZ.
    """
    hesaplandi: bool
    neden: str | None = None
    deger_alt: float | None = None
    deger_ust: float | None = None
    birim: str | None = None
    kullanilan_katsayi: float | None = None
    katsayi_kaynagi: str | None = None
    yontem: str | None = None


def hesapla(tespit: Tespit, olcumler: list[Olcum]) -> Sonuc:
    """Bir tespit için miktar aralığı üretir ya da üretmeyi reddeder.

    Tespit nesnesini bütün olarak alır — yalnızca sınıfını değil. Doğrulama
    durumu kontrolünün çağıran tarafa bırakılmaması bilinçlidir.
    """
    # Kural 3: uzman onaylamadıysa hesap yapılmaz. En başta, çünkü ölçüm
    # varlığından da katsayıdan da önce gelir.
    if tespit.dogrulama_durumu not in DOGRULANMIS:
        return Sonuc(hesaplandi=False, neden=DOGRULANMADI)

    # Uzman düzeltmesi varsa geçerli sınıf odur — insanın kararı modelin
    # tahminini geçersiz kılar.
    sinif = tespit.duzeltilen_sinif or tespit.sinif

    # Kural: konteyner gibi malzeme olmayan sınıflar miktara girmez (K-007).
    if sinif not in malzeme_siniflari():
        return Sonuc(hesaplandi=False, neden=MALZEME_DEGIL)

    # Kural 1: ölçüm yoksa miktar üretilmez.
    if not olcumler:
        return Sonuc(hesaplandi=False, neden=OLCUM_YOK)

    # Doğrudan ağırlık ölçümü varsa katsayıya gerek yoktur.
    agirlik = [o for o in olcumler if o.tur == OlcumTuru.AGIRLIK]
    if agirlik:
        degerler = [o.deger for o in agirlik]
        alt, ust = min(degerler), max(degerler)
        if alt == ust:
            # Tek ölçüm: aralık, ölçüm belirsizliğinden türetilir.
            # %10 saha ölçüm belirsizliği, yöntem alanında açıkça belirtilir.
            alt, ust = alt * 0.90, ust * 1.10
            yontem = (
                "Doğrudan ağırlık ölçümü (tek kayıt). Aralık, ±%10 saha "
                "ölçüm belirsizliği varsayımıyla üretildi."
            )
        else:
            yontem = (
                f"Doğrudan ağırlık ölçümü ({len(agirlik)} kayıt). Aralık, "
                "kayıtların en düşük ve en yüksek değerlerinden üretildi."
            )
        return Sonuc(
            hesaplandi=True,
            deger_alt=round(alt, 3),
            deger_ust=round(ust, 3),
            birim=agirlik[0].birim,
            kullanilan_katsayi=1.0,
            katsayi_kaynagi="Katsayı kullanılmadı — doğrudan ölçüm.",
            yontem=yontem,
        )

    # Hacim ölçümü varsa yoğunluk katsayısı gerekir.
    hacim = [o for o in olcumler if o.tur == OlcumTuru.HACIM]
    if not hacim:
        # Yalnızca alan ölçümü var: derinlik bilinmeden hacme çevrilemez.
        return Sonuc(hesaplandi=False, neden=UYGUN_OLCUM_YOK)

    k = katsayilar().get(sinif)
    if not k or not k.get("dogrulandi") or k.get("alt") is None:
        # Dayanağı doğrulanmamış katsayı ile sayı üretilmez (Bölüm 14).
        return Sonuc(hesaplandi=False, neden=KATSAYI_YOK)

    toplam_hacim = sum(o.deger for o in hacim)
    return Sonuc(
        hesaplandi=True,
        deger_alt=round(toplam_hacim * k["alt"], 3),
        deger_ust=round(toplam_hacim * k["ust"], 3),
        birim="ton",
        kullanilan_katsayi=(k["alt"] + k["ust"]) / 2,
        katsayi_kaynagi=k["kaynak"],
        yontem=(
            f"Hacim ölçümü ({toplam_hacim} m³) × yoğunluk aralığı "
            f"({k['alt']}–{k['ust']} ton/m³)."
        ),
    )


# Arayüzde gösterilecek metinler. 'Hesaplanamadı' bir hata değil, bilinçli
# bir karardır ve kullanıcıya böyle anlatılır (ana talimat Bölüm 1.1, 9.4).
NEDEN_METNI = {
    OLCUM_YOK: "Ölçüm girilmediği için miktar hesaplanmadı",
    UYGUN_OLCUM_YOK: (
        "Yalnızca alan ölçümü var; derinlik bilinmeden hacim ve miktar "
        "hesaplanamaz"
    ),
    KATSAYI_YOK: (
        "Bu malzeme için doğrulanmış dönüşüm katsayısı bulunmadığından "
        "miktar hesaplanmadı"
    ),
    MALZEME_DEGIL: "Bu sınıf bir atık malzeme değildir; miktar hesaplanmaz",
    DOGRULANMADI: (
        "Tespit uzman tarafından doğrulanmadığı için miktar hesaplanmadı. "
        "Doğrulanmamış kayıtlar miktar ve raporlama hesaplarına girmez."
    ),
}
