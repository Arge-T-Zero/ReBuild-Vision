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
| 6 | Saha ölçümü gir → miktarın **belirsizlik aralığıyla** çıkması | ~40 sn | `4,012 – 6,360 ton` + yöntem + katsayı kaynağı (demo verisinde **tespit #6**) |
| 7 | **Ölçüm olmayan kayıtta miktar alanının boş kalması** | ~40 sn | ⭐ **EN GÜÇLÜ AN** (demo verisinde **tespit #3**) |
| 8 | Malzeme Kaynak Haritası → filtreleme | ~30 sn | Yalnızca doğrulanmış kayıtlar; kapsam uyarısı lejandda |

**Toplam:** ~5 dakika

### Demo verisindeki hangi kayıt neyi gösteriyor

`scripts/demo_veri.py` her çalıştığında aynı 14 tespiti üretir (kutular
ve güven skorları gerçek modelden, `scripts/demo_tespitleri.json`).
Çekim sırasında aranacak kayıtlar:

| Kayıt | Ne gösterir | Ekranda |
|---|---|---|
| **#6** ahşap %58,60 | Ölçüm + kaynaklı katsayı | `4,012 – 6,360 ton`, EPA kaynağı görünür |
| **#3** metal %76,09 | Doğrulanmış ama **ölçümsüz** | Miktar alanı **boş** — 7. adımın kaydı |
| **#4** beton/tuğla %66,13 | Ölçüm **var**, katsayı **yok** | Miktar yine boş, gerekçesi ayrı yazılı |
| **#7** ahşap %53,43 | Uzman düzeltmesi | "Ahşap → Beton / tuğla", ham tahmin üstü çizili |
| **#11** metal %54,30 | Doğrudan tartım | `3,150 – 3,850 ton`, katsayı kullanılmadı |
| **#14** ahşap %31,51 | Belirsiz işaretlenmiş | İkinci incelemeye açık |

#4 ile #3'ün birlikte gösterilmesi 7. adımı güçlendirir: biri ölçümü
olmadığı için boş, diğeri ölçümü **olduğu hâlde** katsayısı olmadığı için
boş. Sistem iki farklı nedenle de sayı uydurmuyor.

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
  söylenmelidir: test mAP50 **0,4334**, `cam` sınıfı **0,7257**. Sınırı
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
