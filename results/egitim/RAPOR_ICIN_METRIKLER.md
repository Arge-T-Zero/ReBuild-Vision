# ReBuild Vision — Eğitim Sonuçları (rapor için ham veri)

- Üretim tarihi: 01.09.2026 10:12
- Model: Ultralytics YOLO11m (AGPL-3.0), girdi çözünürlüğü 640x640
- Optimizer: AdamW, lr0=0.001, batch=16, seed=0

## Veri seti

- Toplam görüntü: **2765**
- Toplam etiketli kutu: **9348**
- Sınıflar (5): ahsap, beton_tugla, cam, metal, seramik

  - train: 2184 görüntü / 7265 kutu
  - valid: 384 görüntü / 1407 kutu
  - test: 197 görüntü / 676 kutu

- Eğitim süresi: **2.025 saat** (hedef 150 epoch, patience=30)

## VAL sonuçları

| sinif        |   precision |   recall |   mAP50 |   mAP50_95 |
|:-------------|------------:|---------:|--------:|-----------:|
| ahsap        |      0.4359 |   0.4553 |  0.4127 |     0.2681 |
| beton_tugla  |      0.4715 |   0.4367 |  0.4092 |     0.3072 |
| cam          |      0.7896 |   0.6848 |  0.7035 |     0.4638 |
| metal        |      0.4953 |   0.3482 |  0.3848 |     0.2782 |
| seramik      |      0.4669 |   0.3402 |  0.3019 |     0.2274 |
| TÜM SINIFLAR |      0.5318 |   0.453  |  0.4424 |     0.3089 |

## TEST sonuçları

| sinif        |   precision |   recall |   mAP50 |   mAP50_95 |
|:-------------|------------:|---------:|--------:|-----------:|
| ahsap        |      0.3887 |   0.4143 |  0.3607 |     0.2549 |
| beton_tugla  |      0.5818 |   0.5758 |  0.6268 |     0.4685 |
| cam          |      0.7928 |   0.6545 |  0.7257 |     0.4952 |
| metal        |      0.4477 |   0.3241 |  0.366  |     0.2779 |
| seramik      |      0.229  |   0.119  |  0.0877 |     0.0699 |
| TÜM SINIFLAR |      0.488  |   0.4176 |  0.4334 |     0.3132 |

## Kullanılacak görseller

- `rapor_ciktilari/gorseller/` — karışıklık matrisi, PR/F1 eğrileri, val batch tahminleri
- `rapor_ciktilari/egitim_egrileri.png` — loss/mAP eğrileri
- `rapor_ciktilari/sinif_dagilimi.png` — sınıf dengesizliği görseli
- `rapor_ciktilari/tahmin_ornekleri/` — test seti örnek çıkarımları
