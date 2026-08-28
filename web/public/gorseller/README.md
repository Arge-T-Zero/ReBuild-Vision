# Görseller

Bu klasördeki görüntüler **yapay zekâ ile üretilmiştir.** Gerçek bir afet
fotoğrafı değildirler.

Bu bilinçli bir tercihtir:

- **Şartname Madde 10.7** demo ortamında sentetik veri kullanılmasını
  esas alıyor — üretilmiş görsel bu koşulu doğrudan karşılar.
- Gerçek 6 Şubat görselleri AA, AFAD ve İHA arşivlerinde **lisanslıdır**;
  izinsiz kullanım telif sorunu doğurur.
- İnsanların hayatını kaybettiği gerçek bir felaketin fotoğrafını demo
  görseli olarak kullanmak, projenin ciddiyetiyle bağdaşmaz.

## Dosyalar

| Dosya | Kullanım |
|---|---|
| `giris-hero.webp` | Giriş ekranı arka planı (%25 opaklık + geçiş katmanı) |
| `ornek-enkaz-1…3.webp` | Demo görüntüleri |
| `*-kucuk.webp` | Kart ve liste önizlemeleri (640px) |

## Üretim

Kaynak PNG'ler ~3 MB'tı ve depoya alınmadı (`.gitignore`). Web sürümleri
WebP'ye çevrildi: **11.6 MB → 1.27 MB**.

Yeni görsel eklerken aynı dönüşümü uygulayın:

```python
from PIL import Image
im = Image.open("yeni.png").convert("RGB")
im.save("yeni.webp", "WEBP", quality=82, method=6)
kucuk = im.copy(); kucuk.thumbnail((640, 640), Image.LANCZOS)
kucuk.save("yeni-kucuk.webp", "WEBP", quality=78, method=6)
```

## OG kapağı

`og-kapak.jpg` üç adaydan **ölçülerek** seçilmiş bir zemin üzerine
bestelenmiştir.

Zemin seçimi: metnin oturacağı sol bölge her adayda ölçüldü (parlaklık ve
hareketlilik). `kapak-2` açık ara en uygunu çıktı — koyu ve sakin, metin
taşıyabiliyor.

Üzerine basılanlar: ürün adı, tek cümlelik tanım, projenin asıl iddiası
(*"Ölçüm yoksa miktar üretilmez"*) ve yarışma künyesi.

Metin kontrastları ölçüldü: başlık **12,5:1**, gövde **8,7:1**, marka
metni **5,6:1** — hepsi WCAG AA üzerinde.

Ham adaylar (`og-kapak-1/2/3.jpg`) karşılaştırma için tutuluyor; yayında
kullanılan `og-kapak.jpg`'dir.

## Logo

`logo-isaret.svg` ve `favicon.svg` **geçicidir.**

Takımın mevcut logosu koyu temada kullanılamıyordu: piksellerin yalnızca
%17'si siyah zeminde görünür parlaklıkta ve oranı 1.84:1 olduğu için kare
alana sığmıyor.

Geçici işaret `currentColor` kullanır — hangi temada olursa olsun metin
rengini alır, ayrı açık/koyu sürüm gerekmez.

**Gerçek logo geldiğinde gereken iki dosya:**

| Dosya | Ne olmalı |
|---|---|
| Kare işaret | Yazısız, 1:1, 24 pikselde okunur. Açık sürüm (koyu tema) ya da `currentColor` |
| Yatay logo | Yazılı tam sürüm; giriş ekranı ve altbilgi için |
