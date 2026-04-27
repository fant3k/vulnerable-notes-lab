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
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --panel: #ffffff;
      --text: #1f2937;
      --muted: #667085;
      --accent: #2563eb;
      --border: #d7deea;
      --danger: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    header {{
      background: #111827;
      color: white;
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }}
    header a {{ color: #dbeafe; margin-left: 14px; text-decoration: none; }}
    main {{ max-width: 980px; margin: 32px auto; padding: 0 20px; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 22px;
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }}
    label {{ display: block; margin-top: 14px; font-weight: 650; }}
    input, textarea {{
      width: 100%;
      margin-top: 6px;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      font: inherit;
    }}
    textarea {{ min-height: 150px; resize: vertical; }}
    button, .button {{
      display: inline-block;
      margin-top: 18px;
      background: var(--accent);
      color: white;
      border: 0;
      border-radius: 6px;
      padding: 10px 14px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
    }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
    th, td {{ border-bottom: 1px solid var(--border); text-align: left; padding: 10px; }}
    code, pre {{ background: #eef2f7; border-radius: 6px; padding: 2px 5px; }}
    pre {{ padding: 14px; overflow: auto; }}
    .muted {{ color: var(--muted); }}
    .error {{ color: var(--danger); font-weight: 700; }}
    .note-body {{ border-left: 4px solid var(--accent); padding-left: 16px; }}
  </style>
</head>
<body>
  <header>
    <strong>Vulnerable Notes Lab</strong>
    <nav>{nav}</nav>
  </header>
  <main>{body}</main>
</body>
</html>"""


def login_page(error: str = "") -> str:
    message = f'<p class="error">{escape(error)}</p>' if error else ""
    body = f"""
    <section class="panel">
      <h1>Sign in</h1>
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
      <h1>{escape(user['username'])}'s notes</h1>
      <table>
        <thead><tr><th>Title</th><th>Owner</th><th>Created</th></tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
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
      <form method="post" action="/upload">
        <label>Filename
          <input name="filename" placeholder="demo.html">
        </label>
        <label>File content
          <textarea name="content"></textarea>
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
