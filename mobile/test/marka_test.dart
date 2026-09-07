import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:rebuild_vision_mobil/marka.dart';

/// Marka işaretinin WEB SÖZLEŞMESİ.
///
/// ⚠️ MOBİLDE MARKA İŞARETİ YOKTU: giriş ekranında Material'ın hazır
/// `Icons.layers_outlined` simgesi duruyordu. Aynı ürünün web arayüzünde
/// üç katmanlı özel bir işaret var — iki yüz farklı simge gösteriyordu.
///
/// İşaret artık `Path` ile çiziliyor (`flutter_svg` bağımlılığı
/// eklemeden). Bedeli, koordinatların SVG dosyasından kopyalanmış
/// olması. Bu test o kopyayı bağlar: `web/public/logo-isaret.svg`
/// değişirse mobil sessizce eski işareti çizmeye devam edemez.
void main() {
  final kok = Directory.current.path.endsWith('mobile')
      ? Directory.current.parent
      : Directory.current;
  final svg =
      File('${kok.path}/web/public/logo-isaret.svg').readAsStringSync();

  /// SVG'deki `<path>` ögeleri: (d, opacity).
  final yollar = RegExp(r'<path\s+([^>]*?)/>')
      .allMatches(svg)
      .map((m) {
        final oz = m.group(1)!;
        final d = RegExp(r'd="([^"]*)"').firstMatch(oz)!.group(1)!;
        final o = RegExp(r'opacity="([^"]*)"').firstMatch(oz)?.group(1);
        return (d, o == null ? 1.0 : double.parse(o));
      })
      .toList();

  test('SVG üç katman içeriyor', () {
    expect(yollar.length, 3,
        reason: 'logo-isaret.svg katman sayısı değişmiş');
    expect(markaKatmanlari.length, yollar.length);
  });

  test('her katmanın yolu SVG ile birebir aynı', () {
    for (var i = 0; i < yollar.length; i++) {
      expect(markaKatmanlari[i].svgYolu, yollar[i].$1,
          reason: '$i. katmanın geometrisi ayrışmış');
    }
  });

  test('her katmanın opaklığı SVG ile aynı', () {
    for (var i = 0; i < yollar.length; i++) {
      expect(markaKatmanlari[i].opaklik, yollar[i].$2,
          reason: '$i. katmanın opaklığı ayrışmış');
    }
  });

  test('çizgi kalınlığı SVG ile aynı', () {
    final k = RegExp(r'stroke-width="([\d.]+)"').firstMatch(svg);
    expect(k, isNotNull, reason: 'SVG stroke-width taşımıyor');
    expect(markaCizgiKalinligi, double.parse(k!.group(1)!));
  });

  test('yalnızca son katman kapalıdır', () {
    // Üst katman dörtgen (`Z`), diğer ikisi açık çizgi. Kapanma
    // yanlışsa işaret bambaşka görünür.
    expect(markaKatmanlari.map((k) => k.kapali).toList(),
        [false, false, true]);
    expect(yollar.map((y) => y.$1.trimRight().endsWith('Z')).toList(),
        [false, false, true]);
  });

  test('bütün noktalar 32x32 çerçevenin içinde', () {
    for (final k in markaKatmanlari) {
      for (final n in k.noktalar) {
        expect(n.dx, inInclusiveRange(0, 32));
        expect(n.dy, inInclusiveRange(0, 32));
      }
    }
  });
}
