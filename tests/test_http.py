import base64
import http.cookiejar
import os
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def available_port() -> int:
    with socket.socket() as candidate:
        candidate.bind(("127.0.0.1", 0))
        return int(candidate.getsockname()[1])


class VulnerableNotesHttpTests(unittest.TestCase):
    """End-to-end checks for every intentionally vulnerable HTTP scenario."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.port = available_port()
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        env = os.environ.copy()
        env["VNL_PORT"] = str(cls.port)
        env["VNL_DATA_DIR"] = cls.temp_dir.name
        cls.process = subprocess.Popen(
            ["python3", "app.py"],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(f"{cls.base_url}/health", timeout=0.25) as response:
                    if response.status == 200:
                        break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.05)
        else:
            cls.process.terminate()
            raise RuntimeError("test server did not start")

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        try:
            cls.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            cls.process.kill()
        cls.temp_dir.cleanup()

    def setUp(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.client = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )

    def request(self, path: str, data=None, headers=None):
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers or {},
        )
        return self.client.open(request, timeout=4)

    def login(self, username="alice", password="password123"):
        payload = urllib.parse.urlencode(
            {"username": username, "password": password}
        ).encode()
        return self.request("/login", data=payload)

    def test_health_and_login_flow(self):
        with self.login() as response:
            body = response.read().decode()
        self.assertEqual(response.geturl(), f"{self.base_url}/notes")
        self.assertIn("alice's notes", body)

    def test_sql_injection_bypasses_login(self):
        with self.login("alice' -- ", "wrong-password") as response:
            body = response.read().decode()
        self.assertIn("alice's notes", body)

    def test_idor_returns_another_users_note(self):
        self.login().close()
        with self.request("/note?id=3") as response:
            body = response.read().decode()
        self.assertIn("Bob private note", body)
        self.assertIn("Owner: bob", body)

    def test_stored_xss_reaches_the_html_response(self):
        self.login().close()
        payload = '<script>document.body.dataset.xss="executed"</script>'
        note = urllib.parse.urlencode({"title": "XSS", "body": payload}).encode()
        with self.request("/new", data=note) as response:
            body = response.read().decode()
        self.assertIn(payload, body)

    def test_unsigned_cookie_allows_impersonation(self):
        forged = base64.urlsafe_b64encode(b"3:admin:admin").decode()
        request = urllib.request.Request(
            f"{self.base_url}/notes",
            headers={"Cookie": f"vn_session={forged}"},
        )
        with urllib.request.urlopen(request, timeout=4) as response:
            body = response.read().decode()
        self.assertIn("admin's notes", body)

    def test_uploaded_html_is_served_inline_from_the_app_origin(self):
        self.login().close()
        boundary = "----vnl-integration-boundary"
        html = b'<script>document.body.dataset.uploaded="true"</script>'
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="proof.html"\r\n'
            "Content-Type: text/html\r\n\r\n"
        ).encode() + html + f"\r\n--{boundary}--\r\n".encode()
        with self.request(
            "/upload",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        ) as response:
            self.assertIn("Uploaded", response.read().decode())
        with self.request("/uploads/proof.html") as response:
            self.assertEqual(response.headers.get_content_type(), "text/html")
            self.assertEqual(response.read(), html)

    def test_ssrf_reaches_internal_endpoint_on_the_same_server(self):
        self.login().close()
        target = urllib.parse.quote(f"{self.base_url}/internal/metadata", safe="")
        with self.request(f"/preview?url={target}") as response:
            body = response.read().decode()
        self.assertIn("metadata-demo", body)
        self.assertIn("vnl_metadata_token_for_training_only", body)

    def test_debug_endpoint_exposes_demo_configuration(self):
        self.login().close()
        with self.request("/debug/config") as response:
            body = response.read().decode()
        self.assertIn("dev-secret-key-do-not-use-in-production", body)
        self.assertIn(self.temp_dir.name, body)

    def test_cors_reflects_untrusted_origin_with_credentials(self):
        self.login().close()
        with self.request(
            "/notes", headers={"Origin": "https://evil.example"}
        ) as response:
            self.assertEqual(
                response.headers["Access-Control-Allow-Origin"],
                "https://evil.example",
            )
            self.assertEqual(
                response.headers["Access-Control-Allow-Credentials"], "true"
            )


if __name__ == "__main__":
    unittest.main()
