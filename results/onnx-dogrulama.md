# ONNX çalışma zamanı — ölçüm ve eşdeğerlik doğrulaması

**Tarih:** 06.09.2026
**Ağırlık:** `best.pt` (YOLO11s, epoch 142, 5 sınıf) → `best.onnx`
**Soru:** Canlı demo gerçek modeli çalıştırabilir mi, ve çalıştırırsa
`results/model-metrikleri.md`'deki sayılar hâlâ geçerli mi?

> Bu belgedeki her satır çalıştırılarak elde edilmiştir. Sayılar
> `tests/test_onnx_esdegerlik.py` ile yeniden üretilebilir.

---

## 1. Sorun: canlı demo gerçek modeli çalıştıramıyordu

`render.yaml` bugüne kadar **sahte** model servisini dağıtıyordu ve
arayüzde her ekranda kalıcı **"SAHTE MODEL SERVİSİ"** bandı görünüyordu.

Gerekçe belgede "torch tek başına diskte 1,2 GB" olarak yazılıydı. Disk
doğru ölçü değil; sınırlayan **bellek**. Ölçüldü:

| Aşama | torch + ultralytics | ONNX Runtime |
|---|---:|---:|
| `import` sonrası | 531,8 MB | 47,1 MB |
| ağırlık yüklendikten sonra | 577,4 MB | 141,7 MB |
| 1. çıkarımdan sonra | 790,6 MB | 214,4 MB |
| **tepe (birkaç çıkarım sonrası)** | **809,4 MB** | **280,9 MB** |
| ilk çıkarım süresi | 15.192 ms | 100 ms |
| sanal ortam boyutu | 5,4 GB | 191 MB |

**Render ücretsiz katmanı: 512 MB RAM.**
torch yolu sığmıyor (810 MB), ONNX yolu sığıyor (281 MB).

Canlı sunucuyla aynı bağımlılık listesiyle (`requirements-onnx.txt`,
sürümler sabit) ayağa kaldırılan gerçek uvicorn sürecinde ölçülen
yerleşik bellek: **283,7 MB**.

---

## 2. "Aynı model mi?" — üç ayrı doğrulama

Bellek kazancı, sonuç değişiyorsa bir işe yaramaz: o hâlde canlıda
ölçülmemiş **ikinci bir model** çalışıyor olurdu ve
`results/model-metrikleri.md`'deki mAP değerleri onu tarif etmezdi.

### 2.1 Ham ağ çıktısı

Aynı ön işlenmiş tensör iki yola da verildi; çıktı tensörleri
karşılaştırıldı (`(1, 9, 8400)`).

| Görüntü | maks mutlak fark | ortalama | bağıl |
|---|---:|---:|---:|
| og-kapak-1.jpg | 1,587e-03 | 1,638e-05 | 2,48e-06 |
| og-kapak-2.jpg | 2,472e-03 | 1,654e-05 | 3,88e-06 |
| og-kapak-3.jpg | 1,953e-03 | 1,639e-05 | 3,04e-06 |
| og-kapak.jpg | 1,923e-03 | 1,616e-05 | 3,02e-06 |
| labels.jpg | 1,007e-03 | 1,067e-05 | 1,58e-06 |

Bağıl fark ~3e-6: float32 birikim gürültüsü. Aynı işlev.

### 2.2 Ön işleme — birebir aynı

`tests/test_onnx_esdegerlik.py::test_on_isleme_ultralytics_ile_birebir_ayni`
ultralytics'in **kendi** `LetterBox(auto=True, stride=32)` sınıfıyla
karşılaştırır: **maks fark 0,0** (`np.array_equal`).

⚠️ Bu test bir kez gerçekten kırmızıydı ve iki tuzak ortaya çıkardı:

1. **Ölçekleme OpenCV `INTER_LINEAR` ile yapılmalı, Pillow `BILINEAR`
   ile değil.** Pillow küçültürken kenar yumuşatma uygular. Piksel farkı
   0,384'e çıkıyordu ve güven skorları **0,5041 ↔ 0,9163** gibi
   ayrışıyordu — sessizce başka bir model.
2. **Dolgu kareye değil, `stride` katına yapılır.** `predict()`
   görüntüyü 640×640'a tamamlamaz; uzun kenarı 640 yapıp her kenarı
   32'nin katına yuvarlar (1200×630 → **640×352**). Bu yüzden ONNX
   `dynamic=True` dışa aktarıldı.

### 2.3 Uçtan uca tespitler

24 görüntüde (`web/public/gorseller/*.jpg` + `results/egitim/gorseller/*`)
`predict()` ile ONNX yolu karşılaştırıldı — **ham görüntüden** başlayarak,
her iki taraf kendi ön işlemesiyle:

```
24/24 goruntude BIREBIR ayni (sinif ayni, guven <1e-4, kutu <0.05 px)
```

Gözlenen en büyük güven farkı: **1,52e-06**.

---

## 3. Sınıf sırası denetimi ONNX yolunda da çalışıyor

K-021'in tekrarını engelleyen açılış denetimi (`model-service/app.py`)
ağırlığın kendi `names` sözlüğüyle `siniflar.json`'u karşılaştırır.
`.onnx` dosyası bu sözlüğü meta verisinde taşır, yani denetim
zayıflamadı. Doğrulandı: `siniflar.json`'da `seramik` ve `tugla`
bilerek yer değiştirildi →

```
durum            : agirlik_yok
agirlik_yuklendi : false
hata             : SINIF SIRASI UYUŞMUYOR — servis çalışmayı reddetti.
                     id 3: siniflar.json='tugla'   ağırlık='seramik'
                     id 4: siniflar.json='seramik' ağırlık='tugla'
/predict         : HTTP 503
```

---

## 4. Lisans — ne değişti, ne DEĞİŞMEDİ

**Değişen:** canlı imajda `ultralytics` kurulu değil. ONNX yolunun
çalışma zamanı bağımlılıkları: onnxruntime (MIT), NumPy (BSD-3),
OpenCV (Apache-2.0), FastAPI (MIT), Uvicorn (BSD-3), Pillow (MIT-CMU).

**DEĞİŞMEYEN:** ağırlık ultralytics ile eğitildi ve dışa aktarılan
`.onnx` dosyası kendi meta verisinde şunu taşır:

```
license = AGPL-3.0 License (https://ultralytics.com/license)
```

`/health` `model_license: "AGPL-3.0 (ultralytics)"` demeye devam eder ve
`docs/lisans-analizi.md` Bölüm 3 olduğu gibi geçerlidir. ONNX'e geçmek
bir lisans kaçışı değildir; **bellek** çözümüdür.

---

## 5. Yayımlanan dosya ve tekrar üretilebilirlik

`model-v2` yayınına yüklenen dosya:

| | |
|---|---|
| ad | `best.onnx` |
| boyut | 38.052.133 bayt |
| sha256 | `8955d9ca9414f499357b7706e9d581a3e7efe099866f775032b7112f7866e8ea` |
| üreten | GitHub Actions — *ONNX dışa aktarımı* (koşu #1) |
| kaynak | `best.pt`, sha256 `468cf535a4e26977…` |

⚠️ **Dışa aktarım bayt bayt tekrar üretilebilir DEĞİLDİR.** Ultralytics
üretilen dosyanın meta verisine dışa aktarım zamanını (`date`) yazar;
`onnxslim`/`onnx` sürüm farkları da grafı biraz değiştirebilir. Aynı
`best.pt`den bu ortamda üretilen dosya 38.385.572 bayt ve farklı bir
sha256 taşıyordu — **işlevsel olarak aynı, baytça farklı.**

Bu yüzden güvence checksum'a değil **teste** bağlandı: dışa aktarım işi
`tests/test_onnx_esdegerlik.py`'yi kendi ürettiği dosya üzerinde
çalıştırır ve **yalnızca geçerse** yayına yükler. Yukarıdaki sha256
o koşuda doğrulanmış dosyaya aittir.

---

## 6. İmaj — CI'da derlendi ve ÇALIŞTIRILDI

`docker build` **bu ortamda** çalıştırılamıyor; ağ politikası Docker
Hub'ı engelliyor:

```
production.cloudfront.docker.com … Forbidden
```

Bu boşluk açık bırakılmadı: doğrulama GitHub koşucusuna taşındı
(`.github/workflows/imaj.yml`, koşu #1 — 06.09.2026). İmaj gerçekten
derlendi, **Render ücretsiz katmanının sınırı olan 512 MB bellekle**
kaldırıldı ve uç noktaları çağrıldı.

| Ölçüm | Sonuç |
|---|---|
| İmaj boyutu | 557 MB |
| Konteyner belleği (512 MB sınırıyla) | **192,9 MiB — sınırın %37,7'si** |
| Ağırlığın yayından indirilmesi | ✅ derleme sırasında başarılı |
| `/health` | `sahte: false` · `agirlik_yuklendi: true` · `calisma_zamani: onnx` · `sinif_sayisi: 5` |
| `/predict` (og-kapak-1.jpg) | 3 tespit — `cam 0,5858` · `ahsap 0,3715` · `cam 0,3064` |

Son satır önemli: bu değerler işin içine **sabit yazılmıştır**. Canlı
imaj bu görüntüye başka bir cevap verirse iş kırmızıya döner. Yani
"aynı model" iddiası her imaj derlemesinde yeniden sınanır.

Eksik bir sistem kütüphanesi de artık çalışma zamanında değil derleme
zamanında yakalanır: `opencv-python-headless` tekerleği bağımlılıklarının
hepsini taşımıyor — `libxcb1`, `libxau6`, `libxdmcp6`, `libbsd0`,
`libmd0` sistemden gelir ("headless" adına rağmen X kütüphaneleri
bağlanır) ve `python:3.11-slim`de yokturlar. Dockerfile bunları kurar ve
`model-service/dogrula_kurulum.py` içe aktarmaları, ağırlığı ve sınıf
sırasını derleme sırasında sınar.

Ağırlık indirilemezse **uydurma üretilmez**: `agirlik_yuklendi: false`,
`/predict` 503 ve arayüz sahte model bandını geri getirir.

---

## 7. Canlıda MODEL SERVİSİ doğrulandı — 06.09.2026

`https://rebuild-vision-model.onrender.com/health` çıktısı:

```json
{"durum":"calisiyor","sahte":false,"agirlik_yuklendi":true,"model":"best",
 "calisma_zamani":"onnx","model_license":"AGPL-3.0 (ultralytics)",
 "sinif_sayisi":5,"review_threshold":0.5}
```

Render ücretsiz katmanında **gerçek model çalışıyor**: ağırlık yüklendi,
çalışma zamanı ONNX, beş sınıf. `sahte: false` olduğu için arayüzdeki
kalıcı "SAHTE MODEL SERVİSİ" bandı canlı demoda **artık görünmüyor**.

Bu belgenin 1. bölümündeki sorun tanımı böylece kapandı: canlı demo
02.09–06.09 arasında sahte servisle çalışıyordu, bugünden itibaren
takımın eğittiği modelle çalışıyor.

⚠️ **BU SATIRIN KAPSAMI DAR — ilk yazıldığında fazla geniş anlaşıldı.**

`/health` YALNIZCA model servisinin ayakta ve ağırlığın yüklü olduğunu
söyler. API'nin veri tabanında ne olduğu, arayüzde ne göründüğü
hakkında hiçbir şey söylemez. Bu belge ilk yazıldığında başlığı
"CANLIDA doğrulandı" idi; o ifade, arayüzün de doğrulandığı izlenimini
veriyordu. Vermiyordu.

Nitekim aynı gün arayüz açıldığında canlı veri tabanının 30.08.2026'dan
kalma olduğu ve artık var olmayan v1 sınıflarını (`sert_plastik`,
`karton`, `konteyner`…) gösterdiği görüldü. Model servisi doğruydu,
gösterilen veri değildi. Ayrıntı ve düzeltme: `CHANGELOG.md`
06.09.2026 girdisi.

**Ders:** bir uç noktanın yeşil dönmesi, sistemin doğrulandığı anlamına
gelmez. Arayüz ekranları açılmadan "canlıda doğrulandı" yazılmamalıdır.

> ⚠️ Ücretsiz katman 15 dakika hareketsizlikten sonra servisi uyutur;
> ilk istek ~50 saniye sürer. **Sunum ve demo öncesi adresi bir kez açıp
> uyandırın** (docs/yayin.md 2.4).
