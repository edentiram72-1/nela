import json
import tempfile
import unittest
from pathlib import Path

from language.engine import HebrewLanguageEngine
from language.loader import DEFAULT_LANGUAGE_PACK, load_language_pack
from language.selector import PhraseSelector
from language.validator import validate_pack


class LanguageEngineTests(unittest.TestCase):
    def test_loads_hebrew_language_pack(self) -> None:
        pack = load_language_pack(DEFAULT_LANGUAGE_PACK)

        self.assertEqual(pack.language, "he")
        self.assertIn("greeting.day", pack.categories)
        self.assertGreater(len(pack.entries), 0)

    def test_validation_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "manifest.json").write_text(
                json.dumps(
                    {
                        "language": "he",
                        "version": "1.0",
                        "files": ["phrases.json"],
                        "categories": ["success.general"],
                        "tones": ["warm"],
                        "emotions": ["neutral"],
                    }
                ),
                encoding="utf-8",
            )
            phrase = {
                "id": "dup",
                "text": "בוצע.",
                "category": "success.general",
                "language": "he",
                "tone": ["warm"],
                "emotion": "neutral",
                "requires": [],
            }
            (root / "phrases.json").write_text(json.dumps({"phrases": [phrase, phrase]}), encoding="utf-8")

            report = validate_pack(root)

        self.assertFalse(report.is_valid)
        self.assertIn("duplicate_id", {issue.code for issue in report.issues})

    def test_rendering_keeps_missing_variables_visible(self) -> None:
        engine = HebrewLanguageEngine(selector=PhraseSelector(seed=1))

        text = engine.render_response("desktop.launch", {})

        self.assertIn("{application}", text)

    def test_category_fallback_is_safe_hebrew(self) -> None:
        engine = HebrewLanguageEngine(selector=PhraseSelector(seed=1))

        text = engine.render_response("missing.category")

        self.assertTrue(text)
        self.assertIn("אני", text)

    def test_selector_avoids_immediate_repetition(self) -> None:
        engine = HebrewLanguageEngine(selector=PhraseSelector(seed=7))

        first = engine.select_phrase("success.short")
        second = engine.select_phrase("success.short")

        self.assertNotEqual(first.id, second.id)

    def test_personality_selection_prefers_requested_tone(self) -> None:
        engine = HebrewLanguageEngine(selector=PhraseSelector(seed=3))

        phrase = engine.select_phrase("thinking")

        self.assertEqual(phrase.eye_state, "thinking")

    def test_hebrew_output_for_known_response(self) -> None:
        engine = HebrewLanguageEngine(selector=PhraseSelector(seed=1))

        text = engine.render_response("media.play", {"resource": "Night"})

        self.assertIn("Night", text)
        self.assertRegex(text, r"[\u0590-\u05ff]")


if __name__ == "__main__":
    unittest.main()
