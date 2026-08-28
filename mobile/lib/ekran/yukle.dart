import 'dart:io';

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';

import '../api.dart';
import '../tema.dart';

/// Görüntü çekme/seçme + konum — P2, madde 7.
///
/// Görüntü yükleme çevrimiçi olmayı gerektirir: sınıflandırma sunucudaki
/// modelde yapılır. Çevrimdışıyken kullanıcıya bu açıkça söylenir;
/// fotoğraflar sessizce kaybolmaz, kullanıcı bağlantı gelince tekrar
/// dener.
class YukleEkrani extends StatefulWidget {
  final Api api;
  final bool cevrimici;

  const YukleEkrani({super.key, required this.api, required this.cevrimici});

  @override
  State<YukleEkrani> createState() => _YukleDurumu();
}

class _YukleDurumu extends State<YukleEkrani> {
  final _secici = ImagePicker();

  List<EnkazAlani> _alanlar = [];
  int? _seciliAlan;
  final List<File> _dosyalar = [];
  Position? _konum;
  bool _yukleniyor = false;
  String _hata = '';
  Map<String, dynamic>? _sonuc;

  @override
  void initState() {
    super.initState();
    _alanlariGetir();
  }

  Future<void> _alanlariGetir() async {
    try {
      final a = await widget.api.alanlar();
      if (!mounted) return;
      setState(() {
        _alanlar = a;
        if (a.length == 1) _seciliAlan = a.first.id;
      });
    } catch (_) {
      if (mounted) {
        setState(() => _hata = 'Saha listesi alınamadı. Bağlantı gerekiyor.');
      }
    }
  }

  Future<void> _konumAl() async {
    try {
      var izin = await Geolocator.checkPermission();
      if (izin == LocationPermission.denied) {
        izin = await Geolocator.requestPermission();
      }
      if (izin == LocationPermission.denied ||
          izin == LocationPermission.deniedForever) {
        return;
      }
      final k = await Geolocator.getCurrentPosition();
      if (mounted) setState(() => _konum = k);
    } catch (_) {
      // Konum alınamazsa yükleme yine yapılır; konum isteğe bağlıdır.
    }
  }

  Future<void> _secKamera() async {
    final x = await _secici.pickImage(
      source: ImageSource.camera,
      imageQuality: 88,
    );
    if (x == null) return;
    setState(() => _dosyalar.add(File(x.path)));
    await _konumAl();
  }

  Future<void> _secGaleri() async {
    final liste = await _secici.pickMultiImage(imageQuality: 88);
    if (liste.isEmpty) return;
    setState(() => _dosyalar.addAll(liste.map((x) => File(x.path))));
  }

  Future<void> _gonder() async {
    if (_seciliAlan == null || _dosyalar.isEmpty) return;
    setState(() {
      _hata = '';
      _yukleniyor = true;
      _sonuc = null;
    });
    try {
      final s = await widget.api.goruntuYukle(
        _seciliAlan!,
        _dosyalar,
        enlem: _konum?.latitude,
        boylam: _konum?.longitude,
      );
      if (!mounted) return;
      setState(() {
        _sonuc = s;
        _dosyalar.clear();
      });
    } catch (_) {
      if (mounted) {
        setState(() => _hata =
            'Yükleme başarısız. Fotoğraflar listede duruyor; '
            'bağlantı geldiğinde tekrar deneyin.');
      }
    } finally {
      if (mounted) setState(() => _yukleniyor = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (!widget.cevrimici)
          _Not(
            renk: Renk.uyari,
            ikon: Icons.cloud_off_outlined,
            metin: 'Görüntü yükleme bağlantı gerektirir: sınıflandırma '
                'sunucudaki modelde yapılır. Fotoğrafları şimdi çekebilir, '
                'bağlantı geldiğinde gönderebilirsiniz.',
          ),

        const SizedBox(height: 4),
        const Text('Enkaz alanı',
            style: TextStyle(
                color: Renk.metin2, fontSize: 12, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        DropdownButtonFormField<int>(
          initialValue: _seciliAlan,
          hint: const Text('Alan seçin…'),
          dropdownColor: Renk.yuzey2,
          items: _alanlar
              .map((a) => DropdownMenuItem(value: a.id, child: Text(a.ad)))
              .toList(),
          onChanged: (v) => setState(() => _seciliAlan = v),
        ),

        const SizedBox(height: 20),
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: _secKamera,
                icon: const Icon(Icons.photo_camera_outlined, size: 20),
                label: const Text('Fotoğraf çek'),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: _secGaleri,
                icon: const Icon(Icons.photo_library_outlined, size: 20),
                label: const Text('Galeriden'),
              ),
            ),
          ],
        ),

        if (_konum != null) ...[
          const SizedBox(height: 12),
          Row(
            children: [
              const Icon(Icons.place_outlined, size: 15, color: Renk.metin4),
              const SizedBox(width: 6),
              Text(
                '${_konum!.latitude.toStringAsFixed(5)}, '
                '${_konum!.longitude.toStringAsFixed(5)}',
                style: const TextStyle(
                    color: Renk.metin4,
                    fontSize: 12,
                    fontFeatures: [FontFeature.tabularFigures()]),
              ),
            ],
          ),
        ],

        if (_dosyalar.isNotEmpty) ...[
          const SizedBox(height: 18),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('${_dosyalar.length} fotoğraf seçildi',
                  style: const TextStyle(color: Renk.metin2, fontSize: 13)),
              TextButton(
                onPressed: () => setState(_dosyalar.clear),
                child: const Text('Temizle',
                    style: TextStyle(fontSize: 12, color: Renk.metin3)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          GridView.count(
            crossAxisCount: 3,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
            children: _dosyalar
                .map((d) => ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.file(d, fit: BoxFit.cover),
                    ))
                .toList(),
          ),
          const SizedBox(height: 16),
          FilledButton(
            onPressed:
                (_yukleniyor || _seciliAlan == null || !widget.cevrimici)
                    ? null
                    : _gonder,
            child: Text(
              _yukleniyor
                  ? 'Gönderiliyor…'
                  : !widget.cevrimici
                      ? 'Bağlantı bekleniyor'
                      : _seciliAlan == null
                          ? 'Önce alan seçin'
                          : '${_dosyalar.length} fotoğrafı gönder',
            ),
          ),
        ],

        if (_hata.isNotEmpty) ...[
          const SizedBox(height: 14),
          _Not(renk: Renk.dikkat, ikon: Icons.error_outline, metin: _hata),
        ],

        if (_sonuc != null) ...[
          const SizedBox(height: 18),
          _SonucKarti(sonuc: _sonuc!),
        ],

        const SizedBox(height: 28),
        const Text(
          'Sistem yalnızca görünür yüzeye ilişkin ön değerlendirme yapar; '
          'enkaz altı içerik değerlendirilmez.',
          style: TextStyle(color: Renk.metin4, fontSize: 11, height: 1.5),
        ),
      ],
    );
  }
}

class _SonucKarti extends StatelessWidget {
  final Map<String, dynamic> sonuc;
  const _SonucKarti({required this.sonuc});

  @override
  Widget build(BuildContext context) {
    final goruntuler = (sonuc['goruntuler'] as List?) ?? [];
    final tespitler =
        goruntuler.expand((g) => (g['tespitler'] as List? ?? [])).toList();
    final kuyruga = sonuc['inceleme_kuyruguna_dusen'] as int? ?? 0;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${goruntuler.length} görüntü işlendi · '
              '${tespitler.length} tespit bulundu',
              style: const TextStyle(
                  color: Renk.metin, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 4),
            Text(
              kuyruga > 0
                  ? 'Düşük güvenli $kuyruga tespit otomatik olarak uzman '
                      'incelemesine gitti.'
                  : 'Uzman incelemesi gerektiren tespit çıkmadı.',
              style: const TextStyle(
                  color: Renk.metin3, fontSize: 12, height: 1.4),
            ),
            const SizedBox(height: 12),
            ...tespitler.map((t) {
              final m = t as Map<String, dynamic>;
              final sinif = (m['duzeltilen_sinif'] ?? m['sinif']) as String;
              final guven = (m['guven_skoru'] as num).toDouble();
              final inceleme = (m['inceleme_gerekli'] ?? false) as bool;
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                        color: Renk.sinif(sinif),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(sinif,
                          style: const TextStyle(
                              color: Renk.metin2, fontSize: 13)),
                    ),
                    // Güven skoru yuvarlanmaz (ana talimat Bölüm 9.2).
                    Text(
                      '%${(guven * 100).toStringAsFixed(guven * 100 % 1 == 0 ? 0 : 1)}',
                      style: TextStyle(
                        color: inceleme ? Renk.uyari : Renk.metin3,
                        fontSize: 13,
                        fontFeatures: const [FontFeature.tabularFigures()],
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Her model çıktısı "ön tahmin"dir, istisnasız.
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Renk.yuzey3,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text('ÖN TAHMİN',
                          style: TextStyle(
                              color: Renk.metin3,
                              fontSize: 9,
                              letterSpacing: 0.5)),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}

class _Not extends StatelessWidget {
  final Color renk;
  final IconData ikon;
  final String metin;

  const _Not({required this.renk, required this.ikon, required this.metin});

  @override
  Widget build(BuildContext context) {
    return Container(
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
            child: Text(metin,
                style: TextStyle(color: renk, fontSize: 12, height: 1.45)),
          ),
        ],
      ),
    );
  }
}
