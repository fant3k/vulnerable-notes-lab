# 07. Debug Config Exposure

## Summary

The `/debug/config` endpoint is available to any authenticated user and exposes internal configuration such as the database path, upload directory, fake secret key, statistics, and current user context.

## Reproduction

1. Log in as any user.
2. Open:

```text
http://127.0.0.1:8090/debug/config
```

## Root Cause

In `vuln_notes/server.py`:

```python
"secret_key": DEMO_SECRET_KEY,
"database_path": str(DB_PATH),
"upload_dir": str(UPLOAD_DIR),
```

## Impact

Debug endpoints can disclose secrets, environment variables, filesystem paths, component versions, and internal application structure. This information helps attackers chain additional vulnerabilities.

## Remediation

- Disable debug endpoints in production.
- Restrict access to a dedicated admin role and stronger authentication.
- Never display secrets in UI or logs.
- Separate debug builds from production builds.
