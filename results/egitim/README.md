# Eğitim çıktıları (ham)

Bu klasör, 01.09.2026 tarihli eğitim koşusunun **ham çıktılarıdır**.
Yorum eklenmemiştir; `results/model-metrikleri.md` bu dosyalara dayanarak
doldurulacaktır.

## ⚠️ Sınıf listesi `siniflar.json` ile UYUŞMUYOR

Buradaki bütün metrikler **5 sınıflı** bir veri setiyle üretilmiştir:

    ahsap, beton_tugla, cam, metal, seramik

Deponun sınıf doğruluk kaynağı `siniflar.json` ise **10 sınıflıdır**
(CDW-Seg: beton, dolgu_toprak, ahsap, sert_plastik, yumusak_plastik,
metal, tekstil, karton, alcipan, konteyner) ve `cam` ile `seramik`'i
açıkça "kapsanmayan grup" sayar.

Yani bu sayılar CDW-Seg sonuçları **değildir** ve `siniflar.json`'daki
adlarla eşleştirilemez. `model-service/app.py` sınıf adını id üzerinden
`siniflar.json`'dan okuduğu için, bu ağırlıkla çalışan servis her
tespiti yanlış adla döndürür (id 0 = model'de `ahsap`, depoda `beton`).

Uyuşmazlık `tests/test_sinif_tanimlari.py` içindeki
`test_data_yaml_sinif_sirasi_siniflar_json_ile_ayni` ile yakalanır ve
**test bilerek kırmızıdır**. Çözülene kadar buradaki hiçbir metrik
rapora, arayüze veya sunuma taşınmamalıdır.

Veri setinin gerçek künyesi: `veri_seti_kunyesi.json`,
ön işleme kaydı: `on_isleme_kaydi.json`.

## İçerik

| Dosya | Nedir |
|---|---|
| `RAPOR_ICIN_METRIKLER.md` | Koşunun özeti, val/test tabloları |
| `metrikler.json`, `metrikler_sinif_bazli.{csv,md}` | Sınıf bazlı precision/recall/mAP |
| `results.csv` | Epoch epoch eğitim günlüğü |
| `args.yaml` | Ultralytics eğitim parametreleri (YOLO11m, 150 epoch hedefi, AdamW) |
| `egitim_suresi.json` | Süre ve durdurma bilgisi |
| `veri_seti_kunyesi.json` | Bölme, görüntü/kutu sayıları, sınıf dağılımı |
| `on_isleme_kaydi.json` | Sızıntı ve filigran nedeniyle silinen görüntüler |
| `egitim_egrileri.png`, `sinif_dagilimi.png` | Kayıp/mAP eğrileri, sınıf dengesizliği |
| `gorseller/` | Karışıklık matrisleri, PR/P/R/F1 eğrileri (val ve test) |

Depoya alınmayanlar: `train_batch*`, `val_batch*` önizlemeleri ve
`tahmin_ornekleri/` (~18 MB, birbirinin benzeri kareler). Bunlar model
ağırlığıyla birlikte GitHub Releases'e eklenecektir.
