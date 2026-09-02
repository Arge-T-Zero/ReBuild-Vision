# model-service — YOLO11 çıkarım servisi

⚠️ **AGPL-3.0 sınırı bu dizindedir.**

`ultralytics` AGPL-3.0 lisanslıdır. `api/` bu paketi **hiçbir koşulda**
import etmez; model ayrı bir süreçte çalışır ve yalnızca HTTP ile
çağrılır. Sınır bir yorumla değil, `tests/test_agpl_siniri.py`
içindeki beş testle korunur.

Gerekçe: [`docs/lisans-analizi.md`](../docs/lisans-analizi.md) Bölüm 3.4.

```
web/  ──HTTP──>  api/  ──HTTP──>  model-service/   (ultralytics, AGPL-3.0)
                   │
                   └──HTTP──>  model-mock/         (kendi kodumuz, AGPL değil)
```

## Ağırlık nereden gelir

Eğitim Kaggle'da yapılır; çıktı `best.pt` dosyasıdır. Ağırlıklar
**depoya girmez** (büyük ikili dosyalar git geçmişini şişirir ve her
sürüm yeni bir kopya bırakır).

```bash
# varsayılan konum
cp best.pt model-service/agirliklar/

# ya da yolu ortam değişkeniyle ver
export MODEL_AGIRLIK=/bir/yer/best.pt
```

### ⚠️ Sınıf sırası eşleşmek zorundadır

Eğitimdeki `data.yaml` içindeki `names:` listesi
[`siniflar.json`](../siniflar.json) ile **birebir aynı sırada** olmalıdır:

| id | ad | görünen ad |
|---|---|---|
| 0 | ahsap | Ahşap |
| 1 | beton_tugla | Beton / tuğla |
| 2 | cam | Cam |
| 3 | metal | Metal |
| 4 | seramik | Seramik |

Bu liste 02.09.2026'da **10 sınıftan 5'e indi**: model CDW-Seg ile değil,
takımın kendi topladığı veri setiyle eğitildi. Sıra `data.yaml`'dan gelir;
`tests/test_sinif_tanimlari.py` ikisinin ayrışmasını CI'da yakalar.

Sıra kayarsa model "ahşap" derken arayüz "metal" gösterir. Servis, sınıf
adını modelin kendi `names` sözlüğünden **almaz** — `siniflar.json`
tektir. Model, listede olmayan bir id dönerse istek 500 ile reddedilir
ve gerekçe yazılır; sessizce geçilmez.

## Ağırlık yoksa ne olur

Servis **sahte veri üretmez** ve sessizce `model-mock`'a düşmez:

| Uç nokta | Ağırlık yokken |
|---|---|
| `/health` | `agirlik_yuklendi: false` + `hata` alanında neden |
| `/predict` | **503** |

Bu bilinçlidir. Bu projede en pahalı arıza, uydurma bir çıktının gerçek
sanılmasıdır (ana talimat Bölüm 9.5). Boş liste dönmek de kabul
edilemez — çağıran taraf bunu "görüntüde malzeme yok" diye okur.

## Çalıştırma

```bash
python -m venv .venv
.venv/bin/pip install -r model-service/requirements.txt
MODEL_AGIRLIK=/yol/best.pt .venv/bin/uvicorn app:app --app-dir model-service --port 8090
```

`api/` tarafında tek değişiklik:

```bash
MODEL_SERVICE_URL=http://localhost:8090
```

## İnceleme eşiği

`INCELEME_ESIGI` (varsayılan `0.50`), altındaki tespitleri uzman
incelemesine yönlendirir.

**Bu ölçülmüş bir değer değildir** — ama sebebi değişti. Model
01.09.2026'da eğitildi ve ölçüldü
([`results/model-metrikleri.md`](../results/model-metrikleri.md)).

Eşik yine de türetilemiyor: doğru seçmek için precision ve recall'un
**güvene göre** değişimi gerekir, elimizdeki ölçüm her sınıf için tek bir
çalışma noktası veriyor. Eğriler yalnızca görsel olarak var
(`results/egitim/gorseller/*_BoxF1_curve.png`) ve bir görselden sayı
okumak ölçüm değildir. 0,50 bir mühendislik varsayımıdır ve kod
değişikliği gerekmesin diye ortam değişkeniyle değiştirilebilir
tutuluyor.

## Sözleşme

Bu servis `model-mock/app.py` ile **birebir aynı** yanıt biçimini üretir;
`api/` ikisini ayırt etmez. Sözleşme
[`tests/test_model_servisi_sozlesmesi.py`](../tests/test_model_servisi_sozlesmesi.py)
ile doğrulanır — alan adları ayrışırsa arayüz sessizce bozulurdu.

Tek fark, olması gereken farktır: `/health` → `sahte: false`.
