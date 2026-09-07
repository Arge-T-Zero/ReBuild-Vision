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

# Demo verisi betiği yeniden çalıştırılabilir ve SÜRÜME BAKAR.
#
# ⚠️ 06.09.2026'YA KADAR BURASI HİÇBİR ŞEY YAPMIYORDU. Betik ilk demo
# sahasını görünce "zaten var" deyip dönüyordu; canlı veri tabanı
# 30.08.2026'da kuruldu ve bir daha yenilenmedi. Sınıf listesi 02.09'da
# 10'dan 5'e inince ekranda artık üretilemeyecek sınıf adları kaldı.
#
# Betik artık her açılışta:
#   · eksik sentetik görselleri geri kopyalar (Render'ın dosya sistemi
#     her dağıtımda sıfırlanıyor),
#   · senaryonun sürüm damgasına bakar; damga aynıysa hiçbir kayda
#     dokunmaz, değiştiyse yalnızca sentetik demo kayıtlarını yenileyip
#     kullanıcı verisini bırakır.
#
# Tek seferlik zorlama:  DEMO_VERISI_ZORLA=1  (Render panelinden)
echo ">> Demo verisi kontrol ediliyor"
python scripts/demo_veri.py

echo ">> API başlatılıyor (port $PORT)"
exec uvicorn api.app.main:app --host 0.0.0.0 --port "$PORT"
