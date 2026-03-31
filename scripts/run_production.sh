#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -x "$ROOT_DIR/venv/bin/gunicorn" ]]; then
  echo "gunicorn is not installed in ./venv. Install requirements first."
  echo "Run: ./venv/bin/pip install -r requirements.txt"
  exit 1
fi

export FLASK_DEBUG=0
export SESSION_COOKIE_SECURE="${SESSION_COOKIE_SECURE:-1}"
export SESSION_COOKIE_SAMESITE="${SESSION_COOKIE_SAMESITE:-Lax}"

HOST="${FLASK_HOST:-0.0.0.0}"
PORT="${FLASK_PORT:-5000}"
WORKERS="${GUNICORN_WORKERS:-2}"
THREADS="${GUNICORN_THREADS:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

exec "$ROOT_DIR/venv/bin/gunicorn" \
  --bind "${HOST}:${PORT}" \
  --workers "$WORKERS" \
  --threads "$THREADS" \
  --timeout "$TIMEOUT" \
  --access-logfile - \
  --error-logfile - \
  "wsgi:application"
