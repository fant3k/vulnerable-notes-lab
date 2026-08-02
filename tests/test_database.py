import tempfile
import unittest
from pathlib import Path

from vuln_notes.database import (
    authenticate_vulnerable,
    create_note,
    get_connection,
    get_note_vulnerable,
    init_database,
)


class VulnerableDatabaseTests(unittest.TestCase):
    """Тесты фиксируют поведение лаборатории, включая намеренные уязвимости."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "lab.sqlite3"
        init_database(db_path=self.db_path, reset=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_seeded_user_can_login(self):
        with get_connection(self.db_path) as connection:
            user = authenticate_vulnerable(connection, "alice", "password123")

        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "alice")

    def test_sql_injection_bypasses_password_check(self):
        with get_connection(self.db_path) as connection:
            user = authenticate_vulnerable(connection, "alice' -- ", "wrong-password")

        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "alice")

    def test_idor_allows_reading_another_users_note(self):
        with get_connection(self.db_path) as connection:
            note = get_note_vulnerable(connection, "3")

        self.assertIsNotNone(note)
        self.assertEqual(note["owner"], "bob")

    def test_idor_lookup_does_not_add_a_second_sql_injection(self):
        with get_connection(self.db_path) as connection:
            note = get_note_vulnerable(connection, "3 OR 1=1")

        self.assertIsNone(note)

    def test_note_body_is_stored_without_sanitization(self):
        payload = '<script>alert("xss")</script>'
        with get_connection(self.db_path) as connection:
            note_id = create_note(connection, 1, "XSS test", payload)
            note = get_note_vulnerable(connection, str(note_id))

        self.assertIn(payload, note["body"])


if __name__ == "__main__":
    unittest.main()
