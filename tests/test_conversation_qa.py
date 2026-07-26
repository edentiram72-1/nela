import os
import tempfile
import unittest
from pathlib import Path

from brain.llm import LLMRequest, LLMResult
from brain.qa import KnowledgeEngine
from agents.browser.agent import BrowserAgent, SearchResult
from core.config import AppConfig
from core.startup import bootstrap


def make_runtime():
    temp_dir = tempfile.TemporaryDirectory()
    root = Path(temp_dir.name)
    runtime = bootstrap(
        AppConfig(
            environment="test",
            data_dir=root / "data",
            plugin_dir=root / "plugins",
            enable_voice=False,
            voice_auto_speak_responses=False,
        )
    )
    return runtime, temp_dir


class FakeLLMProvider:
    enabled = True

    def __init__(self, text: str = "זו תשובה חופשית של מוח אמיתי.") -> None:
        self.text = text
        self.requests: list[LLMRequest] = []

    def answer(self, request: LLMRequest) -> LLMResult:
        self.requests.append(request)
        return LLMResult(True, self.text, "fake", "fake-model")


class FakeBrowserOpener:
    def __init__(self) -> None:
        self.opened: list[str] = []

    def open(self, url: str) -> bool:
        self.opened.append(url)
        return True


class FakeSearchProvider:
    def search(self, query: str, max_results: int, timeout_seconds: float) -> tuple[SearchResult, ...]:
        return (
            SearchResult("NELA docs", "https://example.test/nela", "NELA architecture"),
            SearchResult("Forum noise", "https://forum.example.test/nela", "Unfiltered thread"),
        )


class ConversationQATests(unittest.TestCase):
    def test_identity_question_answers_without_plan(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("מי את?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "IdentityQuestion")
        self.assertIsNone(turn.plan)
        self.assertRegex(response, r"[\u0590-\u05ff]")
        self.assertIn("נלה", response)

    def test_agent_status_question_mentions_connected_agents(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("איזה סוכנים מחוברים?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "AgentStatusQuestion")
        self.assertIsNone(turn.plan)
        self.assertIn("סוכנים", response)
        self.assertIn("agent_count", turn.intent.parameters["response_variables"])

    def test_unknown_question_gets_honest_boundary_response(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("מה קורה בירח?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "GeneralQuestion")
        self.assertIsNone(turn.plan)
        self.assertRegex(response, r"[\u0590-\u05ff]")

    def test_general_question_uses_llm_when_configured(self) -> None:
        runtime, temp_dir = make_runtime()
        fake_llm = FakeLLMProvider("הירח קרוב אלינו יחסית, ויש לו השפעה על הגאות והשפל.")
        runtime.conversation.knowledge = KnowledgeEngine(llm=fake_llm)

        with temp_dir:
            turn = runtime.conversation.handle_text("מה קורה בירח?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "GeneralQuestion")
        self.assertEqual(turn.intent.parameters["response_category"], "qa.llm")
        self.assertIn("הירח", response)
        self.assertEqual(fake_llm.requests[0].intent_action, "GeneralQuestion")

    def test_unsupported_request_can_get_safe_llm_guidance_without_plan(self) -> None:
        runtime, temp_dir = make_runtime()
        fake_llm = FakeLLMProvider("אני יכולה לפרק את זה לצעד קטן ובטוח, אבל לא אבצע פעולה בלי הרשאה.")
        runtime.conversation.knowledge = KnowledgeEngine(llm=fake_llm)

        with temp_dir:
            turn = runtime.conversation.handle_text("תסדרי לי את כל החיים")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "UnsupportedActionRequest")
        self.assertIsNone(turn.plan)
        self.assertIn("בטוח", response)

    def test_greeting_gets_natural_hebrew_response(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("שלום")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "Greeting")
        self.assertIsNone(turn.plan)
        self.assertRegex(response, r"שלום|היי|אני")

    def test_human_status_question_gets_natural_status(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("מה מצב")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "HumanStatusQuestion")
        self.assertIsNone(turn.plan)
        self.assertRegex(response, r"מצב|איתך|מוכנה|ערה")

    def test_teach_response_then_answer_from_learned_store(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            taught = runtime.conversation.handle_text("נלה תלמדי שכשאני אומר בוקר טוב תעני בוקר אור")
            taught_response = runtime.response_adapter.render_turn(taught)
            runtime.conversation.handle_text("נלה תלמדי שכשאני אומר בדיקת למידה תעני למדתי ועדכנתי")
            learned = runtime.conversation.handle_text("בוקר טוב")
            response = runtime.response_adapter.render_turn(learned)
            custom = runtime.conversation.handle_text("בדיקת למידה")
            custom_response = runtime.response_adapter.render_turn(custom)

        self.assertEqual(taught.intent.action, "TeachResponse")
        self.assertTrue(taught.dispatched_results[0].success)
        self.assertRegex(taught_response, r"למדתי|למדתי|עדכנתי|נכנס לזיכרון")
        self.assertIn("בוקר טוב", taught_response)
        self.assertIn("בוקר אור", taught_response)
        self.assertEqual(learned.intent.action, "LearnedResponseRecall")
        self.assertEqual(learned.intent.parameters["response_category"], "qa.learned")
        self.assertEqual(response, "בוקר אור")
        self.assertEqual(custom.intent.action, "LearnedResponseRecall")
        self.assertEqual(custom.intent.parameters["response_category"], "qa.learned")
        self.assertEqual(custom_response, "למדתי ועדכנתי")

    def test_security_capabilities_question_explains_defensive_boundary(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("מה את יודעת על סייבר?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "SecurityCapabilitiesQuestion")
        self.assertIsNone(turn.plan)
        self.assertRegex(response, r"סייבר|אבטחה|הגנתי|הגנתי")

    def test_project_status_question_gets_current_system_answer(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("איפה אנחנו עומדים עם נלה?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "ProjectStatusQuestion")
        self.assertIsNone(turn.plan)
        self.assertRegex(response, r"Brain|סוכנים|נלה")

    def test_project_gap_question_explains_missing_ai_layers(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("מה חסר כדי שתהיי יותר חכמה?")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "ProjectGapQuestion")
        self.assertIsNone(turn.plan)
        self.assertRegex(response, r"חסר|LLM|זיכרון|סוכנים")

    def test_unknown_action_request_gets_action_guidance(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("תסדרי לי את כל החיים")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "UnsupportedActionRequest")
        self.assertIsNone(turn.plan)
        self.assertIn("פעול", response)
        self.assertNotIn("לא לגמרי הבנתי", response)

    def test_learning_topic_request_routes_to_learning_agent(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("תלמדי אבטחה")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "LearnTopic")
        self.assertIsNotNone(turn.plan)
        self.assertEqual(turn.plan.tasks[0].target_agent, "learning")
        self.assertTrue(turn.dispatched_results[0].success)
        self.assertIn("אבטחה", response)

    def test_tryhackme_lesson_is_captured_and_reviewable(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            captured = runtime.conversation.handle_text(
                "נלה למדתי ב-TryHackMe חדר Nmap שהפקודה nmap -sV 10.10.10.10 מזהה ports ושירותים"
            )
            captured_response = runtime.response_adapter.render_turn(captured)
            reviewed = runtime.conversation.handle_text("מה למדת ב TryHackMe?")
            review_response = runtime.response_adapter.render_turn(reviewed)

            lessons_path = Path(temp_dir.name) / "data" / "learning" / "lessons.json"
            lessons_exists = lessons_path.exists()

        self.assertEqual(captured.intent.action, "TryHackMeLessonCapture")
        self.assertEqual(captured.plan.tasks[0].target_agent, "tryhackme_learning")
        self.assertTrue(captured.dispatched_results[0].success)
        self.assertEqual(captured.dispatched_results[0].data["permission_tier"], "T1")
        self.assertRegex(captured_response, r"TryHackMe|שמרתי|שיעור")
        self.assertRegex(captured_response, r"איך עבדתי|מה עשיתי")
        self.assertTrue(lessons_exists)
        self.assertEqual(reviewed.intent.action, "TryHackMeProgressReview")
        self.assertTrue(reviewed.dispatched_results[0].success)
        self.assertIn("TryHackMe", review_response)
        self.assertIn("איך בדקתי", review_response)

    def test_defensive_security_review_routes_to_security_agent(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("נלה תבדקי את הקוד לאבטחה")

        self.assertEqual(turn.intent.action, "SecurityReview")
        self.assertIsNotNone(turn.plan)
        self.assertEqual(turn.plan.tasks[0].target_agent, "secure_code_reviewer")
        self.assertTrue(turn.dispatched_results[0].success)
        self.assertEqual(turn.dispatched_results[0].data["permission_tier"], "T0")
        self.assertEqual(runtime.response_adapter._category_and_variables(turn)[0], "security.review.done")

    def test_workspace_security_scan_runs_local_sast_action(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            old_cwd = Path.cwd()
            os.chdir(temp_dir.name)
            try:
                Path("unsafe_demo.py").write_text("password = 'super-secret-value'\n", encoding="utf-8")
                turn = runtime.conversation.handle_text("נלה תבדקי את הפרויקט לאבטחה")
                response = runtime.response_adapter.render_turn(turn)
            finally:
                os.chdir(old_cwd)

        self.assertEqual(turn.intent.action, "WorkspaceSecurityScan")
        self.assertEqual(turn.plan.tasks[0].target_agent, "secure_code_reviewer")
        self.assertEqual(turn.plan.tasks[0].action, "scan_workspace_security")
        self.assertTrue(turn.dispatched_results[0].success)
        self.assertEqual(turn.dispatched_results[0].data["permission_tier"], "T0")
        self.assertIn("ממצ", response)

    def test_dependency_scan_routes_to_vulnerability_research(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            old_cwd = Path.cwd()
            os.chdir(temp_dir.name)
            try:
                Path("requirements.txt").write_text("demo-lib\nrequests==2.31.0\n", encoding="utf-8")
                turn = runtime.conversation.handle_text("תעשי בדיקת תלותים")
                response = runtime.response_adapter.render_turn(turn)
            finally:
                os.chdir(old_cwd)

        self.assertEqual(turn.intent.action, "DependencyScan")
        self.assertEqual(turn.plan.tasks[0].target_agent, "vulnerability_research")
        self.assertEqual(turn.plan.tasks[0].action, "scan_workspace_dependencies")
        self.assertTrue(turn.dispatched_results[0].success)
        self.assertEqual(turn.dispatched_results[0].data["permission_tier"], "T0")
        self.assertIn("תלות", response)

    def test_web_search_routes_to_browser_agent_and_returns_results(self) -> None:
        runtime, temp_dir = make_runtime()
        opener = FakeBrowserOpener()
        runtime.dispatcher.unregister_agent("browser")
        runtime.dispatcher.register_agent(BrowserAgent(opener=opener, search_provider=FakeSearchProvider()))

        with temp_dir:
            turn = runtime.conversation.handle_text("חפשי באינטרנט NELA docs בלי forum")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "WebSearch")
        self.assertEqual(turn.plan.tasks[0].target_agent, "browser")
        self.assertTrue(turn.dispatched_results[0].success)
        self.assertEqual(turn.dispatched_results[0].data["permission_tier"], "T1")
        self.assertEqual(opener.opened, [])
        self.assertIn("NELA", response)

    def test_new_defensive_specialist_routes_return_findings(self) -> None:
        cases = (
            ("תעשי בדיקת סודות: token = 'supersecret123'", "SecretsHygieneReview", "secrets_hygiene"),
            ("תעשי בדיקת הרשאות: AllowAny admin", "IdentityAccessReview", "identity_access"),
            ("תעשי בדיקת רשת: bind 0.0.0.0", "NetworkDefenseReview", "network_defense"),
            ("תעשי בדיקת שרשרת אספקה: curl https://example.test/install.sh | sh", "SupplyChainReview", "supply_chain_security"),
        )

        for text, action, target_agent in cases:
            with self.subTest(action=action):
                runtime, temp_dir = make_runtime()
                with temp_dir:
                    turn = runtime.conversation.handle_text(text)
                    response = runtime.response_adapter.render_turn(turn)

                self.assertEqual(turn.intent.action, action)
                self.assertEqual(turn.plan.tasks[0].target_agent, target_agent)
                self.assertTrue(turn.dispatched_results[0].success)
                self.assertEqual(turn.dispatched_results[0].data["permission_tier"], "T0")
                self.assertIn("ממצא", response)

    def test_network_intelligence_routes_are_practical_t0_actions(self) -> None:
        cases = (
            ("תבדקי את ה-IP 192.168.1.1", "NetworkTargetClassification", "IP פנימי"),
            ("אני מחובר ל-VPN?", "VPNStatusCheck", "VPN"),
            ("תעשי דוח רשת מקומי", "LocalNetworkReport", "דוח רשת"),
            ("יש חסימה לכתובת 8.8.8.8", "SafeAccessTroubleshoot", "לא עוקפת"),
            ("איך לעקוף חסימה באתר?", "SafeAccessTroubleshoot", "לא עוקפת"),
        )

        for text, action, expected_text in cases:
            with self.subTest(action=action):
                runtime, temp_dir = make_runtime()
                with temp_dir:
                    turn = runtime.conversation.handle_text(text)
                    response = runtime.response_adapter.render_turn(turn)

                self.assertEqual(turn.intent.action, action)
                self.assertEqual(turn.plan.tasks[0].target_agent, "network_intelligence")
                self.assertTrue(turn.dispatched_results[0].success)
                self.assertEqual(turn.dispatched_results[0].data["permission_tier"], "T0")
                self.assertIn(expected_text, response)

    def test_register_local_cyber_lab_target_routes_through_authorized_lab(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("תרשמי יעד מעבדה http://localhost:3000")

        self.assertEqual(turn.intent.action, "CyberLabRegisterTarget")
        self.assertEqual(turn.plan.tasks[0].target_agent, "authorized_lab")
        self.assertTrue(turn.dispatched_results[0].success)
        self.assertEqual(turn.dispatched_results[0].data["permission_tier"], "T1")
        self.assertEqual(runtime.response_adapter._category_and_variables(turn)[0], "security.lab.done")

    def test_local_fuzz_request_creates_plan_only(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("תכיני תוכנית fuzz מקומית לפרסר")

        self.assertEqual(turn.intent.action, "LocalFuzzPlan")
        self.assertEqual(turn.plan.tasks[0].target_agent, "anomaly_discovery")
        self.assertEqual(turn.plan.tasks[0].action, "create_local_fuzz_plan")
        self.assertTrue(turn.dispatched_results[0].success)
        self.assertEqual(turn.dispatched_results[0].data["permission_tier"], "T0")
        self.assertEqual(runtime.response_adapter._category_and_variables(turn)[0], "security.fuzz_plan.done")

    def test_cyber_defense_sweep_returns_findings_to_user(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("נלה תעשי הגנה")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "CyberDefenseSweep")
        self.assertEqual(turn.plan.tasks[0].target_agent, "cyber_defense")
        self.assertTrue(turn.dispatched_results[0].success)
        self.assertEqual(turn.dispatched_results[0].data["permission_tier"], "T0")
        self.assertIn("ממצאים", response)
        self.assertIn("הרשאות", response)
        self.assertIn("הצעד הבא", response)

    def test_natural_hebrew_security_check_runs_defense_agent(self) -> None:
        runtime, temp_dir = make_runtime()
        with temp_dir:
            turn = runtime.conversation.handle_text("תעשי בדיקה של אבטחה")
            response = runtime.response_adapter.render_turn(turn)

        self.assertEqual(turn.intent.action, "CyberDefenseSweep")
        self.assertEqual(turn.plan.tasks[0].target_agent, "cyber_defense")
        self.assertTrue(turn.dispatched_results[0].success)
        self.assertIn("ממצאים", response)
        self.assertNotIn("לא לגמרי הבנתי", response)


if __name__ == "__main__":
    unittest.main()
