# Model Metrikleri — model-v2

> **Bu dosyaya ölçülmemiş hiçbir sayı yazılmaz.** *(Ana talimat Bölüm 7.4
> ve 14)*

**Son güncelleme:** 03.09.2026 · **Model:** YOLO11s · **Sürüm:** `model-v2`
· sha256 `468cf535a4e26977…` (18 MB)

v1'in ölçümleri silinmedi, tarihî kayıt olarak duruyor:
[`model-metrikleri-v1-TARIHI.md`](model-metrikleri-v1-TARIHI.md).

---

## Ölçüm

150 epoch, ~91 dakika, 640 px. Gönderilen ağırlık **epoch 142**
checkpoint'idir — Ultralytics `best`i *fitness*'a (0,1·mAP50 +
0,9·mAP50-95) göre seçer, son epoch'a ya da en yüksek mAP50'ye göre
değil. Sayılar `results/egitim-v2/results.csv`'nin 142. satırından gelir.

| Bölme | precision | recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| **val** | 0,9087 | 0,8316 | **0,8824** | 0,6497 |

Bağlam olarak, aynı koşudan diğer iki dikkat çekici epoch:

| epoch | mAP50 | mAP50-95 | not |
|---|---|---|---|
| 109 | 0,8900 | 0,6414 | en yüksek mAP50 |
| **142** | 0,8824 | **0,6497** | **gönderilen ağırlık** (en yüksek fitness) |
| 150 | 0,8855 | 0,6475 | son epoch |

### 🔴 TEST KÜMESİ ÖLÇÜLMEDİ

v1'de hem val hem test ölçümü vardı (test mAP50 0,4334). v2 için
`split=test` ile ayrı bir koşu **yapılmadı**; elimizde yalnızca eğitim
sırasındaki val ölçümü var.

Val sayısını "test" diye beyan etmek yanlış beyan olurdu. Arayüzün
altbilgisi de bu yüzden **"val mAP50 = 0,8824"** diyor — bölme adı
`results/egitim/metrikler.json`'dan okunur, sabit yazılmaz.

### Sınıf bazlı sayısal tablo da yok

`results.csv` yalnızca genel ortalamayı taşır. Karışıklık matrisi ve
F1/P eğrileri görsel olarak elimizde; sayısal per-sınıf tablo için
`model.val()` çıktısı gerekir. Görsellerden **okunabilen** sınıf bazlı
köşegen (normalize karışıklık matrisi):

| Sınıf | Köşegen |
|---|---|
| cam | 0,95 |
| beton | 0,87 |
| tugla | 0,87 |
| seramik | 0,85 |
| **ahsap** | **0,82** |

`ahsap` en zayıf sınıf ve arka planın %38'ini ahşap sanıyor (83 yanlış
pozitif). v1'de de en zayıf sınıflardan biriydi; bu tutarlı bir zayıflık.

---

## ⚠️ ÖLÇÜLMÜŞ GENELLEME FARKI — bu bölüm atlanmamalıdır

v2 kendi doğrulama kümesinde **mAP50 0,8824** alıyor. Deponun üç
**sentetik** demo görüntüsünde ise yalnızca **4 tespit** üretiyor ve
hepsi `ahsap`:

| Görüntü | v1 (YOLO11m) | v2 (YOLO11s) |
|---|---|---|
| `ornek-enkaz-1.webp` | 8 tespit | 2 (`ahsap` %51,00 · %27,11) |
| `ornek-enkaz-2.webp` | 4 tespit | 1 (`ahsap` %94,20) |
| `ornek-enkaz-3.webp` | 2 tespit | 1 (`ahsap` %76,12) |
| **toplam** | **14 tespit / 4 sınıf** | **4 tespit / 1 sınıf** |

**Sebep dağılım farkıdır, bozukluk değil.** v2, gerçek yıkım atığı
fotoğraflarıyla eğitildi (Mendeley CODD yakın çekim beton/tuğla/seramik,
kırık cam, ahşap). Demo görüntüleri ise yapay zekâ üretimi **geniş moloz
sahneleridir** (`web/public/gorseller/README.md`) — eğitim dağılımının
dışındadır. v1, takımın internetten topladığı benzer geniş sahnelerle
eğitildiği için bu görüntülerde daha çok kutu üretiyordu.

**Bu neden gizlenmiyor ve neden önemli:** iki sayıyı yan yana koymak,
sistemin neden hiçbir çıktıyı kendiliğinden onaylamadığının somut
kanıtıdır. Yüksek bir mAP50, modelin sizin sahanızda çalışacağı anlamına
gelmez. Sistemin cevabı eşiği oynatmak değil, **doğrulama kapısıdır**:
doğrulanmamış hiçbir tespit miktara, haritaya ya da rapora girmez.

Gerçek sahada kullanım öncesi yapılması gereken açıktır: **saha
görüntüleriyle yeniden ölçüm.**

---

## Bilinen sınırlar

- **`metal` sınıfı YOK.** v1'de vardı, v2'nin veri setinde yok. Enkazdaki
  metal kayıt dışı kalır. Bu aynı zamanda kaynaklı katsayısı olan iki
  sınıftan birinin kaybı demektir — bkz. aşağıda.
- **Kaynaklı dönüşüm katsayısı yalnızca 1 sınıfta var** (`ahsap`).
  v1'de 2 idi (`ahsap`, `metal`). `beton`, `tugla`, `cam` ve `seramik`
  için doğrulanmış kaynak yok; bu sınıflarda ölçüm girilse bile miktar
  ÜRETİLMEZ ve gerekçesi ekranda yazılıdır. `katsayilar.json`
  `acik_sorular` bölümüne işlendi.
- Beton, enkazın ana kütlesidir ve katsayısı hâlâ kapalıdır — yani
  miktar göstergesi enkazın en büyük bileşenini kapsamamaya devam eder.
- Test kümesi ölçülmedi (yukarıda).
- Yük testi yapılmadı; hiçbir kapasite sayısı beyan edilmiyor.

---

## Veri seti

Üç kamuya açık veri setinin birleşimi, **üçü de CC BY 4.0**. Kaynaklar,
lisansın ne verip ne istediği, atıf metni ve teslimden önce gözle teyit
edilmesi gerekenler: [`docs/lisans-analizi.md`](../docs/lisans-analizi.md)
**Bölüm 2.1.2**.

## Ham çıktılar

`results/egitim-v2/` — `results.csv`, `data.yaml`, okunan değerler.
