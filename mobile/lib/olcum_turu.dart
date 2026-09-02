/// Ölçüm türünün adı, ekranda görünen birimi ve SUNUCUYA GİDEN birimi.
///
/// ⚠️ BU DOSYA BİR HATANIN ÜZERİNE AÇILDI.
///
/// Eşleme eskiden `olcum.dart` içinde, ekrana özel bir sabitin içinde
/// duruyordu ve gönderilecek birim şöyle türetiliyordu:
///
///     birim: _turler[_tur]!.$2 == 'm³' ? 'm3' : _turler[_tur]!.$2
///
/// Yani 'm³' düzeltiliyor, **'m²' düzeltilmiyordu.** Alan ölçümleri
/// sunucuya `m²` olarak gidiyor, sunucu `m2` beklediği için (bkz.
/// api/app/schemas.py `TURUN_BIRIMI`) reddediyordu.
///
/// Etkisi tek bir kaydın kaybolmasıyla sınırlı değildi. Eşitleme toplu
/// çalışır: kuyrukta bir alan ölçümü bulunduğu anda BÜTÜN PARTİ 422 ile
/// reddoluyor, o cihazdaki sağlam ölçümler de gönderilemiyordu. Uygulama
/// bunu ağ hatası sanıp "kayıtlar cihazda güvende, sonra denenecek"
/// diyordu — kuyruk bir daha hiç boşalmıyordu.
///
/// Eşleme buraya, ekrandan bağımsız ve SINANABİLİR bir yere taşındı;
/// `test/olcum_turu_test.dart` sunucunun sözleşmesini birebir doğrular.
/// Sunucu tarafında da bozuk bir satır artık partiyi düşürmüyor.
library;

class OlcumTuru {
  /// Kullanıcıya gösterilen ad.
  final String ad;

  /// Ekranda gösterilen birim — doğru tipografik simgeyle ('m²', 'm³').
  final String gorunenBirim;

  /// Sunucuya gönderilen birim. Ekrandakinden BİLEREK farklı:
  /// kullanıcı doğru simgeyi görür, sunucu beklediği metni alır.
  final String sunucuBirimi;

  const OlcumTuru(this.ad, this.gorunenBirim, this.sunucuBirimi);
}

/// Tür anahtarı → tanım. Anahtarlar sunucunun `OlcumTuru` enum'uyla aynı.
const olcumTurleri = <String, OlcumTuru>{
  'agirlik': OlcumTuru('Ağırlık', 'ton', 'ton'),
  'hacim': OlcumTuru('Hacim', 'm³', 'm3'),
  'alan': OlcumTuru('Görünür alan', 'm²', 'm2'),
};

/// Tek bir tespit için üst sınır — sunucudaki `OLCUM_UST_SINIR` ile aynı.
///
/// Sunucu bunu zaten reddediyordu, ama kayıt önce ÇEVRİMDIŞI KUYRUĞA
/// giriyor: red saatler sonra, sahadan dönülmüşken geliyordu. İstemcide
/// kontrol edilmesi, yazım hatasının kuyruğa hiç girmemesini sağlar.
/// Web arayüzünde (MiktarKarti.tsx) aynı kontrol zaten vardı.
const olcumUstSiniri = 100000.0;

/// Sunucu biriminden EKRANDA görünen birime çevirir.
///
/// ⚠️ KUYRUK LİSTESİ SUNUCU BİRİMİNİ BASIYORDU: kullanıcı formda "m³"
/// seçip gönderdikten sonra kuyrukta aynı kaydı "m2" olarak görüyordu.
/// Aynı ölçüm, aynı ekranda iki farklı birimle görünüyordu.
///
/// Bilinmeyen bir birim gelirse OLDUĞU GİBİ gösterilir — uydurulmaz.
String gorunenBirimi(String sunucuBirimi) {
  for (final t in olcumTurleri.values) {
    if (t.sunucuBirimi == sunucuBirimi) return t.gorunenBirim;
  }
  return sunucuBirimi;
}
