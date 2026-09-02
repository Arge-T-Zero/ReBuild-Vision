# Veri Modeli

**Son güncelleme:** 27.08.2026
Şema kaynağı: `api/app/models.py` · Göç: `api/alembic/versions/`
Veri tabanı: PostgreSQL 17 + PostGIS 3.6, geometri SRID **4326**

---

## 1. Tablolar

### `kullanici`

| Alan | Tip | Not |
|---|---|---|
| `id` | int PK | |
| `eposta` | varchar(255) | benzersiz, indeksli |
| `sifre_hash` | varchar(255) | bcrypt; işlem geçmişine **yazılmaz** |
| `ad` | varchar(200) | |
| `rol` | enum, **NULL olabilir** | Kayıtta atanmaz — yönetici atar |
| `onay_durumu` | enum | `beklemede` \| `onaylandi` \| `reddedildi` |
| `olusturma_tarihi` | timestamptz | |

> `rol` alanının NULL olabilmesi bilinçlidir: **kullanıcı kayıt olurken
> kendi rolünü seçemez** (Brief Bölüm 3). Bu, kamu sistemi mantığının
> göstergesidir.

**Roller:** `yonetici` `afad` `belediye` `saha` `uzman` `yikim` `tesis`

---

### `enkaz_alani`

| Alan | Tip | Not |
|---|---|---|
| `id` | int PK | |
| `ad` | varchar(200) | |
| `konum` | `geometry(POINT, 4326)` | |
| `sinir` | `geometry(POLYGON, 4326)` | |
| `erisim_durumu` | enum | `acik` \| `kisitli` \| `kapali` |
| `sorumlu` | varchar(200) | |
| `inceleme_tarihi` | timestamptz | |
| `olusturan_id` | FK → `kullanici` | |
| `olusturma_tarihi` | timestamptz | |

---

### `goruntu`

| Alan | Tip | Not |
|---|---|---|
| `id` | int PK | |
| `enkaz_alani_id` | FK, indeksli | `ON DELETE CASCADE` |
| `dosya_yolu` | varchar(500) | |
| `konum` | `geometry(POINT, 4326)` | |
| `cekim_tarihi` | timestamptz | |
| `cihaz` | varchar(200) | |
| `kalite_durumu` / `kalite_notu` | varchar / text | |
| `genislik` / `yukseklik` | int | Kutu ölçekleme için gerekli |
| `yukleyen_id` | FK → `kullanici` | |

---

### `tespit`

| Alan | Tip | Not |
|---|---|---|
| `id` | int PK | |
| `goruntu_id` | FK, indeksli | `ON DELETE CASCADE` |
| `sinif` | varchar(50), indeksli | Modelin **ham** tahmini |
| `guven_skoru` | float | `CHECK 0 ≤ x ≤ 1` |
| `bbox` | jsonb | `{x, y, w, h}` |
| **`bbox_format`** | varchar(50) **NOT NULL** | `CHECK <> ''` |
| `konum` | `geometry(POINT, 4326)` | |
| `dogrulama_durumu` | enum, indeksli | varsayılan `beklemede` |
| `dogrulayan_id` | FK → `kullanici` | |
| `dogrulama_tarihi` | timestamptz | |
| `duzeltilen_sinif` | varchar(50) | Uzman düzeltmesi |
| `inceleme_gerekli` | bool, indeksli | Düşük güvende **otomatik** true |

#### `bbox_format` neden NOT NULL

Kutuların orijinal görüntüye göre mi yoksa modelin giriş boyutuna
(640×640) göre mi verildiği **belirsiz bırakılmaz.** Brief bunu en sık
hata kaynağı olarak işaretlemiştir.

Arayüz ölçeklemeyi bu alana bakarak yapar; format tanınmıyorsa **kutu
çizilmez** ve durum kullanıcıya söylenir — yanlış konumda kutu
göstermektense hiç göstermemek doğrudur.

#### `dogrulama_durumu` — dört değer

```
beklemede | onaylandi | duzeltildi | belirsiz
```

**`reddet` bilinçli olarak yoktur.** Raporun gövde metni üç ayrı yerde
(Bölüm 3.5, 6, 9) "onaylayacak, düzeltecek ya da belirsiz olarak
işaretleyecektir" der; Şekil 1'de bir kez geçen "reddet" alınmamıştır.
Gerekçe: bir tespiti reddetmek kaydın bilgi değerini yok eder; "belirsiz"
ise kaydı izlenebilir tutarak ikinci incelemeye açık bırakır.
Tam gerekçe: `docs/karar-kaydi.md` **K-004**.

---

### `olcum`

| Alan | Tip | Not |
|---|---|---|
| `id` | int PK | |
| `tespit_id` | FK, indeksli | |
| `tur` | enum | `alan` \| `hacim` \| `agirlik` |
| `deger` | float | `CHECK > 0` |
| `birim` | varchar(20) | |
| `yontem` | varchar(200) | **Zorunlu** — izlenebilirlik için |
| `giren_id` | FK → `kullanici` | |
| `tarih` | timestamptz | |
| `yerel_kimlik` | varchar(64), **benzersiz** | Çevrimdışı eşitleme anahtarı |

> Bu tabloda kayıt olması, miktar hesabının **tek ön koşuludur.**

#### `yerel_kimlik` neden var

Saha personeli çoğu zaman bağlantısız çalışır; kayıtlar cihazda şifreli
bir kuyrukta birikir ve bağlantı gelince toplu gönderilir (Rapor Bölüm 12).

Ağ koptuğunda istemci isteği tekrarlar ama sonucu bilemez. Bu alan
cihazda üretilir ve **benzersizdir**: aynı ölçüm iki kez gönderilse bile
bir kez yazılır. Bu koruma olmasa tek bir zayıf bağlantı ölçümleri ikiye
katlar ve miktar hesabını bozardı.

Sunucudan girilen ölçümlerde alan `NULL` kalır.

---

### `miktar_hesabi`

| Alan | Tip | Not |
|---|---|---|
| `id` | int PK | |
| `tespit_id` | FK, **benzersiz** | Tespit başına en fazla bir hesap |
| `deger_alt` | float **NOT NULL** | |
| `deger_ust` | float **NOT NULL** | |
| `birim` | varchar(20) **NOT NULL** | |
| `kullanilan_katsayi` | float **NOT NULL** | |
| `katsayi_kaynagi` | varchar(300) **NOT NULL** | Dayanak zorunlu |
| `yontem` | varchar(300) **NOT NULL** | |
| `tarih` | timestamptz | |

**CHECK kısıtları:**

```sql
CHECK (deger_alt <= deger_ust)      -- ck_miktar_aralik_tutarli
CHECK (deger_alt >= 0)              -- ck_miktar_alt_negatif_degil
CHECK (deger_ust > deger_alt)       -- ck_miktar_araliksiz_degil
```

Üçüncü kısıt kritiktir: **tek değerli miktar fiziksel olarak
yazılamaz.** `12.5 – 12.5` denemesi veri tabanı tarafından reddedilir.
Rapor Bölüm 4'teki "belirsizlik aralığı" taahhüdü şema seviyesinde
zorlanır.

> ⚠️ **Bu tabloda satır olmaması, miktarın SIFIR olduğu anlamına
> gelmez — HESAPLANMADIĞI anlamına gelir.** Ölçüm yoksa satır
> oluşturulmaz; 0 veya NULL yazılmaz. Arayüz bunu "Ölçüm girilmediği için
> miktar hesaplanmadı" olarak gösterir ve ölçüm ekleme aksiyonu sunar.

---

### `tehlikeli_kayit`

| Alan | Tip | Not |
|---|---|---|
| `id` | int PK | |
| `tespit_id` | FK, indeksli | |
| `durum` | enum | `incelemeye_yonlendirildi` \| `lab_sonucu_var` |
| `lab_sonucu_notu` | text | Sonucu **insan** girer |
| `giren_id` | FK → `kullanici` | |
| `tarih` | timestamptz | |

#### Bu tabloda bilinçli olarak BULUNMAYAN alanlar

`olasilik` · `guven_skoru` · `madde_adi_tahmini` · `risk_seviyesi` ·
`guvenli`

**Sistem tehlikeli madde teşhisi yapmaz** (Rapor 3.5). Enum yalnızca iki
değer alır; `'guvenli'` yazma denemesi veri tabanı tarafından
reddedilir — denenerek doğrulanmıştır.

Ayrıca: **analiz sonucu bulunmayan alan için "güvenli" değerlendirmesi de
yapılmaz.** Yokluk, güvenlik anlamına gelmez (Rapor 12).

---

### `islem_gecmisi`

| Alan | Tip | Not |
|---|---|---|
| `id` | int PK | |
| `kayit_tipi` | varchar(60), indeksli | Tablo adı |
| `kayit_id` | int, indeksli | Değişen satırın id'si |
| `islem` | varchar(20) | `olusturma` \| `guncelleme` \| `silme` |
| `eski_deger` | jsonb | |
| `yeni_deger` | jsonb | |
| `kullanici_id` | FK → `kullanici` | |
| `tarih` | timestamptz | |

**Opsiyonel değildir** (Rapor Bölüm 6, dördüncü yenilikçi yön). Kayıtlar
SQLAlchemy `after_flush` olay dinleyicisiyle **otomatik** yazılır; elle
çağrılmaz, dolayısıyla unutulamaz.

Yazılmayanlar: `sifre_hash` ve geometri sütunları.

---

## 2. İlişki şeması

```
kullanici ─┬─< enkaz_alani ─< goruntu ─< tespit ─┬─< olcum
           │                                     ├─── miktar_hesabi (1:1)
           │                                     └─< tehlikeli_kayit
           └─< islem_gecmisi
```

---

## 3. Malzeme sınıfları

Sınıf listesi veri tabanında **enum değildir**; `siniflar.json` dosyasından
gelir ve `tespit.sinif` bir `varchar`'dır. Gerekçe: model sınıf kümesi
değiştiğinde veri tabanı göçü gerekmesin.

Tanım ve gerekçe: `docs/siniflar.md` · Makine tarafından okunan sürüm:
`siniflar.json`

`malzeme_mi: false` işaretli sınıflar miktar hesabına ve Malzeme Kaynak
Haritası'na **girmez** (`docs/karar-kaydi.md` K-007). Bu sürümde beş
sınıfın beşi de malzemedir, yani liste bugün boştur; alan ve süzgeç
kaldırılmadı.

---

## 4. Şema doğrulama

Kuralların gerçekten SQL seviyesinde tuttuğu şu komutlarla sınanabilir:

```sql
-- 'guvenli' yazılamamalı
INSERT INTO tehlikeli_kayit (tespit_id, durum, giren_id)
VALUES (1, 'guvenli', 1);
-- ERROR: invalid input value for enum tehlikeli_durum_turu

-- bbox_format boş geçilememeli
INSERT INTO tespit (goruntu_id, sinif, guven_skoru) VALUES (1, 'metal', 0.8);
-- ERROR: null value in column "bbox_format" violates not-null constraint

-- tek değerli miktar yazılamamalı
INSERT INTO miktar_hesabi
  (tespit_id, deger_alt, deger_ust, birim, kullanilan_katsayi,
   katsayi_kaynagi, yontem)
VALUES (1, 12.5, 12.5, 'ton', 1, 'k', 'y');
-- ERROR: violates check constraint "ck_miktar_araliksiz_degil"
```
