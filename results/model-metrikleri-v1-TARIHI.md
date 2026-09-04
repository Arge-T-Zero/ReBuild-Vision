# Model Metrikleri — model-v1 (TARİHÎ KAYIT)

> ⚠️ **BU MODEL ARTIK KULLANILMIYOR.** 03.09.2026'da `model-v2` ile
> değiştirildi. Güncel ölçümler: [`model-metrikleri.md`](model-metrikleri.md).
>
> Silinmedi çünkü CHANGELOG, karar kaydı ve eski denetim raporları bu
> sayılara atıf yapıyor; kaldırılsaydı o atıflar kaynaksız kalırdı.
>
> **Değişimin sebebi yalnızca başarım değildi:** v1'in veri setinin
> lisans beyanı eksikti (aşağıda 3. maddede yazılı) ve bu, teslimin
> tek 🔴 maddesiydi. v2 üç CC BY 4.0 veri setiyle eğitildi.

---


> **Bu dosyaya ölçülmemiş hiçbir sayı yazılmaz.** *(Ana talimat Bölüm 7.4
> ve 14)*

**Son güncelleme:** 02.09.2026

---

## Durum: ✅ ÖLÇÜLDÜ

Model eğitildi ve ölçüldü. Aşağıdaki bütün sayılar
[`results/egitim/`](egitim/) altındaki ham çıktılardan gelir; hiçbiri
elle yazılmamış ya da yuvarlanmamıştır.

### ⚠️ Önce okunması gereken üç şey

1. **Veri seti CDW-Seg DEĞİL.** Önceki sürümlerde bu dosya eğitim
   kaynağını CDW-Seg (CC0, DOI 10.6084/m9.figshare.28573229) olarak
   beyan ediyordu. **Eğitim o veri setiyle yapılmamıştır.** Model,
   takımın kendi topladığı ve Roboflow ile etiketlediği **5 sınıflı**
   bir veri setiyle eğitilmiştir.
2. **Sınıf sayısı 10 değil 5.** `siniflar.json` 02.09.2026'da eğitilen
   modele çekildi (`docs/karar-kaydi.md` K-021).
3. **Veri setinin lisans ve kaynak beyanı EKSİKTİR.** Görüntülerin
   nereden toplandığı ve hangi hakla kullanıldığı henüz yazılı değildir.
   Şartname Madde 5.2 "kaynaklarını açıkça belirtmek kaydıyla" diyor;
   Madde 9.2 üçüncü taraf hak ihlalinin sorumluluğunu katılımcıya
   yüklüyor. Bkz. `docs/lisans-analizi.md` Bölüm 2.1.

---

## Deney künyesi

| Alan | Değer |
|---|---|
| Model | **YOLO11m** (`yolo11m.pt` başlangıç ağırlığı) |
| Girdi boyutu | 640 × 640 |
| Eğitim veri seti | Takımın kendi veri seti, Roboflow etiketli — **5 sınıf** |
| Sınıflar | `ahsap`, `beton_tugla`, `cam`, `metal`, `seramik` |
| Bölme | train 2.184 · valid 384 · test 197 görüntü |
| Nesne sayısı | 7.265 · 1.407 · 676 kutu (toplam **9.348**) |
| Epoch hedefi | 150 (`patience: 30` ile erken durdurma) |
| Optimizasyon | AdamW, `lr0 = 0.001`, `batch = 16` |
| Süre | **2,03 saat** |
| Ham çıktılar | [`results/egitim/`](egitim/) |

Ön işleme: sızıntı ve filigran nedeniyle görüntü silindi, 750 görüntü
oversample edildi — ayrıntı `results/egitim/on_isleme_kaydi.json`.

---

## Sonuçlar

### Genel

| Bölme | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| val | 0,5318 | 0,4530 | **0,4424** | 0,3089 |
| test | 0,4880 | 0,4176 | **0,4334** | 0,3132 |

### Sınıf bazlı

| Bölme | Sınıf | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|
| val | ahsap | 0,4359 | 0,4553 | 0,4127 | 0,2681 |
| val | beton_tugla | 0,4715 | 0,4367 | 0,4092 | 0,3072 |
| val | **cam** | 0,7896 | 0,6848 | **0,7035** | 0,4638 |
| val | metal | 0,4953 | 0,3482 | 0,3848 | 0,2782 |
| val | seramik | 0,4669 | 0,3402 | 0,3019 | 0,2274 |
| test | ahsap | 0,3887 | 0,4143 | 0,3607 | 0,2549 |
| test | beton_tugla | 0,5818 | 0,5758 | 0,6268 | 0,4685 |
| test | **cam** | 0,7928 | 0,6545 | **0,7257** | 0,4952 |
| test | metal | 0,4477 | 0,3241 | 0,3660 | 0,2779 |
| test | **seramik** | 0,2290 | 0,1190 | **0,0877** | 0,0699 |

Eğriler ve karışıklık matrisleri:
[`results/egitim/gorseller/`](egitim/gorseller/)

---

## Bu sayılar ne diyor — abartmadan

**Model çalışıyor ama zayıf.** Genel mAP50 **0,43–0,44**. Bu, tespitlerin
ancak bir kısmının doğru bulunduğu anlamına gelir; sistemin zorunlu uzman
doğrulaması bu yüzden bir süs değil, **çalışma koşuludur.**

### Sınıf bazında dürüst okuma

| Sınıf | Durum |
|---|---|
| **cam** | En iyi sınıf (mAP50 0,70–0,73). Camın görsel imzası ayırt edici |
| **beton_tugla** | Testte val'den iyi (0,63 / 0,41) — küçük test kümesinde olağan dalgalanma |
| **ahsap**, **metal** | Orta (0,36–0,41). Metalin recall'ü düşük (0,32–0,35): **bulduğunu doğru buluyor ama çoğunu kaçırıyor** |
| **seramik** | 🔴 **Testte 0,0877 — pratikte çalışmıyor.** val'de 0,30, testte 0,09; en az örneğe sahip sınıf (939 / 97 / 42 kutu). Bu bir sınıf değil, bir uyarıdır |

### Ne iddia EDİLMİYOR

- Bu sayılar **afet enkazı sahasında** ölçülmemiştir. Veri seti internetten
  toplanmış görüntülerden oluşuyor; gerçek saha koşulunda (toz, ölçek,
  iç içe geçmiş malzeme) başarım **daha düşük olacaktır** ve ne kadar
  düşük olacağı ölçülmemiştir.
- `seramik` sınıfının çıktısı **kullanılabilir sayılmamalıdır.**
- Hiçbir çevresel fayda, geri kazanım oranı veya karbon sayısı bu
  metriklerden türetilmemiştir (`docs/cevresel-etki.md`).

---

## Eşik

`model-service` inceleme eşiği varsayılan **0,50**. Bu ölçülen
metriklerden türetilmiş bir değer **değildir**, mühendislik varsayımıdır
ve `INCELEME_ESIGI` ortam değişkeniyle değiştirilebilir.

Ölçüm artık elde olduğuna göre eşik PR eğrisinden türetilebilir —
`results/egitim/gorseller/val_val__BoxPR_curve.png`. Bu henüz
yapılmamıştır ve yapılana kadar eşik bir varsayım olarak beyan edilir.
