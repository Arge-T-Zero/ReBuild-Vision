import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:rebuild_vision_mobil/api.dart';
import 'package:rebuild_vision_mobil/ekran/giris.dart';
import 'package:rebuild_vision_mobil/ekran/hesap.dart';
import 'package:rebuild_vision_mobil/roller.dart';
import 'package:rebuild_vision_mobil/tema.dart';

/// Ekran görüntüsü üretici — gözle denetim için.
///
/// Çalıştırma:
///     flutter test tools/ekran_goruntusu.dart
///
/// Çıktı: `tools/ekran-goruntusu/` altına PNG dosyaları.
///
/// NEDEN TARAYICI DEĞİL: `flutter run -d web-server` + Playwright yolu
/// bu ortamda çalışmıyor — CanvasKit WebGL yüzeyi başsız tarayıcıda
/// ekran görüntüsüne düşmüyor ve dosya bembeyaz çıkıyor (ölçüldü: tek
/// renk, #FFFFFF). Buradaki yol Flutter'ın kendi rasterleştiricisini
/// kullanır; altın (golden) testlerinin kullandığı mekanizmanın aynısı.
///
/// Bu bir TEST DEĞİLDİR: hiçbir şeyi doğrulamaz, yalnızca çizer. Asıl
/// doğrulamalar `test/` altındadır.
void main() {
  final klasor = Directory('tools/ekran-goruntusu')..createSync(recursive: true);

  /// Widget'ı verilen boyutta çizip PNG olarak yazar.
  Future<void> ciz(
    WidgetTester t,
    String ad,
    Size boyut,
    Widget cocuk, {
    Future<void> Function(WidgetTester)? sonra,
  }) async {
    t.view.physicalSize = boyut;
    t.view.devicePixelRatio = 1.0;
    addTearDown(t.view.reset);

    final anahtar = GlobalKey();
    await t.pumpWidget(RepaintBoundary(key: anahtar, child: cocuk));
    await t.pump();
    // Varlıklar (hero görseli) çözülene kadar birkaç kare.
    for (var i = 0; i < 8; i++) {
      await t.pump(const Duration(milliseconds: 120));
    }
    if (sonra != null) await sonra(t);

    final sinir =
        anahtar.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    final resim = await sinir.toImage(pixelRatio: 2);
    final bayt = await resim.toByteData(format: ui.ImageByteFormat.png);
    File('${klasor.path}/$ad.png')
        .writeAsBytesSync(bayt!.buffer.asUint8List());
    // ignore: avoid_print
    print('yazıldı: ${klasor.path}/$ad.png  (${boyut.width.toInt()}x'
        '${boyut.height.toInt()})');
  }

  Widget uygulama(Widget ekran, {required bool koyu}) => MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: uygulamaTemasi(koyu: koyu),
        home: ekran,
      );

  /// Sahte sunucu: sahte model servisi kapalı, giriş 500 dönüyor.
  Api sunucu({bool sahteModel = false, int girisDurumu = 500}) => Api(
        istemci: MockClient((i) async {
          if (i.url.path.endsWith('/sistem/durum')) {
            return http.Response(
              '{"model_servisi":{"sahte":$sahteModel}}',
              200,
              headers: {'content-type': 'application/json; charset=utf-8'},
            );
          }
          return http.Response('Internal Server Error', girisDurumu,
              headers: {'content-type': 'text/plain'});
        }),
      );

  Widget giris({bool koyu = false, bool sahteModel = false}) => uygulama(
        GirisEkrani(
          api: sunucu(sahteModel: sahteModel),
          girisYapildi: (_) {},
          koyuTema: koyu,
          temaDegistir: () async {},
        ),
        koyu: koyu,
      );

  Widget hesap(String? rol, {bool koyu = false, bool? sahte}) => uygulama(
        Scaffold(
          appBar: AppBar(
            title: const Text('ReBuild Vision',
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.w600)),
          ),
          body: HesapEkrani(
            kullanici: Kullanici(
              id: 4,
              ad: 'Mehmet Demir',
              eposta: 'belediye@demo.local',
              rol: rol,
            ),
            tanim: rolTanimi(rol),
            sahteModel: sahte,
          ),
        ),
        koyu: koyu,
      );

  const telefon = Size(412, 915);
  const tablet = Size(1194, 834);

  testWidgets('giriş ekranı', (t) async {
    await ciz(t, '01-giris-telefon-acik', telefon, giris());
    await ciz(t, '02-giris-telefon-koyu', telefon, giris(koyu: true));
    await ciz(t, '03-giris-tablet-acik', tablet, giris());
    await ciz(t, '04-giris-sahte-model', telefon,
        giris(sahteModel: true));
  });

  testWidgets('giriş — hata ve bekleyiş', (t) async {
    await ciz(
      t,
      '05-giris-500-hatasi',
      telefon,
      giris(),
      sonra: (t) async {
        await t.tap(find.text('Giriş yap').last);
        await t.pumpAndSettle();
      },
    );
  });

  testWidgets('hesap ekranı — roller', (t) async {
    await ciz(t, '06-hesap-belediye', telefon, hesap('belediye'));
    await ciz(t, '07-hesap-afad', telefon, hesap('afad'));
    await ciz(t, '08-hesap-rol-yok', telefon, hesap(null));
    await ciz(t, '09-hesap-saha-sahte-model', telefon,
        hesap('saha', sahte: true));
  });
}
