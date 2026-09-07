/// Roller ve mobil uygulamada NE YAPABİLECEKLERİ.
///
/// ⚠️ BU DOSYA BİR ARIZANIN ÜZERİNE AÇILDI.
///
/// Mobil uygulama `Kullanici.rol` alanını sunucudan OKUYOR ama HİÇBİR
/// YERDE KULLANMIYORDU (`api.dart` → `Kullanici.rol`; başka referans
/// yok). Sonuç: hangi rolle girilirse girilsin ekranda aynı iki sekme
/// vardı — "Görüntü" ve "Ölçüm". Yani:
///
///   - **Belediye yetkilisi** giriş yapınca saha personelinin ekranını
///     görüyordu. Kendi işi (alan tanımlama, dağılım izleme, rapor)
///     hiçbir yerde yoktu ve bunun web arayüzünde olduğu da
///     söylenmiyordu. Kullanıcının bildirdiği arıza tam olarak budur.
///   - **AFAD, yıkım firması ve tesis operatörü** — sunucuda ne görüntü
///     yükleme ne ölçüm girme yetkisi olan üç rol — kendilerine kapalı
///     iki formla karşılaşıyordu. Düğmeye bastıklarında sunucudan 403
///     dönüyordu: uygulama, yapılamayacak bir işi yapılabilirmiş gibi
///     gösteriyordu.
///   - **Doğrulayıcı uzman** görüntü yükleme sekmesini görüyordu; sunucu
///     ona bu yetkiyi vermiyor (`GORUNTU_YUKLEYEBILIR`).
///   - **Rolü henüz atanmamış** (onay bekleyen) hesap da aynı ekranı
///     görüyordu.
///
/// TASARIM KARARI: mobil uygulama SAHA uygulamasıdır ve öyle kalır.
/// Harita, inceleme kuyruğu, işlem geçmişi, rapor ve rol onayı ekranları
/// web arayüzündedir; bunları telefona taşımak bu turun işi değil. Ama
/// "yalnızca saha akışı var" demek, "herkese saha akışını göster"
/// demek DEĞİLDİR. Uygulama artık:
///
///   1. Sekmeleri rolün SUNUCUDAKİ yetkisine göre kurar — kullanıcı
///      yalnızca gerçekten yapabileceği işi görür.
///   2. Her role, kendi işinin nerede olduğunu açıkça söyleyen bir
///      "Hesap" ekranı gösterir (bkz. `ekran/hesap.dart`).
///   3. Asıl işi mobilde OLMAYAN rolleri girişten sonra doğrudan o
///      ekrana düşürür — sessizce yanlış ekran göstermez.
///
/// ⚠️ BU DOSYA YALNIZCA ARAYÜZ İÇİNDİR. Yetki kontrolü sunucudadır
/// (`api/app/core/permissions.py`); buradaki gizleme kolaylıktır,
/// güvenlik değildir. İki tarafın ayrışmaması `test/roller_test.dart`
/// ile bağlanmıştır: o test bu dosyayı deponun `permissions.py`
/// dosyasıyla karşılaştırır.
library;

/// Mobil uygulamadaki ekranlar.
///
/// Web'deki `SayfaAdi` listesinin mobilde karşılığı olan alt kümesi.
/// `hesap` mobile özgüdür: web'de rolün görevi ana sayfada bir cümleyle
/// yazılıdır (`roller.ts` → `sayfaGorevi`), mobilde ise anlatılacak
/// fazladan bir şey var — hangi ekranın burada OLMADIĞI.
enum MobilEkran { yukle, olcum, hesap }

/// Rol tanımı — ad, görev cümlesi ve mobil yetkiler.
///
/// `ad` ve `gorev` alanları `web/src/roller.ts` ile birebir aynıdır;
/// aynı kullanıcı iki arayüzde kendi rolünü aynı adla görmelidir.
class RolTanimi {
  /// Rolün ekranda görünen adı — "Belediye yetkilisi" gibi.
  final String ad;

  /// Rolün tek cümlelik görevi (web'deki `gorev` ile aynı).
  final String gorev;

  /// Sunucu bu role görüntü yüklettiriyor mu?
  /// (`permissions.GORUNTU_YUKLEYEBILIR`)
  final bool goruntuYukleyebilir;

  /// Sunucu bu role ölçüm girdiriyor mu?
  /// (`permissions.OLCUM_GIREBILIR`)
  final bool olcumGirebilir;

  /// Rolün asıl işi mobilde mi yapılıyor?
  ///
  /// Saha personeli ve yönetici için evet. Belediye yetkilisi görüntü
  /// YÜKLEYEBİLİR ama asıl işi (alan tanımlama, dağılım izleme, rapor)
  /// web'dedir; bu yüzden girişte doğrudan yükleme formuna düşürülmez,
  /// önce nerede ne olduğunu anlatan ekranı görür.
  final bool asilIsiMobilde;

  /// Bu rolün web arayüzünde bulacağı ekranlar — Hesap ekranında
  /// listelenir. Kaynak: `web/src/roller.ts` → `ROLLER[rol].menu`,
  /// mobilde karşılığı olmayanlar.
  final List<String> webEkranlari;

  const RolTanimi({
    required this.ad,
    required this.gorev,
    required this.goruntuYukleyebilir,
    required this.olcumGirebilir,
    required this.asilIsiMobilde,
    required this.webEkranlari,
  });

  /// Bu rolün mobilde kullanabileceği sekmeler, sırayla.
  ///
  /// "Hesap" her zaman vardır: yetkisi olmayan rolün de rolünü, görevini
  /// ve işinin nerede olduğunu görebilmesi gerekir. Boş bir uygulama
  /// açılışı, yanlış ekran kadar kötüdür.
  List<MobilEkran> get ekranlar => [
        if (goruntuYukleyebilir) MobilEkran.yukle,
        if (olcumGirebilir) MobilEkran.olcum,
        MobilEkran.hesap,
      ];

  /// Girişten sonra açılacak sekmenin sıradaki yeri.
  ///
  /// Asıl işi mobilde olan rol doğrudan işine düşer; olmayan rol önce
  /// açıklamayı görür. Web'deki `anaSayfa` alanının mobil karşılığı.
  int get acilisSekmesi => asilIsiMobilde ? 0 : ekranlar.length - 1;
}

/// Rol anahtarları — sunucunun `Rol` enum DEĞERLERİ ile birebir aynı.
///
/// Anahtarlar sunucudan gelen ham dizedir (`kullanici.rol`); burada
/// çevrilmez, eşlenir.
const roller = <String, RolTanimi>{
  'saha': RolTanimi(
    ad: 'Saha personeli',
    gorev: 'Sahadan görüntü yükleyin ve ölçüm girin.',
    goruntuYukleyebilir: true,
    olcumGirebilir: true,
    asilIsiMobilde: true,
    webEkranlari: ['Enkaz alanları', 'Malzeme haritası'],
  ),
  'uzman': RolTanimi(
    ad: 'Doğrulayıcı uzman',
    gorev: 'Model güveni düşük tespitleri inceleyin ve karara bağlayın.',
    // Sunucu uzmana görüntü YÜKLETMİYOR (GORUNTU_YUKLEYEBILIR).
    goruntuYukleyebilir: false,
    olcumGirebilir: true,
    // Asıl işi inceleme kuyruğu — mobilde yok.
    asilIsiMobilde: false,
    webEkranlari: [
      'İnceleme kuyruğu',
      'Enkaz alanları',
      'Malzeme haritası',
      'İşlem geçmişi',
    ],
  ),
  'belediye': RolTanimi(
    ad: 'Belediye yetkilisi',
    gorev: 'Enkaz alanlarını tanımlayın ve malzeme dağılımını izleyin.',
    goruntuYukleyebilir: true,
    // Sunucu belediyeye ölçüm GİRDİRMİYOR (OLCUM_GIREBILIR).
    olcumGirebilir: false,
    asilIsiMobilde: false,
    webEkranlari: [
      'Enkaz alanları',
      'Malzeme haritası',
      'İşlem geçmişi',
      'Rapor indirme',
    ],
  ),
  'afad': RolTanimi(
    ad: 'AFAD yetkilisi',
    gorev: 'Sahaları ve doğrulanmış malzeme dağılımını izleyin.',
    goruntuYukleyebilir: false,
    olcumGirebilir: false,
    asilIsiMobilde: false,
    webEkranlari: [
      'Malzeme haritası',
      'Enkaz alanları',
      'İşlem geçmişi',
      'Rapor indirme',
    ],
  ),
  'yikim': RolTanimi(
    ad: 'Yıkım firması',
    gorev: 'Size atanmış sahaları görüntüleyin.',
    goruntuYukleyebilir: false,
    olcumGirebilir: false,
    asilIsiMobilde: false,
    webEkranlari: ['Enkaz alanları', 'Malzeme haritası'],
  ),
  'tesis': RolTanimi(
    ad: 'Tesis operatörü',
    gorev: 'Size yönlendirilen malzeme kayıtlarını görüntüleyin.',
    goruntuYukleyebilir: false,
    olcumGirebilir: false,
    asilIsiMobilde: false,
    webEkranlari: ['Malzeme haritası', 'Enkaz alanları'],
  ),
  'yonetici': RolTanimi(
    ad: 'Yönetici',
    gorev: 'Sistemin tamamına erişiminiz var.',
    goruntuYukleyebilir: true,
    olcumGirebilir: true,
    asilIsiMobilde: true,
    webEkranlari: [
      'Enkaz alanları',
      'İnceleme kuyruğu',
      'Malzeme haritası',
      'İşlem geçmişi',
      'Rol onayları',
    ],
  ),
};

/// Rolü atanmamış hesap için güvenli varsayılan.
///
/// Sunucu kayıt sırasında rolü `null` bırakır ve yönetici atar
/// (`api/app/routers/auth.py`). O ana kadar hesap HİÇBİR ŞEY yapamaz —
/// uygulama da öyle davranmalıdır. Web'deki `VARSAYILAN` ile aynı
/// mantık.
const rolYok = RolTanimi(
  ad: 'Rol atanmadı',
  gorev: 'Hesabınız yönetici onayı bekliyor.',
  goruntuYukleyebilir: false,
  olcumGirebilir: false,
  asilIsiMobilde: false,
  webEkranlari: [],
);

/// Sunucudan gelen rol dizesini tanıma çevirir.
///
/// Tanınmayan bir rol gelirse (sunucuya yeni rol eklenmiş, mobil
/// güncellenmemiş) yetkisiz varsayılana düşülür: uydurulmuş bir yetkiyle
/// kullanıcıyı 403'e göndermektense hiçbir şey vaat etmemek doğrudur.
/// Ad ise gizlenmez, ham hâliyle gösterilir — kullanıcı bir tuhaflık
/// olduğunu görebilmelidir (`tema.dart` → `sinifAdi` ile aynı ilke).
RolTanimi rolTanimi(String? rol) {
  if (rol == null) return rolYok;
  final t = roller[rol];
  if (t != null) return t;
  return RolTanimi(
    ad: rol,
    gorev: 'Bu rol mobil uygulamada tanınmıyor. '
        'Uygulamayı güncelleyin ya da web arayüzünü kullanın.',
    goruntuYukleyebilir: false,
    olcumGirebilir: false,
    asilIsiMobilde: false,
    webEkranlari: const [],
  );
}
