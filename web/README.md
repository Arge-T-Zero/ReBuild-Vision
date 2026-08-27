# web — ReBuild Vision arayüzü

React 19 + Vite + TypeScript + Tailwind. Harita için **çıplak Leaflet**
(BSD-2-Clause) kullanılır; `react-leaflet` lisansı (`Hippocratic-2.1`)
nedeniyle **bilinçli olarak kullanılmamaktadır** — bkz.
`docs/karar-kaydi.md` K-002. React entegrasyonu `src/lib/leaflet/`
altındaki kendi ince sarmalayıcımızdır.

## Çalıştırma

```bash
npm install
npm run dev     # http://localhost:5173
```

`/api` istekleri `vite.config.ts` içindeki vekil ile `localhost:8000`
adresindeki backend'e yönlendirilir.

## Klasörler

| Yol | İçerik |
|---|---|
| `src/bilesenler/` | Paylaşılan bileşenler |
| `src/sayfalar/` | Ekranlar |
| `src/lib/leaflet/` | Leaflet React sarmalayıcısı |
| `src/api.ts` | Backend istemcisi |
| `src/durum.tsx` | Oturum, sistem durumu ve sınıf tanımları |

## İhlal edilemez arayüz kuralları

Bunlar tasarım tercihi değil, teslim edilmiş rapordaki taahhütlerdir:

1. **Her model çıktısında "ön tahmin" etiketi** bulunur, istisnasız
   (`OnTahminEtiketi`).
2. **Ölçüm yoksa miktar alanında sayı gösterilmez.** Yer tutucu, "≈0" veya
   "hesaplanıyor" yazılmaz; gerekçe yazılır ve ölçüm ekleme aksiyonu
   sunulur (`MiktarKarti`).
3. **Kapsam uyarısı** sonuç ekranında ve harita lejandında yazılıdır
   (`KapsamUyarisi`).
4. **Sahte model servisi** etkinken kapatılamayan bir uyarı bandı görünür
   (`SahteServisRozeti`).
5. **Renk tek başına anlam taşımaz** — her renkli göstergenin yanında metin
   etiketi vardır.
6. **Güven skoru yuvarlanmaz**, sayı olarak gösterilir.
7. **Kutu ölçekleme `bbox_format` alanına göre yapılır.** Format
   tanınmıyorsa kutu çizilmez ve durum kullanıcıya söylenir — yanlış yerde
   kutu göstermektense hiç göstermemek doğrudur.
