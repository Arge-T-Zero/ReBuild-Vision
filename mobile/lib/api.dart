import 'dart:convert';
import 'dart:io';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import 'kuyruk.dart';

/// Sunucu istemcisi.
///
/// Oturum jetonu güvenli depoda tutulur — `SharedPreferences` düz metindir,
/// jeton orada durmamalıdır.
/// Güven skorunu ekrana yazar — **yuvarlamadan**, Türkçe biçimde.
///
/// ⚠️ MOBİL BU SAYIYI YUVARLIYORDU: `toStringAsFixed(1)` ile 0,8734567
/// telefonda **"%87.3"** görünüyordu; aynı kayıt web'de "%87,3457".
/// Üstelik ondalık ayracı **nokta**ydı. Kodun hemen üstündeki yorum
/// "Güven skoru yuvarlanmaz" diyordu — yorum kodu yalanlıyordu.
///
/// Ana talimat Bölüm 9.2: "Güven skoru gizlenmez. Sayı olarak gösterilir,
/// YUVARLANMAZ." Web'deki `yuzdeMetni()` ile aynı davranış: en çok dört
/// ondalık, gereksiz sıfır yok, ayraç virgül.
String guvenYuzdesi(double skor) {
  // Kayan nokta artığını temizle: 0.78 * 100 = 78.00000000000001
  final y = (skor * 100 * 1e6).round() / 1e6;
  var metin = y.toStringAsFixed(4);
  if (metin.contains('.')) {
    metin = metin.replaceAll(RegExp(r'0+$'), '').replaceAll(RegExp(r'\.$'), '');
  }
  return metin.replaceAll('.', ',');
}

/// Sunucunun kabul ettiği görüntü türleri.
///
/// `api/app/routers/goruntuler.py` → `IZINLI_TURLER` ile **birebir aynı**
/// olmak zorundadır. Biri değişirse ikisi birden değişmelidir;
/// `test/goruntu_turu_test.dart` ayrışmayı yakalar.
const izinliGoruntuTurleri = {'image/jpeg', 'image/png', 'image/webp'};

/// Dosya adından MIME türü çıkarır.
///
/// ⚠️ BU EKSİKLİK SAHA UYGULAMASININ ANA İŞLEVİNİ ÇALIŞMAZ HÂLE
/// GETİRİYORDU. `MultipartFile.fromPath` çağrısına `contentType`
/// verilmediğinde `http` paketi varsayılan olarak
/// `application/octet-stream` gönderir (http 1.6.0,
/// `multipart_file.dart:54`). Sunucu ise yalnızca `image/*` üçlüsünü
/// kabul ediyor ve ilk dosyada **bütün partiyi** 415 ile düşürüyor
/// (`goruntuler.py:62` — döngü içinde `raise`).
///
/// Yani telefondan yüklenen her fotoğraf reddediliyordu ve kullanıcı
/// ekranda ham MIME tipini görüyordu. Web arayüzü tarayıcı türü kendisi
/// belirlediği için etkilenmiyordu; hata yalnızca gerçek cihazda ortaya
/// çıkıyordu.
///
/// Bilinmeyen uzantıda `null` DÖNMEZ — `image/jpeg` varsayılır, çünkü
/// `image_picker` kameradan gelen dosyaya her zaman `.jpg` verir ve
/// sessizce `octet-stream`'e düşmek tam da bu arızayı geri getirirdi.
MediaType goruntuTuru(String yol) {
  final uzanti = yol.split('.').last.toLowerCase();
  return switch (uzanti) {
    'png' => MediaType('image', 'png'),
    'webp' => MediaType('image', 'webp'),
    _ => MediaType('image', 'jpeg'),
  };
}


class Api {
  /// Sunucu adresi. Derleme sırasında değiştirilebilir:
  ///   flutter run --dart-define=API_TABAN=https://...
  static const taban = String.fromEnvironment(
    'API_TABAN',
    defaultValue: 'https://rebuild-vision-api.onrender.com',
  );

  static const _jetonAnahtari = 'rebuild_vision_jeton';
  static const _temaAnahtari = 'rebuild_vision_tema';

  final http.Client _istemci;
  final FlutterSecureStorage _depo;

  Api({http.Client? istemci, FlutterSecureStorage? depo})
      : _istemci = istemci ?? http.Client(),
        _depo = depo ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(),
              iOptions: IOSOptions(
                accessibility: KeychainAccessibility.first_unlock,
              ),
            );

  Future<String?> jeton() => _depo.read(key: _jetonAnahtari);
  Future<void> jetonSil() => _depo.delete(key: _jetonAnahtari);

  /// Tema tercihi. Seçim YAPILMADIYSA açık tema (`false`) döner.
  ///
  /// Depoya yalnızca kullanıcı düğmeye bastığında yazılır. Web tarafında
  /// tam bu ayrım atlanmıştı: uygulama her açılışta seçilmemiş varsayılanı
  /// da diske yazıyordu, bu yüzden varsayılan sonradan değiştirildiğinde
  /// eski kullanıcılar hâlâ koyu temayla açılıyordu. Aynı hataya burada
  /// düşülmemesi için okuma/yazma bilinçli olarak ayrı.
  Future<bool> temaKoyuMu() async {
    try {
      return (await _depo.read(key: _temaAnahtari)) == 'koyu';
    } catch (_) {
      // Güvenli depo okunamıyorsa (nadir; cihaz kilidi, bozuk anahtar)
      // uygulama açılmalıdır — tema bir tercihtir, engel değil.
      return false;
    }
  }

  Future<void> temaKaydet({required bool koyu}) async {
    try {
      await _depo.write(key: _temaAnahtari, value: koyu ? 'koyu' : 'acik');
    } catch (_) {
      // Yazılamazsa tercih o oturum için geçerli kalır; uygulama çökmez.
    }
  }

  Future<Map<String, String>> _basliklar({bool govdeVar = false}) async {
    final j = await jeton();
    return {
      if (j != null) 'Authorization': 'Bearer $j',
      if (govdeVar) 'Content-Type': 'application/json',
    };
  }

  Never _hata(http.Response y) {
    String mesaj = 'İstek başarısız (${y.statusCode})';
    try {
      final g = jsonDecode(utf8.decode(y.bodyBytes));
      if (g is Map && g['detail'] is String) mesaj = g['detail'] as String;
    } catch (_) {/* gövde JSON değilse varsayılan mesaj kalır */}
    throw ApiHatasi(y.statusCode, mesaj);
  }

  dynamic _coz(http.Response y) {
    if (y.statusCode < 200 || y.statusCode >= 300) _hata(y);
    return jsonDecode(utf8.decode(y.bodyBytes));
  }

  // --- Kimlik ---------------------------------------------------------

  Future<Kullanici> giris(String eposta, String parola) async {
    final y = await _istemci.post(
      Uri.parse('$taban/auth/giris'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'eposta': eposta, 'parola': parola}),
    );
    final d = _coz(y) as Map<String, dynamic>;
    await _depo.write(key: _jetonAnahtari, value: d['jeton'] as String);
    return Kullanici.jsondan(d['kullanici'] as Map<String, dynamic>);
  }

  Future<Kullanici?> ben() async {
    if (await jeton() == null) return null;
    final y = await _istemci.get(
      Uri.parse('$taban/auth/ben'),
      headers: await _basliklar(),
    );
    if (y.statusCode == 401 || y.statusCode == 403) {
      await jetonSil();
      return null;
    }
    return Kullanici.jsondan(_coz(y) as Map<String, dynamic>);
  }

  // --- Saha ve görüntü -------------------------------------------------

  Future<List<EnkazAlani>> alanlar() async {
    final y = await _istemci.get(
      Uri.parse('$taban/enkaz-alani'),
      headers: await _basliklar(),
    );
    return (_coz(y) as List)
        .map((e) => EnkazAlani.jsondan(e as Map<String, dynamic>))
        .toList();
  }

  /// Görüntü yükler. Konum verilirse sorgu dizesine eklenir.
  Future<Map<String, dynamic>> goruntuYukle(
    int alanId,
    List<File> dosyalar, {
    double? enlem,
    double? boylam,
  }) async {
    final adres = Uri.parse('$taban/goruntu/yukle/$alanId').replace(
      queryParameters: {
        if (enlem != null) 'enlem': '$enlem',
        if (boylam != null) 'boylam': '$boylam',
      },
    );
    final istek = http.MultipartRequest('POST', adres)
      ..headers.addAll(await _basliklar());
    for (final d in dosyalar) {
      istek.files.add(await http.MultipartFile.fromPath(
        'dosyalar',
        d.path,
        contentType: goruntuTuru(d.path),
      ));
    }
    final y = await http.Response.fromStream(await istek.send());
    return _coz(y) as Map<String, dynamic>;
  }

  Future<List<Tespit>> alanTespitleri(int alanId) async {
    final y = await _istemci.get(
      Uri.parse('$taban/goruntu/alan/$alanId'),
      headers: await _basliklar(),
    );
    return (_coz(y) as List)
        .expand((g) => (g['tespitler'] as List))
        .map((e) => Tespit.jsondan(e as Map<String, dynamic>))
        .toList();
  }

  // --- Çevrimdışı eşitleme ---------------------------------------------

  /// Kuyruğu sunucuya gönderir ve satır sonuçlarını döner.
  ///
  /// Kısmi başarı normaldir: yirmi kayıttan üçü geçersizse diğerleri
  /// yazılır. Çağıran taraf yalnızca `hata` olanları kuyrukta tutmalıdır.
  Future<EsitlemeSonucu> esitle(List<KuyrukKaydi> kayitlar) async {
    final y = await _istemci.post(
      Uri.parse('$taban/esitleme/olcum'),
      headers: await _basliklar(govdeVar: true),
      body: jsonEncode({
        'kayitlar': kayitlar.map((k) => k.esitlemeIcin()).toList(),
      }),
    );
    return EsitlemeSonucu.jsondan(_coz(y) as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> siniflar() async {
    final y = await _istemci.get(Uri.parse('$taban/sistem/siniflar'));
    return _coz(y) as Map<String, dynamic>;
  }

  /// Model servisinin SAHTE olup olmadığını sorar.
  ///
  /// ⚠️ MOBİL BU UÇ NOKTAYI HİÇ ÇAĞIRMIYORDU. Ana talimat Bölüm 9.5 ve
  /// `README.md` sahte servis çalışırken **kalıcı** bir rozet istiyor;
  /// web arayüzünde üst çubukta her ekranda duruyordu, mobilde ise
  /// yalnızca bir yükleme yapıldıktan sonra sonuç kartında beliriyordu.
  /// Yani jüri telefonu eline alıp Ölçüm sekmesine baksa sahtelik
  /// hakkında tek bir işaret görmüyordu.
  ///
  /// Kimlik gerektirmez; giriş yapılmadan da çağrılabilir.
  Future<bool> sahteModelMi() async {
    final y = await _istemci.get(Uri.parse('$taban/sistem/durum'));
    final d = _coz(y) as Map<String, dynamic>;
    final servis = d['model_servisi'] as Map<String, dynamic>?;
    return servis?['sahte'] == true;
  }
}

class ApiHatasi implements Exception {
  final int durum;
  final String mesaj;
  ApiHatasi(this.durum, this.mesaj);
  @override
  String toString() => mesaj;
}

// --- Veri sınıfları ---------------------------------------------------

class Kullanici {
  final int id;
  final String ad;
  final String eposta;
  final String? rol;

  Kullanici({
    required this.id,
    required this.ad,
    required this.eposta,
    this.rol,
  });

  factory Kullanici.jsondan(Map<String, dynamic> j) => Kullanici(
        id: j['id'] as int,
        ad: j['ad'] as String,
        eposta: j['eposta'] as String,
        rol: j['rol'] as String?,
      );
}

class EnkazAlani {
  final int id;
  final String ad;
  final int goruntuSayisi;
  final int tespitSayisi;
  final int incelemeBekleyen;

  EnkazAlani({
    required this.id,
    required this.ad,
    required this.goruntuSayisi,
    required this.tespitSayisi,
    required this.incelemeBekleyen,
  });

  factory EnkazAlani.jsondan(Map<String, dynamic> j) => EnkazAlani(
        id: j['id'] as int,
        ad: j['ad'] as String,
        goruntuSayisi: (j['goruntu_sayisi'] ?? 0) as int,
        tespitSayisi: (j['tespit_sayisi'] ?? 0) as int,
        incelemeBekleyen: (j['inceleme_bekleyen'] ?? 0) as int,
      );
}

class Tespit {
  final int id;
  final String sinif;
  final String? duzeltilenSinif;
  final double guvenSkoru;
  final String dogrulamaDurumu;
  final bool incelemeGerekli;

  /// Her model çıktısı "ön tahmin"dir, istisnasız (ana talimat Bölüm 1.4).
  final String etiket;

  Tespit({
    required this.id,
    required this.sinif,
    this.duzeltilenSinif,
    required this.guvenSkoru,
    required this.dogrulamaDurumu,
    required this.incelemeGerekli,
    required this.etiket,
  });

  /// Uzman düzelttiyse geçerli sınıf odur — insan kararı modeli geçersiz kılar.
  String get gecerliSinif => duzeltilenSinif ?? sinif;

  factory Tespit.jsondan(Map<String, dynamic> j) => Tespit(
        id: j['id'] as int,
        sinif: j['sinif'] as String,
        duzeltilenSinif: j['duzeltilen_sinif'] as String?,
        guvenSkoru: (j['guven_skoru'] as num).toDouble(),
        dogrulamaDurumu: j['dogrulama_durumu'] as String,
        incelemeGerekli: (j['inceleme_gerekli'] ?? false) as bool,
        etiket: (j['etiket'] ?? 'ön tahmin') as String,
      );
}

class EsitlemeSonucu {
  final int yazilan;
  final int yinelenen;
  final int hatali;

  /// Kuyruktan silinecek kayıtlar: yazılan + yinelenen.
  /// Yinelenen de silinir çünkü sunucuda zaten vardır.
  final Set<String> silinecek;

  /// Reddedilen kayıtların GEREKÇESİ — `yerel_kimlik` → açıklama.
  ///
  /// ⚠️ SUNUCU BUNU DÖNÜYORDU VE UYGULAMA ATIYORDU. Yalnızca sayı
  /// okunuyor, kullanıcıya "3 kayıt kuyrukta kaldı" deniyordu. Neden
  /// kaldığı — birim yanlış mı, tespit silinmiş mi, değer mi olağandışı —
  /// hiçbir yerde yazmıyordu. Saha personeli, düzeltebileceği bir kaydı
  /// düzeltemeden bırakıyor; kayıt her eşitlemede yeniden reddediliyordu.
  final Map<String, String> gerekceler;

  EsitlemeSonucu({
    required this.yazilan,
    required this.yinelenen,
    required this.hatali,
    required this.silinecek,
    this.gerekceler = const {},
  });

  factory EsitlemeSonucu.jsondan(Map<String, dynamic> j) {
    final satirlar = (j['satirlar'] as List).cast<Map<String, dynamic>>();
    return EsitlemeSonucu(
      yazilan: j['yazilan'] as int,
      yinelenen: j['yinelenen'] as int,
      hatali: j['hatali'] as int,
      silinecek: satirlar
          .where((s) => s['durum'] == 'yazildi' || s['durum'] == 'yinelenen')
          .map((s) => s['yerel_kimlik'] as String)
          .toSet(),
      gerekceler: {
        for (final s in satirlar)
          if (s['durum'] == 'hata' && s['aciklama'] != null)
            s['yerel_kimlik'] as String: s['aciklama'] as String,
      },
    );
  }
}
