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
3. **Shared modules** (all 33 are in the overlap map): [quantitative aptitude](modules/quant-aptitude.md) ·
   [reasoning](modules/reasoning.md) · [English](modules/english-language.md) ·
   [general awareness](modules/general-awareness.md) · [general science](modules/general-science.md)
4. **Electrical engineering track:** [EE subject map](resources/ee-subject-map.md) ·
   [EE free resources](resources/ee-free-resources.md)
5. **[Previous-year papers](resources/previous-papers.md):** the official archives of UPSC, SSC, GATE, NTA and state
   commissions, plus official JoSAA and MCC counselling data.
6. **[Free coaching](resources/free-coaching.md):** SATHEE (IIT Kanpur), IIT-PAL, SWAYAM Prabha, and government
   schemes that pay coaching fees for eligible students.
7. **[Free official platforms](resources/free-official-platforms.md):** NCERT, NIOS, DIKSHA, NTA Abhyas, SWAYAM,
   NPTEL, e-PG Pathshala, National Digital Library, PIB.
8. **[Open-source projects](resources/open-source-projects.md):** community question banks, datasets, planners and
   notes vaults.
9. **[How to study](resources/study-methods.md):** the methods with the strongest research evidence, and the
   aspirant tips that keep coming up.
10. **[Free study tools](tools/index.md):** a study planner for your exam with a focus timer and streaks,
   spaced-repetition flashcards, a marks calculator, and AI study prompts. No login, no ads; progress stays in
   your browser, and they work in the offline copy too.
11. **Open data:** every exam, module and page status as one JSON file, built by
   [`scripts/export_json.py`](scripts/export_json.py) for apps and planners.

## Exams

<!-- EXAMS:START -->
**Coverage:** 118 exam pages written, 118 exams in the [registry](resources/all-exams.md). The hive adds pages every hour.

### Engineering jobs: GATE, ESE, JE, PSU, state AE/JE

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [GATE Civil Engineering (CE)](exams/engineering/gate-ce.md) | IISc + 7 IITs for NCB-GATE (MoE) | GATE 2027 (IIT Madras) | ✅ official | 2026-09-28 |
| [GATE Computer Science and Information Technology (CS)](exams/engineering/gate-cs.md) | IISc + 7 IITs for NCB-GATE (MoE) | GATE 2027 (IIT Madras) | ✅ official | 2026-09-28 |
| [GATE Data Science and Artificial Intelligence (DA)](exams/engineering/gate-da.md) | IISc + 7 IITs for NCB-GATE (MoE) | GATE 2027 (IIT Madras) | ✅ official | 2026-09-28 |
| [GATE Electrical Engineering (EE)](exams/engineering/gate-ee.md) | IISc + 7 IITs for NCB-GATE (MoE) | GATE 2027 (IIT Madras) | 🟡 secondary | 2026-09-27 |
| [GATE Electronics and Communication (EC)](exams/engineering/gate-ec.md) | IISc + 7 IITs for NCB-GATE (MoE) | GATE 2027 (IIT Madras) | ✅ official | 2026-09-28 |
| [GATE Instrumentation Engineering (IN)](exams/engineering/gate-in.md) | IISc + 7 IITs for NCB-GATE (MoE) | GATE 2027 (IIT Madras) | ✅ official | 2026-09-28 |
| [GATE Mechanical Engineering (ME)](exams/engineering/gate-me.md) | IISc + 7 IITs for NCB-GATE (MoE) | GATE 2027 (IIT Madras) | 🟡 secondary | 2026-09-27 |
| [PSU recruitment for EE graduates](exams/engineering/psu-ee.md) | Central PSUs (each recruits separately) | Rolling, per PSU advertisement | ⚪ unverified | 2026-09-28 |
| [RRB Junior Engineer (JE) — Electrical](exams/engineering/rrb-je-ee.md) | Railway Recruitment Boards | CEN 04/2026 | ✅ official | 2026-09-28 |
| [SSC Junior Engineer (JE) — Electrical](exams/engineering/ssc-je-ee.md) | Staff Selection Commission | SSC JE 2026 | ✅ official | 2026-09-28 |
| [State AE / JE (Electrical) tracker](exams/engineering/state-ae-je.md) | State PSCs and state power utilities | Rolling, per state advertisement | ✅ official | 2026-09-28 |
| [UPSC Engineering Services (ESE) — Electrical](exams/engineering/upsc-ese-ee.md) | Union Public Service Commission | ESE 2027 | 🟡 secondary | 2026-09-27 |

### Engineering entrance: JEE and state CETs

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [AP EAPCET](exams/engineering-entrance/ap-eapcet.md) | JNT University Kakinada on behalf of APSCHE | AP EAPCET 2026 | ✅ official | 2026-09-27 |
| [BITSAT](exams/engineering-entrance/bitsat.md) | BITS Pilani | BITSAT 2026 | ✅ official | 2026-09-28 |
| [COMEDK UGET](exams/engineering-entrance/comedk-uget.md) | COMEDK | COMEDK UGET 2026 | ✅ official | 2026-09-28 |
| [JEE Advanced](exams/engineering-entrance/jee-advanced.md) | IITs (organising IIT rotates) | JEE Advanced 2026 (IIT Roorkee) | ✅ official | 2026-09-27 |
| [JEE Main](exams/engineering-entrance/jee-main.md) | National Testing Agency (NTA) | JEE Main 2026 | 🟡 secondary | 2026-09-27 |
| [KEAM (Engineering)](exams/engineering-entrance/keam.md) | Commissioner for Entrance Examinations, Kerala | KEAM 2026 | ✅ official | 2026-09-28 |
| [Karnataka CET (KCET)](exams/engineering-entrance/kcet.md) | Karnataka Examinations Authority | KCET 2026 | ✅ official | 2026-09-28 |
| [MHT CET (PCM)](exams/engineering-entrance/mht-cet.md) | State Common Entrance Test Cell, Maharashtra | MHT CET 2026 | ✅ official | 2026-09-28 |
| [TG (Telangana) EAPCET](exams/engineering-entrance/ts-eapcet.md) | JNTUH (on behalf of TGCHE) | TG EAPCET 2026 | ✅ official | 2026-09-27 |
| [VITEEE](exams/engineering-entrance/viteee.md) | Vellore Institute of Technology | VITEEE 2026 | ✅ official | 2026-09-27 |
| [WBJEE](exams/engineering-entrance/wbjee.md) | West Bengal Joint Entrance Examinations Board | WBJEE 2026 | ✅ official | 2026-09-27 |

### Medical: NEET and medical PG

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [AIIMS NORCET (Nursing Officer)](exams/medical/aiims-norcet.md) | AIIMS New Delhi | NORCET-11 (Notice No. 103/2026, 24 July 2026) | ✅ official | 2026-09-28 |
| [FMGE (Foreign Medical Graduate Examination)](exams/medical/fmge.md) | National Board of Examinations in Medical Sciences (NBEMS) | FMGE October 2026 | ✅ official | 2026-09-28 |
| [INI-CET](exams/medical/ini-cet.md) | AIIMS New Delhi | INI-CET (latest session) | ⚪ unverified | 2026-09-27 |
| [NEET PG](exams/medical/neet-pg.md) | National Board of Examinations in Medical Sciences (NBEMS) | NEET PG 2026 | 🟡 secondary | 2026-09-28 |
| [NEET UG](exams/medical/neet-ug.md) | National Testing Agency (NTA) | NEET UG 2026 | 🟡 secondary | 2026-09-27 |

### UPSC

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [UPSC CAPF (Assistant Commandant)](exams/upsc/upsc-capf.md) | Union Public Service Commission | CAPF (AC) 2026 | 🟡 secondary | 2026-09-28 |
| [UPSC Civil Services (CSE) — for engineers](exams/upsc/upsc-cse.md) | Union Public Service Commission | CSE 2027 | 🟡 secondary | 2026-09-27 |
| [UPSC Combined Defence Services (CDS)](exams/upsc/upsc-cds.md) | Union Public Service Commission | CDS (I/II) 2026 | ✅ official | 2026-09-28 |
| [UPSC Combined Geo-Scientist](exams/upsc/upsc-geoscientist.md) | Union Public Service Commission | Combined Geo-Scientist 2027 | 🟡 secondary | 2026-09-28 |
| [UPSC Combined Medical Services (CMS)](exams/upsc/upsc-cms.md) | Union Public Service Commission | CMS 2026 | 🟡 secondary | 2026-09-27 |
| [UPSC EPFO (EO/AO and APFC)](exams/upsc/upsc-epfo.md) | Union Public Service Commission | EPFO (latest notice) | 🟡 secondary | 2026-09-27 |
| [UPSC Indian Economic Service / Indian Statistical Service (IES/ISS)](exams/upsc/upsc-ies-iss.md) | Union Public Service Commission | IES/ISS 2026 | 🟡 secondary | 2026-09-27 |
| [UPSC Indian Forest Service (IFoS)](exams/upsc/upsc-ifos.md) | Union Public Service Commission | IFoS 2026 | 🟡 secondary | 2026-09-28 |
| [UPSC NDA and NA](exams/upsc/upsc-nda.md) | Union Public Service Commission | NDA & NA (I/II) 2026 | 🟡 secondary | 2026-09-28 |

### State PSC civil services

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [APPSC Group 1](exams/state-psc/appsc-group-1.md) | Andhra Pradesh Public Service Commission | APPSC Group 1 (latest) | ⚪ unverified | 2026-09-27 |
| [APSC Combined Competitive Examination (Assam)](exams/state-psc/apsc-cce.md) | Assam Public Service Commission | APSC CCE (latest) | ⚪ unverified | 2026-09-27 |
| [BPSC Combined Competitive Examination](exams/state-psc/bpsc-cce.md) | Bihar Public Service Commission | BPSC 71st CCE (2025) | 🟡 secondary | 2026-09-27 |
| [CGPSC State Service Examination](exams/state-psc/cgpsc-sse.md) | Chhattisgarh Public Service Commission | CGPSC State Service Exam (latest) | ⚪ unverified | 2026-09-27 |
| [GPSC Class 1–2 (Gujarat)](exams/state-psc/gpsc-class-1-2.md) | Gujarat Public Service Commission | GPSC Class 1–2 (latest) | 🟡 secondary | 2026-09-28 |
| [HPSC HCS (Haryana Civil Services)](exams/state-psc/hpsc-hcs.md) | Haryana Public Service Commission | HPSC HCS (latest) | ⚪ unverified | 2026-09-27 |
| [JPSC Combined Civil Services](exams/state-psc/jpsc-cce.md) | Jharkhand Public Service Commission | JPSC CCE (latest) | ⚪ unverified | 2026-09-27 |
| [KPSC KAS (Karnataka Administrative Service)](exams/state-psc/kpsc-kas.md) | Karnataka Public Service Commission | KPSC KAS (latest) | ⚪ unverified | 2026-09-27 |
| [Kerala PSC exams (LDC, KAS and others)](exams/state-psc/kerala-psc.md) | Kerala Public Service Commission | Kerala PSC (rolling notifications) | ⚪ unverified | 2026-09-27 |
| [MPPSC State Service Examination](exams/state-psc/mppsc-sse.md) | Madhya Pradesh Public Service Commission | MPPSC State Service Exam (latest) | ⚪ unverified | 2026-09-27 |
| [MPSC State Services (Rajyaseva)](exams/state-psc/mpsc-rajyaseva.md) | Maharashtra Public Service Commission | MPSC Rajyaseva (latest) | ⚪ unverified | 2026-09-28 |
| [OPSC Odisha Civil Services](exams/state-psc/opsc-ocs.md) | Odisha Public Service Commission | OPSC OCS (latest) | ⚪ unverified | 2026-09-27 |
| [RPSC RAS/RTS](exams/state-psc/rpsc-ras.md) | Rajasthan Public Service Commission | RPSC RAS/RTS (latest) | ⚪ unverified | 2026-09-27 |
| [TGPSC (Telangana) Group 1](exams/state-psc/tgpsc-group-1.md) | Telangana Public Service Commission | TGPSC Group 1 (latest) | ⚪ unverified | 2026-09-27 |
| [TNPSC Group 1](exams/state-psc/tnpsc-group-1.md) | Tamil Nadu Public Service Commission | TNPSC Group 1 (latest) | ⚪ unverified | 2026-09-27 |
| [TNPSC Group 4](exams/state-psc/tnpsc-group-4.md) | Tamil Nadu Public Service Commission | TNPSC Group 4 (latest) | ⚪ unverified | 2026-09-27 |
| [UKPSC Combined State Civil Services](exams/state-psc/ukpsc-pcs.md) | Uttarakhand Public Service Commission | UKPSC PCS 2026 (Advt A-1/E-1/2026-27) | ✅ official | 2026-09-28 |
| [UPPSC PCS (Combined State/Upper Subordinate Services)](exams/state-psc/uppsc-pcs.md) | Uttar Pradesh Public Service Commission | PCS 2025 (Advt. A-1/E-1/2025) | 🟡 secondary | 2026-09-28 |
| [WBCS (West Bengal Civil Service)](exams/state-psc/wbcs.md) | Public Service Commission, West Bengal | WBCS (latest) | ⚪ unverified | 2026-09-27 |

### SSC

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [Delhi Police Constable (Executive)](exams/ssc/delhi-police-constable.md) | Staff Selection Commission | Constable (Executive) Male and Female in Delhi Police Examination, 2025 | ✅ official | 2026-09-27 |
| [SSC CGL (Combined Graduate Level)](exams/ssc/ssc-cgl.md) | Staff Selection Commission | SSC CGL 2026 | ✅ official | 2026-09-27 |
| [SSC CHSL (Combined Higher Secondary Level)](exams/ssc/ssc-chsl.md) | Staff Selection Commission | SSC CHSL 2026 | 🟡 secondary | 2026-09-27 |
| [SSC CPO (Sub-Inspector in Delhi Police and CAPFs)](exams/ssc/ssc-cpo.md) | Staff Selection Commission | SSC CPO 2025 | ✅ official | 2026-09-28 |
| [SSC GD Constable](exams/ssc/ssc-gd.md) | Staff Selection Commission | SSC GD Constable 2026 | ✅ official | 2026-09-28 |
| [SSC Junior Hindi Translator (JHT)](exams/ssc/ssc-jht.md) | Staff Selection Commission | SSC JHT 2026 (Combined Hindi Translators Examination, 2026) | ✅ official | 2026-09-27 |
| [SSC MTS (Multi-Tasking Staff) and Havaldar](exams/ssc/ssc-mts.md) | Staff Selection Commission | SSC MTS 2025 | ✅ official | 2026-09-27 |
| [SSC Selection Posts](exams/ssc/ssc-selection-post.md) | Staff Selection Commission | SSC Selection Post Phase 14 (2026) | ✅ official | 2026-09-28 |
| [SSC Stenographer (Grade C and D)](exams/ssc/ssc-stenographer.md) | Staff Selection Commission | SSC Stenographer (latest) | 🟡 secondary | 2026-09-27 |

### Railways: RRB and RPF

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [RPF Constable](exams/railways/rpf-constable.md) | Railway Protection Force (through RRBs) | RPF Constable (latest CEN) | 🟡 secondary | 2026-09-27 |
| [RPF Sub-Inspector](exams/railways/rpf-si.md) | Railway Protection Force (through RRBs) | CEN RPF 01/2024 | ✅ official | 2026-09-28 |
| [RRB Assistant Loco Pilot (ALP)](exams/railways/rrb-alp.md) | Railway Recruitment Boards | RRB ALP (CEN 01/2026) | 🟡 secondary | 2026-09-27 |
| [RRB Group D (Level 1)](exams/railways/rrb-group-d.md) | Railway Recruitment Boards | RRB Group D (latest CEN) | 🟡 secondary | 2026-09-27 |
| [RRB NTPC (Non-Technical Popular Categories)](exams/railways/rrb-ntpc.md) | Railway Recruitment Boards | RRB NTPC (latest CEN) | 🟡 secondary | 2026-09-27 |
| [RRB Technician (Grade 1 Signal and Grade 3)](exams/railways/rrb-technician.md) | Railway Recruitment Boards | CEN 02/2026 | ✅ official | 2026-09-28 |

### Banking, insurance and regulators

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [IBPS Clerk](exams/banking/ibps-clerk.md) | Institute of Banking Personnel Selection | IBPS Clerk (CRP CSA, latest) | 🟡 secondary | 2026-09-27 |
| [IBPS PO (Probationary Officer)](exams/banking/ibps-po.md) | Institute of Banking Personnel Selection | IBPS PO/MT 2026 | 🟡 secondary | 2026-09-27 |
| [IBPS RRB (Officer Scale I and Office Assistant)](exams/banking/ibps-rrb.md) | Institute of Banking Personnel Selection | IBPS RRB (CRP RRBs-XV, 2026) | 🟡 secondary | 2026-09-28 |
| [IBPS SO (Specialist Officer)](exams/banking/ibps-so.md) | Institute of Banking Personnel Selection | IBPS SO (CRP SPL, latest) | ⚪ unverified | 2026-09-27 |
| [LIC AAO (Assistant Administrative Officer)](exams/banking/lic-aao.md) | Life Insurance Corporation of India | LIC AAO (latest) | ⚪ unverified | 2026-09-27 |
| [NABARD Grade A (Assistant Manager)](exams/banking/nabard-grade-a.md) | National Bank for Agriculture and Rural Development | NABARD Grade A (latest) | ⚪ unverified | 2026-09-27 |
| [RBI Assistant](exams/banking/rbi-assistant.md) | Reserve Bank of India | RBI Assistant (latest) | 🟡 secondary | 2026-09-27 |
| [RBI Grade B (Officer, DR General)](exams/banking/rbi-grade-b.md) | Reserve Bank of India | RBI Grade B (DR) General, PY2026 | ✅ official | 2026-09-27 |
| [SBI Clerk (Junior Associate)](exams/banking/sbi-clerk.md) | State Bank of India | SBI Clerk (latest) | 🟡 secondary | 2026-09-27 |
| [SBI PO (Probationary Officer)](exams/banking/sbi-po.md) | State Bank of India | SBI PO 2026 (Advt CRPD/PO/2026-27/09) | 🟡 secondary | 2026-09-28 |
| [SEBI Grade A (Assistant Manager)](exams/banking/sebi-grade-a.md) | Securities and Exchange Board of India | SEBI Grade A (latest) | 🟡 secondary | 2026-09-27 |

### Defence (non-UPSC entries)

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [AFCAT (Air Force Common Admission Test)](exams/defence/afcat.md) | Indian Air Force | AFCAT (latest) | 🟡 secondary | 2026-09-27 |
| [Agniveer (Army) Common Entrance Exam](exams/defence/agniveer-army.md) | Indian Army | Agnipath Army CEE (latest) | ✅ official | 2026-09-28 |
| [Agniveer (Navy) SSR and MR](exams/defence/agniveer-navy.md) | Indian Navy | Navy Agniveer (latest batch) | 🟡 secondary | 2026-09-27 |
| [Agniveer Vayu (Air Force)](exams/defence/agniveer-vayu.md) | Indian Air Force | Agniveer Vayu (latest intake) | 🟡 secondary | 2026-09-27 |
| [Indian Coast Guard Navik (GD) / Yantrik](exams/defence/icg-navik.md) | Indian Coast Guard | ICG (CGEPT, latest batch) | 🟡 secondary | 2026-09-27 |

### Teaching and research: TET, NET, KVS

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [CSIR NET (JRF / Assistant Professor)](exams/teaching/csir-net.md) | National Testing Agency (NTA) | CSIR NET (latest session) | 🟡 secondary | 2026-09-27 |
| [CTET (Central Teacher Eligibility Test)](exams/teaching/ctet.md) | Central Board of Secondary Education | CTET September 2026 | ✅ official | 2026-09-28 |
| [DSSSB teacher and staff recruitment (Delhi)](exams/teaching/dsssb.md) | Delhi Subordinate Services Selection Board | Rolling advertisements | ✅ official | 2026-09-27 |
| [KVS teacher and staff recruitment](exams/teaching/kvs-recruitment.md) | Kendriya Vidyalaya Sangathan | KVS & NVS combined recruitment (latest) | 🟡 secondary | 2026-09-27 |
| [NVS teacher and staff recruitment](exams/teaching/nvs-recruitment.md) | Navodaya Vidyalaya Samiti | Recruitment Notification 01/2025 (joint KVS+NVS, via CBSE) | ✅ official | 2026-09-28 |
| [State TETs (UPTET, REET, MAHA TET and others)](exams/teaching/state-tet.md) | State education boards (under the NCTE framework) | Varies by state (each state notifies its own TET) | ⚪ unverified | 2026-09-27 |
| [UGC NET](exams/teaching/ugc-net.md) | National Testing Agency (NTA) | UGC NET (latest session) | 🟡 secondary | 2026-09-27 |

### University and design entrance: CUET, JAM, NIFT, NID

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [CUET PG](exams/university-entrance/cuet-pg.md) | National Testing Agency | CUET PG 2026 | ⚪ unverified | 2026-09-27 |
| [CUET UG](exams/university-entrance/cuet-ug.md) | National Testing Agency (NTA) | CUET UG 2026 | 🟡 secondary | 2026-09-27 |
| [IIT JAM (Joint Admission Test for Masters)](exams/university-entrance/iit-jam.md) | IITs and IISc (IIT Kharagpur for JAM 2027) | JAM 2027 (IIT Kharagpur, 14 February 2027) | ⚪ unverified | 2026-09-27 |
| [NATA (National Aptitude Test in Architecture)](exams/university-entrance/nata.md) | Council of Architecture | NATA 2026 | ✅ official | 2026-09-28 |
| [NCHM JEE (hotel management)](exams/university-entrance/nchm-jee.md) | National Testing Agency | NCHM JEE (latest) | ⚪ unverified | 2026-09-27 |
| [NID Design Aptitude Test (DAT)](exams/university-entrance/nid-dat.md) | National Institute of Design | NID DAT (latest) | 🟡 secondary | 2026-09-27 |
| [NIFT entrance (B.Des, B.FTech)](exams/university-entrance/nift-entrance.md) | National Institute of Fashion Technology | NIFTEE 2026 | ✅ official | 2026-09-28 |
| [UCEED](exams/university-entrance/uceed.md) | IIT Bombay | UCEED 2026 | ✅ official | 2026-09-28 |

### School-level entrance

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [AISSEE (Sainik School entrance)](exams/school/aissee.md) | National Testing Agency | AISSEE 2026 | ✅ official | 2026-09-28 |
| [JNV Selection Test (Navodaya, Class 6)](exams/school/jnvst.md) | Navodaya Vidyalaya Samiti | JNVST Class VI (latest) | ⚪ unverified | 2026-09-27 |

### Law entrance

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [AILET (NLU Delhi)](exams/law/ailet.md) | National Law University Delhi | AILET 2027 | ✅ official | 2026-09-28 |
| [CLAT (Common Law Admission Test)](exams/law/clat.md) | Consortium of National Law Universities | CLAT 2027 | 🟡 secondary | 2026-09-27 |
| [MAH CET Law](exams/law/mh-cet-law.md) | State CET Cell, Maharashtra | MAH CET Law (latest) | ⚪ unverified | 2026-09-27 |

### Management entrance: CAT, XAT and others

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [CAT (Common Admission Test)](exams/management/cat.md) | IIMs (convening IIM rotates) | CAT 2026 | ✅ official | 2026-09-27 |
| [CMAT](exams/management/cmat.md) | National Testing Agency | CMAT (latest) | ⚪ unverified | 2026-09-27 |
| [IPMAT (IIM Indore)](exams/management/ipmat-indore.md) | IIM Indore | IPMAT Indore 2027 | 🟡 secondary | 2026-09-27 |
| [MAH MBA/MMS CET](exams/management/mah-mba-cet.md) | State CET Cell, Maharashtra | MAH MBA/MMS CET 2026 | ✅ official | 2026-09-27 |
| [MAT (Management Aptitude Test)](exams/management/mat.md) | All India Management Association | Multiple sessions per year | ⚪ unverified | 2024-05-22 |
| [NMAT by GMAC](exams/management/nmat.md) | GMAC | NMAT 2026-27 (test window 2 November – 20 December 2026) | ✅ official | 2026-09-27 |
| [SNAP](exams/management/snap.md) | Symbiosis International University | SNAP 2026 | ✅ official | 2026-09-28 |
| [XAT](exams/management/xat.md) | XLRI Jamshedpur | XAT 2027 (3 January 2027) | 🟡 secondary | 2026-09-27 |

### Professional courses: CA, CS, CMA

| Exam | Conducted by | Cycle | Evidence | Last verified |
|---|---|---|---|---|
| [CA Foundation](exams/professional/ca-foundation.md) | Institute of Chartered Accountants of India | Thrice a year (January, May, September) | ✅ official | 2026-09-28 |
| [CMA Foundation](exams/professional/cma-foundation.md) | Institute of Cost Accountants of India | December 2026 term (Syllabus 2022) | ✅ official | 2026-09-28 |
| [CSEET (CS Executive Entrance Test)](exams/professional/cseet.md) | Institute of Company Secretaries of India | CSEET October 2026 | ✅ official | 2026-09-28 |
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
