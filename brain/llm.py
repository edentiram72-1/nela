"""LLM adapter for open-ended NELA conversation.

The adapter is intentionally text-only and actionless. It can help NELA answer
open questions, but it cannot dispatch Agents or bypass the Planner,
Permission Engine, or Dispatcher.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


NELA_LLM_INSTRUCTIONS = """את נלה, עוזרת AI מקומית בעברית.
דברי בעברית טבעית, חמה, קצרה ומדויקת. את תמיד בנקבה.
אל תגידי שביצעת פעולה אם לא קיבלת תוצאת פעולה מה-Brain.
אם המשתמש מבקש פעולה, הסבירי מה אפשר לעשות או מה צריך לאשר, אבל אל תבחרי סוכן ואל תעקפי הרשאות.
בסייבר: הגנתי, מקומי, מורשה בלבד. בלי ניצול חולשות, עקיפה, פישינג, נוזקות, גניבת סודות או סריקה של צד שלישי.
אם אינך יודעת, אמרי זאת בפשטות ותציעי צעד בטוח הבא.
"""


@dataclass(frozen=True)
class LLMRequest:
    """Input for a safe, actionless LLM answer."""

    user_text: str
    intent_action: str
    supported_actions: str
    recent_context: tuple[str, ...] = ()


@dataclass(frozen=True)
class LLMResult:
    """Result from an LLM provider."""

    ok: bool
    text: str
    provider: str
    model: str | None = None
    error: str | None = None


class LLMProvider(Protocol):
    """Minimal provider protocol for open-ended answer generation."""

    @property
    def enabled(self) -> bool:
        """Whether this provider can be used."""

    def answer(self, request: LLMRequest) -> LLMResult:
        """Return a safe answer for an open-ended conversation request."""


class DisabledLLMProvider:
    """Provider used when no real model is configured."""

    enabled = False

    def answer(self, request: LLMRequest) -> LLMResult:
        return LLMResult(False, "", "disabled", error="LLM is disabled.")


class OpenAIResponsesProvider:
    """OpenAI Responses API provider using only the Python standard library."""

    endpoint = "https://api.openai.com/v1/responses"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 20.0,
        max_output_tokens: int = 500,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.model)

    def answer(self, request: LLMRequest) -> LLMResult:
        if not self.enabled:
            return LLMResult(False, "", "openai", self.model, "Missing API key or model.")

        payload = {
            "model": self.model,
            "instructions": NELA_LLM_INSTRUCTIONS,
            "input": self._input_text(request),
            "max_output_tokens": self.max_output_tokens,
            "store": False,
        }
        body = json.dumps(payload).encode("utf-8")
        http_request = urllib.request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            return LLMResult(False, "", "openai", self.model, _http_error_message(exc))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return LLMResult(False, "", "openai", self.model, str(exc))

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return LLMResult(False, "", "openai", self.model, f"Invalid JSON response: {exc}")

        text = _extract_response_text(data)
        if not text:
            return LLMResult(False, "", "openai", self.model, "No text output in response.")
        return LLMResult(True, text.strip(), "openai", self.model)

    def _input_text(self, request: LLMRequest) -> str:
        context = "\n".join(f"- {item}" for item in request.recent_context[-5:])
        return (
            f"שאלת המשתמש: {request.user_text}\n"
            f"Intent שזוהה: {request.intent_action}\n"
            f"פעולות שמותר לנלה להציע דרך ה-Brain: {request.supported_actions}\n"
            f"הקשר שיחה אחרון:\n{context or '- אין'}\n\n"
            "עני כטקסט שיחה בלבד. אל תחזירי JSON ואל תמציאי תוצאת פעולה."
        )


def build_llm_provider(
    provider_name: str,
    enabled: bool,
    model: str,
    timeout_seconds: float,
) -> LLMProvider:
    """Build the configured LLM provider."""

    if not enabled:
        return DisabledLLMProvider()
    if provider_name != "openai":
        return DisabledLLMProvider()
    api_key = os.getenv("NELA_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    return OpenAIResponsesProvider(api_key=api_key, model=model, timeout_seconds=timeout_seconds)


def _extract_response_text(data: dict[str, object]) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str):
        return output_text

    parts: list[str] = []
    output = data.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for content_item in content:
                if not isinstance(content_item, dict):
                    continue
                text = content_item.get("text")
                if isinstance(text, str):
                    parts.append(text)
    return "\n".join(parts)


def _http_error_message(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8")
    except OSError:
        body = ""
    if not body:
        return f"HTTP {exc.code}"
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return f"HTTP {exc.code}: {body[:160]}"
    error = data.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str):
            return f"HTTP {exc.code}: {message}"
    return f"HTTP {exc.code}"
