import 'dart:math';

import 'package:flutter/material.dart';

import '../api.dart';
import '../kuyruk.dart';
import '../tema.dart';

/// Ölçüm girişi + çevrimdışı kuyruk — P2, madde 8, 9 ve 10.
///
/// Ölçüm girişi **çevrimdışı çalışır**: kayıt cihazda şifreli kuyruğa
/// yazılır, bağlantı gelince kendiliğinden gönderilir. Saha personeli
/// bağlantı beklemek zorunda kalmaz.
class OlcumEkrani extends StatefulWidget {
  final Api api;
  final Kuyruk kuyruk;
  final bool cevrimici;
  final Future<void> Function() kuyrukDegisti;
  final Future<void> Function({bool sessiz}) esitle;

  const OlcumEkrani({
    super.key,
    required this.api,
    required this.kuyruk,
    required this.cevrimici,
    required this.kuyrukDegisti,
    required this.esitle,
  });

  @override
  State<OlcumEkrani> createState() => _OlcumDurumu();
}

class _OlcumDurumu extends State<OlcumEkrani> {
  static const _turler = {
    'agirlik': ('Ağırlık', 'ton'),
    'hacim': ('Hacim', 'm³'),
    'alan': ('Görünür alan', 'm²'),
  };

  final _deger = TextEditingController();
  final _yontem = TextEditingController();

  List<EnkazAlani> _alanlar = [];
  int? _seciliAlan;
  List<Tespit> _tespitler = [];
  int? _seciliTespit;
  String _tur = 'agirlik';
  String _hata = '';
  List<KuyrukKaydi> _bekleyen = [];

  @override
  void initState() {
    super.initState();
    _alanlariGetir();
    _kuyrugu();
  }

  @override
  void dispose() {
    _deger.dispose();
    _yontem.dispose();
    super.dispose();
  }

  Future<void> _alanlariGetir() async {
    try {
      final a = await widget.api.alanlar();
      if (!mounted) return;
      setState(() {
        _alanlar = a;
        if (a.length == 1) _seciliAlan = a.first.id;
      });
      if (_seciliAlan != null) await _tespitleriGetir(_seciliAlan!);
    } catch (_) {
      // Çevrimdışıyken liste alınamaz; kuyruk yine de kullanılabilir.
    }
  }

  Future<void> _tespitleriGetir(int alanId) async {
    try {
      final t = await widget.api.alanTespitleri(alanId);
      if (mounted) setState(() => _tespitler = t);
    } catch (_) {/* çevrimdışı */}
  }

  Future<void> _kuyrugu() async {
    final k = await widget.kuyruk.hepsi();
    if (mounted) setState(() => _bekleyen = k);
  }

  /// Cihazda benzersiz kimlik üretir.
  ///
  /// Ağ koptuğunda istemci isteği tekrarlar ama sonucu bilemez; sunucu bu
  /// kimliğe bakıp aynı ölçümü iki kez yazmaz.
  String _yerelKimlik() {
    final r = Random.secure();
    final ek = List.generate(8, (_) => r.nextInt(16).toRadixString(16)).join();
    return '${DateTime.now().microsecondsSinceEpoch}-$ek';
  }

  Future<void> _kaydet() async {
    final deger = double.tryParse(_deger.text.trim().replaceAll(',', '.'));
    if (_seciliTespit == null) {
      setState(() => _hata = 'Önce bir tespit seçin.');
      return;
    }
    if (deger == null || deger <= 0) {
      setState(() => _hata = 'Ölçüm değeri sıfırdan büyük bir sayı olmalı.');
      return;
    }
    if (_yontem.text.trim().isEmpty) {
      // Yöntem izlenebilirlik için zorunlu: ölçümün nasıl yapıldığı
      // bilinmeden miktarın dayanağı da bilinemez.
      setState(() => _hata = 'Ölçümün nasıl yapıldığını yazın.');
      return;
    }

    await widget.kuyruk.ekle(KuyrukKaydi(
      yerelKimlik: _yerelKimlik(),
      tespitId: _seciliTespit!,
      tur: _tur,
      deger: deger,
      birim: _turler[_tur]!.$2 == 'm³' ? 'm3' : _turler[_tur]!.$2,
      yontem: _yontem.text.trim(),
      olusturma: DateTime.now(),
    ));

    _deger.clear();
    _yontem.clear();
    setState(() => _hata = '');
    await _kuyrugu();
    await widget.kuyrukDegisti();

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
      content: Text('Ölçüm kuyruğa alındı — cihazda şifreli tutuluyor.'),
    ));

    // Bağlantı varsa hemen gönder; yoksa kuyrukta bekler.
    if (widget.cevrimici) await widget.esitle(sessiz: true);
    await _kuyrugu();
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('Ölçüm gir',
            style: TextStyle(
                fontSize: 18, fontWeight: FontWeight.w700, color: Renk.metin)),
        const SizedBox(height: 6),
        const Text(
          'Ölçüm girilmeyen tespitlerde sistem miktar hesaplamaz — '
          'tahmin uydurmaz. Girilen ölçüm belirsizlik aralığıyla sonuç verir.',
          style: TextStyle(color: Renk.metin3, fontSize: 12, height: 1.5),
        ),
        const SizedBox(height: 20),

        DropdownButtonFormField<int>(
          initialValue: _seciliAlan,
          hint: const Text('Enkaz alanı seçin…'),
          dropdownColor: Renk.yuzey2,
          decoration: const InputDecoration(labelText: 'Enkaz alanı'),
          items: _alanlar
              .map((a) => DropdownMenuItem(value: a.id, child: Text(a.ad)))
              .toList(),
          onChanged: (v) {
            setState(() {
              _seciliAlan = v;
              _seciliTespit = null;
              _tespitler = [];
            });
            if (v != null) _tespitleriGetir(v);
          },
        ),
        const SizedBox(height: 14),

        DropdownButtonFormField<int>(
          initialValue: _seciliTespit,
          hint: Text(_tespitler.isEmpty
              ? 'Tespit yok — bağlantı gerekiyor'
              : 'Tespit seçin…'),
          dropdownColor: Renk.yuzey2,
          decoration: const InputDecoration(labelText: 'Tespit'),
          isExpanded: true,
          items: _tespitler
              .map((t) => DropdownMenuItem(
                    value: t.id,
                    child: Row(
                      children: [
                        Container(
                          width: 10,
                          height: 10,
                          decoration: BoxDecoration(
                            color: Renk.sinif(t.gecerliSinif),
                            borderRadius: BorderRadius.circular(3),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(child: Text('#${t.id} · ${t.gecerliSinif}')),
                      ],
                    ),
                  ))
              .toList(),
          onChanged: (v) => setState(() => _seciliTespit = v),
        ),
        const SizedBox(height: 14),

        SegmentedButton<String>(
          segments: _turler.entries
              .map((e) => ButtonSegment(
                    value: e.key,
                    label: Text(e.value.$1, style: const TextStyle(fontSize: 12)),
                  ))
              .toList(),
          selected: {_tur},
          onSelectionChanged: (s) => setState(() => _tur = s.first),
          style: SegmentedButton.styleFrom(
            selectedBackgroundColor: Renk.marka.withValues(alpha: 0.2),
            selectedForegroundColor: Renk.marka,
          ),
        ),
        const SizedBox(height: 14),

        TextField(
          controller: _deger,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: InputDecoration(
            labelText: 'Değer (${_turler[_tur]!.$2})',
            hintText: 'örn. 12,4',
          ),
        ),
        const SizedBox(height: 14),

        TextField(
          controller: _yontem,
          decoration: const InputDecoration(
            labelText: 'Ölçüm yöntemi',
            hintText: 'örn. Saha kantar ölçümü',
            helperText: 'Kim, neyle, nasıl ölçtü? İşlem geçmişine kaydedilir.',
            helperMaxLines: 2,
          ),
        ),

        if (_hata.isNotEmpty) ...[
          const SizedBox(height: 12),
          Text(_hata,
              style: const TextStyle(color: Renk.dikkat, fontSize: 13)),
        ],

        const SizedBox(height: 18),
        FilledButton.icon(
          onPressed: _kaydet,
          icon: const Icon(Icons.save_outlined, size: 20),
          label: Text(widget.cevrimici
              ? 'Ölçümü kaydet ve gönder'
              : 'Ölçümü kuyruğa al'),
        ),

        if (_bekleyen.isNotEmpty) ...[
          const SizedBox(height: 28),
          const Divider(),
          const SizedBox(height: 14),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Kuyrukta ${_bekleyen.length} kayıt',
                  style: const TextStyle(
                      color: Renk.metin2, fontWeight: FontWeight.w600)),
              if (widget.cevrimici)
                TextButton(
                  onPressed: () async {
                    await widget.esitle();
                    await _kuyrugu();
                  },
                  child: const Text('Şimdi gönder'),
                ),
            ],
          ),
          const SizedBox(height: 4),
          const Text(
            'Kayıtlar cihazda şifreli olarak saklanır; uygulama kapansa da '
            'kaybolmaz.',
            style: TextStyle(color: Renk.metin4, fontSize: 11, height: 1.4),
          ),
          const SizedBox(height: 10),
          ..._bekleyen.map((k) => Card(
                child: ListTile(
                  dense: true,
                  leading: const Icon(Icons.schedule,
                      size: 18, color: Renk.metin4),
                  title: Text(
                    'Tespit #${k.tespitId} · ${k.deger} ${k.birim}',
                    style: const TextStyle(fontSize: 13, color: Renk.metin2),
                  ),
                  subtitle: Text(
                    k.yontem,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 11, color: Renk.metin4),
                  ),
                ),
              )),
        ],
      ],
    );
  }
}
