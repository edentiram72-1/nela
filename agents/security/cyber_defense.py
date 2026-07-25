"""Defensive cyber posture agent for NELA."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


class CyberDefenseAgent(SpecialistAgent):
    name = "cyber_defense"
    domain = AgentDomain.SECURITY
    purpose = "Build defensive posture reports and prioritized protection actions."
    capabilities = ("defense.posture", "defense.findings", "defense.plan")

    def _handlers(self):
        return {
            **super()._handlers(),
            "defense_posture_check": self._defense_posture_check,
            "recommend_defense_actions": self._recommend_defense_actions,
            "prioritize_security_findings": self._prioritize_security_findings,
        }

    def _defense_posture_check(self, command: AgentCommand) -> AgentWorkProduct:
        target = str(command.payload.get("target") or command.payload.get("text") or "NELA local workspace")
        findings = (
            TaskFinding(
                title="לבדוק הרשאות וגישה",
                severity=RiskLevel.MEDIUM,
                category="access_control",
                location=target,
                evidence="No explicit owner/scope evidence was supplied with this request.",
                recommendation="להגדיר מי הבעלים של היעד, אילו פעולות מותרות, ואילו נתיבים או שירותים מחוץ לתחום.",
            ),
            TaskFinding(
                title="להפעיל תיעוד וביקורת לפני פעולה",
                severity=RiskLevel.MEDIUM,
                category="audit",
                location=target,
                evidence="Defense flow should preserve what was checked and what was changed.",
                recommendation="לתעד כל בדיקה הגנתית, ממצא, החלטה ומשימת המשך ביומן הביקורת.",
            ),
            TaskFinding(
                title="להקשיח תלותים וקונפיגורציה",
                severity=RiskLevel.LOW,
                category="hardening",
                location=target,
                evidence="Dependency and configuration data were not supplied yet.",
                recommendation="להריץ סקירת תלותים, חיפוש סודות, בדיקת TLS/קונפיגורציה ובדיקת הרשאות מינימליות.",
            ),
            TaskFinding(
                title="להגדיר גיבוי והתאוששות",
                severity=RiskLevel.LOW,
                category="resilience",
                location=target,
                evidence="No backup or restore proof was supplied.",
                recommendation="לתעד שלבי שחזור ולבדוק שאפשר לשחזר מידע חשוב באופן מקומי.",
            ),
        )
        return AgentWorkProduct(
            summary=f"Defensive posture check prepared for {target}.",
            findings=findings,
            artifacts=(
                artifact(
                    "defense_plan",
                    "first_defense_actions",
                    (
                        "1. Confirm authorized scope.",
                        "2. Review access and secrets.",
                        "3. Check dependencies and configuration.",
                        "4. Add monitoring/audit coverage.",
                        "5. Test recovery path.",
                    ),
                ),
            ),
            next_steps=(
                "להתחיל באישור scope ובכיסוי audit לפני כל בדיקה אקטיבית.",
                "להריץ סקירת קוד, קונפיגורציה ותלותים רק על ארטיפקטים מקומיים שסופקו.",
            ),
        )

    def _recommend_defense_actions(self, command: AgentCommand) -> AgentWorkProduct:
        target = str(command.payload.get("target") or "the local system")
        return AgentWorkProduct(
            summary=f"Defense action plan prepared for {target}.",
            findings=(
                TaskFinding(
                    title="להתחיל בהגנות שלא משנות מערכת",
                    severity=RiskLevel.INFO,
                    category="defense_plan",
                    location=target,
                    recommendation="להתחיל בסקירה פסיבית, ואז לבקש אישור לפני כל שינוי.",
                ),
            ),
            artifacts=(
                artifact(
                    "defense_actions",
                    "safe_defense_sequence",
                    (
                        "Passive review",
                        "Findings summary",
                        "User confirmation",
                        "Scoped local fix",
                        "Regression test",
                        "Audit update",
                    ),
                ),
            ),
        )

    def _prioritize_security_findings(self, command: AgentCommand) -> AgentWorkProduct:
        findings = command.payload.get("findings", ())
        count = len(findings) if isinstance(findings, (list, tuple)) else 0
        return AgentWorkProduct(
            summary=f"Prioritized {count} supplied finding(s).",
            findings=(
                TaskFinding(
                    title="לתעדף לפי השפעה והרשאה",
                    severity=RiskLevel.INFO,
                    category="triage",
                    recommendation="לטפל קודם בממצאי הרשאות, סודות והרצה לפני ניקיון או שיפורי נוחות.",
                ),
            ),
            next_steps=("להפוך את הממצא המאושר הראשון למשימה קטנה ומדידה.",),
        )
