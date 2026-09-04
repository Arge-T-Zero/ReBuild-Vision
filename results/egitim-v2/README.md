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

## `model-service/data.yaml` ne olacak

Deponun kendi kopyası (`model-service/data.yaml`) hâlâ **v1** sırasını
taşır ve öyle kalmalıdır — çünkü teslim edilen sistem v1 ile çalışıyor.

Bu dosya tek başına değiştirilemez: `siniflar.json` ile **teste
bağlıdır** (`tests/test_sinif_tanimlari.py::
test_data_yaml_sinif_sirasi_siniflar_json_ile_ayni`). Bu bağ K-021'den
sonra bilerek kuruldu; birini değiştirip diğerini unutmak takımı kırmızıya
düşürür. 03.09'da eklenen ağırlık denetimiyle birlikte artık **üç kilit**
var:

| Kilit | Neyi neye bağlar | Nerede |
|---|---|---|
| 1 | `data.yaml` ↔ `siniflar.json` | test |
| 2 | ağırlığın `names`'i ↔ `siniflar.json` | `model-service/app.py`, çalışma anı |
| 3 | `katsayilar.json` + renkler ↔ `siniflar.json` | test |

Bu yüzden dört dosya **tek commit'te birlikte** göç eder ve **ağırlık
gelmeden göç edemez**: siniflar.json v2'ye çevrilirse 2. kilit mevcut
v1 ağırlığını reddeder ve çalışan teslim bozulur.

Yeni sürüm bu klasörde (`results/egitim-v2/data.yaml`) olduğu gibi
saklanıyor; hiçbir şey kaybolmadı.

**Göç sırasında korunacak:** yeni `data.yaml` bir `roboflow:` bloğu
taşıyor — çalışma alanı, proje, sürüm, **lisans (CC BY 4.0)** ve veri
seti adresi. Bu, Madde 5.2 ve 10.4 için makinece okunabilir bir kaynak
kaydıdır. Deponun kopyasına alınırken bu blok **kırpılmamalıdır**; hatta
`docs/lisans-analizi.md` 2.1.2'deki beyanla ayrışmasın diye
`test_lisans_beyani.py` biçiminde bir teste bağlanması yerinde olur.

## Renk paleti — göçe hazır, ÖLÇÜLDÜ (uygulanmadı)

v2'de `metal` kalkıyor, `beton_tugla` ikiye ayrılıyor: iki renk yeniden
seçilmeli. Ölçüm K-022'deki ölçütle yapıldı — *bütün ikililerin* en
kötüsü, normal görüş + protanopi + dötanopi + tritanopi benzetimi
birlikte. Betik artık depoda: `scripts/renk_olc.py`.

| | v1 (teslimdeki) | v2 (öneri) |
|---|---|---|
| ahsap | `#d95926` | `#d95926` (aynı) |
| beton / beton_tugla | `#6b7280` | `#6b7280` (aynı) |
| cam | `#008300` | `#008300` (aynı) |
| metal | `#3987e5` | — (sınıf kalktı) |
| seramik | `#c98500` | **`#d4a017`** |
| tugla | — | **`#8c1d18`** |
| **bütün-ikili en kötü ΔE** | **8,95** | **15,45** |
| en düşük etiket kontrastı | 4,83 | 4,83 (AA ✅) |

**Neden `seramik` de değişti:** v1'in en zayıf ikilisi `cam ↔ seramik`
(protanopi, 8,95) idi ve tuğlaya hangi rengi verirsek verelim tavanı o
belirliyordu — sekiz aday da aynı 8,95'i verdi. Seramiği bir tık açmak
(`#c98500` → `#d4a017`) tabanı **8,95'ten 15,45'e** çıkarıyor. Yani göç
zorunluluğu, paletin v1'deki bilinen zayıflığını kapatma fırsatına
dönüştü.

**Anlamsal tutarlılık korunuyor:** turuncu ahşap, gri beton, koyu yeşil
cam, altın seramik, koyu kırmızı tuğla.

⚠️ **Bu sayı K-022'deki 6,79 ile karşılaştırılamaz.** `scripts/renk_olc.py`
aynı paleti **8,95** ölçüyor; yani benzetim matrisi ya da ΔE formülü
(CIE76 / CIEDE2000) K-022'de kullanılandan farklı. Kontrast tarafı ise
birebir aynı çıkıyor (4,83). Yukarıdaki 8,95 → 15,45 karşılaştırması
geçerlidir çünkü **iki palet de aynı kodla** ölçülmüştür; mutlak değeri
eski kayıtla eşitlemeye çalışmak yanlış olur. Göç yapılırsa K-022'ye bu
not düşülmeli.

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
