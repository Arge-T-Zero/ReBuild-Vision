# "Görüntü geneli" kutular — bulgu ve çözüm

**Tarih:** 07.09.2026 · sunumdan bir gün önce, canlı siteye bakılırken

## Belirti

Arayüzde tespit kutuları **tüm görüntüyü kaplıyordu.** Bakan kişi
"model hiçbir şeyi konumlandıramamış, sistem bozuk" diyordu.

## Bu bir çizim hatası DEĞİL

Demo verisindeki ham kutu (1200×896 görüntüde):

    x=0, y=38, w=1200, h=858   → karenin %95,8'i

Model gerçekten bunu üretiyor. Depodaki bütün geniş sahne görüntüleri
ölçüldü (model v2, ONNX yolu):

| Görüntü | Tespit | Kutuların kapladığı alan |
|---|---:|---|
| ornek-enkaz-1.webp | 2 | %96 · %57 |
| ornek-enkaz-2.webp | 1 | %100 |
| ornek-enkaz-3.webp | 1 | %93 |
| giris-hero.webp | 1 | %97 |
| og-kapak-1.jpg | 3 | %0 · %1 · %1 |
| og-kapak-2/3/.jpg | 0 | — |

## Sebep: eğitim etiketlerinin kendisi

`results/egitim/gorseller/rebuild_vision_yolo11m_v3__labels.jpg`
genişlik–yükseklik grafiğinde **(1,0 · 1,0) noktasında yoğun bir yığın**
var: eğitim veri setindeki etiketlerin önemli bir bölümü tüm görüntüyü
kaplayan kutulardır. Üç kaynak veri seti (Mendeley CODD,
broken-glass-kaggle, wood-0nvcu) büyük ölçüde "bu fotoğrafın tamamı şu
malzemedir" biçiminde etiketlenmiş.

Model tam olarak öğrendiği şeyi yapıyor: bazı görüntülerde bir nesneyi
konumlandırıyor (%0–1), bazılarında kareye **bütün olarak** karar
veriyor (%93–100). Arada örnek yok.

## Çözüm: doğru olanı göstermek

Böyle bir çıktıyı kenarlara yapışan sıkı bir kutu gibi çizmek **yanlış
beyandır** — model bir nesneyi çerçevelediğini değil, kareye bütün
olarak karar verdiğini söylüyor.

`web/src/bilesenler/TespitKutulari.tsx`: kutu karenin **%85'inden**
fazlasını kaplıyorsa

- kenarlara yapıştırılmaz, içeriden boşluk bırakılır
- kenarlık kesikli çizilir
- etiket **"GÖRÜNTÜ GENELİ · Ahşap · %94,1995 · ÖN TAHMİN"** olur
- ekran okuyucu "görüntünün geneli için" der

Eşik ölçülerek seçildi: yukarıdaki tabloda %1 ile %93 arasında hiç
örnek yok, yani %85 geniş bir boşluğun ortasında duruyor.

## Ne YAPILMADI ve neden

- **Kutular küçültülmedi.** Modelin çıktısını görüntüde olduğundan
  farklı göstermek, tam da bu deponun reddettiği şeydir.
- **Demo görüntüleri "modelin iyi çalıştığı" karelerle değiştirilmedi.**
  Eldeki görüntülerde zaten yalnızca `og-kapak-1.jpg` sıkı kutu veriyor
  ve o bir kapak görselidir, saha fotoğrafı değil.
- **Model yeniden eğitilmedi.** Sunuma bir gün kala eğitim değişikliği
  ölçülemez; ölçülmemiş bir model teslim edilemez.

## Sonraki sürüm için

Konumlandırma isteniyorsa eğitim veri setinin **nesne düzeyinde**
etiketlenmiş örneklerle güçlendirilmesi gerekir. Bu bir model
seçimi ya da eşik sorunu değil, **etiket sorunudur**.
