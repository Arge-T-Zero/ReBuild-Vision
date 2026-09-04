# Malzeme Sınıfları — tek doğruluk kaynağı

**Karar tarihi:** 02.09.2026 · **Dayanak:** eğitilen modelin
`model-service/data.yaml` sınıf sırası

Makine tarafından okunan sürüm: `siniflar.json` (depo kökü).
Kod içinde sınıf listesi **elle yazılmaz**; hem `model-mock` hem `api` bu
dosyayı okur.

> ⚠️ **02.09.2026 — liste 10'dan 5'e indi.** Önceki sürüm CDW-Seg'in on
> sınıfını tanımlıyordu, ama model **o veri setiyle eğitilmedi.**
> `model-service/app.py` sınıf adını modelden değil buradan, **id
> üzerinden** okuduğu için uyuşmazlık her tespiti sessizce yanlış adla
> kaydediyordu. Gerekçe ve etki tablosu: `docs/karar-kaydi.md` **K-021**.

## Sınıf tablosu

Sıra **modelin `data.yaml` sırasıdır ve değiştirilemez.**

| id | Sistem adı | Görünen ad | Malzeme mi? | Renk | Katsayı |
|---|---|---|---|---|---|
| 0 | `ahsap` | Ahşap | ✅ | `#d95926` | ✅ kaynaklı |
| 1 | `beton` | Beton | ✅ | `#6b7280` | ❌ kapalı |
| 2 | `cam` | Cam | ✅ | `#008300` | ❌ kapalı |
| 3 | `seramik` | Seramik | ✅ | `#d4a017` | ❌ kapalı |
| 4 | `tugla` | Tuğla | ✅ | `#8c1d18` | ❌ kapalı |

Katsayı durumu: `katsayilar.json` — beşten **yalnızca biri** kaynaklı
(`ahsap`). Neden bir sayı uydurulmadığı: `docs/cevresel-etki.md` Bölüm 2.

> ⚠️ **v2 geçişinin bedeli (03.09.2026).** v1'de `metal` sınıfı vardı ve
> kaynaklı katsayısı olan **iki** sınıftan biriydi. v2'nin eğitim veri
> setinde metal yok; kaynaklı katsayı sayısı **2'den 1'e** düştü. Yani
> hacim ölçümünden tonaj üretilebilen tek malzeme ahşaptır. Ayrıca
> `beton_tugla` ikiye ayrıldı ve ikisinin de kaynağı yok. Bu, modelin
> genel başarımındaki artışın (val mAP50 0,44 → 0,88) yanında kayıtlı bir
> **kapsam kaybıdır** ve gizlenmez.

### Modelin tanımadığı gruplar

`dolgu_toprak`, `sert_plastik`, `yumusak_plastik`, `tekstil`, `karton`,
`alcipan` — eğitim veri setinde yok, model tanımaz.

**Bir sınıfın çıktıda görünmemesi "o malzeme sahada yok" anlamına
gelmez.** Bu, sistemin en temel ilkelerinden biridir ve arayüzde de
böyle gösterilir.

### Malzeme olmayan sınıf

Bu sürümde **yok** — beşi de atık malzemedir. Önceki sürümdeki
`konteyner` (skip bin) eğitim setinde bulunmadığı için kalktı.
Ayıklama **mekanizması** (`malzeme_mi: false`) kaldırılmadı; kural kodda
ve testte duruyor (`K-007`).

### Renkler ölçülerek seçildi

Beş renk protanopi, dötanopi ve tritanopi benzetimiyle LAB uzayında
ölçülerek seçildi.

**Ölçüt:** bütün ikililerin en kötüsü — normal görüş ve üç renk körlüğü
birlikte. Ölçüm betiği artık depoda: **`scripts/renk_olc.py`**.

v2 paleti bu ölçütte **ΔE = 15,45**; v1 paleti aynı kodla **8,95**.
Darboğaz v1'de `cam ↔ seramik` (protanopi) idi ve tuğlaya hangi renk
verilirse verilsin tavanı o belirliyordu — seramiği bir tık açmak
(`#c98500` → `#d4a017`) tabanı neredeyse iki katına çıkardı. Zorunlu göç,
paletin bilinen zayıflığını kapatma fırsatına dönüştü.
Karar: `docs/karar-kaydi.md` **K-024**.

⚠️ Bu sayı **K-022'deki 6,79 ile karşılaştırılamaz**: o değer başka bir
uygulamayla (farklı benzetim matrisi ya da ΔE formülü) üretilmişti.
8,95 → 15,45 karşılaştırması geçerlidir çünkü iki palet de aynı kodla
ölçülmüştür.

Anlamsal tutarlılık korundu: turuncu ahşap, gri beton, koyu yeşil cam,
altın seramik, koyu kırmızı tuğla.

En düşük etiket kontrastı **4,83** (WCAG AA eşiği 4,5) — değişmedi.

**Renk hiçbir zaman TEK BAŞINA anlam taşımaz** — her etikette sınıf adı
yazılıdır (WCAG 1.4.1). Ölçüm, rengin yardımcı olduğu durumu
iyileştirmek içindir, ona bağımlılık yaratmak için değil.


## Malzeme olmayan sınıf kuralı (K-007)

`siniflar.json` içindeki her sınıfın bir `malzeme_mi` alanı vardır.
`false` işaretli sınıflar

- miktar hesabına **girmez**
- Malzeme Kaynak Haritası'nda malzeme olarak **gösterilmez**
- geri kazanım/yönlendirme akışına **girmez**

Kural veri katmanında uygulanır (`api/app/services/queries.py`), yalnızca
arayüzde gizlenerek değil; ve HAM tahmine değil **geçerli sınıfa** bakar,
yani uzmanın düzelttiği sınıf esas alınır.

**Bu sürümde `malzeme_mi: false` olan sınıf yoktur.** Kural yine de
kaldırılmadı: atığın içinde bulunduğu kap (ör. hurda konteyneri) ya da
zemin sahada tanınmaya başlarsa tonaja karışmamalıdır. Mekanizmasız bir
kural, ihtiyaç duyulduğu gün sessizce yok olurdu — bu yüzden test de
mekanizmayı sınar, sınıf adını değil (`tests/conftest.py` →
`malzeme_olmayan_sinif`).

## Rapordaki ifadeyle ilişki

Teslim edilmiş ön değerlendirme raporu şöyle diyor:

> "beton/tuğla, metal, ahşap, cam ve seramik **gibi** ana malzeme grupları
> için ön sınıflandırma yapılacaktır."

### 🔴 v2 ile ortaya çıkan sapma: `metal` artık yok

Raporda sayılan beş gruptan **dördü** bugünkü modelde var:
`beton` ✅ · `tugla` ✅ (v2'de ayrı ayrı) · `ahsap` ✅ · `cam` ✅ ·
`seramik` ✅. **`metal` YOK.**

v1'de metal bir sınıftı. v2'nin eğitim veri seti (üç kamuya açık kaynağın
birleşimi) metal içermiyor — kaynak veri setlerinden birinde (`wood-0nvcu`)
bir `metal` sınıfı bulunuyordu ama alınmadı.

**Bu, teslim edilmiş bir belgede verilen örnekten sapmadır ve
gizlenmemektedir.** Raporun ifadesi "…**gibi** ana malzeme grupları"
biçiminde olduğu için kapalı bir liste taahhüdü değildir; yine de
enkazdaki metalin kayıt dışı kaldığı doğrudur ve arayüzde
"kapsanmayan gruplar" arasında yazılıdır (`siniflar.json`).

Mentöre sorulacaklar arasına eklenmelidir: metal, geri kazanım değeri en
yüksek malzemelerden biridir; kapsam dışı kalması operasyonel bir
eksikliktir. Kapatma yolu, metal içeren izin verici lisanslı bir veri
setiyle yeniden eğitimdir.

### Tarihçe

27.08.2026'da kullanılması planlanan kamuya açık veri setinde (CDW-Seg)
**cam ve seramik sınıfı yoktu** ve tuğla ayrılmıyordu. v1 (takımın kendi
veri seti) bu boşluğu kapattı ama lisans beyanı eksikti; v2 lisans
sorununu çözdü, karşılığında metali kaybetti.

**Açılan yeni boşluk gizlenmiyor:** `seramik` sınıfı tanınıyor ama test
mAP50'si **0,0877** — yani pratikte çalışmıyor. Bir sınıfın listede
olması, o sınıfın güvenilir bulunduğu anlamına gelmez. Ayrıntı:
`results/model-metrikleri.md` ve `results/bilinen-sinirlar.md`.

Sistem, tanımadığı bir sınıf için **tahmin üretmez ve o sınıfın yokluğunu
"o malzeme sahada yok" anlamına gelecek biçimde göstermez** (talimat
Bölüm 1.2'deki "yokluk güvenlik değildir" ilkesinin malzeme tarafındaki
karşılığı).
