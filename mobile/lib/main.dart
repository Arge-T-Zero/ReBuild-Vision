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

  @override
  void initState() {
    super.initState();
    _oturumKontrol();
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
      theme: koyuTema(),
      home: _yukleniyor
          ? const Scaffold(
              body: Center(child: CircularProgressIndicator(color: Renk.marka)),
            )
          : _kullanici == null
              ? GirisEkrani(
                  api: api,
                  girisYapildi: (k) => setState(() => _kullanici = k),
                )
              : Kabuk(
                  api: api,
                  kuyruk: kuyruk,
                  kullanici: _kullanici!,
                  cikisYapildi: () async {
                    await api.jetonSil();
                    if (mounted) setState(() => _kullanici = null);
                  },
                ),
    );
  }
}
