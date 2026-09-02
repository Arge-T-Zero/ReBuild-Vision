# Değişiklik Günlüğü

Biçim: [Keep a Changelog](https://keepachangelog.com/tr/1.1.0/) · tarihler
GG.AA.YYYY.

## [Yayımlanmamış]

### 02.09.2026 — Sınıf listesi eğitilen modele çekildi (10 → 5)

**Sorun — sessiz yanlış etiketleme**
- Model, planlanan kamuya açık veri setiyle (CDW-Seg, 10 sınıf) değil
  **takımın kendi topladığı 5 sınıflı veri setiyle** eğitildi:
  `ahsap`, `beton_tugla`, `cam`, `metal`, `seramik`.
- `siniflar.json` hâlâ 10 sınıflıydı ve sıra kaymıştı. `model-service`
  sınıf adını modelin kendi `names` sözlüğünden değil `siniflar.json`'dan
  okuduğu için, id 0 modelde `ahsap` iken depoda `beton` demekti. Ağırlık
  yerine konsaydı **her tespit yanlış adla** kaydedilir, oradan miktar
  hesabına ve rapora geçerdi — hiçbir yerde hata görünmeden.
- Uyuşmazlığı `test_data_yaml_sinif_sirasi_siniflar_json_ile_ayni`
  yakaladı ve bir süre bilerek kırmızı bırakıldı.

**Değişti**
- `siniflar.json` v2.0: beş sınıf, `data.yaml` sırasıyla birebir.
- `katsayilar.json` v0.3: kaynaklı katsayı 4'ten **2'ye** düştü
  (`ahsap`, `metal`). `tekstil` ve `karton` katsayıları sınıfları
  kalktığı için tablodan çıktı — kaynakları geçersizleşmedi, `git`
  geçmişinde duruyor.
- Renk paleti 5 sınıf için **yeniden ölçülerek** seçildi (K-022):
  protanopi/dötanopi/tritanopi benzetimi + LAB ΔE. En kötü komşu ayrımı
  **6,8**; önceki 10 renkli paletin aynı ölçüdeki skoru 3,5 idi.
- Etiket metni kontrastı yeni paletle yeniden ölçüldü: en düşük oran
  **4,83** (AA eşiği 4,5). Parlaklık eşiği 0,19 tarama ile doğrulandı —
  geçerli aralık 0,17–0,22, eşik ortada duruyor. Kod değişmedi, ölçüm
  yenilendi.

**Testler — yeşil ama YANLIŞ ŞEYİ sınıyordu**
- Sınıf listesi değişince testlerin yarısı artık var olmayan adlarla
  (`beton`, `sert_plastik`, `konteyner`) kayıt kuruyordu. **Hiçbiri
  patlamadı**, çünkü tanınmayan sınıf da malzeme süzgecinden eleniyor.
  Yani K-007'yi sınadığını sanan testler aslında "bilinmeyen sınıf
  süzülür"ü sınıyordu. Yeşil bir test, sandığın şeyi sınamıyorsa
  korumadan beterdir: koruma yokken var sanılır.
- `tespit_kur` artık sınıf adını `siniflar.json` ile **doğruluyor**;
  tanımsız bir ad açık bir hata mesajıyla patlıyor
  (`sinif_dogrula=False` bilinçli kaçış kapısı).
- K-007 testleri sınıf adına değil **mekanizmaya** bakacak biçimde
  yeniden yazıldı: `malzeme_olmayan_sinif` fixture'ı `malzeme_mi: false`
  bir sınıfı enjekte ederek koşulu üretiyor. `siniflar.json`'da böyle
  bir sınıf kalmasa da kural sınanmaya devam ediyor.
- "Bilinmeyen sınıf hesaba girmez" davranışı **ayrı** bir testle
  yazıldı; iki davranış da gerçek ve ikisi de korunuyor.
- Doğrulandı: sınıf adı elle bozulduğunda (`metal` → `demir`) suite
  8 testte kırmızıya dönüyor; eskiden sessizce yeşil kalırdı.

**Gerçek modelle uçtan uca doğrulama — üç arıza bulundu**

Sınıf göçünden sonra zincir gerçek bir ultralytics ağırlığıyla (5 sınıflı,
`nc: 5`, `data.yaml` sırasında) baştan sona çalıştırıldı: web'den yükleme
→ model servisi → API → doğrulama → **mobil uygulamadan** ölçüm → miktar.
Sonuç: 5 tespitin beşi de doğru sınıfla döndü (kutular sentetik görüntünün
gerçek etiketleriyle IoU 0,61–0,98 örtüştü) ve 40 m³ ahşap ölçümü
**4,012–6,36 ton** aralığına, EPA kaynağı yazılı olarak dönüştü.

Yol boyunca üç şey bozuktu ve düzeltildi:

1. **Arayüz "model henüz ölçülmedi" diyordu — ölçüm depoda dururken.**
   Altbilgideki başarım özeti iki router'da elle yazılmış sabit metindi.
   Model 01.09'da ölçüldü, metin değişmedi: jüri ekranda "ölçülmedi"
   görürken `results/egitim/` dolu duruyordu. Özet artık
   `results/egitim/metrikler.json`'dan **üretiliyor**
   (`config.model_metrik_ozeti`) ve bir testle ölçüme bağlandı. Sabit
   metnin sorunu yanlış olması değil, sessizce yanlışa dönüşebilmesiydi.

2. **Mobil, saha personeline HAM sınıf adını gösteriyordu:**
   `beton_tugla`, `ahsap`. Web aynı kaydı "Beton / tuğla" diye
   gösteriyordu — iki arayüz aynı tespite iki farklı ad veriyordu.
   `Renk.malzemeAdi` eklendi; ekranlar `Renk.sinifAdi()` kullanıyor.
   Çevrimdışı çalışma zorunluluğu yüzünden liste mobilde sabit
   tutulmak zorunda, o yüzden `test/sinif_adlari_test.dart` haritayı
   `siniflar.json` ile karşılaştırıyor: renk, ad ve sınıf kümesi.

3. **Mobil yükleme hatası her durumda "bağlantı" diyordu.** Tek bir
   `catch (_)` vardı: sunucu 403 (yetki yok), 413 (dosya büyük) ya da
   503 (model servisi kapalı) dönse bile kullanıcı "bağlantı geldiğinde
   tekrar deneyin" görüyordu. Enkaz alanında bu, sonuçsuz bir döngü
   demek. Artık `ApiHatasi` ayrı yakalanıyor ve sunucunun gerekçesi
   yazılıyor; "bağlantıyı kontrol edin" yalnızca sunucuya HİÇ
   ulaşılamadığında çıkıyor. Giriş ekranı bu ayrımı zaten yapıyordu.

**Doğrulamanın sınırı — açıkça yazılıyor:** kullanılan ağırlık `best.pt`
DEĞİLDİR. Eğitim ağırlığı henüz depoda/Release'te olmadığı için, sınıf
sırası `data.yaml` ile birebir aynı olan **5 sınıflı bir tesisat
ağırlığı** üretildi (sentetik renkli dikdörtgenlerle eğitildi). Bu,
**boru hattını** kanıtlar: id → `siniflar.json` adı → renk → arayüz →
miktar. Modelin SAHA BAŞARIMINI kanıtlamaz; o sayılar
`results/model-metrikleri.md`'dedir ve gerçek eğitimden gelir.

**Belgeler — kullanılmayan veri setine verilen kredi geri alındı**
- `README.md` eğitim veri seti olarak CDW-Seg'e (CC0) atıf yapıyordu ve
  "model henüz eğitilmemiştir" diyordu. **İkisi de yanlıştı.** Atıf
  kaldırıldı, ölçülen metrikler yazıldı, CDW-Seg künyesi
  "değerlendirildi, KULLANILMADI" notuyla `docs/lisans-analizi.md`
  Bölüm 2.7'de kayıt olarak bırakıldı.
- 🔴 **Açık kalan eksik:** eğitim veri setinin kaynak ve lisans beyanı
  hâlâ yazılı değil. Madde 5.2 "kaynaklarını açıkça belirtmek kaydıyla"
  diyor; Madde 9.2 üçüncü taraf hak ihlalinin tüm hukuki ve mali
  sorumluluğunu katılımcıya yüklüyor; Madde 5.5 ürünü Kuruma
  devrettiği için bu sorumluluk teslimden sonra da sürüyor. Gizlenmiyor:
  `README.md`, `docs/lisans-analizi.md` 2.1.1, `results/model-metrikleri.md`
  ve `results/bilinen-sinirlar.md` dördü de yazıyor.
- `model-mock/ornek_cikti_SAHTE.json` elle düzeltilmedi; sahte servis
  yeniden çalıştırılıp **üretildi** ve üretme komutu README'ye yazıldı.


### 01.09.2026 — OGC API - Features (Madde 10.8)

**Eklendi — `/ogc` altında açık coğrafi servis**
- Madde 10.8 "OGC API benzeri servis yaklaşımı" bekliyordu; depoda
  yoktu ve `docs/mimari.md` bunu açıkça boşluk olarak sayıyordu.
- Sistem GeoJSON dışa aktarımı zaten yapıyordu ama o bir **dosya
  indirmedir**: QGIS'te açmak için indirmek gerekir ve veri o anda
  donar. OGC API **canlı bir servistir** — QGIS, ArcGIS ve kamu CBS
  katmanları doğrudan adresten bağlanır, `bbox` ile ekrandaki alanı
  ister, veri güncellendiğinde tazelenir.
- Uç noktalar: karşılama, `/conformance`, `/collections`,
  `/collections/tespit`, `/items` (bbox + sayfalama), `/items/{id}`.

**Kritik tasarım kararı — yeni sorgu yolu AÇILMADI**
- Kayıtlar `rapor.py` içindeki ortak sorgudan gelir; yani rapor ve
  harita ile birebir aynı kural süzgecinden geçer: yalnızca
  **doğrulanmış** tespitler, `konteyner` hariç, uzman düzeltmesi
  geçerli, rol kapsamı zorunlu.
- Sorguyu yeniden yazmak, bu dört kuralın birinin sessizce atlanması
  demek olurdu — coğrafi bir uç noktada bu, **doğrulanmamış bir ön
  tahminin kamu haritasına düşmesi** anlamına gelir.
- 13 test bunu koruyor; en önemlisi `test_ogc_ve_rapor_ayni_kayitlari_verir`:
  iki uç nokta ayrışırsa biri kuralı atlıyor demektir.

**Dürüstlük — karşılanmayan uygunluk sınıfı beyan edilmedi**
- Yalnızca `core` ve `geojson` beyan edildi. `oas30` **beyan
  EDİLMEDİ**: sistem OpenAPI 3.1 üretir, 3.0 değil. Karşılanmayan bir
  uygunluk sınıfını beyan etmek yanlış beyandır ve ayrı bir test bunu
  denetliyor.
- Kapsam uyarısı `kunye` alanında çıktının içinde taşınıyor: QGIS'ten
  bağlanan biri README okumaz, veriyi olduğu gibi alır.

**Ölçüldü:** doğrulanmamış kayıt ve `konteyner` çıktıya sızmıyor;
`/ogc` ile `/rapor/geojson` aynı kayıtları veriyor; id ile doğrudan
erişim de süzgeçten geçiyor (doğrulanmamış kayıt → 404). Test paketi
138 → **151**.

---

### 01.09.2026 — Mobil parola göster/gizle; beton katsayısı araştırıldı

**Eklendi — mobil giriş ekranında parola göster/gizle**
- Web arayüzünde vardı, mobilde yoktu. Saha koşulunda bu bir
  kullanılabilirlik sorunu: eldivenli parmakla, güneş altında, küçük bir
  klavyede yanlış girilen parolada kullanıcı nerede hata yaptığını
  göremiyor, yalnızca "giriş başarısız" görüyordu.
- `mobile/README.md` "Bilinen eksikler" listesinden çıkarıldı.

**Araştırıldı — beton dönüşüm katsayısı · sonuç: DEĞER YAZILMADI**
- `katsayilar.json`'da 9 malzeme sınıfından 5'i kapalı ve en kritiği
  beton. Kaynak arandı; **uygun kaynak bulunamadı ve hiçbir sayı
  yazılmadı.**
- Bulunan asıl şey, sorunun sanılandan zor olduğu: yayımlanmış "beton"
  dönüşüm değerleri **860 ile 4.200 lb/yd³ arasında, beşe katlanıyor.**
  Sebep ölçüm belirsizliği değil **kategori farkı** — kimi kaynak katı
  betonu (~4.050), kimi kırılmış gevşek molozu (~2.025), kimi karışık
  Y&D atığını (~417) ölçüyor. EPA'nın elimizdeki 860 değeri gevşek moloz
  kategorisinde.
- Enkaz sahasındaki malzeme gevşek moloz kategorisindedir. Bu aralığın
  ortasından bir sayı seçmek kategorileri karıştırmak olurdu ve tonajı
  katlayabilirdi — dayanaksız bir sayının neden yalnızca yanlış değil
  **zararlı** olduğunun somut örneği.
- İkinci aday kaynak (Contra Costa County tablosu, 1.400 lb/yd³)
  **belgeye erişilemediği için doğrulanamadı**; ayrıca betonu asfaltla
  birlikte veriyor.
- Bulgu `katsayilar.json` → `acik_sorular` ve `docs/cevresel-etki.md`
  Bölüm 2'ye işlendi. Gereken şey "bir sayı" değil: **gevşek yıkım
  molozu kategorisinde alt–üst aralığı veren, doğrulanabilir tek bir
  kaynak.**

---

### 01.09.2026 — Şartname denetimi; lisans kararı verildi

Şartnamenin güncel metni **ilk kez birincil kaynak olarak** okundu. Depo
bugüne kadar dokuz maddeye atıf yapıyor ama metnin kendisi hiç
görülmemişti.

**Doğrulandı — mevcut atıfların hepsi doğru**
- 5.5, 5.2, 2.6.2, 5.4, 9.1, 10.3, 10.5, 10.6, 10.7 — dokuzu da metni
  doğru alıntılıyor. Bugüne kadar test edilmemiş bir varsayımdı.

**Karar verildi — proje AGPL-3.0 ile lisanslandı (K-020)**
- `LICENSE` beş gündür "KARARI BEKLEMEDE" notu taşıyordu. Bekleme
  gerekçesi, Madde 5.5'in kopyaleft bileşene kapalı olabileceği
  ihtimaliydi. **Metin bunun tersini söylüyor:**
  - **Madde 10.4** AGPL'i *adıyla anıyor* ve kuralı "kullanma" değil
    **"ayrıca belirtilecektir"** olarak koyuyor.
  - **Madde 9.2** açık kaynak kullanımını beklenen durum sayıyor.
  - **Madde 10.10** devri ve **lisanslamayı** ayrıca imzalanacak bir
    protokole bırakıyor — 5.5'teki devir mutlak ve anında değil.
- `LICENSE`'a FSF'nin resmi AGPL-3.0 metni (661 satır, §13 dahil)
  birebir yazıldı; ezberden yazılmadı, metin değiştirilmedi.
- Ürün `ultralytics` içerdiği sürece AGPL-3.0 **tek tutarlı seçenektir**:
  MIT yazmak §13'ü karşılamaz, boş bırakmak teslimde Madde 10.4'ü
  karşılamaz.
- Karar mentör teyidine açıktır ve geri alınabilir — Seçenek C'ye
  (izin verici model) geçiş için mimari zaten hazır.

**Eklendi — `docs/yapay-zeka-beyani.md` (Madde 10.5)**
- Madde yedi kalem beyan istiyordu; depoda **son üçü hiç yoktu**
  (çıktı doğrulama yöntemi, hata/yanlılık riski, açıklanabilirlik
  yaklaşımı — "açıklanabilir" ve "yanlılık" kelimeleri depoda sıfır
  eşleşme veriyordu). Malzemesi zaten vardı, beyan olarak yazılmamıştı.
- Açıklanabilirlik bölümü, **yapılmayanları da** gerekçesiyle sayıyor:
  ısı haritası ve doğal dil gerekçe üretimi bilinçli olarak yok —
  kalibre edilmemiş bir modelde ikisi de hak edilmemiş bir anlayış
  hissi verir.

**Eklendi — `docs/cevresel-etki.md` (Madde 10.9)**
- Bu madde depoda **hiç kapsanmamıştı**; "çevresel" kelimesi hiçbir
  belgede geçmiyordu. Finalde %30, ön elemede %35 ağırlıklı kritere
  dokunuyor.
- Belge **hiçbir çevresel fayda sayısı iddia etmiyor** — ne ton, ne
  yüzde, ne karbon. Bunun yerine dört göstergenin hesap yöntemini,
  beş varsayımı (ikisi kırmızı) ve eksik girdileri kaynağıyla listeliyor.
- Ölçülen gerçek durum: **9 malzeme sınıfından yalnızca 4'ü** kaynaklı
  katsayıya sahip (ahşap, metal, tekstil, karton). **Beton kapalı** —
  EPA tek nokta değer veriyor, aralık vermiyor; aralık uydurulmadı.
  Yani miktar göstergesi bugün enkazın ana kütlesini kapsamıyor.

**Eklendi — `docs/mimari.md` Bölüm 7 (Madde 10.8)**
- Maddenin yedi kaleminden altısı zaten yazılıydı; eksik olan
  **ölçeklenebilirlik yaklaşımı**ydı ("ölçeklenebilir" kelimesi depoda
  sıfır eşleşme).
- Açık standart uyumu doğrulandı, iddia edilmedi: OpenAPI **3.1.0**
  (`/openapi.json` 200), geometri **EPSG:4326**, GeoJSON koordinat
  sırası ve CSV Excel uyumu testli, oturum tablosu yok (JWT durumsuz).
- **OGC API yok** — Madde 10.8'in beklediği coğrafi standart; açıkça
  boşluk olarak yazıldı.
- Ölçeklendiğinde ilk kırılacak dört yer sayıldı. Yük testi
  yapılmadığı için **hiçbir kapasite sayısı beyan edilmiyor.**
- "Bilinen mimari boşluklar" tablosu güncellendi: Docker, mobil
  uygulama ve model servisi artık var; tablo bunları hâlâ eksik
  gösteriyordu.

**Bulundu — şartnamenin kendi içinde üç tutarsızlık**
- Sunum süresi: Madde 2.6.2 **5 dakika**, Madde 5.4 **7+3 dakika**
  (deponun daha önce bulduğu çelişki güncel sürümde de duruyor).
- Finalist sayısı: Madde 4 "en fazla **15 takım**", Madde 5.3 "ilk
  **10 proje**".
- Takvim sırası: Tablo 1'de final sunumu (09.09), finalistlerin
  açıklanmasından (11.09) **önce** görünüyor.
- Üçü de mentör sorularına eklendi (`docs/lisans-analizi.md` Bölüm 7,
  soru 5-7); katsayı ve emisyon faktörü soruları da eklendi (8-9).

---

### 01.09.2026 — Gerçek model servisi, sürekli tümleştirme

**Eklendi — `model-service/` (Kaggle ağırlıklarının ineceği yer)**
- README ve `docs/mimari.md` bu dizine atıf yapıyor, `test_agpl_siniri.py`
  etrafındaki sınırı beş testle savunuyordu — ama **dizin yoktu.**
  Eğitim bittiğinde `best.pt`'yi servis edecek hiçbir şey yoktu.
- Servis `model-mock/app.py` ile birebir aynı sözleşmeyi konuşur;
  `api/` ikisini ayırt etmez, geçiş tek ortam değişkenidir. Tek fark
  olması gereken farktır: `/health` → `sahte: false`.
- **Ağırlık yoksa sahte veri üretmez.** `/health` `agirlik_yuklendi:
  false` ve nedenini döner, `/predict` **503** verir. Sessizce mock'a
  düşmek ya da boş liste dönmek seçenek değil — ikincisi "görüntüde
  malzeme yok" diye okunur.
- **Sınıf adı modelden değil `siniflar.json`'dan alınır.** Model kendi
  `names` sözlüğünü taşır; eğitimdeki sıra kayarsa arayüz "ahşap" yerine
  "metal" gösterir ve hiçbir hata görünmez — miktar da yanlış malzemenin
  katsayısıyla hesaplanır. Listede olmayan bir id gelirse istek 500 ile
  reddedilir ve mesaj sorunun `data.yaml`'da olduğunu söyler.
- İnceleme eşiği ölçülmüş değer olmadığı için (henüz metrik yok) ortam
  değişkeniyle değiştirilebilir; kod değişikliği gerektirmez.
- Ağırlıklar depoya girmez (`agirliklar/.gitignore`).

**Eklendi — sözleşme testi (8 test)**
- İki servisin aynı alan adlarını döndüğü, sahte bayrağının doğru
  yönde olduğu, ağırlıksız serviste uydurma üretilmediği, AGPL
  beyanının gizlenmediği ve bilinmeyen sınıf id'sinin sessizce
  geçilmediği doğrulanıyor.
- Ultralytics bu kapta kurulup gerçek bir ağırlıkla çalıştırılarak
  uçtan uca denendi: ağırlık yokken 503, ağırlıkla 200 ve çıkarım.

**Eklendi — sürekli tümleştirme**
- Depoda 130 sunucu + 13 mobil testi vardı ve **hiçbiri otomatik
  koşmuyordu.** `.github/workflows/testler.yml` üç işi paralel çalıştırır:
  pytest (PostGIS servisiyle), `npm run build` (tsc dahil),
  `flutter analyze` + `flutter test`.

**Düzeltildi — test bağlantı adresi sabit kodlanmıştı**
- İlk CI koşusunda sunucu işi düştü: `createdb` çıkış kodu 1, ardından
  138 testin tamamı kurulum aşamasında hata verdi.
- Sebep: `conftest.py` bağlantı adresini kimlik bilgisi olmadan
  üretiyordu. Geliştirme makinesinde veri tabanı yerelde ve
  geliştiricinin kendi adıyla açılmış bir rolle çalıştığı için kullanıcı
  adı vermeye gerek yok; CI'da ise veri tabanı **ayrı bir kapsayıcıda**
  ve yalnızca `postgres` rolü var. asyncpg işletim sistemi kullanıcısıyla
  bağlanmaya çalışıyor, sunucu `role does not exist` diyordu. `psql` ve
  `createdb` de Unix soketi arıyordu — runner'da öyle bir sunucu yok.
- `PGHOST`, `PGUSER`, `PGPASSWORD` artık ortamdan okunuyor.
  **Varsayılanlar bugünkü davranışı korur:** `PGUSER` tanımlı değilse
  adres eskisiyle birebir aynı üretilir, geliştirme makinesinde hiçbir
  şey değişmez. İki yapılandırma da yerelde doğrulandı.

---

### 01.09.2026 — Mobil tablet düzeni; Flutter derlemesi doğrulandı

**Eklendi — uygulama artık tablette de düzgün**
- Uygulama yalnızca telefon için yazılmıştı; `yukle.dart` ve
  `olcum.dart` düz `ListView` idi, hiçbir genişlik sınırı yoktu.
  Ölçüldü, 1194×834 tablette: "Alan seçin…" açılır listesi **1160 px**
  genişliğinde, içerik 834 px yüksekliğin yalnızca üst ~280 px'ini
  kaplıyor, alt gezinme iki sekmeyi tüm genişliğe yayıyor.
- Sorun estetik değil: 1160 px'lik bir form alanı kullanılamaz (göz,
  etiketten değere kadar ekranın yarısını kat eder) ve o genişlikte
  metin satırı 200 karakteri aşıyor — rahat okuma 60-75 karakterdir.
- `lib/duzen.dart` eklendi: 600 dp eşiği ve 560 dp içerik genişliği.
  Dar ekranda hiçbir şey değişmiyor, telefon düzeni aynen duruyor.
- 600 dp üstünde alt çubuk yerine `NavigationRail` (Material 3'ün
  tablet kuralı): sekmeler tek kenarda toplanıyor, dikey alan içeriğe
  kalıyor.
- Sahada tablet gerçek bir kullanım — ekip fotoğrafı tablette çekip
  ölçümü orada giriyor.

**Düzeltildi — giriş ekranında logo tüm genişliğe yayılıyordu**
- `CrossAxisAlignment.stretch`, alt ögelerin genişliğini eziyor: kutu
  `width: 44` yazmasına rağmen 420 px'e uzuyor, logo 44×44 kare yerine
  geniş bir şerit olarak çiziliyordu. Hem telefonda hem tablette, ve
  giriş ekranının ilk göze çarpan ögesinde.

**Doğrulandı — mobil derlemesi ilk kez gerçekten çalıştırıldı**
- Önceki tur mobil değişiklikleri derleyiciyle doğrulanamamıştı
  (araç zinciri yoktu). Flutter 3.47.2 kuruldu:
  `flutter analyze` → **No issues found**, `flutter test` → **13/13**.
  Tema refaktörü sırasındaki 35 `const` kaldırma işlemi temiz çıktı.
- Ekran doğrulaması Flutter'ın web hedefiyle 390 / 834 / 1194 px'te
  ekran görüntüsü alınarak yapıldı.

---

### 31.08.2026 — Jüri gözüyle web denetimi; mobil eşitleme hatası ve açık tema

Bu tur iki bölümden oluşuyor: web arayüzünün hakem bakışıyla baştan sona
gözden geçirilmesi ve mobil uygulamanın ilk gerçek denetimi.

---

## Web

**Eklendi — adres çubuğu artık ekranı gösteriyor (en büyük bulgu)**
- Uygulamanın **hiç URL yönlendirmesi yoktu.** Her ekran
  `http://localhost:5173/` adresindeydi. Ölçülen sonuç: enkaz alanı
  detayındayken tarayıcının **Geri** düğmesine basmak kullanıcıyı
  `about:blank` sayfasına atıyor, yani **uygulamadan tamamen çıkarıyordu.**
- Bir ekranın bağlantısı paylaşılamıyor, yer imi konulamıyor, sayfa
  yenilendiğinde bulunulan yer kayboluyordu. Bir kamu sisteminde
  "şu sahaya bak" demenin yolu ekran görüntüsü göndermek olamaz.
- History API ile çözüldü; yönlendirme kütüphanesi **kullanılmadı**
  (lisans disiplini — Madde 5.5). Her ekranın adresi ve `<title>`'ı var:
  `/alanlar`, `/kuyruk`, `/harita`, `/gecmis`, `/roller`, `/yukle`,
  `/alan/:id`.
- Derin bağlantı doğrulandı: oturum açılmamışken `/alan/1` giriş formunu
  gösterip girişten sonra doğru sayfaya iniyor; `saha` rolüyle `/roller`
  adresine gidildiğinde yetkili olunan sayfaya düşüyor.

**Düzeltildi — reddedilen hesap başvurusu geri alınamıyordu**
- Yönetici ekranında **"Başvuruyu reddet" tek tıkla ve geri dönüşsüzdü.**
  `/auth/bekleyenler` yalnızca `beklemede` durumundaki hesapları döner;
  reddedilen kayıt listeden çıkar ve **onu geri getiren hiçbir ekran
  yoktur.** Yanlışlıkla dokunulan bir düğme gerçek bir kamu personelini
  sistemden kalıcı olarak kilitliyordu.
- Onaylama tarafı zaten rol seçimi istediği için kazara tıklamaya
  kapalıydı; asimetri buradaydı. Yıkıcı olan taraf artık ikinci bir adım
  istiyor ve sonucun kalıcı olduğunu yazıyor.

**Düzeltildi — tehlikeli madde kartı sessizce kayboluyordu**
- `catch(() => {})` hatayı yutuyor, kart ekrandan **tamamen
  siliniyordu.** Ağ koptuğunda tespit sayfasında "Tehlikeli madde
  incelemesi" başlığı hiç görünmüyor, kullanıcı bunu "kayıt yok" diye
  okuyordu. Oysa kayıt var olabilirdi.
- Yokluğun güvenlik anlamına gelmediğini yazan bir kart, yükleyemediğinde
  de bunu söylemek zorundadır. Artık hata durumu ve yeniden deneme var.

**Düzeltildi — ölçüm kaydedildiğine dair hiçbir işaret yoktu**
- Kullanıcı ölçümü kaydettiğinde kartın tepesindeki "miktar hesaplanmadı"
  cümlesi harfi harfine aynı kalıyordu. Doğrulanmamış tespitte miktar
  zaten üretilmeyeceği için saha personeli "kaydedilmedi mi?" diye düşünüp
  aynı ölçümü tekrar giriyordu.
- Kural değişmedi; artık kaydın alındığı ve miktarın çıkması için sırada
  **uzman doğrulaması** olduğu yazılı.
- Uçtan uca ölçüldü: iki ölçüm → uzman onayı → miktar **8,75 – 12,4 ton**
  belirsizlik aralığıyla, yöntemi ve katsayı kaynağı yazılı olarak
  hesaplandı.

**Düzeltildi — ham veri ekrana sızıyordu**
- Girilen ölçümler listesi veri tabanı enum'unu doğrudan basıyordu:
  *"12,4 ton · agirlik · Saha kantar ölçümü"*. Kullanıcı formda "Ağırlık
  (ton)" seçip kaydettikten sonra onu küçük harfli, şapkasız görüyordu.

**Eklendi — görüntülerin kimliği ve çekim künyesi**
- Bir sahadaki beş görüntü kartının hepsi yalnızca "Tespitler" diyordu;
  ekran okuyucunun başlık listesi *"Tespitler, Tespitler, Tespitler…"*
  diye okunuyor, hangi fotoğrafta olunduğu anlaşılmıyordu. Her kartın
  artık kendi başlığı var.
- Aynı yerde bir izlenebilirlik eksiği vardı: `cekim_tarihi` ve `cihaz`
  API'den geliyor, tipte duruyor ve **hiçbir ekranda gösterilmiyordu.**
  Görüntünün ne zaman ve neyle çekildiği, kararı sonradan denetleyecek
  kişinin ilk soracağı şeydir.

**Düzeltildi — geri çekilen tespit etiketleri okunmaz hâlde ekranda kalıyordu**
- Enkaz alanı görüntüsünde bir tespit listede vurgulandığında diğer
  kutular `opacity: 0.35` ile geri çekiliyordu. Opaklık düğmenin
  tamamına uygulandığı için etiketlerin **yazısı da** fotoğrafa doğru
  soluyordu. Ölçüldü: `#0e1116` yazı `#3987e5` zeminde `#abacad` /
  `#bad5f6` olarak render ediliyor, kontrast **1,5** (eşik 4,5). Dolgu
  toprak 1,57, ahşap 1,45.
- Geçici bir durum değildi: listede **herhangi bir satırın üzerine
  gelindiği anda** doğru olur — yani uzmanın kuyrukta çalıştığı sürenin
  neredeyse tamamında. Ekranda, okunamayacak kadar soluk ama yer kaplayan
  dokuz etiket duruyordu.
- Yazıyı soldurmak yerine **kaldırıldı**: geri çekilen tespidin kutusu
  (konum + sınıf rengi) yerinde kalır, etiketi çizilmez. Bilgi kaybı yok
  — vurgulu ve seçili etiketler tam okunaklı, imleç çekilince hepsi geri
  geliyor — üstelik fotoğrafın üstü gerçekten sadeleşiyor.

**Düzeltildi — en açık metin jetonu en koyu yüzeyde kalıyordu**
- `--u-yuzey-vurgu` (#dfe3db) açık temanın kontrast hesabına dahil
  değildi; jeton `ikincil` düğmenin üzerine gelme rengi olarak sonradan
  eklenmiş, metin jetonlarıyla hiç ölçülmemişti. Rapor indirme
  panelindeki yardımcı metin orada **4,45** ölçüldü — eşiğin 0,05 altında.
- `--u-metin-4` #5b6772'den #566270'e karartıldı. Jeton artık bütün
  açık-tema yüzeylerinde geçiyor; en düşüğü 4,78. Mobil paleti de
  eşitlendi.

**Düzeltildi — ağ hatası İngilizce görünüyordu**
- Sunucuya ulaşılamadığında tarayıcının ham `Failed to fetch` metni
  ekrana basılıyordu. Yerine ne olduğunu ve ne yapılacağını söyleyen
  Türkçe bir mesaj kondu; sunucunun uyku modundan uyanması bir dakika
  sürebileceği de yazılı.
- Kuyruk, harita, geçmiş, yönetici ve alan listesi ekranlarına
  **"Yeniden dene"** düğmesi ve `role="alert"` eklendi — hata
  durumundan çıkışı olmayan ekran kalmadı.

---

## Mobil (Flutter)

Mobil uygulama bu turda ilk kez uçtan uca denetlendi.

**Düzeltildi — ⚠️ eşitleme kuyruğu kalıcı olarak kilitleniyordu**
- Bu projedeki en ciddi kusurdu. Uygulama alan ölçümlerinin birimini
  sunucuya **`m²`** olarak gönderiyordu; sunucu `m2` bekliyor
  (`TURUN_BIRIMI`). Birim türetmesi `m³ → m3` düzeltmesini yapıyor,
  **`m² → m2` düzeltmesini yapmıyordu.**
- Etkisi tek bir kaydın kaybolmasıyla sınırlı değildi. Şema doğrulaması
  gövdeyi bir bütün olarak denetlediği için **tek bozuk satır bütün
  partiyi 422 ile düşürüyordu.** Ölçüldü: 3 sağlam + 1 bozuk kayıt
  gönderildiğinde `HTTP 422, yazılan: 0`.
- Uygulama bunu ağ hatası sanıp *"kayıtlar cihazda güvende, sonra
  denenecek"* diyordu. Yani kuyruğa bir kez alan ölçümü girdiğinde o
  cihaz **bir daha hiç eşitlenemiyordu** ve kimse nedenini
  öğrenemiyordu.
- Üç uçtan düzeltildi:
  1. İstemci artık doğru birimi gönderiyor. Eşleme ekrandan bağımsız,
     **sınanabilir** bir yere taşındı (`lib/olcum_turu.dart`) ve
     `test/olcum_turu_test.dart` sunucunun sözleşmesini doğruluyor.
  2. Sunucu tarafında birim ve üst sınır kuralı artık **satır
     düzeyinde** uygulanıyor; bozuk satır `durum: "hata"` olarak geri
     bildiriliyor, parti düşmüyor. Ölçüldü: aynı gövde artık
     `HTTP 200, yazılan: 3, hatalı: 2`. Bu, uç noktanın kendi
     dokümantasyonunun ("kısmi başarı normaldir") ilk kez gerçekten
     çalışması demek — çevrimdışı eşitleme tanımı gereği **sürümleri
     farklı** cihazlardan veri alır.
  3. Uygulama artık sunucunun **reddini** ağ kopmasından ayırıyor ve
     reddin gerekçesini gösteriyor.

**Eklendi — ölçüm üst sınırı istemcide de kontrol ediliyor**
- Sunucu 100.000 üstünü zaten reddediyordu, ama kayıt önce çevrimdışı
  kuyruğa giriyor: red saatler sonra, sahadan dönülmüşken geliyordu.
  Yazım hatası artık kuyruğa hiç girmiyor. Web arayüzünde bu kontrol
  zaten vardı.

**Eklendi — açık tema (varsayılan) ve tema seçimi**
- Uygulama `theme: koyuTema()` ile **koyu temaya sabitlenmişti**; ne açık
  palet ne de bir seçenek vardı. Web arayüzü açık temaya çevrildikten
  sonra aynı sistemin iki yüzü birbirini tutmuyordu.
- Açık palet web'deki `:root` ile birebir aynı. Koyu tema kaldırılmadı —
  gece çalışmasında ve pil ömründe gerçek yararı var — ama artık bir
  tercih. Düğme hem giriş ekranında hem üst çubukta; seçim güvenli
  depoda saklanıyor.
- Koyu paletteki `metin4` jetonu web'de AA'nın altında kaldığı için
  `#909cab`'e çıkarılmıştı; mobil de aynı değeri aldı.
- Marka rengi zemin olduğunda üzerine gelen metin rengi jetonlaştırıldı:
  sabit kalsaydı açık temada koyu yeşil düğmenin üstüne kırık beyaz
  gelir ve yazı okunmazdı.

**Eklendi — "SAHTE MODEL SERVİSİ" uyarısı**
- Yükleme yanıtı `sahte_model_servisi` alanını dönüyor, ekran onu
  **hiç okumuyordu.** Sistem sahte model servisiyle çalışırken telefonda
  bunu söyleyen tek bir işaret yoktu: kullanıcı *"sert_plastik %87,3 ·
  ÖN TAHMİN"* görüp gerçek bir modelin çıktısı sanıyordu.
- Ana talimat Bölüm 9.5 açık: sahtelik hiçbir yerde gizlenmez. Web
  arayüzünde rozet vardı, mobilde yoktu. "ÖN TAHMİN" etiketi bunun
  yerini tutmaz — o, gerçek bir modelin çıktısının da ön tahmin
  olduğunu söyler; buradaki ise ortada model bile olmadığıdır.

**Eklendi — reddedilen kayıt kuyrukta işaretleniyor ve silinebiliyor**
- Kuyrukta **bekleyen** kayıt ile sunucunun **reddettiği** kayıt aynı
  görünüyordu: ikisi de aynı saat ikonu, aynı renk. Oysa biri bağlantı
  bekler, diğeri kullanıcının müdahalesini — tekrar denemek sonsuza
  kadar aynı sonucu verir.
- Reddedilen kayıt artık kırmızı ikon ve **gerekçesiyle** görünüyor;
  gerekçe kayıtla birlikte şifreli depoda saklanıyor, yani uygulama
  kapanıp açılsa da kayboluyor değil. Yalnızca reddedilen kayıtta silme
  düğmesi var — henüz gönderilmemiş bir ölçümün yanına silme düğmesi
  koymak kazara veri kaybını davet ederdi.

**Eklendi — mobil README'ye "Bilinen eksikler" bölümü**
- Kayıt ol ekranı, parola göster/gizle, fotoğraf şifrelemesi ve saha
  tanımlama/doğrulama/harita ekranlarının bulunmadığı açıkça yazıldı.

**⚠️ Derleyiciyle doğrulanmadı**
- Bu ortamda Flutter/Dart araç zinciri kurulu değil (SDK indirmesi ağ
  ilkesince engelli). Mobil değişiklikler elle gözden geçirildi ve
  sözdizimi denetimden geçirildi, ancak `flutter analyze` ve
  `flutter test` **çalıştırılamadı**; geliştirme makinesinde
  koşturulmalıdır.

---

## Test altyapısı

**Düzeltildi — testler yalnızca tek bir makinede çalışıyordu**
- `tests/conftest.py` Alembic'i sabit mutlak yoldan çağırıyordu
  (`api/.venv/bin/alembic`). `PG_BIN` zaten ortamdan geçersiz
  kılınabilirken bu satırın sabit kalması bir tutarsızlıktı ve depoyu
  farklı bir makinede (CI, jüri değerlendirmesi, Linux kabı) çalıştıran
  herkesi kilitliyordu. Artık `ALEMBIC` ortam değişkeniyle
  değiştirilebiliyor.

### 30.08.2026 — Geçmiş renklendirildi, saha araması, kanıt büyüteci

**Eklendi — işlem geçmişi tür bazlı renklendirildi**
- Karışık bir akışta "hangi kayıt neydi" ancak satır okunarak
  anlaşılıyordu; elli satırlık bir geçmişte göz hiçbir şey ayırt
  edemiyordu. Yedi kayıt tipinin her birinin kendi rengi ve ikonu var.
- Renk **tek başına** anlam taşımaz (Bölüm 9.3): her satırda türün adı
  yazılı ve ayırt edici bir ikon duruyor. Kayıt tipi renkleri malzeme
  sınıfı ve durum renklerinden bilinçli olarak ayrı — aynı ekranda üç
  renk dili olursa hiçbiri okunmaz.
- Süzgeç düğmeleri aynı renkleri taşıyor; süzgeç artık bir **renk
  anahtarı** işlevi de görüyor.
- Kontrast ölçüldü: açık temada en düşük **4,88**, koyu temada **5,58**.

**Değiştirildi — geçmiş metinleri**
- Her kayıt aynı kalıptan çıkıyordu: "X kaydını Y değiştirdi". Teknik
  olarak doğru ama hiçbir şey anlatmıyordu — bir tespitin doğrulanmasıyla
  bir hesaba rol atanması aynı cümleyle görünüyordu. Fiil artık yapılan
  işi söylüyor: *"… tespiti onayladı"*, *"… saha ölçümü girdi"*,
  *"… bu hesaba rol atadı"*.
- **"Tespiti X oluşturdu" düzeltildi:** tespiti insan oluşturmaz, model
  üretir. Eski cümle tespiti insanın kararıymış gibi gösteriyor ve
  projenin en temel ayrımını (ön tahmin ≠ karar) geçmişte siliyordu.
- Kaydolan kişinin `kullanici_id`'si boştur; "Sistem oluşturdu" yerine
  "Yeni hesap başvurusu alındı" yazıyor.
- Kayıtlar **güne göre gruplanıyor** (Bugün / Dün / tarih); satırlarda
  yalnızca saat kalıyor. Elli satırda tam tarihin tekrarı saatleri
  karşılaştırmayı zorlaştırıyordu.

**Eklendi — enkaz alanı listesinde arama ve süzgeç**
- Üç sahayla gerek yoktu; elli sahayla liste kullanılamaz hâle gelirdi.
- Ada **ve sorumluya** göre arama (Türkçe büyük/küçük ve aksan duyarsız),
  erişim durumu süzgeci, "inceleme bekleyen" süzgeci.
- Sıralama "inceleme bekleyen önce": listeyi açanın ilk sorusu
  "nerede iş var" oluyor.
- Kaç kaydın gizlendiği yazılı — süzgeç açıkken kısa liste görmek
  sahaların silindiği izlenimi veriyordu.
- Süzgeç yalnızca üçten fazla saha varsa çıkıyor.

**Eklendi — kuyrukta kanıt büyüteci**
- Uzman kararını **112 px'lik** bir önizlemeye bakarak veriyordu. Bir
  malzemenin ahşap mı metal mi olduğu o boyutta çoğu zaman ayırt
  edilemez; sistemin bütün iddiası ise insanın modelden iyi karar
  vermesi üzerine kurulu. Kanıta bakılamıyorsa iddia da boşa çıkar.
- Önizlemeye tıklayınca görüntünün tamamı açılıyor, model kutusu üzerinde
  işaretli kalıyor. Esc kapatıyor.

**🔴 Düzeltildi — tespit etiketleri okunmuyordu ve sayfayı taşırıyordu**
- Etiket metni `#0e1116` olarak sabit kodlanmıştı ve **üç sınıf renginde
  AA'nın altında** kalıyordu: `yumusak_plastik` 3,82 · `konteyner` 3,91 ·
  `dolgu_toprak` 4,14. Etiket kutunun ne olduğunu söyleyen tek yazıdır.
- Sınıf renkleri `siniflar.json`'dan gelir ve değiştirilemez; düzeltme
  metin tarafında yapıldı — rengin bağıl parlaklığına göre koyu ya da
  beyaz seçiliyor. On sınıfta en düşük oran artık **4,57**.
- Etiket `left:0`/`right:0` ile kutuya yapışıyordu; sağ kenardaki bir
  kutunun uzun etiketi görüntüyü aşıyor ve **390 px telefonda sayfayı
  461 px'e uzatıp yatay kaydırmaya** düşürüyordu. Etiket artık görüntü
  sınırlarına kırpılıyor.
- Bu sayfa daha önce hiç taranmamıştı; iki hata da bu turda ortaya çıktı.

**Doğrulama**
- axe-core: 320 / 390 / 1280 px × iki tema × iki rol × altı ekran +
  kanıt büyüteci = **84 tarama, 0 ihlal, 0 yatay taşma**

### 30.08.2026 — Giriş ekranı ortalandı, kayıt ekranının metni de ayrıldı

**Değiştirildi — düzen ortalandı ve TEK oldu**
- Önceki düzen ikiye bölünüyordu (solda görsel, sağda form). İki bedeli
  vardı: dar ekranda sol panel tamamen gizlendiği için **mobil ile
  masaüstü başka ürünler gibi duruyordu**, ve metin fotoğrafın üzerinde
  kaldığı için okunurluk perdenin gücüne bağlıydı — perde iki temada
  aynı işi görmüyordu.
- Görsel artık sayfanın tamamını kaplar, kart ortada durur ve **kendi
  zeminine oturur**: kontrast fotoğraftan bağımsız garanti altında,
  düzen her ekran boyutunda aynı.

**Düzeltildi — "Hesap oluştur" geçişi sıçrıyordu**
- Tek bir `src` değiştiriliyordu; yeni dosya inene kadar arka plan
  boşalıyor, geçiş kopuk görünüyordu.
- İki görsel de yüklü duruyor ve **opaklıkla geçiş** yapıyor (420 ms);
  kart içeriği de yerinde beliriyor (260 ms). Hareket azaltma tercihi
  olan kullanıcıda ikisi de kapanır (mevcut global kural).

**Düzeltildi — görsel değişiyordu ama METİN aynı kalıyordu**
- Kayıt ekranına ayrı fotoğraf konmuştu, başlık sabitti: kullanıcı
  başka bir yere geldiğini görselden seziyor ama metinden
  doğrulayamıyordu. Yarım işti.
- Kayıt ekranının artık kendi başlığı var: *"Ayrıştırılan her malzeme,
  doğrulanmış bir kayda dönüşür."* Giriş ekranındaki üç kural bloğu
  kayıt ekranında gösterilmiyor; yerini üç adımlı süreç anlatımı alıyor.
- "Girişe dön" bağlantısı başlığın ÜSTÜNE alındı; altında kalınca ekran
  başlığıyla form başlığı arasına sıkışıp okuma sırasını bozuyordu.

**Düzeltildi**
- Künye hiçbir yer işaretinin içinde değildi (axe: `region`, 16 taramanın
  tamamında); `footer` içine alındı.
- Önyükleme sadeleşti: düzen tekleştiği için ekran boyutuna göre iki ayrı
  dosya önyüklemeye gerek kalmadı.

**Doğrulama**
- axe-core: 320 / 390 / 768 / 1440 px × iki tema × giriş ve kayıt =
  **16 tarama, 0 ihlal, 0 yatay taşma**
- Giriş sonrası ekranlar: telefon + masaüstü × iki tema × üç rol =
  **0 ihlal, 0 taşma, 0 sayfa hatası**

### 30.08.2026 — İlk giriş turu, büyütülmüş gezinme, kayıt ekranına ayrı görsel

**Eklendi — adım adım ilk giriş turu**
- Menüde bir sekmenin ADINI görmek ne yaptığını söylemiyordu: "Kuyruk"
  nedir, oraya niye gidilir, kim gider? Kullanıcı sistemi deneyerek
  öğrenmek zorundaydı — burası bir afet yönetim aracı, deneyerek
  öğrenmenin maliyeti yüksek.
- Tur ilgili menü öğesinin ÜZERİNİ aydınlatır ve yanında tek cümlelik
  açıklamasını gösterir. Liste yerine tur seçildi: liste "şurada şu var"
  der ama o şeyin EKRANDA NEREDE olduğunu öğretmez.
- Hedefler ekran genişliğine göre değişir (masaüstünde üst çubuk, dar
  ekranda alt çubuk); bileşen görünür olanı **ölçerek** bulur.
- Tur yalnızca O ROLÜN menüsünü anlatır ve son adımda sistemin sınırını
  söyler: her çıktı ön tahmindir, nihai kararı sistem vermez. Sahte
  model servisi etkinse rozeti de ayrı bir adımda anlatılır.
- Esc atlar, ok tuşları gezinir, odak karta geçer, `role="dialog"`.
- Bir kez bitirilince ya da atlanınca bir daha gösterilmez; tercih
  kullanıcı kimliğine göre saklanır.

**🔴 Düzeltildi — tur kartını harita işaretçisi deliyordu**
- Leaflet katmanları 400–700, harita altlık uyarısı 1000 z-index'inde.
  Tur 60/61'deydi ve mobilde 4. adımda harita işaretçisi kartın üstüne
  biniyordu. Tur 2000/2001'e alındı; ölçüldü.

**Değiştirildi — gezinme büyütüldü**
- Mobil alt çubuk: simge 16 → **22 px**, düğme yüksekliği ~48 → **60 px**.
  Eldivenli parmakla ve sallanan bir araçta kullanılacak; WCAG 2.5.5'in
  44 px asgarisi burada taban, hedef değil.
- Masaüstü üst çubuk: simge 16 → **18 px**, yazı 14 → **15 px**, aktif
  sekme kalınlaştı. Menü hâlâ 1024–1920 px arasında taşmıyor.

**Değiştirildi — kayıt ekranının arka planı ayrı**
- İki ekran aynı fotoğrafı paylaşınca kullanıcı yer değiştirdiğini
  hissetmiyordu; kayıt bir "kip" gibi duruyordu.
- Kayıt ekranı artık `ornek-enkaz-3` görselini kullanıyor: ayrıştırılmış
  malzeme yığınları (ahşap, beton, tuğla, metal) sistemin ne ürettiğini
  gösteriyor. Görsel depoda zaten vardı, yeni dosya eklenmedi.

**Düzeltildi**
- Tur adım sayacı koyu temada `yuzey-ust` üzerinde tam **4,50** ile
  sınırda kalıp AA'yı geçemiyordu; bir ton açıldı (5,01).

**Doğrulama**
- axe-core: telefon + masaüstü × iki tema × üç rol, **tur açıkken ve
  kapalıyken** = 24 tarama, **0 ihlal, 0 yatay taşma**
- Tur uçtan uca yürütüldü: 7 adım, iki cihazda da sorunsuz; bitirince
  kapanıyor, yenileyince tekrar çıkmıyor

### 30.08.2026 — Mobil giriş ekranı ve ayrı kayıt ekranı

**Doğrulandı — kayıt akışı uçtan uca çalışıyor**
- `POST /auth/kayit` hesabı oluşturuyor, parola **bcrypt** ile
  özetleniyor (`$2b$12$…`), hesap `beklemede` durumunda açılıyor.
- Onaylanmamış hesapla giriş **engelleniyor**: "Hesabınız henüz yönetici
  tarafından onaylanmadı."
- Yönetici "Rol onayları" ekranında hesabı **görüyor** ve rol atıyor.
- Arayüzden de sınandı: form gönderildi, veri tabanında satır oluştu.

**Değiştirildi — mobil giriş ekranının sırası**
- Masaüstünde anlatı solda, form sağda; ikisi aynı anda görünür.
  Telefonda alt alta gelmek zorundalar ve anlatı üstteyken her gün
  giriş yapan saha personeli formu görmek için onu her seferinde
  geçiyordu.
- Sıra artık: **görsel → kimlik → form** → sahte model uyarısı →
  tanıtım metni → künye. Arayan açıklamayı buluyor, aramayan doğrudan
  formla karşılaşıyor.
- Değer önermeleri mobilde yalnızca başlıktı; **açıklamalarıyla
  birlikte** geldi — masaüstüyle içerik eşitliği sağlandı.

**Değiştirildi — kayıt artık ayrı bir ekran**
- Önceden aynı forma bir alan eklenip başlığı değişiyordu; kullanıcı
  nereye geldiğini anlamıyor, kaydın ardından ne olacağını
  öğrenmiyordu.
- Kendi başlığı, "Girişe dön" bağlantısı ve **üç adımlı süreç
  anlatımı** var: başvuru kuyruğa alınır → yönetici rol atar → onay
  sonrası giriş yapılır.
- **Parola tekrarı eklendi.** Tek alanda yazılan bir parolanın yanlış
  yazıldığı ancak ilk giriş denemesinde anlaşılıyordu — ve o an hesap
  çoktan onay kuyruğuna girmiş oluyordu.
- Kurallar yazarken canlı güncelleniyor (asgari 8 karakter, iki parola
  aynı); koşullar sağlanana kadar gönder düğmesi kapalı. Kurallar
  sunucudaki `Field(min_length=8)` ile birebir aynı.
- Kayıt sonucu giriş ekranında karşılıyor: hangi adresle başvurulduğu
  yazılı.

**Doğrulama**
- axe-core: telefon / tablet / masaüstü × iki tema × giriş ve kayıt
  ekranı = **12 kombinasyon, 0 ihlal, 0 yatay taşma**
- Kayıt formu davranışı ölçüldü: parolalar eşleşmezken düğme kapalı,
  eşleşince açılıyor, gönderim veri tabanına yazıyor

### 30.08.2026 — Tema değişince sayfanın altında koyu bant kalıyordu

**🔴 Düzeltildi**
- Koyu temada açılıp açık temaya geçildiğinde sayfanın alt kısmında
  **siyah bir bant** kalıyordu (ters yönde de aynısı, açık bant olarak).
- Sebep: açılış betiği ilk boyamada parlama olmasın diye `html`e SATIR
  İÇİ bir zemin rengi yazıyor, ama bu stil bir kez yazılıp bir daha
  güncellenmiyordu. Satır içi stil CSS'i ezdiği için tema değişse de
  `html` eski renginde kalıyordu.
- Bant `body`nin kapsamadığı alandır: `body` yüksekliği `100%`, yani
  görüntü alanı kadar; giriş ekranı telefonda 954 px olduğu için altta
  **110 px'lik** bir şerit kalıyor ve orada `html`in zemini görünüyor.
- Zemin artık `html { background: var(--u-taban) }` kuralından, yani
  jetondan geliyor; satır içi stil React yüklenince kaldırılıyor.
  Böylece tek doğruluk kaynağı tema jetonu oluyor.
- Ölçüldü: telefon ve masaüstünde, iki yönde de `html` ve `body` zemini
  artık aynı; axe-core 0 ihlal.

### 30.08.2026 — Saha görseli telefonda da görünüyor

**Eklendi**
- Giriş ekranındaki saha görüntüsü `hidden lg:flex` içindeydi: **telefonda
  hiç görünmüyordu.** Oysa sahanın asıl aygıtı telefon ve görsel, ekranın
  ne işe yaradığını metinden önce anlatan öğe.
- Küçük ekranda tam genişlikte bir hero şeridi olarak eklendi; alt kenarı
  sayfa zeminine eriyor. Marka, başlık ve form şeridin ALTINDA, düz
  zeminde kalıyor — fotoğrafın üzerine form girdisi koymak okunurluğu
  iki temada da kumara çevirirdi.

**Düzeltildi**
- `index.html` **her cihaza** 170 KB'lık masaüstü görselini önceden
  yüklettiriyordu; telefonda o dosya hiç gösterilmediği hâlde. Önyükleme
  `media` sorgusuyla ayrıldı ve mobil, zaten depoda duran ama hiç
  kullanılmayan 640 px'lik `giris-hero-kucuk.webp` sürümünü (102 KB)
  çekiyor.

**Doğrulama**
- axe-core: masaüstü / tablet / telefon × iki tema → **0 ihlal**
- 320 / 390 / 768 px'te yatay taşma yok, masaüstü paneli değişmedi

### 30.08.2026 — Arayüz denetimi: varsayılan tema, dürüstlük rozeti ve 5 kırık ekran

Arayüz dört bakış açısıyla yeniden denetlendi (genel kullanıcı, jüri /
şartname tutarlılığı, erişilebilirlik, tasarım sistemi). Uygulama ayağa
kaldırılıp **tarayıcıda ölçülerek** incelendi: 4 rol, 7 sayfa, iki tema,
320–1920 px.

**Değiştirildi — varsayılan tema artık AÇIK**
- Sistem "güneş altında kullanılır" diyor ve açık zeminin doğrudan
  güneşte daha okunur olduğunu kendi kodunda yazıyordu; buna rağmen
  kullanıcıyı koyu ekranla karşılıyordu. Varsayılan açık temaya alındı.
- `index.css` tersine çevrildi: `:root` artık açık tema, koyu tema
  `[data-theme="dark"]` altında. Hiçbir renk yalnızca koşullu bir blokta
  tanımlı değil.
- `index.html` açılış betiği ve `theme-color` buna göre güncellendi;
  tema değişince tarayıcı çubuğu da değişiyor.

**🔴 Düzeltildi — varsayılan tema değişikliği ESKİ ZİYARETÇİLERDE ÇALIŞMIYORDU**
- Eski sürüm `rebuild_vision_tema` anahtarına her açılışta yürürlükteki
  temayı yazıyordu — kullanıcı hiçbir şey seçmemiş olsa bile. Varsayılan
  o dönemde koyu olduğu için, siteyi bir kez açmış **herkesin**
  tarayıcısında `"dark"` yazılı kaldı; bir tercih olarak değil, yan etki
  olarak.
- Yeni kod bu anahtarı okuduğu sürece varsayılanı açık yapmak eski
  ziyaretçilerde hiçbir şey değiştirmiyordu: sistemi daha önce açmış olan
  jüri üyesi de dâhil herkes yine koyu ekranla karşılaşacaktı. Yani
  düzeltme, tam da düzeltmesi gereken kişilerde çalışmıyordu.
- Tercih artık `rebuild_vision_tema_secim` anahtarında ve **yalnızca
  kullanıcı düğmeye bastığında** yazılıyor; içindeki değer her zaman
  gerçek bir tercih. Eski anahtar okunmuyor ve temizleniyor.
- Dört senaryo tarayıcıda ölçüldü: eski ziyaretçi → açık (eski anahtar
  silindi) · yeni ziyaretçi → açık · düğmeyle seçilen koyu → yenilemede
  korunuyor · sayfayı açıp dokunmayan → depoya hiçbir şey yazılmıyor.

**🔴 Düzeltildi — depolama engelliyken uygulama HİÇ AÇILMIYORDU**
- `jetonAl/jetonYaz/jetonSil` `localStorage`'a korumasız dokunuyordu.
  Tarayıcı "tüm site verilerini engelle" ayarındaysa erişimin kendisi
  `SecurityError` atıyor; hata React ağacının kökünde patlıyor ve ekranda
  **bomboş beyaz sayfa** kalıyordu — ne form, ne hata, ne açıklama.
- Ölçüldü: `Storage.prototype` erişimi hata atacak biçimde ayarlandığında
  `#root` tamamen boş kalıyordu. Düzeltmeden sonra giriş yapılabiliyor ve
  tema değiştirilebiliyor; jeton depolama yoksa bellekte tutuluyor.
- `tema.tsx` bu riski görüp try/catch kullanıyordu; jeton tarafına
  uygulanmamıştı.

**🔴 Düzeltildi — README'nin vaat ettiği "SAHTE MODEL SERVİSİ" rozeti yoktu**
- README ve `/sistem/durum` uç noktasının kendi belgesi kalıcı bir rozet
  taahhüt ediyordu. `sahte` alanı API'den geliyor, `types.ts` onu tipliyor,
  `durum.tsx` çekiyordu — **hiçbir bileşen okumuyordu.**
- Yani sistem sahte model servisiyle çalışırken ekranda bunu söyleyen tek
  bir işaret yoktu. Demoyu izleyen bir jüri üyesinin gerçek bir modelin
  çalıştığını sanması, sonradan öğrenmesinden kötüdür (Bölüm 9.5).
- `ModelDurumu.tsx` eklendi: üst çubukta kalıcı rozet, giriş ve yükleme
  ekranlarında açıklamalı uyarı. Model servisine ulaşılamadığı durum da
  aynı yerden söyleniyor — kullanıcı bunu yükleme anında değil önceden
  öğreniyor.

**🔴 Düzeltildi — üst menü 640–1280 px arasında kırpılıyordu**
- Eşik `sm` (640 px) idi. 768 px'te dört sekmelik 610 px'lik içeriğe
  177 px yer kalıyor, sekmeler sessizce kırpılıyor ve kaydırılabildiğine
  dair hiçbir ipucu bulunmuyordu: tablet kullanıcısı menünün çoğunu
  hiç göremiyordu.
- Eşik ölçülerek `lg`ye çekildi; altında alt çubuk devralıyor. Üst menü
  kısa etiket kullanıyor (tam ad `aria-label` ve `title`'da) — kapsayıcı
  1240 px'te sınırlı ve tam adlarla beş sekme 737 px istiyor, eldeki yer
  614 px. Ölçüldü: artık 1024–1920 px arasında hiçbir sekme kırpılmıyor.

**Düzeltildi — açık ve koyu temada 5 WCAG AA kontrast ihlali**
axe-core ile ölçüldü; hepsi arayüzün en çok kullanılan öğeleri:
- birincil düğme (marka üzerinde metin) **4,27** → 6,02
- kuyruk rozeti (uyarı %10 zeminde) **4,09** → 5,40
- erişim rozeti (marka %10 zeminde) **4,07** → 5,21
- yardımcı metin (metin-4 / yüzey-3, açık) **4,11** → 4,68
- rapor biçim açıklaması (metin-4 / yüzey-3, **koyu**) **3,95** → 5,18

Sonuç: 4 rol × 7 sayfa × 2 tema taramasında **sıfır ihlal.**

**Düzeltildi — erişilebilirlik**
- Giriş yapıldıktan sonra **hiçbir sayfada `h1` yoktu** (`Baslik` `h2`
  üretiyordu). Başlığa göre gezinen kullanıcı sayfanın konusunu söyleyen
  düğümü hiç bulamıyordu.
- Başlık sırası atlıyordu (`h1` → `h3`/`h4`); tüm bölüm başlıkları
  hiyerarşiye oturtuldu.
- Harita işaretçilerinin **erişilebilir adı yoktu** (serious): Leaflet
  onları `role="button"` ile çiziyor, ekran okuyucu yalnızca "düğme"
  diyordu. Saha adı `title`/`alt` ile verildi.
- Tespit kutusunun `aria-label`'ı ham sınıf adını ("dolgu_toprak")
  okuyor ve uzman düzeltmesini yansıtmıyordu — kutu görsel olarak
  düzeltilmiş sınıfı gösterirken sesli olarak modelin ilk tahminini
  söylüyordu.
- Giriş ekranının sol paneli hiçbir yer işaretinin içinde değildi.
- "İçeriğe geç" bağlantısı eklendi.

**Düzeltildi — giriş ekranı**
- **Mobilde ekran bomboştu.** Kimlik, üç iddia ve TEKNOFEST künyesi
  `hidden lg:*` ile gizliydi; telefondaki kullanıcı siyah bir boşlukta
  tek bir form görüyordu — üstelik sahanın asıl aygıtı telefon.
  Anlatının sıkışmış hâli küçük ekrana eklendi.
- **Tema düğmesi giriş ekranında yoktu.** Temayı en çok isteyecek kişi
  ekranı henüz okuyamayan kişidir; tercihini yapmak için önce giriş
  yapması gerekiyordu.
- Görselin üzerindeki okunabilirlik perdesi iki temada aynı güçteydi ve
  açık temada fotoğrafı beyaz bir sise çeviriyordu. Perde artık temaya
  bağlı bir jeton.
- Parola göster/gizle eklendi.

**Düzeltildi — kararın ve sahanın görünmezliği**
- **Kuyrukta karar sonrası hiçbir geri bildirim yoktu:** uzman
  "Onayla"ya bastığında satır sessizce yok oluyor, kaydın işlendiğini mi
  yoksa uygulamanın mı düştüğünü ayırt edemiyordu. Bu ürünün ana işi
  insanın kararını kaydetmek; kararın kaydedildiğini söylememek en pahalı
  yerdeki sessizlikti. Karar artık adıyla duyuruluyor (`role="status"`).
- **Enkaz alanı detayında künye yoktu:** erişim durumu, sorumlu, koordinat
  ve sınır listedeki kartta görünüp alanın kendi sayfasında kayboluyordu.
  Sahaya ekip gönderecek yetkilinin ilk soracağı şey ("girilebiliyor mu")
  tam da orada eksikti.
- **`roller.ts` içindeki `gorev` alanı ölü veriydi:** yedi rol için
  yazılmış "ana sayfada gösterilecek tek cümlelik yönlendirme" hiçbir
  bileşen tarafından okunmuyordu. Artık rolün kendi ana sayfasında
  görünüyor.

**Düzeltildi — harita altlığı sessizce boş kalıyordu**
- Karolar OpenStreetMap'ten gelir. Ağ kapalıysa, kurum güvenlik duvarı
  engelliyorsa ya da jüri sistemi çevrimdışı bir makinede çalıştırıyorsa
  Leaflet hiçbir şey söylemeden **boş gri bir kutu** bırakıyordu:
  projenin amiral gemisi olan Malzeme Kaynak Haritası "bozuk" görünüyordu,
  oysa işaretçiler ve saha sınırları çalışıyordu.
- Artık karo hatası sayılıyor ve haritanın üstünde durumu söyleyen bir not
  çıkıyor: altlık eksik, veri duruyor. Bu senaryo ölçülerek doğrulandı
  (inceleme ortamında OSM erişimi kapalıydı).

**Düzeltildi — tema sızıntıları ve küçük tutarsızlıklar**
- `ikincil` düğmenin üzerine gelme rengi `#2a3140` olarak sabit
  kodlanmıştı: açık temada düğme imlecin altında koyu laciverte
  dönüyordu (ölçüldü: `rgb(42,49,64)`). Kart ve düğme gölgeleri de sabit
  siyahtı; hepsi jetona bağlandı.
- Harita işaretçisinin halkası sabit `#0e1116` idi — açık temada neredeyse
  siyah bir çember bırakıyordu.
- Rapor dosya adı hep aynıydı (`rebuild-vision-rapor.csv`); üç sahanın
  raporunu indiren yetkilinin klasöründe hangisinin hangisi olduğu
  kayboluyordu. Ada kapsam ve tarih eklendi.
- Ölçüm formunun örneği "12.4" diyerek kullanıcıyı noktaya yönlendiriyordu;
  kod virgülü zaten kabul ediyordu. Örnek kabul edilen biçimle eşitlendi.

**Doğrulama**
- Backend: **130 test geçti**
- `tsc -b` temiz, üretim derlemesi başarılı
- axe-core: 4 rol × 7 sayfa × 2 tema → **0 ihlal**
- 320 / 360 / 390 / 414 / 768 / 1024 / 1280 / 1440 / 1920 px'te
  **yatay taşma yok**

### 29.08.2026 — Madde 10.3 karşılandı (Docker doğrulandı)

**Doğrulandı**
- `docker compose up` **uçtan uca çalıştırıldı**: Colima + Docker Engine
  29.7.2 + Compose 5.5.0, macOS / Apple Silicon. Dört servis ayağa kalktı,
  Alembic göçü çalıştı (12 tablo), PostGIS 3.5 doğrulandı, demo verisi
  konteyner içinde yüklendi, `http://localhost:8080` üzerinden giriş
  yapıldı.
- Düzeltilen kurallar konteynerde de sınandı: `yikim` → `/gecmis` **403**,
  10⁹ ton ölçüm **422**.
- Şartnamenin karşılanmayan tek maddesi buydu; **kapandı** (K-009 → K-019).

**🔴 Düzeltildi — Apple Silicon'da sistem hiç açılmıyordu**
- `postgis/postgis:17-3.5` resmî imajının **arm64 sürümü yayımlanmıyor**;
  manifest yalnızca `linux/amd64` içeriyor. `docker compose up`
  `no matching manifest for linux/arm64/v8` hatasıyla düşüyordu.
- Jüri üyesi M serisi bir Mac kullansaydı sistem açılmayacaktı — dosyalar
  doğru olduğu hâlde Madde 10.3 karşılanmamış olacaktı.
- `veritabani` servisine `platform: linux/amd64` eklendi; imaj
  emülasyonla çalışıyor, sağlık kontrolünden geçtiği doğrulandı.
- Çok mimarili `imresamu/postgis` alternatifi topluluk derlemesi olduğu
  için seçilmedi; gerekçe `compose.yaml` içinde ve K-019'da kayıtlı.

**Bu, yalnızca çalıştırınca bulunabilecek bir hataydı.** Dosyalara
bakarak fark edilemezdi — K-009'daki "Madde 10.3, dosyalar yazıldığı için
değil, çalıştığı doğrulandığı için karşılanır" cümlesinin kanıtı.

**Güncellendi**
- `README.md`, `docs/kurulum.md`, `docker/README.md`: Docker artık
  önerilen yol; eski "henüz doğrulanmadı" uyarıları kaldırıldı

Karar: K-019

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
