# model-v2 — eğitim kaydı

**⚠️ BU MODEL TESLİMDE DEĞİLDİR.** 03.09.2026 itibarıyla ağırlık
(`best.pt`) depoya ya da bir GitHub sürümüne konmamıştır; çalışan sistem
hâlâ `model-v1` kullanmaktadır. Bu klasör, eğitimin **ham çıktısını**
kayıt altına alır — sistemin beyan ettiği metrikler değildir.

## Ne ölçüldü, ne ölçülmedi

| | Durum |
|---|---|
| Doğrulama (val) metrikleri | ✅ `results.csv` — epoch başına |
| **Test kümesi metrikleri** | ❌ **ölçülmedi.** `split=test` ile ayrı bir koşu gerekir |
| Sınıf bazlı sayısal tablo | ❌ `results.csv` yalnızca genel ortalamayı taşır |
| Karışıklık matrisi / F1-P eğrileri | görsel olarak var (varsayılan: val) |

Depo bugüne kadar **test** mAP50'yi beyan ediyor (`results/model-metrikleri.md`).
Buradaki sayılar **val**'dir; ikisi karıştırılırsa beyan yanlış olur.

## Okunan değerler

Son epoch (150) · val:

| Ölçüt | Değer |
|---|---|
| precision | 0,9185 |
| recall | 0,8296 |
| mAP50 | 0,8855 |
| mAP50-95 | 0,6475 |

Eğitim boyunca en iyi: mAP50 **0,8900** (epoch 109) · mAP50-95 **0,6497**
(epoch 142). Toplam 150 epoch, ~91 dakika.

## v1 ile karşılaştırma — dikkatli okuyun

v1 için depoda **test** mAP50 = 0,4334 yazılıdır; v1'in **val** mAP50'si
0,4424'tür. Karşılaştırma val↔val yapılmalıdır:

| | v1 (val) | v2 (val) |
|---|---|---|
| mAP50 | 0,4424 | 0,8855 |

İki modelin **veri setleri farklıdır** (v1: takımın topladığı görüntüler;
v2: üç kamuya açık CC BY 4.0 veri setinin birleşimi). Yani bu, aynı veri
üzerinde bir mimari iyileştirmesi değildir — büyük ölçüde daha temiz ve
daha tutarlı etiketli bir veri setinin sonucudur. Sunumda böyle
anlatılmalıdır.

## Sınıf listesi DEĞİŞTİ

`data.yaml`: `['ahsap', 'beton', 'cam', 'seramik', 'tugla']`

| id | v1 | v2 |
|---|---|---|
| 0 | ahsap | ahsap |
| 1 | beton_tugla | **beton** |
| 2 | cam | cam |
| 3 | **metal** | **seramik** |
| 4 | seramik | **tugla** |

`metal` kalktı, `beton_tugla` ikiye ayrıldı. **id 1, 3 ve 4'ün anlamı
değişti.** Ağırlık `siniflar.json` güncellenmeden konursa her tespit
sessizce yanlış adla kaydedilirdi; bunu artık `model-service`
başlangıçta yakalayıp çalışmayı reddediyor (bkz.
`tests/test_model_servisi_sozlesmesi.py`).

## Miktar katsayılarına etkisi

Bugün kaynaklı katsayısı olan iki sınıf `ahsap` ve `metal`'dir. v2'de
**metal yoktur** — yani kaynaklı katsayı sayısı 2'den **1'e** düşer.
`beton` ve `tugla` ayrı sınıf olur ve ikisinin de kaynağı yoktur.
Bu, "ölçüm + kaynaklı katsayı → miktar" zincirinin v2'de daha dar bir
malzeme kümesinde çalışacağı anlamına gelir ve
`docs/cevresel-etki.md` ile `katsayilar.json` buna göre güncellenmelidir.

## Veri seti

Üç CC BY 4.0 kaynağın birleşimi; kaynaklar, lisanslar ve atıf metni:
`docs/lisans-analizi.md` **Bölüm 2.1.2**.
