#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
cd "${HOME}/ai-radio-live"
. .venv/bin/activate
mkdir -p data music
export DATA_DIR="$PWD/data"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
