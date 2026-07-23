# NELA Visual Identity & Design System

The eye is not decoration. The eye **is** NELA — its face, its status, its
personality. Every other visual decision in this document exists to keep the
eye alive and legible.

Companion artifacts:

- `nela_living_eye.html` — working prototype: the living logo, all 11 states,
  gaze tracking, blinking, chat layout. Open it in a browser; this document
  explains what you're seeing.
- `nela_app_icon.svg` — static app / dock icon.
- `nela_menubar_icon.svg` — monochrome macOS menu-bar template icon.

---

## 1. Brand identity

**Essence:** a loyal, intelligent presence that watches over your computer the
way a dog watches the door — alert, warm, never menacing.

**Why a dog's eye, structurally.** The design is canine by anatomy, not by
styling:

| Anatomical fact | Design consequence |
| --- | --- |
| Dogs show almost no sclera (white) | The iris fills the entire aperture. No white ring — that alone makes it read as non-human at a glance. |
| Round pupil (cats have slits, predators glare) | The pupil is always a soft circle. Never an ellipse, never a slit. |
| Soft rounded-almond aperture | The eye shape has a gentle lower curve — relaxed, not narrowed. |
| The "puppy look" is a raised inner gaze | Primary catchlight sits high and inner (10–11 o'clock), producing the upward look-at-you gaze. |

**Anti-references (hard rules):** no rings-of-light HUD (JARVIS/Iron Man), no
single red lens (HAL), no featureless orb (Cortana/Siri), no cartoon mascot, no
photoreal eyeball, no horror imagery. If a draft resembles any of these, the
draft is wrong.

**Psychedelic direction, disciplined.** The trip lives *inside* the iris
(liquid aurora, drifting bioluminescent color) and *around* the eye (two
counter-rotating sacred-geometry rings, floating motes). Everything outside
that — chat, typography, chrome — stays quiet and near-monochrome, so the eye
is the only loud thing on screen. Spend the boldness in one place.

---

## 2. The living logo

Layer stack, back to front (matches the SVG in the prototype):

1. **Outer lattice ring** — 12-point star chords + dashed circle. Rotates
   clockwise, period per state.
2. **Inner petal ring** — six flower-of-life arcs + dashed circle. Rotates
   counter-clockwise (counter-rotation = depth without 3D).
3. **Halo** — an expanding/contracting ring used only by `listening`
   (contracts inward = focusing on you) and `success` (blooms outward).
4. **Iris** — radial gradient (state colors A→B→C) with three drifting
   screen-blended aurora blobs, all under a `feTurbulence` displacement filter.
   The turbulence itself animates slowly, so the color is genuinely liquid.
5. **Striations** — 64 fine radial filaments at 30% opacity, rotating slowly.
6. **Pupil** — round, gradient to near-black, radius owned by the state.
7. **Catchlights** — one large high-inner spark plus one small opposite spark.
   Catchlights vanish only when offline: they are the "alive" bit.
8. **Eyelid** — a soft curved lid, not a shutter. Used for blinking, sleeping
   (two-thirds closed), offline (closed).

**Idle is alive.** At idle the whole eye breathes (scale 1 → 1.035, 6s), the
rings drift, the aurora flows, motes float, and the eye blinks softly every
4–8 seconds and follows the pointer with a gentle lag. Nothing is ever fully
static except `offline` — and that stillness is itself the message.

---

## 3. Emotional states

Each state changes four channels at once: **color**, **pupil**, **rhythm**
(breathing period), and **rings** — so states remain distinguishable for
color-blind users by motion alone.

| State | Color core | Pupil | Rhythm & signature motion |
| --- | --- | --- | --- |
| Idle | Amber → teal | medium | 6s breath; everything drifts lazily |
| Listening | Blue `#3D7DFF` | constricts | halo rings contract *inward* — the eye focuses on you |
| Thinking | Purple `#8A4FE0` | medium | rings spin fast; iris striations swirl — visible computation |
| Speaking | Turquoise `#19C8C0` | pulses | pupil beats at speech rhythm, a heartbeat of talk |
| Executing | Signal green-teal `#28D0A0` | small, focused | motes orbit at 3× speed; short 2.6s breath — busy hands |
| Waiting | Orange `#F09B3A` | dilates | very slow 7s breath; patient, heavy-lidded feel |
| Success | Green `#39D97A` | dilates wide | one ring blooms outward and fades — a silent "done" |
| Warning | Amber `#FFB020` | tight | fast 2.2s breath; urgent but not alarmed |
| Error | Red `#FF4D5E` | tightest | two quick horizontal tremors, then still. Never strobing. |
| Sleeping | Dark violet `#5A3AA0` | large, soft | lid two-thirds closed; 10s breath; no blinking |
| Offline | Desaturated gray | — | lid closed, rings frozen, catchlight gone. The only dead frame. |

Transitions between states are 1.0–1.6s eased color/geometry morphs — states
flow into each other like weather, never cut.

---

## 4. Color system

**Environment (constant):**

| Token | Hex | Use |
| --- | --- | --- |
| `void` | `#080514` | app background (deep space, never pure black) |
| `nebula` | `#120B26` | raised surfaces, composer, eyelid |
| `starlight` | `#EDE8FF` | primary text |
| `dim` | `#8D84B8` | secondary text, labels |
| `hairline` | `rgba(160,140,255,.14)` | borders |

**State channel (dynamic):** every state defines `--st-a` (iris core),
`--st-b` (aurora flow — also the accent that leaks into UI), `--st-c` (iris
edge/depth), and `--glow` (outer light). The chat's active border, the send
button, and the state word all inherit `--st-b`, so the whole interface
breathes with the eye without competing with it.

Gradient rule: state colors always meet through radial/aurora gradients, never
hard stops. Color changes are 1.2s eased transitions on gradient stops.

---

## 5. Typography

| Role | Face | Why |
| --- | --- | --- |
| Display / wordmark | **Syne** (700–800) | geometric with an organic warp — cosmic without being sci-fi cliché. Wordmark: `N E L A`, 0.42em tracking, always small. NELA's face is the eye; the wordmark whispers. |
| Body / chat | **Assistant** (300–600) | humanist, excellent Hebrew + Latin — the product speaks both. Light 300 for messages keeps the screen airy. |
| Utility / state words, data | **Space Grotesk** (400–500) | tabular feel for status and telemetry, uppercase, 0.24–0.28em tracking. |

Scale: 12 (utility) / 15 (chat) / 20 (section) / 28 (headings) — deliberately
small; the eye owns the visual volume.

---

## 6. Motion guidelines

1. **One heartbeat.** All idle motion derives from the breath variable. When
   the state changes, the breath period changes — one knob, coherent mood.
2. **Slow is alive, fast is busy.** Ring speed and mote speed communicate load.
   Never animate faster than 1.6s periods except `speaking`'s pulse.
3. **Ease like tissue, not machinery.** `cubic-bezier(.4,0,.2,1)` and softer;
   no linear moves except infinite rotations.
4. **Error is percussive, not persistent.** Two tremors, then stillness. A
   continuously shaking or flashing eye reads as horror — forbidden.
5. **Blink budget.** One soft 340ms blink every 4–8s randomised. Blinking stops
   when sleeping (lids already down) and offline.
6. **Respect `prefers-reduced-motion`:** all ambient animation stops; states
   communicate through color and pupil size only.

---

## 7. Icon style

- Icons across the app are **stroke-based, 1.6px, rounded caps**, single
  color `dim`, hover `starlight` — quiet lines that echo the ring geometry.
- **App/dock icon** (`nela_app_icon.svg`): macOS squircle, eye at rest in
  idle colors, exactly four shapes so it survives 16px.
- **Menu bar** (`nela_menubar_icon.svg`): a template image — pure black on
  transparency, three shapes; macOS recolors it. An active-task variant fills
  the aperture.

---

## 8. macOS desktop layout

```text
┌──────────────────────────────────────────────┐
│  ● ● ●                              (⋯ menu) │  traffic lights on void
│                                              │
│                  N E L A                     │  whisper wordmark
│                                              │
│                 ╭────────╮                   │
│                ( the eye  )                  │  always visible,
│                 ╰────────╯                   │  ~46% of window height
│                  thinking                    │  state word
│                                              │
│   ┌──────────────────────────────────────┐   │
│   │  chat thread (scrolls, max ~30vh)    │   │
│   └──────────────────────────────────────┘   │
│   (—————————— composer pill ——————————)(▲)   │
└──────────────────────────────────────────────┘
```

Rules:

- The eye is never covered, cropped, or scrolled away. The thread scrolls
  *under* a fade, the eye holds its ground.
- Compact mode (window < 480px tall): the eye docks to 64px beside the
  composer and keeps full state behavior — it shrinks, it never disappears.
- When an Agent executes, the eye is the feedback: `executing` motes + a
  one-line utility caption under the state word (e.g. `desktop · launching
  Spotify`). No progress bars near the eye.
- Voice: `listening` halo replaces any waveform widget. The eye *is* the mic
  indicator.

---

## 9. Loading & splash

- **Splash:** void background → motes condense inward → aperture rim draws
  itself (stroke-dash reveal, 900ms) → iris blooms from the pupil outward →
  one blink → `idle`. Total ≤ 2.4s, skippable.
- **In-app loading:** never a spinner. The eye enters `thinking` (local) or
  `waiting` (remote). If something takes > 10s, the pupil drifts down-left —
  the "checking on it" glance.
- **App icon → window handoff:** dock icon's eye position matches the splash
  eye position, so launch feels like the same eye waking up.

---

## 10. Implementation notes (for Codex, later)

- The prototype is dependency-free (SVG + CSS variables + ~120 lines of JS).
  State = one attribute: `document.body.dataset.state`.
- State names map 1:1 to Brain events: `IntentRecognized→thinking`,
  `TaskDispatched→executing`, `ConfirmationRequested→waiting`,
  `TaskCompleted→success`, `TaskFailed→error`, `WakeWordDetected→listening`.
  A 12-line subscriber on the Event Bus drives the entire face.
- `success`, `warning`, `error` are *moments*: auto-return to `idle` after
  2–4s unless re-triggered.
- Ship reduced-motion and a "calm mode" toggle (iris flow at 30% amplitude)
  for accessibility and battery.
