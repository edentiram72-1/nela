# NELA OS

[English](README.md) | עברית

NELA OS היא תשתית למערכת הפעלה מבוססת בינה מלאכותית, בגישה של עוזר חכם לשולחן העבודה, בהשראת רעיון בסגנון JARVIS.

הפרויקט נבנה כמערכת מודולרית ומבוססת אירועים, שיכולה להתפתח לשיחה קולית, זיכרון, שליטה במחשב, הבנת מסך, אוטומציה, תמיכה בתוספים, תיאום בין סוכנים, ואינטגרציה עתידית עם מובייל.

## משימה

לבנות שכבת הפעלה חכמה ותחזוקתית, שבה Brain מרכזי אחד מבין בקשות, חושב עליהן, יוצר תוכניות, זוכר הקשר, ומאציל ביצוע לסוכנים עצמאיים.

ה-Brain לעולם לא מבצע פעולות חיצוניות בעצמו. הסוכנים עושים את העבודה. המודולים מתקשרים דרך אירועים ולא דרך תלות ישירה בין מודולים.

## מצב נוכחי

NELA OS השלימה את **Integration Sprint 1** עבור baseline מאוחד בענף `develop`: **Phase 1 Brain Foundation + Desktop/UI + Claude Hebrew Language And Voice Foundation**.

במאגר קיימת עכשיו תשתית עובדת שיכולה:

- לעלות משורת הפקודה.
- לקבל קלט טקסט או תמלול קול.
- לסווג כוונה של משתמש למבנה נתונים מסודר.
- להחליט האם לשאול, להמתין, לזכור, להאציל או לדחות.
- ליצור תוכנית משימות.
- לעקוב אחרי הקשר שיחה ומשימות רצות.
- לנהל שכבות זיכרון קצר-טווח וארוך-טווח.
- לשלוח משימות לסוכנים רשומים דרך חוזה משותף.
- לרשום תשתית multi-agent ראשונית והגנתית לתיאום, תכנון, פיתוח, QA, זיכרון, למידה, סקירת קוד מאובטחת, מחקר פגיעויות וגילוי אנומליות.
- לפרסם אירועי מחזור חיים דרך Event Bus פנימי.
- להשתמש בסוכני mock בטוחים לצורך בדיקות MVP, כאשר Desktop Agent V1 מתחיל שליטה מוגבלת ובטוחה במחזור חיים של אפליקציות macOS.
- להפעיל תשתית UI מודולרית שמחברת קלט טקסט ל-Brain הקיים.
- ליצור תשובות דרך חבילת השפה והאישיות הרשמית של Claude.
- להחזיק את ה-Living Eye של קלוד כארטיפקט העיצוב הרשמי תחת `design/`.
- לייצא חבילת סקירה לקלוד בלי ליצור חיבור ישיר לקלוד.
- לתמוך בשיתוף פעולה דרך GitHub בין Codex, Claude ו-ChatGPT.
- להעביר את קלט ה-smoke בעברית `נלה, תפתחי את Spotify` דרך Brain, Planner, יצירת תשובה בעברית, הצגה ב-UI, האצלה ל-Voice Agent ומעברי Eye.

Desktop Agent V1 הוא הסוכן האמיתי הראשון, והוא מוגבל לניהול מחזור חיים של אפליקציות macOS נתמכות. דפדפן, טרמינל, Spotify, Gmail, GitHub, קול וראייה נשארים placeholders בטוחים אלא אם ימומשו במפורש בהמשך.

הזהות הוויזואלית של קלוד כבר נוספה כארטיפקט רשמי. חלון ה-Tkinter החי עדיין מציג placeholder לעין, עד שתתקבל החלטה איך לארח את prototype ה-HTML/SVG בתוך האפליקציה.

חבילת העברית והאישיות של Claude היא עכשיו מקור התוכן הרשמי של השפה. החבילה כוללת 117 ניסוחים בעברית, 31 קטגוריות ו-3 פרופילי אישיות. Codex אחראי על המנוע ושכבת התאימות; Claude אחראי על הטון, האישיות והתוכן.

## מה נעשה עד עכשיו

### 1. מאגר מוכן לשיתוף פעולה

המאגר אורגן כך שכמה עוזרי AI יוכלו לעבוד דרך GitHub כמקור אמת משותף.

נוצרו ואורגנו:

- `core/`
- `brain/`
- `agents/`
- `memory/`
- `voice/`
- `vision/`
- `skills/`
- `plugins/`
- `docs/`
- `prompts/`
- `tests/`
- `scripts/`
- `config/`
- `assets/`
- `logs/`

נוספו מסמכי עבודה:

- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/api.md`
- `docs/ai_handoff.md`
- `docs/decisions.md`
- `docs/coding_rules.md`
- `docs/memory_model.md`
- `docs/claude_review_findings.md`
- `docs/personality_bible.md`
- `docs/hebrew_language_guide.md`
- `docs/tone_of_voice.md`
- `docs/conversation_rules.md`
- `docs/language_compat_report.md`
- `docs/claude_handoff_2026-07-24.md`
- `docs/releases/v0.1-alpha.md`

נוספו פרומפטים לתפקידי AI:

- `prompts/codex.md`
- `prompts/claude.md`
- `prompts/chatgpt.md`

### 2. שכבת שיתוף פעולה דרך GitHub

GitHub הוא שכבת שיתוף הפעולה בין כל העוזרים.

מאגר ציבורי:

```text
https://github.com/edentiram72-1/nela
```

ענפים חשובים:

- `main`: בסיס שחרור יציב.
- `develop`: בסיס אינטגרציה לשחרור הבא.
- `feature/NELA-0001-foundation-architecture`: ארכיטקטורת foundation ו-Brain ראשוני.
- `feature/NELA-0002-confirmation-deadlock`: ענף תיקון האישורים.
- `feature/NELA-0005-desktop-agent-v1`: Desktop Agent ראשון.
- `feature/NELA-0006-ui-foundation`: תשתית UI.
- `feature/NELA-0007-ai-inbox`: inbox לשיתוף פעולה בין AI.
- `feature/NELA-0011-visual-identity`: Living Eye ומערכת עיצוב של Claude.
- `feature/NELA-0012-claude-review-fixes`: תיקוני סקירת Claude.
- `feature/NELA-language-voice-foundation`: תשתית עברית וקול.

ענפי הפיצ'רים האלה אוחדו לתוך `develop`. במסגרת Integration Sprint 1 לא מבצעים merge נוסף ל-`main`.

קלוד לא מתחבר ישירות ל-Codex או למחשב המקומי. קלוד סוקר ענפים ב-GitHub, קישורי blob ישירים, diff של Pull Request, או חבילת Markdown שנוצרת לסקירה.

### 3. תשתית Phase 1 Brain

מומשה תשתית Brain ראשונה.

מודולים מרכזיים:

- `brain/conversation.py`: ניהול זרימת השיחה.
- `brain/intent_router.py`: זיהוי כוונה דטרמיניסטי.
- `brain/decision.py`: קבלת החלטות.
- `brain/planner.py`: הפיכת כוונה למשימות.
- `brain/context.py`: מצב שיחה, משימות, דסקטופ ואישורים.
- `brain/dispatcher.py`: האצלת משימות לסוכנים.
- `brain/memory_manager.py`: ניהול זיכרון קצר-טווח וארוך-טווח.
- `brain/reasoning.py`: תשתיות חשיבה.

ה-Brain יכול לעבד בקשה בזרימה הבאה:

```text
קלט משתמש
  |
  v
Conversation Engine
  |
  v
Intent Router
  |
  v
Decision Engine
  |
  v
Planner
  |
  v
Agent Dispatcher
  |
  v
Agent
```

### 4. Runtime מבוסס אירועים

נוספו תשתיות אירועים ב-`core/events.py`.

אירועי מחזור החיים הנוכחיים כוללים:

- `InputReceived`
- `IntentRecognized`
- `DecisionMade`
- `ConfirmationRequested`
- `ConfirmationResolved`
- `ConfirmationExpired`
- `PlanCreated`
- `TaskCreated`
- `TaskDispatched`
- `TaskStarted`
- `TaskCompleted`
- `TaskFailed`
- `TaskCancelled`
- `AgentStatusChanged`
- `AgentUnavailable`
- `MemoryUpdated`
- `MemoryRetrieved`
- `ContextUpdated`
- `ConversationEnded`

ה-Event Bus כרגע סינכרוני ופנימי לתהליך. הקשחת מערכת האירועים היא משימת המשך.

### 5. חוזה סוכנים וסוכני mock בטוחים

כל הסוכנים חולקים חוזה אחיד מתוך `agents/base.py`:

```python
initialize()
execute(command)
stop()
status()
health_check()
```

סוכנים קיימים כ-placeholders או mock-backed:

- Desktop
- Terminal
- Browser
- Voice
- Vision
- Memory
- Spotify
- Files
- Calendar
- Gmail
- GitHub
- Codex
- Claude
- Automation
- Orchestrator
- Planner
- Learning
- Code Architect
- Backend
- Frontend
- Test/QA
- Secure Code Reviewer
- Vulnerability Research
- Anomaly Discovery
- Authorized Lab

הסוכנים האלה בודקים כרגע האצלה ומחזור חיים. הם לא מבצעים פעולות אמיתיות עם תופעות לוואי.

שכבת הסוכנים המתמחים הראשונה זמינה דרך `agents.build_default_registry()`.
סוכני הסייבר הם הגנתיים בלבד: ניתוח קוד מקומי, בדיקות בסגנון SAST,
התאמת תלותים לנתוני advisory/CVE שסופקו, הכנת סקירת קונפיגורציה,
תוכניות fuzzing מקומיות/מעבדתיות, גילוי אנומליות, threat modeling
והצעת תיקונים. הם לא בונים exploitation, persistence, credential theft,
evasion, malware, phishing, DDoS או תקיפה נגד מטרות חיצוניות.

מצב Authorized Lab רושם targets, בודק authorization מוגבל, כותב audit
decisions, ומכין סריקות dry-run או fuzz cases מקומיים בלי לפנות למערכות
ציבוריות חיצוניות.

ראו `docs/multi_agent_foundation.md`, `docs/cyber_lab.md` ו-`agents/README.md`.

### 6. זרימת סקירה עם Claude

הוכנה עבודה עם קלוד ללא חיבור ישיר לקלוד.

מומש:

- `agents/claude/agent.py`
- `scripts/export_claude_review_bundle.py`
- זרימת יצירת review bundle
- `docs/claude_review_findings.md`

קלוד סקר את Phase 1 Brain וסימן את משימות ההקשחה הבאות:

- `NELA-0002-confirmation-deadlock`
- `NELA-0003-dispatcher-timeout-retry-safety`
- `NELA-0004-task-idempotency`
- הקשחת Event Bus
- הקשחת Intent Matching
- מדיניות הרשאות
- Capability Registry
- סמנטיקת Plan Execution

### 7. NELA-0002: תיקון Confirmation Deadlock

תוקן deadlock דטרמיניסטי בזרימת האישורים.

הבעיה:

- ה-Brain שאל שאלה לאישור.
- תשובות המשך סווגו כקלט חדש.
- `resolve_confirmation()` מעולם לא נקרא.
- השיחה יכלה להיתקע ב-`WAIT`.

ההתנהגות שמומשה:

- אישורים פתוחים מטופלים לפני סיווג Intent חדש.
- תשובות חיוביות כמו `yes`, `confirm`, `do it`, וגם מקבילות בעברית, ממשיכות את ה-Intent המקורי.
- תשובות שליליות כמו `no`, `cancel`, וגם מקבילות בעברית, מבטלות את הפעולה.
- תשובה לא ברורה נשאלת שוב פעם אחת.
- תשובות לא ברורות חוזרות מבטלות את האישור.
- אישורים שפג תוקפם מבוטלים אחרי TTL ניתן להגדרה.
- נוספו אירועים למעקב אחר מחזור חיי אישור.

החלטת ארכיטקטורה:

- `DEC-0005`: שמירת ה-Intent המקורי בתוך `PendingConfirmation.metadata`, ואז יצירת Plan חדש אחרי אישור.

### 8. הקשחת Dispatcher Timeout ו-Retry

התחילה הקשחה של תזמון וניסיונות חוזרים ב-Dispatcher.

התנהגות נוכחית:

- timeout נמדד לכל ניסיון בנפרד.
- תוצאה סינכרונית מוצלחת ואיטית לא נכתבת מחדש ככישלון אחרי שכבר הסתיימה.
- ניסיון שנכשל ועבר את metadata של timeout מדווח כ-timeout.
- הצלחה אחרי retry מכוסה בבדיקות.

עבודה שנשארה:

- להוסיף metadata של idempotency לפני שמאפשרים retry למשימות עם תופעות לוואי.
- להשאיר timeout כמידע advisory עד שהביצוע יהיה ניתן לביטול אמיתי.

### 9. שיפור Intent Matching

Intent matching עכשיו בודק מילים וביטויים מלאים במקום תתי-מחרוזות אקראיות.

זה מונע false positives כמו התאמה של `play` בתוך `display`.

### 10. תיעוד ועקיבות

נוספו ועודכנו:

- תיעוד ארכיטקטורה
- תיעוד API
- roadmap
- מודל זיכרון
- coding rules
- קובץ AI handoff
- ממצאי Claude
- החלטות ארכיטקטורה
- README למודולים
- תבניות GitHub ל-Issues ו-Pull Requests

כל שינוי משמעותי צריך לעדכן את `docs/ai_handoff.md`.

### 11. זהות ויזואלית: Living Eye

קלוד סיפק את חבילת הזהות הוויזואלית של NELA. היא נשמרה במאגר בלי restyling:

- `design/nela_living_eye.html`: prototype חי, מונפש ונטול תלויות של העין.
- `design/nela_app_icon.svg`: אייקון אפליקציה ודוק.
- `design/nela_menubar_icon.svg`: אייקון macOS menu-bar.
- `docs/design_system.md`: מערכת העיצוב הרשמית לצבעים, טיפוגרפיה, תנועה, מצבים, אייקונים וכללי UI.

ה-Living Eye מונע מערך מצב אחד. `UIEventBridge` ממפה אירועי Brain למצבי Eye לפי מערכת העיצוב:

- `InputReceived`: `listening`
- `IntentRecognized`, `DecisionMade`: `thinking`
- `TaskDispatched`, `TaskStarted`: `executing`
- `ConfirmationRequested`: `waiting`
- `TaskCompleted`: `success`
- `TaskFailed`, `AgentUnavailable`: `error`
- `ConversationEnded`: `idle`

המצבים `success`, `warning`, ו-`error` הם רגעיים. כאשר host של UI מספק תזמון, הם חוזרים ל-`idle` אחרי 3 שניות.

## מפת המאגר

| נתיב | מטרה |
| --- | --- |
| `core/` | עליית אפליקציה, קונפיגורציה, אירועים, לוגים ותשתיות runtime משותפות. |
| `brain/` | שיחה, זיהוי כוונות, החלטות, תכנון, הקשר, זיכרון והאצלת משימות. |
| `agents/` | סוכני ביצוע עצמאיים וחוזה הסוכנים המשותף. |
| `ui/` | תשתית חלון דסקטופ, state manager, event bridge, theme tokens ורכיבי placeholder. |
| `design/` | Living Eye של קלוד, אייקון אפליקציה ואייקון menu-bar. |
| `memory/` | זיכרון קצר-טווח, ארוך-טווח, vector store ופרופיל משתמש. |
| `voice/` | Wake word, מיקרופון, speech-to-text ו-text-to-speech. |
| `vision/` | צילום מסך, קריאת מסך, OCR וזיהוי UI. |
| `skills/` | יכולות reusable עתידיות. |
| `plugins/` | חבילות יכולת עתידיות להתקנה. |
| `docs/` | ארכיטקטורה, roadmap, API, coding rules, memory model, decisions, Claude findings, design system ו-handoff. |
| `prompts/` | פרומפטים לתפקידי Codex, Claude ו-ChatGPT. |
| `tests/` | בדיקות יחידה ואינטגרציה. |
| `scripts/` | כלי פיתוח, כולל יצוא חבילת סקירה לקלוד. |
| `config/` | ברירות מחדל ותבניות קונפיגורציה. |
| `assets/` | צלילים, קולות ונכסי מדיה עתידיים. |
| `logs/` | פלט לוגים בזמן ריצה. קבצי לוג לא נשמרים ב-Git. |

## איך להריץ את NELA

שיחה אינטראקטיבית בטקסט:

```bash
python3 -m core.app
```

הרצת Brain חד-פעמית עם mock dispatch:

```bash
python3 -m core.app --once "Open Spotify and play my Night playlist"
```

בדיקת Plan בלי dispatch לסוכנים:

```bash
python3 -m core.app --once "Open Spotify and play my Night playlist" --no-dispatch
```

יציאה ממצב אינטראקטיבי:

```text
exit
```

## איך להריץ בדיקות

```bash
python3 -m unittest discover -s tests
```

מצב ולידציה נוכחי:

```text
כל הבדיקות עברו.
```

וולידציית Integration Sprint 1 האחרונה:

```text
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
```

תוצאה: 66 בדיקות עברו, חבילת העברית תקינה, ו-bootstrap של UI במצב headless הצליח.

דוח האינטגרציה:

```text
docs/integration_sprint_1_merge_report.md
```

## תשתית עברית וקול

נוספה שכבת תגובה נפרדת אחרי ה-Brain.

ה-Brain עדיין מייצר משמעות, החלטות ותכניות, ומאציל פעולות ל-Agents. הוא לא מכיל ניסוחים בעברית, לא כללי אישיות, ולא קוד ספציפי לספק קול.

זרימה חדשה:

```text
קלט משתמש
  |
  v
פלט סמנטי מה-Brain
  |
  v
Language Engine
  |
  v
טקסט עברי סופי
  |
  +--> UI
  |
  v
Voice Agent
```

נוסף:

- `language/`: מנוע שפה עברית מודולרי.
- `language/hebrew/`: חבילת עברית התחלתית קטנה.
- `language/personality/`: פרופילי העדפות נטענים לכללי האישיות שקלוד יגדיר.
- `core/response.py`: התאמה בין פלט סמנטי של ה-Brain לבין תשובה עברית ודיבור אופציונלי.
- `agents/voice/agent.py`: בסיס אמיתי לסוכן קול עם תור, עצירה, interruption, pause/resume, סטטוס, health check ותוצאות מובנות.
- `voice/providers/`: ארכיטקטורת ספקי דיבור ניתנת להחלפה, כולל ספק macOS מקומי ו-Mock לבדיקות.
- `docs/language_system.md`: תיעוד מערכת השפה.
- `docs/voice_architecture.md`: תיעוד ארכיטקטורת הקול.

אימות חבילות שפה:

```bash
python3 -m scripts.validate_language_packs
```

ברירת מחדל בטוחה לקול:

- `NELA_VOICE_AUTO_SPEAK_RESPONSES=true`
- `NELA_VOICE_SILENT_MODE=true`

כך כל צינור השפה-לקול פעיל, אבל בלי השמעת אודיו בזמן פיתוח מוקדם.

## זרימת סקירה עם Claude

אפשרות 1: קישורי GitHub.

שולחים לקלוד קישור ישיר לענף, diff או קובצי blob ספציפיים.

ענף האינטגרציה הנוכחי:

```text
https://github.com/edentiram72-1/nela/tree/develop
```

אפשרות 2: יצירת review bundle.

```bash
python3 -m scripts.export_claude_review_bundle
```

ואז מדביקים או מעלים:

```text
docs/claude_review_bundle.md
```

קלוד אמור לסקור ארכיטקטורה, סיכונים, תיעוד, מקרי קצה ובטיחות מימוש. קלוד לא אמור לשכתב מודולים שהושלמו ללא הצדקה.

## חוקי שיתוף פעולה בין AI

### Codex

Codex אחראי על:

- מימוש
- תיקון באגים
- בדיקות
- ריפקטורינג
- סנכרון תיעוד עם קוד

Codex לא משנה ארכיטקטורה בלי תיעוד.

### Claude

Claude אחראי על:

- סקירת ארכיטקטורה
- סקירת תיעוד
- מציאת מקרי קצה
- הצעות UX
- ניתוח סיכונים
- הצעות ביצועים

Claude סוקר דרך קישורי GitHub, Pull Requests או review bundles.

### ChatGPT

ChatGPT אחראי על:

- הגדרת ארכיטקטורה
- עיצוב מערכות
- תיאום פיתוח
- אישור שינויים מבניים גדולים

## חוקי פיתוח

- פיצ'ר אחד לכל ענף.
- קומיטים קטנים.
- לעדכן תיעוד עם כל פיצ'ר.
- לשמור מודולים עצמאיים.
- לא לשנות קוד לא קשור.
- להוסיף בדיקות כשאפשר.
- להשאיר לוגיקת ביצוע בתוך Agents.
- להשאיר את ה-Brain ניטרלי לסוכנים.
- לעדכן `docs/ai_handoff.md` לפני handoff.
- לרשום החלטות מבניות משמעותיות ב-`docs/decisions.md`.

## מגבלות ידועות כרגע

- Desktop Agent V1 יכול לשלוט במחזור חיים של אפליקציות macOS נתמכות. שאר הסוכנים עדיין placeholders בטוחים.
- Hebrew Language Engine ו-Voice Agent Foundation הם עדיין תשתית foundation. חבילת השפה של Claude כבר משולבת כמקור תוכן רשמי, אבל התנהגות schema מלאה עדיין דורשת עבודת מנוע נוספת.
- ארטיפקטי הזהות הוויזואלית קיימים תחת `design/`, אבל חלון ה-Tkinter החי עדיין משתמש ב-placeholder לעין.
- זיהוי כוונות הוא דטרמיניסטי ומבוסס חוקים.
- Event Bus סינכרוני ופנימי לתהליך.
- זיכרון ארוך-טווח כרגע בזיכרון בלבד ולא נשמר לאורך זמן.
- timeout metadata לא יכול עדיין לעצור Agent סינכרוני תקוע.
- retries עדיין צריכים idempotency metadata לפני שמאפשרים תופעות לוואי אמיתיות.
- אין עדיין מדיניות הרשאות מרכזית.
- אין עדיין plugin loader.
- ביצוע parallel ו-conditional מיוצג במודל, אבל לא ממומש במלואו.

## העבודה הבאה המומלצת

לפני שמפעילים Agents אמיתיים:

1. להוסיף metadata של idempotency למשימות.
2. להוסיף מדיניות הרשאות ל-terminal, desktop, browser, files, accounts ופעולות תקשורת.
3. להקשיח את Event Bus עם בידוד שגיאות ו-history מוגבל.
4. לשפר metadata של capability registry.
5. לפשט את הנתיב הכפול של בקשות `Remember`.
6. לעדכן דיאגרמות כך שיציגו במפורש Decision Engine ו-Dispatcher.

ה-milestone הבא: לשלב את מערכת הזיכרון כאשר ה-ZIP יהיה זמין, ואז לחבר את ה-Living Eye דרך host שתומך ב-WebView ולהתקדם לקול production. אחרי שכבות הבטיחות האלה, להמשיך בזהירות לסוכנים אמיתיים נוספים.

## צעד ראשון לכל עוזר AI

1. לקרוא את `docs/ai_handoff.md`.
2. לקרוא את `docs/architecture.md`.
3. לקרוא את `docs/coding_rules.md`.
4. לבדוק את הענף הפעיל ב-Git.
5. לסקור קומיטים אחרונים.
6. לאשר את המשימה הנוכחית ואת מודול היעד.
7. לעדכן את `docs/ai_handoff.md` לפני עצירה.
