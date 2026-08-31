import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Çevrimdışı ölçüm kuyruğu — **cihazda şifreli** saklanır.
///
/// Rapor Bölüm 12 (risk tablosu):
///
///     "Mobil kayıtların cihazda şifreli olarak geçici biçimde saklanması
///      ve bağlantı sağlandığında eşitlenmesi."
///
/// Bu, raporda verilmiş somut bir taahhüttür; düz JSON dosyası
/// kullanılmaz.
///
/// ŞİFRELEME NASIL SAĞLANIYOR
/// `flutter_secure_storage` platformun kendi güvenli deposunu kullanır:
///
/// - **Android:** veri AES/GCM/NoPadding ile şifrelenir; şifreleme
///   anahtarı Android Keystore içinde RSA-OAEP (SHA-256 + MGF1) ile
///   sarmalanır. Bu, paketin 11. sürümündeki varsayılan davranıştır.
/// - **iOS:** Keychain; `first_unlock` erişilebilirliğiyle, yani cihaz
///   açıldıktan sonra okunabilir, kilitliyken okunamaz.
///
/// Anahtar hiçbir zaman uygulamanın içinde tutulmaz; işletim sistemi
/// yönetir ve uygulama kaldırılınca anahtar da gider.
///
/// SINIR — dürüst beyan
/// Burada yalnızca **ölçüm kayıtları** şifreli tutulur. Fotoğraflar
/// cihazın normal dosya sisteminde durur; güvenli depo büyük ikili
/// dosyalar için tasarlanmamıştır. Fotoğrafların şifrelenmesi ayrı bir
/// çözüm gerektirir ve bu sürümde yapılmamıştır
/// (`docs/veri-politikasi.md`).
class Kuyruk {
  static const _anahtar = 'rebuild_vision_olcum_kuyrugu';

  final FlutterSecureStorage _depo;

  Kuyruk([FlutterSecureStorage? depo])
      : _depo = depo ??
            const FlutterSecureStorage(
              // Varsayılan Android seçenekleri zaten AES-GCM + Keystore'da
              // RSA-OAEP anahtar sarmalamadır; ayrıca ayar gerekmez.
              aOptions: AndroidOptions(),
              iOptions: IOSOptions(
                accessibility: KeychainAccessibility.first_unlock,
              ),
            );

  Future<List<KuyrukKaydi>> hepsi() async {
    final ham = await _depo.read(key: _anahtar);
    if (ham == null || ham.isEmpty) return [];
    try {
      final liste = jsonDecode(ham) as List<dynamic>;
      return liste
          .map((e) => KuyrukKaydi.jsondan(e as Map<String, dynamic>))
          .toList();
    } on FormatException {
      // Bozuk kayıt kuyruğu tamamen kilitlemesin: temizlenip devam edilir.
      // Veri kaybı olur ama uygulama kullanılamaz hale gelmez.
      await _depo.delete(key: _anahtar);
      return [];
    }
  }

  Future<void> ekle(KuyrukKaydi kayit) async {
    final liste = await hepsi()..add(kayit);
    await _yaz(liste);
  }

  /// Sunucunun reddettiği kayıtlara GEREKÇEYİ yazar.
  ///
  /// Reddedilen kayıt kuyrukta kalır — silinmesi kullanıcının kararıdır,
  /// veri kaybı sessizce yapılmaz. Ama neden reddedildiği kayıtla
  /// birlikte saklanmalıdır: eşitleme uygulamayı kapatıp açtıktan sonra
  /// da denenir ve kullanıcı o anda bir bildirim görmez. Gerekçe kaydın
  /// üstünde durursa, kullanıcı Ölçüm ekranını açtığında sorunu görür.
  Future<void> gerekceleriYaz(Map<String, String> gerekceler) async {
    if (gerekceler.isEmpty) return;
    final liste = await hepsi();
    for (var i = 0; i < liste.length; i++) {
      final g = gerekceler[liste[i].yerelKimlik];
      if (g != null) liste[i] = liste[i].notlu(g);
    }
    await _yaz(liste);
  }

  /// Tek bir kaydı kuyruktan siler — kullanıcı isteğiyle.
  ///
  /// Sunucunun kalıcı olarak reddettiği bir kaydın (yanlış birim, hatalı
  /// değer) kuyrukta sonsuza kadar kalması anlamsızdır; kullanıcı onu
  /// atıp doğrusunu girebilmelidir. Silme yalnızca elle yapılır.
  Future<void> tekSil(String yerelKimlik) => sil({yerelKimlik});

  /// Eşitlenen kayıtları kuyruktan siler.
  ///
  /// Sunucu "yazıldı" ya da "yinelenen" dediyse kayıt kuyruktan çıkar;
  /// yalnızca "hata" alanlar kalır. Yinelenen de silinir çünkü sunucuda
  /// zaten vardır.
  Future<void> sil(Set<String> yerelKimlikler) async {
    final kalan = (await hepsi())
        .where((k) => !yerelKimlikler.contains(k.yerelKimlik))
        .toList();
    await _yaz(kalan);
  }

  Future<void> temizle() => _depo.delete(key: _anahtar);

  Future<void> _yaz(List<KuyrukKaydi> liste) async {
    await _depo.write(
      key: _anahtar,
      value: jsonEncode(liste.map((k) => k.jsona()).toList()),
    );
  }
}

/// Kuyrukta bekleyen tek ölçüm.
class KuyrukKaydi {
  /// Cihazda üretilen benzersiz kimlik.
  ///
  /// Ağ koptuğunda istemci isteği tekrarlar ama sonucu bilemez. Sunucu bu
  /// kimliğe bakıp aynı ölçümü iki kez yazmaz. Bu koruma olmadan tek bir
  /// zayıf bağlantı ölçümleri ikiye katlar ve miktar hesabını bozardı.
  final String yerelKimlik;

  final int tespitId;
  final String tur; // alan | hacim | agirlik
  final double deger;
  final String birim;
  final String yontem;
  final DateTime olusturma;

  /// Sunucu bu kaydı reddettiyse gerekçesi; aksi hâlde `null`.
  ///
  /// Kuyrukta bekleyen kayıt ile REDDEDİLEN kayıt aynı şey değildir:
  /// birincisi bağlantı bekler, ikincisi kullanıcının müdahalesini.
  /// Ayrım ekranda görünmeden kullanıcı hangisinin hangisi olduğunu
  /// bilemez ve reddedilen kayıt sonsuza kadar kuyrukta kalır.
  final String? sunucuNotu;

  KuyrukKaydi({
    required this.yerelKimlik,
    required this.tespitId,
    required this.tur,
    required this.deger,
    required this.birim,
    required this.yontem,
    required this.olusturma,
    this.sunucuNotu,
  });

  KuyrukKaydi notlu(String not) => KuyrukKaydi(
        yerelKimlik: yerelKimlik,
        tespitId: tespitId,
        tur: tur,
        deger: deger,
        birim: birim,
        yontem: yontem,
        olusturma: olusturma,
        sunucuNotu: not,
      );

  Map<String, dynamic> jsona() => {
        'yerel_kimlik': yerelKimlik,
        'tespit_id': tespitId,
        'tur': tur,
        'deger': deger,
        'birim': birim,
        'yontem': yontem,
        'olusturma': olusturma.toIso8601String(),
        if (sunucuNotu != null) 'sunucu_notu': sunucuNotu,
      };

  factory KuyrukKaydi.jsondan(Map<String, dynamic> j) => KuyrukKaydi(
        yerelKimlik: j['yerel_kimlik'] as String,
        tespitId: j['tespit_id'] as int,
        tur: j['tur'] as String,
        deger: (j['deger'] as num).toDouble(),
        birim: j['birim'] as String,
        yontem: j['yontem'] as String,
        olusturma: DateTime.parse(j['olusturma'] as String),
        sunucuNotu: j['sunucu_notu'] as String?,
      );

  /// Sunucunun `/esitleme/olcum` uç noktasının beklediği biçim.
  Map<String, dynamic> esitlemeIcin() => {
        'yerel_kimlik': yerelKimlik,
        'tespit_id': tespitId,
        'tur': tur,
        'deger': deger,
        'birim': birim,
        'yontem': yontem,
      };
}
