"""YOLO11 çıkarımı — ONNX Runtime ile, ultralytics OLMADAN.

## Bu dosya neden var

Gerçek model `torch` + `ultralytics` ile çalıştığında **810 MB** yerleşik
bellek (RSS) tüketiyor; yalnızca `import torch` 532 MB. Render'ın
ücretsiz katmanı 512 MB verir. Bu yüzden canlı demo bugüne kadar SAHTE
model servisiyle çalıştı ve arayüzde kalıcı "SAHTE MODEL SERVİSİ" bandı
göründü.

Aynı ağırlık ONNX'e aktarılıp ONNX Runtime ile koşturulunca tepe bellek
**281 MB**'a düşer (ölçüm: `results/onnx-dogrulama.md`). Sınır 512 MB
olduğuna göre gerçek model canlıda çalışabilir.

## Bu bir "yaklaşık" model DEĞİLDİR

Aynı ağırlık, aynı sayılar. Doğrulama `tests/test_onnx_esdegerlik.py`
içinde ve `results/onnx-dogrulama.md`'de yazılıdır:

- ham ağ çıktısı torch ile **bağıl 3e-6** farkla aynı (float32 gürültüsü)
- ön işleme torch yolununkiyle **birebir aynı** (maks fark 0.0)
- tespitler (sınıf, güven, kutu) **birebir aynı**

Birebirliğin bedeli iki ayrıntıya dikkat etmekti; ikisi de kolayca
gözden kaçar ve sessizce FARKLI bir model verirdi:

1. **Ölçekleme OpenCV ile yapılır, Pillow ile değil.** Pillow'un
   `BILINEAR`'ı küçültürken kenar yumuşatma uygular, OpenCV'nin
   `INTER_LINEAR`'ı uygulamaz. Pillow ile ön işleme farkı 0.38'e kadar
   çıkıyordu ve güven skorları 0,50 ↔ 0,92 gibi ayrışıyordu.
2. **Dolgu kareye değil, `stride` katına yapılır.** Ultralytics
   `LetterBox(auto=True)` görüntüyü 640×640'a tamamlamaz; uzun kenarı
   640 yapıp her kenarı 32'nin katına yuvarlar (1200×630 → 640×352).
   Kare dolgu farklı tespitler üretir.

## Lisans

ONNX Runtime (MIT), NumPy (BSD-3), OpenCV (Apache-2.0) — hepsi izin
verici. Bu servis `ultralytics` İÇE AKTARMAZ.

⚠️ Bu, AGPL yükümlülüğünü ortadan KALDIRMAZ. Ağırlık ultralytics ile
eğitildi ve dışa aktarılan `.onnx` dosyası kendi meta verisinde
`license = AGPL-3.0 License` taşır. Değişen tek şey çalışma zamanında
AGPL bir paketin kurulu olmaması; modelin kendisiyle ilgili beyan
`docs/lisans-analizi.md` Bölüm 3'te durmaya devam eder.
"""

from __future__ import annotations

import ast

import cv2
import numpy as np

DOLGU = 114  # ultralytics LetterBox varsayılanı


def mektup_kutusu(
    goruntu: np.ndarray, hedef: int = 640, adim: int = 32
) -> tuple[np.ndarray, float, int, int]:
    """`ultralytics.data.augment.LetterBox(auto=True)` ile aynı kareyi üretir.

    Dönen: (kare, ölçek, sol_dolgu, üst_dolgu)
    """
    y, g = goruntu.shape[:2]
    olcek = min(hedef / g, hedef / y)
    yeni_g, yeni_y = round(g * olcek), round(y * olcek)

    # ⚠️ INTER_LINEAR şart — dosya başındaki 1. maddeye bakın.
    kucuk = cv2.resize(goruntu, (yeni_g, yeni_y), interpolation=cv2.INTER_LINEAR)

    # Kareye değil, `adim` katına tamamla — 2. madde.
    fark_g, fark_y = (-yeni_g) % adim, (-yeni_y) % adim
    ust = round(fark_y / 2 - 0.1)
    sol = round(fark_g / 2 - 0.1)
    kare = cv2.copyMakeBorder(
        kucuk, ust, fark_y - ust, sol, fark_g - sol,
        cv2.BORDER_CONSTANT, value=(DOLGU, DOLGU, DOLGU),
    )
    return kare, olcek, sol, ust


def _nms(kutular: np.ndarray, skorlar: np.ndarray, esik: float) -> list[int]:
    x1, y1, x2, y2 = kutular.T
    alan = (x2 - x1) * (y2 - y1)
    sira = skorlar.argsort()[::-1]
    tut: list[int] = []
    while sira.size:
        i = sira[0]
        tut.append(int(i))
        if sira.size == 1:
            break
        kalan = sira[1:]
        kx1 = np.maximum(x1[i], x1[kalan])
        ky1 = np.maximum(y1[i], y1[kalan])
        kx2 = np.minimum(x2[i], x2[kalan])
        ky2 = np.minimum(y2[i], y2[kalan])
        kesisim = np.clip(kx2 - kx1, 0, None) * np.clip(ky2 - ky1, 0, None)
        iou = kesisim / (alan[i] + alan[kalan] - kesisim + 1e-9)
        sira = kalan[iou <= esik]
    return tut


class OnnxModel:
    """Tek bir `.onnx` ağırlığını yükler ve çıkarım yapar.

    `names` ağırlığın KENDİ meta verisinden okunur; app.py'deki sınıf
    sırası denetimi torch yolundakiyle aynı şekilde çalışır.
    """

    def __init__(self, yol: str) -> None:
        import onnxruntime as ort  # noqa: PLC0415 — kurulu değilse servis yine kalksın

        self._oturum = ort.InferenceSession(
            yol,
            providers=["CPUExecutionProvider"],
        )
        self._girdi = self._oturum.get_inputs()[0].name
        ust = self._oturum.get_modelmeta().custom_metadata_map
        self.names: dict[int, str] = {
            int(k): str(v) for k, v in ast.literal_eval(ust.get("names", "{}")).items()
        }
        self._adim = int(float(ust.get("stride", 32)))
        boy = ast.literal_eval(ust.get("imgsz", "[640, 640]"))
        self._hedef = int(boy[0])

    def tahmin(
        self, goruntu: np.ndarray, conf: float = 0.25, iou: float = 0.7
    ) -> list[dict]:
        """RGB `np.ndarray` alır, `{sinif_id, guven, kutu}` listesi döner.

        Varsayılan `conf`/`iou` değerleri ultralytics `predict()` ile
        aynıdır; torch yolu da bu varsayılanlarla çağrılıyor.
        """
        y0, g0 = goruntu.shape[:2]
        kare, olcek, sol, ust = mektup_kutusu(goruntu, self._hedef, self._adim)
        x = kare.astype(np.float32).transpose(2, 0, 1)[None] / 255.0

        ham = self._oturum.run(None, {self._girdi: x})[0]  # (1, 4+nc, N)
        p = ham[0].T                                       # (N, 4+nc)

        skor = p[:, 4:].max(1)
        sinif = p[:, 4:].argmax(1)
        secili = skor > conf
        if not secili.any():
            return []
        p, skor, sinif = p[secili], skor[secili], sinif[secili]

        cx, cy, w, h = p[:, 0], p[:, 1], p[:, 2], p[:, 3]
        kutu = np.stack([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 1)

        # Ultralytics NMS SINIF BAZLIDIR: farklı sınıflar birbirini
        # bastırmaz. Sınıf başına büyük bir kaydırma eklemek bunu tek
        # çağrıda verir (ultralytics'in kendi yöntemi de budur).
        kayma = sinif[:, None].astype(np.float32) * 7680.0

        sonuc = []
        for i in _nms(kutu + kayma, skor, iou):
            b = kutu[i].copy()
            b[[0, 2]] = np.clip((b[[0, 2]] - sol) / olcek, 0, g0)
            b[[1, 3]] = np.clip((b[[1, 3]] - ust) / olcek, 0, y0)
            sonuc.append({
                "sinif_id": int(sinif[i]),
                "guven": float(skor[i]),
                "kutu": [float(v) for v in b],
            })
        return sorted(sonuc, key=lambda d: -d["guven"])
