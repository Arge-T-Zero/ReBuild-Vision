"""Belgelerdeki sınıf listelerini `siniflar.json` ile kilitler.

## Neden bu dosya var

07.09.2026 denetiminde `docs/kullanici-kilavuzu.md` şunu yazıyordu:

    ### Modelin tanıdığı beş sınıf
    Ahşap · Beton / tuğla · Cam · METAL · Seramik

Bu v1'in ara listesiydi. Metal v2'de **tanınan bir sınıf değil** —
`kapsanmayan_gruplar` içinde. Kılavuzu okuyan bir hakem, modelin metali
tanıdığını sanacaktı. Aynı gün `model-service/README.md` de aynı eski
tabloyu taşıyordu; üstelik o tablonun hemen üstünde
"`siniflar.json` ile **birebir aynı sırada** olmalıdır" yazıyordu.

## Neden mevcut kilitler yakalamadı

Sınıf listesinin üç kilidi vardı ve üçü de sağlamdı:

1. `data.yaml` ↔ `siniflar.json`            (tests/test_sinif_tanimlari.py)
2. ağırlığın `names` sözlüğü ↔ `siniflar.json`  (model-service/app.py, açılışta)
3. `katsayilar.json` + renkler ↔ `siniflar.json` (tests/)

Üçü de **makine tarafından okunan** dosyaları koruyordu. İNSAN TARAFINDAN
OKUNAN belgeler korumasızdı ve tam da orada aylarca yanlış liste durdu.
Bu dosya dördüncü kilittir.

## Nasıl çalışır

Belgelerde makine tarafından okunabilir işaretler var:

    <!-- siniflar:taninan -->      ... <!-- /siniflar:taninan -->
    <!-- siniflar:kapsanmayan -->  ... <!-- /siniflar:kapsanmayan -->
    <!-- siniflar:tablo -->        ... <!-- /siniflar:tablo -->

İşaretlerin arasındaki metin `siniflar.json` ile karşılaştırılır. Yeni
bir belgeye sınıf listesi yazan biri bu işaretleri koyarsa liste
kendiliğinden korunur.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

DEPO = Path(__file__).resolve().parent.parent
SINIFLAR = json.loads((DEPO / "siniflar.json").read_text(encoding="utf-8"))

TANINAN = [s["gorunen_ad"] for s in SINIFLAR["siniflar"]]
TANINAN_AD = [s["ad"] for s in SINIFLAR["siniflar"]]
KAPSANMAYAN = [g["gorunen_ad"] for g in SINIFLAR["kapsanmayan_gruplar"]]


def _blok(yol: Path, isaret: str) -> str:
    """İşaretler arasındaki metni döner; işaret yoksa testi düşürür."""
    metin = yol.read_text(encoding="utf-8")
    kalip = rf"<!-- siniflar:{isaret} -->(.*?)<!-- /siniflar:{isaret} -->"
    eslesme = re.search(kalip, metin, re.S)
    assert eslesme, (
        f"{yol.relative_to(DEPO)} içinde `siniflar:{isaret}` işareti yok. "
        "Sınıf listesi taşıyan bir belge bu işaretlerle sarılmalıdır; "
        "yoksa liste sessizce eskir (bu dosyanın başındaki gerekçe)."
    )
    return eslesme.group(1)


def test_kilavuzdaki_taninan_liste_siniflar_json_ile_ayni() -> None:
    blok = _blok(DEPO / "docs/kullanici-kilavuzu.md", "taninan")
    for ad in TANINAN:
        assert ad in blok, f"kılavuzun tanınan listesinde `{ad}` yok"
    # ⚠️ ASIL TEST BU: kapsanmayan bir grup tanınan gibi yazılamaz.
    # Kılavuz tam olarak bunu yapıyordu (Metal).
    for ad in KAPSANMAYAN:
        assert ad not in blok, (
            f"kılavuz `{ad}` grubunu MODELİN TANIDIĞI sınıf gibi gösteriyor. "
            f"{ad}, siniflar.json'da kapsanmayan_gruplar içinde — model onu "
            "tanımaz. Bu, hakeme yanlış beyandır."
        )


def test_kilavuzdaki_kapsanmayan_liste_eksiksiz() -> None:
    blok = _blok(DEPO / "docs/kullanici-kilavuzu.md", "kapsanmayan")
    for ad in KAPSANMAYAN:
        assert ad in blok, (
            f"kılavuzun kapsanmayan listesinde `{ad}` yok. Eksik yazılırsa "
            "kullanıcı o malzemenin tanındığını sanır."
        )


def test_model_servisi_readme_tablosu_siniflar_json_ile_ayni() -> None:
    blok = _blok(DEPO / "model-service/README.md", "tablo")
    satirlar = [
        s for s in re.findall(r"^\|\s*(\d+)\s*\|\s*(\S+)\s*\|\s*([^|]+?)\s*\|$",
                              blok, re.M)
    ]
    assert satirlar, "README tablosu okunamadı"
    gelen = [(int(i), ad) for i, ad, _ in satirlar]
    beklenen = [(s["id"], s["ad"]) for s in SINIFLAR["siniflar"]]
    assert gelen == beklenen, (
        f"model-service/README.md sınıf tablosu ayrışmış.\n"
        f"  siniflar.json: {beklenen}\n  README        : {gelen}"
    )


def test_sahte_servis_ornek_ciktisi_gecerli_sinif_kullaniyor() -> None:
    """Örnek çıktı dosyası da güncel kalmalı.

    Servisin kendisi `siniflar.json`'u çalışma anında okur, yani üretimde
    risk yok. Ama bu dosya belgedir: hakem açıp bakabilir ve orada
    olmayan bir sınıf adı görmemelidir.
    """
    yol = DEPO / "model-mock/ornek_cikti_SAHTE.json"
    ornek = json.loads(yol.read_text(encoding="utf-8"))
    for tespit in ornek.get("detections", []):
        assert tespit["class_name"] in TANINAN_AD, (
            f"örnek çıktıda geçersiz sınıf: {tespit['class_name']!r} "
            f"(geçerli: {TANINAN_AD})"
        )
