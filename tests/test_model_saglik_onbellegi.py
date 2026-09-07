"""Model sağlık sorgusu — önbellek ve 429 ayrımı.

⚠️ BU DOSYA 06.09.2026'DA BİR CANLI ARIZASINDAN SONRA YAZILDI.

Yükleme sayfasında kırmızı "MODEL YOK" rozetiyle şu yazıyordu:

    Model servisine ulaşılamadı: Client error '429 Too Many Requests'
    for url 'https://rebuild-vision-model.onrender.com/health'

Model servisi ÇALIŞIYORDU: aynı adres doğrudan çağrıldığında
`{"durum":"calisiyor","sahte":false,"agirlik_yuklendi":true}` dönüyordu.
İki ayrı hata vardı:

  1. `/health` çok sık çağrılıyordu (`/sistem/durum` her sayfa
     yüklemesinde, ayrıca her görüntü yüklemesinde bir kez) ve Render'ın
     ücretsiz katmanı bunu hız sınırına takıyordu.
  2. 429 "model yok" gibi gösteriliyordu. 429 servisin ÇALIŞTIĞINI ama
     şu an cevap veremediğini söyler; ikisini aynı göstermek yanlış
     beyandır.
"""
from __future__ import annotations

import httpx
import pytest

from api.app.services import model_client


class _SahteIstemci:
    """`httpx.AsyncClient` yerine geçen sayaçlı sahte istemci."""

    cagri = 0
    yanit_uretici = None

    def __init__(self, *a, **kw):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def get(self, url):
        type(self).cagri += 1
        return type(self).yanit_uretici(url)


def _yanit(kod: int, govde: dict | None = None,
           basliklar: dict | None = None) -> httpx.Response:
    return httpx.Response(
        kod, json=govde or {}, headers=basliklar or {},
        request=httpx.Request("GET", "http://model.test/health"),
    )


@pytest.fixture
def sahte_istemci(monkeypatch):
    _SahteIstemci.cagri = 0
    _SahteIstemci.yanit_uretici = None
    monkeypatch.setattr(model_client.httpx, "AsyncClient", _SahteIstemci)
    model_client.onbellegi_temizle()
    yield _SahteIstemci
    model_client.onbellegi_temizle()


SAGLAM = {"durum": "calisiyor", "sahte": False, "agirlik_yuklendi": True,
          "calisma_zamani": "onnx", "sinif_sayisi": 5}


# --- Önbellek --------------------------------------------------------------

async def test_ardarda_cagrilar_tek_istek_uretir(sahte_istemci):
    """Asıl hız sınırı sebebi: aynı cevabı defalarca sormak."""
    sahte_istemci.yanit_uretici = lambda url: _yanit(200, SAGLAM)

    for _ in range(10):
        assert (await model_client.saglik())["sahte"] is False
    assert sahte_istemci.cagri == 1, (
        f"10 çağrı {sahte_istemci.cagri} HTTP isteği üretti; önbellek "
        "çalışmıyor ve hız sınırı yeniden tetiklenir")


async def test_onbellek_suresi_dolunca_yeniden_sorulur(sahte_istemci, monkeypatch):
    """Önbellek KISA olmalı: servis geri geldiğinde arayüz öğrenmeli."""
    sahte_istemci.yanit_uretici = lambda url: _yanit(200, SAGLAM)
    await model_client.saglik()
    assert sahte_istemci.cagri == 1

    # Saati ileri al: gerçek beklemek testi yavaşlatır ve kırılgan yapar.
    gercek = model_client.time.monotonic
    monkeypatch.setattr(
        model_client.time, "monotonic",
        lambda: gercek() + model_client.SAGLIK_ONBELLEK_SANIYE + 1)
    await model_client.saglik()
    assert sahte_istemci.cagri == 2


async def test_onbellek_temizlenince_yeniden_sorulur(sahte_istemci):
    sahte_istemci.yanit_uretici = lambda url: _yanit(200, SAGLAM)
    await model_client.saglik()
    model_client.onbellegi_temizle()
    await model_client.saglik()
    assert sahte_istemci.cagri == 2


async def test_hata_da_onbelleklenir(sahte_istemci):
    """Servis düştüğünde her sayfa yüklemesi yeni bir istek üretmemeli."""
    sahte_istemci.yanit_uretici = lambda url: _yanit(429)

    for _ in range(5):
        with pytest.raises(model_client.ModelServisiHatasi):
            await model_client.saglik()
    assert sahte_istemci.cagri == 1


# --- 429 ayrımı ------------------------------------------------------------

async def test_429_hiz_siniri_olarak_isaretlenir(sahte_istemci):
    """429 = "servis meşgul", "ağırlık yüklü değil" DEĞİL."""
    sahte_istemci.yanit_uretici = lambda url: _yanit(429)

    with pytest.raises(model_client.ModelServisiHatasi) as e:
        await model_client.saglik()
    assert e.value.durum_kodu == 429
    assert e.value.hiz_siniri is True


async def test_baglanti_hatasi_hiz_siniri_degildir(sahte_istemci):
    """Gerçekten ulaşılamayan servis 'meşgul' diye gösterilmemeli."""
    def _patla(url):
        raise httpx.ConnectError("baglanti yok")

    sahte_istemci.yanit_uretici = _patla
    with pytest.raises(model_client.ModelServisiHatasi) as e:
        await model_client.saglik()
    assert e.value.hiz_siniri is False
    assert e.value.durum_kodu is None


async def test_500_hiz_siniri_degildir(sahte_istemci):
    sahte_istemci.yanit_uretici = lambda url: _yanit(500)
    with pytest.raises(model_client.ModelServisiHatasi) as e:
        await model_client.saglik()
    assert e.value.durum_kodu == 500
    assert e.value.hiz_siniri is False


async def test_retry_after_basligina_uyulur(sahte_istemci):
    sahte_istemci.yanit_uretici = lambda url: _yanit(
        429, basliklar={"Retry-After": "30"})
    with pytest.raises(model_client.ModelServisiHatasi) as e:
        await model_client.saglik()
    assert e.value.tekrar_dene_saniye == 30.0


async def test_asiri_retry_after_kirpilir(sahte_istemci):
    """Sunucu saatlerce beklememizi isterse arayüz o kadar kör kalmamalı."""
    sahte_istemci.yanit_uretici = lambda url: _yanit(
        429, basliklar={"Retry-After": "99999"})
    with pytest.raises(model_client.ModelServisiHatasi) as e:
        await model_client.saglik()
    assert e.value.tekrar_dene_saniye == model_client.EN_UZUN_BEKLEME_SANIYE


# --- Uç noktalara yansıması ------------------------------------------------

async def test_sistem_durumu_429u_model_yok_diye_gostermez(istemci, sahte_istemci):
    """Arayüzün üç durumu ayırabilmesi için alanlar yanıtta olmalı."""
    sahte_istemci.yanit_uretici = lambda url: _yanit(429)

    d = (await istemci.get("/sistem/durum")).json()["model_servisi"]
    assert d["ulasilabilir"] is False
    assert d["hiz_siniri"] is True
    assert d["durum_kodu"] == 429
    # `sahte` BİLİNMİYOR — false yazmak "gerçek model çalışıyor" demek
    # olurdu (ana talimat Bölüm 9.5).
    assert d["sahte"] is None


async def test_sistem_durumu_saglam_serviste_sahteligi_bildirir(
    istemci, sahte_istemci
):
    sahte_istemci.yanit_uretici = lambda url: _yanit(
        200, {**SAGLAM, "sahte": True, "model": "yolo11-rebuild-SAHTE"})
    d = (await istemci.get("/sistem/durum")).json()["model_servisi"]
    assert d["ulasilabilir"] is True
    assert d["sahte"] is True


async def test_yukleme_429da_500_dondurmez(
    istemci, jeton, kullanicilar, sahte_istemci, db_oturum
):
    """429'da kullanıcı "Internal Server Error" görmemeli.

    `ModelServisiHatasi` bir `RuntimeError`'dı ve yakalanmıyordu.
    """
    from api.app.models import EnkazAlani

    alan = EnkazAlani(ad="Test Alan", olusturan_id=kullanicilar["belediye"])
    db_oturum.add(alan)
    await db_oturum.commit()

    sahte_istemci.yanit_uretici = lambda url: _yanit(429)
    y = await istemci.post(
        f"/goruntu/yukle/{alan.id}",
        headers=await jeton("saha"),
        files={"dosyalar": ("a.jpg", b"veri", "image/jpeg")},
    )
    assert y.status_code == 503, y.text
    mesaj = y.json()["detail"]
    assert "yoğun" in mesaj
    # Kullanıcıya ne yapacağı söylenmeli; "hata oluştu" yetmez.
    assert "tekrar deneyin" in mesaj


async def test_yukleme_429da_uydurma_tespit_uretmez(
    istemci, jeton, kullanicilar, sahte_istemci, db_oturum
):
    """Ana talimat Bölüm 9.5: model yoksa sahte çıktı üretilmez."""
    from sqlalchemy import func, select

    from api.app.models import EnkazAlani, Goruntu, Tespit

    alan = EnkazAlani(ad="Test Alan", olusturan_id=kullanicilar["belediye"])
    db_oturum.add(alan)
    await db_oturum.commit()

    sahte_istemci.yanit_uretici = lambda url: _yanit(429)
    await istemci.post(
        f"/goruntu/yukle/{alan.id}",
        headers=await jeton("saha"),
        files={"dosyalar": ("a.jpg", b"veri", "image/jpeg")},
    )
    assert await db_oturum.scalar(select(func.count(Tespit.id))) == 0
    assert await db_oturum.scalar(select(func.count(Goruntu.id))) == 0
