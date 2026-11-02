# AI RADIO LIVE — MVP

Emisora web con reproductor de streaming, peticiones musicales, panel de administración y automatización de audio.

## Qué incluye
- Web pública responsive (`/`) con reproductor conectado al stream Icecast.
- Formulario independiente (`/peticiones.html`) y seguimiento por código.
- API FastAPI + SQLite para registrar y moderar peticiones.
- Panel protegido (`/admin`) para aprobar/rechazar peticiones.
- Icecast + Liquidsoap en Docker Compose para emitir una lista de archivos de audio continuamente.
- Carpeta persistente `music/` para el catálogo musical.

## Requisitos
Docker y Docker Compose.

## Puesta en marcha
1. Copia `.env.example` a `.env` y cambia `ADMIN_PASSWORD` e `ICECAST_SOURCE_PASSWORD`.
2. Coloca archivos MP3/OGG compatibles en `music/`.
3. Ejecuta:
   ```bash
   docker compose up --build -d
   ```
4. Abre `http://localhost:8000`.
5. Radio: `http://localhost:8000/`
6. Peticiones: `http://localhost:8000/peticiones.html`
7. Administración: `http://localhost:8000/admin`
8. Stream directo: `http://localhost:8000/stream`

## Emisión
Liquidsoap lee `music/` y envía la emisión a Icecast. La lista se reproduce en bucle y se actualiza al reiniciar el servicio `radio`:
```bash
docker compose restart radio
```
Icecast sirve el flujo en el puerto interno 8000; la aplicación lo expone mediante `/stream`.

## Generación musical con IA
Este MVP no finge generar música. La generación real requiere una API y licencia de un proveedor musical. El flujo implementado es:
1. El oyente envía una petición.
2. El administrador la revisa y aprueba.
3. Se genera la canción externamente y se incorpora el audio a `music/`.
4. Se reinicia `radio` para incluir el archivo en la rotación.

La arquitectura deja preparada la integración futura con un proveedor mediante un adaptador backend. No introduzcas claves API en el navegador.

## Seguridad y producción
- Cambia todas las contraseñas de ejemplo.
- Usa HTTPS mediante un proxy inverso (Caddy/Nginx).
- Configura firewall, copias de seguridad y límites de petición.
- Para producción pública, añade CAPTCHA, política de privacidad y retención de datos.
- El panel usa sesión firmada; define `SECRET_KEY` larga y aleatoria.
- Este MVP usa SQLite: migra a PostgreSQL cuando haya concurrencia o volumen relevante.

## Variables
Consulta `.env.example`.


## Instalación en Termux (Android)

Termux puede ejecutar la API/web. Para emisión 24/7 estable, usa un VPS Linux con Docker para Icecast + Liquidsoap; Android puede suspender procesos y Docker no suele estar disponible de forma nativa.

1. Instala Termux desde una fuente mantenida (F-Droid o GitHub oficial).
2. En Termux:
   ```bash
   pkg update -y && pkg install -y git
   git clone https://github.com/USUARIO/ai-radio-live.git ~/ai-radio-live
   cd ~/ai-radio-live
   bash scripts/termux-deploy.sh
   ```
3. Si la app ya está en `~/ai-radio-live`, ejecuta `bash scripts/termux-run-local.sh`.
4. Abre `http://127.0.0.1:8000`.

## Publicar en GitHub desde Termux

Crea primero un repositorio vacío en GitHub (sin README ni licencia), y luego:
```bash
cd ~/ai-radio-live
git init
git branch -M main
git add .
git commit -m "Initial AI RADIO LIVE MVP"
git remote add origin https://github.com/USUARIO/ai-radio-live.git
git push -u origin main
```
Autentícate con un token de acceso personal cuando Git lo solicite; no guardes tokens dentro del repositorio. Alternativamente configura una clave SSH.

El script `scripts/termux-github-push.sh` prepara el commit y muestra el comando del remoto si todavía no existe.
