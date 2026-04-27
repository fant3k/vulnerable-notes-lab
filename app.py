#!/usr/bin/env python3
"""Точка входа для локального запуска Vulnerable Notes Lab."""

from vuln_notes.config import APP_HOST, APP_PORT
from vuln_notes.database import init_database
from vuln_notes.server import run_server


def main() -> int:
    """Инициализировать SQLite-базу и запустить HTTP-сервер."""
    init_database()
    run_server(host=APP_HOST, port=APP_PORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
