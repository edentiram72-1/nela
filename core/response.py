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
            for key in ("query", "url", "search_url", "results_count"):
                if key in first_result.data:
                    variables[key] = first_result.data[key]
            findings = _summarize_findings(turn.dispatched_results)
            variables.update(findings)
            variables.update(_summarize_learning_update(turn.dispatched_results))
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
        if turn.intent.action == "TryHackMeLessonCapture":
            return "learning.tryhackme.saved", variables
        if turn.intent.action in {"TryHackMeLearningPlan", "TryHackMeProgressReview"}:
            return "learning.tryhackme.review", variables
        if turn.intent.action == "SecurityReview":
            return _security_category("security.review.done", variables), variables
        if turn.intent.action == "WorkspaceSecurityScan":
            return _security_category("security.review.done", variables), variables
        if turn.intent.action == "DependencyScan":
            return _security_category("security.review.done", variables), variables
        if turn.intent.action in {
            "SecretsHygieneReview",
            "IdentityAccessReview",
            "NetworkDefenseReview",
            "NetworkTargetClassification",
            "VPNStatusCheck",
            "LocalNetworkReport",
            "SafeAccessTroubleshoot",
            "SupplyChainReview",
        }:
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
        if turn.intent.action == "OpenWeb":
            return "browser.open.done", variables
        if turn.intent.action == "WebSearch":
            if int(variables.get("findings_count", 0) or 0) == 0:
                variables["findings_count_label"] = "אין תוצאות"
                variables["findings"] = "לא מצאתי תוצאות רלוונטיות במסנן הזה."
            return "browser.search.done", variables
        if turn.plan:
            return "success.short", variables
        return "smalltalk.daily", variables


def _security_category(default_category: str, variables: dict[str, object]) -> str:
    if int(variables.get("findings_count", 0) or 0) > 0:
        return "security.findings.done"
    return default_category


def _summarize_findings(results: tuple[AgentResult, ...]) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    steps: list[str] = []
    next_steps: list[str] = []
    for result in results:
        product = result.data.get("work_product")
        if not isinstance(product, dict):
            continue
        raw_steps = product.get("steps", ())
        if isinstance(raw_steps, list):
            steps.extend(str(item) for item in raw_steps)
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
        location = str(finding.get("location") or "").strip()
        if str(finding.get("category") or "") == "web_result" and location:
            title = f"{title} — {location}"
        recommendation = str(finding.get("recommendation") or "").strip()
        if recommendation:
            finding_lines.append(f"{index}. {severity}: {title}. המלצה: {recommendation}")
        else:
            finding_lines.append(f"{index}. {severity}: {title}.")

    return {
        "findings_count": len(findings),
        "findings_count_label": _count_label(len(findings)),
        "steps": "\n".join(f"{index}. {step}" for index, step in enumerate(steps[:5], start=1))
        if steps
        else "בדקתי את הבקשה, בחרתי סוכן מתאים, והרצתי פעולה בטוחה דרך ה-Brain.",
        "findings": "\n".join(finding_lines) if finding_lines else "לא נמצאו ממצאים חריגים בבדיקה הזאת.",
        "next_steps": " ".join(next_steps[:2]) if next_steps else "להמשיך בבדיקה הגנתית ממוקדת לפי scope מאושר.",
    }


def _summarize_learning_update(results: tuple[AgentResult, ...]) -> dict[str, object]:
    """Extract user-visible learning details from specialist work products."""

    artifacts: list[dict[str, object]] = []
    next_steps: list[str] = []
    for result in results:
        product = result.data.get("work_product")
        if not isinstance(product, dict):
            continue
        raw_artifacts = product.get("artifacts", ())
        if isinstance(raw_artifacts, list):
            artifacts.extend(item for item in raw_artifacts if isinstance(item, dict))
        raw_next_steps = product.get("next_steps", ())
        if isinstance(raw_next_steps, list):
            next_steps.extend(str(item) for item in raw_next_steps)

    learned_response = _learning_artifact(artifacts, "learned_response")
    if learned_response is not None:
        details = _artifact_lines(learned_response)
        trigger = _line_value(details, "trigger") or "הביטוי החדש"
        response = _line_value(details, "response") or "התשובה החדשה"
        tags = _line_value(details, "tags") or "conversation"
        return {
            "learning_update": f"למדתי תגובה חדשה: כשנשמע \"{trigger}\" אענה \"{response}\".",
            "learning_detail": f"טריגר: {trigger}. תשובה: {response}. תגיות: {tags}.",
            "memory_target": "זיכרון השפה המקומי",
            "next_steps": _join_next_steps(next_steps, "אפשר לבדוק מיד: כתוב את הטריגר ותראה שאני עונה ממנו."),
        }

    lesson = _learning_artifact(artifacts, "lesson")
    if lesson is not None:
        details = _artifact_lines(lesson)
        first_line = details[0] if details else "שיעור חדש"
        return {
            "learning_update": f"למדתי ועדכנתי את הזיכרון שלי עם {first_line}.",
            "learning_detail": "\n".join(details[:4]) if details else first_line,
            "memory_target": "זיכרון הלמידה המקומי",
            "next_steps": _join_next_steps(next_steps, "להמשיך עם שאלת חזרה קצרה או להוסיף עוד דוגמה."),
        }

    if artifacts:
        names = ", ".join(str(item.get("name") or item.get("kind") or "artifact") for item in artifacts[:3])
        return {
            "learning_update": f"עדכנתי תוצר למידה: {names}.",
            "learning_detail": names,
            "memory_target": "זיכרון העבודה של נלה",
            "next_steps": _join_next_steps(next_steps, "להמשיך לעדכון הבא או לבקש ממני לסכם מה למדתי."),
        }

    return {
        "learning_update": "למדתי ועדכנתי את הזיכרון שלי.",
        "learning_detail": "העדכון נשמר דרך סוכן הלמידה.",
        "memory_target": "זיכרון הלמידה המקומי",
        "next_steps": _join_next_steps(next_steps, "אפשר לבקש ממני לספר מה למדתי."),
    }


def _learning_artifact(artifacts: list[dict[str, object]], kind: str) -> dict[str, object] | None:
    for artifact in artifacts:
        if str(artifact.get("kind") or "") == kind:
            return artifact
    return None


def _artifact_lines(artifact: dict[str, object]) -> list[str]:
    content = str(artifact.get("content") or "").strip()
    return [line.strip() for line in content.splitlines() if line.strip()]


def _line_value(lines: list[str], key: str) -> str | None:
    prefix = f"{key}="
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _join_next_steps(next_steps: list[str], fallback: str) -> str:
    return " ".join(next_steps[:2]) if next_steps else fallback


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
