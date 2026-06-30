#!/bin/sh
set -e

echo ">> Rodando seed..."
python seed.py

echo ">> Iniciando gunicorn na porta ${PORT:-5000}..."
exec gunicorn \
  --bind "0.0.0.0:${PORT:-5000}" \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  "run:app"
