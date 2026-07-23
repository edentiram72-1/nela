# Untracked Duplicate Files Report

Generated: 2026-07-23

Scope: untracked files whose names contain duplicate suffixes such as ` 2`, ` 3`, `(2)`, or `(3)`.

No duplicate file was deleted, moved, renamed, staged, or committed during inspection.

## Summary

- Total duplicate-suffix untracked files: 94
- Identical to likely original: 91
- Different from likely original: 3
- Duplicate files with confirmed unique additions: 0
- Recommended action: clean up identical duplicates only after explicit user approval; review the 3 different duplicates before cleanup even though they appear to be older copies missing current tracked changes.

## Different Files

| File path | Likely original | Contents identical | Unique changes in duplicate | Recommended action |
|---|---|---:|---|---|
| `tests/test_intent_recognition 2.py` | `tests/test_intent_recognition.py` | No | No confirmed unique additions. Duplicate appears older and is missing the Hebrew open-application intent test now present in the tracked original. | Do not delete without user approval; safe cleanup candidate after confirming the older copy is not needed. |
| `tests/test_ui_state 2.py` | `tests/test_ui_state.py` | No | No confirmed unique additions. Duplicate appears older and is missing voice event bridge tests now present in the tracked original. | Do not delete without user approval; safe cleanup candidate after confirming the older copy is not needed. |
| `ui/events 2.py` | `ui/events.py` | No | No confirmed unique additions. Duplicate appears older and is missing voice event-to-eye-state handling now present in the tracked original. | Do not delete without user approval; safe cleanup candidate after confirming the older copy is not needed. |

## Identical Files

All files below are byte-for-byte identical to the likely original. They contain no unique changes. Recommended action for each: safe cleanup candidate after explicit user approval.

| File path | Likely original |
|---|---|
| `core/README 2.md` | `core/README.md` |
| `core/__init__ 2.py` | `core/__init__.py` |
| `core/app 2.py` | `core/app.py` |
| `core/config 2.py` | `core/config.py` |
| `core/events 2.py` | `core/events.py` |
| `core/logger 2.py` | `core/logger.py` |
| `core/startup 2.py` | `core/startup.py` |
| `core/startup 3.py` | `core/startup.py` |
| `design/nela_app_icon 2.svg` | `design/nela_app_icon.svg` |
| `design/nela_living_eye 2.html` | `design/nela_living_eye.html` |
| `design/nela_menubar_icon 2.svg` | `design/nela_menubar_icon.svg` |
| `docs/ai_inbox 2.md` | `docs/ai_inbox.md` |
| `docs/claude_review_findings 2.md` | `docs/claude_review_findings.md` |
| `docs/design_system 2.md` | `docs/design_system.md` |
| `docs/language_system 2.md` | `docs/language_system.md` |
| `docs/memory_model 2.md` | `docs/memory_model.md` |
| `language/__init__ 2.py` | `language/__init__.py` |
| `language/context 2.py` | `language/context.py` |
| `language/engine 2.py` | `language/engine.py` |
| `language/fallback 2.py` | `language/fallback.py` |
| `language/loader 2.py` | `language/loader.py` |
| `language/models 2.py` | `language/models.py` |
| `language/renderer 2.py` | `language/renderer.py` |
| `language/selector 2.py` | `language/selector.py` |
| `language/validator 2.py` | `language/validator.py` |
| `logs/.gitkeep 2` | `logs/.gitkeep` |
| `logs/.gitkeep 3` | `logs/.gitkeep` |
| `memory/README 2.md` | `memory/README.md` |
| `memory/__init__ 2.py` | `memory/__init__.py` |
| `memory/long_term 2.py` | `memory/long_term.py` |
| `memory/profile 2.py` | `memory/profile.py` |
| `memory/short_term 2.py` | `memory/short_term.py` |
| `memory/vector_store 2.py` | `memory/vector_store.py` |
| `plugins/.gitkeep 2` | `plugins/.gitkeep` |
| `scripts/__init__ 2.py` | `scripts/__init__.py` |
| `tests/__init__ 2.py` | `tests/__init__.py` |
| `tests/test_agent_contract 2.py` | `tests/test_agent_contract.py` |
| `tests/test_app_cli 2.py` | `tests/test_app_cli.py` |
| `tests/test_claude_agent 2.py` | `tests/test_claude_agent.py` |
| `tests/test_context_engine 2.py` | `tests/test_context_engine.py` |
| `tests/test_conversation_confirmations 2.py` | `tests/test_conversation_confirmations.py` |
| `tests/test_decision_engine 2.py` | `tests/test_decision_engine.py` |
| `tests/test_desktop_agent 2.py` | `tests/test_desktop_agent.py` |
| `tests/test_dispatcher 2.py` | `tests/test_dispatcher.py` |
| `tests/test_events 2.py` | `tests/test_events.py` |
| `tests/test_language_engine 2.py` | `tests/test_language_engine.py` |
| `tests/test_language_voice_integration 2.py` | `tests/test_language_voice_integration.py` |
| `tests/test_memory_manager 2.py` | `tests/test_memory_manager.py` |
| `tests/test_planner 2.py` | `tests/test_planner.py` |
| `tests/test_startup 2.py` | `tests/test_startup.py` |
| `tests/test_ui_app 2.py` | `tests/test_ui_app.py` |
| `tests/test_ui_router 2.py` | `tests/test_ui_router.py` |
| `tests/test_voice_agent 2.py` | `tests/test_voice_agent.py` |
| `ui/__init__ 2.py` | `ui/__init__.py` |
| `ui/animations 2.py` | `ui/animations.py` |
| `ui/app 2.py` | `ui/app.py` |
| `ui/router 2.py` | `ui/router.py` |
| `ui/state 2.py` | `ui/state.py` |
| `ui/theme 2.py` | `ui/theme.py` |
| `ui/window 2.py` | `ui/window.py` |
| `vision/README 2.md` | `vision/README.md` |
| `vision/README 3.md` | `vision/README.md` |
| `vision/__init__ 2.py` | `vision/__init__.py` |
| `vision/__init__ 3.py` | `vision/__init__.py` |
| `vision/screen_capture 2.py` | `vision/screen_capture.py` |
| `vision/screen_capture 3.py` | `vision/screen_capture.py` |
| `vision/screen_reader 2.py` | `vision/screen_reader.py` |
| `vision/screen_reader 3.py` | `vision/screen_reader.py` |
| `vision/ui_detector 2.py` | `vision/ui_detector.py` |
| `vision/ui_detector 3.py` | `vision/ui_detector.py` |
| `voice/README 2.md` | `voice/README.md` |
| `voice/README 3.md` | `voice/README.md` |
| `voice/__init__ 2.py` | `voice/__init__.py` |
| `voice/__init__ 3.py` | `voice/__init__.py` |
| `voice/events 2.py` | `voice/events.py` |
| `voice/microphone 2.py` | `voice/microphone.py` |
| `voice/microphone 3.py` | `voice/microphone.py` |
| `voice/playback 2.py` | `voice/playback.py` |
| `voice/providers/__init__ 2.py` | `voice/providers/__init__.py` |
| `voice/providers/base 2.py` | `voice/providers/base.py` |
| `voice/providers/factory 2.py` | `voice/providers/factory.py` |
| `voice/providers/macos 2.py` | `voice/providers/macos.py` |
| `voice/providers/mock 2.py` | `voice/providers/mock.py` |
| `voice/queue 2.py` | `voice/queue.py` |
| `voice/speech_to_text 2.py` | `voice/speech_to_text.py` |
| `voice/speech_to_text 3.py` | `voice/speech_to_text.py` |
| `voice/text_to_speech 2.py` | `voice/text_to_speech.py` |
| `voice/text_to_speech 3.py` | `voice/text_to_speech.py` |
| `voice/voice_profile 2.py` | `voice/voice_profile.py` |
| `voice/wake_word 2.py` | `voice/wake_word.py` |
| `voice/wake_word 3.py` | `voice/wake_word.py` |
