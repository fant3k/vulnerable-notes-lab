# 05. Insecure File Upload

## Summary

The `/upload` endpoint accepts arbitrary filenames and content, saves files under `data/uploads/`, and serves them back through `/uploads/...`. There is no extension allowlist, content validation, or safe download policy.

## Reproduction

1. Log in.
2. Open `/upload`.
3. Choose an HTML file named:

```text
xss.html
```

4. Put this content in the file:

```html
<script>alert("uploaded html")</script>
```

5. Open `/uploads/xss.html`.

## Root Cause

In `vuln_notes/server.py`:

```python
destination = UPLOAD_DIR / filename
destination.write_bytes(content)
```

The response content type is inferred from the extension:

```python
content_type = mimetypes.guess_type(path.name)[0] or "text/plain"
```

## Impact

In production this can lead to Stored XSS, malicious file hosting, content policy bypasses, or even remote code execution if uploaded files are executed by the server.

## Remediation

- Use an extension allowlist.
- Rename files to random server-generated names.
- Store uploads outside the web root.
- Serve user files as `application/octet-stream`.
- Enforce file size limits.
- Add malware/content scanning where appropriate.
