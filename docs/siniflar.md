# Malzeme Sınıfları — tek doğruluk kaynağı

**Karar tarihi:** 27.08.2026 · **Dayanak:** CDW-Seg veri seti (CC0)

Makine tarafından okunan sürüm: `siniflar.json` (depo kökü).
Kod içinde sınıf listesi **elle yazılmaz**; hem `model-mock` hem `api` bu
dosyayı okur.

## Sınıf tablosu

| id | CDW-Seg (İngilizce) | Sistem adı | Görünen ad | Malzeme mi? |
|---|---|---|---|---|
| 0 | concrete | `beton` | Beton | ✅ |
| 1 | fill dirt | `dolgu_toprak` | Dolgu toprak | ✅ |
| 2 | timber | `ahsap` | Ahşap | ✅ |
| 3 | hard plastic | `sert_plastik` | Sert plastik | ✅ |
| 4 | soft plastic | `yumusak_plastik` | Yumuşak plastik | ✅ |
| 5 | steel | `metal` | Metal | ✅ |
| 6 | fabric | `tekstil` | Tekstil | ✅ |
| 7 | cardboard | `karton` | Karton | ✅ |
| 8 | plasterboard | `alcipan` | Alçıpan | ✅ |
| 9 | skip bin | `konteyner` | Konteyner | ❌ **hayır** |

## `konteyner` neden özel

`skip bin` (hurda konteyneri) bir **atık malzeme değildir** — atığın içinde
bulunduğu kaptır. Veri setinde sınıf olarak etiketlenmiştir çünkü modelin
sahneyi ayrıştırmasına yardım eder.

**Kural:** `malzeme_mi = false` olan sınıflar

- miktar hesabına **girmez**
- Malzeme Kaynak Haritası'nda malzeme olarak **gösterilmez**
- geri kazanım/yönlendirme akışına **girmez**

Bu kural veri katmanında uygulanır (`api/app/services/queries.py`), yalnızca
arayüzde gizlenerek değil.

## Rapordaki ifadeyle ilişki

Teslim edilmiş ön değerlendirme raporu şöyle diyor:

> "beton/tuğla, metal, ahşap, cam ve seramik **gibi** ana malzeme grupları
> için ön sınıflandırma yapılacaktır."

"gibi" sözcüğü listeyi **örnekleyici** kılar, kapalı bir taahhüt değil.
Bu nedenle CDW-Seg'in on sınıfının kullanılması raporla çelişmez.

**Ancak dürüstlük gereği kayda geçen boşluk:** CDW-Seg'de **cam ve seramik
sınıfı yoktur.** Raporda örnek olarak anılan bu iki grup, mevcut eğitim
verisiyle tanınamaz. Ayrıca `concrete` sınıfı betonu kapsar ama **tuğlayı
ayrı bir sınıf olarak ayırmaz.**

Bu boşluk `results/bilinen-sinirlar.md`'de ayrıntılı olarak kaydedilmiştir.
Sistem, tanımadığı bir sınıf için **tahmin üretmez ve o sınıfın yokluğunu
"o malzeme sahada yok" anlamına gelecek biçimde göstermez** (talimat
Bölüm 1.2'deki "yokluk güvenlik değildir" ilkesinin malzeme tarafındaki
karşılığı).
