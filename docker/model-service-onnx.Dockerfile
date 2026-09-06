# GERÇEK model servisi — ONNX Runtime ile, DÜŞÜK BELLEKLİ.
#
# ## Neden bu imaj var
#
# `model-service.Dockerfile` aynı modeli torch + ultralytics ile
# çalıştırır ve **810 MB** tepe bellek ister (ölçüm:
# results/onnx-dogrulama.md). Render'ın ücretsiz katmanı **512 MB**
# verir. Bu yüzden canlı demo bugüne kadar SAHTE model servisiyle
# çalıştı ve arayüzde kalıcı "SAHTE MODEL SERVİSİ" bandı göründü.
#
# Aynı ağırlık ONNX Runtime ile **281 MB**'a düşer. Sınırın altında.
#
# ## Aynı model mi?
#
# Evet — aynı ağırlık, aynı sayılar. `tests/test_onnx_esdegerlik.py`
# üç şeyi doğrular: sınıf listesi aynı, ön işleme ultralytics
# `LetterBox` ile BİREBİR aynı, tespitler (sınıf/güven/kutu) aynı.
#
# ## Lisans
#
# Bu imajda `ultralytics` KURULU DEĞİLDİR; çalışma zamanı bağımlılıkları
# MIT/BSD/Apache'dir. Bu, AGPL beyanını ORTADAN KALDIRMAZ: ağırlık
# ultralytics ile eğitildi, `.onnx` dosyası meta verisinde `AGPL-3.0`
# taşır ve /health bunu bildirmeye devam eder
# (docs/lisans-analizi.md Bölüm 3).
FROM python:3.11-slim

WORKDIR /uygulama

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# `opencv-python-headless` tekerleği (wheel) bağımlılıklarının çoğunu
# kendi içinde taşır, ama HEPSİNİ değil. `ldd cv2.abi3.so` ile bulunan,
# python:3.11-slim'de BULUNMAYAN paketler:
#
#   libxcb1  libxau6  libxdmcp6  libbsd0  libmd0
#
# "headless" adına aldanmayın — X kütüphaneleri yine de bağlanır.
# Eksik olsalar `import cv2` çalışma zamanında patlardı; aşağıdaki
# doğrulama adımı bunu DERLEME zamanına çeker.
#
# curl: ağırlığı indirmek için (aşağıya bakın).
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libxcb1 libxau6 libxdmcp6 libbsd0 libmd0 \
      curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY model-service/requirements-onnx.txt model-service/requirements-onnx.txt
RUN pip install --no-cache-dir -r model-service/requirements-onnx.txt

COPY model-service/app.py model-service/app.py
COPY model-service/onnx_cikarim.py model-service/onnx_cikarim.py
COPY model-service/dogrula_kurulum.py model-service/dogrula_kurulum.py
COPY model-service/data.yaml model-service/data.yaml
COPY siniflar.json ./

# --- AĞIRLIK ---------------------------------------------------------
#
# Ağırlık depoda DEĞİLDİR (model-service/agirliklar/.gitignore) ve
# Render derlemeyi doğrudan git deposundan yapar; bağlanacak bir birim
# de yoktur. Bu yüzden ağırlık derleme sırasında yayın (release)
# varlığından indirilir.
#
# ⚠️ İNDİRME BAŞARISIZ OLURSA DERLEME DURMAZ ve SAHTE VERİ ÜRETİLMEZ.
# Servis ayağa kalkar, /health `agirlik_yuklendi: false` der ve /predict
# 503 döner. Sessizce sahte servise düşmek seçenek değildir: çağıran
# taraf gerçek modelin çalıştığını sanır (ana talimat Bölüm 9.5).
ARG AGIRLIK_URL=https://github.com/Arge-T-Zero/ReBuild-Vision/releases/download/model-v2/best.onnx
RUN mkdir -p model-service/agirliklar \
 && (curl -fsSL --retry 3 -o model-service/agirliklar/best.onnx "$AGIRLIK_URL" \
     && echo "ağırlık indirildi: $(du -h model-service/agirliklar/best.onnx | cut -f1)" \
     || echo "⚠️ ağırlık İNDİRİLEMEDİ ($AGIRLIK_URL) — servis /health ile bunu bildirecek")

ENV MODEL_AGIRLIK=/uygulama/model-service/agirliklar/best.onnx

# ⚠️ İMAJ KENDİNİ DERLEME ZAMANINDA SINAR.
#
# Eksik bir sistem kütüphanesi aksi hâlde ancak Render'da, ilk istekte
# ortaya çıkardı: servis ayağa kalkar, /health "Ağırlık yüklenemedi:
# ImportError…" der ve arayüz sahte model bandını geri getirir. Derleme
# burada patlarsa sorun yayına hiç çıkmaz.
#
# Betik ayrıca ağırlığın yüklenebildiğini ve sınıf sırasının
# siniflar.json ile uyuştuğunu görür. Ağırlık yoksa uyarır ve geçer —
# yokluk zaten /health ile bildiriliyor, uydurma üretilmiyor.
RUN python model-service/dogrula_kurulum.py

RUN useradd -u 10001 -m -s /usr/sbin/nologin uygulama \
 && chown -R uygulama:uygulama /uygulama
USER uygulama

EXPOSE 8090

# Kabuk biçimi bilinçli: Render dinlenecek portu PORT ile bildirir ve
# exec biçiminde ${PORT} genişlemez (model-mock.Dockerfile ile aynı
# gerekçe; orada çıkış kodu 127 alınmıştı).
CMD uvicorn app:app --app-dir model-service --host 0.0.0.0 --port ${PORT:-8090}
