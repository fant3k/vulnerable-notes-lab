import base64
import unittest

from vuln_notes.sessions import create_session_cookie, parse_session_cookie


class SessionTests(unittest.TestCase):
    """Проверки intentionally weak session format."""

    def test_session_cookie_contains_plain_user_context(self):
        cookie_value = create_session_cookie(1, "alice", "user")
        decoded = base64.urlsafe_b64decode(cookie_value.encode("ascii")).decode("utf-8")

        self.assertEqual(decoded, "1:alice:user")

    def test_session_cookie_can_be_tampered(self):
        forged = base64.urlsafe_b64encode(b"3:admin:admin").decode("ascii")
        session = parse_session_cookie(f"vn_session={forged}")

        self.assertEqual(session["id"], "3")
        self.assertEqual(session["role"], "admin")


if __name__ == "__main__":
    unittest.main()
