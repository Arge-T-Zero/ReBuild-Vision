# Çevresel Etki Doğrulama

**Dayanak:** Şartname **Madde 10.9** — Çevresel Etki Doğrulama Maddesi

> "Projeler, sundukları çevresel faydayı ölçülebilir göstergelerle
> açıklamalıdır. Atık azaltımı, geri kazanım oranı, kaynak verimliliği,
> karbon azaltım potansiyeli, maliyet avantajı ve davranış değişikliği
> etkisi gibi iddialar varsayım, yöntem ve veri kaynağı ile birlikte
> sunulacaktır."

**Son güncelleme:** 01.09.2026

---

## 0. Bu belgenin duruşu

Madde 10.9 iki şey söylüyor: faydayı **ölçülebilir göstergelerle**
açıkla, ve **iddialarını** varsayım/yöntem/kaynakla birlikte sun.

Bu belge birincisini yapar, ikincisini **bilinçli olarak yapmaz** —
çünkü bugün beyan edilebilecek doğrulanmış bir sayı yoktur.

> **Bu projede hiçbir çevresel fayda sayısı iddia edilmemektedir.**
> Ne ton, ne yüzde, ne karbon, ne para.

Bu bir eksiklik değil, projenin en temel kuralının çevresel etki
tarafındaki karşılığıdır: *ölçülmemiş sayı üretilmez.* Aynı kural
miktar hesabında da işler — ölçüm yoksa tonaj yazılmaz, katsayının
kaynağı yoksa hesap yapılmaz.

Bir enkaz sahasında "%40 geri kazanım sağladık" cümlesi, dayanağı
olmadan söylendiğinde yalnızca yanlış değil, **zararlıdır**: kaynak
planlaması o sayıya göre yapılır.

Bunun yerine bu belge şunu sunar: **hangi göstergeyi, hangi yöntemle,
hangi veriden üreteceğimiz** ve **o sayıyı üretebilmek için tam olarak
neyin eksik olduğu.** Eksik kapandığında sayı buraya yazılacaktır — bir
gün önce değil.

---

## 1. Sistemin bugün gerçekten ürettiği ölçülebilir çıktı

Bunlar iddia değil, sistemin çalışan davranışıdır ve doğrulanabilir:

| Çıktı | Nasıl üretiliyor | Güvenilirlik |
|---|---|---|
| Görünür malzeme sınıfı dağılımı | Model ön tahmini + **zorunlu uzman doğrulaması** | Yalnızca doğrulanmış kayıtlar sayılır |
| Tespit başına miktar **aralığı** | Saha ölçümü + kaynaklı katsayı | Tek değer değil, alt–üst aralık |
| Kullanılan yöntem ve katsayı kaynağı | Her miktar kaydında yazılı | İzlenebilir |
| Kim, ne zaman, ne yaptı | İşlem geçmişi (otomatik) | Kapatılamaz |
| Saha konumu ve sınırı | PostGIS geometrisi | GeoJSON olarak dışa aktarılabilir |

**Kritik ayrım:** Sistem "sahada şu kadar beton var" demez. "Doğrulanmış
şu tespitlerde, şu ölçümlere dayanarak, şu aralıkta beton ölçülmüştür"
der. İkisi arasındaki fark, bu projenin tamamıdır.

---

## 2. Hedeflenen göstergeler ve hesap yöntemi

Aşağıdaki dört gösterge, sistemin veri modelinden **türetilebilir**.
Her biri için yöntem yazılıdır; eksik girdi ayrıca işaretlenmiştir.

### G1. Doğrulanmış malzeme miktarı (ton)

**Yöntem:**

```
Bir tespit için:
  doğrudan ağırlık ölçümü varsa  →  miktar = ölçülen değer (katsayı yok)
  hacim ölçümü varsa             →  miktar_alt = hacim × katsayı_alt
                                    miktar_üst = hacim × katsayı_üst
  ölçüm yoksa                    →  MİKTAR ÜRETİLMEZ
```

**Veri kaynağı (katsayılar):** U.S. EPA, Office of Resource Conservation
and Recovery — *Volume-to-Weight Conversion Factors*. Değerler lb/yd³
cinsindendir; `katsayilar.json` içinde ton/m³'e çevrilmiştir (çarpan
0,000593276; dayanağı: 1 lb = 0,45359237 kg, 1 yd³ = 0,764554857984 m³).

**Durum — dokuz malzeme sınıfından yalnızca dördü kullanılabilir:**

| Sınıf | Aralık (ton/m³) | Durum |
|---|---|---|
| ahşap | 0,1003 – 0,159 | ✅ kaynaklı |
| metal | 0,0279 – 0,1335 | ✅ kaynaklı |
| tekstil | 0,0742 – 0,1038 | ✅ kaynaklı |
| karton | 0,0442 – 0,0629 | ✅ kaynaklı |
| **beton** | — | ❌ **kapalı** |
| dolgu toprak | — | ❌ kapalı |
| alçıpan | — | ❌ kapalı |
| sert plastik | — | ❌ kapalı |
| yumuşak plastik | — | ❌ kapalı |

⚠️ **Beton kapalı olduğu için bu gösterge bugün enkaz sahasının ana
kütlesini kapsamıyor.** Kapalı olmasının sebebi veri yokluğu değil,
**aralık** yokluğu: EPA beton için tek nokta değer veriyor (860 lb/yd³ ≈
0,510 ton/m³), aralık vermiyor. Tek değerle miktar üretmek belirsizlik
aralığı kuralını çiğnerdi; **aralık uydurulmadı**, satır kapalı
bırakıldı.

**Eksik:** Beton, dolgu toprak ve alçıpan için **aralık veren ikinci bir
kaynak.** Plastikler için inşaat/yıkım alanından kaynak bulunamadı.

#### Beton araştırması — 01.09.2026, sonuç: değer yazılmadı

Beton için kaynak arandı ve **uygun kaynak bulunamadı.** Bulunan şey,
sorunun sanılandan zor olduğuydu: yayımlanmış "beton" dönüşüm değerleri
**860 ile 4.200 lb/yd³ arasında, yani beşe katlanıyor.**

Sebep bir ölçüm belirsizliği değil, **kategori farkı**:

| Kategori | Yaklaşık değer | Ne ölçüyor |
|---|---|---|
| Katı beton | ~4.050 lb/yd³ | Dökülmüş, boşluksuz beton |
| Kırılmış/gevşek moloz | ~2.025 lb/yd³ | Konteynere atılmış kırık beton |
| **EPA (elimizdeki)** | **860 lb/yd³** | Gevşek Y&D atığı |
| Karışık Y&D atığı | ~417 lb/yd³ | Sınıflandırılmamış moloz |

Enkaz sahasındaki malzeme **gevşek moloz** kategorisindedir. Bu aralığın
ortasından bir sayı seçmek kategorileri karıştırmak olurdu ve tonajı
katlayabilirdi — bu, dayanaksız bir sayının neden yalnızca yanlış değil
**zararlı** olduğunun somut örneğidir.

İkinci aday (Contra Costa County dönüşüm tablosu, 1.400 lb/yd³)
**belgenin kendisine erişilemediği için doğrulanamadı**; ayrıca betonu
asfaltla birlikte veriyor.

**Gereken şey "bir sayı" değil:** gevşek yıkım molozu kategorisinde
**alt–üst aralığı** veren, doğrulanabilir tek bir kaynak. Ayrıntı:
`katsayilar.json` → `acik_sorular`.

### G2. Geri kazanım yönlendirme oranı

**Yöntem:**

```
oran = (geri kazanılabilir sınıfa ait doğrulanmış miktar)
       ÷ (doğrulanmış toplam miktar)
```

`konteyner` sınıfı paydaya **girmez** — malzeme değildir
(`siniflar.json` → `malzeme_mi: false`, karar `K-007`).

**Durum:** Yöntem hazır, G1'e bağlı. G1 kapsanmadan bu oran anlamlı
değildir.

**Ayrıca eksik:** Hangi sınıfın hangi geri kazanım akışına gittiği
Türkiye mevzuatına göre tanımlanmalıdır. Bu, EPA katsayı tablosundan
gelmez — **Atık Yönetimi Yönetmeliği ve atık kodları** esas alınmalıdır.

### G3. Karbon azaltım potansiyeli

**Yöntem:**

```
potansiyel = Σ (malzeme_miktarı × emisyon_faktörü)
              malzeme
```

⚠️ **Bu gösterge bugün hesaplanamaz ve hesaplanmaya çalışılmamıştır.**

**Eksik olan tek şey emisyon faktörleridir** ve bunlar **uydurulamaz.**
Bir emisyon faktörü, malzemenin düzenli depolamaya gitmesi ile geri
kazanılması arasındaki farkı ifade eder; ülkeye, tesise ve sürece göre
değişir. Yanlış bir faktör, sonucu kat kat saptırır.

**Kabul edilebilir kaynak sırası:**

1. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı'nın yayımladığı
   dönüşüm/emisyon faktörü tablosu — **varsa öncelikle bu**
2. TÜİK atık istatistikleri
3. Uluslararası, yöntemi yayımlanmış bir kaynak (ülke farkı açıkça
   beyan edilmek kaydıyla)

Kaynak bulunana kadar bu satır boş kalır.

### G4. Karar süresi ve izlenebilirlik kazancı

**Yöntem:** İşlem geçmişi zaman damgalıdır. "Görüntü yüklenmesi →
uzman doğrulaması" ve "doğrulama → ölçüm girişi" süreleri sistemden
**doğrudan ölçülebilir.**

**Durum:** Ölçüm altyapısı hazır ve çalışıyor; ancak gerçek saha
kullanımı olmadığı için **veri yoktur.** Sentetik demo verisinden
üretilecek bir süre sayısı gerçek bir kazancı temsil etmez.

Bu gösterge, pilot uygulamada (Madde 10.10) ilk ölçülebilecek olandır —
çünkü dış bir katsayıya değil, yalnızca sistemin kendi kaydına dayanır.

---

## 3. Varsayımlar — açıkça

Bir sayı üretildiğinde altında duracak varsayımlar. Şimdiden yazılıdır ki
sonradan sessizce değiştirilemesin.

| # | Varsayım | Risk |
|---|---|---|
| V1 | Görünür yüzey, sahanın malzeme dağılımını temsil eder | 🔴 **Doğrulanmamış.** Enkaz altı görülmez; yüzeydeki dağılım alttakinden farklı olabilir |
| V2 | Uzman doğrulaması model hatasını düzeltir | 🟡 Uzmanın da yanılma payı vardır; sistem çift doğrulama zorlamaz |
| V3 | Hacim ölçümü doğru alınmıştır | 🟡 Ölçümün yöntemi kayıtlıdır ama doğruluğu sistemce sınanamaz |
| V4 | EPA katsayıları Türkiye yapı malzemesi için geçerlidir | 🔴 **Doğrulanmamış.** Değerler ABD inşaat/yıkım karakterizasyonundan gelir; Türkiye pratiği farklı olabilir |
| V5 | Sınırlayıcı kutu, malzeme alanını doğru temsil eder | 🟡 Kutu, bölütleme maskesinden kabadır; komşu malzemeyi kapsayabilir |

V1 ve V4 kırmızıdır: birincisi projenin **tasarım sınırıdır** ve
kapatılamaz (`results/bilinen-sinirlar.md` A.3); ikincisi kapatılabilir
ve kapatılması gerekir.

---

## 4. Sistemin çevresel faydaya asıl katkısı

Sayı üretilemiyor olması, faydanın olmadığı anlamına gelmiyor. Bu
sistemin katkısı bir sayıda değil, **kararın dayanağında**:

**Bugün:** Enkaz sahasında malzeme ayrıştırma kararı çoğunlukla gözle,
tecrübeyle ve kayıt tutulmadan verilir. Karar sonradan denetlenemez,
çünkü neye dayandığı yazılı değildir.

**Bu sistemle:** Her karar bir görüntüye, bir uzman onayına, bir ölçüme
ve bir zaman damgasına bağlanır. Miktar, aralığı ve yöntemiyle birlikte
saklanır. Kim ne yaptı, geri dönülüp görülebilir.

Bu **doğrudan** bir çevresel fayda değildir — ama geri kazanım oranını
gerçekten artıracak her müdahalenin ön koşuludur: **ölçemediğin şeyi
iyileştiremezsin.** Sistemin ürettiği asıl değer, bugün var olmayan
ölçüm kaydının kendisidir.

Bir ikinci katkı daha var: sistem **yanlış sayı üretmeyerek** de fayda
sağlar. Dayanaksız bir tonaj tahmini, ona göre planlanan araç, personel
ve tesis kapasitesi demektir.

---

## 5. Bu boşluğun kapanması için gereken

Sıraya konmuş, somut:

| # | Gereken | Kim / nereden | Açar |
|---|---|---|---|
| 1 | Beton için **aralık** veren kaynak | Literatür / Bakanlık tablosu | G1'in ana kütlesi |
| 2 | Bakanlık dönüşüm katsayısı tablosu (varsa) | Bakanlık | G1 — EPA'nın yerini alır, V4 riskini kapatır |
| 3 | Emisyon faktörleri | Bakanlık / TÜİK | **G3'ün tamamı** |
| 4 | Atık kodu ↔ sınıf eşlemesi | Atık Yönetimi Yönetmeliği | G2 |
| 5 | Modelin eğitilmesi ve ölçülmesi | Proje ekibi | Tüm göstergelerin güvenilirliği |
| 6 | Pilot saha kullanımı | Madde 10.10 protokolü | G4 |

1–4 arası **mentör görüşmesinde sorulacaktır** (Madde 5.2). Özellikle
2 ve 3 doğrudan Bakanlık'ın elinde olabilir; varsa dış kaynak
aramaya gerek kalmaz.

---

## 6. Beyan

Bu proje, çevresel fayda konusunda **hiçbir gerçekleşmiş sonuç beyan
etmemektedir**: ne atık azaltımı, ne geri kazanım oranı, ne karbon
azaltımı, ne maliyet avantajı.

Beyan edilen şey yöntemdir: hangi göstergenin hangi veriden, hangi
formülle ve hangi kaynağa dayanarak üretileceği yukarıda yazılıdır.
Eksik girdiler adıyla ve kaynağıyla listelenmiştir.

Bu tutum, teslim edilmiş ön değerlendirme raporundaki duruşun
sürdürülmesidir:

> "Bu nedenle raporda model doğruluğu, geri kazanım oranı, karbon
> tasarrufu veya ekonomik faydaya ilişkin gerçekleşmiş sonuç beyan
> edilmemektedir."

Sonuçlar geldiğinde bu belge güncellenecek ve sayılar varsayım, yöntem
ve kaynağıyla birlikte buraya yazılacaktır.
