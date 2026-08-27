# docker/ — henüz hazır değil ⚠️

**Bu klasör bilinçli olarak boştur ve bu bir eksiktir; gizlenmemektedir.**

## Durum

Şartname **Madde 10.3**:

> "Teslim edilen proje, jüri veya teknik komite tarafından **bağımsız bir
> ortamda kurulabilir ve çalıştırılabilir olmalıdır.**"

Bu, `docker compose up` ile tek komutta çalışması anlamına gelir.
**Bugün itibarıyla bu koşul karşılanmamaktadır.**

- Karar ve gerekçe: `docs/karar-kaydi.md` **K-009**
- Hedef tarih: **03.09.2026** (takvimdeki teslim paketi kontrol günü)
- Çalışan alternatif: `docs/kurulum.md` — yerel kurulum yolu doğrulanmıştır

## Neden ertelendi

Geliştirme makinesinde Docker kurulu değildi (Docker Desktop, OrbStack,
Colima, podman — hiçbiri). Takvimde geri kalınmış durumdayken kurulum ve
imaj indirme süresi P0'ı geciktirecekti.

## Depo buna hazır

Erteleme, ileride yapılacak işi ucuzlatacak biçimde yönetildi:

- Her servisin bağımlılıkları kendi klasöründe **sürüm kilitli**:
  `api/requirements.txt`, `model-mock/requirements.txt`,
  `scripts/requirements.txt`, `web/package-lock.json`
- Yapılandırma tamamen ortam değişkenleriyle: `.env.example`
- Servisler arası bağlantı adres tabanlı (`MODEL_SERVICE_URL`,
  `VERITABANI_URL`) — konteynere taşımak yapılandırma değişikliğidir,
  kod değişikliği değil
- Veri tabanı portu `.env` ile yönetilir (geliştirmede 5433, konteynerde
  standart 5432 olacak)

Dockerfile ve `compose.yaml` eklemek **saatlik** bir iştir, günlük değil.

## Yapılacaklar

- [ ] `docker/api.Dockerfile`
- [ ] `docker/model-service.Dockerfile` (AGPL bileşeni ayrı imajda kalmalı)
- [ ] `docker/model-mock.Dockerfile`
- [ ] `docker/web.Dockerfile` (çok aşamalı: build → nginx)
- [ ] `docker/compose.yaml` (postgis/postgis imajı ile)
- [ ] **Temiz bir makinede `docker compose up` ile doğrulama**

> Son madde en önemlisidir. Kendi makinede çalışıyor olması kanıt
> değildir; Madde 10.3 bağımsız ortam istiyor.
