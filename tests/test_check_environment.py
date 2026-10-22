"""Tests for skills/img2pptx/scripts/check_environment.py.

Run with:
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "img2pptx" / "scripts" / "check_environment.py"


class CheckEnvironmentTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_help(self) -> None:
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--json", result.stdout)
        self.assertIn("--strict", result.stdout)

    def test_human_output(self) -> None:
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("img2pptx environment check", result.stdout)
        self.assertIn("Summary:", result.stdout)
        self.assertIn("image_decoder", result.stdout)

    def test_json_output(self) -> None:
        result = self.run_script("--json")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        report = json.loads(result.stdout)
        self.assertIn("platform", report)
        self.assertIn("python", report)
        self.assertIn("modules", report)
        self.assertIn("tools", report)
        self.assertIn("summary", report)
        self.assertIn("recommendations", report)
        for key in ("image_decoder", "svg_renderer", "pptx_generator", "powerpoint_app"):
            self.assertIn(key, report["summary"])
            self.assertIsInstance(report["summary"][key], bool)

    def test_strict_exit_code_is_meaningful(self) -> None:
        result = self.run_script("--strict")
        self.assertIn(result.returncode, (0, 1), result.stderr)


if __name__ == "__main__":
    unittest.main()
