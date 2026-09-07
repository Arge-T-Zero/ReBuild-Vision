import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:rebuild_vision_mobil/api.dart';

/// Sunucu hatalarının KULLANICIYA NASIL GÖRÜNDÜĞÜ.
///
/// ⚠️ BU TEST BİR SAHA BİLDİRİMİNİN NÖBETÇİSİDİR. Kullanıcı tablette
/// fotoğraf yüklemeyi denedi ve şunu gördü:
///
///     Yükleme başarısız (500): İstek başarısız (500)
///
/// Aynı sayı iki kez, hiçbir anlam bir kez. 500'ün kaynağı yerelde
/// yeniden üretildi: model servisi 429 döndüğünde
/// `api/app/routers/goruntuler.py` içindeki `ModelServisiHatasi`
/// yakalanmıyor ve FastAPI **JSON DEĞİL, DÜZ METİN** bir gövdeyle 500
/// dönüyor (`Internal Server Error`). Mobil de `detail` alanını
/// bulamayınca yer tutucu mesajı ekrana basıyordu.
///
/// Kural: ANLAM önce, ham kod sonra. Ham kod gizlenmez — bildirim yapan
/// kullanıcının işine yarar — ama tek başına da bırakılmaz.
void main() {
  /// Verilen yanıtı döndüren sahte sunucuyla `Api` kurar.
  Api sahteSunucu(int durum, String govde, {String? tur}) => Api(
        istemci: MockClient((_) async => http.Response(
              govde,
              durum,
              headers: {
                'content-type': tur ?? 'application/json; charset=utf-8',
              },
            )),
      );

  group('sunucu düz metin döndüğünde', () {
    test('500 için anlamlı bir cümle yazılır — çıplak sayı değil', () async {
      // Yerelde ölçülen gerçek yanıt: gövde `Internal Server Error`,
      // içerik türü `text/plain`.
      final api = sahteSunucu(500, 'Internal Server Error', tur: 'text/plain');
      final h = await api.siniflar().then<ApiHatasi?>((_) => null,
          onError: (e) => e is ApiHatasi ? e : null);

      expect(h, isNotNull);
      expect(h!.sunucuAcikladi, isFalse,
          reason: 'Sunucu açıklama yapmadı; mesaj bizim kurmamız gerekir');
      expect(h.kullaniciMesaji, contains('Sunucuda beklenmeyen bir hata'));
      expect(h.kullaniciMesaji, contains('500'),
          reason: 'Ham kod gizlenmez');
      expect(h.kullaniciMesaji.contains('İstek başarısız'), isFalse,
          reason: 'Yer tutucu metin kullanıcıya gösterilmemeli');
    });

    test('yüklemede 500 bilinen nedeni de söyler', () {
      final m = yuklemeHataMesaji(
        ApiHatasi(500, 'İstek başarısız (500)', sunucuAcikladi: false),
      );
      expect(m, contains('model servisinin'));
      expect(m, contains('500'));
      expect(m, contains('tekrar gönderin'),
          reason: 'Geçici bir durum — ne yapılacağı söylenmeli');
      expect(m, contains('Fotoğraflar listede duruyor'));
    });

    test('429 hız sınırı olarak anlatılır', () {
      final m = yuklemeHataMesaji(
        ApiHatasi(429, 'İstek başarısız (429)', sunucuAcikladi: false),
      );
      expect(m, contains('hız sınırı'));
      expect(m, contains('429'));
    });

    test('503 uyanma olarak anlatılır', () {
      final h = ApiHatasi(503, 'İstek başarısız (503)', sunucuAcikladi: false);
      expect(h.kullaniciMesaji, contains('Uyanması'));
      expect(h.kullaniciMesaji, contains('503'));
    });
  });

  group('sunucu gerekçe yazdığında', () {
    test('sunucunun kendi Türkçe metni korunur', () async {
      final api = sahteSunucu(
        403,
        jsonEncode({'detail': 'Bu işlem için yetkiniz yok'}),
      );
      final h = await api.siniflar().then<ApiHatasi?>((_) => null,
          onError: (e) => e is ApiHatasi ? e : null);

      expect(h!.sunucuAcikladi, isTrue);
      expect(h.kullaniciMesaji, startsWith('Bu işlem için yetkiniz yok'));
      expect(h.kullaniciMesaji, contains('403'));
    });

    test('yükleme mesajı sunucunun gerekçesini ezmez', () {
      final m = yuklemeHataMesaji(
        ApiHatasi(413, 'Görüntü çok büyük (48 MB): saha.jpg'),
      );
      expect(m, startsWith('Görüntü çok büyük'));
      expect(m, contains('413'));
    });
  });

  group('her hata metni bir kod taşır', () {
    test('bilinen kodların hepsinde ham kod görünür', () {
      for (final kod in [400, 401, 403, 404, 413, 415, 422, 429, 500, 503]) {
        final h = ApiHatasi(kod, 'yer tutucu', sunucuAcikladi: false);
        expect(h.kullaniciMesaji, contains('$kod'), reason: 'kod $kod');
        // Yer tutucu metin ekrana çıkmamalı.
        expect(h.kullaniciMesaji.contains('yer tutucu'), isFalse,
            reason: 'kod $kod');
      }
    });

    test('tanınmayan kodda da genel bir cümle vardır', () {
      final h = ApiHatasi(418, 'yer tutucu', sunucuAcikladi: false);
      expect(h.kullaniciMesaji, 'Sunucu isteği tamamlayamadı. (HTTP 418)');
    });
  });

  group('zaman aşımı', () {
    // ⚠️ HİÇBİR İSTEKTE ZAMAN AŞIMI YOKTU: sunucu susarsa uygulama
    // süresiz bekliyordu. Kullanıcının "geç giriyor" bildirimi burada
    // karşılık buluyor — bekleyişin bir sonu olmalı.
    test('giriş isteği süresiz beklemez', () async {
      final api = Api(
        istemci: MockClient((_) async {
          // Sunucu hiç cevap vermiyor.
          await Future<void>.delayed(const Duration(minutes: 5));
          return http.Response('{}', 200);
        }),
      );
      await expectLater(
        api.giris('a@b.c', 'parola').timeout(const Duration(seconds: 2)),
        throwsA(isA<TimeoutException>()),
      );
    }, timeout: const Timeout(Duration(seconds: 10)));

    test('kimlik süresi sunucunun uyanmasına yeter', () {
      // Render ücretsiz katmanında uyanma ~1 dakika (docs/yayin.md).
      // Süre bunun altına düşerse kullanıcı hiç giremez.
      expect(Api.kimlikSuresi.inSeconds, greaterThanOrEqualTo(60));
    });

    test('yükleme süresi dosya sayısıyla büyür', () {
      // Sunucu her görüntü için model servisini ayrı çağırıyor ve
      // oradaki zaman aşımı 60 saniye (model_client.py → ZAMAN_ASIMI).
      final bir = Api.yuklemeSuresi(1);
      final uc = Api.yuklemeSuresi(3);
      expect(uc - bir, Api.yuklemeDosyaBasiSure * 2);
      expect(Api.yuklemeDosyaBasiSure.inSeconds, greaterThanOrEqualTo(60),
          reason: 'Sunucunun model zaman aşımından önce vazgeçmemeli');
    });
  });
}
