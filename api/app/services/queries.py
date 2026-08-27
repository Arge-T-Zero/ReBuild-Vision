"""Sorgu yardımcıları — veri katmanı kuralları.

Ana talimat Bölüm 1.4:
"Doğrulanmamış kayıtlar miktar, ekonomik değer ve yönlendirme hesaplarına
girmez. Bu bir arayüz kuralı değil, veri katmanı kuralıdır — sorgu
seviyesinde filtrelensin."

Miktar, harita ve rapor üreten her sorgu buradaki yardımcılardan geçer.
"""
from __future__ import annotations

from sqlalchemy import Select, func, select

from ..core.config import malzeme_siniflari
from ..core.permissions import TUM_SAHALARI_GORUR, Rol
from ..models import DogrulamaDurumu, EnkazAlani, Goruntu, Tespit

# İnsan tarafından doğrulanmış sayılan durumlar. 'beklemede' ve 'belirsiz'
# BURADA YOKTUR: belirsiz işaretlenmiş bir kayıt, uzmanın karar veremediği
# kayıttır ve hesaplara katılmaz.
DOGRULANMIS = (DogrulamaDurumu.ONAYLANDI, DogrulamaDurumu.DUZELTILDI)


def sadece_dogrulanmis(sorgu: Select) -> Select:
    """Doğrulanmamış tespitleri eler."""
    return sorgu.where(Tespit.dogrulama_durumu.in_(DOGRULANMIS))


def gecerli_sinif():
    """Kaydın GEÇERLİ sınıfı: uzman düzelttiyse düzeltilen sınıf.

    Projenin ayırt edici iddiası insan denetimli yapay zekâdır; uzmanın
    düzeltmesi model tahminini geçersiz kılar. Miktar, harita ve rapor
    hesaplarında modelin ilk tahmini değil, insanın onayladığı sınıf
    kullanılır. Ham tahmin `tespit.sinif` alanında ve islem_gecmisi'nde
    izlenebilirlik için korunur.
    """
    return func.coalesce(Tespit.duzeltilen_sinif, Tespit.sinif)


def sadece_malzeme(sorgu: Select) -> Select:
    """Malzeme olmayan sınıfları eler.

    `konteyner` (skip bin) atığın içinde bulunduğu kaptır, atık değildir.
    Miktara katılırsa sistem var olmayan bir malzeme kütlesi üretir.
    Bkz. docs/karar-kaydi.md K-007.

    Filtre GEÇERLİ sınıf üzerinden çalışır: uzman bir kaydı `konteyner`
    olarak düzelttiyse o kayıt da hesaptan çıkar.
    """
    return sorgu.where(gecerli_sinif().in_(tuple(malzeme_siniflari())))


def hesaba_girebilir(sorgu: Select) -> Select:
    """Miktar/harita/rapor hesaplarına girebilecek tespitler.

    İki filtrenin birleşimi. Hesap üreten her sorgu bunu kullanır.
    """
    return sadece_malzeme(sadece_dogrulanmis(sorgu))


def gorulebilir_alanlar(rol: Rol | None, kullanici_id: int) -> Select:
    """Rolün görebileceği enkaz alanları.

    Ana talimat Bölüm 5'teki tablo. Yetki kontrolü API katmanındadır;
    arayüzde gizleme yeterli değildir.
    """
    sorgu = select(EnkazAlani)
    if rol in TUM_SAHALARI_GORUR:
        return sorgu
    # Diğer roller yalnızca oluşturdukları ya da görüntü yükledikleri
    # sahaları görür.
    alt = select(Goruntu.enkaz_alani_id).where(Goruntu.yukleyen_id == kullanici_id)
    return sorgu.where(
        (EnkazAlani.olusturan_id == kullanici_id) | (EnkazAlani.id.in_(alt))
    )
