import subprocess
import sys
import unittest


class UIAppTests(unittest.TestCase):
    def test_headless_smoke_bootstraps_ui_dependencies(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "ui.app", "--headless-smoke"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("NELA UI foundation bootstrapped.", result.stdout)


if __name__ == "__main__":
    unittest.main()
