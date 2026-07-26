# TryHackMe Learning

NELA treats TryHackMe as an authorized cyber-learning source.

This feature is for learning, note-taking, review, and defensive understanding.
It does not connect to TryHackMe directly, does not scrape rooms, and does not
run commands against targets.

## Purpose

NELA must learn from legal cyber labs and keep that knowledge for future
conversations. A TryHackMe lesson becomes structured memory:

- Source: `tryhackme`
- Room name, when supplied
- Topic
- Concepts
- Commands as study notes only
- Safety boundaries
- Review questions
- Skill graph signals

## Agent

Agent: `tryhackme_learning`

Actions:

- `capture_tryhackme_lesson`
- `plan_tryhackme_learning`
- `review_tryhackme_progress`

The lesson-capture action is T1 because it writes to local learning memory. The
planning and progress-review actions are read-only.

## Storage

Runtime storage path:

```text
data/learning/lessons.json
```

The data is local JSON so future memory/vector backends can ingest it without
changing the Agent contract.

## Examples

```text
נלה למדתי ב-TryHackMe חדר Nmap שהפקודה nmap -sV מזהה ports ושירותים
```

NELA captures a lesson and returns:

- A saved lesson ID
- Concepts such as `nmap`, `ports`, and `services`
- Commands as study notes
- Safety notes
- Review questions

```text
מה למדת ב TryHackMe?
```

NELA reviews stored TryHackMe lessons and reports the current skill graph.

```text
תבני לי מסלול TryHackMe ל-SOC
```

NELA prepares a safe learning path without performing external actions.

## Safety Boundary

Allowed:

- Learning from user-provided TryHackMe notes
- Summarizing legal lab concepts
- Saving safe commands as study notes
- Creating review questions
- Building a skill graph

Not allowed:

- Scanning third-party systems
- Bypassing access controls
- Executing commands from notes
- Scraping TryHackMe behind login
- Turning a lab technique into an action against an external target

Active security work remains limited to TryHackMe rooms, localhost, or owned
assets with explicit scope and authorization.

## Future Extensions

- Browser-assisted room note capture after a user-controlled login flow.
- Flashcard generation.
- Spaced repetition.
- Skill-level scoring.
- Integration with the long-term memory/vector store.
