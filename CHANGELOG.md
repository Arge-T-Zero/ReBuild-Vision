# Değişiklik Günlüğü

Biçim: [Keep a Changelog](https://keepachangelog.com/tr/1.1.0/) · tarihler
GG.AA.YYYY.

## [Yayımlanmamış]

### 27.08.2026 — Proje iskeleti

**Eklendi**
- Depo yapısı: `web/` `mobile/` `api/` `model-service/` `model-mock/`
  `docs/` `scripts/` `docker/` `results/`
- `docs/lisans-analizi.md` — bağımlılık envanteri, AGPL-3.0 / Madde 5.5
  gerilim analizi, elenen bileşenler
- `docs/karar-kaydi.md` — K-001…K-010 arası on karar
- `docs/siniflar.md` + `siniflar.json` — on malzeme sınıfı, tek doğruluk
  kaynağı
- `results/bilinen-sinirlar.md` ve `results/model-metrikleri.md`
- `model-mock` — sahte model servisi, gerçek HTTP uç noktası (port 8090)
- `api/` çekirdek katmanı: yapılandırma, roller/yetkiler, JWT + bcrypt
  güvenlik, sekiz tablodan oluşan veri modeli
- `data/bakanlik/UYARI.md` — Madde 9.1 uyarısı

**Kararlar**
- Web arayüzü React 19 + Vite + TypeScript seçildi (K-001)
- `react-leaflet` **reddedildi** — `Hippocratic-2.1` lisansı Madde 5.5
  devrini kirletiyor; çıplak `leaflet` (BSD-2) kullanılacak (K-002)
- `psycopg` yerine `asyncpg` (Apache-2.0) — gereksiz LGPL yüzeyinden
  kaçınıldı (K-003)
- `dogrulama_durumu` rapor gövde metnine göre belirlendi:
  `beklemede | onaylandi | duzeltildi | belirsiz` (K-004)
- Eğitim veri seti CDW-Seg (CC0), on sınıf kabul edildi (K-006)
- `konteyner` sınıfı miktar hesabına girmez (K-007)
- PostgreSQL 17 + PostGIS 3.6, port 5433 (K-008)

**Bilinen boşluklar**
- 🔴 Docker paketi hazır değil — Madde 10.3 henüz karşılanmıyor (K-009)
- 🟡 `LICENSE` kararı mentör görüşmesi bekliyor (K-010)
- 🔴 Eğitim verisinde cam ve seramik sınıfı yok
  (`results/bilinen-sinirlar.md` B.1)
