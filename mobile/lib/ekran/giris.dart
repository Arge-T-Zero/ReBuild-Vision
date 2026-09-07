import 'dart:async';

import 'package:flutter/material.dart';

import '../api.dart';
import '../bekleme.dart';
import '../marka.dart';
import '../tema.dart';

/// Giriş ekranı — düzeni ve metinleri `web/src/sayfalar/Giris.tsx`'ten.
///
/// ⚠️ KULLANICI ŞUNU BİLDİRDİ: "Arka planın güzelliği yok, giriş arka
/// planı web'deki gibi değil."
///
/// Haklıydı, ve fark yalnızca "güzellik" değildi: iki ekran aynı ürüne
/// ait görünmüyordu. Web'deki giriş ekranında tam sayfa bir hero
/// görseli, üstünde ölçülü bir perde, kendi zeminine oturan bir kart,
/// üç maddelik çalışma kuralları ve yarışma künyesi var. Mobilde ise
/// düz zemin üzerine Material'ın hazır `layers` simgesi ve iki alan
/// vardı.
///
/// Bu ekran WEB'DEN TÜRETİLDİ, yeniden tasarlanmadı:
///
///   - Arka plan görseli aynı dosya: `giris-hero.webp`
///     (`web/public/gorseller/` → `mobile/assets/gorseller/`).
///   - Perde aynı ölçülerde: açık temada %38, koyu temada %58 taban
///     rengi + üstte %22, altta %45 biten dikey geçiş
///     (`web/src/index.css` → `.giris-perde-tam`).
///   - Kart YARI SAYDAM DEĞİL, kendi zeminine oturur: kontrast
///     fotoğraftan bağımsız garanti altındadır (web'deki aynı gerekçe).
///   - Başlık, alt başlık, üç kural ve künye metni birebir aynı.
///   - Marka işareti aynı geometri (`marka.dart`).
///
/// Kayıt formu bilinçli olarak MOBİLE ALINMADI: mobil saha
/// uygulamasıdır, hesap açma kurumsal bir işlemdir ve web'de yapılır.
/// Bunun yerine web adresi yazılı — ölü bir düğme göstermektense nereye
/// gidileceğini söylemek doğrudur.
class GirisEkrani extends StatefulWidget {
  final Api api;
  final void Function(Kullanici) girisYapildi;
  final bool koyuTema;
  final Future<void> Function() temaDegistir;

  const GirisEkrani({
    super.key,
    required this.api,
    required this.girisYapildi,
    required this.koyuTema,
    required this.temaDegistir,
  });

  @override
  State<GirisEkrani> createState() => _GirisDurumu();
}

/// Web'deki `OZELLIKLER` dizisiyle birebir aynı üç madde.
const _ozellikler = <(String, String)>[
  (
    'İnsan denetimli sınıflandırma',
    'Model çıktıları ön tahmindir; uzman onaylar, düzeltir ya da '
        'belirsiz işaretler. İnsanın kararı modelin tahminini geçersiz '
        'kılar.',
  ),
  (
    'Ölçüm yoksa miktar üretilmez',
    'Sistem dayanağı olmayan tonaj tahmini oluşturmaz. Miktar '
        'hesaplandığında tek bir kesin değer değil, belirsizlik aralığı '
        'verilir.',
  ),
  (
    'Her kayıt izlenebilir',
    'Kimin ne zaman neyi değiştirdiği otomatik kaydedilir. Kayıtlar '
        'silinemez ve düzenlenemez.',
  ),
];

/// Web'deki `KUNYE` ile birebir aynı.
const _kunye = 'TEKNOFEST 2026 Sıfır Atık ve Döngüsel Ekonomi Yarışması · '
    'Takım Arge-T Zero. Sistem yalnızca görünür yüzeye ilişkin ön '
    'değerlendirme yapar ve tehlikeli madde teşhisi yapmaz.';

/// Web'deki `EKRAN.giris.baslik` ile birebir aynı.
const _baslik = 'Enkaz malzemelerinin görüntü tabanlı ön sınıflandırması '
    've doğrulanabilir kaynak haritası';

class _GirisDurumu extends State<GirisEkrani> {
  final _eposta = TextEditingController();
  final _parola = TextEditingController();
  String _hata = '';
  bool _bekliyor = false;

  /// Sahte model servisi çalışıyor mu? `null` = bilinmiyor.
  bool? _sahteModel;

  /// Parola gizli mi?
  ///
  /// ⚠️ MOBİLDE GÖSTER/GİZLE YOKTU, web arayüzünde vardı. Saha
  /// koşulunda bu bir kullanılabilirlik sorunu: eldivenli parmakla,
  /// güneş altında, küçük bir klavyede yazılan parola yanlış girildiğinde
  /// kullanıcı nerede hata yaptığını göremiyor — yalnızca "giriş
  /// başarısız" görüyor ve baştan yazıyordu.
  bool _parolaGizli = true;

  @override
  void initState() {
    super.initState();
    _modelDurumu();
  }

  /// Sahte model servisi uyarısı için sunucu durumunu sorar.
  ///
  /// Web giriş ekranı bu uyarıyı gösteriyordu, mobil göstermiyordu:
  /// demoyu izleyen kişi giriş ekranına bakıp gerçek bir modelin
  /// çalıştığını sanabilirdi (ana talimat Bölüm 9.5). Uç nokta kimlik
  /// GEREKTİRMEZ, giriş yapılmadan çağrılabilir.
  ///
  /// Yan faydası bilinçli: bu istek sunucuyu UYANDIRIR. Kullanıcı
  /// e-postasını yazarken Render konteyneri ayağa kalkmaya başlar, ve
  /// "Giriş yap"a basıldığında beklenen süre kısalır. Uyandırma amacıyla
  /// boş bir istek atmak yerine zaten göstermemiz gereken bilgiyi
  /// çekiyoruz.
  Future<void> _modelDurumu() async {
    try {
      final sahte = await widget.api.sahteModelMi();
      if (mounted) setState(() => _sahteModel = sahte);
    } catch (_) {
      // Sunucuya ulaşılamıyorsa hiçbir şey iddia edilmez: ne "gerçek"
      // ne "sahte". Giriş ekranı bu yüzden bozulmaz.
      if (mounted) setState(() => _sahteModel = null);
    }
  }

  @override
  void dispose() {
    _eposta.dispose();
    _parola.dispose();
    super.dispose();
  }

  Future<void> _gonder() async {
    setState(() {
      _hata = '';
      _bekliyor = true;
    });
    try {
      final k = await widget.api.giris(_eposta.text.trim(), _parola.text);
      widget.girisYapildi(k);
    } on ApiHatasi catch (h) {
      // Sunucu gerekçesini yazdıysa o gösterilir ("E-posta veya parola
      // hatalı", "Hesabınız henüz onaylanmadı"); yazmadıysa kodun
      // Türkçe karşılığı. Ham kod her hâlde metnin içinde.
      setState(() => _hata = h.kullaniciMesaji);
    } on TimeoutException {
      // ⚠️ ESKİDEN BURAYA HİÇ DÜŞÜLEMİYORDU: hiçbir istekte zaman aşımı
      // yoktu, uygulama süresiz bekliyordu. Artık 90 saniye sonra
      // vazgeçiliyor ve NEDEN vazgeçildiği söyleniyor.
      setState(() => _hata =
          'Sunucu ${Api.kimlikSuresi.inSeconds} saniye içinde yanıt '
          'vermedi. Ücretsiz sunucu katmanında uyandırma bu kadar '
          'sürebiliyor; birazdan tekrar deneyin.');
    } catch (_) {
      // Saha uygulamasında ağ hatası sık görülür; teknik ayrıntı yerine
      // ne yapılacağını söyleyen bir mesaj daha yararlıdır.
      setState(() => _hata =
          'Sunucuya ulaşılamadı. Bağlantınızı kontrol edin; '
          'kuyruktaki kayıtlarınız cihazda güvende.');
    } finally {
      if (mounted) setState(() => _bekliyor = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Arka plan görseli tam sayfa. `Stack` içinde ilk katman görsel,
      // ikincisi perde, üçüncüsü içerik.
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Görsel YAPAY ZEKÂ İLE ÜRETİLMİŞTİR; gerçek bir afet
          // fotoğrafı değildir (web/public/gorseller/README.md,
          // şartname Madde 10.7).
          Image.asset(
            'assets/gorseller/giris-hero.webp',
            fit: BoxFit.cover,
            // Görsel yüklenemezse (bozuk varlık) ekran boş kalmasın:
            // düz taban rengine düşülür ve giriş yine yapılabilir.
            errorBuilder: (_, _, _) => ColoredBox(color: Renk.taban),
          ),
          const _Perde(),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
              child: Center(
                child: ConstrainedBox(
                  // Web'deki `max-w-[460px]` ile aynı.
                  constraints: const BoxConstraints(maxWidth: 460),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Align(
                        alignment: Alignment.centerRight,
                        child: _TemaDugmesi(
                          koyu: widget.koyuTema,
                          degistir: widget.temaDegistir,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _Kart(child: _girisKarti()),
                      const SizedBox(height: 12),
                      _Kart(child: _kurallar()),
                      const SizedBox(height: 12),
                      _Kart(
                        dolgu: const EdgeInsets.symmetric(
                            horizontal: 20, vertical: 16),
                        child: Text(
                          _kunye,
                          style: TextStyle(
                              color: Renk.metin3,
                              fontSize: 11.5,
                              height: 1.6),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _girisKarti() => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Marka — web'deki `Marka()` bileşeni: kare işaret + ürün adı.
          //
          // ⚠️ ESKİ KOD BURADA `CrossAxisAlignment.stretch` YÜZÜNDEN
          // BOZULUYORDU: `width: 44` yazan kutu 420 px'e yayılıyor,
          // logo kare yerine şerit olarak çiziliyordu. `Row` +
          // `mainAxisSize` ile esnetme baştan söz konusu değil.
          Row(
            children: [
              const MarkaKutusu(boyut: 38),
              const SizedBox(width: 10),
              Text(
                'ReBuild Vision',
                style: TextStyle(
                  color: Renk.metin,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.3,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Text(
            _baslik,
            style: TextStyle(
              color: Renk.metin,
              fontSize: 20,
              height: 1.35,
              fontWeight: FontWeight.w600,
              letterSpacing: -0.3,
            ),
          ),
          const SizedBox(height: 26),
          Text(
            'Giriş yap',
            style: TextStyle(
              color: Renk.metin,
              fontSize: 17,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Kurumsal hesabınızla oturum açın.',
            style: TextStyle(color: Renk.metin3, fontSize: 13),
          ),
          const SizedBox(height: 20),
          TextField(
            controller: _eposta,
            keyboardType: TextInputType.emailAddress,
            autocorrect: false,
            enabled: !_bekliyor,
            autofillHints: const [AutofillHints.username],
            decoration: const InputDecoration(
              labelText: 'E-posta',
              hintText: 'ad.soyad@kurum.gov.tr',
            ),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: _parola,
            obscureText: _parolaGizli,
            enabled: !_bekliyor,
            autofillHints: const [AutofillHints.password],
            decoration: InputDecoration(
              labelText: 'Parola',
              suffixIcon: IconButton(
                tooltip:
                    _parolaGizli ? 'Parolayı göster' : 'Parolayı gizle',
                onPressed: () =>
                    setState(() => _parolaGizli = !_parolaGizli),
                icon: Icon(
                  _parolaGizli
                      ? Icons.visibility_outlined
                      : Icons.visibility_off_outlined,
                  size: 20,
                  color: Renk.metin3,
                ),
              ),
            ),
            onSubmitted: (_) => _bekliyor ? null : _gonder(),
          ),
          if (_hata.isNotEmpty) ...[
            const SizedBox(height: 14),
            _Uyari(renk: Renk.dikkat, ikon: Icons.error_outline, metin: _hata),
          ],
          // ⚠️ BEKLEYİŞ AÇIKLANMIYORDU. Kullanıcı "girişler yavaş, geç
          // giriyor" dedi; sunucunun uyanması gerçekten uzun sürüyor
          // (Render ücretsiz katman) ama ekranda bunu söyleyen hiçbir
          // şey yoktu — yalnızca devre dışı bir düğme vardı.
          if (_bekliyor) ...[
            const SizedBox(height: 14),
            UyanmaNotu(
              islem: 'Giriş yapılıyor…',
              enFazla: Api.kimlikSuresi,
            ),
          ],
          const SizedBox(height: 18),
          FilledButton(
            onPressed: _bekliyor ? null : _gonder,
            child: Text(_bekliyor ? 'Giriş yapılıyor…' : 'Giriş yap'),
          ),
          // Sahte model servisi uyarısı giriş ekranında da durur:
          // demoyu izleyen kişi sisteme girmeden gerçek bir modelin
          // çalıştığını sanmamalı (ana talimat Bölüm 9.5). Yalnızca
          // sunucu açıkça `sahte: true` dediğinde çıkar.
          if (_sahteModel == true) ...[
            const SizedBox(height: 18),
            _Uyari(
              renk: Renk.uyari,
              ikon: Icons.science_outlined,
              metin: 'SAHTE MODEL SERVİSİ etkin. Bu ortamda üretilen '
                  'sınıflar, güven skorları ve kutular uydurmadır; '
                  'gerçek bir modelin çıktısı değildir. Sahte olan '
                  'servistir, model değil: model eğitildi ve ölçüldü.',
            ),
          ],
          const SizedBox(height: 20),
          Divider(color: Renk.kenar, height: 1),
          const SizedBox(height: 16),
          // Kayıt formu mobilde YOK — gerekçesi sınıf başlığında.
          Text(
            'Kurumsal hesabınız yok mu? Hesap başvurusu ve yönetici '
            'onayı web arayüzünden yapılır:',
            style: TextStyle(color: Renk.metin3, fontSize: 12.5, height: 1.5),
          ),
          const SizedBox(height: 6),
          SelectableText(
            Api.webTaban,
            style: TextStyle(
              color: Renk.bilgi,
              fontSize: 12.5,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
        ],
      );

  Widget _kurallar() => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (var i = 0; i < _ozellikler.length; i++) ...[
            if (i > 0) const SizedBox(height: 18),
            // Web'de her madde sol kenarında bir çizgi taşıyor
            // (`border-l-2 border-kenar-net pl-4`); aynı ayrım burada
            // da korunuyor.
            Container(
              padding: const EdgeInsets.only(left: 14),
              decoration: BoxDecoration(
                border: Border(
                  left: BorderSide(color: Renk.kenarNet, width: 2),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _ozellikler[i].$1,
                    style: TextStyle(
                      color: Renk.metin,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _ozellikler[i].$2,
                    style: TextStyle(
                        color: Renk.metin3, fontSize: 12.5, height: 1.55),
                  ),
                ],
              ),
            ),
          ],
        ],
      );
}

/// Arka plan perdesi — `web/src/index.css` → `.giris-perde-tam`.
///
/// Ölçüler web'den alındı, uydurulmadı: düz katman açık temada %38,
/// koyu temada %58 taban rengi; üstüne üstte %22'den şeffafa, altta
/// şeffaftan %45'e giden dikey bir geçiş biniyor. Perdenin işi kartın
/// altındaki fotoğrafı bastırmak değil, ekranın üst ve alt kenarlarını
/// koyulaştırıp durum çubuğu ile künyeyi okunur tutmak.
class _Perde extends StatelessWidget {
  const _Perde();

  @override
  Widget build(BuildContext context) {
    final taban = Renk.taban;
    final duz = Renk.koyuMu ? 0.58 : 0.38;
    return DecoratedBox(
      decoration: BoxDecoration(color: taban.withValues(alpha: duz)),
      child: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              taban.withValues(alpha: 0.22),
              taban.withValues(alpha: 0.0),
              taban.withValues(alpha: 0.0),
              taban.withValues(alpha: 0.45),
            ],
            stops: const [0.0, 0.30, 0.62, 1.0],
          ),
        ),
        child: const SizedBox.expand(),
      ),
    );
  }
}

/// Kendi zeminine oturan kart — yarı saydam DEĞİL.
///
/// Web'deki gerekçenin aynısı: kart saydam olsaydı metin kontrastı
/// altındaki fotoğrafın o bölgesine bağlı olurdu ve okunurluk garanti
/// edilemezdi.
class _Kart extends StatelessWidget {
  final Widget child;
  final EdgeInsets dolgu;

  const _Kart({
    required this.child,
    this.dolgu = const EdgeInsets.all(20),
  });

  @override
  Widget build(BuildContext context) => Container(
        padding: dolgu,
        decoration: BoxDecoration(
          color: Renk.yuzey,
          border: Border.all(color: Renk.kenar),
          borderRadius: BorderRadius.circular(14),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: Renk.koyuMu ? 0.5 : 0.12),
              blurRadius: 24,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: child,
      );
}

class _TemaDugmesi extends StatelessWidget {
  final bool koyu;
  final Future<void> Function() degistir;

  const _TemaDugmesi({required this.koyu, required this.degistir});

  @override
  Widget build(BuildContext context) {
    // Düğme fotoğrafın üstünde duruyor: kendi zemini olmalı, yoksa
    // görselin açık bir bölgesine denk geldiğinde kaybolur.
    return Material(
      color: Renk.yuzey.withValues(alpha: 0.92),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(9),
        side: BorderSide(color: Renk.kenar),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => degistir(),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                koyu ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
                size: 15,
                color: Renk.metin2,
              ),
              const SizedBox(width: 7),
              Text(
                koyu ? 'Açık tema' : 'Koyu tema',
                style: TextStyle(color: Renk.metin2, fontSize: 12.5),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Renkli kutu içinde uyarı/hata metni.
class _Uyari extends StatelessWidget {
  final Color renk;
  final IconData ikon;
  final String metin;

  const _Uyari({required this.renk, required this.ikon, required this.metin});

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: renk.withValues(alpha: 0.1),
          border: Border.all(color: renk.withValues(alpha: 0.3)),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(ikon, size: 16, color: renk),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                metin,
                style: TextStyle(color: renk, fontSize: 12.5, height: 1.5),
              ),
            ),
          ],
        ),
      );
}
