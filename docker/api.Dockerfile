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
# Açılışta göç ve demo verisi çalıştırılır (compose.yaml komutu).
COPY scripts/demo_veri.py scripts/demo_veri.py

# Yüklenen görüntüler için kalıcı hacim bağlanır (compose.yaml).
RUN mkdir -p api/yuklenenler

# Kök olmayan kullanıcı — konteyner içinde gereksiz yetki tutulmaz.
RUN useradd --create-home --uid 10001 rebuild \
    && chown -R rebuild:rebuild /uygulama
USER rebuild

EXPOSE 8000

CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
