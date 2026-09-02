# docker/

## Durum — neyin doğrulandığı, neyin doğrulanmadığı

> ⚠️ Bu dosyanın başlığı 02.09.2026'ya kadar **"doğrulandı ✅"** idi ve
> aynı dosyanın sonunda *"Temiz bir makinede doğrulama"* kutucuğu
> işaretsiz duruyordu. İki ifade birbirini yalanlıyordu. Aşağıdaki tablo
> neyin gerçekten çalıştırıldığını, sonraki bölüm neyin hâlâ
> çalıştırılmadığını söyler.

## Durum

Şartname **Madde 10.3**:

> "Teslim edilen proje, jüri veya teknik komite tarafından **bağımsız bir
> ortamda kurulabilir ve çalıştırılabilir olmalıdır.**"

**29.08.2026'da uçtan uca doğrulandı.** Ortam: Colima + Docker Engine
29.7.2 + Compose 5.5.0, macOS 26.5.1, Apple Silicon (arm64).

| Adım | Sonuç |
|---|---|
| Üç imajın derlenmesi (`api`, `web`, `model-mock`) | ✅ |
| Dört servisin ayağa kalkması | ✅ `veritabani`, `model-mock` **healthy** |
| Alembic göçü | ✅ 12 tablo |
| PostGIS | ✅ `3.5 USE_GEOS=1 USE_PROJ=1 USE_STATS=1` |
| `scripts/demo_veri.py` konteyner içinde | ✅ |
| Arayüz `http://localhost:8080` | ✅ HTTP 200 |
| nginx `/api` vekili | ✅ HTTP 200 |
| Giriş (`uzman@demo.local`) | ✅ |
| Yetki kuralı: `yikim` → `/gecmis` | ✅ **403** |
| Ölçüm sınırı: 10⁹ ton reddi | ✅ **422** |

Karar kaydı: `docs/karar-kaydi.md` **K-019** (K-009 bu doğrulamayla kapandı).

---

## ⚠️ Apple Silicon (M serisi Mac) — `platform` satırını silmeyin

`compose.yaml` içindeki `veritabani` servisinde şu satır vardır:

```yaml
    platform: linux/amd64
```

**Resmî `postgis/postgis` imajının arm64 sürümü yayımlanmıyor** —
manifest yalnızca `linux/amd64` içeriyor. Bu satır olmadan Apple
Silicon'lu bir makinede sistem hiç açılmaz:

```
no matching manifest for linux/arm64/v8 in the manifest list entries
```

Satır sayesinde imaj emülasyonla çalışır; açılış ~40 saniye sürer.
Doğrulama sırasında sağlık kontrolünden geçtiği görüldü.

Alternatif `imresamu/postgis:17-3.5` çok mimarilidir ve emülasyon
gerektirmez, ancak topluluk derlemesidir; resmî tedarik zinciri tercih
edildiği için seçilmedi (K-019).

## ⚠️ Zayıf bağlantı

İmaj indirmesi ağ hatasıyla kesilebilir (`failed to copy: ... EOF`).
Doğrulama sırasında `nginx:1.27-alpine` bir kez böyle düştü, komutun
tekrarında sorunsuz indi. Kalıcı bir sorun değildir; `docker compose
build` komutunu tekrar çalıştırmak yeterlidir.

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
ayrı bir imajdır (`docker/model-service.Dockerfile`, 02.09.2026'da
eklendi) ve `api` ona yalnızca `MODEL_SERVICE_URL` üzerinden bağlanır.

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
- [x] Gerçek model için `docker/model-service.Dockerfile` *(02.09.2026)*
- [x] `docker/compose.gercek-model.yaml` bindirmesi *(02.09.2026)*
- [ ] 🔴 **Gerçek model imajının derlenmesi ve çalıştırılması**

> ⚠️ **Son madde teslim öncesi mutlaka yapılmalıdır.**
>
> `model-service.Dockerfile` ve compose bindirmesi yazıldı,
> `docker compose config` ile **söz dizimi doğrulandı**, ama imaj
> **derlenemedi**: geliştirme oturumunun ağ politikası Docker kayıt
> defterinin dağıtım ağını (`production.cloudfront.docker.com`)
> engelliyor, temel imaj (`python:3.11-slim`) indirilemiyor.
>
> Yani bu iki dosya, çalıştığı **görülmemiş** koddur. Bu depoda
> "yazdım, herhalde çalışıyor" kabul edilmiyor; kutucuk bu yüzden
> işaretsiz. Doğrulama komutu aşağıdaki bölümdedir.

## Gerçek modeli çalıştırma

Varsayılan `docker compose up` **sahte** model servisini kaldırır ve
arayüzde kalıcı "SAHTE MODEL SERVİSİ" bandı gösterir. Gerçek YOLO11
modelini çalıştırmak için:

```bash
# 1. Ağırlığı yerine koyun (depoya girmez, ~40 MB — ayrıca verilir)
cp best.pt model-service/agirliklar/

# 2. Gerçek model bindirmesiyle başlatın
docker compose -f docker/compose.yaml \
               -f docker/compose.gercek-model.yaml up --build
```

Doğrulama:

```bash
curl -s http://localhost:8080/api/sistem/durum
# model_servisi.sahte  → false   olmalı
```

**Ağırlık yoksa sessiz düşüş YOKTUR:** `/health` `agirlik_yuklendi: false`
der, `/predict` **503** döner, arayüz uydurma tespit göstermez. Bu
bilinçlidir (ana talimat Bölüm 9.5) — ağırlıksız çalışmak istiyorsanız
bindirmeyi hiç kullanmayın; sahte servis, sahte olduğunu ekranda söyler.

**İlk derleme uzun sürer:** torch ve ultralytics indirilir (~1 GB).
`compose.gercek-model.yaml` bu yüzden 90 saniyelik bir başlangıç payı
tanır.

---

## Doğrulama kontrol listesi

Docker kurulduğunda sırayla:

1. `docker compose -f docker/compose.yaml up --build` hatasız tamamlanıyor
2. http://localhost:8080 arayüzü açılıyor
3. `belediye@demo.local` / `demo1234` ile giriş yapılıyor
4. Görüntü yükleniyor, tespitler "ön tahmin" etiketiyle geliyor
5. Ölçüm girilmemiş tespitte miktar alanı **boş**
6. `docker compose down -v && docker compose up` — sıfırdan yine çalışıyor
7. `docker image inspect` çıktısında `api` imajında `ultralytics` yok
8. Altbilgide **ölçülmüş** mAP değeri yazıyor ("henüz ölçülmedi" DEĞİL)
9. Gerçek model bindirmesiyle `/api/sistem/durum` → `sahte: false`
10. Ağırlık kaldırıldığında `/predict` **503** veriyor, uydurma üretmiyor
