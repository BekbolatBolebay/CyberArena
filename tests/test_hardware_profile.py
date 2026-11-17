"""Tests for CyberArena hardware-adaptive profiler and compose generator."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from hardware_profile import HostSpecs, choose_profile, render_adaptive_compose  # noqa: E402


class HardwareProfileTests(unittest.TestCase):
    def test_light_when_no_docker_or_low_ram(self) -> None:
        no_docker = HostSpecs(8, 16384, 8000, 50.0, False, "none")
        profile, _ = choose_profile(no_docker)
        self.assertEqual(profile, "light")

        low_ram = HostSpecs(4, 4096, 2000, 20.0, True, "docker")
        profile, _ = choose_profile(low_ram)
        self.assertEqual(profile, "light")

        low_avail = HostSpecs(8, 8192, 1000, 20.0, True, "docker")
        profile, _ = choose_profile(low_avail)
        self.assertEqual(profile, "light")

    def test_balanced_on_mid_laptop(self) -> None:
        mid = HostSpecs(4, 8192, 4200, 25.0, True, "docker")
        profile, _ = choose_profile(mid)
        self.assertEqual(profile, "balanced")
        yml = render_adaptive_compose("balanced")
        self.assertIn("juice-shop:", yml)
        self.assertNotIn("dvwa:", yml)

    def test_full_on_strong_laptop(self) -> None:
        strong = HostSpecs(12, 16000, 8000, 40.0, True, "docker")
        profile, _ = choose_profile(strong)
        self.assertEqual(profile, "full")
        yml = render_adaptive_compose("full")
        self.assertIn("juice-shop:", yml)
        self.assertIn("dvwa:", yml)
        self.assertIn("portal:", yml)
        self.assertIn("ip-camera:", yml)

    def test_forced_override_respects_missing_docker(self) -> None:
        no_docker = HostSpecs(12, 16000, 8000, 40.0, False, "none")
        profile, _ = choose_profile(no_docker, forced="full")
        self.assertEqual(profile, "light")


if __name__ == "__main__":
    unittest.main()
