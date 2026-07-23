import subprocess
import sys
import unittest


class AppCliTests(unittest.TestCase):
    def test_once_mode_prints_brain_summary(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "core.app",
                "--once",
                "Open Spotify and play my Night playlist",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("NELA Brain", result.stdout)
        self.assertIn("Intent: PlayMedia", result.stdout)
        self.assertIn("Plan: 4 task(s)", result.stdout)
        self.assertIn("ok:", result.stdout)
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
