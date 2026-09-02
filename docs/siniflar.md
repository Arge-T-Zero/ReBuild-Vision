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
| 1 | `beton_tugla` | Beton / tuğla | ✅ | `#6b7280` | ❌ kapalı |
| 2 | `cam` | Cam | ✅ | `#008300` | ❌ kapalı |
| 3 | `metal` | Metal | ✅ | `#3987e5` | ✅ kaynaklı |
| 4 | `seramik` | Seramik | ✅ | `#c98500` | ❌ kapalı |

Katsayı durumu: `katsayilar.json` — beşten ikisi kaynaklı. Neden bir sayı
uydurulmadığı: `docs/cevresel-etki.md` Bölüm 2.

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
birlikte. Seçilen küme **ΔE = 6,8**; önceki 10 renkli paletin aynı
ölçütteki skoru **3,5** idi, yani yeni palet iki kat daha ayırt
edilebilir. Karar: `docs/karar-kaydi.md` **K-022**.

Anlamsal tutarlılık da korundu: gri beton/tuğla, koyu yeşil cam, mavi
metal, turuncu ahşap, kehribar seramik.

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

**Bugünkü beş sınıf bu listeyle birebir örtüşüyor.** Raporda örneklenen
beş grubun beşi de modelin tanıdığı sınıflardır; `beton_tugla` ikisini
birlikte kapsar.

Bu, 27.08.2026'daki durumun tersidir: o tarihte kullanılması planlanan
kamuya açık veri setinde (CDW-Seg) **cam ve seramik sınıfı yoktu** ve
tuğla ayrı ayrılmıyordu; belge bu boşluğu kayda geçiriyordu. Kendi veri
setiyle eğitim bu boşluğu kapattı.

**Açılan yeni boşluk gizlenmiyor:** `seramik` sınıfı tanınıyor ama test
mAP50'si **0,0877** — yani pratikte çalışmıyor. Bir sınıfın listede
olması, o sınıfın güvenilir bulunduğu anlamına gelmez. Ayrıntı:
`results/model-metrikleri.md` ve `results/bilinen-sinirlar.md`.

Sistem, tanımadığı bir sınıf için **tahmin üretmez ve o sınıfın yokluğunu
"o malzeme sahada yok" anlamına gelecek biçimde göstermez** (talimat
Bölüm 1.2'deki "yokluk güvenlik değildir" ilkesinin malzeme tarafındaki
karşılığı).
