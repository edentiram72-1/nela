"""TryHackMe learning specialist.

This agent does not connect to TryHackMe directly. It learns from user-supplied
room notes, commands, summaries, and lab reflections, then stores structured
lessons for future NELA answers.
"""

from __future__ import annotations

from pathlib import Path
import re

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding
from memory.learning_core import LearningMemoryStore


class TryHackMeLearningAgent(SpecialistAgent):
    name = "tryhackme_learning"
    domain = AgentDomain.LEARNING
    purpose = "Learn from authorized TryHackMe study sessions and turn them into durable NELA knowledge."
    capabilities = (
        "tryhackme.lesson.capture",
        "tryhackme.learning.path",
        "tryhackme.progress.review",
    )

    def __init__(self, store: LearningMemoryStore | None = None, store_path: Path | str | None = None) -> None:
        super().__init__()
        self.store = store or LearningMemoryStore(store_path)

    def _handlers(self):
        return {
            **super()._handlers(),
            "capture_tryhackme_lesson": self._capture_tryhackme_lesson,
            "plan_tryhackme_learning": self._plan_tryhackme_learning,
            "review_tryhackme_progress": self._review_tryhackme_progress,
        }

    def _capture_tryhackme_lesson(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        room = _room(command, text)
        topic = _topic(command, text)
        concepts = _concepts(text, topic)
        commands = _commands(text)
        safety_notes = _safety_notes(text, commands)
        summary = _summary(text, topic, concepts)
        lesson = self.store.add_lesson(
            source="tryhackme",
            topic=topic,
            summary=summary,
            concepts=concepts,
            commands=commands,
            safety_notes=safety_notes,
            room=room,
            tags=("cyber", "authorized_lab", "tryhackme", *_topic_tags(concepts)),
        )
        findings = (
            TaskFinding(
                title="שיעור TryHackMe נשמר לזיכרון הלימודי",
                severity=RiskLevel.INFO,
                category="learning_memory",
                location=room or "tryhackme",
                evidence=f"lesson_id={lesson.id}; topic={lesson.topic}",
                recommendation="לחזור על השיעור בהמשך דרך שאלות חזרה ולחבר אותו רק למעבדות חוקיות.",
            ),
            TaskFinding(
                title="גבול בטיחות לימודי נשמר",
                severity=RiskLevel.INFO,
                category="learning_safety",
                location="tryhackme",
                evidence="source=authorized_training",
                recommendation="להשתמש בידע מול TryHackMe, localhost, או יעד בבעלות/הרשאה בלבד.",
            ),
        )
        return AgentWorkProduct(
            summary=f"TryHackMe lesson captured: {topic}.",
            steps=(
                "קראתי את סיכום החדר שקיבלתי ממך ולא התחברתי לאתר חיצוני.",
                f"זיהיתי נושא מרכזי: {topic}.",
                f"חילצתי מושגים ללמידה: {', '.join(concepts[:6])}.",
                "שמרתי את השיעור בזיכרון הלימודי המקומי של נלה.",
                "הכנתי שאלות חזרה ומפת מיומנויות להמשך.",
            ),
            findings=findings,
            artifacts=(
                artifact("lesson", lesson.id, _lesson_lines(lesson.topic, summary, concepts, commands, safety_notes)),
                artifact("review_questions", "tryhackme_review_questions", _review_questions(topic, concepts)),
                artifact("skill_graph", "tryhackme_skill_graph", _skill_graph_lines(self.store)),
            ),
            next_steps=(
                "לבקש מנלה לשאול שאלות חזרה על החדר.",
                "להוסיף פלטים, טעויות ותובנות אחרי כל משימה ב-TryHackMe.",
            ),
        )

    def _plan_tryhackme_learning(self, command: AgentCommand) -> AgentWorkProduct:
        topic = _topic(command, _text(command))
        concepts = _concepts(topic, topic)
        lines = (
            f"Topic: {topic}",
            "1. Read the room objective and define the legal lab scope.",
            "2. Capture terms, tools, and commands before running anything.",
            "3. Run only inside the TryHackMe room or an owned local lab.",
            "4. Save findings, mistakes, and safe remediation notes into NELA.",
            "5. Review with flashcards and one small defensive checklist.",
        )
        return AgentWorkProduct(
            summary=f"TryHackMe learning path prepared for {topic}.",
            steps=(
                f"זיהיתי בקשת מסלול לימוד עבור: {topic}.",
                "בניתי סדר עבודה בטוח: להבין scope, לתעד מושגים, לבצע רק במעבדה חוקית.",
                "חיברתי את המסלול לזיכרון הלימודי כדי שתוכל להוסיף חדרים בהמשך.",
            ),
            findings=(
                TaskFinding(
                    title="מסלול TryHackMe מוכן",
                    severity=RiskLevel.INFO,
                    category="learning_plan",
                    location="tryhackme",
                    recommendation="להתחיל מחדר בסיסי, לשמור שיעור אחרי כל משימה, ולבצע רק בתוך scope חוקי.",
                ),
            ),
            artifacts=(
                artifact("learning_plan", "tryhackme_learning_path", lines),
                artifact("concepts", "starter_concepts", concepts or ("lab scope", "notes", "review")),
            ),
            next_steps=("להדביק לנלה את שם החדר או סיכום המשימה הראשונה.",),
        )

    def _review_tryhackme_progress(self, command: AgentCommand) -> AgentWorkProduct:
        lessons = self.store.list_lessons(source="tryhackme")
        graph = self.store.skill_graph(source="tryhackme")
        if not lessons:
            findings = (
                TaskFinding(
                    title="עוד אין שיעורי TryHackMe שמורים",
                    severity=RiskLevel.INFO,
                    category="learning_progress",
                    location="tryhackme",
                    recommendation="להתחיל בהדבקת סיכום חדר או פקודות שלמדת במעבדה.",
                ),
            )
        else:
            findings = (
                TaskFinding(
                    title=f"נשמרו {len(lessons)} שיעורי TryHackMe",
                    severity=RiskLevel.INFO,
                    category="learning_progress",
                    location="tryhackme",
                    evidence=", ".join(lesson.topic for lesson in lessons[-5:]),
                    recommendation="לחזור על הנושאים עם ספירת מופעים נמוכה במפת המיומנויות.",
                ),
            )
        return AgentWorkProduct(
            summary=f"TryHackMe progress reviewed: {len(lessons)} lesson(s).",
            steps=(
                "פתחתי את זיכרון הלמידה המקומי של TryHackMe.",
                f"ספרתי {len(lessons)} שיעורים שמורים.",
                "בניתי תמונת מצב לפי נושאים ומושגים שחוזרים על עצמם.",
            ),
            findings=findings,
            artifacts=(
                artifact("lessons", "tryhackme_recent_lessons", _recent_lesson_lines(lessons)),
                artifact("skill_graph", "tryhackme_skill_graph", _graph_lines(graph)),
            ),
            next_steps=("לבקש: נלה, תשאלי אותי שאלות חזרה על TryHackMe.",),
        )


def _text(command: AgentCommand) -> str:
    return str(command.payload.get("text") or command.payload.get("notes") or command.payload.get("summary") or "")


def _room(command: AgentCommand, text: str) -> str | None:
    value = command.payload.get("room")
    if value:
        return str(value).strip()
    match = re.search(r"(?:room|חדר)\s*[:=]?\s*([\wא-ת ._-]{2,50})", text, flags=re.IGNORECASE)
    return match.group(1).strip(" ._-") if match else None


def _topic(command: AgentCommand, text: str) -> str:
    value = str(command.payload.get("topic") or "").strip()
    if value:
        return value
    lowered = text.lower()
    topic_map = (
        ("nmap", "network scanning basics"),
        ("port", "ports and services"),
        ("linux", "linux fundamentals"),
        ("http", "web fundamentals"),
        ("burp", "web security tooling"),
        ("sql", "sql injection concepts"),
        ("xss", "cross-site scripting concepts"),
        ("soc", "soc analyst foundations"),
        ("wireshark", "packet analysis"),
        ("tryhackme", "tryhackme study"),
    )
    for marker, topic in topic_map:
        if marker in lowered:
            return topic
    return "tryhackme study"


def _concepts(text: str, topic: str) -> tuple[str, ...]:
    lowered = f"{text} {topic}".lower()
    concepts: list[str] = []
    concept_map = {
        "nmap": "nmap",
        "port": "ports",
        "service": "services",
        "ssh": "ssh",
        "http": "http",
        "dns": "dns",
        "linux": "linux",
        "permission": "linux permissions",
        "gobuster": "content discovery",
        "ffuf": "content discovery",
        "burp": "burp suite",
        "sql": "sql injection concepts",
        "xss": "xss concepts",
        "log": "log analysis",
        "soc": "soc analyst",
        "wireshark": "packet analysis",
        "hash": "hashing",
        "privilege": "privilege escalation concepts",
    }
    for marker, concept in concept_map.items():
        if marker in lowered and concept not in concepts:
            concepts.append(concept)
    return tuple(concepts or ("authorized lab scope", "study notes"))


def _commands(text: str) -> tuple[str, ...]:
    known_tools = ("nmap", "gobuster", "ffuf", "curl", "ping", "traceroute", "dig", "nslookup", "ssh", "hydra")
    commands: list[str] = []
    for line in text.splitlines() or [text]:
        cleaned = " ".join(line.strip().split())
        lowered = cleaned.lower()
        if not cleaned:
            continue
        if any(lowered.startswith(tool) or f" {tool} " in f" {lowered} " for tool in known_tools):
            commands.append(_redact_command(cleaned))
    return tuple(commands[:8])


def _redact_command(command: str) -> str:
    command = re.sub(r"(?i)(password|pass|token|key|secret)=\S+", r"\1=[redacted]", command)
    command = re.sub(r"(?i)(-p|--password)\s+\S+", r"\1 [redacted]", command)
    return command[:240]


def _safety_notes(text: str, commands: tuple[str, ...]) -> tuple[str, ...]:
    notes = [
        "TryHackMe is treated as authorized training scope only.",
        "Use active commands only inside the room, localhost, or an owned lab target.",
    ]
    if commands:
        notes.append("Commands are saved as study notes, not executed by NELA.")
    if re.search(r"\b(public ip|internet|real target|third party)\b", text, flags=re.IGNORECASE):
        notes.append("Public or third-party targets require refusal or explicit authorized scope.")
    return tuple(notes)


def _summary(text: str, topic: str, concepts: tuple[str, ...]) -> str:
    compact = " ".join(text.strip().split())
    if compact:
        return compact[:420]
    return f"Study lesson about {topic}: {', '.join(concepts[:5])}."


def _topic_tags(concepts: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(concept.replace(" ", "_") for concept in concepts[:6])


def _lesson_lines(
    topic: str,
    summary: str,
    concepts: tuple[str, ...],
    commands: tuple[str, ...],
    safety_notes: tuple[str, ...],
) -> tuple[str, ...]:
    return (
        f"Topic: {topic}",
        f"Summary: {summary}",
        f"Concepts: {', '.join(concepts)}",
        f"Commands: {', '.join(commands) if commands else 'none captured'}",
        f"Safety: {' | '.join(safety_notes)}",
    )


def _review_questions(topic: str, concepts: tuple[str, ...]) -> tuple[str, ...]:
    primary = concepts[0] if concepts else topic
    return (
        f"What problem does {primary} solve in a legal lab?",
        f"Which signals show that {topic} is inside authorized scope?",
        "What should NELA refuse if the same technique is aimed at a third party?",
    )


def _skill_graph_lines(store: LearningMemoryStore) -> tuple[str, ...]:
    return _graph_lines(store.skill_graph(source="tryhackme"))


def _graph_lines(graph: dict[str, int]) -> tuple[str, ...]:
    if not graph:
        return ("No TryHackMe skill graph yet.",)
    return tuple(f"{name}: {count}" for name, count in list(graph.items())[:12])


def _recent_lesson_lines(lessons) -> tuple[str, ...]:
    if not lessons:
        return ("No TryHackMe lessons saved yet.",)
    return tuple(f"{lesson.created_at}: {lesson.topic} ({lesson.room or 'no room'})" for lesson in lessons[-8:])
