"""Response rendering and voice delegation for Brain turns."""

from __future__ import annotations

from agents.base import AgentResult
from brain.conversation import ConversationTurn
from brain.decision import DecisionType
from brain.dispatcher import AgentDispatcher
from brain.planner import Task
from core.config import AppConfig
from language.engine import LanguageEngine


class NelaResponseAdapter:
    """Converts semantic Brain turns into user-facing Hebrew and optional speech."""

    def __init__(self, language: LanguageEngine, dispatcher: AgentDispatcher, config: AppConfig) -> None:
        self.language = language
        self.dispatcher = dispatcher
        self.config = config

    def render_turn(self, turn: ConversationTurn) -> str:
        category, variables = self._category_and_variables(turn)
        return self.language.render_response(category=category, variables=variables)

    def render_and_maybe_speak(self, turn: ConversationTurn) -> str:
        text = self.render_turn(turn)
        if self.config.voice_auto_speak_responses:
            self.speak_text(text)
        return text

    def speak_text(self, text: str) -> AgentResult | None:
        if "voice" not in self.dispatcher.discover_agents():
            return None
        task = Task(
            description="Speak final assistant response",
            action="speak",
            target_agent="voice",
            payload={
                "text": text,
                "interrupt": True,
                "silent": self.config.voice_silent_mode,
            },
            timeout_seconds=10.0,
        )
        return self.dispatcher.dispatch(task, plan_id="response-output")

    def _category_and_variables(self, turn: ConversationTurn) -> tuple[str, dict[str, object]]:
        application = turn.intent.application or "האפליקציה"
        resource = turn.intent.resource or "הבקשה"

        variables: dict[str, object] = {
            "application": application,
            "resource": resource,
            "message": turn.message,
            "intent": turn.intent.action,
            "task_hint": turn.message,
        }
        if turn.dispatched_results:
            first_result = turn.dispatched_results[0]
            variables["summary"] = first_result.message
            variables["task_hint"] = first_result.message
            findings = _summarize_findings(turn.dispatched_results)
            variables.update(findings)
        response_variables = turn.intent.parameters.get("response_variables")
        if isinstance(response_variables, dict):
            variables.update(response_variables)

        response_category = turn.intent.parameters.get("response_category")
        if isinstance(response_category, str) and response_category:
            return response_category, variables

        if turn.decision.type in {DecisionType.ASK_CLARIFICATION, DecisionType.WAIT}:
            variables["question"] = turn.message
            variables["clarify"] = turn.message
            return "clarify.one_question", variables
        if turn.decision.type == DecisionType.REJECT:
            return "success.short", variables
        if turn.dispatched_results and any(not result.success for result in turn.dispatched_results):
            failed = next(result for result in turn.dispatched_results if not result.success)
            variables["error"] = failed.message
            variables["what"] = failed.message
            return "error.recovering", variables
        if turn.intent.action == "OpenApplication":
            return "desktop.launch", variables
        if turn.intent.action == "CloseApplication":
            return "desktop.closed", variables
        if turn.intent.action == "PlayMedia":
            return "media.play", variables
        if turn.intent.action == "Remember":
            return "learning.saved", variables
        if turn.intent.action == "TeachResponse":
            return "learning.saved", variables
        if turn.intent.action == "LearnTopic":
            variables["topic"] = str(turn.intent.parameters.get("topic", "הנושא הזה"))
            return "learning.topic.started", variables
        if turn.intent.action == "SecurityReview":
            return _security_category("security.review.done", variables), variables
        if turn.intent.action == "WorkspaceSecurityScan":
            return _security_category("security.review.done", variables), variables
        if turn.intent.action == "DependencyScan":
            return _security_category("security.review.done", variables), variables
        if turn.intent.action == "CyberDefenseSweep":
            if int(variables.get("findings_count", 0) or 0) > 0:
                return "security.defense.findings", variables
            return "security.review.done", variables
        if turn.intent.action == "ThreatModel":
            return _security_category("security.threat_model.done", variables), variables
        if turn.intent.action == "CyberLabRegisterTarget":
            return "security.lab.done", variables
        if turn.intent.action == "CyberLabStatus":
            return "security.lab.status", variables
        if turn.intent.action == "LocalFuzzPlan":
            return _security_category("security.fuzz_plan.done", variables), variables
        if turn.plan:
            return "success.short", variables
        return "smalltalk.daily", variables


def _security_category(default_category: str, variables: dict[str, object]) -> str:
    if int(variables.get("findings_count", 0) or 0) > 0:
        return "security.findings.done"
    return default_category


def _summarize_findings(results: tuple[AgentResult, ...]) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    next_steps: list[str] = []
    for result in results:
        product = result.data.get("work_product")
        if not isinstance(product, dict):
            continue
        raw_findings = product.get("findings", ())
        if isinstance(raw_findings, list):
            findings.extend(item for item in raw_findings if isinstance(item, dict))
        raw_next_steps = product.get("next_steps", ())
        if isinstance(raw_next_steps, list):
            next_steps.extend(str(item) for item in raw_next_steps)

    finding_lines = []
    for index, finding in enumerate(findings[:4], start=1):
        severity = _severity_label(str(finding.get("severity", "info")))
        title = _finding_title(str(finding.get("title", "ממצא הגנתי")))
        recommendation = str(finding.get("recommendation") or "").strip()
        if recommendation:
            finding_lines.append(f"{index}. {severity}: {title}. המלצה: {recommendation}")
        else:
            finding_lines.append(f"{index}. {severity}: {title}.")

    return {
        "findings_count": len(findings),
        "findings_count_label": _count_label(len(findings)),
        "findings": "\n".join(finding_lines) if finding_lines else "לא נמצאו ממצאים חריגים בבדיקה הזאת.",
        "next_steps": " ".join(next_steps[:2]) if next_steps else "להמשיך בבדיקה הגנתית ממוקדת לפי scope מאושר.",
    }


def _severity_label(severity: str) -> str:
    labels = {
        "critical": "קריטי",
        "high": "גבוה",
        "medium": "בינוני",
        "low": "נמוך",
        "info": "מידע",
    }
    return labels.get(severity.lower(), "מידע")


def _count_label(count: int) -> str:
    if count == 0:
        return "אין ממצאים"
    if count == 1:
        return "ממצא אחד"
    if count == 2:
        return "שני ממצאים"
    return f"{count} ממצאים"


def _finding_title(title: str) -> str:
    known = {
        "Dynamic eval usage": "שימוש ב-eval דינמי",
        "Dynamic exec usage": "שימוש ב-exec דינמי",
        "Shell execution enabled": "הרצת shell פעילה",
        "Unsafe pickle deserialization": "טעינת pickle לא בטוחה",
        "YAML load without SafeLoader": "טעינת YAML בלי SafeLoader",
        "TLS certificate verification disabled": "אימות תעודת TLS כבוי",
        "Weak hash algorithm": "אלגוריתם hash חלש",
        "Possible hardcoded secret": "ייתכן שיש סוד קשיח בקוד",
        "Debug mode enabled": "מצב debug פעיל",
        "Broad network bind": "חשיפת רשת רחבה",
        "Permissive CORS/origin policy": "מדיניות CORS פתוחה מדי",
        "Overly permissive file mode": "הרשאות קובץ רחבות מדי",
        "Floating container tag": "תג container לא מקובע",
        "Dependency file could not be parsed": "קובץ תלותים לא ניתן לפענוח",
    }
    if title.startswith("Dependency is not pinned:"):
        return title.replace("Dependency is not pinned:", "תלות לא מקובעת:")
    if title.startswith("Known advisory for"):
        return title.replace("Known advisory for", "התראת אבטחה ידועה עבור")
    return known.get(title, title)
