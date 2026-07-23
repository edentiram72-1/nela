"""Language pack and personality profile loading."""

from __future__ import annotations

import json
from pathlib import Path

from language.models import LanguagePack, PersonalityProfile, PhraseEntry
from language.pack_format import language_file_entries
from language.validator import validate_pack

DEFAULT_LANGUAGE_PACK = Path(__file__).parent / "hebrew"
DEFAULT_PERSONALITY_DIR = Path(__file__).parent / "personality"


def load_language_pack(path: Path | str = DEFAULT_LANGUAGE_PACK) -> LanguagePack:
    pack_path = Path(path)
    report = validate_pack(pack_path)
    if not report.is_valid:
        messages = "; ".join(issue.message for issue in report.issues)
        raise ValueError(f"Invalid language pack: {messages}")

    manifest = json.loads((pack_path / "manifest.json").read_text(encoding="utf-8"))
    entries: list[PhraseEntry] = []
    for filename in manifest["files"]:
        raw = json.loads((pack_path / str(filename)).read_text(encoding="utf-8"))
        phrase_items = language_file_entries(raw)
        entries.extend(PhraseEntry.from_dict(item) for item in phrase_items)

    return LanguagePack(
        language=str(manifest["language"]),
        version=str(manifest.get("version", "1.0")),
        categories=tuple(str(item) for item in manifest.get("categories", ())),
        tones=tuple(str(item) for item in manifest.get("tones", ())),
        emotions=tuple(str(item) for item in manifest.get("emotions", ())),
        entries=tuple(entries),
        source=str(pack_path),
    )


def load_personality_profile(name: str = "default", directory: Path | str = DEFAULT_PERSONALITY_DIR) -> PersonalityProfile:
    path = Path(directory) / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return PersonalityProfile.from_dict(data)
