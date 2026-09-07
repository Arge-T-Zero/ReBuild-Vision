import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rebuild_vision_mobil/api.dart';
import 'package:rebuild_vision_mobil/ekran/hesap.dart';
import 'package:rebuild_vision_mobil/roller.dart';
import 'package:rebuild_vision_mobil/tema.dart';

/// Hesap ekranı — "benim ekranım nerede?" sorusuna verilen cevap.
///
/// ⚠️ KULLANICI ŞUNU BİLDİRDİ: "Belediye yetkilisi olarak giriş yaptım
/// ama bana belediyenin ekranı gelmedi, sadece saha personeli ekranı
/// var."
///
/// Verilen tasarım kararı: mobil SAHA uygulaması olarak kalır; web'deki
/// altı ekran telefona taşınmaz. Karar meşru, ama SESSİZLİK değil. Bu
/// test o sessizliğin geri gelmediğini kovalar: hangi rolle bakılırsa
/// bakılsın ekranda rolün adı, ne yapabileceği ve yapamadıklarının
/// nerede olduğu yazılı olmalıdır.
void main() {
  Widget sar(Widget c) => MaterialApp(
        theme: uygulamaTemasi(koyu: false),
        home: Scaffold(body: c),
      );

  Kullanici kisi(String? rol) => Kullanici(
        id: 1,
        ad: 'Ayşe Yılmaz',
        eposta: 'ayse@kurum.gov.tr',
        rol: rol,
      );

  /// Test yüzeyi varsayılan olarak 800x600'dür ve `ListView` görünmeyen
  /// çocuklarını HİÇ KURMAZ — ekranın altındaki metinler bulunamaz.
  /// Yüzey, ekranın tamamı tek karede sığacak kadar uzatılıyor.
  void uzunEkran(WidgetTester t) {
    t.view.physicalSize = const Size(900, 2600);
    t.view.devicePixelRatio = 1.0;
    addTearDown(t.view.reset);
  }

  Future<void> ac(WidgetTester t, String? rol, {bool? sahte}) async {
    uzunEkran(t);
    await t.pumpWidget(sar(HesapEkrani(
      kullanici: kisi(rol),
      tanim: rolTanimi(rol),
      sahteModel: sahte,
    )));
    await t.pump();
  }

  testWidgets('rolün adı ve görevi ekranda yazılıdır', (t) async {
    await ac(t, 'belediye');
    expect(find.text('BELEDİYE YETKİLİSİ'), findsOneWidget);
    expect(
      find.textContaining('Enkaz alanlarını tanımlayın'),
      findsOneWidget,
    );
    expect(find.text('Ayşe Yılmaz'), findsOneWidget);
    expect(find.text('ayse@kurum.gov.tr'), findsOneWidget);
  });

  testWidgets('mobilin SAHA uygulaması olduğu açıkça söylenir', (t) async {
    await ac(t, 'belediye');
    expect(find.textContaining('SAHA ÇALIŞMASI içindir'), findsOneWidget);
    expect(find.textContaining('web arayüzündedir'), findsOneWidget);
  });

  testWidgets('web arayüzünün adresi gösterilir', (t) async {
    // "Web arayüzünü kullanın" deyip nereye gidileceğini söylememek
    // yarım bir yönlendirmedir.
    await ac(t, 'afad');
    expect(find.text(Api.webTaban), findsOneWidget);
  });

  testWidgets('yetkisi olan rol ne yapabileceğini görür', (t) async {
    await ac(t, 'saha');
    expect(find.textContaining('fotoğraf yükleyip'), findsOneWidget);
    expect(find.textContaining('ölçüm girmek'), findsOneWidget);
  });

  testWidgets('belediye ölçüm girişini YAPABİLECEKLERİ arasında görmez',
      (t) async {
    await ac(t, 'belediye');
    expect(find.textContaining('fotoğraf yükleyip'), findsOneWidget);
    expect(find.textContaining('ölçüm girmek'), findsNothing);
  });

  testWidgets('yetkisiz rol boş ekran değil, gerekçe görür', (t) async {
    // AFAD sunucuda ne yükleyebilir ne ölçüm girebilir. Ona boş bir
    // form göstermek yanlış; hiçbir şey göstermemek de yanlış.
    await ac(t, 'afad');
    expect(find.textContaining('yapabileceği bir işlem yok'), findsOneWidget);
    expect(find.textContaining('Bu bir arıza değil'), findsOneWidget);
  });

  testWidgets('rolü atanmamış hesaba onay beklediği söylenir', (t) async {
    await ac(t, null);
    expect(find.text('ROL ATANMADI'), findsOneWidget);
    expect(find.textContaining('yönetici onayı bekliyor'), findsOneWidget);
    expect(find.textContaining('Rol atamasını'), findsOneWidget);
  });

  testWidgets('yetkinin sunucuda denetlendiği yazılıdır', (t) async {
    // Arayüzde gizlemek güvenlik değildir; bunu kullanıcıya da
    // söylemek, listenin ne olduğunu doğru anlatır.
    await ac(t, 'saha');
    expect(find.textContaining('Yetki denetimi sunucuda yapılır'),
        findsOneWidget);
  });

  group('sahte model servisi rozeti', () {
    testWidgets('sahte servis çalışıyorsa söylenir', (t) async {
      await ac(t, 'saha', sahte: true);
      expect(find.textContaining('SAHTE MODEL SERVİSİ etkin'), findsOneWidget);
      expect(find.textContaining('uydurmadır'), findsOneWidget);
    });

    testWidgets('bilinmiyorsa HİÇBİR ŞEY iddia edilmez', (t) async {
      // Çevrimdışıyken "gerçek model çalışıyor" demek de "sahte" demek
      // de yanlış olurdu (ana talimat Bölüm 9.5).
      await ac(t, 'saha');
      expect(find.textContaining('SAHTE MODEL SERVİSİ'), findsNothing);
      expect(find.textContaining('Gerçek model servisi'), findsNothing);
    });
  });
}
