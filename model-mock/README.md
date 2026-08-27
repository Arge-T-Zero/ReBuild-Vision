# model-mock — SAHTE model servisi

Gerçek YOLO11 servisi hazır olana kadar `api/`'nin konuştuğu **gerçek bir
HTTP uç noktası**. Kod içinde sabit dizi değildir; `api/` bu servisi ağ
üzerinden çağırır, tıpkı gerçek servisi çağıracağı gibi.

## Neden ayrı bir servis

İki nedeni var:

1. **Sözleşme doğrulaması.** `api/` sahte ile gerçek servis arasında geçerken
   tek bir ortam değişkeni (`MODEL_SERVICE_URL`) değişir, kod değişmez.
2. **AGPL sınırı.** Gerçek servis `ultralytics` (AGPL-3.0) kullanacak.
   `api/` hiçbir zaman o kütüphaneyi import etmez.
   Bkz. `docs/lisans-analizi.md` Bölüm 3.4.

## Çalıştırma

```bash
pip install -r model-mock/requirements.txt
uvicorn app:app --app-dir model-mock --port 8090 --reload
```

## Uç noktalar

| Yöntem | Yol | Açıklama |
|---|---|---|
| GET | `/health` | Servisin sahte olduğunu bildirir |
| GET | `/siniflar` | `siniflar.json` içeriğini döner |
| POST | `/predict` | multipart görüntü → tespit listesi |

## Determinizm

Çıktı, görüntü içeriğinin SHA-256 özetinden türetilen bir tohumla
üretilir. **Aynı görüntü her zaman aynı sonucu verir** — demo provası
tekrarlanabilir olsun diye.

## Garantiler

- Her yanıtta `"sahte": true` bayrağı bulunur.
- Her tespitte `bbox_format` **doludur** (`pixel_absolute_original`).
- Her yanıtta **en az bir** tespit `confidence < 0.50` ve
  `needs_review: true` olur — final demosunun 4. adımı (düşük güvenli
  kaydın otomatik uzman kuyruğuna düşmesi) her seferinde gösterilebilsin
  diye.
- `konteyner` sınıfı üretilebilir; `malzeme_mi: false` olduğu için miktar
  hesabına `api/` tarafında girmez (`docs/karar-kaydi.md` K-007).

## Sahtelik işareti

Talimat Bölüm 9.5 gereği sahtelik gizlenmez:
`model_license` alanı `"YOK - SAHTE SERVIS"`, model adı
`yolo11-rebuild-SAHTE` ve `sahte: true` bayrağı. Arayüz bu bayrağa bakarak
ekranda kalıcı "SAHTE MODEL SERVİSİ" rozeti gösterir.

Örnek çıktı: `ornek_cikti_SAHTE.json`
