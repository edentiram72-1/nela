"""Claude collaboration agent.

This agent does not connect directly to Claude. It prepares structured review
tasks and exportable bundles that Claude can use after reading a GitHub pull
request or a pasted Markdown bundle.
"""

from __future__ import annotations

from pathlib import Path

from agents.base import AgentCommand, AgentResult, BaseAgent
from scripts.export_claude_review_bundle import CLAUDE_REVIEW_PROMPT, DEFAULT_REVIEW_FILES, export_bundle


class ClaudeAgent(BaseAgent):
    name = "claude"

    def execute(self, command: AgentCommand) -> AgentResult:
        if command.action == "create_review_request":
            return self._create_review_request(command)
        if command.action == "export_review_bundle":
            return self._export_review_bundle(command)
        return AgentResult(
            False,
            "Unsupported Claude collaboration action.",
            {
                "command": command.action,
                "supported_actions": (
                    "create_review_request",
                    "export_review_bundle",
                ),
            },
        )

    def _create_review_request(self, command: AgentCommand) -> AgentResult:
        focus = command.payload.get("focus", "Architecture review for Phase 1 Brain foundation.")
        return AgentResult(
            True,
            "Claude review request prepared.",
            {
                "review_focus": focus,
                "prompt": f"{CLAUDE_REVIEW_PROMPT.strip()}\n\nReview focus:\n{focus}",
                "required_files": DEFAULT_REVIEW_FILES,
                "delivery_options": (
                    "Paste docs/claude_review_bundle.md into Claude.",
                    "Attach docs/claude_review_bundle.md to a GitHub pull request.",
                    "Push the repository to GitHub and ask Claude to review the public PR.",
                ),
            },
        )

    def _export_review_bundle(self, command: AgentCommand) -> AgentResult:
        repo_root = Path(command.payload.get("repo_root", "."))
        output_path = Path(command.payload.get("output_path", "docs/claude_review_bundle.md"))
        focus = command.payload.get("focus", "Architecture review for Phase 1 Brain foundation.")
        result = export_bundle(repo_root=repo_root, output_path=output_path, focus=focus)
        return AgentResult(
            True,
            "Claude review bundle exported.",
            {
                "output_path": str(result.output_path),
                "included_files": result.included_files,
                "missing_files": result.missing_files,
            },
        )

