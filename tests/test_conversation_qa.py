import os
import tempfile
import unittest
from pathlib import Path

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
            learned = runtime.conversation.handle_text("בוקר טוב")
            response = runtime.response_adapter.render_turn(learned)

        self.assertEqual(taught.intent.action, "TeachResponse")
        self.assertTrue(taught.dispatched_results[0].success)
        self.assertEqual(learned.intent.action, "Greeting")
        self.assertEqual(learned.intent.parameters["response_category"], "qa.learned")
        self.assertEqual(response, "בוקר אור")

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
