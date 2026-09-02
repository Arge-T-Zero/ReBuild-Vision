# Denetim — 29.08.2026

> ⚠️ **TARİHÎ KAYIT — güncel durumu ANLATMAZ.**
>
> Bu belge 29.08.2026 günündeki durumun fotoğrafıdır ve o hâliyle
> korunuyor: neyin ne zaman doğrulandığı izlenebilsin diye. Ama o
> tarihten sonra depo çok değişti; aşağıdaki satırlar **bugün yanlıştır**:
>
> | Bu belgede yazan | Bugünkü gerçek |
> |---|---|
> | Sınıf sayısı 10 = 10 | **5 sınıf** (`docs/karar-kaydi.md` K-021) |
> | Doğrulanmış katsayı 0/9 | **2/5** (`katsayilar.json` v0.3) |
> | Raporda `konteyner` yok | `konteyner` diye bir sınıf artık **yok** |
> | Arayüzde sahte model işareti yok | Eklendi (web ve mobil) |
> | `LICENSE` kararı bekliyor, depo lisanssız | **AGPL-3.0** (K-020) |
> | Model eğitimi ve metrikler ⏳ | **Ölçüldü** (01.09.2026) |
> | İzlenen dosya 205 | 256 — arada kazayla işlenen 1.906 dosyalık bir
>   sanal ortam 02.09'da temizlendi |
>
> **Güncel durum için:** `results/teslim-denetimi.md` (02.09.2026).

Yapılan bütün işin baştan sona kontrolü. Her satır **çalıştırılarak**
doğrulanmıştır; "yazdım, herhalde çalışıyor" yok.

---

## 1. Depo

| | |
|---|---|
| Commit | 33 |
| İzlenen dosya | 205 |
| Çalışma ağacı | temiz |
| `origin/main` ile eşit | ✓ |

**Sızıntı kontrolü**

| Kontrol | Sonuç |
|---|---|
| `.env`, anahtar, model ağırlığı, ortam dosyası depoda | ✓ yok |
| `data/bakanlik/` içine atılan dosya `git status`'ta | ✓ görünmüyor |
| `data/saha-foto/` içine atılan dosya | ✓ görünmüyor |

**Kod büyüklüğü:** api 2.570 · web 3.825 · mobil 1.660 · test 1.568 ·
doküman 2.780 satır.

---

## 2. Testler ve derlemeler

| | Sonuç |
|---|---|
| Python testleri | **118 geçti** |
| Bölüm 1 kural testleri (`-m kural`) | **39 geçti** |
| Flutter `analyze` | temiz |
| Flutter testleri | 3 geçti |
| Web TypeScript | temiz |
| Web derlemesi | başarılı |

> **Denetimde bulunan ve düzeltilen sorun:** Flutter paket önbelleğinden
> `flutter_secure_storage` ve `connectivity_plus` silinmişti (disk
> temizliği sırasında). `flutter analyze` 32 hata veriyordu.
> `flutter pub get` ile geri getirildi.

---

## 3. Bölüm 1 — dört ihlal edilemez kural

### Veri tabanı katmanı (SQL'de denenerek)

| Deneme | Sonuç |
|---|---|
| `'guvenli'` tehlikeli durumu yaz | **reddedildi** ✓ |
| `bbox_format` boş bırak | **reddedildi** ✓ |
| Tek değerli miktar (`alt = ust`) | **reddedildi** ✓ |
| Güven skoru `1.5` | **reddedildi** ✓ |

Enum içerikleri:

- `tehlikeli_durum_turu`: `incelemeye_yonlendirildi | lab_sonucu_var`
  — "güvenli" yok, olasılık yok
- `dogrulama_durumu_turu`: `beklemede | onaylandi | duzeltildi | belirsiz`
  — "reddet" yok (K-004)

### Canlı sistem (üretimde denenerek)

| Deneme | Sonuç |
|---|---|
| Onaysız hesapla giriş | **HTTP 403** ✓ |
| Kayıtta rol yükseltme (`rol: yonetici` gönderildi) | `rol = None`, `onay = beklemede` ✓ |
| Tehlikeli madde kaydı yokken | `degerlendirilmedi` — "güvenli" demiyor ✓ |
| Raporda `konteyner` | **yok** ✓ (K-007) |
| Raporda ölçümsüz kayıtta miktar | **`null`** ✓ (sıfır değil) |

---

## 4. Bölüm 14 — ölçülmemiş sayı sızmış mı

| Kontrol | Sonuç |
|---|---|
| `results/model-metrikleri.md` hâlâ "henüz ölçülmedi" | ✓ |
| README ve dokümanlarda doğruluk/mAP/F1 iddiası | ✓ yok |
| `katsayilar.json` doğrulanmış katsayı | **0/9** — dayanaksız katsayıyla miktar hesaplanmıyor ✓ |

Kodda geçen "güvenli" ifadelerinin **hepsi**, o değerin
*kullanılmadığını* açıklayan yorumlardır.

---

## 5. AGPL sınırı (docs/lisans-analizi.md 3.4)

| Kontrol | Sonuç |
|---|---|
| `api/requirements.txt` içinde `ultralytics` | ✓ yok |
| `api/` kodunda `import ultralytics` | ✓ yok |
| `docker/api.Dockerfile` içinde | ✓ yok |

Bu sınır `tests/test_agpl_siniri.py` ile testle korunuyor — yorum
satırına güvenilmiyor.

---

## 6. Tutarlılık

| Kontrol | Sonuç |
|---|---|
| Malzeme renkleri `siniflar.json` = web = mobil | ✓ **10/10 birebir aynı** |
| `siniflar.json` sınıf sayısı = `docs/siniflar.md` tablosu | ✓ 10 = 10 |
| Teslim paketi (Madde 10.3) sekiz kalem | ✓ tamam |

> **Denetimde düzeltildi:** `tests/README.md` ve `CHANGELOG.md` "89 test"
> diyordu, gerçek sayı 118'di. Güncellendi.

---

## 7. Canlı sistem

| Parça | Durum |
|---|---|
| Vercel arayüz | ✓ HTTP 200 (0,4 sn) |
| OG kapağı, logo, yazı tipleri | ✓ |
| `/api` yönlendirmesi → Render | ✓ |
| Render API → model servisi | ✓ ulaşılabilir |
| Supabase PostgreSQL + PostGIS | ✓ |

Lighthouse (üretim derlemesi, üç turun ortancası):
**Erişilebilirlik 100 · En İyi Uygulamalar 100 · SEO 100 · Performans 81**

---

## 8. Açık kalanlar — dürüst liste

### Bize bağlı olanlar

| Konu | Durum |
|---|---|
| Docker temiz ortamda doğrulanmadı | 🟠 K-009 — dosyalar hazır, çalıştırılmadı |
| Android APK / iOS derlemesi | 🟠 araç zinciri kurulu değil, kaynak kod tamam |
| Mobilde fotoğraflar şifreli değil | 🟡 kayıtlı sınır — ölçüm ve jeton şifreli |
| `katsayilar.json` boş | 🟡 hacim→ağırlık hesabı yapılamıyor |
| Logo geçici | 🟡 gerçek logo koyu temada kayboluyor |
| Arayüzde sahte model işareti yok | 🟠 K-011 — itiraz kayıtlı |

### Ekibe bağlı olanlar

| Konu | Durum |
|---|---|
| **Mentör görüşmesi 0/4** | 🔴 şartname Madde 5.2 dördünü zorunlu kılıyor |
| `LICENSE` kararı | 🟡 mentör görüşmesine bağlı; depo şu an açık ve lisanssız |
| Model eğitimi ve metrikler | ⏳ Burak |
| Demo videosu | ⏳ 03.09 |

---

## Sonuç

Denetimde **üç sorun** bulundu, üçü de düzeltildi:

1. Flutter paketleri önbellekten silinmişti → geri yüklendi
2. Belgelerdeki test sayısı eskimişti (89 → 118)
3. `tests/README.md` yeni test dosyalarını listelemiyordu

Bölüm 1'in dört kuralı üç katmanda da (veri tabanı, API, canlı sistem)
denenerek doğrulandı ve tutuyor.
