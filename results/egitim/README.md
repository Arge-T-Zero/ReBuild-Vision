# Eğitim çıktıları (ham)

Bu klasör, 01.09.2026 tarihli eğitim koşusunun **ham çıktılarıdır**.
Yorum eklenmemiştir; `results/model-metrikleri.md` bu dosyalara dayanarak
doldurulacaktır.

## Sınıf listesi — uyuşmazlık ÇÖZÜLDÜ (02.09.2026)

Buradaki bütün metrikler **5 sınıflı** bir veri setiyle üretilmiştir:

    ahsap, beton_tugla, cam, metal, seramik

Bu çıktılar depoya girdiğinde `siniflar.json` hâlâ **10 sınıflıydı**
(CDW-Seg listesi) ve `cam` ile `seramik`'i açıkça "kapsanmayan grup"
sayıyordu. Sıra da kaymıştı: id 0 modelde `ahsap`, depoda `beton`
demekti — yani bu ağırlıkla çalışan servis **her tespiti yanlış adla**
döndürürdü ve hata hiçbir yerde görünmezdi.

`tests/test_sinif_tanimlari.py` içindeki
`test_data_yaml_sinif_sirasi_siniflar_json_ile_ayni` bunu yakalamak için
yazılmıştı ve bir süre **bilerek kırmızı** bırakıldı.

**02.09.2026'da `siniflar.json` eğitilen modele çekildi** (`docs/karar-kaydi.md`
**K-021**); `katsayilar.json`, renk paleti, belgeler ve testler aynı
commit'te güncellendi. Test artık yeşildir ve iki dosyayı birbirine
bağlı tutar. Buradaki metrikler `results/model-metrikleri.md`'ye
taşınmıştır.

⚠️ **Kalan eksik lisanstır, sınıf değil:** veri setinin kaynak ve lisans
beyanı hâlâ yazılı değildir — `docs/lisans-analizi.md` Bölüm 2.1.1.

Veri setinin künyesi: `veri_seti_kunyesi.json`,
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
