# 07. Debug Config Exposure

## Суть

Endpoint `/debug/config` доступен любому авторизованному пользователю и показывает внутреннюю конфигурацию: путь к базе, директорию uploads, fake secret key, статистику и текущий user context.

## Как воспроизвести

1. Войдите любым пользователем.
2. Откройте:

```text
http://127.0.0.1:8090/debug/config
```

## Где проблема в коде

В `vuln_notes/server.py`:

```python
"secret_key": DEMO_SECRET_KEY,
"database_path": str(DB_PATH),
"upload_dir": str(UPLOAD_DIR),
```

## Impact

Debug endpoints часто раскрывают секреты, переменные окружения, пути на сервере, версии компонентов и внутреннюю структуру приложения. Эта информация помогает атакующему строить дальнейшую цепочку эксплуатации.

## Как исправить

- Полностью отключать debug endpoints в production.
- Ограничивать доступ отдельной admin-role и дополнительной аутентификацией.
- Никогда не выводить секреты в UI и логи.
- Разделять debug build и production build.
