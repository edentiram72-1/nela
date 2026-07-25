import unittest

from brain.intent_router import IntentRouter, Priority


class IntentRecognitionTests(unittest.TestCase):
    def test_recognizes_structured_music_intent(self) -> None:
        intent = IntentRouter().classify("Open Spotify and play my Night playlist now")

        self.assertEqual(intent.action, "PlayMedia")
        self.assertEqual(intent.application, "Spotify")
        self.assertEqual(intent.resource, "Night")
        self.assertEqual(intent.priority, Priority.HIGH)
        self.assertEqual(intent.target_agent, "spotify")

    def test_low_confidence_unknown_request_requires_more_context_later(self) -> None:
        intent = IntentRouter().classify("blue umbrella")

        self.assertEqual(intent.action, "GeneralRequest")
        self.assertLess(intent.confidence, 0.5)

    def test_does_not_match_keywords_inside_other_words(self) -> None:
        intent = IntentRouter().classify("Open display settings")

        self.assertEqual(intent.action, "OpenApplication")
        self.assertEqual(intent.application, "Display Settings")

    def test_recognizes_close_application_intent(self) -> None:
        intent = IntentRouter().classify("NELA, close Finder")

        self.assertEqual(intent.action, "CloseApplication")
        self.assertEqual(intent.application, "Finder")
        self.assertTrue(intent.requires_confirmation)

    def test_recognizes_switch_application_intent(self) -> None:
        intent = IntentRouter().classify("switch to Spotify")

        self.assertEqual(intent.action, "SwitchApplication")
        self.assertEqual(intent.application, "Spotify")

    def test_recognizes_hebrew_open_application_intent(self) -> None:
        intent = IntentRouter().classify("נלה, תפתחי את Spotify")

        self.assertEqual(intent.action, "OpenApplication")
        self.assertEqual(intent.application, "Spotify")
        self.assertEqual(intent.target_agent, "spotify")

    def test_resolves_hebrew_application_alias(self) -> None:
        intent = IntentRouter().classify("נלה, תפתחי את ספוטיפיי")

        self.assertEqual(intent.action, "OpenApplication")
        self.assertEqual(intent.application, "Spotify")

    def test_hebrew_identity_question_is_conversational(self) -> None:
        intent = IntentRouter().classify("מי את?")

        self.assertEqual(intent.action, "IdentityQuestion")
        self.assertGreaterEqual(intent.confidence, 0.5)

    def test_hebrew_capabilities_question_is_conversational(self) -> None:
        intent = IntentRouter().classify("מה את יודעת לעשות?")

        self.assertEqual(intent.action, "CapabilitiesQuestion")

    def test_hebrew_agent_status_question_is_conversational(self) -> None:
        intent = IntentRouter().classify("איזה סוכנים מחוברים?")

        self.assertEqual(intent.action, "AgentStatusQuestion")

    def test_unknown_question_gets_general_question_intent(self) -> None:
        intent = IntentRouter().classify("מה קורה בירח?")

        self.assertEqual(intent.action, "GeneralQuestion")
        self.assertGreaterEqual(intent.confidence, 0.5)

    def test_recognizes_hebrew_teach_response_intent(self) -> None:
        intent = IntentRouter().classify("נלה תלמדי שכשאני אומר בוקר טוב תעני בוקר אור")

        self.assertEqual(intent.action, "TeachResponse")
        self.assertEqual(intent.target_agent, "learning")
        self.assertEqual(intent.parameters["trigger"], "בוקר טוב")
        self.assertEqual(intent.parameters["response"], "בוקר אור")

    def test_recognizes_defensive_security_review_intent(self) -> None:
        intent = IntentRouter().classify("נלה תבדקי את הקוד לאבטחה")

        self.assertEqual(intent.action, "SecurityReview")
        self.assertEqual(intent.target_agent, "secure_code_reviewer")

    def test_recognizes_security_capabilities_question(self) -> None:
        intent = IntentRouter().classify("מה את יודעת בסייבר?")

        self.assertEqual(intent.action, "SecurityCapabilitiesQuestion")

    def test_recognizes_local_lab_target_registration(self) -> None:
        intent = IntentRouter().classify("תרשמי יעד מעבדה http://localhost:3000")

        self.assertEqual(intent.action, "CyberLabRegisterTarget")
        self.assertEqual(intent.target_agent, "authorized_lab")
        self.assertEqual(intent.resource, "http://localhost:3000")

    def test_recognizes_local_fuzz_plan(self) -> None:
        intent = IntentRouter().classify("תכיני תוכנית fuzz מקומית לפרסר")

        self.assertEqual(intent.action, "LocalFuzzPlan")
        self.assertEqual(intent.target_agent, "anomaly_discovery")


if __name__ == "__main__":
    unittest.main()
