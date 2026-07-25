"""Intent recognition for NELA OS."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from brain.applications import resolve_application_alias


class Priority(str, Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"


@dataclass(frozen=True)
class Intent:
    """Structured representation of a user request."""

    action: str
    raw_text: str
    confidence: float
    application: str | None = None
    resource: str | None = None
    priority: Priority = Priority.NORMAL
    parameters: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False

    @property
    def name(self) -> str:
        return self.action

    @property
    def target_agent(self) -> str | None:
        if self.application:
            return _slug(self.application)
        if self.parameters.get("domain"):
            return str(self.parameters["domain"])
        return None


@dataclass(frozen=True)
class IntentPattern:
    """Configurable pattern for turning text into an intent."""

    action: str
    keywords: tuple[str, ...]
    domain: str | None = None
    requires_confirmation: bool = False


DEFAULT_PATTERNS: tuple[IntentPattern, ...] = (
    IntentPattern("Greeting", ("שלום", "היי", "הי", "בוקר טוב", "ערב טוב", "hello", "hi")),
    IntentPattern("Thanks", ("תודה", "תודה רבה", "thanks", "thank you")),
    IntentPattern(
        "SecurityReview",
        ("סקירת אבטחה", "בדיקת אבטחה", "תבדקי אבטחה", "תבדקי את הקוד לאבטחה", "security review", "secure code review"),
        domain="secure_code_reviewer",
    ),
    IntentPattern("ThreatModel", ("מודל איומים", "threat model"), domain="secure_code_reviewer"),
    IntentPattern(
        "CyberLabStatus",
        ("מצב מעבדת סייבר", "סטטוס סייבר", "מצב הסייבר", "cyber lab status"),
        domain="authorized_lab",
    ),
    IntentPattern(
        "CyberLabRegisterTarget",
        ("תרשמי יעד מעבדה", "תוסיפי יעד מעבדה", "register lab target"),
        domain="authorized_lab",
    ),
    IntentPattern(
        "LocalFuzzPlan",
        ("תוכנית fuzz", "תכנון fuzz", "תכיני fuzz", "local fuzz plan", "fuzz plan"),
        domain="anomaly_discovery",
    ),
    IntentPattern(
        "SecurityCapabilitiesQuestion",
        (
            "מה את יודעת בסייבר",
            "מה את יודעת על סייבר",
            "מה את יודעת באבטחה",
            "מה את יודעת על אבטחה",
            "מה יכולות האבטחה שלך",
            "יכולות אבטחה",
            "יכולות סייבר",
            "cyber capabilities",
        ),
    ),
    IntentPattern(
        "CyberDefenseSweep",
        (
            "תעשי הגנה",
            "תתחילי להגן",
            "תגני",
            "הגני",
            "תבני מערך סייבר",
            "תבני מערך הגנה",
            "מערך סייבר",
            "מערך הגנה",
            "בדיקה של אבטחה",
            "בדיקת הגנה",
            "בדיקה הגנתית",
            "בדיקה אבטחתית",
            "בדיקת סייבר",
            "בדיקת ממצאי אבטחה",
            "תעשי בדיקת סייבר",
            "תעשי בדיקה של סייבר",
            "defense sweep",
            "defense check",
            "security posture",
            "protect",
        ),
        domain="cyber_defense",
    ),
    IntentPattern(
        "CapabilitiesQuestion",
        (
            "מה את יודעת לעשות",
            "מה את יכולה לעשות",
            "איך את יכולה לעזור",
            "איזה יכולות יש לך",
            "מה היכולות שלך",
            "help",
            "capabilities",
        ),
    ),
    IntentPattern(
        "AgentStatusQuestion",
        (
            "איזה סוכנים מחוברים",
            "מי מחובר",
            "מה מצב הסוכנים",
            "סטטוס סוכנים",
            "agent status",
            "status",
        ),
    ),
    IntentPattern(
        "HumanStatusQuestion",
        ("מה מצב", "מה המצב", "מה קורה", "איך הולך", "איך את", "מה איתך", "how are you"),
    ),
    IntentPattern("IdentityQuestion", ("מי את", "מה את", "מי את נלה", "ספרי על עצמך", "who are you")),
    IntentPattern("LearnTopic", ("תלמדי", "למדי", "תלמדני", "learn about", "study"), domain="learning"),
    IntentPattern("Remember", ("remember", "save this", "learn this", "תזכרי", "תזכור", "תשמרי")),
    IntentPattern("CloseApplication", ("close", "quit", "תסגרי", "סגרי", "לסגור"), requires_confirmation=True),
    IntentPattern("SwitchApplication", ("switch to", "focus", "bring to front", "תעברי", "לעבור אל")),
    IntentPattern("StopTask", ("stop", "cancel", "עצור", "תעצרי", "בטלי"), requires_confirmation=True),
    IntentPattern("PlayMedia", ("play", "music", "playlist", "song", "תנגני", "מוזיקה", "פלייליסט", "שיר")),
    IntentPattern("OpenApplication", ("open", "launch", "start", "תפתחי", "פתחי", "לפתוח")),
    IntentPattern("Search", ("search", "find", "look up", "חפשי", "תחפשי", "מצא")),
    IntentPattern("CreateItem", ("create", "make", "draft", "write", "צרי", "תכתבי", "כתבי")),
)


class IntentRouter:
    """Converts text into structured, agent-neutral intents."""

    def __init__(self, patterns: tuple[IntentPattern, ...] = DEFAULT_PATTERNS) -> None:
        self._patterns = patterns

    def classify(self, text: str, context: dict[str, Any] | None = None) -> Intent:
        normalized = _normalize(text)
        priority = _detect_priority(normalized)
        taught_response = _extract_teach_response(text)
        if taught_response is not None:
            return Intent(
                action="TeachResponse",
                raw_text=text,
                confidence=0.88,
                priority=priority,
                parameters={**taught_response, "domain": "learning"},
            )

        pattern = self._match_pattern(normalized)
        application = _extract_application(text)
        resource = _extract_resource(text)
        parameters: dict[str, Any] = {}
        if pattern and pattern.domain:
            parameters["domain"] = pattern.domain
        if pattern and pattern.action == "LearnTopic":
            parameters["topic"] = _extract_learning_topic(text)
        if _looks_like_follow_up(normalized) and context:
            parameters["follow_up_to"] = context.get("last_intent")

        if pattern:
            return Intent(
                action=pattern.action,
                raw_text=text,
                confidence=0.82,
                application=resolve_application_alias(application),
                resource=resource or _extract_url(text),
                priority=priority,
                parameters=parameters,
                requires_confirmation=pattern.requires_confirmation,
            )

        if _looks_like_question(normalized):
            return Intent(
                action="GeneralQuestion",
                raw_text=text,
                confidence=0.62,
                application=resolve_application_alias(application),
                resource=resource or _extract_url(text),
                priority=priority,
                parameters=parameters,
            )

        return Intent(
            action="GeneralRequest",
            raw_text=text,
            confidence=0.45,
            application=resolve_application_alias(application),
            resource=resource or _extract_url(text),
            priority=priority,
            parameters=parameters,
        )

    def _match_pattern(self, normalized: str) -> IntentPattern | None:
        for pattern in self._patterns:
            if pattern.action == "HumanStatusQuestion":
                if any(_is_exact_short_phrase(normalized, keyword) for keyword in pattern.keywords):
                    return pattern
                continue
            if any(_contains_keyword(normalized, keyword) for keyword in pattern.keywords):
                return pattern
        return None


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _detect_priority(normalized: str) -> Priority:
    if any(word in normalized for word in ("urgent", "immediately", "asap", "now")):
        return Priority.HIGH
    if any(word in normalized for word in ("later", "when you can")):
        return Priority.LOW
    return Priority.NORMAL


def _extract_application(text: str) -> str | None:
    hebrew_match = re.search(
        r"(?:תפתחי|פתחי|לפתוח|תסגרי|סגרי|לסגור|תעברי|לעבור)\s+(?:את|אל|ל)?\s*([A-Za-zא-ת][\wא-ת-]*(?:\s+[A-Za-zא-ת][\wא-ת-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if hebrew_match:
        candidate = _title_name(_trim_application_name(hebrew_match.group(1).strip()))
        return None if _is_generic_application_word(candidate) else candidate
    match = re.search(
        r"\b(?:open|launch|start|close|quit|focus)\s+([A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        candidate = _title_name(_trim_application_name(match.group(1).strip()))
        return None if _is_generic_application_word(candidate) else candidate
    match = re.search(
        r"\b(?:switch|bring)\s+(?:to\s+)?([A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        candidate = _title_name(_trim_application_name(match.group(1).strip()))
        return None if _is_generic_application_word(candidate) else candidate
    match = re.search(
        r"\bin\s+([A-Z][\w-]*(?:\s+[A-Z][\w-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        candidate = _title_name(_trim_application_name(match.group(1).strip()))
        return None if _is_generic_application_word(candidate) else candidate
    return None


def _extract_resource(text: str) -> str | None:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted:
        return quoted.group(1).strip()
    playlist = re.search(r"\bmy\s+([\w\s-]+?)\s+playlist\b", text, flags=re.IGNORECASE)
    if playlist:
        return playlist.group(1).strip()
    return None


def _extract_url(text: str) -> str | None:
    match = re.search(r"\b(?:https?://|localhost:)\S+", text, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(0).rstrip(".,;!?")


def _extract_teach_response(text: str) -> dict[str, str] | None:
    patterns = (
        r"(?:תלמדי|למדי|תלמדני).*?כשאני אומר(?:ת)?\s+(.+?)\s+(?:תעני|תגידי|תאמרי)\s+(.+)",
        r"כשאני אומר(?:ת)?\s+(.+?)\s+(?:תעני|תגידי|תאמרי)\s+(.+)",
        r"(?:learn|teach).*?when i say\s+(.+?)\s+(?:answer|reply|say)\s+(.+)",
        r"(?:learn response|teach response|למדי תשובה|תלמדי תשובה)\s*:\s*(.+?)\s*=>\s*(.+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        trigger = _strip_teach_delimiters(match.group(1))
        response = _strip_teach_delimiters(match.group(2))
        if trigger and response:
            return {"trigger": trigger, "response": response}
    return None


def _strip_teach_delimiters(value: str) -> str:
    return value.strip(" \t\n\r\"'׳״.,;:!?")


def _extract_learning_topic(text: str) -> str:
    patterns = (
        r"(?:נלה[,\s]+)?(?:תלמדי|למדי|תלמדני)\s+(.+)",
        r"(?:learn about|study)\s+(.+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            topic = _strip_teach_delimiters(match.group(1))
            if topic:
                return topic
    return "הנושא שביקשת"


def _looks_like_follow_up(normalized: str) -> bool:
    return normalized.startswith(("also ", "then ", "and ", "do that", "same "))


def _looks_like_question(normalized: str) -> bool:
    question_words = (
        "what",
        "who",
        "how",
        "why",
        "when",
        "where",
        "which",
        "can you",
        "do you",
        "מה",
        "מי",
        "איך",
        "למה",
        "מתי",
        "איפה",
        "איזה",
        "האם",
        "אפשר",
    )
    return normalized.endswith("?") or normalized.startswith(question_words)


def _contains_keyword(normalized: str, keyword: str) -> bool:
    escaped = re.escape(_normalize(keyword))
    return re.search(rf"(?<!\w){escaped}(?!\w)", normalized) is not None


def _is_exact_short_phrase(normalized: str, keyword: str) -> bool:
    value = normalized.strip(" ?!.,;:׳״\"'")
    expected = _normalize(keyword).strip(" ?!.,;:׳״\"'")
    return value == expected


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _title_name(value: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in value.split())


def _trim_application_name(value: str) -> str:
    stopwords = {"and", "then", "to", "with", "for", "play", "search", "open", "front"}
    parts = []
    for part in value.split():
        if part.lower() in stopwords:
            break
        parts.append(part)
    return " ".join(parts) if parts else value


def _is_generic_application_word(value: str) -> bool:
    return _normalize(value) in {"app", "application", "אפליקציה", "יישום"}
