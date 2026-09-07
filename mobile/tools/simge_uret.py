#!/usr/bin/env python3
"""Android uygulama simgesini üretir.

⚠️ UYGULAMANIN SİMGESİ YOKTU. Cihazda Flutter'ın varsayılan mavi "F"
simgesi görünüyordu (`mipmap-*/ic_launcher.png` şablondan gelen
dosyalardı). Kullanıcı tablette bunu bildirdi: "dışarıda sadece F harfli
bir simge gözüküyor".

Simge, web arayüzünün `favicon.svg` dosyasından TÜRETİLDİ — yeni bir
tasarım uydurulmadı. Favicon zaten logonun küçük boy sürümüdür: üç
katmanlı işaretin ayrıntısı azaltılmış hâli (bkz. dosyanın kendi
yorumu). Aynı geometri burada Pillow ile çiziliyor.

Tek fark ZEMİN RENGİ: favicon koyu lacivert (#0d1117) üzerine açık yeşil
işaret kullanıyor, uygulama simgesi ise projenin marka rengi #0d6b48
üzerine beyaz işaret kullanıyor. Gerekçe:

  - #0d6b48 projenin marka rengidir (`mobile/lib/tema.dart` → `Acik.marka`,
    `siniflar.json` ile aynı palet). Uygulama listesinde ürünü rengiyle
    tanımak, koyu lacivert bir kareyle tanımaktan kolaydır.
  - Beyaz/marka eşleşmesi uygulamada zaten tanımlı: `Renk.markaUstu`
    açık temada marka rengi ZEMİN olduğunda üzerine beyaz koyar.

Katman opaklıkları favicon'daki 0,5 / 0,75 / 1 değerlerinden ÖLÇÜLEREK
yükseltildi (0,58 / 0,78 / 1): bu betik her katmanın zeminle kontrast
oranını hesaplayıp yazdırır ve en soluk katman 3:1 eşiğinin (WCAG 1.4.11,
metin dışı ögeler) üstünde tutuldu. Ölçüm çıktısı için betiği çalıştırın.

Kullanım:
    python3 mobile/tools/simge_uret.py

Üretilenler (`mobile/android/app/src/main/res/` altına):
    mipmap-*/ic_launcher.png            eski sürüm simgesi (kare, yuvarlak köşe)
    mipmap-*/ic_launcher_round.png      eski sürüm yuvarlak simge (API 25)
    mipmap-*/ic_launcher_foreground.png uyarlanır simge ön katmanı (API 26+)

`flutter_launcher_icons` paketi bilinçli kullanılmadı: ağ erişimi
gerektiriyor ve ürettiği dosyalar zaten bunlar. Betik, çıktının nasıl
üretildiğini de kayda geçirir.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

KOK = Path(__file__).resolve().parent.parent
RES = KOK / "android/app/src/main/res"

# --- Renkler ---------------------------------------------------------
ZEMIN = (0x0D, 0x6B, 0x48)      # tema.dart → Acik.marka
ISARET = (0xFF, 0xFF, 0xFF)     # tema.dart → Renk.markaUstu (açık tema)

# --- Geometri — web/public/favicon.svg (viewBox 0 0 32 32) ------------
# Yollar dosyadan birebir alındı; stroke-width 2.2, yuvarlak uç ve köşe.
KATMANLAR: list[tuple[list[tuple[float, float]], bool, float]] = [
    # (noktalar, kapalı_mı, opaklık)
    ([(6, 22), (16, 26.5), (26, 22)], False, 0.58),
    ([(6, 16.5), (16, 21), (26, 16.5)], False, 0.78),
    ([(6, 10.5), (16, 6), (26, 10.5), (16, 15)], True, 1.0),
]
CIZGI_KALINLIGI = 2.2  # favicon.svg → stroke-width

# Android yoğunlukları. Eski sürüm simgesi dp değil piksel cinsinden
# tanımlıdır: 48/72/96/144/192.
YOGUNLUKLAR = {
    "mdpi": 1,
    "hdpi": 1.5,
    "xhdpi": 2,
    "xxhdpi": 3,
    "xxxhdpi": 4,
}
ESKI_TABAN = 48        # dp
UYARLANIR_TABAN = 108  # dp — uyarlanır simge tuvali her zaman 108dp

# Süper örnekleme: yuvarlak uçlar ve köşegen çizgiler 48 pikselde
# tırtıklı çıkmasın diye 8 kat büyük çizilip küçültülüyor.
KAT = 8


def _luminans(renk: tuple[float, float, float]) -> float:
    """WCAG bağıl parlaklık."""
    kanallar = []
    for k in renk:
        o = k / 255
        kanallar.append(o / 12.92 if o <= 0.03928 else ((o + 0.055) / 1.055) ** 2.4)
    r, g, b = kanallar
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _kontrast(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    la, lb = _luminans(a), _luminans(b)
    ust, alt = max(la, lb), min(la, lb)
    return (ust + 0.05) / (alt + 0.05)


def _karisim(opaklik: float) -> tuple[float, float, float]:
    """İşaret renginin zemin üzerindeki görünen hâli."""
    return tuple(
        ISARET[i] * opaklik + ZEMIN[i] * (1 - opaklik) for i in range(3)
    )


def _yuvarlak_cizgi(
    ciz: ImageDraw.ImageDraw,
    noktalar: list[tuple[float, float]],
    kalinlik: float,
    renk: tuple[int, int, int, int],
    kapali: bool,
) -> None:
    """Yuvarlak uçlu ve köşeli çoklu çizgi.

    Pillow'un `line` çağrısı yuvarlak UÇ üretmez; her düğüme bir daire
    basılarak hem uçlar hem köşeler yuvarlatılıyor. SVG'nin
    `stroke-linecap="round" stroke-linejoin="round"` davranışının
    karşılığı budur.
    """
    dizi = noktalar + [noktalar[0]] if kapali else noktalar
    ciz.line(dizi, fill=renk, width=int(round(kalinlik)), joint="curve")
    yaricap = kalinlik / 2
    for x, y in dizi:
        ciz.ellipse(
            [x - yaricap, y - yaricap, x + yaricap, y + yaricap], fill=renk
        )


def _isaret_ciz(tuval: Image.Image, merkez: float, olcek: float) -> None:
    """32 birimlik işareti verilen ölçekte tuvalin ortasına çizer."""
    for noktalar, kapali, opaklik in KATMANLAR:
        katman = Image.new("RGBA", tuval.size, (0, 0, 0, 0))
        ciz = ImageDraw.Draw(katman)
        olcekli = [
            (merkez + (x - 16) * olcek, merkez + (y - 16) * olcek)
            for x, y in noktalar
        ]
        _yuvarlak_cizgi(
            ciz,
            olcekli,
            CIZGI_KALINLIGI * olcek,
            (*ISARET, round(255 * opaklik)),
            kapali,
        )
        tuval.alpha_composite(katman)


def eski_simge(boyut: int, yuvarlak: bool) -> Image.Image:
    """API 25 ve öncesi için tam simge: zemin + işaret tek dosyada."""
    b = boyut * KAT
    im = Image.new("RGBA", (b, b), (0, 0, 0, 0))
    ciz = ImageDraw.Draw(im)
    if yuvarlak:
        ciz.ellipse([0, 0, b - 1, b - 1], fill=(*ZEMIN, 255))
    else:
        # favicon.svg'deki `rx=7` oranı: 7/32 ≈ %22.
        ciz.rounded_rectangle(
            [0, 0, b - 1, b - 1], radius=b * 7 / 32, fill=(*ZEMIN, 255)
        )
    oran = ESKI_YUVARLAK_ORANI if yuvarlak else ESKI_KARE_ORANI
    _isaret_ciz(im, b / 2, (b * oran) / 32)
    return im.resize((boyut, boyut), Image.LANCZOS)


def isaret_yaricapi() -> float:
    """İşaretin 32 birimlik tuvalin merkezinden ölçülen ÇİZİM yarıçapı.

    32'lik kutunun köşegenini kullanmak yanıltıcı olurdu: işaret o
    kutunun tamamını doldurmuyor (x 6-26, y 6-26,5) ve köşeleri boş.
    Burada gerçekten mürekkep bulunan en uzak nokta ölçülüyor —
    çizgi kalınlığının yarısı da ekleniyor, çünkü çizgi düğümün
    üstünde değil çevresinde duruyor.
    """
    return max(
        math.hypot(x - 16, y - 16)
        for noktalar, _, _ in KATMANLAR
        for x, y in noktalar
    ) + CIZGI_KALINLIGI / 2


# Uyarlanır simgede işaretin oturacağı kutu (108 dp tuvalde).
#
# Android'in güvenli alanı ortadaki 72 dp'lik dairedir; yaygın öneri
# içeriği 66 dp'nin içinde tutmaktır. Kutu, ÖLÇÜLEN çizim yarıçapına
# göre seçildi (bkz. `isaret_yaricapi`) ve `main()` sınırı doğruluyor.
UYARLANIR_KUTU = 76

# Eski sürüm simgelerinde işaretin oturacağı kutu, simge boyutuna oran.
# Kare simge daha çok yer kaplar; yuvarlak simgede kenar payı gerekir.
ESKI_KARE_ORANI = 0.82
ESKI_YUVARLAK_ORANI = 0.72


def uyarlanir_on(boyut: int) -> Image.Image:
    """API 26+ uyarlanır simgenin ÖN katmanı — zemin ayrı bir renktir.

    Tuval 108 dp'dir ve dış kenardan her yönde kırpılabilir; güvenli
    alan ortadaki 72 dp'lik dairedir.
    """
    b = boyut * KAT
    im = Image.new("RGBA", (b, b), (0, 0, 0, 0))
    _isaret_ciz(im, b / 2, (b * UYARLANIR_KUTU / UYARLANIR_TABAN) / 32)
    return im.resize((boyut, boyut), Image.LANCZOS)


def main() -> None:
    print("Katman kontrastları (zemin #0d6b48 üzerinde):")
    for noktalar, _, opaklik in KATMANLAR:
        oran = _kontrast(_karisim(opaklik), ZEMIN)
        durum = "TAMAM" if oran >= 3.0 else "ZAYIF"
        print(f"  opaklık {opaklik:.2f} → kontrast {oran:.2f}:1  [{durum}]")
        if oran < 3.0:
            raise SystemExit(
                "Bir katman 3:1 eşiğinin altında; opaklığı yükseltin."
            )

    # Uyarlanır simgede işaretin güvenli daireye sığdığını DOĞRULA.
    yaricap32 = isaret_yaricapi()
    cap_dp = 2 * yaricap32 * UYARLANIR_KUTU / 32
    print(
        f"\nİşaretin çizim yarıçapı: {yaricap32:.2f}/32 birim"
        f"\nUyarlanır ön katman: {UYARLANIR_KUTU}dp kutu → işaret çapı "
        f"{cap_dp:.1f}dp (güvenli daire 72dp, önerilen 66dp)"
    )
    if cap_dp > 66:
        raise SystemExit("İşaret güvenli alanın dışına taşıyor.")

    # Eski sürüm simgelerinde de kenara taşma olmamalı.
    for etiket, oran in (
        ("kare", ESKI_KARE_ORANI),
        ("yuvarlak", ESKI_YUVARLAK_ORANI),
    ):
        doluluk = 2 * yaricap32 * oran / 32
        print(f"Eski simge ({etiket}): işaret, simge genişliğinin "
              f"%{doluluk * 100:.0f}'ini kaplıyor")
        if doluluk > 0.94:
            raise SystemExit(f"{etiket} simgede işaret kenara taşıyor.")

    print()
    for ad, carpan in YOGUNLUKLAR.items():
        klasor = RES / f"mipmap-{ad}"
        klasor.mkdir(parents=True, exist_ok=True)

        eski_boyut = round(ESKI_TABAN * carpan)
        on_boyut = round(UYARLANIR_TABAN * carpan)

        eski_simge(eski_boyut, yuvarlak=False).save(klasor / "ic_launcher.png")
        eski_simge(eski_boyut, yuvarlak=True).save(
            klasor / "ic_launcher_round.png"
        )
        uyarlanir_on(on_boyut).save(klasor / "ic_launcher_foreground.png")
        print(
            f"mipmap-{ad}: ic_launcher {eski_boyut}px · "
            f"ic_launcher_round {eski_boyut}px · "
            f"ic_launcher_foreground {on_boyut}px"
        )

    print("\nBitti.")


if __name__ == "__main__":
    main()
