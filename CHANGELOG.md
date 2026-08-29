# Değişiklik Günlüğü

Biçim: [Keep a Changelog](https://keepachangelog.com/tr/1.1.0/) · tarihler
GG.AA.YYYY.

## [Yayımlanmamış]

### 29.08.2026 — Dönüşüm katsayıları kaynaklandı (hacim → tonaj açıldı)

**Eklendi**
- `katsayilar.json` **0.1 → 0.2**. Dokuz katsayının tamamı kaynaksızdı;
  bu yüzden **hacim ölçümü hiçbir zaman miktar üretmiyordu** — yalnızca
  doğrudan tartım çalışıyordu.
- Kaynak: **U.S. EPA, "Volume-to-Weight Conversion Factors", Nisan 2016**
  (C&D tablosu; EPA'nın gösterdiği birincil kaynak CIWMB 2006). Belge
  indirilip metni çıkarıldı, değerler **tablodan okundu**.
- **4 sınıf açıldı** — aralıkları kaynağın kendisinden geliyor:
  `ahsap` 0,1003–0,1590 · `metal` 0,0279–0,1335 ·
  `tekstil` 0,0742–0,1038 · `karton` 0,0442–0,0629 ton/m³
- Ölçüldü: 40 m³ ahşap → **4,012 – 6,360 ton**, tam atıfla birlikte

**Bilinçli olarak kapalı bırakıldı**
- `beton`, `dolgu_toprak`, `alcipan`: EPA **tek nokta değer** veriyor,
  aralık vermiyor. Miktar tek kesin değer olamayacağı için aralık zorunlu;
  **uydurulmadı**. ⚠️ Beton en kritik sınıf — ikinci kaynak öncelikli
- `sert_plastik`, `yumusak_plastik`: EPA'nın C&D bölümünde plastik kalemi
  yok. Tablodaki plastik satırları ambalaj geri dönüşümüne ait; bir PVC
  borunun yoğunluğu şişe yoğunluğu değildir, bu eşleme yapılmadı

**Düzeltildi**
- `miktar_hesabi.katsayi_kaynagi` `varchar(300)` → **`Text`**. Tam atıf
  sığmıyordu ve miktar hesabı HTTP 500 ile düşüyordu. Uzunluk sınırı
  yüzünden gerekçeyi kısaltmak izlenebilirliği veri modeline feda etmek
  olurdu

Karar: K-018 · Testler: 127 → **130**

### 29.08.2026 — Arayüz denetimi: güvenlik açığı, kural ihlali ve 15 hata

Arayüz otomatik testten geçirildi (8 hesap, 7 sayfa, 12 senaryo, koyu +
açık tema, 360–1400 px). Bulunanlar aşağıda; her biri düzeltilip
**tarayıcıda ölçülerek** doğrulandı.

**Güvenlik**
- **Haritada saklanmış XSS (kritik).** Leaflet `bindPopup`'a dize
  verilince içeriği HTML olarak ayrıştırıyor; enkaz alanı adı ise
  kullanıcı girdisi. Alan tanımlayabilen biri adın içine betik koyarsa
  haritayı açan herkesin oturum jetonu çalınabilirdi. Açık **yük fiilen
  çalıştırılarak** doğrulandı, sonra balon DOM olarak kuruldu
  (`textContent`); yeniden çalıştırılan kanıt betiğinde yük artık metin
- **`/harita` ve `/gecmis` yetki sızıntısı.** İki uç nokta yalnızca
  "giriş yapmış olmak" istiyordu. Hiçbir saha göremeyen yıkım/tesis
  rolleri haritada "0 enkaz alanı" yazarken sistemin **tamamına** ait
  malzeme kırılımını ve bütün denetim kaydını okuyabiliyordu (K-017)

**İhlal edilemez kural ihlalleri**
- **Bölüm 1.4 — doğrulanmamış kayıt miktar hesabına giriyordu.** Toplu
  sorgular filtreliydi ama tekil `GET /miktar/{id}` doğrulama durumuna
  **hiç bakmıyordu**: `beklemede` bir tespit için sayı döndürüyor ve
  `miktar_hesabi` satırını kalıcı yazıyordu. Kural miktar servisinin
  içine taşındı; artık atlanamaz (K-016)
- **Ölçüm girdisinde üst sınır yoktu.** Tek tespite **999.999.999 ton**
  girilebiliyordu ve miktar kartı bunu gösteriyordu. Üst sınır ve
  türden türetilen birim doğrulaması eklendi (K-015)

**İşlevsel hatalar**
- **Saha personeli hiçbir alan göremiyordu** → görüntü yükleyemiyordu.
  Tavuk–yumurta kilidi: bir sahaya yükleme yapabilmek için o sahaya daha
  önce yükleme yapmış olmak gerekiyordu. Rol tamamen işlevsizdi (K-014)
- **İnceleme kuyruğunda görüntü, kutu ve saha bilgisi yoktu.** Uzman
  kanıta bakmadan karar veriyordu; iki tespit ekranda ayırt edilemiyordu.
  Artık kutuya göre ölçeklenmiş kırpma + üzerine çizilmiş model kutusu
- **"Bu tespitin geçmişi" yarım kalıyordu**: ölçüm ve tehlikeli madde
  kayıtları görünmüyordu, işlem sonrası tazelenmiyordu (2 → 4 kayıt)
- Oturum düştüğünde kullanıcı hâlâ giriş yapmış görünüyordu
- API hata verdiğinde sayfalar sonsuza kadar "Yükleniyor…" kalıyordu
- Mobilde 360 px'te beş sekmeden **biri** görünüyordu, ipucu da yoktu →
  alt gezinme çubuğu
- Tespit kutusu etiketleri üst üste biniyordu ve **"ön tahmin"
  taşımıyordu** (Bölüm 1.4 istisnasız istiyor)
- Malzeme filtresi haritayı etkilemiyordu
- Alan bazlı rapor arayüzden alınamıyordu (API destekliyordu)
- İşlem geçmişi kullanıcı adı yerine kimlik, sınıf adı yerine ham anahtar
  gösteriyordu ("kullanıcı #3", "duzeltildi")
- Pydantic'in İngilizce doğrulama mesajları ekrana çıkıyordu
- Ölçüm alanı Türkçe ondalık ayracını (virgül) reddediyordu
- Koyu temada "Yeni alan tanımla" haritası bembeyaz kalıyordu
- Miktarlar Türkçe sayı biçiminde değildi (11.16 → 11,16)

**Ölçülen sonuç**
- Etiket çakışması 1 → **0**, görselden taşma **0**
- 360 px'te beş sayfanın hiçbirinde yatay taşma **yok**
- JavaScript hatası **yok**
- Testler **118 → 127**, hepsi geçiyor

**Sorun bulunmayan** (doğrulandı): rol bazlı menüler, onay bekleyen hesabın
engellenmesi, alan oluşturma ve sınır çizimi, görüntü yükleme ve otomatik
kuyruğa düşme, uzman doğrulama akışı, ölçüm → aralıklı miktar, rapor
indirme (CSV/GeoJSON/JSON), tema geçişi, klavye erişilebilirliği, Türkçe
karakterler.

### 29.08.2026 — Mobil uygulama, rapor indirme ve çevrimdışı eşitleme

**Eklendi**
- **`mobile/` — Flutter saha uygulaması (P2)**. Çevrimdışı çalışır;
  ölçümler cihazda **şifreli** kuyrukta birikir, bağlantı gelince
  kendiliğinden gönderilir (Rapor Bölüm 12)
- `POST /esitleme/olcum` — çevrimdışı kuyruğun sunucu tarafı. Yinelenen
  yazım `yerel_kimlik` ile engellenir; kısmi başarı normaldir
- **Rapor indirme (P3)**: JSON, GeoJSON ve CSV. Dosyadaki kurallar
  ekrandakiyle aynı — doğrulanmamış kayıt dışa aktarılmaz, hesaplanmamış
  miktar boş kalır
- OG kapağı bestelendi; geçici marka işareti ve favicon

**Ölçüldü**
- Lighthouse: **Erişilebilirlik 100 · En İyi Uygulamalar 100 · SEO 100**,
  Performans 81 (`results/lighthouse.md`)

**Kayda geçen sınırlar**
- Mobilde **fotoğraflar şifreli değil** — güvenli depo büyük ikili
  dosyalar için tasarlanmamış (`docs/veri-politikasi.md`)
- Android APK ve iOS derlemesi araç zinciri kurulumu bekliyor; kaynak kod
  tamam

### 28.08.2026 — Canlı demo ortamı yayında

**Eklendi**
- **https://re-build-vision.vercel.app** — uçtan uca çalışan canlı demo
- `render.yaml` (Render Blueprint), `web/vercel.json` (API yönlendirmesi,
  güvenlik başlıkları), `docker/baslat-api.sh`
- `docs/yayin.md` — kurulum, mimari, sorun giderme

**Düzeltildi**
- Render dağıtımı `status 127` ile başarısız oluyordu: `render.yaml`
  `dockerCommand` alanına yazılan çok parçalı `sh -c "..."` dizesi doğru
  ayrıştırılmıyor, komutun tamamı tek program adı sanılıyordu. Başlatma
  Dockerfile'a alındı
- `${PORT}` exec biçimli `CMD` içinde genişlemiyordu; kabuk biçimine
  geçildi
- Bağlantı dizesinin sonuna karışan satır sonu
  `database "postgres\n" does not exist` hatası veriyordu. Bütün metin
  ayarları artık okunurken kırpılıyor

**Güvenlik**
- Depo herkese açıldı; öncesinde geçmiş tarandı: `.env`, anahtar, Bakanlık
  verisi, gerçek e-posta hiçbir commit'te yok
- Supabase **Data API kapalı** — açık olsaydı `kullanici` (parola özeti),
  `tespit` ve `islem_gecmisi` tabloları herkese açık REST uç noktasından
  erişilebilir olurdu
- `ORTAM=uretim` iken varsayılan JWT anahtarıyla uygulama başlamıyor

**Bilinen sınırlar (ücretsiz katman)**
- 15 dk hareketsizlikten sonra uyku; ilk istek ~50 sn
- Yüklenen görüntüler dağıtımda sıfırlanır
- ⚠️ Model hâlâ sahte; arayüzde bunu gösteren işaret yok (K-011)

### 27.08.2026 — Kalite kapısı, izlenebilirlik arayüzü ve tehlikeli madde akışı

**Eklendi**
- **118 test** (`tests/`): Bölüm 1'deki dört ihlal edilemez kural,
  yedi rolün yetkileri, izlenebilirlik ve `bbox_format` regresyon testleri.
  Test veri tabanı ayrı; şema gerçek Alembic göçüyle kuruluyor
- İşlem geçmişi **arayüzü** — Bölüm 4.2 "arayüzde de görünür olmalı"
  diyordu, uç nokta vardı ama ekran yoktu. Tespit detayında ve ayrı bir
  sayfada, kayıt türüne göre süzülebilir
- Rol onay ekranı (yönetici) — kayıt sırasında rol seçilemediği için
  yetkiyi yönetici bu ekrandan verir
- Tehlikeli madde **yönlendirme** akışı: `POST /tehlikeli`,
  `GET /tehlikeli/tespit/{id}` ve tespit detayında kart. Teşhis değil,
  yönlendirme kaydıdır; kayıt yokken "güvenli" denmez

**Docker paketi**
- `docker/api.Dockerfile` · `model-mock.Dockerfile` · `web.Dockerfile`
  (çok aşamalı → nginx) · `nginx.conf` · `compose.yaml` · `.dockerignore`
- Tek giriş noktası `http://localhost:8080`; şema göçü ve demo verisi
  açılışta otomatik
- `.dockerignore` Bakanlık verisinin imaja sızmasını da engeller (Madde 9.1)
- `tests/test_agpl_siniri.py`: `api/` bağımlılıklarında ve kodunda model
  kütüphanesi bulunmadığı, model adresinin yalnızca `model_client.py`
  içinde kullanıldığı testle korunuyor — yorum satırına güvenilmiyor
- ⚠️ **Henüz temiz bir ortamda çalıştırılmadı.** Madde 10.3 dosyalar
  yazıldığı için değil, çalıştığı doğrulandığı için karşılanır (K-009)

**Düzeltildi**
- Doğrulayıcı uzman hiçbir enkaz alanını göremiyordu; kuyruktan doğrulama
  yapıyor ama tespiti bağlamında göremiyor, ölçüm ve laboratuvar kaydı
  ekleyemiyordu. Görünürlük artık **iş üzerinden** türetiliyor
- İşlem geçmişi listesinde ham ISO tarih damgaları görünüyordu;
  `dogrulayan_id` ve `dogrulama_tarihi` başlık satırıyla tekrar ediyordu

**Belgelendi**
- `docs/kurulum.md`: Vite vekili yapılandırma değişikliğinden sonra bazen
  yeniden yüklenmiyor ve `/api` isteklerine `index.html` dönüyor. Belirti
  girişin sessizce başarısız olması; kontrol **durum koduna değil gövdeye**
  bakarak yapılmalı
- `docs/kullanici-kilavuzu.md`: tehlikeli madde incelemesi bölümü

### 27.08.2026 — P0 tamamlandı

**Eklendi**
- `api/` uç noktaları: `/auth` `/enkaz-alani` `/goruntu` `/tespit`
  `/olcum` `/miktar` `/harita` `/gecmis` `/sistem/*`
- Alembic şeması — sekiz tablo, PostGIS geometrileriyle
- `scripts/demo_veri.py` — sekiz sentetik demo hesabı (Madde 10.7)
- `scripts/gelistirme.sh` — tek komutla yerel çalıştırma
- `scripts/maskele.py` — yüz ve plaka maskeleme (Rapor Bölüm 6)
- `web/` React arayüzü: giriş/kayıt, enkaz alanı tanımlama (harita
  üzerinde konum + sınır çizimi), sonuç ekranı, uzman inceleme kuyruğu,
  Malzeme Kaynak Haritası
- Teslim dokümanları (Madde 10.3): `kurulum.md` `kullanici-kilavuzu.md`
  `mimari.md` `veri-modeli.md` `veri-politikasi.md` `demo-video.md`
- `katsayilar.json` — dönüşüm katsayıları (kaynak bekliyor)

**Düzeltildi**
- Uzman düzeltmesi harita ve miktar hesabına yansımıyordu. Geçerli sınıf
  artık `COALESCE(duzeltilen_sinif, sinif)` — insan kararı model
  tahminini geçersiz kılar
- `islem_gecmisi` oluşturma kayıtlarında `kayit_id` boş kalıyordu;
  dinleyici `before_flush` yerine `after_flush` kullanıyor
- `.gitignore` Bakanlık verisi klasörünü tümüyle dışlıyor ve `UYARI.md`
  depoya giremiyordu; içerik bazlı dışlamaya geçildi
- Alembic, GeoAlchemy2'nin oluşturduğu uzamsal indeksleri ikinci kez
  oluşturmaya çalışıyordu

**Doğrulandı (fiilen denendi)**
- `'guvenli'` tehlikeli durumu SQL seviyesinde reddediliyor
- `bbox_format` boş geçilemiyor
- Tek değerli miktar (`alt = ust`) CHECK kısıtıyla reddediliyor
- Ölçüm yoksa `miktar_hesabi` satırı yazılmıyor, API sayı döndürmüyor
- Kayıtta rol yükseltme denemesi yok sayılıyor
- `'reddet'` doğrulama şeması tarafından reddediliyor
- Parola özeti işlem geçmişine sızmıyor
- Bakanlık verisi ve saha fotoğrafları `git status`'ta görünmüyor

**Bilinen boşluklar**
- 🔴 Docker paketi hâlâ yok — Madde 10.3 karşılanmıyor (K-009)
- 🟡 `katsayilar.json` boş: hacim→ağırlık dönüşümü için doğrulanmış
  kaynak gerekiyor. Dayanaksız katsayıyla miktar hesaplanmaz
- 🟡 Uzmana/yıkım firmasına saha atama akışı yok
- ⏳ Mobil uygulama (P2) başlamadı

### 27.08.2026 — Proje iskeleti

**Eklendi**
- Depo yapısı: `web/` `mobile/` `api/` `model-service/` `model-mock/`
  `docs/` `scripts/` `docker/` `results/`
- `docs/lisans-analizi.md` — bağımlılık envanteri, AGPL-3.0 / Madde 5.5
  gerilim analizi, elenen bileşenler
- `docs/karar-kaydi.md` — K-001…K-010 arası on karar
- `docs/siniflar.md` + `siniflar.json` — on malzeme sınıfı, tek doğruluk
  kaynağı
- `results/bilinen-sinirlar.md` ve `results/model-metrikleri.md`
- `model-mock` — sahte model servisi, gerçek HTTP uç noktası (port 8090)
- `api/` çekirdek katmanı: yapılandırma, roller/yetkiler, JWT + bcrypt
  güvenlik, sekiz tablodan oluşan veri modeli
- `data/bakanlik/UYARI.md` — Madde 9.1 uyarısı

**Kararlar**
- Web arayüzü React 19 + Vite + TypeScript seçildi (K-001)
- `react-leaflet` **reddedildi** — `Hippocratic-2.1` lisansı Madde 5.5
  devrini kirletiyor; çıplak `leaflet` (BSD-2) kullanılacak (K-002)
- `psycopg` yerine `asyncpg` (Apache-2.0) — gereksiz LGPL yüzeyinden
  kaçınıldı (K-003)
- `dogrulama_durumu` rapor gövde metnine göre belirlendi:
  `beklemede | onaylandi | duzeltildi | belirsiz` (K-004)
- Eğitim veri seti CDW-Seg (CC0), on sınıf kabul edildi (K-006)
- `konteyner` sınıfı miktar hesabına girmez (K-007)
- PostgreSQL 17 + PostGIS 3.6, port 5433 (K-008)

**Bilinen boşluklar**
- 🔴 Docker paketi hazır değil — Madde 10.3 henüz karşılanmıyor (K-009)
- 🟡 `LICENSE` kararı mentör görüşmesi bekliyor (K-010)
- 🔴 Eğitim verisinde cam ve seramik sınıfı yok
  (`results/bilinen-sinirlar.md` B.1)
