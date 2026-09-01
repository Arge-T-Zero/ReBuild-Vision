# mobile — ReBuild Vision saha uygulaması

Flutter. Saha personelinin görüntü yükleyip ölçüm girdiği, **çevrimdışı
çalışabilen** uygulama.

## Neden çevrimdışı

Saha personeli çoğu zaman bağlantısız çalışır. Rapor Bölüm 12 bunu somut
bir taahhüt olarak yazmıştır:

> "Mobil kayıtların cihazda **şifreli olarak** geçici biçimde saklanması
> ve bağlantı sağlandığında eşitlenmesi."

## Şifreleme nasıl sağlanıyor

`flutter_secure_storage` platformun kendi güvenli deposunu kullanır:

| Platform | Yöntem |
|---|---|
| Android | Veri **AES/GCM/NoPadding**; anahtar Android Keystore içinde **RSA-OAEP** (SHA-256 + MGF1) ile sarmalanır |
| iOS | **Keychain**, `first_unlock` erişilebilirliğiyle — cihaz kilitliyken okunamaz |

Anahtar hiçbir zaman uygulamanın içinde tutulmaz; işletim sistemi yönetir
ve uygulama kaldırılınca anahtar da gider.

Oturum jetonu da aynı depoda tutulur — `SharedPreferences` düz metindir,
jeton orada durmamalıdır.

### ⚠️ Sınır — dürüst beyan

Şifreli tutulan **ölçüm kayıtları ve oturum jetonudur.** Fotoğraflar
cihazın normal dosya sisteminde durur; güvenli depo büyük ikili dosyalar
için tasarlanmamıştır. Fotoğrafların da şifrelenmesi ayrı bir çözüm
gerektirir ve bu sürümde yapılmamıştır.

## Tema

Varsayılan **açık tema**. Gündüz, güneş altında, eldivenli bir saha
personelinin okuyacağı ekran budur. Koyu tema kaldırılmadı — gece
çalışmasında ve pil ömründe gerçek bir yararı var — ama artık bir
tercih, tek seçenek değil. Düğme hem giriş ekranında hem üst çubukta;
seçim güvenli depoda saklanır.

Palet web arayüzüyle birebir aynıdır (`lib/tema.dart` ↔ `web/src/index.css`).

## Telefon ve tablet

Uygulama **her iki cihaz sınıfında** çalışır. Eşik 600 dp
(`lib/duzen.dart`):

| | Telefon (< 600 dp) | Tablet (≥ 600 dp) |
|---|---|---|
| Gezinme | Alt çubuk (`NavigationBar`) | Yan ray (`NavigationRail`) |
| İçerik genişliği | Ekranın tamamı | Ortalanmış, en fazla 560 dp |

Eşik ve genişlik sınırı bir hatanın ardından kondu: uygulama yalnızca
telefon için yazılmıştı ve tablette "esniyordu". Ölçülen sonuç,
1194×834 bir tablette: açılır liste **1160 px**, içerik 834 px
yüksekliğin yalnızca üst ~280 px'i, alt gezinme iki sekmeyi tüm
genişliğe yayıyor. 1160 px'lik bir form alanı kullanılamaz — göz,
etiketten değere kadar ekranın yarısını kat eder.

Doğrulama Flutter'ın web hedefiyle 390 / 834 / 1194 px'te ekran
görüntüsü alınarak yapılır.

## Yinelenen kayıt nasıl engelleniyor

Her ölçüm cihazda üretilen bir `yerel_kimlik` taşır ve sunucuda bu alan
benzersizdir.

Ağ koptuğunda istemci isteği tekrarlar ama sonucu bilemez. Bu koruma
olmadan **tek bir zayıf bağlantı ölçümleri ikiye katlar** ve miktar
hesabını bozardı.

Sunucu satır satır sonuç döner (`yazildi` / `yinelenen` / `hata`);
uygulama yalnızca `hata` alanları kuyrukta tutar.

### Birim sözleşmesi

Ekranda gösterilen birim ile sunucuya gönderilen birim **bilerek
farklıdır**: kullanıcı `m²` görür, sunucu `m2` alır. İkisi
`lib/olcum_turu.dart` içinde yan yana durur ve `test/olcum_turu_test.dart`
sunucunun sözleşmesini (`api/app/schemas.py` → `TURUN_BIRIMI`) doğrular.

Bu ayrım bir hatanın ardından yazıldı: alan ölçümleri sunucuya `m²`
olarak gidiyor, reddediliyordu. Eşitleme toplu çalıştığı için kuyrukta
tek bir alan ölçümü bulunduğu anda **bütün parti düşüyor**, o cihaz bir
daha hiç eşitlenemiyordu — üstelik uygulama bunu ağ hatası sanıp
"sonra denenecek" diyordu. İki uçlu düzeltildi: istemci doğru birimi
gönderiyor, sunucu da bozuk bir satır yüzünden partiyi düşürmüyor
(sahadaki güncellenmemiş telefonlar için).

## Çalıştırma

```bash
cd mobile
flutter pub get
flutter run -d chrome        # web
flutter run                  # bağlı cihaz
```

Sunucu adresi derleme sırasında değiştirilebilir:

```bash
flutter run --dart-define=API_TABAN=http://localhost:8000
```

Varsayılan: `https://rebuild-vision-api.onrender.com`

## Yapı

| Dosya | İşi |
|---|---|
| `lib/main.dart` | Uygulama girişi, oturum kontrolü |
| `lib/api.dart` | Sunucu istemcisi ve veri sınıfları |
| `lib/kuyruk.dart` | Şifreli çevrimdışı kuyruk |
| `lib/tema.dart` | Açık/koyu palet — web arayüzüyle birebir aynı |
| `lib/duzen.dart` | Telefon/tablet eşiği ve içerik genişliği |
| `lib/olcum_turu.dart` | Ölçüm türü, görünen birim, sunucu birimi |
| `lib/ekran/giris.dart` | Giriş |
| `lib/ekran/kabuk.dart` | Alt gezinme, bağlantı durumu, eşitleme |
| `lib/ekran/yukle.dart` | Fotoğraf çekme/seçme + konum |
| `lib/ekran/olcum.dart` | Ölçüm girişi + kuyruk listesi |

## Arayüzde korunan kurallar

Web arayüzündekilerle aynıdır:

1. Her model çıktısında **"ÖN TAHMİN"** etiketi
2. Sahte model servisi etkinken yükleme sonucunda **"SAHTE MODEL
   SERVİSİ"** uyarısı — sahtelik hiçbir yerde gizlenmez
3. Güven skoru **yuvarlanmaz**
4. Malzeme renkleri `siniflar.json` ile birebir aynı — doğrulayıcıdan
   geçmiş palet
5. Kapsam uyarısı ekranda yazılı
6. Dokunma hedefleri en az 52px — eldivenli kullanım

**Çevrimdışı olmak bir hata değildir**, sahada beklenen durumdur. Bu
yüzden kırmızı hata değil, nötr/uyarı tonunda gösterilir.

## Derleme durumu

| Hedef | Durum |
|---|---|
| Web | ✅ çalışır |
| Android APK | ⏳ Android SDK cmdline-tools kurulu değil |
| iOS | ⏳ Xcode kurulu değil |

Kaynak kod tamamdır; APK üretimi yalnızca araç zinciri kurulumu
gerektirir (`flutter doctor`).

## Bilinen eksikler

Dürüst beyan — bunlar henüz yapılmadı:

- **Kayıt ol ekranı yok.** Hesap açma yalnızca web arayüzünden yapılır;
  telefondan başvurulamaz.
- **Parolayı göster/gizle yok.** Web arayüzünde var.
- **Fotoğraflar şifreli değil.** Yalnızca ölçüm kayıtları ve oturum
  jetonu güvenli depoda tutulur (yukarıdaki sınır beyanı).
- **Enkaz alanı tanımlama, doğrulama kuyruğu ve harita ekranları yok.**
  Mobil uygulama saha personelinin iki işine odaklanır: görüntü yükleme
  ve ölçüm girme. Diğer roller web arayüzünü kullanır.
