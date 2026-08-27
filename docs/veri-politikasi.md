# Veri Politikası

**Dayanak:** Şartname Madde 9.1, 10.5, 10.6, 10.7 · Rapor Bölüm 6
**Son güncelleme:** 27.08.2026

---

## 1. Veri envanteri — hangi veri nereden geliyor

| Veri | Kaynak | Lisans/koşul | Nerede saklanıyor | Depoya girer mi |
|---|---|---|---|---|
| CDW-Seg eğitim veri seti | Figshare (açık akademik) | CC0 1.0 | Yerel eğitim makinesi | ❌ (boyut) |
| Bakanlık tarafından sağlanan veri | Bakanlık | **Madde 9.1 — kopyalanamaz** | `data/bakanlik/` (yalnızca yerel) | ❌ **asla** |
| Saha fotoğrafları (maskelenmemiş) | Ekip çekimi | Kişisel veri içerebilir | `data/saha-foto/` | ❌ **asla** |
| Maskelenmiş örnek görseller | `scripts/maskele.py` çıktısı | — | `data/ornek/` | ✅ |
| Sentetik demo görselleri | Üretilmiş | — | `data/ornek/` | ✅ |
| Demo hesapları | `scripts/demo_veri.py` | Sentetik | Veri tabanı | ✅ (betik) |
| Yüklenen görüntüler (çalışma zamanı) | Kullanıcı | — | `api/yuklenenler/` | ❌ |

---

## 2. Bakanlık verisi — mutlak kurallar

> **Madde 9.1:** "Verilerin kopyalanması, paylaşılması veya farklı bir
> platformda kullanılması yasaktır."
>
> **Madde 10.5:** "Bakanlık tarafından sağlanan veriler, açık izin
> olmaksızın üçüncü taraf yapay zekâ servislerine veya bulut tabanlı model
> sağlayıcılarına gönderilemez."

1. Bakanlık verisi **yalnızca** `data/bakanlik/` klasöründe tutulur.
2. Bu klasörün içeriği `.gitignore` ile dışlanmıştır ve **asla commit
   edilmez.** Klasördeki `UYARI.md` bu kuralı belgeler.
3. Bakanlık verisi **hiçbir bulut servisine gönderilmez**: Supabase,
   Google Colab, barındırılan model API'leri, nesne depolama — hiçbiri.
4. **Model eğitimi bulut ortamında yapılacaksa yalnızca kendi ürettiğimiz
   veya açık kaynak (CC0/CC-BY) veriyle yapılır.** CDW-Seg bu koşulu
   karşılar; Bakanlık verisi karşılamaz.
5. Bakanlık verisi üçüncü kişilerle paylaşılmaz, ekip dışına çıkarılmaz.

### `.gitignore` doğrulaması

Klasörün **kendisi** değil, **içeriği** dışlanır — klasör dışlanırsa git
içine hiç bakmaz ve `UYARI.md` gibi izlenmesi gereken dosyalar depoya
giremez:

```gitignore
data/bakanlik/*
!data/bakanlik/.gitkeep
!data/bakanlik/UYARI.md
```

Doğrulama (her `.gitignore` değişikliğinden sonra çalıştırılmalıdır):

```bash
touch data/bakanlik/sizinti_testi.csv
git status --porcelain data/ | grep sizinti_testi && echo "SIZINTI VAR" || echo "temiz"
rm data/bakanlik/sizinti_testi.csv
```

---

## 3. Kişisel veri ve maskeleme

> **Rapor Bölüm 6:** "gereksiz yüz ve plaka görüntülerinin maskelenmesi"

- Saha fotoğraflarında **yüz ve plaka maskelenir.**
- Maskeleme **elle değil**, `scripts/maskele.py` betiği ile yapılır —
  tekrarlanabilir ve denetlenebilir olması için.
- Maskeleme **geri döndürülemez**: çıktı yeni bir dosyadır, orijinal
  üzerine yazılmaz; orijinal `data/saha-foto/` içinde kalır ve depoya
  girmez.
- **Proje alanı dışındaki konum verisi saklanmaz** (Rapor Bölüm 6).

### Maskelemenin sınırı — dürüst beyan

`scripts/maskele.py` OpenCV'nin Haar cascade yüz sezicilerini kullanır.
Bu yöntem **her yüzü yakalamaz**: profilden bakan, kısmen kapalı, çok
küçük veya düşük ışıktaki yüzler kaçabilir. Plaka sezimi ise biçim
temellidir ve daha da kırılgandır.

**Bu nedenle betiğin çıktısı otomatik olarak "temiz" sayılmaz.** Her
maskelenmiş görsel, depoya veya sunuma girmeden önce **gözle kontrol
edilir.** Betik, insan kontrolünü ortadan kaldırmaz; kolaylaştırır.

---

## 4. Demo ortamı

> **Madde 10.7:** "Demo ortamlarında anonimleştirilmiş, sentetik veya
> maskeleme uygulanmış veri kullanılması esastır."

- Tüm demo hesapları `@demo.local` alan adındadır. `.local` ayrılmış bir
  üst alan adıdır; bu adresler **gerçek bir posta kutusuna karşılık
  gelmez** ve dışarıya e-posta gönderilemez.
- **Gerçek e-posta adresi hiçbir yerde kullanılmaz** — ekip üyelerinin
  kendi adresleri dahil.
- Demo görselleri sentetiktir ve dosya adında/içeriğinde bunu belirtir
  (`ornek_saha_SAHTE.jpg`).
- Demo veri tabanı gerçek saha kaydı içermez.

---

## 5. Çevrimdışı mobil kayıtlar — şifreli saklama

> **Rapor Bölüm 12 (risk tablosu):** "Mobil kayıtların cihazda **şifreli
> olarak** geçici biçimde saklanması ve bağlantı sağlandığında
> eşitlenmesi."

Bu, raporda verilmiş somut bir taahhüttür.

- Çevrimdışı kuyruk **düz JSON dosyası olarak saklanmayacaktır.**
- Kullanılacak yöntem: platformun güvenli anahtar deposuyla korunan
  şifreli yerel depolama (iOS Keychain / Android Keystore üzerinden
  türetilen anahtar ile şifrelenmiş veri tabanı).
- Eşitleme başarıyla tamamlandığında yerel kopya **silinir.**

**Durum:** ⏳ Mobil uygulama (P2) henüz geliştirilmemiştir. Kullanılan
kütüphane ve yöntem, geliştirme tamamlandığında bu bölüme yazılacaktır.
Yöntem belirlenmeden "şifreli" iddiası yapılmayacaktır.

---

## 6. Erişim — kim neyi görüyor

Rol tabanlı erişim **API katmanında** uygulanır; arayüzde gizleme yeterli
sayılmaz. Ayrıntı: `docs/mimari.md` ve `api/app/core/permissions.py`.

| Rol | Görebildiği |
|---|---|
| Yönetici | Tümü |
| AFAD yetkilisi | Çok sahalı görünüm |
| Belediye yetkilisi | Kendi oluşturduğu/ilişkili sahalar |
| Saha personeli | Kendi sahası |
| Doğrulayıcı uzman | Atandığı sahalar |
| Yıkım firması | Yalnızca kendi sahası (salt okunur) |
| Tesis operatörü | Kendine yönlendirilen kayıtlar (salt okunur) |

**Bilinen sınır:** Uzmana ve yıkım firmasına saha atama akışı henüz
uygulanmamıştır; bu roller şu an yalnızca kendi oluşturdukları/yükledikleri
sahaları görür. İnceleme kuyruğu bundan bağımsız çalışır.

---

## 7. Parola ve kimlik verisi

- Parolalar **bcrypt** ile özetlenerek saklanır; düz metin parola hiçbir
  yerde tutulmaz.
- Parola özetleri **işlem geçmişine yazılmaz** (`denetim.py` →
  `GIZLI_ALANLAR`). Bu, kodda test edilerek doğrulanmıştır.
- Oturum jetonları JWT'dir ve varsayılan geçerlilik süresi 8 saattir.
- Kimlik doğrulama tamamen yereldir; hiçbir dış kimlik servisi
  kullanılmaz (Madde 9.1 / 10.5).

---

## 8. Saklama ve silme — Madde 10.6

> **Madde 10.6:** Yarışma sonrası veri silme yükümlülüğü — finalist
> olmayan takımlar **15 gün**, finalist takımlar **30 gün** içinde.

### Silme prosedürü

Sorumlu: takım kaptanı. Tamamlandığında bu bölüme tarih ve imza düşülür.

1. **Bakanlık verisi**
   ```bash
   rm -rf data/bakanlik/*
   ```
   Yedek kopyaların bulunduğu tüm cihazlar (kişisel bilgisayarlar, harici
   diskler) tek tek kontrol edilir.

2. **Saha fotoğrafları (maskelenmemiş)**
   ```bash
   rm -rf data/saha-foto/*
   ```

3. **Çalışma zamanı yüklemeleri**
   ```bash
   rm -rf api/yuklenenler/*
   ```

4. **Veri tabanı**
   ```bash
   /opt/homebrew/opt/postgresql@17/bin/dropdb -p 5433 rebuild_vision
   ```

5. **Bulut kopyaları** — Bakanlık verisi buluta hiç gönderilmediği için
   silinecek bulut kopyası bulunmamalıdır. Yine de eğitim ortamları
   (varsa) kontrol edilir ve kapatılır.

6. **Doğrulama** — silme sonrası kontrol:
   ```bash
   ls -la data/bakanlik/ data/saha-foto/ api/yuklenenler/
   ```
   Yalnızca `.gitkeep` ve `UYARI.md` kalmalıdır.

### Silme kaydı

| Tarih | Ne silindi | Kim | Doğrulandı |
|---|---|---|---|
| — | *(yarışma sonrası doldurulacak)* | — | — |

---

## 9. Kod deposuna girmeyecekler

`.gitignore` ile dışlananlar ve gerekçeleri:

| Yol | Gerekçe |
|---|---|
| `.env` | Gizli anahtarlar |
| `data/bakanlik/*` | Madde 9.1 |
| `data/saha-foto/*` | Kişisel veri (Madde 10.7) |
| `model-service/weights/` | Büyük ikili dosyalar |
| `api/yuklenenler/` | Çalışma zamanı kullanıcı verisi |
| `api/.venv/`, `.venv-mock/`, `web/node_modules/` | Ortam dosyaları |

Depoya **girmesi gerekenler**: `.env.example`, sahte model çıktıları
(`ornek_cikti_SAHTE.json`), demo veri şeması, maskelenmiş/sentetik örnek
görseller.
