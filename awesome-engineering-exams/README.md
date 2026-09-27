# Awesome Engineering Exams (India) ⚡

**Free, evidence-gated preparation maps for circuital-branch engineers:** GATE, UPSC ESE, UPSC CSE,
SSC JE, RRB JE, state AE/JE and PSU recruitment. We start with Electrical Engineering; ECE and Instrumentation
come next.

Coaching can cost lakhs. The information you need to start (official patterns, syllabi, previous papers,
free courses) is free, but scattered and often reposted wrong. This list gathers it in one place, links only
to the source, and tells you honestly how well each page has been checked.

It is updated every hour by an open agent pipeline (the [hive](ops/HIVE.md)). Every change is a public pull
request with a receipt. See [UPDATES.md](UPDATES.md).

## Exams

<!-- EXAMS:START -->
| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [GATE Electrical Engineering (EE)](exams/gate-ee.md) | IISc + 7 IITs for NCB-GATE (MoE) | GATE 2027 (IIT Madras) | 🟡 secondary | 2026-09-27 |
| [PSU recruitment for EE graduates](exams/psu-ee.md) | Central PSUs (each recruits separately) | Rolling, per PSU advertisement | ⚪ unverified | 2026-09-27 |
| [RRB Junior Engineer (JE) — Electrical](exams/rrb-je-ee.md) | Railway Recruitment Boards | CEN 05/2025 | 🟡 secondary | 2026-09-27 |
| [SSC Junior Engineer (JE) — Electrical](exams/ssc-je-ee.md) | Staff Selection Commission | SSC JE 2026 | 🟡 secondary | 2026-09-27 |
| [State AE / JE (Electrical) tracker](exams/state-ae-je.md) | State PSCs and state power utilities | Rolling, per state advertisement | ⚪ unverified | 2026-09-27 |
| [UPSC Civil Services (CSE) — for engineers](exams/upsc-cse.md) | Union Public Service Commission | CSE 2027 | 🟡 secondary | 2026-09-27 |
| [UPSC Engineering Services (ESE) — Electrical](exams/upsc-ese-ee.md) | Union Public Service Commission | ESE 2027 | 🟡 secondary | 2026-09-27 |
<!-- EXAMS:END -->

**Evidence status:** ✅ official = checked against the official notification · 🟡 secondary = cross-checked
against multiple non-official sources, official check pending · ⚪ unverified = starting list, not yet checked.
Whatever the status, confirm with the official notification before you apply or pay a fee.

## Start here

1. **[One preparation, many exams](resources/subject-map.md):** which EE subjects each exam tests, and what to
   add on top of the GATE core for ESE, CSE, SSC JE and RRB JE.
2. **[Free resources](resources/free-resources.md):** NPTEL, MIT OCW, simulators, and official sources for
   current affairs, organised by subject.
3. Open your exam's page above. Each one has the pattern, syllabus, a study order and its official links.

## How this list stays correct

- **Official sources only** for exam facts: notifications and brochures on government, IIT and PSU domains
  ([allowlist](ops/official-domains.txt)).
- **Every page states its evidence status**, and a page is marked ✅ only after someone opens the official
  document.
- **No piracy:** no coaching notes, book scans or lecture transcripts, and no Telegram or Drive dumps.
- **A content gate runs on every change** ([`scripts/validate.py`](scripts/validate.py)). It rejects missing
  sources, non-official links under "Official sources", file-dump links and dates in the future.

Found a mistake? Open an issue with the official link that shows it. Corrections backed by an official source
are merged first. See [CONTRIBUTING](CONTRIBUTING.md).

## Maintainer

Started by **[Rajon Das](https://github.com/lakhidas168-ship-it)**: B.Tech Electrical, NIT Silchar. Qualified
GATE EE twice and cleared SSC JE (Electrical); now preparing for UPSC ESE. This is the list Rajon wished had existed.

## License

Content: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Share and adapt it freely with credit.
Code (`scripts/`, `ops/`, `tests/`): MIT. See [LICENSE.md](LICENSE.md).

*Not affiliated with UPSC, SSC, the RRBs, the GATE organising institutes, any state commission or any PSU.*
