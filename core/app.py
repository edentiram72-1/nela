"""NELA OS application entry point."""

from __future__ import annotations

from core.startup import bootstrap


def main() -> None:
    runtime = bootstrap()
    print(
        "NELA OS foundation runtime ready "
        f"({runtime.config.environment}, voice={runtime.config.enable_voice}, "
        f"vision={runtime.config.enable_vision})"
    )


if __name__ == "__main__":
    main()

