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

⚠️ BU BETİK 06.09.2026'YA KADAR CANLI ORTAMI DONDURUYORDU.

`docker/baslat-api.sh` her açılışta bu betiği çalıştırıyor, betik de ilk
demo sahasını görünce "zaten var" deyip DÖNÜYORDU. Sonuç: canlı veri
tabanı 30.08.2026'da kuruldu ve bir daha hiç yenilenmedi. Sınıf listesi
02.09'da 10'dan 5'e inince canlıda artık var OLMAYAN sınıflar kaldı —
jüri ekranda `sert_plastik`, `karton`, `konteyner`, `alcipan` görüyordu.
Modelin üretebileceği adlarla ekrandakiler tutmuyordu.

Erken dönüşü tamamen kaldırmak da yanlış olurdu: her açılışta veri silip
yeniden kurmak jürinin girdiği kayıtları da siler. Bu yüzden karar
SÜRÜME bağlandı (bkz. `demo_damgasi()` ve `main()`):

  1. Görüntü dosyaları HER AÇILIŞTA geri kopyalanır. Render ücretsiz
     katmanında dosya sistemi her dağıtımda sıfırlanır; veri tabanındaki
     yollar duruyor ama dosyalar gitmiş oluyor ve arayüzde kutuların
     yerinde kırık görsel çıkıyordu. Kopyalama ucuz ve idempotenttir.
  2. Senaryonun parmak izi `demo_damgasi` tablosunda saklanır. Parmak izi
     aynıysa hiçbir kayda dokunulmaz.
  3. Parmak izi değiştiyse — ya da veri tabanında `siniflar.json`'da
     bulunmayan bir sınıf kaldıysa — YALNIZCA sentetik demo kayıtları
     silinip senaryo yeniden kurulur. Kullanıcı verisine dokunulmaz.
  4. `DEMO_VERISI_ZORLA=1` ortam değişkeni bu kararı elle tetikler
     (Render panelinden tek seferlik yeniden kurulum için).
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEPO_KOKU = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPO_KOKU))

from sqlalchemy import delete, func, insert, select  # noqa: E402

from api.app.core.config import ayarlar, siniflar  # noqa: E402
from api.app.core.permissions import OnayDurumu, Rol  # noqa: E402
from api.app.core.security import parola_ozetle  # noqa: E402
from api.app.db import OturumUret  # noqa: E402
from api.app.geo import nokta, poligon  # noqa: E402
from api.app.models import (  # noqa: E402
    DemoDamgasi, DogrulamaDurumu, EnkazAlani, ErisimDurumu, Goruntu,
    IslemGecmisi, Kullanici, MiktarHesabi, Olcum, OlcumTuru, Tespit,
)
from api.app.services import miktar as miktar_servisi  # noqa: E402
from api.app.services.queries import (  # noqa: E402
    bilinmeyen_sinifli_tespitler, tanimli_siniflar,
)

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

    # ⚠️ UZMAN KARARLARI 08.09.2026'DA FOTOĞRAFLARA GÖRE YENİDEN
    # KURULDU. Önceki senaryoda uzman, %94,20 güvenli `ahsap` tahminini
    # ONAYLIYORDU — oysa o fotoğrafta ahşap YOK: metal karkas, beton
    # moloz ve cam var. Yani demo, uzmanın yanlış bir tahmini onayladığını
    # gösteriyordu. Bu, doğrulama kapısının varlık sebebini yalanlar.
    #
    # Görüntülerde gerçekte ne olduğu (gözle bakıldı):
    #   ornek-enkaz-1: beton moloz + demir donatı — ahşap YOK
    #   ornek-enkaz-2: metal karkas + beton + cam — ahşap YOK
    #   ornek-enkaz-3: ayrık yığınlar; ahşap, tuğla, beton, metal — ahşap VAR
    #
    # Model üçünde de yalnızca `ahsap` diyor. Yani sınıf yalnızca 3.
    # görüntüde doğru. Senaryo bunu olduğu gibi yansıtır.

    # --- 3. görüntü (Saha B) · %76,12 — SINIF DOĞRU ------------------
    # Fotoğrafta sol üstte gerçek bir ahşap yığını var. Model sınıfı
    # doğru bildi (kapsamı abarttı; arayüz onu "GÖRÜNTÜ GENELİ" diye
    # gösteriyor). Uzman onaylıyor, ölçüm giriliyor.
    # Kural 1: ölçüm + katsayı kaynaklı sınıf → belirsizlik aralığı.
    (2, 0): dict(dogrulama="onaylandi",
                 olcum=(OlcumTuru.HACIM, 40.0, "m3",
                        "Şerit metre ile kaba hacim")),

    # --- 2. görüntü (Saha A) · %94,20 — MODEL YÜKSEK GÜVENLE YANILDI -
    # DEMONUN EN ÖNEMLİ ANI. Model %94,20 ile `ahsap` diyor; fotoğrafta
    # ahşap yok. Uzman yakalıyor ve `beton` yapıyor (moloz baskın).
    # Ham tahmin izlenebilirlik için saklanır, silinmez.
    #
    # Kural 3 + Kural 4 aynı kayıtta: etkin sınıf `beton` oldu, betonun
    # doğrulanmış katsayısı YOK — ölçüm girilmiş olmasına rağmen miktar
    # üretilmiyor ve gerekçesi ekranda yazılı.
    #
    # Not: karedeki baskın malzeme aslında METAL, ama metal v2'de
    # tanınan bir sınıf değil (siniflar.json kapsanmayan_gruplar).
    # Uzman yalnızca tanınan sınıflar arasından seçebilir; sistemin
    # kapsam sınırı burada da görünür.
    (1, 0): dict(dogrulama="duzeltildi", duzeltilen="beton",
                 olcum=(OlcumTuru.HACIM, 62.0, "m3",
                        "Şerit metre ile kaba hacim")),

    # --- 1. görüntü (Saha A) · %51,00 — YİNE YANLIŞ ------------------
    # Fotoğraf baştan sona beton moloz ve donatı demiri. Uzman `beton`
    # yapıyor ama ÖLÇÜM GİRMİYOR.
    # Kural 2: ölçüm yoksa miktar BOŞ kalır — sıfır değil.
    (0, 0): dict(dogrulama="duzeltildi", duzeltilen="beton"),

    # (0, 1) — %27,11: dokunulmuyor. Eşiğin (0,50) altında olduğu için
    # sistem kendiliğinden `inceleme_gerekli` işaretleyip uzman kuyruğuna
    # düşürüyor. Senaryo değil, mekanizma.
}

# Hangi görüntü hangi sahaya gider (görüntü sırası -> saha sırası).
GORUNTU_SAHASI = [0, 0, 1]


# --- Sürüm damgası --------------------------------------------------------
#
# Senaryonun sürümü. Senaryo ÖRTÜSÜ ya da saha listesi elle değiştiğinde
# artırılır. Parmak izinin tek girdisi bu değil: aşağıdaki `demo_damgasi()`
# sınıf listesini ve gerçek model çıktısını da içeri katar, böylece
# sürümü artırmayı unutmak sessiz bir arızaya dönüşmez.
SENARYO_SURUMU = "3"

# `DEMO_VERISI_ZORLA=1` — damga aynı olsa bile yeniden kurar.
#
# Canlıda tek seferlik bir müdahale kapısı olmalı: Render panelinden bu
# değişkeni ekleyip yeniden dağıtmak, veri tabanını elle açmadan demo
# verisini tazeler. Kabul edilen değerler bilinçli olarak geniş — panelde
# "true" yazan biri "1 yazmadım" diye saatini kaybetmemeli.
ZORLA_DEGERLERI = {"1", "evet", "true", "yes", "e", "y"}

# Sentetik demo sahalarının adında geçen işaret. Saha adları değişebilir
# ama bu ek DEĞİŞMEZ: Madde 10.7 gereği her demo sahası kendini sentetik
# ilan eder. Temizlik kapsamı bu işarete bakar, sabit bir ada değil —
# böylece eski sürümlerde kurulmuş sahalar da kapsama girer.
SENTETIK_ISARETI = "(sentetik)"

# Demo görüntülerinin `cihaz` alanı. Kayıt bu betikten mi geldi, yoksa
# arayüzden mi yüklendi — ayrım buradan da okunabilir.
DEMO_CIHAZ = "Sentetik demo görüntüsü"


def demo_damgasi() -> str:
    """Kurulacak demo senaryosunun parmak izi.

    NEDEN SADECE BİR SÜRÜM NUMARASI DEĞİL: numarayı artırmak insana
    kalır ve unutulur — bu depoda tam olarak bu unutuldu. Parmak izi
    senaryonun KENDİSİNDEN üretilir; sınıf listesi, saha adları ya da
    gerçek model çıktısı değişirse damga kendiliğinden değişir ve demo
    verisi bir sonraki açılışta yenilenir.

    Girdiler:
      · senaryo sürümü (elle artırılan, örtü değişince)
      · siniflar.json sürümü ve sınıf adları  ← 02.09'daki arıza buradan
      · sahaların adları
      · gerçek model çıktısının (`demo_tespitleri.json`) özeti
    """
    tanim = siniflar()
    parcalar = [
        f"senaryo={SENARYO_SURUMU}",
        f"siniflar_surumu={tanim.get('surum', '?')}",
        "siniflar=" + ",".join(s["ad"] for s in tanim["siniflar"]),
        "alanlar=" + "|".join(a["ad"] for a in ALANLAR),
        "tespitler=" + hashlib.sha256(
            TESPITLER_YOLU.read_bytes()).hexdigest(),
        "ortu=" + ";".join(
            f"{k}:{sorted(v.items())}" for k, v in sorted(SENARYO_ORTUSU.items())
        ),
    ]
    return hashlib.sha256("\n".join(parcalar).encode("utf-8")).hexdigest()


def _zorlama_istendi() -> bool:
    return os.environ.get("DEMO_VERISI_ZORLA", "").strip().lower() in ZORLA_DEGERLERI


def _gorselleri_kopyala() -> tuple[list[str], list[str]]:
    """Sentetik görselleri yükleme klasörüne kopyalar, yollarını döner.

    ⚠️ BU İŞ ARTIK HER AÇILIŞTA YAPILIR, YALNIZCA İLK KURULUMDA DEĞİL.

    Render ücretsiz katmanında dosya sistemi her dağıtımda sıfırlanır
    (docs/yayin.md). Veri tabanındaki `dosya_yolu` duruyor, dosya gitmiş
    oluyor: arayüzde tespit kutularının yerinde kırık görsel ikonu
    çıkıyordu. Eskiden kopyalama senaryo kurulumunun İÇİNDEYDİ, kurulum
    da "zaten var" diye atlandığı için dosyalar bir daha hiç geri
    gelmiyordu.

    Kopyalama ucuz ve idempotenttir: dosya varsa ve boş değilse
    dokunulmaz. Sıfır baytlık dosya da eksik sayılır — yarım kalmış bir
    kopya sessizce kırık görsel demektir.

    Dönen ikinci liste, gerçekten kopyalanan dosyaların adlarıdır; açılış
    kaydında "ne yapıldı" yazılabilsin diye.
    """
    hedef_klasor = ayarlar().yukleme_yolu
    hedef_klasor.mkdir(parents=True, exist_ok=True)
    yollar: list[str] = []
    kopyalanan: list[str] = []
    for i, ad in enumerate(KAYNAK_GORSELLER):
        kaynak = DEPO_KOKU / "web/public/gorseller" / ad
        hedef_ad = f"demo_sentetik_{i + 1}{Path(ad).suffix}"
        hedef = hedef_klasor / hedef_ad
        eksik = not hedef.exists() or hedef.stat().st_size == 0
        if kaynak.is_file() and eksik:
            shutil.copyfile(kaynak, hedef)
            kopyalanan.append(hedef_ad)
        yollar.append(hedef_ad)
    return yollar, kopyalanan


def _senaryo_siniflarini_denetle(kaynak: dict) -> None:
    """Demo verisi `siniflar.json`'da OLMAYAN bir sınıf yazamaz.

    Bu betiğin kendisi de aynı tuzağa düşebilir: `demo_tespitleri.json`
    eski bir modelle üretilmişse ya da senaryo örtüsündeki `duzeltilen`
    alanı eski bir ada bakıyorsa, temizlediğimiz arızayı bu kez BİZ
    kurarız. Sessizce kurmaktansa açıkça durmak doğrudur.
    """
    tanimli = tanimli_siniflar()
    bulunan = {
        t["sinif"] for g in kaynak["goruntuler"] for t in g["tespitler"]
    } | {
        o["duzeltilen"] for o in SENARYO_ORTUSU.values() if o.get("duzeltilen")
    }
    eksik = sorted(bulunan - tanimli)
    if eksik:
        raise SystemExit(
            f"Demo senaryosu siniflar.json'da bulunmayan sınıf(lar) "
            f"kurmaya çalışıyor: {eksik}. Tanımlı olanlar: "
            f"{sorted(tanimli)}. Ya senaryo güncellenmeli ya da "
            "scripts/demo_tespitleri_uret.py güncel ağırlıkla yeniden "
            "çalıştırılmalı — eski sınıf adlarını veri tabanına yazmak, "
            "az önce temizlediğimiz arızayı geri getirir."
        )


async def _demo_kayitlarini_temizle(db, demo_idler: list[int]) -> dict[str, int]:
    """SENTETİK demo kayıtlarını siler. Kullanıcı verisine dokunmaz.

    Kapsam üç kalemdir ve üçü de "bu kayıt sentetik mi?" sorusuna
    veriden cevap verir, tahminle değil:

      1. Demo hesaplarının yüklediği görüntüler. Demo hesapları
         `@demo.local` adreslidir ve gerçek bir posta kutusuna karşılık
         gelmez (Madde 10.7); onların yüklediği her görüntü sentetiktir.
      2. Sınıfı `siniflar.json`'da BULUNMAYAN tespitler — hangi hesap
         yüklemiş olursa olsun. Bu kayıtlar emekli bir modelin
         çıktısıdır: haritaya girmez, miktara girmez, arayüzde
         düzeltilemez ve ekranda modelin üretemeyeceği bir ad gösterir.
         Kaydın kendisi değil, TESPİTİ silinir; kullanıcının yüklediği
         görüntü yerinde kalır.
      3. Görüntüsü kalmamış sentetik demo sahaları.

    Alt kayıtlar (ölçüm, miktar hesabı, tehlikeli kayıt) veri tabanı
    seviyesinde ON DELETE CASCADE ile gider; burada tek tek silinmez.

    Silme ORM ile değil Core `delete()` ile yapılır: ORM ilişki
    davranışı çocukların yabancı anahtarını NULL'lamaya çalışır ve
    NOT NULL kısıtına takılırdı. Bunun bedeli, otomatik izlenebilirlik
    dinleyicisinin (services/denetim.py) bu silmeleri görmemesidir —
    o yüzden temizliğin kendisi `main()` içinde AÇIKÇA işlem geçmişine
    yazılır. Silinen kayıtların eski geçmiş satırları da yerinde kalır:
    izlenebilirlik geçmişi temizlik yüzünden kaybolmaz.
    """
    sayim = {"goruntu": 0, "tespit": 0, "alan": 0}

    # 1) Demo hesaplarının yüklediği görüntüler.
    goruntu_idler = list(await db.scalars(
        select(Goruntu.id).where(Goruntu.yukleyen_id.in_(demo_idler))
    )) if demo_idler else []

    # 2) Artık tanınmayan sınıflı tespitler (emekli modelin ölü kayıtları).
    #    Silinecek görüntülerin içindekiler zaten gidecek; kalanlar
    #    kullanıcının kendi yüklediği görüntülerdeki eski tespitlerdir.
    eski_tespit_idler = [
        t.id for t in await db.scalars(bilinmeyen_sinifli_tespitler())
        if t.goruntu_id not in set(goruntu_idler)
    ]

    if eski_tespit_idler:
        await db.execute(
            delete(Tespit).where(Tespit.id.in_(eski_tespit_idler))
        )
        sayim["tespit"] = len(eski_tespit_idler)

    if goruntu_idler:
        sayim["tespit"] += await db.scalar(
            select(func.count(Tespit.id))
            .where(Tespit.goruntu_id.in_(goruntu_idler))
        ) or 0
        await db.execute(delete(Goruntu).where(Goruntu.id.in_(goruntu_idler)))
        sayim["goruntu"] = len(goruntu_idler)

    await db.flush()

    # 3) Görüntüsü kalmamış sentetik sahalar.
    #
    #    Görüntüsü KALAN bir sentetik saha silinmez: içinde kullanıcının
    #    yüklediği bir kayıt var demektir. O saha aşağıda yeniden
    #    kurulmaz, ADIYLA BULUNUP kullanılır (bkz. `_saha_kur`), yoksa
    #    aynı adda ikinci bir saha doğardı.
    bos_alanlar = list(await db.scalars(
        select(EnkazAlani.id).where(
            EnkazAlani.ad.contains(SENTETIK_ISARETI),
            ~select(Goruntu.id)
            .where(Goruntu.enkaz_alani_id == EnkazAlani.id)
            .exists(),
        )
    ))
    if bos_alanlar:
        await db.execute(delete(EnkazAlani).where(EnkazAlani.id.in_(bos_alanlar)))
        sayim["alan"] = len(bos_alanlar)

    await db.flush()
    return sayim


async def _saha_kur(db, tanim: dict, belediye_id: int) -> EnkazAlani:
    """Sahayı adıyla bulur, yoksa oluşturur.

    Temizlikten sonra bir sentetik saha hâlâ duruyorsa içinde kullanıcı
    kaydı var demektir; onu silmek yerine yeniden kullanırız. Aksi hâlde
    aynı adda ikinci bir saha oluşur ve jüri hangisinin demo olduğunu
    anlayamaz.
    """
    a = await db.scalar(select(EnkazAlani).where(EnkazAlani.ad == tanim["ad"]))
    if a is None:
        a = EnkazAlani(ad=tanim["ad"], olusturan_id=belediye_id)
        db.add(a)
    a.sorumlu = tanim["sorumlu"]
    a.erisim_durumu = tanim["erisim"]
    a.konum = nokta(*tanim["konum"])
    if tanim["sinir"]:
        a.sinir = poligon(tanim["sinir"])
    return a


async def main() -> None:
    eklenen: list[str] = []

    # Görsel dosyaları senaryodan ÖNCE ve her koşulda geri kopyalanır:
    # Render'ın efemer dosya sistemi yüzünden dosyalar her dağıtımda
    # kayboluyor, veri tabanı kayıtları ise duruyor.
    yollar, kopyalanan = _gorselleri_kopyala()
    if kopyalanan:
        print(f">> Eksik sentetik görsel geri kopyalandı: {', '.join(kopyalanan)}")

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

        # --- Yeniden kurulum gerekiyor mu? ----------------------------
        #
        # ⚠️ ESKİDEN BURADA "ilk saha var mı" DİYE BAKILIP DÖNÜLÜYORDU.
        # O erken dönüş canlı veri tabanını 30.08.2026'da dondurdu; sınıf
        # listesi değişince ekranda artık üretilemeyecek sınıf adları
        # kaldı. Karar artık SÜRÜME bağlı.
        damga = demo_damgasi()
        kayitli = await db.scalar(select(DemoDamgasi).where(DemoDamgasi.id == 1))
        bilinmeyen = await db.scalar(
            select(func.count()).select_from(
                bilinmeyen_sinifli_tespitler().subquery())
        ) or 0

        sebepler: list[str] = []
        if kayitli is None:
            sebepler.append("demo damgası yok (ilk kurulum ya da eski sürüm)")
        elif kayitli.damga != damga:
            sebepler.append(
                f"senaryo damgası değişti ({kayitli.damga[:12]}… → "
                f"{damga[:12]}…; sınıflar: {kayitli.siniflar} → "
                f"{','.join(s['ad'] for s in siniflar()['siniflar'])})"
            )
        if bilinmeyen:
            sebepler.append(
                f"{bilinmeyen} tespitin sınıfı siniflar.json'da yok "
                "(emekli modelden kalan ölü kayıt)"
            )
        if _zorlama_istendi():
            sebepler.append("DEMO_VERISI_ZORLA ayarlı")

        if not sebepler:
            print("Demo verisi güncel; senaryo yeniden kurulmadı "
                  f"(damga {damga[:12]}…).")
            print(f"\nTüm demo hesaplarının parolası: {DEMO_PAROLA}")
            return

        print(">> Demo verisi yeniden kuruluyor. Sebep:")
        for s in sebepler:
            print(f"   · {s}")

        kaynak = _tespit_kaynagi()
        # Kendi kurduğumuz veri de denetimden geçer: eski sınıf adı
        # yazmaktansa açıkça durmak doğrudur.
        _senaryo_siniflarini_denetle(kaynak)

        demo_idler = list(await db.scalars(
            select(Kullanici.id).where(Kullanici.eposta.like("%@demo.local"))
        ))
        silinen = await _demo_kayitlarini_temizle(db, demo_idler)
        if any(silinen.values()):
            print(f">> Temizlenen sentetik kayıt: {silinen['goruntu']} görüntü, "
                  f"{silinen['tespit']} tespit, {silinen['alan']} saha")
            # Temizlik Core `delete()` ile yapıldığı için otomatik denetim
            # dinleyicisi görmez; izi burada AÇIKÇA bırakılır.
            await db.execute(insert(IslemGecmisi), [{
                "kayit_tipi": "demo_verisi",
                "kayit_id": None,
                "islem": "silme",
                "eski_deger": silinen,
                "yeni_deger": {"damga": damga, "sebepler": sebepler},
                "kullanici_id": None,
            }])

        alanlar = [await _saha_kur(db, t, belediye.id) for t in ALANLAR]
        await db.flush()
        eklenen += [t["ad"] for t in ALANLAR]

        # --- Görüntüler -----------------------------------------------
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
                cihaz=DEMO_CIHAZ,
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

        # --- Damga --------------------------------------------------------
        # En sona yazılır: kurulum yarıda kalırsa damga da yazılmamış olur
        # ve bir sonraki açılış yeniden dener.
        sinif_adlari = ",".join(s["ad"] for s in siniflar()["siniflar"])
        if kayitli is None:
            db.add(DemoDamgasi(
                id=1, damga=damga, senaryo_surumu=SENARYO_SURUMU,
                siniflar_surumu=str(siniflar().get("surum", "?")),
                siniflar=sinif_adlari,
            ))
        else:
            kayitli.damga = damga
            kayitli.senaryo_surumu = SENARYO_SURUMU
            kayitli.siniflar_surumu = str(siniflar().get("surum", "?"))
            kayitli.siniflar = sinif_adlari
            kayitli.tarih = datetime.now(timezone.utc)
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
    print(f"Senaryo damgası: {damga[:12]}… "
          f"(sınıflar: {sinif_adlari})")
    print("Madde 10.7 — neyin ne olduğu:")
    print("  · hesaplar, sahalar ve görüntüler SENTETİKTİR")
    print("  · doğrulama ve ölçüm senaryosu SENTETİKTİR "
          "(gerçek uzman/şerit metre yok)")
    print("  · tespit kutuları ve güven skorları GERÇEK model çıktısıdır")


if __name__ == "__main__":
    asyncio.run(main())
