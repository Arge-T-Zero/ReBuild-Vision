# Değişiklik Günlüğü

Biçim: [Keep a Changelog](https://keepachangelog.com/tr/1.1.0/) · tarihler
GG.AA.YYYY.

## [Yayımlanmamış]

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
