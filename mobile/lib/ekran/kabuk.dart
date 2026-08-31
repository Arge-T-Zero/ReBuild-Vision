import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';

import '../api.dart';
import '../kuyruk.dart';
import '../tema.dart';
import 'olcum.dart';
import 'yukle.dart';

/// Uygulama kabuğu — alt gezinme ve bağlantı durumu.
///
/// Kuyruk sayacı burada tutulur: hangi sekmede olursanız olun kaç kaydın
/// beklediğini görürsünüz. Saha personelinin en çok merak ettiği şey budur.
class Kabuk extends StatefulWidget {
  final Api api;
  final Kuyruk kuyruk;
  final Kullanici kullanici;
  final VoidCallback cikisYapildi;
  final bool koyuTema;
  final Future<void> Function() temaDegistir;

  const Kabuk({
    super.key,
    required this.api,
    required this.kuyruk,
    required this.kullanici,
    required this.cikisYapildi,
    required this.koyuTema,
    required this.temaDegistir,
  });

  @override
  State<Kabuk> createState() => _KabukDurumu();
}

class _KabukDurumu extends State<Kabuk> {
  int _sekme = 0;
  int _kuyruktaBekleyen = 0;
  bool _cevrimici = true;
  StreamSubscription<List<ConnectivityResult>>? _baglantiAboneligi;

  @override
  void initState() {
    super.initState();
    _kuyrukSay();
    _baglantiIzle();
  }

  @override
  void dispose() {
    _baglantiAboneligi?.cancel();
    super.dispose();
  }

  Future<void> _baglantiIzle() async {
    final simdi = await Connectivity().checkConnectivity();
    if (mounted) setState(() => _cevrimici = _bagliMi(simdi));

    _baglantiAboneligi =
        Connectivity().onConnectivityChanged.listen((durum) async {
      final bagli = _bagliMi(durum);
      if (mounted) setState(() => _cevrimici = bagli);
      // Bağlantı geri geldiğinde kuyruk kendiliğinden gönderilir; saha
      // personelinin bunu hatırlaması gerekmez (Rapor Bölüm 12).
      if (bagli && _kuyruktaBekleyen > 0) await esitle(sessiz: true);
    });
  }

  bool _bagliMi(List<ConnectivityResult> d) =>
      d.isNotEmpty && !d.contains(ConnectivityResult.none);

  Future<void> _kuyrukSay() async {
    final n = (await widget.kuyruk.hepsi()).length;
    if (mounted) setState(() => _kuyruktaBekleyen = n);
  }

  /// Kuyruğu sunucuya gönderir.
  ///
  /// Kısmi başarı normaldir: sunucu satır satır sonuç döner, yalnızca
  /// başarısızlar kuyrukta kalır.
  Future<void> esitle({bool sessiz = false}) async {
    final bekleyen = await widget.kuyruk.hepsi();
    if (bekleyen.isEmpty) {
      if (!sessiz) _bildir('Kuyruk zaten boş.');
      return;
    }
    try {
      final s = await widget.api.esitle(bekleyen);
      await widget.kuyruk.sil(s.silinecek);
      // Reddedilen kayıtlara gerekçe yazılır: bildirim kaybolur, kayıt
      // kalır. Kullanıcı Ölçüm ekranını açtığında sorunu orada görür.
      await widget.kuyruk.gerekceleriYaz(s.gerekceler);
      await _kuyrukSay();
      if (!mounted) return;

      // Reddedilen kayıt varsa GEREKÇESİ söylenir ve bildirim ekranda
      // daha uzun kalır: bu, kullanıcının bir şey yapması gereken tek
      // durumdur. Eskiden yalnızca "N kayıt kuyrukta kaldı" yazıyor,
      // neden kaldığı hiçbir yerde görünmüyordu.
      if (s.hatali > 0) {
        final ilk = s.gerekceler.values.isNotEmpty
            ? s.gerekceler.values.first
            : 'Sunucu kaydı kabul etmedi.';
        _bildir(
          '${s.yazilan} kayıt gönderildi. '
          '${s.hatali} kayıt sunucuya yazılamadı: $ilk'
          '${s.hatali > 1 ? " (ve ${s.hatali - 1} kayıt daha)" : ""} '
          'Bu kayıtlar Ölçüm sekmesindeki listede gerekçesiyle '
          'işaretlendi; düzeltip yeniden girmeniz gerekir.',
          uzun: true,
        );
        return;
      }

      _bildir(
        '${s.yazilan} kayıt gönderildi'
        '${s.yinelenen > 0 ? ", ${s.yinelenen} zaten vardı" : ""}.',
      );
    } on ApiHatasi catch (h) {
      // ⚠️ AYRIM ÖNEMLİ. Eskiden her başarısızlık "sonra denenecek" diye
      // geçiştiriliyordu. Sunucunun kaydı REDDETMESİ ile AĞIN KOPMASI
      // aynı şey değildir: ilki kendiliğinden düzelmez, tekrar denemek
      // sonsuza kadar aynı sonucu verir. Kullanıcı hangisiyle karşı
      // karşıya olduğunu bilmelidir.
      if (!sessiz) {
        _bildir('Sunucu kayıtları kabul etmedi: ${h.mesaj}', uzun: true);
      }
    } catch (_) {
      // Buraya yalnızca gerçek ağ/bağlantı arızaları düşer — sahada
      // beklenen durum. Bu bir hata değildir, bu yüzden dili sakin.
      if (!sessiz) {
        _bildir('Gönderilemedi. Kayıtlar cihazda güvende, sonra denenecek.');
      }
    }
  }

  void _bildir(String m, {bool uzun = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(
        content: Text(m),
        // Kullanıcının bir şey yapması gereken bildirim, okunacak kadar
        // durmalıdır; varsayılan 4 saniye iki satırlık bir gerekçeye
        // yetmiyor.
        duration: Duration(seconds: uzun ? 10 : 4),
      ));
  }

  @override
  Widget build(BuildContext context) {
    final sayfalar = [
      YukleEkrani(api: widget.api, cevrimici: _cevrimici),
      OlcumEkrani(
        api: widget.api,
        kuyruk: widget.kuyruk,
        cevrimici: _cevrimici,
        kuyrukDegisti: _kuyrukSay,
        esitle: esitle,
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('ReBuild Vision',
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w600)),
        actions: [
          IconButton(
            // Tema seçimi uygulamada HİÇ YOKTU; koyu tema tek seçenekti.
            // Gündüz güneş altında çalışan saha personeli için bu bir
            // kullanılabilirlik sorunuydu.
            tooltip: widget.koyuTema
                ? 'Açık temaya geç'
                : 'Koyu temaya geç',
            onPressed: () => widget.temaDegistir(),
            icon: Icon(
              widget.koyuTema
                  ? Icons.light_mode_outlined
                  : Icons.dark_mode_outlined,
              size: 20,
            ),
          ),
          IconButton(
            tooltip: 'Çıkış',
            onPressed: widget.cikisYapildi,
            icon: const Icon(Icons.logout, size: 20),
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(30),
          child: _DurumSeridi(
            cevrimici: _cevrimici,
            bekleyen: _kuyruktaBekleyen,
            esitle: esitle,
          ),
        ),
      ),
      body: IndexedStack(index: _sekme, children: sayfalar),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _sekme,
        onDestinationSelected: (i) => setState(() => _sekme = i),
        backgroundColor: Renk.yuzey,
        indicatorColor: Renk.marka.withValues(alpha: 0.18),
        destinations: [
          NavigationDestination(
            icon: Icon(Icons.photo_camera_outlined),
            selectedIcon: Icon(Icons.photo_camera, color: Renk.marka),
            label: 'Görüntü',
          ),
          NavigationDestination(
            icon: Badge(
              isLabelVisible: _kuyruktaBekleyen > 0,
              label: Text('$_kuyruktaBekleyen'),
              backgroundColor: Renk.uyari,
              textColor: Renk.taban,
              child: const Icon(Icons.straighten_outlined),
            ),
            selectedIcon: Icon(Icons.straighten, color: Renk.marka),
            label: 'Ölçüm',
          ),
        ],
      ),
    );
  }
}

/// Bağlantı ve kuyruk durumu — her ekranda görünür.
class _DurumSeridi extends StatelessWidget {
  final bool cevrimici;
  final int bekleyen;
  final Future<void> Function({bool sessiz}) esitle;

  const _DurumSeridi({
    required this.cevrimici,
    required this.bekleyen,
    required this.esitle,
  });

  @override
  Widget build(BuildContext context) {
    // Çevrimdışı olmak bir HATA DEĞİLDİR — sahada beklenen durumdur.
    // Bu yüzden kırmızı değil, nötr/uyarı tonunda gösterilir.
    final (renk, metin) = !cevrimici
        ? (Renk.uyari, 'Çevrimdışı · kayıtlar cihazda şifreli tutuluyor')
        : bekleyen > 0
            ? (Renk.bilgi, '$bekleyen kayıt gönderilmeyi bekliyor')
            : (Renk.metin4, 'Çevrimiçi · kuyruk boş');

    return Container(
      width: double.infinity,
      color: Renk.yuzey2,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Row(
        children: [
          Icon(
            !cevrimici
                ? Icons.cloud_off_outlined
                : bekleyen > 0
                    ? Icons.cloud_upload_outlined
                    : Icons.cloud_done_outlined,
            size: 15,
            color: renk,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(metin,
                style: TextStyle(color: renk, fontSize: 12)),
          ),
          if (cevrimici && bekleyen > 0)
            TextButton(
              onPressed: () => esitle(),
              style: TextButton.styleFrom(
                minimumSize: const Size(0, 30),
                padding: const EdgeInsets.symmetric(horizontal: 10),
                foregroundColor: Renk.bilgi,
              ),
              child: const Text('Şimdi gönder',
                  style: TextStyle(fontSize: 12)),
            ),
        ],
      ),
    );
  }
}
