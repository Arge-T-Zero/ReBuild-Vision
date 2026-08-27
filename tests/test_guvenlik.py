"""Güvenlik korumaları.

Depo herkese açık olduğunda kodda yazılı her varsayılan da herkese açıktır.
Bu testler, güvensiz varsayılanlarla yayına çıkılmasını engelleyen
korumaların sessizce kaldırılmamasını sağlar.
"""
from __future__ import annotations

import pytest

from api.app.core.config import GUVENSIZ_VARSAYILAN_ANAHTAR, Ayarlar
from api.app.core.security import jeton_coz, jeton_uret, parola_ozetle, parola_dogrula


def test_uretimde_varsayilan_jwt_anahtari_reddedilir():
    """Varsayılan anahtarla ORTAM=uretim açılışı DURDURUR.

    Bu anahtar depoda açıkça yazılıdır; onunla imzalanan jetonlar taklit
    edilebilir ve herhangi biri kendine yönetici jetonu üretebilir.
    """
    with pytest.raises(RuntimeError) as h:
        Ayarlar(ortam="uretim", jwt_gizli_anahtar=GUVENSIZ_VARSAYILAN_ANAHTAR)
    assert "JWT_GIZLI_ANAHTAR" in str(h.value)


def test_uretimde_gercek_anahtar_kabul_edilir():
    a = Ayarlar(ortam="uretim", jwt_gizli_anahtar="x" * 48)
    assert a.ortam == "uretim"


def test_gelistirmede_varsayilan_anahtar_engellenmez():
    """Yerel geliştirme uyarıyla çalışmaya devam eder."""
    a = Ayarlar(ortam="gelistirme", jwt_gizli_anahtar=GUVENSIZ_VARSAYILAN_ANAHTAR)
    assert a.jwt_gizli_anahtar == GUVENSIZ_VARSAYILAN_ANAHTAR


def test_parola_duz_metin_saklanmaz():
    ozet = parola_ozetle("gizliparola123")
    assert ozet != "gizliparola123"
    assert "gizliparola123" not in ozet
    assert parola_dogrula("gizliparola123", ozet)
    assert not parola_dogrula("yanlisparola", ozet)


def test_ayni_parola_farkli_ozet_uretir():
    """bcrypt tuzu — aynı parolanın özeti her seferinde farklı olmalı."""
    assert parola_ozetle("aynisi") != parola_ozetle("aynisi")


def test_bozuk_jeton_cozulmez():
    assert jeton_coz("bu.bir.jeton.degil") is None
    assert jeton_coz("") is None


def test_baska_anahtarla_imzalanan_jeton_reddedilir():
    """Jeton taklidi engellenir."""
    import jwt as pyjwt

    sahte = pyjwt.encode(
        {"sub": "1", "rol": "yonetici"}, "saldirganin-anahtari", algorithm="HS256"
    )
    assert jeton_coz(sahte) is None


def test_gecerli_jeton_rol_tasir():
    yuk = jeton_coz(jeton_uret(7, "uzman"))
    assert yuk is not None
    assert yuk["sub"] == "7"
    assert yuk["rol"] == "uzman"


def test_ortam_degiskenlerindeki_bosluk_kirpilir():
    """Panele yapıştırırken sona karışan satır sonu ayarı bozmamalı.

    Render'a yapıştırılan bağlantı dizesinin sonuna bir '\\n' karışmıştı;
    asyncpg 'database "postgres\\n" does not exist' diyerek reddetti. Dize
    doğruydu, görünmez karakter yüzünden başarısız oldu.
    """
    a = Ayarlar(
        veritabani_url="postgresql+asyncpg://localhost:5433/rebuild_vision\n",
        model_service_url="  http://localhost:8090  ",
        jwt_gizli_anahtar="x" * 48,
    )
    assert a.veritabani_url.endswith("rebuild_vision")
    assert "\n" not in a.veritabani_url
    assert a.model_service_url == "http://localhost:8090"
