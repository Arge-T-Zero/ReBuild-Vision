import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:rebuild_vision_mobil/api.dart';

/// Görüntü yüklemenin SUNUCU SÖZLEŞMESİ.
///
/// Bu test bir arızanın nöbetçisidir — kardeşi `olcum_turu_test.dart` gibi.
///
/// `MultipartFile.fromPath` çağrısına `contentType` verilmediğinde `http`
/// paketi `application/octet-stream` gönderiyordu. Sunucu yalnızca
/// `image/jpeg|png|webp` kabul ediyor ve ilk dosyada BÜTÜN partiyi 415 ile
/// düşürüyor. Sonuç: saha uygulamasından yüklenen hiçbir fotoğraf
/// geçmiyordu ve kullanıcı ekranda ham MIME tipini görüyordu.
///
/// Hata yalnızca gerçek cihazda ortaya çıkıyordu: web arayüzünde türü
/// tarayıcı belirliyor, Flutter web'de ise `fromPath` zaten daha önce
/// hata veriyor. Bu yüzden hiçbir el denemesi yakalamamıştı.
void main() {
  group('gönderilen MIME türü', () {
    test('jpg ve jpeg → image/jpeg', () {
      expect(goruntuTuru('/tmp/foto.jpg').toString(), 'image/jpeg');
      expect(goruntuTuru('/tmp/foto.jpeg').toString(), 'image/jpeg');
    });

    test('png → image/png, webp → image/webp', () {
      expect(goruntuTuru('/tmp/foto.png').toString(), 'image/png');
      expect(goruntuTuru('/tmp/foto.webp').toString(), 'image/webp');
    });

    test('büyük harfli uzantı da tanınır', () {
      expect(goruntuTuru('/tmp/FOTO.PNG').toString(), 'image/png');
    });

    test('bilinmeyen uzantı octet-stream\'e DÜŞMEZ', () {
      // Asıl arıza buydu: sessiz varsayılan sunucuyu 415'e sürüklüyordu.
      final t = goruntuTuru('/tmp/kameradan-gelen-dosya');
      expect(t.mimeType, isNot('application/octet-stream'));
      expect(t.type, 'image');
    });

    test('üretilen her tür sunucunun izin listesinde', () {
      for (final yol in ['a.jpg', 'a.jpeg', 'a.png', 'a.webp', 'a.bilinmeyen']) {
        expect(izinliGoruntuTurleri, contains(goruntuTuru(yol).mimeType),
            reason: '$yol için üretilen tür sunucuca reddedilirdi');
      }
    });
  });

  group('izin listesi sunucuyla aynı', () {
    test('goruntuler.py içindeki IZINLI_TURLER ile birebir', () {
      // Sunucu kaynağı doğrudan okunur; iki liste ayrışırsa test kırılır.
      final kok = Directory.current.path.endsWith('mobile')
          ? Directory.current.parent
          : Directory.current;
      final kaynak =
          File('${kok.path}/api/app/routers/goruntuler.py').readAsStringSync();
      final satir = RegExp(r'IZINLI_TURLER\s*=\s*\{([^}]*)\}')
          .firstMatch(kaynak)!
          .group(1)!;
      final sunucu = RegExp(r'"([^"]+)"')
          .allMatches(satir)
          .map((m) => m.group(1)!)
          .toSet();
      expect(izinliGoruntuTurleri, sunucu,
          reason: 'Mobil izin listesi sunucununkiyle ayrışmış');
    });
  });
}
