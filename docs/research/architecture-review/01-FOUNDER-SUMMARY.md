# 01 — Founder Summary (one page)

*Everything below is MEASURED on the six Science SGK books (1,049 pages), a 75-page SGV sample and a 54-page gold set unless marked. Details in A–J.*

**THE QUESTION.** Does the chain **Source → SDM → block trust → Role Layer → deterministic guards → lesson attachment → Trusted Structured Lesson** hold end to end on a real, bounded, versioned slice? **Yes for reading, no for asking.**

| stage | status | the number |
|---|---|---|
| Source → SDM (Docling + Apple Vision, XY-cut verifier) | **DONE** | 1,049 pages in ≈ 18 min (2 workers), 0 errors, deterministic (7/7 shared pages byte-identical with TC-v1); enumerators restored on 5,110 blocks (TC-v1's 65-event defect closed) |
| Block trust (agreement + 10 reason-coded guards) | **DONE, target not reached** | slice: 0.854 of learning blocks TRUSTED; gold: FTR 0.112 dev / 0.121 held-out / 0.100 science — **the guards did not lower the hard-page false-trust floor** (TC-v1 cascade 0.121); they changed *what* is withheld (figure-dependent prompts, objectives, answer keys, teacher text, diagram labels) |
| Role Layer — six roles | **PARTIAL** | science gold: QUESTION 0.889 / 0.870 (trusted-question precision 0.970, n=33) · SIDEBAR 0.964 / 0.818 · OBJECTIVE 0.696 / 0.941 · ANSWER 0.800 / 0.400 · INSTRUCTION 0.50 / 0.50 · **ACTIVITY 0.00 / 0.00** — see ROLE-LAYER-AND-SHORT-ANSWER-GATE.md |
| Guards | **DONE** | reason codes on 2,032 withheld regions: agree_text 865 · figure_dependent 638 · agree_order 229 · diagram-page 199 · colour-heavy page 111 · box_boundary 95 · math 42 · answer_leak 30 · low OCR 20 · role_conflict 7 |
| Lesson attachment + TOC repair | **DONE** | header-based correct on 22/23 science gold pages (TOC range: 15/23), 15/16 held-out; six books ranged 194 → **238**; KHTN 7 18 → 37 lessons, KHTN 8 22 → 44 (the printed books run to Bài 39 / Bài 47) |
| Trusted Structured Lesson | **DONE** | 238 documents, 2 FULL / 236 PARTIAL, 11,971 native blocks + 2,032 withheld regions with bbox + reason + provenance; 0 answer keys inside |
| Hybrid Smart Book feed, `with_images` / `no_images` | **DONE (data only)** | same sequence, both modes: 11,971 native + 2,032 crop-refs / withheld-refs (14.5 % of the sequence); `no_images` is fully functional; page images remain a **LEGAL GATE** |
| Provenance / bbox check | **DONE** | every block id → (book, pdf page, printed page, bbox, pipeline, OCR conf, agreement score) |
| Old-vs-new WAL-206 funnel (measurement) | **DONE** | exact-scope gate pass 5 → 12 lessons; variant (+EXPLAIN) 96 → 154; TOC lessons 194 → 238 — **not the success criterion**, and every NEW question carries the 0.83–0.89 role precision |
| SGV sample (≤ 100 pages) | **DONE** | 75 pages: 0 SGV blocks trusted for a learner, 711 blocks that would have leaked without the SGV lexicon; pairing by enumerator 2 / 26 |
| Decision records (knowledge base) | **DONE (PROPOSED)** | 4 PROPOSED decisions filed per KNOWLEDGE_UPDATE_PROTOCOL (see JIRA-STATUS.md for the PR) |
| Architecture Review A–J | **DONE** | this package |

**VERDICTS.**
1. **Source architecture: validated.** The chain runs, is versioned, resumable, deterministic and cheap (≈ 1.5 s/page); every withheld block keeps a bbox and a reason. Filed as PROPOSED decisions 1–4.
2. **Short-Answer Surface: stays DEFERRED — measured.** QUESTION precision 0.83–0.89 < 0.95; ACTIVITY is not detectable from words at all (0.00). The missing signal is the page's icons/box colours, not more lexicon (H2).
3. **False trust: unchanged at ≈ 1 in 10 on hard pages, ≈ 0 on prose.** Guards make the withheld set meaningful but do not beat the shared-mode floor; the < 1 % bar needs a statistical audit on shipped lessons or a structurally different verifier (H5, J.4).
4. **"Fully sourceable lesson" is the wrong unit** on the Science family: 2 of 238; every lesson is PARTIAL with a median of 8 withheld regions. The product unit is *a lesson with references*, i.e. the `no_images` Hybrid Smart Book.
5. **Denominators must not be collapsed** — and the TOC repair moves them: ranged 3,381 → ≈ 3,425 (six books alone), canonical 3,679 → ≥ 3,725 if KHTN 7/8's real lesson counts are adopted. Founder decision requested (DECISIONS-REQUESTED #5).
6. **Runtime semantics stay OPEN.** Four options laid out (F.4); the first Dart change under any option is a TSL reader, not a View.

**FALSIFIED this round (kept, not hacked):** guards ≠ lower FTR on hard pages; deterministic lexicon ≠ 0.95 question precision; ACTIVITY ≠ a lexical role; page-feature guard costs real questions on colour-heavy elementary pages.

**COST.** ≈ 25 min of Docling wall time, ≈ 10 min of other tooling, ≈ 115 MB under `tc-v2/tc2-p1/`, no cloud spend, no new project dependency, nothing old modified or deleted.

**ASK.** Read `DECISIONS-REQUESTED.md` (10 items). Recommended minimum: ratify decisions 1–4 as PROPOSED → ACCEPTED, confirm the two-denominator rule and the TOC repair (#5), and choose H1 + H3 as the next bounded step.

**READY FOR FOUNDER REVIEW — nothing merged.**
