# Feature map: what exam-prep products offer, and our free version

Input for the JEVX planner. A survey on 2026-09-27 of about 80 products that Indian aspirants use: young startups
(seed to Series B, well under $100M; large players such as Physics Wallah, Unacademy, BYJU'S, Vedantu and Allen
left out on purpose) plus free tools and open-source projects. We take **ideas and features, never content**. Each
feature is rebuilt here free, with no login, open source, and honest about official sources.

Funding figures are from press reports found in the survey. They are context only and are never published on
student-facing pages.

## 1. AI mentor, tutor and doubt solving

| Who | What they sell |
|---|---|
| SuperKalam (UPSC; $2M seed, YC) | Personal AI mentor, daily plan, answer practice |
| Lytmus AI (NEET; ₹5 cr pre-seed) | AI mentors, study plans, doubt solving (₹499/month from 2026) |
| YoLearn.ai ($500K pre-seed), Sortmyprep ($350K), ProLearn (₹30 cr pre-seed) | AI tutors mapped to JEE, NEET, CUET, board syllabi |
| SATHEE (government, free) | AI weak-area detection with lectures and practice |

**Our free version:** [AI study prompts](../../tools/ai-study-prompts.md) for any free AI chat. They make the model
work from the official syllabus, cite NCERT or official sources, and say when it is unsure. Built. Next:
`T-314` adds an exam-specific prompt pack per family.

## 2. UPSC Mains answer evaluation

| Who | What they sell |
|---|---|
| Prayas AI, Prep IQ, Dalvoy, UPSC Answer Check, Aspirants.ai ($9/month), UPSC AI, CollectorBabu, Prepp IAS | Upload a handwritten answer; get rubric scores and feedback, with 2 to 5 free evaluations |

**Our free version:** an answer-evaluation prompt with the full rubric (demand of the question, directive word,
structure, substantiation, conclusion, word limit) in [AI study prompts](../../tools/ai-study-prompts.md). Built.
Next: `T-311` adds a daily answer-writing question from the official syllabus, linked to the official papers.

## 3. Previous-year questions, chapter-wise

| Who | What they offer |
|---|---|
| MARKS / MathonGo | Chapter-wise JEE and NEET PYQs, custom tests, preparation tracker |
| ExamSIDE, ExamGOAL, Examsnet, AcadXL | Free PYQs by subject, chapter and year |
| GATE Overflow (community) | Every GATE CSE PYQ since 1987, with discussion |

**Our free version:** [official archives](../../resources/previous-papers.md), built. The copyright of the papers
stays with the exam bodies, so we link and never copy. Next: `T-306` (more commissions), plus topic maps from
official papers, like the GATE EE and ESE EE topic-map tasks already in the backlog.

## 4. Mock tests in the real CBT interface

| Who | What they sell or share |
|---|---|
| Testbook (Series B), Oliveboard (₹23 cr pre-Series A, 8M users), ixamBee, Entri (24,000+ mocks, 6 languages), Cracku (large free tier), 2IIM | Paid test series with analysis, percentile and rank |
| neet-cbt (MIT), TakeMock, mock-test-canvas (open source) | NTA-style interface: question palette, mark for review, timer, negative marking |
| NTA Abhyas, SATHEE (government, free) | Official-interface mocks |

**Our free version:** link the free official mocks ([free coaching](../../resources/free-coaching.md)), built. Next:
`T-110` builds an NTA-style CBT engine in the website that runs the hive's original questions (`T-101` format),
offline.

## 5. Daily quiz and current affairs

| Who | What they offer |
|---|---|
| padhai.ai, PrepAiro, IAS Pilot, daily-quiz pages of coaching sites | Daily MCQs from PIB and newspapers, leaderboards |

**Our free version:** `T-310`, a daily PIB digest with original MCQs. Every question links the PIB release it comes
from.

## 6. Spaced repetition and flashcards

| Who | What they sell |
|---|---|
| FlashGenius, Spaced Revision (10,000+ cards), Reviso, DrNEET, MemoNeet, Revu, NEET Flashcards | Spaced-repetition flashcards, AI-generated decks |

**Our free version:** a [flashcards](../../tools/flashcards.md) tool in the website. It uses spaced repetition, works
offline, and saves progress only in the student's browser. It starts with a deck taken from the official text of
the Constitution. Built. Next: `T-313` adds one deck per module, each card sourced.

## 7. Planner, tracker, streaks and focus

| Who | What they offer |
|---|---|
| MARKS preparation tracker, Pariksha Sathi, Competitive Exam Tracker, MemoNeet, StudyPlanner | Syllabus checklists, countdowns, plans |
| Sankalp, LiveStudyRoom, Group Study Timer, FocusRoom, Virtual Library, StudyStream | Study rooms, Pomodoro, streaks, leaderboards |

**Our free version:** a [study planner](../../tools/study-planner.md). You pick an exam and it lists every shared
module it needs. You set a target date and it spreads the modules over the weeks left. It also has a module
checklist, a Pomodoro timer and a daily streak. Progress stays in your browser, with no login. Built.

## 8. Score, rank and college predictors

| Who | What they offer |
|---|---|
| TestPaper, MarksCalculator, ScoreGuru, ExamRanks | Score from the official response sheet |
| CareerDiksha, govtthub | Normalisation calculators |
| JoSAA Live, CatalyseR, MathonGo tools, NEET Companion and others | College predictors from JoSAA or MCC data |

**Our free version:** a [marks calculator](../../tools/score-calculator.md) for any marking scheme, built. Next:
- `T-111`: a college predictor from the official JoSAA archive.
- `T-113`: a normalisation calculator, only with the formula published by the exam body.

## 9. Job alerts and eligibility

| Who | What they offer |
|---|---|
| Naukri Alert, Sarkari Result apps and many clones | Notification alerts, eligibility summaries, often ad-heavy and unofficial |

**Our free version:** `T-107`, an exam calendar built from official dates only (`.ics`, which works in any calendar
app). `T-112` adds an RSS feed of updates. `T-315` adds eligibility (age, qualification, attempts) to the registry
from official notifications, with a checker.

## 10. Regional languages and low data

| Who | What they offer |
|---|---|
| Entri (6 languages), Pariksha (8 languages, 50 lakh students), SATHEE (12 languages) | Vernacular prep for state and central exams |

**Our free version:**
- **Built:** the whole website as an offline download (a zip that opens without internet).
- **Next:** `T-312`, Hindi versions of the most-used pages first.

## 11. Free official programmes (not competitors: we point students to them)

SATHEE, NTA Abhyas, IIT-PAL, SWAYAM Prabha, NPTEL, SWAYAM, DIKSHA, NCERT, NIOS, the MoSJE free coaching scheme,
Jamia RCA. See [free coaching](../../resources/free-coaching.md) and
[free platforms](../../resources/free-official-platforms.md).

## How this list stays ahead

- **Everything free, no login, no ads, open source.** That covers the website, the tools and the data
  (`/data/exams.json`).
- **Official sources first,** with an honest evidence status on every page. Most alert and PYQ sites give none.
- **One preparation, many exams:** the shared-module overlap map, which no product in the survey has.
- **Updated every hour** by the hive, in public, with receipts.
