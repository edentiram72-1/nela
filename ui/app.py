"""Launch entry point for the NELA desktop UI foundation."""

from __future__ import annotations

import argparse

from core.startup import bootstrap
from ui.window import NelaWindow


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NELA desktop UI shell.")
    parser.add_argument(
        "--headless-smoke",
        action="store_true",
        help="Bootstrap UI dependencies without opening a window.",
    )
    args = parser.parse_args()

    runtime = bootstrap()
    if args.headless_smoke:
        print("NELA UI foundation bootstrapped.")
        return

    window = NelaWindow(runtime=runtime)
    window.run()


if __name__ == "__main__":
    main()
