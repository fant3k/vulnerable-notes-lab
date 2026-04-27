# 08. Permissive CORS

## Summary

The application reflects any `Origin` into `Access-Control-Allow-Origin` and also sends `Access-Control-Allow-Credentials: true`.

## Reproduction

```bash
curl -i http://127.0.0.1:8090/notes \
  -H "Origin: https://evil.example"
```

The response includes:

```text
Access-Control-Allow-Origin: https://evil.example
Access-Control-Allow-Credentials: true
```

## Root Cause

In `vuln_notes/server.py`:

```python
origin = self.headers.get("Origin", "*")
self.send_header("Access-Control-Allow-Origin", origin)
self.send_header("Access-Control-Allow-Credentials", "true")
```

## Impact

If cookies are sent by the browser, a malicious website may be able to read authenticated responses from the vulnerable application.

## Remediation

- Use a strict allowlist of trusted origins.
- Do not reflect `Origin` automatically.
- Avoid credentials unless they are required.
- Separate CORS policy for public and authenticated APIs.
