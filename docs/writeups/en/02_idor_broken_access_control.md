# 02. IDOR in the lab: reading another user's private note

## Summary

The notes list only shows the current user's notes, but `/note?id=...` does not check note ownership. The object is selected by a predictable id without an authorization check.

## Reproduction

1. Log in as `alice / password123`.
2. Open:

```text
http://127.0.0.1:8090/note?id=3
```

3. Alice can read Bob's private note.

The [HTTP test](../../../tests/test_http.py) logs in as Alice and checks
that the response contains Bob's note and identifies Bob as its owner.

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

## Fix and verification

The [owner-scoped lookup](../../../vuln_notes/database.py) checks the
requested note and its owner in the same parameterized query:

```sql
SELECT ...
FROM notes
WHERE notes.id = ? AND notes.owner_id = ?
```

The application must supply the user ID from a verified session. A caller
can treat foreign and nonexistent notes alike because both return no row.
If the product requires administrator access, enforce it through a
separate, explicit authorization policy.

The [regression tests](../../../tests/test_database.py) verify that Alice
cannot read Bob's note and Bob can read the same note. They also check that
Alice can still read her own note and that alternate forms of the ID do
not bypass the owner check.

```sh
python3 -B -m unittest discover -s tests -k idor -k owner_scoped -v
```

The lab's HTTP route remains intentionally vulnerable for the reproduction
above. The fixed lookup is tested at the database boundary. The lab's
unsigned session cookie is a separate exercise and cannot provide a
trusted identity for a production route.
