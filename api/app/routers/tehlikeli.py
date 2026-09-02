"""Tehlikeli madde — TEŞHİS DEĞİL, YÖNLENDİRME KAYDI.

Ana talimat Bölüm 1.2 / Rapor 3.5:
"Asbest ve benzeri tehlikeli maddeler görüntü üzerinden teşhis
edilmeyecek."

Bu yönlendiricide bilinçli olarak BULUNMAYAN şeyler:
- Model çıktısından tehlikeli madde üreten hiçbir kod yolu
- Olasılık, güven skoru, risk seviyesi veya madde adı tahmini
- "Güvenli" / "tehlikesiz" değerlendirmesi döndüren hiçbir uç nokta

Kayıt her zaman bir İNSAN tarafından açılır ve laboratuvar sonucunu da
insan girer.

Rapor 12: analiz sonucu bulunmayan alan için "güvenli" değerlendirmesi de
yapılmaz — yokluk, güvenlik anlamına gelmez. Bu nedenle listeleme uç
noktası "kayıt yok" durumunu güvenlik olarak sunmaz; yalnızca kaydın
bulunmadığını söyler.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.permissions import (
    INCELEMEYE_YONLENDIREBILIR,
    LAB_SONUCU_GIREBILIR,
)
from ..db import oturum
from ..deps import aktif_kullanici, rol_gerekli
from ..models import Kullanici, TehlikeliDurum, TehlikeliKayit, Tespit
from ..schemas import TehlikeliCikti, TehlikeliIstek
from ..services.queries import gorulebilir_tespitler

router = APIRouter(prefix="/tehlikeli", tags=["tehlikeli madde"])

# Bu metin, kayıt bulunmayan durumda döner ve arayüzde aynen gösterilir.
YOKLUK_ACIKLAMASI = (
    "Bu tespit için laboratuvar/uzman inceleme kaydı bulunmuyor. "
    "Kayıt bulunmaması, alanın tehlikeli madde içermediği anlamına GELMEZ. "
    "Sistem tehlikeli madde teşhisi yapmaz."
)


@router.post("", response_model=TehlikeliCikti,
             status_code=status.HTTP_201_CREATED)
async def yonlendir(
    istek: TehlikeliIstek,
    k: Kullanici = Depends(rol_gerekli(INCELEMEYE_YONLENDIREBILIR)),
    db: AsyncSession = Depends(oturum),
):
    """Bir tespiti uzman/laboratuvar incelemesine yönlendirir.

    Bu bir TEŞHİS DEĞİLDİR. Kaydın anlamı yalnızca "bu tespite bakılsın"dır.
    """
    t = await db.get(Tespit, istek.tespit_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tespit bulunamadı")

    # Laboratuvar sonucu girmek ayrı bir yetkidir.
    if istek.durum == TehlikeliDurum.LAB_SONUCU_VAR:
        if k.rol not in LAB_SONUCU_GIREBILIR:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Laboratuvar sonucu girme yetkiniz yok",
            )
        if not (istek.lab_sonucu_notu or "").strip():
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Laboratuvar sonucu için not zorunludur — sonucu insan girer",
            )

    kayit = TehlikeliKayit(
        tespit_id=istek.tespit_id,
        durum=istek.durum,
        lab_sonucu_notu=istek.lab_sonucu_notu,
        giren_id=k.id,
    )
    db.add(kayit)
    await db.commit()
    await db.refresh(kayit)
    return kayit


@router.get("/tespit/{tespit_id}")
async def kayitlar(
    tespit_id: int,
    k: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    """Bir tespitin inceleme kayıtları.

    Kayıt yoksa `kayitlar: []` döner ve `aciklama` alanı yokluğun güvenlik
    anlamına gelmediğini AÇIKÇA söyler. Arayüz bu metni gösterir.
    """
    # Tespit rolün kapsamı dışındaysa kayıtları da dönmez. Yokluk
    # açıklaması yine verilir: "kayıt yok" ile "göremiyorsun" arasındaki
    # farkı sızdırmamak, ikisini de aynı biçimde yanıtlamak demektir —
    # ve yokluğun güvenlik anlamına gelmediği her iki durumda da doğru.
    gorunur = (await db.execute(
        gorulebilir_tespitler(k.rol, k.id).where(Tespit.id == tespit_id)
    )).scalar_one_or_none()
    if not gorunur:
        return {
            "tespit_id": tespit_id,
            "kayitlar": [],
            "aciklama": YOKLUK_ACIKLAMASI,
        }

    y = await db.execute(
        select(TehlikeliKayit, Kullanici.ad)
        .join(Kullanici, Kullanici.id == TehlikeliKayit.giren_id, isouter=True)
        .where(TehlikeliKayit.tespit_id == tespit_id)
        .order_by(TehlikeliKayit.id.desc())
    )
    kayit_listesi = [
        TehlikeliCikti.model_validate(x).model_copy(update={"giren_ad": ad})
        for x, ad in y.all()
    ]
    return {
        "tespit_id": tespit_id,
        "kayitlar": kayit_listesi,
        "aciklama": None if kayit_listesi else YOKLUK_ACIKLAMASI,
        # Bu alan bilinçli olarak "guvenli" DEĞİL, "degerlendirilmedi"dir.
        "degerlendirme": "degerlendirilmedi" if not kayit_listesi else "kayit_var",
    }
