# 01. SQL Injection in Login

## Summary

The login form builds an SQL query using string interpolation. User input is inserted directly into the `WHERE` clause, allowing an attacker to change the query logic.

## Reproduction

1. Open `http://127.0.0.1:8090/login`.
2. Use this username:

```text
alice' -- 
```

3. Enter any password.
4. The application logs in as `alice` without a valid password.

With curl:

```bash
curl -i -X POST http://127.0.0.1:8090/login \
  -d "username=alice' -- " \
  -d "password=wrong-password"
```

## Root Cause

In `vuln_notes/database.py`:

```python
query = (
    "SELECT id, username, role FROM users "
    f"WHERE username = '{username}' AND password = '{password}'"
)
```

## Impact

An attacker can bypass authentication and access the application as another user.

## Remediation

Use parameterized queries:

```python
connection.execute(
    "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
    (username, password),
)
```

Passwords should also be stored as salted password hashes, not plaintext.
