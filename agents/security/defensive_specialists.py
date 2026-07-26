"""Focused passive cyber-defense specialist agents."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import re
import socket
from urllib.parse import urlparse

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


@dataclass(frozen=True)
class DefenseCheck:
    rule_id: str
    pattern: str
    title: str
    severity: RiskLevel
    recommendation: str


class SecretsHygieneAgent(SpecialistAgent):
    name = "secrets_hygiene"
    domain = AgentDomain.SECURITY
    purpose = "Find likely secret-handling risks in supplied local text or configuration."
    capabilities = ("secrets.review", "secret_rotation.plan", "credential_hygiene")

    def _handlers(self):
        return {**super()._handlers(), "review_secrets_hygiene": self._review_secrets_hygiene}

    def _review_secrets_hygiene(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        checks = (
            DefenseCheck(
                "SEC-001",
                r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[^'\"\s]{8,}",
                "ייתכן שיש סוד גלוי",
                RiskLevel.CRITICAL,
                "להוציא סודות מהקוד, לסובב credentials שנחשפו, ולהשתמש במנהל סודות או משתני סביבה מאובטחים.",
            ),
            DefenseCheck(
                "SEC-002",
                r"(bearer|basic)\s+[a-z0-9._~+/=-]{12,}",
                "נראה כמו credential בתוך טקסט",
                RiskLevel.HIGH,
                "להחליף את ה־credential, להסיר אותו מהטקסט, ולבדוק אם נשמר בהיסטוריית Git או בלוגים.",
            ),
            DefenseCheck(
                "SEC-003",
                r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
                "מפתח פרטי נמצא בטקסט",
                RiskLevel.CRITICAL,
                "להחליף את המפתח, להסיר אותו מהמאגר, ולוודא שהרשאות הגישה מוגבלות.",
            ),
            DefenseCheck(
                "SEC-004",
                r"\.env(?:\s|$|/)",
                "קובץ env דורש בדיקת חשיפה",
                RiskLevel.MEDIUM,
                "לוודא שהקובץ לא מחויב ל־Git, שיש `.env.example`, ושאין ערכי production מקומיים.",
            ),
            DefenseCheck(
                "SEC-005",
                r"\bAKIA[0-9A-Z]{16}\b",
                "נראה כמו AWS access key",
                RiskLevel.CRITICAL,
                "לסובב את המפתח ב־AWS, לבדוק CloudTrail לשימוש חריג, ולהעביר את הסוד למנהל סודות.",
            ),
            DefenseCheck(
                "SEC-006",
                r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b",
                "נראה כמו GitHub token",
                RiskLevel.CRITICAL,
                "לבטל או לסובב את ה־token, לבדוק הרשאות scope, ולהחליף לשימוש ב־GitHub secret מאובטח.",
            ),
            DefenseCheck(
                "SEC-007",
                r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b",
                "נראה כמו Slack token",
                RiskLevel.CRITICAL,
                "לבטל את ה־token, לבדוק התקנות app והרשאות workspace, ולהעביר לשמירה מאובטחת.",
            ),
        )
        findings = _findings_from_checks(command, checks, "secrets_hygiene")
        return AgentWorkProduct(
            summary=f"Secrets hygiene review completed with {len(findings)} finding(s).",
            findings=tuple(findings),
            artifacts=(artifact("checklist", "secrets_hygiene", _secrets_checklist()),),
            next_steps=("אם אושר ממצא סוד, לסובב אותו לפני שממשיכים לפתח.",),
        )


class IdentityAccessAgent(SpecialistAgent):
    name = "identity_access"
    domain = AgentDomain.SECURITY
    purpose = "Review access-control and permission posture for least-privilege risks."
    capabilities = ("access.review", "least_privilege", "permission_boundary")

    def _handlers(self):
        return {**super()._handlers(), "review_access_controls": self._review_access_controls}

    def _review_access_controls(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        checks = (
            DefenseCheck(
                "IAM-001",
                r"\b(admin|owner|root)\b",
                "הרשאת על דורשת הצדקה",
                RiskLevel.MEDIUM,
                "להחליף הרשאת על ב־role מצומצם, עם תוקף, בעלים וסיבה מתועדת.",
            ),
            DefenseCheck(
                "IAM-002",
                r"\b(allow_all|AllowAny|anyone|public-read|public-write|anonymous|unauthenticated)\b",
                "מדיניות גישה פתוחה מדי",
                RiskLevel.HIGH,
                "להגדיר זהויות מפורשות, להגביל ציבוריות, ולתעד חריגים זמניים בלבד.",
            ),
            DefenseCheck(
                "IAM-003",
                r"\*\s*:\s*\*|\baction\s*:\s*\*|\b(Action|Resource|Principal)\s*[:=]\s*['\"]?\*",
                "הרשאה כללית מדי",
                RiskLevel.HIGH,
                "להחליף wildcard ברשימת פעולות, משאבים וזהויות מינימלית.",
            ),
            DefenseCheck(
                "IAM-004",
                r"\bskip(_|-)?auth\b|\bauth\s*[:=]\s*false\b",
                "עקיפת אימות אפשרית",
                RiskLevel.HIGH,
                "להשאיר אימות פעיל, ולנתב חריגי פיתוח דרך feature flag מקומי עם audit.",
            ),
            DefenseCheck(
                "IAM-005",
                r"NOPASSWD\s*:\s*ALL|sudo\s+ALL\s*=\s*\(ALL\)",
                "sudo רחב מדי",
                RiskLevel.HIGH,
                "להגביל sudo לפקודות ספציפיות, להסיר NOPASSWD כשאפשר, ולבדוק מי חבר בקבוצה.",
            ),
        )
        findings = _findings_from_checks(command, checks, "identity_access")
        return AgentWorkProduct(
            summary=f"Identity/access review completed with {len(findings)} finding(s).",
            findings=tuple(findings),
            artifacts=(artifact("checklist", "identity_access", _identity_access_checklist()),),
            next_steps=("להתחיל מהרשאות רחבות או אימות חסר, כי אלה מעלות סיכון מהר.",),
        )


class NetworkDefenseAgent(SpecialistAgent):
    name = "network_defense"
    domain = AgentDomain.SECURITY
    purpose = "Review supplied network configuration for exposure and transport-security risks."
    capabilities = ("network.exposure.review", "tls.posture", "local_service_hardening")

    def _handlers(self):
        return {**super()._handlers(), "review_network_exposure": self._review_network_exposure}

    def _review_network_exposure(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        checks = (
            DefenseCheck(
                "NET-001",
                r"0\.0\.0\.0|::/0|0\.0\.0\.0/0",
                "חשיפת רשת רחבה",
                RiskLevel.MEDIUM,
                "להגביל bind או ingress ל־localhost או לטווח מאושר.",
            ),
            DefenseCheck(
                "NET-002",
                r"\bhttp://(?!localhost\b|127\.0\.0\.1\b|\[::1\]|0\.0\.0\.0\b)[^\s]+",
                "תקשורת HTTP ללא TLS",
                RiskLevel.MEDIUM,
                "להשתמש ב־HTTPS או לתעד חריג מקומי זמני.",
            ),
            DefenseCheck(
                "NET-003",
                r"verify\s*[:=]\s*false|insecure_skip_verify",
                "אימות TLS כבוי",
                RiskLevel.HIGH,
                "להשאיר אימות TLS פעיל ולתקן trust roots במקום לעקוף.",
            ),
            DefenseCheck(
                "NET-004",
                r"(?:0\.0\.0\.0|::)\s*:\s*(22|3389|5432|6379|9200)\b|\b(22|3389|5432|6379|9200)\b.*\b(public|open|internet)\b",
                "שירות רגיש נראה חשוף",
                RiskLevel.HIGH,
                "לסגור חשיפה ציבורית ולהשתמש ב־VPN, tunnel, או רשת פנימית.",
            ),
            DefenseCheck(
                "NET-005",
                r"Access-Control-Allow-Origin\s*:\s*\*|\bcors\s*[:=]\s*['\"]?\*",
                "CORS פתוח מדי",
                RiskLevel.MEDIUM,
                "להגדיר allowlist לדומיינים צפויים בלבד ולחסום credentials עם wildcard.",
            ),
        )
        findings = _findings_from_checks(command, checks, "network_defense")
        return AgentWorkProduct(
            summary=f"Network defense review completed with {len(findings)} finding(s).",
            findings=tuple(findings),
            artifacts=(artifact("checklist", "network_defense", _network_defense_checklist()),),
            next_steps=("לא לבצע סריקה אקטיבית בלי יעד מקומי/מאושר והרשאה מפורשת.",),
        )


class NetworkIntelligenceAgent(SpecialistAgent):
    name = "network_intelligence"
    domain = AgentDomain.SECURITY
    purpose = "Classify IPs and explain local network/VPN posture without external scanning."
    capabilities = ("ip.classification", "vpn.status", "network.status", "access.troubleshoot")

    def _handlers(self):
        return {
            **super()._handlers(),
            "classify_network_target": self._classify_network_target,
            "detect_vpn_status": self._detect_vpn_status,
            "local_network_report": self._local_network_report,
            "safe_access_troubleshoot": self._safe_access_troubleshoot,
        }

    def _classify_network_target(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        targets = _network_targets(text)
        findings = tuple(_target_finding(target) for target in targets) or (
            TaskFinding(
                title="לא זוהה יעד רשת ברור",
                severity=RiskLevel.INFO,
                category="network_intelligence",
                location="conversation",
                recommendation="שלח IP, דומיין או URL, למשל 192.168.1.1 או https://example.com.",
            ),
        )
        return AgentWorkProduct(
            summary=f"Network target classification completed for {len(targets)} target(s).",
            findings=findings,
            artifacts=(artifact("network_targets", "classified_targets", tuple(targets) or ("No target found.",)),),
            next_steps=("יעד חיצוני מקבל הסבר בלבד. בדיקות אקטיביות דורשות בעלות או אישור מפורש.",),
        )

    def _detect_vpn_status(self, command: AgentCommand) -> AgentWorkProduct:
        interface_names = _interface_names(command)
        vpn_interfaces = tuple(name for name in interface_names if _looks_like_vpn_interface(name))
        if vpn_interfaces:
            finding = TaskFinding(
                title="נראה שיש ממשק VPN פעיל",
                severity=RiskLevel.INFO,
                category="vpn_status",
                location="local_machine",
                evidence=f"interfaces: {', '.join(vpn_interfaces)}",
                recommendation="לאמת מול אפליקציית ה־VPN ולבדוק שאין DNS leak אם עובדים על מידע רגיש.",
            )
            summary = "VPN-like interface detected."
        else:
            finding = TaskFinding(
                title="לא זוהה ממשק VPN ברור",
                severity=RiskLevel.INFO,
                category="vpn_status",
                location="local_machine",
                evidence=f"interfaces checked: {', '.join(interface_names[:12]) if interface_names else 'none'}",
                recommendation="אם VPN אמור להיות מחובר, לפתוח את אפליקציית ה־VPN ולבדוק route/DNS לפני עבודה רגישה.",
            )
            summary = "No VPN-like interface detected."
        return AgentWorkProduct(
            summary=summary,
            findings=(finding,),
            artifacts=(artifact("interfaces", "local_interfaces", interface_names or ("No interfaces found.",)),),
            next_steps=("הבדיקה פסיבית ומקומית; היא לא מאשרת אנונימיות ולא עוקפת חסימות.",),
        )

    def _local_network_report(self, command: AgentCommand) -> AgentWorkProduct:
        interface_names = _interface_names(command)
        local_ips = _local_ip_candidates()
        findings = [
            TaskFinding(
                title="דוח רשת מקומי נבנה",
                severity=RiskLevel.INFO,
                category="network_status",
                location="local_machine",
                evidence=f"interfaces={', '.join(interface_names[:12]) if interface_names else 'none'}; local_ips={', '.join(local_ips) if local_ips else 'none'}",
                recommendation="להשתמש בדוח הזה לאבחון מקומי בלבד; בדיקת יעד חיצוני דורשת scope מאושר.",
            )
        ]
        if any(_looks_like_vpn_interface(name) for name in interface_names):
            findings.append(
                TaskFinding(
                    title="סימן אפשרי ל־VPN בדוח המקומי",
                    severity=RiskLevel.INFO,
                    category="vpn_status",
                    location="local_machine",
                    recommendation="לוודא שה־VPN הוא זה שהתכוונת להשתמש בו ולבדוק DNS במידת הצורך.",
                )
            )
        return AgentWorkProduct(
            summary="Local network report prepared.",
            findings=tuple(findings),
            artifacts=(
                artifact("interfaces", "local_interfaces", interface_names or ("No interfaces found.",)),
                artifact("local_ips", "local_ip_candidates", local_ips or ("No local IP candidates found.",)),
            ),
            next_steps=("אפשר לבקש ממני לסווג IP מסוים או לבדוק אם נראה VPN פעיל.",),
        )

    def _safe_access_troubleshoot(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        findings = [
            TaskFinding(
                title="זוהתה בקשת גישה או חסימה",
                severity=RiskLevel.INFO,
                category="access_troubleshooting",
                location="conversation",
                evidence=_redact(text),
                recommendation="אני לא עוקפת חסימות. הדרך התקינה היא לבדוק DNS/VPN/firewall, להתחבר עם הרשאה, לבקש allowlist, או לתקן config.",
            )
        ]
        targets = _network_targets(text)
        findings.extend(_target_finding(target) for target in targets[:3])
        return AgentWorkProduct(
            summary="Safe access troubleshooting guidance prepared.",
            findings=tuple(findings),
            artifacts=(artifact("playbook", "safe_access_troubleshooting", _safe_access_playbook()),),
            next_steps=("להתחיל באבחון מקומי: VPN, DNS, route, הרשאות, ואז לפנות לבעל המערכת אם צריך.",),
        )


class SupplyChainSecurityAgent(SpecialistAgent):
    name = "supply_chain_security"
    domain = AgentDomain.SECURITY
    purpose = "Review dependency, build, and release hygiene for supply-chain risk."
    capabilities = ("supply_chain.review", "build_integrity", "release_hygiene")

    def _handlers(self):
        return {**super()._handlers(), "review_supply_chain": self._review_supply_chain}

    def _review_supply_chain(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        checks = (
            DefenseCheck(
                "SUP-001",
                r":latest\b|\blatest\b",
                "גרסה לא מקובעת",
                RiskLevel.MEDIUM,
                "לקבע גרסאות או digests כדי למנוע שינוי לא צפוי.",
            ),
            DefenseCheck(
                "SUP-002",
                r"curl\s+[^|]+?\|\s*(sh|bash)|wget\s+[^|]+?\|\s*(sh|bash)",
                "הרצת סקריפט מרשת בצינור",
                RiskLevel.HIGH,
                "להוריד, לאמת hash/signature, ואז להריץ רק אם המקור מאושר.",
            ),
            DefenseCheck(
                "SUP-003",
                r"--no-verify|--ignore-scripts|strict-ssl\s*=\s*false",
                "עקיפת בדיקות supply-chain",
                RiskLevel.HIGH,
                "לא לעקוף אימות או hooks בלי חריג מתועד.",
            ),
            DefenseCheck(
                "SUP-004",
                r"(package-lock\.json|poetry\.lock|uv\.lock|pnpm-lock\.yaml|yarn\.lock)",
                "Lockfile זוהה",
                RiskLevel.INFO,
                "לוודא שה־lockfile מחויב ונבדק ב־CI.",
            ),
            DefenseCheck(
                "SUP-005",
                r"--extra-index-url|--trusted-host|pip\s+install\s+git\+http://",
                "מקור תלותים דורש אימות",
                RiskLevel.HIGH,
                "להגביל registries מאושרים, להימנע מ־trusted-host, ולבדוק dependency confusion.",
            ),
            DefenseCheck(
                "SUP-006",
                r"\"postinstall\"\s*:",
                "סקריפט postinstall דורש סקירה",
                RiskLevel.MEDIUM,
                "לבדוק שהסקריפט הכרחי, מקומי, לא מוריד קוד נוסף, ומתועד ב־review.",
            ),
        )
        findings = _findings_from_checks(command, checks, "supply_chain")
        return AgentWorkProduct(
            summary=f"Supply-chain review completed with {len(findings)} finding(s).",
            findings=tuple(findings),
            artifacts=(artifact("checklist", "supply_chain_security", _supply_chain_checklist()),),
            next_steps=("להפריד בין עדכון תלותים, בדיקת advisories, והרצת בדיקות לפני merge.",),
        )


def _text(command: AgentCommand) -> str:
    return str(command.payload.get("text") or command.payload.get("source") or command.payload.get("config") or "")


def _network_targets(text: str) -> tuple[str, ...]:
    targets: list[str] = []
    seen: set[str] = set()
    for raw in re.findall(r"\bhttps?://[^\s,;]+", text, flags=re.IGNORECASE):
        value = raw.rstrip(".,;!?)'\"")
        if value not in seen:
            targets.append(value)
            seen.add(value)
    ip_pattern = r"(?<![\w:])(?:\d{1,3}\.){3}\d{1,3}(?![\w:])|(?<!\w)(?:[0-9a-f]{0,4}:){2,}[0-9a-f]{0,4}(?!\w)"
    for raw in re.findall(ip_pattern, text, flags=re.IGNORECASE):
        value = raw.strip("[]").rstrip(".,;!?)'\"")
        if _is_ip(value) and value not in seen:
            targets.append(value)
            seen.add(value)
    host_pattern = r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b"
    for raw in re.findall(host_pattern, text, flags=re.IGNORECASE):
        value = raw.lower().rstrip(".,;!?)'\"")
        if value not in seen:
            targets.append(value)
            seen.add(value)
    return tuple(targets)


def _target_finding(target: str) -> TaskFinding:
    parsed = urlparse(target if "://" in target else f"//{target}")
    host = parsed.hostname or target.strip("[]")
    if _is_ip(host):
        address = ipaddress.ip_address(host)
        label, recommendation = _ip_classification(address)
        return TaskFinding(
            title=f"{host} הוא {label}",
            severity=RiskLevel.INFO if not address.is_global else RiskLevel.MEDIUM,
            category="ip_classification",
            location=target,
            evidence=f"version=IPv{address.version}; private={address.is_private}; global={address.is_global}; loopback={address.is_loopback}",
            recommendation=recommendation,
        )
    if host in {"localhost"} or host.endswith(".local"):
        return TaskFinding(
            title=f"{host} הוא יעד מקומי",
            severity=RiskLevel.INFO,
            category="target_classification",
            location=target,
            recommendation="מתאים לאבחון מקומי. פעולה אקטיבית עדיין צריכה להיות מוגדרת וברורה.",
        )
    return TaskFinding(
        title=f"{host} נראה יעד חיצוני",
        severity=RiskLevel.MEDIUM,
        category="target_classification",
        location=target,
        recommendation="אני יכולה להסביר ולסווג את היעד, אבל לא לסרוק או לעקוף אותו בלי בעלות או הרשאה כתובה.",
    )


def _ip_classification(address: ipaddress._BaseAddress) -> tuple[str, str]:
    if address.is_loopback:
        return "localhost", "זה יעד מקומי על המחשב עצמו. טוב לבדיקות פיתוח מקומיות."
    if address.is_private:
        return "IP פנימי/private", "זה יעד ברשת פנימית. בדוק בעלות והרשאה לפני פעולה אקטיבית."
    if address.is_link_local:
        return "IP link-local", "זה יעד מקומי לרשת/ממשק. מתאים לאבחון מקומי בלבד."
    if address.is_multicast:
        return "כתובת multicast", "לא מטפלים בזה כיעד רגיל; צריך להבין את פרוטוקול הרשת לפני פעולה."
    if address.is_reserved:
        return "כתובת reserved", "לא להשתמש בזה כיעד בדיקה רגיל."
    if address.is_global:
        return "IP ציבורי", "הסבר וסיווג בלבד. אין סריקה או עקיפה בלי הרשאה מפורשת."
    return "IP לא מסווג בבירור", "להמשיך בזהירות ולבדוק scope לפני פעולה."


def _is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True


def _interface_names(command: AgentCommand) -> tuple[str, ...]:
    supplied = command.payload.get("interfaces")
    if isinstance(supplied, (list, tuple)):
        return tuple(str(item) for item in supplied)
    try:
        return tuple(name for _, name in socket.if_nameindex())
    except OSError:
        return ()


def _looks_like_vpn_interface(name: str) -> bool:
    normalized = name.lower()
    return normalized.startswith(("utun", "tun", "tap", "ppp", "wg")) or any(
        marker in normalized for marker in ("vpn", "wireguard", "tailscale", "zerotier", "ipsec")
    )


def _local_ip_candidates() -> tuple[str, ...]:
    candidates: list[str] = []
    seen: set[str] = set()
    try:
        hostname = socket.gethostname()
        infos = socket.getaddrinfo(hostname, None)
    except OSError:
        return ()
    for info in infos:
        address = str(info[4][0])
        if address not in seen and _is_ip(address):
            candidates.append(address)
            seen.add(address)
    return tuple(candidates)


def _findings_from_checks(command: AgentCommand, checks: tuple[DefenseCheck, ...], category: str) -> list[TaskFinding]:
    text = _text(command)
    location = str(command.payload.get("target", "conversation"))
    findings: list[TaskFinding] = []
    for check in checks:
        if re.search(check.pattern, text, flags=re.IGNORECASE):
            findings.append(
                TaskFinding(
                    title=check.title,
                    severity=check.severity,
                    category=category,
                    location=location,
                    evidence=f"{check.rule_id}: {_redact(text)}",
                    recommendation=check.recommendation,
                )
            )
    return findings


def _redact(text: str) -> str:
    compact = " ".join(text.split())[:180]
    compact = re.sub(r"(?i)(api[_-]?key|secret|token|password)(\s*[:=]\s*)['\"]?[^'\"\s]+['\"]?", r"\1\2[redacted]", compact)
    compact = re.sub(r"(?i)(bearer|basic)\s+[a-z0-9._~+/=-]{8,}", r"\1 [redacted]", compact)
    compact = re.sub(r"\bAKIA[0-9A-Z]{16}\b", "[redacted-aws-key]", compact)
    compact = re.sub(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b", "[redacted-github-token]", compact)
    compact = re.sub(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b", "[redacted-slack-token]", compact)
    compact = re.sub(r"-----BEGIN [^-]+PRIVATE KEY-----.*", "-----BEGIN [redacted] PRIVATE KEY-----", compact)
    return compact


def _secrets_checklist() -> tuple[str, ...]:
    return (
        "Search for hardcoded keys, tokens, passwords, and private keys.",
        "Rotate confirmed leaked credentials before merging.",
        "Store runtime secrets outside source control.",
        "Keep evidence redacted in user-facing responses and logs.",
    )


def _identity_access_checklist() -> tuple[str, ...]:
    return (
        "Confirm every high-privilege role has an owner, reason, and expiry.",
        "Replace wildcard actions, resources, and principals with least-privilege scopes.",
        "Reject unauthenticated or anonymous access unless it is public-by-design and documented.",
        "Audit every permission exception and review it before release.",
    )


def _network_defense_checklist() -> tuple[str, ...]:
    return (
        "Prefer localhost for development services and explicit allowlists for shared services.",
        "Avoid public exposure of SSH, RDP, databases, caches, and search backends.",
        "Keep TLS verification enabled; fix trust configuration instead of bypassing it.",
        "Keep active scans limited to approved local or owned targets.",
    )


def _supply_chain_checklist() -> tuple[str, ...]:
    return (
        "Pin dependency versions or image digests for repeatable builds.",
        "Avoid curl-to-shell install paths; verify source and integrity first.",
        "Use approved registries and watch for dependency-confusion paths.",
        "Review install scripts and keep lockfiles under source control.",
    )


def _safe_access_playbook() -> tuple[str, ...]:
    return (
        "Do not bypass controls or hide traffic.",
        "Check local connectivity, VPN state, DNS, route, and firewall rules.",
        "Use normal sign-in, approved allowlists, or written authorization.",
        "For owned systems, document scope before any active diagnostic action.",
    )
