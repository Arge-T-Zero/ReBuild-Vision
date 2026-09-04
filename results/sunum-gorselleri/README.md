# Sunum görselleri

> 🔴 **BU GÖRSELLER ESKİDİR (03.09.2026 itibarıyla).**
>
> Ekran görüntüleri **model-v1** ile alındı. O modelde `metal` ve
> `beton_tugla` sınıfları vardı; v2'de ikisi de yok (`metal` kalktı,
> `beton_tugla` `beton` ve `tugla` diye ayrıldı). Renk paleti de değişti.
>
> **Sunumda bu görseller kullanılırsa jüri, sistemde olmayan sınıfları
> görür.** Yeniden çekilmeleri gerekir; komutlar bu dosyanın sonunda.
>
> Ayrıca v2 bu üç sentetik görüntüde 14 değil **4 tespit** üretiyor
> (ölçülmüş genelleme farkı — `results/model-metrikleri.md`), yani yeni
> ekran görüntüleri daha az kutu gösterecektir. Bu bir kusur değil,
> beyan edilmiş bir ölçümdür.

Final sunumunun slaytlarında kullanılmak üzere, **çalışan sistemden**
alınmış ekran görüntüleri. 03.09.2026.

## ⚠️ Ne gerçek, ne sentetik — sunumda söylenmesi gereken

| Öğe | Durum |
|---|---|
| **Tespit kutuları, sınıflar, güven skorları** | **GERÇEK.** `model-v1` sürümündeki `best.pt` (YOLO11m, 5 sınıf) ile üretildi. Elle yazılmadı |
| Model servisi | **Gerçek** — `/health` → `sahte: false`, `agirlik_yuklendi: true` |
| Güven skorları | **Yuvarlanmamış** (%76,0914 gibi) — ana talimat Bölüm 9.2 |
| Enkaz fotoğrafları | **Sentetik.** Ekranda da "Sentetik demo görüntüsü" yazıyor |
| Saha adları | **Sentetik.** Hepsi "(sentetik)" etiketli |
| Doğrulama ve ölçüm senaryosu | **Sentetik.** Sahada gerçek bir uzman ya da şerit metre yok |

Jüri bunları ekranda zaten görüyor; sunumda da aynısı söylenmelidir.

## Dosyalar

### `cerceveli/` — slayta doğrudan konulabilir (cihaz çerçevesi + numara + altyazı)

**Mobil**

| Dosya | İçerik |
|---|---|
| `mobil-1.png` | Giriş ekranı |
| `mobil-2.png` | Saha görüntüsü yükleme |
| `mobil-3.png` | Modelin ürettiği tespitler (`#1…#10`) |
| `mobil-4.png` | Saha ölçümü girişi |

**Web**

| Dosya | İçerik |
|---|---|
| `web-1.png` | Giriş ekranı |
| `web-2.png` | Enkaz alanları panosu — üç saha, üç erişim durumu |
| `web-3.png` | Sınıflandırma sonuçları · her kutuda **ÖN TAHMİN**, uzman düzeltmesi, inceleme kuyruğu |
| `web-4.png` | Ölçüm girilince: **4,012 – 6,36 ton** + belirsizlik aralığı + EPA kaynağı |
| `web-5.png` | Ölçüm yoksa miktar **boş** — sıfır değil |
| `web-6.png` | Katsayı yoksa, ölçüm olsa da miktar üretilmez |

**Birleşik levhalar** — tek başına bir slayt olur

| Dosya | İçerik |
|---|---|
| `LEVHA-mobil.png` | Dört mobil ekran yan yana |
| `LEVHA-web-genel.png` | Giriş + pano |
| `LEVHA-miktar-kurali.png` | Miktarın üç durumu yan yana — projenin en ayırt edici slaytı |

### Kök dizin — çerçevesiz ham kareler
Kendi düzeninizi kurmak isterseniz.

## Eksik: harita ekranı

`Malzeme Kaynak Haritası` bu ortamda çekilemedi: geliştirme konteynerinin
ağ politikası OpenStreetMap'e erişimi engelliyor, harita altlığı boş
kalıyor. (Uygulama bunu gizlemiyor, ekranda *"Harita altlığı
yüklenemedi… işaretçiler gösterilmeye devam ediyor"* yazıyor.)

**Kendi makinenizde** `/harita` sayfasını açıp bir ekran görüntüsü alın;
orada altlık yüklenir.

## Yeniden üretmek

Görüntüler `scripts/demo_veri.py` ile kurulmuş demo veri tabanından
alınmıştır; demo verisi de `scripts/demo_tespitleri.json` (gerçek model
çıktısı) üzerine kuruludur. Aynı adımlar `docs/kurulum.md` ve
`docker/README.md` içinde yazılıdır.
