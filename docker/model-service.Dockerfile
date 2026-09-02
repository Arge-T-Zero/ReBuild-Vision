# GERÇEK model servisi — YOLO11 çıkarımı.
#
# ⚠️ AGPL-3.0 SINIRI BU İMAJDADIR.
#
# `ultralytics` AGPL-3.0'dır. `api.Dockerfile` onu ASLA içermez ve bunu
# `tests/test_agpl_siniri.py` imaj düzeyinde de denetler. İki servis ayrı
# süreçlerde çalışır, aralarındaki tek bağ HTTP'dir.
# Gerekçe: docs/lisans-analizi.md Bölüm 3.4.
#
# NEDEN AYRI BİR DOSYA
#
# Bu imaj 02.09.2026'ya kadar YOKTU. `docker/compose.yaml` yalnızca sahte
# servisi ayağa kaldırıyordu ve compose.yaml'daki yorum hâlâ "gerçek model
# hazır olduğunda eklenecek" diyordu — oysa model 01.09'da eğitilmiş,
# ölçülmüş ve servis sözleşmesi sekiz testle doğrulanmıştı. Sonuç: jüri
# Madde 10.3 paketini kurduğunda ekranda kalıcı "SAHTE MODEL SERVİSİ"
# bandı görüyor, takımın eğittiği modeli hiç göremiyordu.
FROM python:3.11-slim

WORKDIR /uygulama

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Ultralytics ilk çalıştırmada ev dizinine ayar dosyası yazar; kök
    # olmayan kullanıcı için yazılabilir bir yer gerekiyor.
    YOLO_CONFIG_DIR=/uygulama/.ultralytics \
    MPLCONFIGDIR=/uygulama/.matplotlib

# OpenCV'nin (ultralytics bağımlılığı) çalışma zamanı kütüphaneleri.
# `opencv-python-headless` bile libGL olmadan import edilemiyor.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 \
 && rm -rf /var/lib/apt/lists/*

# torch'un CPU sürümü ayrı bir dizinden gelir ve CUDA sürümünden ~3 kat
# küçüktür (imaj ~1 GB yerine ~3 GB olurdu). `--extra-index-url` bilinçli:
# o dizine ulaşılamayan bir ağda (kurumsal vekil, kısıtlı ortam) pip
# PyPI'ye düşer ve derleme YİNE tamamlanır — yalnızca imaj büyür.
# Sürüm sabitlendiği için hangi dizinden geldiği sonucu değiştirmez.
COPY model-service/requirements.txt model-service/requirements.txt
RUN pip install --no-cache-dir \
      --extra-index-url https://download.pytorch.org/whl/cpu \
      -r model-service/requirements.txt

COPY model-service/app.py model-service/app.py
COPY model-service/data.yaml model-service/data.yaml
COPY siniflar.json ./

# Ağırlık İMAJA GÖMÜLMEZ.
#
# Dosya ~40 MB ve depoya girmiyor (model-service/agirliklar/.gitignore).
# `compose.gercek-model.yaml` bu dizini ana makineden salt okunur bağlar.
# Ağırlık yoksa servis SAHTE VERİ ÜRETMEZ: /health `agirlik_yuklendi:
# false` der, /predict 503 döner (model-service/app.py).
RUN mkdir -p model-service/agirliklar "$YOLO_CONFIG_DIR" "$MPLCONFIGDIR"

# Kök olmayan kullanıcı — api.Dockerfile ile aynı uid.
RUN useradd -u 10001 -m -s /usr/sbin/nologin uygulama \
 && chown -R uygulama:uygulama /uygulama
USER uygulama

EXPOSE 8090

# Sahte servisle AYNI port ve AYNI sözleşme; ikisi arasında geçiş tek bir
# adres değişikliğidir (tests/test_model_servisi_sozlesmesi.py).
CMD ["python", "-m", "uvicorn", "app:app", \
     "--app-dir", "model-service", "--host", "0.0.0.0", "--port", "8090"]
