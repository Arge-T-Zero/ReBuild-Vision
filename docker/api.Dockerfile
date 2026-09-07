# ReBuild Vision — API
#
# ÖNEMLİ: Bu imajda `ultralytics` BULUNMAZ. Model çıkarımı ayrı bir
# konteynerde (model-service) çalışır ve buraya yalnızca HTTP ile
# bağlanılır. Gerekçe: docs/lisans-analizi.md Bölüm 3.4 (AGPL-3.0 sınırı).

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /uygulama

# Bağımlılıklar önce kopyalanır: kod değiştiğinde katman önbelleği korunur.
COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

# Uygulama kodu ve çalışma zamanında okunan yapılandırma dosyaları.
COPY api/ api/
COPY siniflar.json katsayilar.json ./

# ⚠️ BU SATIR YOKTU VE JÜRİYE YANLIŞ BİLGİ GİDİYORDU.
#
# `api/app/core/config.py` → `model_metrik_ozeti()` başarım özetini
# `results/egitim/metrikler.json` dosyasından ÜRETİR; dosya yoksa
# "henüz ölçülmedi" döner. Bu metin üç yerde görünür: /sistem/durum,
# arayüzün altbilgisi ve İNDİRİLEN HER RAPORUN künyesi.
#
# Dosya imaja kopyalanmadığı için, konteynerde çalışan sistem
# "model henüz ölçülmedi" diyordu — README aynı anda test mAP50 = 0,4334
# ilan ederken. Yani jürinin çalıştıracağı sürüm, deponun kendi
# ölçümünü yalanlıyordu.
COPY results/egitim/metrikler.json results/egitim/metrikler.json
# Açılışta göç ve demo verisi çalıştırılır (docker/baslat-api.sh).
#
# ⚠️ BETİK TEK BAŞINA YETMEZ — OKUDUĞU DOSYALAR DA GELMELİ.
#
# 07.09.2026'da canlı dağıtım tam burada çöktü:
#   FileNotFoundError: '/uygulama/scripts/demo_tespitleri.json'
#
# Sebep: yalnızca `demo_veri.py` kopyalanıyordu. Eskiden sorun çıkarmıyordu
# çünkü betik ilk demo sahasını görünce hemen dönüyor, o dosyaya hiç
# ulaşmıyordu. Sürüm damgası eklenince damga EN BAŞTA hesaplanır oldu ve
# eksiklik ilk açılışta ortaya çıktı.
COPY scripts/demo_veri.py scripts/demo_veri.py

# Demo tespitlerinin GERÇEK model çıktısı — senaryonun parmak izi bundan
# hesaplanır (demo_veri.py: TESPITLER_YOLU).
COPY scripts/demo_tespitleri.json scripts/demo_tespitleri.json

# Sentetik demo görselleri. Render ücretsiz katmanında dosya sistemi her
# dağıtımda sıfırlanır; betik eksik görselleri buradan geri kopyalar
# (demo_veri.py: KAYNAK_GORSELLER). Bunlar imajda yoksa arayüzde tespit
# kutularının yerinde kırık görsel ikonu kalır.
COPY web/public/gorseller/ornek-enkaz-1.webp \
     web/public/gorseller/ornek-enkaz-2.webp \
     web/public/gorseller/ornek-enkaz-3.webp \
     web/public/gorseller/
COPY docker/baslat-api.sh /baslat-api.sh
RUN chmod +x /baslat-api.sh

# Yüklenen görüntüler için kalıcı hacim bağlanır (compose.yaml).
RUN mkdir -p api/yuklenenler

# Kök olmayan kullanıcı — konteyner içinde gereksiz yetki tutulmaz.
RUN useradd --create-home --uid 10001 rebuild \
    && chown -R rebuild:rebuild /uygulama
USER rebuild

EXPOSE 8000

# Göç → demo verisi → sunucu. Ayrıntı ve gerekçe betiğin başında.
CMD ["/baslat-api.sh"]
