# Demo Videosu

**Şartname Madde 10.3** teslim paketinde demo videosu istemektedir.

**Durum:** ⏳ **Henüz çekilmedi.** Planlanan çekim tarihi: **03.09.2026**
(uçtan uca prova günü).

---

## Bağlantı

| Alan | Değer |
|---|---|
| Video bağlantısı | *(çekildiğinde buraya eklenecek)* |
| Süre | hedef 4–5 dakika |
| Format | MP4, 1080p |
| Ses | Türkçe anlatım |

---

## Senaryo

Final sunumu için **5 dakikaya sığacak** biçimde hazırlanır. Şartnamede
bir tutarsızlık vardır — Madde 2.6.2 **5 dakika**, Madde 5.4 **7 dakika +
3 dakika soru** demektedir. 5 dakikaya hazırlanıp genişletmek kolaydır;
sahnede kısaltmak mümkün değildir. Konu mentöre sorulacaktır
(`docs/karar-kaydi.md`, mentör görüşmesi 1).

### Akış

| # | Adım | Süre | Ne gösterilir |
|---|---|---|---|
| 1 | Belediye rolüyle giriş, enkaz alanı kaydı | ~40 sn | Harita üzerinde konum ve sınır çizimi |
| 2 | Konum bilgili görüntüleri yükleme | ~30 sn | Toplu yükleme |
| 3 | Sınıflandırma sonuçları | ~50 sn | Kutular, sınıf adları, güven skorları, **"ön tahmin" etiketi** |
| 4 | Düşük güvenli kaydın **otomatik** kuyruğa düşmesi | ~30 sn | "N tespit otomatik olarak uzman inceleme kuyruğuna alındı" — sayı yüklenen görüntüye göre değişir, ekranda ne yazıyorsa o söylenir |
| 5 | Uzman rolüne geçiş: bir tahmini düzelt, birini belirsiz işaretle | ~50 sn | Üç aksiyon; eski/yeni sınıfın birlikte görünmesi |
| 6 | Saha ölçümü gir → miktarın **belirsizlik aralığıyla** çıkması | ~40 sn | `4,012 – 6,36 ton` + yöntem + EPA kaynağı (demo verisinde **tespit #3**) |
| 7 | **Ölçüm olmayan kayıtta miktar alanının boş kalması** | ~40 sn | ⭐ **EN GÜÇLÜ AN** (demo verisinde **tespit #4**, Saha B) |
| 8 | Malzeme Kaynak Haritası → filtreleme | ~30 sn | Yalnızca doğrulanmış kayıtlar; kapsam uyarısı lejandda |

**Toplam:** ~5 dakika

### Demo verisindeki hangi kayıt neyi gösteriyor

`scripts/demo_veri.py` her çalıştığında aynı **4 tespiti** üretir
(kutular ve güven skorları gerçek `model-v2` çıktısıdır,
`scripts/demo_tespitleri.json`). Çekim sırasında aranacak kayıtlar:

| Kayıt | Ne gösterir | Ekranda |
|---|---|---|
| **#3** ahşap %94,1995 · Saha A | Ölçüm (40 m³) + kaynaklı katsayı | **`4,012 – 6,36 ton`**, belirsizlik aralığı, EPA kaynağı |
| **#4** ahşap %76,1155 · Saha B | Doğrulanmış ama **ölçümsüz** | *"Ölçüm girilmediği için miktar hesaplanmadı"* — 7. adımın kaydı |
| **#1** ahşap %50,9970 · Saha A | Uzman düzeltmesi **+** katsayısız sınıf | *"Uzman düzeltmesi: ~~Ahşap~~ → Beton"*, ölçüm **var** (62 m³) ama miktar **yok**: *"doğrulanmış dönüşüm katsayısı bulunmadığından"* |
| **#2** ahşap %27,1051 · Saha A | Eşik altı | Kendiliğinden `inceleme_gerekli`, uzman kuyruğunda |

**#1 tek başına iki kuralı taşıyor** ve en güçlü kayıttır: model "ahşap"
dedi, uzman "beton" yaptı; ham tahmin üstü çizili duruyor. Etkin sınıf
artık `beton` ve betonun doğrulanmış katsayısı **yok** — yani ölçüm
girilmiş olmasına rağmen sistem sayı üretmiyor ve gerekçesini yazıyor.

### ⚠️ Anlatımda mutlaka söylenmesi gereken: neden sadece 4 kutu

Model kendi doğrulama kümesinde **mAP50 0,8824** alıyor. Bu üç
**sentetik** demo görüntüsünde ise yalnızca 4 tespit üretiyor.

Sebep dağılım farkıdır: model gerçek yıkım atığı fotoğraflarıyla eğitildi
(Mendeley CODD, kırık cam, ahşap veri setleri), demo görüntüleri ise
yapay zekâ üretimi geniş moloz sahneleri.

**Bu bir kusur değil, projenin en güçlü argümanı.** Önerilen cümle:

> "Modelimiz kendi test verisinde 0,88 alıyor. Bu görüntülerde 4 şey
> buluyor. İkisini de size söylüyoruz. Yüksek bir skor, modelin sizin
> sahanızda çalışacağı anlamına gelmez — sistemin cevabı eşiği oynatmak
> değil, doğrulama kapısıdır: doğrulanmamış hiçbir tespit miktara,
> haritaya ya da rapora girmez."

### 7. adım özellikle vurgulanmalı

Rakip projeler büyük sayılar gösterecektir. Bu projenin farkı,
**doğrulanamayan sayıyı üretmemesidir.**

Gösterilecek ekran:

> **Ölçüm girilmediği için miktar hesaplanmadı**
> *Sistem, dayanağı olmayan bir miktar tahmini üretmez.*

Söylenecek cümle (öneri):

> "Burada bir sayı göremiyorsunuz. Bu bir eksiklik değil, bir karar.
> Ölçüm yoksa sistem tonaj uydurmuyor. Ölçümü girdiğimiz anda ise tek bir
> kesin sayı değil, belirsizlik aralığı ve kullanılan yöntem birlikte
> geliyor."

Bu, raporun Bölüm 4'teki üçüncü yenilikçi yönünün sahnedeki karşılığıdır.

---

## Çekim notları

- **Drone sahnede uçurulmayacaktır** (Rapor Bölüm 7, Final Gösterim
  Planı). Görüntü toplama süreci kısa bir saha videosuyla gösterilir.
- Demo verisi **sentetiktir** ve ekranda böyle görünür (Madde 10.7).
  Gerçek e-posta adresi ve maskelenmemiş saha fotoğrafı ekrana gelmez.
- Ekranın üstündeki **"SAHTE MODEL SERVİSİ"** bandı, gerçek model
  bağlanmadan çekim yapılırsa görünür olacaktır. Bu **gizlenmez** —
  gerçek model bağlandığında bant kendiliğinden kaybolur.
- **Model 01.09.2026'da eğitildi ve ölçüldü** — bu kural 02.09'da
  güncellendi. Videoda **ölçülmüş** metrikler söylenebilir ve
  söylenmelidir: **val** mAP50 **0,8824** (test kümesi ölçülmedi). Sınırı
  da birlikte söylemek gerekir: `seramik` sınıfı test mAP50 **0,0877**,
  yani pratikte çalışmıyor. Kaynak: `results/model-metrikleri.md`.
- **Ölçülmemiş hiçbir sayı söylenmeyecektir**: geri kazanım oranı,
  ekonomik fayda, çıkarım hızı, kapasite. Bunlar ölçülmedi
  (`results/bilinen-sinirlar.md` Bölüm C).

## Kontrol listesi (çekimden önce)

- [ ] Gerçek model bağlandı mı?
      `curl -L -o model-service/agirliklar/best.pt https://github.com/Arge-T-Zero/ReBuild-Vision/releases/download/model-v2/best.pt`
      sonra `docker compose -f docker/compose.yaml -f docker/compose.gercek-model.yaml up`.
      Doğrulama: `/api/sistem/durum` → `sahte: false`.
      Bağlanmadıysa sahte servis bandı ekranda görünüyor ve anlatımda
      belirtiliyor mu?
- [ ] Demo verisindeki tespitler gerçek model çıktısı mı?
      (`scripts/demo_tespitleri.json` → `model: "best"`)
- [ ] Altbilgide **ölçülmüş** mAP yazıyor mu ("henüz ölçülmedi" DEĞİL)?
- [ ] Demo veri tabanı temiz mi? (`scripts/demo_veri.py`)
- [ ] Ekranda gerçek e-posta adresi görünüyor mu? (görünmemeli)
- [ ] Maskelenmemiş saha fotoğrafı ekrana geliyor mu? (gelmemeli)
- [ ] Ölçülmemiş bir sayı söyleniyor mu? (söylenmemeli)
- [ ] Süre 5 dakikanın altında mı?
