import 'package:flutter/material.dart';

import 'api.dart';
import 'ekran/giris.dart';
import 'ekran/kabuk.dart';
import 'kuyruk.dart';
import 'tema.dart';

void main() => runApp(const Uygulama());

class Uygulama extends StatefulWidget {
  const Uygulama({super.key});

  @override
  State<Uygulama> createState() => _UygulamaDurumu();
}

class _UygulamaDurumu extends State<Uygulama> {
  final api = Api();
  final kuyruk = Kuyruk();

  Kullanici? _kullanici;
  bool _yukleniyor = true;

  /// Koyu tema seçili mi?
  ///
  /// ⚠️ UYGULAMA KOYU TEMAYA SABİTLENMİŞTİ. `theme: koyuTema()` tek
  /// seçenekti; ne açık tema paleti, ne de bir seçim vardı. Web arayüzü
  /// varsayılan açık temaya çevrildikten sonra aynı sistemin iki yüzü
  /// birbirini tutmuyordu.
  ///
  /// Varsayılan AÇIK: gündüz, güneş altında, eldivenli bir saha
  /// personelinin okuyacağı ekran budur. Koyu tema kaldırılmadı —
  /// gece çalışmasında ve pil ömründe gerçek bir yararı var — ama artık
  /// bir tercih, tek seçenek değil.
  bool _koyuTema = false;

  @override
  void initState() {
    super.initState();
    _temayiOku();
    _oturumKontrol();
  }

  Future<void> _temayiOku() async {
    final koyu = await api.temaKoyuMu();
    if (mounted) setState(() => _koyuTema = koyu);
  }

  Future<void> _temaDegistir() async {
    final yeni = !_koyuTema;
    setState(() => _koyuTema = yeni);
    await api.temaKaydet(koyu: yeni);
  }

  Future<void> _oturumKontrol() async {
    try {
      final k = await api.ben();
      if (mounted) setState(() => _kullanici = k);
    } catch (_) {
      // Sunucuya ulaşılamıyor olabilir — saha uygulamasında bu normaldir.
      // Kullanıcıyı giriş ekranına düşürüp devam ediyoruz; kuyruktaki
      // kayıtlar zaten cihazda duruyor.
      if (mounted) setState(() => _kullanici = null);
    } finally {
      if (mounted) setState(() => _yukleniyor = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ReBuild Vision',
      debugShowCheckedModeBanner: false,
      theme: uygulamaTemasi(koyu: _koyuTema),
      home: _yukleniyor
          ? Scaffold(
              body: Center(child: CircularProgressIndicator(color: Renk.marka)),
            )
          : _kullanici == null
              ? GirisEkrani(
                  api: api,
                  girisYapildi: (k) => setState(() => _kullanici = k),
                  koyuTema: _koyuTema,
                  temaDegistir: _temaDegistir,
                )
              : Kabuk(
                  api: api,
                  kuyruk: kuyruk,
                  kullanici: _kullanici!,
                  koyuTema: _koyuTema,
                  temaDegistir: _temaDegistir,
                  cikisYapildi: () async {
                    await api.jetonSil();
                    if (mounted) setState(() => _kullanici = null);
                  },
                ),
    );
  }
}
