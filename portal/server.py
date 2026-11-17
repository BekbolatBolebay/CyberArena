#!/usr/bin/env python3
"""
CyberArena Portal Server ("Who Am I / CLAY" Edition).
Dependency-free Python 3 standard library HTTP server + SQLite backend
with strict security headers, PBKDF2 password hashing, rate limiting,
and isolated educational cybersecurity missions.
"""

from __future__ import annotations

import contextlib
import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import threading
import time
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from missions import (
    get_public_missions,
    run_sandboxed_camera_login,
    run_sandboxed_ddos_mitigation,
    run_sandboxed_sqli,
    verify_flag,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DEFAULT_DB_PATH = BASE_DIR / "data" / "arena.db"

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,24}$")
MAX_BODY_BYTES = 16 * 1024
SESSION_TTL_SECONDS = 7 * 24 * 3600


class RateLimiter:
    """Thread-safe sliding window rate limiter per (ip, bucket)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: dict[tuple[str, str], list[float]] = {}

    def allow(self, key: str, bucket: str, limit: int, window_sec: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_sec
        composite = (key, bucket)
        with self._lock:
            timestamps = [t for t in self._events.get(composite, []) if t > cutoff]
            if len(timestamps) >= limit:
                self._events[composite] = timestamps
                return False
            timestamps.append(now)
            self._events[composite] = timestamps
            return True


class ArenaDatabase:
    """SQLite persistence layer with parameterized queries."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        with self._lock, contextlib.closing(self._connect()) as conn, conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    pass_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS solves (
                    user_id INTEGER NOT NULL,
                    mission_id TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    solved_at INTEGER NOT NULL,
                    PRIMARY KEY (user_id, mission_id),
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """
            )

    @staticmethod
    def _hash_password(password: str, salt_hex: str) -> str:
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            200_000,
        )
        return dk.hex()

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def register_user(self, username: str, password: str) -> tuple[bool, str, int | None]:
        salt = secrets.token_bytes(16).hex()
        pass_hash = self._hash_password(password, salt)
        now = int(time.time())
        with self._lock, contextlib.closing(self._connect()) as conn, conn:
            try:
                cur = conn.execute(
                    "INSERT INTO users (username, pass_hash, salt, created_at) VALUES (?, ?, ?, ?)",
                    (username, pass_hash, salt, now),
                )
                return True, "Оператор тіркелді.", int(cur.lastrowid)
            except sqlite3.IntegrityError:
                return False, "Бұл лақап ат (handle) бос емес.", None

    def authenticate(self, username: str, password: str) -> tuple[int, str] | None:
        with self._lock, contextlib.closing(self._connect()) as conn, conn:
            row = conn.execute(
                "SELECT id, username, pass_hash, salt FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if not row:
                return None
            candidate = self._hash_password(password, row["salt"])
            if not hmac.compare_digest(candidate, row["pass_hash"]):
                return None
            return int(row["id"]), str(row["username"])

    def create_session(self, user_id: int) -> str:
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        expires_at = int(time.time()) + SESSION_TTL_SECONDS
        with self._lock, contextlib.closing(self._connect()) as conn, conn:
            conn.execute(
                "DELETE FROM sessions WHERE expires_at < ?",
                (int(time.time()),),
            )
            conn.execute(
                "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
                (token_hash, user_id, expires_at),
            )
        return raw_token

    def get_session_user(self, raw_token: str) -> dict[str, Any] | None:
        if not raw_token:
            return None
        token_hash = self._hash_token(raw_token)
        now = int(time.time())
        with self._lock, contextlib.closing(self._connect()) as conn, conn:
            row = conn.execute(
                """
                SELECT u.id, u.username, s.expires_at
                FROM sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token_hash = ?
                """,
                (token_hash,),
            ).fetchone()
            if not row:
                return None
            if int(row["expires_at"]) < now:
                conn.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
                return None
            solves = conn.execute(
                "SELECT mission_id, points, solved_at FROM solves WHERE user_id = ?",
                (row["id"],),
            ).fetchall()
            solved_ids = [str(r["mission_id"]) for r in solves]
            total_points = sum(int(r["points"]) for r in solves)
            return {
                "id": int(row["id"]),
                "username": str(row["username"]),
                "solved_ids": solved_ids,
                "score": total_points,
            }

    def delete_session(self, raw_token: str) -> None:
        if not raw_token:
            return
        token_hash = self._hash_token(raw_token)
        with self._lock, contextlib.closing(self._connect()) as conn, conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))

    def delete_user(self, user_id: int) -> None:
        with self._lock, contextlib.closing(self._connect()) as conn, conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    def record_solve(self, user_id: int, mission_id: str, points: int) -> bool:
        """Record mission completion; returns True if newly solved."""
        now = int(time.time())
        with self._lock, contextlib.closing(self._connect()) as conn, conn:
            existing = conn.execute(
                "SELECT 1 FROM solves WHERE user_id = ? AND mission_id = ?",
                (user_id, mission_id),
            ).fetchone()
            if existing:
                return False
            conn.execute(
                "INSERT INTO solves (user_id, mission_id, points, solved_at) VALUES (?, ?, ?, ?)",
                (user_id, mission_id, points, now),
            )
            return True

    def get_leaderboard(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock, contextlib.closing(self._connect()) as conn, conn:
            rows = conn.execute(
                """
                SELECT
                    u.username,
                    COALESCE(SUM(s.points), 0) AS score,
                    COUNT(s.mission_id) AS solved_count,
                    COALESCE(MAX(s.solved_at), u.created_at) AS last_activity
                FROM users u
                LEFT JOIN solves s ON s.user_id = u.id
                GROUP BY u.id
                ORDER BY score DESC, solved_count DESC, last_activity ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [
                {
                    "rank": idx + 1,
                    "username": str(r["username"]),
                    "score": int(r["score"]),
                    "solved_count": int(r["solved_count"]),
                }
                for idx, r in enumerate(rows)
            ]


class CyberArenaServer(ThreadingHTTPServer):
    """HTTP server holding shared database and rate limiter instances."""

    def __init__(
        self,
        server_address: tuple[str, int],
        db: ArenaDatabase,
        trust_proxy: bool = False,
    ) -> None:
        self.db = db
        self.limiter = RateLimiter()
        self.trust_proxy = trust_proxy
        super().__init__(server_address, ArenaRequestHandler)


class ArenaRequestHandler(BaseHTTPRequestHandler):
    """Handles static portal files, CTF API, and isolated mission simulators."""

    server: CyberArenaServer
    server_version = "CyberArena/2.0"

    def log_message(self, format: str, *args: Any) -> None:
        # Keep stdout logs clean and structured
        sys_msg = format % args
        print(f"[{self.log_date_time_string()}] {self._client_ip()} - {sys_msg}")

    def _client_ip(self) -> str:
        if self.server.trust_proxy:
            cf_ip = self.headers.get("CF-Connecting-IP")
            if cf_ip:
                return cf_ip.strip()
            real_ip = self.headers.get("X-Real-IP")
            if real_ip:
                return real_ip.strip()
        return self.client_address[0]

    def _is_https(self) -> bool:
        if self.server.trust_proxy:
            return self.headers.get("X-Forwarded-Proto", "").lower() == "https"
        return False

    def _send_security_headers(self) -> None:
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'",
        )
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

    def _send_json(
        self,
        status: int,
        payload: dict[str, Any],
        extra_headers: list[tuple[str, str]] | None = None,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_security_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for k, v in extra_headers:
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status: int, text: str, content_type: str = "text/plain; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self._send_security_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any] | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None
        if length <= 0 or length > MAX_BODY_BYTES:
            return None
        raw = self.rfile.read(length)
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        return parsed if isinstance(parsed, dict) else None

    def _session_token(self) -> str:
        raw_cookie = self.headers.get("Cookie", "")
        if not raw_cookie:
            return ""
        jar = cookies.SimpleCookie()
        try:
            jar.load(raw_cookie)
        except cookies.CookieError:
            return ""
        morsel = jar.get("arena_session")
        return morsel.value if morsel else ""

    def _session_cookie_header(self, token: str, clear: bool = False) -> tuple[str, str]:
        secure_attr = "; Secure" if self._is_https() else ""
        if clear:
            return (
                "Set-Cookie",
                f"arena_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0{secure_attr}",
            )
        return (
            "Set-Cookie",
            f"arena_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_TTL_SECONDS}{secure_attr}",
        )

    def _current_user(self) -> dict[str, Any] | None:
        return self.server.db.get_session_user(self._session_token())

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/health":
            self._send_json(200, {"status": "ok", "service": "CyberArena"})
            return

        if path == "/robots.txt":
            self._send_text(
                200,
                "User-agent: *\nDisallow: /clay-audit-vault\n# CLAY Audit: Kein System ist sicher.\n",
            )
            return

        if path == "/clay-audit-vault":
            self._send_json(
                200,
                {
                    "vault": "CLAY_AUDIT_ARCHIVE",
                    "note": "Күнделікті есеп: Бөгде адамдар robots.txt ішіндегі жасырын папкаларды бірінші болып оқиды.",
                    "flag": "FLAG{KEIN_SYSTEM_IST_SICHER_01}",
                },
            )
            return

        if path == "/api/me":
            user = self._current_user()
            self._send_json(200, {"user": user})
            return

        if path == "/api/missions":
            user = self._current_user()
            solved = set(user["solved_ids"]) if user else set()
            missions = []
            for m in get_public_missions():
                item = dict(m)
                item["solved"] = m["id"] in solved
                missions.append(item)
            self._send_json(200, {"missions": missions})
            return

        if path == "/api/leaderboard":
            self._send_json(200, {"leaderboard": self.server.db.get_leaderboard()})
            return

        # Static file serving with strict path traversal protection
        rel = "index.html" if path == "/" else path.lstrip("/")
        static_root = STATIC_DIR.resolve()
        candidate = (static_root / rel).resolve()
        if not candidate.is_relative_to(static_root) or not candidate.is_file():
            self._send_json(404, {"error": "Ресурс табылмады."})
            return

        mime, _ = mimetypes.guess_type(str(candidate))
        content_type = mime or "application/octet-stream"
        if content_type.startswith("text/") or content_type == "application/javascript":
            content_type = f"{content_type}; charset=utf-8"

        data = candidate.read_bytes()
        self.send_response(200)
        self._send_security_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        ip = self._client_ip()

        if path == "/api/register":
            if not self.server.limiter.allow(ip, "register", limit=8, window_sec=300):
                self._send_json(429, {"error": "Сұраныс тым жиі. Сәл күтіңіз."})
                return
            body = self._read_json()
            if not body:
                self._send_json(400, {"error": "Дұрыс JSON жіберіңіз."})
                return
            username = str(body.get("username", "")).strip()
            password = str(body.get("password", ""))
            if not USERNAME_RE.match(username):
                self._send_json(400, {"error": "Лақап ат 3–24 таңба, тек латын әріптері, сандар және _ . - болуы керек."})
                return
            if len(password) < 6 or len(password) > 128:
                self._send_json(400, {"error": "Құпия сөз кемінде 6 таңбадан тұруы тиіс."})
                return
            ok, msg, user_id = self.server.db.register_user(username, password)
            if not ok or user_id is None:
                self._send_json(409, {"error": msg})
                return
            token = self.server.db.create_session(user_id)
            user = self.server.db.get_session_user(token)
            self._send_json(201, {"user": user, "message": msg}, [self._session_cookie_header(token)])
            return

        if path == "/api/login":
            if not self.server.limiter.allow(ip, "login", limit=15, window_sec=300):
                self._send_json(429, {"error": "Кіру әрекеті тым көп. 5 минуттан соң көріңіз."})
                return
            body = self._read_json()
            if not body:
                self._send_json(400, {"error": "Дұрыс JSON жіберіңіз."})
                return
            username = str(body.get("username", "")).strip()
            password = str(body.get("password", ""))
            auth = self.server.db.authenticate(username, password)
            if not auth:
                self._send_json(401, {"error": "Лақап ат немесе құпия сөз қате."})
                return
            user_id, _ = auth
            token = self.server.db.create_session(user_id)
            user = self.server.db.get_session_user(token)
            self._send_json(200, {"user": user}, [self._session_cookie_header(token)])
            return

        if path == "/api/logout":
            self.server.db.delete_session(self._session_token())
            self._send_json(200, {"ok": True}, [self._session_cookie_header("", clear=True)])
            return

        if path == "/api/submit":
            if not self.server.limiter.allow(ip, "submit", limit=30, window_sec=60):
                self._send_json(429, {"error": "Тексеру тым жиі. Бір минут күтіңіз."})
                return
            body = self._read_json()
            if not body:
                self._send_json(400, {"error": "Дұрыс JSON жіберіңіз."})
                return
            mission_id = str(body.get("mission_id", "")).strip()
            flag = str(body.get("flag", "")).strip()
            mission = next((m for m in get_public_missions() if m["id"] == mission_id), None)
            if not mission:
                self._send_json(404, {"error": "Миссия табылмады."})
                return
            if not verify_flag(mission_id, flag):
                self._send_json(400, {"ok": False, "error": "Флаг қате. Қайта тексеріңіз."})
                return

            user = self._current_user()
            newly_solved = False
            if user:
                newly_solved = self.server.db.record_solve(user["id"], mission_id, int(mission["points"]))
                user = self._current_user()
            self._send_json(
                200,
                {
                    "ok": True,
                    "newly_solved": newly_solved,
                    "points": int(mission["points"]),
                    "defense_takeaway": mission["defense_takeaway"],
                    "user": user,
                    "message": "Қабылданды! Жүйе сәтті талданды." if newly_solved or not user else "Бұл миссия бұрын шешілген.",
                },
            )
            return

        if path == "/api/sim/sqli":
            if not self.server.limiter.allow(ip, "sim", limit=40, window_sec=60):
                self._send_json(429, {"error": "Симуляторға сұраныс тым көп."})
                return
            body = self._read_json()
            if not body:
                self._send_json(400, {"error": "Дұрыс JSON жіберіңіз."})
                return
            result = run_sandboxed_sqli(str(body.get("username", "")), str(body.get("password", "")))
            self._send_json(200, result)
            return

        if path == "/api/sim/camera":
            if not self.server.limiter.allow(ip, "sim", limit=40, window_sec=60):
                self._send_json(429, {"error": "Симуляторға сұраныс тым көп."})
                return
            body = self._read_json()
            if not body:
                self._send_json(400, {"error": "Дұрыс JSON жіберіңіз."})
                return
            result = run_sandboxed_camera_login(str(body.get("username", "")), str(body.get("password", "")))
            self._send_json(200, result)
            return

        if path == "/api/sim/ddos":
            if not self.server.limiter.allow(ip, "sim", limit=40, window_sec=60):
                self._send_json(429, {"error": "Симуляторға сұраныс тым көп."})
                return
            body = self._read_json()
            if not body:
                self._send_json(400, {"error": "Дұрыс JSON жіберіңіз."})
                return
            result = run_sandboxed_ddos_mitigation(str(body.get("subnet", "")))
            self._send_json(200, result)
            return

        self._send_json(404, {"error": "API нүктесі табылмады."})

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/account":
            user = self._current_user()
            if not user:
                self._send_json(401, {"error": "Алдымен жүйеге кіріңіз."})
                return
            self.server.db.delete_user(int(user["id"]))
            self._send_json(200, {"ok": True, "message": "Аккаунт толық өшірілді."}, [self._session_cookie_header("", clear=True)])
            return
        self._send_json(404, {"error": "Табылмады."})


def main() -> None:
    host = os.environ.get("ARENA_HOST", "127.0.0.1")
    port = int(os.environ.get("ARENA_PORT", "8000"))
    db_path = Path(os.environ.get("ARENA_DB_PATH", str(DEFAULT_DB_PATH)))
    trust_proxy = os.environ.get("ARENA_TRUST_PROXY", "0") == "1"

    db = ArenaDatabase(db_path)
    server = CyberArenaServer((host, port), db=db, trust_proxy=trust_proxy)
    print(f"[CyberArena] Portal listening on http://{host}:{port} (db={db_path})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[CyberArena] Shutting down.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
