import 'package:flutter/material.dart';

/// Ekran genişliğine göre yerleşim kuralları.
///
/// ⚠️ BU DOSYA BİR EKSİĞİN ÜZERİNE AÇILDI. Uygulama yalnızca telefon
/// için yazılmıştı: `yukle.dart` ve `olcum.dart` düz `ListView` idi,
/// hiçbir genişlik sınırı yoktu. Ölçülen sonuç, 1194x834 bir tablette:
///
///   - "Alan seçin…" açılır listesi **1160 px** genişliğinde
///   - İçerik, 834 px yüksekliğin yalnızca üst ~280 px'ini kaplıyor
///   - Alt gezinme iki sekmeyi 1194 px'e yayıyor
///   - Kapsam uyarısı tek satır hâlinde sol kenarda asılı kalıyor
///
/// Sorun "çirkin durması" değil: bir form alanının 1160 px olması onu
/// kullanılmaz yapar (göz, etiketten değere kadar ekranın yarısını kat
/// eder) ve uzun metin satırı okunmaz — rahat satır uzunluğu 60-75
/// karakterdir, orada 200 karakteri geçiyordu.
///
/// Sahada tablet gerçek bir kullanım: saha ekibi fotoğrafı tablette
/// çekip ölçümü orada giriyor. Telefon düzeninin "esneyerek" tablete
/// yayılması bir tasarım değil, tasarımın yokluğudur.
class Duzen {
  Duzen._();

  /// Geniş ekran eşiği (Material 3 "medium" başlangıcı).
  ///
  /// 600 dp'nin altı telefon, üstü tablet sayılır. Bu eşik hem yan
  /// gezinme rayına geçiş hem de içerik sınırı için kullanılır.
  static const genisEsik = 600.0;

  /// İçeriğin alabileceği en fazla genişlik.
  ///
  /// Form ağırlıklı bir ekran için 560 dp, rahat satır uzunluğunu
  /// (yaklaşık 70 karakter) 13-14 px gövde metniyle karşılar. Giriş
  /// ekranı 420 kullanıyor çünkü orada yalnızca iki alan var.
  static const icerikGenisligi = 560.0;

  static bool genisMi(BuildContext c) =>
      MediaQuery.sizeOf(c).width >= genisEsik;
}

/// İçeriği ortalayıp genişliğini sınırlayan sarmalayıcı.
///
/// Dar ekranda hiçbir şey yapmaz — telefon düzeni olduğu gibi kalır.
class OrtaSutun extends StatelessWidget {
  final Widget cocuk;
  final double enFazla;

  const OrtaSutun({
    super.key,
    required this.cocuk,
    this.enFazla = Duzen.icerikGenisligi,
  });

  @override
  Widget build(BuildContext context) => Align(
        alignment: Alignment.topCenter,
        child: ConstrainedBox(
          constraints: BoxConstraints(maxWidth: enFazla),
          child: cocuk,
        ),
      );
}
