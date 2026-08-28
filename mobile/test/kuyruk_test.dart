import 'package:flutter_test/flutter_test.dart';
import 'package:rebuild_vision_mobil/kuyruk.dart';

/// Çevrimdışı kuyruğun veri sözleşmesi.
///
/// Şifreli depoya erişim gerçek cihaz gerektirir; burada kaydın kendi
/// dönüşümleri sınanır. Asıl korunan şey `yerel_kimlik` alanının
/// eşitleme gövdesinde mutlaka bulunması: o olmadan sunucu yinelenen
/// kaydı ayıramaz ve tek bir zayıf bağlantı ölçümleri ikiye katlar.
void main() {
  KuyrukKaydi ornek() => KuyrukKaydi(
        yerelKimlik: 'cihaz-test-0001',
        tespitId: 42,
        tur: 'agirlik',
        deger: 12.4,
        birim: 'ton',
        yontem: 'Saha kantar ölçümü',
        olusturma: DateTime.utc(2026, 8, 29, 10, 30),
      );

  test('kayıt JSON turundan geçince bozulmaz', () {
    final k = KuyrukKaydi.jsondan(ornek().jsona());
    expect(k.yerelKimlik, 'cihaz-test-0001');
    expect(k.tespitId, 42);
    expect(k.deger, 12.4);
    expect(k.birim, 'ton');
    expect(k.yontem, 'Saha kantar ölçümü');
    expect(k.olusturma, DateTime.utc(2026, 8, 29, 10, 30));
  });

  test('eşitleme gövdesi yerel_kimlik taşır', () {
    final g = ornek().esitlemeIcin();
    expect(g['yerel_kimlik'], 'cihaz-test-0001',
        reason: 'Sunucu yinelenen kaydı bu alana bakarak ayıklar');
    expect(g.containsKey('olusturma'), isFalse,
        reason: 'Sunucu şeması bu alanı beklemiyor');
  });

  test('eşitleme gövdesi sunucunun beklediği alanları içerir', () {
    expect(ornek().esitlemeIcin().keys.toSet(), {
      'yerel_kimlik', 'tespit_id', 'tur', 'deger', 'birim', 'yontem',
    });
  });
}
