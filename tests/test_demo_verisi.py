"""Demo verisi — sürüm damgası, temizlik ve sınıf tutarlılığı.

⚠️ BU DOSYA 06.09.2026'DA, CANLI ORTAMDA AYLARDIR DURAN BİR ARIZADAN
SONRA YAZILDI.

`scripts/demo_veri.py` her açılışta çalışıyor ama ilk demo sahasını
görünce "zaten var" deyip dönüyordu. Canlı veri tabanı 30.08.2026'da
kuruldu ve bir daha hiç yenilenmedi; sınıf listesi 02.09'da 10'dan 5'e
inince ekranda artık üretilemeyecek sınıflar kaldı (`sert_plastik`,
`karton`, `konteyner`, `alcipan`, `dolgu_toprak`). Hiçbir test bunu
yakalamadı, çünkü hiçbir test "veri tabanındaki sınıf adları
`siniflar.json`'da var mı?" diye sormuyordu.

Buradaki testlerin işi tam olarak o sorudur.
"""
from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest
from sqlalchemy import func, select

import api.app.core.config as yapilandirma
import api.app.db as db_modulu
from api.app.models import (
    DemoDamgasi, EnkazAlani, Goruntu, IslemGecmisi, Kullanici, MiktarHesabi,
    Tespit,
)
from api.app.services.queries import bilinmeyen_sinifli_tespitler

DEPO_KOKU = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def demo():
    """`scripts/demo_veri.py` modülünü yükler.

    Betik `scripts/` altında ve paket değil; dosya yolundan yüklenir.
    """
    yol = DEPO_KOKU / "scripts/demo_veri.py"
    spec = importlib.util.spec_from_file_location("demo_veri_test", yol)
    assert spec and spec.loader
    modul = importlib.util.module_from_spec(spec)
    sys.modules["demo_veri_test"] = modul
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture(autouse=True)
def _test_oturumu(demo, monkeypatch):
    """Betik TEST veri tabanına yazsın.

    `demo_veri.py` `OturumUret`'i içe aktarma anında bağlar; conftest'in
    NullPool'lu oturum üreticisini görmesi için adı modül üzerinde
    değiştirilir. Havuzlanmış bağlantı testler arasında farklı olay
    döngülerine takılıyor.
    """
    monkeypatch.setattr(demo, "OturumUret", db_modulu.OturumUret)
    monkeypatch.delenv("DEMO_VERISI_ZORLA", raising=False)


async def _sayimlar(db) -> dict[str, int]:
    return {
        "alan": await db.scalar(select(func.count(EnkazAlani.id))),
        "goruntu": await db.scalar(select(func.count(Goruntu.id))),
        "tespit": await db.scalar(select(func.count(Tespit.id))),
        "miktar": await db.scalar(select(func.count(MiktarHesabi.id))),
    }


async def _bilinmeyen_sayisi(db) -> int:
    return await db.scalar(
        select(func.count()).select_from(bilinmeyen_sinifli_tespitler().subquery())
    )


# --- Temel kurulum ---------------------------------------------------------

async def test_kurulan_her_tespitin_sinifi_siniflar_jsonda_var(demo, db_oturum):
    """EN ÖNEMLİ TEST: veri tabanında tanınmayan sınıf adı KALMAMALI.

    Canlıdaki arıza tam buydu ve aylarca fark edilmedi: `sadece_malzeme()`
    bilinmeyen adı zaten eliyor, arayüz de tanımadığı sınıf için ham adı
    basıyor — yani sistem hiçbir yerde hata vermeden yanlışı taşıyordu.
    """
    await demo.main()

    tanimli = {s["ad"] for s in yapilandirma.siniflar()["siniflar"]}
    tespitler = list(await db_oturum.scalars(select(Tespit)))
    assert tespitler, "demo verisi hiç tespit kurmadı"
    for t in tespitler:
        assert t.sinif in tanimli, (
            f"Tespit #{t.id} '{t.sinif}' sınıfıyla kurulmuş ama bu ad "
            f"siniflar.json'da yok. Tanımlı olanlar: {sorted(tanimli)}"
        )
        if t.duzeltilen_sinif is not None:
            assert t.duzeltilen_sinif in tanimli, (
                f"Tespit #{t.id} '{t.duzeltilen_sinif}' sınıfına "
                "düzeltilmiş ama bu ad siniflar.json'da yok"
            )
    assert await _bilinmeyen_sayisi(db_oturum) == 0


async def test_guncel_saha_adlari_kurulur(demo, db_oturum):
    """Saha adları betikteki güncel listeyle birebir aynı olmalı.

    Canlıda "Çarşı" ve "Sanayi" sahaları hiç görünmüyordu; betik yeni
    sahaları ekleyecek koda hiç ulaşmıyordu.
    """
    await demo.main()
    adlar = set(await db_oturum.scalars(select(EnkazAlani.ad)))
    assert adlar == {a["ad"] for a in demo.ALANLAR}
    assert any("Çarşı" in a for a in adlar)


async def test_damga_yazilir(demo, db_oturum):
    await demo.main()
    d = await db_oturum.scalar(select(DemoDamgasi))
    assert d is not None and d.id == 1
    assert d.damga == demo.demo_damgasi()
    assert d.siniflar == ",".join(
        s["ad"] for s in yapilandirma.siniflar()["siniflar"])


# --- Eski sürüm kayıtlarının temizlenmesi ---------------------------------

async def _v1_kayitlari_kur(db, demo) -> dict[str, int]:
    """30.08.2026 canlı veri tabanının benzetimi: v1 sınıflı kayıtlar."""
    from api.app.core.permissions import OnayDurumu, Rol
    from api.app.core.security import parola_ozetle

    saha = Kullanici(eposta="saha@demo.local", sifre_hash=parola_ozetle("x"),
                     ad="Demo Saha", rol=Rol.SAHA,
                     onay_durumu=OnayDurumu.ONAYLANDI)
    juri = Kullanici(eposta="juri@ornek.gov.tr", sifre_hash=parola_ozetle("x"),
                     ad="Jüri Üyesi", rol=Rol.SAHA,
                     onay_durumu=OnayDurumu.ONAYLANDI)
    db.add_all([saha, juri])
    await db.flush()

    demo_alan = EnkazAlani(ad=demo.ALANLAR[0]["ad"], olusturan_id=saha.id)
    juri_alan = EnkazAlani(ad="Jüri Test Sahası", olusturan_id=juri.id)
    db.add_all([demo_alan, juri_alan])
    await db.flush()

    demo_g = Goruntu(enkaz_alani_id=demo_alan.id,
                     dosya_yolu="demo_sentetik_1.webp",
                     genislik=1200, yukseklik=896,
                     cihaz=demo.DEMO_CIHAZ, yukleyen_id=saha.id)
    juri_g = Goruntu(enkaz_alani_id=juri_alan.id, dosya_yolu="juri.jpg",
                     genislik=800, yukseklik=600, yukleyen_id=juri.id)
    db.add_all([demo_g, juri_g])
    await db.flush()

    def _t(gid, sinif, duzeltilen=None):
        return Tespit(goruntu_id=gid, sinif=sinif, guven_skoru=0.7,
                      bbox={"x": 1, "y": 1, "w": 5, "h": 5},
                      bbox_format="pixel_absolute_original",
                      duzeltilen_sinif=duzeltilen)

    db.add_all([
        _t(demo_g.id, "sert_plastik"),
        _t(demo_g.id, "karton"),
        # Ekran görüntüsündeki "Uzman düzeltmesi: konteyner → Beton"
        _t(demo_g.id, "konteyner", "beton"),
        # Jürinin kendi görüntüsündeki kayıtlar
        _t(juri_g.id, "tekstil"),     # ölü: sınıf artık yok
        _t(juri_g.id, "beton"),       # geçerli: DOKUNULMAMALI
    ])
    await db.commit()
    return {"juri_alan": juri_alan.id, "juri_goruntu": juri_g.id}


async def test_eski_surum_kayitlari_temizlenip_v2ye_gecilir(demo, db_oturum):
    """v1 sınıflı canlı veri tabanı, yeni mantıkla v2'ye geçmeli."""
    await _v1_kayitlari_kur(db_oturum, demo)
    assert await _bilinmeyen_sayisi(db_oturum) == 4

    await demo.main()

    db_oturum.expire_all()
    assert await _bilinmeyen_sayisi(db_oturum) == 0, (
        "Eski sürümün sınıfları veri tabanında kaldı")
    kalan = set(await db_oturum.scalars(select(Tespit.sinif)))
    for eski in ("sert_plastik", "karton", "konteyner", "tekstil"):
        assert eski not in kalan


async def test_temizlik_kullanici_verisine_dokunmaz(demo, db_oturum):
    """Jürinin kurduğu saha, yüklediği görüntü ve GEÇERLİ tespiti kalır.

    Erken dönüşü tamamen kaldırıp her açılışta her şeyi silmek en kolay
    çözümdü ve yanlış olurdu: jürinin sisteme girdiği kayıtlar da uçardı.
    """
    kimlikler = await _v1_kayitlari_kur(db_oturum, demo)

    await demo.main()
    db_oturum.expire_all()

    assert await db_oturum.get(EnkazAlani, kimlikler["juri_alan"]) is not None
    juri_g = await db_oturum.get(Goruntu, kimlikler["juri_goruntu"])
    assert juri_g is not None, "Kullanıcının yüklediği görüntü silinmiş"

    juri_tespitleri = list(await db_oturum.scalars(
        select(Tespit).where(Tespit.goruntu_id == juri_g.id)))
    # Ölü sınıflı olan gitti, geçerli olan kaldı.
    assert [t.sinif for t in juri_tespitleri] == ["beton"]


async def test_temizlik_islem_gecmisine_yazilir(demo, db_oturum):
    """Silme Core `delete()` ile yapılıyor; izi ELLE bırakılmalı.

    Otomatik denetim dinleyicisi (services/denetim.py) yalnızca ORM
    üzerinden silinen nesneleri görür. İz bırakılmazsa canlıda "kayıtlar
    nereye gitti?" sorusunun cevabı hiçbir yerde olmaz.
    """
    await _v1_kayitlari_kur(db_oturum, demo)
    await demo.main()

    kayit = await db_oturum.scalar(
        select(IslemGecmisi).where(IslemGecmisi.kayit_tipi == "demo_verisi"))
    assert kayit is not None, "Temizliğin izi işlem geçmişine yazılmamış"
    assert kayit.islem == "silme"
    assert kayit.eski_deger["tespit"] >= 4
    assert kayit.yeni_deger["sebepler"]


# --- Damganın kendisi ------------------------------------------------------

async def test_ayni_damgada_yeniden_kurulmaz(demo, db_oturum):
    """İkinci çalıştırma hiçbir kaydı değiştirmemeli.

    Bu, erken dönüşün KORUNAN yanıdır: mükerrer tespit birikmez ve
    jürinin girdiği kayıtlar her açılışta silinmez.
    """
    await demo.main()
    db_oturum.expire_all()
    once = await _sayimlar(db_oturum)
    tespit_idler = sorted(await db_oturum.scalars(select(Tespit.id)))

    await demo.main()
    db_oturum.expire_all()
    assert await _sayimlar(db_oturum) == once
    assert sorted(await db_oturum.scalars(select(Tespit.id))) == tespit_idler, (
        "Kayıtlar silinip yeniden kurulmuş; damga işe yaramıyor")


async def test_sinif_listesi_degisince_damga_degisir(demo, monkeypatch):
    """Damga sınıf listesinden BESLENMELİ.

    02.09'daki arıza tam olarak buydu: sınıf listesi değişti, demo verisi
    değişmedi. Damga sınıf listesini içermeseydi yeni mantık da o
    değişimi kaçırırdı.
    """
    ilk = demo.demo_damgasi()

    veri = copy.deepcopy(yapilandirma.siniflar())
    veri["surum"] = "9.9"
    veri["siniflar"] = veri["siniflar"][:-1]
    yapilandirma.siniflar.cache_clear()
    monkeypatch.setattr(yapilandirma, "siniflar", lambda: veri)
    monkeypatch.setattr(demo, "siniflar", lambda: veri)
    try:
        assert demo.demo_damgasi() != ilk
    finally:
        monkeypatch.undo()
        yapilandirma.siniflar.cache_clear()


async def test_sinif_listesi_degisirse_veri_yeniden_kurulur(demo, db_oturum):
    """Damga eskidiyse senaryo yeniden kurulmalı — asıl arızanın kapağı."""
    await demo.main()
    db_oturum.expire_all()

    # Canlıdaki hâlin benzetimi: damga var ama ESKİ sürümden.
    d = await db_oturum.scalar(select(DemoDamgasi))
    d.damga = "0" * 64
    d.siniflar = "ahsap,beton_tugla,cam,metal,seramik"
    await db_oturum.commit()

    await demo.main()
    db_oturum.expire_all()
    d = await db_oturum.scalar(select(DemoDamgasi))
    assert d.damga == demo.demo_damgasi()
    assert d.siniflar == ",".join(
        s["ad"] for s in yapilandirma.siniflar()["siniflar"])


async def test_zorlama_ortam_degiskeni_yeniden_kurar(demo, db_oturum, monkeypatch):
    """`DEMO_VERISI_ZORLA=1` — Render panelinden tek seferlik tetikleme."""
    await demo.main()
    db_oturum.expire_all()
    tespit_idler = sorted(await db_oturum.scalars(select(Tespit.id)))

    monkeypatch.setenv("DEMO_VERISI_ZORLA", "1")
    await demo.main()
    db_oturum.expire_all()
    yeni_idler = sorted(await db_oturum.scalars(select(Tespit.id)))
    assert yeni_idler != tespit_idler, "Zorlamaya rağmen yeniden kurulmadı"
    assert len(yeni_idler) == len(tespit_idler), "Kayıtlar mükerrerleşti"


# --- Görüntü dosyaları -----------------------------------------------------

async def test_gorseller_her_acilista_geri_kopyalanir(demo):
    """Render'ın efemer dosya sistemi: dosya silinse de geri gelmeli.

    Eskiden kopyalama senaryo kurulumunun içindeydi ve kurulum "zaten
    var" diye atlandığı için dosyalar bir daha hiç geri gelmiyordu;
    arayüzde tespit kutularının yerinde kırık görsel çıkıyordu.
    """
    yollar, _ = demo._gorselleri_kopyala()
    klasor = demo.ayarlar().yukleme_yolu
    hedef = klasor / yollar[0]
    assert hedef.is_file()

    hedef.unlink()
    _, kopyalanan = demo._gorselleri_kopyala()
    assert yollar[0] in kopyalanan
    assert hedef.is_file() and hedef.stat().st_size > 0


async def test_bos_dosya_da_eksik_sayilir(demo):
    """Sıfır baytlık dosya = kırık görsel; yeniden kopyalanmalı."""
    yollar, _ = demo._gorselleri_kopyala()
    hedef = demo.ayarlar().yukleme_yolu / yollar[1]
    hedef.write_bytes(b"")
    _, kopyalanan = demo._gorselleri_kopyala()
    assert yollar[1] in kopyalanan
    assert hedef.stat().st_size > 0


# --- Betiğin kendi koruması ------------------------------------------------

def test_senaryo_bilinmeyen_sinif_kurmaya_calisirsa_durur(demo):
    """Demo verisi de aynı tuzağa düşebilir; sessizce değil AÇIKÇA durmalı.

    `demo_tespitleri.json` eski bir ağırlıkla üretilmişse, temizlediğimiz
    arızayı bu kez betiğin kendisi kurar.
    """
    sahte_kaynak = {"goruntuler": [
        {"tespitler": [{"sinif": "sert_plastik"}]},
    ]}
    with pytest.raises(SystemExit) as e:
        demo._senaryo_siniflarini_denetle(sahte_kaynak)
    assert "sert_plastik" in str(e.value)
    assert "siniflar.json" in str(e.value)


def test_gercek_senaryo_denetimden_gecer(demo):
    """Depodaki gerçek model çıktısı güncel sınıf listesiyle uyumlu olmalı."""
    demo._senaryo_siniflarini_denetle(demo._tespit_kaynagi())


# --- Sorgu yardımcısı ------------------------------------------------------

async def test_bilinmeyen_sinif_sorgusu_yakalar(db_oturum, tespit_kur):
    """`bilinmeyen_sinifli_tespitler()` gerçekten yakalıyor mu?

    Bu sorgu temizliğin ölçütü; yanlış çalışırsa temizlik de sessizce
    hiçbir şey yapmaz.
    """
    gecerli = await tespit_kur("beton")
    olu = await tespit_kur("sert_plastik", sinif_dogrula=False)

    bulunan = {t.id for t in await db_oturum.scalars(
        bilinmeyen_sinifli_tespitler())}
    assert olu in bulunan
    assert gecerli not in bulunan


async def test_bilinmeyen_duzeltme_de_yakalanir(db_oturum, tespit_kur):
    """Uzman düzeltmesi eski bir sınıfa bakıyorsa o kayıt da bozuktur."""
    tid = await tespit_kur("beton")
    t = await db_oturum.get(Tespit, tid)
    t.duzeltilen_sinif = "konteyner"
    await db_oturum.commit()

    bulunan = {x.id for x in await db_oturum.scalars(
        bilinmeyen_sinifli_tespitler())}
    assert tid in bulunan
