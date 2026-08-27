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
# Açılışta göç ve demo verisi çalıştırılır (docker/baslat-api.sh).
COPY scripts/demo_veri.py scripts/demo_veri.py
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
