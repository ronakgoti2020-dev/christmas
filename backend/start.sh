#!/bin/sh
set -e
port="${PORT:-8000}"
exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:${port}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 60
