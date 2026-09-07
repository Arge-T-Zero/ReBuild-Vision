import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../api.dart';
import '../duzen.dart';
import '../roller.dart';
import '../tema.dart';

/// Hesap ve rol ekranı — "benim ekranım nerede?" sorusunun cevabı.
///
/// ⚠️ BU EKRAN BİR ŞİKÂYETİN ÜZERİNE YAZILDI: "Belediye yetkilisi olarak
/// giriş yaptım ama bana belediyenin ekranı gelmedi, sadece saha
/// personeli ekranı var."
///
/// Şikâyet haklıydı ve kökü `roller.dart` başındaki yorumda anlatılıyor:
/// mobil uygulama rolü hiç okumuyordu. Ama düzeltmenin YÖNÜ bir tasarım
/// kararı gerektirdi ve karar şu: mobil uygulama SAHA uygulaması olarak
/// kalır. Web'deki altı ekranı (alanlar, harita, kuyruk, geçmiş, rapor,
/// rol onayı) telefona taşımak ayrı bir iştir ve bu turda yapılmadı.
///
/// Karar meşru; SESSİZLİK meşru değildi. Bir belediye yetkilisine saha
/// formunu gösterip hiçbir şey söylememek, ona yanlış bir ürün
/// göstermektir. Bu ekran o sessizliği kapatır:
///
///   - rolünüz ne (sunucudan gelen gerçek rol, uydurma değil),
///   - bu uygulamada NE YAPABİLİRSİNİZ (sunucudaki yetkiye göre),
///   - yapamadıklarınız NEREDE (web arayüzü, adresiyle birlikte).
class HesapEkrani extends StatelessWidget {
  final Kullanici kullanici;
  final RolTanimi tanim;

  /// Sahte model servisi çalışıyor mu? `null` = bilinmiyor.
  ///
  /// Kabuktaki kalıcı bant zaten görünür; buradaki satır onun yerine
  /// geçmez, hesap dökümünü tamamlar.
  final bool? sahteModel;

  const HesapEkrani({
    super.key,
    required this.kullanici,
    required this.tanim,
    this.sahteModel,
  });

  @override
  Widget build(BuildContext context) {
    final ekranlar = tanim.ekranlar;
    final mobildeYapabilecekleri = [
      if (tanim.goruntuYukleyebilir)
        'Enkaz alanına fotoğraf yükleyip ön sınıflandırmaya sokmak',
      if (tanim.olcumGirebilir)
        'Tespitlere ölçüm girmek (çevrimdışı da çalışır)',
    ];

    return OrtaSutun(
      cocuk: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _KimlikKarti(kullanici: kullanici, tanim: tanim),
          const SizedBox(height: 16),

          // 1) BU UYGULAMADA ne yapabilir.
          _Bolum(
            baslik: 'Bu uygulamada yapabilecekleriniz',
            cocuk: mobildeYapabilecekleri.isEmpty
                ? Text(
                    tanim == rolYok
                        ? 'Hesabınıza henüz rol atanmadı; bu uygulamada '
                            'hiçbir işlem yapamazsınız. Rol atamasını '
                            'yönetici yapar.'
                        : '${tanim.ad} rolünün bu uygulamada yapabileceği '
                            'bir işlem yok. Bu bir arıza değil: sunucu bu '
                            'role görüntü yükleme ve ölçüm girme yetkisi '
                            'vermiyor; rolünüzün işi izlemek ve karara '
                            'bağlamaktır.',
                    style: TextStyle(
                        color: Renk.metin3, fontSize: 13, height: 1.5),
                  )
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      for (final m in mobildeYapabilecekleri)
                        _Madde(metin: m, ikon: Icons.check, renk: Renk.olumlu),
                    ],
                  ),
          ),
          const SizedBox(height: 12),

          // 2) GERİ KALANI nerede.
          _Bolum(
            baslik: 'Rolünüzün diğer ekranları web arayüzünde',
            cocuk: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Bu mobil uygulama SAHA ÇALIŞMASI içindir: fotoğraf '
                  'yükleme ve ölçüm girişi. Harita, inceleme kuyruğu, '
                  'işlem geçmişi, rapor indirme ve rol onayı ekranları '
                  'web arayüzündedir.',
                  style: TextStyle(
                      color: Renk.metin3, fontSize: 13, height: 1.5),
                ),
                if (tanim.webEkranlari.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(
                    '${tanim.ad} olarak web arayüzünde şunları görürsünüz:',
                    style: TextStyle(
                        color: Renk.metin2,
                        fontSize: 12,
                        fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 6),
                  for (final e in tanim.webEkranlari)
                    _Madde(
                        metin: e,
                        ikon: Icons.open_in_new,
                        renk: Renk.bilgi),
                ],
                const SizedBox(height: 12),
                const _WebAdresi(),
              ],
            ),
          ),

          // 3) Sahte model servisi — biliniyorsa yazılır.
          //
          // Kabukta kalıcı bant var; burası hesap dökümünün parçası.
          // Bilinmiyorsa HİÇBİR ŞEY iddia edilmez: ne "gerçek" ne
          // "sahte" (ana talimat Bölüm 9.5).
          if (sahteModel != null) ...[
            const SizedBox(height: 12),
            _Bolum(
              baslik: 'Model servisi',
              cocuk: Text(
                sahteModel == true
                    ? 'SAHTE MODEL SERVİSİ etkin. Bu ortamda üretilen '
                        'sınıflar, güven skorları ve kutular uydurmadır; '
                        'gerçek bir modelin çıktısı değildir. Sahte olan '
                        'servistir, model değil: model eğitildi ve '
                        'ölçüldü.'
                    : 'Gerçek model servisi çalışıyor. Çıktılar yine de '
                        'ÖN TAHMİNDİR; uzman doğrulamadan miktar ve '
                        'yönlendirme hesabına girmez.',
                style: TextStyle(
                  color: sahteModel == true ? Renk.uyari : Renk.metin3,
                  fontSize: 13,
                  height: 1.5,
                ),
              ),
            ),
          ],

          const SizedBox(height: 20),
          Text(
            'Yetki denetimi sunucuda yapılır. Bu ekrandaki liste bir '
            'kolaylıktır; bir işlemi burada görmemeniz onu sunucunun da '
            'reddedeceği anlamına gelir, tersi geçerli değildir.',
            style: TextStyle(color: Renk.metin4, fontSize: 11, height: 1.5),
          ),
          const SizedBox(height: 8),
          Text(
            'Sunucu: ${Api.taban}',
            style: TextStyle(color: Renk.metin4, fontSize: 11, height: 1.5),
          ),
          const SizedBox(height: 4),
          Text(
            'Bu uygulama ${ekranlar.length} sekme gösteriyor; sekmeler '
            'rolünüzün sunucudaki yetkisine göre kuruldu.',
            style: TextStyle(color: Renk.metin4, fontSize: 11, height: 1.5),
          ),
        ],
      ),
    );
  }
}

class _KimlikKarti extends StatelessWidget {
  final Kullanici kullanici;
  final RolTanimi tanim;

  const _KimlikKarti({required this.kullanici, required this.tanim});

  @override
  Widget build(BuildContext context) {
    // Rolü olmayan hesap uyarı tonunda gösterilir: onun için bu bir
    // bilgi değil, engel.
    final rolsuz = kullanici.rol == null;
    final vurgu = rolsuz ? Renk.uyari : Renk.marka;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: vurgu.withValues(alpha: 0.15),
                    border: Border.all(color: vurgu.withValues(alpha: 0.4)),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    rolsuz ? Icons.hourglass_empty : Icons.badge_outlined,
                    color: vurgu,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        kullanici.ad,
                        style: TextStyle(
                          color: Renk.metin,
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        kullanici.eposta,
                        style: TextStyle(color: Renk.metin3, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: vurgu.withValues(alpha: 0.12),
                border: Border.all(color: vurgu.withValues(alpha: 0.35)),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                // Türkçe büyük harf: `toUpperCase()` "i" harfini
                // noktasız "I" yapar ve rol adı yanlış yazılır.
                turkceBuyuk(tanim.ad),
                style: TextStyle(
                  color: vurgu,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.6,
                ),
              ),
            ),
            const SizedBox(height: 10),
            Text(
              tanim.gorev,
              style:
                  TextStyle(color: Renk.metin2, fontSize: 13, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}

class _Bolum extends StatelessWidget {
  final String baslik;
  final Widget cocuk;

  const _Bolum({required this.baslik, required this.cocuk});

  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                baslik,
                style: TextStyle(
                  color: Renk.metin,
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 10),
              cocuk,
            ],
          ),
        ),
      );
}

class _Madde extends StatelessWidget {
  final String metin;
  final IconData ikon;
  final Color renk;

  const _Madde({required this.metin, required this.ikon, required this.renk});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 6),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(ikon, size: 15, color: renk),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                metin,
                style: TextStyle(
                    color: Renk.metin2, fontSize: 13, height: 1.45),
              ),
            ),
          ],
        ),
      );
}

/// Web arayüzünün adresi — kopyalanabilir.
///
/// Bağlantıyı tarayıcıda AÇMAK için `url_launcher` gerekirdi; yeni bir
/// bağımlılık eklemek yerine adres seçilebilir metin olarak yazılıyor ve
/// tek dokunuşla panoya kopyalanıyor. Sahada tabletle çalışan biri için
/// bu, adresi elle yazmaktan iyidir.
class _WebAdresi extends StatelessWidget {
  const _WebAdresi();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Renk.yuzey2,
        border: Border.all(color: Renk.kenar),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Icon(Icons.language, size: 16, color: Renk.metin3),
          const SizedBox(width: 10),
          Expanded(
            child: SelectableText(
              Api.webTaban,
              style: TextStyle(
                color: Renk.metin2,
                fontSize: 12.5,
                fontFeatures: const [FontFeature.tabularFigures()],
              ),
            ),
          ),
          IconButton(
            tooltip: 'Adresi kopyala',
            onPressed: () async {
              await Clipboard.setData(
                  const ClipboardData(text: Api.webTaban));
              if (!context.mounted) return;
              ScaffoldMessenger.of(context)
                ..hideCurrentSnackBar()
                ..showSnackBar(const SnackBar(
                  content: Text('Web arayüzünün adresi kopyalandı.'),
                ));
            },
            icon: Icon(Icons.copy_outlined, size: 18, color: Renk.metin3),
          ),
        ],
      ),
    );
  }
}
