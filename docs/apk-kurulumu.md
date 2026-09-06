# APK üretimi ve cihaza kurulum

**Şartname Madde 10.3** jürinin projeyi bağımsız bir ortamda
çalıştırabilmesini istiyor. Web arayüzü `docker compose` ile kuruluyor;
mobil taraf için jürinin eline **kurulabilir bir APK** geçmelidir.

---

## En kısa yol: APK'yı GitHub üretsin, siz indirin

**Kendi makinenize hiçbir şey kurmanız gerekmez.**

Geliştirme ortamında Android SDK yok ve ağ politikası `dl.google.com`
adresini engelliyor — APK orada üretilemiyor. GitHub'ın koşucularında
Android SDK kurulu gelir, bu yüzden derleme oraya taşındı:
[`.github/workflows/apk.yml`](../.github/workflows/apk.yml).

### İndirme

1. Depoda **Actions** sekmesi → soldan **APK**
2. En üstteki yeşil koşuya girin
3. Sayfanın altında **Artifacts** → `ReBuild-Vision-0.1.0-<özet>.apk`
   dosyasını indirin

İnen dosya bir **.zip**'tir (GitHub her eki zipler); açınca içinden
`.apk` çıkar. Telefona/tablete o `.apk` dosyasını kopyalayın.

Ekler **90 gün** durur. Kalıcı ve herkese açık bir bağlantı gerekiyorsa
bir etiket atın; koşu APK'yı o sürümün Release sayfasına ekler:

```bash
git tag v0.1.0 && git push origin v0.1.0
```

### İş ne yapar

| Adım | Neden |
|---|---|
| `flutter analyze` + `flutter test` | Kırık bir uygulamanın kurulabilir olması, kurulamaz olmasından kötüdür |
| `flutter build apk --release` | Tek (universal) APK — arm64, arm32 ve x86_64 aynı dosyada |
| `aapt2 dump permissions` | **Üretilen dosyada** `INTERNET` dahil dört izni doğrular |

Son satır önemli: aşağıdaki arıza tam olarak manifest doğru göründüğü
hâlde **üretilen APK'da** izin bulunmamasıydı. Artık makinede değil,
çıkan dosyada kontrol ediliyor; izin düşerse iş kırmızıya döner.

---

## 🔴 Önce bilinmesi gereken: bir arıza kapatıldı (04.09.2026)

`INTERNET` izni yalnızca `android/app/src/debug/` ve `src/profile/`
manifestlerinde tanımlıydı — Flutter'ın varsayılanı böyledir.

Sonuç: `flutter run` çalışıyordu ama **release APK internet izni
taşımıyordu.** Jüriye verilecek sürümde her API çağrısı sessizce
başarısız olurdu; kullanıcı yalnızca "bağlantı yok" görürdü.

Kamera ve konum izinleri de hiç tanımlı değildi; `image_picker` ve
`geolocator` cihazda izin isteyemez ve çalışmazdı.

`src/main/AndroidManifest.xml` artık şunları taşıyor:

| İzin | Ne için |
|---|---|
| `INTERNET` | Sunucudaki modele görüntü göndermek, kayıtları eşitlemek |
| `ACCESS_NETWORK_STATE` | Çevrimdışı kuyruğun ne zaman gönderileceğini bilmek |
| `CAMERA` | Saha görüntüsü çekmek |
| `ACCESS_FINE_LOCATION` · `ACCESS_COARSE_LOCATION` | Görüntünün çekildiği yer (İSTEĞE BAĞLI) |
| `READ_MEDIA_IMAGES` | Galeriden seçim (Android 13+) |
| `READ_EXTERNAL_STORAGE` (maxSdk 32) | Galeriden seçim (eski Android) |

Kamera ve konum `uses-feature ... required="false"` ile işaretlidir:
kamerasız bir tablete de kurulabilir, galeriden seçim çalışır.

Uygulama adı da düzeltildi: cihazda `rebuild_vision_mobil` yerine
**ReBuild Vision** görünür.

---

## Elle üretim (kendi makinenizde)

Yukarıdaki GitHub yolu yetmiyorsa ya da kendi sunucunuza bağlanan
bir sürüm istiyorsanız:

### Gereken

- Flutter SDK 3.13+ (`flutter doctor` temiz olmalı)
- Android SDK (Android Studio ya da `commandlinetools`)
- JDK 17

### Komut

Sunucu adresi **derleme sırasında** gömülür. Varsayılan
`https://rebuild-vision-api.onrender.com`; başka bir adres için
`--dart-define` verin.

```bash
cd mobile
flutter pub get

# Canlı sunucuya bağlanan sürüm (jüriye verilecek olan)
flutter build apk --release

# ya da kendi sunucunuza:
flutter build apk --release \
  --dart-define=API_TABAN=https://sizin-sunucunuz.example.com
```

Çıktı: `mobile/build/app/outputs/flutter-apk/app-release.apk`

### Daha küçük APK (isteğe bağlı)

```bash
flutter build apk --release --split-per-abi
```
Üç ayrı APK üretir (`armeabi-v7a`, `arm64-v8a`, `x86_64`). Çoğu telefon
ve tablet **arm64-v8a** ister. Tek dosya vermek istiyorsanız
`--split-per-abi` KULLANMAYIN.

---

## ⚠️ İmzalama — jüriye vermeden önce okuyun

`android/app/build.gradle.kts` içinde release yapılandırması **hâlâ debug
anahtarıyla** imzalıyor:

```kotlin
release {
    // TODO: Add your own signing config for the release build.
    signingConfig = signingConfigs.getByName("debug")
}
```

Bu, **demo/prototip için kabul edilebilir** ve APK kurulur. Ama:

- Google Play'e yüklenemez (kendi anahtarınız gerekir).
- Debug anahtarı makineye özeldir; başka bir makinede üretilen APK
  "farklı imza" sayılır ve üzerine güncelleme kurulmaz.

Prototip teslimi için değiştirmeye gerek yok. Değiştirecekseniz
`keytool -genkey` ile bir keystore üretip `signingConfigs`'e bağlayın ve
**keystore'u depoya koymayın.**

---

## Cihaza kurulum

### USB ile

```bash
adb install -r build/app/outputs/flutter-apk/app-release.apk
```

### Dosyayla (jüri için en pratik)

APK'yı telefona/tablete kopyalayın ve dosya yöneticisinden açın.
Android **"bilinmeyen kaynaklardan kurulum"** izni ister — bu normaldir
ve Play Store dışından kurulan her APK için sorulur.

### İlk açılışta

Uygulama sırasıyla kamera, konum ve galeri izni isteyecektir. **Konumu
reddetseniz de uygulama çalışır** — yalnızca koordinat kaydedilmez;
yükleme yine yapılır.

Demo hesapları: `docs/kurulum.md` Bölüm 8.

---

## Sürüm bilgisi

`pubspec.yaml` içindeki `version:` alanı APK'nın `versionName` ve
`versionCode` değerlerini belirler. Jüriye birden fazla sürüm
verecekseniz her seferinde artırın, yoksa cihaz güncellemeyi reddeder.
