"""HTTP server для Vulnerable Notes Lab."""

from __future__ import annotations

import json
import mimetypes
import os
from email.parser import BytesParser
from email.policy import default as email_policy
from html import escape
import urllib.error
import urllib.parse
import urllib.request
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

from .config import DB_PATH, DEMO_SECRET_KEY, MAX_UPLOAD_BYTES, SESSION_COOKIE_NAME, UPLOAD_DIR
from .database import (
    authenticate_vulnerable,
    create_note,
    database_stats,
    get_connection,
    get_note_vulnerable,
    get_user_by_id,
    list_notes_for_user,
)
from .sessions import create_session_cookie, parse_session_cookie
from .templates import (
    debug_page,
    error_page,
    login_page,
    new_note_page,
    note_page,
    notes_page,
    preview_page,
    upload_page,
)


class VulnerableNotesHandler(BaseHTTPRequestHandler):
    """Request handler с намеренно уязвимыми endpoints."""

    server_version = "VulnerableNotesLab/0.1"

    def do_OPTIONS(self) -> None:
        """Ответить permissive CORS-заголовками.

        Это сделано специально для лабораторной работы по CORS: сервер
        отражает любой Origin и разрешает credentials.
        """
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        route = parsed.path

        if route == "/":
            self._redirect("/notes" if self.current_user() else "/login")
        elif route == "/login":
            self._send_html(login_page())
        elif route == "/logout":
            self._logout()
        elif route == "/notes":
            self._require_user(self._show_notes)
        elif route == "/note":
            self._require_user(lambda user: self._show_note(user, parsed.query))
        elif route == "/new":
            self._require_user(lambda user: self._send_html(new_note_page(user)))
        elif route == "/upload":
            self._require_user(lambda user: self._send_html(upload_page(user)))
        elif route.startswith("/uploads/"):
            self._serve_upload(route)
        elif route == "/preview":
            self._require_user(lambda user: self._preview_url(user, parsed.query))
        elif route == "/debug/config":
            self._require_user(self._debug_config)
        elif route == "/health":
            self._send_json({"status": "ok"})
        elif route == "/internal/metadata":
            self._send_json(
                {
                    "service": "metadata-demo",
                    "environment": "local-lab",
                    "fake_token": "vnl_metadata_token_for_training_only",
                }
            )
        else:
            self._send_error(HTTPStatus.NOT_FOUND, "Not found", "Route does not exist.")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/login":
            self._login()
        elif parsed.path == "/new":
            self._require_user(self._create_note)
        elif parsed.path == "/upload":
            self._require_user(self._upload_file)
        else:
            self._send_error(HTTPStatus.NOT_FOUND, "Not found", "Route does not exist.")

    def current_user(self) -> Optional[dict[str, str]]:
        """Вернуть пользователя из cookie.

        Здесь намеренно доверяется client-side cookie. В реальном приложении
        надо хранить session id на сервере или подписывать cookie.
        """
        session = parse_session_cookie(self.headers.get("Cookie", ""))
        if not session:
            return None

        try:
            user_id = int(session["id"])
        except ValueError:
            return None

        with get_connection() as connection:
            user = get_user_by_id(connection, user_id)
        if not user:
            return None

        return {
            "id": str(user["id"]),
            "username": session["username"],
            "role": session["role"],
        }

    def _login(self) -> None:
        fields = self._read_form()
        username = fields.get("username", "")
        password = fields.get("password", "")

        with get_connection() as connection:
            user = authenticate_vulnerable(connection, username, password)

        if not user:
            self._send_html(login_page("Invalid username or password."), status=HTTPStatus.UNAUTHORIZED)
            return

        cookie_value = create_session_cookie(user["id"], user["username"], user["role"])
        cookie = SimpleCookie()
        cookie[SESSION_COOKIE_NAME] = cookie_value
        cookie[SESSION_COOKIE_NAME]["path"] = "/"
        cookie[SESSION_COOKIE_NAME]["httponly"] = True
        cookie[SESSION_COOKIE_NAME]["samesite"] = "Lax"
        self._redirect("/notes", headers=[("Set-Cookie", cookie.output(header="").strip())])

    def _logout(self) -> None:
        cookie = SimpleCookie()
        cookie[SESSION_COOKIE_NAME] = ""
        cookie[SESSION_COOKIE_NAME]["path"] = "/"
        cookie[SESSION_COOKIE_NAME]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
        self._redirect("/login", headers=[("Set-Cookie", cookie.output(header="").strip())])

    def _show_notes(self, user: dict[str, str]) -> None:
        with get_connection() as connection:
            notes = list_notes_for_user(connection, int(user["id"]))
        self._send_html(notes_page(user, notes))

    def _show_note(self, user: dict[str, str], query: str) -> None:
        params = urllib.parse.parse_qs(query)
        note_id = params.get("id", [""])[0]
        if not note_id:
            self._send_error(HTTPStatus.BAD_REQUEST, "Bad request", "Missing note id.")
            return

        try:
            with get_connection() as connection:
                note = get_note_vulnerable(connection, note_id)
        except Exception as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, "Query error", str(exc))
            return

        if not note:
            self._send_error(HTTPStatus.NOT_FOUND, "Not found", "Note does not exist.")
            return

        self._send_html(note_page(user, note))

    def _create_note(self, user: dict[str, str]) -> None:
        fields = self._read_form()
        title = fields.get("title", "").strip()
        body = fields.get("body", "")
        if not title:
            self._send_html(new_note_page(user, "Title is required."), status=HTTPStatus.BAD_REQUEST)
            return

        with get_connection() as connection:
            note_id = create_note(connection, int(user["id"]), title, body)
        self._redirect(f"/note?id={note_id}")

    def _upload_file(self, user: dict[str, str]) -> None:
        uploaded = self._read_uploaded_file()
        if uploaded is None:
            self._send_html(
                upload_page(user, "Choose a file to upload."),
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        original_name, content = uploaded
        filename = os.path.basename(original_name.strip())

        if not filename:
            self._send_html(upload_page(user, "Filename is required."), status=HTTPStatus.BAD_REQUEST)
            return

        if len(content) > MAX_UPLOAD_BYTES:
            self._send_html(
                upload_page(user, "File is larger than the 256 KiB lab limit."),
                status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            )
            return

        destination = UPLOAD_DIR / filename
        destination.write_bytes(content)
        safe_name = escape(filename)
        link = f'<a href="/uploads/{urllib.parse.quote(filename)}">/uploads/{safe_name}</a>'
        self._send_html(upload_page(user, f"Uploaded: {link}"))

    def _serve_upload(self, route: str) -> None:
        filename = urllib.parse.unquote(route.removeprefix("/uploads/"))
        path = (UPLOAD_DIR / os.path.basename(filename)).resolve()
        if not path.exists() or not path.is_file():
            self._send_error(HTTPStatus.NOT_FOUND, "Not found", "File does not exist.")
            return

        content_type = mimetypes.guess_type(path.name)[0] or "text/plain"
        body = path.read_bytes()
        self._send_bytes(body, content_type=content_type)

    def _preview_url(self, user: dict[str, str], query: str) -> None:
        params = urllib.parse.parse_qs(query)
        url = params.get("url", [""])[0]
        if not url:
            self._send_html(preview_page(user))
            return

        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                body = response.read(2048).decode("utf-8", errors="replace")
                result = f"HTTP {response.status}\n\n{body}"
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            result = f"Fetch failed: {exc}"

        self._send_html(preview_page(user, result))

    def _debug_config(self, user: dict[str, str]) -> None:
        with get_connection() as connection:
            stats = database_stats(connection)
        config_dump = json.dumps(
            {
                "environment": "local-demo",
                "database_path": str(DB_PATH),
                "upload_dir": str(UPLOAD_DIR),
                "secret_key": DEMO_SECRET_KEY,
                "stats": stats,
                "current_user": user,
            },
            indent=2,
            ensure_ascii=False,
        )
        self._send_html(debug_page(user, config_dump))

    def _require_user(self, callback) -> None:
        user = self.current_user()
        if not user:
            self._redirect("/login")
            return
        callback(user)

    def _read_form(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8", errors="replace")
        parsed = urllib.parse.parse_qs(raw_body, keep_blank_values=True)
        return {key: values[0] for key, values in parsed.items()}

    def _read_uploaded_file(self) -> Optional[tuple[str, bytes]]:
        """Разобрать один multipart upload без внешнего web-фреймворка."""
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("multipart/form-data"):
            return None

        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_UPLOAD_BYTES + 64 * 1024:
            return None

        body = self.rfile.read(length)
        envelope = (
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("ascii")
            + body
        )
        message = BytesParser(policy=email_policy).parsebytes(envelope)
        if not message.is_multipart():
            return None

        for part in message.iter_parts():
            if part.get_param("name", header="content-disposition") != "file":
                continue
            filename = part.get_filename() or ""
            payload = part.get_payload(decode=True) or b""
            return filename, payload
        return None

    def _send_cors_headers(self) -> None:
        origin = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_html(self, html: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(html.encode("utf-8"), status=status, content_type="text/html; charset=utf-8")

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(body, status=status, content_type="application/json; charset=utf-8")

    def _send_error(self, status: HTTPStatus, title: str, message: str) -> None:
        self._send_html(error_page(status.value, title, message), status=status)

    def _send_bytes(
        self,
        body: bytes,
        status: HTTPStatus = HTTPStatus.OK,
        content_type: str = "text/plain; charset=utf-8",
        extra_headers: Optional[list[tuple[str, str]]] = None,
    ) -> None:
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in extra_headers or []:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str, headers: Optional[list[tuple[str, str]]] = None) -> None:
        self.send_response(HTTPStatus.FOUND)
        self._send_cors_headers()
        self.send_header("Location", location)
        for name, value in headers or []:
            self.send_header(name, value)
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:
        """Оставить короткий access log без лишнего шума."""
        print(f"{self.address_string()} - {fmt % args}")


def run_server(host: str, port: int) -> None:
    """Запустить локальный HTTP-сервер."""
    # ThreadingHTTPServer нужен не только для отзывчивости UI: SSRF-лаборатория
    # обращается к внутреннему endpoint того же процесса.
    server = ThreadingHTTPServer((host, port), VulnerableNotesHandler)
    print(f"Vulnerable Notes Lab listening on http://{host}:{port}")
    print("Use only as a local training lab. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()
