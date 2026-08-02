"""HTML-шаблоны для уязвимого notes-приложения."""

from __future__ import annotations

from html import escape
from typing import Iterable, Mapping, Optional


def page(title: str, body: str, user: Optional[Mapping[str, str]] = None) -> str:
    """Собрать полный HTML-документ.

    Шаблоны оставлены в Python-коде, чтобы проект запускался без Jinja2/Flask.
    Для небольшой лаборатории это проще и делает места уязвимого rendering
    хорошо видимыми в коде.
    """
    nav = ""
    if user:
        nav = (
            '<a href="/notes">Notes</a>'
            '<a href="/new">New note</a>'
            '<a href="/upload">Upload</a>'
            '<a href="/preview">Preview URL</a>'
            '<a href="/debug/config">Debug</a>'
            '<a href="/logout">Logout</a>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Local intentionally vulnerable web-security training lab">
  <meta name="theme-color" content="#090d14">
  <link rel="icon" href="data:image/svg+xml,&lt;svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'&gt;&lt;rect width='64' height='64' rx='14' fill='%2378a9ff'/&gt;&lt;path d='M20 20l11 12-11 12M35 44h10' fill='none' stroke='%23090d14' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/&gt;&lt;/svg&gt;">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #090d14;
      --panel: #111824;
      --panel-strong: #172131;
      --text: #eef4ff;
      --muted: #9aa9bd;
      --accent: #78a9ff;
      --accent-strong: #4f8cff;
      --border: #263348;
      --danger: #ff8b8b;
      --warning: #f7c873;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
      min-height: 100vh;
    }}
    header {{
      background: rgba(9, 13, 20, 0.94);
      border-bottom: 1px solid var(--border);
      color: white;
      padding: 15px 24px;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }}
    header strong {{ letter-spacing: -0.02em; }}
    header a {{ color: #c4d6f3; margin-left: 14px; text-decoration: none; }}
    header a:hover {{ color: white; }}
    .brand {{ display: flex; align-items: center; gap: 12px; }}
    .lab-badge {{
      color: var(--warning); border: 1px solid #735b2f; background: #2b2418;
      border-radius: 999px; padding: 3px 8px; font: 700 11px/1.4 ui-monospace, monospace;
      letter-spacing: .06em;
    }}
    main {{ max-width: 1040px; margin: 42px auto; padding: 0 22px; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 26px;
      box-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
    }}
    label {{ display: block; margin-top: 14px; font-weight: 650; }}
    input, textarea {{
      width: 100%;
      margin-top: 6px;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 8px;
      font: inherit;
      color: var(--text);
      background: #0b111b;
    }}
    textarea {{ min-height: 150px; resize: vertical; }}
    button, .button {{
      display: inline-block;
      margin-top: 18px;
      background: var(--accent-strong);
      color: #fff;
      border: 0;
      border-radius: 8px;
      padding: 10px 14px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
    }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
    th, td {{ border-bottom: 1px solid var(--border); text-align: left; padding: 10px; }}
    code, pre {{ background: #0a1019; border: 1px solid var(--border); border-radius: 7px; padding: 2px 5px; }}
    pre {{ padding: 14px; overflow: auto; }}
    .muted {{ color: var(--muted); }}
    .error {{ color: var(--danger); font-weight: 700; }}
    .note-body {{ border-left: 4px solid var(--accent); padding-left: 16px; }}
    .eyebrow {{ color: var(--accent); font: 700 12px/1.4 ui-monospace, monospace; letter-spacing: .09em; text-transform: uppercase; }}
    .lead {{ color: var(--muted); max-width: 720px; font-size: 17px; }}
    .lab-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 22px; }}
    .lab-card {{ background: var(--panel-strong); border: 1px solid var(--border); border-radius: 10px; padding: 14px; }}
    .lab-card b {{ display: block; font-size: 14px; }}
    .lab-card span {{ color: var(--muted); font-size: 12px; }}
    footer {{ max-width: 1040px; margin: 0 auto 30px; padding: 0 22px; color: var(--muted); font-size: 13px; }}
    @media (max-width: 760px) {{
      header {{ align-items: flex-start; flex-direction: column; }}
      header nav {{ display: flex; flex-wrap: wrap; gap: 8px 14px; }}
      header a {{ margin-left: 0; }}
      .lab-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand"><strong>Vulnerable Notes Lab</strong><span class="lab-badge">LOCAL LAB</span></div>
    <nav>{nav}</nav>
  </header>
  <main>{body}</main>
  <footer>Intentionally vulnerable software · Run only on 127.0.0.1 · For educational use</footer>
</body>
</html>"""


def login_page(error: str = "") -> str:
    message = f'<p class="error">{escape(error)}</p>' if error else ""
    body = f"""
    <section class="panel">
      <p class="eyebrow">Intentionally vulnerable training target</p>
      <h1>Sign in to the local lab</h1>
      <p class="lead">Explore eight isolated web-security scenarios, reproduce the behavior, then compare it with the remediation writeup.</p>
      <p class="muted">Demo users: alice/password123, bob/qwerty, admin/admin123.</p>
      {message}
      <form method="post" action="/login">
        <label>Username
          <input name="username" autocomplete="username">
        </label>
        <label>Password
          <input name="password" type="password" autocomplete="current-password">
        </label>
        <button type="submit">Sign in</button>
      </form>
    </section>
    """
    return page("Sign in", body)


def notes_page(user: Mapping[str, str], notes: Iterable[Mapping[str, str]]) -> str:
    rows = []
    for note in notes:
        rows.append(
            "<tr>"
            f"<td><a href=\"/note?id={note['id']}\">{escape(str(note['title']))}</a></td>"
            f"<td>{escape(str(note['owner']))}</td>"
            f"<td>{escape(str(note['created_at']))}</td>"
            "</tr>"
        )
    rows_html = "\n".join(rows) or '<tr><td colspan="3">No notes yet.</td></tr>'
    body = f"""
    <section class="panel">
      <p class="eyebrow">Lab workspace</p>
      <h1>{escape(user['username'])}'s notes</h1>
      <p class="lead">The application is vulnerable by design. Each scenario below maps to a documented root cause and a repeatable test.</p>
      <table>
        <thead><tr><th>Title</th><th>Owner</th><th>Created</th></tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
      <div class="lab-grid" aria-label="Available vulnerability labs">
        <div class="lab-card"><b>SQL Injection</b><span>Authentication boundary</span></div>
        <div class="lab-card"><b>IDOR</b><span>Object authorization</span></div>
        <div class="lab-card"><b>Stored XSS</b><span>Output encoding</span></div>
        <div class="lab-card"><b>Weak session</b><span>Client trust</span></div>
        <div class="lab-card"><b>File upload</b><span>Active content</span></div>
        <div class="lab-card"><b>SSRF</b><span>Network boundary</span></div>
        <div class="lab-card"><b>Debug exposure</b><span>Configuration leak</span></div>
        <div class="lab-card"><b>Permissive CORS</b><span>Origin trust</span></div>
      </div>
    </section>
    """
    return page("Notes", body, user)


def note_page(user: Mapping[str, str], note: Mapping[str, str]) -> str:
    """Показать заметку.

    `note['body']` намеренно вставляется без escape. Это учебная Stored XSS:
    пользовательский ввод хранится в базе и затем выполняется браузером.
    """
    body = f"""
    <section class="panel">
      <p class="muted">Owner: {escape(str(note['owner']))} | Created: {escape(str(note['created_at']))}</p>
      <h1>{escape(str(note['title']))}</h1>
      <div class="note-body">{note['body']}</div>
    </section>
    """
    return page(str(note["title"]), body, user)


def new_note_page(user: Mapping[str, str], error: str = "") -> str:
    message = f'<p class="error">{escape(error)}</p>' if error else ""
    body = f"""
    <section class="panel">
      <h1>New note</h1>
      {message}
      <form method="post" action="/new">
        <label>Title
          <input name="title">
        </label>
        <label>Body
          <textarea name="body"></textarea>
        </label>
        <button type="submit">Save note</button>
      </form>
    </section>
    """
    return page("New note", body, user)


def upload_page(user: Mapping[str, str], message: str = "") -> str:
    notice = f"<p>{message}</p>" if message else ""
    body = f"""
    <section class="panel">
      <h1>Upload attachment</h1>
      {notice}
      <p class="muted">The lab intentionally serves uploaded HTML from the application origin.</p>
      <form method="post" action="/upload" enctype="multipart/form-data">
        <label>Attachment
          <input name="file" type="file">
        </label>
        <button type="submit">Upload</button>
      </form>
    </section>
    """
    return page("Upload", body, user)


def preview_page(user: Mapping[str, str], result: str = "") -> str:
    rendered_result = f"<pre>{escape(result)}</pre>" if result else ""
    body = f"""
    <section class="panel">
      <h1>URL preview</h1>
      <form method="get" action="/preview">
        <label>URL
          <input name="url" placeholder="http://127.0.0.1:8090/debug/config">
        </label>
        <button type="submit">Fetch preview</button>
      </form>
      {rendered_result}
    </section>
    """
    return page("URL preview", body, user)


def debug_page(user: Mapping[str, str], config_dump: str) -> str:
    body = f"""
    <section class="panel">
      <h1>Debug configuration</h1>
      <pre>{escape(config_dump)}</pre>
    </section>
    """
    return page("Debug config", body, user)


def error_page(status: int, title: str, message: str) -> str:
    body = f"""
    <section class="panel">
      <h1>{escape(title)}</h1>
      <p>{escape(message)}</p>
      <p><a href="/" class="button">Back</a></p>
    </section>
    """
    return page(f"{status} {title}", body)
