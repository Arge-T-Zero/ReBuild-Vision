# Kullanıcı Kılavuzu

**ReBuild Vision** — enkaz malzemelerinin görüntü tabanlı ön
sınıflandırması ve doğrulanabilir kaynak haritası.

**Son güncelleme:** 27.08.2026

---

## Başlamadan önce: sistemin sınırları

Bu araç bir **karar destek** aracıdır, karar verici değildir.

- Ekrandaki her model çıktısı **"ön tahmin"** etiketiyle görünür.
- Sistem **yalnızca görünür yüzeyi** değerlendirir. Enkaz altındaki
  içerik hakkında hiçbir şey söylemez.
- Sistem **tehlikeli madde teşhisi yapmaz.** Asbest ve benzeri maddeler
  için hiçbir tahmin üretmez. Bir alanda uyarı görmemeniz, o alanın
  **güvenli olduğu anlamına gelmez.**
- **Ölçüm girilmemişse miktar hesaplanmaz.** Boş bir miktar alanı hata
  değildir; dayanağı olmayan sayı üretmeme kararıdır.
- Nihai operasyon kararı yetkili kurum ve uzmanlar tarafından verilir.

---

## 1. Hesap açma ve giriş

1. Giriş ekranında **"Hesabım yok — kayıt ol"** bağlantısına tıklayın.
2. Ad soyad, e-posta ve parolanızı girin (parola en az 8 karakter).
3. **Rolünüzü kendiniz seçemezsiniz.** Bu bilinçli bir tasarımdır:
   yetkiler kamu sistemi mantığıyla, yetkili yönetici tarafından atanır.
4. Kaydınız alındıktan sonra hesabınız **onay bekler.** Yönetici rolünüzü
   atayana kadar giriş yapamazsınız.

Giriş denemenizde *"Hesabınız henüz yönetici tarafından onaylanmadı"*
uyarısı alıyorsanız, yöneticinin rol ataması beklenmektedir.

---

## 2. Roller ve yetkiler

| Rol | Görebildiği | Yapabildiği |
|---|---|---|
| **Saha personeli** | Kendi sahası | Görüntü yükleme, ölçüm girme |
| **Doğrulayıcı uzman** | Atandığı sahalar | Onayla / düzelt / belirsiz işaretle |
| **Belediye yetkilisi** | Kendi ilçesi/sahaları | Saha tanımlama, görüntü yükleme, filtreleme, rapor |
| **AFAD yetkilisi** | Çok sahalı görünüm | Filtreleme, rapor |
| **Yıkım firması** | Yalnızca kendi sahası | Görüntüleme |
| **Tesis operatörü** | Kendine yönlendirilen kayıtlar | Görüntüleme |
| **Yönetici** | Tümü | Rol atama, tüm işlemler |

Yetkiniz olmayan bir işlemi denerseniz sistem izin vermez. Bu kontrol
sunucu tarafında yapılır; arayüzde bir düğmeyi görmemeniz tek engel
değildir.

---

## 3. Enkaz alanı tanımlama

*(Belediye yetkilisi, AFAD yetkilisi veya yönetici)*

1. **Enkaz alanları** sekmesinde **"Yeni alan tanımla"**ya tıklayın.
2. Alan adını yazın. Sorumlu adı isteğe bağlıdır.
3. **Erişim durumunu** seçin: açık / kısıtlı / kapalı.
4. Haritada:
   - **"Konum işaretle"** seçiliyken haritaya tıklayarak alanın merkez
     noktasını belirleyin.
   - **"Sınır çiz"** seçiliyken sırayla tıklayarak sınır köşelerini
     ekleyin. En az 3 nokta gerekir. Yanlış nokta eklerseniz **"Sınırı
     temizle"** ile baştan başlayabilirsiniz.
5. **"Alanı kaydet"**e tıklayın.

---

## 4. Görüntü yükleme

*(Saha personeli, belediye yetkilisi veya yönetici)*

1. Alanı açın, **"Görüntü yükle"**ye tıklayın.
2. Bir veya birden çok görüntü seçin (JPEG, PNG veya WebP).
3. Yükleme tamamlandığında sistem görüntüleri otomatik olarak
   sınıflandırır.

Yükleme sonrasında bir bilgi satırı görürsünüz:

> *Düşük güvenli 1 tespit otomatik olarak uzman inceleme kuyruğuna
> alındı.*

**Bu işlem otomatiktir; sizin bir şey yapmanıza gerek yoktur.**

---

## 5. Sonuçları okuma

Sonuç ekranında görüntünün üzerinde renkli kutular ve sağında tespit
listesi bulunur.

### Kutular

- Her kutunun rengi malzeme sınıfını gösterir; **renk tek başına anlam
  taşımaz**, kutunun üstünde her zaman sınıf adı ve güven skoru yazar.
- **Kesikli çizgili kutu** = model bu tespitten emin değil, uzman
  incelemesi gerekiyor.
- Kutuya tıklayınca sağdaki listede ilgili tespit açılır.

Bazı tespitlerin kutusu çizilemeyebilir. Bu durumda ekranda şu uyarı
çıkar: *"koordinat biçimi tanınmıyor… Yanlış konumda kutu göstermemek
için çizim yapılmadı."* Bu bir hata mesajı değil, bilinçli bir
davranıştır.

### Tespit listesi

Her satırda:

| Öğe | Anlamı |
|---|---|
| Renkli kare + malzeme adı | Sınıf |
| Sayı (örn. `0.83`) | Model güven skoru — **yuvarlanmaz** |
| `ÖN TAHMİN` | Bu bir model çıktısıdır, kesin bilgi değildir |
| Durum rozeti | Doğrulama durumu (aşağı bkz.) |
| *Uzman incelemesi gerekli* | Güven düşük |

### Doğrulama durumu rozetleri

| Rozet | Görünüm | Anlamı |
|---|---|---|
| **Beklemede** | Kesikli çerçeve, nötr | Henüz uzman bakmadı |
| **Onaylandı** ✓ | Dolu çerçeve, yeşil | Uzman doğru buldu |
| **Düzeltildi** ✎ | Dolu çerçeve, mavi | Uzman sınıfı değiştirdi — eski ve yeni sınıf birlikte görünür |
| **Belirsiz** ? | Dolu çerçeve, sarı | Uzman karar veremedi |

---

## 6. Miktar ve ölçüm

Bir tespite tıkladığınızda **Miktar** kartı açılır.

### Ölçüm girilmemişse

> **Ölçüm girilmediği için miktar hesaplanmadı**
> *Sistem, dayanağı olmayan bir miktar tahmini üretmez.*

**Burada bir sayı görmemeniz doğrudur.** Sistem tahmini bir tonaj
uydurmaz. Ölçüm girme yetkiniz varsa **"Ölçüm ekle"** düğmesini
görürsünüz.

### Ölçüm girme

*(Saha personeli, doğrulayıcı uzman veya yönetici)*

1. **"Ölçüm ekle"**ye tıklayın.
2. Ölçüm türünü seçin: ağırlık (ton), hacim (m³) veya görünür alan (m²).
3. Değeri girin.
4. **Ölçüm yöntemini yazın** — bu alan zorunludur. Kim, neyle, nasıl
   ölçtü? Bu bilgi işlem geçmişine kaydedilir ve sonradan denetlenebilir.
5. **"Ölçümü kaydet"**e tıklayın.

### Ölçüm girildikten sonra

Miktar **tek bir kesin değer olarak değil, aralık olarak** gösterilir:

> **7.74 – 9.46 ton**
> *belirsizlik aralığı*
> Yöntem: Doğrudan ağırlık ölçümü (tek kayıt). Aralık, ±%10 saha ölçüm
> belirsizliği varsayımıyla üretildi.

Aralığın altında kullanılan **yöntem** ve **katsayı kaynağı** her zaman
yazılıdır. Dayanağı görünmeyen bir sayı bu sistemde üretilmez.

### Hâlâ sayı görünmüyorsa

Ölçüm girdiğiniz hâlde miktar hesaplanmadıysa, ekranda nedeni yazar:

- *"Yalnızca alan ölçümü var; derinlik bilinmeden hacim ve miktar
  hesaplanamaz"*
- *"Bu malzeme için doğrulanmış dönüşüm katsayısı bulunmadığından miktar
  hesaplanmadı"*
- *"Bu sınıf bir atık malzeme değildir; miktar hesaplanmaz"* (örn.
  konteyner)

---

## 7. Uzman doğrulama

*(Doğrulayıcı uzman veya yönetici)*

**İnceleme kuyruğu** sekmesinde, modelin emin olmadığı tespitler
listelenir. Bu kuyruk **otomatik** dolar.

Her kayıt için üç seçenek vardır:

| Düğme | Ne zaman |
|---|---|
| **Onayla** | Model doğru sınıflandırmış |
| **Düzelt** | Sınıf yanlış — doğru sınıfı listeden seçin |
| **Belirsiz olarak işaretle** | Görüntüden karar verilemiyor |

> **"Reddet" seçeneği bilinçli olarak yoktur.** Bir tespiti reddetmek
> kaydın bilgi değerini yok eder. "Belirsiz" işaretlemek ise kaydı
> izlenebilir tutar ve ikinci bir incelemeye açık bırakır.

Düzeltme yaptığınızda:

- Modelin ilk tahmini **silinmez**; ekranda üstü çizili olarak görünür.
- Bütün hesaplar (miktar, harita) **sizin düzelttiğiniz sınıfa göre**
  yeniden yapılır. İnsan kararı modelin tahminini geçersiz kılar.
- Kim, ne zaman, neyi değiştirdi bilgisi işlem geçmişine kaydedilir.

---

## 8. Malzeme Kaynak Haritası

**Malzeme haritası** sekmesinde enkaz alanları ve doğrulanmış malzeme
dağılımı görünür.

> **Haritada yalnızca uzman tarafından doğrulanmış kayıtlar gösterilir.**
> Doğrulanmamış ön tahminler haritada yer almaz. "Belirsiz" işaretlenmiş
> kayıtlar da gösterilmez.

- Sağdaki listeden malzeme türlerine tıklayarak filtreleyebilirsiniz.
- Lejandın altında **kapsam uyarısı** ve **kapsanmayan malzeme grupları**
  yazılıdır.

### Kapsanmayan gruplar

Mevcut eğitim verisinde **cam** ve **seramik** sınıfı bulunmamaktadır;
**tuğla** ise betondan ayrılmaz. Model bu grupları **tanımaz.**

Bir malzemenin haritada görünmemesi, **o malzemenin sahada olmadığı
anlamına gelmez.** Ayrıntı: `results/bilinen-sinirlar.md`.

---

## 9. Sahte model servisi uyarısı

Ekranın en üstünde sarı bir bant görüyorsanız:

> **SAHTE MODEL SERVİSİ — gösterilen tespitler gerçek bir modelden
> gelmemektedir**

Sistem geliştirme/demo modundadır ve **gerçek bir yapay zekâ modeli
çalışmamaktadır.** Gösterilen sınıflar ve güven skorları üretilmiş
değerlerdir; hiçbir operasyonel karara dayanak yapılamaz.

Bu bant kapatılamaz. Turuncu bant ise model servisine hiç
ulaşılamadığını gösterir.

---

## 10. Sık sorulanlar

**Miktar alanı neden boş?**
Ölçüm girilmediği için. Sistem ölçüm olmadan tonaj tahmini üretmez. Ölçüm
ekleyin, aralık hesaplanacaktır.

**Neden tek bir sayı yerine aralık görüyorum?**
Çünkü tek bir kesin sayı gerçeği yansıtmaz. Sistem belirsizliği gizlemez,
gösterir.

**Asbest uyarısı neden yok?**
Sistem tehlikeli madde teşhisi yapmaz ve yapmayacaktır. Görüntüden asbest
teşhisi güvenilir biçimde yapılamaz. Şüphe varsa uzman/laboratuvar
incelemesi gerekir. **Uyarı olmaması güvenli olduğu anlamına gelmez.**

**Enkaz altındaki malzemeyi neden göremiyorum?**
Sistem yalnızca görünür yüzeyi değerlendirir. Toplam enkaz içeriği
iddiası hiçbir yerde üretilmez.

**Bir tespiti nasıl silerim?**
Silemezsiniz — ve bu bilinçlidir. Yanlış bir tespiti "Düzelt" ile
düzeltebilir veya "Belirsiz" olarak işaretleyebilirsiniz. Kayıtların
izlenebilirliği korunur.

**Giriş yapamıyorum.**
Hesabınız onay bekliyor olabilir. Yöneticinin rol ataması gerekir.
