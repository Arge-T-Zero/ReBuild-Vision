#!/usr/bin/env python3
"""Sınıf renklerini renk körlüğü benzetimi + LAB ΔE ile ölçer.

⚠️ NEDEN BU BETİK VAR

Renk paleti iki kez elle ölçülüp seçildi (K-012, K-022) ama ÖLÇÜM KODU
depoda yoktu — yalnızca sonuç sayıları yazılıydı. Sınıf listesi üçüncü
kez değişirken (v2: metal çıkıyor, beton/tuğla ayrılıyor) ölçümü
yeniden kurmak gerekti. Kayıtlı bir sayı, yeniden üretilemiyorsa
denetlenemez.

ÖLÇÜT (K-022 ile aynı): *bütün ikililerin* en kötüsü — normal görüş ve
üç renk körlüğü benzetimi birlikte. Sıralamadaki komşu ikililer değil;
kullanıcı renkleri lejanttaki sırayla değil haritada yan yana görür.

Renk hiçbir zaman TEK BAŞINA anlam taşımaz — her etikette sınıf adı
yazılıdır (WCAG 1.4.1). Ölçüm, rengin yardımcı olduğu durumu
iyileştirmek içindir, ona bağımlılık yaratmak için değil.

KULLANIM
    python scripts/renk_olc.py                  # siniflar.json'daki paleti ölç
    python scripts/renk_olc.py '#d95926' '#6b7280' ...   # verilen kümeyi ölç
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

DEPO_KOKU = Path(__file__).resolve().parents[1]

# Viénot, Brettel & Mollon (1999) — doğrusal RGB üzerinde çalışan
# dikroma benzetim matrisleri. Yayımlanmış yaklaşıklıklardır; mutlak
# doğruluk değil, KARŞILAŞTIRILABİLİRLİK hedeflenir: aynı kod hem eski
# hem yeni paleti ölçer.
BENZETIM = {
    "normal": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    "protanopi": ((0.11238, 0.88762, 0.0),
                  (0.11238, 0.88762, 0.0),
                  (0.00401, -0.00401, 1.0)),
    "dotanopi": ((0.29275, 0.70725, 0.0),
                 (0.29275, 0.70725, 0.0),
                 (-0.02234, 0.02234, 1.0)),
    "tritanopi": ((1.0, 0.14461, -0.14461),
                  (0.0, 0.85659, 0.14341),
                  (0.0, 0.85659, 0.14341)),
}


def _cozumle(hx: str) -> tuple[float, float, float]:
    hx = hx.strip().lstrip("#")
    return tuple(int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore


def _dogrusal(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _srgb(c: float) -> float:
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _uygula(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def _lab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (_dogrusal(c) for c in rgb)
    # sRGB → XYZ (D65)
    x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
    xn, yn, zn = 0.95047, 1.0, 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def _benzet(hx: str, tur: str) -> tuple[float, float, float]:
    dogrusal = tuple(_dogrusal(c) for c in _cozumle(hx))
    return tuple(_srgb(c) for c in _uygula(BENZETIM[tur], dogrusal))  # type: ignore


def _de76(a, b) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def olc(renkler: dict[str, str]) -> dict:
    """Bütün ikilileri, bütün görme türlerinde ölçer; en kötüsünü döner."""
    ikililer = []
    for (a1, h1), (a2, h2) in itertools.combinations(renkler.items(), 2):
        for tur in BENZETIM:
            d = _de76(_lab(_benzet(h1, tur)), _lab(_benzet(h2, tur)))
            ikililer.append((round(d, 2), a1, a2, tur))
    ikililer.sort()
    return {"en_kotu": ikililer[0][0], "en_kotu_ikili": ikililer[0],
            "en_kotu_bes": ikililer[:5]}


def _goreli_parlaklik(hx: str) -> float:
    r, g, b = (_dogrusal(c) for c in _cozumle(hx))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontrast(hx: str, uzerine: str) -> float:
    a, b = _goreli_parlaklik(hx), _goreli_parlaklik(uzerine)
    a, b = max(a, b), min(a, b)
    return (a + 0.05) / (b + 0.05)


def _yazdir(baslik: str, renkler: dict[str, str]) -> float:
    s = olc(renkler)
    print(f"\n=== {baslik} ===")
    print("  " + "  ".join(f"{a}={h}" for a, h in renkler.items()))
    print(f"  BÜTÜN-İKİLİ EN KÖTÜ ΔE : {s['en_kotu']}")
    for d, a1, a2, tur in s["en_kotu_bes"]:
        print(f"    {d:6.2f}  {a1} ↔ {a2}  ({tur})")
    print("  etiket kontrastı (WCAG AA eşiği 4,5):")
    for a, h in renkler.items():
        beyaz, siyah = kontrast(h, "#ffffff"), kontrast(h, "#000000")
        en_iyi = "beyaz" if beyaz >= siyah else "siyah"
        print(f"    {a:12s} {h}  {max(beyaz, siyah):.2f} ({en_iyi} yazı)"
              + ("" if max(beyaz, siyah) >= 4.5 else "   ⚠️ AA ALTINDA"))
    return s["en_kotu"]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        _yazdir("verilen küme", {f"r{i}": h for i, h in enumerate(sys.argv[1:], 1)})
    else:
        d = json.loads((DEPO_KOKU / "siniflar.json").read_text(encoding="utf-8"))
        _yazdir("siniflar.json (mevcut)",
                {s["ad"]: s["renk"] for s in d["siniflar"]})
