import 'package:flutter_test/flutter_test.dart';
import 'package:rebuild_vision_mobil/api.dart';
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

  group('güven skoru yuvarlanmaz (Bölüm 9.2)', () {
    test('web ile aynı sayıyı verir — 4 ondalığa kadar', () {
      // Gerçek model float32 döner; mobil bunu 1 basamağa yuvarlıyordu.
      expect(guvenYuzdesi(0.8734567), '87,3457');
      expect(guvenYuzdesi(0.5838851928710938), '58,3885');
    });

    test('ondalık ayracı VİRGÜL — nokta değil', () {
      expect(guvenYuzdesi(0.873), contains(','));
      expect(guvenYuzdesi(0.873), isNot(contains('.')));
    });

    test('gereksiz sıfır yazılmaz', () {
      expect(guvenYuzdesi(0.78), '78');
      expect(guvenYuzdesi(0.5), '50');
      expect(guvenYuzdesi(1.0), '100');
    });
  });

  group('kuyrukta gösterilen birim', () {
    test('sunucu biriminden tipografik birime çevrilir', () {
      // Kuyruk listesi sunucu birimini basıyordu: kullanıcı formda "m³"
      // seçip gönderdikten sonra aynı kaydı kuyrukta "m2" görüyordu.
      expect(gorunenBirimi('m2'), 'm²');
      expect(gorunenBirimi('m3'), 'm³');
      expect(gorunenBirimi('ton'), 'ton');
    });

    test('bilinmeyen birim olduğu gibi gösterilir — uydurulmaz', () {
      expect(gorunenBirimi('kg'), 'kg');
    });
  });
}
