# ReBuild Vision — SAHTE model servisi
#
# Gerçek model hazır olana kadar api/'nin konuştuğu HTTP uç noktası.
# Bu imaj hiçbir model ağırlığı içermez ve hiçbir çıkarım yapmaz.

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /uygulama

COPY model-mock/requirements.txt model-mock/requirements.txt
RUN pip install --no-cache-dir -r model-mock/requirements.txt

COPY model-mock/ model-mock/
# Sınıf listesinin tek doğruluk kaynağı; servis bunu okur.
COPY siniflar.json ./

RUN useradd --create-home --uid 10001 rebuild \
    && chown -R rebuild:rebuild /uygulama
USER rebuild

EXPOSE 8090

CMD ["uvicorn", "app:app", "--app-dir", "model-mock", \
     "--host", "0.0.0.0", "--port", "8090"]
