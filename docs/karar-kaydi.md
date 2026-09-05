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

## K-006 · Eğitim veri seti — CDW-Seg ve on sınıf ⚠️ GEÇERSİZ (02.09.2026, bkz. K-021)

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
- **Güncelleme (02.09.2026, K-021):** Sınıf listesi 10'dan 5'e indi ve
  `konteyner` kalktı; artık `malzeme_mi: false` işaretli **hiçbir sınıf
  yok.** Karar geri alınmadı, **mekanizması korundu** — `malzeme_mi`
  alanı, `malzeme_siniflari()` süzgeci ve veri katmanındaki `where`
  yerinde duruyor. Testler de sınıf adına değil mekanizmaya bakacak
  biçimde yeniden yazıldı (`tests/conftest.py` → `malzeme_olmayan_sinif`
  fixture'ı koşulu üreterek sınar). Gerekçe: kuralı kaldırmak, malzeme
  olmayan bir sınıf eklendiği gün sessiz bir hataya dönüşürdü.

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

## K-009 · Docker bu aşamada ertelendi ✅ KAPANDI (29.08.2026, bkz. K-019)

- **Tarih:** 27.08.2026
- **Karar:** İlk iskelet aşamasında Docker kurulmadı; sistem yerel süreçlerle
  (Node + uvicorn + yerel PostgreSQL) çalıştırılıyor.
- **Gerekçe:** Geliştirme makinesinde Docker kurulu değildi (Docker Desktop,
  OrbStack, Colima, podman — hiçbiri). Takvimde geri kalınmış durumdayken
  kurulum ve imaj indirme süresi P0'ı geciktirecekti.
- **⚠️ Sonuç:** Bugün itibarıyla teslim paketi **şartname Madde 10.3'ü
  karşılamıyor**: *"Teslim edilen proje, jüri veya teknik komite tarafından
  bağımsız bir ortamda kurulabilir ve çalıştırılabilir olmalıdır."*

### Güncelleme — 27.08.2026 akşamı

Docker dosyalarının **tamamı yazıldı**: `api.Dockerfile`,
`model-mock.Dockerfile`, `web.Dockerfile` (çok aşamalı → nginx),
`nginx.conf`, `compose.yaml` ve `.dockerignore`.

Sınananlar: `compose.yaml` YAML geçerliliği, kopyalanan bütün yolların
depoda bulunması, `api` imajının model kütüphanesi içermemesi
(`tests/test_agpl_siniri.py`).

**Sınanamayan — ve asıl önemli olan:** temiz bir ortamda
`docker compose up` ile fiilen çalıştırma. Docker kurulu olmadığı için
bu adım atılamadı.

> **Madde 10.3, dosyalar yazıldığı için değil, çalıştığı doğrulandığı
> için karşılanır.** Kalan iş küçük ama vazgeçilmezdir.

Doğrulama kontrol listesi: `docker/README.md`.

- **Durum:** ✅ **KAPANDI — 29.08.2026.** Colima kuruldu, dört servis
  ayağa kalktı, uçtan uca doğrulandı. Doğrulama sırasında Apple
  Silicon'da sistemin hiç açılmasını engelleyen bir hata bulundu ve
  düzeltildi. Ayrıntı: **K-019**.

---

## K-010 · `LICENSE` dosyası karar bekliyor ✅ KAPANDI (01.09.2026, bkz. K-020)

- **Tarih:** 27.08.2026
- **Karar:** `LICENSE` dosyasına henüz lisans metni yazılmadı; dosya bir
  karar bekleme notu içeriyor.
- **Gerekçe:** Ultralytics YOLO11 AGPL-3.0 lisanslı ve AGPL §13 ağ üzerinden
  hizmet sunmayı kopyaleft tetikleyicisi sayıyor. Bu, Madde 5.5 ile
  çözülmemiş bir gerilim oluşturuyor. Gerilim çözülmeden MIT yazmak hukuken
  tutarsız olur.
- **Durum:** ✅ **KAPANDI.** Şartnamenin güncel metni okunduğunda Madde
  10.4'ün AGPL'i **adıyla anıp beyan şartına bağladığı** görüldü.
  Bekleme gerekçesi ortadan kalktı; karar K-020'de verildi.

---

## K-020 · Proje lisansı: AGPL-3.0

- **Tarih:** 01.09.2026
- **Karar:** Proje **AGPL-3.0** ile lisanslandı. `LICENSE` dosyasına
  FSF'nin resmi AGPL-3.0 metni (661 satır, §13 dahil) **birebir**
  yazıldı; metin değiştirilmedi.
- **Gerekçe — üç şey aynı yöne işaret ediyor:**

  1. **Madde 10.4 AGPL'i yasaklamıyor, beyan şartına bağlıyor:**
     *"GPL, AGPL, ticari kullanımı sınırlı, attribution gerektiren veya
     kapalı lisanslı bileşenlerin kullanımı ayrıca belirtilecektir."*
     Bakanlık kopyaleft bileşen kullanılacağını öngörmüş ve kuralı
     "kullanma" değil "bildir" olarak koymuş.
  2. **Madde 9.2:** *"Açık kaynak içerikler kullanılmışsa, lisanslara
     uygunluk sorumluluğu Katılımcı'ya aittir"* — açık kaynak bekleniyor.
  3. **Madde 10.10:** *"Projenin Bakanlık sistemlerinde kullanılması,
     devri, lisanslanması, bakım-destek süreci ve ticarileştirilmesi
     ayrıca imzalanacak protokol ile düzenlenir."* Madde 5.5'teki devir
     mutlak ve anında değil; ayrıntısı protokole bırakılmış.

- **Neden AGPL-3.0, neden başka bir şey değil:** Ürün `ultralytics`
  içerdiği sürece AGPL-3.0 **tek tutarlı seçenektir.** MIT yazmak,
  AGPL'li bir bileşenle aynı programı oluşturan kodu izin verici
  lisansla sunmak olurdu — AGPL §13'ü karşılamaz ve yanlış bir taahhüt
  üretir. Boş bırakmak ise teslim anında Madde 10.4'ü karşılamaz.
- **Kalan sınır — dürüst beyan:** Madde 5.5'in lafzı hâlâ mutlaktır
  ("kullanım hakları ve sahiplikleri Kuruma bedelsiz olarak
  devredilecektir"). Ultralytics'in telif hakkı Ultralytics'te kalır;
  devredilebilecek olan yalnızca ekibin kendi yazdığı kodun haklarıdır.
  Bu, gizlenen değil beyan edilen bir sınırdır.
- **Geri alınabilirlik:** Karar mentör görüşmesinde teyide açıktır.
  Mentör Madde 5.5'i farklı yorumlarsa iki yol vardır: Ultralytics
  Enterprise lisansı (ücretli) ya da izin verici lisanslı bir modele
  geçiş. İkincisi için mimari **zaten hazırdır** — model ayrı bir
  süreçte çalışır ve `api/` onu yalnızca HTTP ile çağırır, yani model
  değişimi tek bir servisi etkiler.
- **Durum:** ✅ Uygulandı. Ayrıntı: `docs/lisans-analizi.md` Bölüm 3 ve 6.

---

## K-011 · Arayüzdeki "sahte model servisi" işareti kaldırıldı ⚠️ İTİRAZ KAYITLI

- **Tarih:** 27.08.2026
- **Karar:** Ekip kararıyla arayüzden model durumu bandı **kaldırıldı**.
  Sistem sahte servisle çalışırken arayüzde bunu gösteren bir işaret
  bulunmuyor.
- **Gerekçe (ekip):** Sistem herkese açık bir bağlantıdan yayınlanacak;
  bant vitrini bozuyordu. Gerçek model geldiğinde tespitler zaten gerçek
  olacak.
- **⚠️ Kaydedilen itiraz:** Ana talimat **Bölüm 9.5** bu işareti ismen
  istiyor:

  > "Arayüzde sahte servis kullanılıyorsa bunu gösteren bir işaret dursun —
  > demo sırasında yanlışlıkla 'gerçek model çalışıyor' izlenimi
  > verilmesin."

  Herkese açık bir bağlantıda etiketsiz sahte tespitler göstermek, bağlantıyı
  açan herkesin (jüri, mentör, üçüncü kişiler) gerçek bir modelin çalıştığını
  sanmasına yol açar. Bu, projenin dürüstlük iddiasıyla çelişir.

  Ara çözüm önerilmişti (turuncu bant yerine sakin bir "Demo · model
  bağlanmadı" rozeti); kabul edilmedi.

- **Korunanlar:** API tarafında dürüstlük sürüyor — `/sistem/durum`
  yanıtı hâlâ `sahte: true` döner, `model-mock` kendini
  `yolo11-rebuild-SAHTE` olarak tanıtır, örnek çıktı dosyası
  `ornek_cikti_SAHTE.json` adını taşır. Altbilgideki *"Model metrikleri:
  henüz ölçülmedi"* cümlesi de yerinde duruyor (Bölüm 14).
- **Durum:** 🟠 Uygulandı — itiraz kayıtlı. Gerçek model bağlanana kadar
  geçerli bir risktir.

---

## K-012 · Malzeme renkleri ölçülerek seçildi

- **Tarih:** 27.08.2026
- **Karar:** Dokuz malzeme sınıfının renkleri, doğrulanmış kategorik
  paletten ölçülerek atandı. Sıra sabittir ve değiştirilmemelidir.
- **Gerekçe:** İlk palet gözle seçilmişti ve beş kontrolün **dördünden
  kaldı**: parlaklık bandı, kroma tabanı, renk körlüğü ayrımı ve normal
  görüş tabanı. Özellikle `#9AA6B2`/`#E4E4E7`/`#6B7280` üçlüsü gri olarak
  okunuyordu ve iki kahve/turuncu ton normal görüşte dahi ayırt
  edilemiyordu (ΔE 10.6, taban 15).
- **Yöntem:** Bütün ikili mesafeler ölçüldü, ardından her komşu ikilinin
  eşiği geçtiği bir sıralama permütasyon taramasıyla bulundu. Sonuç:
  en zayıf **komşu** renk körlüğü ΔE **8.6**, normal görüş ΔE **19.3** —
  beş kontrol de geçiyor.
- ⚠️ **Ölçüt uyarısı (02.09.2026 eklendi).** Buradaki 8,6 değeri
  *sıralamadaki komşu ikililerin* en kötüsüdür; K-022'deki 3,5 ise aynı
  paletin *bütün ikililerinin* en kötüsüdür. İki sayı çelişmiyor, **farklı
  şeyleri ölçüyor**: sıralama optimize edilince lejantta yan yana gelen
  renkler ayrılır, ama uzaktaki iki renk yine birbirine yakın kalabilir.
  K-022 "aynı ölçüdeki skoru" derken bunu belirtmiyordu; düzeltildi.
- **Not:** Malzeme olmayan sınıflar kategorik paletten renk almaz (K-007
  ile tutarlı), nötr gridir.
- **Durum:** ⚠️ **Yerini K-022'ye bıraktı.** Bu ölçüm 10 renkli palet
  içindir; sınıf listesi 5'e inince palet yeniden seçildi. Kayıt, yöntemin
  (renk körlüğü benzetimi + LAB ΔE) daha önce de uygulandığını gösterdiği
  için duruyor. Ayrıntı: `docs/siniflar.md`.

---

## K-013 · Depo herkese açılıyor

- **Tarih:** 27.08.2026
- **Karar:** GitHub deposu `private` → `public` yapılacak.
- **Gerekçe:** Vercel'in ücretsiz katmanı kurum (organization) hesaplarında
  özel depoya bağlanmıyor.
- **Açılmadan önce yapılan denetim:**
  - Geçmişte `.env`, anahtar dosyası, Bakanlık verisi, maskelenmemiş saha
    fotoğrafı ve gerçek e-posta adresi **bulunmadığı** doğrulandı.
  - Varsayılan JWT anahtarıyla üretime çıkış **engellendi**: `ORTAM=uretim`
    iken uygulama açılmıyor. Depo açık olduğunda o anahtar da açık olacağı
    için, onunla imzalanan jetonlar taklit edilebilirdi.
- **Kalan risk:** Demo hesapları (`demo1234`) herkese açık bir yayında
  herkesin giriş yapmasına ve görüntü yüklemesine izin verir. Yalnızca
  sentetik veri bulunduğu için Madde 10.7 ihlali yok, ancak depolama
  kötüye kullanımı mümkündür.
- **Durum:** Uygulandı (depo ayarı ekip tarafından değiştirilecek).

---

## K-014 · Saha personeli bütün sahaları görür (ara çözüm)

- **Tarih:** 29.08.2026
- **Karar:** `saha` rolü, tanımlı bütün enkaz alanlarını görür. `yikim` ve
  `tesis` rolleri için kısıt korunur.
- **Sorun:** Bölüm 5 tablosu saha personeli için "kendi sahası" diyor.
  Saha ataması akışı henüz yazılmadığı için bu kural "oluşturduğu ya da
  daha önce görüntü yüklediği saha" olarak uygulanıyordu. Saha personeli
  saha oluşturamadığı için sonuç bir tavuk–yumurta kilidi oldu: bir sahaya
  görüntü yükleyebilmek için o sahaya **daha önce** görüntü yüklemiş olmak
  gerekiyordu. Rolün tek işi görüntü yüklemek olduğundan rol tamamen
  işlevsizdi — `saha@demo.local` ile girişte "Size atanmış bir saha
  bulunmuyor" boş durumu çıkıyor ve demonun 3. adımı yapılamıyordu.
- **Gerekçe:** İşlevsiz bir rol, belgelenmiş bir genişletmeden kötüdür.
  Aynı yaklaşım `uzman` rolü için de uygulanmıştı (görünürlük iş
  üzerinden türetiliyor). Sızıntı yüzeyi dar: saha personeli saha
  **listesini** görür; rapor alamaz, doğrulama yapamaz, işlem geçmişini
  göremez.
- **Reddedilen seçenek:** `erisim_durumu` alanını yetki kapısı olarak
  kullanmak. Bu alan sahaya **fiziksel** erişimi anlatır (açık / kısıtlı /
  kapalı — girmek güvenli mi); veri yetkisi değildir. İkisini
  karıştırmak, yapısal olarak güvensiz bir sahanın kayıtlarını da
  gizlerdi.
- **Kalan boşluk:** `yikim` ve `tesis` rolleri atama gelene kadar boş liste
  görür. Bu **doğru** davranıştır — bu roller dış taraflardır. Arayüz
  bunu "sistemde saha yok" diye değil "size saha atanmamış" diye anlatır.
- **Kapatma koşulu:** Saha atama tablosu eklendiğinde
  `services/queries.py` içindeki `Rol.SAHA` dalı silinip yerine atama
  sorgusu gelmelidir.

---

## K-015 · Ölçüm girdisine üst sınır ve birim denetimi

- **Tarih:** 29.08.2026
- **Karar:** Ölçüm değeri için tek tespit başına **100.000** üst sınırı
  kondu ve birim, ölçüm türünden **türetilerek** doğrulanıyor
  (`alan→m2`, `hacim→m3`, `agirlik→ton`).
- **Sorun:** `deger` alanında yalnızca `gt=0` kısıtı vardı. Testte tek bir
  tekstil tespitine **999.999.999 ton** girilebildi ve miktar kartı
  "899999999,1 – 1099999998,9 ton" gösterdi. `birim` serbest metindi:
  `agirlik` türüne `m3` gönderilebiliyordu; kabul edilseydi hacim değeri
  ağırlık sanılıp katsayısız hesaba girerdi.
- **Sınırın dayanağı:** Bir tespit tek fotoğraftaki tek görünür bölgedir.
  Tek karede görülebilecek en büyük yığın kabaca 50 × 50 × 10 m = 25.000 m³;
  beton yoğunluğuyla (~2,4 ton/m³) 60.000 ton eder. 100.000 bunun rahatça
  üstünde ama parmak kaymasıyla girilen 10⁹'u durdurur. Bu bir alan
  iddiası değil, **yazım hatası kalkanıdır**.
- **Neden kırpma değil ret:** Kullanıcının girdiği sayıyı sessizce
  değiştirip kaydetmek, ölçümü uydurmak olurdu. İstek 422 ile reddedilir.
- **Nerede:** `api/app/schemas.py` — `OlcumDogrulamasi`, hem `/olcum` hem
  `/esitleme/olcum` üzerinde.

---

## K-016 · Doğrulama kapısı miktar servisinin içine taşındı

- **Tarih:** 29.08.2026
- **Karar:** `miktar.hesapla()` artık sınıf dizesi değil **`Tespit`
  nesnesi** alır ve doğrulama durumunu kendisi kontrol eder.
- **Sorun:** Bölüm 1.4 "doğrulanmamış kayıtlar miktar hesaplarına girmez;
  bu bir arayüz kuralı değil, veri katmanı kuralıdır" diyor. Toplu
  sorgular (`/harita`, `/rapor`) `hesaba_girebilir()` ile filtreleniyordu
  ama tekil `GET /miktar/{id}` uç noktası doğrulama durumuna **hiç
  bakmıyordu**: `beklemede` durumundaki bir tespit için sayı döndürüyor ve
  `miktar_hesabi` satırını kalıcı olarak **yazıyordu**. Yerel veri
  tabanında böyle iki satır bulundu ve silindi.
- **Gerekçe:** Kural router'da kalsaydı yeni bir çağıran onu atlayabilirdi.
  Servisin içinde atlanamaz.
- **Ek düzeltme:** Uç noktada önbelleğe alınmış `miktar_hesabi` satırına
  bakış, hesaptan **sonraya** alındı. Ters sırada, kural konmadan önce
  yazılmış eski bir satır kuralı delerdi.
- **Testler:** `test_dogrulanmamis_tespit_miktara_girmez`,
  `test_belirsiz_isaretlenen_tespit_de_miktara_girmez`.

---

## K-017 · `/harita` ve `/gecmis` rol kapsamına indirildi

- **Tarih:** 29.08.2026
- **Sorun:** İki uç nokta yalnızca "giriş yapmış olmak" istiyordu.
  Sonuç: hiçbir saha göremeyen `yikim` ve `tesis` rolleri haritada
  "**0 Enkaz alanı**" yazarken yanında sistemin **tamamına** ait
  doğrulanmış malzeme kırılımını okuyordu. `/gecmis` de bu rollere
  sistemin bütün denetim kaydını döndürüyordu. Arayüz sekmeyi gizliyordu
  ama uç nokta doğrudan çağrılabilirdi.
- **Karar:** `/harita` dağılımı `gorulebilir_alanlar()` ile sınırlandı;
  `/gecmis` yeni `GECMIS_GORUR` kümesine bağlandı
  (`yonetici, uzman, belediye, afad` — `web/src/roller.ts` menüleriyle
  birebir aynı).
- **İlke:** Arayüzde gizlemek yetki değildir. Yetki API katmanında
  zorlanır (ana talimat Bölüm 5).

---

## K-018 · Dönüşüm katsayıları kaynaklandı — 9 sınıftan 4'ü açıldı

> ⚠️ **GEÇERSİZ (02.09.2026, bkz. K-021).** Bu kayıt 10 sınıflı listeye
> göre yazıldı ve `tekstil`, `karton`, `dolgu_toprak`, `alcipan`,
> `sert_plastik`, `yumusak_plastik` üzerine kuruludur — bunların hiçbiri
> artık bir sınıf değil. **Bugünkü durum: 5 sınıftan 2'si açık**
> (`ahsap`, `metal`). Kayıt silinmedi çünkü katsayıların NASIL
> kaynaklandığını ve `tekstil`/`karton` değerlerinin nereden geldiğini
> gösteren tek belge budur; sınıflar geri gelirse dayanak hazırdır.

- **Tarih:** 29.08.2026
- **Durum:** `katsayilar.json` sürüm 0.2 · **kısmen** kaynaklandı
- **Sorun:** Dosyadaki dokuz katsayının tamamı `dogrulandi: false` ve
  değerleri `null` idi. Sonuç: **hacim ölçümü hiçbir zaman miktar
  üretmiyordu**; yalnızca doğrudan tartım çalışıyordu. Projenin miktar
  iddiası fiilen tek bir yola bağlıydı.

### Kullanılan kaynak

> U.S. EPA, Office of Resource Conservation and Recovery,
> *"Volume-to-Weight Conversion Factors"*, Nisan 2016 — C&D tablosu.

EPA'nın bu satırlar için gösterdiği birincil kaynak (dipnot 18):
California Integrated Waste Management Board, *"Targeted Statewide Waste
Characterization Study: Detailed Characterization of Construction and
Demolition Waste"*, Haziran 2006.

Belge indirilip metni çıkarıldı; değerler **tablodan okundu**, arama
sonucu özetinden alınmadı. Birim çevrimi: `1 lb = 0,45359237 kg`,
`1 yd³ = 0,764554857984 m³` → çarpan `0,000593276`.

### Açılan sınıflar (4)

| Sınıf | Aralık (ton/m³) | Aralık nereden geliyor |
|---|---|---|
| `ahsap` | 0,1003 – 0,1590 | EPA'nın kendi alt satırları: kereste 169, mühendislik ürünü ahşap 268 lb/yd³ |
| `metal` | 0,0279 – 0,1335 | Hava kanalı 47 … demir/demir dışı hurda 225 lb/yd³ |
| `tekstil` | 0,0742 – 0,1038 | Aralık EPA tablosunda **basılı**: 125–175 lb/yd³ |
| `karton` | 0,0442 – 0,0629 | OCC+mukavva sıkıştırılmamış 74,54; OCC yassı 106 lb/yd³ |

`metal` aralığı 4,7 kat geniştir. Daraltılmadı: kaynakta olmayan bir
kesinlik iddia etmek olurdu. Geniş ama dürüst bir aralık, dar ve
uydurma bir aralıktan iyidir.

### Kapalı kalan sınıflar (5) — gerekçeleriyle

- **`beton`, `dolgu_toprak`, `alcipan`:** EPA **tek nokta değer** veriyor
  (sırasıyla 860 / 929 / 467 lb/yd³), aralık vermiyor. Miktar tek kesin
  değer olarak üretilemeyeceği için (Rapor Bölüm 4) aralık zorunlu; aralık
  **uydurulmadı**. Değerler dosyaya `epa_lb_yd3` alanında kayıtlı, kullanıma
  kapalı. ⚠️ **Beton en kritik sınıftır; ikinci kaynak önceliklidir.**
- **`sert_plastik`, `yumusak_plastik`:** EPA'nın C&D bölümünde plastik
  kalemi **yok**. Tablodaki plastik satırları ambalaj geri dönüşümüne ait
  (şişe, kap, film). Bir PVC borunun yoğunluğu şişe yoğunluğu değildir;
  bu eşleme **yapılmadı**.

### Mentöre sorulacaklar

1. Bu değerler **ABD** inşaat/yıkım atığı karakterizasyonundan geliyor.
   Türkiye'deki yapı malzemesi ve yıkım pratiği farklı olabilir. Kabul
   edilebilir mi?
2. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı'nın yayımlanmış bir
   dönüşüm katsayısı tablosu var mı? Varsa **öncelikle o** kullanılmalı.
3. Beton / dolgu toprak / alçıpan için aralık veren bir kaynak önerisi?

### Yan düzeltme — `miktar_hesabi.katsayi_kaynagi` artık `Text`

Tam atıf `varchar(300)`'e sığmıyordu; kayıt yazılamıyor ve miktar hesabı
HTTP 500 ile düşüyordu. Uzunluk sınırı yüzünden gerekçeyi kısaltmak,
izlenebilirliği veri modeline feda etmek olurdu. Bir katsayının dayanağı
üretilen tonajın **tek gerekçesidir**; kırpılamaz. Göç:
`20260829_1557_miktar_hesabi_katsayi_kaynagi_text.py`.

---

## K-019 · Madde 10.3 doğrulandı — ve arm64 taşınabilirlik hatası bulundu

- **Tarih:** 29.08.2026
- **Ortam:** Colima 0.9 (`--cpu 2 --memory 4 --disk 20`) + Docker Engine
  29.7.2 + Docker Compose 5.5.0, macOS 26.5.1, **Apple Silicon (arm64)**
- **Karar:** Docker çalıştırıcısı olarak **Colima** seçildi. Gerekçe:
  Docker Desktop ~4–5 GB yer kaplıyor, makinede yeterli boş alan yoktu;
  Colima arayüzsüz ve belirgin biçimde hafif.

### 🔴 Bulunan hata — sistem Apple Silicon'da hiç açılmıyordu

`docker compose up` şu hatayla düştü:

```
no matching manifest for linux/arm64/v8 in the manifest list entries
```

Manifest denetlendi:

| İmaj | Yayımlanan mimariler |
|---|---|
| `postgis/postgis:17-3.5` (resmî) | **yalnızca** linux/amd64 |
| `imresamu/postgis:17-3.5` (topluluk) | linux/amd64 + linux/arm64 |

**Resmî PostGIS imajının arm64 sürümü yayımlanmıyor.** Bu, yazılan
dosyalara bakarak fark edilemeyecek bir hataydı; ancak fiilen
çalıştırınca ortaya çıktı. Jüri üyesi M serisi bir Mac kullansaydı
sistem **hiç açılmayacaktı** — yani Madde 10.3 dosyalar doğru olduğu
hâlde karşılanmamış olacaktı.

> Bu, K-009'da yazılan cümlenin kanıtıdır: *"Madde 10.3, dosyalar
> yazıldığı için değil, çalıştığı doğrulandığı için karşılanır."*

### Düzeltme

`compose.yaml` içindeki `veritabani` servisine `platform: linux/amd64`
eklendi. amd64 imajı arm64 makinede emülasyonla çalışır.

**Neden çok mimarili topluluk imajı seçilmedi:** `imresamu/postgis`
emülasyon gerektirmez ve daha hızlıdır, ancak topluluk derlemesidir.
Kamu kurumuna devredilecek bir üründe resmî tedarik zinciri tercih
edildi. Emülasyonun bedeli yalnızca açılış süresidir (~40 sn); resmî
imajdan vazgeçmenin bedeli ise tedarik zinciri denetlenebilirliğidir.
Seçenek `compose.yaml` içinde yorumla kayıtlıdır.

### Doğrulanan adımlar

| Adım | Sonuç |
|---|---|
| Üç imajın derlenmesi (`api`, `web`, `model-mock`) | ✅ |
| Dört servisin ayağa kalkması | ✅ `veritabani` ve `model-mock` **healthy** |
| Alembic göçü | ✅ 12 tablo oluştu |
| PostGIS | ✅ `3.5 USE_GEOS=1 USE_PROJ=1 USE_STATS=1` |
| `scripts/demo_veri.py` konteyner içinde | ✅ hesaplar oluştu |
| Arayüz `http://localhost:8080` | ✅ HTTP 200 |
| nginx `/api` vekili | ✅ HTTP 200 |
| Giriş (`uzman@demo.local`) | ✅ |
| Yetki kuralı: `yikim` → `/gecmis` | ✅ **403** |
| Ölçüm sınırı: 10⁹ ton | ✅ **422** |

Yani düzeltilen kurallar konteyner ortamında da geçerli — yalnızca
geliştirme makinesinde değil.

### Yan bulgu

`nginx:1.27-alpine` çekilirken bir kez ağ hatası (`EOF`) alındı;
tekrar denemede sorunsuz indi. Kalıcı bir sorun değil, ancak jüri
zayıf bağlantıdaysa `docker compose build` bir kez başarısız olabilir —
`docker/README.md`'ye not düşüldü.

### Not

Doğrulama sonrası imajlar ve birimler temizlendi
(`docker compose down -v` + `docker system prune -af --volumes`),
Colima durduruldu. Depoda kalıcı bir iz yok.

---

## Mentör görüşmeleri

| # | Tarih | Katılımcılar | Sorulan | Karar |
|---|---|---|---|---|
| 1 | — | — | K-010 (AGPL / Madde 5.5), sunum süresi çelişkisi | *henüz yapılmadı* |
| 2 | — | — | — | — |
| 3 | — | — | — | — |
| 4 | — | — | — | — |

**1. görüşmede sorulacaklar** (`docs/lisans-analizi.md` Bölüm 7'nin özeti):

0. **Dönüşüm katsayıları** (K-018): ABD (EPA/CIWMB) verisi Türkiye enkazı
   için kabul edilebilir mi? Bakanlığın yayımlanmış bir tablosu var mı?
   Beton için aralık veren kaynak önerisi? *(Beton kapalı olduğu sürece
   en kritik malzemede hacimden tonaj üretilemiyor.)*
1. Madde 5.5'teki "sahiplik devri" AGPL'li bir bileşen içeren ürün için
   nasıl yorumlanmalı?
2. Madde 5.5 üçüncü taraf lisanslarını mı kapsıyor, yalnızca takımın kendi
   kodunu mu?
3. Projenin tamamının AGPL-3.0 ile açılması kabul edilebilir mi?
4. Madde 10.4 lisans beyanı için ayrı bir form var mı?
5. Sunum süresi: Madde 2.6.2 **5 dakika**, Madde 5.4 **7+3 dakika** diyor.
   Hangisi esas? *(Bu netleşene kadar demo 5 dakikaya sığacak biçimde
   hazırlanıyor — genişletmek kolay, kısaltmak sahnede imkânsız.)*

---

## K-021 · Sınıf listesi eğitilen modele çekildi (10 → 5)

- **Tarih:** 02.09.2026
- **Karar:** `siniflar.json` on CDW-Seg sınıfından, eğitilen modelin beş
  sınıfına indirildi: `ahsap`, `beton_tugla`, `cam`, `metal`, `seramik`.
  Sıra `model-service/data.yaml` ile birebir aynıdır.
- **Neden zorunluydu — sessiz bir hata vardı:** Model takımın kendi
  veri setiyle (Roboflow etiketli, 5 sınıf) eğitildi, CDW-Seg ile değil.
  `model-service/app.py` sınıf adını modelden değil `siniflar.json`'dan
  **id üzerinden** okuyor. Oradaki koruma yalnızca BİLİNMEYEN id'yi
  yakalıyordu; model 0–4 döndürdüğü sürece hepsi geçerli id olduğu için
  istisna atılmıyor ve her tespit **sessizce yanlış adla** miktar
  hesabına ve rapora geçiyordu:

  | model ne der | servis ne kaydederdi |
  |---|---|
  | `ahsap` | `beton` |
  | `beton_tugla` | `dolgu_toprak` |
  | `cam` | `ahsap` |
  | `metal` | `sert_plastik` |
  | `seramik` | `yumusak_plastik` |

- **Neden yeniden eğitim değil:** Teslime üç gün var ve elde ölçülmüş,
  çalışan bir model var. CDW-Seg ile yeniden eğitmek hem takvime sığmaz
  hem de elde edilen ölçümü çöpe atardı.
- **Bedeli — gizlenmiyor:**
  - `konteyner` sınıfı kalktı; K-007'nin ayıklama **mekanizması**
    korundu (`malzeme_mi`) ve testle sabitlendi.
  - Katsayı tablosu 4 kaynaklı sınıftan **2'ye** düştü (`ahsap`,
    `metal`); `tekstil` ve `karton` katsayıları artık o sınıf olmadığı
    için kaldırıldı.
  - Renk paleti 5 sınıfa göre yeniden seçildi.
- **Durum:** ✅ Uygulandı. Sıra koruması
  `tests/test_sinif_tanimlari.py` ile zorlanıyor.

---

## K-022 · Sınıf renkleri renk körlüğü ölçümüyle yeniden seçildi

- **Tarih:** 02.09.2026
- **Karar:** Beş sınıfın rengi: `ahsap #d95926`, `beton_tugla #6b7280`,
  `cam #008300`, `metal #3987e5`, `seramik #c98500`.
- **Gerekçe:** Renkler protanopi, dötanopi ve tritanopi benzetimiyle
  LAB uzayında ölçüldü.
- **Ölçüt açıkça:** *bütün ikililerin* en kötüsü — normal görüş ve üç
  renk körlüğü benzetimi birlikte. Seçilen küme **ΔE = 6,8**; önceki 10
  renkli paletin **aynı ölçütteki** skoru **3,5** idi, yani yeni palet
  iki kat daha ayırt edilebilir.
- ⚠️ **K-012'deki 8,6 ile karıştırılmamalı.** O sayı aynı 10 renkli
  paletin *sıralamadaki komşu ikililerinin* en kötüsüdür — farklı bir
  ölçüt, dolayısıyla farklı bir sayı. Sıralamayı optimize etmek lejantta
  yan yana düşen renkleri ayırır ama uzaktaki iki rengi yaklaştırabilir.
  Bu paragrafın ilk sürümü "aynı ölçüdeki skoru" derken ölçütü
  yazmıyordu; iki kayıt 02.09.2026'da yeniden ölçülerek uzlaştırıldı.
- **Yeniden üretilebilir:** ölçüm `siniflar.json` ile git geçmişindeki
  eski palet üzerinde tekrarlandı — bütün-ikili: eski 3,51 · yeni 6,79;
  en iyi komşu sıralama: eski 23,6 · yeni 14,4. (Yeni palet komşu
  ölçütünde daha düşük çünkü beş renkte optimize edilecek daha az
  sıralama var; kritik olan bütün-ikili ölçütüdür, çünkü kullanıcı
  renkleri lejanttaki sırayla değil haritada yan yana görür.)
- **Anlamsal tutarlılık da korundu:** gri beton/tuğla, koyu yeşil cam,
  mavi metal, turuncu ahşap, kehribar seramik.
- **Not:** Renk hiçbir zaman TEK BAŞINA anlam taşımaz — her etikette
  sınıf adı yazılıdır (WCAG 1.4.1). Ölçüm, rengin yardımcı olduğu
  durumu iyileştirmek içindir, ona bağımlılık yaratmak için değil.
- **Durum:** ⛔ **GEÇERSİZ (03.09.2026).** Bu paletin üç rengi K-024 ile
  değişti (`metal` kalktı, `tugla` geldi, `seramik` tabanı yükseltmek için
  açıldı). Ayrıca buradaki **6,79** sayısı `scripts/renk_olc.py` ile
  yeniden üretilemedi — betik aynı paleti **8,95** ölçüyor; kontrast
  tarafı birebir aynı (4,83). Fark benzetim matrisinde ya da ΔE
  formülündedir. Güncel palet ve ölçüm: **K-024**.

---

## K-023 · Nesne düzeyi yetkilendirme tekil uçlara da uygulandı

- **Tarih:** 02.09.2026 (teslim denetimi)
- **Bulunan açık:** Yetki kontrolü **eylem** üzerinden yapılıyordu ("bu
  rol okuyabilir mi?"), **nesne** üzerinden unutulmuştu ("bu rol BU
  KAYDI okuyabilir mi?").

  `gorulebilir_alanlar()` süzgeci **liste** uçlarında uygulanıyordu:
  `yikim` rolü `/enkaz-alani`'nda boş liste, `/harita`'da boş dağılım
  görüyordu (K-017). Ama **tekil kayıt** uçları yalnızca "giriş yapmış
  mı" diye bakıyordu:

  | Uç nokta | Önce | Sonra |
  |---|---|---|
  | `GET /tespit/{id}` | ❌ kapsamsız | ✅ |
  | `GET /miktar/{id}` | ❌ kapsamsız | ✅ |
  | `GET /olcum/tespit/{id}` | ❌ kapsamsız | ✅ |
  | `GET /tehlikeli/tespit/{id}` | ❌ kapsamsız | ✅ |
  | `POST /tespit/{id}/dogrula` | ❌ kapsamsız | ✅ |
  | `POST /olcum` | ❌ kapsamsız | ✅ |

- **Somut sonuç:** dış taraf bir rol (yıkım firması, geri kazanım
  tesisi) id'leri sırayla gezerek göremediği sahaların tespitlerini,
  malzeme sınıflarını ve **hesaplanmış tonajını** okuyabiliyordu. Liste
  ucunda kapatılan kapı tekil uçta açıktı.
- **Çözüm — veri katmanında:** `queries.gorulebilir_tespitler()` eklendi;
  uçlar kaydı `db.get()` ile değil bu sorgudan alıyor. Projenin ilkesi
  gereği süzgeç arayüzde değil sorguda.
- **Ortaya çıkan incelik — bilinçli:** `uzman` rolünün görünürlüğü İŞ
  ÜZERİNDEN türetiliyor (K-014: atama akışı henüz yok). Dolayısıyla bir
  uzman, **başka bir uzmanın** doğruladığı ve kapsamında iş bırakmayan
  bir kaydı artık göremiyor. Bu bir gerileme değil, liste ucundaki
  davranışın tekil uca uygulanmasıdır — `/enkaz-alani` o sahayı zaten
  döndürmüyordu. Kuyruktaki kaydı açmak (demo 5. adım) etkilenmiyor;
  ayrı bir testle sabitlendi.
- **Durum:** ✅ Uygulandı. Üç testle korunuyor
  (`tests/test_yetki_ve_roller.py`): açığın kapandığı, süzgecin fazla
  dar olmadığı ve uzmanın kuyruktaki kaydı açabildiği.

---

## K-024 · Model v2'ye geçirildi — lisans boşluğu kapandı, metal kaybedildi

- **Tarih:** 03.09.2026
- **Karar:** Teslim edilen model `model-v1` (YOLO11m) yerine **`model-v2`**
  (YOLO11s, sha256 `468cf535a4e26977…`, 18 MB). Sınıf listesi değişti:
  `ahsap, beton, cam, seramik, tugla` — `metal` kalktı, `beton_tugla`
  ikiye ayrıldı.

### Asıl gerekçe başarım değil, LİSANSTI

v1, takımın internetten (arama motoru) topladığı görüntülerle eğitilmişti
ve **kaynak/lisans beyanı yoktu**. Bu, teslimin tek 🔴 maddesiydi:
Madde 5.2 "kaynaklarını açıkça belirtmek kaydıyla" diyor, Madde 9.2
üçüncü taraf hak ihlalinin sorumluluğunu katılımcıya yüklüyor ve Madde
5.5 ürünü Kuruma devrettiği için sorumluluk teslimden sonra da sürüyor.

v2 üç **kamuya açık** veri setinin birleşimiyle eğitildi ve üçü de
**CC BY 4.0**: Mendeley CODD/BTC (beton, tuğla, seramik), Roboflow
broken-glass-kaggle (cam), Roboflow wood-0nvcu (yalnızca `wood`).
Beyan ve atıf: `docs/lisans-analizi.md` **2.1.2**.

### Ölçüm — ve iki dürüstlük notu

Gönderilen ağırlık **epoch 142** checkpoint'idir; Ultralytics `best`i
*fitness*'a göre seçer (0,1·mAP50 + 0,9·mAP50-95), son epoch'a ya da en
yüksek mAP50'ye göre değil. Bu, ağırlığı yayımlayan oturum tarafından
yakalandı ve `results.csv` ile çapraz doğrulandı.

| Bölme | precision | recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| val | 0,9087 | 0,8316 | 0,8824 | 0,6497 |

1. **Test kümesi ölçülmedi.** v1'de ölçülmüştü (test mAP50 0,4334); v2
   için `split=test` koşusu yapılmadı. Val'i test diye beyan etmek yanlış
   beyan olurdu, bu yüzden `model_metrik_ozeti()` bölme adını artık
   dosyadan okuyor ve arayüz **"val mAP50 = 0,8824"** diyor. Model adı da
   aynı sebeple sabit değil (v1 YOLO11m, v2 YOLO11s).
2. **Ölçülmüş genelleme farkı.** v2 kendi val kümesinde 0,8824 alıyor ama
   deponun üç **sentetik** demo görüntüsünde yalnızca **4 tespit**
   üretiyor (v1: 14). Sebep dağılım farkıdır: v2 gerçek yıkım atığı
   fotoğraflarıyla eğitildi, demo görüntüleri yapay zekâ üretimi geniş
   moloz sahneleri. Gizlenmiyor — `results/model-metrikleri.md` iki
   sayıyı yan yana koyuyor. Bu, sistemin neden hiçbir çıktıyı
   kendiliğinden onaylamadığının somut kanıtıdır.

### Bedeli: `metal`

`metal`, kaynaklı katsayısı olan **iki** sınıftan biriydi (EPA
0,0279–0,1335 ton/m³). v2'de yok; kaynaklı katsayı **2'den 1'e** düştü —
hacim ölçümünden tonaj üretilebilen tek malzeme `ahsap` kaldı. Ayrıca
teslim edilmiş ön değerlendirme raporu örnekleri arasında metal geçiyor;
sapma `docs/siniflar.md`'de açıkça yazılı ve mentöre sorulacaklar
listesine eklendi.

### Renk paleti — zorunlu göç, fırsata dönüştü

`metal` kalkıp `tugla` gelince iki renk yeniden seçilmeliydi. Ölçüm
sırasında asıl bulgu: v1'in darboğazı `cam ↔ seramik` (protanopi, 8,95)
ve tuğlaya hangi renk verilirse verilsin tavanı o belirliyordu — sekiz
aday da aynı skoru verdi. Seramiği bir tık açmak (`#c98500` → `#d4a017`)
tabanı **8,95 → 15,45**'e çıkardı.

Ölçüm kodu artık depoda: **`scripts/renk_olc.py`** — daha önce yalnızca
sonuç sayıları yazılıydı, ölçüm yeniden üretilemiyordu.

⚠️ Betik mevcut paleti **8,95** ölçüyor, K-022 ise aynı palet için
**6,79** diyor. Kontrast tarafı birebir aynı (4,83); fark benzetim
matrisinde ya da ΔE formülünde. Bu saklanmadı: 8,95 → 15,45
karşılaştırması geçerlidir çünkü iki palet de aynı kodla ölçülmüştür,
ama 15,45 eski kayıttaki 6,79 ile yan yana konulamaz.

### Göçü mümkün kılan koruma

Aynı gün, ağırlığın kendi `names` sözlüğü ile `siniflar.json`'u
karşılaştıran bir başlangıç denetimi eklendi (`model-service/app.py`).
Eski koruma yalnızca BİLİNMEYEN id'yi yakalıyordu; v2 de 0–4 döndürdüğü
için sessizce geçerdi ve her `metal` "Seramik", her `seramik` "Tuğla"
olarak kaydedilirdi. Denetim çalıştırılarak doğrulandı: yeni ağırlık
eski `siniflar.json` ile reddediliyor ve üç kaymayı isim isim bildiriyor.

- **Durum:** ✅ Uygulandı. Dört kural v2 verisiyle uçtan uca doğrulandı.
