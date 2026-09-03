# Teslim Denetimi — 02.09.2026

Teslime iki gün kala yapılan, sıfırdan ve her şeyi kapsayan kontrol:
depo, otuz belge, kod, testler, sürekli tümleştirme, dağıtım, güvenlik
ve iki arayüz.

`results/denetim-29-08.md` bu belgenin öncülüdür ve aynı ilke geçerlidir:
**her satırın arkasında çalıştırılmış bir komut vardır.** Çalıştırılamayan
şeyler ayrı bir başlıkta, gerekçesiyle listelenmiştir — "yazdım, herhalde
çalışıyor" bu belgede geçmez.

**Yöntem:** üç bağımsız envanter taraması (belgeler / kod-test-güvenlik /
arayüzler) + elle doğrulama. Bulgular ciddiyetine göre sıralandı,
düzeltildi ve düzeltmeler yeniden çalıştırılarak doğrulandı.

---

## 1. Özet

| | |
|---|---|
| İncelenen belge | 29 `.md` + 2 kök JSON beyanı |
| İncelenen kaynak | api 3.198 · web 6.345 · mobil 2.294 · test 2.433 satır |
| Bulgu | **49** (10 kritik · 26 önemli · 13 kozmetik) |
| Düzeltilen | **41** |
| Açık bırakılan | 8 — hepsi gerekçesiyle Bölüm 6'da |
| Sunucu testi | 155 → **170** |
| Mobil testi | 18 → **29** |

**En pahalı üç bulgu, üçü de test takımının kör noktasındaydı:** mobil
uygulamanın ana işlevi gerçek cihazda hiç çalışmıyordu, jürinin kurulum
yolu gerçek modeli hiç çalıştırmıyordu ve konteynerde çalışan sistem
kendi ölçümünü yalanlıyordu.

---

## 2. Kritik bulgular ve düzeltmeleri

### 2.1 🔴 Mobil görüntü yükleme gerçek cihazda hiç çalışmıyordu

`mobile/lib/api.dart` → `MultipartFile.fromPath` çağrısında `contentType`
verilmiyordu. `http` 1.6.0 varsayılan olarak `application/octet-stream`
gönderir (`multipart_file.dart:54`); sunucu yalnızca
`image/jpeg|png|webp` kabul ediyor ve **ilk dosyada bütün partiyi** 415
ile düşürüyor (`goruntuler.py`, döngü içinde `raise`).

Yani saha uygulamasının **ana işlevi** çalışmıyordu ve kullanıcı ekranda
ham MIME tipini görüyordu.

**Neden hiçbir denemede görünmedi:** web arayüzünde türü tarayıcı
belirliyor; Flutter web'de `fromPath` zaten daha önce hata veriyor. Hata
yalnızca gerçek telefonda ortaya çıkıyordu.

**Düzeltme:** `goruntuTuru()` dosya adından MIME türü üretir; bilinmeyen
uzantıda `octet-stream`'e düşmez, `image/jpeg` varsayar.
**Nöbetçi:** `mobile/test/goruntu_turu_test.dart` — izin listesini
sunucunun `goruntuler.py` dosyasından **okuyarak** karşılaştırır.

### 2.2 🔴 Jürinin kurulum yolu gerçek modeli hiç çalıştırmıyordu

`docker/` altında `model-service` için Dockerfile yoktu; `compose.yaml`
yalnızca sahte servisi kaldırıyor ve yorumu hâlâ *"gerçek model hazır
olduğunda eklenecek"* diyordu. Model **01.09'da** hazır olmuştu.

Sonuç: jüri Madde 10.3 paketini kurduğunda ekranda kalıcı **"SAHTE MODEL
SERVİSİ"** bandı görüyor, takımın 2,03 saat eğittiği YOLO11m'i hiç
göremiyordu.

**Düzeltme:** `docker/model-service.Dockerfile` +
`docker/compose.gercek-model.yaml` bindirmesi. Ağırlık salt okunur
bağlanır; yoksa `/predict` **503** döner ve uydurma üretilmez.

**Canlı demo ayrı bir karar:** gerçek servis torch içerir (diskte
**1,2 GB**, ölçüldü); Render ücretsiz katmanı **512 MB RAM** veriyor.
Sığmıyor. Bu bir tercih değil ölçülmüş bir kısıt; `render.yaml`'a
gerekçesiyle yazıldı ve arayüz sahteliği zaten kalıcı bantla söylüyor.

### 2.3 🔴 Konteynerde sistem kendi ölçümünü yalanlıyordu

`docker/api.Dockerfile` `results/egitim/metrikler.json` dosyasını imaja
kopyalamıyordu. `config.model_metrik_ozeti()` dosyayı bulamayınca
`"henüz ölçülmedi"` döner — ve bu metin **üç yerde** görünür:
`/sistem/durum`, arayüz altbilgisi ve **indirilen her raporun künyesi**.

README aynı anda test mAP50 = 0,4334 ilan ederken, jürinin çalıştıracağı
sürüm "model ölçülmedi" diyordu.

**Düzeltme:** tek `COPY` satırı.

### 2.4 🔴 Demo verisi boştu — jüri boş bir sistem görüyordu

`scripts/demo_veri.py` yedi hesap ve bir alan üretiyordu; **tek görüntü
ve tek tespit yoktu.** Projenin en güçlü anları jürinin önüne
kendiliğinden hiç gelmiyordu.

**Düzeltme:** üç saha, üç görüntü, sekiz tespit — dört kural da ilk
ekranda görünür (temiz bir veri tabanında çalıştırılarak doğrulandı):

| # | Senaryo | Görünen |
|---|---|---|
| 1 | ölçüm + kaynaklı katsayı | **4,012 – 6,360 ton** aralık + EPA kaynağı |
| 2 | doğrulanmış, ölçüm yok | **MİKTAR BOŞ** — sıfır değil |
| 3 | doğrulanmamış | hiçbir hesaba girmiyor |
| 4 | düşük güven (%31,8) | uzman kuyruğuna **kendiliğinden** düştü |
| 5 | uzman düzeltmesi | ham tahmin + geçerli sınıf birlikte |
| 6 | doğrudan tartım | katsayısız aralık |
| 7 | ölçüm VAR, katsayı kapalı | **MİKTAR YİNE BOŞ**, sebebi yazılı |
| 8 | belirsiz | ikinci incelemeye açık |

Yeniden çalıştırıldığında mükerrer kayıt üretmiyor (doğrulandı).

### 2.5 🔴 Nesne düzeyi yetkilendirme eksikti

Yetki kontrolü **eylem** üzerinden yapılıyordu, **nesne** üzerinden
unutulmuştu. `gorulebilir_alanlar()` liste uçlarında uygulanıyordu ama
`GET /tespit/{id}`, `/miktar/{id}`, `/olcum/tespit/{id}`,
`/tehlikeli/tespit/{id}`, `POST /tespit/{id}/dogrula` ve `POST /olcum`
yalnızca "giriş yapmış mı" diye bakıyordu.

Dış taraf bir rol (yıkım firması) id'leri gezerek göremediği sahaların
tespitlerini, sınıflarını ve **hesaplanmış tonajını** okuyabiliyordu.

**Düzeltme:** `queries.gorulebilir_tespitler()` — veri katmanında.
Karar: **K-023**. Üç testle korunuyor.

### 2.6 🔴 Mobil güven skorunu yuvarlıyordu

`toStringAsFixed(1)` ile 0,8734567 telefonda **"%87.3"** görünüyordu;
aynı kayıt web'de "%87,3457". Ondalık ayracı da **nokta**ydı. Kodun
hemen üstündeki yorum *"Güven skoru yuvarlanmaz"* diyordu (Bölüm 9.2) —
yorum kodu yalanlıyordu. **Düzeltildi**, üç testle bağlandı.

### 2.7 🔴 Mobilde kalıcı sahte model rozeti yoktu

Uyarı yalnızca bir yükleme yapıldıktan sonra sonuç kartında beliriyordu;
mobil `/sistem/durum` ucunu **hiç çağırmıyordu**. Jüri telefonu elinde
Ölçüm sekmesine baksa sahtelik hakkında tek işaret görmezdi
(`README.md` bunu taahhüt ediyordu). **AppBar'a kalıcı bant eklendi.**
Durum bilinmiyorken (çevrimdışı) bant **gösterilmez** — sahteliği
gizlemek için değil, bilmediğimiz bir şeyi iddia etmemek için.

### 2.8 🔴 Depoya kazayla bir Python sanal ortamı işlenmişti

`web/.venv-inceleme/` **1.906 dosya** olarak izleniyordu — izlenen 2.162
dosyanın **%88'i**. Gerçek proje 256 dosya. 30.08'de girmiş; 29.08
denetimi 205 dosya sayıyordu, boşluk tam o denetimden bir gün sonra
açılmış ve dört gün fark edilmemiş.

İçinde beyan edilmemiş üçüncü taraf kod da vardı (`pip`, `setuptools`,
**`certifi` — MPL-2.0**), yani aynı zamanda bir Madde 10.4 boşluğuydu.

**Düzeltme:** `git rm -r --cached`; `.gitignore` ad kalıbına çevrildi ve
yedi ayrı konumla doğrulandı.

### 2.9 🔴 Kullanıcı kılavuzu jüriye yanlış bilgi veriyordu

> "Mevcut eğitim verisinde **cam** ve **seramik** sınıfı bulunmamaktadır;
> **tuğla** ise betondan ayrılmaz. Model bu grupları **tanımaz.**"

Üçü de yanlış. `cam` modelin **en iyi** sınıfı (test mAP50 0,7257).
**Yeniden yazıldı** — ve `seramik`'in pratikte çalışmadığı (0,0877)
açıkça eklendi.

### 2.10 🔴 Madde 10.5 beyanı kendi içinde çelişiyordu

`docs/yapay-zeka-beyani.md` bir bölümde "on sınıftan birine atamak" ve
"model henüz eğitilmediği için" diyor, başka bir bölümünde beş sınıfı ve
ölçülmüş metrikleri beyan ediyordu. Şartname maddesine cevap veren
belgenin kendi içinde çelişmesi en pahalı hata türü. **Düzeltildi.**

---

## 3. Önemli bulgular — düzeltilenler

| # | Bulgu | Düzeltme |
|---|---|---|
| 3.1 | Yükleme boyut/sayı sınırı **yoktu**; her dosya belleğe okunuyordu. Tek koruma nginx'teydi ve yerel/Render/**mobil** yolları kapsamıyordu | Dosya başına 32 MB, istek başına 10 dosya / 64 MB. İki testle bağlandı; sınırların nginx'inkiyle uyumu da sınanıyor |
| 3.2 | Lisans beyanında **11 sürüm yanlıştı**, bir paket hayaletti (`@tanstack/react-query`), üç paket eksikti, model servisi ve temel imajlar hiç beyan edilmemişti | Tablolar manifestolardan yeniden üretildi. **`tests/test_lisans_beyani.py`** eklendi: beyanı `requirements.txt`, `package.json`, `pubspec.yaml` ve Dockerfile'lara bağlar — ayrışırsa kırılır |
| 3.3 | `oxlint` kurulu ve yapılandırılmış ama CI'da **hiç çağrılmıyordu** | `npm run lint` CI'ya eklendi |
| 3.4 | Web yükleme sonuç listesinde **ÖN TAHMİN etiketi yoktu** (kural "istisnasız" diyor) | Eklendi |
| 3.5 | Harita balonu ve lejandı **ham sınıf adı** basıyordu ("beton_tugla (3)") | `siniflar.json` → `kapsanmayan_gruplar`'a `gorunen_ad` eklendi; arayüz onu kullanıyor |
| 3.6 | Kuyruk `aria-label`'ı ham ad okuyordu — aynı hata `TespitKutulari`'nda bir kez düzeltilmişti | Düzeltildi |
| 3.7 | `index.css`'te 10 sınıflık **ölü ve yanıltıcı** palet: `--color-m-yumusak_plastik` bugün `cam`'ın rengi | Kaldırıldı; renkler çalışma zamanında `/sistem/siniflar`'dan geliyor |
| 3.8 | `sistem.py` docstring'i "cam ve seramik tanınmaz" diyordu — FastAPI `/docs`'ta **jüriye görünüyor** | Düzeltildi |
| 3.9 | `results/bilinen-sinirlar.md` C bölümü, ölçülmüş iki satırı "ölçülmedi" sayıyordu | Üstü çizilerek kapatıldı; eşik satırının sebebi güncellendi |
| 3.10 | `docker/README.md` başlığı "doğrulandı ✅", sonu "doğrulama yapılmadı" | Tek durum beyanına indirildi |
| 3.11 | ΔE sayıları iki kararda uyuşmuyordu (K-012: 8,6 · K-022: 3,5) | **Yeniden ölçüldü**: çelişki yok, **ölçütler farklı**. K-022 bütün ikilileri, K-012 komşu sıralamayı ölçüyor. Her iki karara ölçüt yazıldı |
| 3.12 | K-018 geçersiz kalmıştı (9 sınıf / 4 katsayı üzerine kurulu) | Geçersizlik notu eklendi (K-006 ve K-012 gibi) |
| 3.13 | Altı belgede "Son güncelleme" damgası içerikten eskiydi | Güncellendi |
| 3.14 | `tests/README.md` envanterinde **üç test dosyası eksikti** | Eklendi |
| 3.15 | `results/denetim-29-08.md` tek başına okununca yanlış bilgi veriyordu | Üstüne "tarihî kayıt" uyarısı ve yedi satırlık fark tablosu |
| 3.16 | `RAPOR_ICIN_METRIKLER.md` var olmayan `rapor_ciktilari/` klasörüne atıf yapıyordu | Yollar düzeltildi |
| 3.17 | README şartname tablosunda **5.2, 5.5 ve 9.2 satırları yoktu** — 5.2 projenin kendi beyanına göre en acil boşluğu | Eklendi; 5.2 kırmızı işaretli |
| 3.18 | `docs/demo-video.md` "metrikler ölçülmedi" diyordu ve eski bir tonaj örneği taşıyordu — **çekim yarın** | Güncellendi; videoda ölçülmüş mAP söylenebilir, sınırıyla birlikte |
| 3.19 | `docs/lisans-analizi.md` "9 sınıftan 4'ü kaynaklı" diyordu | 5'ten 2'si |
| 3.20 | `docs/cevresel-etki.md` "modelin eğitilmesi" hâlâ gereken işler listesindeydi | Kapatıldı |
| 3.21 | `mobile/` sınıf renk/ad haritası `siniflar.json` ile elle senkron tutuluyordu | `test/sinif_adlari_test.dart` bağladı |
| 3.22 | Mobil yükleme hatası **her durumda** "bağlantı" diyordu; 403/413/503 de öyle görünüyordu | `ApiHatasi` ayrı yakalanıyor, sunucunun gerekçesi yazılıyor |
| 3.23 | **Yükleme yetkisi olan iki rol yükleme ekranını göremiyordu.** Sunucu `belediye` ve `yonetici`'ye izin veriyor, kılavuz da öyle diyor; menüde `yukle` yoktu ve `/yukle` derin bağlantısı ana sayfaya düşüyordu | Menüye eklendi |
| 3.24 | **Sunucu birimi ekrana basılıyordu:** "Değer (m3)", "12,4 m2", kuyrukta "40 m3". Bunlar makine biçimidir; kullanıcı formda "m³" seçip kuyrukta "m2" görüyordu | Web ve mobilde sunucu birimi ↔ görünen birim ayrıldı; mobilde iki testle bağlandı |
| 3.25 | İstemci dosya süzgeci sunucu sözleşmesinden **genişti** (`image/*`); iPhone HEIC dosyaları geçiyor, sunucu 415 verip **bütün partiyi** düşürüyordu | Süzgeç ve `accept` daraltıldı; hata metni HEIC'i adıyla anlatıyor |

---

## 4. Çalıştırılarak doğrulananlar

| Kontrol | Sonuç |
|---|---|
| `pytest tests` | **170 geçti**, 0 hata (4 dk 59 sn) |
| `flutter analyze` | temiz |
| `flutter test` | **27 geçti** |
| `npm run build` | başarılı |
| `npm run lint` | uyarı var, hata yok (çıkış 0) |
| `docker compose config` (varsayılan) | geçerli |
| `docker compose config` (gerçek model bindirmesi) | geçerli; `MODEL_SERVICE_URL` doğru yönleniyor |
| `render.yaml` | geçerli YAML |
| Demo verisi, temiz veri tabanında | 3 saha · 3 görüntü · 8 tespit; sekiz senaryonun sekizi de doğru |
| Demo verisi, ikinci çalıştırma | mükerrer kayıt yok |
| Sınıf adı bozulduğunda | suite **8 testte kırmızıya** dönüyor (koruma çalışıyor) |
| Sızıntı denetimi | `.env` yok · ağırlık yok · arşiv yok · bakanlık verisi yok · `node_modules` yok · `__pycache__` yok · sır deseni taraması temiz |
| İzlenen dosya | 2.162 → **256** |
| ΔE ölçümü (iki palet, iki ölçüt) | eski 3,51 / 23,6 · yeni **6,79** / 14,4 |
| Etiket kontrastı (5 renk) | en düşük **4,83** (AA eşiği 4,5) |
| CI (`main`) | yeşil |

### Jüri gibi çalıştırma — ekranla doğrulandı

Yığın yeni demo veri tabanına bağlanıp gerçek bir ultralytics ağırlığıyla
gezildi (`belediye@demo.local`):

| Ne | Sonuç |
|---|---|
| Giriş sonrası ilk ekran | **Boş değil**: 3 saha, 3 farklı erişim durumu, doğrulanmış malzeme dağılımları |
| Altbilgi | **"test mAP50 = 0,4334"** — "henüz ölçülmedi" değil |
| `/sistem/durum` | `sahte: false`, `AGPL-3.0 (ultralytics)` |
| Menüde `Yükle` (belediye) | ✅ göründü (3.23 düzeltmesi) |
| Her tespitte "ÖN TAHMİN" | ✅ |
| Uzman düzeltmesi | ✅ "Seramik → Beton / tuğla" — ham tahmin ve geçerli sınıf birlikte |
| Düşük güvenli tespit | ✅ "Uzman incelemesi gerekli" |
| Miktar kartı | **4,012 – 6,36 ton** + "belirsizlik aralığı" + yöntem + EPA kaynağı |
| Ölçümsüz tespitte miktar | boş — sıfır değil |
| Tehlikeli madde bölümü | "Kayıt bulunmaması… anlamına GELMEZ" yazılı |
| Tarayıcı konsolu | temiz (harita karo isteklerinin ağ politikasıyla engellenmesi dışında) |

---

## 5. Doğrulanamayanlar — ve nedeni

Bu başlık bilinçli olarak ayrı. Aşağıdakiler **çalıştığı görülmemiş**
şeylerdir; teslim öncesi çalıştırılmaları gerekir.

> ✅ **03.09.2026 güncellemesi — gerçek model çalıştı.** Ağırlık
> [`model-v1`](https://github.com/Arge-T-Zero/ReBuild-Vision/releases/tag/model-v1)
> sürümünden indirildi (39 MB, sha256 `6864a909d1969548…`), model servisi
> onunla ayağa kalktı (`/health` → `sahte: false`, `agirlik_yuklendi: true`),
> deponun üç örnek görüntüsü üzerinde çıkarım yapıldı ve **14 gerçek
> tespit** üretildi. Sınıf sırası `siniflar.json` ile birebir doğrulandı.
> Demo verisi artık elle yazılmış kutular değil, **bu çıktıyı** kullanıyor.
>
> Kalan tek doğrulanamayan: imajın **docker içinde** derlenmesi.

| Ne | Neden | Kim yapmalı |
|---|---|---|
| 🔴 **Gerçek model imajının DERLENMESİ** | Ağ politikası Docker kayıt defterinin dağıtım ağını (`production.cloudfront.docker.com`) engelliyor; `python:3.11-slim` indirilemiyor. Servisin kendisi ağırlıkla **çalıştı** (docker dışında); doğrulanamayan yalnızca imaj derlemesi | Teslim öncesi, gerçek bir makinede |
| 🔴 **`docker compose up` uçtan uca** | Aynı kısıt | Teslim öncesi |
| 🟠 Mobil `contentType` düzeltmesinin gerçek cihazda sınanması | Emülatör/cihaz yok. Birim testle bağlandı ama gerçek bir yükleme denenmedi | Teslim öncesi, tek fotoğraf yeterli |
| 🟠 Canlı demo (Vercel/Render) | Ağ politikası dış erişimi engelliyor | Sunum öncesi bir kez uyandırın |
| 🟡 `ultralytics==8.4.0` sürümünün PyPI'da varlığı | CI onu hiç kurmuyor | CI'ya eklenebilir |

**Komut:**

```bash
cp best.pt model-service/agirliklar/
docker compose -f docker/compose.yaml \
               -f docker/compose.gercek-model.yaml up --build
curl -s http://localhost:8080/api/sistem/durum   # sahte: false olmalı
```

---

## 6. Açık bırakılanlar — ve gerekçesi

| Bulgu | Neden düzeltilmedi |
|---|---|
| 🔴 **Eğitim veri setinin kaynak/lisans beyanı** | Kod işi değil, kayıt işi. Görüntülerin nereden toplandığını yalnızca takım bilir. Madde 5.2 ve 9.2 kapsamında; yedi belgede açıkça yazılı, gizlenmiyor. **Teslim öncesi kapatılması gereken tek gerçek boşluk budur** |
| Yüklenen görüntüler kimlik doğrulaması olmadan servis ediliyor (`/dosya`) | Dosya adları 64 bitlik rastgele; pratik risk düşük. Kimlik denetimi eklemek statik dosya sunumunu değiştirmeyi gerektirir — teslime iki gün kala riskli. `docs/mimari.md` bilinen boşluklar tablosuna yazıldı |
| Dosya uzantısı istemciden geliyor, MIME'dan türetilmiyor | Aynı gerekçe; MIME denetimi zaten var, uzantı yalnızca dosya adında kullanılıyor |
| CORS `allow_credentials=True` + kaynak listesi doğrulanmıyor | Bugünkü değerler dar; jeton çerezde değil `Authorization` başlığında. Etkisi sınırlı |
| Mobilde rol duyarlılığı yok | `yikim`/`tesis` telefonda yükleme arayüzünü görüyor, sunucudan 403 alıyor. Güvenlik açığı değil, kullanılabilirlik pürüzü. Mobil zaten yalnızca saha personeli için tasarlandı |
| Mobilde kayıt (hesap açma) ekranı yok | Tasarım kararı; `mobile/README.md`'de yazılı |
| Web için birim test yok | Teslime iki gün kala yeni bir test altyapısı kurmak, mevcut olanı doğrulamaktan daha riskli |
| oxlint uyarıları (10 adet) | Uyarı, hata değil. Hepsi biçim/hook bağımlılığı; son gün davranış değiştirmeye değmez |

---

## 7. Jüri gözüyle — güçlü kalan yanlar

Denetimin bulduğu şeyler kadar **bulamadıkları** da anlamlı:

- **Metrik sayıları her yerde birebir aynı.** 0,4424 / 0,4334 / 0,7257 /
  0,0877 / 2.765 / 9.348 — yedi belge ve ham çıktılar arasında tek bir
  sapma yok.
- **Kırık iç bağlantı yok.** 29 belgedeki bütün göreli bağlantı hedefleri
  ve K-001…K-023 atıflarının tamamı mevcut.
- **Dört temel kural üç katmanda birden korunuyor:** API, servis katmanı
  ve veri tabanı `CHECK` kısıtı.
- **AGPL sınırı** beş testle, imaj düzeyinde dahil.
- **`ORTAM=uretim` + varsayılan JWT anahtarı → açılış durur.** Çok az
  proje bunu yapar.
- **Bilinen sınırlar gizlenmiyor:** `seramik` sınıfının çalışmadığı,
  betonun katsayısız olduğu, veri setinin lisans beyanının eksik olduğu
  — üçü de kendi belgelerinde yazılı.
- **Testler kuralları koruyor, yeşil olmak için yazılmamış.** `conftest`
  içindeki `malzeme_olmayan_sinif` fixture'ı ve `tespit_kur`'un sınıf
  doğrulaması bunun kanıtı.

---

## 8. Teslim öncesi kalan iş

1. 🔴 **Eğitim veri setinin kaynak/lisans beyanı** —
   `docs/lisans-analizi.md` Bölüm 2.1.1'de tablo hazır
2. 🔴 **`best.pt` + `docker compose ... gercek-model` uçtan uca çalıştırma**
3. 🟠 Mobil uygulamadan gerçek bir cihazda tek fotoğraf yükleme
4. 🟠 Demo videosu (03.09) — senaryo ve kontrol listesi
   `docs/demo-video.md`'de güncel
5. 🟡 Canlı demoyu sunumdan önce uyandırma
