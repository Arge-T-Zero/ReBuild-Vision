"""Test altyapısı.

Testler AYRI bir veri tabanında çalışır (`rebuild_vision_test`); geliştirme
veri tabanına dokunmaz.

Şema `Temel.metadata.create_all` ile değil, **gerçek Alembic göçüyle**
kurulur — böylece göç dosyası da her test çalıştırmasında sınanmış olur.
"""
from __future__ import annotations

import copy
import os
import subprocess
import sys
from pathlib import Path

DEPO_KOKU = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPO_KOKU))

TEST_VT = os.environ.get("TEST_VERITABANI", "rebuild_vision_test")
PG_BIN = os.environ.get("PG_BIN", "/opt/homebrew/opt/postgresql@17/bin")
PG_PORT = os.environ.get("PGPORT", "5433")
# Alembic yolu da PG_BIN gibi ortamdan geçersiz kılınabilir. Sabit mutlak
# yol, depoyu farklı bir makinede (CI, jüri değerlendirmesi, Linux
# geliştirme kabı) çalıştıran herkesi kilitliyordu; PG_BIN zaten
# geçersiz kılınabilirken bu satırın kalması bir tutarsızlıktı.
ALEMBIC = os.environ.get("ALEMBIC", str(DEPO_KOKU / "api/.venv/bin/alembic"))

# Bağlantı kimliği ortamdan gelir.
#
# ⚠️ BAĞLANTI ADRESİ SABİT KODLANMIŞTI ve CI'da tüm testler patlıyordu.
# Geliştirme makinesinde veri tabanı yerelde, geliştiricinin kendi
# adıyla açılmış bir rolle çalışıyor; orada kullanıcı adı vermeye gerek
# yok. CI'da ise veri tabanı AYRI BİR KAPSAYICIDA ve yalnızca `postgres`
# rolü var — asyncpg kimlik verilmediğinde işletim sistemi kullanıcısıyla
# (`runner`) bağlanmaya çalışıyor ve sunucu "role does not exist" diyor.
#
# Varsayılanlar bilinçli olarak BUGÜNKÜ davranışı korur: `PGUSER`
# tanımlı değilse adres eskisiyle birebir aynı üretilir, yani
# geliştirme makinesinde hiçbir şey değişmez.
PG_HOST = os.environ.get("PGHOST", "localhost")
PG_KULLANICI = os.environ.get("PGUSER", "")
PG_PAROLA = os.environ.get("PGPASSWORD", "")
_KIMLIK = f"{PG_KULLANICI}:{PG_PAROLA}@" if PG_KULLANICI else ""
TEST_URL = f"postgresql+asyncpg://{_KIMLIK}{PG_HOST}:{PG_PORT}/{TEST_VT}"

# Uygulama modülleri içe aktarılmadan ÖNCE ayarlanmalı: config.py bunu okur.
os.environ["VERITABANI_URL"] = TEST_URL
os.environ["MODEL_SERVICE_URL"] = "http://localhost:8090"

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import select, text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession, async_sessionmaker, create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

import api.app.db as db_modulu  # noqa: E402

# Havuzlanmış bağlantılar testler arasında farklı olay döngülerine takılır.
# NullPool her oturumda taze bağlantı açar ve kapatır; döngü çakışması olmaz.
# `oturum()` bağımlılığı OturumUret'i çağrı anında aradığı için bu değişim
# uygulama koduna dokunmadan etkili olur.
db_modulu.motor = create_async_engine(TEST_URL, poolclass=NullPool, future=True)
db_modulu.OturumUret = async_sessionmaker(
    db_modulu.motor, expire_on_commit=False, class_=AsyncSession
)

import api.app.core.config as yapilandirma  # noqa: E402
from api.app.core.permissions import OnayDurumu, Rol  # noqa: E402
from api.app.core.security import parola_ozetle  # noqa: E402
from api.app.main import app  # noqa: E402
from api.app.models import EnkazAlani, Goruntu, Kullanici, Tespit  # noqa: E402

TABLOLAR = [
    "miktar_hesabi", "tehlikeli_kayit", "olcum", "tespit",
    "goruntu", "enkaz_alani", "islem_gecmisi", "kullanici",
]

TEST_PAROLA = "test12345"


def _psql(vt: str, sql: str) -> str:
    return subprocess.run(
        [f"{PG_BIN}/psql", "-p", PG_PORT, "-d", vt, "-tAc", sql],
        capture_output=True, text=True,
    ).stdout


@pytest.fixture(scope="session", autouse=True)
def _test_veritabani():
    """Test veri tabanını oluşturur ve Alembic göçünü uygular."""
    if "1" not in _psql("postgres",
                        f"select 1 from pg_database where datname='{TEST_VT}'"):
        subprocess.run([f"{PG_BIN}/createdb", "-p", PG_PORT, TEST_VT], check=True)
    _psql(TEST_VT, "CREATE EXTENSION IF NOT EXISTS postgis;")

    ortam = {**os.environ, "VERITABANI_URL": TEST_URL}
    s = subprocess.run(
        [ALEMBIC,
         "-c", str(DEPO_KOKU / "api/alembic.ini"), "upgrade", "head"],
        cwd=DEPO_KOKU, env=ortam, capture_output=True, text=True,
    )
    assert s.returncode == 0, f"Alembic göçü başarısız:\n{s.stderr}"
    yield


@pytest.fixture(autouse=True)
def _temiz_tablolar():
    """Her testten önce tabloları boşaltır (senkron psql — döngüden bağımsız)."""
    _psql(TEST_VT, f"TRUNCATE {', '.join(TABLOLAR)} RESTART IDENTITY CASCADE")
    yield


@pytest_asyncio.fixture
async def istemci():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest_asyncio.fixture
async def kullanicilar() -> dict[str, int]:
    """Her rolden onaylı bir test kullanıcısı. rol adı -> kullanıcı id."""
    async with db_modulu.OturumUret() as db:
        for rol in Rol:
            db.add(Kullanici(
                eposta=f"{rol.value}@test.local",
                sifre_hash=parola_ozetle(TEST_PAROLA),
                ad=f"Test {rol.value}",
                rol=rol,
                onay_durumu=OnayDurumu.ONAYLANDI,
            ))
        await db.commit()
        y = await db.execute(select(Kullanici))
        return {k.rol.value: k.id for k in y.scalars()}


@pytest_asyncio.fixture
async def jeton(istemci, kullanicilar):
    """rol adı -> Authorization başlığı."""
    async def al(rol: str) -> dict[str, str]:
        y = await istemci.post("/auth/giris", json={
            "eposta": f"{rol}@test.local", "parola": TEST_PAROLA,
        })
        assert y.status_code == 200, y.text
        return {"Authorization": f"Bearer {y.json()['jeton']}"}
    return al


@pytest.fixture
def malzeme_olmayan_sinif(monkeypatch):
    """K-007 mekanizmasını sınamak için sahte bir "malzeme değil" sınıfı.

    02.09.2026'ya kadar bu rolü gerçek bir sınıf, `konteyner` (skip bin)
    oynuyordu. Model takımın kendi veri setiyle yeniden eğitilince o
    sınıf kalktı ve `siniflar.json` içinde `malzeme_mi: false` işaretli
    TEK BİR SINIF BİLE KALMADI.

    Testleri olduğu gibi bırakmak en kötü seçenekti: `konteyner` artık
    tanınmayan bir ad olduğu için sorgu onu yine eliyordu ve testler
    YEŞİL KALIYORDU — ama artık K-007'yi değil, "bilinmeyen sınıf
    süzülür"ü sınıyorlardı. Yeşil bir test, sınadığını sandığın şeyi
    sınamıyorsa korumadan beter: koruma yokken var sanılır.

    Bu yüzden mekanizma, ona ihtiyaç duyan koşul ÜRETİLEREK sınanır.
    `siniflar()` ve `malzeme_siniflari()` aynı modülde yaşayan
    `lru_cache`'li iki fonksiyondur ve ikincisi birincisini modül
    genelinden çağırır; bu yüzden `siniflar`'ı değiştirip iki önbelleği
    de temizlemek, fonksiyonu içeri aktarmış tüm modülleri kapsar.
    """
    veri = copy.deepcopy(yapilandirma.siniflar())
    veri["siniflar"].append({
        "id": 900,
        "ad": "test_malzeme_degil",
        "gorunen_ad": "Test — malzeme değil",
        "malzeme_mi": False,
        "renk": "#000000",
    })

    def temizle() -> None:
        yapilandirma.siniflar.cache_clear()
        yapilandirma.malzeme_siniflari.cache_clear()

    temizle()
    monkeypatch.setattr(yapilandirma, "siniflar", lambda: veri)
    yield "test_malzeme_degil"
    monkeypatch.undo()
    temizle()


@pytest_asyncio.fixture
async def tespit_kur(kullanicilar):
    """Alan → görüntü → tespit zinciri kurar, tespit id'sini döner."""
    async def kur(sinif: str = "beton", guven: float = 0.9,
                  inceleme: bool = False,
                  dogrulama: str = "beklemede",
                  sinif_dogrula: bool = True) -> int:
        # Sınıf adı `siniflar.json`'da GERÇEKTEN var mı?
        #
        # Bu denetim, 02.09.2026'da sınıf listesi 10'dan 5'e inerken
        # yaşanan sessiz arızadan sonra eklendi: testlerin yarısı artık
        # var olmayan adlarla (`beton`, `sert_plastik`, `konteyner`)
        # kayıt kuruyordu. Hiçbiri patlamadı — çünkü tanınmayan sınıf da
        # malzeme süzgecinden eleniyor. Testler yeşildi ve YANLIŞ ŞEYİ
        # sınıyordu.
        #
        # `sinif_dogrula=False` bilinçli kaçış kapısıdır: "bilinmeyen
        # sınıf hesaba girmez" davranışını sınayan test, bilinmeyen bir
        # ad kurabilmelidir.
        if sinif_dogrula:
            # Modül üzerinden okunur, doğrudan içe aktarılan bir adla
            # değil: `malzeme_olmayan_sinif` fixture'ı `siniflar`'ı
            # yamalıyor ve denetim o yamayı GÖRMEK zorunda, yoksa
            # fixture'ın enjekte ettiği sınıfı "tanımsız" sanar.
            tanimli = {s["ad"] for s in yapilandirma.siniflar()["siniflar"]}
            assert sinif in tanimli, (
                f"Test '{sinif}' sınıfıyla kayıt kuruyor ama bu ad "
                f"siniflar.json'da yok. Tanımlı olanlar: {sorted(tanimli)}. "
                "Sınıf listesi değiştiyse test de güncellenmeli; bilinmeyen "
                "bir ad kullanmak testi sessizce anlamsızlaştırır. Bilerek "
                "bilinmeyen bir sınıf kuruluyorsa sinif_dogrula=False geçin."
            )
        # `dogrulama` varsayılanı `beklemede`: modelden yeni çıkmış bir
        # tespitin gerçek hâli budur. Miktar hesabı sınayan testler
        # açıkça "onaylandi" geçmek zorundadır — doğrulanmamış kayıt
        # miktara giremez (Bölüm 1.4).
        async with db_modulu.OturumUret() as db:
            a = EnkazAlani(ad="Test Alan", olusturan_id=kullanicilar["belediye"])
            db.add(a)
            await db.flush()
            g = Goruntu(enkaz_alani_id=a.id, dosya_yolu="t.jpg",
                        genislik=1000, yukseklik=800,
                        yukleyen_id=kullanicilar["saha"])
            db.add(g)
            await db.flush()
            t = Tespit(goruntu_id=g.id, sinif=sinif, guven_skoru=guven,
                       bbox={"x": 1, "y": 1, "w": 10, "h": 10},
                       bbox_format="pixel_absolute_original",
                       inceleme_gerekli=inceleme,
                       dogrulama_durumu=dogrulama)
            db.add(t)
            await db.commit()
            return t.id
    return kur


@pytest_asyncio.fixture
async def db_oturum():
    """Doğrudan veri tabanı erişimi gereken testler için."""
    async with db_modulu.OturumUret() as s:
        yield s
