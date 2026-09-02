# Yapay Zekâ Kullanım Beyanı

**Dayanak:** Şartname **Madde 10.5** — Yapay Zekâ Kullanımı Maddesi

> "Yapay zekâ, makine öğrenmesi veya üretken yapay zekâ kullanılan
> projelerde; kullanılan modelin adı, lisansı, eğitim/veri kaynağı, dış
> API kullanımı, çıktı doğrulama yöntemi, hata/yanlılık riski ve
> açıklanabilirlik yaklaşımı proje dokümanında beyan edilecektir.
> Bakanlık tarafından sağlanan veriler, açık izin olmaksızın üçüncü
> taraf yapay zekâ servislerine veya bulut tabanlı model sağlayıcılarına
> gönderilemez."

**Son güncelleme:** 02.09.2026 — sınıf sayısı ve eşik gerekçesi düzeltildi

Madde yedi kalem beyan istiyor. Aşağıda her biri ayrı başlık altında,
maddedeki sırayla yanıtlanmıştır.

---

## 1. Kullanılan modelin adı

**YOLO11** (Ultralytics), nesne tespiti görevi.

Sistemde **tek bir model** vardır ve yalnızca bir iş yapar: bir enkaz
fotoğrafındaki görünür malzeme bölgelerini sınırlayıcı kutu olarak
işaretleyip **beş sınıftan** birine atamak (`ahsap`, `beton_tugla`,
`cam`, `metal`, `seramik`).

Üretken yapay zekâ (LLM, görüntü üretimi vb.) **kullanılmamaktadır.**
Sistemde metin üreten, özetleyen veya karar gerekçesi yazan hiçbir model
yoktur; ekrandaki bütün açıklama metinleri insan tarafından yazılmıştır.

### Modelin durumu — eğitildi ve ölçüldü (02.09.2026)

| Bölme | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| val | 0,5318 | 0,4530 | **0,4424** | 0,3089 |
| test | 0,4880 | 0,4176 | **0,4334** | 0,3132 |

YOLO11m, 640×640, AdamW, 2,03 saat. Tam künye ve sınıf bazlı sonuçlar:
`results/model-metrikleri.md`; ham çıktılar: `results/egitim/`.

**Model çalışıyor ama zayıf.** mAP50 0,43–0,44 — tespitlerin ancak bir
kısmı doğru bulunuyor. Sistemin zorunlu uzman doğrulaması bu yüzden bir
süs değil, **çalışma koşuludur.** `seramik` sınıfı testte 0,0877 ile
pratikte çalışmıyor ve çıktısı kullanılabilir sayılmamalıdır.

Sahte servis (`model-mock/`) hâlâ mevcuttur ve ağırlık yüklü olmadığında
kullanılabilir. Sahtelik gizlenmez: sahte servis etkinken arayüzde kalıcı
bir "SAHTE MODEL SERVİSİ" rozeti görünür. Gerçek servis ağırlık yoksa
uydurma üretmez, 503 döner.

---

## 2. Modelin lisansı

| Bileşen | Lisans |
|---|---|
| Ultralytics YOLO11 (çıkarım kütüphanesi) | **AGPL-3.0** 🔴 |
| Proje kodu | AGPL-3.0 (bkz. `LICENSE`) |
| Eğitim veri seti (takımın kendi topladığı) | 🔴 **beyan eksik** — bkz. Bölüm 3 |
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

**Takımın kendi oluşturduğu veri seti**, Roboflow ile etiketlenmiştir.

| Alan | Değer |
|---|---|
| Sınıf sayısı | **5** — `ahsap`, `beton_tugla`, `cam`, `metal`, `seramik` |
| Görüntü | 2.765 (train 2.184 · valid 384 · test 197) |
| Kutu | 9.348 |
| Lisans / kaynak | 🔴 **BEYAN EKSİK** — aşağıya bakınız |
| Künye | `results/egitim/veri_seti_kunyesi.json` |
| Ön işleme | `results/egitim/on_isleme_kaydi.json` — sızıntı ve filigran temizliği, 750 görüntü oversample |

### ⚠️ Önceki sürümdeki beyan yanlıştı

Bu belge 01.09.2026'da veri kaynağını **CDW-Seg (CC0, DOI
10.6084/m9.figshare.28573229)** olarak beyan ediyordu. **Eğitim o veri
setiyle yapılmamıştır.** Depo o tarihte modelin hangi veriyle eğitildiğini
bilmiyordu; ağırlık geldiğinde `data.yaml` ile `siniflar.json` arasındaki
uyuşmazlık ortaya çıktı ve düzeltildi (`docs/karar-kaydi.md` K-021).

### 🔴 Kaynak ve lisans beyanı eksik

Görüntülerin **nereden toplandığı ve hangi hakla kullanıldığı henüz
yazılı değildir.** Madde 5.2 "kaynaklarını açıkça belirtmek kaydıyla"
diyor; Madde 9.2 üçüncü taraf hak ihlalinin sorumluluğunu katılımcıya
yüklüyor; Madde 10.4 veri seti lisansını beyan edilecekler arasında
sayıyor.

Bu, teslim öncesi kapatılması gereken en acil boşluktur ve kod işi
değildir. Ayrıntı ve kapatma yolu: `docs/lisans-analizi.md` Bölüm 2.1.1.

### Bu veri setinin bilinen sınırları

`results/bilinen-sinirlar.md` Bölüm B'de ölçülmüş hâlleriyle:

- **`seramik` pratikte çalışmıyor** — testte mAP50 0,0877, en az örnekli sınıf.
- **`beton_tugla` iki malzemeyi birlikte kapsıyor** — geri kazanım
  yönlendirmesi açısından ikisi farklı süreçlere gider.
- **Alan uyuşmazlığı:** görüntüler internetten toplanmış; kullanım alanı
  afet enkaz sahası. Saha başarımı ölçülenden **düşük olacaktır** ve ne
  kadar düşük olacağı ölçülmemiştir.
- **Kapsanmayan gruplar:** `dolgu_toprak`, `sert_plastik`,
  `yumusak_plastik`, `tekstil`, `karton`, `alcipan` — model bunları
  tanımaz ve çıktıda görünmemeleri "sahada yok" anlamına gelmez.

### Bakanlık verisi

Bakanlık tarafından sağlanan veriler **hiçbir dış yapay zekâ servisine
veya bulut model sağlayıcısına gönderilmez.** Model çıkarımı yerel
altyapıda yapılır. Ayrıntı: [`docs/veri-politikasi.md`](veri-politikasi.md).

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

⚠️ Eşik (varsayılan 0,50) **ölçülmüş bir değer değildir** — ama sebebi
değişti. Eski gerekçe "model henüz eğitilmedi" idi; model 01.09.2026'da
eğitildi ve ölçüldü.

Eşik yine de türetilemiyor: doğru seçmek için precision ve recall'un
**güvene göre** değişimi gerekir, elimizdeki `results/egitim/metrikler.json`
ise her sınıf için tek bir çalışma noktası veriyor. Eğriler yalnızca
görsel olarak var (`results/egitim/gorseller/*_BoxF1_curve.png`); bir
görselden sayı okumak ölçüm değildir.

Gerekli olan: eğitim ortamında eşiği tarayan bir doğrulama koşusunun ham
p/r/f1 dizileri. O gelene kadar 0,50 bir mühendislik varsayımıdır ve
ortam değişkeniyle değiştirilebilir tutulmuştur.

**Pratik etkisi gizlenmiyor:** modelin genel precision'ı val'de 0,53;
yani bu eşiğin üstünde kalan tespitlerin azımsanmayacak kısmı da
yanlıştır. Sistemin cevabı eşiği yükseltmek değil **doğrulama
kapısıdır**: doğrulanmamış hiçbir tespit miktara, haritaya ya da rapora
girmez.

### "Reddet" aksiyonu bilinçli olarak yoktur

Uzman bir tespiti reddedemez; yalnızca onaylayabilir, düzeltebilir ya da
belirsiz işaretleyebilir. Reddetmek kaydın bilgi değerini yok eder;
"belirsiz" kaydı izlenebilir tutarak ikinci incelemeye açık bırakır
(`docs/karar-kaydi.md` K-004).

---

## 6. Hata ve yanlılık riski

Riskler gizlenmez; ölçülmüş sınır, ölçülmemiş iddiadan güçlüdür.
Tam liste: [`results/bilinen-sinirlar.md`](../results/bilinen-sinirlar.md).

### 6.1. Ölçülmüş başarım düşük — en büyük risk

Genel mAP50 **0,43–0,44**. Metalin recall'ü 0,32–0,35: bulduğunu doğru
buluyor ama **çoğunu kaçırıyor.** `seramik` testte 0,0877 ile pratikte
çalışmıyor.

**Sonuç:** Zorunlu uzman doğrulaması bir süs değil, sistemin çalışma
koşuludur. Bir malzemenin çıktıda görünmemesi **"sahada yok" anlamına
gelmez** — bu ilke burada sayıyla karşılanmaktadır.

### 6.2. Alan yanlılığı

Eğitim görüntüleri internetten toplanmış; kullanım alanı afet enkaz
sahasıdır.

| | Eğitim verisi | Afet enkazı (kullanım) |
|---|---|---|
| Sahne | Çerçevelenmiş, seçilmiş kare | Açık, düzensiz saha |
| Ölçek | Değişken, çoğu yakın çekim | Değişken, çoğu zaman uzak/havadan |
| Toz / renk | Temiz görüntü | Yoğun toz, renk bozulması |
| Malzeme durumu | Genelde ayrışmış | Çökmüş yapı, iç içe geçmiş |

**Sonuç:** Saha başarımı ölçülen 0,43–0,44'ten **düşük olacaktır.** Ne
kadar düşük olacağı **ölçülmemiştir** ve ölçülene kadar hiçbir genelleme
iddiası yapılmamaktadır.

### 6.3. Temsil yanlılığı — kutu ile maske farkı

Sınırlayıcı kutu, iç içe geçmiş malzemelerde **kaba** bir temsildir ve
komşu malzemeyi kendi alanına katabilir. Bu, alan tabanlı her hesabı
yukarı yönlü saptırır. Enkaz sahnesi tanımı gereği iç içe geçmiş
olduğundan bu sapma burada kuraldır, istisna değil.

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
| Modelin adı | Bölüm 1 | YOLO11m — eğitildi, mAP50 0,43–0,44 |
| Lisansı | Bölüm 2 | AGPL-3.0 — Madde 10.4 uyarınca ayrıca beyan |
| Eğitim/veri kaynağı | Bölüm 3 | Takımın kendi veri seti, 5 sınıf · 🔴 lisans beyanı eksik |
| Dış API kullanımı | Bölüm 4 | Yapay zekâ amaçlı dış API **yok** |
| Çıktı doğrulama yöntemi | Bölüm 5 | Zorunlu uzman doğrulaması + veri katmanı kısıtları |
| Hata/yanlılık riski | Bölüm 6 | Beş risk açıkça sayılmış |
| Açıklanabilirlik yaklaşımı | Bölüm 7 | İzlenebilirlik; sahte açıklama üretilmez |
