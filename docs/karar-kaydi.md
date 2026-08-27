# Karar Kaydı

Proje boyunca alınan teknik ve hukuki kararlar, tarihli ve gerekçeli.
Mentör görüşmelerinden (şartname Madde 5.2, en az 4 görüşme) çıkan kararlar
da buraya işlenir.

Biçim: her karar bir başlık · **Tarih · Karar · Gerekçe · Alternatif ·
Durum**.

---

## K-001 · Web arayüzü teknolojisi

- **Tarih:** 27.08.2026
- **Karar:** React 19 + Vite + TypeScript ile bağımsız bir web uygulaması.
- **Gerekçe:** Ölçüt, ana talimat Bölüm 8.1'de tek cümleyle konmuştu:
  *9 günde bitip bitmeyeceği.* React'in harita ve veri-tablosu ekosistemi
  (Leaflet, TanStack Query) en olgun olanı; jüri sistemi tarayıcıda açacak.
- **Alternatif:** Flutter Web — mobil ile ortak kod tabanı sağlardı, ancak
  harita/tablo yoğun panellerde derleme süresi ve paket boyutu maliyeti
  yüksek. Vue 3 — uygun ama ekipte deneyim avantajı yok.
- **Durum:** Uygulandı.

---

## K-002 · Harita kütüphanesi — `react-leaflet` reddedildi

- **Tarih:** 27.08.2026
- **Karar:** Çıplak `leaflet@1.9.4` (BSD-2-Clause) kullanılacak. React
  entegrasyonu `web/src/lib/leaflet/` altında kendi yazdığımız ince
  sarmalayıcıdır. **`react-leaflet` kullanılmayacak.**
- **Gerekçe:** `react-leaflet@5.0.0` lisansı `Hippocratic-2.1`
  (27.08.2026'da `npm view` ile doğrulandı). Bu OSI onaylı bir açık kaynak
  lisansı değildir; kullanım kısıtları ve fesih maddesi içerir. Şartname
  Madde 5.5 ürünün Kuruma **bedelsiz ve koşulsuz** devrini istiyor —
  kullanım kısıtı taşıyan bir bileşen bu devri kirletir.
- **Alternatif:** MapLibre GL (BSD-3) — lisansı temiz, ancak vektör karo
  sağlayıcısı (API anahtarı) veya kendi karo sunucumuz gerekir; 9 günde
  ek yük.
- **Durum:** Uygulandı. Ayrıntı: `docs/lisans-analizi.md` Bölüm 5.1.

---

## K-003 · Veri tabanı sürücüsü — `psycopg` yerine `asyncpg`

- **Tarih:** 27.08.2026
- **Karar:** `asyncpg` (Apache-2.0) kullanılacak.
- **Gerekçe:** `psycopg2-binary` LGPL, `psycopg@3` ise LGPL-3.0-only
  (PyPI meta verisinden doğrulandı). LGPL zayıf kopyaleft olduğu için
  kullanılabilirdi, ancak Madde 5.5 devrinde gereksiz bir kopyaleft yüzeyi
  oluşturur. Bu kararla kopyaleft yüzeyi yalnızca YOLO11 (AGPL) ve
  PostGIS (GPL-2.0) ile sınırlandı.
- **Durum:** Uygulandı. Ayrıntı: `docs/lisans-analizi.md` Bölüm 5.2.

---

## K-004 · `dogrulama_durumu` değer kümesi — rapordaki çelişki çözüldü

- **Tarih:** 27.08.2026
- **Karar:** `beklemede | onaylandi | duzeltildi | belirsiz`
- **Gerekçe:** Teslim edilmiş raporda bir tutarsızlık var. **Gövde metni**
  üç ayrı yerde (Bölüm 3.5, 6 ve 9) *"onaylayacak, düzeltecek ya da
  belirsiz olarak işaretleyecektir"* diyor. **Şekil 1**'in KATMAN 3
  kutusunda ise *"onayla · düzelt · reddet"* yazıyor. Gövde metni esas
  alındı: üç yerde tekrarlanıyor, şekilde bir kez geçiyor.
- **Jüri sorarsa cevap:** "Reddet" eylemi bilinçli olarak yoktur. Bir
  tespiti reddetmek, o kaydın bilgi değerini yok eder; "belirsiz" ise
  kaydı izlenebilir tutarak ikinci bir incelemeye açık bırakır. Rapor
  gövdesi de bu tasarımı anlatır.
- **Durum:** Uygulandı.

---

## K-005 · Kimlik doğrulama — tamamen yerel

- **Tarih:** 27.08.2026
- **Karar:** bcrypt parola özeti + JWT (HS256), tamamen kendi backend'imizde.
  Hiçbir bulut kimlik servisi kullanılmayacak.
- **Gerekçe:** Madde 9.1 ve Madde 10.5 verinin dışarı çıkmasını yasaklıyor.
  Ayrıca Madde 10.3 "bağımsız bir ortamda kurulabilir ve çalıştırılabilir"
  diyor — dış servise bağımlı bir kimlik katmanı bunu imkânsız kılardı.
- **Alternatif:** Supabase Auth — hızlı kurulum, ancak yukarıdaki üç maddeyle
  de çelişir.
- **Durum:** Uygulandı.

---

## K-006 · Eğitim veri seti — CDW-Seg ve on sınıf

- **Tarih:** 27.08.2026
- **Karar:** CDW-Seg veri seti (CC0) kullanılacak; modelin sınıf kümesi
  veri setinin **on sınıfı** olacak. Sınıf tanımı: `docs/siniflar.md` ve
  makine tarafından okunan `siniflar.json`.
- **Gerekçe:**
  1. **Lisans:** CC0 — kamu malı. Madde 5.5 devrini hiç kirletmiyor;
     mümkün olan en temiz durum.
  2. **Madde 10.5:** Bakanlık verisi değil, kamuya açık akademik veri seti.
     Bulutta eğitim önünde engel yok.
  3. **Rapor uyumu:** Rapor *"beton/tuğla, metal, ahşap, cam ve seramik
     **gibi** ana malzeme grupları"* diyor. "gibi" sözcüğü listeyi
     örnekleyici kılar, kapalı taahhüt değil. On sınıf raporla çelişmez.
  4. Hazır ve elle etiketlenmiş 5.413 nesne — 9 günlük takvimde sıfırdan
     veri toplamaktan çok daha gerçekçi.
- **Kabul edilen boşluklar (gizlenmiyor):**
  - CDW-Seg'de **cam** ve **seramik** sınıfı **yoktur**. Raporda örnek
    olarak anılan bu iki grup mevcut veriyle tanınamaz.
  - `concrete` sınıfı betonu kapsar, **tuğlayı ayırmaz**.
  - Görüntüler **şantiye hurda konteynerlerinden** derlenmiştir, afet
    sonrası enkaz sahasından değil — alan uyuşmazlığı var.
  - Etiketler **bölütleme maskesi**dir; kutu (bbox) COCO formatından
    türetilecektir.
  - Bu dört madde `results/bilinen-sinirlar.md`'ye kaydedildi ve ölçülene
    kadar orada sınır olarak kalacak (talimat Bölüm 14).
- **Durum:** Kabul edildi; Burak veri setini inceliyor.

---

## K-007 · `konteyner` sınıfı miktar hesabına girmez

- **Tarih:** 27.08.2026
- **Karar:** `siniflar.json` içinde `malzeme_mi: false` işaretli sınıflar
  (şu an yalnızca `konteyner` / skip bin) miktar hesabına, Malzeme Kaynak
  Haritası'na ve yönlendirme akışına girmez.
- **Gerekçe:** Hurda konteyneri bir atık malzeme değil, atığın içinde
  bulunduğu kaptır. Miktara katılırsa sistem gerçekte var olmayan bir
  malzeme kütlesi üretir — bu, talimat Bölüm 1.1'in ("ölçüm yoksa miktar
  üretilmez") ruhuna aykırıdır.
- **Uygulama yeri:** Veri katmanı (`api/app/services/queries.py`), yalnızca
  arayüzde gizleme değil.
- **Durum:** Uygulandı.

---

## K-008 · PostgreSQL 17 + PostGIS 3.6, port 5433

- **Tarih:** 27.08.2026
- **Karar:** Geliştirme veri tabanı PostgreSQL 17.11 + PostGIS 3.6.4,
  **port 5433** üzerinde çalışır. Veri tabanı adı `rebuild_vision`.
- **Gerekçe:** Geliştirme makinesinde önceden kurulu PostgreSQL 15 vardı ve
  5432'de başka bir projeye hizmet ediyordu. Homebrew'un `postgis` formülü
  uzantıyı yalnızca PostgreSQL 17 ve 18 için derliyor — PostGIS 15 ile
  kullanılamıyordu. Çakışmayı önlemek ve mevcut veri tabanına
  dokunmamak için 17 ayrı portta ayağa kaldırıldı.
- **Not:** Bu yalnızca geliştirme ortamı ayrıntısıdır. Docker'a geçildiğinde
  konteyner içindeki PostGIS imajı standart 5432'yi kullanacak; port farkı
  `.env` ile yönetilir.
- **Durum:** Uygulandı. Kurulum adımları: `docs/kurulum.md`.

---

## K-009 · Docker bu aşamada ertelendi ⚠️ AÇIK RİSK

- **Tarih:** 27.08.2026
- **Karar:** İlk iskelet aşamasında Docker kurulmadı; sistem yerel süreçlerle
  (Node + uvicorn + yerel PostgreSQL) çalıştırılıyor.
- **Gerekçe:** Geliştirme makinesinde Docker kurulu değildi (Docker Desktop,
  OrbStack, Colima, podman — hiçbiri). Takvimde geri kalınmış durumdayken
  kurulum ve imaj indirme süresi P0'ı geciktirecekti.
- **⚠️ Sonuç:** Bugün itibarıyla teslim paketi **şartname Madde 10.3'ü
  karşılamıyor**: *"Teslim edilen proje, jüri veya teknik komite tarafından
  bağımsız bir ortamda kurulabilir ve çalıştırılabilir olmalıdır."*
- **Telafi planı:** Depo Docker'a hazır yapıda kuruldu (her servisin
  bağımlılıkları kendi klasöründe kilitli, `docker/` klasörü açık).
  Dockerfile ve `compose.yaml` eklemek saatlik iştir. **En geç 03.09'daki
  "teslim paketi kontrolü" gününe kadar tamamlanmalı ve temiz bir ortamda
  doğrulanmalıdır.** Takvimdeki tek günlük tampon buraya harcanmamalıdır.
- **Durum:** 🔴 **AÇIK** — kapatılması gereken risk.

---

## K-010 · `LICENSE` dosyası karar bekliyor

- **Tarih:** 27.08.2026
- **Karar:** `LICENSE` dosyasına henüz lisans metni yazılmadı; dosya bir
  karar bekleme notu içeriyor.
- **Gerekçe:** Ultralytics YOLO11 AGPL-3.0 lisanslı ve AGPL §13 ağ üzerinden
  hizmet sunmayı kopyaleft tetikleyicisi sayıyor. Bu, Madde 5.5 ile
  çözülmemiş bir gerilim oluşturuyor. Gerilim çözülmeden MIT yazmak hukuken
  tutarsız olur.
- **Durum:** 🟡 **BEKLEMEDE** — ilk mentör görüşmesinde sorulacak
  (`docs/lisans-analizi.md` Bölüm 7, soru 1-3).

---

## Mentör görüşmeleri

| # | Tarih | Katılımcılar | Sorulan | Karar |
|---|---|---|---|---|
| 1 | — | — | K-010 (AGPL / Madde 5.5), sunum süresi çelişkisi | *henüz yapılmadı* |
| 2 | — | — | — | — |
| 3 | — | — | — | — |
| 4 | — | — | — | — |

**1. görüşmede sorulacaklar** (`docs/lisans-analizi.md` Bölüm 7'nin özeti):

1. Madde 5.5'teki "sahiplik devri" AGPL'li bir bileşen içeren ürün için
   nasıl yorumlanmalı?
2. Madde 5.5 üçüncü taraf lisanslarını mı kapsıyor, yalnızca takımın kendi
   kodunu mu?
3. Projenin tamamının AGPL-3.0 ile açılması kabul edilebilir mi?
4. Madde 10.4 lisans beyanı için ayrı bir form var mı?
5. Sunum süresi: Madde 2.6.2 **5 dakika**, Madde 5.4 **7+3 dakika** diyor.
   Hangisi esas? *(Bu netleşene kadar demo 5 dakikaya sığacak biçimde
   hazırlanıyor — genişletmek kolay, kısaltmak sahnede imkânsız.)*
