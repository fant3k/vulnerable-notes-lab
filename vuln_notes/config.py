"""Конфигурация локальной лаборатории.

По умолчанию приложение слушает только localhost. Это важная граница
безопасности: проект специально уязвим и не должен быть доступен извне.
"""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "notes_lab.sqlite3"

APP_HOST = os.environ.get("VNL_HOST", "127.0.0.1")
APP_PORT = int(os.environ.get("VNL_PORT", "8090"))

SESSION_COOKIE_NAME = "vn_session"

# Значение специально статичное и слабое: оно используется в writeup про
# небезопасную модель сессий. В production-проекте такие секреты должны быть
# случайными, длинными и храниться вне репозитория.
DEMO_SECRET_KEY = "dev-secret-key-do-not-use-in-production"
