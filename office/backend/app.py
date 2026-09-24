import os
import secrets
import sqlite3
import time
import uuid
from datetime import timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, send_file, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from database import get_db, init_db
from openapi import OPENAPI_SPEC


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("PORTAL_SECRET_KEY", secrets.token_hex(32)),
    MAX_CONTENT_LENGTH=500 * 1024 * 1024,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
)
CORS(app, supports_credentials=True)

STORAGE_ROOT = Path(os.environ.get("PORTAL_STORAGE_ROOT", "/srv/office"))
BLOCKED_EXTENSIONS = {".exe", ".bat", ".sh", ".msi", ".vbs", ".cmd"}
failed_logins = {}


def client_ip():
    return request.headers.get("X-Real-IP") or request.remote_addr or "unknown"


def log_event(user_id, username, action, detail, status):
    with get_db() as db:
        db.execute(
            "INSERT INTO activity_logs (user_id, username, action, detail, ip, status) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, action, detail, client_ip(), status),
        )


def api_error(message, status=400):
    return jsonify({"error": message}), status


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    if time.time() - session.get("last_activity", 0) > 30 * 60:
        session.clear()
        return None
    with get_db() as db:
        user = db.execute(
            "SELECT id, username, role, is_active, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    if not user or not user["is_active"]:
        session.clear()
        return None
    session["last_activity"] = time.time()
    return user


def login_required(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            return api_error("Authentication required", 401)
        return handler(user, *args, **kwargs)

    return wrapped


def admin_required(handler):
    @wraps(handler)
    @login_required
    def wrapped(user, *args, **kwargs):
        if user["role"] != "admin":
            return api_error("Admin access required", 403)
        return handler(user, *args, **kwargs)

    return wrapped


def user_payload(user):
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "is_active": bool(user["is_active"]),
        "created_at": user["created_at"],
    }


def file_payload(row):
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "username": row["username"],
        "folder": row["folder"],
        "original_name": row["original_name"],
        "size": row["size"],
        "uploaded_at": row["uploaded_at"],
    }


def file_path(row):
    folder = STORAGE_ROOT / "common" if row["folder"] == "common" else STORAGE_ROOT / "users" / Path(row["username"])
    return folder / row["stored_name"]


def ensure_storage(usernames=()):
    (STORAGE_ROOT / "common").mkdir(parents=True, exist_ok=True)
    for username in usernames:
        (STORAGE_ROOT / "users" / username).mkdir(parents=True, exist_ok=True)


@app.errorhandler(413)
def too_large(_error):
    return api_error("File exceeds the 500 MB limit", 413)


@app.route("/api/health")
def health():
    return jsonify({"status": "success", "message": "Office Portal Backend is running"})


@app.get("/api/openapi.json")
def openapi_json():
    return jsonify(OPENAPI_SPEC)


@app.get("/api/docs")
def swagger_ui():
    return """
    <!doctype html>
    <html>
      <head>
        <title>Office Portal API - Swagger UI</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
          window.onload = () => SwaggerUIBundle({
            url: '/api/openapi.json',
            dom_id: '#swagger-ui',
            withCredentials: true,
            persistAuthorization: true
          });
        </script>
      </body>
    </html>
    """


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    key = f"{client_ip()}:{username.lower()}"
    attempts = failed_logins.get(key, [])
    now = time.time()
    attempts = [attempt for attempt in attempts if now - attempt < 900]
    if len(attempts) >= 5:
        log_event(None, username or None, "login_failed", "Too many attempts; temporarily blocked", "failed")
        return api_error("Too many login attempts. Try again later.", 429)

    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or not user["is_active"] or not check_password_hash(user["password_hash"], password):
        failed_logins[key] = attempts + [now]
        detail = "Account disabled" if user and not user["is_active"] else "Invalid credentials"
        log_event(user["id"] if user else None, username or None, "login_failed", detail, "failed")
        return api_error("Account disabled, contact admin" if user and not user["is_active"] else "Username or password is incorrect", 401)

    failed_logins.pop(key, None)
    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    session["last_activity"] = time.time()
    log_event(user["id"], user["username"], "login_success", "Login successful", "success")
    return jsonify({"user": user_payload(user)})


@app.post("/api/auth/logout")
@login_required
def logout(user):
    log_event(user["id"], user["username"], "logout", "Logout successful", "success")
    session.clear()
    return jsonify({"message": "Logged out"})


@app.get("/api/auth/me")
@login_required
def me(user):
    return jsonify({"user": user_payload(user)})


@app.get("/api/dashboard/stats")
@login_required
def dashboard_stats(user):
    with get_db() as db:
        stats = db.execute(
            "SELECT COUNT(*) AS count, COALESCE(SUM(size), 0) AS bytes FROM files "
            "WHERE user_id = ? AND folder = 'personal'", (user["id"],)
        ).fetchone()
        latest = db.execute(
            "SELECT original_name, uploaded_at FROM files WHERE user_id = ? "
            "ORDER BY uploaded_at DESC LIMIT 1", (user["id"],)
        ).fetchone()
    return jsonify({"file_count": stats["count"], "storage_bytes": stats["bytes"], "last_uploaded": dict(latest) if latest else None})


@app.post("/api/files/upload")
@login_required
def upload(user):
    folder = request.form.get("folder", "personal")
    if folder not in {"personal", "common"}:
        return api_error("Folder must be personal or common")
    files = request.files.getlist("files")
    if not files:
        return api_error("No files were provided")
    target = STORAGE_ROOT / ("common" if folder == "common" else "users" / Path(user["username"]))
    target.mkdir(parents=True, exist_ok=True)
    results = []
    for uploaded in files:
        original_name = uploaded.filename or ""
        safe_name = secure_filename(original_name)
        suffix = Path(safe_name).suffix.lower()
        if not safe_name or suffix in BLOCKED_EXTENSIONS:
            log_event(user["id"], user["username"], "upload_failed", f"{original_name} - blocked file type", "failed")
            continue
        stored_name = f"{uuid.uuid4().hex}{suffix}"
        path = target / stored_name
        uploaded.save(path)
        size = path.stat().st_size
        with get_db() as db:
            cursor = db.execute(
                "INSERT INTO files (user_id, username, folder, original_name, stored_name, size) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user["id"], user["username"], folder, original_name, stored_name, size),
            )
            file_id = cursor.lastrowid
        log_event(user["id"], user["username"], "upload_success", f"{original_name} ({size} bytes) - {folder}", "success")
        results.append({"id": file_id, "name": original_name, "size": size, "folder": folder})
    if not results:
        return api_error("No allowed files were uploaded", 400)
    return jsonify({"files": results}), 201


def list_files(folder, user=None):
    search = request.args.get("search", "").strip()
    query = "SELECT * FROM files WHERE folder = ?"
    params = [folder]
    if folder == "personal":
        query += " AND user_id = ?"
        params.append(user["id"])
    if search:
        query += " AND original_name LIKE ?"
        params.append(f"%{search}%")
    query += " ORDER BY uploaded_at DESC"
    with get_db() as db:
        rows = db.execute(query, params).fetchall()
    return jsonify({"files": [file_payload(row) for row in rows]})


@app.get("/api/files/personal")
@login_required
def personal_files(user):
    return list_files("personal", user)


@app.get("/api/files/common")
@login_required
def common_files(user):
    return list_files("common", user)


@app.get("/api/files/download/<int:file_id>")
@login_required
def download(user, file_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
    if not row or (row["folder"] == "personal" and row["user_id"] != user["id"] and user["role"] != "admin"):
        return api_error("File not found", 404)
    path = file_path(row)
    if not path.is_file():
        return api_error("File is missing from storage", 404)
    log_event(user["id"], user["username"], "download", row["original_name"], "success")
    return send_file(path, as_attachment=True, download_name=row["original_name"])


@app.delete("/api/files/<int:file_id>")
@login_required
def delete_file(user, file_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
    if not row:
        return api_error("File not found", 404)
    if user["role"] != "admin" and row["user_id"] != user["id"]:
        return api_error("You cannot delete this file", 403)
    path = file_path(row)
    if path.is_file():
        path.unlink()
    with get_db() as db:
        db.execute("DELETE FROM files WHERE id = ?", (file_id,))
    log_event(user["id"], user["username"], "delete", row["original_name"], "success")
    return jsonify({"message": "File deleted"})


@app.get("/api/admin/stats")
@admin_required
def admin_stats(_user):
    with get_db() as db:
        users = db.execute("SELECT COUNT(*) total, SUM(is_active) active FROM users").fetchone()
        files = db.execute("SELECT COUNT(*) total, COALESCE(SUM(size), 0) bytes FROM files").fetchone()
        today = db.execute("SELECT COUNT(*) FROM activity_logs WHERE action = 'login_success' AND date(created_at) = date('now')").fetchone()[0]
        failed = db.execute("SELECT COUNT(*) FROM activity_logs WHERE action = 'login_failed'").fetchone()[0]
    return jsonify({"total_users": users["total"], "active_users": users["active"] or 0, "total_files": files["total"], "storage_bytes": files["bytes"], "today_logins": today, "failed_logins": failed})


@app.route("/api/admin/users", methods=["GET", "POST"])
@admin_required
def admin_users(_admin):
    if request.method == "GET":
        with get_db() as db:
            rows = db.execute("SELECT id, username, role, is_active, created_at FROM users ORDER BY username").fetchall()
        return jsonify({"users": [user_payload(row) for row in rows]})
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    role = data.get("role", "employee")
    if not username or len(password) < 8 or role not in {"employee", "admin"}:
        return api_error("Username, a password of at least 8 characters, and a valid role are required")
    try:
        with get_db() as db:
            cursor = db.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, generate_password_hash(password), role))
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return api_error("Username already exists", 409)
    ensure_storage([username])
    return jsonify({"id": user_id, "username": username, "role": role}), 201


@app.route("/api/admin/users/<int:user_id>", methods=["PUT", "DELETE"])
@admin_required
def manage_user(_admin, user_id):
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return api_error("User not found", 404)
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        if "is_active" not in data:
            return api_error("is_active is required")
        with get_db() as db:
            db.execute("UPDATE users SET is_active = ? WHERE id = ?", (int(bool(data["is_active"])), user_id))
        return jsonify({"message": "User status updated"})
    if user["role"] == "admin":
        return api_error("Admin accounts cannot be deleted through this endpoint", 400)
    with get_db() as db:
        files = db.execute("SELECT * FROM files WHERE user_id = ?", (user_id,)).fetchall()
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    for row in files:
        path = file_path(row)
        if path.is_file():
            path.unlink()
    return jsonify({"message": "User deleted"})


@app.post("/api/admin/users/<int:user_id>/reset-password")
@admin_required
def reset_password(_admin, user_id):
    data = request.get_json(silent=True) or {}
    password = str(data.get("password", ""))
    if len(password) < 8:
        return api_error("Password must be at least 8 characters")
    with get_db() as db:
        changed = db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash(password), user_id)).rowcount
    if not changed:
        return api_error("User not found", 404)
    return jsonify({"message": "Password reset"})


@app.get("/api/admin/files")
@admin_required
def admin_files(_admin):
    search = request.args.get("search", "").strip()
    with get_db() as db:
        rows = db.execute("SELECT * FROM files WHERE original_name LIKE ? ORDER BY uploaded_at DESC", (f"%{search}%",)).fetchall()
    return jsonify({"files": [file_payload(row) for row in rows]})


@app.get("/api/admin/logs")
@admin_required
def admin_logs(_admin):
    query = "SELECT * FROM activity_logs WHERE 1 = 1"
    params = []
    if request.args.get("username"):
        query += " AND username = ?"
        params.append(request.args["username"])
    if request.args.get("status"):
        query += " AND status = ?"
        params.append(request.args["status"])
    if request.args.get("date"):
        query += " AND date(created_at) = ?"
        params.append(request.args["date"])
    query += " ORDER BY created_at DESC LIMIT 500"
    with get_db() as db:
        rows = db.execute(query, params).fetchall()
    return jsonify({"logs": [dict(row) for row in rows]})


with get_db() as _db:
    init_db()
    with get_db() as _users_db:
        usernames = [row["username"] for row in _users_db.execute("SELECT username FROM users").fetchall()]
ensure_storage(usernames)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
