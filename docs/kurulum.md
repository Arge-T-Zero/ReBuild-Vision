# Kurulum Dokümanı

**Şartname Madde 10.3:** "Teslim edilen proje, jüri veya teknik komite
tarafından bağımsız bir ortamda kurulabilir ve çalıştırılabilir olmalıdır."

---

## İki kurulum yolu

### A. Docker — ÖNERİLEN

```bash
docker compose -f docker/compose.yaml up --build
# Tek adres: http://localhost:8080
```

Başka hiçbir şey kurmanız gerekmez: PostgreSQL, PostGIS, API, model
servisi ve arayüz konteynerlerden gelir. Şema göçü ve demo verisi açılışta
otomatik çalışır — giriş yaptığınızda **üç saha, üç görüntü ve sekiz
tespit** hazır bekler (hepsi sentetik, Madde 10.7).

### Gerçek modeli çalıştırma

Yukarıdaki komut **sahte** model servisini kaldırır; arayüzde kalıcı
"SAHTE MODEL SERVİSİ" bandı görürsünüz. Eğitilmiş YOLO11 modelini
çalıştırmak için ağırlık dosyasını yerine koyup bindirme dosyasıyla
başlatın:

```bash
cp best.pt model-service/agirliklar/        # ~40 MB, ayrıca verilir
docker compose -f docker/compose.yaml \
               -f docker/compose.gercek-model.yaml up --build
```

Doğrulama: `curl -s http://localhost:8080/api/sistem/durum` çıktısında
`model_servisi.sahte` **false** olmalıdır.

Ağırlık dosyası depoya girmez (büyük ikili dosyalar git geçmişini şişirir).
Ağırlık yokken servis **sahte veri üretmez**: `/predict` 503 döner ve
arayüz uydurma tespit göstermez.

⚠️ **Bu yol henüz temiz bir makinede çalıştırılmadı** — dosyalar yazıldı ve
`docker compose config` ile doğrulandı, ama imaj derlemesi geliştirme
ortamının ağ kısıtı nedeniyle denenemedi. Ayrıntı: `docker/README.md`.

İlk açılış imajların derlenmesi ve indirilmesiyle birkaç dakika sürer.
Dört servis de ayağa kalkınca `http://localhost:8080` adresinden
`uzman@demo.local` / `demo1234` ile giriş yapabilirsiniz (bütün demo
hesapları: `docs/kullanici-kilavuzu.md`).

**29.08.2026'da uçtan uca doğrulandı:** Colima + Docker Engine 29.7.2,
macOS / Apple Silicon. Dört servis ayağa kalktı, göç çalıştı (12 tablo),
PostGIS 3.5 doğrulandı, demo verisi yüklendi, arayüzden giriş yapıldı.
Karar kaydı: `docs/karar-kaydi.md` **K-019**.

> **Apple Silicon (M serisi Mac) notu**
> `compose.yaml` içindeki `platform: linux/amd64` satırını **silmeyin**.
> Resmî `postgis/postgis` imajının arm64 sürümü yayımlanmıyor; o satır
> olmadan `docker compose up` şu hatayla düşer:
> `no matching manifest for linux/arm64/v8`. Satır sayesinde imaj
> emülasyonla çalışır (açılış ~40 sn sürer).

> **Zayıf bağlantı notu**
> `docker compose build` sırasında imaj indirmesi ağ hatasıyla
> kesilebilir (`EOF`). Komutu tekrar çalıştırmak yeterlidir; indirme
> kaldığı yerden sürer.

### B. Yerel kurulum — doğrulanmıştır ✅

Docker kullanmak istemiyorsanız ya da geliştirme yapacaksanız.

Aşağıdaki adımlar geliştirme makinesinde uçtan uca çalıştırılmıştır.

---

## 1. Sistem gereksinimleri

| Bileşen | Sürüm | Not |
|---|---|---|
| Python | 3.11+ | `api/` ve `model-mock/` için |
| Node.js | 20+ | `web/` için (geliştirmede 24.5 kullanıldı) |
| PostgreSQL | 17 | PostGIS uzantısı ile |
| PostGIS | 3.6+ | Homebrew'da yalnızca PostgreSQL 17/18 için derlenir |

macOS (Homebrew):

```bash
brew install postgresql@17 postgis node python@3.11
```

---

## 2. Veri tabanı

PostGIS uzantısı PostgreSQL 17 gerektirir. Makinede başka bir PostgreSQL
sürümü 5432'de çalışıyorsa çakışmayı önlemek için 17'yi **5433**'te
başlatın (bkz. `docs/karar-kaydi.md` K-008):

```bash
PGB=/opt/homebrew/opt/postgresql@17/bin
PGDATA=/opt/homebrew/var/postgresql@17

$PGB/initdb -D "$PGDATA" -U "$USER" --encoding=UTF8 --locale=C
echo "port = 5433" >> "$PGDATA/postgresql.conf"
$PGB/pg_ctl -D "$PGDATA" -l "$PGDATA/server.log" start

$PGB/createdb -p 5433 rebuild_vision
$PGB/psql -p 5433 -d rebuild_vision -c "CREATE EXTENSION postgis;"
```

Doğrulama:

```bash
$PGB/psql -p 5433 -d rebuild_vision -tAc "SELECT PostGIS_Version();"
# 3.6 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
```

---

## 3. Ortam değişkenleri

```bash
cp .env.example .env
```

`.env` içindeki `JWT_GIZLI_ANAHTAR` **üretimde mutlaka değiştirilmelidir**:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

`.env` dosyası versiyon kontrolüne **girmez**.

---

## 4. Bağımlılıklar

```bash
# Backend
python3 -m venv api/.venv
api/.venv/bin/pip install -r api/requirements.txt

# Sahte model servisi
python3 -m venv .venv-mock
./.venv-mock/bin/pip install -r model-mock/requirements.txt

# Web arayüzü
npm --prefix web install
```

---

## 5. Şema ve demo verisi

```bash
api/.venv/bin/alembic -c api/alembic.ini upgrade head
api/.venv/bin/python scripts/demo_veri.py
```

---

## 6. Çalıştırma

Tek komut:

```bash
scripts/gelistirme.sh
```

Ya da servisleri ayrı ayrı:

```bash
./.venv-mock/bin/uvicorn app:app --app-dir model-mock --port 8090
api/.venv/bin/uvicorn api.app.main:app --port 8000 --reload
npm --prefix web run dev
```

---

## 7. Erişim adresleri

| Servis | Adres |
|---|---|
| Web arayüzü | http://localhost:5173 |
| API | http://localhost:8000 |
| API dokümantasyonu | http://localhost:8000/docs |
| Sahte model servisi | http://localhost:8090/health |
| Veri tabanı | localhost:5433 / `rebuild_vision` |

---

## 8. Demo hesapları

**Şartname Madde 10.7 gereği tüm demo hesapları sentetiktir.** `@demo.local`
alan adı ayrılmış bir üst alan adıdır; bu adresler gerçek bir posta
kutusuna karşılık gelmez.

| E-posta | Rol | Ne yapabilir |
|---|---|---|
| `yonetici@demo.local` | Yönetici | Rol atama, her şey |
| `belediye@demo.local` | Belediye yetkilisi | Alan tanımlama, görüntü yükleme, rapor |
| `afad@demo.local` | AFAD yetkilisi | Çok sahalı görünüm, rapor |
| `saha@demo.local` | Saha personeli | Görüntü yükleme, ölçüm girme |
| `uzman@demo.local` | Doğrulayıcı uzman | Onayla / düzelt / belirsiz |
| `yikim@demo.local` | Yıkım firması | Yalnızca görüntüleme |
| `tesis@demo.local` | Tesis operatörü | Yalnızca görüntüleme |
| `yeni.kullanici@demo.local` | *(rol atanmadı)* | Onay bekliyor — rol onay akışını göstermek için |

**Parola (hepsi):** `demo1234`

> `yeni.kullanici@demo.local` ile giriş denemesi bilinçli olarak **403**
> döner: "Hesabınız henüz yönetici tarafından onaylanmadı." Bu, kamu
> sistemi mantığının göstergesidir.

---

## 9. Sorun giderme

**`CREATE EXTENSION postgis` hata veriyor**
PostGIS, çalışan PostgreSQL sürümü için derlenmemiş olabilir. Kontrol:

```bash
/opt/homebrew/opt/postgresql@17/bin/pg_config --sharedir
ls $(/opt/homebrew/opt/postgresql@17/bin/pg_config --sharedir)/extension/postgis.control
```

Dosya yoksa `brew install postgis` PostgreSQL 17'yi görmüyordur;
`brew install postgresql@17` kurulu olduğundan emin olun.

**`alembic upgrade head` → `DuplicateTableError: idx_..._konum`**
GeoAlchemy2 uzamsal indeksleri kendi oluşturur. `api/alembic/env.py`
içindeki `_dahil_mi` filtresi bunları göçten dışlar; filtre kaldırılmışsa
hata döner.

**Arayüzde "Model servisine ulaşılamıyor" bandı**
`model-mock` çalışmıyordur:

```bash
curl localhost:8090/health
```

**Giriş 403 dönüyor**
Hesabın `onay_durumu` değeri `beklemede`dir. Yönetici hesabıyla giriş
yapıp rol atayın ya da `scripts/demo_veri.py` çalıştırın.

**Port 5432 çakışması**
Bu proje 5433 kullanır. `.env` içindeki `VERITABANI_URL` değerinin portu
doğru olmalıdır.

**Arayüz giriş yapamıyor / `/api` istekleri HTML döndürüyor**
Vite geliştirme sunucusu `vite.config.ts` değişikliğinden sonra "server
restarted" yazsa bile vekil (proxy) ayarını bazen yeniden yüklemez ve
`/api/*` isteklerine SPA'nın `index.html`'ini döndürür. Belirti: giriş
formu hata vermeden başarısız olur.

Kontrol — **durum koduna değil, gövdeye bakın**, ikisi de 200 döner:

```bash
curl -s localhost:5173/api/sistem/durum | head -c 60
# Beklenen: {"model_servisi":{...
# Sorunlu : <!doctype html>
```

Çözüm: geliştirme sunucusunu tamamen durdurup yeniden başlatın
(`Ctrl+C`, sonra `npm run dev`).
