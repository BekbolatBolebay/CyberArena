"""Automated tests for CyberArena Portal security, missions, and API."""

from __future__ import annotations

import http.cookiejar
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

PORTAL_DIR = Path(__file__).resolve().parent.parent / "portal"
sys.path.insert(0, str(PORTAL_DIR))

from missions import FLAG_HASHES, run_sandboxed_sqli, verify_flag  # noqa: E402
from server import ArenaDatabase, CyberArenaServer  # noqa: E402


class CyberArenaPortalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test_arena.db"
        self.db = ArenaDatabase(self.db_path)
        self.server = CyberArenaServer(("127.0.0.1", 0), db=self.db, trust_proxy=False)
        self.port = self.server.server_address[1]
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmpdir.cleanup()

    def _req(self, method: str, path: str, body: dict | None = None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"} if data is not None else {}
        req = urllib.request.Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=5) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, dict(resp.headers), json.loads(raw) if resp.headers.get("Content-Type", "").startswith("application/json") else raw
        except urllib.error.HTTPError as err:
            raw = err.read().decode("utf-8")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = raw
            return err.code, dict(err.headers), parsed

    def test_security_headers_and_no_flag_leaks(self) -> None:
        status, headers, html = self._req("GET", "/")
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("default-src 'self'", headers.get("Content-Security-Policy", ""))
        self.assertNotIn("FLAG{KEIN_SYSTEM_IST_SICHER_01}", html)

        _, _, missions_res = self._req("GET", "/api/missions")
        self.assertEqual(len(missions_res["missions"]), 6)
        serialized = json.dumps(missions_res)
        self.assertNotIn("FLAG{", serialized)

    def test_path_traversal_blocked(self) -> None:
        status, _, _ = self._req("GET", "/../../etc/passwd")
        self.assertEqual(status, 404)

    def test_robots_and_clay_vault_mission(self) -> None:
        status, _, robots = self._req("GET", "/robots.txt")
        self.assertEqual(status, 200)
        self.assertIn("/clay-audit-vault", robots)

        status, _, vault = self._req("GET", "/clay-audit-vault")
        self.assertEqual(status, 200)
        self.assertTrue(verify_flag("m01_recon", vault["flag"]))

    def test_sandboxed_sqli_simulator_safety(self) -> None:
        res_ok = run_sandboxed_sqli("' OR 1=1--", "anything")
        self.assertTrue(res_ok["ok"])
        self.assertEqual(res_ok["user"], "admin")
        self.assertTrue(verify_flag("m03_sqli", res_ok["secret_note"]))

        res_blocked = run_sandboxed_sqli("admin'; DROP TABLE users;--", "x")
        self.assertFalse(res_blocked["ok"])
        self.assertIn("тыйым салынған", res_blocked["error"])

    def test_auth_solve_leaderboard_and_delete(self) -> None:
        # Register
        status, _, reg = self._req("POST", "/api/register", {"username": "benjamin", "password": "clay_secret_password"})
        self.assertEqual(status, 201)
        self.assertEqual(reg["user"]["username"], "benjamin")

        # Duplicate blocked
        status, _, _ = self._req("POST", "/api/register", {"username": "benjamin", "password": "clay_secret_password"})
        self.assertEqual(status, 409)

        # Solve m02 via decoded Base64 token
        status, _, sub1 = self._req("POST", "/api/submit", {"mission_id": "m02_sniff", "flag": "FLAG{CLEARTEXT_HTTP_LEAK_7742}"})
        self.assertEqual(status, 200)
        self.assertTrue(sub1["newly_solved"])
        self.assertEqual(sub1["user"]["score"], 150)

        # Idempotent re-submit does not double-count
        status, _, sub2 = self._req("POST", "/api/submit", {"mission_id": "m02_sniff", "flag": "FLAG{CLEARTEXT_HTTP_LEAK_7742}"})
        self.assertEqual(status, 200)
        self.assertFalse(sub2["newly_solved"])
        self.assertEqual(sub2["user"]["score"], 150)

        # Leaderboard reflects score
        status, _, lb = self._req("GET", "/api/leaderboard")
        self.assertEqual(status, 200)
        self.assertEqual(lb["leaderboard"][0]["username"], "benjamin")
        self.assertEqual(lb["leaderboard"][0]["score"], 150)

        # Simulators work over HTTP
        status, _, cam = self._req("POST", "/api/sim/camera", {"username": "admin", "password": "camera123"})
        self.assertEqual(status, 200)
        self.assertTrue(cam["ok"])
        self.assertTrue(verify_flag("m05_camera", cam["flag"]))

        status, _, ddos = self._req("POST", "/api/sim/ddos", {"subnet": "198.51.100.0/24"})
        self.assertEqual(status, 200)
        self.assertTrue(ddos["ok"])
        self.assertTrue(verify_flag("m06_ddos", ddos["flag"]))

        # Verify all 6 flag hashes are registered
        self.assertEqual(len(FLAG_HASHES), 6)

        # Delete account
        status, _, del_res = self._req("DELETE", "/api/account")
        self.assertEqual(status, 200)
        self.assertTrue(del_res["ok"])

        status, _, me_after = self._req("GET", "/api/me")
        self.assertIsNone(me_after["user"])


if __name__ == "__main__":
    unittest.main()
