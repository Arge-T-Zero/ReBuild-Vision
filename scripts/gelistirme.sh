#!/usr/bin/env bash
# ReBuild Vision — yerel geliştirme ortamını başlatır.
#
# NOT: Docker paketi henüz hazır değildir (docs/karar-kaydi.md K-009).
# Şartname Madde 10.3 tek komutla bağımsız ortamda çalıştırma istiyor;
# o boşluk 03.09'a kadar kapatılacaktır.

set -euo pipefail
cd "$(dirname "$0")/.."

PG_BIN=${PG_BIN:-/opt/homebrew/opt/postgresql@17/bin}
PGDATA=${PGDATA:-/opt/homebrew/var/postgresql@17}
PGPORT=${PGPORT:-5433}
VT=${VT:-rebuild_vision}

renk() { printf "\033[1;36m%s\033[0m\n" "$*"; }
hata() { printf "\033[1;31m%s\033[0m\n" "$*" >&2; }

renk ">> PostgreSQL kontrol ediliyor (port $PGPORT)"
if ! "$PG_BIN/pg_isready" -p "$PGPORT" -q; then
  renk "   başlatılıyor..."
  "$PG_BIN/pg_ctl" -D "$PGDATA" -l "$PGDATA/server.log" start
  sleep 3
fi
"$PG_BIN/pg_isready" -p "$PGPORT" || { hata "PostgreSQL başlatılamadı"; exit 1; }

if ! "$PG_BIN/psql" -p "$PGPORT" -d postgres -tAc \
     "select 1 from pg_database where datname='$VT'" | grep -q 1; then
  renk ">> $VT veritabanı oluşturuluyor"
  "$PG_BIN/createdb" -p "$PGPORT" "$VT"
fi
"$PG_BIN/psql" -p "$PGPORT" -d "$VT" -qc "CREATE EXTENSION IF NOT EXISTS postgis;"

[ -f .env ] || { renk ">> .env oluşturuluyor"; cp .env.example .env; }

renk ">> Veri tabanı şeması güncelleniyor"
api/.venv/bin/alembic -c api/alembic.ini upgrade head

renk ">> Sahte model servisi başlatılıyor (8090)"
./.venv-mock/bin/uvicorn app:app --app-dir model-mock --port 8090 &
MOCK_PID=$!

renk ">> API başlatılıyor (8000)"
api/.venv/bin/uvicorn api.app.main:app --port 8000 --reload &
API_PID=$!

renk ">> Web arayüzü başlatılıyor (5173)"
(cd web && npm run dev) &
WEB_PID=$!

trap 'kill $MOCK_PID $API_PID $WEB_PID 2>/dev/null' EXIT INT TERM

cat <<BILGI

  Web arayüzü        http://localhost:5173
  API                http://localhost:8000/docs
  Sahte model        http://localhost:8090/health
  Veri tabanı        localhost:$PGPORT/$VT

  Demo hesapları     scripts/demo_veri.py ile oluşturulur
  Parola             demo1234

  Durdurmak için Ctrl+C

BILGI

wait
