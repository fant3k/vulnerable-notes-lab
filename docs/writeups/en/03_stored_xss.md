# 03. Stored XSS

## Summary

The application stores note bodies as raw text and renders them into HTML without output encoding. A saved `<script>` tag executes when the note is opened.

## Reproduction

1. Log in.
2. Create a note with this body:

```html
<script>alert(document.cookie)</script>
```

3. Open the note.

## Root Cause

In `vuln_notes/templates.py`:

```python
<div class="note-body">{note['body']}</div>
```

`note['body']` is not escaped.

## Impact

Stored XSS can execute JavaScript for every user who opens the affected note. In a real application it could steal session data, perform actions as the victim, or modify the UI.

## Remediation

At minimum:

```python
escape(str(note["body"]))
```

If rich text is required, use an allowlist-based sanitizer. CSP is useful defense-in-depth but does not replace output encoding.
