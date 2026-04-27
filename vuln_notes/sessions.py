"""Намеренно слабая модель сессий для учебной лаборатории."""

from __future__ import annotations

import base64
from http.cookies import SimpleCookie
from typing import Optional

from .config import SESSION_COOKIE_NAME


def create_session_cookie(user_id: int, username: str, role: str) -> str:
    """Создать cookie без подписи и server-side хранения.

    Это небезопасный подход: пользователь может изменить содержимое cookie и
    выдать себя за другого пользователя. Уязвимость оставлена специально для
    writeup по authentication/session management.
    """
    raw_value = f"{user_id}:{username}:{role}".encode("utf-8")
    return base64.urlsafe_b64encode(raw_value).decode("ascii")


def parse_session_cookie(cookie_header: str) -> Optional[dict[str, str]]:
    """Разобрать session cookie, доверяя клиентскому значению.

    Функция демонстрационно уязвима: она не проверяет подпись, срок жизни и
    соответствие username/role данным в базе.
    """
    cookie = SimpleCookie()
    cookie.load(cookie_header or "")
    morsel = cookie.get(SESSION_COOKIE_NAME)
    if not morsel:
        return None

    try:
        decoded = base64.urlsafe_b64decode(morsel.value.encode("ascii")).decode("utf-8")
        user_id, username, role = decoded.split(":", 2)
    except Exception:
        return None

    return {"id": user_id, "username": username, "role": role}
