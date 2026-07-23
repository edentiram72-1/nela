"""Validate NELA language packs."""

from __future__ import annotations

import argparse
from pathlib import Path

from language.loader import DEFAULT_LANGUAGE_PACK
from language.validator import validate_pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate NELA language packs.")
    parser.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_LANGUAGE_PACK),
        help="Language pack directory. Defaults to language/hebrew.",
    )
    args = parser.parse_args()

    report = validate_pack(Path(args.path))
    if report.is_valid:
        print(f"Language pack is valid: {args.path}")
        return 0

    print(f"Language pack is invalid: {args.path}")
    for issue in report.issues:
        location = issue.file or "<unknown>"
        entry = f" entry={issue.entry_id}" if issue.entry_id else ""
        print(f"- {issue.code} {location}{entry}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
