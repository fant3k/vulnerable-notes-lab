# 04. Weak Session Cookie

## Summary

The application stores user id, username, and role directly in a base64-encoded cookie. The cookie is not signed and is not backed by server-side session state.

## Reproduction

1. Log in as `alice`.
2. Generate a forged cookie value:

```bash
python3 - <<'PY'
import base64
print(base64.urlsafe_b64encode(b"3:admin:admin").decode())
PY
```

3. Replace the `vn_session` cookie with the generated value.
4. The application trusts the modified user context.

## Root Cause

In `vuln_notes/sessions.py`:

```python
raw_value = f"{user_id}:{username}:{role}".encode("utf-8")
return base64.urlsafe_b64encode(raw_value).decode("ascii")
```

Base64 is encoding, not protection.

## Impact

An attacker can impersonate another user or change their role if they know the cookie format.

## Remediation

- Store only a random session id client-side and keep session state server-side.
- Or sign cookies with HMAC and verify the signature.
- Set `Secure`, `HttpOnly`, and `SameSite`.
- Add session expiration and server-side invalidation.
