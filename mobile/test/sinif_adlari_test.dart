import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:rebuild_vision_mobil/tema.dart';

/// Mobil sınıf haritasının SUNUCU SÖZLEŞMESİ.
///
/// `siniflar.json` deponun tek sınıf doğruluk kaynağıdır (`docs/siniflar.md`).
/// Mobil uygulama listeyi ÇEVRİMDIŞI da göstermek zorunda olduğu için renk
/// ve adları kendi içinde sabit tutar — sahada bağlantı olmayabilir ve
/// `/sistem/siniflar` çağrılamayabilir.
///
/// Sabit kopyanın bedeli sessiz ayrışmadır: 02.09.2026'da sınıf listesi
/// 10'dan 5'e indi ve mobil taraf elle güncellenmek zorunda kaldı. Bir
/// dahakine unutulursa mobil arayüz YANLIŞ RENK ve YANLIŞ AD gösterir,
/// hiçbir yerde hata görünmez. Bu test o sessizliği bozar.
void main() {
  final kok = Directory.current.path.endsWith('mobile')
      ? Directory.current.parent
      : Directory.current;
  final siniflar = (jsonDecode(
    File('${kok.path}/siniflar.json').readAsStringSync(),
  ) as Map<String, dynamic>)['siniflar'] as List;

  group('siniflar.json ile aynı', () {
    test('sınıf kümesi birebir aynı', () {
      final depo = siniflar.map((s) => s['ad'] as String).toSet();
      expect(Renk.malzeme.keys.toSet(), depo,
          reason: 'Mobil renk haritası siniflar.json ile ayrışmış');
      expect(Renk.malzemeAdi.keys.toSet(), depo,
          reason: 'Mobil ad haritası siniflar.json ile ayrışmış');
    });

    test('her sınıfın rengi siniflar.json ile aynı', () {
      for (final s in siniflar) {
        final ad = s['ad'] as String;
        final beklenen = (s['renk'] as String).replaceFirst('#', '').toUpperCase();
        final gercek = Renk.malzeme[ad]!
            .toARGB32()
            .toRadixString(16)
            .padLeft(8, '0')
            .substring(2)
            .toUpperCase();
        expect(gercek, beklenen, reason: '$ad rengi ayrışmış');
      }
    });

    test('her sınıfın görünen adı siniflar.json ile aynı', () {
      for (final s in siniflar) {
        expect(Renk.malzemeAdi[s['ad']], s['gorunen_ad'],
            reason: '${s['ad']} görünen adı ayrışmış');
      }
    });
  });

  group('ekranda ham sınıf adı görünmez', () {
    test('görünen adların hiçbiri alt çizgi taşımaz', () {
      for (final ad in Renk.malzemeAdi.values) {
        expect(ad.contains('_'), isFalse,
            reason: '"$ad" makine tanımlayıcısı gibi görünüyor');
      }
    });

    test('tanınmayan sınıfta ham ad gösterilir — uydurulmaz', () {
      expect(Renk.sinifAdi('bilinmeyen_sinif'), 'bilinmeyen_sinif');
    });
  });
}
