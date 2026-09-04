# Bilinen Sınırlar

> **İlke (ana talimat Bölüm 14):** Ölçülmüş bir sınır, ölçülmemiş bir
> iddiadan güçlüdür. Bu dosya sistemin yapamadıklarını gizlemek yerine
> sayar.

**Son güncelleme:** 02.09.2026 — B bölümü baştan yazıldı, C bölümünün
ilk iki satırı ölçüldü olarak kapandı

Sınırlar iki gruba ayrılıyor: **tasarım gereği olanlar** (bilinçli seçim,
değişmeyecek) ve **mevcut durum sınırları** (veri/zaman kaynaklı,
ölçüldükçe güncellenecek).

---

## A. Tasarım gereği — bunlar hata değil, karar

Bu dört madde teslim edilmiş raporda taahhüt edilmiştir ve ihlal edilemez.

### A.1. Ölçüm yoksa miktar üretilmez

Yeterli ölçüm bulunmayan alanlar için tonaj tahmini **oluşturulmaz**.
Miktar alanı boş kalır; varsayılan değer, tahmini değer, "≈0" veya
"hesaplanıyor" yazılmaz. *(Rapor 3.6)*

Miktar hesaplandığında tek bir kesin değer değil, **belirsizlik aralığı ve
kullanılan yöntem** birlikte gösterilir. *(Rapor 4)*

### A.2. Tehlikeli madde teşhisi yapılmaz

Asbest ve benzeri tehlikeli maddeler görüntü üzerinden **teşhis edilmez**.
Hiçbir tahmin, ikon, renk kodu, uyarı rozeti veya olasılık değeri
üretilmez. *(Rapor 3.5)*

**Kritik:** Analiz sonucu bulunmayan alan için **"güvenli" veya "tehlikesiz"
değerlendirmesi de yapılmaz.** Yokluk, güvenlik anlamına gelmez.
*(Rapor 12)*

### A.3. Enkaz altı görülmez

Sistem yalnızca **görünür yüzeye** ilişkin ön değerlendirme yapar. Toplam
enkaz içeriği iddiası hiçbir yerde üretilmez. *(Rapor 12)*

### A.4. Nihai kararı sistem vermez

Her model çıktısı **"ön tahmin"** etiketiyle görünür. Nihai operasyon kararı
yetkili kurum ve uzmanlar tarafından verilir. Doğrulanmamış kayıtlar miktar
ve yönlendirme hesaplarına girmez. *(Rapor 3.7 ve 12)*

---

## B. Eğitim verisinden kaynaklanan sınırlar

**Güncelleme — 02.09.2026.** Bu bölüm baştan yazıldı. Önceki hâli
CDW-Seg veri setini anlatıyordu; **model o veri setiyle eğitilmedi.**
Eğitim, üç kamuya açık CC BY 4.0 veri setinin birleşimiyle **5 sınıflı**
bir veri setiyle yapıldı (`results/egitim/veri_seti_kunyesi.json`).

Önceki sürümün "cam ve seramik eğitim verisinde yok, model tanımaz"
tespiti **artık geçersizdir** — ikisi de eğitildi; `cam` modelin en iyi
sınıfı.

### B.1. 🔴 Veri setinin kaynak ve lisans beyanı eksik

Görüntüler takımca toplanmıştır. **Nereden toplandığı ve hangi hakla
kullanıldığı henüz yazılı değildir.**

Şartname iki yerden bağlıyor:

- **Madde 5.2:** takımlar kendi veri setlerini kullanabilir — *"kaynaklarını
  açıkça belirtmek kaydıyla"*.
- **Madde 9.2:** *"Katılımcılar, geliştirdikleri projelerin ... herhangi bir
  üçüncü kişi veya kuruluşa ait hakları ihlal etmediğini beyan eder. Aksi
  durumda doğabilecek tüm hukuki ve mali sorumluluk ilgili katılımcıya
  aittir."*

Madde 5.5 ürünü Kuruma devrettiği için bu, teslim sonrasına da uzanan bir
sorumluluktur. **Kapatılması gereken en acil boşluk budur** ve kod işi
değildir. Ayrıntı: `docs/lisans-analizi.md` Bölüm 2.1.

### B.2. 🔴 `seramik` sınıfı pratikte çalışmıyor

Testte **mAP50 = 0,0877** (precision 0,229 · recall 0,119). En az örneğe
sahip sınıf: 939 / 97 / 42 kutu.

**Sonuç:** Bu sınıfın çıktısı kullanılabilir sayılmamalıdır. Sistem onu
gizlemiyor — ama uzman doğrulaması bu sınıfta bir formalite değil,
zorunluluktur.

### B.3. 🟡 Genel başarım düşük

Genel mAP50 **0,43–0,44**. Tespitlerin ancak bir kısmı doğru bulunuyor.
Metalin recall'ü 0,32–0,35: **bulduğunu doğru buluyor ama çoğunu
kaçırıyor.** Bir malzemenin çıktıda görünmemesi "sahada yok" anlamına
gelmez — bu, sistemin en temel ilkelerinden biridir ve burada sayıyla
karşılanır.

### B.4. 🔴 Alan uyuşmazlığı: internet görüntüsü ≠ deprem enkazı

Veri seti internetten toplanmış görüntülerden oluşuyor; proje ise afet
sonrası **enkaz sahası** iddiasındadır.

| | Eğitim verisi | Afet enkazı |
|---|---|---|
| Sahne | Çerçevelenmiş, seçilmiş kare | Açık, düzensiz saha |
| Ölçek | Değişken, çoğu yakın çekim | Değişken, çoğu zaman uzak/havadan |
| Toz / renk | Temiz görüntü | Yoğun toz, renk bozulması |
| Malzeme durumu | Genelde ayrışmış | Çökmüş yapı, iç içe geçmiş |

**Sonuç:** Saha başarımı ölçülen 0,43–0,44'ten **düşük olacaktır.** Ne
kadar düşük olacağı **henüz ölçülmemiştir** ve ölçülene kadar hiçbir
genelleme iddiası yapılmamaktadır.

### B.5. 🔴 `metal` sınıfı YOK (v2) · beton ve tuğla artık ayrı

Sınıf, betonu ve tuğlayı ayırmaz. Geri kazanım yönlendirmesi açısından
ikisi farklı süreçlere gider. Ayrıca hacim→ağırlık katsayısı bu yüzden
iki kat belirsiz (`katsayilar.json`).

### B.6. 🟡 Katsayı 5 sınıftan yalnızca 2'sinde var

Yalnızca `ahsap` kaynaklı (U.S. EPA); `beton`, `tugla`, `cam` ve `seramik`
kapalı. **Beton kapalı olduğu için miktar hesabı enkazın ana kütlesini
kapsamıyor.** Ayrıntı ve neden bir sayı seçilmediği:
`docs/cevresel-etki.md` Bölüm 2.

### B.7. 🟡 Etiketler kutu, çıktı kutu — ama kutu kaba bir temsildir

İç içe geçmiş malzemelerde sınırlayıcı kutu komşu malzemeyi kendi alanına
katabilir. Bu, alan tabanlı her hesabı yukarı yönlü saptırır.

---

## C. Henüz ölçülmemiş olanlar

Aşağıdakiler için **hiçbir sayı beyan edilmemektedir.** Ölçüm yapıldıkça
bu bölüm `results/model-metrikleri.md` ile birlikte güncellenecektir.

> **02.09.2026 — bu tablonun ilk iki satırı kapandı.** Model
> 01.09.2026'da eğitildi ve ölçüldü; sınıf bazlı metrikler ve karışıklık
> matrisleri artık elde. Kapanan satırlar aşağıda üstü çizili bırakıldı
> ki neyin ne zaman ölçüldüğü izlenebilsin.

| Sınır | Durum |
|---|---|
| ~~Sınıf bazında precision / recall / F1 / mAP~~ | ✅ **ölçüldü** — `results/model-metrikleri.md`, B.2 bölümü |
| ~~Hangi sınıfların birbirine karıştığı (karışıklık matrisi)~~ | ✅ **ölçüldü** — `results/egitim/gorseller/val_{val,test}__confusion_matrix.png` |
| Düşük güven eşiğinin (`needs_review`) doğru değeri | ⏳ **hâlâ ölçülmedi, ama sebebi değişti.** Eşiği türetmek için precision/recall'un güvene göre değişimi gerekir; elimizdeki ölçüm her sınıf için tek çalışma noktası veriyor. Eğriler yalnızca görsel olarak var. 0,50 gerçek serviste de bir mühendislik varsayımıdır |
| Afet enkazı görüntülerinde başarım düşüşü | ⏳ henüz ölçülmedi (bkz. B.3) |
| Çıkarım süresi ve eşzamanlı istek kapasitesi | ⏳ henüz ölçülmedi |
| Toz / düşük ışık / hareket bulanıklığı etkisi | ⏳ henüz ölçülmedi |

---

## D. Kapsam dışı bırakılanlar

Bunlar sınır değil, **bilinçli kapsam kararıdır**; rapor Bölüm 12'de sonraki
sürümlere bırakıldığı beyan edilmiştir:

fotogrametri / ortofoto üretimi · karbon ve ekonomik değer hesabı ·
kamu sistemi entegrasyonu · tesis yönlendirme optimizasyonu ·
çok dilli arayüz · bildirim sistemi
