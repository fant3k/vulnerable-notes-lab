# 05. Insecure File Upload

## Суть

Endpoint `/upload` принимает произвольное имя файла и содержимое, сохраняет файл в `data/uploads/` и затем отдает его через `/uploads/...`. Нет проверки расширения, MIME-типа и безопасной политики отдачи.

## Как воспроизвести

1. Войдите в приложение.
2. Откройте `/upload`.
3. Укажите filename:

```text
xss.html
```

4. Укажите content:

```html
<script>alert("uploaded html")</script>
```

5. Откройте `/uploads/xss.html`.

## Где проблема в коде

В `vuln_notes/server.py` файл сохраняется почти напрямую:

```python
destination = UPLOAD_DIR / filename
destination.write_text(content, encoding="utf-8")
```

А при отдаче используется MIME-type по расширению:

```python
content_type = mimetypes.guess_type(path.name)[0] or "text/plain"
```

## Impact

В реальном приложении это может привести к Stored XSS, загрузке вредоносных файлов, обходу политик контента или даже remote code execution, если upload-директория исполняется сервером.

## Как исправить

- Использовать allowlist расширений.
- Переименовывать файлы в случайные имена.
- Хранить uploads вне web root.
- Отдавать пользовательские файлы как `application/octet-stream`.
- Проверять размер файла.
- Добавлять антивирусную/контентную проверку для production-сценариев.
