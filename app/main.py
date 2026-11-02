import os, sqlite3, secrets, string
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import urllib.request

BASE = Path(__file__).resolve().parent.parent
WEB = BASE / "web"
DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB = DATA_DIR / "radio.db"

app = FastAPI(title="AI RADIO LIVE", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "dev-only-change-me"))
app.mount("/assets", StaticFiles(directory=WEB / "assets"), name="assets")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL, alias TEXT NOT NULL, genre TEXT NOT NULL,
            style TEXT DEFAULT '', theme TEXT NOT NULL, language TEXT DEFAULT 'Español',
            voice TEXT DEFAULT 'Indiferente', mood TEXT DEFAULT '', details TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Recibida',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )""")
init_db()

def page(name):
    return (WEB / name).read_text(encoding="utf-8")

def is_admin(request: Request):
    return bool(request.session.get("admin"))

@app.get("/", response_class=HTMLResponse)
def home():
    return page("index.html")

@app.get("/peticiones.html", response_class=HTMLResponse)
def requests_page():
    return page("peticiones.html")

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    if not is_admin(request):
        return page("login.html")
    return page("admin.html")

@app.get("/api/status")
def status():
    with db() as con:
        total = con.execute("SELECT COUNT(*) n FROM requests").fetchone()["n"]
        emitted = con.execute("SELECT COUNT(*) n FROM requests WHERE status='Emitida'").fetchone()["n"]
    return {"station": "AI RADIO LIVE", "status": "online", "requests_total": total, "requests_emitted": emitted}

@app.post("/api/requests")
def create_request(
    alias: str = Form(...), genre: str = Form(...), theme: str = Form(...),
    style: str = Form(""), language: str = Form("Español"),
    voice: str = Form("Indiferente"), mood: str = Form(""), details: str = Form("")
):
    fields = [alias.strip(), genre.strip(), theme.strip()]
    if not all(fields) or any(len(x) > 100 for x in fields):
        raise HTTPException(400, "Completa nombre, género y temática (máximo 100 caracteres).")
    code = "AIR-" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))
    now = datetime.now(timezone.utc).isoformat()
    with db() as con:
        con.execute("""INSERT INTO requests
        (code,alias,genre,style,theme,language,voice,mood,details,status,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,'Recibida',?,?)""",
        (code, fields[0][:40], fields[1], style[:160], fields[2], language[:40],
         voice[:40], mood[:60], details[:1000], now, now))
    return {"ok": True, "code": code, "status": "Recibida"}

@app.get("/api/requests/{code}")
def get_request(code: str):
    with db() as con:
        row = con.execute("SELECT code,alias,genre,theme,status,created_at,updated_at FROM requests WHERE code=?", (code.upper(),)).fetchone()
    if not row:
        raise HTTPException(404, "No encontramos esa petición.")
    return dict(row)

@app.post("/api/admin/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if secrets.compare_digest(username, os.getenv("ADMIN_USER", "admin")) and secrets.compare_digest(password, os.getenv("ADMIN_PASSWORD", "cambia-esta-clave")):
        request.session["admin"] = True
        return RedirectResponse("/admin", status_code=303)
    raise HTTPException(401, "Usuario o contraseña incorrectos.")

@app.post("/api/admin/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin", status_code=303)

@app.get("/api/admin/requests")
def admin_requests(request: Request):
    if not is_admin(request):
        raise HTTPException(401, "No autorizado")
    with db() as con:
        rows = con.execute("SELECT * FROM requests ORDER BY created_at DESC LIMIT 300").fetchall()
    return [dict(r) for r in rows]

@app.patch("/api/admin/requests/{request_id}")
async def update_request(request: Request, request_id: int):
    if not is_admin(request):
        raise HTTPException(401, "No autorizado")
    body = await request.json()
    allowed = {"Recibida", "En cola", "En producción", "Pendiente de revisión", "Aprobada", "Programada", "Emitida", "Rechazada"}
    new_status = body.get("status")
    if new_status not in allowed:
        raise HTTPException(400, "Estado no válido")
    now = datetime.now(timezone.utc).isoformat()
    with db() as con:
        cur = con.execute("UPDATE requests SET status=?, updated_at=? WHERE id=?", (new_status, now, request_id))
        if cur.rowcount == 0:
            raise HTTPException(404, "Petición no encontrada")
    return {"ok": True, "status": new_status}

@app.get("/stream")
def stream():
    url = "http://icecast:8000/live.mp3"
    try:
        upstream = urllib.request.urlopen(url, timeout=5)
    except Exception:
        return JSONResponse({"error": "La emisión todavía no está disponible. Comprueba que Liquidsoap esté emitiendo."}, status_code=503)
    return StreamingResponse(upstream, media_type="audio/mpeg", headers={"Cache-Control": "no-cache", "icy-name": "AI RADIO LIVE"})
