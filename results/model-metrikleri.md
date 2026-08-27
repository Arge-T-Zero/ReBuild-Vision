# Model Metrikleri

> **Bu dosyaya ölçülmemiş hiçbir sayı yazılmaz.** *(Ana talimat Bölüm 7.4
> ve 14)*

**Son güncelleme:** 27.08.2026

---

## Durum: ⏳ HENÜZ ÖLÇÜLMEDİ

Malzeme sınıflandırma modeli proje kapsamındaki veri setiyle **henüz
eğitilmemiştir.** Bu nedenle bu dosyada precision, recall, F1 veya mAP
sonucu bulunmamaktadır.

Bu, teslim edilmiş ön değerlendirme raporunun Bölüm 7'sindeki tutumun
sürdürülmesidir:

> "Malzeme sınıflandırma modeli proje kapsamındaki özgün veri setiyle henüz
> eğitilmediğinden precision, recall, F1 veya mAP sonucu bulunmamaktadır.
> Bu nedenle raporda model doğruluğu, geri kazanım oranı, karbon tasarrufu
> veya ekonomik faydaya ilişkin gerçekleşmiş sonuç beyan edilmemektedir."

Sonuçlar geldiğinde bu bölüm silinecek ve aşağıdaki tablolar
doldurulacaktır. **Sonuç gelene kadar hiçbir yere tahmini sayı
yazılmayacaktır** — README'ye, arayüze veya sunuma da.

---

## Ölçüm yapıldığında doldurulacak

### Deney künyesi

| Alan | Değer |
|---|---|
| Model | *(YOLO11-? / girdi boyutu)* |
| Eğitim veri seti | CDW-Seg — DOI 10.6084/m9.figshare.28573229 |
| Bölme (train/val/test) | — |
| Görüntü sayısı | — |
| Nesne sayısı | — |
| Epoch / durdurma ölçütü | — |
| Donanım | — |
| Eğitim tarihi | — |
| Ölçüm yapılan küme | *(hangi kümede ölçüldüğü açıkça yazılacak)* |

### Genel sonuçlar

| Ölçüt | Değer |
|---|---|
| mAP@0.5 | — |
| mAP@0.5:0.95 | — |
| Ortalama precision | — |
| Ortalama recall | — |
| Ortalama F1 | — |

### Sınıf bazında sonuçlar

Sınıf listesi `siniflar.json` ile birebir aynı olacaktır.

| id | Sınıf | Precision | Recall | F1 | AP@0.5 | Örnek sayısı |
|---|---|---|---|---|---|---|
| 0 | beton | — | — | — | — | — |
| 1 | dolgu_toprak | — | — | — | — | — |
| 2 | ahsap | — | — | — | — | — |
| 3 | sert_plastik | — | — | — | — | — |
| 4 | yumusak_plastik | — | — | — | — | — |
| 5 | metal | — | — | — | — | — |
| 6 | tekstil | — | — | — | — | — |
| 7 | karton | — | — | — | — | — |
| 8 | alcipan | — | — | — | — | — |
| 9 | konteyner | — | — | — | — | — |

> `konteyner` bir malzeme değildir (`siniflar.json` → `malzeme_mi: false`);
> metriği ölçülür ama miktar hesabına girmez. Bkz. `docs/karar-kaydi.md`
> K-007.

### Düşük güven eşiği

`needs_review` bayrağını tetikleyen eşik, **ölçümle** belirlenecektir:
uzman incelemesine düşen kayıt oranı ile yakalanan hata oranı arasındaki
denge. Şu an sahte serviste **0.50** varsayılmaktadır; bu bir ölçüm sonucu
değil, yer tutucudur.

| Eşik | Uzmana düşen oran | Yakalanan hatalı tespit oranı |
|---|---|---|
| — | — | — |

### Karışıklık matrisi

Hangi sınıfların birbirine karıştığı `results/bilinen-sinirlar.md` C
bölümüne de işlenecektir.

---

## Kapsanmayan sınıflar

`siniflar.json` → `kapsanmayan_gruplar`:

| Grup | Durum |
|---|---|
| cam | CDW-Seg'de sınıf yok — model tanımıyor, metrik üretilemez |
| seramik | CDW-Seg'de sınıf yok — model tanımıyor, metrik üretilemez |
| tuğla | `concrete` sınıfına dahil, ayrı ölçülemez |

Ayrıntı: `results/bilinen-sinirlar.md` B.1 ve B.2.

---

## Atıf

Eğitim veri seti:

> Sirimewan, D. & Arashpour, M. *A benchmark dataset for class-wise
> segmentation of construction and demolition waste in cluttered
> environments.* Scientific Data (2025).
> https://doi.org/10.1038/s41597-025-05243-x
> Veri: https://doi.org/10.6084/m9.figshare.28573229 — CC0 1.0
