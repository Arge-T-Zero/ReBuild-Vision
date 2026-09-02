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

    Bir sınıf, atığın kendisi değil atığın içinde bulunduğu kap ya da
    zemin olabilir (ör. hurda konteyneri). Miktara katılırsa sistem var
    olmayan bir malzeme kütlesi üretir. Ayıklama, sınıf adına göre değil
    `siniflar.json` içindeki `malzeme_mi` alanına göre yapılır — sınıf
    listesi değişince kural kendiliğinden doğru kalır.
    Bkz. docs/karar-kaydi.md K-007.

    02.09.2026 itibarıyla beş sınıfın beşi de malzemedir, yani bu filtre
    bugün hiçbir kaydı elemiyor. Kaldırılmadı: eleme mantığının yokluğu,
    malzeme olmayan bir sınıf eklendiği gün sessiz bir hata olurdu.

    Filtre GEÇERLİ sınıf üzerinden çalışır: uzman bir kaydı malzeme
    olmayan bir sınıfa düzelttiyse o kayıt da hesaptan çıkar.
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

    if rol == Rol.UZMAN:
        # Doğrulayıcı uzman, rapordaki tanıma göre "atandığı sahaları"
        # görür. Uzmana saha atama akışı henüz uygulanmadığı için
        # görünürlük İŞ ÜZERİNDEN türetilir: uzman, inceleme bekleyen ya da
        # kendisinin doğruladığı bir tespit içeren sahaları görür.
        #
        # Bu bilinçli bir ara çözümdür; "her şeyi görsün" demekten daha
        # dar, "hiçbir şeyi görmesin" demekten kullanışlıdır. Kuyruktan
        # doğrulama yapan uzmanın tespiti bağlamında görebilmesi,
        # ölçüm ve laboratuvar kaydı ekleyebilmesi için gereklidir.
        # Bkz. docs/mimari.md — bilinen mimari boşluklar.
        uzman_alt = (
            select(Goruntu.enkaz_alani_id)
            .join(Tespit, Tespit.goruntu_id == Goruntu.id)
            .where(
                Tespit.inceleme_gerekli.is_(True)
                | (Tespit.dogrulayan_id == kullanici_id)
                | (Tespit.dogrulama_durumu == DogrulamaDurumu.BEKLEMEDE)
            )
        )
        return sorgu.where(EnkazAlani.id.in_(uzman_alt))

    if rol == Rol.SAHA:
        # Saha personeli TANIMLI BÜTÜN sahaları görür.
        #
        # Bu, Bölüm 5 tablosundaki "kendi sahası" tanımından DAHA GENİŞTİR
        # ve bilinçli bir ara çözümdür. Gerekçe: saha personeline saha
        # atama akışı henüz yazılmadı. "Kendi sahası" kuralı atama olmadan
        # uygulandığında rol tamamen çalışmaz hale geliyordu — saha
        # personeli bir sahaya görüntü yükleyebilmek için o sahaya daha
        # önce görüntü yüklemiş olmak zorunda kalıyordu (tavuk–yumurta).
        # Rolün tek işi görüntü yüklemek olduğu için bu, rolü işlevsiz
        # bırakıyordu.
        #
        # Sızıntı yüzeyi dar tutuldu: saha personeli saha LİSTESİNİ görür,
        # rapor alamaz ve doğrulama yapamaz. Atama tablosu eklendiğinde bu
        # dal silinip yerine atama sorgusu gelmelidir.
        # Bkz. docs/karar-kaydi.md K-014.
        return sorgu

    # Kalan roller (yikim, tesis) yalnızca oluşturdukları ya da görüntü
    # yükledikleri sahaları görür. Bu roller dış taraflardır (yıklım
    # firması, geri kazanım tesisi); atama olmadan sistemin tamamını
    # görmeleri gerçek bir yetki sızıntısı olurdu. Atama akışı gelene
    # kadar boş liste görmeleri DOĞRU davranıştır; arayüz bunu "sistemde
    # saha yok" diye değil, "size saha atanmamış" diye anlatır.
    alt = select(Goruntu.enkaz_alani_id).where(Goruntu.yukleyen_id == kullanici_id)
    return sorgu.where(
        (EnkazAlani.olusturan_id == kullanici_id) | (EnkazAlani.id.in_(alt))
    )
