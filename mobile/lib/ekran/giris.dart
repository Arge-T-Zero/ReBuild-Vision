import 'package:flutter/material.dart';

import '../api.dart';
import '../tema.dart';

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

class _GirisDurumu extends State<GirisEkrani> {
  final _eposta = TextEditingController();
  final _parola = TextEditingController();
  String _hata = '';
  bool _bekliyor = false;

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
      setState(() => _hata = h.mesaj);
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
      // Tema düğmesi giriş ekranında da durur: kullanıcının ilk gördüğü
      // ekran budur ve tercihini oturum açmadan önce yapabilmelidir.
      // Web arayüzünde de aynı yerde.
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            tooltip: widget.koyuTema ? 'Açık temaya geç' : 'Koyu temaya geç',
            onPressed: () => widget.temaDegistir(),
            icon: Icon(
              widget.koyuTema
                  ? Icons.light_mode_outlined
                  : Icons.dark_mode_outlined,
              size: 20,
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // ⚠️ `CrossAxisAlignment.stretch` ALT ÖGELERİN GENİŞLİĞİNİ
                  // EZİYOR. Bu kutu `width: 44` yazmasına rağmen 420 px'e
                  // yayılıyor, logo 44x44 kare yerine geniş bir şerit
                  // olarak çiziliyordu — giriş ekranının ilk göze çarpan
                  // ögesinde. `Align` sarmalayıcısı esnetmeyi keser.
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: Renk.marka.withValues(alpha: 0.15),
                      border: Border.all(
                        color: Renk.marka.withValues(alpha: 0.4),
                      ),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(Icons.layers_outlined,
                        color: Renk.marka, size: 22),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text('ReBuild Vision',
                      style: TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.w700,
                          color: Renk.metin)),
                  const SizedBox(height: 6),
                  Text(
                    'Saha uygulaması — çevrimdışı çalışır',
                    style: TextStyle(color: Renk.metin3, fontSize: 14),
                  ),
                  const SizedBox(height: 32),
                  TextField(
                    controller: _eposta,
                    keyboardType: TextInputType.emailAddress,
                    autocorrect: false,
                    decoration: const InputDecoration(labelText: 'E-posta'),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _parola,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: 'Parola'),
                    onSubmitted: (_) => _gonder(),
                  ),
                  if (_hata.isNotEmpty) ...[
                    const SizedBox(height: 14),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Renk.dikkat.withValues(alpha: 0.1),
                        border: Border.all(
                          color: Renk.dikkat.withValues(alpha: 0.3),
                        ),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(_hata,
                          style: TextStyle(
                              color: Renk.dikkat, fontSize: 13)),
                    ),
                  ],
                  const SizedBox(height: 22),
                  FilledButton(
                    onPressed: _bekliyor ? null : _gonder,
                    child: Text(_bekliyor ? 'Giriş yapılıyor…' : 'Giriş yap'),
                  ),
                  const SizedBox(height: 28),
                  Text(
                    'Model çıktıları ön tahmindir. Sistem tehlikeli madde '
                    'teşhisi yapmaz ve yalnızca görünür yüzeyi değerlendirir.',
                    style: TextStyle(
                        color: Renk.metin4, fontSize: 12, height: 1.5),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
