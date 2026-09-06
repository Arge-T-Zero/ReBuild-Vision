#!/usr/bin/env python
"""`best.pt` → `best.onnx` dışa aktarımı.

Canlı ortam modeli ONNX biçiminde çalıştırır: torch yolu 810 MB tepe
bellek ister, ücretsiz katman 512 MB verir, ONNX yolu 281 MB'da kalır
(results/onnx-dogrulama.md).

⚠️ ÜRETİLEN DOSYA DEPOYA GİRMEZ (model-service/agirliklar/.gitignore).
Yayın (release) varlığı olarak yüklenir; docker imajı oradan indirir.

Kullanım (ultralytics kurulu bir ortamda):

    python scripts/onnx_disa_aktar.py

Dışa aktarımdan sonra eşdeğerlik MUTLAKA doğrulanmalıdır:

    pytest tests/test_onnx_esdegerlik.py

`dynamic=True` bilinçlidir: ultralytics `predict()` görüntüyü kareye
değil, `stride` katına tamamlar (1200x630 → 640x352). Sabit 640x640
girdi zorunlu kılınsaydı ön işleme torch yolundan ayrışır ve tespitler
değişirdi.
"""
from __future__ import annotations

import sys
from pathlib import Path

DEPO = Path(__file__).resolve().parent.parent
KAYNAK = DEPO / "model-service/agirliklar/best.pt"


def main() -> int:
    if not KAYNAK.is_file():
        print(f"Ağırlık yok: {KAYNAK}", file=sys.stderr)
        return 1
    try:
        from ultralytics import YOLO
    except ImportError:
        print(
            "ultralytics kurulu değil. Bu betik AGPL bir paket gerektirir "
            "ve yalnızca dışa aktarım için çalıştırılır; üretim servisi "
            "onu içe aktarmaz (model-service/onnx_cikarim.py).",
            file=sys.stderr,
        )
        return 1

    cikti = YOLO(str(KAYNAK)).export(
        format="onnx", imgsz=640, opset=17, simplify=True, dynamic=True
    )
    print(f"üretildi: {cikti}")
    print("şimdi doğrulayın:  pytest tests/test_onnx_esdegerlik.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
