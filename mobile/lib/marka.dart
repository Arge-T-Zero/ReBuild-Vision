import 'package:flutter/material.dart';

import 'tema.dart';

/// Marka işareti — `web/public/logo-isaret.svg` ile AYNI geometri.
///
/// ⚠️ MOBİLDE MARKA İŞARETİ YOKTU: giriş ekranında Material'ın hazır
/// `Icons.layers_outlined` simgesi kullanılıyordu. Aynı ürünün web
/// arayüzünde üç katmanlı özel bir işaret var; iki yüz farklı simge
/// gösteriyordu.
///
/// Yol verileri SVG'den birebir alındı (viewBox 0 0 32 32, çizgi
/// kalınlığı 2, yuvarlak uç ve köşe):
///
///   M4 22.5 L16 28 L28 22.5        opaklık 0.45   (alt katman)
///   M4 16   L16 21.5 L28 16        opaklık 0.70   (orta katman)
///   M4 9.5  L16 4 L28 9.5 L16 15 Z opaklık 1      (üst katman, kapalı)
///
/// Neden SVG dosyası kullanılmıyor: `flutter_svg` yeni bir bağımlılık
/// demek. Üç çizgiden ibaret bir işaret için paket eklemek yerine aynı
/// koordinatlar `Path` ile çiziliyor; ölçekten bağımsız keskin kalıyor
/// ve dosya ile ayrışırsa `test/marka_test.dart` yakalar.
///
/// Aynı geometri Android uygulama simgesinde de kullanılır
/// (`tools/simge_uret.py`) — üç yüzey tek işaret gösterir.
class MarkaIsareti extends StatelessWidget {
  final double boyut;
  final Color? renk;

  const MarkaIsareti({super.key, this.boyut = 20, this.renk});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: boyut,
        height: boyut,
        child: CustomPaint(
          painter: _IsaretCizeri(renk ?? Renk.marka),
        ),
      );
}

/// İşaretin kare çerçeveli hâli — web'deki `Marka` bileşeninin karşılığı
/// (`bg-marka/15`, `border-marka/40`, `rounded-lg`).
class MarkaKutusu extends StatelessWidget {
  final double boyut;

  const MarkaKutusu({super.key, this.boyut = 44});

  @override
  Widget build(BuildContext context) => Container(
        width: boyut,
        height: boyut,
        decoration: BoxDecoration(
          color: Renk.marka.withValues(alpha: 0.15),
          border: Border.all(color: Renk.marka.withValues(alpha: 0.4)),
          borderRadius: BorderRadius.circular(boyut * 0.23),
        ),
        alignment: Alignment.center,
        child: MarkaIsareti(boyut: boyut * 0.5),
      );
}

/// İşaretin bir katmanı — SVG'deki tek bir `<path>` ögesinin karşılığı.
class MarkaKatmani {
  /// 32x32 düzlemindeki düğüm noktaları.
  final List<Offset> noktalar;

  /// SVG'de yol `Z` ile kapanıyor mu?
  final bool kapali;

  /// SVG'deki `opacity` özniteliği (yoksa 1).
  final double opaklik;

  const MarkaKatmani(this.noktalar, {this.kapali = false, this.opaklik = 1});

  /// Katmanın SVG `d` özniteliği karşılığı.
  ///
  /// ÇİZİM VE SINAMA AYNI VERİDEN türesin diye burada üretiliyor:
  /// koordinatlar bir yerde, karşılaştırma dizesi başka yerde yazılsaydı
  /// biri değişip diğeri unutulurdu. `marka_test.dart` bu dizeyi
  /// `web/public/logo-isaret.svg` içindekiyle karşılaştırır.
  String get svgYolu {
    String sayi(double d) =>
        d == d.roundToDouble() ? '${d.toInt()}' : '$d';
    final parcalar = <String>[
      'M${sayi(noktalar.first.dx)} ${sayi(noktalar.first.dy)}',
      for (final n in noktalar.skip(1)) 'L${sayi(n.dx)} ${sayi(n.dy)}',
      if (kapali) 'Z',
    ];
    return parcalar.join(' ');
  }
}

/// Marka işaretinin katmanları — `web/public/logo-isaret.svg` ile aynı.
const markaKatmanlari = <MarkaKatmani>[
  // Alt katman
  MarkaKatmani(
    [Offset(4, 22.5), Offset(16, 28), Offset(28, 22.5)],
    opaklik: 0.45,
  ),
  // Orta katman
  MarkaKatmani(
    [Offset(4, 16), Offset(16, 21.5), Offset(28, 16)],
    opaklik: 0.7,
  ),
  // Üst katman — kapalı dörtgen
  MarkaKatmani(
    [Offset(4, 9.5), Offset(16, 4), Offset(28, 9.5), Offset(16, 15)],
    kapali: true,
  ),
];

/// SVG'deki `stroke-width`.
const markaCizgiKalinligi = 2.0;

class _IsaretCizeri extends CustomPainter {
  final Color renk;
  const _IsaretCizeri(this.renk);

  @override
  void paint(Canvas tuval, Size boyut) {
    // SVG 32x32 düzleminde çizilmiş; istenen boyuta ölçekleniyor.
    final o = boyut.width / 32.0;

    final firca = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = markaCizgiKalinligi * o
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    for (final k in markaKatmanlari) {
      final yol = Path()
        ..moveTo(k.noktalar.first.dx * o, k.noktalar.first.dy * o);
      for (final n in k.noktalar.skip(1)) {
        yol.lineTo(n.dx * o, n.dy * o);
      }
      if (k.kapali) yol.close();
      tuval.drawPath(yol, firca..color = renk.withValues(alpha: k.opaklik));
    }
  }

  @override
  bool shouldRepaint(_IsaretCizeri eski) => eski.renk != renk;
}
