import unittest

from brain.llm import (
    DisabledLLMProvider,
    LLMRequest,
    build_llm_provider,
    _extract_response_text,
)


class LLMAdapterTests(unittest.TestCase):
    def test_disabled_provider_is_safe_noop(self) -> None:
        provider = DisabledLLMProvider()

        result = provider.answer(
            LLMRequest(
                user_text="מה את יודעת?",
                intent_action="GeneralQuestion",
                supported_actions="פעולות בטוחות בלבד",
            )
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.provider, "disabled")

    def test_build_provider_disabled_without_api_call(self) -> None:
        provider = build_llm_provider(
            provider_name="openai",
            enabled=False,
            model="test-model",
            timeout_seconds=1,
        )

        self.assertFalse(provider.enabled)

    def test_extracts_output_text_shortcut(self) -> None:
        self.assertEqual(_extract_response_text({"output_text": "שלום"}), "שלום")

    def test_extracts_nested_response_text(self) -> None:
        payload = {
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": "שלום"},
                        {"type": "output_text", "text": "אני איתך"},
                    ]
                }
            ]
        }

        self.assertEqual(_extract_response_text(payload), "שלום\nאני איתך")


if __name__ == "__main__":
    unittest.main()
