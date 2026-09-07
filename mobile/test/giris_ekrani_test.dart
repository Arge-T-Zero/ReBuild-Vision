import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:rebuild_vision_mobil/api.dart';
import 'package:rebuild_vision_mobil/ekran/giris.dart';
import 'package:rebuild_vision_mobil/marka.dart';
import 'package:rebuild_vision_mobil/tema.dart';

/// Giriş ekranı — görünüş ve BEKLEYİŞİN ANLATIMI.
///
/// İki saha bildiriminin nöbetçisi:
///
///   1. "Arka planın güzelliği yok, giriş arka planı web'deki gibi
///      değil." → ekran web'den türetildi; hero görseli, marka işareti,
///      üç çalışma kuralı ve künye burada olmalı.
///   2. "Girişler filan yavaş, geç giriyor." → yavaşlığın kaynağı sunucu
///      (Render ücretsiz katmanı uyanıyor) ama arayüz bunu söylemeliydi;
///      söylemiyordu.
void main() {
  /// Yüzeyi uzat: `SingleChildScrollView` görünmeyen içeriği kurar ama
  /// dokunma/bulma işlemleri için ekranın sığması daha güvenli.
  void uzunEkran(WidgetTester t) {
    t.view.physicalSize = const Size(900, 2600);
    t.view.devicePixelRatio = 1.0;
    addTearDown(t.view.reset);
  }

  /// Giriş ekranını verilen sahte sunucuyla kurar.
  Future<Api> ac(
    WidgetTester t, {
    required Future<http.Response> Function(http.Request) yanit,
  }) async {
    uzunEkran(t);
    final api = Api(istemci: MockClient(yanit));
    await t.pumpWidget(MaterialApp(
      theme: uygulamaTemasi(koyu: false),
      home: GirisEkrani(
        api: api,
        girisYapildi: (_) {},
        koyuTema: false,
        temaDegistir: () async {},
      ),
    ));
    await t.pump();
    return api;
  }

  /// `/sistem/durum` dışındaki her isteğe 500 dönen sunucu.
  Future<http.Response> sessizSunucu(http.Request i) async =>
      http.Response('Internal Server Error', 500,
          headers: {'content-type': 'text/plain'});

  group('web arayüzünden türetilen düzen', () {
    testWidgets('arka planda hero görseli var', (t) async {
      await ac(t, yanit: sessizSunucu);
      final gorsel = t.widget<Image>(find.byType(Image).first);
      expect(gorsel.image, isA<AssetImage>());
      expect((gorsel.image as AssetImage).assetName,
          'assets/gorseller/giris-hero.webp',
          reason: 'Web ile aynı dosya kullanılmalı');
      expect(gorsel.fit, BoxFit.cover);
    });

    testWidgets('marka işareti Material simgesi DEĞİL', (t) async {
      // Eskiden `Icons.layers_outlined` kullanılıyordu; web'de özel bir
      // işaret var ve iki yüz farklı simge gösteriyordu.
      await ac(t, yanit: sessizSunucu);
      expect(find.byType(MarkaIsareti), findsOneWidget);
      expect(find.byIcon(Icons.layers_outlined), findsNothing);
    });

    testWidgets('web başlığı birebir aynı', (t) async {
      await ac(t, yanit: sessizSunucu);
      expect(
        find.textContaining('Enkaz malzemelerinin görüntü tabanlı ön '
            'sınıflandırması ve doğrulanabilir kaynak haritası'),
        findsOneWidget,
      );
    });

    testWidgets('üç çalışma kuralı ve künye gösterilir', (t) async {
      await ac(t, yanit: sessizSunucu);
      expect(find.text('İnsan denetimli sınıflandırma'), findsOneWidget);
      expect(find.text('Ölçüm yoksa miktar üretilmez'), findsOneWidget);
      expect(find.text('Her kayıt izlenebilir'), findsOneWidget);
      expect(find.textContaining('TEKNOFEST 2026'), findsOneWidget);
    });
  });

  group('bekleyiş anlatılır', () {
    /// Cevabı testin denetlediği sunucu.
    ///
    /// `Future.delayed` KULLANILAMAZ: testi bitiren doğrulama bekleyen
    /// zamanlayıcı bırakılmasına izin vermiyor. Cevap bir `Completer`
    /// ile, tam istenen anda veriliyor.
    (Completer<http.Response>, Future<http.Response> Function(http.Request))
        askidaSunucu() {
      final c = Completer<http.Response>();
      return (
        c,
        (i) => i.url.path.endsWith('/sistem/durum')
            ? Future.value(http.Response('{}', 500))
            : c.future,
      );
    }

    testWidgets('ilk saniyelerde "sunucu uyanıyor" YAZMAZ', (t) async {
      // Sunucu uyanıksa bu cümle yanlış bilgi olurdu; ekranda parlayıp
      // kaybolan bir metin de gürültüdür.
      final (bitir, sunucu) = askidaSunucu();
      await ac(t, yanit: sunucu);
      await t.tap(find.text('Giriş yap').last);
      // İlk `pump` bekleme kutusunu KURAR; zamanlayıcı ancak o anda
      // başlar. Süre bundan sonra ilerletilir.
      await t.pump();
      await t.pump(const Duration(seconds: 1));

      expect(find.byType(LinearProgressIndicator), findsOneWidget);
      expect(find.textContaining('Giriş yapılıyor'), findsWidgets);
      expect(find.textContaining('Sunucu uyanıyor'), findsNothing);

      bitir.complete(http.Response('{}', 500));
      await t.pumpAndSettle();
    });

    testWidgets('bekleyiş uzayınca dürüst açıklama belirir', (t) async {
      final (bitir, sunucu) = askidaSunucu();
      await ac(t, yanit: sunucu);
      await t.tap(find.text('Giriş yap').last);
      await t.pump();
      await t.pump(const Duration(seconds: 6));

      expect(find.textContaining('Sunucu uyanıyor olabilir'), findsOneWidget);
      // Ne kadar bekleneceği SOMUT olarak yazılır.
      expect(
        find.textContaining('${Api.kimlikSuresi.inSeconds} saniye'),
        findsOneWidget,
      );
      expect(find.byType(LinearProgressIndicator), findsOneWidget);

      bitir.complete(http.Response('{}', 500));
      await t.pumpAndSettle();
    });
  });

  group('hata mesajları', () {
    testWidgets('500 çıplak sayı olarak gösterilmez', (t) async {
      await ac(t, yanit: sessizSunucu);
      await t.tap(find.text('Giriş yap').last);
      await t.pumpAndSettle();

      expect(find.textContaining('Sunucuda beklenmeyen bir hata'),
          findsOneWidget);
      // Ham kod gizlenmez.
      expect(find.textContaining('500'), findsOneWidget);
    });

    testWidgets('sunucunun kendi gerekçesi korunur', (t) async {
      await ac(t, yanit: (i) async {
        if (i.url.path.endsWith('/sistem/durum')) {
          return http.Response('{"model_servisi":{"sahte":false}}', 200);
        }
        return http.Response(
          jsonEncode({'detail': 'E-posta veya parola hatalı'}),
          401,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });
      await t.tap(find.text('Giriş yap').last);
      await t.pumpAndSettle();

      expect(find.textContaining('E-posta veya parola hatalı'),
          findsOneWidget);
      expect(find.textContaining('401'), findsOneWidget);
    });
  });

  group('sahte model servisi', () {
    testWidgets('sunucu sahte diyorsa giriş ekranında da söylenir',
        (t) async {
      // Web giriş ekranı bu uyarıyı gösteriyordu, mobil göstermiyordu:
      // demoyu izleyen kişi sisteme girmeden gerçek bir modelin
      // çalıştığını sanabilirdi (ana talimat Bölüm 9.5).
      await ac(t, yanit: (i) async {
        if (i.url.path.endsWith('/sistem/durum')) {
          return http.Response(
            '{"model_servisi":{"sahte":true}}',
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          );
        }
        return http.Response('{}', 500);
      });
      await t.pumpAndSettle();
      expect(find.textContaining('SAHTE MODEL SERVİSİ etkin'), findsOneWidget);
    });

    testWidgets('sunucuya ulaşılamıyorsa hiçbir şey iddia edilmez',
        (t) async {
      await ac(t, yanit: sessizSunucu);
      await t.pumpAndSettle();
      expect(find.textContaining('SAHTE MODEL SERVİSİ'), findsNothing);
    });

    testWidgets('sunucu gerçek diyorsa rozet ÇIKMAZ', (t) async {
      await ac(t, yanit: (i) async => http.Response(
            '{"model_servisi":{"sahte":false}}',
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          ));
      await t.pumpAndSettle();
      expect(find.textContaining('SAHTE MODEL SERVİSİ'), findsNothing);
    });
  });
}
