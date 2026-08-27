# Yayın (canlı demo ortamı)

**Son güncelleme:** 27.08.2026

Bu belge, herkese açık demo bağlantısının nasıl kurulduğunu anlatır.

> ⚠️ **Canlı ortam, şartname Madde 10.3'ün yerine geçmez.** Madde 10.3
> jürinin projeyi *bağımsız bir ortamda kurup çalıştırabilmesini* istiyor;
> bunun karşılığı `docker compose` paketidir (bkz. `docker/README.md`).
> Canlı bağlantı ek bir kolaylıktır.

---

## Mimari

```
  Vercel                    Render                      Supabase
┌──────────────┐  /api/*  ┌─────────────────┐  SQL   ┌──────────────┐
│ web (React)  ├─────────►│ api (FastAPI)   ├───────►│ PostgreSQL   │
│ statik dosya │          │                 │        │ + PostGIS    │
└──────────────┘          └────────┬────────┘        └──────────────┘
                                   │ HTTP
                          ┌────────▼────────┐
                          │ model servisi   │  ← AGPL sınırı burada
                          └─────────────────┘
```

`/api` yönlendirmesi `web/vercel.json` içindedir. Böylece arayüz kodu hem
geliştirmede hem canlıda `/api/...` çağırır ve değişmez; CORS sorunu da
doğmaz çünkü istek tarayıcı için aynı kökenden gelir.

---

## ⚠️ Veri kuralı — istisnasız

Bu ortamda **yalnızca sentetik demo verisi** bulunur.

Bakanlık tarafından sağlanan veri ve maskelenmemiş saha fotoğrafı buraya
**asla** yüklenmez (şartname Madde 9.1 ve 10.5). Bu bir tavsiye değil,
yasaktır.

Demo hesapları herkese açıktır (`demo1234`); bağlantıyı bilen herkes giriş
yapıp görüntü yükleyebilir. Bu bilinçli kabul edilmiş bir risktir
(`docs/karar-kaydi.md` K-013).

---

## 1. Supabase — veri tabanı

### 1.1. Proje oluştur

1. https://supabase.com → **Start your project** → GitHub ile giriş
2. **New project**
3. Alanlar:
   - **Name:** `rebuild-vision`
   - **Database Password:** güçlü bir parola üretin ve **kaydedin** —
     sonra bir daha gösterilmez
   - **Region:** `Central EU (Frankfurt)` — Türkiye'ye en yakın ücretsiz
     bölge
   - **Plan:** Free
4. **Create new project** → kurulum 1–2 dakika sürer

> Parolada `@ : / ? # [ ] %` gibi karakterler varsa bağlantı dizesinde
> sorun çıkarır. Yalnızca harf ve rakam kullanmak en pratiği.

### 1.2. PostGIS'i etkinleştir

Sistem coğrafi geometri kullanır; PostGIS olmadan şema göçü **başarısız
olur**.

Sol menü → **SQL Editor** → **New query** → şunu çalıştırın:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

Doğrulama — aynı editörde:

```sql
SELECT PostGIS_Version();
```

Sürüm numarası dönmelidir. Dönmüyorsa devam etmeyin.

### 1.3. Bağlantı dizesini al

Sol menü → **Connect** (üst barda) → **Connection String** →
**Session pooler** sekmesi.

> **Neden Session pooler?**
> Üç seçenek var: *Direct*, *Transaction pooler* (port 6543) ve
> *Session pooler* (port 5432).
> - *Direct* yalnızca IPv6; Render'ın ücretsiz katmanında sorun çıkarır.
> - *Transaction pooler* hazırlanmış sorguları (prepared statements)
>   desteklemez; `asyncpg` bunları kullanır, bağlantı kopar.
> - **Session pooler** ikisini de çözer. Bunu seçin.

Dize şuna benzer:

```
postgresql://postgres.abcdefghijklm:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
```

### 1.4. Dizeyi uygulamanın beklediği biçime çevir

İki değişiklik gerekir:

1. `postgresql://` → **`postgresql+asyncpg://`**
2. `[YOUR-PASSWORD]` yerine gerçek parolanız

Sonuç:

```
postgresql+asyncpg://postgres.abcdefghijklm:PAROLANIZ@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
```

Bu dizeyi bir sonraki adımda Render'a gireceksiniz. **Hiçbir yere commit
etmeyin, sohbete yapıştırmayın.**

---

## 2. Render — API ve model servisi

### 2.1. Blueprint ile kur

1. https://render.com → GitHub ile giriş
2. **New** → **Blueprint**
3. `Arge-T-Zero/ReBuild-Vision` deposunu seçin
4. Render `render.yaml` dosyasını okuyup iki servis önerir:
   `rebuild-vision-model` ve `rebuild-vision-api`
5. **Apply**

### 2.2. Veri tabanı dizesini gir

Render kurulum sırasında `VERITABANI_URL` değerini soracak (dosyada
`sync: false` işaretli, yani depoya yazılmaz).

Adım 1.4'te hazırladığınız dizeyi yapıştırın.

Diğer değişkenler otomatik gelir:

| Değişken | Değer | Not |
|---|---|---|
| `ORTAM` | `uretim` | Varsayılan JWT anahtarıyla açılışı engeller |
| `JWT_GIZLI_ANAHTAR` | *(Render üretir)* | Kimse görmez, kopyalanmaz |
| `MODEL_SERVICE_URL` | model servisinin adresi | |
| `IZIN_VERILEN_KAYNAKLAR` | Vercel adresi | |

### 2.3. İlk açılışta ne olur

`rebuild-vision-api` servisi açılırken sırayla:

1. `alembic upgrade head` → sekiz tabloyu Supabase'de oluşturur
2. `python scripts/demo_veri.py` → sekiz sentetik demo hesabı ekler
3. `uvicorn` → API'yi başlatır

İlk derleme 5–10 dakika sürebilir.

### 2.4. Doğrula

```bash
curl https://rebuild-vision-api.onrender.com/sistem/durum
```

`model_servisi.ulasilabilir: true` dönmelidir.

> **Ücretsiz katman uyarısı:** Render ücretsiz servisleri 15 dakika
> hareketsizlikten sonra uyutur. İlk istek ~50 saniye sürer. Demo veya
> sunum öncesi bağlantıyı bir kez açıp uyandırın.

---

## 3. Vercel — arayüz

Arayüz zaten yayında: **https://re-build-vision.vercel.app**

Ayarları (ilk kurulumda yapıldı):

| Alan | Değer |
|---|---|
| Root Directory | `web` |
| Framework Preset | Vite |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Environment Variables | **hiçbiri** |

> Ortam değişkeni eklenmez. Vercel `.env.example` dosyasını okuyup yedi
> değişken önerir; **hepsi backend'e aittir.** Özellikle
> `JWT_GIZLI_ANAHTAR` buraya girilmez — orada işe yaramaz, sadece sırrı
> ikinci bir yere kopyalamış olursunuz.

### 3.1. API adresini bağla

Render adresi kesinleştiğinde `web/vercel.json` içindeki
`rewrites.destination` değerini güncelleyin:

```json
{ "source": "/api/:yol*",
  "destination": "https://rebuild-vision-api.onrender.com/:yol*" }
```

Push edin; Vercel otomatik yeniden dağıtır.

---

## 4. Uçtan uca doğrulama

```bash
# 1) Arayüz açılıyor mu
curl -sI https://re-build-vision.vercel.app/ | head -1

# 2) /api yönlendirmesi backend'e ulaşıyor mu
curl -s https://re-build-vision.vercel.app/api/sistem/durum

# 3) Giriş çalışıyor mu
curl -s -X POST https://re-build-vision.vercel.app/api/auth/giris \
  -H 'Content-Type: application/json' \
  -d '{"eposta":"belediye@demo.local","parola":"demo1234"}'
```

Üçü de çalışıyorsa tarayıcıda:

1. `belediye@demo.local` / `demo1234` ile giriş
2. Alan aç → bir tespite tıkla → **miktar alanının boş kaldığını** gör
3. `uzman@demo.local` ile gir → kuyruktan bir kaydı düzelt
4. `saha@demo.local` ile ölçüm gir → miktarın **aralıkla** geldiğini gör

---

## 5. Sorun giderme

**`/api/...` 404 dönüyor**
`web/vercel.json` içindeki `destination` hâlâ yer tutucu adrestir ya da
Render servisi ayakta değildir.

**API açılmıyor, günlükte `JWT_GIZLI_ANAHTAR` hatası**
Bu bilinçli bir korumadır: `ORTAM=uretim` iken varsayılan anahtarla
başlamaz. Render'da `JWT_GIZLI_ANAHTAR` değerinin üretildiğini doğrulayın.

**`alembic upgrade head` → `type "geometry" does not exist`**
Supabase'de PostGIS etkin değildir. Adım 1.2'yi çalıştırın, sonra Render'da
servisi **Manual Deploy → Clear build cache & deploy** ile yeniden başlatın.

**Bağlantı kopuyor / `prepared statement ... already exists`**
Transaction pooler (port 6543) kullanılmıştır. **Session pooler** (port
5432) dizesine geçin — gerekçe adım 1.3'te.

**İlk istek çok yavaş (~50 sn)**
Render ücretsiz katmanı servisi uyutmuştur. Normaldir; sunum öncesi
uyandırın.
