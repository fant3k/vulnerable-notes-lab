"""Работа с SQLite и intentionally vulnerable data access layer."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from .config import DB_PATH, UPLOAD_DIR


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Открыть SQLite connection с доступом к колонкам по имени."""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_database(db_path: Path = DB_PATH, reset: bool = False) -> None:
    """Создать схему и seed-данные.

    Параметр `reset` нужен для demo-сценария и тестов: можно быстро вернуть
    лабораторию к известному состоянию без ручного удаления файлов.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if reset and db_path.exists():
        db_path.unlink()

    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                is_private INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(owner_id) REFERENCES users(id)
            );
            """
        )
        seed_database(connection)


def seed_database(connection: sqlite3.Connection) -> None:
    """Заполнить базу демонстрационными пользователями и заметками."""
    users_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if users_count:
        return

    connection.executemany(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        [
            ("alice", "password123", "user"),
            ("bob", "qwerty", "user"),
            ("admin", "admin123", "admin"),
        ],
    )
    connection.executemany(
        "INSERT INTO notes (owner_id, title, body, is_private) VALUES (?, ?, ?, ?)",
        [
            (
                1,
                "Alice personal note",
                "Remember to rotate the demo API key before production.",
                1,
            ),
            (
                1,
                "Frontend TODO",
                "Sanitize note body before rendering. Current behavior is intentionally unsafe.",
                1,
            ),
            (
                2,
                "Bob private note",
                "The staging database password is not actually here, but IDOR should reveal this note.",
                1,
            ),
            (
                3,
                "Admin checklist",
                "Review CORS, cookies, and debug endpoints before release.",
                1,
            ),
        ],
    )
    connection.commit()


def authenticate_vulnerable(
    connection: sqlite3.Connection,
    username: str,
    password: str,
) -> Optional[sqlite3.Row]:
    """Уязвимая аутентификация через SQL-конкатенацию.

    Этот код намеренно написан неправильно для лабораторной работы по SQL
    Injection. Он показывает, почему параметры запроса должны передаваться
    отдельно от SQL-строки.
    """
    query = (
        "SELECT id, username, role FROM users "
        f"WHERE username = '{username}' AND password = '{password}'"
    )
    return connection.execute(query).fetchone()


def get_user_by_id(connection: sqlite3.Connection, user_id: int) -> Optional[sqlite3.Row]:
    """Получить пользователя безопасным параметризованным запросом."""
    return connection.execute(
        "SELECT id, username, role FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()


def list_notes_for_user(connection: sqlite3.Connection, user_id: int) -> list[sqlite3.Row]:
    """Показать пользователю его список заметок.

    Список фильтруется по owner_id, но endpoint чтения конкретной заметки ниже
    сделан уязвимым. Так проще показать разницу между корректным списком и
    broken access control на detail-view.
    """
    return connection.execute(
        """
        SELECT notes.id, notes.title, notes.created_at, users.username AS owner
        FROM notes
        JOIN users ON users.id = notes.owner_id
        WHERE notes.owner_id = ?
        ORDER BY notes.id DESC
        """,
        (user_id,),
    ).fetchall()


def get_note_vulnerable(connection: sqlite3.Connection, note_id: str) -> Optional[sqlite3.Row]:
    """Уязвимое чтение заметки без проверки владельца.

    В функции сразу две учебные проблемы: нет authorization check по owner_id
    и `note_id` вставляется в SQL напрямую. В реальном коде это должны быть
    параметризованный запрос и проверка прав доступа.
    """
    query = (
        "SELECT notes.id, notes.title, notes.body, notes.created_at, "
        "users.username AS owner "
        "FROM notes JOIN users ON users.id = notes.owner_id "
        f"WHERE notes.id = {note_id}"
    )
    return connection.execute(query).fetchone()


def create_note(connection: sqlite3.Connection, user_id: int, title: str, body: str) -> int:
    """Создать заметку, сохраняя body без HTML-sanitization.

    Хранение raw HTML нужно для лабораторной Stored XSS. Название сохраняется
    безопасно через параметры, чтобы XSS был сфокусирован именно на rendering.
    """
    cursor = connection.execute(
        "INSERT INTO notes (owner_id, title, body, is_private) VALUES (?, ?, ?, 1)",
        (user_id, title, body),
    )
    connection.commit()
    return int(cursor.lastrowid)


def database_stats(connection: sqlite3.Connection) -> dict[str, int]:
    """Вернуть агрегированную статистику для debug endpoint."""
    users = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    notes = connection.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    return {"users": int(users), "notes": int(notes)}
