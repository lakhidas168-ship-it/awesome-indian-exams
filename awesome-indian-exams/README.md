# Awesome Indian Exams ⚡

**Free, evidence-gated preparation maps for India's most-attempted competitive exams:** GATE, ESE, JEE,
NEET, UPSC, state PSCs, SSC, RRB, IBPS/SBI/RBI, defence, CTET/NET, CUET, CLAT, CAT and more.

Coaching can cost lakhs. The information you need to start (official patterns, syllabi, previous papers, free
courses) is free, but scattered and often reposted wrong. This list gathers it in one place, links only to the
source, and tells you honestly how well each page has been checked.

**Most exams share most of their syllabus.** SSC, railway and banking exams largely overlap. JEE, NEET, state CETs
and CUET share NCERT science. UPSC and the state PSCs share general studies. So this list is built from **shared
modules**: prepare a module once and see every exam it counts for in the
[overlap map](resources/overlap-map.md).

It is updated every hour by an open agent pipeline (the [hive](ops/HIVE.md)). Every change is public and comes
with a receipt. See [UPDATES.md](UPDATES.md).

## Start here

1. **[Overlap map](resources/overlap-map.md):** the shared modules and every exam each one covers.
2. **[All exams](resources/all-exams.md):** the full registry with conducting bodies and official websites.
3. **Shared modules:** [quantitative aptitude](modules/quant-aptitude.md) · [reasoning](modules/reasoning.md) ·
   [English](modules/english-language.md) · [general awareness](modules/general-awareness.md) ·
   [general science](modules/general-science.md)
4. **Electrical engineering track:** [EE subject map](resources/ee-subject-map.md) ·
   [EE free resources](resources/ee-free-resources.md)

## Exams

<!-- EXAMS:START -->
**Coverage:** 10 exam pages written, 118 exams in the [registry](resources/all-exams.md). The hive adds pages every hour.

### Engineering jobs: GATE, ESE, JE, PSU, state AE/JE

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [GATE Electrical Engineering (EE)](exams/engineering/gate-ee.md) | IISc + 7 IITs for NCB-GATE (MoE) | GATE 2027 (IIT Madras) | 🟡 secondary | 2026-09-27 |
| [PSU recruitment for EE graduates](exams/engineering/psu-ee.md) | Central PSUs (each recruits separately) | Rolling, per PSU advertisement | ⚪ unverified | 2026-09-27 |
| [RRB Junior Engineer (JE) — Electrical](exams/engineering/rrb-je-ee.md) | Railway Recruitment Boards | CEN 05/2025 | 🟡 secondary | 2026-09-27 |
| [SSC Junior Engineer (JE) — Electrical](exams/engineering/ssc-je-ee.md) | Staff Selection Commission | SSC JE 2026 | 🟡 secondary | 2026-09-27 |
| [State AE / JE (Electrical) tracker](exams/engineering/state-ae-je.md) | State PSCs and state power utilities | Rolling, per state advertisement | ⚪ unverified | 2026-09-27 |
| [UPSC Engineering Services (ESE) — Electrical](exams/engineering/upsc-ese-ee.md) | Union Public Service Commission | ESE 2027 | 🟡 secondary | 2026-09-27 |

_6 more in the [registry](resources/all-exams.md#engineering), pages queued for the hive._

### Engineering entrance: JEE and state CETs

_11 exams in the [registry](resources/all-exams.md#engineering-entrance), pages queued for the hive._

### Medical: NEET and medical PG

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [NEET UG](exams/medical/neet-ug.md) | National Testing Agency (NTA) | NEET UG 2026 | 🟡 secondary | 2026-09-27 |

_4 more in the [registry](resources/all-exams.md#medical), pages queued for the hive._

### UPSC

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [UPSC Civil Services (CSE) — for engineers](exams/upsc/upsc-cse.md) | Union Public Service Commission | CSE 2027 | 🟡 secondary | 2026-09-27 |

_8 more in the [registry](resources/all-exams.md#upsc), pages queued for the hive._

### State PSC civil services

_19 exams in the [registry](resources/all-exams.md#state-psc), pages queued for the hive._

### SSC

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [SSC CGL (Combined Graduate Level)](exams/ssc/ssc-cgl.md) | Staff Selection Commission | SSC CGL 2026 | 🟡 secondary | 2026-09-27 |

_8 more in the [registry](resources/all-exams.md#ssc), pages queued for the hive._

### Railways: RRB and RPF

_6 exams in the [registry](resources/all-exams.md#railways), pages queued for the hive._

### Banking, insurance and regulators

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [IBPS PO (Probationary Officer)](exams/banking/ibps-po.md) | Institute of Banking Personnel Selection | IBPS PO/MT 2026 | 🟡 secondary | 2026-09-27 |

_10 more in the [registry](resources/all-exams.md#banking), pages queued for the hive._

### Defence (non-UPSC entries)

_5 exams in the [registry](resources/all-exams.md#defence), pages queued for the hive._

### Teaching and research: TET, NET, KVS

_7 exams in the [registry](resources/all-exams.md#teaching), pages queued for the hive._

### University and design entrance: CUET, JAM, NIFT, NID

_8 exams in the [registry](resources/all-exams.md#university-entrance), pages queued for the hive._

### School-level entrance

_2 exams in the [registry](resources/all-exams.md#school), pages queued for the hive._

### Law entrance

_3 exams in the [registry](resources/all-exams.md#law), pages queued for the hive._

### Management entrance: CAT, XAT and others

_8 exams in the [registry](resources/all-exams.md#management), pages queued for the hive._

### Professional courses: CA, CS, CMA

_3 exams in the [registry](resources/all-exams.md#professional), pages queued for the hive._
<!-- EXAMS:END -->

**Evidence status:** ✅ official = checked against the official notification · 🟡 secondary = cross-checked
against multiple non-official sources, official check pending · ⚪ unverified = starting list, not yet checked.
Whatever the status, confirm with the official notification before you apply or pay a fee.

## How this list stays correct

- **Official sources only** for exam facts: notifications and brochures on government, university, IIT and
  exam-body domains ([allowlist](ops/official-domains.txt)).
- **Every page states its evidence status**, and a page is marked ✅ only when there is evidence that the official
  document was opened. In the cloud hive, the code records every page the agent fetched, and a page is not
  accepted as ✅ without a recorded fetch of an official source.
- **No piracy:** no coaching notes, book scans or lecture transcripts, and no Telegram or Drive dumps.
- **A content gate runs on every change** ([`scripts/validate.py`](scripts/validate.py)). It rejects missing
  sources, non-official links under "Official sources", file-dump links, broken internal links and dates in the
  future.

Found a mistake? Open an issue with the official link that shows it. See [CONTRIBUTING](CONTRIBUTING.md).

## Maintainer

Started by **[Rajon Das](https://github.com/lakhidas168-ship-it)**: B.Tech Electrical, NIT Silchar. Qualified
GATE EE twice and cleared SSC JE (Electrical); now preparing for UPSC ESE. Built for every student who can't afford
coaching.

## License

Content: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Share and adapt it freely with credit.
Code (`scripts/`, `ops/`, `tests/`): MIT. See [LICENSE.md](LICENSE.md).

*Not affiliated with any exam body, commission, university or employer listed here.*
