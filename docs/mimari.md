# Teknik Mimari

**Son güncelleme:** 02.09.2026 — sınıf listesi 10'dan 5'e indi, Bölüm 7
(Madde 10.8) ve OGC API eklendi, bilinen boşluklar tablosu güncellendi

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

**İki ayrı soru, iki ayrı süzgeç:**

| Soru | Nerede |
|---|---|
| Bu rol bu **eylemi** yapabilir mi? | `deps.rol_gerekli()` — `permissions.py` kümeleri |
| Bu rol bu **kaydı** görebilir mi? | `queries.gorulebilir_alanlar()` (listeler) ve `queries.gorulebilir_tespitler()` (tekil kayıtlar) |

İkincisi 02.09.2026'ya kadar yalnızca liste uçlarında uygulanıyordu;
tekil kayıt uçları kapsamsızdı ve dış taraf roller id gezerek göremedikleri
sahaların tonajını okuyabiliyordu. Bkz. `docs/karar-kaydi.md` **K-023**.

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
sınıflar miktar ve harita hesaplarına girmez; bu sürümde beş sınıfın
beşi de malzeme olduğu için ayıklama listesi boştur, ama mekanizma
kaldırılmadı (`K-007`).

Sınıf listesi 02.09.2026'da **10'dan 5'e indi** — model CDW-Seg ile
değil, takımın kendi veri setiyle eğitildi. Bu yüzden `siniflar.json`
artık ikinci bir dosyaya, eğitimdeki `model-service/data.yaml`
dosyasına da bağlıdır: sıra ayrışırsa arayüz **yanlış malzeme** gösterir.
`tests/test_sinif_tanimlari.py` ikisini CI'da karşılaştırır.

---

## 7. Ölçeklenebilirlik ve entegrasyon — Madde 10.8

> **Madde 10.8:** "Projelerin teknik mimarisinde kullanılan bileşenler,
> veri akışı, API yapısı, kullanıcı rolleri, veri tabanı tasarımı,
> entegrasyon noktaları ve ölçeklenebilirlik yaklaşımı açıkça dokümante
> edilecektir. Kamu sistemlerine entegrasyon potansiyeli bulunan
> projelerde açık standartlara, REST API/OGC API benzeri servis
> yaklaşımına ve taşınabilir veri formatlarına öncelik verilmesi
> beklenir."

Maddenin yedi kaleminden altısı bu belgenin önceki bölümlerinde ve
`docs/veri-modeli.md`'de yazılıdır. Bu bölüm kalan kalemi —
**ölçeklenebilirlik yaklaşımı** — ve entegrasyon beklentisini ele alır.

### 7.1. Açık standartlar ve taşınabilir formatlar

| Beklenti | Durum |
|---|---|
| **REST API** | ✅ FastAPI · OpenAPI 3.1 şeması `/docs` ve `/openapi.json` üzerinden otomatik yayımlanır |
| **Taşınabilir veri formatı** | ✅ Rapor **GeoJSON**, **CSV** (BOM'lu, Excel/Türkçe ayraç uyumlu) ve **JSON** olarak dışa aktarılır |
| **Coğrafi standart** | ✅ Geometri **PostGIS**'te, **EPSG:4326** ile saklanır; GeoJSON çıktısı RFC 7946 koordinat sırasına uyar (boylam, enlem) |
| **Kimlik** | ✅ JWT — standart taşıyıcı jeton; dış kimlik servisine bağımlılık yok |
| **OGC API - Features** | ✅ `/ogc` altında · Core + GeoJSON uygunluk sınıfları. QGIS/ArcGIS doğrudan bağlanabilir. `oas30` **beyan edilmez** — sistem OpenAPI 3.1 üretir, karşılanmayan sınıf beyan edilmez |

Hiçbir tescilli (proprietary) veri formatı kullanılmaz. Dışa aktarılan
her dosya, sistem olmadan da okunabilir.

### 7.2. Ölçeklenebilirlik yaklaşımı

Mimari, üç bileşeni **birbirinden bağımsız ölçeklenebilir** biçimde
ayırır. Bu ayrım ölçeklenebilirlik için tasarlanmadı — AGPL sınırı için
tasarlandı (Bölüm 2) — ama sonucu ölçeklenebilirliktir:

```
web/  ──HTTP──>  api/  ──HTTP──>  model-service/
 statik            durumsuz          GPU'ya bağlı
 (CDN)             (yatay)           (ayrı ölçek)
```

| Katman | Ölçekleme biçimi | Neden mümkün |
|---|---|---|
| **web/** | Statik dosya — CDN | Sunucu tarafı çalışma yok |
| **api/** | **Yatay** — kopya ekleyerek | Durumsuz: oturum sunucuda tutulmaz (JWT), yüklenen dosya paylaşılan depoya yazılır |
| **model-service/** | **Ayrı** ölçek | Darboğaz burasıdır; GPU'ya bağlıdır ve API'den bağımsız çoğaltılabilir |
| **PostgreSQL/PostGIS** | Dikey + okuma kopyası | Yazma tek düğüm; raporlama okuma kopyasından beslenebilir |

**Kritik nokta:** Yük dengeleyici arkasına ikinci bir `api/` kopyası
koymak için kod değişikliği gerekmez — API durumsuzdur. Asıl darboğaz
model çıkarımıdır ve o zaten ayrı bir süreçtedir; `MODEL_SERVICE_URL`
bir kuyruğa ya da yük dengeleyiciye çevrilerek çoğaltılabilir.

### 7.3. Ölçeklendiğinde ilk kırılacak yerler — dürüst beyan

Bunlar bugün darboğaz değil çünkü sistem tek makinede ve demo yüküyle
çalışıyor. Gerçek yükte ilk buralar kırılır:

| Yer | Sorun | Çözüm yönü |
|---|---|---|
| **Yüklenen görüntüler** | `api/yuklenenler/` yerel diskte; ikinci bir API kopyası dosyayı göremez | Nesne depolama (S3 uyumlu) |
| **Çıkarım eşzamanlılığı** | `/predict` senkron; uzun süren istek bağlantıyı tutar | İş kuyruğu + asenkron sonuç |
| **Rapor üretimi** | Rapor istek anında hesaplanır; saha sayısı arttıkça yavaşlar | Önbellek ya da zamanlanmış üretim |
| **İşlem geçmişi** | Tek tablo, sınırsız büyür | Tarih bazlı bölümleme (partition) |

Hiçbiri için bugün ölçüm yoktur — **"şu kadar eşzamanlı kullanıcıyı
kaldırır" gibi bir sayı beyan edilmemektedir.** Yük testi yapılmamıştır.

### 7.4. Kamu sistemlerine entegrasyon noktaları

| Nokta | Bugün | Entegrasyonda |
|---|---|---|
| Kimlik | Yerel JWT | Kurum kimlik sağlayıcısı (OIDC) eklenebilir; kimlik katmanı tek dosyada izole |
| Coğrafi veri | GeoJSON dışa aktarım | OGC API - Features (7.1) |
| Atık sınıfı | `siniflar.json` tek kaynak | Atık kodu eşlemesi bu dosyaya eklenir |
| Model | `MODEL_SERVICE_URL` | Kurumun kendi modeli aynı sözleşmeyle takılabilir |

Son satır önemlidir: model servisi sözleşmesi
(`tests/test_model_servisi_sozlesmesi.py`) sabitlenmiştir. Kurum kendi
modelini bu sözleşmeye uygun bir servis olarak sunarsa, sistemin geri
kalanında **tek satır değişmez.**

---

## 8. Bilinen mimari boşluklar

| Boşluk | Etki | Durum |
|---|---|---|
| Uzmana/firmaya saha atama akışı yok | Uzman görünürlüğü **iş üzerinden** türetiliyor: inceleme bekleyen ya da kendi doğruladığı tespiti içeren sahaları görür. Yıkım firması ve tesis operatörü yalnızca ilişkili sahalarını görür | 🟡 ara çözüm |
| Katsayı tablosu kısmen dolu | 5 malzeme sınıfından **2'si** kaynaklı (`ahsap`, `metal`); `beton_tugla`, `cam`, `seramik` kapalı — hacim→ağırlık dönüşümü ana kütlede yapılamıyor | 🔴 kaynak bekliyor (`docs/cevresel-etki.md` Bölüm 5) |
| Eğitim veri setinin lisans beyanı eksik | Görüntülerin kaynağı ve kullanım hakkı yazılı değil; Madde 5.2 açıkça istiyor, Madde 9.2 sorumluluğu katılımcıya yüklüyor | 🔴 **teslim öncesi kapatılmalı** (`docs/lisans-analizi.md` 2.1.1) |
| `seramik` sınıfı pratikte çalışmıyor | Test mAP50 **0,0877**. Sınıf tanınıyor ama çıktısına güvenilemez; listede olması güvenilir olduğu anlamına gelmiyor | 🔴 beyan edildi (`results/model-metrikleri.md`) |
| Ağırlık dosyası depoda değil | `best.pt` boyutu nedeniyle depoya girmez; `model-service/agirliklar/` altına elle konur. Ağırlık yokken servis sahte veri üretmez, `/predict` **503** döner | 🟡 bilinçli (`model-service/README.md`) |
| Nesne depolama yok | Yatay ölçeklemede görüntüler paylaşılamaz (Bölüm 7.3) | 🟡 tek makinede sorun değil |
| Yük testi yapılmadı | Ölçeklenebilirlik iddiası ölçülmemiştir | 🟡 beyan edilmiyor |
