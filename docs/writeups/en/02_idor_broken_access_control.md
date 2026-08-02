# 02. IDOR / Broken Access Control

## Summary

The notes list only shows the current user's notes, but `/note?id=...` does not check note ownership. The object is selected by a predictable id without an authorization check.

## Reproduction

1. Log in as `alice / password123`.
2. Open:

```text
http://127.0.0.1:8090/note?id=3
```

3. Alice can read Bob's private note.

## Root Cause

`get_note_vulnerable()` in `vuln_notes/database.py` selects by note id only:

```python
WHERE notes.id = ?
```

There is no condition such as:

```sql
AND notes.owner_id = ?
```

## Impact

Any authenticated user can enumerate note ids and read other users' private notes.

## Remediation

Include the current user id in the query:

```python
SELECT ...
FROM notes
WHERE notes.id = ? AND notes.owner_id = ?
```

Admin access should be handled through an explicit authorization branch.
