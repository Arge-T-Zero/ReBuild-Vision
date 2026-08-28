"""Veri modeli — ana talimat Bölüm 4.

Bölüm 1'deki dört ihlal edilemez kural burada, veri katmanında zorlanır.
Arayüzde gizlemek yeterli değildir.
"""
from __future__ import annotations

import enum
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core.permissions import OnayDurumu, Rol
from .db import Temel

SRID = 4326


def _simdi() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now())


# --------------------------------------------------------------------------
# Sabit değer kümeleri
# --------------------------------------------------------------------------

class DogrulamaDurumu(str, enum.Enum):
    """Rapor gövde metni esas alınmıştır (docs/karar-kaydi.md K-004).

    Şekil 1'deki 'reddet' bilinçli olarak YOKTUR: bir tespiti reddetmek
    kaydın bilgi değerini yok eder, 'belirsiz' ise kaydı izlenebilir
    tutarak ikinci incelemeye açık bırakır.
    """
    BEKLEMEDE = "beklemede"
    ONAYLANDI = "onaylandi"
    DUZELTILDI = "duzeltildi"
    BELIRSIZ = "belirsiz"


class OlcumTuru(str, enum.Enum):
    ALAN = "alan"
    HACIM = "hacim"
    AGIRLIK = "agirlik"


class TehlikeliDurum(str, enum.Enum):
    """DİKKAT — ana talimat Bölüm 1.2.

    Bu kümede 'guvenli', 'tehlikesiz' veya herhangi bir olasılık değeri
    BULUNMAZ ve EKLENMEZ. Sistem tehlikeli madde teşhisi yapmaz; yalnızca
    uzman/laboratuvar incelemesine yönlendirildiğini kaydeder. Analiz
    sonucu bulunmayan alan için 'güvenli' değerlendirmesi de yapılmaz —
    yokluk, güvenlik anlamına gelmez.
    """
    INCELEMEYE_YONLENDIRILDI = "incelemeye_yonlendirildi"
    LAB_SONUCU_VAR = "lab_sonucu_var"


class ErisimDurumu(str, enum.Enum):
    ACIK = "acik"
    KISITLI = "kisitli"
    KAPALI = "kapali"


# --------------------------------------------------------------------------
# Tablolar
# --------------------------------------------------------------------------

class Kullanici(Temel):
    __tablename__ = "kullanici"

    id: Mapped[int] = mapped_column(primary_key=True)
    eposta: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    sifre_hash: Mapped[str] = mapped_column(String(255))
    ad: Mapped[str] = mapped_column(String(200))

    # Kullanıcı kayıt olurken kendi rolünü SEÇEMEZ (Brief 3).
    # Kayıt sonrası onay_durumu=beklemede ile başlar, rolü yönetici atar.
    rol: Mapped[Rol | None] = mapped_column(
        Enum(Rol, name="rol_turu", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    onay_durumu: Mapped[OnayDurumu] = mapped_column(
        Enum(OnayDurumu, name="onay_durumu_turu",
             values_callable=lambda e: [x.value for x in e]),
        default=OnayDurumu.BEKLEMEDE,
        server_default=OnayDurumu.BEKLEMEDE.value,
    )
    olusturma_tarihi: Mapped[datetime] = _simdi()


class EnkazAlani(Temel):
    __tablename__ = "enkaz_alani"

    id: Mapped[int] = mapped_column(primary_key=True)
    ad: Mapped[str] = mapped_column(String(200))
    konum = mapped_column(Geometry("POINT", srid=SRID), nullable=True)
    sinir = mapped_column(Geometry("POLYGON", srid=SRID), nullable=True)
    erisim_durumu: Mapped[ErisimDurumu] = mapped_column(
        Enum(ErisimDurumu, name="erisim_durumu_turu",
             values_callable=lambda e: [x.value for x in e]),
        default=ErisimDurumu.ACIK,
        server_default=ErisimDurumu.ACIK.value,
    )
    sorumlu: Mapped[str | None] = mapped_column(String(200), nullable=True)
    inceleme_tarihi: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    olusturan_id: Mapped[int] = mapped_column(ForeignKey("kullanici.id"))
    olusturma_tarihi: Mapped[datetime] = _simdi()

    goruntuler: Mapped[list["Goruntu"]] = relationship(back_populates="alan")


class Goruntu(Temel):
    __tablename__ = "goruntu"

    id: Mapped[int] = mapped_column(primary_key=True)
    enkaz_alani_id: Mapped[int] = mapped_column(
        ForeignKey("enkaz_alani.id", ondelete="CASCADE"), index=True
    )
    dosya_yolu: Mapped[str] = mapped_column(String(500))
    konum = mapped_column(Geometry("POINT", srid=SRID), nullable=True)
    cekim_tarihi: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cihaz: Mapped[str | None] = mapped_column(String(200), nullable=True)
    kalite_durumu: Mapped[str | None] = mapped_column(String(50), nullable=True)
    kalite_notu: Mapped[str | None] = mapped_column(Text, nullable=True)
    genislik: Mapped[int | None] = mapped_column(Integer, nullable=True)
    yukseklik: Mapped[int | None] = mapped_column(Integer, nullable=True)
    yukleyen_id: Mapped[int] = mapped_column(ForeignKey("kullanici.id"))
    olusturma_tarihi: Mapped[datetime] = _simdi()

    alan: Mapped["EnkazAlani"] = relationship(back_populates="goruntuler")
    tespitler: Mapped[list["Tespit"]] = relationship(back_populates="goruntu")


class Tespit(Temel):
    __tablename__ = "tespit"

    id: Mapped[int] = mapped_column(primary_key=True)
    goruntu_id: Mapped[int] = mapped_column(
        ForeignKey("goruntu.id", ondelete="CASCADE"), index=True
    )
    sinif: Mapped[str] = mapped_column(String(50), index=True)
    guven_skoru: Mapped[float] = mapped_column(Float)
    bbox = mapped_column(JSONB)

    # Ana talimat Bölüm 4.3: kutuların hangi koordinat uzayında verildiği
    # belirsiz bırakılmaz. En sık hata kaynağı burasıdır.
    bbox_format: Mapped[str] = mapped_column(String(50), nullable=False)

    konum = mapped_column(Geometry("POINT", srid=SRID), nullable=True)

    dogrulama_durumu: Mapped[DogrulamaDurumu] = mapped_column(
        Enum(DogrulamaDurumu, name="dogrulama_durumu_turu",
             values_callable=lambda e: [x.value for x in e]),
        default=DogrulamaDurumu.BEKLEMEDE,
        server_default=DogrulamaDurumu.BEKLEMEDE.value,
        index=True,
    )
    dogrulayan_id: Mapped[int | None] = mapped_column(
        ForeignKey("kullanici.id"), nullable=True
    )
    dogrulama_tarihi: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duzeltilen_sinif: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Model 'uzman incelemesi gerekli' dediyse otomatik olarak kuyruğa
    # düşer — kullanıcının bir şey yapmasına gerek yoktur (talimat 7.3).
    inceleme_gerekli: Mapped[bool] = mapped_column(
        default=False, server_default="false", index=True
    )
    olusturma_tarihi: Mapped[datetime] = _simdi()

    goruntu: Mapped["Goruntu"] = relationship(back_populates="tespitler")
    olcumler: Mapped[list["Olcum"]] = relationship(back_populates="tespit")

    __table_args__ = (
        CheckConstraint("guven_skoru >= 0 AND guven_skoru <= 1",
                        name="ck_tespit_guven_araligi"),
        CheckConstraint("bbox_format <> ''", name="ck_tespit_bbox_format_dolu"),
    )


class Olcum(Temel):
    """Saha ölçümü — miktar hesabının TEK ön koşulu.

    Bu tabloda kayıt yoksa ilgili tespit için miktar_hesabi satırı
    oluşturulamaz (talimat Bölüm 1.1).
    """
    __tablename__ = "olcum"

    id: Mapped[int] = mapped_column(primary_key=True)
    tespit_id: Mapped[int] = mapped_column(
        ForeignKey("tespit.id", ondelete="CASCADE"), index=True
    )
    tur: Mapped[OlcumTuru] = mapped_column(
        Enum(OlcumTuru, name="olcum_turu",
             values_callable=lambda e: [x.value for x in e])
    )
    deger: Mapped[float] = mapped_column(Float)
    birim: Mapped[str] = mapped_column(String(20))
    yontem: Mapped[str] = mapped_column(String(200))
    giren_id: Mapped[int] = mapped_column(ForeignKey("kullanici.id"))
    tarih: Mapped[datetime] = _simdi()

    # Çevrimdışı eşitleme: mobil cihazda üretilen kimlik. Ağ koptuğunda
    # istemci isteği tekrarlar ama sonucu bilemez; benzersizlik kısıtı
    # aynı ölçümün iki kez yazılmasını engeller.
    yerel_kimlik: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )

    tespit: Mapped["Tespit"] = relationship(back_populates="olcumler")

    __table_args__ = (
        CheckConstraint("deger > 0", name="ck_olcum_deger_pozitif"),
    )


class MiktarHesabi(Temel):
    """Miktar — ASLA tek bir kesin değer olarak tutulmaz.

    Ana talimat Bölüm 1.1 ve Rapor Bölüm 4 (üçüncü yenilikçi yön):
    belirsizlik aralığı ve kullanılan yöntem birlikte saklanır.
    Bu, veri katmanında NOT NULL ile zorlanır — 'tek değerli miktar'
    fiziksel olarak yazılamaz.

    Ayrıca: bu tabloda satır olmaması, miktarın SIFIR olduğu anlamına
    gelmez; HESAPLANMADIĞI anlamına gelir. Arayüz bunu böyle gösterir.
    """
    __tablename__ = "miktar_hesabi"

    id: Mapped[int] = mapped_column(primary_key=True)
    tespit_id: Mapped[int] = mapped_column(
        ForeignKey("tespit.id", ondelete="CASCADE"), unique=True, index=True
    )
    deger_alt: Mapped[float] = mapped_column(Float, nullable=False)
    deger_ust: Mapped[float] = mapped_column(Float, nullable=False)
    birim: Mapped[str] = mapped_column(String(20), nullable=False)
    kullanilan_katsayi: Mapped[float] = mapped_column(Float, nullable=False)
    katsayi_kaynagi: Mapped[str] = mapped_column(String(300), nullable=False)
    yontem: Mapped[str] = mapped_column(String(300), nullable=False)
    tarih: Mapped[datetime] = _simdi()

    __table_args__ = (
        CheckConstraint("deger_alt <= deger_ust", name="ck_miktar_aralik_tutarli"),
        CheckConstraint("deger_alt >= 0", name="ck_miktar_alt_negatif_degil"),
        # Belirsizlik aralığı gerçekten aralık olmalı; alt=üst bir "kesin
        # değer" kaçamağıdır ve engellenir.
        CheckConstraint("deger_ust > deger_alt", name="ck_miktar_araliksiz_degil"),
    )


class TehlikeliKayit(Temel):
    """Tehlikeli madde — TEŞHİS DEĞİL, YÖNLENDİRME KAYDI.

    Ana talimat Bölüm 1.2. Bu tabloda bilinçli olarak BULUNMAYAN alanlar:
    olasılık, güven skoru, madde adı tahmini, risk seviyesi, 'güvenli'
    değerlendirmesi. Sonucu model değil İNSAN girer.
    """
    __tablename__ = "tehlikeli_kayit"

    id: Mapped[int] = mapped_column(primary_key=True)
    tespit_id: Mapped[int] = mapped_column(
        ForeignKey("tespit.id", ondelete="CASCADE"), index=True
    )
    durum: Mapped[TehlikeliDurum] = mapped_column(
        Enum(TehlikeliDurum, name="tehlikeli_durum_turu",
             values_callable=lambda e: [x.value for x in e])
    )
    lab_sonucu_notu: Mapped[str | None] = mapped_column(Text, nullable=True)
    giren_id: Mapped[int] = mapped_column(ForeignKey("kullanici.id"))
    tarih: Mapped[datetime] = _simdi()


class IslemGecmisi(Temel):
    """İzlenebilirlik — opsiyonel değildir (Rapor Bölüm 6, 4. yenilikçi yön).

    Her yazma işlemi buraya düşer. Elle çağrılmaz; SQLAlchemy olay
    dinleyicisi otomatik yazar (api/app/services/denetim.py) — böylece
    unutulamaz.
    """
    __tablename__ = "islem_gecmisi"

    id: Mapped[int] = mapped_column(primary_key=True)
    kayit_tipi: Mapped[str] = mapped_column(String(60), index=True)
    kayit_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    islem: Mapped[str] = mapped_column(String(20))  # olusturma | guncelleme | silme
    eski_deger = mapped_column(JSONB, nullable=True)
    yeni_deger = mapped_column(JSONB, nullable=True)
    kullanici_id: Mapped[int | None] = mapped_column(
        ForeignKey("kullanici.id"), nullable=True
    )
    tarih: Mapped[datetime] = _simdi()
