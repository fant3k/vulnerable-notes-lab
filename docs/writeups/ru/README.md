# Writeups: Vulnerable Notes Lab

Эта папка содержит разборы уязвимостей, которые намеренно реализованы в приложении. Каждый writeup построен одинаково: что за проблема, как воспроизвести локально, почему она появилась в коде, какой риск создает и как исправить.

Перед началом запустите приложение:

```bash
cd vulnerable-notes-lab
scripts/reset_db.sh
scripts/run.sh
```

Доступные пользователи:

```text
alice / password123
bob   / qwerty
admin / admin123
```

## Карта уязвимостей

| Файл | Тема | OWASP Top 10 mapping |
| --- | --- | --- |
| [01_sql_injection_login.md](01_sql_injection_login.md) | SQL Injection в логине | A03:2021 Injection |
| [02_idor_broken_access_control.md](02_idor_broken_access_control.md) | IDOR при чтении заметок | A01:2021 Broken Access Control |
| [03_stored_xss.md](03_stored_xss.md) | Stored XSS в тексте заметки | A03:2021 Injection |
| [04_weak_session_cookie.md](04_weak_session_cookie.md) | Подделка session cookie | A07:2021 Identification and Authentication Failures |
| [05_insecure_file_upload.md](05_insecure_file_upload.md) | Небезопасная загрузка файлов | A05:2021 Security Misconfiguration |
| [06_ssrf_url_preview.md](06_ssrf_url_preview.md) | SSRF через URL preview | A10:2021 Server-Side Request Forgery |
| [07_debug_config_exposure.md](07_debug_config_exposure.md) | Утечка debug config | A05:2021 Security Misconfiguration |
| [08_cors_misconfiguration.md](08_cors_misconfiguration.md) | Permissive CORS | A05:2021 Security Misconfiguration |
