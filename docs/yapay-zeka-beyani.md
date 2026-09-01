# Yapay Zekâ Kullanım Beyanı

**Dayanak:** Şartname **Madde 10.5** — Yapay Zekâ Kullanımı Maddesi

> "Yapay zekâ, makine öğrenmesi veya üretken yapay zekâ kullanılan
> projelerde; kullanılan modelin adı, lisansı, eğitim/veri kaynağı, dış
> API kullanımı, çıktı doğrulama yöntemi, hata/yanlılık riski ve
> açıklanabilirlik yaklaşımı proje dokümanında beyan edilecektir.
> Bakanlık tarafından sağlanan veriler, açık izin olmaksızın üçüncü
> taraf yapay zekâ servislerine veya bulut tabanlı model sağlayıcılarına
> gönderilemez."

**Son güncelleme:** 01.09.2026

Madde yedi kalem beyan istiyor. Aşağıda her biri ayrı başlık altında,
maddedeki sırayla yanıtlanmıştır.

---

## 1. Kullanılan modelin adı

**YOLO11** (Ultralytics), nesne tespiti görevi.

Sistemde **tek bir model** vardır ve yalnızca bir iş yapar: bir enkaz
fotoğrafındaki görünür malzeme bölgelerini sınırlayıcı kutu olarak
işaretleyip on sınıftan birine atamak.

Üretken yapay zekâ (LLM, görüntü üretimi vb.) **kullanılmamaktadır.**
Sistemde metin üreten, özetleyen veya karar gerekçesi yazan hiçbir model
yoktur; ekrandaki bütün açıklama metinleri insan tarafından yazılmıştır.

### ⚠️ Modelin şu anki durumu

Model, proje kapsamındaki veri setiyle **henüz eğitilmemiştir.** Bu
nedenle hiçbir başarım sayısı (precision, recall, F1, mAP) beyan
edilmemektedir — bkz. `results/model-metrikleri.md`.

Geliştirme ve demo sırasında **sahte bir model servisi** (`model-mock/`)
kullanılır. Sahtelik gizlenmez: sahte servis etkinken arayüzde kalıcı bir
"SAHTE MODEL SERVİSİ" rozeti görünür ve yükleme sonucunda çıktıların
uydurma olduğu yazılı olarak belirtilir.

---

## 2. Modelin lisansı

| Bileşen | Lisans |
|---|---|
| Ultralytics YOLO11 (çıkarım kütüphanesi) | **AGPL-3.0** 🔴 |
| Proje kodu | AGPL-3.0 (bkz. `LICENSE`) |
| Eğitim veri seti (CDW-Seg) | CC0 1.0 — kamu malı |
| Model ağırlıkları (özgün eğitim) | Bkz. `docs/lisans-analizi.md` Bölüm 2.1 |

AGPL-3.0, şartname **Madde 10.4**'ün "ayrıca belirtilecektir" dediği
lisans türlerindendir ve bu belge ile ayrıca belirtilmektedir. Tam
analiz: [`docs/lisans-analizi.md`](lisans-analizi.md) Bölüm 3.

Mimari not: AGPL'li kütüphane **ayrı bir süreçte** (`model-service/`)
çalışır; `api/` onu yalnızca HTTP ile çağırır ve `ultralytics` paketini
hiçbir koşulda import etmez. Bu sınır bir yorum satırıyla değil,
`tests/test_agpl_siniri.py` içindeki beş testle korunur.

---

## 3. Eğitim / veri kaynağı

**CDW-Seg** — inşaat ve yıkım atığı bölütleme veri seti.

| Alan | Değer |
|---|---|
| Lisans | **CC0 1.0** (kamu malı) |
| DOI | 10.6084/m9.figshare.28573229 |
| Makale | Sirimewan & Arashpour, *Scientific Data* (2025) |
| Sınıf sayısı | 10 |

Karar gerekçesi: `docs/karar-kaydi.md` K-006.

### Bu veri setinin bilinen sınırları

Bunlar `results/bilinen-sinirlar.md` Bölüm B'de ayrıntılı yazılıdır ve
model başarımını doğrudan etkiler:

- **Cam ve seramik sınıfları veri setinde YOKTUR.** Model bu iki malzeme
  grubunu tanımaz.
- **Tuğla, betondan ayrılmaz** — CDW-Seg'in `concrete` sınıfı ikisini
  birlikte kapsar.
- **Alan uyuşmazlığı:** Görüntüler şantiye hurda konteynerlerinden
  çekilmiştir; proje ise afet sonrası enkaz sahası iddiasındadır. Sahne,
  ölçek, toz ve malzeme durumu farklıdır.

### Bakanlık verisi

Bakanlık tarafından sağlanan veriler **hiçbir dış yapay zekâ servisine
veya bulut model sağlayıcısına gönderilmez.** Model çıkarımı yerel
altyapıda, proje ekibinin kendi çalıştırdığı serviste yapılır. Ayrıntı:
[`docs/veri-politikasi.md`](veri-politikasi.md).

---

## 4. Dış API kullanımı

**Yapay zekâ amaçlı hiçbir dış API kullanılmamaktadır.**

| Servis | Kullanım |
|---|---|
| Bulut model sağlayıcısı (OpenAI, Google, AWS, Azure vb.) | ❌ **yok** |
| Dış görüntü işleme API'si | ❌ **yok** |
| Dış kimlik doğrulama servisi | ❌ **yok** — kimlik doğrulama tamamen yereldir (`docs/karar-kaydi.md` K-005) |
| OpenStreetMap karo sunucusu | ✅ yalnızca **harita altlığı görüntüsü** — hiçbir proje verisi gönderilmez |

OpenStreetMap tek dış bağımlılıktır ve yalnızca haritanın arka plan
görüntüsünü çeker. Karo isteği yalnızca ekrandaki coğrafi kutuyu içerir;
tespit, ölçüm, saha adı veya kullanıcı bilgisi taşımaz. Altlık
yüklenemediğinde sistem çalışmaya devam eder ve arayüz bunu yazıyla
bildirir.

---

## 5. Çıktı doğrulama yöntemi

**Sistemin en temel kuralı budur: model hiçbir zaman son sözü söylemez.**

Her model çıktısı bir **ön tahmindir** ve arayüzde istisnasız "ÖN TAHMİN"
etiketiyle görünür. Bir tespitin karara dönüşmesi için zincirin tamamı
işlemek zorundadır:

```
model çıktısı (ön tahmin)
      ↓
uzman doğrulaması  →  onayla / düzelt / belirsiz işaretle
      ↓
saha ölçümü (kim, neyle, nasıl ölçtü — zorunlu alan)
      ↓
miktar (tek değer değil, belirsizlik aralığı + yöntem + katsayı kaynağı)
```

Zincirin her halkası **veri katmanında** zorlanır, yalnızca arayüzde
değil:

| Kural | Nerede zorlanıyor |
|---|---|
| Doğrulanmamış tespit miktar hesabına girmez | `api/` + veri tabanı kısıtı |
| "Belirsiz" işaretlenen kayıt da girmez | aynı |
| Ölçüm yoksa miktar üretilmez — varsayılan, tahmini veya "≈0" yazılmaz | aynı |
| Miktar tek kesin değer olarak üretilemez; aralık zorunludur | veri tabanı kısıtı |
| Doğrulanmamış katsayı ile hesap yapılmaz | `katsayilar.json` → `dogrulandi:false` |
| Uzman düzeltmesi model tahminini geçersiz kılar | `duzeltilen_sinif` alanı |

Bu kuralların her biri için otomatik test vardır
(`tests/test_kural_1_olcum_yoksa_miktar_yok.py`,
`tests/test_kural_3_ve_4_kapsam_ve_on_tahmin.py`). Testler her itmede
GitHub Actions üzerinde koşar.

### Düşük güvenli çıktı otomatik olarak insana gider

Güven skoru eşiğin altında kalan tespitler **kendiliğinden uzman
inceleme kuyruğuna** düşer; kullanıcının bunu fark etmesi gerekmez.

⚠️ Eşik (varsayılan 0,50) **ölçülmüş bir değer değildir.** Model henüz
eğitilmediği için precision/recall eğrisinden türetilememiştir; şu an
bir mühendislik varsayımıdır ve ortam değişkeniyle değiştirilebilir
tutulmuştur. Ölçüm yapıldığında eğriden türetilecektir.

### "Reddet" aksiyonu bilinçli olarak yoktur

Uzman bir tespiti reddedemez; yalnızca onaylayabilir, düzeltebilir ya da
belirsiz işaretleyebilir. Reddetmek kaydın bilgi değerini yok eder;
"belirsiz" kaydı izlenebilir tutarak ikinci incelemeye açık bırakır
(`docs/karar-kaydi.md` K-004).

---

## 6. Hata ve yanlılık riski

Riskler gizlenmez; ölçülmüş sınır, ölçülmemiş iddiadan güçlüdür.
Tam liste: [`results/bilinen-sinirlar.md`](../results/bilinen-sinirlar.md).

### 6.1. Alan yanlılığı — en büyük risk

Eğitim verisi **şantiye hurda konteynerlerinden**, kullanım alanı ise
**afet enkaz sahasından**dır.

| | CDW-Seg (eğitim) | Afet enkazı (kullanım) |
|---|---|---|
| Sahne | Sınırlı, çerçevelenmiş konteyner | Açık, düzensiz saha |
| Ölçek | Yakın çekim | Değişken, çoğu zaman uzak/havadan |
| Toz / renk | Şantiye koşulu | Yoğun toz, renk bozulması |
| Malzeme durumu | Ayrışmış, üst üste | Çökmüş yapı, iç içe geçmiş |

**Sonuç:** Modelin saha başarımı, CDW-Seg üzerinde ölçülecek
başarımından **düşük olacaktır.** Ne kadar düşük olacağı **henüz
ölçülmemiştir** ve ölçülene kadar hiçbir genelleme iddiası
yapılmamaktadır.

### 6.2. Sınıf kapsama yanlılığı

Cam ve seramik model tarafından **tanınmaz.** Kritik olan şudur: bir
sınıfın çıktıda görünmemesi, arayüzde **"o malzeme sahada yok" anlamına
gelecek biçimde gösterilmez.** Yokluk, kanıt değildir.

### 6.3. Temsil yanlılığı — kutu ile maske farkı

CDW-Seg etiketleri bölütleme maskesidir; sistemin arayüz sözleşmesi ise
sınırlayıcı kutudur. İç içe geçmiş malzemelerde kutu, maskeden **kaba**
bir temsildir ve komşu malzemeyi kendi alanına katabilir. Bu, alan
tabanlı her hesabı yukarı yönlü saptırır.

### 6.4. Güven skoru yanlış okunabilir

Güven skoru **doğruluk olasılığı değildir** — modelin kendi iç skorudur
ve kalibre edilmemiştir. Bu yüzden arayüzde skor **yuvarlanmadan**
gösterilir; yuvarlamak ona hak etmediği bir kesinlik görüntüsü verir.

### 6.5. Sistemin risk karşısındaki duruşu

Üç şey bilinçli olarak **yapılmaz**:

1. **Tehlikeli madde teşhisi yapılmaz.** Asbest ve benzeri maddeler
   görüntüden teşhis edilmez; hiçbir tahmin, ikon, renk kodu veya
   olasılık üretilmez. Sistem yalnızca uzman/laboratuvar yönlendirme
   kaydı tutar. Kayıt bulunmaması **"güvenli" anlamına gelmez** ve
   arayüzde yeşil bir "temiz" göstergesi bulunmaz.
2. **Enkaz altı değerlendirilmez.** Yalnızca görünür yüzey. Toplam enkaz
   içeriği iddiası hiçbir yerde üretilmez.
3. **Nihai kararı sistem vermez.** Karar yetkili kurum ve uzmanlarındır.

---

## 7. Açıklanabilirlik yaklaşımı

Sistem, modeli **açıklamaya çalışmaz** — bunun yerine kararın dayanağını
uçtan uca **izlenebilir** kılar. Gerekçe: kalibre edilmemiş bir modelin
üreteceği ısı haritası veya öznitelik önemi görselleştirmesi, kullanıcıya
gerçek olmayan bir anlayış hissi verir. Kamu kararında bu, açıklama
yokluğundan daha tehlikelidir.

Bunun yerine dört katman:

### 7.1. Görsel kanıt — kutu her zaman görüntünün üstünde

Her tespit, kaynak fotoğrafın üzerinde sınırlayıcı kutusuyla çizilir;
sınıf adı, güven skoru ve "ÖN TAHMİN" rozeti kutunun yanında durur.
Kullanıcı modelin **neye baktığını** doğrudan görür.

Çizilemeyen kutu sessizce yutulmaz: beklenen biçimde olmayan koordinat
gelirse arayüz bunu ayrıca uyarı olarak yazar.

### 7.2. Sayının nereden geldiği yazılıdır

Miktar gösterilirken üç şey birlikte gösterilir: **belirsizlik aralığı**,
**kullanılan yöntem** ve **katsayı kaynağı**. Ölçüme dayanan bir miktarda
"Katsayı kullanılmadı — doğrudan ölçüm" yazar; katsayı kullanıldığında
kaynağın adı görünür.

### 7.3. Kim, ne zaman, ne yaptı — işlem geçmişi

Her tespit, ölçüm, doğrulama ve rol ataması işlem geçmişine **otomatik**
düşer (Şartname Madde 9.1 · `docs/mimari.md` Bölüm 3.2). Geçmiş
kullanıcı tarafından kapatılamaz ve arayüzde tespit bazında görülebilir.
Bir kararın neden o şekilde alındığı, sonradan denetlenebilir.

Ölçüm girerken **"nasıl ölçüldü"** alanı zorunludur — ölçümün yöntemi
bilinmeden miktarın dayanağı da bilinemez.

### 7.4. Görüntünün künyesi

Çekim tarihi ve cihaz bilgisi görüntü kartında gösterilir. Kararı
sonradan denetleyecek kişinin ilk soracağı şey budur.

### Bilinçli olarak yapılmayan

| Yapılmayan | Neden |
|---|---|
| Isı haritası / Grad-CAM | Kalibre edilmemiş modelde yanıltıcı kesinlik hissi verir |
| Doğal dil gerekçe üretimi | Üretken model yok; uydurma gerekçe en tehlikeli açıklama biçimidir |
| Güven skorunun yuvarlanması | Hak edilmemiş kesinlik görüntüsü |
| "Sistem şu kararı öneriyor" ifadesi | Nihai kararı sistem vermez |

---

## 8. Özet tablo

| Madde 10.5 kalemi | Bu belgede | Durum |
|---|---|---|
| Modelin adı | Bölüm 1 | YOLO11 — henüz eğitilmedi, sahte servis işaretli |
| Lisansı | Bölüm 2 | AGPL-3.0 — Madde 10.4 uyarınca ayrıca beyan |
| Eğitim/veri kaynağı | Bölüm 3 | CDW-Seg, CC0 1.0, DOI'li |
| Dış API kullanımı | Bölüm 4 | Yapay zekâ amaçlı dış API **yok** |
| Çıktı doğrulama yöntemi | Bölüm 5 | Zorunlu uzman doğrulaması + veri katmanı kısıtları |
| Hata/yanlılık riski | Bölüm 6 | Beş risk açıkça sayılmış |
| Açıklanabilirlik yaklaşımı | Bölüm 7 | İzlenebilirlik; sahte açıklama üretilmez |
