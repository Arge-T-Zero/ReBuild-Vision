#!/bin/sh
# API konteynerinin açılış betiği.
#
# Başlatma neden YAML'de değil burada:
# Render'ın `dockerCommand` alanı çok parçalı bir `sh -c "..."` dizesini
# doğru ayrıştırmıyor; komutun tamamını tek bir program adı sanıp
# "not found" (çıkış kodu 127) veriyor. Betik hem bu sorunu ortadan
# kaldırır hem de Docker Compose, Render ve yerel çalıştırmada aynı
# davranışı verir.
set -e

# Render dinlenecek portu PORT ile bildirir; yerelde ve compose'da 8000.
PORT="${PORT:-8000}"

echo ">> Şema göçü uygulanıyor"
alembic -c api/alembic.ini upgrade head

# Demo verisi betiği yeniden çalıştırılabilir: var olan kayıtları atlar.
echo ">> Demo verisi kontrol ediliyor"
python scripts/demo_veri.py

echo ">> API başlatılıyor (port $PORT)"
exec uvicorn api.app.main:app --host 0.0.0.0 --port "$PORT"
