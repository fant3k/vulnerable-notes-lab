# 06. SSRF through URL Preview

## Summary

The `/preview?url=...` endpoint accepts a user-controlled URL and makes a server-side request with `urllib.request.urlopen()`. There is no host allowlist, private IP filtering, or scheme validation.

## Reproduction

1. Log in.
2. Open:

```text
http://127.0.0.1:8090/preview?url=http://127.0.0.1:8090/internal/metadata
```

3. The application fetches the internal endpoint from the server side and displays the response.

## Root Cause

In `vuln_notes/server.py`:

```python
with urllib.request.urlopen(url, timeout=2) as response:
    body = response.read(2048)
```

The user controls the destination.

## Impact

In production SSRF may allow access to internal services, cloud metadata endpoints, admin panels, or internal dashboards. It may also enable network scanning from a trusted network position.

## Remediation

- Allow only explicitly trusted domains.
- Block private IP ranges, localhost, and link-local addresses after DNS resolution.
- Allow only `http` and `https`.
- Do not follow redirects into private ranges.
- Limit timeout, response size, and content type.
