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

- **Kalan iş:** Docker kurulup `docker compose -f docker/compose.yaml up
  --build` çalıştırılacak. **En geç 03.09'daki "teslim paketi kontrolü"
  gününe kadar.** Takvimdeki tek günlük tampon buraya harcanmamalıdır.
- **Durum:** 🟠 **KISMEN AÇIK** — kod hazır, doğrulama bekliyor.

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
  en zayıf komşu renk körlüğü ΔE **8.6**, normal görüş ΔE **19.3** —
  beş kontrol de geçiyor.
- **Not:** `konteyner` malzeme olmadığı için kategorik paletten renk almaz
  (K-007 ile tutarlı), nötr gridir.
- **Durum:** Uygulandı. Ayrıntı: `docs/siniflar.md`.

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
