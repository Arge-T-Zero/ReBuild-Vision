"""İmajın kendini derleme zamanında sınaması.

## Neden

Eksik bir sistem kütüphanesi ancak çalışma zamanında ortaya çıkar:
servis ayağa kalkar, `/health` "Ağırlık yüklenemedi: ImportError…" der ve
arayüz sahte model bandını geri getirir. Bunu Render'da ilk istekte değil,
`docker build` sırasında görmek gerekir.

`opencv-python-headless` tekerleği bağımlılıklarının çoğunu taşır ama
hepsini değil; `libxcb1`, `libxau6`, `libxdmcp6`, `libbsd0`, `libmd0`
sistemden gelir ("headless" adına rağmen X kütüphaneleri bağlanır).

Ağırlık YOKSA bu bir hata değildir — yokluk `/health` ile bildiriliyor ve
uydurma üretilmiyor. O durumda betik uyarır ve 0 döner.
"""
from __future__ import annotations

import sys
from pathlib import Path

DIZIN = Path(__file__).resolve().parent


def main() -> int:
    import cv2
    import fastapi
    import numpy
    import onnxruntime

    print(
        f"içe aktarmalar tamam — opencv {cv2.__version__}, "
        f"onnxruntime {onnxruntime.__version__}, numpy {numpy.__version__}, "
        f"fastapi {fastapi.__version__}"
    )

    agirlik = DIZIN / "agirliklar/best.onnx"
    if not agirlik.is_file():
        print(f"⚠️ ağırlık yok ({agirlik}) — servis bunu /health ile bildirecek")
        return 0

    sys.path.insert(0, str(DIZIN))
    from onnx_cikarim import OnnxModel

    model = OnnxModel(str(agirlik))
    print(f"ağırlık yüklendi — sınıflar: {model.names}")

    # Sınıf listesi depodakiyle uyuşmuyorsa servis zaten çalışmayı
    # reddedecek; bunu derleme zamanında görmek daha ucuz.
    import json

    siniflar = json.loads((DIZIN.parent / "siniflar.json").read_text(encoding="utf-8"))
    beklenen = {s["id"]: s["ad"] for s in siniflar["siniflar"]}
    if model.names != beklenen:
        print(
            f"❌ SINIF SIRASI UYUŞMUYOR\n   siniflar.json: {beklenen}\n"
            f"   ağırlık      : {model.names}",
            file=sys.stderr,
        )
        return 1

    print("sınıf sırası siniflar.json ile uyuşuyor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
