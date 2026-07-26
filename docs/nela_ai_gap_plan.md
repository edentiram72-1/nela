# NELA AI Gap Plan

This document tracks the gap between the current NELA demo and the desired
desktop-first AI assistant experience.

## Current State

NELA currently has:

- A Brain that routes user input through intent recognition, decisions, planning,
  memory, and Agent dispatch.
- Hebrew response packs and a visible Living Eye UI.
- A first safe Desktop Agent for application lifecycle actions.
- A defensive security layer with posture findings, local security review,
  dependency review, and authorized lab boundaries.
- A learning flow for user-taught trigger/response pairs.
- A Permission Engine, capability routing, audit foundations, lock mode, and kill
  switch foundations.

## Main Gaps

NELA still needs these layers before it feels like a capable AI assistant:

- Open-ended understanding: a controlled LLM provider behind the Brain, not inside
  individual Agents.
- Better action guidance: unknown requests should become suggestions, supported
  actions, or safe next steps instead of generic clarification.
- Tool confidence: every supported action should clearly say whether it executed,
  only planned, or needs confirmation.
- Deeper memory retrieval: use stored preferences, learned phrasing, project
  context, and recent activity when answering.
- Real Agent coverage: connect useful Agents gradually behind manifests,
  permissions, tests, and rollback paths.
- UI confirmations: actions requiring approval need a visible confirmation flow in
  the Living Eye interface.
- Status transparency: NELA should explain what is connected, what is safe, and
  what is still a placeholder.

## Immediate Improvements

1. Add project status and gap Q&A.
2. Treat unsupported action requests as helpful guidance, not failure.
3. Expand safe Hebrew intent coverage for already-connected Agents.
4. Add real UI confirmation controls.
5. Add an LLM adapter as a replaceable provider behind permission and prompt
   boundaries.

## Guardrails

- The Brain remains the orchestrator and never executes external actions directly.
- New capabilities go through Agents, manifests, permissions, audit logs, tests,
  and documentation.
- Cybersecurity remains defensive, authorized, local or owned-scope only.
- No direct Claude/ChatGPT/Codex private channel is introduced; GitHub remains the
  collaboration layer.
