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

NE GERÇEK, NE SENTETİK — İKİSİ DE AÇIKÇA

- **Tespit kutuları ve güven skorları GERÇEKTİR.** Eğitilen `best.pt`
  ile üretilmiştir (`scripts/demo_tespitleri.json`). 02.09.2026'ya
  kadar elle yazılıyorlardı; jürinin gördüğü her kutu uydurmaydı.
- **Görüntüler sentetiktir** (`web/public/gorseller/README.md`).
- **Doğrulama ve ölçüm senaryosu sentetiktir:** gerçek bir uzman ya da
  gerçek bir şerit metre yoktur. Her saha adı "(sentetik)" taşır.
"""
from __future__ import annotations

import asyncio
import json
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


TESPITLER_YOLU = DEPO_KOKU / "scripts/demo_tespitleri.json"


def _tespit_kaynagi() -> dict:
    """GERÇEK model çıktısını okur.

    ⚠️ BU KUTULAR 02.09.2026'YA KADAR ELLE YAZILIYORDU. Sayılar makul
    görünüyordu ama hiçbiri bir modelden gelmiyordu — jürinin demo
    ortamında gördüğü her kutu uydurmaydı. Ana talimat Bölüm 9.5
    sahteliğin gizlenmemesini istiyor; en iyisi hiç üretmemek.

    Dosya `scripts/demo_tespitleri_uret.py` ile gerçek `best.pt`
    çalıştırılarak üretilir ve depoya girer, böylece demo verisi ağırlık
    olmadan da kurulabilir ama içindeki her kutu gerçek kalır.
    """
    if not TESPITLER_YOLU.is_file():
        raise SystemExit(
            f"{TESPITLER_YOLU} yok. Gerçek model çıktısı olmadan demo "
            "tespiti üretilmez — uydurma kutu yazmaktansa hiç yazmamak "
            "doğrudur. Üretmek için: scripts/demo_tespitleri_uret.py"
        )
    return json.loads(TESPITLER_YOLU.read_text(encoding="utf-8"))


# Senaryo ÖRTÜSÜ — kutular modelden, bu tablo yalnızca "sonra ne oldu"yu
# söyler. Dört kural da böylece ilk ekranda görünür.
#
#   (görüntü sırası, tespit sırası): {dogrulama, duzeltilen, olcum}
#   olcum: (tür, değer, birim, yöntem) ya da yok → miktar BOŞ kalır
#
# `ahsap` ve `metal` katsayıları kaynaklıdır (katsayilar.json v0.3);
# `beton_tugla`, `cam`, `seramik` kapalıdır — ölçüm olsa bile miktar
# üretilmez ve sebebi yazılır. Bu bir eksiklik değil, kuralın kendisi.
#
# Gerçek uzman ve gerçek şerit metre YOKTUR: aşağısı sentetik örtüdür.
SENARYO_ORTUSU = {
    # ⚠️ v2 MODELİYLE YENİDEN KURULDU (03.09.2026).
    #
    # v2, bu üç SENTETİK görüntüde yalnızca 4 tespit üretiyor ve hepsi
    # `ahsap`. v1 aynı görüntülerde 14 tespit / 4 sınıf veriyordu. Bu bir
    # gerileme değil DAĞILIM FARKI: v2 gerçek yıkım atığı fotoğraflarıyla
    # (Mendeley CODD + broken-glass + wood) eğitildi, bu görüntüler ise
    # yapay zekâ üretimi geniş moloz sahneleri. Kendi val kümesinde v2'nin
    # mAP50'si 0,8824; buradaki azlık ölçülmüş bir genelleme farkıdır ve
    # results/model-metrikleri.md'de açıkça yazılıdır.
    #
    # Dört kural TEK SINIFLA da gösterilebiliyor, çünkü uzman düzeltmesi
    # ETKİN SINIFI değiştiriyor (`miktar.py`: duzeltilen_sinif or sinif).
    # `ahsap` katsayılı tek sınıf; `beton` katsayısız. Düzeltme, bir
    # kaydın iki kuralı birden taşımasını sağlıyor.

    # --- 2. görüntü (Saha A) — modelin en güvenli çıktısı (%94,20) ----
    # Kural 1: ölçüm var + katsayı kaynaklı (ahsap) → belirsizlik aralığı.
    (1, 0): dict(dogrulama="onaylandi",
                 olcum=(OlcumTuru.HACIM, 40.0, "m3",
                        "Şerit metre ile kaba hacim")),

    # --- 3. görüntü (Saha B, kısıtlı erişim) · %76,12 -----------------
    # Kural 2 — EN GÜÇLÜ AN: doğrulandı ama ölçüm YOK → miktar BOŞ.
    (2, 0): dict(dogrulama="onaylandi"),

    # --- 1. görüntü (Saha A) · %51,00 --------------------------------
    # Kural 4 + Kural 3 AYNI KAYITTA: model `ahsap` dedi, uzman `beton`
    # yaptı. Ham tahmin izlenebilirlik için saklanır. Etkin sınıf artık
    # `beton` ve betonun doğrulanmış katsayısı YOK — yani ölçüm girilmiş
    # olmasına rağmen miktar üretilmiyor. "Ölçüm var ama sayı yok" da bir
    # kuraldır ve gerekçesi ekranda yazılıdır.
    (0, 0): dict(dogrulama="duzeltildi", duzeltilen="beton",
                 olcum=(OlcumTuru.HACIM, 62.0, "m3",
                        "Şerit metre ile kaba hacim")),

    # (0, 1) — %27,11: dokunulmuyor. Eşiğin (0,50) altında olduğu için
    # sistem kendiliğinden `inceleme_gerekli` işaretleyip uzman kuyruğuna
    # düşürüyor. Senaryo değil, mekanizma.
}

# Hangi görüntü hangi sahaya gider (görüntü sırası -> saha sırası).
GORUNTU_SAHASI = [0, 0, 1]


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
        kaynak = _tespit_kaynagi()
        yollar = await _gorselleri_kopyala()
        simdi = datetime.now(timezone.utc)
        goruntuler = []
        for i, kayit in enumerate(kaynak["goruntuler"]):
            alan_ix = GORUNTU_SAHASI[i]
            g = Goruntu(
                enkaz_alani_id=alanlar[alan_ix].id,
                dosya_yolu=yollar[i],
                # Boyutlar da modelin gördüğü boyutlardır; kutular bu
                # uzaya göre ölçeklenir (bbox_format).
                genislik=kayit["genislik"],
                yukseklik=kayit["yukseklik"],
                cekim_tarihi=simdi - timedelta(hours=6 - i),
                cihaz="Sentetik demo görüntüsü",
                yukleyen_id=saha.id,
            )
            g.konum = nokta(*ALANLAR[alan_ix]["konum"])
            db.add(g)
            goruntuler.append(g)
        await db.flush()

        # --- Tespitler, ölçümler, miktarlar ---------------------------
        #
        # Kutular, sınıflar, güven skorları ve `inceleme_gerekli` bayrağı
        # GERÇEK model çıktısından gelir — hiçbiri elle yazılmaz.
        # `SENARYO_ORTUSU` yalnızca "sonra ne oldu"yu söyler.
        tespitler = []
        for i, kayit in enumerate(kaynak["goruntuler"]):
            for j, ham in enumerate(kayit["tespitler"]):
                ortu = SENARYO_ORTUSU.get((i, j), {})
                durum = ortu.get("dogrulama", "beklemede")
                t = Tespit(
                    goruntu_id=goruntuler[i].id,
                    sinif=ham["sinif"],
                    guven_skoru=ham["guven"],
                    bbox=ham["bbox"],
                    bbox_format=ham["bbox_format"],
                    inceleme_gerekli=ham["inceleme_gerekli"],
                    dogrulama_durumu=DogrulamaDurumu(durum),
                    duzeltilen_sinif=ortu.get("duzeltilen"),
                )
                if durum != "beklemede":
                    t.dogrulayan_id = uzman.id
                    t.dogrulama_tarihi = simdi - timedelta(hours=2)
                db.add(t)
                tespitler.append(((i, j), t))
        await db.flush()

        for anahtar, t in tespitler:
            olcum = SENARYO_ORTUSU.get(anahtar, {}).get("olcum")
            if not olcum:
                continue
            tur, deger, birim, yontem = olcum
            db.add(Olcum(
                tespit_id=t.id, tur=tur, deger=deger, birim=birim,
                yontem=yontem, giren_id=saha.id,
                tarih=simdi - timedelta(hours=1),
            ))
        await db.commit()

        # Miktar hesabı, ölçüm girildikten SONRA ve aynı servis
        # üzerinden yapılır — demo verisi kuralları atlamaz, onlara tabidir.
        for _, t in tespitler:
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
            f"{len(goruntuler)} sentetik görüntü · {len(tespitler)} "
            f"GERÇEK model tespiti ({kaynak['model']})")

    print("Demo verisi hazır.")
    for e in eklenen:
        print(f"  + {e}")
    if not eklenen:
        print("  (her şey zaten mevcuttu)")
    print(f"\nTüm demo hesaplarının parolası: {DEMO_PAROLA}")
    print("Madde 10.7 — neyin ne olduğu:")
    print("  · hesaplar, sahalar ve görüntüler SENTETİKTİR")
    print("  · doğrulama ve ölçüm senaryosu SENTETİKTİR "
          "(gerçek uzman/şerit metre yok)")
    print("  · tespit kutuları ve güven skorları GERÇEK model çıktısıdır")


if __name__ == "__main__":
    asyncio.run(main())
