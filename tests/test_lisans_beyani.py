"""Lisans beyanı GERÇEK bağımlılıklarla aynı olmalı — şartname Madde 10.4.

> "Kullanılan tüm kütüphane, çerçeve, model ve veri setlerinin lisans
> bilgileri açıkça beyan edilecektir."

⚠️ BU TEST 02.09.2026'DA BİR DENETİMDEN SONRA YAZILDI.

`docs/lisans-analizi.md` sürüm sütununda **on bir satır yanlıştı** (ör.
fastapi için 0.141 yazıyordu, sabitlenmiş sürüm 0.115.6), listede
**olmayan bir paket** vardı (`@tanstack/react-query`) ve `package.json`'da
olan **üç paket listede yoktu**. Lisansların kendisi doğruydu; ayrışan
sürüm ve kapsamdı.

Belgenin kendi bakım kuralı (Bölüm 8) "her yeni bağımlılıkta bu tablo
aynı commit'te güncellenir" diyordu — kural vardı, mekanizması yoktu ve
fiilen işlemiyordu. Bu depo aynı sorunu başka bir yerde mekanizmayla
çözmüş (`data.yaml` ↔ `siniflar.json`, `test_sinif_tanimlari.py`); burada
da öyle çözülüyor.

Test, beyanı manifestolara bağlar: biri değişip diğeri değişmezse kırılır.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DEPO_KOKU = Path(__file__).resolve().parents[1]
BEYAN = DEPO_KOKU / "docs/lisans-analizi.md"


def _beyan_metni() -> str:
    return BEYAN.read_text(encoding="utf-8")


def _tablo_satirlari() -> dict[str, str]:
    """Beyandaki `| paket | sürüm | ...` satırlarını ad → sürüm olarak verir.

    Markdown kalın işaretleri (`**asyncpg**`) ve ters tırnaklar temizlenir;
    beyan biçimi okunabilirlik için değişebilir, testin buna takılmaması
    gerekir.
    """
    satirlar: dict[str, str] = {}
    for satir in _beyan_metni().splitlines():
        if not satir.startswith("|"):
            continue
        h = [x.strip().strip("*`") for x in satir.strip("|").split("|")]
        if len(h) < 2 or h[0].lower() in {"paket", "kaynak", "---"}:
            continue
        if set(h[0]) <= {"-"}:
            continue
        satirlar[h[0]] = h[1]
    return satirlar


def _python_bagimliliklari(dosya: str) -> dict[str, str]:
    """`ad==sürüm` satırlarını okur. `-r` yönlendirmeleri izlenmez."""
    metin = (DEPO_KOKU / dosya).read_text(encoding="utf-8")
    paketler: dict[str, str] = {}
    for satir in metin.splitlines():
        satir = satir.split("#", 1)[0].strip()
        if not satir or satir.startswith("-r"):
            continue
        if "==" not in satir:
            continue
        ad, surum = satir.split("==", 1)
        paketler[ad.strip()] = surum.strip()
    return paketler


def _npm_bagimliliklari() -> dict[str, str]:
    d = json.loads((DEPO_KOKU / "web/package.json").read_text(encoding="utf-8"))
    return {**d.get("dependencies", {}), **d.get("devDependencies", {})}


# --- Python (api/) --------------------------------------------------------


def test_backend_paketleri_beyanda_ve_surumleri_ayni():
    """`api/requirements.txt` ↔ beyan tablosu."""
    tablo = _tablo_satirlari()
    for ad, surum in _python_bagimliliklari("api/requirements.txt").items():
        assert ad in tablo, (
            f"'{ad}' api/requirements.txt'te var ama docs/lisans-analizi.md'de "
            f"YOK. Madde 10.4 her bileşenin lisansının beyan edilmesini "
            f"istiyor; beyan edilmeyen paket koda giremez (belgenin Bölüm 8 "
            f"bakım kuralı)."
        )
        assert tablo[ad] == surum, (
            f"'{ad}' sürümü ayrışmış — beyan: {tablo[ad]}, gerçek: {surum}. "
            f"Hatalı bir sürüm beyanı, denetlenemez bir beyandır."
        )


def test_gelistirme_paketleri_de_beyanda():
    """Test araçları da beyan edilir; teslim imajına girmeseler bile."""
    tablo = _tablo_satirlari()
    for ad, surum in _python_bagimliliklari("api/requirements-dev.txt").items():
        assert ad in tablo, f"'{ad}' (dev) beyanda yok"
        assert tablo[ad] == surum, (
            f"'{ad}' (dev) sürümü ayrışmış — beyan: {tablo[ad]}, gerçek: {surum}"
        )


def test_model_servisi_paketleri_beyanda():
    """AGPL sınırındaki paketler — en kritik beyan."""
    tablo = _tablo_satirlari()
    paketler = _python_bagimliliklari("model-service/requirements.txt")
    assert "ultralytics" in paketler, (
        "model-service/requirements.txt içinde ultralytics yok; AGPL "
        "analizinin dayanağı kayboldu"
    )
    for ad in paketler:
        assert ad in tablo, f"'{ad}' (model servisi) beyanda yok"


# --- Web (npm) ------------------------------------------------------------


def test_web_paketleri_beyanda_ve_surumleri_ayni():
    tablo = _tablo_satirlari()
    for ad, surum in _npm_bagimliliklari().items():
        # react ve react-dom beyanda tek satırda birleştirilmiş.
        aday = "react / react-dom" if ad in {"react", "react-dom"} else ad
        assert aday in tablo, (
            f"'{ad}' web/package.json'da var ama beyanda YOK"
        )
        assert tablo[aday] == surum, (
            f"'{ad}' sürümü ayrışmış — beyan: {tablo[aday]}, gerçek: {surum}"
        )


def test_beyanda_olup_projede_olmayan_paket_yok():
    """Hayalet satır, eksik satır kadar kusurludur.

    `@tanstack/react-query` beyanda vardı, projede yoktu. İkisi de beyanın
    gerçekle denetlenmediğini gösterir; jüri bir paketi arayıp
    bulamadığında beyanın tamamına olan güven düşer.
    """
    gercek = set(_npm_bagimliliklari())
    metin = _beyan_metni()
    # Beyandaki npm kapsam adlarını (@scope/ad) tara.
    for ad in set(re.findall(r"\|\s*(@[a-z0-9-]+/[a-z0-9-]+)\s*\|", metin)):
        assert ad in gercek, (
            f"'{ad}' docs/lisans-analizi.md'de beyan edilmiş ama "
            f"web/package.json'da YOK. Var olmayan bir paketi beyan etmek, "
            f"beyanın denetlenmediğini gösterir."
        )


# --- Mobil (pub) ----------------------------------------------------------


def test_mobil_paketleri_beyanda():
    """`mobile/pubspec.yaml` bağımlılıkları da Madde 10.4 kapsamındadır."""
    tablo = _tablo_satirlari()
    metin = (DEPO_KOKU / "mobile/pubspec.yaml").read_text(encoding="utf-8")
    govde = metin.split("dependencies:", 1)[1].split("dev_dependencies:", 1)[0]
    for satir in govde.splitlines():
        m = re.match(r"^  ([a-z_][a-z0-9_]*):\s*\^?([0-9][^\s#]*)", satir)
        if not m:
            continue
        ad = m.group(1)
        assert ad in tablo, (
            f"'{ad}' mobile/pubspec.yaml'da var ama beyanda YOK"
        )


# --- Temel imajlar --------------------------------------------------------


def test_docker_temel_imajlari_beyanda():
    """Teslim paketindeki imajların temeli de üçüncü taraf yazılımdır.

    Jüri `docker compose up` çalıştırdığında python, node, nginx ve
    postgis imajları da makinesine iner. Madde 10.4 "kullanılan tüm
    kütüphane, çerçeve..." diyor; bunlar beyan dışı bırakılamaz.
    """
    metin = _beyan_metni()
    imajlar = set()
    for df in (DEPO_KOKU / "docker").glob("*.Dockerfile"):
        imajlar |= set(re.findall(r"^FROM\s+([^\s]+)", df.read_text(encoding="utf-8"),
                                  re.M))
    for c in (DEPO_KOKU / "docker/compose.yaml").read_text(encoding="utf-8").splitlines():
        m = re.search(r"^\s*image:\s*([^\s]+)", c)
        if m:
            imajlar.add(m.group(1))

    for imaj in imajlar:
        ad = imaj.split(":", 1)[0]
        assert ad in metin, (
            f"'{imaj}' temel imajı Dockerfile/compose'da kullanılıyor ama "
            f"docs/lisans-analizi.md'de anılmıyor"
        )
