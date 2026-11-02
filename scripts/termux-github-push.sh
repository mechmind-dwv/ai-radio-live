#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
cd "${HOME}/ai-radio-live"
git init
git branch -M main
git add .
git status --short
echo
read -r -p "¿Crear commit con estos archivos? [s/N] " answer
[[ "$answer" =~ ^[sS]$ ]] || { echo "Cancelado."; exit 0; }
git commit -m "Initial AI RADIO LIVE MVP"
if git remote get-url origin >/dev/null 2>&1; then
  git push -u origin main
else
  echo "Añade el remoto de GitHub con:"
  echo "git remote add origin https://github.com/USUARIO/REPOSITORIO.git"
  echo "Después ejecuta: git push -u origin main"
fi
