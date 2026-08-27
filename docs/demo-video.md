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
| 4 | Düşük güvenli kaydın **otomatik** kuyruğa düşmesi | ~30 sn | "1 tespit otomatik olarak uzman inceleme kuyruğuna alındı" |
| 5 | Uzman rolüne geçiş: bir tahmini düzelt, birini belirsiz işaretle | ~50 sn | Üç aksiyon; eski/yeni sınıfın birlikte görünmesi |
| 6 | Saha ölçümü gir → miktarın **belirsizlik aralığıyla** çıkması | ~40 sn | `7.74 – 9.46 ton` + yöntem + katsayı kaynağı |
| 7 | **Ölçüm olmayan kayıtta miktar alanının boş kalması** | ~40 sn | ⭐ **EN GÜÇLÜ AN** |
| 8 | Malzeme Kaynak Haritası → filtreleme | ~30 sn | Yalnızca doğrulanmış kayıtlar; kapsam uyarısı lejandda |

**Toplam:** ~5 dakika

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
- Model metrikleri henüz ölçülmediği için videoda **hiçbir doğruluk
  oranı, geri kazanım oranı veya ekonomik fayda sayısı
  söylenmeyecektir** (`results/model-metrikleri.md`).

## Kontrol listesi (çekimden önce)

- [ ] Gerçek model bağlandı mı? Bağlanmadıysa sahte servis bandı ekranda
      görünüyor ve anlatımda belirtiliyor mu?
- [ ] Demo veri tabanı temiz mi? (`scripts/demo_veri.py`)
- [ ] Ekranda gerçek e-posta adresi görünüyor mu? (görünmemeli)
- [ ] Maskelenmemiş saha fotoğrafı ekrana geliyor mu? (gelmemeli)
- [ ] Ölçülmemiş bir sayı söyleniyor mu? (söylenmemeli)
- [ ] Süre 5 dakikanın altında mı?
