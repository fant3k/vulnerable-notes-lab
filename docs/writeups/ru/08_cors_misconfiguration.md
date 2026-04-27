# 08. Permissive CORS

## Суть

Приложение отражает любой `Origin` в `Access-Control-Allow-Origin` и одновременно отправляет `Access-Control-Allow-Credentials: true`.

## Как воспроизвести

```bash
curl -i http://127.0.0.1:8090/notes \
  -H "Origin: https://evil.example"
```

В ответе будет:

```text
Access-Control-Allow-Origin: https://evil.example
Access-Control-Allow-Credentials: true
```

## Где проблема в коде

В `vuln_notes/server.py`:

```python
origin = self.headers.get("Origin", "*")
self.send_header("Access-Control-Allow-Origin", origin)
self.send_header("Access-Control-Allow-Credentials", "true")
```

## Impact

Если браузер отправляет cookies, вредоносный сайт может читать ответы приложения от имени пользователя, если CORS разрешает недоверенный origin.

## Как исправить

- Использовать allowlist trusted origins.
- Не отражать `Origin` автоматически.
- Не включать credentials без необходимости.
- Разделять CORS для public API и private authenticated API.
