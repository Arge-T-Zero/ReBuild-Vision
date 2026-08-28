# Lighthouse Ölçümü

**Ölçüm tarihi:** 28.08.2026
**Dayanak:** Ana talimat Bölüm 13 — *"Web arayüzü için Lighthouse dört
kategoride ölçülsün."*

Ölçüm **üretim derlemesi** üzerinde (`vite preview`, port 4173), üç tur
çalıştırılıp **ortanca** alınarak yapıldı. Tek tur güvenilir değildir;
makine yükü sonucu 5–10 puan oynatır.

```bash
npm --prefix web run build
npx vite preview --port 4173 --strictPort
npx lighthouse http://localhost:4173/ --only-categories=performance,accessibility,best-practices,seo
```

## Sonuç

| Kategori | Puan | Not |
|---|---|---|
| **Erişilebilirlik** | **100** | Bölüm 13'ün asıl önemsediği kategori |
| **En İyi Uygulamalar** | **100** | |
| **SEO** | **100** | |
| Performans | 81 | Ölçüt bilgileri aşağıda |

Üç turun üçünde de aynı puanlar alındı — sonuç kararlı.

| Ölçüt | Değer |
|---|---|
| First Contentful Paint | 3,0 s |
| Largest Contentful Paint | 4,1 s |
| Speed Index | 3,0 s |
| Total Blocking Time | 0 ms |
| Cumulative Layout Shift | 0 |

## Erişilebilirlik neden önemli

Sistem *"saha koşulunda, güneş altında, eldivenli parmakla kullanılacak"*
iddiasında. Bölüm 14'e göre ölçülmemiş iddia beyan edilmez; bu ölçüm o
iddianın kanıtıdır.

Tarayıcıda ayrıca elle ölçülenler (her iki temada da):

| Kontrol | Sonuç |
|---|---|
| WCAG AA kontrast ihlali | **0** |
| 12 pikselden küçük metin | **0** |
| 32 pikselden küçük dokunma hedefi | **0** |
| 360 piksel genişlikte yatay taşma | **yok** |

Ayrıca `prefers-reduced-motion` desteklenir ve odak halkası her zaman
görünürdür.

## İyileştirme geçmişi

| | İlk ölçüm | Son |
|---|---|---|
| Performans | 68 | **81** |
| Erişilebilirlik | 97 | **100** |
| En İyi Uygulamalar | 96 | **100** |
| SEO | 91 | **100** |

Yapılanlar:

1. **Yazı tipleri kendi sunucumuza alındı.** Google Fonts stil dosyası
   render'ı 2.480 ms bloke ediyordu. Yan fayda daha önemli: her
   ziyaretçinin IP adresi artık üçüncü bir tarafa gitmiyor — kamu afet
   yönetimi aracında gereksiz bir veri sızıntısıydı. Yalnızca `latin` ve
   `latin-ext` alt kümeleri indirildi (Türkçe karakterler orada).
2. **Giriş ekranı oturum sorgusunu beklemiyor.** Jeton yoksa `/auth/ben`
   hiç çağrılmıyor. Önceden sunucu uykudayken (Render ücretsiz katmanı
   ilk isteği ~50 sn bekletir) kullanıcı "Yükleniyor…" ekranına bakıp
   sistemin bozuk olduğunu sanıyordu.
3. **Leaflet ayrı parçaya alındı.** Ana paket 402 KB → 248 KB; harita
   yalnızca harita sayfası açılınca yükleniyor.
4. **Hero görseli optimize edildi** (345 KB → 166 KB) ve önceden
   yükleniyor. %25 opaklıkla iki geçiş katmanının altında durduğu için
   düşük kalite görünmüyor.
5. `<main>` işareti, `robots.txt` ve `sitemap.xml` eklendi.

## Kalan sınır

Performans 81'de duruyor; LCP 4,1 sn. Sebep tek sayfa uygulamasının
JavaScript'i indirip React'i başlatması. Bunu daha da düşürmek sunucu
tarafı render (SSR) gerektirir — 9 günlük takvimde kapsam dışıdır ve
Bölüm 10'daki kapsam kararıyla tutarlıdır.

> Ölçülmüş bir sınır, ölçülmemiş bir iddiadan güçlüdür.
