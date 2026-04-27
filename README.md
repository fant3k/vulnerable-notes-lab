# Vulnerable Notes Lab

Vulnerable Notes Lab — локальное intentionally vulnerable web-приложение для практики OWASP Top 10, подготовки writeups и демонстрации AppSec-навыков в GitHub-портфолио.

Проект имитирует простое приложение заметок: пользователи логинятся, создают заметки, открывают detail-view, загружают attachment и используют URL preview. Внутри намеренно оставлены уязвимости, которые часто обсуждают на собеседованиях для Application Security / Security Engineer ролей.

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
- Unit-тесты, которые фиксируют учебное поведение приложения.
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
    test_sessions.py
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

## Как показывать проект в резюме

Можно описать так:

```text
Vulnerable Notes Lab
Built an intentionally vulnerable Python web application mapped to OWASP Top 10.
Implemented SQLi, IDOR, Stored XSS, weak sessions, insecure upload, SSRF, CORS
misconfiguration and debug exposure, with bilingual writeups and remediation notes.
```

## Ограничения

- Это учебная лаборатория, а не production-приложение.
- UI минимальный и сделан для демонстрации security flaws.
- Некоторые уязвимости упрощены, чтобы их было легче объяснить на собеседовании.
- Приложение не должно запускаться на публичном интерфейсе.

## Планы развития

- Добавить secure branch с исправлениями и diff-based writeups.
- Добавить Dockerfile и docker-compose.
- Добавить Playwright screenshots для README.
- Добавить отдельные labs по CSRF и mass assignment.
- Добавить checklist по OWASP ASVS для каждой secure-fix версии.

## Этика

Проект предназначен для локального обучения, портфолио и подготовки к собеседованиям. Не используйте его как основу для реального приложения без полного устранения уязвимостей.
