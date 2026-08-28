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
