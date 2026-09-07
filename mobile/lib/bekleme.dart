import 'dart:async';

import 'package:flutter/material.dart';

import 'tema.dart';

/// Uzun bekleyişlerde gösterilen ilerleme göstergesi ve DÜRÜST açıklama.
///
/// ⚠️ KULLANICI "GİRİŞLER YAVAŞ, GEÇ GİRİYOR" DİYE BİLDİRDİ.
///
/// Yavaşlığın büyük kısmı mobil tarafta değil: canlı ortam Render
/// ücretsiz katmanında çalışıyor ve 15 dakika hareketsizlikten sonra
/// servis uyutuluyor; sonraki ilk istek, konteyner ayağa kalkana kadar
/// bekliyor (docs/yayin.md). Bu bir sunucu kısıtıdır ve mobil uygulama
/// onu ortadan kaldıramaz.
///
/// Mobilin yapabileceği şey BEKLEYİŞİ AÇIKLAMAKTI ve yapmıyordu:
/// kullanıcı "Giriş yapılıyor…" yazan devre dışı bir düğmeye bakıyor,
/// hiçbir ilerleme göstergesi görmüyor, ne kadar süreceğini
/// bilmiyordu. Uygulamanın donduğunu düşünüp kapatması işten değildi.
///
/// Açıklama HEMEN çıkmaz. İlk saniyelerde çıkarsa sunucu uyanıkken de
/// (yaygın durum) "uyuyor" der ve yanlış bilgi verir; üstelik hızlı bir
/// girişte ekranda parlayıp kaybolan bir metin gürültüdür. Eşik geçince
/// belirir ve o andan sonra doğrudur: iki saniyede dönmeyen bir istek
/// için beklemenin uzayacağı gerçekten muhtemeldir.
class UyanmaNotu extends StatefulWidget {
  /// Açıklamanın ne kadar beklemeden sonra belireceği.
  final Duration esik;

  /// Beklenen en uzun süre — metinde yazılır, "ne kadar sürer"
  /// sorusuna somut cevap verir.
  final Duration enFazla;

  /// İlk satır: ne yapılıyor ("Giriş yapılıyor", "Fotoğraflar
  /// gönderiliyor" gibi).
  final String islem;

  const UyanmaNotu({
    super.key,
    required this.islem,
    this.esik = const Duration(seconds: 4),
    this.enFazla = const Duration(seconds: 90),
  });

  @override
  State<UyanmaNotu> createState() => _UyanmaDurumu();
}

class _UyanmaDurumu extends State<UyanmaNotu> {
  Timer? _sayac;
  bool _uzuyor = false;

  @override
  void initState() {
    super.initState();
    _sayac = Timer(widget.esik, () {
      if (mounted) setState(() => _uzuyor = true);
    });
  }

  @override
  void dispose() {
    _sayac?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Renk.yuzey2,
        border: Border.all(color: Renk.kenar),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Belirsiz ilerleme çubuğu: ne kadar kaldığını bilmiyoruz ve
          // bilmediğimiz bir yüzdeyi göstermek uydurma olurdu. Çubuğun
          // söylediği tek şey doğru: iş sürüyor.
          ClipRRect(
            borderRadius: BorderRadius.circular(3),
            child: LinearProgressIndicator(
              minHeight: 4,
              color: Renk.marka,
              backgroundColor: Renk.yuzey3,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            widget.islem,
            style: TextStyle(
              color: Renk.metin2,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
          if (_uzuyor) ...[
            const SizedBox(height: 6),
            Text(
              'Sunucu uyanıyor olabilir. Ücretsiz sunucu katmanında '
              'servis bir süre kullanılmayınca uykuya geçer; ilk istek '
              'bir dakikaya kadar sürebilir. '
              'En fazla ${widget.enFazla.inSeconds} saniye beklenecek, '
              'sonra hata bildirilecek.',
              style: TextStyle(
                color: Renk.metin3,
                fontSize: 12,
                height: 1.5,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
