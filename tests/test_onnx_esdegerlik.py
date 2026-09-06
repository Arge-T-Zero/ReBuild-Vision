"""ONNX yolunun torch yoluyla AYNI sayıları ürettiğini doğrular.

## Neden bu dosya var

Canlı demo bugüne kadar SAHTE model servisiyle çalıştı: gerçek servis
`torch` ile 810 MB tepe bellek istiyor, Render'ın ücretsiz katmanı
512 MB veriyor. Aynı ağırlık ONNX Runtime ile 281 MB'a düşüyor ve
canlıda gerçek model çalışabiliyor.

Bu ancak iki yol AYNI SONUCU veriyorsa dürüsttür. Aksi hâlde ortada
"ölçülmemiş ikinci bir model" olur: `results/model-metrikleri.md`
içindeki mAP torch yolunda ölçüldü, canlıda başka bir şey koşuyor
olurdu ve kimse fark etmezdi.

## Ölçüm neden burada tekrarlanıyor

`results/onnx-dogrulama.md` sayıları yazar; bu dosya onları YENİDEN
ÜRETİR. Yazılı bir sayı, ağırlık değiştiğinde kendini güncellemez.

## Neden çoğu zaman atlanır

Ağırlık dosyaları depoda değildir (`.gitignore`) ve CI'da ne
`ultralytics` ne `onnxruntime` kurulur. Testler sessizce GEÇMEZ,
açıkça ATLANIR; neden atlandığı mesajda yazar.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

DEPO = Path(__file__).resolve().parent.parent
AGIRLIK = DEPO / "model-service/agirliklar"
ONNX = AGIRLIK / "best.onnx"
PT = AGIRLIK / "best.pt"
GORUNTULER = sorted((DEPO / "web/public/gorseller").glob("*.jpg"))

onnx_yok = pytest.mark.skipif(
    not ONNX.is_file(), reason=f"ONNX ağırlığı yok: {ONNX}"
)


def _onnx_model():
    sys.path.insert(0, str(DEPO / "model-service"))
    from onnx_cikarim import OnnxModel

    return OnnxModel(str(ONNX))


@onnx_yok
def test_onnx_sinif_listesi_siniflar_json_ile_ayni() -> None:
    """Ağırlığın kendi `names` sözlüğü depodakiyle aynı olmalı.

    Bu, servisin açılıştaki sınıf sırası denetiminin ONNX yolunda da
    çalıştığını doğrular: `.onnx` dosyası `names` meta verisini taşır.
    """
    pytest.importorskip("onnxruntime", reason="onnxruntime kurulu değil")
    siniflar = json.loads((DEPO / "siniflar.json").read_text(encoding="utf-8"))
    beklenen = {s["id"]: s["ad"] for s in siniflar["siniflar"]}
    assert _onnx_model().names == beklenen


@onnx_yok
def test_on_isleme_ultralytics_ile_birebir_ayni() -> None:
    """Ölçekleme ve dolgu ultralytics `LetterBox` ile bit bit aynı olmalı.

    ⚠️ Bu test bir kez GERÇEKTEN kırmızıydı. İlk sürüm Pillow'un
    `BILINEAR`'ıyla ölçekliyordu; Pillow küçültürken kenar yumuşatma
    uygular, OpenCV'nin `INTER_LINEAR`'ı uygulamaz. Piksel farkı 0,38'e
    çıkıyor ve güven skorları 0,50 ↔ 0,92 gibi ayrışıyordu — yani sessizce
    BAŞKA bir model. Ayrıca dolgu kareye değil, `stride` katına yapılır.
    """
    pytest.importorskip("onnxruntime", reason="onnxruntime kurulu değil")
    pytest.importorskip("ultralytics", reason="ultralytics kurulu değil")
    import numpy as np
    from PIL import Image
    from ultralytics.data.augment import LetterBox

    sys.path.insert(0, str(DEPO / "model-service"))
    from onnx_cikarim import mektup_kutusu

    for yol in GORUNTULER:
        with Image.open(yol) as im:
            dizi = np.asarray(im.convert("RGB"))
        bizim, *_ = mektup_kutusu(dizi)
        onlarin = LetterBox((640, 640), auto=True, stride=32)(image=dizi)
        assert bizim.shape == onlarin.shape, f"{yol.name}: şekil ayrıştı"
        assert np.array_equal(bizim, onlarin), f"{yol.name}: piksel ayrıştı"


@onnx_yok
@pytest.mark.skipif(not PT.is_file(), reason="torch ağırlığı yok, karşılaştırılamaz")
def test_tespitler_torch_yoluyla_ayni() -> None:
    """Sınıf, güven ve kutu — iki yol arasında ayrışmamalı.

    Eşikler ölçülmüş değerlerden gelir (`results/onnx-dogrulama.md`):
    güven farkı gözlenen en büyük değerin ~50 katı, kutu farkı yarım
    pikselin altı. Gevşek değil; float32 gürültüsünün üstünde herhangi
    bir sapmayı yakalar.
    """
    pytest.importorskip("onnxruntime", reason="onnxruntime kurulu değil")
    pytest.importorskip("ultralytics", reason="ultralytics kurulu değil")
    import numpy as np
    from PIL import Image
    from ultralytics import YOLO

    torch_model = YOLO(str(PT))
    onnx_model = _onnx_model()

    for yol in GORUNTULER:
        with Image.open(yol) as im:
            goruntu = im.convert("RGB")
            sonuc = torch_model.predict(goruntu, verbose=False)[0]
            beklenen = sorted(
                (
                    int(k.cls.item()),
                    float(k.conf.item()),
                    [float(v) for v in k.xyxy[0].tolist()],
                )
                for k in sonuc.boxes
            )
            gelen = sorted(
                (d["sinif_id"], d["guven"], d["kutu"])
                for d in onnx_model.tahmin(np.asarray(goruntu))
            )

        assert len(beklenen) == len(gelen), (
            f"{yol.name}: torch {len(beklenen)} tespit, onnx {len(gelen)}"
        )
        for (sb, gb, kb), (sg, gg, kg) in zip(beklenen, gelen):
            assert sb == sg, f"{yol.name}: sınıf ayrıştı ({sb} vs {sg})"
            assert abs(gb - gg) < 1e-4, f"{yol.name}: güven ayrıştı ({gb} vs {gg})"
            assert max(abs(u - v) for u, v in zip(kb, kg)) < 0.5, (
                f"{yol.name}: kutu ayrıştı ({kb} vs {kg})"
            )
