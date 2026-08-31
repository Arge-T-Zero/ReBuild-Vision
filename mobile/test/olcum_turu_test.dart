import 'package:flutter_test/flutter_test.dart';
import 'package:rebuild_vision_mobil/olcum_turu.dart';

/// Ölçüm biriminin SUNUCU SÖZLEŞMESİ.
///
/// Bu test bir hatanın nöbetçisidir. Alan ölçümleri sunucuya `m²` olarak
/// gidiyordu; sunucu `m2` bekliyor (api/app/schemas.py `TURUN_BIRIMI`) ve
/// isteği reddediyordu. Eşitleme toplu çalıştığı için kuyrukta tek bir
/// alan ölçümü bulunduğunda bütün parti düşüyor, o cihaz bir daha hiç
/// eşitlenemiyordu.
///
/// Aşağıdaki değerler sunucudaki sözlükle BİREBİR aynı olmak zorundadır.
/// Biri değişirse ikisi birden değişmelidir.
void main() {
  group('sunucuya giden birim', () {
    test('alan ölçümü m2 gönderir — m² DEĞİL', () {
      expect(olcumTurleri['alan']!.sunucuBirimi, 'm2');
      expect(olcumTurleri['alan']!.sunucuBirimi, isNot('m²'),
          reason: 'Sunucu m² birimini reddeder ve bütün partiyi düşürürdü');
    });

    test('hacim ölçümü m3 gönderir', () {
      expect(olcumTurleri['hacim']!.sunucuBirimi, 'm3');
    });

    test('ağırlık ölçümü ton gönderir', () {
      expect(olcumTurleri['agirlik']!.sunucuBirimi, 'ton');
    });

    test('gönderilen birimlerin hiçbiri tipografik simge içermez', () {
      for (final t in olcumTurleri.values) {
        expect(RegExp(r'^[a-z0-9]+$').hasMatch(t.sunucuBirimi), isTrue,
            reason: '"${t.sunucuBirimi}" sunucunun kabul ettiği biçimde değil');
      }
    });
  });

  group('ekranda görünen birim', () {
    test('kullanıcı doğru tipografik simgeyi görür', () {
      expect(olcumTurleri['alan']!.gorunenBirim, 'm²');
      expect(olcumTurleri['hacim']!.gorunenBirim, 'm³');
      expect(olcumTurleri['agirlik']!.gorunenBirim, 'ton');
    });
  });

  group('tür anahtarları', () {
    test('sunucunun OlcumTuru enum değerleriyle aynı', () {
      expect(olcumTurleri.keys.toSet(), {'agirlik', 'hacim', 'alan'});
    });
  });

  group('üst sınır', () {
    test('sunucudaki OLCUM_UST_SINIR ile aynı', () {
      expect(olcumUstSiniri, 100000.0);
    });
  });
}
