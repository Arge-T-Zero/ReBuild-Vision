import 'dart:async';
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

  /// Web arayüzünün adresi (docs/yayin.md).
  ///
  /// Mobil uygulama saha akışını taşır; harita, inceleme kuyruğu, işlem
  /// geçmişi ve rapor ekranları webdedir. Hesap ekranı kullanıcıya bu
  /// adresi GÖSTERİR — "web arayüzünü kullanın" deyip nereye gideceğini
  /// söylememek yarım bir yönlendirmedir.
  static const webTaban = String.fromEnvironment(
    'WEB_TABAN',
    defaultValue: 'https://re-build-vision.vercel.app',
  );

  /// Zaman aşımı süreleri.
  ///
  /// ⚠️ HİÇBİR İSTEKTE ZAMAN AŞIMI YOKTU. `http.Client` kendiliğinden
  /// bir istek zaman aşımı uygulamaz (`HttpClient.connectionTimeout`
  /// varsayılan `null`); yani sunucu cevap vermediğinde uygulama
  /// süresiz bekliyor, kullanıcı da "Giriş yapılıyor…" yazısına
  /// bakıyordu. Kullanıcının bildirdiği "girişler yavaş" şikâyetinin
  /// arayüz tarafındaki payı budur: bekleyişin bir sonu ve açıklaması
  /// yoktu.
  ///
  /// Süreler CANLI ORTAMIN ÖLÇÜLEN DAVRANIŞINA göre seçildi: Render
  /// ücretsiz katmanı 15 dakika hareketsizlikten sonra servisi uyutur
  /// ve ilk istek konteyner ayağa kalkana kadar bekler (docs/yayin.md
  /// → "Uyanma"). Bu yüzden kimlik istekleri cömert, sıradan istekler
  /// dar tutuldu — kısa bir zaman aşımı sunucuyu uyandırmadan vazgeçer
  /// ve kullanıcı hiç giremez.
  static const kimlikSuresi = Duration(seconds: 90);

  /// Liste/okuma istekleri. Sunucu zaten uyanıksa bu kadarı fazlasıyla
  /// yeter; uyanık değilse kimlik isteği onu zaten uyandırmış olur.
  static const istekSuresi = Duration(seconds: 45);

  /// Yükleme için TABAN süre — üstüne dosya başına pay eklenir.
  ///
  /// Sunucu her görüntü için model servisini çağırır ve oradaki zaman
  /// aşımı 60 saniyedir (`api/app/services/model_client.py` →
  /// `ZAMAN_ASIMI`). Mobil tarafın bundan önce vazgeçmesi, sunucunun
  /// yazdığı kaydı kullanıcının hiç görmemesi demektir.
  static const yuklemeTabanSuresi = Duration(seconds: 90);
  static const yuklemeDosyaBasiSure = Duration(seconds: 60);

  /// Bir yükleme isteği için toplam süre.
  static Duration yuklemeSuresi(int dosyaSayisi) =>
      yuklemeTabanSuresi + yuklemeDosyaBasiSure * dosyaSayisi;

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

  /// Sunucu hatasını okunur bir istisnaya çevirir.
  ///
  /// ⚠️ SUNUCU HER ZAMAN JSON DÖNMÜYOR. FastAPI, yakalanmamış bir
  /// istisnada Starlette'in düz metin `Internal Server Error` gövdesini
  /// döner — JSON değil. Eski kod bu durumda `jsonDecode` hatasını yutup
  /// mesaj olarak "İstek başarısız (500)" bırakıyordu; yükleme ekranı da
  /// onu "Yükleme başarısız (500): İstek başarısız (500)" diye
  /// yazıyordu. Kullanıcının gördüğü tek bilgi iki kez tekrarlanmış bir
  /// sayıydı.
  ///
  /// Artık sunucunun AÇIKLAMA YAPIP YAPMADIĞI da taşınıyor
  /// (`sunucuAcikladi`): açıkladıysa onun Türkçe gerekçesi gösterilir,
  /// açıklamadıysa duruma göre anlamlı bir cümle yazılır. Ham kod her
  /// iki hâlde de metnin içinde kalır — gizlenmez.
  Never _hata(http.Response y) {
    String? detay;
    try {
      final g = jsonDecode(utf8.decode(y.bodyBytes));
      if (g is Map && g['detail'] is String) detay = g['detail'] as String;
    } catch (_) {/* gövde JSON değil — düz metin ya da boş */}
    throw ApiHatasi(
      y.statusCode,
      detay ?? 'İstek başarısız (${y.statusCode})',
      sunucuAcikladi: detay != null,
    );
  }

  dynamic _coz(http.Response y) {
    if (y.statusCode < 200 || y.statusCode >= 300) _hata(y);
    return jsonDecode(utf8.decode(y.bodyBytes));
  }

  // --- Kimlik ---------------------------------------------------------

  Future<Kullanici> giris(String eposta, String parola) async {
    final y = await _istemci
        .post(
          Uri.parse('$taban/auth/giris'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'eposta': eposta, 'parola': parola}),
        )
        .timeout(kimlikSuresi);
    final d = _coz(y) as Map<String, dynamic>;
    await _depo.write(key: _jetonAnahtari, value: d['jeton'] as String);
    return Kullanici.jsondan(d['kullanici'] as Map<String, dynamic>);
  }

  Future<Kullanici?> ben() async {
    if (await jeton() == null) return null;
    final y = await _istemci
        .get(
          Uri.parse('$taban/auth/ben'),
          headers: await _basliklar(),
        )
        // Uygulama açılışındaki tek istek budur ve sunucu uykuda
        // olabilir: kimlik süresi (90 sn) kullanılır. Kısa tutulursa
        // oturumu açık olan kullanıcı her sabah giriş ekranına düşer.
        .timeout(kimlikSuresi);
    if (y.statusCode == 401 || y.statusCode == 403) {
      await jetonSil();
      return null;
    }
    return Kullanici.jsondan(_coz(y) as Map<String, dynamic>);
  }

  // --- Saha ve görüntü -------------------------------------------------

  Future<List<EnkazAlani>> alanlar() async {
    final y = await _istemci
        .get(
          Uri.parse('$taban/enkaz-alani'),
          headers: await _basliklar(),
        )
        .timeout(istekSuresi);
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
    // Zaman aşımı dosya sayısına göre uzar: sunucu her görüntü için
    // model servisini ayrı ayrı çağırıyor.
    final y = await http.Response.fromStream(
      await istek.send().timeout(yuklemeSuresi(dosyalar.length)),
    );
    return _coz(y) as Map<String, dynamic>;
  }

  Future<List<Tespit>> alanTespitleri(int alanId) async {
    final y = await _istemci
        .get(
          Uri.parse('$taban/goruntu/alan/$alanId'),
          headers: await _basliklar(),
        )
        .timeout(istekSuresi);
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
    final y = await _istemci
        .post(
          Uri.parse('$taban/esitleme/olcum'),
          headers: await _basliklar(govdeVar: true),
          body: jsonEncode({
            'kayitlar': kayitlar.map((k) => k.esitlemeIcin()).toList(),
          }),
        )
        .timeout(istekSuresi);
    return EsitlemeSonucu.jsondan(_coz(y) as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> siniflar() async {
    final y = await _istemci
        .get(Uri.parse('$taban/sistem/siniflar'))
        .timeout(istekSuresi);
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
    final y = await _istemci
        .get(Uri.parse('$taban/sistem/durum'))
        .timeout(istekSuresi);
    final d = _coz(y) as Map<String, dynamic>;
    final servis = d['model_servisi'] as Map<String, dynamic>?;
    return servis?['sahte'] == true;
  }
}

class ApiHatasi implements Exception {
  final int durum;

  /// Sunucunun ham gerekçesi ya da (yoksa) yer tutucu bir cümle.
  final String mesaj;

  /// Sunucu `detail` alanında GERÇEKTEN bir açıklama yazdı mı?
  ///
  /// `false` ise `mesaj` bizim ürettiğimiz yer tutucudur; kullanıcıya
  /// gösterilecek metin duruma göre kurulur.
  final bool sunucuAcikladi;

  ApiHatasi(this.durum, this.mesaj, {this.sunucuAcikladi = true});

  /// HTTP kodunun Türkçe karşılığı — sunucu susarsa bu kullanılır.
  ///
  /// Kod listesi bu uygulamanın gerçekten karşılaştığı durumlarla
  /// sınırlı: yetki (401/403), bulunamayan kayıt (404), boyut ve tür
  /// denetimleri (413/415 — `api/app/routers/goruntuler.py`), hız
  /// sınırı (429) ve sunucu arızaları (5xx).
  String? get _kodAciklamasi => switch (durum) {
        400 => 'Sunucu isteği geçersiz buldu.',
        401 => 'Oturumunuz geçerli değil. Yeniden giriş yapın.',
        403 => 'Bu işlem için yetkiniz yok.',
        404 => 'İstenen kayıt sunucuda bulunamadı.',
        408 => 'Sunucu isteği zamanında alamadı.',
        409 => 'Bu kayıt sunucuda zaten var.',
        413 => 'Gönderilen dosya sunucunun kabul ettiğinden büyük.',
        415 => 'Sunucu bu dosya türünü kabul etmiyor.',
        422 => 'Gönderilen bilgiler eksik ya da hatalı.',
        // Ücretsiz sunucu katmanında sık görülür ve GEÇİCİDİR.
        429 => 'Sunucu şu an çok fazla istek alıyor (hız sınırı). '
            'Bir iki dakika bekleyip tekrar deneyin.',
        500 => 'Sunucuda beklenmeyen bir hata oluştu; istek '
            'tamamlanamadı.',
        502 || 503 || 504 => 'Sunucu şu an cevap veremiyor. '
            'Uyanması bir dakika sürebilir; tekrar deneyin.',
        _ => null,
      };

  /// Kullanıcıya gösterilecek metin.
  ///
  /// Kural: ANLAM önce, ham kod sonra. Ham kod gizlenmez — hata
  /// bildirimi yapan kullanıcının ve jürinin işine yarar — ama tek
  /// başına da bırakılmaz. "500" bir kullanıcıya hiçbir şey anlatmaz.
  String get kullaniciMesaji {
    final anlam = sunucuAcikladi
        ? mesaj
        : (_kodAciklamasi ?? 'Sunucu isteği tamamlayamadı.');
    return '$anlam (HTTP $durum)';
  }

  @override
  String toString() => kullaniciMesaji;
}

/// Yükleme hatası için kullanıcı mesajı — bilinen nedeni de söyler.
///
/// ⚠️ KULLANICI TABLETTE "Yükleme başarısız 500" GÖRÜYORDU ve bu doğru
/// ama yararsız bir cümleydi. 500'ün kaynağı YERELDE YENİDEN ÜRETİLDİ:
/// model servisi 429 (hız sınırı) döndüğünde
/// `api/app/routers/goruntuler.py` içindeki `model_client.saglik()`
/// çağrısı `ModelServisiHatasi` fırlatıyor, bu istisnayı yakalayan bir
/// işleyici olmadığı için FastAPI düz metin `Internal Server Error`
/// gövdesiyle 500 dönüyor. (Sunucu tarafındaki asıl düzeltme API
/// ekibindedir; mobil, sunucunun 500'ünü 200 yapamaz.)
///
/// Mobilin yapabileceği ve yapması gereken şey: kullanıcıya NE OLDUĞUNU
/// ve NE YAPACAĞINI söylemek. Sahada telefonuna bakan kişi için
/// "birazdan tekrar deneyin" ile "boşuna deneme" arasındaki fark,
/// enkaz alanında geçirilen dakikalardır.
String yuklemeHataMesaji(ApiHatasi h) {
  final taban = h.kullaniciMesaji;
  // 429 ve 5xx: model servisi meşgul ya da uykuda olabilir. Bu geçici
  // bir durumdur; tekrar denemek işe yarar.
  if (h.durum == 429 || h.durum >= 500) {
    return '$taban\n\nBunun bilinen nedeni model servisinin şu an '
        'ulaşılamaz olmasıdır: ücretsiz sunucu katmanında servis '
        'uykuya geçebilir ya da hız sınırına takılabilir. '
        'Fotoğraflar listede duruyor — bir iki dakika sonra tekrar '
        'gönderin.';
  }
  // Yetki, boyut, tür… — sunucu ne dediyse o geçerlidir. Her hâlde
  // fotoğrafların kaybolmadığı söylenir: kullanıcı yeniden çekmeye
  // kalkmasın.
  return '$taban Fotoğraflar listede duruyor.';
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
