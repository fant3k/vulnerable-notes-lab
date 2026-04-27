# 01. SQL Injection в логине

## Суть

Форма логина строит SQL-запрос через конкатенацию строк. Пользовательский ввод попадает прямо в `WHERE username = '...' AND password = '...'`, поэтому атакующий может изменить структуру запроса.

## Как воспроизвести

1. Откройте `http://127.0.0.1:8090/login`.
2. Введите username:

```text
alice' -- 
```

3. Введите любой пароль.
4. Приложение авторизует пользователя `alice`, хотя пароль неверный.

То же самое через curl:

```bash
curl -i -X POST http://127.0.0.1:8090/login \
  -d "username=alice' -- " \
  -d "password=wrong-password"
```

## Где проблема в коде

Функция `authenticate_vulnerable()` в `vuln_notes/database.py`:

```python
query = (
    "SELECT id, username, role FROM users "
    f"WHERE username = '{username}' AND password = '{password}'"
)
```

## Impact

Атакующий может обойти аутентификацию, получить доступ к чужому аккаунту и дальше использовать другие уязвимости приложения.

## Как исправить

Использовать параметризованные запросы:

```python
connection.execute(
    "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
    (username, password),
)
```

Дополнительно пароль должен храниться не в открытом виде, а как password hash с salt, например через `argon2` или `bcrypt`.
