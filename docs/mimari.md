# Teknik Mimari

**Son güncelleme:** 27.08.2026

---

## 1. Genel görünüm

```
┌──────────────┐        ┌──────────────┐        ┌────────────────────┐
│   web/       │  HTTP  │    api/      │  HTTP  │  model-service/    │
│  React 19    ├───────►│   FastAPI    ├───────►│  YOLO11            │
│  Vite + TS   │        │              │        │  ** AGPL-3.0 **    │
│  Leaflet     │        │              │        └────────────────────┘
└──────────────┘        │              │              ▲
                        │              │   MODEL_SERVICE_URL
┌──────────────┐  HTTP  │              │              │
│  mobile/     ├───────►│              │        ┌────────────────────┐
│  Flutter     │        │              ├───────►│  model-mock/       │
└──────────────┘        └──────┬───────┘        │  sahte servis      │
                               │                └────────────────────┘
                               │ asyncpg
                        ┌──────▼───────────────┐
                        │ PostgreSQL 17        │
                        │ + PostGIS 3.6        │
                        │ ** GPL-2.0 **        │
                        └──────────────────────┘
```

## 2. En önemli mimari karar: model izolasyonu

**`api/` hiçbir koşulda `ultralytics` paketini import etmez.**
`api/requirements.txt` içinde bu paket yoktur ve olmayacaktır.

Neden:

- Ultralytics YOLO11 **AGPL-3.0** lisanslıdır ve §13 gereği yazılımı ağ
  üzerinden hizmet olarak sunmak kopyaleft tetikleyicisidir.
- Şartname Madde 5.5 ürünün Kuruma bedelsiz devrini istiyor. Gerilim
  `docs/lisans-analizi.md` Bölüm 3'te ayrıntılı olarak ele alınmıştır.

Uygulanan sınır:

| Kural | Uygulama |
|---|---|
| Model ayrı süreçte çalışır | `model-service/` kendi ortamında |
| Tek temas noktası | `api/app/services/model_client.py` |
| Geçiş tek değişken | `MODEL_SERVICE_URL` ortam değişkeni |
| Sözleşme modelden bağımsız | JSON şeması `docs/` içinde tanımlı |

Sonuç: YOLO11 yerine izin verici lisanslı bir modele geçilirse `api/` ve
`web/` tarafında **hiçbir kod değişmez.**

> Dürüst uyarı: süreç izolasyonu bir "AGPL kaçamağı" değildir. Asıl
> faydası hukuki koruma değil, geçiş maliyetini düşürmesi ve sınırı
> denetlenebilir kılmasıdır.

---

## 3. Backend katmanları

```
api/app/
├── main.py              uygulama girişi, CORS, yönlendirici kaydı
├── db.py                SQLAlchemy async motor + oturum
├── deps.py              kimlik ve yetki bağımlılıkları
├── geo.py               PostGIS geometri yardımcıları
├── models.py            sekiz tablo — kurallar burada zorlanır
├── schemas.py           API sözleşmesi (Pydantic)
├── core/
│   ├── config.py        ortam + siniflar.json okuma
│   ├── permissions.py   roller ve yetki kümeleri (TEK tanım yeri)
│   └── security.py      bcrypt + JWT
├── routers/             uç noktalar
└── services/
    ├── denetim.py       otomatik işlem geçmişi (olay dinleyicisi)
    ├── miktar.py        miktar kuralı — Bölüm 1.1
    ├── model_client.py  AGPL sınırı
    └── queries.py       veri katmanı filtreleri — Bölüm 1.4
```

### 3.1. Kurallar veri katmanında zorlanır

Arayüzde gizlemek yeterli sayılmaz. Aşağıdakiler SQL seviyesinde
denenerek doğrulanmıştır:

| Kural | Nerede | Denendiğinde |
|---|---|---|
| Tehlikeli madde teşhisi yok | `tehlikeli_durum_turu` enum | `'guvenli'` yazılamaz — enum hatası |
| `bbox_format` zorunlu | `NOT NULL` + `CHECK <> ''` | NULL yazılamaz |
| Miktar tek değer olamaz | `CHECK deger_ust > deger_alt` | `12.5–12.5` reddedilir |
| Ölçüm yoksa miktar yok | `services/miktar.py` | Satır **oluşturulmaz** |
| Doğrulanmamış kayıt hesaba girmez | `services/queries.py` | Sorgudan elenir |

### 3.2. İzlenebilirlik otomatiktir

`services/denetim.py` bir SQLAlchemy `after_flush` olay dinleyicisidir.
Her `INSERT`/`UPDATE`/`DELETE` `islem_gecmisi` tablosuna eski ve yeni
değerleriyle düşer.

- **Elle çağrılmaz** — bir uç nokta yazarken kayıt tutmayı unutmak mümkün
  değildir.
- `before_flush` yerine `after_flush` kullanılır: `before_flush` anında
  yeni kayıtların `id` değeri henüz atanmamış olur.
- Geçmiş satırları Core `insert()` ile yazılır; `after_flush` içinde
  session'a ORM nesnesi eklemek aynı işlemde yazılacağını garanti etmez.
- Parola özetleri ve geometri sütunları geçmişe **yazılmaz**.

### 3.3. İnsan kararı modelin tahminini geçersiz kılar

Miktar, harita ve rapor hesaplarında kullanılan **geçerli sınıf**:

```sql
COALESCE(tespit.duzeltilen_sinif, tespit.sinif)
```

Uzman bir tespiti düzelttiğinde bütün hesaplar düzeltilen sınıfa göre
yeniden yapılır. Modelin ham tahmini `tespit.sinif` alanında ve
`islem_gecmisi`'nde izlenebilirlik için korunur.

Bu, raporun "insan denetimli yapay zekâ" iddiasının kod karşılığıdır.

---

## 4. Kimlik ve yetki

- **bcrypt** parola özeti, **JWT (HS256)** oturum jetonu. Tamamen yerel;
  hiçbir bulut kimlik servisi kullanılmaz (Madde 9.1 / 10.5).
- Kullanıcı kayıt olurken **kendi rolünü seçemez**: `rol=None`,
  `onay_durumu=beklemede` ile başlar. İsteğe `rol` alanı eklense bile
  şema bunu yok sayar (denenerek doğrulanmıştır).
- Yetki kontrolü **API katmanında**, FastAPI bağımlılığı olarak
  (`deps.rol_gerekli`). Roller tek yerde tanımlıdır:
  `core/permissions.py`.
- Saha görünürlüğü sorgu seviyesinde filtrelenir
  (`queries.gorulebilir_alanlar`).

---

## 5. Frontend

- React 19 + Vite + TypeScript + Tailwind 4.
- Harita: **çıplak Leaflet (BSD-2)**. `react-leaflet` lisansı
  (`Hippocratic-2.1`) nedeniyle kullanılmaz — `docs/karar-kaydi.md` K-002.
  React entegrasyonu `src/lib/leaflet/` altındaki kendi sarmalayıcımızdır.
- Yönlendirme basit durum makinesidir; yönlendirici kütüphanesi eklenmedi
  (9 günlük kapsamda gerek yok, bağımlılık azaltıldı).
- Sınıf renkleri ve etiketleri `/sistem/siniflar` uç noktasından gelir —
  arayüzde sabit sınıf listesi yoktur.

---

## 6. Sınıf tanımı tek kaynaktan

`siniflar.json` (depo kökü) sınıf listesinin **tek doğruluk kaynağıdır**.

- `model-mock` bu dosyayı okur.
- `api` bu dosyayı okur (`core/config.py`).
- `web` sınıfları API'den alır.

Sınıf adları hiçbir yerde elle yazılmaz. `malzeme_mi: false` işaretli
sınıflar (şu an `konteyner`) miktar ve harita hesaplarına girmez.

---

## 7. Bilinen mimari boşluklar

| Boşluk | Etki | Durum |
|---|---|---|
| Docker paketi yok | Madde 10.3 karşılanmıyor | 🔴 K-009, hedef 03.09 |
| Uzmana/firmaya saha atama akışı yok | Bu roller yalnızca kendi ilişkili sahalarını görür | 🟡 P1 kapsamında |
| Mobil uygulama yok | P2 | ⏳ 31.08–02.09 |
| Katsayı tablosu boş | Hacim→ağırlık dönüşümü yapılamıyor | 🟡 kaynak bekliyor |
| Gerçek model bağlı değil | Sahte servis kullanılıyor | ⏳ 03.09 |
