#!/usr/bin/env bash
set -o errexit

DB_DIR="${RENDER_DISK_PATH:-/opt/render/project/src}"
DB_PATH="${DB_DIR}/db.sqlite3"
SEED_DB_PATH="/opt/render/project/src/seed.sqlite3"

mkdir -p "${DB_DIR}"

if [ ! -f "${DB_PATH}" ] && [ -f "${SEED_DB_PATH}" ]; then
  cp "${SEED_DB_PATH}" "${DB_PATH}"
fi

python manage.py migrate --noinput
exec gunicorn dbd_config.wsgi:application --bind 0.0.0.0:${PORT:-10000}
