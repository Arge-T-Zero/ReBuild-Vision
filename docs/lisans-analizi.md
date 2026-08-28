# Kütüphane ve Lisans Analizi

**Proje:** ReBuild Vision · **Takım:** Arge-T Zero (Başvuru 5387352)
**Belge tarihi:** 27.08.2026 · **Durum:** Canlı belge — her yeni bağımlılıkta güncellenir
**Son güncelleme:** 27.08.2026 — CDW-Seg veri seti (CC0) eklendi; PostgreSQL 17 / PostGIS 3.6.4 sürümleri kesinleşti

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
| ultralytics (YOLO11) | 8.4.x | **AGPL-3.0** 🔴 | **ayrı süreç** (`model-service/`) | https://github.com/ultralytics/ultralytics |
| model ağırlıkları (özgün eğitim) | — | karar bekliyor | model dosyası | proje içi |

### 2.2. Veri tabanı

| Paket | Sürüm | Lisans | Kullanım biçimi | Kaynak |
|---|---|---|---|---|
| PostgreSQL | 17.11 | PostgreSQL License (izin verici) | ayrı süreç | https://www.postgresql.org |
| PostGIS | 3.6.4 | **GPL-2.0-or-later** 🔴 | veri tabanı uzantısı (ayrı süreç) | https://postgis.net |
| GEOS | — | LGPL-2.1 | PostGIS bağımlılığı | https://libgeos.org |
| PROJ | — | MIT | PostGIS bağımlılığı | https://proj.org |

### 2.3. Backend (`api/`)

| Paket | Sürüm | Lisans | Kullanım biçimi | Kaynak |
|---|---|---|---|---|
| fastapi | 0.141 | MIT | kütüphane | https://github.com/fastapi/fastapi |
| uvicorn | 0.52 | BSD-3-Clause | kütüphane | https://github.com/encode/uvicorn |
| pydantic | 2.x | MIT | kütüphane | https://github.com/pydantic/pydantic |
| sqlalchemy | 2.0 | MIT | kütüphane | https://github.com/sqlalchemy/sqlalchemy |
| geoalchemy2 | 0.20 | MIT | kütüphane | https://github.com/geoalchemy/geoalchemy2 |
| alembic | 1.19 | MIT | kütüphane | https://github.com/sqlalchemy/alembic |
| **asyncpg** | 0.31 | **Apache-2.0** | kütüphane | https://github.com/MagicStack/asyncpg |
| pyjwt | 2.13 | MIT | kütüphane | https://github.com/jpadilla/pyjwt |
| bcrypt | 5.0 | Apache-2.0 | kütüphane | https://github.com/pyca/bcrypt |
| python-multipart | 0.0.32 | Apache-2.0 | kütüphane | https://github.com/Kludex/python-multipart |
| pillow | 12.x | MIT-CMU | kütüphane | https://github.com/python-pillow/Pillow |
| httpx | 0.28 | BSD-3-Clause | kütüphane | https://github.com/encode/httpx |

### 2.4. Web arayüzü (`web/`)

| Paket | Sürüm | Lisans | Kullanım biçimi | Kaynak |
|---|---|---|---|---|
| react / react-dom | 19.x | MIT | kütüphane | https://github.com/facebook/react |
| vite | 8.x | MIT | derleme aracı | https://github.com/vitejs/vite |
| typescript | 5.x | Apache-2.0 | derleme aracı | https://github.com/microsoft/TypeScript |
| **leaflet** | 1.9.4 | **BSD-2-Clause** | kütüphane | https://github.com/Leaflet/Leaflet |
| @tanstack/react-query | 5.x | MIT | kütüphane | https://github.com/TanStack/query |
| tailwindcss | 4.x | MIT | derleme aracı | https://github.com/tailwindlabs/tailwindcss |
| @tailwindcss/vite | 4.x | MIT | derleme aracı | https://github.com/tailwindlabs/tailwindcss |
| @types/leaflet | 1.9 | MIT (DefinitelyTyped) | tip tanımı (derleme) | https://github.com/DefinitelyTyped/DefinitelyTyped |
| @vitejs/plugin-react | 5.x | MIT | derleme aracı | https://github.com/vitejs/vite-plugin-react |
| oxlint | 1.x | MIT | geliştirme aracı (lint) | https://github.com/oxc-project/oxc |

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
| flutter_secure_storage | 11.0 | BSD-3-Clause | Şifreli yerel depolama |
| http | 1.6 | BSD-3-Clause | API çağrıları |
| image_picker | 1.2 | BSD-3-Clause | Kamera ve galeri |
| geolocator | 14.0 | MIT | Konum |
| connectivity_plus | 7.3 | BSD-3-Clause | Bağlantı durumu |

Hepsi izin vericidir; Madde 5.5 devrini kirletmez.

### 2.5. Yardımcı betikler (`scripts/`)

| Paket | Sürüm | Lisans | Kullanım biçimi | Kaynak |
|---|---|---|---|---|
| opencv-python-headless | **4.10.0.84** | Apache-2.0 | kütüphane (`maskele.py`) | https://github.com/opencv/opencv-python |

### 2.6. Veri kaynakları (kod değil)

| Kaynak | Lisans / koşul | Not |
|---|---|---|
| **CDW-Seg** eğitim veri seti | **CC0 1.0 (kamu malı)** ✅ | Sirimewan & Arashpour, *Scientific Data*, 28.05.2025. DOI: 10.6084/m9.figshare.28573229 · Makale DOI: 10.1038/s41597-025-05243-x. Ayrıntı: Bölüm 2.7 |
| OpenStreetMap karo görüntüleri | ODbL 1.0 + OSMF Tile Usage Policy | **Atıf zorunlu.** Karo sunucusuna yük bindirilmeyecek; demo ölçeğinde kullanılıyor. Üretimde kendi karo sunucusu gerekir. |
| Bakanlık tarafından sağlanan veri | Madde 9.1 — kopyalanamaz, paylaşılamaz | Depoya **asla** girmez. Bkz. `docs/veri-politikasi.md` |


### 2.7. Eğitim veri seti — CDW-Seg

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

## 6. `LICENSE` dosyası — karar bekliyor

Depodaki `LICENSE` dosyasına **henüz nihai bir lisans yazılmamıştır.**

Gerekçe: Bölüm 3.3'teki seçenek doğrudan `LICENSE` içeriğini belirler.
Seçenek A benimsenirse projenin kendisi **AGPL-3.0** ile lisanslanmalıdır;
MIT yazmak hukuken tutarsız olur — AGPL'li bir bileşenle aynı programı
oluşturan kodu MIT ile sunmak AGPL §13'ü karşılamaz.

Bu nedenle `LICENSE` dosyası şu an bir **karar bekleme notu** içeriyor.
Mentör görüşmesinden sonra tek seferde doldurulacak ve
`docs/karar-kaydi.md`'ye tarihli olarak işlenecektir. Karar verilmeden
yer tutucu bir lisans metni yazmak, yanlış bir taahhüt üretme riski taşır.

---

## 7. Mentöre sorulacak sorular

Şartname Madde 5.2 her takıma en az dört mentör görüşmesi zorunluluğu
getiriyor. Aşağıdaki sorular **ilk görüşmede** sorulacak; cevaplar
`docs/karar-kaydi.md`'ye tarihli olarak yazılacaktır.

1. Madde 5.5'teki "sahiplik devri", AGPL-3.0 lisanslı bir bileşen içeren
   ürün için nasıl yorumlanmalıdır? Kurum, devraldığı ürünü AGPL koşullarıyla
   işletmeyi kabul ediyor mu?
2. Madde 5.5, bileşenlerin üçüncü taraf lisanslarını mı kapsıyor, yoksa
   yalnızca takımın kendi yazdığı kodun haklarını mı?
3. Kopyaleft bileşen kullanımı değerlendirmede olumsuz bir unsur mudur?
   Değilse, projenin tamamının AGPL-3.0 ile açılması kabul edilebilir mi?
4. Madde 10.4'ün istediği lisans beyanı için bu belgenin biçimi yeterli mi,
   yoksa ayrı bir form/şablon var mı?
5. (İlgili) Madde 2.6.2 sunum süresini 5 dakika, Madde 5.4 ise 7+3 dakika
   olarak veriyor. Hangisi esastır?

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
