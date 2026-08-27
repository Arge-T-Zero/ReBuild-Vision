"""İzlenebilirlik — otomatik işlem geçmişi.

Rapor Bölüm 6, dördüncü yenilikçi yön:
"Her kayıt için oluşturan kullanıcı, tarih, doğrulama durumu ve değişiklik
geçmişi saklanarak izlenebilirlik sağlanacaktır."

Bu modül elle çağrılmaz. SQLAlchemy olay dinleyicisi her yazma işlemini
yakalar — böylece bir uç nokta yazarken kayıt tutmayı unutmak MÜMKÜN
DEĞİLDİR.
"""
from __future__ import annotations

import contextvars
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import event, insert, inspect
from sqlalchemy.orm import Session

from ..models import IslemGecmisi

# İstek başına aktif kullanıcı. Middleware/bağımlılık tarafından set edilir.
aktif_kullanici_id: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "aktif_kullanici_id", default=None
)

# Kendi kendini kaydetmemesi için geçmiş tablosu hariç tutulur.
HARIC = {IslemGecmisi.__tablename__}

# Parola özeti gibi alanlar geçmişe yazılmaz.
GIZLI_ALANLAR = {"sifre_hash"}


def _serilestir(deger):
    if isinstance(deger, (datetime, date)):
        return deger.isoformat()
    if isinstance(deger, Decimal):
        return float(deger)
    if isinstance(deger, (str, int, float, bool)) or deger is None:
        return deger
    return str(deger)


def _anlik(nesne) -> dict:
    """Nesnenin sütun değerlerini sözlüğe çevirir.

    Geometry sütunları atlanır: WKB gösterimi geçmiş kaydında okunabilir
    değildir ve gereksiz yer kaplar.
    """
    d = {}
    for sutun in inspect(nesne).mapper.columns:
        ad = sutun.key
        if ad in GIZLI_ALANLAR:
            continue
        if sutun.type.__class__.__name__ == "Geometry":
            continue
        d[ad] = _serilestir(getattr(nesne, ad, None))
    return d


def _degisiklikler(nesne) -> tuple[dict, dict]:
    eski, yeni = {}, {}
    durum = inspect(nesne)
    for sutun in durum.mapper.columns:
        ad = sutun.key
        if ad in GIZLI_ALANLAR or sutun.type.__class__.__name__ == "Geometry":
            continue
        gecmis = durum.attrs[ad].history
        if gecmis.has_changes():
            eski[ad] = _serilestir(gecmis.deleted[0]) if gecmis.deleted else None
            yeni[ad] = _serilestir(gecmis.added[0]) if gecmis.added else None
    return eski, yeni


@event.listens_for(Session, "after_flush")
def _kaydet(session: Session, flush_baglami) -> None:
    """Yazma işlemlerini işlem geçmişine yazar.

    `after_flush` kullanılır çünkü `before_flush` anında yeni kayıtların
    id değeri henüz atanmamış olur ve geçmiş kaydı satıra bağlanamaz.

    Geçmiş satırları ORM birim-iş döngüsüne değil, doğrudan Core insert
    ile yazılır: `after_flush` içinde session'a yeni ORM nesnesi eklemek
    aynı işlemde yazılacağını garanti etmez.
    """
    kullanici = aktif_kullanici_id.get()
    satirlar: list[dict] = []

    for nesne in session.new:
        if nesne.__tablename__ in HARIC:
            continue
        satirlar.append({
            "kayit_tipi": nesne.__tablename__,
            "kayit_id": getattr(nesne, "id", None),
            "islem": "olusturma",
            "eski_deger": None,
            "yeni_deger": _anlik(nesne),
            "kullanici_id": kullanici,
        })

    for nesne in session.dirty:
        if nesne.__tablename__ in HARIC:
            continue
        eski, yeni = _degisiklikler(nesne)
        if not yeni:
            continue
        satirlar.append({
            "kayit_tipi": nesne.__tablename__,
            "kayit_id": getattr(nesne, "id", None),
            "islem": "guncelleme",
            "eski_deger": eski,
            "yeni_deger": yeni,
            "kullanici_id": kullanici,
        })

    for nesne in session.deleted:
        if nesne.__tablename__ in HARIC:
            continue
        satirlar.append({
            "kayit_tipi": nesne.__tablename__,
            "kayit_id": getattr(nesne, "id", None),
            "islem": "silme",
            "eski_deger": _anlik(nesne),
            "yeni_deger": None,
            "kullanici_id": kullanici,
        })

    if satirlar:
        session.execute(insert(IslemGecmisi), satirlar)
