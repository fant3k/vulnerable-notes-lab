# Vulnerable Notes Lab

[![tests](https://github.com/fant3k/vulnerable-notes-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/fant3k/vulnerable-notes-lab/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776ab)
![Scope](https://img.shields.io/badge/scope-localhost_only-f59e0b)

Vulnerable Notes Lab — небольшое намеренно уязвимое веб-приложение для
воспроизведения базовых ошибок веб-безопасности и разбора их первопричин.

Проект имитирует сервис заметок: пользователи входят в аккаунт, создают и
открывают заметки, загружают вложения и запрашивают URL preview.

> Приложение уязвимо специально. Запускайте его только локально на `127.0.0.1` и не публикуйте в интернет.

## Что реализовано

- Локальное web-приложение на Python standard library без Flask/FastAPI.
- SQLite-база с demo-пользователями и заметками.
- Простая HTML UI для заметок, загрузок и URL preview.
- 8 намеренно реализованных уязвимостей с writeups:
  - SQL Injection в логине;
  - IDOR / Broken Access Control;
  - Stored XSS;
  - Weak session cookie;
  - Insecure file upload;
  - SSRF через URL preview;
  - Debug config exposure;
  - Permissive CORS.
- Русские и английские writeups с воспроизведением, impact и remediation.
- Unit- и HTTP integration-тесты, которые фиксируют каждый учебный сценарий.
- GitHub Actions workflow для запуска тестов.

## Архитектура

```text
vulnerable-notes-lab/
  app.py                    # точка входа
  vuln_notes/
    config.py               # пути, host/port, demo secret
    database.py             # SQLite и intentionally vulnerable queries
    server.py               # HTTP routes и web endpoints
    sessions.py             # слабая client-side session model
    templates.py            # HTML rendering, включая Stored XSS sink
  docs/
    writeups/
      ru/                   # русские writeups
      en/                   # английские writeups
  scripts/
    run.sh                  # запуск приложения
    reset_db.sh             # сброс SQLite-базы
    test.sh                 # тесты и compile check
  tests/
    test_database.py
    test_http.py
    test_sessions.py
  Dockerfile                # non-root образ для локального запуска
  docker-compose.yml        # публикация порта только на localhost
```

## Быстрый старт

```bash
cd vulnerable-notes-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
scripts/reset_db.sh
scripts/run.sh
```

Откройте приложение:

```text
http://127.0.0.1:8090
```

Demo-пользователи:

```text
alice / password123
bob   / qwerty
admin / admin123
```

Порт можно изменить:

```bash
VNL_PORT=9090 scripts/run.sh
```

Или через Docker Compose:

```bash
docker compose up --build
```

Compose публикует порт только на `127.0.0.1`.

## Как пользоваться для обучения

1. Запустите приложение локально.
2. Откройте русские writeups: [docs/writeups/ru](docs/writeups/ru/README.md).
3. Воспроизведите каждую уязвимость.
4. Найдите соответствующее место в коде.
5. Прочитайте remediation и попробуйте сделать secure-fix в отдельной ветке.

Английские writeups находятся здесь: [docs/writeups/en](docs/writeups/en/README.md).

## Пример: SQL Injection

В форме логина можно использовать username:

```text
alice' -- 
```

и любой пароль. Уязвимость находится в `vuln_notes/database.py`, где SQL-запрос строится через f-string.

## Пример: IDOR

Войдите как `alice` и откройте:

```text
http://127.0.0.1:8090/note?id=3
```

Вы увидите заметку пользователя `bob`, потому что detail endpoint не проверяет `owner_id`.

## Пример: SSRF

Войдите в приложение и откройте:

```text
http://127.0.0.1:8090/preview?url=http://127.0.0.1:8090/internal/metadata
```

Сервер сделает запрос к внутреннему endpoint и покажет ответ.

## Проверка проекта

```bash
scripts/test.sh
```

Или вручную:

```bash
python3 -B -m unittest discover -s tests
PYTHONPYCACHEPREFIX=/tmp/vulnerable_notes_pycache python3 -m compileall vuln_notes
```

## Что я изучил в процессе

- Как уязвимости OWASP Top 10 выглядят в реальном коде, а не только в теории.
- Почему SQL Injection возникает из-за смешивания данных и SQL-команд.
- Как Broken Access Control появляется даже в приложении с логином.
- Чем output encoding отличается от input validation.
- Почему base64 cookie не является безопасной сессией.
- Как SSRF связан с доверием server-side network context.
- Как писать writeups: reproduction, root cause, impact, remediation.

## Контролируемый scope

Каждая заявленная уязвимость имеет отдельный writeup и автоматическую проверку.
В IDOR-кейсе идентификатор параметризован, поэтому он демонстрирует только
ошибку авторизации, а не случайную вторую SQL Injection. SSRF-сценарий работает
через внутренний endpoint того же процесса и проверяется end-to-end тестом.

Подробнее о принятых границах: [docs/LAB_DESIGN.md](docs/LAB_DESIGN.md).

## Ограничения

- Это учебная лаборатория, а не production-приложение.
- UI предназначен для воспроизведения security-сценариев, а не для production.
- Некоторые уязвимости упрощены, чтобы их было легче объяснить на собеседовании.
- Приложение не должно запускаться на публичном интерфейсе.

## Этика

Проект предназначен для локального обучения, портфолио и подготовки к собеседованиям. Не используйте его как основу для реального приложения без полного устранения уязвимостей.
