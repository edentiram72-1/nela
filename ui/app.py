"""Launch entry point for the NELA desktop UI foundation."""

from __future__ import annotations

import argparse
from pathlib import Path

from core.startup import bootstrap
from ui.web import serve_visual_prototype
from ui.window import NelaWindow


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NELA desktop UI shell.")
    parser.add_argument(
        "--headless-smoke",
        action="store_true",
        help="Bootstrap UI dependencies without opening a window.",
    )
    parser.add_argument(
        "--tk-shell",
        action="store_true",
        help="Open the temporary Tkinter shell instead of the visual HTML prototype.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Local browser prototype port. Use 0 to choose an available port.",
    )
    args = parser.parse_args()

    runtime = bootstrap()
    if args.headless_smoke:
        print("NELA UI foundation bootstrapped.")
        return

    if args.tk_shell:
        window = NelaWindow(runtime=runtime)
        window.run()
        return

    prototype = Path(__file__).resolve().parents[1] / "design" / "nela_living_eye.html"
    serve_visual_prototype(runtime=runtime, index_path=prototype, port=args.port)


if __name__ == "__main__":
    main()
