# Lab design and trust boundaries

Vulnerable Notes Lab is intentionally unsafe, but it is not meant to be
accidentally unsafe. The distinction matters: every advertised flaw should be
isolated, reproducible and covered by a test.

## Scenario contract

| Scenario | Trust boundary | Automated evidence |
|---|---|---|
| SQL Injection | Form input → SQL interpreter | Password bypass succeeds |
| IDOR | User identity → note ownership | Alice reads Bob's note |
| Stored XSS | Note body → HTML document | Raw script reaches response |
| Weak session | Cookie → authenticated identity | Forged user id is accepted |
| File upload | Multipart file → same-origin content | HTML is served inline |
| SSRF | URL input → server network access | Internal metadata is returned |
| Debug exposure | Authenticated user → configuration | Demo secret and paths leak |
| Permissive CORS | Origin header → credentialed response | Arbitrary origin is reflected |

## Guardrails

- The default bind address is `127.0.0.1`.
- Docker Compose publishes the port on localhost only.
- Uploads are capped at 256 KiB to prevent an unrelated disk-exhaustion lab.
- Upload filenames use a basename to keep path traversal out of this exercise.
- IDOR lookup is parameterized to keep SQL Injection out of that exercise.
- Session cookies use `HttpOnly` and `SameSite=Lax`; their intentional weakness
  is integrity, not missing browser flags.
- Demo secrets and tokens are visibly fake and scoped to the local lab.

## Testing strategy

Unit tests cover the database and session primitives. Integration tests start
the real HTTP server on an ephemeral localhost port and verify the eight
documented scenarios through requests. A green CI run therefore means that the
lab behavior described in the writeups is actually reproducible.

