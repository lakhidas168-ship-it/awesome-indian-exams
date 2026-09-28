# Feature catalogue: 100 features, how they connect, and our free version

Companion to [feature-map.md](feature-map.md), for the JEVX planner. It lists every feature seen across the
roughly 80 surveyed products (young startups under $100M, free tools, open-source projects). Many products sell
one or two of these features in isolation; the advantage here is **connecting them**: the output of one feature
is the input of the next, all free, offline-capable and official-source-first.

**Status:** ✅ built · 🔜 backlog task · 💡 idea for JEVX to schedule (highest-value first).

## The features

### A. Content and syllabus

| # | Feature | Status |
|---|---|---|
| 1 | Exam page with official pattern, syllabus and links | ✅ 118 exams |
| 2 | Shared-module overlap map: one preparation, many exams | ✅ (no surveyed product has it) |
| 3 | Module pages with free, official resources | ✅ 33 modules |
| 4 | Evidence status on every page (official / secondary / unverified) | ✅ (no surveyed product has it) |
| 5 | Official notification and website links | ✅ |
| 6 | Syllabus as structured data: a topic tree per module | 💡 |
| 7 | Topic weightage from official previous papers | 🔜 GATE EE, ESE EE tasks |
| 8 | Formula sheets | 🔜 T-103 |
| 9 | Concept prerequisite map | 🔜 backlog |
| 10 | Hindi and regional-language pages | ✅ Hindi start page · 🔜 T-312 |

### B. Previous papers and practice

| # | Feature | Status |
|---|---|---|
| 11 | Official previous-paper archives | ✅ |
| 12 | Topic-wise tagging of previous-year questions | 💡 |
| 13 | Original practice questions under an open license | 🔜 T-101 |
| 14 | Daily practice set | ✅ question of the day (`tools/daily`) · 🔜 bigger pool `T-319` |
| 15 | Custom test builder (pick modules and topics) | 💡 needs 13, 22 |
| 16 | Bookmarks and a local mistake list | 💡 with 22 |
| 17 | Links to official answer keys | ✅ via the archives |
| 18 | Topic-frequency heatmap from previous papers | 💡 needs 12 |
| 19 | Difficulty tags | 💡 |
| 20 | Discussion per question (GitHub Discussions) | 💡 needs an owner setting |

### C. Mock tests

| # | Feature | Status |
|---|---|---|
| 21 | Links to the free official mocks (NTA Abhyas, SATHEE) | ✅ |
| 22 | NTA-style CBT engine: palette, mark for review, timer | 🔜 T-110 |
| 23 | Section timers and section switching | 🔜 T-110 |
| 24 | Negative-marking scoring | ✅ calculator · 🔜 T-110 |
| 25 | Post-mock analysis: accuracy, time per question | 🔜 T-110 |
| 26 | Mistake classification: concept, silly, time, guess | ✅ as a method and an AI prompt · 💡 in the engine |
| 27 | Expected value of a guess | ✅ calculator |
| 28 | Percentile estimate | 💡 only from official score distributions, never invented |
| 29 | Mocks that work offline | ✅ offline copy · 🔜 T-110 |
| 30 | Printable test | 💡 |

### D. Revision and memory

| # | Feature | Status |
|---|---|---|
| 31 | Spaced-repetition flashcards | ✅ |
| 32 | Decks built from official sources | ✅ 1 deck · 🔜 T-313 |
| 33 | Make a deck with a free AI chat, in our format | ✅ prompt |
| 34 | Import your own deck file (local only) | 💡 |
| 35 | Export decks to Anki (CSV) | 💡 |
| 36 | Cloze (fill-in-the-blank) cards | 💡 |
| 37 | Daily review reminder in any calendar app | 💡 with 76 |
| 38 | Mock mistakes become flashcards | 💡 needs 22, 31 |
| 39 | Short-notes templates | 💡 |
| 40 | Revision block in the plan | ✅ planner |

### E. Planning and motivation

| # | Feature | Status |
|---|---|---|
| 41 | Pick an exam, see every module it needs | ✅ planner |
| 42 | Week-by-week plan to the exam date | ✅ planner |
| 43 | Module checklist with progress | ✅ planner |
| 44 | Focus (Pomodoro) timer | ✅ planner |
| 45 | Daily streak | ✅ planner |
| 46 | Multi-exam plan: shared modules once | 💡 (built on 2) |
| 47 | Countdown to the official exam date | 🔜 T-107 |
| 48 | Weekly review routine | ✅ AI prompt and study methods |
| 49 | Export the plan to a calendar | 💡 |
| 50 | Study rooms and accountability | 💡 point to existing free rooms rather than build |

### F. AI help

| # | Feature | Status |
|---|---|---|
| 51 | Doubt solver grounded in NCERT and the official syllabus | ✅ prompt |
| 52 | UPSC Mains answer evaluator with the full rubric | ✅ prompt |
| 53 | Previous-paper analyst | ✅ prompt |
| 54 | Flashcard maker | ✅ prompt |
| 55 | Mistake coach | ✅ prompt |
| 56 | Current affairs from an official release | ✅ prompt |
| 57 | Interview board practice | ✅ prompt |
| 58 | Prompt packs per exam family | 🔜 T-314 |
| 59 | An evidence-gated exam AI that cites this list, runs in the browser or offline | 🔜 see [exam-llm.md](exam-llm.md) |
| 60 | MCP server for AI agents (`ops/mcp_server.py`) | ✅ |

### G. Current affairs

| # | Feature | Status |
|---|---|---|
| 61 | Daily PIB digest | 🔜 T-310 |
| 62 | Original MCQs from each digest | 🔜 T-310 |
| 63 | Monthly compilation | 💡 needs 61 |
| 64 | Budget and Economic Survey guide, official links | 💡 |
| 65 | Government schemes tracker | ✅ partly (free coaching, myScheme) |
| 66 | Links from current events to the static syllabus | ✅ prompt · 💡 in 61 |

### H. Answer writing and interview

| # | Feature | Status |
|---|---|---|
| 67 | Daily Mains question | 🔜 T-311 |
| 68 | Directive words guide (discuss, critically examine…) | 💡 |
| 69 | Essay topics from official papers | 💡 |
| 70 | Self-evaluation rubric | ✅ prompt |
| 71 | Interview question bank from the official DAF sections | 💡 |
| 72 | PSU and bank interview guides | 💡 |

### I. Admissions, jobs and counselling

| # | Feature | Status |
|---|---|---|
| 73 | Official JoSAA and MCC data links | ✅ |
| 74 | College predictor from official data | 🔜 T-111 |
| 75 | Eligibility checker | 🔜 T-315 |
| 76 | Exam calendar (.ics) from official dates | 🔜 T-107 |
| 77 | Updates feed (RSS) | 🔜 T-112 |
| 78 | Normalisation calculator with the official formula | 🔜 T-113 |
| 79 | Score from a pasted response sheet (client-side) | 💡 |
| 80 | Posts, pay levels and departments from the notification | 💡 |
| 81 | Official cut-off history | 💡 |
| 82 | Application checklist: documents, photo and signature sizes | 💡 |
| 83 | Free coaching and fee-paying scheme finder | ✅ |
| 84 | Scholarship links | ✅ National Scholarship Portal |

### J. Access, platform and trust

| # | Feature | Status |
|---|---|---|
| 85 | Free website with search | ✅ |
| 86 | Dark mode | ✅ |
| 87 | Phone-friendly layout | ✅ |
| 88 | Offline download of everything | ✅ |
| 89 | No login; progress stays on the device | ✅ |
| 90 | No ads, no tracking, no third-party fonts | ✅ |
| 91 | Open data (`/data/exams.json`) | ✅ |
| 92 | Open source: MIT code, CC BY-SA content | ✅ |
| 93 | Works as an Obsidian vault | ✅ |
| 94 | Installable app (PWA) | ✅ manifest and service worker |
| 95 | Low-data, text-first pages | ✅ mostly · 💡 audit |
| 96 | Accessibility: keyboard and screen reader | 💡 audit |
| 97 | Updated every hour by the hive | ✅ |
| 98 | Receipts for every change | ✅ |
| 99 | Contributions through issues and pull requests | ✅ |
| 100 | Community Q&A | 💡 needs an owner setting |

## The interconnections: where one feature feeds the next

These chains are what no single product in the survey offers, and they cost nothing because everything is static
files plus the student's own browser.

1. **Previous papers → topic tags → plan order** (11 → 12 → 18 → 42). The most-asked topics are scheduled first.
2. **Mock → mistakes → flashcards → daily review** (22 → 26 → 38 → 31). Every mistake is revised at growing gaps.
3. **Official calendar → planner date → countdown and reminders** (76 → 42 → 47 → 37). One official date drives
   the whole plan.
4. **Overlap map → multi-exam plan** (2 → 46). Aim at an exam family, not one exam.
5. **Eligibility → exam picker** (75 → 41). Students only see exams they can actually take.
6. **PIB digest → MCQs → flashcards** (61 → 62 → 31). Current affairs join the same spaced revision.
7. **Deck format ↔ AI flashcard maker** (32 ↔ 54 → 34). Any free AI chat produces cards that import directly.
8. **Official data → predictor → counselling links** (73 → 74). College choice from the official archive only.
9. **Evidence status → exam AI citations** (4 → 59). The AI answers only from pages whose status it can show.
10. **Everything → offline copy** (88). Every tool, deck and page ships in one download for patchy internet.

## Insights behind the design

- **From learning research:** practice testing and spaced practice are the highest-utility techniques, while
  rereading and highlighting are low utility ([resources/study-methods.md](../../resources/study-methods.md)).
  So the tools centre on testing (previous papers, mocks, flashcards) and on spacing (flashcard intervals, the
  revision block).
- **From aspirant advice:** previous papers first, analyse every mock, use fewer sources with more revisions, and
  protect sleep. Each of these is a tool or a default here.
- **From the paid products:** the value students pay for is feedback (evaluation, analysis) and structure (plans,
  daily targets). Rubric prompts, the planner and mock analysis give both for free.
- **What we do not copy:** paywalled content, coaching notes, pirated PDFs, invented percentiles or "guaranteed
  selection" claims. Trust is our edge: official sources and honest statuses.
- **Gap to close:** community threads on Reddit and similar forums could not be read from the cloud session.
  `T-316` mines them from the Mac.

Growth loops (sharing, previews, posters, the daily question) are planned in [growth-plan.md](growth-plan.md).
