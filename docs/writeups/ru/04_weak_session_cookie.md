# 04. Weak Session Cookie

## Суть

Приложение хранит user id, username и role прямо в cookie, кодируя их через base64. Cookie не подписана и не проверяется на сервере, поэтому пользователь может изменить ее и выдать себя за другого.

## Как воспроизвести

1. Войдите как `alice`.
2. Создайте поддельное значение cookie:

```bash
python3 - <<'PY'
import base64
print(base64.urlsafe_b64encode(b"3:admin:admin").decode())
PY
```

3. Подставьте полученное значение в cookie `vn_session`.
4. Приложение начнет считать пользователя admin.

## Где проблема в коде

В `vuln_notes/sessions.py`:

```python
raw_value = f"{user_id}:{username}:{role}".encode("utf-8")
return base64.urlsafe_b64encode(raw_value).decode("ascii")
```

Base64 не является защитой. Это только формат кодирования.

## Impact

Атакующий может подделать идентификатор пользователя или роль, если знает формат cookie.

## Как исправить

Варианты:

- хранить на клиенте только случайный `session_id`, а состояние сессии держать на сервере;
- подписывать cookie через HMAC и проверять подпись;
- задавать `Secure`, `HttpOnly`, `SameSite`;
- добавлять срок жизни и server-side invalidation.
