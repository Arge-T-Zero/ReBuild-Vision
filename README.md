# ReBuild Vision

**Afet sonrası enkaz malzemelerinin görüntü tabanlı ön sınıflandırması ve
doğrulanabilir kaynak haritası**

**Takım:** Arge-T Zero · Başvuru ID 5387352 · Takım ID 1003428
**Yarışma:** TEKNOFEST 2026 Sıfır Atık & Döngüsel Ekonomi — Tema 3.1

---

## Bu sistemin yapmadıkları

Çoğu proje ne yaptığını anlatır. Bu sistemin ayırt edici yanı, **ne
yapmadığını da açıkça söylemesidir.** Aşağıdaki dört kural teslim edilmiş
ön değerlendirme raporunda taahhüt edilmiştir ve yazılımda **veri katmanında**
zorlanır — yalnızca arayüzde gizlenerek değil.

### 1. Ölçüm yoksa miktar üretilmez

Yeterli ölçüm bulunmayan alanlar için tonaj tahmini **oluşturulmaz.**
Miktar alanı boş kalır; varsayılan değer, tahmini değer, "≈0" veya
"hesaplanıyor" yazılmaz. Miktar hesaplandığında ise **tek bir kesin değer
değil**, belirsizlik aralığı ve kullanılan yöntem birlikte gösterilir.

Veri tabanında `miktar_hesabi` tablosunda satır olmaması, miktarın sıfır
olduğu anlamına gelmez — **hesaplanmadığı** anlamına gelir.

### 2. Tehlikeli madde teşhisi yapılmaz

Asbest ve benzeri tehlikeli maddeler görüntü üzerinden teşhis edilmez.
Hiçbir tahmin, ikon, renk kodu, uyarı rozeti veya olasılık değeri
üretilmez. Yalnızca "uzman/laboratuvar incelemesine yönlendirildi" durumu
tutulur ve sonucu **model değil, insan girer**.

Analiz sonucu bulunmayan alan için **"güvenli" değerlendirmesi de
yapılmaz.** Yokluk, güvenlik anlamına gelmez.

### 3. Enkaz altı görülmez

Sistem yalnızca **görünür yüzeye** ilişkin ön değerlendirme yapar. Toplam
enkaz içeriği iddiası hiçbir yerde üretilmez. Bu ifade arayüzde yazılıdır.

### 4. Nihai kararı sistem vermez

Her model çıktısı **"ön tahmin"** etiketiyle görünür. Doğrulanmamış
kayıtlar miktar ve yönlendirme hesaplarına girmez. Nihai operasyon kararı
yetkili kurum ve uzmanlar tarafından verilir.

> Ölçülmüş bir sınır, ölçülmemiş bir iddiadan güçlüdür.
> Sistemin bilinen sınırları: [`results/bilinen-sinirlar.md`](results/bilinen-sinirlar.md)

---

## Mimari

```
web/            React 19 + Vite + TypeScript arayüzü
mobile/         Flutter saha uygulaması
api/            FastAPI backend + PostgreSQL/PostGIS
model-service/  YOLO11 çıkarım servisi — İZOLE (AGPL-3.0 sınırı)
model-mock/     Sahte model servisi — gerçek HTTP uç noktası
scripts/        Kurulum, maskeleme, demo verisi
docs/           Teslim dokümanları
results/        Ölçüm çıktıları ve bilinen sınırlar
```

`api/` **hiçbir koşulda** `ultralytics` paketini import etmez. Model yalnızca
ayrı bir süreçte çalışır ve HTTP ile çağrılır. Gerekçe:
[`docs/lisans-analizi.md`](docs/lisans-analizi.md) Bölüm 3.4.

---

## Canlı demo

**https://re-build-vision.vercel.app**

Demo hesapları ve parolaları: [`docs/kurulum.md`](docs/kurulum.md) Bölüm 8.
Yayın mimarisi ve kurulum adımları: [`docs/yayin.md`](docs/yayin.md).

> Canlı ortamda **yalnızca sentetik demo verisi** bulunur. Bakanlık verisi
> ve maskelenmemiş saha fotoğrafı buraya asla yüklenmez (Madde 9.1, 10.5).
>
> Canlı bağlantı, Madde 10.3'ün yerine geçmez — jürinin bağımsız ortamda
> çalıştırması için `docker compose` paketi kullanılır.

---

## Kurulum

Ayrıntılı adımlar: [`docs/kurulum.md`](docs/kurulum.md)

### Docker ile (önerilen — başka bir şey kurmanız gerekmez)

```bash
docker compose -f docker/compose.yaml up --build
# Tek adres: http://localhost:8080
```

Şema göçü ve demo verisi açılışta otomatik çalışır. Giriş:
`uzman@demo.local` / `demo1234`.

29.08.2026'da uçtan uca doğrulandı (Colima + Docker 29.7.2, macOS /
Apple Silicon): dört servis ayağa kalktı, göç çalıştı, PostGIS 3.5
doğrulandı, arayüzden giriş yapıldı. Ayrıntı:
[`docker/README.md`](docker/README.md), karar
[`docs/karar-kaydi.md`](docs/karar-kaydi.md) K-019.

> **Apple Silicon:** `compose.yaml` içindeki `platform: linux/amd64`
> satırını silmeyin — resmî PostGIS imajının arm64 sürümü yayımlanmıyor.

### Yerel kurulum (geliştirme için)

```bash
cp .env.example .env
scripts/gelistirme.sh
```

| Servis | Adres |
|---|---|
| Web arayüzü | http://localhost:5173 |
| API | http://localhost:8000 (dokümantasyon: `/docs`) |
| Sahte model servisi | http://localhost:8090 |
| PostgreSQL + PostGIS | localhost:5433 |

---

## Malzeme sınıfları

**Beş sınıf:** `ahsap` · `beton` · `cam` · `seramik` · `tugla`

Tek doğruluk kaynağı [`siniflar.json`](siniflar.json) dosyasıdır; sınıf
adları kodda elle yazılmaz. Liste iki kez değişti: 02.09.2026'da 10'dan
5'e indi (**K-021**), 03.09.2026'da yeni modelle birlikte içeriği değişti
(**K-024**) — `metal` kalktı, `beton_tugla` `beton` ve `tugla` diye ikiye
ayrıldı. Tanım ve gerekçe: [`docs/siniflar.md`](docs/siniflar.md),
kararlar [`docs/karar-kaydi.md`](docs/karar-kaydi.md).

⚠️ **`metal` artık tanınmıyor.** v1'de sınıf vardı, v2'nin eğitim veri
setinde yok. Enkazdaki metal kayıt dışı kalır; bu bir kapsam daralmasıdır
ve gizlenmez.

Eğitimdeki sınıf **sırası** ile `siniflar.json` ayrışırsa arayüz yanlış
malzeme gösterir. Üç kilit birden vardır: `data.yaml` ↔ `siniflar.json`
testle (`tests/test_sinif_tanimlari.py`), **ağırlığın kendi `names`
sözlüğü ↔ `siniflar.json`** çalışma anında (`model-service/app.py` —
ayrışırsa servis çalışmayı reddeder), katsayılar ve renkler yine testle.

**Kapsanmayan gruplar:** model bu beşin dışındaki malzeme gruplarını
(dolgu/toprak, plastik, tekstil, karton, alçıpan) **tanımaz.** Bir sınıfın
çıktıda görünmemesi "o malzeme sahada yok" anlamına gelecek biçimde
gösterilmez.

---

## Model durumu

✅ **Model eğitildi ve ölçüldü** (03.09.2026, **YOLO11s**, 640 px, 150
epoch / ~91 dakika). Gönderilen ağırlık **epoch 142** checkpoint'idir;
Ultralytics `best`i fitness'a göre seçer, son epoch'a göre değil.

| Bölme | precision | recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| **val** | 0,9087 | 0,8316 | **0,8824** | 0,6497 |

⚠️ **Test kümesi ölçülmedi.** v1'de test ölçümü vardı (mAP50 0,4334);
v2 için `split=test` ile ayrı bir koşu yapılmadı. Elimizde yalnızca
eğitim sırasındaki val ölçümü var ve arayüz de bu yüzden "val" diyor —
val sayısını test diye beyan etmek yanlış beyan olurdu.

⚠️ **Ölçülmüş genelleme farkı.** v2, kendi val kümesinde 0,8824 alıyor
ama deponun üç **sentetik** demo görüntüsünde yalnızca 4 tespit üretiyor
(v1 aynı görüntülerde 14 üretiyordu). Sebep dağılım farkıdır: v2 gerçek
yıkım atığı fotoğraflarıyla eğitildi, demo görüntüleri ise yapay zekâ
üretimi geniş moloz sahneleri. Bu, sistemin neden hiçbir çıktıyı
kendiliğinden onaylamadığının somut kanıtıdır ve gizlenmez —
[`results/model-metrikleri.md`](results/model-metrikleri.md).

**Ağırlık nereden gelir:** [`model-v2`](https://github.com/Arge-T-Zero/ReBuild-Vision/releases/tag/model-v2) sürümünden indirilir
(18 MB; büyük ikili dosyalar depoya girmez).

```bash
curl -L -o model-service/agirliklar/best.pt \
  https://github.com/Arge-T-Zero/ReBuild-Vision/releases/download/model-v2/best.pt
```

sha256: `468cf535a4e26977…`

Ağırlık yokken servis **sahte veri üretmez**: `/predict` 503 döner.
Ayrıntı: [`model-service/README.md`](model-service/README.md).

Ağırlıksız geliştirme için `model-mock` sahte servisi kullanılır. Sahte
servis etkinken arayüzde kalıcı bir **"SAHTE MODEL SERVİSİ"** rozeti
gösterilir — demo sırasında yanlışlıkla "gerçek model çalışıyor" izlenimi
verilmez.

---

## Lisans

Proje **AGPL-3.0** ile lisanslanmıştır — bkz. [`LICENSE`](LICENSE).

Copyright (C) 2026 Takım Arge-T Zero

**Neden AGPL-3.0:** Ürün, AGPL-3.0 lisanslı Ultralytics YOLO11'i
kullanır. AGPL §13 ağ üzerinden hizmet sunmayı da kopyaleft tetikleyicisi
saydığı için, aynı programı oluşturan kodun izin verici bir lisansla
sunulması hukuken tutarsız olurdu.

Şartname **Madde 10.4** GPL/AGPL'li bileşenlerin kullanımını yasaklamaz,
**ayrıca beyan edilmesini** ister; bu beyan
[`docs/lisans-analizi.md`](docs/lisans-analizi.md) Bölüm 3'tedir. Karar
kaydı: `docs/karar-kaydi.md` **K-020**.

Kullanılan tüm üçüncü taraf bileşenlerin lisansları
[`docs/lisans-analizi.md`](docs/lisans-analizi.md) Bölüm 2'de eksiksiz
listelenmiştir.

---

## Şartname uyumu

Teslim paketinde istenen belgeler (Madde 10.3) ve beyan yükümlülükleri:

| Madde | Konu | Belge |
|---|---|---|
| **5.2** | **Veri seti kaynak beyanı** | ✅ üç kaynak, CC BY 4.0 — [`docs/lisans-analizi.md`](docs/lisans-analizi.md) Bölüm 2.1.2 |
| 5.5 | Ürünün Kuruma devri | [`docs/lisans-analizi.md`](docs/lisans-analizi.md) Bölüm 3.2 |
| 9.1 · 10.6 · 10.7 | Veri hakları, silme, KVKK | [`docs/veri-politikasi.md`](docs/veri-politikasi.md) |
| 9.2 | Üçüncü taraf hakları | [`docs/lisans-analizi.md`](docs/lisans-analizi.md) Bölüm 2.1.1 |
| 10.3 | Kurulum ve çalıştırılabilirlik | [`docs/kurulum.md`](docs/kurulum.md) · [`docs/kullanici-kilavuzu.md`](docs/kullanici-kilavuzu.md) · [`docker/`](docker/) |
| 10.3 · 10.4 | Kütüphane ve lisans listesi | [`docs/lisans-analizi.md`](docs/lisans-analizi.md) |
| 10.3 | Demo videosu | [`docs/demo-video.md`](docs/demo-video.md) |
| **10.5** | **Yapay zekâ beyanı** | [`docs/yapay-zeka-beyani.md`](docs/yapay-zeka-beyani.md) |
| 10.8 | Teknik mimari, veri modeli, ölçeklenebilirlik | [`docs/mimari.md`](docs/mimari.md) · [`docs/veri-modeli.md`](docs/veri-modeli.md) |
| 10.8 | Açık coğrafi standart | **OGC API - Features** → `/ogc` |
| **10.9** | **Çevresel etki doğrulama** | [`docs/cevresel-etki.md`](docs/cevresel-etki.md) |

> **Madde 5.2 nasıl kapandı:** 03.09.2026'da model, lisansı beyan
> edilmemiş bir veri setiyle eğitilmiş v1'den, üçü de CC BY 4.0 olan üç
> kamuya açık veri setiyle eğitilmiş **v2**'ye geçirildi. Atıf README'nin
> "Atıf" bölümünde ve `docs/lisans-analizi.md` 2.1.2'de yazılıdır.
> Kalan tek işlem: Mendeley kaydının lisans alanının gözle teyidi.

---

## Veri politikası

Bakanlık tarafından sağlanan veriler **asla** versiyon kontrolüne girmez ve
hiçbir bulut servisine gönderilmez (şartname Madde 9.1 ve 10.5). Demo
ortamında yalnızca anonimleştirilmiş/sentetik veri kullanılır (Madde 10.7).
Bkz. [`docs/veri-politikasi.md`](docs/veri-politikasi.md) ve
[`data/bakanlik/UYARI.md`](data/bakanlik/UYARI.md).

---

## Atıf

**Eğitim veri seti (v2):** üç kamuya açık veri setinin birleşimi
(Roboflow projesi `burak-alkan/newdetect-jvc1e` v4). **Üçü de CC BY 4.0.**

> Bu çalışmada kullanılan görüntü veri setleri CC BY 4.0 lisansı altında
> paylaşılmıştır:
>
> - Demetriou, D. ve ark. *Construction and Demolition Waste Object
>   Detection Dataset.* Mendeley Data.
>   <https://doi.org/10.17632/24d45pf8wm> — beton, tuğla, seramik
> - waste seg 2. *broken-glass kaggle Dataset.* Roboflow Universe.
>   <https://universe.roboflow.com/waste-seg-2/broken-glass-kaggle> — cam
> - asdasd. *Wood Dataset.* Roboflow Universe.
>   <https://universe.roboflow.com/asdasd-boz3q/wood-0nvcu> — yalnızca
>   `wood` sınıfı alınmıştır

CC BY 4.0 ticari kullanıma, değiştirmeye ve türetilmiş çalışmaya
(ince ayarlanmış model dahil) izin verir; **tek şart atıftır.**
Share-alike yoktur. Ayrıntı ve doğrulama notları:
[`docs/lisans-analizi.md`](docs/lisans-analizi.md) Bölüm **2.1.2**.

> ⚠️ Mendeley kaydının lisans alanı geliştirme ortamından **okunamadı**
> (ağ politikası engelliyor). Teslimden önce kayıt sayfası açılıp gözle
> teyit edilmelidir; atıfta fiilen indirilen **sürüm numarası** da
> yazılmalıdır.

**v1 veri seti (artık kullanılmıyor):** takımın kendi topladığı 5 sınıflı
set — lisans beyanı eksikti ve v2 geçişinin asıl sebeplerinden biri
buydu. Künye tarihî kayıt olarak duruyor:
[`results/egitim/veri_seti_kunyesi.json`](results/egitim/veri_seti_kunyesi.json).

Daha önce bu bölümde CDW-Seg (Sirimewan & Arashpour, *Scientific Data*
2025, CC0 1.0) veri setine atıf yapılıyordu. **O veri seti eğitimde
kullanılmamıştır**; atıf, kullanılmayan bir kaynağa kredi verdiği için
kaldırıldı. Değerlendirme kaydı
[`docs/lisans-analizi.md`](docs/lisans-analizi.md) Bölüm 2.7'de duruyor.

Harita altlığı: © OpenStreetMap katkıcıları (ODbL 1.0)
