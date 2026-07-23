import tempfile
import unittest
from pathlib import Path

from agents.base import AgentCommand
from agents.claude.agent import ClaudeAgent


class ClaudeAgentTests(unittest.TestCase):
    def test_create_review_request_returns_prompt_and_files(self) -> None:
        agent = ClaudeAgent()

        result = agent.execute(
            AgentCommand(
                action="create_review_request",
                payload={"focus": "Review the Brain event model."},
            )
        )

        self.assertTrue(result.success)
        self.assertIn("Review the Brain event model.", result.data["prompt"])
        self.assertIn("docs/architecture.md", result.data["required_files"])
        self.assertIn("Paste docs/claude_review_bundle.md into Claude.", result.data["delivery_options"])

    def test_export_review_bundle_writes_markdown_file(self) -> None:
        agent = ClaudeAgent()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "docs").mkdir()
            (root / "brain").mkdir()
            (root / "core").mkdir()
            (root / "agents").mkdir()
            (root / "tests").mkdir()
            for relative_path in (
                "README.md",
                "docs/architecture.md",
                "docs/ai_handoff.md",
                "docs/coding_rules.md",
                "docs/api.md",
                "docs/decisions.md",
                "docs/memory_model.md",
                "docs/roadmap.md",
            ):
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"# {relative_path}\n", encoding="utf-8")

            output = root / "docs" / "claude_review_bundle.md"
            result = agent.execute(
                AgentCommand(
                    action="export_review_bundle",
                    payload={
                        "repo_root": str(root),
                        "output_path": str(output),
                        "focus": "Review generated bundle.",
                    },
                )
            )

        self.assertTrue(result.success)
        self.assertEqual(result.data["output_path"], str(output.resolve()))
        self.assertIn("README.md", result.data["included_files"])
        self.assertIn("brain/README.md", result.data["missing_files"])


if __name__ == "__main__":
    unittest.main()

