import 'package:flutter/material.dart';

/// Tema — web arayüzüyle aynı renk ve ölçüler.
///
/// Mobil ve web ayrı ürünler değil; aynı sistemin iki yüzü. Saha
/// personeli telefonda gördüğü rengi masaüstünde de görmeli.
///
/// Malzeme sınıfı renkleri `siniflar.json` ile birebir aynıdır.
/// Değiştirilmemeli — ayrışırsa iki yüz farklı renk gösterir.

/// Koyu tema renkleri — web arayüzündeki `:root[data-theme="dark"]` ile aynı.
class Koyu {
  static const taban = Color(0xFF000000);
  static const yuzey = Color(0xFF12161D);
  static const yuzey2 = Color(0xFF191E27);
  static const yuzey3 = Color(0xFF232A35);
  static const kenar = Color(0xFF303845);
  static const kenarNet = Color(0xFF414B5B);

  static const metin = Color(0xFFF4F7FA);
  static const metin2 = Color(0xFFC7D1DD);
  static const metin3 = Color(0xFF99A5B4);
  // Web'de bu jeton #7b8796'ydı ve `yuzey-3` üzerinde 3,95 ölçüldü —
  // AA'nın altında. Orada #909cab'e çıkarıldı; mobil de aynı değeri alır,
  // yoksa iki yüz farklı renk gösterir.
  static const metin4 = Color(0xFF909CAB);

  static const marka = Color(0xFF2FBD82);
  static const olumlu = Color(0xFF2FBD82);
  static const uyari = Color(0xFFE5A52E);
  static const dikkat = Color(0xFFEF6A4A);
  static const bilgi = Color(0xFF4D9BFF);
}

/// Açık tema renkleri — web arayüzündeki `:root` ile aynı.
///
/// ⚠️ BU PALET MOBİLDE HİÇ YOKTU. Uygulama `koyuTema()` ile sabitlenmişti
/// ve tema seçeneği bulunmuyordu. Web tarafında varsayılan açık temaya
/// çevrildikten sonra iki yüz birbirini tutmuyordu: aynı sistemin
/// masaüstü hâli aydınlık, telefon hâli simsiyah açılıyordu.
///
/// Sahada koyu tema hâlâ savunulabilir (gece çalışması, pil), ama bu bir
/// VARSAYILAN meselesidir, tek seçenek olması değil. Gündüz, güneş
/// altında, koyu bir ekran okunmaz.
class Acik {
  static const taban = Color(0xFFF5F6F3);
  static const yuzey = Color(0xFFFFFFFF);
  static const yuzey2 = Color(0xFFF0F2EE);
  static const yuzey3 = Color(0xFFE5E8E2);
  static const kenar = Color(0xFFD9DED5);
  static const kenarNet = Color(0xFFB7BFB2);

  static const metin = Color(0xFF0E1319);
  static const metin2 = Color(0xFF39434F);
  static const metin3 = Color(0xFF4C5763);
  // Web'de bu jeton #5b6772'ydi ve `yuzey-vurgu` (#dfe3db) üzerinde 4,45
  // ölçüldü — eşiğin 0,05 altında. Orada #566270'e karartıldı; mobil de
  // aynı değeri alır, yoksa iki yüz farklı renk gösterir.
  static const metin4 = Color(0xFF566270);

  static const marka = Color(0xFF0D6B48);
  static const olumlu = Color(0xFF0D6B48);
  static const uyari = Color(0xFF7D5305);
  static const dikkat = Color(0xFFA8371F);
  static const bilgi = Color(0xFF1A5FC4);
}

/// Yürürlükteki palet.
///
/// `Renk.taban` gibi çağrılar bütün ekranlarda dağınık hâlde duruyordu;
/// bu sınıf, seçilen temaya göre doğru değeri döndürerek o çağrıları
/// olduğu gibi bırakır. `temayiKur()` uygulama açılışında bir kez çağrılır.
class Renk {
  static bool _koyu = false;

  /// Hangi tema yürürlükte?
  static bool get koyuMu => _koyu;

  static void temayiKur({required bool koyu}) => _koyu = koyu;

  static Color get taban => _koyu ? Koyu.taban : Acik.taban;
  static Color get yuzey => _koyu ? Koyu.yuzey : Acik.yuzey;
  static Color get yuzey2 => _koyu ? Koyu.yuzey2 : Acik.yuzey2;
  static Color get yuzey3 => _koyu ? Koyu.yuzey3 : Acik.yuzey3;
  static Color get kenar => _koyu ? Koyu.kenar : Acik.kenar;
  static Color get kenarNet => _koyu ? Koyu.kenarNet : Acik.kenarNet;

  static Color get metin => _koyu ? Koyu.metin : Acik.metin;
  static Color get metin2 => _koyu ? Koyu.metin2 : Acik.metin2;
  static Color get metin3 => _koyu ? Koyu.metin3 : Acik.metin3;
  static Color get metin4 => _koyu ? Koyu.metin4 : Acik.metin4;

  static Color get marka => _koyu ? Koyu.marka : Acik.marka;
  static Color get olumlu => _koyu ? Koyu.olumlu : Acik.olumlu;
  static Color get uyari => _koyu ? Koyu.uyari : Acik.uyari;
  static Color get dikkat => _koyu ? Koyu.dikkat : Acik.dikkat;
  static Color get bilgi => _koyu ? Koyu.bilgi : Acik.bilgi;

  /// Marka rengi ZEMİN olarak kullanıldığında üzerine gelecek metin rengi.
  ///
  /// Koyu temada marka açık yeşil (#2FBD82) — üzerine siyah yazılır.
  /// Açık temada marka koyu yeşil (#0D6B48) — üzerine beyaz yazılır.
  /// Sabit `Renk.taban` kullanılırsa açık temada koyu yeşil düğmenin
  /// üzerine kırık beyaz gelir ve okunmaz.
  static Color get markaUstu =>
      _koyu ? Koyu.taban : const Color(0xFFFFFFFF);

  /// Malzeme sınıfı renkleri — `siniflar.json` ile aynı.
  ///
  /// ⚠️ SIRA VE ADLAR MODELİN `data.yaml`'INDAN GELİR. 02.09.2026'da
  /// sınıf listesi 10'dan 5'e indi: eğitilen model takımın kendi veri
  /// setiyle (Roboflow etiketli, 5 sınıf) eğitildi, CDW-Seg'in 10
  /// sınıfıyla değil. Bu liste `siniflar.json` ile birebir aynı kalmak
  /// zorundadır — ayrışırsa mobil arayüz yanlış renk gösterir.
  ///
  /// Renkler renk körlüğü benzetimiyle seçildi (en kötü ΔE=6,8).
  /// Renk tek başına anlam taşımaz; etiketlerde sınıf adı yazılıdır.
  static const malzeme = <String, Color>{
    'ahsap': Color(0xFFD95926),
    'beton_tugla': Color(0xFF6B7280),
    'cam': Color(0xFF008300),
    'metal': Color(0xFF3987E5),
    'seramik': Color(0xFFC98500),
  };

  /// Sınıfın EKRANDA görünen adı — `siniflar.json` → `gorunen_ad`.
  ///
  /// ⚠️ MOBİL, SAHA PERSONELİNE HAM SINIF ADINI GÖSTERİYORDU:
  /// "beton_tugla", "ahsap". Bunlar makine tanımlayıcısıdır, Türkçe
  /// değildir ve enkaz alanında telefonuna bakan biri için "Beton /
  /// tuğla" kadar okunaklı değildir. Web arayüzü aynı kaydı doğru adla
  /// gösteriyordu; iki arayüz aynı tespite iki farklı ad veriyordu.
  ///
  /// Aynı hata bir kez de ekran okuyucuda yakalanmıştı
  /// (`web/.../TespitKutulari.tsx`): ham ad okunuyordu.
  ///
  /// Liste neden burada sabit: uygulama ÇEVRİMDIŞI çalışmak zorunda
  /// (sahada bağlantı yok) ve sunucudan sınıf listesi çekemeyebilir.
  /// Sabit kalması `siniflar.json` ile ayrışma riski doğurur; risk
  /// `test/sinif_adlari_test.dart` ile kapatılmıştır — o test bu haritayı
  /// deponun `siniflar.json` dosyasıyla karşılaştırır.
  static const malzemeAdi = <String, String>{
    'ahsap': 'Ahşap',
    'beton_tugla': 'Beton / tuğla',
    'cam': 'Cam',
    'metal': 'Metal',
    'seramik': 'Seramik',
  };

  static Color sinif(String ad) => malzeme[ad] ?? metin4;

  /// Ekranda gösterilecek ad. Tanınmayan bir sınıf gelirse ham ad
  /// gösterilir — uydurulmaz ve gizlenmez; kullanıcı bir tuhaflık
  /// olduğunu görebilmelidir.
  static String sinifAdi(String ad) => malzemeAdi[ad] ?? ad;
}

/// Seçilen temaya göre `ThemeData` üretir.
///
/// `Renk` sınıfı önce `temayiKur()` ile ayarlanmalıdır; bu fonksiyon
/// oradaki yürürlükteki paleti okur.
ThemeData uygulamaTemasi({required bool koyu}) {
  Renk.temayiKur(koyu: koyu);
  final taban = koyu
      ? ThemeData.dark(useMaterial3: true)
      : ThemeData.light(useMaterial3: true);

  return taban.copyWith(
    scaffoldBackgroundColor: Renk.taban,
    colorScheme: taban.colorScheme.copyWith(
      primary: Renk.marka,
      surface: Renk.yuzey,
      error: Renk.dikkat,
      // Marka rengi ZEMİN olduğunda üzerine gelen renk. Eskiden
      // `Renk.taban`dı; açık temada koyu yeşil düğmenin üstüne kırık
      // beyaz zemin rengi gelirdi ve yazı okunmazdı.
      onPrimary: Renk.markaUstu,
      onSurface: Renk.metin,
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: Renk.yuzey,
      foregroundColor: Renk.metin,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: Renk.yuzey,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Renk.kenar),
      ),
      margin: EdgeInsets.zero,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: Renk.marka,
        foregroundColor: Renk.markaUstu,
        // Saha koşulunda eldivenli parmakla kullanılacak: dokunma hedefi
        // geniş tutulur (WCAG 2.5.5 asgari 44px).
        minimumSize: const Size.fromHeight(52),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: Renk.metin,
        side: BorderSide(color: Renk.kenarNet),
        minimumSize: const Size.fromHeight(52),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Renk.yuzey2,
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: Renk.kenar),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: Renk.kenar),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: Renk.marka, width: 2),
      ),
      labelStyle: TextStyle(color: Renk.metin3),
    ),
    dividerTheme: DividerThemeData(color: Renk.kenar, thickness: 1),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: Renk.yuzey3,
      contentTextStyle: TextStyle(color: Renk.metin),
      behavior: SnackBarBehavior.floating,
    ),
  );
}
