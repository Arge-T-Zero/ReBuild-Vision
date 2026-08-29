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

On sınıf, tek doğruluk kaynağı [`siniflar.json`](siniflar.json) dosyasıdır;
sınıf adları kodda elle yazılmaz. Tanım ve gerekçe:
[`docs/siniflar.md`](docs/siniflar.md).

`konteyner` (skip bin) bir **malzeme değildir** — miktar hesabına ve
Malzeme Kaynak Haritası'na girmez.

**Kapsanmayan gruplar:** eğitim verisinde **cam** ve **seramik** sınıfı
bulunmamaktadır; **tuğla** ayrı bir sınıf olarak ayrılmaz. Model bu grupları
tanımaz ve bir sınıfın yokluğu "o malzeme sahada yok" anlamına gelecek
biçimde gösterilmez.

---

## Model durumu

⏳ **Model henüz eğitilmemiştir.** Bu nedenle precision, recall, F1 veya mAP
sonucu **beyan edilmemektedir.** Ölçülmemiş hiçbir sayı arayüze, bu dosyaya
veya sunuma girmez. Bkz. [`results/model-metrikleri.md`](results/model-metrikleri.md).

Geliştirme sırasında `model-mock` sahte servisi kullanılır. Sahte servis
etkinken arayüzde kalıcı bir **"SAHTE MODEL SERVİSİ"** rozeti gösterilir —
demo sırasında yanlışlıkla "gerçek model çalışıyor" izlenimi verilmez.

---

## Lisans

⚠️ Proje lisansı **henüz belirlenmemiştir.** Ultralytics YOLO11'in AGPL-3.0
lisansı ile şartname Madde 5.5'in ("kullanım hakları ve sahipliği Kuruma
bedelsiz olarak devredilecektir") arasındaki gerilim çözülmeden bir lisans
metni yazılmayacaktır. Ayrıntı: [`LICENSE`](LICENSE) ve
[`docs/lisans-analizi.md`](docs/lisans-analizi.md).

Kullanılan tüm üçüncü taraf bileşenlerin lisansları
[`docs/lisans-analizi.md`](docs/lisans-analizi.md) Bölüm 2'de eksiksiz
listelenmiştir.

---

## Veri politikası

Bakanlık tarafından sağlanan veriler **asla** versiyon kontrolüne girmez ve
hiçbir bulut servisine gönderilmez (şartname Madde 9.1 ve 10.5). Demo
ortamında yalnızca anonimleştirilmiş/sentetik veri kullanılır (Madde 10.7).
Bkz. [`docs/veri-politikasi.md`](docs/veri-politikasi.md) ve
[`data/bakanlik/UYARI.md`](data/bakanlik/UYARI.md).

---

## Atıf

Eğitim veri seti:

> Sirimewan, D. & Arashpour, M. *A benchmark dataset for class-wise
> segmentation of construction and demolition waste in cluttered
> environments.* Scientific Data (2025).
> https://doi.org/10.1038/s41597-025-05243-x — CC0 1.0

Harita altlığı: © OpenStreetMap katkıcıları (ODbL 1.0)
