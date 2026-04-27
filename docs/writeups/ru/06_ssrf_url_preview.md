# 06. SSRF через URL Preview

## Суть

Endpoint `/preview?url=...` принимает URL от пользователя и делает server-side запрос через `urllib.request.urlopen()`. Нет allowlist хостов, запрета localhost/internal ranges и проверки схемы.

## Как воспроизвести

1. Войдите в приложение.
2. Откройте:

```text
http://127.0.0.1:8090/preview?url=http://127.0.0.1:8090/internal/metadata
```

3. Приложение сделает запрос с сервера к внутреннему endpoint и покажет ответ.

## Где проблема в коде

В `vuln_notes/server.py`:

```python
with urllib.request.urlopen(url, timeout=2) as response:
    body = response.read(2048)
```

Пользователь полностью контролирует destination.

## Impact

В production SSRF может позволить читать internal services, cloud metadata, admin panels, Redis/Elasticsearch dashboards или выполнять port scanning из внутренней сети.

## Как исправить

- Разрешить только заранее известные домены.
- Запретить private IP ranges, localhost и link-local addresses после DNS resolution.
- Разрешить только `http`/`https`.
- Не следовать redirect в private ranges.
- Ограничить timeout, размер ответа и content-type.
