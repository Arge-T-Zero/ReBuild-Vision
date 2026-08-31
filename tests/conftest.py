"""Test altyapısı.

Testler AYRI bir veri tabanında çalışır (`rebuild_vision_test`); geliştirme
veri tabanına dokunmaz.

Şema `Temel.metadata.create_all` ile değil, **gerçek Alembic göçüyle**
kurulur — böylece göç dosyası da her test çalıştırmasında sınanmış olur.
"""
from __future__ import annotations

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
TEST_URL = f"postgresql+asyncpg://localhost:{PG_PORT}/{TEST_VT}"

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


@pytest_asyncio.fixture
async def tespit_kur(kullanicilar):
    """Alan → görüntü → tespit zinciri kurar, tespit id'sini döner."""
    async def kur(sinif: str = "beton", guven: float = 0.9,
                  inceleme: bool = False,
                  dogrulama: str = "beklemede") -> int:
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
