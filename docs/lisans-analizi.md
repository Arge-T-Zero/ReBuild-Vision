# Kütüphane ve Lisans Analizi

**Proje:** ReBuild Vision · **Takım:** Arge-T Zero (Başvuru 5387352)
**Belge tarihi:** 27.08.2026 · **Durum:** Canlı belge — her yeni bağımlılıkta güncellenir
**Son güncelleme:** 02.09.2026 — eğitimin CDW-Seg ile DEĞİL takımın kendi
veri setiyle yapıldığı ortaya çıktı; Bölüm 2.6 ve 2.7 düzeltildi, veri
setinin lisans beyanı eksiği Bölüm 2.1.1'de açıldı

---

## 1. Amaç ve dayanak

Bu belge iki şartname maddesinin gereğidir:

- **Madde 10.4** — teslim paketinde kullanılan kütüphanelerin ve lisanslarının
  listelenmesi; **GPL/AGPL gibi kopyaleft lisansların ayrıca belirtilmesi**
  zorunludur.
- **Madde 5.5** — geliştirilen ürünün kullanım hakları ve sahipliği Kuruma
  **bedelsiz olarak devredilecektir**.

Bu iki madde birlikte okunduğunda bir gerilim doğuyor. Belgenin 4. bölümü bu
gerilimi gizlemeden ortaya koyuyor; 7. bölümü mentöre sorulacak soruları
listeliyor.

**Belgedeki bütün lisans bilgileri paket meta verisinden fiilen okunmuştur
(PyPI JSON API ve `npm view`), ezberden veya tahminle yazılmamıştır.**
Doğrulama tarihi: 27.08.2026.

---

## 2. Bağımlılık envanteri

Kullanım biçimi sütunu lisans yayılımı açısından belirleyicidir:
*kütüphane* = sürecimize bağlanır · *ayrı süreç* = yalnızca ağ üzerinden
konuşulur · *veri* = kod değil içerik.

### 2.1. Model katmanı

| Paket | Sürüm | Lisans | Kullanım biçimi | Kaynak |
|---|---|---|---|---|
| ultralytics (YOLO11) | 8.4.0 | **AGPL-3.0** 🔴 | **ayrı süreç** (`model-service/`) | https://github.com/ultralytics/ultralytics |
| model ağırlıkları (özgün eğitim) | — | **AGPL-3.0** (proje lisansıyla aynı) ⚠️ | model dosyası | proje içi |
| **eğitim veri seti** (takımın kendi topladığı) | — | 🔴 **BEYAN EKSİK** | veri | proje içi — bkz. 2.1.1 |

#### 2.1.1. 🔴 Eğitim veri setinin kaynak ve lisans beyanı EKSİK

**Bu, teslim öncesi kapatılması gereken en acil boşluktur ve kod işi
değildir.**

Model, takımın kendi topladığı ve Roboflow ile etiketlediği 5 sınıflı bir
veri setiyle eğitilmiştir (2.765 görüntü, 9.348 kutu —
`results/egitim/veri_seti_kunyesi.json`). **Görüntülerin nereden
toplandığı ve hangi hakla kullanıldığı hiçbir yerde yazılı değildir.**

Şartname iki yerden bağlıyor:

> **Madde 5.2:** "…**kaynaklarını açıkça belirtmek kaydıyla** açık kaynak
> veri setleri, sentetik veri setleri veya kendi oluşturdukları veri
> setlerini de kullanabileceklerdir."

> **Madde 9.2:** "Katılımcılar, geliştirdikleri projelerin kendi özgün
> çalışmaları olduğunu, **herhangi bir üçüncü kişi veya kuruluşa ait
> hakları ihlal etmediğini** beyan eder. Aksi durumda doğabilecek tüm
> hukuki ve mali sorumluluk ilgili katılımcıya aittir."

Madde 10.4 ayrıca "veri seti" lisansını açıkça beyan edilecekler arasında
sayıyor.

⚠️ **Arama motorundan toplanan görüntüler otomatik olarak kullanılabilir
değildir.** Google Görseller bir arama motorudur; görüntüler asıl
sahiplerine aittir ve çoğu telif korumalıdır. Madde 5.5 ürünü Kuruma
devrettiği için bu sorumluluk teslimden sonra da sürer.

**Kapatmak için gereken** — her görüntü kümesi için:

| Alan | Örnek |
|---|---|
| Kaynak | Hangi site / veri seti / kendi çekimimiz |
| Lisans | CC0 / CC-BY / kendi çekimimiz / izin alındı |
| Tarih | Toplama tarihi |
| Sayı | Kaç görüntü |

Kendi çektiğiniz fotoğraflar en temiz yoldur — hak sizindir ve devri
Madde 5.5'i sorunsuz karşılar. İzin verici lisanslı kamu veri setleri
(CC0/CC-BY) ikinci en temiz yoldur. **Kaynağı belirsiz görüntüler
teslimden önce ya belgelenmeli ya da veri setinden çıkarılıp model
yeniden eğitilmelidir.**

Bu soru mentöre de sorulacaktır (Bölüm 7, soru 10).

---

### 2.2. Veri tabanı

| Paket | Sürüm | Lisans | Kullanım biçimi | Kaynak |
|---|---|---|---|---|
| PostgreSQL | 17.11 | PostgreSQL License (izin verici) | ayrı süreç | https://www.postgresql.org |
| PostGIS | 3.6.4 | **GPL-2.0-or-later** 🔴 | veri tabanı uzantısı (ayrı süreç) | https://postgis.net |
| GEOS | — | LGPL-2.1 | PostGIS bağımlılığı | https://libgeos.org |
| PROJ | — | MIT | PostGIS bağımlılığı | https://proj.org |

### 2.3. Backend (`api/`)

> ⚠️ **Sürüm sütunu 02.09.2026'da `api/requirements.txt` dosyasından
> YENİDEN ÜRETİLDİ.** Önceki sürümde **on bir satırın sürümü yanlıştı**
> (ör. fastapi 0.141 yazıyordu, sabitlenmiş sürüm 0.115.6). Lisanslar
> doğruydu; hatalı olan yalnızca sürümlerdi — ama Madde 10.4 beyanı
> denetlenebilir olmalıdır, hatalı bir sürüm beyanı beyan sayılmaz.

| Paket | Sürüm | Lisans | Kullanım biçimi | Kaynak |
|---|---|---|---|---|
| fastapi | 0.115.6 | MIT | kütüphane | https://github.com/fastapi/fastapi |
| uvicorn[standard] | 0.34.0 | BSD-3-Clause | kütüphane | https://github.com/encode/uvicorn |
| pydantic | 2.10.4 | MIT | kütüphane | https://github.com/pydantic/pydantic |
| pydantic-settings | 2.7.0 | MIT | kütüphane | https://github.com/pydantic/pydantic-settings |
| sqlalchemy[asyncio] | 2.0.36 | MIT | kütüphane | https://github.com/sqlalchemy/sqlalchemy |
| geoalchemy2 | 0.16.0 | MIT | kütüphane | https://github.com/geoalchemy/geoalchemy2 |
| alembic | 1.14.0 | MIT | kütüphane | https://github.com/sqlalchemy/alembic |
| **asyncpg** | 0.30.0 | **Apache-2.0** | kütüphane | https://github.com/MagicStack/asyncpg |
| pyjwt | 2.10.1 | MIT | kütüphane | https://github.com/jpadilla/pyjwt |
| bcrypt | 4.2.1 | Apache-2.0 | kütüphane | https://github.com/pyca/bcrypt |
| python-multipart | 0.0.20 | Apache-2.0 | kütüphane | https://github.com/Kludex/python-multipart |
| pillow | 11.1.0 | MIT-CMU | kütüphane | https://github.com/python-pillow/Pillow |
| httpx | 0.28.1 | BSD-3-Clause | kütüphane | https://github.com/encode/httpx |

**Yalnızca geliştirme/test** (`api/requirements-dev.txt`; teslim edilen
imaja girmez, `api.Dockerfile` yalnızca `requirements.txt` kurar):

| Paket | Sürüm | Lisans | Kaynak |
|---|---|---|---|
| pytest | 8.3.4 | MIT | https://github.com/pytest-dev/pytest |
| pytest-asyncio | 0.25.2 | Apache-2.0 | https://github.com/pytest-dev/pytest-asyncio |

### 2.4. Web arayüzü (`web/`)

| Paket | Sürüm | Lisans | Kullanım biçimi | Kaynak |
|---|---|---|---|---|
| react / react-dom | ^19.2.8 | MIT | kütüphane | https://github.com/facebook/react |
| vite | ^8.2.2 | MIT | derleme aracı | https://github.com/vitejs/vite |
| typescript | ~6.0.2 | Apache-2.0 | derleme aracı | https://github.com/microsoft/TypeScript |
| **leaflet** | ^1.9.4 | **BSD-2-Clause** | kütüphane | https://github.com/Leaflet/Leaflet |
| tailwindcss | ^4.3.3 | MIT | derleme aracı | https://github.com/tailwindlabs/tailwindcss |
| @tailwindcss/vite | ^4.3.3 | MIT | derleme aracı | https://github.com/tailwindlabs/tailwindcss |
| @types/leaflet | ^1.9.22 | MIT (DefinitelyTyped) | tip tanımı (derleme) | https://github.com/DefinitelyTyped/DefinitelyTyped |
| @types/node | ^24.13.3 | MIT (DefinitelyTyped) | tip tanımı (derleme) | https://github.com/DefinitelyTyped/DefinitelyTyped |
| @types/react | ^19.2.18 | MIT (DefinitelyTyped) | tip tanımı (derleme) | https://github.com/DefinitelyTyped/DefinitelyTyped |
| @types/react-dom | ^19.2.4 | MIT (DefinitelyTyped) | tip tanımı (derleme) | https://github.com/DefinitelyTyped/DefinitelyTyped |
| @vitejs/plugin-react | ^6.1.0 | MIT | derleme aracı | https://github.com/vitejs/vite-plugin-react |
| oxlint | ^1.79.0 | MIT | geliştirme aracı (lint) | https://github.com/oxc-project/oxc |

> ⚠️ **`@tanstack/react-query` bu tablodan ÇIKARILDI (02.09.2026).**
> Beyanda vardı ama `web/package.json`'da yok ve `web/src` içinde hiç
> kullanılmıyor — hayalet bir satırdı. Bir lisans beyanında var olmayan
> paket, eksik paket kadar kusurludur: ikisi de beyanın gerçekle
> denetlenmediğini gösterir.
>
> `@types/node`, `@types/react`, `@types/react-dom` ise **eklendi**;
> `@types/leaflet` listedeyken bu üçü atlanmıştı.

### 2.4.1. Yazı tipleri — kendi sunucumuzdan

Üçü de **SIL Open Font License 1.1** ile lisanslıdır; gömme, değiştirme ve
yeniden dağıtım serbesttir. Madde 5.5 devrini kirletmezler.

| Aile | Lisans | Kullanım | Kaynak |
|---|---|---|---|
| Manrope | OFL 1.1 | başlıklar | https://github.com/sharanda/manrope |
| Inter | OFL 1.1 | gövde metni | https://github.com/rsms/inter |
| IBM Plex Mono | OFL 1.1 | sayısal değerler | https://github.com/IBM/plex |

Dosyalar `web/public/yazitipi/` altında **kendi sunucumuzdan** servis edilir,
Google Fonts'tan çekilmez. İki gerekçe:

1. **Gizlilik.** Google Fonts'tan çekmek her ziyaretçinin IP adresini
   üçüncü bir tarafa gönderir. Kamu afet yönetimi aracında bu gereksiz bir
   veri akışıdır ve Madde 10.5'in ruhuyla bağdaşmaz.
2. **Performans.** Stil dosyası sayfa render'ını 2.480 ms bloke ediyordu
   (`results/lighthouse.md`).

Yalnızca `latin` ve `latin-ext` alt kümeleri indirilmiştir; Türkçe
karakterler (ğ ş ı İ ç ö ü) `latin-ext` içindedir. Kiril, Yunan ve
Vietnamca alt kümeleri alınmamıştır.

### 2.4.2. Mobil uygulama (`mobile/`)

Flutter ve Dart **BSD-3-Clause** lisanslıdır.

Lisanslar `pub.dev` sayfasından değil, **paketlerin kendi `LICENSE`
dosyalarından** doğrulanmıştır (29.08.2026). Bu ayrım önemli: pub.dev
üzerinden okunan değerler yanlış çıktı (hepsine MIT diyordu).

| Paket | Sürüm | Lisans | Kullanım |
|---|---|---|---|
| flutter_secure_storage | ^11.0.0 | BSD-3-Clause | Şifreli yerel depolama |
| http | ^1.6.0 | BSD-3-Clause | API çağrıları |
| http_parser | ^4.1.2 | BSD-3-Clause | Yüklenen görüntünün MIME türü |
| image_picker | ^1.2.3 | BSD-3-Clause | Kamera ve galeri |
| geolocator | ^14.0.3 | MIT | Konum |
| connectivity_plus | ^7.3.1 | BSD-3-Clause | Bağlantı durumu |

Hepsi izin vericidir; Madde 5.5 devrini kirletmez.

### 2.4.2. Model servisi (`model-service/`) — AGPL sınırının içi

Bu tablo bilinçli olarak ayrıdır: buradaki paketler `api/` imajına
**girmez** ve girmediği `tests/test_agpl_siniri.py` ile denetlenir.

| Paket | Sürüm | Lisans | Not |
|---|---|---|---|
| fastapi | 0.115.6 | MIT | |
| uvicorn[standard] | 0.34.0 | BSD-3-Clause | |
| python-multipart | 0.0.20 | Apache-2.0 | |
| pillow | 11.1.0 | MIT-CMU | |
| **ultralytics** | **8.4.0** | **AGPL-3.0** 🔴 | Bölüm 3 — yalnızca bu serviste |

`ultralytics` kendi bağımlılıklarını (torch, opencv, numpy…) beraberinde
getirir. Bunlar AGPL sınırının **içinde** kalır ve yine `api/`'ye
girmez; torch **BSD-3-Clause**, opencv **Apache-2.0**, numpy
**BSD-3-Clause** lisanslıdır — hiçbiri ek bir kopyaleft yükümlülüğü
doğurmaz. Kopyaleft tetikleyicisi yalnızca `ultralytics`'in kendisidir.

### 2.4.3. Konteyner temel imajları

Jüri `docker compose up` çalıştırdığında bu imajlar da makinesine iner;
Madde 10.4 "kullanılan tüm kütüphane, çerçeve..." diyor ve bunlar beyan
dışı bırakılamaz. (02.09.2026'ya kadar hiçbiri beyan edilmemişti.)

| İmaj | Nerede | Lisans |
|---|---|---|
| `python:3.11-slim` | `api.Dockerfile`, `model-mock.Dockerfile`, `model-service.Dockerfile` | PSF-2.0 (Python) + Debian temel katmanı |
| `node:22-alpine` | `web.Dockerfile` (yalnızca derleme aşaması) | MIT (Node.js) + Alpine (çoğunlukla MIT/BSD) |
| `nginx:1.27-alpine` | `web.Dockerfile` (son katman) | BSD-2-Clause |
| `postgis/postgis:17-3.5` | `compose.yaml` | PostgreSQL License + **PostGIS GPL-2.0-or-later** 🔴 (Bölüm 4) |

Dördü de resmî ya da proje tarafından yayımlanan imajlardır; hiçbiri
değiştirilmemiştir. `node:22-alpine` çok aşamalı derlemede yalnızca
derleyici olarak kullanılır ve son imajda **bulunmaz**.

### 2.5. Yardımcı betikler (`scripts/`)

| Paket | Sürüm | Lisans | Kullanım biçimi | Kaynak |
|---|---|---|---|---|
| opencv-python-headless | **4.10.0.84** | Apache-2.0 | kütüphane (`maskele.py`) | https://github.com/opencv/opencv-python |

### 2.6. Veri kaynakları (kod değil)

| Kaynak | Lisans / koşul | Not |
|---|---|---|
| **Takımın kendi eğitim veri seti** | 🔴 **BEYAN EKSİK** | Modelin eğitildiği veri setidir. Kaynak ve lisans yazılı değil — Bölüm **2.1.1** |
| CDW-Seg eğitim veri seti | CC0 1.0 (kamu malı) ✅ | **KULLANILMADI.** Değerlendirildi ve elenmedi ama eğitim onunla yapılmadı; künyesi kayıt için Bölüm 2.7'de duruyor |
| OpenStreetMap karo görüntüleri | ODbL 1.0 + OSMF Tile Usage Policy | **Atıf zorunlu.** Karo sunucusuna yük bindirilmeyecek; demo ölçeğinde kullanılıyor. Üretimde kendi karo sunucusu gerekir. |
| Bakanlık tarafından sağlanan veri | Madde 9.1 — kopyalanamaz, paylaşılamaz | Depoya **asla** girmez. Bkz. `docs/veri-politikasi.md` |


### 2.7. CDW-Seg — değerlendirildi, KULLANILMADI

> ⚠️ **02.09.2026 düzeltmesi.** Bu bölüm 27.08.2026'da, model CDW-Seg ile
> eğitilecek varsayımıyla yazıldı. **Eğitim o veri setiyle
> yapılmamıştır.** Model, takımın kendi topladığı 5 sınıflı veri setiyle
> eğitildi (Bölüm 2.1.1). Aşağıdaki künye silinmedi çünkü (a) hangi
> seçeneğin değerlendirildiğinin kaydıdır, (b) kullanılan veri setinin
> lisans beyanı kapanmazsa geri dönülecek en temiz alternatiftir: CC0
> olması Madde 5.5 devri açısından kusursuzdur.
>
> Aşağıdaki "Madde 10.5 açısından" ve "Kapsam sınırlaması" değerlendirmeleri
> de bu veri setine aittir; **bugünkü modele uygulanmazlar.**

#### CDW-Seg künyesi (kayıt amaçlı)

| Alan | Değer |
|---|---|
| Ad | CDW-Seg — *A benchmark dataset for class-wise segmentation of construction and demolition waste in cluttered environments* |
| Yazarlar | Diani Sirimewan, Mehrdad Arashpour |
| Yayın | Scientific Data (Springer Nature), 28.05.2025 |
| Makale DOI | 10.1038/s41597-025-05243-x |
| Veri DOI | 10.6084/m9.figshare.28573229 |
| **Lisans** | **CC0 1.0 Universal — kamu malına adama** ✅ |
| İçerik | 5.413 elle etiketlenmiş nesne, 10 sınıf, anlamsal bölütleme |
| Format | Özgün görüntüler + VOC ve COCO formatında ground truth (~4,5 GB) |

**Lisans değerlendirmesi:** CC0, telif hakkından feragat anlamına gelir.
Kullanım, değiştirme, dağıtma ve ticari kullanım için hiçbir koşul yoktur;
atıf dahi hukuken zorunlu değildir. **Bu, Madde 5.5 devri açısından mümkün
olan en temiz durumdur** — veri setinden kaynaklanan hiçbir hak kısıtı
Kuruma geçmez.

Buna rağmen proje, akademik dürüstlük gereği veri setine `README.md`,
`docs/veri-politikasi.md` ve `results/model-metrikleri.md` içinde **atıf
yapar**.

**Madde 10.5 açısından:** CDW-Seg **Bakanlık verisi değildir**, kamuya açık
bir akademik veri setidir. Bu nedenle bulut ortamında model eğitimi için
kullanılmasında Madde 10.5 engeli yoktur. Bakanlık verisi için yasak
aynen sürer (bkz. `data/bakanlik/UYARI.md`).

**Kapsam sınırlaması (lisans değil, veri sınırı):** Veri setinin görüntüleri
şantiye hurda konteynerlerinden derlenmiştir; afet sonrası enkaz sahasından
değildir. Bu bir alan uyuşmazlığıdır ve `results/bilinen-sinirlar.md`'ye
kaydedilmiştir. Lisans analizi kapsamı dışındadır ancak burada da anılması
gerekir çünkü modelin genelleme iddiasını sınırlar.

---

## 3. 🔴 AGPL-3.0 — Ultralytics YOLO11

### 3.1. Neden özel bir başlık

AGPL-3.0 güçlü kopyaleft bir lisanstır ve GPL'den farkı **§13**'tedir:

> "…if you modify the Program, your modified version must prominently offer
> all users interacting with it remotely through a computer network … an
> opportunity to receive the Corresponding Source of your version…"

Klasik GPL yalnızca **dağıtımda** tetiklenir. AGPL, yazılımı **ağ üzerinden
hizmet olarak sunmayı da** tetikleyici sayar. ReBuild Vision tam olarak bunu
yapıyor: kullanıcı tarayıcıdan görüntü yüklüyor, model sunucuda çalışıyor,
sonuç ağ üzerinden dönüyor. Yazılımı hiç kimseye "dağıtmasak" bile AGPL
yükümlülüğü doğar.

Sonuç: YOLO11 ile aynı programı oluşturan her bileşenin kaynak kodu
AGPL-3.0 ile sunulmak zorundadır.

### 3.2. Madde 5.5 ile gerilim

Madde 5.5 ürünün "kullanım hakları ve sahipliğinin Kuruma bedelsiz olarak
devredilmesini" istiyor. AGPL'li bir eser için bu ifade tam olarak
karşılanamaz:

1. **Sahiplik devredilemez.** Ultralytics'in telif hakkı Ultralytics'te
   kalır. Devredebileceğimiz şey yalnızca *kendi yazdığımız kodun* telif
   hakkıdır.
2. **Devralan taraf da aynı koşullara bağlıdır.** Kurum, AGPL'li bir sistemi
   devraldığında kendisi de AGPL yükümlülüğü altına girer — sistemi kapalı
   kaynak olarak işletemez, üzerine kapalı bir modül ekleyip hizmet veremez.
3. **"Bedelsiz" ile "koşulsuz" aynı şey değildir.** AGPL bedelsizdir ama
   koşulsuz değildir.

Teslim edilmiş ön değerlendirme raporu (Bölüm 5) bu konuyu şöyle ifade
etmişti:

> "Ticarileştirme veya kapalı kaynaklı kullanım durumunda bütün yazılım
> bileşenlerinin lisans koşulları yeniden değerlendirilecektir."

**Bu ifade yetersizdir.** Madde 5.5 ticarileştirmeden bağımsız olarak, teslim
anında işler. Rapor değiştirilemez olduğu için buradaki tespit, raporun
eksiğini kapatan tamamlayıcı bir belge olarak duruyor.

### 3.3. Seçenekler

| Seçenek | Sonuç | Değerlendirme |
|---|---|---|
| **A. AGPL kabul edilir**, tüm sistem AGPL-3.0 ile açılır | Madde 5.5 "kullanım hakkı devri" olarak yorumlanır, "münhasır sahiplik" olarak değil | En dürüst ve en uygulanabilir yol. Kamu projesi için açık kaynak zaten olumlu. |
| **B. Ultralytics Enterprise License** alınır | AGPL yükümlülüğü kalkar, kapalı kaynak mümkün olur | Ücretli. Yarışma bütçesi ve takvimi içinde gerçekçi değil. |
| **C. İzin verici lisanslı modele geçilir** | AGPL tamamen ortadan kalkar | Teknik olarak mümkün (bkz. 3.4), ama rapor YOLO11 beyan etti; sapma gerekçelendirilmeli. |
| **D. Görmezden gelinir** | — | **Kabul edilemez.** Madde 10.4 açıkça beyan istiyor. |

**Ekibin şu anki tercihi: A**, mentör görüşmesinde teyit edilmek üzere.

### 3.3.1. ✅ Şartnamenin güncel metni gerilimi büyük ölçüde çözüyor

**Güncelleme — 01.09.2026.** Şartnamenin güncel metni ilk kez birincil
kaynak olarak okundu. Yukarıdaki analiz, Madde 5.5'in kopyaleft bileşene
kapalı olabileceği ihtimali üzerine kuruluydu. **Metin bunun tersini
söylüyor.**

**Madde 10.4 — Açık Kaynak ve Lisans Uygunluğu:**

> "Katılımcılar, projelerinde kullandıkları tüm açık kaynak yazılım,
> model, veri seti, API, kütüphane ve üçüncü taraf bileşenlerin
> lisanslarını beyan etmek zorundadır. **GPL, AGPL**, ticari kullanımı
> sınırlı, attribution gerektiren veya kapalı lisanslı bileşenlerin
> kullanımı **ayrıca belirtilecektir.** Lisans ihlalinden doğacak tüm
> hukuki sorumluluk katılımcılara aittir."

Madde AGPL'i **adıyla anıyor** ve kuralı *kullanma* değil **bildir**
olarak koyuyor. Yani Bakanlık kopyaleft bileşen kullanılacağını
öngörmüş; Seçenek A'nın önündeki temel engel metinsel dayanağını
kaybediyor.

İki madde daha aynı yöne işaret ediyor:

**Madde 9.2:** *"Açık kaynak içerikler kullanılmışsa, lisanslara
uygunluk sorumluluğu Katılımcı'ya aittir."* — açık kaynak kullanımı
beklenen bir durum olarak ele alınmış.

**Madde 10.10 — İdarenin Kullanım Hakkı:**

> "Projenin Bakanlık sistemlerinde kullanılması, **devri,
> lisanslanması**, bakım-destek süreci ve ticarileştirilmesi **ayrıca
> imzalanacak protokol ile düzenlenir.**"

Bu, Bölüm 3.2'deki en sert yorumu yumuşatıyor: Madde 5.5'teki devir
mutlak ve anında bir hak geçişi değil; ayrıntısı **protokole**
bırakılmış. Madde 9.2 de dereceye giren projeler için ayrı protokol
öngörüyor.

**Kalan sınır — gizlenmiyor.** Madde 5.5'in lafzı hâlâ mutlaktır ve ekip
hukukçu değildir. Ultralytics'in telif hakkı Ultralytics'te kalır;
devredilebilecek olan yalnızca ekibin kendi yazdığı kodun haklarıdır.
Mentöre sorulacak sorular (Bölüm 7) **kaldırılmadı** — ama artık "ne
yapalım?" değil, **"okumamız doğru mu?"** sorusudur.

### 3.4. Teknik hafifletme — süreç izolasyonu

AGPL yayılımını *hukuken kesin olarak* engellemez, ama sınırı belirginleştirir
ve alternatif modele geçişi ucuzlatır:

```
web/  ──HTTP──>  api/  ──HTTP──>  model-service/   (ultralytics, AGPL-3.0)
                  │                     ▲
                  │              MODEL_SERVICE_URL
                  └──HTTP──>  model-mock/          (kendi kodumuz, AGPL değil)
```

Uygulanan kurallar:

1. `api/` **hiçbir koşulda** `ultralytics` paketini `import` etmez.
   Bağımlılık listesinde de yer almaz (`api/requirements.txt` içinde yoktur).
2. Model yalnızca `model-service/` içinde, kendi Python ortamında,
   kendi süreci olarak çalışır.
3. İki servis arasındaki tek temas noktası **tek dosyadır**:
   `api/app/services/model_client.py`. Bu dosya `MODEL_SERVICE_URL` ortam
   değişkenini okur; `model-mock` ile gerçek servis arasındaki geçiş tek
   satırlık yapılandırma değişikliğidir.
4. Sözleşme (istek/yanıt JSON şeması) model kütüphanesinden bağımsız
   tanımlıdır — YOLO11 yerine izin verici lisanslı bir modele geçilirse
   `api/` ve `web/` tarafında **hiçbir kod değişmez**.

**Dürüst uyarı:** Süreç izolasyonu bir "AGPL kaçamağı" değildir. Free Software
Foundation, süreç ayrımının tek başına belirleyici olmadığını; bileşenlerin
tek bir işlevsel bütün oluşturup oluşturmadığına bakılması gerektiğini
savunur. Bu proje bir bütün oluşturuyor. İzolasyonun asıl faydası hukuki
koruma değil, **geçiş maliyetini düşürmesi** ve sınırı denetlenebilir
kılmasıdır. Bu belge o iddiadan fazlasını ileri sürmez.

---

## 4. 🔴 GPL-2.0-or-later — PostGIS

PostGIS, PostgreSQL'e yüklenen bir uzantıdır ve GPL-2.0-or-later lisanslıdır.
Raporun 5. bölümünde beyan edilmiştir.

**Değerlendirme:** Uygulamamız PostGIS'i kod olarak bağlamaz. PostgreSQL ayrı
bir süreçtir; uygulama ona ağ soketi üzerinden SQL gönderir. SQL sorgusu
yazmak, GPL'li bir programın kullanıcısı olmaktır — türetilmiş eser üretmek
değil. Bu, GPL uygulamalarının bilinen ve yaygın kabul gören yorumudur
(PostgreSQL çekirdeğinin kendisi izin verici lisanslıdır ve PostGIS'i uzantı
olarak barındırır).

**Sınır nerede:** PostGIS kaynak kodunu değiştirip dağıtırsak veya PostGIS
koduyla statik bağlanan bir ikili üretirsek GPL-2.0 doğrudan işler. Projede
böyle bir plan yoktur.

**AGPL'ye göre neden daha az sorunlu:** GPL-2.0'da ağ üzerinden hizmet sunmak
tetikleyici değildir; AGPL §13 gibi bir madde içermez.

---

## 5. Elenen bileşenler ve gerekçeleri

Bu bölüm, lisans incelemesinin proje kararlarını fiilen değiştirdiğini
gösteriyor.

### 5.1. ❌ `react-leaflet` — Hippocratic-2.1

`react-leaflet@5.0.0` paketinin lisansı **`Hippocratic-2.1`**'dir
(27.08.2026'da `npm view react-leaflet license` ile doğrulandı).

Hippocratic License **OSI onaylı bir açık kaynak lisansı değildir.** Belirli
kullanım biçimlerini yasaklayan etik kısıtlar ve bu kısıtların ihlalinde
devreye giren bir fesih maddesi içerir. Kullanımı kısıtlayan bir bileşen,
Madde 5.5'in istediği **bedelsiz ve koşulsuz hak devrini** kirletir: Kuruma
devredilen üründe, Kurumun kullanımını kısıtlayabilecek üçüncü taraf koşulu
bulunmamalıdır.

**Karar:** `react-leaflet` kullanılmıyor. Onun yerine `leaflet@1.9.4`
(**BSD-2-Clause**, temiz izin verici lisans) doğrudan kullanılıyor; React
entegrasyonu `web/src/lib/leaflet/` altında kendi yazdığımız ince bir
sarmalayıcıdır. Yan fayda: bir bağımlılık eksildi.

### 5.2. ❌ `psycopg2-binary` / `psycopg` — LGPL

`psycopg2-binary` LGPL, `psycopg@3` ise **LGPL-3.0-only** lisanslıdır
(PyPI meta verisinden doğrulandı). LGPL zayıf kopyalefttir ve dinamik
bağlamada uygulama kodunu kapsamaz; yani kullanılabilirdi. Ancak Madde 5.5
devrinde açıklanması gereken gereksiz bir kopyaleft yüzeyi oluşturur.

**Karar:** `asyncpg@0.31` (**Apache-2.0**) kullanılıyor. SQLAlchemy 2.0 async
+ GeoAlchemy2 ile sorunsuz çalışır ve daha hızlıdır. Kopyaleft yüzeyi bu
kararla yalnızca YOLO11 ve PostGIS'e indirilmiştir.

---

## 6. `LICENSE` dosyası — ✅ AGPL-3.0 (01.09.2026)

Proje **AGPL-3.0** ile lisanslanmıştır. `LICENSE` dosyası, Free Software
Foundation'ın resmi AGPL-3.0 metnini (661 satır, §13 *Remote Network
Interaction* dahil) **birebir** içerir; metin değiştirilmemiştir.

**Karar gerekçesi:** Bölüm 3.3.1 — şartnamenin güncel metni (Madde 10.4,
9.2, 10.10) kopyaleft bileşen kullanımını beyan şartına bağlıyor,
yasaklamıyor. Tam kayıt: `docs/karar-kaydi.md` **K-020**.

**Neden başka bir şey değil:** Ürün `ultralytics` içerdiği sürece
AGPL-3.0 tek tutarlı seçenektir. MIT yazmak AGPL §13'ü karşılamaz ve
yanlış bir taahhüt üretir; boş bırakmak ise teslim anında Madde 10.4'ü
karşılamaz.

**Geri alınabilirlik:** Mentör Madde 5.5'i farklı yorumlarsa Seçenek B
(Enterprise lisans) veya C (izin verici modele geçiş) açıktır. C için
mimari zaten hazırdır: model ayrı süreçte çalışır, `api/` onu yalnızca
HTTP ile çağırır — model değişimi tek bir servisi etkiler (Bölüm 3.4).

---

## 7. Mentöre sorulacak sorular

Şartname Madde 5.2 her takıma en az dört mentör görüşmesi zorunluluğu
getiriyor. Aşağıdaki sorular **ilk görüşmede** sorulacak; cevaplar
`docs/karar-kaydi.md`'ye tarihli olarak yazılacaktır.

> **Güncelleme — 01.09.2026.** Şartnamenin güncel metni okundu (Bölüm
> 3.3.1). Sorular **kaldırılmadı** ama nitelikleri değişti: artık "ne
> yapalım?" değil, **"okumamız doğru mu?"** sorularıdır. Proje bu arada
> AGPL-3.0 ile lisanslandı (K-020); mentör farklı yorumlarsa karar geri
> alınabilir.

1. Madde 10.4 GPL/AGPL'li bileşenlerin "ayrıca belirtilmesini" istiyor,
   kullanımını yasaklamıyor. Madde 10.10 da devir ve lisanslamayı ayrı
   bir protokole bırakıyor. **Buradan, Madde 5.5'in AGPL'li bir bileşene
   kapalı olmadığı sonucunu çıkarmamız doğru mu?**
2. Madde 5.5, bileşenlerin üçüncü taraf lisanslarını mı kapsıyor, yoksa
   yalnızca takımın kendi yazdığı kodun haklarını mı?
3. Kopyaleft bileşen kullanımı değerlendirmede olumsuz bir unsur mudur?
   Değilse, projenin tamamının AGPL-3.0 ile açılması kabul edilebilir mi?
4. Madde 10.4'ün istediği lisans beyanı için bu belgenin biçimi yeterli mi,
   yoksa ayrı bir form/şablon var mı?
5. (İlgili) Madde 2.6.2 sunum süresini 5 dakika, Madde 5.4 ise 7+3 dakika
   olarak veriyor. Hangisi esastır?

**Şartnamenin güncel metninde bulunan iki tutarsızlık daha** (01.09.2026):

6. **Finalist sayısı:** Madde 4 "en fazla **15 takım** / 75 kişi" diyor,
   Madde 5.3 ise "ilk **10 proje** seçilecektir" diyor. Hangisi geçerli?
7. **Takvim sırası:** Tablo 1'de 09.09.2026 "Proje Sunumu (Final)",
   11.09.2026 "Finalistlerin Açıklanması" olarak sıralanmış — final
   sunumu, finalistler açıklanmadan önce görünüyor. Sıralama doğru mu?

**Çevresel etki (Madde 10.9) için — `docs/cevresel-etki.md` Bölüm 5:**

8. Bakanlık'ın yayımlanmış bir **hacim→ağırlık dönüşüm katsayısı**
   tablosu var mı? Varsa EPA değerlerinin yerine öncelikle o
   kullanılmalıdır (şu an 5 malzeme sınıfından yalnızca 2'si kaynaklı;
   **beton kapalı**).
9. Karbon azaltım potansiyeli için kullanılabilecek **emisyon faktörü**
   kaynağı var mı? Bu olmadan Madde 10.9'un o kalemi hesaplanamaz ve
   sayı uydurulmayacaktır.

**Veri seti kaynağı (Madde 5.2 / 9.2 / 10.4) — 02.09.2026:**

10. Eğitim veri seti takımca toplandı. Görüntülerin **kaynak ve lisans
    beyanı** hangi ayrıntıda isteniyor? Arama motorundan alınan
    görüntüler için Madde 9.2'nin "üçüncü taraf hakkı ihlal edilmedi"
    beyanı nasıl karşılanmalı? Bkz. Bölüm 2.1.1.

---

## 8. Bakım kuralı

Depoya **her yeni bağımlılık eklendiğinde** bu belgedeki ilgili tablo aynı
commit içinde güncellenir. Lisansı bilinmeyen veya izin verici olmayan bir
paket, bu belgeye işlenmeden koda girmez.

Kontrol komutları:

```bash
# Python
curl -s https://pypi.org/pypi/<paket>/json | python3 -c \
  "import sys,json; d=json.load(sys.stdin)['info']; print(d.get('license_expression') or d.get('license'))"

# Node
npm view <paket> license
```
