#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

APP_DIR="${HOME}/ai-radio-live"
REPO_URL="${1:-}"
BRANCH="${2:-main}"

say(){ printf '\n\033[1;36m[AI RADIO]\033[0m %s\n' "$*"; }
fail(){ printf '\n\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2; exit 1; }

say "Comprobando Termux"
command -v pkg >/dev/null 2>&1 || fail "Este script debe ejecutarse dentro de Termux."
pkg update -y
pkg install -y git python openssh curl

if [[ -n "$REPO_URL" ]]; then
  if [[ -d "$APP_DIR/.git" ]]; then
    say "Actualizando repositorio existente"
    git -C "$APP_DIR" fetch origin
    git -C "$APP_DIR" checkout "$BRANCH"
    git -C "$APP_DIR" pull --ff-only origin "$BRANCH"
  else
    [[ ! -e "$APP_DIR" ]] || fail "$APP_DIR existe y no es un repositorio Git. Renómbralo o muévelo primero."
    say "Clonando $REPO_URL"
    git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
  fi
else
  [[ -d "$APP_DIR" ]] || fail "No existe $APP_DIR. Pasa la URL del repositorio como primer argumento."
fi

cd "$APP_DIR"
say "Preparando entorno Python"
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  say "Se ha creado .env. Edita ADMIN_PASSWORD, SECRET_KEY y contraseñas Icecast antes de exponer la app."
fi

mkdir -p music
say "Comprobando Docker"
if ! command -v docker >/dev/null 2>&1; then
  cat <<'EOF'
Docker no está disponible en este Termux.
La app FastAPI puede ejecutarse en modo local, pero Icecast/Liquidsoap 24/7
necesitan Docker en un servidor Linux/VPS o una instalación equivalente.
EOF
  say "Iniciando únicamente la web en modo local"
  export DATA_DIR="$APP_DIR/data"
  mkdir -p "$DATA_DIR"
  uvicorn app.main:app --host 0.0.0.0 --port 8000
else
  say "Iniciando stack Docker"
  docker compose up --build -d
  docker compose ps
  say "Web: http://127.0.0.1:8000"
  say "Peticiones: http://127.0.0.1:8000/peticiones.html"
  say "Admin: http://127.0.0.1:8000/admin"
fi
