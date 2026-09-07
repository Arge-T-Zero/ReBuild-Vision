import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:rebuild_vision_mobil/roller.dart';
import 'package:rebuild_vision_mobil/tema.dart';

/// Mobil rol tanımlarının SUNUCU SÖZLEŞMESİ.
///
/// `siniflar.json` testinin (`sinif_adlari_test.dart`) kardeşi. Mobil,
/// hangi rolün ne yapabileceğini kendi içinde sabit tutuyor — sekmeler
/// açılışta kurulmalı ve sunucuya sormak için bir tur beklenmemeli. Bu
/// kopyanın bedeli sessiz ayrışmadır:
///
///   - Sunucuda bir role yetki EKLENİRSE mobil o sekmeyi göstermez;
///     kullanıcı yapabileceği bir işi yapamaz ve nedenini göremez.
///   - Sunucudan bir yetki KALDIRILIRSA mobil sekmeyi göstermeye devam
///     eder; kullanıcı formu doldurup 403 alır.
///
/// İkisi de sessizdir. Bu test o sessizliği bozar: `roller.dart`
/// deponun `api/app/core/permissions.py` dosyasıyla karşılaştırılır.
void main() {
  final kok = Directory.current.path.endsWith('mobile')
      ? Directory.current.parent
      : Directory.current;
  final kaynak =
      File('${kok.path}/api/app/core/permissions.py').readAsStringSync();

  /// `permissions.py` içindeki bir rol kümesini okur.
  ///
  /// Dosya biçimi sabit: `AD = {Rol.X, Rol.Y}`. Python'u çalıştırmak
  /// yerine metin okunuyor — test ortamında yorumlayıcı olmayabilir ve
  /// bu kadarı ayrışmayı yakalamaya yeter.
  Set<String> kume(String ad) {
    final e = RegExp('^$ad = \\{([^}]*)\\}', multiLine: true).firstMatch(kaynak);
    expect(e, isNotNull,
        reason: '$ad kümesi permissions.py içinde bulunamadı — '
            'dosyanın biçimi değişmiş olabilir');
    return RegExp(r'Rol\.([A-Z_]+)')
        .allMatches(e!.group(1)!)
        .map((m) => m.group(1)!.toLowerCase())
        .toSet();
  }

  /// `Rol` enum'undaki bütün değerler.
  Set<String> tumRoller() {
    final govde = RegExp(r'class Rol\(str, enum\.Enum\):([\s\S]*?)\n\n')
        .firstMatch(kaynak);
    expect(govde, isNotNull, reason: 'Rol enum tanımı okunamadı');
    return RegExp(r'^\s+[A-Z_]+ = "([a-z]+)"', multiLine: true)
        .allMatches(govde!.group(1)!)
        .map((m) => m.group(1)!)
        .toSet();
  }

  group('permissions.py ile aynı', () {
    test('rol kümesi birebir aynı', () {
      expect(roller.keys.toSet(), tumRoller(),
          reason: 'Mobil rol listesi sunucuyla ayrışmış');
    });

    test('görüntü yükleyebilen roller aynı', () {
      final mobil = roller.entries
          .where((e) => e.value.goruntuYukleyebilir)
          .map((e) => e.key)
          .toSet();
      expect(mobil, kume('GORUNTU_YUKLEYEBILIR'),
          reason: 'Yükleme sekmesi yanlış rollere gösteriliyor');
    });

    test('ölçüm girebilen roller aynı', () {
      final mobil = roller.entries
          .where((e) => e.value.olcumGirebilir)
          .map((e) => e.key)
          .toSet();
      expect(mobil, kume('OLCUM_GIREBILIR'),
          reason: 'Ölçüm sekmesi yanlış rollere gösteriliyor');
    });

    test('salt okunur roller mobilde hiçbir şey yapamaz', () {
      // Sunucu bu rollere HİÇBİR yazma işlemi açmıyor; mobil de
      // açmamalı. Aksi hâlde kullanıcı formu doldurup 403 alır.
      for (final r in kume('SALT_OKUNUR')) {
        final t = roller[r]!;
        expect(t.goruntuYukleyebilir, isFalse, reason: '$r yükleyemez');
        expect(t.olcumGirebilir, isFalse, reason: '$r ölçüm giremez');
      }
    });
  });

  group('sekmeler role göre kurulur', () {
    test('saha personeli üç sekme görür', () {
      expect(roller['saha']!.ekranlar,
          [MobilEkran.yukle, MobilEkran.olcum, MobilEkran.hesap]);
    });

    test('belediye yetkilisi ölçüm sekmesi GÖRMEZ', () {
      // Kullanıcının bildirdiği arızanın çekirdeği: belediye yetkilisi
      // saha personelinin ekranını görüyordu. Sunucu ona ölçüm
      // girdirmiyor (OLCUM_GIREBILIR).
      final e = roller['belediye']!.ekranlar;
      expect(e, [MobilEkran.yukle, MobilEkran.hesap]);
      expect(e.contains(MobilEkran.olcum), isFalse);
    });

    test('doğrulayıcı uzman yükleme sekmesi GÖRMEZ', () {
      final e = roller['uzman']!.ekranlar;
      expect(e, [MobilEkran.olcum, MobilEkran.hesap]);
    });

    test('AFAD, yıkım ve tesis yalnızca Hesap sekmesini görür', () {
      for (final r in ['afad', 'yikim', 'tesis']) {
        expect(roller[r]!.ekranlar, [MobilEkran.hesap], reason: r);
      }
    });

    test('her rolde en az bir sekme vardır', () {
      // Boş bir uygulama açılışı, yanlış ekran kadar kötüdür.
      for (final t in [...roller.values, rolYok]) {
        expect(t.ekranlar, isNotEmpty, reason: t.ad);
      }
    });
  });

  group('açılış sekmesi', () {
    test('asıl işi mobilde olan rol doğrudan işine düşer', () {
      for (final r in ['saha', 'yonetici']) {
        final t = roller[r]!;
        expect(t.ekranlar[t.acilisSekmesi], MobilEkran.yukle, reason: r);
      }
    });

    test('asıl işi webde olan rol önce açıklamayı görür', () {
      // Sessizce yanlış ekran göstermemenin karşılığı budur.
      for (final r in ['belediye', 'uzman', 'afad', 'yikim', 'tesis']) {
        final t = roller[r]!;
        expect(t.ekranlar[t.acilisSekmesi], MobilEkran.hesap, reason: r);
      }
    });

    test('açılış sekmesi her zaman geçerli bir sıradadır', () {
      for (final t in [...roller.values, rolYok]) {
        expect(t.acilisSekmesi, greaterThanOrEqualTo(0), reason: t.ad);
        expect(t.acilisSekmesi, lessThan(t.ekranlar.length), reason: t.ad);
      }
    });
  });

  group('tanınmayan ve atanmamış rol', () {
    test('rol atanmamışsa hiçbir yetki verilmez', () {
      expect(rolTanimi(null), rolYok);
      expect(rolYok.goruntuYukleyebilir, isFalse);
      expect(rolYok.olcumGirebilir, isFalse);
      expect(rolYok.ekranlar, [MobilEkran.hesap]);
    });

    test('tanınmayan rolde yetki uydurulmaz', () {
      // Sunucuya yeni bir rol eklenip mobil güncellenmezse: yetkisiz
      // varsayılana düşülür. 403 almaktansa hiçbir şey vaat etmemek
      // doğrudur.
      final t = rolTanimi('yeni_rol_2027');
      expect(t.goruntuYukleyebilir, isFalse);
      expect(t.olcumGirebilir, isFalse);
    });

    test('tanınmayan rolün adı gizlenmez', () {
      // `tema.dart` → `sinifAdi` ile aynı ilke: uydurma yok, gizleme
      // yok. Kullanıcı bir tuhaflık olduğunu görebilmelidir.
      expect(rolTanimi('yeni_rol_2027').ad, 'yeni_rol_2027');
    });
  });

  group('rol adı büyük harfle DOĞRU yazılır', () {
    // ⚠️ `String.toUpperCase()` TÜRKÇEYİ BOZAR: yerel duyarlı değildir
    // ve "i" harfini noktasız "I" yapar. Hesap ekranındaki rol rozeti
    // büyük harf kullanıyor; kullanıcı kendi rolünü "BELEDIYE
    // YETKILISI" diye yanlış yazılmış görüyordu.
    test('Dart nokta kuralını bilmiyor — bu yüzden kendi çevirimiz var', () {
      expect('Belediye yetkilisi'.toUpperCase(), 'BELEDIYE YETKILISI',
          reason: 'Dart davranışı değişmiş; çevirimiz gereksizleşmiş '
              'olabilir');
    });

    test('noktalı i büyük harfte noktasını korur', () {
      expect(turkceBuyuk('Belediye yetkilisi'), 'BELEDİYE YETKİLİSİ');
      expect(turkceBuyuk('Tesis operatörü'), 'TESİS OPERATÖRÜ');
      expect(turkceBuyuk('Doğrulayıcı uzman'), 'DOĞRULAYICI UZMAN');
    });

    test('noktasız ı büyük harfte noktasız kalır', () {
      expect(turkceBuyuk('Yıkım firması'), 'YIKIM FİRMASI');
    });

    test('her rol adı çevrildikten sonra da okunur', () {
      for (final t in [...roller.values, rolYok]) {
        final buyuk = turkceBuyuk(t.ad);
        expect(buyuk.contains('I'), t.ad.contains('ı') || t.ad.contains('I'),
            reason: '${t.ad} → $buyuk : noktasız I yalnızca ı harfinden '
                'gelmeli');
      }
    });
  });

  group('metinler web arayüzüyle aynı', () {
    test('rol adları ve görev cümleleri roller.ts ile aynı', () {
      final ts = File('${kok.path}/web/src/roller.ts').readAsStringSync();
      for (final g in roller.entries) {
        // roller.ts biçimi: `  <rol>: {\n    ad: '...',` ve `gorev: '...'`
        final blok = RegExp(
          "^  ${g.key}: \\{([\\s\\S]*?)^  \\},",
          multiLine: true,
        ).firstMatch(ts);
        expect(blok, isNotNull, reason: '${g.key} roller.ts içinde yok');
        final ad =
            RegExp(r"ad: '([^']*)'").firstMatch(blok!.group(1)!)?.group(1);
        expect(ad, g.value.ad, reason: '${g.key} rol adı ayrışmış');

        final gorev =
            RegExp(r"gorev: '([^']*)'").firstMatch(blok.group(1)!)?.group(1);
        expect(gorev, g.value.gorev, reason: '${g.key} görev cümlesi ayrışmış');
      }
    });
  });
}
