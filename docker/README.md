# docker/ — yazıldı, henüz DOĞRULANMADI ⚠️

## Durum

Şartname **Madde 10.3**:

> "Teslim edilen proje, jüri veya teknik komite tarafından **bağımsız bir
> ortamda kurulabilir ve çalıştırılabilir olmalıdır.**"

| | Durum |
|---|---|
| Dockerfile'lar ve `compose.yaml` yazıldı | ✅ |
| YAML geçerliliği ve kopyalanan yolların varlığı sınandı | ✅ |
| **Temiz bir ortamda `docker compose up` ile çalıştırıldı** | ❌ **HENÜZ DEĞİL** |

**Madde 10.3 son satır doğrulanmadan karşılanmış sayılmaz.** Geliştirme
makinesinde Docker kurulu olmadığı için bu adım atılamadı.

- Karar ve gerekçe: `docs/karar-kaydi.md` **K-009**
- Hedef tarih: **03.09.2026** (teslim paketi kontrol günü)
- Çalışan alternatif: `docs/kurulum.md` — yerel kurulum yolu doğrulanmıştır

---

## Çalıştırma

```bash
docker compose -f docker/compose.yaml up --build
```

Tek giriş noktası: **http://localhost:8080**
Arayüz ve `/api` aynı porttan sunulur (nginx vekili), böylece jüri tek
adres kullanır.

Şema göçü ve demo verisi **açılışta otomatik** çalışır; ayrıca bir komut
gerekmez. Demo hesapları ve parolaları: `docs/kurulum.md` Bölüm 8.

### Üretim öncesi mutlaka değiştirin

```bash
export JWT_GIZLI_ANAHTAR=$(python3 -c "import secrets;print(secrets.token_urlsafe(48))")
export VERITABANI_PAROLA=$(python3 -c "import secrets;print(secrets.token_urlsafe(24))")
```

Varsayılan değerler bilinçli olarak "DEGISTIRIN" uyarısı taşır.

---

## Servisler

| Servis | İmaj / Dockerfile | Port | Not |
|---|---|---|---|
| `veritabani` | `postgis/postgis:17-3.5` | iç | PostGIS **GPL-2.0** |
| `model-mock` | `docker/model-mock.Dockerfile` | iç | Sahte servis, model ağırlığı içermez |
| `api` | `docker/api.Dockerfile` | iç | **`ultralytics` İÇERMEZ** |
| `web` | `docker/web.Dockerfile` | **8080** | Çok aşamalı derleme → nginx |

### AGPL sınırı imaj düzeyinde korunur

`api` imajına model kütüphanesi **kurulmaz**. Gerçek YOLO11 servisi
eklendiğinde ayrı bir imaj (`model-service`) olacak ve `api` ona yalnızca
`MODEL_SERVICE_URL` üzerinden bağlanacaktır — tek satırlık değişiklik.

Bu sınır `tests/test_agpl_siniri.py` ile testle korunur; yorum satırına
güvenilmez.

Gerekçe: `docs/lisans-analizi.md` Bölüm 3.4

---

## Yapılacaklar

- [x] `docker/api.Dockerfile`
- [x] `docker/model-mock.Dockerfile`
- [x] `docker/web.Dockerfile` + `docker/nginx.conf`
- [x] `docker/compose.yaml`
- [x] `.dockerignore` — Bakanlık verisinin imaja sızmasını da engeller
- [ ] **Temiz bir makinede `docker compose up` ile doğrulama**
- [ ] Gerçek model için `docker/model-service.Dockerfile`

> Son iki madde kaldı. Doğrulama en önemlisidir: kendi makinede çalışıyor
> olması kanıt değildir, Madde 10.3 bağımsız ortam istiyor.

## Doğrulama kontrol listesi

Docker kurulduğunda sırayla:

1. `docker compose -f docker/compose.yaml up --build` hatasız tamamlanıyor
2. http://localhost:8080 arayüzü açılıyor
3. `belediye@demo.local` / `demo1234` ile giriş yapılıyor
4. Görüntü yükleniyor, tespitler "ön tahmin" etiketiyle geliyor
5. Ölçüm girilmemiş tespitte miktar alanı **boş**
6. `docker compose down -v && docker compose up` — sıfırdan yine çalışıyor
7. `docker image inspect` çıktısında `api` imajında `ultralytics` yok
