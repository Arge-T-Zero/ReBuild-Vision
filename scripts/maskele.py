#!/usr/bin/env python3
"""Yüz ve plaka maskeleme.

Rapor Bölüm 6: "gereksiz yüz ve plaka görüntülerinin maskelenmesi"
Şartname Madde 10.7: demo ortamında maskelenmiş veri kullanılması esastır.

Maskeleme ELLE YAPILMAZ; bu betikle yapılır — tekrarlanabilir ve
denetlenebilir olsun diye.

┌─────────────────────────────────────────────────────────────────────┐
│ DÜRÜST UYARI — BU BETİK TEK BAŞINA YETERLİ DEĞİLDİR                  │
│                                                                     │
│ Haar cascade yüz sezimi HER YÜZÜ YAKALAMAZ: profilden bakan,        │
│ kısmen kapalı, çok küçük veya düşük ışıktaki yüzler kaçar. Plaka     │
│ sezimi biçim temellidir ve daha da kırılgandır.                     │
│                                                                     │
│ Bu nedenle çıktı otomatik olarak "temiz" SAYILMAZ. Her maskelenmiş  │
│ görsel, depoya veya sunuma girmeden önce GÖZLE KONTROL EDİLİR.      │
│ Betik insan kontrolünü ortadan kaldırmaz, kolaylaştırır.            │
└─────────────────────────────────────────────────────────────────────┘

Kullanım:
    python3 scripts/maskele.py data/saha-foto/ data/ornek/
    python3 scripts/maskele.py girdi.jpg cikti_klasoru/

Maskeleme geri döndürülemez: orijinal dosyanın ÜZERİNE YAZILMAZ, çıktı
ayrı bir dosyadır.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import cv2
except ImportError:
    sys.exit(
        "OpenCV kurulu değil.\n"
        "  pip install opencv-python-headless\n"
        "(Apache-2.0 — docs/lisans-analizi.md Bölüm 2.5)"
    )

import numpy as np

UZANTILAR = {".jpg", ".jpeg", ".png", ".webp"}
BULANIKLIK = 61  # tek sayı olmalı


def _seziciler() -> tuple:
    yol = Path(cv2.data.haarcascades)
    yuz_on = cv2.CascadeClassifier(str(yol / "haarcascade_frontalface_default.xml"))
    yuz_yan = cv2.CascadeClassifier(str(yol / "haarcascade_profileface.xml"))
    plaka_dosya = yol / "haarcascade_russian_plate_number.xml"
    plaka = cv2.CascadeClassifier(str(plaka_dosya)) if plaka_dosya.exists() else None
    return yuz_on, yuz_yan, plaka


def _bolgeleri_bul(gri, seziciler) -> list[tuple[int, int, int, int]]:
    yuz_on, yuz_yan, plaka = seziciler
    bolgeler: list[tuple[int, int, int, int]] = []

    for sezici in (yuz_on, yuz_yan):
        if sezici is None or sezici.empty():
            continue
        for (x, y, w, h) in sezici.detectMultiScale(gri, 1.1, 5, minSize=(24, 24)):
            bolgeler.append((x, y, w, h))

    # Yan profil sezici yalnızca bir yöne bakar; ayna görüntüsünde de arar.
    if yuz_yan is not None and not yuz_yan.empty():
        aynali = cv2.flip(gri, 1)
        genislik = gri.shape[1]
        for (x, y, w, h) in yuz_yan.detectMultiScale(aynali, 1.1, 5, minSize=(24, 24)):
            bolgeler.append((genislik - x - w, y, w, h))

    if plaka is not None and not plaka.empty():
        for (x, y, w, h) in plaka.detectMultiScale(gri, 1.1, 4, minSize=(40, 12)):
            bolgeler.append((x, y, w, h))

    return bolgeler


def maskele(girdi: Path, cikti: Path) -> int:
    """Görüntüyü maskeler ve maskelenen bölge sayısını döner."""
    im = cv2.imread(str(girdi))
    if im is None:
        raise ValueError(f"Görüntü okunamadı: {girdi}")

    gri = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    bolgeler = _bolgeleri_bul(gri, _seziciler())

    for (x, y, w, h) in bolgeler:
        # Kenar payı: sezici kutusu genelde yüzü tam örtmez.
        pay = int(max(w, h) * 0.15)
        x0, y0 = max(0, x - pay), max(0, y - pay)
        x1, y1 = min(im.shape[1], x + w + pay), min(im.shape[0], y + h + pay)
        alan = im[y0:y1, x0:x1]
        if alan.size == 0:
            continue
        # Güçlü bulanıklık + pikselleştirme: geri döndürülemez olması için.
        kucuk = cv2.resize(alan, (8, 8), interpolation=cv2.INTER_LINEAR)
        im[y0:y1, x0:x1] = cv2.resize(
            kucuk, (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST
        )

    cikti.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(cikti), im):
        raise OSError(f"Yazılamadı: {cikti}")
    return len(bolgeler)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Saha görüntülerinde yüz ve plaka maskeler.",
        epilog="Çıktı gözle kontrol edilmeden depoya veya sunuma girmez.",
    )
    ap.add_argument("girdi", type=Path, help="Görüntü dosyası veya klasör")
    ap.add_argument("cikti", type=Path, help="Çıktı klasörü")
    ap.add_argument("--sonek", default="_maskeli",
                    help="Çıktı dosya adı soneki (varsayılan: _maskeli)")
    a = ap.parse_args()

    if not a.girdi.exists():
        print(f"Girdi bulunamadı: {a.girdi}", file=sys.stderr)
        return 1

    dosyalar = (
        [a.girdi] if a.girdi.is_file()
        else sorted(d for d in a.girdi.iterdir() if d.suffix.lower() in UZANTILAR)
    )
    if not dosyalar:
        print(f"İşlenecek görüntü yok: {a.girdi}", file=sys.stderr)
        return 1

    toplam = 0
    bolgesiz: list[str] = []
    for d in dosyalar:
        hedef = a.cikti / f"{d.stem}{a.sonek}{d.suffix}"
        try:
            n = maskele(d, hedef)
        except (ValueError, OSError) as e:
            print(f"  ! {d.name}: {e}", file=sys.stderr)
            continue
        toplam += n
        if n == 0:
            bolgesiz.append(d.name)
        print(f"  {d.name} -> {hedef.name}  ({n} bölge maskelendi)")

    print(f"\n{len(dosyalar)} görüntü işlendi, toplam {toplam} bölge maskelendi.")

    if bolgesiz:
        print(
            f"\nUYARI: {len(bolgesiz)} görüntüde hiçbir bölge bulunamadı:\n"
            + "\n".join(f"  - {a}" for a in bolgesiz)
            + "\nBu, görüntüde yüz/plaka OLMADIĞI anlamına GELMEZ; sezici"
              " kaçırmış olabilir."
        )

    print(
        "\n>> ÇIKTILARI GÖZLE KONTROL EDİN.\n"
        "   Bu betik her yüzü ve plakayı yakalamaz. Kontrol edilmemiş bir\n"
        "   görsel depoya, demoya veya sunuma girmez.\n"
        "   Ayrıntı: docs/veri-politikasi.md Bölüm 3."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
