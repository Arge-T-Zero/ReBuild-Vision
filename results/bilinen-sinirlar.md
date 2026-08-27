# Bilinen Sınırlar

> **İlke (ana talimat Bölüm 14):** Ölçülmüş bir sınır, ölçülmemiş bir
> iddiadan güçlüdür. Bu dosya sistemin yapamadıklarını gizlemek yerine
> sayar.

**Son güncelleme:** 27.08.2026

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

Kaynak: **CDW-Seg** (CC0, DOI 10.6084/m9.figshare.28573229).
Karar gerekçesi: `docs/karar-kaydi.md` K-006.

### B.1. 🔴 Cam ve seramik sınıfları eğitim verisinde YOK

Teslim edilmiş rapor *"beton/tuğla, metal, ahşap, cam ve seramik **gibi**
ana malzeme grupları"* diyor. CDW-Seg'in on sınıfı içinde **cam** ve
**seramik** bulunmuyor.

**Sonuç:** Model bu iki malzeme grubunu **tanımaz**. Sahada cam veya seramik
bulunsa dahi tespit edilmez veya başka bir sınıfa atanır.

**Sistem ne yapıyor:** Bu iki sınıf için tahmin üretmiyor. Ayrıca bir
sınıfın çıktıda görünmemesi, **"o malzeme sahada yok" anlamına gelecek
biçimde gösterilmiyor** — A.2'deki "yokluk güvenlik değildir" ilkesinin
malzeme tarafındaki karşılığı.

**Kapatmak için ne gerekir:** Cam ve seramik için etiketli görüntü toplanıp
veri setine eklenmesi. Bu sürüm kapsamında yapılmadı.

### B.2. 🟡 Tuğla, betondan ayrılmıyor

CDW-Seg'in `concrete` sınıfı betonu kapsar; **tuğla ayrı bir sınıf
değildir.** Rapordaki "beton/tuğla" ifadesi tek bir sınıfa karşılık geliyor.

**Sonuç:** Tuğla ağırlıklı bir enkazda malzeme dağılımı `beton` olarak
raporlanır. Geri kazanım yönlendirmesi açısından bu ikisi farklı süreçlere
gider — sınır burada.

### B.3. 🔴 Alan uyuşmazlığı: şantiye konteyneri ≠ deprem enkazı

CDW-Seg görüntüleri **şantiyelerdeki hurda konteynerlerinden** (skip bin)
çekilmiştir. Proje ise afet sonrası **enkaz sahası** iddiasındadır.

İki alan arasındaki farklar:

| | CDW-Seg | Afet enkazı |
|---|---|---|
| Sahne | Sınırlı, çerçevelenmiş konteyner | Açık, düzensiz saha |
| Ölçek | Yakın çekim | Değişken, çoğu zaman uzak/havadan |
| Toz/renk | Şantiye koşulu | Yoğun toz, renk bozulması |
| Malzeme durumu | Ayrışmış, üst üste | Çökmüş yapı, iç içe geçmiş |

**Sonuç:** Modelin afet enkazı görüntülerindeki başarımı, CDW-Seg üzerinde
ölçülen başarımdan **düşük olacaktır.** Ne kadar düşük olacağı
**henüz ölçülmemiştir.**

**Sistem ne yapıyor:** Bu fark ölçülene kadar hiçbir genelleme iddiası
yapılmıyor. `results/model-metrikleri.md` yalnızca üzerinde ölçüm yapılan
veri kümesini adıyla belirtir.

### B.4. 🟡 Etiketler bölütleme maskesi, çıktı kutu

CDW-Seg anlamsal bölütleme (semantic segmentation) etiketleri içerir.
Sistemin arayüz sözleşmesi ise sınırlayıcı kutu (bbox) üzerinedir.

**Sonuç:** Kutular COCO formatındaki maskelerden türetiliyor. İç içe geçmiş
malzemelerde kutu, maskeden daha kaba bir temsildir — birbirine değen iki
malzemenin kutuları örtüşür.

**Etkilenen alan:** `bbox_format` alanı bu nedenle veri modelinde zorunlu
tutuluyor (`NOT NULL`); kutunun hangi koordinat uzayında verildiği
belirsiz bırakılmıyor.

---

## C. Henüz ölçülmemiş olanlar

Aşağıdakiler için **hiçbir sayı beyan edilmemektedir.** Ölçüm yapıldıkça
bu bölüm `results/model-metrikleri.md` ile birlikte güncellenecektir.

| Sınır | Durum |
|---|---|
| Sınıf bazında precision / recall / F1 / mAP | ⏳ henüz ölçülmedi |
| Hangi sınıfların birbirine karıştığı (karışıklık matrisi) | ⏳ henüz ölçülmedi |
| Düşük güven eşiğinin (`needs_review`) doğru değeri | ⏳ henüz ölçülmedi — şu an sahte serviste 0.50 varsayılıyor |
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
