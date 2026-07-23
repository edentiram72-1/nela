"""Export a Claude review bundle from repository files.

The bundle is a plain Markdown document that can be pasted into Claude or
attached to a GitHub pull request. It does not connect to Claude directly.
"""

from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_REVIEW_FILES = (
    "README.md",
    "docs/architecture.md",
    "docs/ai_handoff.md",
    "docs/coding_rules.md",
    "docs/api.md",
    "docs/decisions.md",
    "docs/memory_model.md",
    "docs/roadmap.md",
    "brain/README.md",
    "brain/conversation.py",
    "brain/intent_router.py",
    "brain/planner.py",
    "brain/decision.py",
    "brain/context.py",
    "brain/dispatcher.py",
    "brain/memory_manager.py",
    "core/events.py",
    "core/startup.py",
    "agents/base.py",
    "agents/registry.py",
    "tests/test_intent_recognition.py",
    "tests/test_planner.py",
    "tests/test_decision_engine.py",
    "tests/test_context_engine.py",
    "tests/test_memory_manager.py",
    "tests/test_dispatcher.py",
)


CLAUDE_REVIEW_PROMPT = """You are Claude reviewing NELA OS.

Responsibilities:
- Review architecture.
- Review documentation.
- Find edge cases.
- Improve UX ideas.
- Suggest risk and performance improvements.

Rules:
- Do not rewrite completed modules without justification.
- Do not ask for direct access to local files.
- Treat GitHub, pasted bundles, and pull requests as the collaboration layer.
- Focus on architecture, documentation, edge cases, security, maintainability, and long-term extensibility.
- Return findings with severity, affected files, reasoning, and suggested next steps.
"""


@dataclass(frozen=True)
class BundleResult:
    output_path: Path
    included_files: tuple[str, ...]
    missing_files: tuple[str, ...]


def export_bundle(
    repo_root: Path,
    output_path: Path,
    focus: str = "Architecture review for Phase 1 Brain foundation.",
    review_files: tuple[str, ...] = DEFAULT_REVIEW_FILES,
) -> BundleResult:
    repo_root = repo_root.resolve()
    output_path = output_path.resolve()
    included_files: list[str] = []
    missing_files: list[str] = []

    sections = [
        "# NELA OS Claude Review Bundle",
        "",
        "This bundle is prepared for Claude review.",
        "It does not create any direct connection to Claude.",
        "",
        "## Review Focus",
        "",
        focus,
        "",
        "## Claude Instructions",
        "",
        CLAUDE_REVIEW_PROMPT.strip(),
        "",
        "## Repository Metadata",
        "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"- Branch: {_git(repo_root, 'branch', '--show-current') or 'unknown'}",
        f"- Commit: {_git(repo_root, 'rev-parse', '--short', 'HEAD') or 'unknown'}",
        f"- Working tree: {_working_tree_state(repo_root)}",
        "",
        "## Requested Review Output",
        "",
        "Please return:",
        "",
        "- Critical architecture risks.",
        "- Missing abstractions or over-coupling.",
        "- Event model gaps.",
        "- Memory model gaps.",
        "- Agent lifecycle risks.",
        "- Plugin readiness gaps.",
        "- Security and permission concerns.",
        "- Documentation improvements.",
        "- Recommended next tasks in priority order.",
        "",
        "## Included Files",
        "",
    ]

    for relative_path in review_files:
        path = repo_root / relative_path
        if not path.exists():
            missing_files.append(relative_path)
            continue
        included_files.append(relative_path)
        sections.extend(
            [
                f"### `{relative_path}`",
                "",
                f"```{_fence_language(relative_path)}",
                path.read_text(encoding="utf-8").rstrip(),
                "```",
                "",
            ]
        )

    if missing_files:
        sections.extend(
            [
                "## Missing Files",
                "",
                *[f"- `{missing}`" for missing in missing_files],
                "",
            ]
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    return BundleResult(
        output_path=output_path,
        included_files=tuple(included_files),
        missing_files=tuple(missing_files),
    )


def _git(repo_root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ("git", *args),
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _working_tree_state(repo_root: Path) -> str:
    status = _git(repo_root, "status", "--short")
    return "dirty" if status else "clean"


def _fence_language(relative_path: str) -> str:
    suffix = Path(relative_path).suffix
    if suffix == ".py":
        return "python"
    if suffix == ".md":
        return "markdown"
    return "text"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a Claude review bundle.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--output",
        default="docs/claude_review_bundle.md",
        help="Output Markdown path.",
    )
    parser.add_argument(
        "--focus",
        default="Architecture review for Phase 1 Brain foundation.",
        help="Review focus to include in the bundle.",
    )
    args = parser.parse_args()

    result = export_bundle(
        repo_root=Path(args.repo_root),
        output_path=Path(args.output),
        focus=args.focus,
    )
    print(f"Bundle written: {result.output_path}")
    print(f"Included files: {len(result.included_files)}")
    if result.missing_files:
        print(f"Missing files: {', '.join(result.missing_files)}")


if __name__ == "__main__":
    main()

