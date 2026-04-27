# Vulnerable Notes Lab

Vulnerable Notes Lab is a local intentionally vulnerable web application for OWASP Top 10 practice, security writeups, and AppSec portfolio demonstration.

The project simulates a simple notes application: users log in, create notes, open note details, upload attachments, and use a URL preview feature. Several vulnerabilities are intentionally implemented to make the project useful for Application Security / Security Engineer interviews.

> This application is intentionally vulnerable. Run it locally on `127.0.0.1` only. Do not expose it to the internet.

## Features

- Local web application built with the Python standard library, without Flask or FastAPI.
- SQLite database with demo users and notes.
- Simple HTML UI for notes, uploads, and URL preview.
- 8 intentionally implemented vulnerabilities with writeups:
  - SQL Injection in login;
  - IDOR / Broken Access Control;
  - Stored XSS;
  - Weak session cookie;
  - Insecure file upload;
  - SSRF through URL preview;
  - Debug config exposure;
  - Permissive CORS.
- Russian and English writeups with reproduction steps, impact, root cause, and remediation.
- Unit tests that document the lab behavior.
- GitHub Actions workflow for tests.

## Architecture

```text
vulnerable-notes-lab/
  app.py                    # entrypoint
  vuln_notes/
    config.py               # paths, host/port, demo secret
    database.py             # SQLite and intentionally vulnerable queries
    server.py               # HTTP routes and web endpoints
    sessions.py             # weak client-side session model
    templates.py            # HTML rendering, including the Stored XSS sink
  docs/
    writeups/
      ru/                   # Russian writeups
      en/                   # English writeups
  scripts/
    run.sh                  # start the app
    reset_db.sh             # reset the SQLite database
    test.sh                 # run tests and compile check
  tests/
    test_database.py
    test_sessions.py
```

## Quick Start

```bash
cd vulnerable-notes-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
scripts/reset_db.sh
scripts/run.sh
```

Open the application:

```text
http://127.0.0.1:8090
```

Demo users:

```text
alice / password123
bob   / qwerty
admin / admin123
```

Change the port if needed:

```bash
VNL_PORT=9090 scripts/run.sh
```

## How to Use This Lab

1. Start the application locally.
2. Open the English writeups: [docs/writeups/en](docs/writeups/en/README.md).
3. Reproduce each vulnerability.
4. Locate the vulnerable code path.
5. Read the remediation section and implement a secure fix in a separate branch.

Russian writeups are available here: [docs/writeups/ru](docs/writeups/ru/README.md).

## Example: SQL Injection

Use this username in the login form:

```text
alice' -- 
```

Use any password. The vulnerable code is in `vuln_notes/database.py`, where the SQL query is built with an f-string.

## Example: IDOR

Log in as `alice` and open:

```text
http://127.0.0.1:8090/note?id=3
```

Alice can read Bob's note because the detail endpoint does not check `owner_id`.

## Example: SSRF

Log in and open:

```text
http://127.0.0.1:8090/preview?url=http://127.0.0.1:8090/internal/metadata
```

The server fetches an internal endpoint and displays the response.

## Testing

```bash
scripts/test.sh
```

Or manually:

```bash
python3 -B -m unittest discover -s tests
PYTHONPYCACHEPREFIX=/tmp/vulnerable_notes_pycache python3 -m compileall vuln_notes
```

## What I Learned

- How OWASP Top 10 vulnerabilities appear in real application code.
- Why SQL Injection happens when data and SQL commands are mixed.
- How Broken Access Control can exist even when login is implemented.
- How output encoding differs from input validation.
- Why base64-encoded cookies are not secure sessions.
- How SSRF abuses the server-side network context.
- How to write security findings with reproduction, root cause, impact, and remediation.

## Resume Description

```text
Vulnerable Notes Lab
Built an intentionally vulnerable Python web application mapped to OWASP Top 10.
Implemented SQLi, IDOR, Stored XSS, weak sessions, insecure upload, SSRF, CORS
misconfiguration and debug exposure, with bilingual writeups and remediation notes.
```

## Limitations

- This is a training lab, not a production application.
- The UI is intentionally minimal and focused on security flaws.
- Some vulnerabilities are simplified to make them easier to explain during interviews.
- The app must not be bound to a public network interface.

## Roadmap

- Add a secure branch with fixes and diff-based writeups.
- Add Dockerfile and docker-compose.
- Add Playwright screenshots for README.
- Add separate labs for CSRF and mass assignment.
- Add an OWASP ASVS checklist for each secure-fix version.

## Ethics

This project is intended for local training, portfolio demonstration, and interview preparation. Do not use it as a base for a real application without removing the vulnerabilities.
