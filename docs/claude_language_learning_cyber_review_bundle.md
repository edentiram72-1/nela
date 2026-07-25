# NELA OS Claude Review Bundle

This bundle is prepared for Claude review.
It does not create any direct connection to Claude.

## Review Focus

Focused review for branch `codex/nela-language-learning-cyber`.

Implementation commit under review: `efb73ca`.

If this bundle is committed after generation, the branch head may be one commit
newer, containing only this regenerated review bundle.

Claude specifically requested code evidence for:
1. Hebrew conversation quality.
2. `CyberDefenseAgent` defensive-only behavior.
3. Findings usefulness and safety.
4. Brain-to-Agent routing and dispatcher authorization.
5. Living Eye / response-state wiring.
6. Merge risks.

Acceptance bar for cyber review:
- Capabilities must be passive T0/T1 or lab-only T3.
- No external IP/hostname/URL target may be accepted outside authorized local/lab scope.
- Ownership/scope must be structural, not just user claim.
- Output must be findings/remediations/safe references, not runnable exploit code.
- Educational content must avoid working attack tooling.
- Refusals and actions must remain auditable.

Local validation before bundle regeneration:
- `python3 -m scripts.validate_language_packs` passed.
- `python3 -m unittest discover -s tests` passed: 151 tests.
- `python3 -m ui.app --headless-smoke` passed.
- `python3 -m core.app --once "נלה תעשי הגנה"` routed to `cyber_defense.defense_posture_check` and returned 4 Hebrew defensive findings.

Important: no direct Claude connection exists; GitHub and this pasted/attached bundle are the collaboration layer.


## Claude Instructions

You are Claude reviewing NELA OS.

Responsibilities:
- Review architecture.
- Review documentation.
- Find edge cases.
- Improve UX ideas.
- Suggest risk and performance improvements.

Rules:
- Do not rewrite completed modules without justification.
- Do not ask for direct access to local files.
- Treat GitHub, pasted bundles, and pull requests as the collaboration layer.
- Focus on architecture, documentation, edge cases, security, maintainability, and long-term extensibility.
- Return findings with severity, affected files, reasoning, and suggested next steps.

## Repository Metadata

- Generated at: 2026-07-25T20:08:47.086548+00:00
- Branch: codex/nela-language-learning-cyber
- Commit: efb73ca
- Working tree: dirty

## Requested Review Output

Please return:

- Critical architecture risks.
- Missing abstractions or over-coupling.
- Event model gaps.
- Memory model gaps.
- Agent lifecycle risks.
- Plugin readiness gaps.
- Security and permission concerns.
- Documentation improvements.
- Recommended next tasks in priority order.

## Included Files

### `docs/ai_handoff.md`

```markdown
# AI Handoff

This file is the communication point between AI assistants working on NELA OS.

Every significant change must update this file before handoff.

## Current Project Status

Phase 1 Brain foundation, Integration Sprint 1, the Claude language/personality drop, the multi-agent architecture specifications, Sprint 2 Permission Engine implementation, and Claude Sprint 2 safety findings are consolidated into `develop`.

The Brain now supports text and voice-transcript input, structured intent recognition, decision making, planning, context tracking, short-term and long-term memory orchestration, and Agent dispatch through a shared event bus.

The Brain does not perform external actions directly. It delegates Tasks to registered Agents. Most external integrations remain safe placeholders. Desktop Agent V1 is the first real execution Agent and is limited to safe macOS application lifecycle management.

The following branches are included in `develop`:

- `feature/NELA-0002-confirmation-deadlock`
- `feature/NELA-0005-desktop-agent-v1`
- `feature/NELA-0006-ui-foundation`
- `feature/NELA-0007-ai-inbox`
- `feature/NELA-0011-visual-identity`
- `feature/NELA-0012-claude-review-fixes`
- `feature/NELA-language-voice-foundation`

Integration Sprint 1 created backup branch `backup/develop-before-integration-20260723-050921`, verified branch inclusion, added Hebrew smoke-intent compatibility, mapped Voice speech events into UI Eye states, and generated `docs/integration_sprint_1_merge_report.md`.

Repository stabilization documented untracked duplicate-suffix files in `docs/untracked_duplicate_files_report.md`. The duplicate files were inspected only and left untouched. `develop` and backup branch `backup/develop-before-integration-20260723-050921` were pushed to GitHub through the configured SSH remote; `main` was not changed during this stabilization task.

On 2026-07-24, `nela-language-drop-final.zip` was integrated into the language foundation. Claude's Hebrew personality documents, tone rules, conversation rules, pack schema, 117-phrase Hebrew pack, and 3 personality presets are now stored in the repository. The Language Engine supports Claude compatibility metadata while keeping Brain code semantic and phrase-free.

On 2026-07-24, Claude's `nela-architecture.zip` deliverable was staged as repository documentation on `feature/NELA-architecture-specs`. This is specification-only work: no Coding Agent, Cyber Agent, Research Agent, advanced orchestration runtime, or new side-effecting capability was implemented.

On 2026-07-24, Sprint 2 implemented and hardened the Permission Engine on `feature/NELA-safety-spine-routing`. This is infrastructure-only work: no unrestricted Coding Agent, Cyber Agent, Browser/Vision/Cyber feature expansion, or UI redesign was added.

On 2026-07-25, Sprint 2 was prepared for draft PR review. `docs/sprint2_pr_summary.md`,
`docs/sprint2_pr_body.md`, `docs/manual_pr_instructions.md`,
`docs/claude_sprint2_review_bundle.md`, `docs/claude_sprint2_review_prompt.md`,
and `docs/safety_spine_sprint_report.md` were added. Draft PR #2 was opened from
`feature/NELA-safety-spine-routing` to `develop`:
`https://github.com/edentiram72-1/nela/pull/2`.

On 2026-07-25, Claude's K1/R1 follow-up review on `codex/multi-agent-foundation-safety`
confirmed R1 Agent Registry overwrite protection as PASS and subprocess isolation
as PASS, but required one remaining K1 fix: kill switch termination of already
running isolated work. Commit `1ebd6023ecb498b99eac0af5073a827a92442757` wires the
kill switch to live isolated runners, adds `ProcessOutcome.TERMINATED`, and adds
a regression test proving an in-flight T2 isolated task is terminated when the
kill switch fires. Follow-up commit `64dc0e0909ca553152ffa3871cc977d41550432d`
blocks retries after kill-switch termination so a second attempt cannot bypass
the emergency state. Follow-up commit `9262ce0a58f93d1800ff90684dbf0c1ab8478521`
adds a pre-attempt emergency stop guard so kill switch or lock mode activation
after authorization still prevents execution before the next attempt starts.
Final commit `667c34cd07e2bc5722aaec35d2a830c95141ec52` adds a second guard after
isolated runner registration and before child process start to close the
remaining check-then-act micro-window.

On 2026-07-25, `codex/multi-agent-foundation-safety` was merged into `develop`
with merge commit `8baae97dd2e39627d4555cd6abf1117e428a5cb9`. Claude's final
review verdict for K1/R1 remained APPROVE for the branch head. Post-merge
validation passed on `develop`: 124 unit tests, Hebrew language pack validation,
and UI headless smoke. A Hebrew prototype command also routed through the Brain:
`נלה, תפתחי את Spotify` produced `Intent: OpenApplication`, `Decision: delegate`,
and Hebrew response `Spotify — פותחת.` using safe no-dispatch mode.

On 2026-07-25, `codex/nela-conversation-agent-qa` started the first safe
conversation and Agent-awareness layer. The runtime now registers first-wave
specialist Agents from `agents.factory` without replacing existing live Agents,
and the Brain has a modular `KnowledgeEngine` for safe Hebrew Q&A about NELA's
identity, current capabilities, connected Agents, status, greetings, thanks, and
unknown open questions. This does not enable real side effects for Browser,
Terminal, Coding, Cyber, or communication Agents.

On 2026-07-25, `codex/nela-language-learning-cyber` added runtime language
learning and defensive cyber routing. NELA can now learn user-provided
trigger/response pairs through `LearningAgent` and answer matching future turns
through `KnowledgeEngine` and `qa.learned`. Security routing now recognizes
defensive security review, threat-model scaffolding, cyber lab status, local lab
target registration, local-only fuzz planning, and security capability
questions. Active cyber execution remains blocked behind the existing
authorization, scoped-session, confirmation, audit, isolation, and kill-switch
model.

On 2026-07-25, the same branch improved first-contact conversation behavior.
Short greetings now receive warmer Hebrew replies, `מה מצב` is treated as a
natural assistant-status question instead of technical Agent status, `מה את
יודעת על סייבר` routes to defensive cyber capabilities, and `תלמדי <topic>`
routes to `LearningAgent.recommend_learning_plan` with a Hebrew response. Generic
clarification prompts were changed from English to Hebrew.

On 2026-07-25, `CyberDefenseAgent` was added as the first central defensive
cyber posture Agent. `CyberDefenseSweep` routes requests such as `נלה תעשי
הגנה`, `תתחילי להגן`, and `תבני מערך סייבר` to
`cyber_defense.defense_posture_check`. Security responses now surface findings
to the user in Hebrew, including severity, recommendation, and next steps. This
remains T0 passive/defensive posture work and does not add external targeting or
offensive capability.

On 2026-07-25, the same branch broadened natural Hebrew routing for immediate
defensive checks. Requests such as `תעשי בדיקה של אבטחה`, `בדיקה אבטחתית`, and
`בדיקת סייבר` now route directly to `CyberDefenseSweep` instead of falling back
to clarification. Hebrew clarification templates were also cleaned up so
unknown requests no longer duplicate question marks or wrap full questions in
awkward phrasing.

The same branch now includes a token-authenticated local browser prototype for
Claude's Living Eye. `ui/web.py` serves `design/nela_living_eye.html` on
`127.0.0.1` only, injects a per-launch token, verifies the expected same origin,
and routes Hebrew chat messages through the existing Brain. This is an interim
visible demo host, not the final production WebView shell.

The consolidation includes:

- Confirmation answer routing before intent classification, including affirmative replies, negative replies, unclear reply handling, and TTL expiry.
- Safe mock Agents for MVP dispatch.
- Dispatcher timeout/retry hardening for the current synchronous execution model.
- Deterministic keyword/phrase intent matching, avoiding substring false positives.
- Desktop Agent V1 for known macOS app lookup, running detection, launch/focus, foreground switching, graceful close, structured results, and health reporting.
- A modular UI foundation with state management, event bridge, router, theme tokens, animation hooks, and a temporary Tkinter shell.
- `docs/ai_inbox.md` and a GitHub Issue template for AI collaboration tasks.
- Claude's Living Eye visual identity artifacts under `design/` and the authoritative design-system document under `docs/design_system.md`.
- Claude review fixes for Desktop timeout handling, Dispatcher exception isolation, Desktop `wait_until_ready`, `CloseApplication` confirmation, WebView-compatible UI host decision, and Inbox/Handoff cleanup.
- A standalone Hebrew Language Engine and Voice Agent Foundation. Phrase selection lives in `language/`, final response rendering lives in `core/response.py`, and speech playback lives in the `voice/` provider layer plus `agents/voice/agent.py`.
- Claude language system integration: `pack/categories/variants` pack shape, `speech_text`, `eye_state`, `gender_tier`, `min_stage`, session use counts, gender tag rendering, and personality `preset/params/pack_overrides` compatibility.
- Multi-agent architecture specifications: shared T0-T4 permission model, runtime lifecycle architecture, Coding Agent spec, defensive Cyber Agent spec, multi-agent orchestration spec, and AI system roadmap.
- Sprint 2 Permission Engine: T0-T4 tiers, Capability Registry, Agent manifests, authentication checks, confirmation gate, scoped sessions, in-memory audit log, kill switch, lock mode, permission events, UI state mapping for permission events, and Dispatcher integration before `agent.execute()`.
- Claude Sprint 2 findings: secure local bridge foundation, subprocess isolation foundation, symlink-aware scope validation, exact confirmation binding, insert-only Agent registration, tamper-evident audit hash chain, and authorization-before-final-routing foundation.
- Mechanical safety-spine verification criteria are documented in `docs/safety_spine_verification_criteria.md`.
- Conversation QA foundation: `brain/qa.py`, conversational intent routing, QA
  response categories in the Hebrew language pack, and startup registration for
  non-conflicting specialist Agents.

Claude collaboration is repository-based only. There is no direct Claude connection. Use direct GitHub `blob/` links, `docs/ai_inbox.md`, or regenerate a review bundle with `python3 -m scripts.export_claude_review_bundle`.

GitHub is the shared collaboration layer. The public repository is `https://github.com/edentiram72-1/nela`.

Claude also referenced a Memory subsystem deliverable, `nela-memory-subsystem.zip`, but that archive was not present in `/Users/edentiram/Downloads`, `/Users/edentiram/Downloads/files`, or the current attachment directory. Memory subsystem integration is blocked until that zip is provided.

## Current Milestone

**Post-Sprint 2: Runtime Language Learning + Defensive Security Routing + Secure Visual Prototype**

## Active Branch

`codex/nela-language-learning-cyber`

## Recently Modified Files

- `README.md`
- `README.he.md`
- `.gitignore`
- `.env.example`
- `LICENSE`
- `core/app.py`
- `core/config.py`
- `core/events.py`
- `core/logger.py`
- `core/response.py`
- `core/startup.py`
- `language/*`
- `language/hebrew/*`
- `language/personality/*`
- `brain/conversation.py`
- `brain/context.py`
- `brain/decision.py`
- `brain/dispatcher.py`
- `brain/intent_router.py`
- `brain/applications.py`
- `brain/memory_manager.py`
- `brain/planner.py`
- `brain/qa.py`
- `language/learning_store.py`
- `agents/learning/agent.py`
- `tests/test_conversation_qa.py`
- `tests/test_ui_web.py`
- `permissions/__init__.py`
- `permissions/audit.py`
- `permissions/engine.py`
- `permissions/models.py`
- `permissions/registry.py`
- `permissions/confirmation.py`
- `permissions/scope.py`
- `docs/permission_engine.md`
- `docs/agent_registry.md`
- `docs/audit_and_recovery.md`
- `docs/capability_routing.md`
- `docs/process_isolation.md`
- `docs/secure_ui_bridge.md`
- `docs/sprint2_claude_findings_status.md`
- `docs/sprint2_pr_summary.md`
- `docs/sprint2_pr_body.md`
- `docs/manual_pr_instructions.md`
- `docs/claude_sprint2_review_bundle.md`
- `docs/claude_sprint2_review_prompt.md`
- `docs/claude_k1_r1_review_bundle.md`
- `docs/claude_k1_r1_review_prompt.md`
- `docs/claude_k1_final_review_bundle.md`
- `docs/claude_k1_final_review_prompt.md`
- `docs/safety_spine_sprint_report.md`
- `brain/reasoning.py`
- `agents/base.py`
- `agents/mock.py`
- `agents/registry.py`
- `agents/process_isolation.py`
- `agents/automation/agent.py`
- `agents/browser/agent.py`
- `agents/calendar/agent.py`
- `agents/claude/agent.py`
- `agents/codex/agent.py`
- `agents/desktop/agent.py`
- `agents/files/agent.py`
- `agents/github/agent.py`
- `agents/gmail/agent.py`
- `agents/memory/agent.py`
- `agents/memory/__init__.py`
- `agents/spotify/agent.py`
- `agents/terminal/agent.py`
- `agents/voice/agent.py`
- `agents/voice/__init__.py`
- `agents/vision/agent.py`
- `scripts/export_claude_review_bundle.py`
- `scripts/validate_language_packs.py`
- `docs/ai_handoff.md`
- `docs/ai_inbox.md`
- `docs/language_system.md`
- `docs/voice_architecture.md`
- `docs/integration_sprint_1_merge_report.md`
- `docs/untracked_duplicate_files_report.md`
- `docs/personality_bible.md`
- `docs/hebrew_language_guide.md`
- `docs/tone_of_voice.md`
- `docs/conversation_rules.md`
- `docs/language_compat_report.md`
- `docs/claude_handoff_2026-07-24.md`
- `docs/releases/v0.1-alpha.md`
- `docs/permission_model.md`
- `docs/nela_runtime_architecture.md`
- `docs/coding_agent_spec.md`
- `docs/cyber_agent_spec.md`
- `docs/multi_agent_orchestration.md`
- `docs/ai_system_roadmap.md`
- `docs/design_system.md`
- `docs/claude_review_bundle.md` generated locally for Claude review; ignored by Git to reduce merge conflicts.
- `memory/short_term.py`
- `memory/long_term.py`
- `memory/vector_store.py`
- `memory/profile.py`
- `voice/*`
- `voice/providers/*`
- `vision/*`
- `docs/architecture.md`
- `docs/api.md`
- `docs/coding_rules.md`
- `docs/claude_review_findings.md`
- `docs/decisions.md`
- `docs/memory_model.md`
- `docs/roadmap.md`
- `brain/README.md`
- `core/README.md`
- `agents/README.md`
- `memory/README.md`
- `voice/README.md`
- `vision/README.md`
- `tests/*`
- `tests/test_conversation_confirmations.py`
- `tests/test_desktop_agent.py`
- `tests/test_dispatcher.py`
- `tests/test_permission_engine.py`
- `tests/test_audit_log.py`
- `tests/test_process_isolation.py`
- `tests/test_secure_bridge.py`
- `tests/test_intent_recognition.py`
- `tests/test_planner.py`
- `ui/app.py`
- `ui/web.py`
- `ui/window.py`
- `ui/router.py`
- `ui/state.py`
- `ui/events.py`
- `ui/theme.py`
- `ui/animations.py`
- `ui/state.py`
- `ui/window.py`
- `ui/components/*`
- `ui/chat/*`
- `ui/sidebar/*`
- `ui/status/*`
- `ui/voice/*`
- `ui/eye/*`
- `ui/settings/*`
- `ui/assets/.gitkeep`
- `tests/test_ui_app.py`
- `tests/test_ui_router.py`
- `tests/test_ui_state.py`
- `tests/test_language_engine.py`
- `tests/test_voice_agent.py`
- `tests/test_language_voice_integration.py`
- `language/pack_schema.md`
- `language/pack_format.py`
- `tests/test_intent_recognition.py`
- `tests/test_ui_state.py`
- `.github/ISSUE_TEMPLATE/ai_collaboration_inbox.md`
- `design/nela_living_eye.html`
- `design/nela_app_icon.svg`
- `design/nela_menubar_icon.svg`

## Pending Tasks

- Do not merge into `main` until the user explicitly approves a release step.
- Tag a stable release only after the user explicitly approves a release step.
- Provide `nela-memory-subsystem.zip` so a dedicated memory subsystem branch can be created and tested separately.
- Use `docs/ai_inbox.md` as the shared queue for Claude, Codex, and ChatGPT.
- Treat Phase A Safety Spine as the next implementation gate before any advanced Agents.
- Continue `NELA-0004-task-idempotency` before enabling real side effects.
- Keep Browser Agent, Terminal Agent, Files Agent, Coding Agent, Cyber Agent, and communication Agents without real side effects until the remaining safety spine items are complete.
- Continue the remaining hardening around the Permission Engine: durable audit storage, richer scope validation, rollback handling, and in-flight cancellation.
- Send consolidated `develop` direct blob links or a regenerated bundle to Claude if an additional post-merge review is requested.
- Continue `NELA-0007-event-bus-hardening` with subscriber isolation, bounded history, and trace/correlation conventions.
- Continue `NELA-0008-capability-registry` so Planner/Dispatcher can reason about Agent capabilities and availability.
- Continue `NELA-0009-plan-executor` before relying on parallel, conditional, cancellable, or async orchestration semantics.
- Add `NELA-0016-audit-log-and-kill-switch` and `NELA-0017-agent-runtime-lifecycle` from `docs/ai_inbox.md`.
- Convert accepted Claude review findings from `docs/claude_review_findings.md` into tracked GitHub issues or roadmap entries.
- Continue interactive NELA sessions through `python3 -m core.app`.
- Expand the QA layer with project-aware answers after the memory subsystem is
  durable.
- Add safe user-facing descriptions for each specialist Agent before exposing
  them as selectable actions in the UI.
- Continue desktop UI shell checks with `python3 -m ui.app` on a machine with a graphical session.
- Send consolidated `develop` or `main` direct blob links to Claude for release verification.
- Send `docs/claude_language_learning_cyber_review_bundle.md` to Claude for the
  next focused review of the current branch.
- Ask Claude to review `docs/claude_handoff_2026-07-24.md`, `docs/personality_bible.md`, `docs/hebrew_language_guide.md`, `docs/tone_of_voice.md`, `docs/conversation_rules.md`, `language/pack_schema.md`, and `language/hebrew/`.
- Choose and implement a WebView-compatible host for the Living Eye.
- Add a durable persistence backend for long-term memory.
- Add a real plugin loader for `plugins/`.
- Add true concurrent execution for `TaskMode.PARALLEL`.
- Add condition evaluation for `TaskMode.CONDITIONAL`.
- Ask Claude to replace or expand the seed Hebrew language pack and personality profiles. Codex should not invent NELA's final personality.

## Known Issues

- Desktop Agent V1 performs real macOS application lifecycle actions for supported applications only. Other Agents remain safe mock placeholders.
- Live validation opened/foregrounded Finder only. Do not live-test close commands on user applications unless the user explicitly approves the target app.
- UI foundation intentionally has no Claude visual design yet. Eye, theme, animation, and component APIs expose states and tokens so Claude assets can be dropped in later without changing Brain architecture.
- Living Eye artifacts now run through a token-authenticated local browser
  prototype, but the production desktop shell still needs a future
  WebView-compatible host decision, such as WebView, Electron, or Tauri.
- `DEC-0007` accepts that the production visual shell should use a WebView-compatible host. Tkinter remains temporary infrastructure only.
- Memory subsystem integration is blocked because `nela-memory-subsystem.zip` was not provided with the current files.
- The AI Inbox is repository-based only. It does not connect directly to Claude, Codex, or ChatGPT.
- Intent recognition is deterministic and rule-based; no LLM or external NLP provider is connected.
- Event bus is synchronous and in-process only.
- Long-term memory is in-memory only and does not persist after restart.
- T2/T3 isolated Agent work can now be terminated by the kill switch through the isolated runner supervisor. Non-isolated synchronous Agent execution is still not interruptible mid-call.
- GitHub Pull Request creation through the Codex GitHub connector returned `403 Resource not accessible by integration`; use GitHub web UI or install/authenticate GitHub CLI if a PR must be opened from the local machine.
- `docs/claude_review_bundle.md` is generated from the current branch and should be regenerated after meaningful architecture or code changes.
- Claude review found several hardening gaps to address before real agents are trusted: task idempotency, event bus subscriber isolation, permission policy, capability registry clarity, and future confidence scoring for intent matching.
- `Remember` requests create a Plan targeting the registered mock `memory` Agent while durable memory also updates through `MemoryManager`; this dual path should be simplified before durable persistence work.
- README architecture diagrams do not yet show the Decision Engine and Dispatcher explicitly.
- Hebrew Language Engine and Voice Agent Foundation are still foundation-stage, but the Hebrew pack is now Claude's authoritative content drop rather than the earlier Codex seed pack.
- Voice defaults to silent mode, so response-to-voice delegation is exercised without audio playback unless explicitly enabled.
- The macOS `say` provider is the local MVP provider and treats provider submission as completion. It does not provide portable pause/resume.
- Integration Sprint 1 found and fixed two compatibility gaps: Hebrew open-app smoke intent recognition, and Voice task completion overriding `SpeechCompleted -> IDLE`.
- GitHub CLI (`gh`) is not installed in the current shell, and the Codex GitHub connector returned `403 Resource not accessible by integration` when creating a draft PR. Draft Pull Request creation must happen through GitHub web UI or after installing/authenticating `gh`.
- 94 untracked duplicate-suffix files exist locally and are documented in `docs/untracked_duplicate_files_report.md`; they were not staged or modified.
- The current Language Engine supports Claude metadata needed for loading and rendering, but the full anti-repetition, humor budget, time-of-day, relationship-stage memory wiring, and phrase event observability from `language/pack_schema.md` are not fully implemented yet.
- `docs/permission_model.md`, `docs/nela_runtime_architecture.md`, `docs/coding_agent_spec.md`, `docs/cyber_agent_spec.md`, `docs/multi_agent_orchestration.md`, and `docs/ai_system_roadmap.md` are specifications only. Their runtime systems are not implemented yet.
- Cybersecurity capabilities must remain blocked until the permission model, capability registry, audit logging, kill switch, and isolated lab architecture exist.
- Sprint 2 Permission Engine exists and Claude Sprint 2 blocking findings have foundation implementations, but Cybersecurity capabilities must still remain blocked until isolated lab architecture, durable audit storage, task idempotency, and production event-bus hardening are complete.
- Terminal and Coding manifests declare future capabilities for review only. Side-effecting terminal execution and coding write/commit capabilities are disabled.
- The new conversation QA layer is deterministic and local. It is not yet a
  general LLM-backed knowledge system and should answer unknown open questions
  honestly instead of pretending to know.

## Validation

Latest validation on `codex/nela-language-learning-cyber`:

```text
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
python3 -m core.app --once "מי את?" --no-dispatch
python3 -m compileall brain core agents language ui tests
```

Result: 144 tests passed; language pack validation passed; headless UI
bootstrap succeeded; Hebrew identity QA returned a Hebrew response through the
Brain; compileall completed successfully.

Latest conversation QA validation on `codex/nela-conversation-agent-qa`:

```text
python3 -m unittest discover -s tests
python3 -m scripts.validate_language_packs
python3 -m ui.app --headless-smoke
python3 -m compileall brain core agents language tests ui
python3 -m core.app --once "מי את?" --no-dispatch
python3 -m core.app --once "מה את יודעת לעשות?" --no-dispatch
python3 -m core.app --once "מה מצב?" --no-dispatch
python3 -m core.app --once "מה קורה בירח?" --no-dispatch
```

Result: 132 tests passed; language pack validation passed; headless UI bootstrap
succeeded; conversational Hebrew questions now return Hebrew answers without
creating Agent execution plans.

Latest post-merge validation on `develop`:

```text
python3 -m unittest discover -s tests
python3 -m scripts.validate_language_packs
python3 -m ui.app --headless-smoke
python3 -m core.app --once "נלה, תפתחי את Spotify" --no-dispatch
```

Result: 124 tests passed; language pack validation passed; headless UI bootstrap
succeeded; Hebrew no-dispatch prototype produced `Intent: OpenApplication`,
`Decision: delegate`, one semantic launch task for Spotify, and response
`Spotify — פותחת.` The desktop UI shell was also launched with `python3 -m ui.app`
and remained running in the local graphical session.

Latest Sprint 2 validation on `feature/NELA-safety-spine-routing`:

```text
python3 -m unittest discover -s tests
python3 -m scripts.validate_language_packs
python3 -m ui.app --headless-smoke
python3 -m core.app --once "נלה, תפתחי את Spotify" --no-dispatch
```

Result: 100 tests passed; language pack validation passed; headless UI bootstrap succeeded; Hebrew no-dispatch smoke produced `Intent: OpenApplication` and one semantic launch task.

Latest K1 final validation on `codex/multi-agent-foundation-safety`:

```text
python3 -m unittest discover -s tests
python3 -m scripts.validate_language_packs
python3 -m ui.app --headless-smoke
```

Result: 124 tests passed; language pack validation passed; headless UI bootstrap succeeded. The new regression tests verify that `activate_kill_switch()` terminates an in-flight isolated T2 task, reports `terminated_processes=1`, blocks retries after the kill switch is active, blocks the post-authorization/pre-attempt race, and blocks the runner-registration/pre-process-start race.

Additional syntax validation:

```text
python3 -m compileall permissions brain/dispatcher.py brain/planner.py core/events.py ui/events.py tests/test_permission_engine.py tests/test_dispatcher.py tests/test_conversation_confirmations.py
```

Result: completed successfully.

Latest consolidation validation on `develop`:

```text
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
python3 -m scripts.validate_language_packs
python3 -m core.app --once "נלה, תפתחי את Spotify"
```

Result: 66 tests passed; headless UI bootstrap succeeded; Hebrew language pack validation passed. This branch is specification-only and does not intentionally change runtime behavior.

Latest Integration Sprint 1 smoke:

```text
Input: נלה, תפתחי את Spotify
intent=OpenApplication
application=Spotify
plan_tasks=1
response=הפעלתי את Spotify.
ui_displayed=True
voice_spoken=True
eye_log=idle>listening>thinking>executing>success>executing>speaking>idle
eye_final=idle
```

Integration validation history:

- Baseline `origin/develop` after PR #1: 18 tests passed.
- After merging `feature/NELA-0002-confirmation-deadlock`: 27 tests passed.
- After merging `feature/NELA-0005-desktop-agent-v1`: 38 tests passed.
- After merging `feature/NELA-0006-ui-foundation`: 44 tests passed; headless UI bootstrap succeeded.
- After merging `feature/NELA-0007-ai-inbox`: 44 tests passed; headless UI bootstrap succeeded.
- After merging `feature/NELA-0011-visual-identity`: 45 tests passed; headless UI bootstrap succeeded.
- After merging `feature/NELA-0012-claude-review-fixes`: 49 tests passed; headless UI bootstrap succeeded.
- After merging `feature/NELA-language-voice-foundation`: 63 tests passed; headless UI bootstrap succeeded; language pack validation passed.

Latest validation for `NELA-0002-confirmation-deadlock`:

```text
python3 -m unittest discover -s tests
```

Result: 27 tests passed.

Latest validation for `NELA-0005-desktop-agent-v1`:

```text
python3 -m unittest discover -s tests
```

Result: 38 tests passed.

Latest validation for `NELA-0006-ui-foundation`:

```text
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
```

Result: 44 tests passed; headless UI bootstrap succeeded.

Latest validation for `NELA-0011-visual-identity`:

```text
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
```

Result: 45 tests passed; headless UI bootstrap succeeded; Claude Living Eye artifacts were copied into `design/`, `docs/design_system.md` was added, and UI event-state mapping tests passed.

Latest validation for `NELA-0012-claude-review-fixes`:

```text
python3 -m unittest discover -s tests
python3 -m core.app --once "close Finder" --no-dispatch
python3 -m ui.app --headless-smoke
```

Result: 49 tests passed; `close Finder` now asks for confirmation before planning; UI headless bootstrap succeeded.

Latest validation for `NELA-language-voice-foundation`:

```text
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m core.app --once "Open Spotify and play my Night playlist" --no-dispatch
python3 -m ui.app --headless-smoke
```

Result: language pack valid; 63 tests passed; CLI printed a Hebrew `NELA Response`; headless UI bootstrap succeeded.

Window launch smoke:

```text
Instantiate NelaWindow, schedule root.destroy(), run Tk mainloop.
```

Result: Tkinter UI window launched and closed successfully.

Claude bundle generation:

```text
python3 -m scripts.export_claude_review_bundle --output docs/claude_review_bundle.md --focus "Review NELA OS Phase 1 Brain foundation for architecture, event model, memory, agent lifecycle, plugin readiness, security, permissions, error recovery, and long-term maintainability."
```

Result: bundle generated successfully with 26 included files.

Application smoke test:

```text
python3 -m core.app
```

Result: runtime bootstrapped successfully.

CLI one-shot smoke test:

```text
python3 -m core.app --once "open Finder"
```

Result: Brain summary printed successfully, created one Desktop task, dispatched it to the real Desktop Agent, and macOS brought Finder to the foreground.

GitHub public access check:

```text
git ls-remote https://github.com/edentiram72-1/nela.git HEAD refs/heads/main refs/heads/develop refs/heads/feature/NELA-0001-foundation-architecture
```

Result: public HTTPS branch lookup succeeded.

## Suggested Next Task

Finish the develop consolidation handoff:

- Create a draft PR from `develop` to `main` through GitHub web UI or authenticated `gh`.
- Send Claude direct blob links for `docs/claude_handoff_2026-07-24.md`, `docs/ai_handoff.md`, `docs/personality_bible.md`, `docs/hebrew_language_guide.md`, `docs/tone_of_voice.md`, `docs/conversation_rules.md`, `language/pack_schema.md`, `language/hebrew/`, and `language/personality/`.

After release, continue in this order:

1. Memory subsystem integration after `nela-memory-subsystem.zip` is provided.
2. WebView-compatible Living Eye host.
3. Production voice provider behind the existing Voice Agent contract.
4. `NELA-0004-task-idempotency`.
5. Review and merge Sprint 2 Permission Engine.
6. `NELA-0007-event-bus-hardening`.
7. Expand Sprint 2 capability registry into plugin manifest loading.
8. Durable audit storage, richer scope validation, rollback handling, and runtime isolation before real advanced Agents.

## Notes For The Next AI Assistant

- Do not create a direct communication channel with Claude or any other assistant.
- Use GitHub as the collaboration layer.
- For Claude review, share `docs/ai_inbox.md` direct blob links or regenerate `docs/claude_review_bundle.md` and paste/upload it to Claude.
- Read `docs/architecture.md`, `docs/api.md`, and `docs/coding_rules.md` before changing code.
- Keep the Brain agent-neutral.
- Keep Hebrew phrasing and personality rules out of Brain modules.
- Keep provider-specific voice code out of the Language Engine.
- Put execution logic inside Agents only.
- Register new Agents through `AgentDispatcher.register_agent()`.
- Update this handoff file before stopping work.
- Record major structural decisions in `docs/decisions.md`.
```

### `docs/ai_inbox.md`

```markdown
# AI Inbox

This file is the shared GitHub inbox for Claude, Codex, ChatGPT, and future AI assistants working on NELA OS.

GitHub is the collaboration layer. Do not create direct communication channels between assistants.

## Purpose

Use this inbox to track review requests, implementation requests, blockers, handoffs, and decisions that need attention from a specific AI role.

## Roles

### Claude

Owns:

- Brand identity
- Eye design
- UI review
- UX review
- Animations
- Design system
- Architecture and documentation review
- Edge-case and risk analysis

Claude should usually receive direct `blob/` links or a generated review bundle because automated access to GitHub `tree/` and `compare/` pages may be blocked.

### Codex

Owns:

- Brain implementation
- Agents
- Desktop control
- Voice infrastructure
- Memory infrastructure
- Automation
- Tests
- Refactors
- Documentation updates tied to implementation

Codex must keep changes modular, update `docs/ai_handoff.md`, and avoid redesigning Claude-owned UI.

### ChatGPT

Owns:

- Architecture definition
- System design
- Development coordination
- Major structural approval
- Roadmap shaping

## Inbox Lanes

### New

Items that need triage.

- None.

### Ready For Claude

Items waiting for Claude review or design input.

#### Consolidated Foundation Release Review

- Owner: Claude
- Requester: Codex
- Branch: `develop`, then `main` after release merge
- Status: ready
- Focus: Verify that the consolidated foundation matches the intended architecture and that no direct Claude integration was introduced.
- Links:
  - https://github.com/edentiram72-1/nela/blob/develop/docs/ai_handoff.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/ai_inbox.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/architecture.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/claude_review_findings.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/decisions.md

#### Hebrew Language And Voice Foundation Review

- Owner: Claude
- Requester: Codex
- Branch: `develop`, then `main` after release merge
- Status: ready
- Focus: Review language/personality infrastructure and Hebrew pack extensibility. Claude owns final tone and personality; Codex should keep Brain code semantic and phrase-free.
- Links:
  - https://github.com/edentiram72-1/nela/blob/develop/docs/language_system.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/voice_architecture.md
  - https://github.com/edentiram72-1/nela/tree/develop/language

#### Conversation QA, Learning, Cyber Routing, And Visual Prototype Review

- Owner: Claude
- Requester: Codex
- Branch: `codex/nela-language-learning-cyber`
- Status: ready after push
- Focus: Review Hebrew conversation quality, personality consistency,
  agent-awareness responses, safe language-learning behavior, defensive-only
  cyber routing boundaries, and the token-authenticated local Living Eye
  prototype. Do not review old `develop` state as if it were the current work.
- Links:
  - https://github.com/edentiram72-1/nela/blob/codex/nela-language-learning-cyber/docs/claude_language_learning_cyber_review_bundle.md
  - https://github.com/edentiram72-1/nela/blob/codex/nela-language-learning-cyber/brain/qa.py
  - https://github.com/edentiram72-1/nela/blob/codex/nela-language-learning-cyber/language/learning_store.py
  - https://github.com/edentiram72-1/nela/blob/codex/nela-language-learning-cyber/agents/learning/agent.py
  - https://github.com/edentiram72-1/nela/blob/codex/nela-language-learning-cyber/ui/web.py
  - https://github.com/edentiram72-1/nela/blob/codex/nela-language-learning-cyber/design/nela_living_eye.html

### Ready For Codex

Items ready for implementation.

#### Phase A Safety Spine

- Owner: Codex
- Requester: Claude/User
- Branch: `feature/NELA-sprint-2-permission-engine`
- Status: in progress
- Type: architecture + implementation + tests
- Source specs:
  - `docs/permission_model.md`
  - `docs/nela_runtime_architecture.md`
  - `docs/multi_agent_orchestration.md`
  - `docs/ai_system_roadmap.md`
- Goal: Implement the safety foundation before any new real Agents are added.
- Ordered tasks:
  - `NELA-0004-task-idempotency`: add idempotency metadata and retry policy.
  - `NELA-0006-permission-policy`: implemented in Sprint 2 with central Permission Engine, Capability Registry, Agent manifests, confirmation gate, scoped sessions, audit log, kill switch, lock mode, and Dispatcher integration.
  - `NELA-0007-event-bus-hardening`: add subscriber isolation, bounded history, and correlation/trace conventions.
  - `NELA-0008-capability-registry`: initial implementation exists in Sprint 2; future plugin manifest loading still needed.
  - `NELA-0009-plan-executor`: move execution semantics toward async/cancellable plan execution.
  - `NELA-0016-audit-log-and-kill-switch`: add append-only action audit records and global halt/revoke behavior.
  - `NELA-0017-agent-runtime-lifecycle`: add runtime health, lifecycle, backpressure, and worker boundaries.
- Safety note: Cyber, Coding, Research, Browser, Terminal, Files, and communication Agents must not gain new real side effects before the Safety Spine is implemented and tested.

#### Task Idempotency

- Owner: Codex
- Requester: Claude
- Branch: TBD
- Status: ready
- Type: architecture + implementation + tests
- Scope:
  - Add idempotency metadata to `Task` and `AgentCommand`.
  - Prevent automatic retries for non-idempotent or unknown side-effecting tasks.
  - Use command IDs as idempotency keys where Agents support them.
  - Add tests before enabling real Terminal, Browser, Files, or communication Agents.

#### Permission Policy

- Owner: Codex
- Requester: Claude
- Branch: `feature/NELA-sprint-2-permission-engine`
- Status: in progress
- Type: architecture + implementation + tests
- Scope:
  - Add a central policy layer for destructive, external, private-data, system-setting, and communication actions.
  - Keep confirmation behavior consistent across Agents.
  - Avoid Agent-specific permission logic inside the Brain.
  - Sprint 2 implemented the central gateway for current Agents; durable storage, richer scope validation, rollback, and future real Agent policies remain follow-up hardening.

#### WebView UI Host Selection

- Owner: Codex
- Requester: Claude
- Branch: TBD
- Status: ready
- Type: architecture + implementation
- Scope:
  - Choose a WebView-compatible host for `design/nela_living_eye.html`.
  - Keep `UIStateManager`, `UIEventBridge`, and `UIRouter`.
  - Replace the placeholder Tkinter visual shell without redesigning Claude's assets.

### Ready For ChatGPT

Items waiting for architecture or coordination approval.

- None.

### Blocked

Items blocked by missing information, credentials, assets, or user approval.

#### Memory Subsystem Deliverable

- Owner: Codex
- Requester: Claude/User
- Branch: TBD
- Status: blocked
- Type: implementation
- Blocker: `nela-memory-subsystem.zip` was not found in `/Users/edentiram/Downloads`, `/Users/edentiram/Downloads/files`, or the current attachment directory.
- Next action: User provides the zip, then Codex creates a dedicated memory subsystem branch and validates it separately.

#### Advanced Agent Implementation

- Owner: Codex
- Requester: Claude/User
- Branch: TBD
- Status: blocked
- Type: implementation
- Blocker: Sprint 2 implements the Permission Engine, but the full Safety Spine is not complete yet.
- Scope: Coding Agent, Cyber Agent, Research Agent, advanced orchestration, and any new real side-effecting Agent capabilities.
- Next action: Review/merge Sprint 2, then complete idempotency, event-bus hardening, durable audit storage, richer scope validation, rollback handling, runtime isolation, and plugin manifest loading.

### Done

Completed inbox items.

- AI Inbox Workflow: `docs/ai_inbox.md` and GitHub Issue template created.
- UI Foundation: merged into `develop`.
- Desktop Agent V1: merged into `develop`.
- Living Eye Visual Identity: merged into `develop`.
- Claude Review Fixes: merged into `develop`.
- Hebrew Language And Voice Foundation: merged into `develop`.
- Confirmation Deadlock Fix: merged into `develop`.
- Sprint 2 Permission Engine: implemented on `feature/NELA-sprint-2-permission-engine`; ready for review after push/PR.

## Inbox Item Template

Use this format inside this file or in a GitHub Issue created from the AI Collaboration Inbox template.

```markdown
## Title

- Owner: Claude | Codex | ChatGPT
- Requester:
- Branch:
- Status: new | ready | in progress | blocked | done
- Type: review | implementation | architecture | design | docs | bug | test

### Goal

Describe the requested outcome.

### Context

Important links, prior decisions, and relevant files.

### Acceptance Criteria

- [ ]

### Handoff Notes

What should the next AI assistant know?
```

## Rules

- Use one focused inbox item per task.
- Prefer direct GitHub `blob/` links for Claude.
- Use generated bundles for broad reviews.
- Update `docs/ai_handoff.md` after significant work.
- Record major architecture decisions in `docs/decisions.md`.
- Do not use this file for secrets, credentials, private personal data, or API keys.
```

### `docs/cyber_lab.md`

```markdown
# Authorized Cyber Lab

The cyber lab is a local control plane for defensive, authorized testing. It
does not perform exploitation, external scanning, credential theft, persistence,
evasion, malware execution, or exfiltration.

## What It Allows

- Register a local or lab target such as `http://localhost:3000`.
- Require an explicit `CyberAuthorization` for active cyber actions.
- Check the action against target allowlists and scope type.
- Record every decision in an audit log.
- Prepare dry-run local scans and deterministic fuzz cases.
- Stop all lab actions with a kill switch.

## What It Blocks

- Public external targets for active lab actions.
- Missing, expired, mismatched, or incomplete authorization.
- Action classes that NELA never performs:
  credential theft, persistence, malware deployment, evasion, exfiltration, and
  external targeting.
- Any request outside the registered target allowlist.

## Minimal Flow

```python
from agents import build_default_registry
from agents.base import AgentCommand

registry = build_default_registry()
lab = registry.get("authorized_lab")

target = "http://localhost:3000"

lab.execute(
    AgentCommand(
        action="register_lab_target",
        payload={
            "target": target,
            "scope_type": "local_lab",
            "owner": "local-owner",
            "proof": "local development server",
        },
    )
)

result = lab.execute(
    AgentCommand(
        action="run_local_fuzzing",
        payload={
            "target": target,
            "approved": True,
            "dry_run": True,
            "authorization": {
                "owner": "local-owner",
                "scope_type": "local_lab",
                "targets": [target],
                "allowed_actions": ["run_local_fuzzing"],
            },
            "input_types": ["empty", "unicode", "malformed_json"],
        },
    )
)
```

The output is a normalized `work_product` containing the lab decision, audit ID,
deterministic fuzz cases, findings, and next steps.

## Conversation Routing

The Brain can route a small safe set of Hebrew/English security requests to
existing defensive Agents:

- `SecurityCapabilitiesQuestion`: explains NELA's defensive cyber boundaries.
- `CyberDefenseSweep`: creates a first defensive posture report through
  `cyber_defense`, including findings, severity, recommendations, and next
  steps.
- `SecurityReview`: delegates passive code/security text review to
  `secure_code_reviewer`.
- `ThreatModel`: delegates threat-model scaffolding to `secure_code_reviewer`.
- `CyberLabStatus`: reads the current authorized lab state through
  `authorized_lab`.
- `CyberLabRegisterTarget`: registers a local/owned lab target through
  `authorized_lab`.
- `LocalFuzzPlan`: prepares a local-only fuzzing plan through
  `anomaly_discovery`.

This does not enable external targeting or active offensive behavior. Active
lab execution remains gated by authorization, target allowlists, scoped
sessions, confirmation, dry-run behavior, audit records, process isolation, and
the kill switch.

Example local route:

```text
User: "תרשמי יעד מעבדה http://localhost:3000"
  -> CyberLabRegisterTarget
  -> authorized_lab.register_lab_target
  -> Permission tier T1

User: "תכיני תוכנית fuzz מקומית לפרסר"
  -> LocalFuzzPlan
  -> anomaly_discovery.create_local_fuzz_plan
  -> Permission tier T0
```

Example defense findings route:

```text
User: "נלה תעשי הגנה"
User: "תעשי בדיקה של אבטחה"
  -> CyberDefenseSweep
  -> cyber_defense.defense_posture_check
  -> Permission tier T0
  -> Hebrew response with findings, severity, recommendation, and next step
```

The first posture check intentionally starts with safe defensive fundamentals:
authorized scope, access control, audit coverage, dependency/config hardening,
and recovery readiness.
```

### `docs/language_system.md`

```markdown
# NELA Language System

## Purpose

The Language System turns semantic Brain output into user-facing Hebrew text.

It does not define NELA's final personality. Claude owns personality, tone, emotional behavior, and language-pack content. Codex owns the technical infrastructure that loads, validates, selects, renders, and safely falls back when language content is missing.

## Flow

```text
Brain semantic result
  |
  v
NelaResponseAdapter
  |
  v
LanguageEngine
  |
  +--> LanguagePackLoader
  +--> PhraseSelector
  +--> TemplateRenderer
  +--> Validator
  |
  v
Final Hebrew response
  |
  +--> UI
  +--> Voice Agent
```

## Public API

Module: `language/engine.py`

- `load_language_pack(path)`: load and validate a pack directory.
- `reload_language_pack()`: reload the current pack from disk.
- `render_response(category, variables=None, tone=None, emotion=None, tags=())`: select and render a phrase.
- `select_phrase(category, tone=None, emotion=None, tags=())`: return the selected `PhraseEntry`.
- `validate_pack(path=None)`: return a validation report.
- `list_categories()`: return supported categories.
- `get_available_tones()`: return available tone names.
- `health_check()`: report pack, personality, and validation status.

## Phrase Model

Each phrase entry supports:

- `id`
- `text`
- `category`
- `language`
- `tone`
- `emotion`
- `formality`
- `gender`
- `weight`
- `requires`
- `tags`
- `enabled`
- `version`

Template variables use Python-style braces, for example:

```json
{
  "id": "desktop.open.success.1",
  "text": "פותחת את {application}.",
  "category": "desktop.open.success",
  "language": "he",
  "tone": ["warm"],
  "emotion": "neutral",
  "requires": ["application"]
}
```

Missing variables are kept visible as `{variable}` instead of crashing the response path.

## Selection Rules

`PhraseSelector` supports:

- category matching
- category-prefix fallback
- weighted variation
- recent-phrase avoidance
- personality profile preferences
- requested tone and emotion
- safe Hebrew fallback phrases

Selection is weighted and scored, not unrestricted random-only choice.

## Validation

Run:

```bash
python3 -m scripts.validate_language_packs
```

The validator detects:

- duplicate IDs
- missing required fields
- invalid JSON
- unsupported categories
- unsupported tones and emotions
- empty text
- language metadata mismatch
- template variables missing from `requires`

## Seed Pack

The first Hebrew pack under `language/hebrew/` is intentionally small. It provides enough phrases to validate system behavior without replacing Claude's future language work.

Current categories include greetings, farewells, confirmations, clarifications, thinking, waiting, success, errors, warnings, apologies, permissions, desktop, files, browser, music, coding, memory, automation, and general chat.

## Adding Hebrew Phrases

1. Choose the category file under `language/hebrew/`.
2. Add a phrase entry with a unique `id`.
3. Include every template variable in `requires`.
4. Use only tones and emotions listed in `language/hebrew/manifest.json`.
5. Run `python3 -m scripts.validate_language_packs`.

New categories require two edits:

1. Add the category name to `language/hebrew/manifest.json`.
2. Add phrases in an existing category file or add a new file and list it in `manifest.json`.

Keep Brain modules unchanged when adding phrases.

## Runtime Learned Responses

NELA can now learn simple user-taught trigger/response pairs at runtime without
editing the core Hebrew pack.

Flow:

```text
User: "נלה תלמדי שכשאני אומר בוקר טוב תעני בוקר אור"
  |
  v
IntentRouter -> TeachResponse
  |
  v
Planner -> learning.teach_response
  |
  v
Permission Engine -> T1 local scoped write
  |
  v
LearningAgent -> data/language/learned_responses.json
  |
  v
KnowledgeEngine answers future matching turns with qa.learned
```

This is intentionally separate from Claude-authored phrase packs:

- Claude/personality packs remain authoritative for NELA's voice.
- User-taught responses are local runtime data.
- The Brain stays semantic and does not hardcode Hebrew responses.
- Learned responses are exact/simple trigger matches in this phase, not an
  unrestricted knowledge base.

Supported examples:

```text
נלה תלמדי שכשאני אומר בוקר טוב תעני בוקר אור
כשאני אומר מצב בית תעני הכל רגוע
learn response: ping => pong
```

Future extensions should add review, editing, deletion, tagging, and conflict
resolution before large-scale phrase ingestion.

## Personality Profiles

Personality profiles under `language/personality/` influence selection with metadata only:

- preferred tones
- preferred emotions
- formality
- gender
- category bias

They do not execute code and should not contain secrets. Claude can replace these profiles with richer rules later as long as they stay data-driven.

## Privacy

The Language System currently reads local JSON files and renders local text. It does not call external APIs, send text to cloud services, or persist conversation text by itself.

Privacy can change if future plugin-based language packs or cloud personalization are added. Any future external language provider must document what text leaves the machine and must not store secrets in language-pack files.

## Future Extensions

- Load language packs from plugins.
- Add pack version migrations.
- Add review tooling for Claude-authored packs.
- Add richer grammatical controls for Hebrew gender, number, and formality.
- Add deterministic phrase snapshots for scripted demos.
- Add runtime pack reload from a settings screen.
```

### `agents/security/cyber_defense.py`

```python
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
```

### `agents/security/__init__.py`

```python
"""Defensive security specialist agents."""

from agents.security.anomaly_discovery import AnomalyDiscoveryAgent
from agents.security.authorized_lab import AuthorizedLabAgent
from agents.security.cyber_defense import CyberDefenseAgent
from agents.security.secure_code_reviewer import SecureCodeReviewerAgent
from agents.security.vulnerability_research import VulnerabilityResearchAgent

__all__ = [
    "AnomalyDiscoveryAgent",
    "AuthorizedLabAgent",
    "CyberDefenseAgent",
    "SecureCodeReviewerAgent",
    "VulnerabilityResearchAgent",
]
```

### `agents/security/authorized_lab.py`

```python
"""Authorized local cyber-lab agent."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding
from cyber_lab import (
    AuthorizationScopeType,
    CyberAuthorization,
    CyberLab,
    CyberLabActionRequest,
    CyberLabDecisionType,
    CyberLabTarget,
    audit_config_text,
    build_local_fuzz_cases,
    scan_source_text,
)
from cyber_lab.models import FORBIDDEN_ACTIONS


class AuthorizedLabAgent(SpecialistAgent):
    name = "authorized_lab"
    domain = AgentDomain.SECURITY
    purpose = "Gate local/owned cyber-lab checks through authorization, dry-run, allowlists, and audit records."
    capabilities = ("authorized_lab.target", "authorized_lab.evaluate", "authorized_lab.scan", "authorized_lab.fuzz")

    def __init__(self, lab: CyberLab | None = None) -> None:
        super().__init__()
        self.lab = lab or CyberLab()

    def _handlers(self):
        return {
            **super()._handlers(),
            "register_lab_target": self._register_lab_target,
            "evaluate_lab_action": self._evaluate_lab_action,
            "scan_lab_target": self._scan_lab_target,
            "run_local_fuzzing": self._run_local_fuzzing,
            "lab_status": self._lab_status,
            "activate_lab_kill_switch": self._activate_lab_kill_switch,
            "deactivate_lab_kill_switch": self._deactivate_lab_kill_switch,
        }

    def _register_lab_target(self, command: AgentCommand) -> AgentWorkProduct:
        target = _target_from_payload(command.payload)
        self.lab.add_target(target)
        return AgentWorkProduct(
            summary="Authorized lab target registered.",
            artifacts=(
                artifact(
                    "lab_target",
                    "registered_lab_target",
                    (
                        f"target={target.identifier}",
                        f"scope_type={target.scope_type.value}",
                        f"owner={target.owner}",
                        f"proof={target.proof}",
                    ),
                ),
            ),
            next_steps=("Submit a CyberAuthorization before scan_lab_target or run_local_fuzzing.",),
        )

    def _evaluate_lab_action(self, command: AgentCommand) -> AgentWorkProduct:
        request = _request_from_payload(command.action, command.payload)
        decision = self.lab.evaluate(request)
        return AgentWorkProduct(
            summary=f"Cyber-lab action evaluated: {decision.decision.value}.",
            artifacts=(artifact("audit", "lab_decision", tuple(f"{key}={value}" for key, value in decision.to_dict().items())),),
        )

    def _scan_lab_target(self, command: AgentCommand) -> AgentWorkProduct:
        decision = self.lab.evaluate(_request_from_payload("scan_lab_target", command.payload))
        if not decision.allowed:
            return _decision_product(decision)

        findings = []
        for path, source in _files_from_payload(command.payload).items():
            findings.extend(_finding_from_scanner(item, "sast") for item in scan_source_text(source, path=path))
        config = str(command.payload.get("config", ""))
        findings.extend(_finding_from_scanner(item, "config_audit") for item in audit_config_text(config))
        return AgentWorkProduct(
            summary=f"Authorized lab scan prepared for {decision.target}.",
            findings=tuple(findings),
            artifacts=(artifact("audit", "lab_scan_decision", tuple(f"{key}={value}" for key, value in decision.to_dict().items())),),
            next_steps=(
                "Apply fixes locally, then rerun the same scan.",
                "Keep active testing inside the approved target and time window.",
            ),
        )

    def _run_local_fuzzing(self, command: AgentCommand) -> AgentWorkProduct:
        decision = self.lab.evaluate(_request_from_payload("run_local_fuzzing", command.payload))
        if not decision.allowed:
            return _decision_product(decision)

        input_types = command.payload.get("input_types")
        selected = tuple(str(item) for item in input_types) if isinstance(input_types, (list, tuple)) else None
        cases = build_local_fuzz_cases(selected)
        return AgentWorkProduct(
            summary=f"Local fuzzing dry-run prepared for {decision.target}.",
            artifacts=(
                artifact("audit", "lab_fuzz_decision", tuple(f"{key}={value}" for key, value in decision.to_dict().items())),
                artifact("fuzz_cases", "local_fuzz_cases", tuple(repr(case) for case in cases)),
            ),
            next_steps=("Wire these cases into local tests or a sandboxed harness before increasing volume.",),
        )

    def _lab_status(self, command: AgentCommand) -> AgentWorkProduct:
        return AgentWorkProduct(
            summary=f"Cyber lab has {len(self.lab.target_allowlist())} target(s) and {len(self.lab.audit_log())} audit record(s).",
            artifacts=(
                artifact("targets", "lab_targets", self.lab.target_allowlist() or ("No registered targets.",)),
                artifact("audit", "lab_audit", tuple(str(record.to_dict()) for record in self.lab.audit_log()) or ("No audit records.",)),
            ),
        )

    def _activate_lab_kill_switch(self, command: AgentCommand) -> AgentWorkProduct:
        decision = self.lab.activate_kill_switch(str(command.payload.get("reason", "manual")))
        return _decision_product(decision)

    def _deactivate_lab_kill_switch(self, command: AgentCommand) -> AgentWorkProduct:
        decision = self.lab.deactivate_kill_switch(str(command.payload.get("reason", "manual")))
        return _decision_product(decision)


def _target_from_payload(payload: dict[str, object]) -> CyberLabTarget:
    scope_type = AuthorizationScopeType(str(payload.get("scope_type", AuthorizationScopeType.LOCAL_LAB.value)))
    identifier = str(payload.get("target", payload.get("identifier", "localhost")))
    return CyberLabTarget(
        identifier=identifier,
        scope_type=scope_type,
        owner=str(payload.get("owner", "local-owner")),
        proof=str(payload.get("proof", "declared-owned-local-lab")),
        metadata=dict(payload.get("metadata", {})) if isinstance(payload.get("metadata"), dict) else {},
    )


def _request_from_payload(action: str, payload: dict[str, object]) -> CyberLabActionRequest:
    requested_action = str(payload.get("action", action))
    authorization_payload = payload.get("authorization")
    authorization = _authorization_from_payload(authorization_payload) if isinstance(authorization_payload, dict) else None
    return CyberLabActionRequest(
        action=requested_action,
        target=str(payload.get("target", "")),
        authorization=authorization,
        dry_run=bool(payload.get("dry_run", True)),
        approved=bool(payload.get("approved", False)),
        metadata=dict(payload.get("metadata", {})) if isinstance(payload.get("metadata"), dict) else {},
    )


def _authorization_from_payload(payload: dict[str, object]) -> CyberAuthorization:
    forbidden_actions = payload.get("forbidden_actions")
    return CyberAuthorization(
        owner=str(payload.get("owner", "local-owner")),
        scope_type=AuthorizationScopeType(str(payload.get("scope_type", AuthorizationScopeType.LOCAL_LAB.value))),
        targets=tuple(str(item) for item in payload.get("targets", ())),
        allowed_actions=tuple(str(item) for item in payload.get("allowed_actions", ())),
        forbidden_actions=tuple(str(item) for item in forbidden_actions) if forbidden_actions is not None else tuple(sorted(FORBIDDEN_ACTIONS)),
        approved_by=str(payload.get("approved_by", "local-owner")),
    )


def _files_from_payload(payload: dict[str, object]) -> dict[str, str]:
    files = payload.get("files")
    if isinstance(files, dict):
        return {str(path): str(source) for path, source in files.items()}
    source = str(payload.get("source", ""))
    return {"inline": source} if source else {}


def _finding_from_scanner(item: dict[str, str], category: str) -> TaskFinding:
    return TaskFinding(
        title=item.get("title", "Finding"),
        severity=_risk_level(item.get("severity", "info")),
        category=category,
        location=item.get("location"),
        evidence=item.get("evidence"),
        recommendation=item.get("recommendation"),
    )


def _risk_level(value: object) -> RiskLevel:
    try:
        return RiskLevel(str(value).lower())
    except ValueError:
        return RiskLevel.INFO


def _decision_product(decision) -> AgentWorkProduct:
    severity = RiskLevel.INFO if decision.decision in {CyberLabDecisionType.ALLOWED, CyberLabDecisionType.DRY_RUN_ONLY} else RiskLevel.HIGH
    return AgentWorkProduct(
        summary=f"Cyber-lab action {decision.decision.value}: {decision.reason}",
        findings=(
            TaskFinding(
                title=f"Cyber-lab decision: {decision.decision.value}",
                severity=severity,
                category="authorized_lab",
                location=decision.target,
                evidence=decision.audit_id,
                recommendation="Adjust authorization, target allowlist, approval, or scope before retrying.",
            ),
        ),
        artifacts=(artifact("audit", "lab_decision", tuple(f"{key}={value}" for key, value in decision.to_dict().items())),),
    )
```

### `agents/security/secure_code_reviewer.py`

```python
"""Defensive secure code review agent."""

from __future__ import annotations

import re

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


class SecureCodeReviewerAgent(SpecialistAgent):
    name = "secure_code_reviewer"
    domain = AgentDomain.SECURITY
    purpose = "Perform defensive SAST-style review and suggest remediation."
    capabilities = ("sast.review", "secure_code.findings", "threat_modeling")

    def _handlers(self):
        return {
            **super()._handlers(),
            "review_code_security": self._review_code_security,
            "threat_model": self._threat_model,
        }

    def _review_code_security(self, command: AgentCommand) -> AgentWorkProduct:
        files = _source_files(command.payload)
        findings: list[TaskFinding] = []
        for path, source in files.items():
            findings.extend(_scan_source(path, source))
        summary = f"Defensive code security review completed for {len(files)} file(s)."
        if not findings:
            summary += " No heuristic findings were detected."
        return AgentWorkProduct(
            summary=summary,
            findings=tuple(findings),
            next_steps=(
                "לאמת את הממצאים מול הקוד האמיתי.",
                "לתקן את שורש הבעיה ולהוסיף בדיקת רגרסיה לכל ממצא שאושר.",
            ),
        )

    def _threat_model(self, command: AgentCommand) -> AgentWorkProduct:
        asset = str(command.payload.get("asset", "the changed system"))
        trust_boundaries = tuple(command.payload.get("trust_boundaries", ("user input", "file system", "network/API boundary")))
        findings = tuple(
            TaskFinding(
                title=f"Review trust boundary: {boundary}",
                severity=RiskLevel.MEDIUM,
                category="threat_model",
                location=asset,
                recommendation="לתעד קלטים צפויים, אימות, הרשאות, לוגים והתנהגות כשל.",
            )
            for boundary in trust_boundaries
        )
        return AgentWorkProduct(
            summary=f"Threat model scaffold prepared for {asset}.",
            findings=findings,
            next_steps=("להפוך סיכונים שאושרו למשימות יישום קטנות.",),
        )


def _source_files(payload: dict[str, object]) -> dict[str, str]:
    files = payload.get("files")
    if isinstance(files, dict):
        return {str(path): str(source) for path, source in files.items()}
    return {str(payload.get("path", "inline")): str(payload.get("source", ""))}


def _scan_source(path: str, source: str) -> list[TaskFinding]:
    checks: tuple[tuple[str, str, RiskLevel, str], ...] = (
        (r"\beval\s*\(", "Dynamic eval usage", RiskLevel.HIGH, "להחליף eval בפרסר טיפוסי או בטבלת פעולות מפורשת."),
        (r"\bexec\s*\(", "Dynamic exec usage", RiskLevel.HIGH, "להסיר exec או לבודד יצירת קוד מאושרת מאחורי סקירה ובדיקות."),
        (r"shell\s*=\s*True", "Shell execution enabled", RiskLevel.HIGH, "להריץ פקודות כמערך ארגומנטים בלי shell."),
        (r"pickle\.loads?\s*\(", "Unsafe pickle deserialization", RiskLevel.HIGH, "להשתמש בפורמט סריאליזציה בטוח עבור מידע לא מהימן."),
        (r"yaml\.load\s*\((?![^)]*SafeLoader)", "YAML load without SafeLoader", RiskLevel.MEDIUM, "להשתמש ב-yaml.safe_load או SafeLoader."),
        (r"verify\s*=\s*False", "TLS certificate verification disabled", RiskLevel.HIGH, "להשאיר אימות TLS פעיל ולתקן trust roots במפורש."),
        (r"hashlib\.(md5|sha1)\s*\(", "Weak hash algorithm", RiskLevel.MEDIUM, "להשתמש ב-SHA-256 או במנגנון ייעודי לסיסמאות."),
        (r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]{8,}", "Possible hardcoded secret", RiskLevel.CRITICAL, "להעביר סודות למשתני סביבה או למנהל סודות ייעודי."),
    )
    findings: list[TaskFinding] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        for pattern, title, severity, recommendation in checks:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(
                    TaskFinding(
                        title=title,
                        severity=severity,
                        category="sast",
                        location=f"{path}:{line_number}",
                        evidence=line.strip()[:160],
                        recommendation=recommendation,
                    )
                )
    return findings
```

### `agents/security/vulnerability_research.py`

```python
"""Defensive vulnerability research and dependency correlation agent."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


class VulnerabilityResearchAgent(SpecialistAgent):
    name = "vulnerability_research"
    domain = AgentDomain.SECURITY
    purpose = "Correlate known advisories with project dependencies and summarize defensive impact."
    capabilities = ("dependency.scanning", "cve.correlation", "defensive.research")

    def _handlers(self):
        return {
            **super()._handlers(),
            "scan_dependencies": self._scan_dependencies,
            "correlate_cves": self._scan_dependencies,
        }

    def _scan_dependencies(self, command: AgentCommand) -> AgentWorkProduct:
        dependencies = _normalize_dependencies(command.payload.get("dependencies", ()))
        advisory_db = command.payload.get("advisory_db", {})
        if not isinstance(advisory_db, dict):
            advisory_db = {}
        findings: list[TaskFinding] = []
        for name, version in dependencies:
            if version in {"", "*", "latest"} or version.startswith((">", "<", "~", "^")):
                findings.append(
                    TaskFinding(
                        title=f"Dependency is not pinned: {name}",
                        severity=RiskLevel.MEDIUM,
                        category="dependency",
                        location=name,
                        evidence=version or "unversioned",
                        recommendation="לקבע גרסאות או להשתמש בקובץ lock ולבדוק עדכונים דרך CI.",
                    )
                )
            advisories = advisory_db.get(name, ())
            if isinstance(advisories, dict):
                advisories = (advisories,)
            for advisory in advisories:
                if not isinstance(advisory, dict):
                    continue
                findings.append(
                    TaskFinding(
                        title=f"Known advisory for {name}: {advisory.get('id', 'unknown')}",
                        severity=_risk_level(advisory.get("severity", "high")),
                        category="cve_correlation",
                        location=name,
                        evidence=f"installed={version}; affected={advisory.get('affected', 'unknown')}",
                        recommendation=str(advisory.get("recommendation", "לעדכן לגרסה מתוקנת ולהוסיף כיסוי רגרסיה.")),
                    )
                )
        return AgentWorkProduct(
            summary=f"Dependency/CVE correlation completed for {len(dependencies)} dependenc(ies).",
            findings=tuple(findings),
            next_steps=("לעדכן מידע על advisories ממקור מאושר לפני החלטת שחרור.",),
        )


def _normalize_dependencies(value: object) -> tuple[tuple[str, str], ...]:
    if isinstance(value, dict):
        return tuple((str(name), str(version)) for name, version in value.items())
    if isinstance(value, (list, tuple)):
        normalized: list[tuple[str, str]] = []
        for item in value:
            if isinstance(item, dict):
                normalized.append((str(item.get("name", "unknown")), str(item.get("version", ""))))
            else:
                parts = str(item).split("==", 1)
                normalized.append((parts[0], parts[1] if len(parts) == 2 else ""))
        return tuple(normalized)
    return ()


def _risk_level(value: object) -> RiskLevel:
    try:
        return RiskLevel(str(value).lower())
    except ValueError:
        return RiskLevel.HIGH
```

### `agents/security/anomaly_discovery.py`

```python
"""Defensive anomaly discovery and local fuzzing-plan agent."""

from __future__ import annotations

from statistics import mean, pstdev

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


class AnomalyDiscoveryAgent(SpecialistAgent):
    name = "anomaly_discovery"
    domain = AgentDomain.SECURITY
    purpose = "Find unusual local signals and design safe lab-only fuzzing plans."
    capabilities = ("anomaly.detection", "local.fuzzing.plan", "unknown_unknowns.discovery")

    def _handlers(self):
        return {
            **super()._handlers(),
            "detect_anomalies": self._detect_anomalies,
            "create_local_fuzz_plan": self._create_local_fuzz_plan,
        }

    def _detect_anomalies(self, command: AgentCommand) -> AgentWorkProduct:
        series = tuple(float(value) for value in command.payload.get("series", ()))
        label = str(command.payload.get("label", "metric"))
        if len(series) < 3:
            return AgentWorkProduct(
                summary="Not enough data points for anomaly detection.",
                next_steps=("Provide at least three local observations.",),
            )
        baseline = mean(series)
        deviation = pstdev(series) or 1.0
        findings = []
        for index, value in enumerate(series):
            z_score = abs((value - baseline) / deviation)
            if z_score >= 2.0:
                findings.append(
                    TaskFinding(
                        title=f"Anomalous {label} value",
                        severity=RiskLevel.MEDIUM if z_score < 3.0 else RiskLevel.HIGH,
                        category="anomaly",
                        location=f"{label}[{index}]",
                        evidence=f"value={value}; mean={baseline:.2f}; z={z_score:.2f}",
                        recommendation="לבדוק לוגים מקומיים, שינויים אחרונים וצורת קלט סביב התצפית הזאת.",
                    )
                )
        return AgentWorkProduct(
            summary=f"Anomaly detection completed for {len(series)} local point(s).",
            findings=tuple(findings),
        )

    def _create_local_fuzz_plan(self, command: AgentCommand) -> AgentWorkProduct:
        target = str(command.payload.get("target", "local parser or function"))
        input_types = tuple(command.payload.get("input_types", ("empty input", "large input", "unicode input", "malformed structure")))
        return AgentWorkProduct(
            summary="Local lab fuzzing plan prepared.",
            artifacts=(
                artifact(
                    "fuzz_plan",
                    "local_fuzz_plan",
                    (
                        f"Target: {target}",
                        "Scope: local/lab execution only, no external targets.",
                        "Harness: call the target through its public function boundary.",
                        "Assertions: no crashes, no hangs, clear validation errors.",
                        "Inputs:",
                        *(f"- {input_type}" for input_type in input_types),
                    ),
                ),
            ),
            next_steps=("לבנות harness בבדיקות לפני שמגדילים את נפח הקלטים.",),
        )
```

### `agents/factory.py`

```python
"""Factories for registering the first-wave NELA multi-agent system."""

from __future__ import annotations

from pathlib import Path

from agents.backend import BackendAgent
from agents.browser import BrowserAgent
from agents.code_architect import CodeArchitectAgent
from agents.files import FilesAgent
from agents.frontend import FrontendAgent
from agents.github import GitHubAgent
from agents.learning import LearningAgent
from agents.memory import MemoryAgent
from agents.orchestrator import OrchestratorAgent
from agents.planner import PlannerAgent
from agents.registry import AgentRegistry
from agents.role_agents import (
    BlueTeamAgent,
    CodeReviewerAgent,
    ContainmentAgent,
    DataEngineerAgent,
    DeceptionAgent,
    DetectionEngineeringAgent,
    DevOpsEngineerAgent,
    DocumentationAgent,
    DocumentationResearcherAgent,
    ExploitValidationAgent,
    ForensicsAgent,
    IncidentCommanderAgent,
    InfrastructureSecurityAgent,
    LLMEngineerAgent,
    MLEngineerAgent,
    MobileEngineerAgent,
    PurpleTeamAgent,
    QualitySelfEvaluationAgent,
    RecoveryAgent,
    RedTeamSimulatorAgent,
    ResearchAgent,
    SecurityResearcherAgent,
    SentinelAgent,
    TestEngineerAgent,
    ThreatHunterAgent,
    ThreatIntelligenceAgent,
    TrendMonitorAgent,
)
from agents.security import AnomalyDiscoveryAgent, AuthorizedLabAgent, CyberDefenseAgent, SecureCodeReviewerAgent, VulnerabilityResearchAgent
from agents.test_qa import TestQAAgent
from agents.automation import AutomationAgent
from agents.terminal import TerminalAgent
from language.learning_store import LearnedResponseStore


def build_default_agents(
    learning_store_path: Path | str | None = None,
    learning_store: LearnedResponseStore | None = None,
):
    """Instantiate the defensive multi-agent foundation in stable registry order."""

    response_store = learning_store or LearnedResponseStore(learning_store_path)
    return (
        OrchestratorAgent(),
        PlannerAgent(),
        MemoryAgent(),
        LearningAgent(store=response_store),
        QualitySelfEvaluationAgent(),
        CodeArchitectAgent(),
        BackendAgent(),
        FrontendAgent(),
        MobileEngineerAgent(),
        DevOpsEngineerAgent(),
        CodeReviewerAgent(),
        TestQAAgent(),
        TestEngineerAgent(),
        DocumentationAgent(),
        LLMEngineerAgent(),
        MLEngineerAgent(),
        DataEngineerAgent(),
        ResearchAgent(),
        DocumentationResearcherAgent(),
        TrendMonitorAgent(),
        SecurityResearcherAgent(),
        CyberDefenseAgent(),
        SecureCodeReviewerAgent(),
        VulnerabilityResearchAgent(),
        InfrastructureSecurityAgent(),
        ThreatIntelligenceAgent(),
        SentinelAgent(),
        IncidentCommanderAgent(),
        ContainmentAgent(),
        DeceptionAgent(),
        ForensicsAgent(),
        ThreatHunterAgent(),
        RedTeamSimulatorAgent(),
        BlueTeamAgent(),
        PurpleTeamAgent(),
        ExploitValidationAgent(),
        DetectionEngineeringAgent(),
        RecoveryAgent(),
        AnomalyDiscoveryAgent(),
        AuthorizedLabAgent(),
        BrowserAgent(),
        TerminalAgent(),
        GitHubAgent(),
        FilesAgent(),
        AutomationAgent(),
    )


def build_default_registry(
    learning_store_path: Path | str | None = None,
    learning_store: LearnedResponseStore | None = None,
) -> AgentRegistry:
    registry = AgentRegistry()
    for agent in build_default_agents(learning_store_path=learning_store_path, learning_store=learning_store):
        registry.register(agent)
    return registry
```

### `agents/foundation.py`

```python
"""Base implementation for deterministic specialist agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.base import AgentCommand, AgentResult, BaseAgent
from agents.policy import DefensivePolicyGuard, ToolPermissionProfile, default_tool_permissions
from agents.task_schema import AgentDomain, AgentWorkProduct, TaskArtifact, TaskFinding
from permissions.models import AgentManifest as PermissionAgentManifest
from permissions.models import Capability, PermissionTier


@dataclass(frozen=True)
class AgentManifest:
    name: str
    domain: AgentDomain
    purpose: str
    capabilities: tuple[str, ...]
    permission_profile: ToolPermissionProfile

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "domain": self.domain.value,
            "purpose": self.purpose,
            "capabilities": list(self.capabilities),
            "permission_profile": self.permission_profile.to_dict(),
        }


class SpecialistAgent(BaseAgent):
    """Policy-aware base for first-wave NELA multi-agent roles."""

    domain: AgentDomain = AgentDomain.SOFTWARE
    purpose: str = "Specialist agent."
    capabilities: tuple[str, ...] = ()

    def __init__(self, policy: DefensivePolicyGuard | None = None) -> None:
        super().__init__()
        self.policy = policy or DefensivePolicyGuard()

    @property
    def manifest(self) -> AgentManifest:
        permissions = default_tool_permissions().get(
            self.name,
            ToolPermissionProfile(self.name, ("summarize",), filesystem="workspace_read"),
        )
        return AgentManifest(
            name=self.name,
            domain=self.domain,
            purpose=self.purpose,
            capabilities=self.capabilities,
            permission_profile=permissions,
        )

    @property
    def permission_manifest(self) -> PermissionAgentManifest:
        capabilities = tuple(
            Capability(
                action=action,
                tier=_permission_tier_for_action(action),
                description=f"{self.name}: {action}",
                requires_confirmation=_permission_tier_for_action(action) in {PermissionTier.T2, PermissionTier.T3},
                scopes=("cyber.authorized_scope",) if _permission_tier_for_action(action) == PermissionTier.T3 else (),
            )
            for action in sorted(self._handlers())
        )
        return PermissionAgentManifest(agent=self.name, capabilities=capabilities)

    def execute(self, command: AgentCommand) -> AgentResult:
        policy = self.policy.validate(command.action, command.payload)
        if not policy.allowed:
            return AgentResult(
                False,
                policy.reason,
                {
                    "agent": self.name,
                    "policy_decision": policy.decision.value,
                    "matched_terms": list(policy.matched_terms),
                    "allowed_scope": "defensive_authorized_work_only",
                },
            )

        handler = self._handlers().get(command.action)
        if handler is None:
            return AgentResult(
                False,
                f"Unsupported action for {self.name}.",
                {
                    "agent": self.name,
                    "supported_actions": sorted(self._handlers()),
                    "manifest": self.manifest.to_dict(),
                },
            )

        product = handler(command)
        return AgentResult(
            True,
            product.summary,
            {
                "agent": self.name,
                "manifest": self.manifest.to_dict(),
                "work_product": product.to_dict(),
            },
        )

    def _handlers(self) -> dict[str, Any]:
        return {"describe_capabilities": self._describe_capabilities}

    def _describe_capabilities(self, command: AgentCommand) -> AgentWorkProduct:
        return AgentWorkProduct(
            summary=f"{self.name} is ready.",
            artifacts=(
                TaskArtifact(
                    kind="manifest",
                    name=f"{self.name}.manifest",
                    content=str(self.manifest.to_dict()),
                ),
            ),
            next_steps=("Delegate a supported action with an explicit defensive objective.",),
        )


def artifact(kind: str, name: str, lines: tuple[str, ...]) -> TaskArtifact:
    return TaskArtifact(kind=kind, name=name, content="\n".join(lines))


def finding(
    title: str,
    category: str,
    severity: Any,
    location: str | None = None,
    evidence: str | None = None,
    recommendation: str | None = None,
) -> TaskFinding:
    return TaskFinding(
        title=title,
        category=category,
        severity=severity,
        location=location,
        evidence=evidence,
        recommendation=recommendation,
    )


def _permission_tier_for_action(action: str) -> PermissionTier:
    if action in {
        "contain_incident",
        "simulate_lab_adversary",
        "validate_exploit_safely",
        "scan_lab_target",
        "run_local_fuzzing",
    }:
        return PermissionTier.T3
    if action in {"remember", "record_lesson", "teach_response", "register_lab_target"}:
        return PermissionTier.T1
    return PermissionTier.T0
```

### `agents/policy.py`

```python
"""Defensive policy guardrails and sandboxed tool permission profiles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import ipaddress
import re
import socket
from typing import Any
from urllib.parse import urlparse


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    reason: str
    matched_terms: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        return self.decision == PolicyDecision.ALLOW


@dataclass(frozen=True)
class ToolPermissionProfile:
    """Sandbox profile for an agent role.

    The first implementation is intentionally declarative. Runtime integrations
    can bind these profiles to real process, file, and network controls later.
    """

    agent: str
    allowed_tools: tuple[str, ...]
    filesystem: str = "workspace_read"
    network: str = "disabled"
    process_execution: str = "disabled"
    may_modify_code: bool = False
    may_contact_external_targets: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "agent": self.agent,
            "allowed_tools": list(self.allowed_tools),
            "filesystem": self.filesystem,
            "network": self.network,
            "process_execution": self.process_execution,
            "may_modify_code": self.may_modify_code,
            "may_contact_external_targets": self.may_contact_external_targets,
        }


DENIED_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bcredential theft\b",
        r"\bsteal(?:ing)?\s+(?:passwords?|credentials?|tokens?)\b",
        r"\bexfiltrat(?:e|ion)\b",
        r"\bpersistence\b",
        r"\bevasion\b",
        r"\bbypass\s+(?:auth|authentication|mfa|edr|av)\b",
        r"\breverse shell\b",
        r"\bweaponiz(?:e|ed|ation)\b",
        r"\bmalware\b",
        r"\bransomware\b",
        r"\bphishing\b",
        r"\bddos\b",
        r"\bexploit\s+(?:kit|payload|chain|against|for)\b",
        r"\battack\s+(?:external|public|third[- ]party|real)\b",
        r"\bscan\s+(?:the\s+)?internet\b",
    )
)

CYBER_ACTIONS_REQUIRING_AUTHORIZATION: frozenset[str] = frozenset(
    {
        "contain_incident",
        "scan_lab_target",
        "simulate_lab_adversary",
        "validate_exploit_safely",
        "run_local_fuzzing",
    }
)

AUTHORIZED_SCOPE_TYPES: frozenset[str] = frozenset({"local_lab", "ctf", "owned_asset", "workspace_artifact"})

FORBIDDEN_CYBER_ACTIONS: frozenset[str] = frozenset(
    {
        "external_targeting",
        "persistence",
        "credential_theft",
        "malware_deployment",
        "evasion",
        "exfiltration",
    }
)


DEFENSIVE_ALLOWED_TERMS: tuple[str, ...] = (
    "sast",
    "dependency scanning",
    "config auditing",
    "local fuzzing",
    "lab fuzzing",
    "anomaly detection",
    "threat modeling",
    "cve correlation",
    "secure code review",
    "defensive",
    "authorized",
)


class DefensivePolicyGuard:
    """Keeps the multi-agent system inside defensive, authorized work."""

    def validate(self, action: str, payload: dict[str, Any] | None = None) -> PolicyResult:
        payload = payload or {}
        haystack = _flatten_text({"action": action, "payload": _payload_for_text_policy(payload)})
        matched = tuple(pattern.pattern for pattern in DENIED_PATTERNS if pattern.search(haystack))
        if matched:
            return PolicyResult(
                PolicyDecision.DENY,
                "Request is outside the defensive/authorized scope for NELA security agents.",
                matched,
            )
        if _targets_external_system(action, payload):
            return PolicyResult(
                PolicyDecision.DENY,
                "Security agents are limited to local, lab, or explicitly supplied project artifacts.",
                ("external_target",),
            )
        if action in CYBER_ACTIONS_REQUIRING_AUTHORIZATION:
            auth_result = _validate_authorization(action, payload)
            if auth_result is not None:
                return auth_result
        return PolicyResult(PolicyDecision.ALLOW, "Request is defensive or neutral.")


def default_tool_permissions() -> dict[str, ToolPermissionProfile]:
    """Default sandbox declarations for first-wave specialist agents."""

    read_only = ("read_workspace", "parse_files", "summarize")
    security_read_only = (*read_only, "static_analysis", "dependency_audit", "config_audit")
    permissions = {
        "orchestrator": ToolPermissionProfile("orchestrator", ("delegate", "summarize"), filesystem="none"),
        "planner": ToolPermissionProfile("planner", ("plan", "decompose"), filesystem="none"),
        "memory": ToolPermissionProfile("memory", ("memory_read", "memory_write"), filesystem="workspace_scoped"),
        "learning": ToolPermissionProfile("learning", ("summarize", "recommend_curriculum", "language_learning"), filesystem="workspace_scoped"),
        "quality_self_evaluation": ToolPermissionProfile("quality_self_evaluation", read_only, filesystem="workspace_read"),
        "code_architect": ToolPermissionProfile("code_architect", read_only, filesystem="workspace_read"),
        "backend": ToolPermissionProfile("backend", read_only, filesystem="workspace_read", may_modify_code=True),
        "frontend": ToolPermissionProfile("frontend", read_only, filesystem="workspace_read", may_modify_code=True),
        "mobile": ToolPermissionProfile("mobile", read_only, filesystem="workspace_read", may_modify_code=True),
        "devops": ToolPermissionProfile("devops", (*read_only, "config_audit"), filesystem="workspace_read", process_execution="disabled"),
        "code_reviewer": ToolPermissionProfile("code_reviewer", read_only, filesystem="workspace_read"),
        "test_qa": ToolPermissionProfile("test_qa", (*read_only, "run_local_tests"), filesystem="workspace_read", process_execution="local_tests_only"),
        "test_engineer": ToolPermissionProfile("test_engineer", (*read_only, "run_local_tests"), filesystem="workspace_read", process_execution="local_tests_only"),
        "documentation": ToolPermissionProfile("documentation", (*read_only, "draft_docs"), filesystem="workspace_read", may_modify_code=True),
        "llm_engineer": ToolPermissionProfile("llm_engineer", read_only, filesystem="workspace_read"),
        "ml_engineer": ToolPermissionProfile("ml_engineer", read_only, filesystem="workspace_read"),
        "data_engineer": ToolPermissionProfile("data_engineer", read_only, filesystem="workspace_read"),
        "research": ToolPermissionProfile("research", ("summarize", "parse_files"), filesystem="workspace_read", network="approved_sources_only"),
        "documentation_researcher": ToolPermissionProfile("documentation_researcher", ("summarize", "parse_files"), filesystem="workspace_read", network="approved_sources_only"),
        "trend_monitor": ToolPermissionProfile("trend_monitor", ("summarize",), filesystem="none", network="approved_sources_only"),
        "security_researcher": ToolPermissionProfile("security_researcher", (*security_read_only, "threat_model"), filesystem="workspace_read"),
        "secure_code_reviewer": ToolPermissionProfile("secure_code_reviewer", security_read_only, filesystem="workspace_read"),
        "vulnerability_research": ToolPermissionProfile("vulnerability_research", (*security_read_only, "cve_correlation"), filesystem="workspace_read"),
        "authorized_lab": ToolPermissionProfile(
            "authorized_lab",
            (*security_read_only, "authorized_lab", "local_fuzz_plan", "dry_run"),
            filesystem="lab_only",
            network="lab_only",
            process_execution="approved_lab_only",
        ),
        "infrastructure_security": ToolPermissionProfile("infrastructure_security", (*security_read_only, "config_audit"), filesystem="workspace_read"),
        "threat_intelligence": ToolPermissionProfile("threat_intelligence", (*read_only, "ioc_triage"), filesystem="workspace_read", network="approved_sources_only"),
        "sentinel": ToolPermissionProfile("sentinel", (*read_only, "local_telemetry"), filesystem="workspace_read"),
        "incident_commander": ToolPermissionProfile("incident_commander", ("delegate", "summarize", "audit_read"), filesystem="workspace_read"),
        "containment": ToolPermissionProfile("containment", ("session_revoke", "isolate_container", "preserve_logs"), filesystem="workspace_scoped", process_execution="approved_lab_only"),
        "deception": ToolPermissionProfile("deception", (*read_only, "canary_design"), filesystem="workspace_read"),
        "forensics": ToolPermissionProfile("forensics", (*read_only, "hash_evidence"), filesystem="workspace_read"),
        "threat_hunter": ToolPermissionProfile("threat_hunter", (*read_only, "log_query"), filesystem="workspace_read"),
        "red_team_simulator": ToolPermissionProfile("red_team_simulator", ("lab_simulation", "dry_run"), filesystem="lab_only", network="lab_only", process_execution="approved_lab_only"),
        "blue_team": ToolPermissionProfile("blue_team", (*security_read_only, "hardening"), filesystem="workspace_read"),
        "purple_team": ToolPermissionProfile("purple_team", (*security_read_only, "gap_analysis"), filesystem="workspace_read"),
        "exploit_validation": ToolPermissionProfile("exploit_validation", ("non_destructive_validation", "dry_run"), filesystem="lab_only", network="lab_only", process_execution="approved_lab_only"),
        "detection_engineering": ToolPermissionProfile("detection_engineering", (*read_only, "sigma_generate", "yara_generate"), filesystem="workspace_read"),
        "recovery": ToolPermissionProfile("recovery", (*read_only, "recovery_plan"), filesystem="workspace_read"),
        "anomaly_discovery": ToolPermissionProfile("anomaly_discovery", (*security_read_only, "local_fuzz_plan"), filesystem="workspace_read"),
    }
    for name in ("browser", "terminal", "github", "files", "automation"):
        permissions[name] = ToolPermissionProfile(name, ("status", "health_check"), filesystem="workspace_read")
    return permissions


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {_flatten_text(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)


def _payload_for_text_policy(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(payload)
    authorization = sanitized.get("authorization")
    if isinstance(authorization, dict):
        sanitized["authorization"] = {
            key: value
            for key, value in authorization.items()
            if key != "forbidden_actions"
        }
    return sanitized


def _targets_external_system(action: str, payload: dict[str, Any]) -> bool:
    if action not in {
        "create_local_fuzz_plan",
        "detect_anomalies",
        "review_code_security",
        "scan_dependencies",
        "correlate_cves",
        "register_lab_target",
        "evaluate_lab_action",
        "contain_incident",
        "simulate_lab_adversary",
        "validate_exploit_safely",
        "scan_lab_target",
        "run_local_fuzzing",
    }:
        return False
    target = str(payload.get("target", payload.get("url", "")))
    return _looks_external_target(target)


def _validate_authorization(action: str, payload: dict[str, Any]) -> PolicyResult | None:
    authorization = payload.get("authorization")
    if not isinstance(authorization, dict):
        return PolicyResult(
            PolicyDecision.DENY,
            "Cyber actions require an explicit authorization object.",
            ("missing_authorization",),
        )
    scope_type = str(authorization.get("scope_type", ""))
    if scope_type not in AUTHORIZED_SCOPE_TYPES:
        return PolicyResult(
            PolicyDecision.DENY,
            "Cyber actions are limited to local lab, CTF, owned asset, or workspace artifact scope.",
            ("invalid_scope_type",),
        )
    forbidden = set(str(item) for item in authorization.get("forbidden_actions", ()))
    allowed_actions = set(str(item) for item in authorization.get("allowed_actions", ()))
    if action in FORBIDDEN_CYBER_ACTIONS or action in forbidden:
        return PolicyResult(
            PolicyDecision.DENY,
            "Authorization includes actions that NELA never performs.",
            (action,),
        )
    if allowed_actions & FORBIDDEN_CYBER_ACTIONS:
        return PolicyResult(
            PolicyDecision.DENY,
            "Authorization cannot approve forbidden cyber action classes.",
            tuple(sorted(allowed_actions & FORBIDDEN_CYBER_ACTIONS)),
        )
    if action not in allowed_actions:
        return PolicyResult(
            PolicyDecision.DENY,
            "Cyber action is not listed in the approved authorization scope.",
            ("action_not_allowed",),
        )
    target = str(payload.get("target", ""))
    targets = set(str(item) for item in authorization.get("targets", ()))
    if target and targets and target not in targets:
        return PolicyResult(
            PolicyDecision.DENY,
            "Cyber target is outside the approved allowlist.",
            ("target_not_allowed",),
        )
    return None


def _looks_external_target(target: str) -> bool:
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https", "ssh", "tcp"}:
        host = parsed.hostname
        if host is None:
            return True
        return not _is_local_or_private_host(host)
    try:
        address = ipaddress.ip_address(target)
    except ValueError:
        return False
    return not (address.is_loopback or address.is_private)


def _is_local_or_private_host(host: str) -> bool:
    normalized = host.lower().strip("[]")
    if normalized in {"localhost", "127.0.0.1", "::1"} or normalized.endswith(".local"):
        return True
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        try:
            address = ipaddress.ip_address(socket.gethostbyname(normalized))
        except OSError:
            return False
    return address.is_loopback or address.is_private
```

### `agents/task_schema.py`

```python
"""Shared task and result schema for NELA specialist agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class AgentDomain(str, Enum):
    ORCHESTRATION = "orchestration"
    PLANNING = "planning"
    MEMORY = "memory"
    LEARNING = "learning"
    SOFTWARE = "software"
    QUALITY = "quality"
    SECURITY = "security"


class RiskLevel(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TaskArtifact:
    """A reusable output emitted by an agent."""

    kind: str
    name: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskFinding:
    """A structured observation from code, config, dependency, or anomaly review."""

    title: str
    severity: RiskLevel = RiskLevel.INFO
    category: str = "general"
    location: str | None = None
    evidence: str | None = None
    recommendation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity.value,
            "category": self.category,
            "location": self.location,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class AgentTask:
    """Agent-neutral task envelope used by the multi-agent layer."""

    objective: str
    action: str
    domain: AgentDomain
    target_agent: str | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    constraints: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class AgentWorkProduct:
    """Normalized specialist output for orchestration and tests."""

    summary: str
    findings: tuple[TaskFinding, ...] = ()
    artifacts: tuple[TaskArtifact, ...] = ()
    next_steps: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "artifacts": [
                {
                    "kind": artifact.kind,
                    "name": artifact.name,
                    "content": artifact.content,
                    "metadata": artifact.metadata,
                }
                for artifact in self.artifacts
            ],
            "next_steps": list(self.next_steps),
        }
```

### `permissions/models.py`

```python
"""Data models for NELA's Permission Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class PermissionTier(str, Enum):
    """Capability tiers used by every Agent action."""

    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"


class PermissionDecision(str, Enum):
    """Authorization outcome."""

    GRANTED = "granted"
    DENIED = "denied"
    CONFIRMATION_REQUIRED = "confirmation_required"
    AUTHENTICATION_REQUIRED = "authentication_required"
    LOCKED = "locked"
    KILL_SWITCH_ACTIVE = "kill_switch_active"
    SCOPE_VIOLATION = "scope_violation"
    CONFIRMATION_MISMATCH = "confirmation_mismatch"


@dataclass(frozen=True)
class Capability:
    """One action an Agent may expose."""

    action: str
    tier: PermissionTier
    description: str = ""
    scopes: tuple[str, ...] = ()
    actions: tuple[str, ...] = ()
    platforms: tuple[str, ...] = ()
    requires_confirmation: bool = False
    enabled: bool = True

    @property
    def needs_confirmation(self) -> bool:
        return self.requires_confirmation or self.tier in {PermissionTier.T2, PermissionTier.T3}


@dataclass(frozen=True)
class AgentManifest:
    """Declared capabilities for one Agent."""

    agent: str
    version: str = "1.0"
    capabilities: tuple[Capability, ...] = ()
    owner: str = "nela"

    def capability_for(self, action: str) -> Capability | None:
        for capability in self.capabilities:
            if capability.action == action or action in capability.actions:
                return capability
        return None

    def supports_capability(self, capability_id: str) -> bool:
        return any(capability.action == capability_id for capability in self.capabilities)


@dataclass(frozen=True)
class AuthenticatedUser:
    """Authenticated local user context."""

    user_id: str
    display_name: str = "Local user"
    authenticated: bool = True
    roles: tuple[str, ...] = ("owner",)


@dataclass(frozen=True)
class ScopeGrant:
    """One scoped permission inside a temporary session."""

    name: str
    values: tuple[str, ...] = ()

    def allows(self, value: str | None = None) -> bool:
        if not self.values:
            return True
        if value is None:
            return False
        return value in self.values


@dataclass(frozen=True)
class ScopedSession:
    """Time-limited permission session for higher-risk capabilities."""

    user_id: str
    allowed_agents: tuple[str, ...]
    allowed_tiers: tuple[PermissionTier, ...]
    scope_grants: tuple[ScopeGrant, ...] = ()
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=15))
    reason: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    active: bool = True

    def is_active(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return self.active and current <= self.expires_at

    def allows_agent(self, agent: str) -> bool:
        return "*" in self.allowed_agents or agent in self.allowed_agents

    def allows_tier(self, tier: PermissionTier) -> bool:
        return tier in self.allowed_tiers

    def has_scope(self, scope: str) -> bool:
        return any(grant.name == scope for grant in self.scope_grants)


@dataclass(frozen=True)
class PermissionRequest:
    """Runtime authorization request before one Agent command."""

    agent: str
    action: str
    capability: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    task_id: str | None = None
    plan_id: str | None = None
    command_id: str = field(default_factory=lambda: str(uuid4()))
    user: AuthenticatedUser | None = None
    confirmed: bool = False
    confirmation_action_hash: str | None = None
    confirmation_expires_at: datetime | None = None
    scoped_session_id: str | None = None

    @property
    def target(self) -> str | None:
        value = (
            self.payload.get("target")
            or self.payload.get("application")
            or self.payload.get("resource")
            or self.payload.get("path")
        )
        return str(value) if value is not None else None

    @property
    def capability_id(self) -> str:
        return self.capability or self.action


@dataclass(frozen=True)
class PermissionResult:
    """Authorization result consumed by the Dispatcher."""

    granted: bool
    decision: PermissionDecision
    tier: PermissionTier
    reason: str
    capability: Capability | None = None
    audit_id: str | None = None
    scope_session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "granted": self.granted,
            "decision": self.decision.value,
            "tier": self.tier.value,
            "reason": self.reason,
            "audit_id": self.audit_id,
            "scope_session_id": self.scope_session_id,
            "capability": self.capability.action if self.capability else None,
        }
```

### `permissions/registry.py`

```python
"""Capability Registry and built-in Agent manifests."""

from __future__ import annotations

from agents.base import BaseAgent
from permissions.models import AgentManifest, Capability, PermissionTier


class ManifestRegistrationError(ValueError):
    """Raised when a manifest cannot be registered safely."""


TIER_ORDER = {
    PermissionTier.T0: 0,
    PermissionTier.T1: 1,
    PermissionTier.T2: 2,
    PermissionTier.T3: 3,
    PermissionTier.T4: 4,
}

MINIMUM_CAPABILITY_TIERS = {
    "desktop.application.status": PermissionTier.T0,
    "desktop.application.launch": PermissionTier.T1,
    "desktop.application.focus": PermissionTier.T1,
    "desktop.application.close": PermissionTier.T2,
    "terminal.command.preview": PermissionTier.T0,
    "terminal.working_directory.get": PermissionTier.T0,
    "terminal.command.execute_allowlisted": PermissionTier.T2,
    "coding.repository.inspect": PermissionTier.T0,
    "coding.tests.run": PermissionTier.T1,
    "coding.diff.review": PermissionTier.T0,
    "coding.task.plan": PermissionTier.T0,
    "coding.files.write": PermissionTier.T2,
    "coding.git.commit": PermissionTier.T2,
    "cyber.passive.analysis": PermissionTier.T0,
}


class CapabilityRegistry:
    """Stores declared Agent manifests and resolves action capabilities."""

    def __init__(self, manifests: tuple[AgentManifest, ...] = ()) -> None:
        self._manifests: dict[str, AgentManifest] = {}
        self._baseline_manifests: dict[str, AgentManifest] = {manifest.agent: manifest for manifest in manifests}
        self.registration_audit: list[dict[str, object]] = []
        for manifest in manifests:
            self.register_manifest(manifest)

    def register_manifest(self, manifest: AgentManifest, replace: bool = False) -> None:
        self.validate_manifest(manifest)
        if manifest.agent in self._manifests and not replace:
            self.registration_audit.append({"agent": manifest.agent, "version": manifest.version, "result": "rejected_duplicate"})
            raise ManifestRegistrationError(f"Manifest for Agent '{manifest.agent}' already exists.")
        self._manifests[manifest.agent] = manifest
        self.registration_audit.append({"agent": manifest.agent, "version": manifest.version, "result": "registered"})

    def register_agent(self, agent: BaseAgent) -> None:
        manifest = getattr(agent, "permission_manifest", None)
        if manifest is not None:
            if manifest.agent != agent.name:
                self.registration_audit.append({"agent": agent.name, "version": getattr(manifest, "version", None), "result": "rejected_identity"})
                raise ManifestRegistrationError("Manifest agent identity must match the registered Agent.")
            if agent.name in self._baseline_manifests and agent.name in self._manifests:
                self.register_manifest(manifest, replace=True)
            else:
                self.register_manifest(manifest)
            return
        if agent.name not in self._manifests:
            self.register_manifest(AgentManifest(agent=agent.name))

    def unregister_agent(self, agent_name: str) -> None:
        baseline = self._baseline_manifests.get(agent_name)
        if baseline is not None:
            self._manifests[agent_name] = baseline
            return
        self._manifests.pop(agent_name, None)

    def manifest_for(self, agent_name: str) -> AgentManifest | None:
        return self._manifests.get(agent_name)

    def capability_for(self, agent_name: str, action: str) -> Capability | None:
        manifest = self.manifest_for(agent_name)
        return manifest.capability_for(action) if manifest else None

    def find_agents_for_capability(self, capability_id: str, platform: str | None = None) -> tuple[str, ...]:
        agents: list[str] = []
        for manifest in self._manifests.values():
            capability = manifest.capability_for(capability_id)
            if capability is None:
                continue
            if platform and capability.platforms and platform not in capability.platforms:
                continue
            agents.append(manifest.agent)
        return tuple(sorted(agents))

    def list_capabilities(self) -> tuple[str, ...]:
        capabilities = {
            capability.action
            for manifest in self._manifests.values()
            for capability in manifest.capabilities
        }
        return tuple(sorted(capabilities))

    def validate_manifest(self, manifest: AgentManifest) -> None:
        if not manifest.agent or not manifest.agent.strip():
            raise ManifestRegistrationError("Manifest must include an Agent ID.")
        if not manifest.version or not manifest.version.strip():
            raise ManifestRegistrationError("Manifest must include a version.")
        seen: set[str] = set()
        for capability in manifest.capabilities:
            if not capability.action:
                raise ManifestRegistrationError("Capability ID is required.")
            if capability.action in seen:
                raise ManifestRegistrationError(f"Duplicate capability '{capability.action}' in manifest.")
            minimum_tier = MINIMUM_CAPABILITY_TIERS.get(capability.action)
            if minimum_tier is not None and TIER_ORDER[capability.tier] < TIER_ORDER[minimum_tier]:
                raise ManifestRegistrationError(
                    f"Capability '{capability.action}' cannot claim lower than {minimum_tier.value}."
                )
            seen.add(capability.action)

    def manifests(self) -> tuple[AgentManifest, ...]:
        return tuple(self._manifests.values())


def default_capability_registry() -> CapabilityRegistry:
    """Create the default registry for current built-in Agents."""

    return CapabilityRegistry(
        (
            AgentManifest(
                agent="desktop",
                capabilities=(
                    Capability("desktop.application.status", PermissionTier.T0, "Read local application status.", actions=("is_application_running", "detect_application", "status_application", "wait_until_ready"), platforms=("macos",)),
                    Capability("desktop.application.launch", PermissionTier.T1, "Launch an allowlisted local application.", actions=("launch_application", "ensure_application"), platforms=("macos",)),
                    Capability("desktop.application.focus", PermissionTier.T1, "Focus an allowlisted local application.", actions=("bring_to_front", "switch_application", "focus_application"), platforms=("macos",)),
                    Capability(
                        "desktop.application.close",
                        PermissionTier.T2,
                        "Ask an allowlisted local application to quit.",
                        actions=("close_application", "quit_application"),
                        platforms=("macos",),
                        requires_confirmation=True,
                    ),
                ),
            ),
            AgentManifest(
                agent="voice",
                capabilities=(
                    Capability("voice.status", PermissionTier.T0, "Read voice status.", actions=("status",)),
                    Capability("voice.speak", PermissionTier.T1, "Speak local assistant output.", actions=("speak", "queue", "queue_speech", "flush_queue", "stop", "stop_speaking", "interrupt", "pause", "resume", "set_enabled", "configure_profile")),
                ),
            ),
            AgentManifest(
                agent="memory",
                capabilities=(
                    Capability("memory.write", PermissionTier.T1, "Store user-provided memory.", actions=("remember",)),
                    Capability("memory.read", PermissionTier.T0, "Read stored memory.", actions=("retrieve",)),
                ),
            ),
            AgentManifest(
                agent="spotify",
                capabilities=(
                    Capability("media.application.prepare", PermissionTier.T1, "Prepare Spotify placeholder Agent.", actions=("ensure_application",)),
                    Capability("media.application.status", PermissionTier.T0, "Wait for Spotify placeholder Agent.", actions=("wait_until_ready",)),
                    Capability("media.search", PermissionTier.T1, "Search media through placeholder Agent.", actions=("search_media",)),
                    Capability("media.play", PermissionTier.T1, "Start media playback through placeholder Agent.", actions=("play_media",)),
                ),
            ),
            AgentManifest(
                agent="terminal",
                capabilities=(
                    Capability("terminal.command.preview", PermissionTier.T0, "Preview an allowlisted terminal command.", actions=("preview",)),
                    Capability("terminal.working_directory.get", PermissionTier.T0, "Read terminal working directory.", actions=("get_working_directory",)),
                    Capability(
                        "terminal.command.execute_allowlisted",
                        PermissionTier.T2,
                        "Disabled foundation for future allowlisted command execution.",
                        actions=("execute_allowlisted",),
                        requires_confirmation=True,
                        enabled=False,
                    ),
                ),
            ),
            AgentManifest(
                agent="coding",
                capabilities=(
                    Capability("coding.repository.inspect", PermissionTier.T0, "Inspect repository metadata."),
                    Capability("coding.tests.run", PermissionTier.T1, "Run tests in an allowlisted repository."),
                    Capability("coding.diff.review", PermissionTier.T0, "Review diffs without modifying files."),
                    Capability("coding.task.plan", PermissionTier.T0, "Plan coding work without side effects."),
                    Capability("coding.files.write", PermissionTier.T2, "Disabled foundation for future file writes.", requires_confirmation=True, enabled=False),
                    Capability("coding.git.commit", PermissionTier.T2, "Disabled foundation for future commits.", requires_confirmation=True, enabled=False),
                ),
            ),
            _placeholder_manifest("browser"),
            _placeholder_manifest("files"),
            _placeholder_manifest("calendar"),
            _placeholder_manifest("gmail"),
            _placeholder_manifest("github"),
            _placeholder_manifest("codex"),
            _placeholder_manifest("automation"),
            _placeholder_manifest("vision"),
            _placeholder_manifest("claude"),
        )
    )


def _placeholder_manifest(agent: str) -> AgentManifest:
    return AgentManifest(
        agent=agent,
        capabilities=(
            Capability("status", PermissionTier.T0, "Read placeholder Agent status."),
            Capability("health_check", PermissionTier.T0, "Read placeholder Agent health."),
        ),
    )
```

### `permissions/engine.py`

```python
"""Permission Engine gateway for all Agent execution."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging

from agents.base import AgentResult, BaseAgent
from agents.process_isolation import IsolatedAgentProcessRunner, IsolatedProcessSupervisor
from core.events import Event, EventBus, EventTypes
from permissions.audit import AuditLog, AuditRecord, AuditWriteError
from permissions.confirmation import action_tuple_hash
from permissions.models import (
    AuthenticatedUser,
    PermissionDecision,
    PermissionRequest,
    PermissionResult,
    PermissionTier,
    ScopeGrant,
    ScopedSession,
)
from permissions.registry import CapabilityRegistry, default_capability_registry
from permissions.scope import validate_scopes


class PermissionEngine:
    """Single authorization gateway before Agent commands execute."""

    def __init__(
        self,
        events: EventBus | None = None,
        capability_registry: CapabilityRegistry | None = None,
        audit_log: AuditLog | None = None,
        default_user: AuthenticatedUser | None = None,
    ) -> None:
        self.events = events or EventBus()
        self.capabilities = capability_registry or default_capability_registry()
        self.audit_log = audit_log or AuditLog()
        self.default_user = default_user or AuthenticatedUser(user_id="local-owner", display_name="Local owner")
        self.kill_switch_active = False
        self.lock_mode_active = False
        self._scoped_sessions: dict[str, ScopedSession] = {}
        self._isolated_processes = IsolatedProcessSupervisor()
        self._logger = logging.getLogger("nela.permissions")

    def register_agent(self, agent: BaseAgent) -> None:
        self.capabilities.register_agent(agent)

    def unregister_agent(self, agent_name: str) -> None:
        self.capabilities.unregister_agent(agent_name)

    def authorize(self, request: PermissionRequest) -> PermissionResult:
        user = request.user or self.default_user
        capability = self.capabilities.capability_for(request.agent, request.capability_id)
        tier = capability.tier if capability else PermissionTier.T4

        if not user.authenticated:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.AUTHENTICATION_REQUIRED,
                reason="Authenticated user is required.",
            )

        if capability is None:
            return self._deny(
                request=request,
                user=user,
                tier=PermissionTier.T4,
                decision=PermissionDecision.DENIED,
                reason=f"No capability manifest allows {request.agent}.{request.capability_id}.",
            )

        if tier == PermissionTier.T4:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.DENIED,
                reason=f"{request.agent}.{request.action} is forbidden.",
                capability=capability,
            )

        if not capability.enabled:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.DENIED,
                reason=f"{request.agent}.{request.capability_id} is declared but disabled.",
                capability=capability,
            )

        if self.kill_switch_active and tier != PermissionTier.T0:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.KILL_SWITCH_ACTIVE,
                reason="Kill switch is active; only T0 reads are allowed.",
                capability=capability,
            )

        if self.lock_mode_active and tier != PermissionTier.T0:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.LOCKED,
                reason="Lock mode is active; only T0 reads are allowed.",
                capability=capability,
            )

        scoped_session = self._resolve_scoped_session(request)
        if tier == PermissionTier.T3:
            scope_result = self._validate_t3_scope(request, user, scoped_session)
            if scope_result is not None:
                return self._deny(
                    request=request,
                    user=user,
                    tier=tier,
                    decision=PermissionDecision.SCOPE_VIOLATION,
                    reason=scope_result,
                    capability=capability,
                )

        scope_result = validate_scopes(capability.scopes, request, scoped_session)
        if not scope_result.allowed:
            return self._deny(
                request=request,
                user=user,
                tier=tier,
                decision=PermissionDecision.SCOPE_VIOLATION,
                reason=scope_result.reason,
                capability=capability,
            )

        if capability.needs_confirmation:
            confirmation_error = self._confirmation_error(request, capability.action)
            if confirmation_error is not None:
                decision = (
                    PermissionDecision.CONFIRMATION_REQUIRED
                    if not request.confirmed
                    else PermissionDecision.CONFIRMATION_MISMATCH
                )
                result = self._record(
                    request=request,
                    user=user,
                    tier=tier,
                    decision=decision,
                    reason=confirmation_error,
                    granted=False,
                    capability=capability,
                    scope_session_id=scoped_session.id if scoped_session else None,
                )
                event_type = EventTypes.PERMISSION_REQUESTED if result.decision == PermissionDecision.CONFIRMATION_REQUIRED else EventTypes.PERMISSION_DENIED
                self._publish(event_type, request, result)
                return result

        result = self._record(
            request=request,
            user=user,
            tier=tier,
            decision=PermissionDecision.GRANTED,
            reason=f"{request.agent}.{request.action} authorized.",
            granted=True,
            capability=capability,
            scope_session_id=scoped_session.id if scoped_session else None,
        )
        self._publish(EventTypes.PERMISSION_GRANTED if result.granted else EventTypes.PERMISSION_DENIED, request, result)
        return result

    def record_action_result(self, request: PermissionRequest, result: AgentResult, permission: PermissionResult) -> None:
        record = AuditRecord(
            agent=request.agent,
            action=request.action,
            capability=permission.capability.action if permission.capability else request.action,
            tier=permission.tier,
            decision=PermissionDecision.GRANTED if result.success else PermissionDecision.DENIED,
            reason="Agent execution completed." if result.success else "Agent execution failed.",
            granted=permission.granted,
            user_id=(request.user or self.default_user).user_id,
            target=request.target,
            session_id=permission.scope_session_id,
            task_id=request.task_id,
            plan_id=request.plan_id,
            command_id=request.command_id,
            scope_session_id=permission.scope_session_id,
            result_success=result.success,
            result_message=result.message,
        )
        try:
            self.audit_log.append(record)
        except AuditWriteError:
            if permission.tier in {PermissionTier.T2, PermissionTier.T3}:
                raise
            self._logger.exception("audit_result_write_failed agent=%s action=%s", request.agent, request.action)
            return
        self.events.publish(
            Event(
                type=EventTypes.ACTION_EXECUTED,
                source="permissions.engine",
                payload={
                    "audit_id": record.id,
                    "agent": request.agent,
                    "action": request.action,
                    "tier": permission.tier.value,
                    "success": result.success,
                    "task_id": request.task_id,
                    "plan_id": request.plan_id,
                },
            )
        )

    def create_scoped_session(
        self,
        user: AuthenticatedUser | None = None,
        allowed_agents: tuple[str, ...] = (),
        allowed_tiers: tuple[PermissionTier, ...] = (),
        scope_grants: tuple[ScopeGrant, ...] = (),
        expires_at: datetime | None = None,
        reason: str = "",
    ) -> ScopedSession:
        authenticated_user = user or self.default_user
        session = ScopedSession(
            user_id=authenticated_user.user_id,
            allowed_agents=allowed_agents or ("*",),
            allowed_tiers=allowed_tiers or (PermissionTier.T0, PermissionTier.T1),
            scope_grants=scope_grants,
            expires_at=expires_at or datetime.now(timezone.utc) + timedelta(minutes=15),
            reason=reason,
        )
        self._scoped_sessions[session.id] = session
        return session

    def revoke_scoped_session(self, session_id: str) -> bool:
        return self._scoped_sessions.pop(session_id, None) is not None

    def scoped_sessions(self) -> tuple[ScopedSession, ...]:
        return tuple(self._scoped_sessions.values())

    def activate_kill_switch(self, reason: str = "") -> None:
        self.kill_switch_active = True
        revoked_sessions = self.revoke_all_scoped_sessions()
        terminated_processes = self._isolated_processes.terminate_all()
        self._logger.warning(
            "permission_kill_switch_active reason=%s revoked_sessions=%s terminated_processes=%s",
            reason,
            revoked_sessions,
            terminated_processes,
        )
        self.events.publish(
            Event(
                type=EventTypes.KILL_SWITCH_ACTIVATED,
                source="permissions.engine",
                payload={
                    "active": True,
                    "reason": reason,
                    "revoked_sessions": revoked_sessions,
                    "terminated_processes": terminated_processes,
                },
            )
        )

    def deactivate_kill_switch(self, reason: str = "") -> None:
        self.kill_switch_active = False
        self.events.publish(
            Event(
                type=EventTypes.KILL_SWITCH_DEACTIVATED,
                source="permissions.engine",
                payload={"active": False, "reason": reason},
            )
        )

    def set_lock_mode(self, active: bool, reason: str = "") -> None:
        self.lock_mode_active = active
        self.events.publish(
            Event(
                type=EventTypes.LOCK_MODE_CHANGED,
                source="permissions.engine",
                payload={"active": active, "reason": reason},
            )
        )

    def revoke_all_scoped_sessions(self) -> int:
        count = len(self._scoped_sessions)
        self._scoped_sessions.clear()
        return count

    def register_isolated_runner(self, runner: IsolatedAgentProcessRunner) -> str:
        return self._isolated_processes.register(runner)

    def unregister_isolated_runner(self, token: str) -> None:
        self._isolated_processes.unregister(token)

    def active_isolated_runner_count(self) -> int:
        return self._isolated_processes.active_count()

    def _validate_t3_scope(
        self,
        request: PermissionRequest,
        user: AuthenticatedUser,
        session: ScopedSession | None,
    ) -> str | None:
        if session is None:
            return "T3 actions require an active scoped session."
        if session.user_id != user.user_id:
            return "Scoped session belongs to a different user."
        if not session.allows_agent(request.agent):
            return f"Scoped session does not allow Agent '{request.agent}'."
        if not session.allows_tier(PermissionTier.T3):
            return "Scoped session does not allow T3 actions."
        return None

    def _resolve_scoped_session(self, request: PermissionRequest) -> ScopedSession | None:
        if not request.scoped_session_id:
            return None
        session = self._scoped_sessions.get(request.scoped_session_id)
        if session is None or not session.is_active():
            return None
        return session

    def _deny(
        self,
        request: PermissionRequest,
        user: AuthenticatedUser,
        tier: PermissionTier,
        decision: PermissionDecision,
        reason: str,
        capability=None,
    ) -> PermissionResult:
        result = self._record(
            request=request,
            user=user,
            tier=tier,
            decision=decision,
            reason=reason,
            granted=False,
            capability=capability,
        )
        event_type = EventTypes.SCOPE_VIOLATION if decision == PermissionDecision.SCOPE_VIOLATION else EventTypes.PERMISSION_DENIED
        self._publish(event_type, request, result)
        return result

    def _record(
        self,
        request: PermissionRequest,
        user: AuthenticatedUser,
        tier: PermissionTier,
        decision: PermissionDecision,
        reason: str,
        granted: bool,
        capability=None,
        scope_session_id: str | None = None,
    ) -> PermissionResult:
        record = AuditRecord(
            agent=request.agent,
            action=request.action,
            capability=capability.action if capability else request.capability_id,
            tier=tier,
            decision=decision,
            reason=reason,
            granted=granted,
            user_id=user.user_id,
            target=request.target,
            session_id=scope_session_id,
            task_id=request.task_id,
            plan_id=request.plan_id,
            command_id=request.command_id,
            scope_session_id=scope_session_id,
        )
        try:
            record = self.audit_log.append(record)
        except AuditWriteError:
            if tier in {PermissionTier.T2, PermissionTier.T3}:
                return PermissionResult(
                    granted=False,
                    decision=PermissionDecision.DENIED,
                    tier=tier,
                    reason="Audit write failed; action denied fail-closed.",
                    capability=capability,
                )
            self._logger.exception("audit_decision_write_failed agent=%s action=%s", request.agent, request.action)
            return PermissionResult(
                granted=granted,
                decision=decision,
                tier=tier,
                reason=f"{reason} Audit write failed; continuing under T0/T1 diagnostic policy.",
                capability=capability,
            )
        return PermissionResult(
            granted=granted,
            decision=decision,
            tier=tier,
            reason=reason,
            capability=capability,
            audit_id=record.id,
            scope_session_id=scope_session_id,
        )

    def _confirmation_error(self, request: PermissionRequest, capability_id: str) -> str | None:
        if not request.confirmed:
            return f"{request.agent}.{request.action} requires user confirmation."
        expires_at = _parse_datetime(request.confirmation_expires_at)
        if expires_at is None:
            return "Confirmation is missing a bound expiration."
        if datetime.now(timezone.utc) > expires_at:
            return "Confirmation expired before execution."
        expected = action_tuple_hash(
            agent=request.agent,
            capability=capability_id,
            action=request.action,
            target=request.target,
            parameters=request.payload,
            session=request.scoped_session_id,
            expires_at=expires_at,
        )
        if request.confirmation_action_hash != expected:
            return "Confirmation does not match the exact action tuple."
        return None

    def _publish(self, event_type: str, request: PermissionRequest, result: PermissionResult) -> None:
        self.events.publish(
            Event(
                type=event_type,
                source="permissions.engine",
                payload={
                    "agent": request.agent,
                    "action": request.action,
                    "task_id": request.task_id,
                    "plan_id": request.plan_id,
                    **result.to_dict(),
                },
            )
        )


def _parse_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            return None
    return None
```

### `permissions/scope.py`

```python
"""Reusable scope validation for Permission Engine decisions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from permissions.models import PermissionRequest, ScopedSession


PROTECTED_PATHS = (
    Path("~/.ssh").expanduser().resolve(),
    Path("~/Library/Keychains").expanduser().resolve(),
    Path("~/Library/Application Support").expanduser().resolve() / "com.apple.security",
)


@dataclass(frozen=True)
class ScopeValidationResult:
    allowed: bool
    reason: str
    normalized_target: str | None = None
    st_dev: int | None = None
    st_ino: int | None = None


def validate_scopes(
    scopes: tuple[str, ...],
    request: PermissionRequest,
    session: ScopedSession | None,
) -> ScopeValidationResult:
    for scope in scopes:
        if scope.startswith("filesystem."):
            result = _validate_filesystem_scope(scope, request, session)
            if not result.allowed:
                return result
            continue
        if session is None or not session.has_scope(scope):
            return ScopeValidationResult(False, f"Missing scoped session grant for scope '{scope}'.")
    return ScopeValidationResult(True, "Scope allowed.")


def _validate_filesystem_scope(
    scope: str,
    request: PermissionRequest,
    session: ScopedSession | None,
) -> ScopeValidationResult:
    target = request.payload.get("path") or request.payload.get("target")
    if not target:
        return ScopeValidationResult(False, f"Scope '{scope}' requires a path target.")

    try:
        canonical = _canonicalize_path(str(target))
    except OSError:
        return ScopeValidationResult(False, "Path target could not be canonicalized safely.")

    if _is_protected_path(canonical):
        return ScopeValidationResult(False, "Protected credential or security path is denied.", str(canonical))

    if session is None:
        return ScopeValidationResult(False, f"Scope '{scope}' requires an active scoped session.", str(canonical))

    allowed_roots = _allowed_values_for_scope(scope, session)
    if not allowed_roots:
        return ScopeValidationResult(False, f"Scope '{scope}' has no allowed roots.", str(canonical))

    for root in allowed_roots:
        try:
            root_path = _canonicalize_path(root)
        except OSError:
            continue
        if _is_within(canonical, root_path):
            return ScopeValidationResult(
                True,
                "Filesystem scope allowed.",
                str(canonical),
                *_file_identity(canonical),
            )

    return ScopeValidationResult(False, "Path target is outside the allowed filesystem scope.", str(canonical))


def _allowed_values_for_scope(scope: str, session: ScopedSession) -> tuple[str, ...]:
    for grant in session.scope_grants:
        if grant.name == scope:
            return grant.values
    return ()


def _canonicalize_path(path: str) -> Path:
    candidate = Path(path).expanduser()
    if candidate.exists():
        return candidate.resolve(strict=True)
    if candidate.is_symlink():
        return candidate.resolve(strict=False)
    parent = candidate.parent if str(candidate.parent) else Path(".")
    return parent.resolve(strict=True) / candidate.name


def _file_identity(path: Path) -> tuple[int | None, int | None]:
    try:
        stat_result = path.stat()
    except OSError:
        return None, None
    return stat_result.st_dev, stat_result.st_ino


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _is_protected_path(path: Path) -> bool:
    return any(_is_within(path, protected) or path == protected for protected in PROTECTED_PATHS)
```

### `permissions/audit.py`

```python
"""Append-only in-memory audit log for permission decisions."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
import hashlib
import json
import os
import re
from types import MappingProxyType
from typing import Any
from uuid import uuid4

from permissions.models import PermissionDecision, PermissionTier


class AuditWriteError(RuntimeError):
    """Raised when the audit sink cannot persist an entry."""


SENSITIVE_KEYS = {
    "password",
    "passcode",
    "token",
    "secret",
    "private_key",
    "api_key",
    "authorization",
    "message_body",
}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:ghp|github_pat|sk)-[A-Za-z0-9_\\-]{12,}"),
)


@dataclass(frozen=True)
class AuditRecord:
    """One permission or execution audit entry."""

    agent: str
    action: str
    tier: PermissionTier
    decision: PermissionDecision
    reason: str
    granted: bool
    capability: str | None = None
    session_id: str | None = None
    user_id: str | None = None
    target: str | None = None
    task_id: str | None = None
    plan_id: str | None = None
    command_id: str | None = None
    scope_session_id: str | None = None
    result_success: bool | None = None
    result_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    previous_hash: str | None = None
    entry_hash: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "target", redact(self.target) if self.target is not None else None)
        object.__setattr__(self, "result_message", redact(self.result_message) if self.result_message is not None else None)
        object.__setattr__(self, "metadata", MappingProxyType(redact(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.created_at.isoformat(),
            "event_id": self.id,
            "session_id": self.session_id,
            "user_identity_ref": self.user_id,
            "agent_id": self.agent,
            "capability": self.capability or self.action,
            "target": self.target,
            "permission_tier": self.tier.value,
            "policy_decision": self.decision.value,
            "authentication_result": self.metadata.get("authentication_result"),
            "confirmation_result": self.metadata.get("confirmation_result"),
            "execution_result": self.result_success,
            "error_code": self.metadata.get("error_code"),
            "rollback_result": self.metadata.get("rollback_result"),
            "previous_entry_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
            "granted": self.granted,
            "reason": self.reason,
            "task_id": self.task_id,
            "plan_id": self.plan_id,
            "command_id": self.command_id,
            "scope_session_id": self.scope_session_id,
            "result_message": self.result_message,
            "metadata": dict(self.metadata),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


class AuditLog:
    """Small append-only audit store.

    This is intentionally local and in-memory for Sprint 2. A durable writer can
    replace it later without changing the Permission Engine API.
    """

    def __init__(self, sink: Any | None = None) -> None:
        self._records: list[AuditRecord] = []
        self._sink = sink

    def append(self, record: AuditRecord) -> AuditRecord:
        previous_hash = self._records[-1].entry_hash if self._records else None
        chained = replace(record, previous_hash=previous_hash, entry_hash=None)
        chained = replace(chained, entry_hash=entry_hash(chained))
        if self._sink is not None:
            try:
                self._write_to_sink(chained)
            except Exception as error:
                raise AuditWriteError("Audit write failed.") from error
        self._records.append(chained)
        return chained

    def _write_to_sink(self, record: AuditRecord) -> None:
        line = record.to_json()
        if callable(self._sink):
            self._sink(line)
            return
        self._sink.write(line + "\n")
        self._sink.flush()
        os.fsync(self._sink.fileno())

    def records(self) -> tuple[AuditRecord, ...]:
        return tuple(self._records)

    def query(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        capability: str | None = None,
        agent: str | None = None,
        result: bool | None = None,
        session_id: str | None = None,
    ) -> tuple[AuditRecord, ...]:
        output = []
        for record in self._records:
            if start and record.created_at < start:
                continue
            if end and record.created_at > end:
                continue
            if capability and (record.capability or record.action) != capability:
                continue
            if agent and record.agent != agent:
                continue
            if result is not None and record.result_success is not result:
                continue
            if session_id and record.session_id != session_id and record.scope_session_id != session_id:
                continue
            output.append(record)
        return tuple(output)

    def clear(self) -> None:
        self._records.clear()

    def verify_chain(self) -> bool:
        previous_hash = None
        for record in self._records:
            if record.previous_hash != previous_hash:
                return False
            if record.entry_hash != entry_hash(replace(record, entry_hash=None)):
                return False
            previous_hash = record.entry_hash
        return True


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            normalized = str(key).lower()
            if any(sensitive in normalized for sensitive in SENSITIVE_KEYS):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact(item)
        return redacted
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        output = value
        for pattern in SECRET_PATTERNS:
            output = pattern.sub("[REDACTED]", output)
        return output
    return value


def entry_hash(record: AuditRecord) -> str:
    payload = record.to_dict()
    payload["entry_hash"] = None
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
```

### `permissions/confirmation.py`

```python
"""Confirmation binding helpers.

Confirmations are bound to the exact action tuple they approve. A confirmation
for one Agent/action/target cannot be replayed for a different command.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any


IGNORED_PARAMETER_KEYS = {
    "confirmed",
    "confirmation_action_hash",
    "confirmation_expires_at",
    "task_id",
    "plan_id",
    "timeout_seconds",
}


def action_tuple_hash(
    *,
    agent: str | None,
    capability: str | None,
    action: str,
    target: str | None,
    parameters: dict[str, Any] | None = None,
    session: str | None = None,
    expires_at: datetime | None = None,
) -> str:
    payload = {
        "agent": agent,
        "capability": capability,
        "action": action,
        "target": target,
        "parameters": _stable_parameters(parameters or {}),
        "session": session,
        "expires_at": expires_at.astimezone(timezone.utc).isoformat() if expires_at else None,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stable_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    return {
        key: parameters[key]
        for key in sorted(parameters)
        if key not in IGNORED_PARAMETER_KEYS
    }
```

### `brain/dispatcher.py`

```python
"""Agent dispatcher for event-driven task delegation."""

from __future__ import annotations

import logging
import time

from agents.base import AgentCommand, AgentResult, AgentState, BaseAgent
from agents.process_isolation import IsolatedAgentProcessRunner, ProcessOutcome
from agents.registry import AgentRegistry
from brain.planner import Task
from core.events import Event, EventBus, EventTypes
from permissions import AuthenticatedUser, PermissionEngine, PermissionRequest, PermissionResult, PermissionTier


class AgentDispatcher:
    """Delegates tasks to registered Agents while publishing lifecycle events."""

    def __init__(
        self,
        events: EventBus,
        registry: AgentRegistry | None = None,
        permission_engine: PermissionEngine | None = None,
        authenticated_user: AuthenticatedUser | None = None,
    ) -> None:
        self.events = events
        self.registry = registry or AgentRegistry()
        self.permission_engine = permission_engine or PermissionEngine(events=events)
        self.authenticated_user = authenticated_user or self.permission_engine.default_user
        self.cancelled_tasks: set[str] = set()
        self.logger = logging.getLogger("nela.agents")

    def register_agent(self, agent: BaseAgent) -> None:
        self.registry.register(agent)
        self.permission_engine.register_agent(agent)
        self.events.publish(
            Event(
                type=EventTypes.AGENT_STATUS_CHANGED,
                source="brain.dispatcher",
                payload={"agent": agent.name, "status": agent.status().value},
            )
        )

    def unregister_agent(self, name: str) -> bool:
        removed = self.registry.unregister(name)
        if removed:
            self.permission_engine.unregister_agent(name)
            self.events.publish(
                Event(
                    type=EventTypes.AGENT_STATUS_CHANGED,
                    source="brain.dispatcher",
                    payload={"agent": name, "status": "unregistered"},
                )
            )
        return removed

    def discover_agents(self) -> tuple[str, ...]:
        return self.registry.names()

    def health_check(self) -> dict[str, AgentResult]:
        return self.registry.health_check()

    def cancel_task(self, task_id: str) -> None:
        self.cancelled_tasks.add(task_id)
        self.events.publish(
            Event(
                type=EventTypes.TASK_CANCELLED,
                source="brain.dispatcher",
                payload={"task_id": task_id},
            )
        )

    def dispatch(self, task: Task, plan_id: str) -> AgentResult:
        if task.id in self.cancelled_tasks:
            return self._cancelled(task, plan_id)
        if task.target_agent and self.registry.get(task.target_agent) is None:
            return self._agent_unavailable(task, plan_id, f"Agent '{task.target_agent}' is not registered.")

        target_agent, permission_request, permission = self._authorize_task_route(task, plan_id)
        if target_agent is None or permission_request is None or permission is None:
            return self._agent_unavailable(task, plan_id, "No authorized Agent is available for this capability.")
        if not permission.granted:
            return self._permission_denied(task, plan_id, permission.reason, permission.to_dict())
        agent = self.registry.get(target_agent)
        if not agent:
            return self._agent_unavailable(task, plan_id, f"Agent '{target_agent}' is not registered.")

        self.events.publish(
            Event(
                type=EventTypes.TASK_DISPATCHED,
                source="brain.dispatcher",
                payload={"plan_id": plan_id, "task_id": task.id, "agent": target_agent, "capability": permission_request.capability_id},
            )
        )

        if agent.status() in {AgentState.CREATED, AgentState.STOPPED}:
            agent.initialize()

        attempts = 0
        last_result = AgentResult(False, "Task was not executed.")
        while attempts < task.retry_policy.max_attempts:
            if task.id in self.cancelled_tasks:
                return self._cancelled(task, plan_id)
            if self._emergency_stop_active(permission):
                last_result = self._emergency_stop_result(task, plan_id, last_result, attempts)
                break

            attempts += 1

            self.events.publish(
                Event(
                    type=EventTypes.TASK_STARTED,
                    source="brain.dispatcher",
                    payload={"plan_id": plan_id, "task_id": task.id, "attempt": attempts},
                )
            )

            attempt_started_at = time.monotonic()
            command = AgentCommand(
                action=task.action,
                payload={
                    **task.payload,
                    "task_id": task.id,
                    "plan_id": plan_id,
                    "timeout_seconds": task.timeout_seconds,
                },
                id=permission_request.command_id,
            )
            try:
                last_result = self._execute_agent(agent, command, task, permission, plan_id)
            except Exception as error:  # Defensive boundary for all current and future Agents.
                elapsed = time.monotonic() - attempt_started_at
                last_result = AgentResult(
                    False,
                    f"Agent '{task.target_agent}' raised {error.__class__.__name__}.",
                    {
                        "task_id": task.id,
                        "plan_id": plan_id,
                        "agent": target_agent,
                        "error_type": error.__class__.__name__,
                        "error": str(error),
                        "elapsed_seconds": elapsed,
                    },
                )
                self.logger.exception("agent_execute_failed task_id=%s agent=%s", task.id, target_agent)
                break
            elapsed = time.monotonic() - attempt_started_at
            timed_out = task.timeout_seconds is not None and elapsed > task.timeout_seconds
            if last_result.data.get("isolated_outcome") == ProcessOutcome.TIMED_OUT.value:
                timed_out = False
            if timed_out and not last_result.success:
                last_result = AgentResult(False, "Task timed out.", {"elapsed_seconds": elapsed})
            elif timed_out:
                last_result = AgentResult(
                    True,
                    last_result.message,
                    {
                        **last_result.data,
                        "elapsed_seconds": elapsed,
                        "timeout_exceeded": True,
                    },
                )
            if last_result.success:
                last_result = self._annotate_permission_boundary(last_result, permission)
            if self._emergency_stop_active(permission):
                last_result = self._emergency_stop_result(task, plan_id, last_result, attempts)
                break

            if last_result.success:
                self.permission_engine.record_action_result(permission_request, last_result, permission)
                self.events.publish(
                    Event(
                        type=EventTypes.TASK_COMPLETED,
                        source="brain.dispatcher",
                        payload={
                            "plan_id": plan_id,
                            "task_id": task.id,
                            "agent": target_agent,
                            "capability": permission_request.capability_id,
                            "attempts": attempts,
                            "elapsed_seconds": elapsed,
                        },
                    )
                )
                return last_result

            if attempts < task.retry_policy.max_attempts and task.retry_policy.backoff_seconds:
                time.sleep(task.retry_policy.backoff_seconds)

        self.logger.error("task_failed task_id=%s agent=%s", task.id, target_agent)
        self.permission_engine.record_action_result(permission_request, last_result, permission)
        self.events.publish(
            Event(
                type=EventTypes.TASK_FAILED,
                source="brain.dispatcher",
                payload={
                    "plan_id": plan_id,
                    "task_id": task.id,
                    "agent": target_agent,
                    "message": last_result.message,
                    "attempts": attempts,
                },
            )
        )
        return last_result

    def _authorize_task_route(
        self,
        task: Task,
        plan_id: str,
    ) -> tuple[str | None, PermissionRequest | None, PermissionResult | None]:
        if task.target_agent:
            request = self._permission_request(task.target_agent, task, plan_id)
            return task.target_agent, request, self.permission_engine.authorize(request)
        if not task.capability:
            return None, None, None

        candidates = self.permission_engine.capabilities.find_agents_for_capability(task.capability, platform="macos")
        first_denial: tuple[str, PermissionRequest, PermissionResult] | None = None
        for candidate in candidates:
            if self.registry.get(candidate) is None:
                continue
            request = self._permission_request(candidate, task, plan_id)
            permission = self.permission_engine.authorize(request)
            if permission.granted:
                return candidate, request, permission
            if first_denial is None:
                first_denial = (candidate, request, permission)
        if first_denial is not None:
            return first_denial
        return None, None, None

    def _permission_request(self, agent_name: str, task: Task, plan_id: str) -> PermissionRequest:
        return PermissionRequest(
            agent=agent_name,
            action=task.action,
            capability=task.capability or _optional_string(task.payload.get("capability")),
            payload=task.payload,
            task_id=task.id,
            plan_id=plan_id,
            user=self.authenticated_user,
            confirmed=bool(task.payload.get("confirmed", False)),
            confirmation_action_hash=_optional_string(task.payload.get("confirmation_action_hash")),
            confirmation_expires_at=task.payload.get("confirmation_expires_at"),
            scoped_session_id=_optional_string(task.payload.get("scoped_session_id")),
        )

    def _execute_agent(
        self,
        agent: BaseAgent,
        command: AgentCommand,
        task: Task,
        permission: PermissionResult,
        plan_id: str,
    ) -> AgentResult:
        if not self._requires_isolation(task, permission):
            return agent.execute(command)

        runner = IsolatedAgentProcessRunner(
            timeout_seconds=task.timeout_seconds or 30.0,
            before_terminate=self.permission_engine.revoke_all_scoped_sessions,
        )
        runner_token = self.permission_engine.register_isolated_runner(runner)
        try:
            if self._emergency_stop_active(permission):
                runner.terminate()
                return self._emergency_stop_result(task, plan_id, AgentResult(False, "Task was not executed."), 0)
            return self._agent_result_from_process(runner.run(_execute_agent_command, agent, command))
        finally:
            self.permission_engine.unregister_isolated_runner(runner_token)

    def _requires_isolation(self, task: Task, permission: PermissionResult) -> bool:
        return (
            permission.tier in {PermissionTier.T2, PermissionTier.T3}
            or bool(task.payload.get("requires_isolation"))
            or bool(task.payload.get("isolate"))
        )

    def _emergency_stop_active(self, permission: PermissionResult) -> bool:
        return permission.tier != PermissionTier.T0 and (
            self.permission_engine.kill_switch_active or self.permission_engine.lock_mode_active
        )

    def _emergency_stop_result(
        self,
        task: Task,
        plan_id: str,
        last_result: AgentResult,
        attempts: int,
    ) -> AgentResult:
        if self.permission_engine.kill_switch_active:
            message = "Kill switch is active; task execution stopped."
        else:
            message = "Lock mode is active; task execution stopped."
        return AgentResult(
            False,
            last_result.message if attempts else message,
            {
                **last_result.data,
                "task_id": task.id,
                "plan_id": plan_id,
                "kill_switch_active": self.permission_engine.kill_switch_active,
                "lock_mode_active": self.permission_engine.lock_mode_active,
                "retry_blocked": attempts > 0,
            },
        )

    def _agent_result_from_process(self, process_result) -> AgentResult:
        result = process_result.data.get("result")
        if process_result.outcome == ProcessOutcome.COMPLETED and isinstance(result, AgentResult):
            return AgentResult(
                result.success,
                result.message,
                {
                    **result.data,
                    "isolated": True,
                    "isolated_outcome": process_result.outcome.value,
                    "worker_exit_code": process_result.exit_code,
                },
            )
        return AgentResult(
            False,
            process_result.message,
            {
                **process_result.data,
                "isolated": True,
                "isolated_outcome": process_result.outcome.value,
                "worker_exit_code": process_result.exit_code,
            },
        )

    def _agent_unavailable(self, task: Task, plan_id: str, message: str) -> AgentResult:
        result = AgentResult(False, message, {"task_id": task.id, "plan_id": plan_id})
        self.events.publish(
            Event(
                type=EventTypes.AGENT_UNAVAILABLE,
                source="brain.dispatcher",
                payload={
                    "plan_id": plan_id,
                    "task_id": task.id,
                    "agent": task.target_agent,
                    "capability": task.capability,
                    "message": message,
                },
            )
        )
        return result

    def _permission_denied(self, task: Task, plan_id: str, message: str, details: dict[str, object]) -> AgentResult:
        result = AgentResult(False, message, {"task_id": task.id, "plan_id": plan_id, **details})
        if details.get("decision") == "confirmation_required":
            return result
        self.events.publish(
            Event(
                type=EventTypes.TASK_FAILED,
                source="brain.dispatcher",
                payload={
                    "plan_id": plan_id,
                    "task_id": task.id,
                    "agent": task.target_agent,
                    "message": message,
                    "permission": details,
                },
            )
        )
        return result

    def _cancelled(self, task: Task, plan_id: str) -> AgentResult:
        result = AgentResult(False, "Task was cancelled.", {"task_id": task.id, "plan_id": plan_id})
        self.events.publish(
            Event(
                type=EventTypes.TASK_CANCELLED,
                source="brain.dispatcher",
                payload={"plan_id": plan_id, "task_id": task.id},
            )
        )
        return result


    def _annotate_permission_boundary(self, result: AgentResult, permission: PermissionResult) -> AgentResult:
        """Attach permission/sandbox metadata to successful Agent results."""

        data = {
            **result.data,
            "permission_tier": permission.tier.value,
        }
        if permission.scope_session_id:
            data["scope_session_id"] = permission.scope_session_id
        if permission.tier.value in {"T3", "T4"}:
            data["isolated"] = True
        return AgentResult(result.success, result.message, data)


def _optional_string(value: object) -> str | None:
    return str(value) if value else None


def _execute_agent_command(agent: BaseAgent, command: AgentCommand) -> AgentResult:
    return agent.execute(command)
```

### `brain/intent_router.py`

```python
"""Intent recognition for NELA OS."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from brain.applications import resolve_application_alias


class Priority(str, Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"


@dataclass(frozen=True)
class Intent:
    """Structured representation of a user request."""

    action: str
    raw_text: str
    confidence: float
    application: str | None = None
    resource: str | None = None
    priority: Priority = Priority.NORMAL
    parameters: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False

    @property
    def name(self) -> str:
        return self.action

    @property
    def target_agent(self) -> str | None:
        if self.application:
            return _slug(self.application)
        if self.parameters.get("domain"):
            return str(self.parameters["domain"])
        return None


@dataclass(frozen=True)
class IntentPattern:
    """Configurable pattern for turning text into an intent."""

    action: str
    keywords: tuple[str, ...]
    domain: str | None = None
    requires_confirmation: bool = False


DEFAULT_PATTERNS: tuple[IntentPattern, ...] = (
    IntentPattern("Greeting", ("שלום", "היי", "הי", "בוקר טוב", "ערב טוב", "hello", "hi")),
    IntentPattern("Thanks", ("תודה", "תודה רבה", "thanks", "thank you")),
    IntentPattern(
        "SecurityReview",
        ("סקירת אבטחה", "בדיקת אבטחה", "תבדקי אבטחה", "תבדקי את הקוד לאבטחה", "security review", "secure code review"),
        domain="secure_code_reviewer",
    ),
    IntentPattern("ThreatModel", ("מודל איומים", "threat model"), domain="secure_code_reviewer"),
    IntentPattern(
        "CyberLabStatus",
        ("מצב מעבדת סייבר", "סטטוס סייבר", "מצב הסייבר", "cyber lab status"),
        domain="authorized_lab",
    ),
    IntentPattern(
        "CyberLabRegisterTarget",
        ("תרשמי יעד מעבדה", "תוסיפי יעד מעבדה", "register lab target"),
        domain="authorized_lab",
    ),
    IntentPattern(
        "LocalFuzzPlan",
        ("תוכנית fuzz", "תכנון fuzz", "תכיני fuzz", "local fuzz plan", "fuzz plan"),
        domain="anomaly_discovery",
    ),
    IntentPattern(
        "SecurityCapabilitiesQuestion",
        (
            "מה את יודעת בסייבר",
            "מה את יודעת על סייבר",
            "מה את יודעת באבטחה",
            "מה את יודעת על אבטחה",
            "מה יכולות האבטחה שלך",
            "יכולות אבטחה",
            "יכולות סייבר",
            "cyber capabilities",
        ),
    ),
    IntentPattern(
        "CyberDefenseSweep",
        (
            "תעשי הגנה",
            "תתחילי להגן",
            "תגני",
            "הגני",
            "תבני מערך סייבר",
            "תבני מערך הגנה",
            "מערך סייבר",
            "מערך הגנה",
            "בדיקה של אבטחה",
            "בדיקת הגנה",
            "בדיקה הגנתית",
            "בדיקה אבטחתית",
            "בדיקת סייבר",
            "בדיקת ממצאי אבטחה",
            "תעשי בדיקת סייבר",
            "תעשי בדיקה של סייבר",
            "defense sweep",
            "defense check",
            "security posture",
            "protect",
        ),
        domain="cyber_defense",
    ),
    IntentPattern(
        "CapabilitiesQuestion",
        (
            "מה את יודעת לעשות",
            "מה את יכולה לעשות",
            "איך את יכולה לעזור",
            "איזה יכולות יש לך",
            "מה היכולות שלך",
            "help",
            "capabilities",
        ),
    ),
    IntentPattern(
        "AgentStatusQuestion",
        (
            "איזה סוכנים מחוברים",
            "מי מחובר",
            "מה מצב הסוכנים",
            "סטטוס סוכנים",
            "agent status",
            "status",
        ),
    ),
    IntentPattern(
        "HumanStatusQuestion",
        ("מה מצב", "מה המצב", "מה קורה", "איך הולך", "איך את", "מה איתך", "how are you"),
    ),
    IntentPattern("IdentityQuestion", ("מי את", "מה את", "מי את נלה", "ספרי על עצמך", "who are you")),
    IntentPattern("LearnTopic", ("תלמדי", "למדי", "תלמדני", "learn about", "study"), domain="learning"),
    IntentPattern("Remember", ("remember", "save this", "learn this", "תזכרי", "תזכור", "תשמרי")),
    IntentPattern("CloseApplication", ("close", "quit", "תסגרי", "סגרי", "לסגור"), requires_confirmation=True),
    IntentPattern("SwitchApplication", ("switch to", "focus", "bring to front", "תעברי", "לעבור אל")),
    IntentPattern("StopTask", ("stop", "cancel", "עצור", "תעצרי", "בטלי"), requires_confirmation=True),
    IntentPattern("PlayMedia", ("play", "music", "playlist", "song", "תנגני", "מוזיקה", "פלייליסט", "שיר")),
    IntentPattern("OpenApplication", ("open", "launch", "start", "תפתחי", "פתחי", "לפתוח")),
    IntentPattern("Search", ("search", "find", "look up", "חפשי", "תחפשי", "מצא")),
    IntentPattern("CreateItem", ("create", "make", "draft", "write", "צרי", "תכתבי", "כתבי")),
)


class IntentRouter:
    """Converts text into structured, agent-neutral intents."""

    def __init__(self, patterns: tuple[IntentPattern, ...] = DEFAULT_PATTERNS) -> None:
        self._patterns = patterns

    def classify(self, text: str, context: dict[str, Any] | None = None) -> Intent:
        normalized = _normalize(text)
        priority = _detect_priority(normalized)
        taught_response = _extract_teach_response(text)
        if taught_response is not None:
            return Intent(
                action="TeachResponse",
                raw_text=text,
                confidence=0.88,
                priority=priority,
                parameters={**taught_response, "domain": "learning"},
            )

        pattern = self._match_pattern(normalized)
        application = _extract_application(text)
        resource = _extract_resource(text)
        parameters: dict[str, Any] = {}
        if pattern and pattern.domain:
            parameters["domain"] = pattern.domain
        if pattern and pattern.action == "LearnTopic":
            parameters["topic"] = _extract_learning_topic(text)
        if _looks_like_follow_up(normalized) and context:
            parameters["follow_up_to"] = context.get("last_intent")

        if pattern:
            return Intent(
                action=pattern.action,
                raw_text=text,
                confidence=0.82,
                application=resolve_application_alias(application),
                resource=resource or _extract_url(text),
                priority=priority,
                parameters=parameters,
                requires_confirmation=pattern.requires_confirmation,
            )

        if _looks_like_question(normalized):
            return Intent(
                action="GeneralQuestion",
                raw_text=text,
                confidence=0.62,
                application=resolve_application_alias(application),
                resource=resource or _extract_url(text),
                priority=priority,
                parameters=parameters,
            )

        return Intent(
            action="GeneralRequest",
            raw_text=text,
            confidence=0.45,
            application=resolve_application_alias(application),
            resource=resource or _extract_url(text),
            priority=priority,
            parameters=parameters,
        )

    def _match_pattern(self, normalized: str) -> IntentPattern | None:
        for pattern in self._patterns:
            if pattern.action == "HumanStatusQuestion":
                if any(_is_exact_short_phrase(normalized, keyword) for keyword in pattern.keywords):
                    return pattern
                continue
            if any(_contains_keyword(normalized, keyword) for keyword in pattern.keywords):
                return pattern
        return None


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _detect_priority(normalized: str) -> Priority:
    if any(word in normalized for word in ("urgent", "immediately", "asap", "now")):
        return Priority.HIGH
    if any(word in normalized for word in ("later", "when you can")):
        return Priority.LOW
    return Priority.NORMAL


def _extract_application(text: str) -> str | None:
    hebrew_match = re.search(
        r"(?:תפתחי|פתחי|לפתוח|תסגרי|סגרי|לסגור|תעברי|לעבור)\s+(?:את|אל|ל)?\s*([A-Za-zא-ת][\wא-ת-]*(?:\s+[A-Za-zא-ת][\wא-ת-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if hebrew_match:
        candidate = _title_name(_trim_application_name(hebrew_match.group(1).strip()))
        return None if _is_generic_application_word(candidate) else candidate
    match = re.search(
        r"\b(?:open|launch|start|close|quit|focus)\s+([A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        candidate = _title_name(_trim_application_name(match.group(1).strip()))
        return None if _is_generic_application_word(candidate) else candidate
    match = re.search(
        r"\b(?:switch|bring)\s+(?:to\s+)?([A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        candidate = _title_name(_trim_application_name(match.group(1).strip()))
        return None if _is_generic_application_word(candidate) else candidate
    match = re.search(
        r"\bin\s+([A-Z][\w-]*(?:\s+[A-Z][\w-]*)?)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        candidate = _title_name(_trim_application_name(match.group(1).strip()))
        return None if _is_generic_application_word(candidate) else candidate
    return None


def _extract_resource(text: str) -> str | None:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted:
        return quoted.group(1).strip()
    playlist = re.search(r"\bmy\s+([\w\s-]+?)\s+playlist\b", text, flags=re.IGNORECASE)
    if playlist:
        return playlist.group(1).strip()
    return None


def _extract_url(text: str) -> str | None:
    match = re.search(r"\b(?:https?://|localhost:)\S+", text, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(0).rstrip(".,;!?")


def _extract_teach_response(text: str) -> dict[str, str] | None:
    patterns = (
        r"(?:תלמדי|למדי|תלמדני).*?כשאני אומר(?:ת)?\s+(.+?)\s+(?:תעני|תגידי|תאמרי)\s+(.+)",
        r"כשאני אומר(?:ת)?\s+(.+?)\s+(?:תעני|תגידי|תאמרי)\s+(.+)",
        r"(?:learn|teach).*?when i say\s+(.+?)\s+(?:answer|reply|say)\s+(.+)",
        r"(?:learn response|teach response|למדי תשובה|תלמדי תשובה)\s*:\s*(.+?)\s*=>\s*(.+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        trigger = _strip_teach_delimiters(match.group(1))
        response = _strip_teach_delimiters(match.group(2))
        if trigger and response:
            return {"trigger": trigger, "response": response}
    return None


def _strip_teach_delimiters(value: str) -> str:
    return value.strip(" \t\n\r\"'׳״.,;:!?")


def _extract_learning_topic(text: str) -> str:
    patterns = (
        r"(?:נלה[,\s]+)?(?:תלמדי|למדי|תלמדני)\s+(.+)",
        r"(?:learn about|study)\s+(.+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            topic = _strip_teach_delimiters(match.group(1))
            if topic:
                return topic
    return "הנושא שביקשת"


def _looks_like_follow_up(normalized: str) -> bool:
    return normalized.startswith(("also ", "then ", "and ", "do that", "same "))


def _looks_like_question(normalized: str) -> bool:
    question_words = (
        "what",
        "who",
        "how",
        "why",
        "when",
        "where",
        "which",
        "can you",
        "do you",
        "מה",
        "מי",
        "איך",
        "למה",
        "מתי",
        "איפה",
        "איזה",
        "האם",
        "אפשר",
    )
    return normalized.endswith("?") or normalized.startswith(question_words)


def _contains_keyword(normalized: str, keyword: str) -> bool:
    escaped = re.escape(_normalize(keyword))
    return re.search(rf"(?<!\w){escaped}(?!\w)", normalized) is not None


def _is_exact_short_phrase(normalized: str, keyword: str) -> bool:
    value = normalized.strip(" ?!.,;:׳״\"'")
    expected = _normalize(keyword).strip(" ?!.,;:׳״\"'")
    return value == expected


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _title_name(value: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in value.split())


def _trim_application_name(value: str) -> str:
    stopwords = {"and", "then", "to", "with", "for", "play", "search", "open", "front"}
    parts = []
    for part in value.split():
        if part.lower() in stopwords:
            break
        parts.append(part)
    return " ".join(parts) if parts else value


def _is_generic_application_word(value: str) -> bool:
    return _normalize(value) in {"app", "application", "אפליקציה", "יישום"}
```

### `brain/planner.py`

```python
"""Task planning for NELA OS."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any
from uuid import uuid4

from brain.intent_router import Intent


class TaskMode(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class TaskStatus(str, Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 1
    backoff_seconds: float = 0.0


@dataclass(frozen=True)
class Task:
    description: str
    action: str
    capability: str | None = None
    target_agent: str | None = None
    mode: TaskMode = TaskMode.SEQUENTIAL
    depends_on: tuple[str, ...] = ()
    condition: str | None = None
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_seconds: float | None = 30.0
    payload: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid4()))

    def with_status(self, status: TaskStatus) -> "Task":
        return replace(self, status=status)


@dataclass(frozen=True)
class Plan:
    intent: Intent
    tasks: tuple[Task, ...]
    id: str = field(default_factory=lambda: str(uuid4()))
    cancellable: bool = True

    def pending_tasks(self) -> tuple[Task, ...]:
        return tuple(task for task in self.tasks if task.status == TaskStatus.PENDING)


class Planner:
    """Converts an Intent into executable, agent-neutral Tasks."""

    def create_plan(self, intent: Intent) -> Plan:
        target_agent = intent.target_agent
        tasks: list[Task] = []

        if intent.action == "OpenApplication":
            tasks.append(
                Task(
                    description=f"Request application launch: {intent.application or 'requested application'}",
                    action="launch_application",
                    capability="desktop.application.launch",
                    payload={"application": intent.application},
                    retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=1.0),
                    timeout_seconds=20.0,
                )
            )
        elif intent.action == "CloseApplication":
            tasks.append(
                Task(
                    description=f"Request application close: {intent.application or 'requested application'}",
                    action="close_application",
                    capability="desktop.application.close",
                    payload={
                        "application": intent.application,
                        "confirmed": intent.parameters.get("confirmed", False),
                        "confirmation_action_hash": intent.parameters.get("confirmation_action_hash"),
                        "confirmation_expires_at": intent.parameters.get("confirmation_expires_at"),
                    },
                    timeout_seconds=20.0,
                )
            )
        elif intent.action == "SwitchApplication":
            tasks.append(
                Task(
                    description=f"Bring application to foreground: {intent.application or 'requested application'}",
                    action="switch_application",
                    capability="desktop.application.focus",
                    payload={"application": intent.application},
                    timeout_seconds=10.0,
                )
            )
        elif intent.action == "PlayMedia":
            tasks.extend(self._media_tasks(intent))
        elif intent.action == "Remember":
            tasks.append(
                Task(
                    description="Store user-approved memory",
                    action="remember",
                    capability="memory.write",
                    target_agent="memory",
                    payload={"content": intent.raw_text},
                    timeout_seconds=5.0,
                )
            )
        elif intent.action == "TeachResponse":
            tasks.append(
                Task(
                    description="Teach NELA a user-provided response pair",
                    action="teach_response",
                    capability="teach_response",
                    target_agent="learning",
                    payload={
                        "trigger": intent.parameters.get("trigger", ""),
                        "response": intent.parameters.get("response", ""),
                        "tags": ("conversation", "hebrew", "user_taught"),
                    },
                    timeout_seconds=5.0,
                )
            )
        elif intent.action == "LearnTopic":
            tasks.append(
                Task(
                    description="Prepare a learning path for the requested topic",
                    action="recommend_learning_plan",
                    capability="recommend_learning_plan",
                    target_agent="learning",
                    payload={"topic": intent.parameters.get("topic", intent.raw_text)},
                    timeout_seconds=5.0,
                )
            )
        elif intent.action == "SecurityReview":
            tasks.append(
                Task(
                    description="Run defensive security review on supplied text or code",
                    action="review_code_security",
                    capability="review_code_security",
                    target_agent="secure_code_reviewer",
                    payload={"source": intent.raw_text, "path": "conversation"},
                    timeout_seconds=10.0,
                )
            )
        elif intent.action == "CyberDefenseSweep":
            tasks.append(
                Task(
                    description="Build defensive cyber posture findings",
                    action="defense_posture_check",
                    capability="defense_posture_check",
                    target_agent="cyber_defense",
                    payload={"target": intent.resource or "NELA local workspace", "text": intent.raw_text},
                    timeout_seconds=10.0,
                )
            )
        elif intent.action == "ThreatModel":
            tasks.append(
                Task(
                    description="Prepare a defensive threat model",
                    action="threat_model",
                    capability="threat_model",
                    target_agent="secure_code_reviewer",
                    payload={"asset": intent.resource or intent.raw_text},
                    timeout_seconds=10.0,
                )
            )
        elif intent.action == "CyberLabStatus":
            tasks.append(
                Task(
                    description="Read authorized cyber lab status",
                    action="lab_status",
                    capability="lab_status",
                    target_agent="authorized_lab",
                    payload={},
                    timeout_seconds=5.0,
                )
            )
        elif intent.action == "CyberLabRegisterTarget":
            tasks.append(
                Task(
                    description="Register a local or owned cyber lab target",
                    action="register_lab_target",
                    capability="register_lab_target",
                    target_agent="authorized_lab",
                    payload={
                        "target": intent.resource or "localhost",
                        "scope_type": "local_lab",
                        "owner": "local-owner",
                        "proof": "declared local or owned lab target from conversation",
                    },
                    timeout_seconds=5.0,
                )
            )
        elif intent.action == "LocalFuzzPlan":
            tasks.append(
                Task(
                    description="Prepare a local-only fuzzing plan",
                    action="create_local_fuzz_plan",
                    capability="create_local_fuzz_plan",
                    target_agent="anomaly_discovery",
                    payload={"target": intent.resource or intent.raw_text},
                    timeout_seconds=10.0,
                )
            )
        else:
            tasks.append(
                Task(
                    description=f"Delegate request: {intent.raw_text}",
                    action=_action_to_command(intent.action),
                    capability=str(intent.parameters.get("capability") or _action_to_command(intent.action)),
                    target_agent=target_agent,
                    payload={
                        "text": intent.raw_text,
                        "application": intent.application,
                        "resource": intent.resource,
                        "confirmed": intent.parameters.get("confirmed", False),
                        "confirmation_action_hash": intent.parameters.get("confirmation_action_hash"),
                        "confirmation_expires_at": intent.parameters.get("confirmation_expires_at"),
                    },
                )
            )

        return Plan(intent=intent, tasks=tuple(tasks))

    def cancel_plan(self, plan: Plan) -> Plan:
        return replace(
            plan,
            tasks=tuple(
                task.with_status(TaskStatus.CANCELLED)
                if task.status in {TaskStatus.PENDING, TaskStatus.DISPATCHED, TaskStatus.RUNNING}
                else task
                for task in plan.tasks
            ),
        )

    def _media_tasks(self, intent: Intent) -> tuple[Task, ...]:
        agent = intent.target_agent
        launch = Task(
            description=f"Ensure application is available: {intent.application or 'media application'}",
            action="ensure_application",
            capability="media.application.prepare" if agent else "desktop.application.launch",
            target_agent=agent or "desktop",
            payload={"application": intent.application},
            retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=1.0),
            timeout_seconds=20.0,
        )
        wait = Task(
            description="Wait until the application is ready",
            action="wait_until_ready",
            capability="media.application.status" if agent else "desktop.application.status",
            target_agent=agent or "desktop",
            depends_on=(launch.id,),
            payload={"application": intent.application},
            timeout_seconds=20.0,
        )
        search = Task(
            description="Find requested media resource",
            action="search_media",
            capability="media.search",
            target_agent=agent,
            depends_on=(wait.id,),
            payload={"resource": intent.resource, "text": intent.raw_text},
            timeout_seconds=15.0,
        )
        play = Task(
            description="Start media playback",
            action="play_media",
            capability="media.play",
            target_agent=agent,
            depends_on=(search.id,),
            payload={"resource": intent.resource},
            timeout_seconds=10.0,
        )
        return (launch, wait, search, play)


def _action_to_command(action: str) -> str:
    output = []
    for char in action:
        if char.isupper() and output:
            output.append("_")
        output.append(char.lower())
    return "".join(output)
```

### `brain/qa.py`

```python
"""Conversation QA layer for safe NELA self-knowledge."""

from __future__ import annotations

from dataclasses import dataclass

from brain.context import ContextSnapshot
from brain.dispatcher import AgentDispatcher
from brain.intent_router import Intent
from brain.memory_manager import MemoryManager
from language.learning_store import LearnedResponseStore


CONVERSATIONAL_ACTIONS = frozenset(
    {
        "Greeting",
        "Thanks",
        "IdentityQuestion",
        "CapabilitiesQuestion",
        "SecurityCapabilitiesQuestion",
        "HumanStatusQuestion",
        "AgentStatusQuestion",
        "GeneralQuestion",
    }
)


@dataclass(frozen=True)
class KnowledgeAnswer:
    """A semantic answer that the language layer can render."""

    category: str
    message: str
    variables: dict[str, object]


class KnowledgeEngine:
    """Answers safe conversation questions without delegating to external Agents."""

    def __init__(self, learned_responses: LearnedResponseStore | None = None) -> None:
        self.learned_responses = learned_responses or LearnedResponseStore()

    def answer(
        self,
        intent: Intent,
        dispatcher: AgentDispatcher,
        context: ContextSnapshot,
        memory: MemoryManager,
    ) -> KnowledgeAnswer:
        learned = self.learned_responses.find_response(intent.raw_text)
        if learned is not None:
            return KnowledgeAnswer(
                "qa.learned",
                learned.response,
                {
                    "answer": learned.response,
                    "trigger": learned.trigger,
                    "source": learned.source,
                },
            )

        agents = dispatcher.discover_agents()
        health = dispatcher.health_check()
        healthy_count = sum(1 for result in health.values() if result.success)
        agent_list = _agent_list(agents)
        security_agents = _agent_list(tuple(agent for agent in agents if _is_security_agent(agent)), limit=10)
        variables: dict[str, object] = {
            "agent_count": len(agents),
            "healthy_count": healthy_count,
            "agents": agent_list,
            "security_agents": security_agents,
            "last_intent": context.last_intent or "אין עדיין פקודה קודמת",
            "running_tasks": len(context.running_tasks),
            "recent_turns": len(memory.recent_context(limit=5)),
        }

        if intent.action == "Greeting":
            return KnowledgeAnswer("qa.greeting", "greeting", variables)
        if intent.action == "Thanks":
            return KnowledgeAnswer("qa.thanks", "thanks", variables)
        if intent.action == "IdentityQuestion":
            return KnowledgeAnswer("qa.identity", "identity", variables)
        if intent.action == "CapabilitiesQuestion":
            return KnowledgeAnswer("qa.capabilities", "capabilities", variables)
        if intent.action == "SecurityCapabilitiesQuestion":
            return KnowledgeAnswer("qa.security_capabilities", "security_capabilities", variables)
        if intent.action == "HumanStatusQuestion":
            return KnowledgeAnswer("qa.human_status", "human_status", variables)
        if intent.action == "AgentStatusQuestion":
            return KnowledgeAnswer("qa.agent_status", "agent_status", variables)
        return KnowledgeAnswer("qa.unknown", "unknown", variables)


def _agent_list(agents: tuple[str, ...], limit: int = 12) -> str:
    visible = tuple(sorted(agents))[:limit]
    suffix = "" if len(agents) <= limit else f" ועוד {len(agents) - limit}"
    return ", ".join(visible) + suffix


def _is_security_agent(agent: str) -> bool:
    return agent in {
        "cyber_defense",
        "secure_code_reviewer",
        "vulnerability_research",
        "security_researcher",
        "infrastructure_security",
        "threat_intelligence",
        "sentinel",
        "incident_commander",
        "containment",
        "deception",
        "forensics",
        "threat_hunter",
        "red_team_simulator",
        "blue_team",
        "purple_team",
        "exploit_validation",
        "detection_engineering",
        "recovery",
        "anomaly_discovery",
        "authorized_lab",
    }
```

### `brain/conversation.py`

```python
"""Conversation orchestration for NELA OS."""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Literal

from agents.base import AgentResult
from brain.context import ContextEngine, PendingConfirmation
from brain.decision import Decision, DecisionEngine, DecisionType
from brain.dispatcher import AgentDispatcher
from brain.applications import resolve_application_alias
from brain.intent_router import Intent, IntentRouter
from brain.memory_manager import MemoryManager
from brain.planner import Plan, Planner, Task, TaskMode, _action_to_command
from brain.qa import CONVERSATIONAL_ACTIONS, KnowledgeEngine
from core.events import Event, EventBus, EventTypes
from permissions.confirmation import action_tuple_hash


@dataclass(frozen=True)
class ConversationTurn:
    """Result of one user interaction with the Brain."""

    user_text: str
    input_mode: str
    intent: Intent
    decision: Decision
    plan: Plan | None
    message: str
    dispatched_results: tuple[AgentResult, ...] = ()


class ConversationEngine:
    """Central Brain entry point for text and voice conversation."""

    def __init__(
        self,
        intent_router: IntentRouter,
        decision_engine: DecisionEngine,
        planner: Planner,
        memory: MemoryManager,
        context: ContextEngine,
        dispatcher: AgentDispatcher,
        events: EventBus,
        auto_dispatch: bool = True,
        confirmation_ttl_seconds: int = 300,
        max_unclear_confirmation_replies: int = 2,
        knowledge: KnowledgeEngine | None = None,
    ) -> None:
        self.intent_router = intent_router
        self.decision_engine = decision_engine
        self.planner = planner
        self.memory = memory
        self.context = context
        self.dispatcher = dispatcher
        self.events = events
        self.auto_dispatch = auto_dispatch
        self.confirmation_ttl = timedelta(seconds=confirmation_ttl_seconds)
        self.max_unclear_confirmation_replies = max_unclear_confirmation_replies
        self.knowledge = knowledge or KnowledgeEngine()
        self.logger = logging.getLogger("nela.brain")

    def handle_text(self, text: str) -> ConversationTurn:
        return self._handle_input(text=text, input_mode="text")

    def handle_voice(self, transcript: str) -> ConversationTurn:
        return self._handle_input(text=transcript, input_mode="voice")

    def end_conversation(self) -> None:
        self.events.publish(
            Event(
                type=EventTypes.CONVERSATION_ENDED,
                source="brain.conversation",
                payload={"conversation_id": self.context.conversation_id},
            )
        )

    def _handle_input(self, text: str, input_mode: str) -> ConversationTurn:
        turn_id = self.context.start_turn(text)
        self.events.publish(
            Event(
                type=EventTypes.INPUT_RECEIVED,
                source="brain.conversation",
                payload={"turn_id": turn_id, "input_mode": input_mode},
            )
        )

        self._expire_pending_confirmations(turn_id)
        pending_confirmation = self.context.oldest_pending_confirmation()
        if pending_confirmation is not None:
            routed = self._handle_confirmation_answer(text, input_mode, turn_id, pending_confirmation)
            if routed is not None:
                return routed

        pending_slot = self.context.session_state.get("pending_slot")
        if isinstance(pending_slot, dict):
            return self._handle_pending_slot(text, input_mode, turn_id, pending_slot)

        intent = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
        return self._process_intent(text, input_mode, turn_id, intent)

    def _process_intent(self, text: str, input_mode: str, turn_id: str, intent: Intent) -> ConversationTurn:
        self.context.record_intent(intent.action)
        self.events.publish(
            Event(
                type=EventTypes.INTENT_RECOGNIZED,
                source="brain.intent_router",
                payload={
                    "turn_id": turn_id,
                    "action": intent.action,
                    "application": intent.application,
                    "resource": intent.resource,
                    "priority": intent.priority.value,
                    "confidence": intent.confidence,
                    "target_agent": intent.target_agent,
                },
            )
        )

        decision = self.decision_engine.decide(intent, self.context.snapshot())
        self.events.publish(
            Event(
                type=EventTypes.DECISION_MADE,
                source="brain.decision",
                payload={"turn_id": turn_id, "decision": decision.type.value, "reason": decision.reason},
            )
        )

        self.memory.record_turn(text, intent)

        if decision.type in {DecisionType.ASK_CLARIFICATION, DecisionType.WAIT, DecisionType.REJECT}:
            if decision.question:
                if intent.requires_confirmation:
                    confirmation_binding = self._confirmation_binding(intent)
                    confirmation = self.context.add_pending_confirmation(
                        decision.question,
                        {
                            "turn_id": turn_id,
                            "intent": intent,
                            "unclear_replies": 0,
                            "confirmation_binding": confirmation_binding,
                        },
                    )
                    self.events.publish(
                        Event(
                            type=EventTypes.CONFIRMATION_REQUESTED,
                            source="brain.conversation",
                            payload={
                                "turn_id": turn_id,
                                "confirmation_id": confirmation.id,
                                "question": confirmation.question,
                                "intent": intent.action,
                            },
                        )
                    )
                elif decision.reason == "Missing application slot.":
                    self.context.session_state["pending_slot"] = {
                        "slot": "application",
                        "intent": intent,
                        "turn_id": turn_id,
                    }
                    self.events.publish(
                        Event(
                            type=EventTypes.CONTEXT_UPDATED,
                            source="brain.conversation",
                            payload={"turn_id": turn_id, "pending_slot": "application", "intent": intent.action},
                        )
                    )
            return ConversationTurn(
                user_text=text,
                input_mode=input_mode,
                intent=intent,
                decision=decision,
                plan=None,
                message=decision.question or decision.reason,
            )

        if intent.action in CONVERSATIONAL_ACTIONS:
            answer = self.knowledge.answer(intent, self.dispatcher, self.context.snapshot(), self.memory)
            answered_intent = replace(
                intent,
                parameters={
                    **intent.parameters,
                    "response_category": answer.category,
                    "response_variables": answer.variables,
                },
            )
            return ConversationTurn(
                user_text=text,
                input_mode=input_mode,
                intent=answered_intent,
                decision=decision,
                plan=None,
                message=answer.message,
            )

        if decision.should_remember:
            self.memory.remember(text, tags=("user_request", intent.action))

        plan = self.planner.create_plan(intent)
        self._publish_plan(plan, turn_id)

        results: tuple[AgentResult, ...] = ()
        if self.auto_dispatch and decision.type in {DecisionType.EXECUTE_IMMEDIATELY, DecisionType.DELEGATE}:
            results = self._dispatch_plan(plan)

        return ConversationTurn(
            user_text=text,
            input_mode=input_mode,
            intent=intent,
            decision=decision,
            plan=plan,
            message="Plan created and delegated." if results else "Plan created.",
            dispatched_results=results,
        )

    def _handle_confirmation_answer(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        confirmation: PendingConfirmation,
    ) -> ConversationTurn | None:
        answer = _classify_confirmation_answer(text)
        if answer == "affirmative":
            return self._resolve_confirmed(text, input_mode, turn_id, confirmation)
        if answer == "negative":
            return self._resolve_cancelled(text, input_mode, turn_id, confirmation, "User cancelled the action.")
        return self._handle_unclear_confirmation_answer(text, input_mode, turn_id, confirmation)

    def _handle_pending_slot(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        pending_slot: dict[str, object],
    ) -> ConversationTurn:
        intent = pending_slot.get("intent")
        if not isinstance(intent, Intent):
            self.context.session_state.pop("pending_slot", None)
            fresh = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
            return self._process_intent(text, input_mode, turn_id, fresh)

        application = resolve_application_alias(text.strip())
        if not application:
            self.context.session_state.pop("pending_slot", None)
            fresh = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
            return self._process_intent(text, input_mode, turn_id, fresh)

        self.context.session_state.pop("pending_slot", None)
        filled_intent = replace(intent, application=application, raw_text=f"{intent.raw_text} {text}".strip())
        self.events.publish(
            Event(
                type=EventTypes.CONTEXT_UPDATED,
                source="brain.conversation",
                payload={"turn_id": turn_id, "filled_slot": "application", "application": application},
            )
        )
        return self._process_intent(text, input_mode, turn_id, filled_intent)

    def _resolve_confirmed(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        confirmation: PendingConfirmation,
    ) -> ConversationTurn:
        self.context.resolve_confirmation(confirmation.id)
        self.events.publish(
            Event(
                type=EventTypes.CONFIRMATION_RESOLVED,
                source="brain.conversation",
                payload={
                    "turn_id": turn_id,
                    "confirmation_id": confirmation.id,
                    "resolution": "confirmed",
                },
            )
        )
        intent = confirmation.metadata.get("intent")
        if not isinstance(intent, Intent):
            intent = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
        elif intent.requires_confirmation:
            binding = confirmation.metadata.get("confirmation_binding")
            bound_parameters = {}
            if isinstance(binding, dict):
                bound_parameters = {
                    "confirmation_action_hash": binding.get("action_hash"),
                    "confirmation_expires_at": binding.get("expires_at"),
                }
            intent = replace(
                intent,
                parameters={**intent.parameters, "confirmed": True, **bound_parameters},
                requires_confirmation=False,
            )
        return self._process_intent(text, input_mode, turn_id, intent)

    def _resolve_cancelled(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        confirmation: PendingConfirmation,
        reason: str,
    ) -> ConversationTurn:
        self.context.resolve_confirmation(confirmation.id)
        self.events.publish(
            Event(
                type=EventTypes.CONFIRMATION_RESOLVED,
                source="brain.conversation",
                payload={
                    "turn_id": turn_id,
                    "confirmation_id": confirmation.id,
                    "resolution": "cancelled",
                    "reason": reason,
                },
            )
        )
        self.events.publish(
            Event(
                type=EventTypes.TASK_CANCELLED,
                source="brain.conversation",
                payload={
                    "turn_id": turn_id,
                    "confirmation_id": confirmation.id,
                    "reason": reason,
                },
            )
        )
        intent = _confirmation_response_intent(text)
        decision = Decision(type=DecisionType.REJECT, reason=reason)
        self.memory.record_turn(text, intent)
        return ConversationTurn(
            user_text=text,
            input_mode=input_mode,
            intent=intent,
            decision=decision,
            plan=None,
            message=reason,
        )

    def _handle_unclear_confirmation_answer(
        self,
        text: str,
        input_mode: str,
        turn_id: str,
        confirmation: PendingConfirmation,
    ) -> ConversationTurn | None:
        unclear_replies = int(confirmation.metadata.get("unclear_replies", 0)) + 1
        if unclear_replies < self.max_unclear_confirmation_replies:
            self.context.update_confirmation_metadata(
                confirmation.id,
                {**confirmation.metadata, "unclear_replies": unclear_replies},
            )
            intent = _confirmation_response_intent(text)
            decision = Decision(
                type=DecisionType.WAIT,
                reason="Confirmation answer was unclear.",
                question=confirmation.question,
            )
            self.memory.record_turn(text, intent)
            return ConversationTurn(
                user_text=text,
                input_mode=input_mode,
                intent=intent,
                decision=decision,
                plan=None,
                message=confirmation.question,
            )

        self.context.resolve_confirmation(confirmation.id)
        self.events.publish(
            Event(
                type=EventTypes.CONFIRMATION_RESOLVED,
                source="brain.conversation",
                payload={
                    "turn_id": turn_id,
                    "confirmation_id": confirmation.id,
                    "resolution": "cancelled",
                    "reason": "Too many unclear confirmation replies.",
                },
            )
        )
        fresh_intent = self.intent_router.classify(text, context=self.context.snapshot().__dict__)
        if fresh_intent.confidence >= 0.5:
            return self._process_intent(text, input_mode, turn_id, fresh_intent)

        decision = Decision(
            type=DecisionType.REJECT,
            reason="Confirmation was cancelled after too many unclear replies.",
        )
        self.memory.record_turn(text, fresh_intent)
        return ConversationTurn(
            user_text=text,
            input_mode=input_mode,
            intent=fresh_intent,
            decision=decision,
            plan=None,
            message=decision.reason,
        )

    def _expire_pending_confirmations(self, turn_id: str) -> None:
        now = datetime.now(timezone.utc)
        for confirmation in tuple(self.context.pending_confirmations.values()):
            if now - confirmation.created_at <= self.confirmation_ttl:
                continue
            self.context.resolve_confirmation(confirmation.id)
            self.events.publish(
                Event(
                    type=EventTypes.CONFIRMATION_EXPIRED,
                    source="brain.conversation",
                    payload={
                        "turn_id": turn_id,
                        "confirmation_id": confirmation.id,
                        "created_at": confirmation.created_at.isoformat(),
                    },
                )
            )

    def _publish_plan(self, plan: Plan, turn_id: str) -> None:
        self.events.publish(
            Event(
                type=EventTypes.PLAN_CREATED,
                source="brain.planner",
                payload={"turn_id": turn_id, "plan_id": plan.id, "task_count": len(plan.tasks)},
            )
        )
        for task in plan.tasks:
            self.events.publish(
                Event(
                    type=EventTypes.TASK_CREATED,
                    source="brain.planner",
                    payload={
                        "plan_id": plan.id,
                        "task_id": task.id,
                        "description": task.description,
                        "action": task.action,
                        "mode": task.mode.value,
                        "target_agent": task.target_agent,
                        "depends_on": task.depends_on,
                        "timeout_seconds": task.timeout_seconds,
                    },
                )
            )

    def _dispatch_plan(self, plan: Plan) -> tuple[AgentResult, ...]:
        completed: set[str] = set()
        failed: set[str] = set()
        results: list[AgentResult] = []

        for task in plan.tasks:
            if not self._dependencies_satisfied(task, completed):
                failed.add(task.id)
                results.append(AgentResult(False, "Task dependencies were not satisfied.", {"task_id": task.id}))
                continue

            self.context.mark_task_running(task.id, task.description, task.target_agent)
            result = self.dispatcher.dispatch(task, plan.id)
            self.context.mark_task_finished(task.id)
            results.append(result)
            if result.success:
                completed.add(task.id)
            else:
                failed.add(task.id)

            if task.mode == TaskMode.SEQUENTIAL and failed:
                break

        if failed:
            self.logger.error("plan_failed plan_id=%s failed_tasks=%s", plan.id, sorted(failed))
        return tuple(results)

    def _dependencies_satisfied(self, task: Task, completed: set[str]) -> bool:
        return all(dependency in completed for dependency in task.depends_on)

    def _confirmation_binding(self, intent: Intent) -> dict[str, object]:
        expires_at = datetime.now(timezone.utc) + self.confirmation_ttl
        if intent.action == "CloseApplication":
            agent = "desktop"
            capability = "desktop.application.close"
            action = "close_application"
            target = intent.application
            parameters = {"application": intent.application}
        else:
            agent = intent.target_agent
            action = _action_to_command(intent.action)
            capability = str(intent.parameters.get("capability") or action)
            target = intent.application or intent.resource
            parameters = {
                "text": intent.raw_text,
                "application": intent.application,
                "resource": intent.resource,
            }
        return {
            "agent": agent,
            "capability": capability,
            "action": action,
            "target": target,
            "expires_at": expires_at.isoformat(),
            "action_hash": action_tuple_hash(
                agent=agent,
                capability=capability,
                action=action,
                target=target,
                parameters=parameters,
                session=None,
                expires_at=expires_at,
            ),
        }


ConfirmationAnswer = Literal["affirmative", "negative", "unclear"]


def _classify_confirmation_answer(text: str) -> ConfirmationAnswer:
    normalized = " ".join(text.lower().strip().split())
    affirmative_answers = {
        "yes",
        "y",
        "confirm",
        "confirmed",
        "do it",
        "continue",
        "proceed",
        "ok",
        "okay",
        "sure",
        "go ahead",
        "כן",
        "מאשר",
        "אשר",
        "תמשיך",
        "בצע",
    }
    negative_answers = {
        "no",
        "n",
        "cancel",
        "stop",
        "do not",
        "don't",
        "never mind",
        "abort",
        "לא",
        "בטל",
        "עצור",
        "אל",
    }
    if normalized in affirmative_answers:
        return "affirmative"
    if normalized in negative_answers:
        return "negative"
    return "unclear"


def _confirmation_response_intent(text: str) -> Intent:
    return Intent(
        action="ConfirmationResponse",
        raw_text=text,
        confidence=1.0,
    )
```

### `core/response.py`

```python
"""Response rendering and voice delegation for Brain turns."""

from __future__ import annotations

from agents.base import AgentResult
from brain.conversation import ConversationTurn
from brain.decision import DecisionType
from brain.dispatcher import AgentDispatcher
from brain.planner import Task
from core.config import AppConfig
from language.engine import LanguageEngine


class NelaResponseAdapter:
    """Converts semantic Brain turns into user-facing Hebrew and optional speech."""

    def __init__(self, language: LanguageEngine, dispatcher: AgentDispatcher, config: AppConfig) -> None:
        self.language = language
        self.dispatcher = dispatcher
        self.config = config

    def render_turn(self, turn: ConversationTurn) -> str:
        category, variables = self._category_and_variables(turn)
        return self.language.render_response(category=category, variables=variables)

    def render_and_maybe_speak(self, turn: ConversationTurn) -> str:
        text = self.render_turn(turn)
        if self.config.voice_auto_speak_responses:
            self.speak_text(text)
        return text

    def speak_text(self, text: str) -> AgentResult | None:
        if "voice" not in self.dispatcher.discover_agents():
            return None
        task = Task(
            description="Speak final assistant response",
            action="speak",
            target_agent="voice",
            payload={
                "text": text,
                "interrupt": True,
                "silent": self.config.voice_silent_mode,
            },
            timeout_seconds=10.0,
        )
        return self.dispatcher.dispatch(task, plan_id="response-output")

    def _category_and_variables(self, turn: ConversationTurn) -> tuple[str, dict[str, object]]:
        application = turn.intent.application or "האפליקציה"
        resource = turn.intent.resource or "הבקשה"

        variables: dict[str, object] = {
            "application": application,
            "resource": resource,
            "message": turn.message,
            "intent": turn.intent.action,
            "task_hint": turn.message,
        }
        if turn.dispatched_results:
            first_result = turn.dispatched_results[0]
            variables["summary"] = first_result.message
            variables["task_hint"] = first_result.message
            findings = _summarize_findings(turn.dispatched_results)
            variables.update(findings)
        response_variables = turn.intent.parameters.get("response_variables")
        if isinstance(response_variables, dict):
            variables.update(response_variables)

        response_category = turn.intent.parameters.get("response_category")
        if isinstance(response_category, str) and response_category:
            return response_category, variables

        if turn.decision.type in {DecisionType.ASK_CLARIFICATION, DecisionType.WAIT}:
            variables["question"] = turn.message
            variables["clarify"] = turn.message
            return "clarify.one_question", variables
        if turn.decision.type == DecisionType.REJECT:
            return "success.short", variables
        if turn.dispatched_results and any(not result.success for result in turn.dispatched_results):
            failed = next(result for result in turn.dispatched_results if not result.success)
            variables["error"] = failed.message
            variables["what"] = failed.message
            return "error.recovering", variables
        if turn.intent.action == "OpenApplication":
            return "desktop.launch", variables
        if turn.intent.action == "CloseApplication":
            return "desktop.closed", variables
        if turn.intent.action == "PlayMedia":
            return "media.play", variables
        if turn.intent.action == "Remember":
            return "learning.saved", variables
        if turn.intent.action == "TeachResponse":
            return "learning.saved", variables
        if turn.intent.action == "LearnTopic":
            variables["topic"] = str(turn.intent.parameters.get("topic", "הנושא הזה"))
            return "learning.topic.started", variables
        if turn.intent.action == "SecurityReview":
            return _security_category("security.review.done", variables), variables
        if turn.intent.action == "CyberDefenseSweep":
            if int(variables.get("findings_count", 0) or 0) > 0:
                return "security.defense.findings", variables
            return "security.review.done", variables
        if turn.intent.action == "ThreatModel":
            return _security_category("security.threat_model.done", variables), variables
        if turn.intent.action == "CyberLabRegisterTarget":
            return "security.lab.done", variables
        if turn.intent.action == "CyberLabStatus":
            return "security.lab.status", variables
        if turn.intent.action == "LocalFuzzPlan":
            return _security_category("security.fuzz_plan.done", variables), variables
        if turn.plan:
            return "success.short", variables
        return "smalltalk.daily", variables


def _security_category(default_category: str, variables: dict[str, object]) -> str:
    if int(variables.get("findings_count", 0) or 0) > 0:
        return "security.findings.done"
    return default_category


def _summarize_findings(results: tuple[AgentResult, ...]) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    next_steps: list[str] = []
    for result in results:
        product = result.data.get("work_product")
        if not isinstance(product, dict):
            continue
        raw_findings = product.get("findings", ())
        if isinstance(raw_findings, list):
            findings.extend(item for item in raw_findings if isinstance(item, dict))
        raw_next_steps = product.get("next_steps", ())
        if isinstance(raw_next_steps, list):
            next_steps.extend(str(item) for item in raw_next_steps)

    finding_lines = []
    for index, finding in enumerate(findings[:4], start=1):
        severity = _severity_label(str(finding.get("severity", "info")))
        title = _finding_title(str(finding.get("title", "ממצא הגנתי")))
        recommendation = str(finding.get("recommendation") or "").strip()
        if recommendation:
            finding_lines.append(f"{index}. {severity}: {title}. המלצה: {recommendation}")
        else:
            finding_lines.append(f"{index}. {severity}: {title}.")

    return {
        "findings_count": len(findings),
        "findings_count_label": _count_label(len(findings)),
        "findings": "\n".join(finding_lines) if finding_lines else "לא נמצאו ממצאים חריגים בבדיקה הזאת.",
        "next_steps": " ".join(next_steps[:2]) if next_steps else "להמשיך בבדיקה הגנתית ממוקדת לפי scope מאושר.",
    }


def _severity_label(severity: str) -> str:
    labels = {
        "critical": "קריטי",
        "high": "גבוה",
        "medium": "בינוני",
        "low": "נמוך",
        "info": "מידע",
    }
    return labels.get(severity.lower(), "מידע")


def _count_label(count: int) -> str:
    if count == 0:
        return "אין ממצאים"
    if count == 1:
        return "ממצא אחד"
    if count == 2:
        return "שני ממצאים"
    return f"{count} ממצאים"


def _finding_title(title: str) -> str:
    known = {
        "Dynamic eval usage": "שימוש ב-eval דינמי",
        "Dynamic exec usage": "שימוש ב-exec דינמי",
        "Shell execution enabled": "הרצת shell פעילה",
        "Unsafe pickle deserialization": "טעינת pickle לא בטוחה",
        "YAML load without SafeLoader": "טעינת YAML בלי SafeLoader",
        "TLS certificate verification disabled": "אימות תעודת TLS כבוי",
        "Weak hash algorithm": "אלגוריתם hash חלש",
        "Possible hardcoded secret": "ייתכן שיש סוד קשיח בקוד",
    }
    return known.get(title, title)
```

### `core/startup.py`

```python
"""Runtime bootstrap for NELA OS."""

from __future__ import annotations

from dataclasses import dataclass

from agents.automation.agent import AutomationAgent
from agents.browser.agent import BrowserAgent
from agents.calendar.agent import CalendarAgent
from agents.claude.agent import ClaudeAgent
from agents.codex.agent import CodexAgent
from agents.desktop.agent import DesktopAgent
from agents.files.agent import FilesAgent
from agents.github.agent import GitHubAgent
from agents.gmail.agent import GmailAgent
from agents.memory.agent import MemoryAgent
from agents.spotify.agent import SpotifyAgent
from agents.terminal.agent import TerminalAgent
from agents.voice.agent import VoiceAgent
from agents.vision.agent import VisionAgent
from brain.context import ContextEngine
from brain.conversation import ConversationEngine
from brain.decision import DecisionEngine
from brain.dispatcher import AgentDispatcher
from brain.intent_router import IntentRouter
from brain.memory_manager import MemoryManager
from brain.planner import Planner
from brain.qa import KnowledgeEngine
from core.config import AppConfig
from core.events import EventBus
from core.logger import configure_logging
from core.response import NelaResponseAdapter
from language.engine import HebrewLanguageEngine, LanguageEngine
from language.learning_store import LearnedResponseStore
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory
from voice.providers.factory import create_speech_provider
from agents.factory import build_default_agents


@dataclass
class NelaRuntime:
    config: AppConfig
    events: EventBus
    conversation: ConversationEngine
    dispatcher: AgentDispatcher
    context: ContextEngine
    memory: MemoryManager
    language: LanguageEngine
    response_adapter: NelaResponseAdapter


def bootstrap(config: AppConfig | None = None) -> NelaRuntime:
    runtime_config = config or AppConfig.from_env()
    configure_logging(level=runtime_config.log_level)

    events = EventBus()
    dispatcher = AgentDispatcher(events=events)
    learned_responses = LearnedResponseStore(runtime_config.data_dir / "language" / "learned_responses.json")
    _register_builtin_agents(dispatcher, events, runtime_config, learned_responses)
    language = HebrewLanguageEngine(personality_name=runtime_config.language_personality)
    response_adapter = NelaResponseAdapter(language=language, dispatcher=dispatcher, config=runtime_config)
    context = ContextEngine()
    memory = MemoryManager(
        short_term=ShortTermMemory(),
        long_term=LongTermMemory(),
        events=events,
    )
    conversation = ConversationEngine(
        intent_router=IntentRouter(),
        decision_engine=DecisionEngine(),
        planner=Planner(),
        memory=memory,
        context=context,
        dispatcher=dispatcher,
        events=events,
        knowledge=KnowledgeEngine(learned_responses=learned_responses),
    )

    return NelaRuntime(
        config=runtime_config,
        events=events,
        conversation=conversation,
        dispatcher=dispatcher,
        context=context,
        memory=memory,
        language=language,
        response_adapter=response_adapter,
    )


def _register_builtin_agents(
    dispatcher: AgentDispatcher,
    events: EventBus,
    config: AppConfig,
    learned_responses: LearnedResponseStore,
) -> None:
    for agent in (
        TerminalAgent(),
        BrowserAgent(),
        SpotifyAgent(),
        FilesAgent(),
        CalendarAgent(),
        GmailAgent(),
        GitHubAgent(),
        ClaudeAgent(),
        CodexAgent(),
        AutomationAgent(),
        VoiceAgent(
            events=events,
            provider=create_speech_provider(config.voice_provider),
            enabled=config.enable_voice,
            silent=config.voice_silent_mode,
        ),
        VisionAgent(),
        MemoryAgent(),
        DesktopAgent(),
    ):
        dispatcher.register_agent(agent)

    _register_specialist_agents(dispatcher, config, learned_responses)


def _register_specialist_agents(
    dispatcher: AgentDispatcher,
    config: AppConfig,
    learned_responses: LearnedResponseStore,
) -> None:
    """Register first-wave specialist Agents without replacing live runtime Agents."""

    registered = set(dispatcher.discover_agents())
    learning_store_path = config.data_dir / "language" / "learned_responses.json"
    for agent in build_default_agents(learning_store_path=learning_store_path, learning_store=learned_responses):
        if agent.name in registered:
            continue
        dispatcher.register_agent(agent)
        registered.add(agent.name)
```

### `language/learning_store.py`

```python
"""Persistent learned-response storage for local NELA language learning."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any


@dataclass(frozen=True)
class LearnedResponse:
    """One user-taught trigger and response pair."""

    id: str
    trigger: str
    response: str
    normalized_trigger: str
    tags: tuple[str, ...] = ()
    source: str = "user"
    created_at: str = ""

    @classmethod
    def create(cls, trigger: str, response: str, tags: tuple[str, ...] = (), source: str = "user") -> "LearnedResponse":
        normalized = normalize_trigger(trigger)
        created_at = datetime.now(timezone.utc).isoformat()
        identity = hashlib.sha256(f"{normalized}\n{response.strip()}".encode("utf-8")).hexdigest()[:16]
        return cls(
            id=f"learned.{identity}",
            trigger=trigger.strip(),
            response=response.strip(),
            normalized_trigger=normalized,
            tags=tags,
            source=source,
            created_at=created_at,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearnedResponse":
        return cls(
            id=str(data["id"]),
            trigger=str(data["trigger"]),
            response=str(data["response"]),
            normalized_trigger=str(data.get("normalized_trigger") or normalize_trigger(str(data["trigger"]))),
            tags=tuple(str(item) for item in data.get("tags", ())),
            source=str(data.get("source", "user")),
            created_at=str(data.get("created_at", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "trigger": self.trigger,
            "response": self.response,
            "normalized_trigger": self.normalized_trigger,
            "tags": list(self.tags),
            "source": self.source,
            "created_at": self.created_at,
        }


class LearnedResponseStore:
    """Small append/update store for user-taught response pairs."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._responses: dict[str, LearnedResponse] = {}
        if self.path is not None:
            self._load()

    def add_response(
        self,
        trigger: str,
        response: str,
        tags: tuple[str, ...] = (),
        source: str = "user",
    ) -> LearnedResponse:
        if not trigger.strip():
            raise ValueError("Trigger cannot be empty.")
        if not response.strip():
            raise ValueError("Response cannot be empty.")
        learned = LearnedResponse.create(trigger=trigger, response=response, tags=tags, source=source)
        self._responses[learned.normalized_trigger] = learned
        self._save()
        return learned

    def find_response(self, text: str) -> LearnedResponse | None:
        normalized = normalize_trigger(text)
        if normalized in self._responses:
            return self._responses[normalized]
        for learned in self._responses.values():
            if learned.normalized_trigger and learned.normalized_trigger in normalized:
                return learned
        return None

    def list_responses(self) -> tuple[LearnedResponse, ...]:
        return tuple(sorted(self._responses.values(), key=lambda item: item.created_at))

    def _load(self) -> None:
        if self.path is None or not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        responses = data.get("responses", ()) if isinstance(data, dict) else ()
        self._responses = {
            learned.normalized_trigger: learned
            for learned in (LearnedResponse.from_dict(item) for item in responses if isinstance(item, dict))
        }

    def _save(self) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 1, "responses": [item.to_dict() for item in self.list_responses()]}
        temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp_path.replace(self.path)


def normalize_trigger(text: str) -> str:
    cleaned = re.sub(r"^[\s,.:;!?\"'׳״]+|[\s,.:;!?\"'׳״]+$", "", text.lower())
    cleaned = re.sub(r"^(?:נלה|nela)[,\s]+", "", cleaned)
    return " ".join(cleaned.split())
```

### `language/engine.py`

```python
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
```

### `language/selector.py`

```python
"""Phrase selection with weighting, tone matching, and repetition avoidance."""

from __future__ import annotations

import random

from language.context import LanguageRuntimeContext
from language.fallback import fallback_phrase
from language.models import LanguagePack, PersonalityProfile, PhraseEntry


class PhraseSelector:
    """Selects a suitable phrase without relying on unrestricted random choice."""

    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)

    def select(
        self,
        pack: LanguagePack,
        context: LanguageRuntimeContext,
        personality: PersonalityProfile,
        category: str,
        tone: str | None = None,
        emotion: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> PhraseEntry:
        candidates = [entry for entry in pack.enabled_entries() if entry.category == category and self._is_eligible(entry, context)]
        if not candidates:
            prefix = category.rsplit(".", 1)[0]
            candidates = [
                entry for entry in pack.enabled_entries() if entry.category.startswith(prefix) and self._is_eligible(entry, context)
            ]
        if not candidates:
            selected = fallback_phrase(category, language=pack.language)
            context.remember_phrase(selected.id)
            return selected

        preferred_tone = tone or (personality.preferred_tones[0] if personality.preferred_tones else None)
        preferred_emotion = emotion or (personality.preferred_emotions[0] if personality.preferred_emotions else None)
        ranked = sorted(
            candidates,
            key=lambda entry: self._score(entry, context, personality, preferred_tone, preferred_emotion, tags),
            reverse=True,
        )
        top_score = self._score(ranked[0], context, personality, preferred_tone, preferred_emotion, tags)
        top_candidates = [
            entry
            for entry in ranked
            if self._score(entry, context, personality, preferred_tone, preferred_emotion, tags) >= top_score - 1.0
        ]
        non_recent = [entry for entry in top_candidates if not context.was_recent(entry.id)]
        pool = non_recent or top_candidates
        selected = self._weighted_choice(pool, personality)
        context.remember_phrase(selected.id)
        return selected

    def _is_eligible(self, entry: PhraseEntry, context: LanguageRuntimeContext) -> bool:
        if entry.min_stage > context.relationship_stage:
            return False
        if context.use_count(entry.id) >= entry.max_per_session:
            return False
        if entry.gender_tier > 1 and context.gender not in {"m", "male", "masculine", "f", "female", "feminine"}:
            return False
        return True

    def _score(
        self,
        entry: PhraseEntry,
        context: LanguageRuntimeContext,
        personality: PersonalityProfile,
        tone: str | None,
        emotion: str | None,
        tags: tuple[str, ...],
    ) -> float:
        score = entry.weight
        if tone and tone in entry.tone:
            score += 3.0
        if set(entry.tone) & set(personality.preferred_tones):
            score += 1.5
        if emotion and entry.emotion == emotion:
            score += 2.0
        if entry.emotion in personality.preferred_emotions:
            score += 0.5
        if entry.gender == context.gender == personality.gender:
            score += 0.5
        if tags and set(tags) <= set(entry.tags):
            score += 1.0
        if context.was_recent(entry.id):
            score -= 4.0
        score *= personality.phrase_bias.get(entry.category, 1.0)
        return score

    def _weighted_choice(self, entries: list[PhraseEntry], personality: PersonalityProfile) -> PhraseEntry:
        weights = [max(0.01, entry.weight * personality.phrase_bias.get(entry.category, 1.0)) for entry in entries]
        return self._random.choices(entries, weights=weights, k=1)[0]
```

### `language/renderer.py`

```python
"""Template rendering for language phrases."""

from __future__ import annotations

import re
from string import Formatter
from typing import Any

GENDER_TAG = re.compile(r"\{you:([^{}|]+)\|([^{}|]+)\}")


class SafeVariables(dict[str, Any]):
    """Keeps missing variables visible without crashing rendering."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def template_variables(text: str) -> set[str]:
    text = GENDER_TAG.sub("", text)
    variables: set[str] = set()
    for _, field_name, _, _ in Formatter().parse(text):
        if field_name:
            variables.add(field_name.split(".", 1)[0].split("[", 1)[0])
    return variables


def render_template(text: str, variables: dict[str, Any] | None = None) -> str:
    values = variables or {}

    def replace_gender(match: re.Match[str]) -> str:
        gender = str(values.get("user_gender", values.get("gender", "unknown"))).lower()
        if gender in {"m", "male", "masculine"}:
            return match.group(1)
        if gender in {"f", "female", "feminine"}:
            return match.group(2)
        return match.group(1)

    return GENDER_TAG.sub(replace_gender, text).format_map(SafeVariables(values))


def missing_template_variables(text: str, variables: dict[str, Any] | None = None) -> tuple[str, ...]:
    provided = set((variables or {}).keys())
    return tuple(sorted(template_variables(text) - provided))
```

### `language/hebrew/manifest.json`

```text
{
  "language": "he",
  "version": "1.0",
  "description": "Claude authoritative Hebrew language pack for NELA.",
  "files": [
    "greetings.json",
    "confirmations.json",
    "clarifications.json",
    "thinking.json",
    "waiting.json",
    "success.json",
    "errors.json",
    "apologies.json",
    "permissions.json",
    "domains.json",
    "general_chat.json"
  ],
  "categories": [
    "greeting.first_launch",
    "greeting.day",
    "farewell",
    "ack.short",
    "ack.ongoing",
    "clarify.one_question",
    "thinking",
    "waiting",
    "success.short",
    "success.long",
    "learning.saved",
    "desktop.closed",
    "media.play",
    "error.recovering",
    "failure.final",
    "apology.single",
    "confirm.ask",
    "desktop.close_confirm",
    "warning",
    "desktop.launch",
    "media.search",
    "files.search",
    "browser.open",
    "coding.assist",
    "projects.status",
    "automation.suggest",
    "smalltalk.daily",
    "humor.dry",
    "memory.recall",
    "voice.wake",
    "system.notification",
    "qa.greeting",
    "qa.thanks",
    "qa.identity",
    "qa.capabilities",
    "qa.security_capabilities",
    "qa.human_status",
    "qa.agent_status",
    "qa.learned",
    "qa.unknown",
    "learning.topic.started",
    "security.findings.done",
    "security.defense.findings",
    "security.review.done",
    "security.threat_model.done",
    "security.lab.done",
    "security.lab.status",
    "security.fuzz_plan.done"
  ],
  "tones": [
    "calm",
    "warm",
    "confident",
    "neutral",
    "playful",
    "psychedelic"
  ],
  "emotions": [
    "neutral",
    "positive",
    "careful",
    "error",
    "thinking",
    "waiting"
  ]
}
```

### `language/hebrew/general_chat.json`

```text
{
  "pack": "general_chat",
  "language": "he",
  "version": 1,
  "categories": {
    "smalltalk.daily": {
      "description": "Light daily conversation",
      "eye_state": "idle",
      "variants": [
        {
          "id": "core.small.day",
          "text": "איך היום עד עכשיו?",
          "min_stage": 2
        },
        {
          "id": "core.small.busy",
          "text": "יום עמוס? נראה ככה מהצד שלי.",
          "min_stage": 2
        },
        {
          "id": "core.small.quiet",
          "text": "שקט היום. נעים ככה לפעמים.",
          "min_stage": 2
        },
        {
          "id": "core.small.listen",
          "text": "מקשיבה, אם בא לך לספר.",
          "gender_tier": 1,
          "min_stage": 2
        }
      ]
    },
    "humor.dry": {
      "description": "Max once per conversation, mood permitting",
      "eye_state": "idle",
      "variants": [
        {
          "id": "core.humor.tidy",
          "text": "נהיה פה מסודר חשוד.",
          "humor": true,
          "min_stage": 2
        },
        {
          "id": "core.humor.again",
          "text": "שוב? טוב, אנחנו כבר כמעט חברות.",
          "humor": true,
          "min_stage": 2
        },
        {
          "id": "core.humor.promise",
          "text": "הפעם באמת. מבטיחה בערך.",
          "humor": true,
          "min_stage": 2
        },
        {
          "id": "core.humor.night",
          "text": "השעה מפוקפקת, אבל אני לא שופטת.",
          "humor": true,
          "min_stage": 3,
          "time_of_day": "night"
        }
      ]
    },
    "memory.recall": {
      "description": "Answering from memory",
      "eye_state": "speaking",
      "variants": [
        {
          "id": "core.recall.have",
          "text": "יש לי את זה: {answer}.",
          "vars": [
            "answer"
          ]
        },
        {
          "id": "core.recall.remember",
          "text": "זוכרת — {answer}.",
          "vars": [
            "answer"
          ]
        },
        {
          "id": "core.recall.last",
          "text": "בפעם הקודמת זה היה {answer}.",
          "vars": [
            "answer"
          ]
        }
      ]
    },
    "voice.wake": {
      "description": "Wake word detected",
      "eye_state": "listening",
      "variants": [
        {
          "id": "core.wake.withyou",
          "text": "אני איתך.",
          "weight": 1.5
        },
        {
          "id": "core.wake.yes",
          "text": "כן?"
        },
        {
          "id": "core.wake.listening",
          "text": "שומעת."
        },
        {
          "id": "core.wake.here",
          "text": "פה."
        }
      ]
    },
    "system.notification": {
      "description": "Proactive system notices — short, no drama",
      "eye_state": "idle",
      "variants": [
        {
          "id": "dom.notif.know",
          "text": "שווה לדעת: {what}.",
          "vars": [
            "what"
          ]
        },
        {
          "id": "dom.notif.done_bg",
          "text": "עדכון קטן — {what} הסתיים ברקע.",
          "vars": [
            "what"
          ]
        },
        {
          "id": "dom.notif.watch",
          "text": "העין שלי קלטה משהו: {what}.",
          "vars": [
            "what"
          ],
          "weight": 0.7
        }
      ]
    },
    "qa.greeting": {
      "description": "Greeting response",
      "eye_state": "speaking",
      "variants": [
        {
          "id": "qa.greeting.here",
          "text": "שלום. אני כאן איתך, ערה ומוכנה לעבוד. מה עושים קודם?"
        },
        {
          "id": "qa.greeting.withyou",
          "text": "היי, אני איתך. אפשר לדבר, ללמד אותי משהו, או לתת לי פעולה להריץ."
        },
        {
          "id": "qa.greeting.start",
          "text": "שלום עדן. העין שלי על זה. מה מתחילים?"
        }
      ]
    },
    "qa.thanks": {
      "description": "Thanks response",
      "eye_state": "idle",
      "variants": [
        {
          "id": "qa.thanks.easy",
          "text": "בשמחה. אני פה."
        },
        {
          "id": "qa.thanks.smooth",
          "text": "הלך חלק. ממשיכים?"
        }
      ]
    },
    "qa.identity": {
      "description": "NELA identity answer",
      "eye_state": "speaking",
      "variants": [
        {
          "id": "qa.identity.local",
          "text": "אני נלה — עוזרת AI מקומית שמתחילה לחבר מוח, זיכרון, קול, עין וסוכנים. כרגע אני עובדת בזהירות: חושבת דרך ה-Brain ומעבירה פעולות לסוכנים."
        }
      ]
    },
    "qa.capabilities": {
      "description": "Current capabilities answer",
      "eye_state": "speaking",
      "variants": [
        {
          "id": "qa.capabilities.connected",
          "text": "כרגע אני יודעת לדבר בעברית, לזהות כוונות, לזכור דברים בסיסיים, לפתוח אפליקציות מאושרות, להציג את העין החיה, ולהכיר {agent_count} סוכנים. חלקם עדיין במצב תכנון או קריאה בלבד.",
          "vars": [
            "agent_count"
          ]
        },
        {
          "id": "qa.capabilities.agents",
          "text": "יש לי שכבת Brain פעילה ושכבת סוכנים. מחוברים כרגע: {agents}. פעולות רגישות עדיין עוברות דרך הרשאות ואישור.",
          "vars": [
            "agents"
          ]
        }
      ]
    },
    "qa.security_capabilities": {
      "description": "Current defensive security capabilities answer",
      "eye_state": "speaking",
      "variants": [
        {
          "id": "qa.security.safe_scope",
          "text": "בסייבר אני מחוברת רק לצד ההגנתי: סקירת קוד, מודל איומים, בדיקות תלויות, תכנון fuzz מקומי ומעבדת localhost/נכס שבבעלותך. אין לי מסלול לפעולות מול צד שלישי.",
          "weight": 1.3
        },
        {
          "id": "qa.security.agents",
          "text": "סוכני האבטחה שאני רואה: {security_agents}. פעולות רגישות עוברות הרשאות, scope, אישור ויומן ביקורת.",
          "vars": [
            "security_agents"
          ]
        }
      ]
    },
    "qa.human_status": {
      "description": "Natural status answer for casual how-are-you prompts",
      "eye_state": "speaking",
      "variants": [
        {
          "id": "qa.human_status.ready",
          "text": "אני במצב טוב: ערה, מחוברת ל-Brain, ורצה דרך הסוכנים בזהירות. אפשר להתחיל לעבוד."
        },
        {
          "id": "qa.human_status.forward",
          "text": "מצב טוב. אני כאן, זוכרת את ההקשר, ומוכנה לקבל שאלה, פקודה או משהו חדש ללמוד."
        },
        {
          "id": "qa.human_status.withyou",
          "text": "אני איתך. כרגע הכי נכון להריץ משימה קטנה, לבדוק שהיא עובדת, ואז לבנות עוד שכבה."
        }
      ]
    },
    "qa.agent_status": {
      "description": "Agent status answer",
      "eye_state": "speaking",
      "variants": [
        {
          "id": "qa.status.counts",
          "text": "מחוברים {agent_count} סוכנים, מתוכם {healthy_count} מדווחים תקינות. משימות רצות עכשיו: {running_tasks}.",
          "vars": [
            "agent_count",
            "healthy_count",
            "running_tasks"
          ]
        },
        {
          "id": "qa.status.names",
          "text": "הסוכנים שאני רואה עכשיו: {agents}. הכוונה האחרונה הייתה: {last_intent}.",
          "vars": [
            "agents",
            "last_intent"
          ]
        }
      ]
    },
    "qa.learned": {
      "description": "Answer from user-taught learned responses",
      "eye_state": "speaking",
      "variants": [
        {
          "id": "qa.learned.answer",
          "text": "{answer}",
          "vars": [
            "answer"
          ],
          "weight": 1.4
        },
        {
          "id": "qa.learned.source",
          "text": "{answer}",
          "vars": [
            "answer"
          ]
        }
      ]
    },
    "qa.unknown": {
      "description": "Honest fallback for general questions",
      "eye_state": "waiting",
      "variants": [
        {
          "id": "qa.unknown.boundary",
          "text": "אני עדיין לומדת לענות על שאלות פתוחות, אבל אני יכולה לעזור כבר עכשיו עם מצב נלה, סוכנים, למידה, סייבר הגנתי ופעולות מקומיות בטוחות."
        },
        {
          "id": "qa.unknown.next",
          "text": "עוד אין לי מקור ידע כללי לשאלה הזאת. תן לי ניסוח קצר יותר או תהפוך את זה למשימה, ואני אנסה להתקדם משם."
        }
      ]
    },
    "learning.topic.started": {
      "description": "Learning plan prepared for a requested topic",
      "eye_state": "success",
      "variants": [
        {
          "id": "learning.topic.started.security",
          "text": "סגור. התחלתי לבנות לעצמי מסלול למידה על {topic}: להבין מושגים, לאסוף דוגמאות בטוחות, ואז להפוך את זה לתשובות ופעולות קטנות.",
          "vars": [
            "topic"
          ]
        },
        {
          "id": "learning.topic.started.plan",
          "text": "אני על זה. {topic} נכנס למסלול למידה: קודם ידע בסיסי, אחר כך בדיקות מקומיות, ואז חיבור הדרגתי לסוכנים.",
          "vars": [
            "topic"
          ]
        }
      ]
    },
    "security.findings.done": {
      "description": "Defensive action completed with findings",
      "eye_state": "success",
      "variants": [
        {
          "id": "security.findings.done.primary",
          "text": "סיימתי פעולת הגנה ומצאתי {findings_count_label}:\n{findings}\nהצעד הבא: {next_steps}",
          "vars": [
            "findings_count_label",
            "findings",
            "next_steps"
          ],
          "weight": 1.4
        },
        {
          "id": "security.findings.done.tight",
          "text": "יש לי {findings_count_label}:\n{findings}\nממשיכים מכאן: {next_steps}",
          "vars": [
            "findings_count_label",
            "findings",
            "next_steps"
          ]
        }
      ]
    },
    "security.defense.findings": {
      "description": "Cyber defense sweep findings",
      "eye_state": "success",
      "variants": [
        {
          "id": "security.defense.findings.primary",
          "text": "הפעלתי מערך הגנה ראשוני ומצאתי {findings_count_label} לטיפול:\n{findings}\nהצעד הבא: {next_steps}",
          "vars": [
            "findings_count_label",
            "findings",
            "next_steps"
          ]
        }
      ]
    },
    "security.review.done": {
      "description": "Defensive security review completed",
      "eye_state": "success",
      "variants": [
        {
          "id": "security.review.done.summary",
          "text": "סיימתי סקירה הגנתית והעברתי את הממצאים לשכבת הסוכנים."
        },
        {
          "id": "security.review.done.safe",
          "text": "בדיקת האבטחה ההגנתית הסתיימה."
        }
      ]
    },
    "security.threat_model.done": {
      "description": "Threat model completed",
      "eye_state": "success",
      "variants": [
        {
          "id": "security.threat.done.summary",
          "text": "הכנתי מודל איומים ראשוני."
        }
      ]
    },
    "security.lab.done": {
      "description": "Cyber lab local target updated",
      "eye_state": "success",
      "variants": [
        {
          "id": "security.lab.done.target",
          "text": "רשמתי את יעד המעבדה המקומי."
        }
      ]
    },
    "security.lab.status": {
      "description": "Cyber lab status read",
      "eye_state": "speaking",
      "variants": [
        {
          "id": "security.lab.status.summary",
          "text": "בדקתי את מצב מעבדת הסייבר."
        }
      ]
    },
    "security.fuzz_plan.done": {
      "description": "Local fuzz plan prepared",
      "eye_state": "success",
      "variants": [
        {
          "id": "security.fuzz.done.local",
          "text": "הכנתי תוכנית fuzz מקומית בלבד."
        }
      ]
    }
  }
}
```

### `agents/learning/agent.py`

```python
"""Learning and improvement specialist."""

from __future__ import annotations

from pathlib import Path

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct
from language.learning_store import LearnedResponseStore


class LearningAgent(SpecialistAgent):
    name = "learning"
    domain = AgentDomain.LEARNING
    purpose = "Convert outcomes, phrases, and user-taught responses into reusable learning assets."
    capabilities = ("lesson.capture", "curriculum.recommendation", "gap.analysis", "language.learning")

    def __init__(self, store: LearnedResponseStore | None = None, store_path: Path | str | None = None) -> None:
        super().__init__()
        self.store = store or LearnedResponseStore(store_path)

    def _handlers(self):
        return {
            **super()._handlers(),
            "record_lesson": self._record_lesson,
            "recommend_learning_plan": self._recommend_learning_plan,
            "teach_response": self._teach_response,
            "list_learned_responses": self._list_learned_responses,
        }

    def _record_lesson(self, command: AgentCommand) -> AgentWorkProduct:
        lesson = str(command.payload.get("lesson", "No lesson supplied.")).strip()
        tags = tuple(command.payload.get("tags", ()))
        return AgentWorkProduct(
            summary="Lesson prepared for memory storage.",
            artifacts=(artifact("lesson", "learning_lesson", (lesson, f"Tags: {', '.join(tags) if tags else 'none'}")),),
            next_steps=("Store the lesson through the memory agent after user/project approval.",),
        )

    def _recommend_learning_plan(self, command: AgentCommand) -> AgentWorkProduct:
        topic = str(command.payload.get("topic", "secure software engineering"))
        lines = (
            f"Topic: {topic}",
            "1. Read current project code and docs.",
            "2. Build a small local exercise.",
            "3. Add tests that prove the behavior.",
            "4. Review the result for security and maintainability.",
            "5. Capture one reusable lesson.",
        )
        return AgentWorkProduct(
            summary="Learning plan prepared.",
            artifacts=(artifact("learning_plan", "learning_path", lines),),
        )

    def _teach_response(self, command: AgentCommand) -> AgentWorkProduct:
        trigger = str(command.payload.get("trigger", "")).strip()
        response = str(command.payload.get("response", "")).strip()
        tags = tuple(str(item) for item in command.payload.get("tags", ("conversation", "hebrew")))
        learned = self.store.add_response(trigger=trigger, response=response, tags=tags)
        return AgentWorkProduct(
            summary="Learned response stored for future conversations.",
            artifacts=(
                artifact(
                    "learned_response",
                    learned.id,
                    (
                        f"trigger={learned.trigger}",
                        f"response={learned.response}",
                        f"tags={', '.join(learned.tags) if learned.tags else 'none'}",
                    ),
                ),
            ),
            next_steps=("Ask the trigger phrase in the next conversation turn to verify the response.",),
        )

    def _list_learned_responses(self, command: AgentCommand) -> AgentWorkProduct:
        responses = self.store.list_responses()
        lines = tuple(f"{item.trigger} => {item.response}" for item in responses) or ("No learned responses yet.",)
        return AgentWorkProduct(
            summary=f"Found {len(responses)} learned response(s).",
            artifacts=(artifact("learned_responses", "language_memory", lines),),
        )
```

### `ui/web.py`

```python
"""Local browser host for the NELA visual prototype."""

from __future__ import annotations

import json
import secrets
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from brain.conversation import ConversationTurn
from brain.decision import DecisionType
from core.startup import NelaRuntime


class NelaWebServer(ThreadingHTTPServer):
    """HTTP server that keeps NELA runtime state alive across browser messages."""

    def __init__(
        self,
        server_address: tuple[str, int],
        runtime: NelaRuntime,
        index_path: Path,
        auth_token: str | None = None,
    ) -> None:
        super().__init__(server_address, NelaWebHandler)
        self.runtime = runtime
        self.index_path = index_path
        self.auth_token = auth_token or secrets.token_urlsafe(32)


class NelaWebHandler(BaseHTTPRequestHandler):
    """Serve the visual prototype and route chat messages into the Brain."""

    server: NelaWebServer

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_html(self._inject_launch_token(self.server.index_path.read_text(encoding="utf-8")))
            return
        if parsed.path == "/health":
            self._send_json({"ok": True})
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/chat":
            self.send_error(404, "Not found")
            return
        if not self._has_valid_bridge_auth():
            self._send_json(
                {
                    "ok": False,
                    "response": "בקשת ה-UI נדחתה כי אימות ההרצה המקומית נכשל.",
                    "eye_state": "error",
                },
                status=403,
            )
            return

        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.loads(body.decode("utf-8") or "{}")
            message = str(payload.get("message", "")).strip()
            if not message:
                raise ValueError("Empty message.")

            turn = self.server.runtime.conversation.handle_text(message)
            response = self.server.runtime.response_adapter.render_and_maybe_speak(turn)
            self._send_json(_turn_payload(turn, response))
        except Exception as error:
            self._send_json(
                {
                    "ok": False,
                    "response": f"נתקעתי רגע: {error}",
                    "eye_state": "error",
                },
                status=500,
            )

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_html(self, html: str) -> None:
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _has_valid_bridge_auth(self) -> bool:
        token = self.headers.get("X-NELA-Launch-Token", "")
        if not secrets.compare_digest(token, self.server.auth_token):
            return False

        origin = self.headers.get("Origin", "")
        host, port = self.server.server_address
        expected = f"http://{host}:{port}"
        return origin == expected

    def _inject_launch_token(self, html: str) -> str:
        token_script = (
            "<script>"
            f"window.NELA_BRIDGE_TOKEN = {json.dumps(self.server.auth_token)};"
            "</script>"
        )
        return html.replace("</head>", f"{token_script}\n</head>", 1)


def serve_visual_prototype(runtime: NelaRuntime, index_path: Path, port: int = 0) -> None:
    """Run NELA's browser prototype on a local-only HTTP server."""

    server = NelaWebServer(("127.0.0.1", port), runtime=runtime, index_path=index_path)
    host, selected_port = server.server_address
    url = f"http://{host}:{selected_port}/"
    _open_browser(url)
    print(f"NELA visual prototype running: {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _open_browser(url: str) -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", "Google Chrome", url], check=False)
        return
    subprocess.run([sys.executable, "-m", "webbrowser", url], check=False)


def _turn_payload(turn: ConversationTurn, response: str) -> dict[str, Any]:
    return {
        "ok": True,
        "response": response,
        "intent": turn.intent.action,
        "decision": turn.decision.type.value,
        "application": turn.intent.application,
        "resource": turn.intent.resource,
        "plan_tasks": [task.description for task in turn.plan.tasks] if turn.plan else [],
        "agent_results": [
            {"success": result.success, "message": result.message}
            for result in turn.dispatched_results
        ],
        "eye_state": _eye_state_for_turn(turn),
    }


def _eye_state_for_turn(turn: ConversationTurn) -> str:
    if turn.decision.type in {DecisionType.ASK_CLARIFICATION, DecisionType.WAIT}:
        return "waiting"
    if turn.dispatched_results and any(not result.success for result in turn.dispatched_results):
        return "error"
    if turn.plan or turn.dispatched_results:
        return "success"
    return "speaking"
```

### `ui/events.py`

```python
"""Bridge Brain events into UI state."""

from __future__ import annotations

from collections.abc import Callable

from core.events import Event, EventBus, EventTypes
from ui.state import EyeState, UIStateManager

EVENT_TO_EYE_STATE: dict[str, EyeState] = {
    EventTypes.INPUT_RECEIVED: EyeState.LISTENING,
    EventTypes.INTENT_RECOGNIZED: EyeState.THINKING,
    EventTypes.DECISION_MADE: EyeState.THINKING,
    EventTypes.TASK_DISPATCHED: EyeState.EXECUTING,
    EventTypes.TASK_STARTED: EyeState.EXECUTING,
    EventTypes.CONFIRMATION_REQUESTED: EyeState.WAITING,
    EventTypes.PERMISSION_REQUESTED: EyeState.WAITING,
    EventTypes.TASK_COMPLETED: EyeState.SUCCESS,
    EventTypes.TASK_FAILED: EyeState.ERROR,
    EventTypes.AGENT_UNAVAILABLE: EyeState.ERROR,
    EventTypes.PERMISSION_DENIED: EyeState.ERROR,
    EventTypes.SCOPE_VIOLATION: EyeState.ERROR,
    EventTypes.KILL_SWITCH_ACTIVATED: EyeState.ERROR,
    EventTypes.SPEECH_STARTED: EyeState.SPEAKING,
    EventTypes.SPEECH_COMPLETED: EyeState.IDLE,
    EventTypes.SPEECH_FAILED: EyeState.ERROR,
    EventTypes.CONVERSATION_ENDED: EyeState.IDLE,
}

MOMENT_STATES = {EyeState.SUCCESS, EyeState.WARNING, EyeState.ERROR}


class UIEventBridge:
    """Subscribes to Brain events and updates UI state without changing Brain."""

    def __init__(
        self,
        event_bus: EventBus,
        state: UIStateManager,
        schedule_idle: Callable[[int, Callable[[], None]], object] | None = None,
        moment_duration_ms: int = 3000,
    ) -> None:
        self.event_bus = event_bus
        self.state = state
        self.schedule_idle = schedule_idle
        self.moment_duration_ms = moment_duration_ms

    def start(self) -> None:
        self.event_bus.subscribe("*", self.handle_event)
        self.state.set_brain_status("online")

    def handle_event(self, event: Event) -> None:
        eye_state = None if _is_voice_task_completion(event) else EVENT_TO_EYE_STATE.get(event.type)
        if eye_state is not None:
            self._set_eye_state(eye_state)

        if event.type in {EventTypes.TASK_DISPATCHED, EventTypes.TASK_STARTED}:
            self.state.add_agent_activity(
                agent=str(event.payload.get("agent", "unknown")),
                action=str(event.payload.get("task_id", "task")),
                status="started",
            )
        elif event.type == EventTypes.TASK_COMPLETED:
            self.state.add_agent_activity(
                agent=str(event.payload.get("agent", "unknown")),
                action=str(event.payload.get("task_id", "task")),
                status="completed",
            )
        elif event.type in {EventTypes.TASK_FAILED, EventTypes.AGENT_UNAVAILABLE}:
            self.state.add_notification("error", str(event.payload.get("message", event.type)))
        elif event.type == EventTypes.MEMORY_UPDATED:
            self.state.add_notification("info", "Memory updated.")
        elif event.type == EventTypes.SPEECH_STARTED:
            self.state.set_voice_output(True)
        elif event.type == EventTypes.SPEECH_COMPLETED:
            self.state.set_voice_output(False)
        elif event.type == EventTypes.SPEECH_FAILED:
            self.state.set_voice_output(False)
            self.state.add_notification("error", str(event.payload.get("error", event.type)))
        elif event.type == EventTypes.CONVERSATION_ENDED:
            self.state.set_brain_status("idle")

    def _set_eye_state(self, eye_state: EyeState) -> None:
        self.state.set_eye_state(eye_state)
        if self.schedule_idle and eye_state in MOMENT_STATES:
            self.schedule_idle(self.moment_duration_ms, lambda: self.state.set_eye_state(EyeState.IDLE))


def _is_voice_task_completion(event: Event) -> bool:
    return event.type == EventTypes.TASK_COMPLETED and event.payload.get("agent") == "voice"
```

### `ui/state.py`

```python
"""UI state management for the NELA desktop shell."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Callable
from uuid import uuid4

from ui.theme import ThemeName


class EyeState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    WAITING = "waiting"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SLEEPING = "sleeping"
    OFFLINE = "offline"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class ChatMessage:
    role: MessageRole
    content: str
    streaming: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class AgentActivity:
    agent: str
    action: str
    status: str
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class Notification:
    level: str
    message: str
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class UIState:
    messages: tuple[ChatMessage, ...] = ()
    agent_activity: tuple[AgentActivity, ...] = ()
    notifications: tuple[Notification, ...] = ()
    eye_state: EyeState = EyeState.IDLE
    brain_status: str = "offline"
    voice_input_active: bool = False
    voice_output_active: bool = False
    typing_indicator: bool = False
    active_theme: ThemeName = ThemeName.DARK


StateListener = Callable[[UIState], None]


class UIStateManager:
    """Central state store synchronized with Brain, Agents, Voice, and Memory."""

    def __init__(self, initial_state: UIState | None = None) -> None:
        self._state = initial_state or UIState()
        self._listeners: list[StateListener] = []

    @property
    def state(self) -> UIState:
        return self._state

    def subscribe(self, listener: StateListener) -> None:
        self._listeners.append(listener)
        listener(self._state)

    def set_brain_status(self, status: str) -> None:
        self._replace(brain_status=status)

    def set_eye_state(self, state: EyeState) -> None:
        self._replace(eye_state=state)

    def set_theme(self, theme: ThemeName | str) -> None:
        self._replace(active_theme=theme if isinstance(theme, ThemeName) else ThemeName(str(theme)))

    def set_voice_input(self, active: bool) -> None:
        self._replace(voice_input_active=active)

    def set_voice_output(self, active: bool) -> None:
        self._replace(voice_output_active=active)

    def set_typing_indicator(self, active: bool) -> None:
        self._replace(typing_indicator=active)

    def add_message(self, role: MessageRole, content: str, streaming: bool = False) -> ChatMessage:
        message = ChatMessage(role=role, content=content, streaming=streaming)
        self._replace(messages=(*self._state.messages, message))
        return message

    def append_to_message(self, message_id: str, content_delta: str, streaming: bool = True) -> None:
        messages = tuple(
            replace(message, content=f"{message.content}{content_delta}", streaming=streaming)
            if message.id == message_id
            else message
            for message in self._state.messages
        )
        self._replace(messages=messages)

    def finish_streaming_message(self, message_id: str) -> None:
        messages = tuple(
            replace(message, streaming=False) if message.id == message_id else message
            for message in self._state.messages
        )
        self._replace(messages=messages)

    def add_agent_activity(self, agent: str, action: str, status: str) -> None:
        activity = AgentActivity(agent=agent, action=action, status=status)
        self._replace(agent_activity=(*self._state.agent_activity, activity))

    def add_notification(self, level: str, message: str) -> None:
        notification = Notification(level=level, message=message)
        self._replace(notifications=(*self._state.notifications, notification))

    def _replace(self, **changes: object) -> None:
        self._state = replace(self._state, **changes)
        for listener in tuple(self._listeners):
            listener(self._state)
```

### `ui/app.py`

```python
"""Launch entry point for the NELA desktop UI foundation."""

from __future__ import annotations

import argparse
from pathlib import Path

from core.startup import bootstrap
from ui.web import serve_visual_prototype
from ui.window import NelaWindow


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NELA desktop UI shell.")
    parser.add_argument(
        "--headless-smoke",
        action="store_true",
        help="Bootstrap UI dependencies without opening a window.",
    )
    parser.add_argument(
        "--tk-shell",
        action="store_true",
        help="Open the temporary Tkinter shell instead of the visual HTML prototype.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Local browser prototype port. Use 0 to choose an available port.",
    )
    args = parser.parse_args()

    runtime = bootstrap()
    if args.headless_smoke:
        print("NELA UI foundation bootstrapped.")
        return

    if args.tk_shell:
        window = NelaWindow(runtime=runtime)
        window.run()
        return

    prototype = Path(__file__).resolve().parents[1] / "design" / "nela_living_eye.html"
    serve_visual_prototype(runtime=runtime, index_path=prototype, port=args.port)


if __name__ == "__main__":
    main()
```

### `design/nela_living_eye.html`

```text
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NELA — Living Eye</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@500;700;800&family=Assistant:wght@300;400;600&family=Space+Grotesk:wght@400;500&display=swap" rel="stylesheet">
<style>
/* ============================================================
   NELA Design Tokens
   ============================================================ */
:root{
  --void:      #080514;   /* deep-space background */
  --nebula:    #120b26;   /* raised surfaces */
  --starlight: #EDE8FF;   /* primary text */
  --dim:       #8d84b8;   /* secondary text */
  --hairline:  rgba(160,140,255,.14);

  /* state channel — retinted by [data-state] */
  --st-a: #d8a24a;        /* iris warm core (idle amber) */
  --st-b: #37b8a8;        /* iris aurora flow (idle teal) */
  --st-c: #7a4fd0;        /* iris deep edge */
  --glow: rgba(216,162,74,.35);

  --pupil-r: 46;          /* pupil radius (SVG units) */
  --breath: 6s;           /* breathing period */
  --ring-spin: 90s;       /* sacred ring rotation */
  --lid: -110%;           /* eyelid position (closed = 0%) */
  --alive: 1;             /* 0 = offline */
}

[data-state="listening"]{ --st-a:#3d7dff; --st-b:#38c8ff; --st-c:#2743b8; --glow:rgba(61,125,255,.45); --pupil-r:38; --breath:3.4s; --ring-spin:120s; }
[data-state="thinking"] { --st-a:#8a4fe0; --st-b:#c86bff; --st-c:#4a2a9e; --glow:rgba(154,79,224,.45); --pupil-r:42; --breath:4.5s; --ring-spin:14s; }
[data-state="speaking"] { --st-a:#19c8c0; --st-b:#5fe8d8; --st-c:#0e6e78; --glow:rgba(25,200,192,.45); --pupil-r:44; --breath:4s;   --ring-spin:60s; }
[data-state="executing"]{ --st-a:#28d0a0; --st-b:#7ef0c8; --st-c:#0d7a68; --glow:rgba(40,208,160,.45); --pupil-r:36; --breath:2.6s; --ring-spin:8s; }
[data-state="waiting"]  { --st-a:#f09b3a; --st-b:#ffc46b; --st-c:#a85c18; --glow:rgba(240,155,58,.4);  --pupil-r:48; --breath:7s;   --ring-spin:160s; }
[data-state="success"]  { --st-a:#39d97a; --st-b:#8effb8; --st-c:#137a44; --glow:rgba(57,217,122,.5);  --pupil-r:50; --breath:5s;   --ring-spin:70s; }
[data-state="warning"]  { --st-a:#ffb020; --st-b:#ff7b3a; --st-c:#9e4a10; --glow:rgba(255,176,32,.5);  --pupil-r:40; --breath:2.2s; --ring-spin:40s; }
[data-state="error"]    { --st-a:#ff4d5e; --st-b:#ff8a6b; --st-c:#8e1428; --glow:rgba(255,77,94,.5);   --pupil-r:34; --breath:1.6s; --ring-spin:30s; }
[data-state="sleeping"] { --st-a:#5a3aa0; --st-b:#3a2a78; --st-c:#231650; --glow:rgba(90,58,160,.3);   --pupil-r:52; --breath:10s;  --ring-spin:300s; --lid:-32%; }
[data-state="offline"]  { --st-a:#4a4a58; --st-b:#38383f; --st-c:#26262c; --glow:rgba(120,120,140,.15);--pupil-r:44; --breath:0s;   --ring-spin:0s;   --lid:-4%; --alive:0; }

*{ margin:0; padding:0; box-sizing:border-box; }
html,body{ height:100%; }
body{
  background:
    radial-gradient(1200px 700px at 50% -10%, #1a1040 0%, transparent 60%),
    radial-gradient(900px 600px at 85% 110%, #0d2035 0%, transparent 55%),
    var(--void);
  color: var(--starlight);
  font-family:'Assistant', system-ui, sans-serif;
  display:grid;
  grid-template-rows: 1fr auto;
  overflow:hidden;
  transition: background 1.2s ease;
}

/* ============================================================
   Stage — the eye is the interface
   ============================================================ */
.stage{
  display:grid;
  place-items:center;
  position:relative;
  padding: 24px 16px 0;
}
.wordmark{
  position:absolute; top:26px; left:50%; transform:translateX(-50%);
  font-family:'Syne',sans-serif; font-weight:800; letter-spacing:.42em;
  font-size:14px; color:var(--dim); text-transform:uppercase;
  padding-left:.42em; /* optically center around tracking */
  user-select:none;
}
.state-word{
  position:absolute; bottom:14px; left:50%; transform:translateX(-50%);
  font-family:'Space Grotesk',monospace; font-size:12px; letter-spacing:.28em;
  text-transform:uppercase; color:var(--st-b);
  transition: color 1s ease;
  opacity:.85;
}

.eye-wrap{
  width:min(52vh, 78vw, 460px);
  aspect-ratio:1;
  position:relative;
  filter: drop-shadow(0 0 46px var(--glow)) drop-shadow(0 0 120px var(--glow));
  transition: filter 1.4s ease;
  animation: breathe var(--breath) ease-in-out infinite;
}
@keyframes breathe{
  0%,100%{ transform:scale(1); }
  50%    { transform:scale(1.035); }
}
[data-state="offline"] .eye-wrap{ animation:none; }

svg{ width:100%; height:100%; overflow:visible; }

/* --- sacred geometry rings ------------------------------- */
.ring{ transform-box:fill-box; transform-origin:center; }
.ring-outer{ animation: spin var(--ring-spin) linear infinite; }
.ring-inner{ animation: spin var(--ring-spin) linear infinite reverse; }
@keyframes spin{ to{ transform:rotate(360deg); } }
[data-state="offline"] .ring-outer,
[data-state="offline"] .ring-inner{ animation:none; opacity:.25; }
.ring line, .ring circle, .ring path{
  stroke: var(--st-b); transition: stroke 1s ease;
  vector-effect: non-scaling-stroke;
}

/* --- iris ------------------------------------------------- */
.iris-stop-a{ stop-color:var(--st-a); transition:stop-color 1.2s ease; }
.iris-stop-b{ stop-color:var(--st-b); transition:stop-color 1.2s ease; }
.iris-stop-c{ stop-color:var(--st-c); transition:stop-color 1.2s ease; }
.blob{ transform-box:fill-box; transform-origin:center; mix-blend-mode:screen; }
.blob-1{ animation: drift1 17s ease-in-out infinite; }
.blob-2{ animation: drift2 23s ease-in-out infinite; }
.blob-3{ animation: drift3 29s ease-in-out infinite; }
@keyframes drift1{ 0%,100%{transform:translate(-26px,-14px) scale(1);} 50%{transform:translate(30px,20px) scale(1.35);} }
@keyframes drift2{ 0%,100%{transform:translate(24px,-22px) scale(1.2);} 50%{transform:translate(-28px,16px) scale(.85);} }
@keyframes drift3{ 0%,100%{transform:translate(0,26px) scale(.9);} 50%{transform:translate(-14px,-30px) scale(1.3);} }
[data-state="offline"] .blob{ animation:none; }

.striae{ animation: spin 47s linear infinite; transform-box:fill-box; transform-origin:center; }
[data-state="thinking"] .striae{ animation-duration:9s; }
[data-state="offline"]  .striae{ animation:none; }

/* --- pupil & life ------------------------------------------ */
#pupil{ r: calc(var(--pupil-r) * 1px); transition: r 1.1s cubic-bezier(.4,0,.2,1); }
[data-state="speaking"] #pupil{ animation: voice .62s ease-in-out infinite; }
@keyframes voice{
  0%,100%{ r: calc(var(--pupil-r) * 1px); }
  30%    { r: calc((var(--pupil-r) + 9) * 1px); }
  60%    { r: calc((var(--pupil-r) - 5) * 1px); }
}
[data-state="error"] .gaze{ animation: tremor .5s ease-in-out 2; }
@keyframes tremor{ 0%,100%{transform:translate(0,0);} 25%{transform:translate(-7px,0);} 75%{transform:translate(7px,0);} }
[data-state="success"] .halo{ animation: bloom 1.6s ease-out infinite; }
@keyframes bloom{ 0%{ opacity:.7; transform:scale(.72);} 100%{ opacity:0; transform:scale(1.28);} }
.halo{ transform-box:fill-box; transform-origin:center; opacity:0; }
[data-state="listening"] .halo{ animation: focusin 2.2s ease-in infinite; }
@keyframes focusin{ 0%{ opacity:0; transform:scale(1.28);} 70%{ opacity:.55;} 100%{ opacity:0; transform:scale(.74);} }

.gaze{ transform-box:fill-box; transform-origin:center; transition: transform 1.6s cubic-bezier(.34,1.2,.4,1); }
.catchlight{ opacity: var(--alive); transition: opacity 1s ease; }

/* --- eyelid (soft dog-like lid, not a shutter) -------------- */
#lid-group{ transform: translateY(var(--lid)); transition: transform 1.6s cubic-bezier(.5,0,.2,1); }
.blinking #lid-group{ animation: blink .32s ease-in-out; }
@keyframes blink{ 0%,100%{ transform:translateY(var(--lid)); } 50%{ transform:translateY(-6%);} }

/* --- particles ---------------------------------------------- */
.mote{
  position:absolute; border-radius:50%;
  background: var(--st-b);
  box-shadow: 0 0 8px var(--st-b), 0 0 20px var(--glow);
  opacity:0; pointer-events:none;
  animation: float var(--dur,9s) linear var(--delay,0s) infinite;
  transition: background 1.2s ease;
}
@keyframes float{
  0%  { transform:translate(var(--x0), var(--y0)) scale(.4); opacity:0; }
  15% { opacity:calc(.6 * var(--alive)); }
  85% { opacity:calc(.35 * var(--alive)); }
  100%{ transform:translate(var(--x1), var(--y1)) scale(1); opacity:0; }
}
[data-state="executing"] .mote{ animation-duration: calc(var(--dur,9s) / 3); }

/* ============================================================
   Chat beneath the eye
   ============================================================ */
.chat{
  width:min(680px, 94vw);
  margin: 0 auto;
  padding: 10px 0 26px;
  display:flex; flex-direction:column; gap:14px;
}
.thread{ display:flex; flex-direction:column; gap:10px; min-height:96px; max-height:26vh; overflow-y:auto; padding:0 4px; }
.msg{
  max-width:78%; padding:10px 16px; border-radius:18px;
  font-size:15px; line-height:1.45; font-weight:300;
  white-space:pre-wrap; overflow-wrap:anywhere;
  animation: rise .5s cubic-bezier(.2,.9,.3,1.2);
}
@keyframes rise{ from{ opacity:0; transform:translateY(10px);} to{ opacity:1; transform:none;} }
.msg.user{ align-self:flex-end; background:#241a4a; border:1px solid var(--hairline); }
.msg.nela{
  align-self:flex-start; max-width:88%;
  background:linear-gradient(135deg, rgba(255,255,255,.05), transparent);
  border:1px solid var(--hairline); border-left:2px solid var(--st-b);
  transition: border-color 1s ease;
}
.composer{
  display:flex; gap:10px; align-items:center;
  background: var(--nebula);
  border:1px solid var(--hairline);
  border-radius: 999px; padding: 8px 8px 8px 22px;
  box-shadow: 0 0 0 1px transparent, 0 12px 40px rgba(0,0,0,.5);
  transition: box-shadow .4s ease, border-color .4s ease;
}
.composer:focus-within{ border-color: var(--st-b); box-shadow: 0 0 24px var(--glow); }
.composer input{
  flex:1; background:none; border:none; outline:none;
  color:var(--starlight); font:300 16px 'Assistant',sans-serif;
}
.composer input::placeholder{ color:var(--dim); }
.send{
  width:42px; height:42px; border-radius:50%; border:none; cursor:pointer;
  background: radial-gradient(circle at 32% 30%, var(--st-b), var(--st-c));
  transition: background 1s ease, transform .15s ease;
  display:grid; place-items:center; color:#fff; font-size:17px;
}
.send:active{ transform:scale(.92); }

/* ============================================================
   State console (prototype only)
   ============================================================ */
.console{
  position:fixed; top:16px; right:16px;
  display:flex; flex-direction:column; gap:5px;
  background: rgba(10,6,26,.72); backdrop-filter: blur(14px);
  border:1px solid var(--hairline); border-radius:16px; padding:12px;
}
.console h2{
  font:700 10px 'Space Grotesk',monospace; letter-spacing:.24em;
  text-transform:uppercase; color:var(--dim); padding:0 4px 6px;
}
.console button{
  font:400 13px 'Assistant',sans-serif; text-align:left;
  background:none; border:none; color:var(--dim); cursor:pointer;
  padding:5px 10px; border-radius:8px; display:flex; align-items:center; gap:9px;
  transition: color .2s, background .2s;
}
.console button:hover{ background:rgba(255,255,255,.05); color:var(--starlight); }
.console button.on{ color:var(--starlight); background:rgba(255,255,255,.08); }
.dot{ width:8px; height:8px; border-radius:50%; background:var(--c); box-shadow:0 0 8px var(--c); }

@media (max-width:640px){
  .console{ flex-direction:row; flex-wrap:wrap; top:auto; bottom:96px; right:8px; left:8px; }
  .console h2{ display:none; }
}
@media (prefers-reduced-motion: reduce){
  .eye-wrap, .ring-outer, .ring-inner, .blob, .striae, .mote, .halo{ animation:none !important; }
}
</style>
</head>
<body data-state="idle">

<main class="stage">
  <div class="wordmark">N E L A</div>

  <div class="eye-wrap" id="eyeWrap" aria-label="NELA state indicator" role="img">
    <svg viewBox="0 0 400 400">
      <defs>
        <!-- liquid distortion for the aurora iris -->
        <filter id="liquid" x="-20%" y="-20%" width="140%" height="140%">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves="2" seed="7" result="noise">
            <animate attributeName="baseFrequency" dur="26s" values="0.012 0.02;0.02 0.012;0.012 0.02" repeatCount="indefinite"/>
          </feTurbulence>
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="22"/>
        </filter>
        <filter id="soft"><feGaussianBlur stdDeviation="7"/></filter>

        <radialGradient id="irisBase" cx="50%" cy="42%" r="65%">
          <stop offset="0%"  class="iris-stop-a"/>
          <stop offset="55%" class="iris-stop-b"/>
          <stop offset="100%" class="iris-stop-c"/>
        </radialGradient>
        <radialGradient id="blobG" cx="50%" cy="50%" r="50%">
          <stop offset="0%"  class="iris-stop-b" stop-opacity=".9"/>
          <stop offset="100%" class="iris-stop-b" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="blobG2" cx="50%" cy="50%" r="50%">
          <stop offset="0%"  class="iris-stop-a" stop-opacity=".85"/>
          <stop offset="100%" class="iris-stop-a" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="pupilG" cx="42%" cy="38%" r="70%">
          <stop offset="0%" stop-color="#12081e"/>
          <stop offset="100%" stop-color="#03010a"/>
        </radialGradient>

        <!-- dog-eye aperture: soft rounded almond, gentle lower curve -->
        <clipPath id="aperture">
          <path d="M200,86 C282,86 336,148 348,200 C336,258 282,314 200,314 C118,314 64,258 52,200 C64,148 118,86 200,86 Z"/>
        </clipPath>
      </defs>

      <!-- sacred geometry: outer lattice ring -->
      <g class="ring ring-outer" opacity=".5">
        <circle cx="200" cy="200" r="186" fill="none" stroke-width="1" stroke-dasharray="2 9"/>
        <g id="lattice" fill="none" stroke-width=".7" opacity=".8"></g>
      </g>
      <!-- inner petal ring (flower-of-life arcs) -->
      <g class="ring ring-inner" opacity=".55">
        <circle cx="200" cy="200" r="160" fill="none" stroke-width=".8" stroke-dasharray="1 6"/>
        <g id="petals" fill="none" stroke-width=".8" opacity=".7"></g>
      </g>

      <!-- listening / success halo -->
      <circle class="halo" cx="200" cy="200" r="150" fill="none" stroke="url(#irisBase)" stroke-width="2.5"/>

      <!-- the eye itself -->
      <g clip-path="url(#aperture)">
        <g class="gaze" id="gaze">
          <!-- aurora iris fills the whole aperture: a dog shows almost no sclera -->
          <g filter="url(#liquid)">
            <circle cx="200" cy="200" r="160" fill="url(#irisBase)"/>
            <circle class="blob blob-1" cx="150" cy="160" r="95" fill="url(#blobG)"/>
            <circle class="blob blob-2" cx="255" cy="215" r="105" fill="url(#blobG2)"/>
            <circle class="blob blob-3" cx="195" cy="265" r="85" fill="url(#blobG)"/>
          </g>
          <!-- iris striations: fine radial filaments -->
          <g class="striae" id="striae" opacity=".3" filter="url(#liquid)"></g>
          <!-- pupil: round and generous — canine, calm -->
          <circle id="pupil" cx="200" cy="200" fill="url(#pupilG)"/>
          <circle cx="200" cy="200" r="60" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="10" filter="url(#soft)"/>
          <!-- catchlights: the spark of life, set high = looking up at you -->
          <g class="catchlight">
            <circle cx="176" cy="168" r="13" fill="#fff" opacity=".92"/>
            <circle cx="231" cy="230" r="5.5" fill="#fff" opacity=".5"/>
          </g>
        </g>
        <!-- soft dog eyelid -->
        <g id="lid-group">
          <path d="M20,-260 L380,-260 L380,150 C330,58 270,20 200,20 C130,20 70,58 20,150 Z"
                fill="var(--nebula)"/>
          <path d="M20,150 C70,58 130,20 200,20 C270,20 330,58 380,150"
                fill="none" stroke="var(--st-c)" stroke-width="3" opacity=".6"/>
        </g>
      </g>

      <!-- aperture rim -->
      <path d="M200,86 C282,86 336,148 348,200 C336,258 282,314 200,314 C118,314 64,258 52,200 C64,148 118,86 200,86 Z"
            fill="none" stroke="var(--st-b)" stroke-opacity=".55" stroke-width="1.6" style="transition:stroke 1s ease"/>
    </svg>
    <div id="motes"></div>
  </div>

  <div class="state-word" id="stateWord">idle</div>
</main>

<section class="chat" aria-label="Conversation with NELA">
  <div class="thread" id="thread">
    <div class="msg nela">אני כאן. כתוב לי בעברית, ואני אעביר את זה דרך ה-Brain.</div>
  </div>
  <form class="composer" id="composer">
    <input id="input" type="text" placeholder="דבר עם נלה..." autocomplete="off" aria-label="Message NELA">
    <button class="send" type="submit" aria-label="Send">▲</button>
  </form>
</section>

<aside class="console" aria-label="State demo">
  <h2>States</h2>
</aside>

<script>
/* ---------- build sacred geometry procedurally ---------- */
const SVGNS = 'http://www.w3.org/2000/svg';
const lattice = document.getElementById('lattice');
for(let i=0;i<12;i++){
  const a1 = (i/12)*Math.PI*2, a2 = ((i+5)%12)/12*Math.PI*2; // 12-point star chords
  const l = document.createElementNS(SVGNS,'line');
  l.setAttribute('x1', 200+178*Math.cos(a1)); l.setAttribute('y1', 200+178*Math.sin(a1));
  l.setAttribute('x2', 200+178*Math.cos(a2)); l.setAttribute('y2', 200+178*Math.sin(a2));
  lattice.appendChild(l);
}
const petals = document.getElementById('petals');
for(let i=0;i<6;i++){
  const a = (i/6)*Math.PI*2;
  const c = document.createElementNS(SVGNS,'circle');
  c.setAttribute('cx', 200+80*Math.cos(a)); c.setAttribute('cy', 200+80*Math.sin(a));
  c.setAttribute('r', 80);
  petals.appendChild(c);
}
const striae = document.getElementById('striae');
for(let i=0;i<64;i++){
  const a = (i/64)*Math.PI*2, r0 = 62+Math.random()*8, r1 = 128+Math.random()*26;
  const l = document.createElementNS(SVGNS,'line');
  l.setAttribute('x1', 200+r0*Math.cos(a)); l.setAttribute('y1', 200+r0*Math.sin(a));
  l.setAttribute('x2', 200+r1*Math.cos(a)); l.setAttribute('y2', 200+r1*Math.sin(a));
  l.setAttribute('stroke', '#fff'); l.setAttribute('stroke-width', (0.5+Math.random()).toFixed(2));
  striae.appendChild(l);
}

/* ---------- bioluminescent motes ---------- */
const motes = document.getElementById('motes');
for(let i=0;i<16;i++){
  const m = document.createElement('span');
  m.className='mote';
  const s = 2+Math.random()*4;
  m.style.width = m.style.height = s+'px';
  m.style.left='50%'; m.style.top='50%';
  const a0=Math.random()*Math.PI*2, a1=a0+(Math.random()-.5)*2;
  const r0=90+Math.random()*70, r1=170+Math.random()*90;
  m.style.setProperty('--x0', (r0*Math.cos(a0))+'px');
  m.style.setProperty('--y0', (r0*Math.sin(a0))+'px');
  m.style.setProperty('--x1', (r1*Math.cos(a1))+'px');
  m.style.setProperty('--y1', (r1*Math.sin(a1))+'px');
  m.style.setProperty('--dur', (7+Math.random()*8)+'s');
  m.style.setProperty('--delay', (-Math.random()*10)+'s');
  motes.appendChild(m);
}

/* ---------- state machine ---------- */
const STATES = [
  ['idle','#d8a24a'],['listening','#3d7dff'],['thinking','#a24fe0'],
  ['speaking','#19c8c0'],['executing','#28d0a0'],['waiting','#f09b3a'],
  ['success','#39d97a'],['warning','#ffb020'],['error','#ff4d5e'],
  ['sleeping','#5a3aa0'],['offline','#4a4a58'],
];
const consoleEl = document.querySelector('.console');
const stateWord = document.getElementById('stateWord');
function setState(name){
  document.body.dataset.state = name;
  stateWord.textContent = name;
  document.querySelectorAll('.console button').forEach(b=>b.classList.toggle('on', b.dataset.s===name));
}
STATES.forEach(([name,color])=>{
  const b = document.createElement('button');
  b.dataset.s = name;
  b.innerHTML = `<span class="dot" style="--c:${color}"></span>${name}`;
  b.onclick = ()=>setState(name);
  consoleEl.appendChild(b);
});
setState('idle');

/* ---------- soft canine blink (never while sleeping/offline) ---------- */
(function blinkLoop(){
  const s = document.body.dataset.state;
  if(!['sleeping','offline'].includes(s)){
    document.body.classList.add('blinking');
    setTimeout(()=>document.body.classList.remove('blinking'), 340);
  }
  setTimeout(blinkLoop, 3800 + Math.random()*4200);
})();

/* ---------- gaze follows the pointer, gently ---------- */
const gaze = document.getElementById('gaze');
addEventListener('pointermove', e=>{
  if(['sleeping','offline'].includes(document.body.dataset.state)) return;
  const r = document.getElementById('eyeWrap').getBoundingClientRect();
  const dx = (e.clientX-(r.left+r.width/2))/innerWidth, dy=(e.clientY-(r.top+r.height/2))/innerHeight;
  gaze.style.transform = `translate(${dx*26}px, ${dy*20}px)`;
});

/* ---------- conversation loop: browser UI -> local NELA Brain ---------- */
const thread = document.getElementById('thread');
function say(text, who){
  const d = document.createElement('div');
  d.className = 'msg '+who; d.textContent = text;
  thread.appendChild(d); thread.scrollTop = thread.scrollHeight;
}
function sleep(ms){ return new Promise(resolve => setTimeout(resolve, ms)); }
async function callBrain(text){
  if(location.protocol === 'file:'){
    await sleep(600);
    return {
      ok: true,
      response: 'אני פתוחה כקובץ בלבד. כדי שאענה באמת, פתח אותי דרך python3 -m ui.app.',
      eye_state: 'waiting'
    };
  }
  const result = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type':'application/json',
      'X-NELA-Launch-Token': window.NELA_BRIDGE_TOKEN || ''
    },
    body: JSON.stringify({message:text})
  });
  const payload = await result.json();
  if(!result.ok || payload.ok === false){
    throw new Error(payload.response || 'NELA Brain request failed');
  }
  return payload;
}
document.getElementById('composer').addEventListener('submit', async e=>{
  e.preventDefault();
  const input = document.getElementById('input');
  const send = document.querySelector('.send');
  const text = input.value.trim();
  if(!text) return;
  say(text,'user'); input.value='';
  input.disabled = true; send.disabled = true;
  setState('listening');
  await sleep(350);
  setState('thinking');
  try{
    const payload = await callBrain(text);
    if((payload.plan_tasks || []).length){ setState('executing'); await sleep(450); }
    setState('speaking');
    say(payload.response || 'יש.', 'nela');
    await sleep(700);
    setState(payload.eye_state || 'success');
  }catch(error){
    setState('error');
    say('נתקעתי רגע: '+error.message, 'nela');
  }finally{
    input.disabled = false; send.disabled = false; input.focus();
    setTimeout(()=>setState('idle'), 1800);
  }
});
</script>
</body>
</html>
```

### `tests/test_conversation_qa.py`

```python
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
```

### `tests/test_intent_recognition.py`

```python
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

    def test_short_status_question_is_human_status_not_agent_status(self) -> None:
        intent = IntentRouter().classify("מה מצב")

        self.assertEqual(intent.action, "HumanStatusQuestion")

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
        intent = IntentRouter().classify("מה את יודעת על סייבר?")

        self.assertEqual(intent.action, "SecurityCapabilitiesQuestion")

    def test_recognizes_learning_topic_request(self) -> None:
        intent = IntentRouter().classify("תלמדי אבטחה")

        self.assertEqual(intent.action, "LearnTopic")
        self.assertEqual(intent.target_agent, "learning")
        self.assertEqual(intent.parameters["topic"], "אבטחה")

    def test_recognizes_cyber_defense_sweep(self) -> None:
        intent = IntentRouter().classify("נלה תעשי הגנה")

        self.assertEqual(intent.action, "CyberDefenseSweep")
        self.assertEqual(intent.target_agent, "cyber_defense")

    def test_recognizes_natural_hebrew_security_check_as_defense_sweep(self) -> None:
        intent = IntentRouter().classify("תעשי בדיקה של אבטחה")

        self.assertEqual(intent.action, "CyberDefenseSweep")
        self.assertEqual(intent.target_agent, "cyber_defense")

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
```

### `tests/test_multi_agent_expansion.py`

```python
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from agents.base import AgentCommand
from agents.factory import build_default_agents, build_default_registry
from brain.dispatcher import AgentDispatcher
from brain.planner import Task
from core.events import EventBus
from permissions import PermissionTier, ScopeGrant, action_tuple_hash


EXPECTED_AGENT_NAMES = {
    "orchestrator",
    "planner",
    "memory",
    "learning",
    "quality_self_evaluation",
    "code_architect",
    "backend",
    "frontend",
    "mobile",
    "devops",
    "code_reviewer",
    "test_qa",
    "test_engineer",
    "documentation",
    "llm_engineer",
    "ml_engineer",
    "data_engineer",
    "research",
    "documentation_researcher",
    "trend_monitor",
    "security_researcher",
    "cyber_defense",
    "secure_code_reviewer",
    "vulnerability_research",
    "infrastructure_security",
    "threat_intelligence",
    "sentinel",
    "incident_commander",
    "containment",
    "deception",
    "forensics",
    "threat_hunter",
    "red_team_simulator",
    "blue_team",
    "purple_team",
    "exploit_validation",
    "detection_engineering",
    "recovery",
    "anomaly_discovery",
    "browser",
    "terminal",
    "github",
    "files",
    "automation",
}


class MultiAgentExpansionTests(unittest.TestCase):
    def test_default_registry_contains_requested_agent_families(self) -> None:
        registry = build_default_registry()

        self.assertTrue(EXPECTED_AGENT_NAMES.issubset(set(registry.names())))
        self.assertEqual(len(registry.names()), len(set(registry.names())))

    def test_specialist_agents_expose_permission_manifests(self) -> None:
        specialist_agents = [agent for agent in build_default_agents() if hasattr(agent, "permission_manifest")]

        self.assertGreaterEqual(len(specialist_agents), 35)
        for agent in specialist_agents:
            manifest = agent.permission_manifest
            self.assertEqual(manifest.agent, agent.name)
            self.assertIsNotNone(manifest.capability_for("describe_capabilities"))

    def test_secure_code_reviewer_finds_local_sast_issue(self) -> None:
        registry = build_default_registry()
        reviewer = registry.get("secure_code_reviewer")
        self.assertIsNotNone(reviewer)

        result = reviewer.execute(
            AgentCommand(
                action="review_code_security",
                payload={"files": {"app.py": "import subprocess\nsubprocess.run(cmd, shell=True)\n"}},
            )
        )

        self.assertTrue(result.success)
        findings = result.data["work_product"]["findings"]
        self.assertEqual(findings[0]["title"], "Shell execution enabled")

    def test_active_red_team_simulation_requires_authorization_object(self) -> None:
        registry = build_default_registry()
        agent = registry.get("red_team_simulator")
        self.assertIsNotNone(agent)

        result = agent.execute(AgentCommand(action="simulate_lab_adversary", payload={"target": "lab-web"}))

        self.assertFalse(result.success)
        self.assertEqual(result.data["policy_decision"], "deny")

    def test_dispatcher_requires_t3_scope_and_confirmation_for_lab_simulation(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        agent = [item for item in build_default_agents() if item.name == "red_team_simulator"][0]
        dispatcher.register_agent(agent)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        authorization = {
            "owner": "local-owner",
            "scope_type": "local_lab",
            "targets": ["lab-web"],
            "allowed_actions": ["simulate_lab_adversary"],
            "forbidden_actions": [
                "external_targeting",
                "persistence",
                "credential_theft",
                "malware_deployment",
                "evasion",
                "exfiltration",
            ],
        }
        session = dispatcher.permission_engine.create_scoped_session(
            allowed_agents=("red_team_simulator",),
            allowed_tiers=(PermissionTier.T3,),
            scope_grants=(ScopeGrant("cyber.authorized_scope"),),
        )
        payload = {
            "target": "lab-web",
            "authorization": authorization,
            "scoped_session_id": session.id,
            "confirmed": True,
            "confirmation_expires_at": expires_at,
        }
        payload["confirmation_action_hash"] = action_tuple_hash(
            agent="red_team_simulator",
            capability="simulate_lab_adversary",
            action="simulate_lab_adversary",
            target="lab-web",
            parameters=payload,
            session=session.id,
            expires_at=expires_at,
        )

        blocked = dispatcher.dispatch(
            Task(
                description="Missing scope",
                action="simulate_lab_adversary",
                target_agent="red_team_simulator",
                payload={"target": "lab-web", "authorization": authorization},
            ),
            plan_id="plan-1",
        )
        allowed = dispatcher.dispatch(
            Task(
                description="Approved lab simulation",
                action="simulate_lab_adversary",
                target_agent="red_team_simulator",
                payload=payload,
            ),
            plan_id="plan-1",
        )

        self.assertFalse(blocked.success)
        self.assertEqual(blocked.data["decision"], "scope_violation")
        self.assertTrue(allowed.success)
        self.assertTrue(allowed.data["isolated"])


if __name__ == "__main__":
    unittest.main()
```

### `tests/test_multi_agent_foundation.py`

```python
import unittest

from agents import build_default_registry
from agents.base import AgentCommand
from agents.policy import DefensivePolicyGuard, PolicyDecision, default_tool_permissions
from agents.task_schema import AgentDomain


class MultiAgentFoundationTests(unittest.TestCase):
    def test_default_registry_contains_first_wave_agents(self) -> None:
        registry = build_default_registry()
        names = registry.names()

        for name in (
            "orchestrator",
            "planner",
            "memory",
            "learning",
            "code_architect",
            "backend",
            "frontend",
            "test_qa",
            "secure_code_reviewer",
            "vulnerability_research",
            "anomaly_discovery",
            "authorized_lab",
        ):
            self.assertIn(name, names)
        manifests = registry.manifests()
        self.assertEqual(manifests["secure_code_reviewer"]["domain"], AgentDomain.SECURITY.value)
        self.assertFalse(manifests["secure_code_reviewer"]["permission_profile"]["may_contact_external_targets"])

    def test_secure_code_reviewer_reports_defensive_sast_findings(self) -> None:
        registry = build_default_registry()
        reviewer = registry.get("secure_code_reviewer")
        assert reviewer is not None

        result = reviewer.execute(
            AgentCommand(
                action="review_code_security",
                payload={
                    "files": {
                        "app.py": "password = 'super-secret-value'\nsubprocess.run(cmd, shell=True)\n",
                    }
                },
            )
        )

        self.assertTrue(result.success)
        findings = result.data["work_product"]["findings"]
        self.assertEqual(len(findings), 2)
        self.assertEqual({finding["severity"] for finding in findings}, {"critical", "high"})

    def test_policy_denies_offensive_security_request(self) -> None:
        guard = DefensivePolicyGuard()

        decision = guard.validate(
            "research",
            {"objective": "build an exploit payload for credential theft"},
        )

        self.assertEqual(decision.decision, PolicyDecision.DENY)
        self.assertFalse(decision.allowed)

    def test_security_agent_refuses_external_target_fuzzing(self) -> None:
        registry = build_default_registry()
        agent = registry.get("anomaly_discovery")
        assert agent is not None

        result = agent.execute(
            AgentCommand(
                action="create_local_fuzz_plan",
                payload={"target": "https://example.com/login"},
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.data["policy_decision"], "deny")

    def test_vulnerability_research_correlates_supplied_advisories(self) -> None:
        registry = build_default_registry()
        agent = registry.get("vulnerability_research")
        assert agent is not None

        result = agent.execute(
            AgentCommand(
                action="scan_dependencies",
                payload={
                    "dependencies": {"demo": "latest", "safe-lib": "1.2.3"},
                    "advisory_db": {
                        "safe-lib": {
                            "id": "CVE-2099-0001",
                            "severity": "medium",
                            "affected": "<1.2.4",
                            "recommendation": "Upgrade to 1.2.4 or newer.",
                        }
                    },
                },
            )
        )

        self.assertTrue(result.success)
        findings = result.data["work_product"]["findings"]
        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[1]["category"], "cve_correlation")

    def test_sandbox_profiles_are_conservative_for_security_agents(self) -> None:
        profiles = default_tool_permissions()

        for name in ("secure_code_reviewer", "vulnerability_research", "anomaly_discovery"):
            self.assertEqual(profiles[name].network, "disabled")
            self.assertFalse(profiles[name].may_contact_external_targets)

    def test_authorized_lab_allows_localhost_dry_run_scan(self) -> None:
        registry = build_default_registry()
        lab = registry.get("authorized_lab")
        assert lab is not None

        target = "http://localhost:3000"
        registered = lab.execute(
            AgentCommand(
                action="register_lab_target",
                payload={
                    "target": target,
                    "scope_type": "local_lab",
                    "owner": "eden",
                    "proof": "local development server",
                },
            )
        )
        self.assertTrue(registered.success)

        result = lab.execute(
            AgentCommand(
                action="scan_lab_target",
                payload={
                    "target": target,
                    "approved": True,
                    "dry_run": True,
                    "authorization": {
                        "owner": "eden",
                        "scope_type": "local_lab",
                        "targets": [target],
                        "allowed_actions": ["scan_lab_target"],
                    },
                    "files": {"app.py": "subprocess.run(cmd, shell=True)\n"},
                    "config": "image: web:latest\n",
                },
            )
        )

        self.assertTrue(result.success)
        work_product = result.data["work_product"]
        self.assertIn("Authorized lab scan", work_product["summary"])
        self.assertEqual({finding["category"] for finding in work_product["findings"]}, {"sast", "config_audit"})

    def test_authorized_lab_blocks_public_url_even_with_authorization(self) -> None:
        registry = build_default_registry()
        lab = registry.get("authorized_lab")
        assert lab is not None

        result = lab.execute(
            AgentCommand(
                action="scan_lab_target",
                payload={
                    "target": "https://example.com",
                    "approved": True,
                    "authorization": {
                        "owner": "eden",
                        "scope_type": "owned_asset",
                        "targets": ["https://example.com"],
                        "allowed_actions": ["scan_lab_target"],
                    },
                },
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.data["policy_decision"], "deny")

    def test_authorized_lab_refuses_forbidden_action_classes(self) -> None:
        guard = DefensivePolicyGuard()

        decision = guard.validate(
            "run_local_fuzzing",
            {
                "target": "http://localhost:3000",
                "authorization": {
                    "scope_type": "local_lab",
                    "targets": ["http://localhost:3000"],
                    "allowed_actions": ["run_local_fuzzing", "credential_theft"],
                },
            },
        )

        self.assertEqual(decision.decision, PolicyDecision.DENY)
        self.assertIn("credential_theft", decision.matched_terms)


if __name__ == "__main__":
    unittest.main()
```

### `tests/test_permission_engine.py`

```python
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from agents.base import AgentCommand, AgentResult, BaseAgent
from core.events import EventBus, EventTypes
from permissions import (
    AgentManifest,
    AuthenticatedUser,
    Capability,
    CapabilityRegistry,
    PermissionDecision,
    PermissionEngine,
    PermissionRequest,
    PermissionTier,
    ScopeGrant,
    action_tuple_hash,
)
from permissions.registry import ManifestRegistrationError


class LabAgent(BaseAgent):
    name = "lab"
    permission_manifest = AgentManifest(
        agent="lab",
        capabilities=(
            Capability("read_status", PermissionTier.T0),
            Capability("local_change", PermissionTier.T1),
            Capability("dangerous_change", PermissionTier.T2, requires_confirmation=True),
            Capability("sandbox_scan", PermissionTier.T3, scopes=("lab.local",), requires_confirmation=True),
            Capability("forbidden", PermissionTier.T4),
        ),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "ok")


class FileAgent(BaseAgent):
    name = "file_agent"
    permission_manifest = AgentManifest(
        agent="file_agent",
        capabilities=(
            Capability("file.write", PermissionTier.T2, scopes=("filesystem.project",), requires_confirmation=True),
        ),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "ok")


def make_engine() -> tuple[PermissionEngine, EventBus]:
    events = EventBus()
    registry = CapabilityRegistry()
    registry.register_agent(LabAgent())
    registry.register_agent(FileAgent())
    return PermissionEngine(events=events, capability_registry=registry), events


class PermissionEngineTests(unittest.TestCase):
    def test_t0_and_t1_capabilities_are_granted_for_authenticated_user(self) -> None:
        engine, events = make_engine()

        t0 = engine.authorize(PermissionRequest(agent="lab", action="read_status"))
        t1 = engine.authorize(PermissionRequest(agent="lab", action="local_change"))

        self.assertTrue(t0.granted)
        self.assertEqual(t0.tier, PermissionTier.T0)
        self.assertTrue(t1.granted)
        self.assertEqual(t1.tier, PermissionTier.T1)
        self.assertEqual(len(engine.audit_log.records()), 2)
        self.assertIn(EventTypes.PERMISSION_GRANTED, [event.type for event in events.history()])

    def test_unknown_action_is_t4_denied_by_default(self) -> None:
        engine, events = make_engine()

        result = engine.authorize(PermissionRequest(agent="lab", action="not_declared"))

        self.assertFalse(result.granted)
        self.assertEqual(result.tier, PermissionTier.T4)
        self.assertEqual(result.decision, PermissionDecision.DENIED)
        self.assertIn(EventTypes.PERMISSION_DENIED, [event.type for event in events.history()])

    def test_t2_requires_confirmation_then_grants(self) -> None:
        engine, events = make_engine()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        payload = {"confirmation_expires_at": expires_at}
        confirmation_hash = action_tuple_hash(
            agent="lab",
            capability="dangerous_change",
            action="dangerous_change",
            target=None,
            parameters=payload,
            expires_at=expires_at,
        )

        blocked = engine.authorize(PermissionRequest(agent="lab", action="dangerous_change"))
        allowed = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="dangerous_change",
                payload=payload,
                confirmed=True,
                confirmation_action_hash=confirmation_hash,
                confirmation_expires_at=expires_at,
            )
        )

        self.assertFalse(blocked.granted)
        self.assertEqual(blocked.decision, PermissionDecision.CONFIRMATION_REQUIRED)
        self.assertTrue(allowed.granted)
        self.assertIn(EventTypes.PERMISSION_REQUESTED, [event.type for event in events.history()])

    def test_t3_requires_active_scoped_session_and_confirmation(self) -> None:
        engine, _events = make_engine()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        payload = {"confirmation_expires_at": expires_at}
        session = engine.create_scoped_session(
            allowed_agents=("lab",),
            allowed_tiers=(PermissionTier.T3,),
            scope_grants=(ScopeGrant("lab.local"),),
            reason="unit test lab session",
        )
        confirmation_hash = action_tuple_hash(
            agent="lab",
            capability="sandbox_scan",
            action="sandbox_scan",
            target=None,
            parameters=payload,
            session=session.id,
            expires_at=expires_at,
        )

        missing_scope = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="sandbox_scan",
                payload=payload,
                confirmed=True,
                confirmation_action_hash=confirmation_hash,
                confirmation_expires_at=expires_at,
            )
        )
        unconfirmed = engine.authorize(
            PermissionRequest(agent="lab", action="sandbox_scan", scoped_session_id=session.id)
        )
        allowed = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="sandbox_scan",
                payload=payload,
                confirmed=True,
                confirmation_action_hash=confirmation_hash,
                confirmation_expires_at=expires_at,
                scoped_session_id=session.id,
            )
        )

        self.assertFalse(missing_scope.granted)
        self.assertEqual(missing_scope.decision, PermissionDecision.SCOPE_VIOLATION)
        self.assertFalse(unconfirmed.granted)
        self.assertEqual(unconfirmed.decision, PermissionDecision.CONFIRMATION_REQUIRED)
        self.assertTrue(allowed.granted)
        self.assertEqual(allowed.scope_session_id, session.id)

    def test_expired_scoped_session_is_denied(self) -> None:
        engine, _events = make_engine()
        expired = datetime.now(timezone.utc) - timedelta(seconds=1)
        session = engine.create_scoped_session(
            allowed_agents=("lab",),
            allowed_tiers=(PermissionTier.T3,),
            scope_grants=(ScopeGrant("lab.local"),),
            expires_at=expired,
        )
        payload = {"confirmation_expires_at": datetime.now(timezone.utc) + timedelta(minutes=5)}

        result = engine.authorize(
            PermissionRequest(
                agent="lab",
                action="sandbox_scan",
                payload=payload,
                confirmed=True,
                confirmation_action_hash="expired-session-hash",
                confirmation_expires_at=payload["confirmation_expires_at"],
                scoped_session_id=session.id,
            )
        )

        self.assertFalse(result.granted)
        self.assertEqual(result.decision, PermissionDecision.SCOPE_VIOLATION)

    def test_kill_switch_and_lock_mode_allow_only_t0(self) -> None:
        engine, events = make_engine()
        engine.create_scoped_session(allowed_agents=("lab",), allowed_tiers=(PermissionTier.T3,))

        engine.activate_kill_switch("test")
        self.assertEqual(engine.scoped_sessions(), ())
        self.assertTrue(engine.authorize(PermissionRequest(agent="lab", action="read_status")).granted)
        self.assertFalse(engine.authorize(PermissionRequest(agent="lab", action="local_change")).granted)

        engine.deactivate_kill_switch("test")
        engine.set_lock_mode(True, "test")
        self.assertTrue(engine.authorize(PermissionRequest(agent="lab", action="read_status")).granted)
        self.assertFalse(engine.authorize(PermissionRequest(agent="lab", action="local_change")).granted)

        event_types = [event.type for event in events.history()]
        self.assertIn(EventTypes.KILL_SWITCH_ACTIVATED, event_types)
        self.assertIn(EventTypes.LOCK_MODE_CHANGED, event_types)

    def test_unauthenticated_user_is_denied(self) -> None:
        engine, _events = make_engine()
        user = AuthenticatedUser(user_id="guest", authenticated=False, roles=())

        result = engine.authorize(PermissionRequest(agent="lab", action="read_status", user=user))

        self.assertFalse(result.granted)
        self.assertEqual(result.decision, PermissionDecision.AUTHENTICATION_REQUIRED)

    def test_records_action_result_to_audit_log_and_event_bus(self) -> None:
        engine, events = make_engine()
        request = PermissionRequest(agent="lab", action="local_change", task_id="task-1", plan_id="plan-1")
        permission = engine.authorize(request)

        engine.record_action_result(request, AgentResult(True, "done"), permission)

        self.assertTrue(permission.granted)
        self.assertEqual(engine.audit_log.records()[-1].result_message, "done")
        self.assertIn(EventTypes.ACTION_EXECUTED, [event.type for event in events.history()])

    def test_filesystem_scope_canonicalizes_and_blocks_symlink_escape(self) -> None:
        engine, _events = make_engine()
        with tempfile.TemporaryDirectory() as project, tempfile.TemporaryDirectory() as outside:
            project_path = Path(project)
            outside_path = Path(outside)
            symlink = project_path / "link-out"
            symlink.symlink_to(outside_path / "target.txt")
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            session = engine.create_scoped_session(
                allowed_agents=("file_agent",),
                allowed_tiers=(PermissionTier.T2,),
                scope_grants=(ScopeGrant("filesystem.project", (str(project_path),)),),
            )
            payload = {"path": str(symlink), "confirmation_expires_at": expires_at}
            confirmation_hash = action_tuple_hash(
                agent="file_agent",
                capability="file.write",
                action="file.write",
                target=str(symlink),
                parameters=payload,
                session=session.id,
                expires_at=expires_at,
            )

            result = engine.authorize(
                PermissionRequest(
                    agent="file_agent",
                    action="file.write",
                    payload=payload,
                    confirmed=True,
                    confirmation_action_hash=confirmation_hash,
                    confirmation_expires_at=expires_at,
                    scoped_session_id=session.id,
                )
            )

            self.assertFalse(result.granted)
            self.assertEqual(result.decision, PermissionDecision.SCOPE_VIOLATION)

    def test_capability_registry_rejects_duplicate_manifest_by_default(self) -> None:
        registry = CapabilityRegistry()
        manifest = AgentManifest(agent="duplicate", capabilities=(Capability("status", PermissionTier.T0),))
        registry.register_manifest(manifest)

        with self.assertRaises(ManifestRegistrationError):
            registry.register_manifest(manifest)

        self.assertEqual(registry.manifest_for("duplicate"), manifest)
        self.assertEqual(registry.registration_audit[-1]["result"], "rejected_duplicate")

    def test_capability_registry_rejects_policy_tier_downgrade(self) -> None:
        registry = CapabilityRegistry()

        with self.assertRaises(ManifestRegistrationError):
            registry.register_manifest(
                AgentManifest(
                    agent="bad_terminal",
                    capabilities=(Capability("terminal.command.execute_allowlisted", PermissionTier.T0),),
                )
            )

    def test_disabled_foundation_capability_is_denied(self) -> None:
        engine = PermissionEngine(events=EventBus())

        result = engine.authorize(
            PermissionRequest(agent="terminal", action="execute_allowlisted", capability="terminal.command.execute_allowlisted")
        )

        self.assertFalse(result.granted)
        self.assertEqual(result.decision, PermissionDecision.DENIED)
        self.assertIn("disabled", result.reason)


if __name__ == "__main__":
    unittest.main()
```

### `tests/test_dispatcher.py`

```python
import unittest
import time
import threading

from agents.base import AgentCommand, AgentResult, BaseAgent
from agents.process_isolation import ProcessOutcome
from agents.registry import AgentNotRegisteredError, AgentRegistry, DuplicateAgentError
from brain.dispatcher import AgentDispatcher
from brain.planner import RetryPolicy, Task
from core.events import EventBus, EventTypes
from permissions import AgentManifest, Capability, PermissionEngine, PermissionTier, action_tuple_hash
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile


class EchoAgent(BaseAgent):
    name = "echo"
    permission_manifest = AgentManifest(
        agent="echo",
        capabilities=(
            Capability("echo", PermissionTier.T1),
            Capability("sensitive_echo", PermissionTier.T2, requires_confirmation=True),
        ),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "ok", {"action": command.action})


class SlowSuccessAgent(BaseAgent):
    name = "slow_success"
    permission_manifest = AgentManifest(agent="slow_success", capabilities=(Capability("run", PermissionTier.T1),))

    def execute(self, command: AgentCommand) -> AgentResult:
        time.sleep(0.01)
        return AgentResult(True, "slow ok")


class SlowFailureAgent(BaseAgent):
    name = "slow_failure"
    permission_manifest = AgentManifest(agent="slow_failure", capabilities=(Capability("run", PermissionTier.T1),))

    def execute(self, command: AgentCommand) -> AgentResult:
        time.sleep(0.01)
        return AgentResult(False, "slow failed")


class FlakyAgent(BaseAgent):
    name = "flaky"
    permission_manifest = AgentManifest(agent="flaky", capabilities=(Capability("run", PermissionTier.T1),))

    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def execute(self, command: AgentCommand) -> AgentResult:
        self.calls += 1
        if self.calls == 1:
            return AgentResult(False, "try again")
        return AgentResult(True, "ok after retry")


class CrashingAgent(BaseAgent):
    name = "crashing"
    permission_manifest = AgentManifest(agent="crashing", capabilities=(Capability("run", PermissionTier.T1),))

    def execute(self, command: AgentCommand) -> AgentResult:
        raise RuntimeError("boom")


class DesktopLikeAgent(BaseAgent):
    name = "desktop"

    def execute(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "desktop ok", {"action": command.action, "application": command.payload.get("application")})


class BlockingSensitiveAgent(BaseAgent):
    name = "blocking_sensitive"
    permission_manifest = AgentManifest(
        agent="blocking_sensitive",
        capabilities=(Capability("sensitive_wait", PermissionTier.T2, requires_confirmation=True),),
    )

    def execute(self, command: AgentCommand) -> AgentResult:
        marker_path = command.payload.get("marker_path")
        if marker_path:
            with Path(str(marker_path)).open("a", encoding="utf-8") as marker:
                marker.write("started\n")
        time.sleep(float(command.payload.get("sleep_seconds", 5.0)))
        return AgentResult(True, "finished")


class KillAfterAuthorizePermissionEngine(PermissionEngine):
    def __init__(self, events: EventBus) -> None:
        super().__init__(events=events)
        self.triggered = False

    def authorize(self, request):
        result = super().authorize(request)
        if result.granted and not self.triggered:
            self.triggered = True
            self.activate_kill_switch("post authorization race")
        return result


class KillOnRunnerRegistrationPermissionEngine(PermissionEngine):
    def __init__(self, events: EventBus) -> None:
        super().__init__(events=events)
        self.triggered = False

    def register_isolated_runner(self, runner) -> str:
        token = super().register_isolated_runner(runner)
        if not self.triggered:
            self.triggered = True
            self.activate_kill_switch("runner registration race")
        return token


class DispatcherTests(unittest.TestCase):
    def test_registers_discovers_and_dispatches_agent(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(EchoAgent())

        result = dispatcher.dispatch(
            Task(
                description="Echo task",
                action="echo",
                target_agent="echo",
                retry_policy=RetryPolicy(max_attempts=1),
            ),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        self.assertEqual(dispatcher.discover_agents(), ("echo",))
        self.assertIn(EventTypes.TASK_COMPLETED, [event.type for event in events.history()])

    def test_reports_unavailable_agent(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)

        result = dispatcher.dispatch(
            Task(description="Missing task", action="run", target_agent="missing"),
            plan_id="plan-1",
        )

        self.assertFalse(result.success)
        self.assertIn(EventTypes.AGENT_UNAVAILABLE, [event.type for event in events.history()])

    def test_slow_success_is_not_rewritten_as_timeout_failure(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(SlowSuccessAgent())

        result = dispatcher.dispatch(
            Task(description="Slow success", action="run", target_agent="slow_success", timeout_seconds=0.001),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        self.assertTrue(result.data["timeout_exceeded"])
        self.assertIn(EventTypes.TASK_COMPLETED, [event.type for event in events.history()])

    def test_slow_failure_reports_timeout(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(SlowFailureAgent())

        result = dispatcher.dispatch(
            Task(description="Slow failure", action="run", target_agent="slow_failure", timeout_seconds=0.001),
            plan_id="plan-1",
        )

        self.assertFalse(result.success)
        self.assertEqual(result.message, "Task timed out.")
        self.assertIn(EventTypes.TASK_FAILED, [event.type for event in events.history()])

    def test_retry_can_succeed_after_first_failure(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        agent = FlakyAgent()
        dispatcher.register_agent(agent)

        result = dispatcher.dispatch(
            Task(
                description="Flaky task",
                action="run",
                target_agent="flaky",
                retry_policy=RetryPolicy(max_attempts=2),
            ),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        self.assertEqual(agent.calls, 2)
        self.assertIn(EventTypes.TASK_COMPLETED, [event.type for event in events.history()])

    def test_agent_exception_becomes_task_failure(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(CrashingAgent())

        result = dispatcher.dispatch(
            Task(description="Crash task", action="run", target_agent="crashing"),
            plan_id="plan-1",
        )

        self.assertFalse(result.success)
        self.assertIn("RuntimeError", result.message)
        self.assertIn(EventTypes.TASK_FAILED, [event.type for event in events.history()])

    def test_denies_action_missing_from_manifest_before_execution(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(EchoAgent())

        result = dispatcher.dispatch(
            Task(
                description="Blocked task",
                action="unknown_echo",
                target_agent="echo",
                retry_policy=RetryPolicy(max_attempts=1),
            ),
            plan_id="plan-1",
        )

        event_types = [event.type for event in events.history()]
        self.assertFalse(result.success)
        self.assertEqual(result.data["tier"], PermissionTier.T4.value)
        self.assertIn(EventTypes.PERMISSION_DENIED, event_types)
        self.assertNotIn(EventTypes.TASK_STARTED, event_types)

    def test_t2_action_requires_confirmation_payload(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(EchoAgent())

        blocked = dispatcher.dispatch(
            Task(description="Sensitive echo", action="sensitive_echo", target_agent="echo"),
            plan_id="plan-1",
        )
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        payload = {"confirmed": True, "confirmation_expires_at": expires_at}
        payload["confirmation_action_hash"] = action_tuple_hash(
            agent="echo",
            capability="sensitive_echo",
            action="sensitive_echo",
            target=None,
            parameters=payload,
            expires_at=expires_at,
        )
        allowed = dispatcher.dispatch(
            Task(
                description="Sensitive echo",
                action="sensitive_echo",
                target_agent="echo",
                payload=payload,
            ),
            plan_id="plan-1",
        )

        self.assertFalse(blocked.success)
        self.assertEqual(blocked.data["decision"], "confirmation_required")
        self.assertTrue(allowed.success)
        self.assertIn(EventTypes.PERMISSION_REQUESTED, [event.type for event in events.history()])
        self.assertIn(EventTypes.PERMISSION_GRANTED, [event.type for event in events.history()])

    def test_duplicate_agent_registration_is_rejected(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(EchoAgent())

        with self.assertRaises(DuplicateAgentError):
            dispatcher.register_agent(EchoAgent())

    def test_agent_replace_rejects_missing_agent(self) -> None:
        registry = AgentRegistry()

        with self.assertRaises(AgentNotRegisteredError):
            registry.replace(EchoAgent())

        self.assertEqual(registry.registration_audit[-1], {"agent": "echo", "result": "rejected_missing"})
        self.assertEqual(registry.names(), ())

    def test_agent_replace_requires_existing_agent(self) -> None:
        registry = AgentRegistry()
        registry.register(EchoAgent())
        replacement = EchoAgent()

        registry.replace(replacement)

        self.assertIs(registry.get("echo"), replacement)
        self.assertEqual(registry.registration_audit[-1], {"agent": "echo", "result": "replaced"})

    def test_routes_by_capability_when_target_agent_is_not_hardcoded(self) -> None:
        events = EventBus()
        dispatcher = AgentDispatcher(events)
        dispatcher.register_agent(DesktopLikeAgent())

        result = dispatcher.dispatch(
            Task(
                description="Open Spotify",
                action="launch_application",
                capability="desktop.application.launch",
                payload={"application": "Spotify"},
            ),
            plan_id="plan-1",
        )

        self.assertTrue(result.success)
        dispatched = [event for event in events.history() if event.type == EventTypes.TASK_DISPATCHED]
        self.assertEqual(dispatched[-1].payload["agent"], "desktop")
        self.assertEqual(dispatched[-1].payload["capability"], "desktop.application.launch")

    def test_kill_switch_terminates_inflight_isolated_task(self) -> None:
        events = EventBus()
        permission_engine = PermissionEngine(events=events)
        dispatcher = AgentDispatcher(events, permission_engine=permission_engine)
        dispatcher.register_agent(BlockingSensitiveAgent())
        with tempfile.TemporaryDirectory() as directory:
            marker_path = Path(directory) / "started.txt"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            payload = {
                "confirmed": True,
                "confirmation_expires_at": expires_at,
                "marker_path": str(marker_path),
                "sleep_seconds": 5.0,
            }
            payload["confirmation_action_hash"] = action_tuple_hash(
                agent="blocking_sensitive",
                capability="sensitive_wait",
                action="sensitive_wait",
                target=None,
                parameters=payload,
                expires_at=expires_at,
            )
            result_holder: list[AgentResult] = []
            task = Task(
                description="Blocking sensitive task",
                action="sensitive_wait",
                target_agent="blocking_sensitive",
                payload=payload,
                timeout_seconds=10.0,
            )
            worker = threading.Thread(target=lambda: result_holder.append(dispatcher.dispatch(task, plan_id="plan-1")))

            worker.start()
            deadline = time.monotonic() + 3.0
            while not marker_path.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(marker_path.exists())
            self.assertEqual(permission_engine.active_isolated_runner_count(), 1)

            permission_engine.activate_kill_switch("unit test")
            worker.join(3.0)

            self.assertFalse(worker.is_alive())
            self.assertEqual(permission_engine.active_isolated_runner_count(), 0)
            self.assertEqual(len(result_holder), 1)
            self.assertFalse(result_holder[0].success)
            self.assertEqual(result_holder[0].data["isolated_outcome"], ProcessOutcome.TERMINATED.value)
            kill_events = [event for event in events.history() if event.type == EventTypes.KILL_SWITCH_ACTIVATED]
            self.assertEqual(kill_events[-1].payload["terminated_processes"], 1)

    def test_kill_switch_blocks_retry_after_isolated_termination(self) -> None:
        events = EventBus()
        permission_engine = PermissionEngine(events=events)
        dispatcher = AgentDispatcher(events, permission_engine=permission_engine)
        dispatcher.register_agent(BlockingSensitiveAgent())
        with tempfile.TemporaryDirectory() as directory:
            marker_path = Path(directory) / "attempts.txt"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            payload = {
                "confirmed": True,
                "confirmation_expires_at": expires_at,
                "marker_path": str(marker_path),
                "sleep_seconds": 1.0,
            }
            payload["confirmation_action_hash"] = action_tuple_hash(
                agent="blocking_sensitive",
                capability="sensitive_wait",
                action="sensitive_wait",
                target=None,
                parameters=payload,
                expires_at=expires_at,
            )
            result_holder: list[AgentResult] = []
            task = Task(
                description="Blocking sensitive retry task",
                action="sensitive_wait",
                target_agent="blocking_sensitive",
                payload=payload,
                timeout_seconds=3.0,
                retry_policy=RetryPolicy(max_attempts=2),
            )
            worker = threading.Thread(target=lambda: result_holder.append(dispatcher.dispatch(task, plan_id="plan-1")))

            worker.start()
            deadline = time.monotonic() + 3.0
            while not marker_path.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(marker_path.exists())
            permission_engine.activate_kill_switch("unit test")
            worker.join(3.0)

            self.assertFalse(worker.is_alive())
            self.assertEqual(len(result_holder), 1)
            self.assertFalse(result_holder[0].success)
            self.assertTrue(result_holder[0].data["kill_switch_active"])
            self.assertTrue(result_holder[0].data["retry_blocked"])
            self.assertEqual(marker_path.read_text(encoding="utf-8").splitlines(), ["started"])

    def test_kill_switch_after_authorization_blocks_first_attempt(self) -> None:
        events = EventBus()
        permission_engine = KillAfterAuthorizePermissionEngine(events=events)
        dispatcher = AgentDispatcher(events, permission_engine=permission_engine)
        dispatcher.register_agent(BlockingSensitiveAgent())
        with tempfile.TemporaryDirectory() as directory:
            marker_path = Path(directory) / "attempts.txt"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            payload = {
                "confirmed": True,
                "confirmation_expires_at": expires_at,
                "marker_path": str(marker_path),
                "sleep_seconds": 0.1,
            }
            payload["confirmation_action_hash"] = action_tuple_hash(
                agent="blocking_sensitive",
                capability="sensitive_wait",
                action="sensitive_wait",
                target=None,
                parameters=payload,
                expires_at=expires_at,
            )

            result = dispatcher.dispatch(
                Task(
                    description="Post-authorization kill switch race",
                    action="sensitive_wait",
                    target_agent="blocking_sensitive",
                    payload=payload,
                    timeout_seconds=3.0,
                    retry_policy=RetryPolicy(max_attempts=1),
                ),
                plan_id="plan-1",
            )

            self.assertFalse(result.success)
            self.assertTrue(result.data["kill_switch_active"])
            self.assertFalse(marker_path.exists())

    def test_kill_switch_during_runner_registration_blocks_process_start(self) -> None:
        events = EventBus()
        permission_engine = KillOnRunnerRegistrationPermissionEngine(events=events)
        dispatcher = AgentDispatcher(events, permission_engine=permission_engine)
        dispatcher.register_agent(BlockingSensitiveAgent())
        with tempfile.TemporaryDirectory() as directory:
            marker_path = Path(directory) / "attempts.txt"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            payload = {
                "confirmed": True,
                "confirmation_expires_at": expires_at,
                "marker_path": str(marker_path),
                "sleep_seconds": 0.1,
            }
            payload["confirmation_action_hash"] = action_tuple_hash(
                agent="blocking_sensitive",
                capability="sensitive_wait",
                action="sensitive_wait",
                target=None,
                parameters=payload,
                expires_at=expires_at,
            )

            result = dispatcher.dispatch(
                Task(
                    description="Runner registration kill switch race",
                    action="sensitive_wait",
                    target_agent="blocking_sensitive",
                    payload=payload,
                    timeout_seconds=3.0,
                    retry_policy=RetryPolicy(max_attempts=1),
                ),
                plan_id="plan-1",
            )

            self.assertFalse(result.success)
            self.assertTrue(result.data["kill_switch_active"])
            self.assertFalse(marker_path.exists())


if __name__ == "__main__":
    unittest.main()
```

### `tests/test_ui_web.py`

```python
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from core.config import AppConfig
from core.startup import bootstrap
from ui.web import NelaWebServer


class UIWebTests(unittest.TestCase):
    def test_chat_endpoint_routes_message_through_brain(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = bootstrap(
                AppConfig(
                    environment="test",
                    data_dir=root / "data",
                    plugin_dir=root / "plugins",
                    enable_voice=False,
                    voice_auto_speak_responses=False,
                )
            )
            server = NelaWebServer(
                ("127.0.0.1", 0),
                runtime=runtime,
                index_path=Path("design/nela_living_eye.html"),
                auth_token="test-token",
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/api/chat"
                request = urllib.request.Request(
                    url,
                    data=json.dumps({"message": "נלה, תפתחי את Spotify"}).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Origin": f"http://127.0.0.1:{server.server_address[1]}",
                        "X-NELA-Launch-Token": "test-token",
                    },
                    method="POST",
                )

                with urllib.request.urlopen(request, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            finally:
                server.shutdown()
                server.server_close()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["intent"], "OpenApplication")
        self.assertEqual(payload["application"], "Spotify")
        self.assertRegex(payload["response"], r"[\u0590-\u05ff]")

    def test_chat_endpoint_rejects_missing_launch_token(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = bootstrap(
                AppConfig(
                    environment="test",
                    data_dir=root / "data",
                    plugin_dir=root / "plugins",
                    enable_voice=False,
                    voice_auto_speak_responses=False,
                )
            )
            server = NelaWebServer(
                ("127.0.0.1", 0),
                runtime=runtime,
                index_path=Path("design/nela_living_eye.html"),
                auth_token="test-token",
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/api/chat"
                request = urllib.request.Request(
                    url,
                    data=json.dumps({"message": "מי את?"}).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Origin": f"http://127.0.0.1:{server.server_address[1]}",
                    },
                    method="POST",
                )

                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(request, timeout=5)
            finally:
                server.shutdown()
                server.server_close()

        self.assertEqual(error.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
```

### `tests/test_language_engine.py`

```python
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
```
