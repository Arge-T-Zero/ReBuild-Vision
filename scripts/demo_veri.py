#!/usr/bin/env python3
"""Demo verisi — şartname Madde 10.7.

"Demo ortamlarında anonimleştirilmiş, sentetik veya maskeleme uygulanmış
veri kullanılması esastır."

Gerçek e-posta adresi hiçbir yerde kullanılmaz; tüm hesaplar @demo.local
alan adındadır ve gerçek bir posta kutusuna karşılık gelmez.

⚠️ BU BETİK 02.09.2026'YA KADAR JÜRİYE BOŞ BİR SİSTEM BIRAKIYORDU.

Yalnızca yedi hesap ve bir enkaz alanı üretiyordu; tek bir görüntü ya da
tespit yoktu. `docker compose up` çalıştıran bir jüri üyesi giriş yapıyor
ve boş listeler görüyordu. Projenin en güçlü anları — ölçüm yokken
miktarın BOŞ kalması, uzman düzeltmesinin modeli geçersiz kılması,
belirsizlik aralığı, rol kapsamı — kendiliğinden hiç önüne gelmiyordu.

Aşağıdaki senaryo bunu kapatır: dört temel kuralın her biri, hiçbir şey
yapılmadan, ilk ekranda görünür.

SENTETİKLİK GİZLENMEZ
Her saha adı "(sentetik)" taşır, görüntüler deponun kendi sentetik
görselleridir (`web/public/gorseller/README.md`) ve tespit kutuları elle
yazılmıştır — hiçbiri gerçek bir model çıktısı değildir.
"""
from __future__ import annotations

import asyncio
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEPO_KOKU = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPO_KOKU))

from sqlalchemy import select  # noqa: E402

from api.app.core.config import ayarlar  # noqa: E402
from api.app.core.permissions import OnayDurumu, Rol  # noqa: E402
from api.app.core.security import parola_ozetle  # noqa: E402
from api.app.db import OturumUret  # noqa: E402
from api.app.geo import nokta, poligon  # noqa: E402
from api.app.models import (  # noqa: E402
    DogrulamaDurumu, EnkazAlani, ErisimDurumu, Goruntu, Kullanici,
    MiktarHesabi, Olcum, OlcumTuru, Tespit,
)
from api.app.services import miktar as miktar_servisi  # noqa: E402

DEMO_PAROLA = "demo1234"
BBOX_BICIMI = "pixel_absolute_original"

HESAPLAR = [
    ("yonetici@demo.local", "Demo Yönetici",        Rol.YONETICI),
    ("saha@demo.local",     "Demo Saha Personeli",  Rol.SAHA),
    ("uzman@demo.local",    "Demo Doğrulayıcı Uzman", Rol.UZMAN),
    ("belediye@demo.local", "Demo Belediye Yetkilisi", Rol.BELEDIYE),
    ("afad@demo.local",     "Demo AFAD Yetkilisi",  Rol.AFAD),
    ("yikim@demo.local",    "Demo Yıkım Firması",   Rol.YIKIM),
    ("tesis@demo.local",    "Demo Tesis Operatörü", Rol.TESIS),
]

# Sentetik konumlar — hiçbiri gerçek bir enkaz sahası değildir.
ALANLAR = [
    {
        "ad": "Demo Sahası A (sentetik)",
        "sorumlu": "Demo Belediye",
        "erisim": ErisimDurumu.ACIK,
        "konum": (40.9862, 40.5219),
        "sinir": [(40.9872, 40.5205), (40.9872, 40.5233),
                  (40.9852, 40.5233), (40.9852, 40.5205)],
    },
    {
        "ad": "Demo Sahası B — Çarşı (sentetik)",
        "sorumlu": "Demo Belediye",
        "erisim": ErisimDurumu.KISITLI,
        "konum": (40.9930, 40.5100),
        "sinir": None,
    },
    {
        "ad": "Demo Sahası C — Sanayi (sentetik)",
        "sorumlu": "Demo Belediye",
        "erisim": ErisimDurumu.KAPALI,
        "konum": (40.9790, 40.5340),
        "sinir": None,
    },
]

# Sentetik görüntüler: deponun kendi görselleri kopyalanır.
KAYNAK_GORSELLER = [
    "ornek-enkaz-1.webp", "ornek-enkaz-2.webp", "ornek-enkaz-3.webp",
]


def _kutu(x: int, y: int, w: int, h: int) -> dict:
    return {"x": x, "y": y, "w": w, "h": h}


# Senaryo — her satır bir tespit. Dört kural da burada görünür hâle gelir.
#
#   olcum:      (tür, değer, birim, yöntem) ya da None → miktar BOŞ kalır
#   dogrulama:  beklemede / onaylandi / duzeltildi / belirsiz
#
# `ahsap` ve `metal` katsayıları kaynaklıdır (katsayilar.json v0.3), yani
# ölçüm girildiğinde miktar ARALIKLA hesaplanır. `beton_tugla`, `cam` ve
# `seramik` kapalıdır: ölçüm olsa bile miktar üretilmez ve sebebi yazılır
# — bu da bir kural gösterimidir, eksiklik değil.
SENARYO = [
    # --- Saha A · 1. görüntü ------------------------------------------
    # Kural 1 + belirsizlik aralığı: ölçüm var, katsayı kaynaklı.
    dict(alan=0, goruntu=0, sinif="ahsap", guven=0.9137, kutu=(120, 90, 300, 210),
         dogrulama="onaylandi",
         olcum=(OlcumTuru.HACIM, 40.0, "m3", "Şerit metre ile kaba hacim")),
    # Kural 1'in EN GÜÇLÜ hâli: ölçüm YOK → miktar alanı boş kalır.
    dict(alan=0, goruntu=0, sinif="metal", guven=0.8412, kutu=(460, 180, 220, 160),
         dogrulama="onaylandi", olcum=None),
    # Kural 4: doğrulanmamış ön tahmin hiçbir hesaba girmez.
    dict(alan=0, goruntu=0, sinif="beton_tugla", guven=0.7765, kutu=(60, 340, 380, 240),
         dogrulama="beklemede", olcum=None),

    # --- Saha A · 2. görüntü ------------------------------------------
    # Düşük güven → uzman kuyruğuna KENDİLİĞİNDEN düşer (inceleme_gerekli).
    dict(alan=0, goruntu=1, sinif="cam", guven=0.3184, kutu=(200, 120, 180, 150),
         dogrulama="beklemede", olcum=None, inceleme=True),
    # Uzman düzeltmesi: model "seramik" dedi, uzman "beton_tugla" yaptı.
    # Ham tahmin izlenebilirlik için saklanır, geçerli sınıf uzmanınkidir.
    dict(alan=0, goruntu=1, sinif="seramik", guven=0.6023, kutu=(420, 300, 260, 190),
         dogrulama="duzeltildi", duzeltilen="beton_tugla", olcum=None),

    # --- Saha B (kısıtlı erişim) --------------------------------------
    # İkinci kaynaklı katsayı: metal, ağırlık ölçümüyle — katsayı kullanılmaz.
    dict(alan=1, goruntu=2, sinif="metal", guven=0.8890, kutu=(150, 200, 340, 250),
         dogrulama="onaylandi",
         olcum=(OlcumTuru.AGIRLIK, 3.5, "ton", "Kantar fişi (sentetik)")),
    # Katsayısı KAPALI bir sınıfta ölçüm var — miktar yine üretilmez ve
    # sebebi yazılır. "Ölçüm girildi ama sayı çıkmadı" da bir kuraldır.
    dict(alan=1, goruntu=2, sinif="beton_tugla", guven=0.8051, kutu=(520, 120, 300, 320),
         dogrulama="onaylandi",
         olcum=(OlcumTuru.HACIM, 62.0, "m3", "Şerit metre ile kaba hacim")),
    # "Belirsiz" — reddetmek yerine ikinci incelemeye açık bırakma (K-004).
    dict(alan=1, goruntu=2, sinif="cam", guven=0.4471, kutu=(80, 480, 190, 140),
         dogrulama="belirsiz", olcum=None, inceleme=True),
]


async def _gorselleri_kopyala() -> list[str]:
    """Sentetik görselleri yükleme klasörüne kopyalar, yollarını döner.

    Görüntüler `/dosya` üzerinden sunulur; kaynak dosya bulunamazsa kayıt
    yine oluşturulur (yol yazılıdır, önizleme boş kalır) — demo verisi
    yüzünden açılış durmaz.
    """
    hedef_klasor = ayarlar().yukleme_yolu
    hedef_klasor.mkdir(parents=True, exist_ok=True)
    yollar = []
    for i, ad in enumerate(KAYNAK_GORSELLER):
        kaynak = DEPO_KOKU / "web/public/gorseller" / ad
        hedef_ad = f"demo_sentetik_{i + 1}{Path(ad).suffix}"
        hedef = hedef_klasor / hedef_ad
        if kaynak.is_file() and not hedef.exists():
            shutil.copyfile(kaynak, hedef)
        yollar.append(hedef_ad)
    return yollar


async def main() -> None:
    eklenen: list[str] = []

    async with OturumUret() as db:
        for eposta, ad, rol in HESAPLAR:
            if await db.scalar(select(Kullanici).where(Kullanici.eposta == eposta)):
                continue
            db.add(Kullanici(
                eposta=eposta,
                sifre_hash=parola_ozetle(DEMO_PAROLA),
                ad=ad,
                rol=rol,
                onay_durumu=OnayDurumu.ONAYLANDI,
            ))
            eklenen.append(eposta)
        await db.commit()

        # Rol onay akışını demoda gösterebilmek için onay bekleyen bir hesap.
        bekleyen = "yeni.kullanici@demo.local"
        if not await db.scalar(select(Kullanici).where(Kullanici.eposta == bekleyen)):
            db.add(Kullanici(
                eposta=bekleyen,
                sifre_hash=parola_ozetle(DEMO_PAROLA),
                ad="Demo Onay Bekleyen",
                rol=None,
                onay_durumu=OnayDurumu.BEKLEMEDE,
            ))
            await db.commit()
            eklenen.append(f"{bekleyen} (onay bekliyor)")

        belediye = await db.scalar(
            select(Kullanici).where(Kullanici.eposta == "belediye@demo.local"))
        saha = await db.scalar(
            select(Kullanici).where(Kullanici.eposta == "saha@demo.local"))
        uzman = await db.scalar(
            select(Kullanici).where(Kullanici.eposta == "uzman@demo.local"))

        # --- Sahalar --------------------------------------------------
        # Betik yeniden çalıştırılabilir olmalı: ilk saha zaten varsa
        # senaryo bir daha kurulmaz, yoksa mükerrer tespit birikir.
        if await db.scalar(
            select(EnkazAlani).where(EnkazAlani.ad == ALANLAR[0]["ad"])
        ):
            print("Demo verisi zaten mevcut; senaryo yeniden kurulmadı.")
            print(f"\nTüm demo hesaplarının parolası: {DEMO_PAROLA}")
            return

        alanlar = []
        for t in ALANLAR:
            a = EnkazAlani(
                ad=t["ad"],
                sorumlu=t["sorumlu"],
                erisim_durumu=t["erisim"],
                olusturan_id=belediye.id,
            )
            a.konum = nokta(*t["konum"])
            if t["sinir"]:
                a.sinir = poligon(t["sinir"])
            db.add(a)
            alanlar.append(a)
        await db.flush()
        eklenen += [t["ad"] for t in ALANLAR]

        # --- Görüntüler -----------------------------------------------
        yollar = await _gorselleri_kopyala()
        simdi = datetime.now(timezone.utc)
        goruntuler = []
        for i, (alan_ix, saat) in enumerate([(0, 6), (0, 5), (1, 3)]):
            g = Goruntu(
                enkaz_alani_id=alanlar[alan_ix].id,
                dosya_yolu=yollar[i],
                genislik=1200,
                yukseklik=800,
                cekim_tarihi=simdi - timedelta(hours=saat),
                cihaz="Sentetik demo görüntüsü",
                yukleyen_id=saha.id,
            )
            g.konum = nokta(*ALANLAR[alan_ix]["konum"])
            db.add(g)
            goruntuler.append(g)
        await db.flush()

        # --- Tespitler, ölçümler, miktarlar ---------------------------
        tespitler = []
        for k in SENARYO:
            t = Tespit(
                goruntu_id=goruntuler[k["goruntu"]].id,
                sinif=k["sinif"],
                guven_skoru=k["guven"],
                bbox=_kutu(*k["kutu"]),
                bbox_format=BBOX_BICIMI,
                inceleme_gerekli=k.get("inceleme", False),
                dogrulama_durumu=DogrulamaDurumu(k["dogrulama"]),
                duzeltilen_sinif=k.get("duzeltilen"),
            )
            if k["dogrulama"] != "beklemede":
                t.dogrulayan_id = uzman.id
                t.dogrulama_tarihi = simdi - timedelta(hours=2)
            db.add(t)
            tespitler.append(t)
        await db.flush()

        for k, t in zip(SENARYO, tespitler):
            if not k["olcum"]:
                continue
            tur, deger, birim, yontem = k["olcum"]
            db.add(Olcum(
                tespit_id=t.id, tur=tur, deger=deger, birim=birim,
                yontem=yontem, giren_id=saha.id,
                tarih=simdi - timedelta(hours=1),
            ))
        await db.commit()

        # Miktar hesabı, ölçüm girildikten SONRA ve aynı servis
        # üzerinden yapılır — demo verisi kuralları atlamaz, onlara tabidir.
        for t in tespitler:
            olcumler = list(await db.scalars(
                select(Olcum).where(Olcum.tespit_id == t.id)))
            if not olcumler:
                continue
            sonuc = miktar_servisi.hesapla(t, olcumler)
            if not sonuc.hesaplandi:
                continue
            db.add(MiktarHesabi(
                tespit_id=t.id,
                deger_alt=sonuc.deger_alt,
                deger_ust=sonuc.deger_ust,
                birim=sonuc.birim,
                kullanilan_katsayi=sonuc.kullanilan_katsayi,
                katsayi_kaynagi=sonuc.katsayi_kaynagi,
                yontem=sonuc.yontem,
            ))
        await db.commit()

        eklenen.append(
            f"{len(goruntuler)} görüntü · {len(tespitler)} tespit "
            f"(hepsi sentetik)")

    print("Demo verisi hazır.")
    for e in eklenen:
        print(f"  + {e}")
    if not eklenen:
        print("  (her şey zaten mevcuttu)")
    print(f"\nTüm demo hesaplarının parolası: {DEMO_PAROLA}")
    print("Madde 10.7: bu hesaplar ve veriler sentetiktir; gerçek posta "
          "kutusu, gerçek saha ve gerçek model çıktısı yoktur.")


if __name__ == "__main__":
    asyncio.run(main())
