# Writeups: Vulnerable Notes Lab

This directory contains writeups for the vulnerabilities intentionally implemented in the application. Each writeup explains the issue, local reproduction steps, root cause, impact, and remediation.

Start the application first:

```bash
cd vulnerable-notes-lab
scripts/reset_db.sh
scripts/run.sh
```

Demo users:

```text
alice / password123
bob   / qwerty
admin / admin123
```

## Vulnerability Map

| File | Topic | OWASP Top 10 mapping |
| --- | --- | --- |
| [01_sql_injection_login.md](01_sql_injection_login.md) | SQL Injection in login | A03:2021 Injection |
| [02_idor_broken_access_control.md](02_idor_broken_access_control.md) | IDOR in note access | A01:2021 Broken Access Control |
| [03_stored_xss.md](03_stored_xss.md) | Stored XSS in note body | A03:2021 Injection |
| [04_weak_session_cookie.md](04_weak_session_cookie.md) | Tamperable session cookie | A07:2021 Identification and Authentication Failures |
| [05_insecure_file_upload.md](05_insecure_file_upload.md) | Insecure file upload | A05:2021 Security Misconfiguration |
| [06_ssrf_url_preview.md](06_ssrf_url_preview.md) | SSRF through URL preview | A10:2021 Server-Side Request Forgery |
| [07_debug_config_exposure.md](07_debug_config_exposure.md) | Debug config exposure | A05:2021 Security Misconfiguration |
| [08_cors_misconfiguration.md](08_cors_misconfiguration.md) | Permissive CORS | A05:2021 Security Misconfiguration |
