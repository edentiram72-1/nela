"""Public language engine API."""

from __future__ import annotations

from pathlib import Path

from language.context import LanguageRuntimeContext
from language.loader import DEFAULT_LANGUAGE_PACK, DEFAULT_PERSONALITY_DIR, load_language_pack, load_personality_profile
from language.models import LanguagePack, PersonalityProfile, PhraseEntry, ValidationReport
from language.renderer import missing_template_variables, render_template
from language.selector import PhraseSelector
from language.validator import validate_pack


class LanguageEngine:
    """Loads, validates, selects, and renders language-pack phrases."""

    def __init__(
        self,
        language_pack_path: Path | str = DEFAULT_LANGUAGE_PACK,
        personality_name: str = "default",
        personality_dir: Path | str = DEFAULT_PERSONALITY_DIR,
        selector: PhraseSelector | None = None,
    ) -> None:
        self.language_pack_path = Path(language_pack_path)
        self.personality_dir = Path(personality_dir)
        self.selector = selector or PhraseSelector()
        self.context = LanguageRuntimeContext()
        self.pack = load_language_pack(self.language_pack_path)
        self.personality = load_personality_profile(personality_name, self.personality_dir)

    def load_language_pack(self, path: Path | str) -> LanguagePack:
        self.language_pack_path = Path(path)
        self.pack = load_language_pack(self.language_pack_path)
        return self.pack

    def reload_language_pack(self) -> LanguagePack:
        self.pack = load_language_pack(self.language_pack_path)
        return self.pack

    def load_personality(self, name: str) -> PersonalityProfile:
        self.personality = load_personality_profile(name, self.personality_dir)
        return self.personality

    def select_phrase(
        self,
        category: str,
        tone: str | None = None,
        emotion: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> PhraseEntry:
        return self.selector.select(
            pack=self.pack,
            context=self.context,
            personality=self.personality,
            category=category,
            tone=tone,
            emotion=emotion,
            tags=tags,
        )

    def render_response(
        self,
        category: str,
        variables: dict[str, object] | None = None,
        tone: str | None = None,
        emotion: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> str:
        phrase = self.select_phrase(category=category, tone=tone, emotion=emotion, tags=tags)
        return render_template(phrase.text, variables or {})

    def missing_variables(self, phrase: PhraseEntry, variables: dict[str, object] | None = None) -> tuple[str, ...]:
        return missing_template_variables(phrase.text, variables or {})

    def validate_pack(self, path: Path | str | None = None) -> ValidationReport:
        return validate_pack(path or self.language_pack_path)

    def list_categories(self) -> tuple[str, ...]:
        return self.pack.categories

    def get_available_tones(self) -> tuple[str, ...]:
        return self.pack.tones

    def health_check(self) -> dict[str, object]:
        report = self.validate_pack()
        return {
            "ok": report.is_valid,
            "language": self.pack.language,
            "version": self.pack.version,
            "phrase_count": len(self.pack.entries),
            "personality": self.personality.name,
            "issues": [issue.message for issue in report.issues],
        }


class HebrewLanguageEngine(LanguageEngine):
    """Default Hebrew language engine for NELA."""
