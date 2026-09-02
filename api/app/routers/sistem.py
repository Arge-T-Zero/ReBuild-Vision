"""Sistem durumu, sınıflar, harita ve işlem geçmişi."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import model_metrik_ozeti
from ..core.config import siniflar as sinif_tanimlari
from ..db import oturum
from ..core.permissions import GECMIS_GORUR
from ..deps import aktif_kullanici
from ..models import (
    EnkazAlani, Goruntu, IslemGecmisi, Kullanici, MiktarHesabi, Olcum,
    TehlikeliKayit, Tespit,
)
from ..schemas import IslemGecmisiCikti
from ..services import model_client
from ..services.queries import (
    gecerli_sinif, gorulebilir_alanlar, hesaba_girebilir,
)

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
        "model_metrikleri": model_metrik_ozeti(),
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

    Dağılım ayrıca ROLÜN GÖREBİLDİĞİ sahalarla sınırlanır. Bu olmadan,
    hiçbir saha göremeyen bir yıkım firması "0 enkaz alanı" görürken
    yanında sistemin tamamına ait malzeme kırılımını okuyordu: hem
    mantıksal tutarsızlık hem yetki sızıntısı.
    """
    # Uzman düzeltmesi model tahminini geçersiz kılar; gruplama GEÇERLİ
    # sınıf üzerinden yapılır.
    sinif = gecerli_sinif().label("sinif")
    kapsam = gorulebilir_alanlar(k.rol, k.id).with_only_columns(EnkazAlani.id)
    sorgu = hesaba_girebilir(
        select(sinif, func.count(Tespit.id))
        .join(Goruntu, Tespit.goruntu_id == Goruntu.id)
        .where(Goruntu.enkaz_alani_id.in_(kapsam))
    ).group_by(sinif)

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
    tespit_id: int | None = None,
    limit: int = 50,
    k: Kullanici = Depends(aktif_kullanici),
    db: AsyncSession = Depends(oturum),
):
    """İşlem geçmişi — kim, ne zaman, neyi değiştirdi.

    Rapor Bölüm 6, dördüncü yenilikçi yön. Arayüzde de görünür olmalıdır,
    yalnızca veri tabanında durmamalıdır.

    YETKİ İKİ KADEMELİDİR:

    `tespit_id` verilirse, o tespitin BÜTÜN hikâyesi döner: tespitin
    kendi kaydı artı ona bağlı ölçüm, miktar hesabı ve tehlikeli madde
    kayıtları. Yalnızca `kayit_tipi=tespit` ile süzmek yetmiyordu —
    ölçüm girildikten sonra "Bu tespitin geçmişi" paneli hâlâ sadece
    "tespit oluşturuldu" satırını gösteriyor, izlenebilirlik iddiası
    ekranda yarım kalıyordu.

    - **Tek bir kaydın geçmişi** (`kayit_tipi` + `kayit_id`, ya da
      `tespit_id` verilmiş):
      giriş yapmış herkes okuyabilir. Tespit detayındaki "Bu tespitin
      geçmişi" paneli buradan beslenir; ölçüm girebilen saha personelinin
      kendi girdiği kaydın izini görememesi izlenebilirlik iddiasıyla
      çelişirdi.
    - **Sistem geneli döküm** (filtresiz ya da yalnızca `kayit_tipi`):
      `GECMIS_GORUR` rolleriyle sınırlıdır. Bu döküm, kimin neyi
      değiştirdiğini sistemin tamamı için gösterir; salt okunur dış
      taraflara (yıkım firması, geri kazanım tesisi) açık olmamalıdır.

    Yetki API katmanında zorlanır: arayüzde sekmeyi gizlemek yetmez,
    uç nokta doğrudan çağrılabilir.
    """
    if kayit_id is None and tespit_id is None and k.rol not in GECMIS_GORUR:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Sistem geneli işlem geçmişini görme yetkiniz yok. "
            "Tek bir kaydın geçmişini o kaydın ekranından görebilirsiniz.",
        )
    sorgu = (
        select(IslemGecmisi, Kullanici.ad)
        # Dış birleştirme: kullanıcısı olmayan (sistem kaynaklı) kayıtlar
        # da listede kalmalıdır.
        .join(Kullanici, Kullanici.id == IslemGecmisi.kullanici_id, isouter=True)
        .order_by(IslemGecmisi.id.desc())
        .limit(min(limit, 200))
    )
    if tespit_id is not None:
        # Tespite BAĞLI kayıtların kimlikleri. Denetim tablosunda
        # "hangi tespite ait" diye bir sütun yok; ilişki, kaydın kendi
        # tablosundan türetilir.
        bagli = [
            (Olcum, "olcum"),
            (MiktarHesabi, "miktar_hesabi"),
            (TehlikeliKayit, "tehlikeli_kayit"),
        ]
        kosullar = [
            (IslemGecmisi.kayit_tipi == "tespit")
            & (IslemGecmisi.kayit_id == tespit_id)
        ]
        for model, tip in bagli:
            kosullar.append(
                (IslemGecmisi.kayit_tipi == tip)
                & IslemGecmisi.kayit_id.in_(
                    select(model.id).where(model.tespit_id == tespit_id)
                )
            )
        sorgu = sorgu.where(or_(*kosullar))
    else:
        if kayit_tipi:
            sorgu = sorgu.where(IslemGecmisi.kayit_tipi == kayit_tipi)
        if kayit_id is not None:
            sorgu = sorgu.where(IslemGecmisi.kayit_id == kayit_id)
    y = await db.execute(sorgu)
    return [
        IslemGecmisiCikti.model_validate(k).model_copy(update={"kullanici_ad": ad})
        for k, ad in y.all()
    ]
