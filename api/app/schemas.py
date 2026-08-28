"""Pydantic şemaları — API sözleşmesi."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from .core.permissions import OnayDurumu, Rol
from .models import DogrulamaDurumu, ErisimDurumu, OlcumTuru, TehlikeliDurum


class Model(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# E-posta doğrulaması bilinçli olarak SÖZDİZİMSELDİR, alan adı çözümlemesi
# yapılmaz.
#
# Gerekçe: şartname Madde 10.7 demo ortamında gerçek adres kullanılmamasını
# istiyor; demo hesapları @demo.local alan adındadır. `.local` ayrılmış bir
# üst alan adı olduğu için katı doğrulayıcılar (email-validator) bu adresleri
# reddeder. Katı doğrulama, Madde 10.7'nin gerektirdiği hesapları imkânsız
# kılardı.
#
# Yan fayda: email-validator ve dnspython bağımlılıkları gerekmiyor.
Eposta = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        min_length=5,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
]


# --- Kimlik -----------------------------------------------------------------

class KayitIstek(Model):
    """DİKKAT: burada 'rol' alanı YOKTUR ve eklenmeyecektir.

    Kullanıcı kayıt olurken kendi rolünü seçemez (Brief Bölüm 3).
    Kayıt sonrası onay_durumu=beklemede ile başlar; rolü yönetici atar.
    """
    eposta: Eposta
    parola: str = Field(min_length=8)
    ad: str = Field(min_length=2, max_length=200)


class GirisIstek(Model):
    eposta: Eposta
    parola: str


class KullaniciCikti(Model):
    id: int
    eposta: str
    ad: str
    rol: Rol | None
    onay_durumu: OnayDurumu
    olusturma_tarihi: datetime


class JetonCikti(Model):
    jeton: str
    tur: str = "bearer"
    kullanici: KullaniciCikti


class RolAtaIstek(Model):
    rol: Rol
    onay_durumu: OnayDurumu


# --- Enkaz alanı ------------------------------------------------------------

class Nokta(Model):
    enlem: float = Field(ge=-90, le=90)
    boylam: float = Field(ge=-180, le=180)


class EnkazAlaniIstek(Model):
    ad: str = Field(min_length=2, max_length=200)
    konum: Nokta | None = None
    sinir: list[Nokta] | None = Field(default=None, min_length=3)
    erisim_durumu: ErisimDurumu = ErisimDurumu.ACIK
    sorumlu: str | None = None
    inceleme_tarihi: datetime | None = None


class MalzemePayi(Model):
    sinif: str
    adet: int


class EnkazAlaniCikti(Model):
    id: int
    ad: str
    konum: Nokta | None = None
    sinir: list[Nokta] | None = None
    erisim_durumu: ErisimDurumu
    sorumlu: str | None
    inceleme_tarihi: datetime | None
    olusturan_id: int
    olusturma_tarihi: datetime
    goruntu_sayisi: int = 0

    # Kart özeti — sahayı açmadan durumu görebilmek için.
    tespit_sayisi: int = 0
    dogrulanan_sayisi: int = 0
    inceleme_bekleyen: int = 0
    # Yalnızca DOĞRULANMIŞ kayıtlardan; haritayla aynı kural (Bölüm 1.4).
    malzeme_dagilimi: list[MalzemePayi] = []


# --- Görüntü ve tespit ------------------------------------------------------

class BBox(Model):
    x: int
    y: int
    w: int
    h: int


class TespitCikti(Model):
    id: int
    goruntu_id: int
    sinif: str
    guven_skoru: float
    bbox: BBox | None = None

    # Kutunun hangi koordinat uzayında olduğu HER ZAMAN belirtilir.
    # Arayüz ölçeklemeyi bu alana göre yapar (ana talimat Bölüm 4.3).
    bbox_format: str

    dogrulama_durumu: DogrulamaDurumu
    dogrulayan_id: int | None
    dogrulama_tarihi: datetime | None
    duzeltilen_sinif: str | None
    inceleme_gerekli: bool

    # Her model çıktısı 'ön tahmin'dir, istisnasız (ana talimat Bölüm 1.4).
    etiket: str = "ön tahmin"


class GoruntuCikti(Model):
    id: int
    enkaz_alani_id: int
    dosya_yolu: str
    genislik: int | None
    yukseklik: int | None
    cekim_tarihi: datetime | None
    cihaz: str | None
    yukleyen_id: int
    olusturma_tarihi: datetime
    tespitler: list[TespitCikti] = []


class YuklemeCikti(Model):
    goruntuler: list[GoruntuCikti]
    sahte_model_servisi: bool
    inceleme_kuyruguna_dusen: int


# --- Doğrulama --------------------------------------------------------------

class DogrulamaIstek(Model):
    """Üç aksiyon: onayla, düzelt, belirsiz işaretle.

    'reddet' BİLİNÇLİ OLARAK YOKTUR — rapor gövde metni esas alındı.
    Gerekçe: docs/karar-kaydi.md K-004.
    """
    durum: DogrulamaDurumu
    duzeltilen_sinif: str | None = None


# --- Ölçüm ve miktar --------------------------------------------------------

class OlcumIstek(Model):
    tespit_id: int
    tur: OlcumTuru
    deger: float = Field(gt=0)
    birim: str
    yontem: str


class EsitlemeSatiri(Model):
    """Çevrimdışı kuyruktan gelen tek ölçüm."""
    # Cihazda üretilir (UUID). Yinelenen yazımı engelleyen anahtar budur.
    yerel_kimlik: Annotated[str, StringConstraints(min_length=8, max_length=64)]
    tespit_id: int
    tur: OlcumTuru
    deger: float = Field(gt=0)
    birim: str
    yontem: str


class EsitlemeIstek(Model):
    kayitlar: list[EsitlemeSatiri] = Field(min_length=1, max_length=200)


class EsitlemeSatirSonucu(Model):
    yerel_kimlik: str
    # yazildi | yinelenen | hata
    durum: str
    aciklama: str | None = None


class EsitlemeSonucu(Model):
    """Kısmi başarı normaldir; istemci yalnızca hatalıları kuyrukta tutar."""
    yazilan: int
    yinelenen: int
    hatali: int
    satirlar: list[EsitlemeSatirSonucu]


class OlcumCikti(Model):
    id: int
    tespit_id: int
    tur: OlcumTuru
    deger: float
    birim: str
    yontem: str
    giren_id: int
    tarih: datetime


class MiktarCikti(Model):
    """Miktar — hesaplanmadıysa hiçbir sayı alanı doldurulmaz.

    `hesaplandi=False` olduğunda arayüz sayı YAZMAZ; `aciklama` metnini ve
    ölçüm ekleme aksiyonunu gösterir (ana talimat Bölüm 1.1).
    """
    tespit_id: int
    hesaplandi: bool
    aciklama: str | None = None

    deger_alt: float | None = None
    deger_ust: float | None = None
    birim: str | None = None
    kullanilan_katsayi: float | None = None
    katsayi_kaynagi: str | None = None
    yontem: str | None = None


# --- Tehlikeli madde --------------------------------------------------------

class TehlikeliIstek(Model):
    """Sistem tehlikeli madde TEŞHİSİ YAPMAZ (ana talimat Bölüm 1.2).

    Bu şemada bilinçli olarak BULUNMAYAN alanlar: olasılık, güven skoru,
    madde adı tahmini, risk seviyesi ve 'güvenli' değerlendirmesi.
    Kaydı model değil, insan girer.
    """
    tespit_id: int
    durum: TehlikeliDurum
    lab_sonucu_notu: str | None = None


class TehlikeliCikti(Model):
    id: int
    tespit_id: int
    durum: TehlikeliDurum
    lab_sonucu_notu: str | None
    giren_id: int
    tarih: datetime


# --- İşlem geçmişi ----------------------------------------------------------

class IslemGecmisiCikti(Model):
    id: int
    kayit_tipi: str
    kayit_id: int | None
    islem: str
    eski_deger: dict | None
    yeni_deger: dict | None
    kullanici_id: int | None
    tarih: datetime
