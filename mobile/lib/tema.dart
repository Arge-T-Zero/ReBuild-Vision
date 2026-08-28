import 'package:flutter/material.dart';

/// Tema — web arayüzüyle aynı renk ve ölçüler.
///
/// Mobil ve web ayrı ürünler değil; aynı sistemin iki yüzü. Saha
/// personeli telefonda gördüğü rengi masaüstünde de görmeli.
///
/// Malzeme sınıfı renkleri `siniflar.json` ile birebir aynıdır ve dataviz
/// doğrulayıcısından geçmiştir (koyu ve açık zeminde). Değiştirilmemeli.
class Renk {
  // Koyu tema — sahada varsayılan
  static const taban = Color(0xFF000000);
  static const yuzey = Color(0xFF12161D);
  static const yuzey2 = Color(0xFF191E27);
  static const yuzey3 = Color(0xFF232A35);
  static const kenar = Color(0xFF303845);
  static const kenarNet = Color(0xFF414B5B);

  static const metin = Color(0xFFF4F7FA);
  static const metin2 = Color(0xFFC7D1DD);
  static const metin3 = Color(0xFF99A5B4);
  static const metin4 = Color(0xFF7B8796);

  static const marka = Color(0xFF2FBD82);
  static const olumlu = Color(0xFF2FBD82);
  static const uyari = Color(0xFFE5A52E);
  static const dikkat = Color(0xFFEF6A4A);
  static const bilgi = Color(0xFF4D9BFF);

  /// Malzeme sınıfı renkleri — siniflar.json ile aynı.
  static const malzeme = <String, Color>{
    'ahsap': Color(0xFFD95926),
    'sert_plastik': Color(0xFF199E70),
    'metal': Color(0xFF3987E5),
    'karton': Color(0xFFC98500),
    'tekstil': Color(0xFFD55181),
    'yumusak_plastik': Color(0xFF008300),
    'alcipan': Color(0xFFE66767),
    'beton': Color(0xFF9085E9),
    'dolgu_toprak': Color(0xFFA06A2C),
    'konteyner': Color(0xFF6B7280),
  };

  static Color sinif(String ad) => malzeme[ad] ?? metin4;
}

ThemeData koyuTema() {
  final taban = ThemeData.dark(useMaterial3: true);
  return taban.copyWith(
    scaffoldBackgroundColor: Renk.taban,
    colorScheme: taban.colorScheme.copyWith(
      primary: Renk.marka,
      surface: Renk.yuzey,
      error: Renk.dikkat,
      onPrimary: Renk.taban,
      onSurface: Renk.metin,
    ),
    appBarTheme: const AppBarTheme(
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
        side: const BorderSide(color: Renk.kenar),
      ),
      margin: EdgeInsets.zero,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: Renk.marka,
        foregroundColor: Renk.taban,
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
        side: const BorderSide(color: Renk.kenarNet),
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
        borderSide: const BorderSide(color: Renk.kenar),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Renk.kenar),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Renk.marka, width: 2),
      ),
      labelStyle: const TextStyle(color: Renk.metin3),
    ),
    dividerTheme: const DividerThemeData(color: Renk.kenar, thickness: 1),
    snackBarTheme: const SnackBarThemeData(
      backgroundColor: Renk.yuzey3,
      contentTextStyle: TextStyle(color: Renk.metin),
      behavior: SnackBarBehavior.floating,
    ),
  );
}
