# 03 · WORK COMPLETED — the nine lanes, what each built, and its PR

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**Status vocabulary:** DONE · PARTIAL · FAILED · FALSIFIED · BLOCKED · DEFERRED · NOT STARTED.

---

## 0. The PR table — ten open, none merged

*(**PROVEN** — re-read from the GitHub API by the archive builder on 2026-09-06; raw output in
`evidence/round5-pull-requests.json` and `evidence/round5-ci-status.txt`.)*

| PR | Branch | Head *(verified)* | Lane | CI | State |
|---|---|---|---|---|---|
| **#79** | `integration/round5-2026-09-06` → `main` | `bab657a` | integration base | **PASS** | **OPEN — not merged** |
| **#80** | `lane-a3/round5-role-spec-trust-gate` | `569dad6` | A3 · role spec + threshold curve | **PASS** | **OPEN** |
| **#81** | `lane-c/round5-history` | `d241fdc` | C · History | **PASS** | **OPEN** |
| **#82** | `lane-d/round5-legacy-packs` | `0113019` | D · packs + legacy reprocess | **PASS** | **OPEN** |
| **#83** | `a1/round5-repair-framework` | `6652d58` | A1 · repair framework | **PASS** | **OPEN** |
| **#84** | `a2/round5-math-formula-accuracy` | `465d235` | A2 · math / formula / number | **PASS** | **OPEN** |
| **#85** | `e1/round5-semantic-foundation` | `ea6b0f8` | E1 · semantic foundation + census | **PASS** | **OPEN** |
| **#86** | `e2/round5-visualspec-renderer` | `538715f` | E2 · VisualSpec + renderer | **PASS** | **OPEN** |
| **#87** | `lane-b/round5-experience` | `6e5f6e7` | B · experience + workspace UX | **PASS** | **OPEN** |
| **#88** | `a4/round5-multi-signal-verification` | `1733ff7` | A4 · multi-signal verification | **PASS** | **OPEN** |

**All nine lane heads were independently re-resolved from `origin` by the archive builder and
match the heads recorded in the consolidated report, 9 of 9.** All ten PRs report
`Analyze & Test = SUCCESS`. `mergedAt` is `null` on all ten. *(PROVEN)*

---

## 1. Lane A1 — the repair framework and Vietnamese text · PR #83 · **PARTIAL**

**Built:** the `DETECT → REPAIR candidate → VALIDATE → RESTORE or WITHHOLD` framework with a
**plugin registry** (`tool/corpus/repair/**`, new); the third-signal layer in the Founder's
priority order; Vietnamese diacritic/syllable repairers; the **repair ledger** tracing
`source → observation → failure → repair rule → supporting signals → validation → disposition`;
per-signal precision, recall and **false-correction rate**.

**Measured:** the lane's own PR records coverage **0.551 → 0.577 with false trust unchanged** on
the gold set. Attachment closed at **8/8 = 1.000** in the pipeline, credited to A1 by Lane D. The
**R1 class closed on a second book** (tail-scan 1/6 → 0/6).

**Closed a latent trust hole (Founder STEM §4), verified in production code *and* tests.**
Before, `tc2_sdm.py:290-291` gave a Docling `FORMULA` label confidence `0.95` and waived the
math/unit/chem guards for it. After, on `a1/round5-repair-framework` (`tc2_sdm.py:380-390`),
confidence is `0.95` only if `formula_structured` is set, otherwise `0.60` with the evidence
string `structure NOT validated: label only`. Four regression tests
(`tool/tests/test_repair_vi_defects.py`, `class FormulaTrustHole`) pin it. The test class states
its own purpose: the hole is dormant today (Docling formula enrichment is off, FORMULA recall
0.000) and the tests exist so that switching it on cannot silently turn formula recognition into
trusted content. *(MEASURED + coordinator-verified against the branch.)*

**Why PARTIAL:** *(PROVEN, structurally)* **no file outside `tool/corpus/repair/` and
`tool/tests/` imports the `repair` package.** The lane is a validated laboratory with **no
connection to the product**.

## 2. Lane A2 — math / formula / number · PR #84 · **DONE**

| Measure | Result |
|---|---|
| Fraction detection, 89 hand-counted printed fractions across 3 pages | precision **1.000** [0.957–1.000] · recall **0.955** [0.890–0.982] |
| Restored expressions, every one hand-verified against the printed page | **10 / 10 = 1.000** [0.722–1.000] |
| …of which on the **HOLDOUT** (pages never opened while the rules were written) | **8 / 8 = 1.000** |
| Surviving false corrections | **0** |
| Fabricated expressions, before → after | **2 → 0** |
| Physics false trust | **−3 blocks**, at **0** over-withhold cost, across 36,029 blocks / 1,410 pages |
| Toán coverage (97 Toán pages, 2,692 blocks) | 0.1686 → **0.1705** |

**Six deterministic validators** justify each restore — `vinculum-raster-v1`, `ink-accounted-v1`,
`operator-raster-v1`, `structure-grammar-v1`, `digit-provenance-v1`, `arith-selfcheck-v1`.
RESTORE requires **≥1 PASS and no FAIL**; **all-abstain withholds**.

**The lane's own warning, and it is the round's methodological finding.** Two wrong repairs were
produced and **neither was found by a metric — both were found by looking at the page.**
`c) 16/21 × 3/5` came back as `16/21 - 3/5` because Apple Vision returns a token whose text is
`-` for the printed `×`. Ink was fully accounted for, nothing was invented, the grammar was
sound, both vinculums were real. **Ink-accounting proves completeness; provenance proves honesty;
neither proves identity.** Closed by a glyph check, after which the printed `×` is refused and
the correct `b) 8/11 − 19/33` on the same row still restores.

**A design precedent adopted ecosystem-wide.** `MathExpression` has `from_json` but
**deliberately no `from_latex`**; `latex` and `text` are computed properties with no setter. A
rendering string cannot become structure, so model-generated LaTeX cannot launder itself into
truth. Routed to E1 and E2 as a rule: **no constructor from a presentation form.**

## 3. Lane A3 — role spec + trust-gate sensitivity · PR #80 · **PARTIAL**

**Built:** `ROLE DEFINITION SPEC v1` — the Founder's 20 roles, each with semantic definition,
inclusion, exclusion, positive examples, confusing counterexamples, relationship rules, teaching
consequence and default trust consequence; the mapping between three vocabularies (spec 20 /
gold 21 / pipeline 25) and **four holes it exposes** (e.g. `rule` is in the pipeline's map but no
branch ever returns it; `speech_bubble` is never emitted). Plus `tool/corpus/thresholds/`
(`evidence.py · gate.py · sweep.py · run.py`), **25 unit tests**, `THRESHOLDS.example.json`.

**No classifier was trained, tuned or edited** — `tc2_sdm.py` was read, never written, as ordered.

**Reproduction discipline:** the evidence extractor reproduces the published round-5 baseline
exactly — **643 learning blocks · 354 served · coverage 0.5505 · 26 false trusted · FTR 0.0734** —
and asserts it page by page; if the two drift it raises instead of reporting.

**Re-annotation result** (n = 26: all 6 role disagreements + 7 WRONG/WRONG + 13 OK/OK controls):

| | agreement | κ | #1 WRONG | #2 WRONG |
|---|---|---|---|---|
| before (as judged in round 4, these 26 rows) | 0.769 | **0.524** | 0.308 | 0.462 |
| after (spec applied; 3 undecidable rows left as disagreements) | 0.962 | **0.923** | 0.500 | 0.538 |
| after, on the 23 rows the spec decides | 1.000 | **1.000** | — | — |

**Why PARTIAL, in the lane's own words:** «κ = 1.000 on decided rows is not a discovery. A
deterministic procedure applied to identical observations agrees with itself; that is arithmetic,
not evidence.» The spec was written **after** reading these rows — the result is **in-sample**.
The honest measure is the **decidability rate: 23/26 = 0.885 decided, 3 convention-dependent, 0
undecidable**. And the spec is **stricter** than the round-4 annotators were: on one control both
annotators said OK and the spec says WRONG, so **applying it would raise the measured role-error
rate**. Three questions go to the Founder: **Q-ROLE-1 / Q-ROLE-2 / Q-ROLE-3**.

## 4. Lane B — experience · PR #87 · **DONE**

CI pass (2m16s), `flutter analyze` clean, `flutter test` **995 passed / 1 skipped**.
Device: **Nokia 6.1, «Na · Lớp 6», 5 iterations, 36 frames, 28 steps, 0 downgraded.**

**Trực quan reached the concept board: 70–80 % → 85–90 %.** Typed `SemanticData` renders as a
real **mindmap** (hub + four coloured branches + curved edges) and a real **process flow**
(nodes / edges / arrows) instead of a text stand-in, plus a source-grounded figure chip that
**fails closed**. Bookshelf 65–75 % → 80–85 %; Book 70–80 % → 80–88 %.
**Experience Fidelity overall 80–85 % → 85–88 %.**

**The workspace duplication problem, quantified before anything was designed.** The Founder's
complaint («thấy lặp lại, quá nhiều biểu diễn của ba Learning View, SAM chiếm chỗ cố định, CTA
trùng») was measured two independent ways: widget tree at the exact Nokia viewport
(392.7 × 698.2 dp) → pinned chrome **411 dp = 58.9 % of the viewport** with **7 occurrences** of
the three view names on one screen; and on the device with the real Bài 17 fixture, template
match error 0.0 → **first lesson content at y = 820 px, 42.7 % of the screen consumed before
content**. A 13-entry duplication map found **4 genuine duplicates**, plus a finding nobody had
named: the three views carry **two different word sets** — «Học **với** SAM» on the tab versus
«Học **cùng** SAM» on the card — **six labels for three things**.

**Three substantially different concepts, four builds from one commit**
(`--dart-define=WAL_ASSIST=…`, default = current behaviour). See `06-PRODUCT-REALITY.md` §3 for
the measured table and the recommendation.

**Five defects the device found that no test did** — D1 the pinned card hid the mindmap's hub
(48 % → 27 % chrome) · D2 the «why» said «bảng» while showing a mindmap · D3 54 «chưa có» rows
buried the one SAM lesson · D4 a 21 dp badge floating between tabs · D5 dismissing made SAM
vanish entirely. **All five fixed and re-walked.**

## 5. Lane C — History · PR #81 · **DONE, with its own round-4 rule FALSIFIED**

`flutter analyze` clean · `flutter test` 928 passed / 42 skipped · Lane C Python 31 passed /
2 skipped. Bounded to LS&ĐL 5; both rules stayed **PROPOSED and History-only**; nothing entered
the universal bridge.

**Method note that makes every number attributable:** the round-5 run reuses round 4's raw
Docling/XY-cut candidate files and re-runs only `tc2_sdm → tc2_attach → tc2_tsl →
tsl_to_lesson_document`. **Every difference is pipeline *code*, never OCR noise.**

| measure | round 4 | round 5 |
|---|---|---|
| lessons with a TSL (LS&ĐL 5) | 23 / 28 | **28 / 28** |
| headers detected | 23 (TOC-confirmed 6) | **28 (TOC-confirmed 10)** |
| book learning blocks | 1,483 = 1,263 trusted + 220 withheld | 1,472 = **1,020 trusted + 452 withheld** |
| chapters | 0 | **6 «Chủ đề»** |
| Bài 8 learning | 51 = 34 + 17 | 51 = **36 trusted + 15 withheld** |

**On Bài 8's independently print-verified ledger: false trust 8 → 6, correct served 26 → 30,
false withheld 14 → 10.** **6 of 16** withheld Bài 8 blocks became restorable, every one
print-confirmed, **with no guard changed**, recovering the events block and the «Âu Lạc (179
TCN)» anchor that round 4 had lost.

**The falsification — the most valuable thing the lane could have produced.** See
`04-FAILURES-AND-FALSIFICATIONS.md` §4.

**And the harder half of the doctrine, proved:** when the repair signal proposed correcting an
attribution, **two independent signals objected and the candidate was rejected — so the
attribution stopped being served rather than being half-corrected.** That is
`DETECT → REPAIR → VALIDATE → WITHHOLD` completing correctly.

## 6. Lane D — legacy reprocess + packs · PR #82 · **PARTIAL**

CI PASS on head `0113019`. Batch 2 = six lessons across five failure classes, **including
History/Geography, never measured before**. Batch 1 is the holdout.

| Measure | Result |
|---|---|
| Pack `verify` | **0/12 FAIL → 12/12 PASS** |
| OLD baseline reproduced | **three times** — twice by `restore`, once by re-deriving metrics, identical to stored `BASELINE-METRICS.json` field for field |
| Content delta of the provenance rebuild | **exactly zero** (248/248 unchanged, 12/12 hashes identical), confirmed by byte-comparing canonical JSON independently of the tool |
| Blind badge audit of the diagnostic delta | **27/27 = 1.000**; four unbadged pages scored *unjudgeable* and all three newly-flagged rows are among them — reported as **unmeasurable**, not as 0.964 |
| Founder §3 fail-closed | **−41 of 248** activities; 10 grades byte-identical; **10 lessons lose their exercise list entirely**; defect 6 on shipped packs **ABSENT** (0 of 207) |
| Tests | Dart **948 pass / 15 skipped** · Python **348 OK** · `flutter analyze` clean |

**Snapshot discipline enforced in code**, not in prose: `packs.py` refuses to overwrite a
snapshot; a rebuild refuses unless a snapshot matches the packs on disk by sha256; a restore
re-checks every hash. Three snapshots under `poc-out/round5/legacy/`
(`packs-before-round5`, `-before-inferred-fix`, `-before-a1`), each with `SHA256SUMS`, full
`buildProvenance`, baseline metrics, pipeline version and README.

**Founder STEM §3 closed by failing closed.** `tool/extract/rebuild_fractions.py:124` stamps
every row `status: 'INFERRED'`, `method: 'geometric-fraction-rebuild-v1'` — «dựng từ hình học ⇒
KHÔNG phải nguyên văn». The pack builder copied only `expr / skillCaseId / page / book`, so
**41 expressions (g4: 26 across 6 lessons; g5: 15 across 4)** shipped as if printed in the book,
carrying a `skillCaseId` — into the exercise path a child is taught from. The pack schema has no
provenance field and the app cannot display an INFERRED caveat, so Lane D chose **fail closed**:
a non-verbatim upstream record is not emitted at all. Nothing deleted upstream; every drop
counted and logged with a reason; the rows return the moment provenance can travel with them.
**Coverage consequence, stated rather than hidden: 41 expressions leave the packs**, recorded as
a correctness gain with the count named.

**Why PARTIAL:** **R13** and **R15** discovered and left open; defect 8 still open on the lesson
path (9 → 9 and 13 → 13); R2 and R3 present on a fourth build; R7c PARTIAL.

**Lane D's corrections against its own tooling, recorded because they bear on how much weight its
other numbers carry:** a false FIXED verdict on R7c that its own blind audit caught; blank restore
sheets the annotator refused to score (which is why there is no fabricated 6/6); a sandbox
guarantee that silently depended on alphabetical file order; an orphan detector that **missed the
exact case the Founder named** by grouping on the wrong field; and a mechanism string that named
a branch and went stale.

## 7. Lane E1 — semantic foundation + K-12 census · PR #85 · **DONE**

CI green, **285 tool tests OK**. **Recommendation: GO WITH ARCHITECTURE CHANGE** — explicitly
*not* GO (holdout precision and inter-annotator agreement are unmeasured, and `e1-definition-v1`
over-fires: «68.8 % of lessons have a definition» is not credible), and explicitly *not* MORE
EVIDENCE (the load-bearing claims were checked deterministically on real corpus data).

**How few primitives suffice:** **6 primitives · 6 relations carried everything built across 224
lessons**, and 10 visual families are projections of them. `isA` may collapse into `hasPart`, so
possibly **5**. `Method`, `SkillCase`, `CurriculumEdge` and `ConceptMap` are **absent from the
core**. Verified rather than asserted: `compiler_audit()` records **at runtime** that each of six
compilers read only `nodes` / `relations` / `claims`.

**Domain extensions — 3 of 7 proven, 3 refuted:** MATH_AST (66.3 % of lessons) · LIT_TEXT
(14.9 %) · CHEM_REACTION (7.8 %) are **necessary**; History · Geography · Science needed **none**
(`Event` + `atTime` already carried LS&ĐL at 7/7). **So `ToánGraph` / `HistoryGraph` /
`ScienceGraph` are unnecessary** — what is genuinely per-domain is **notation and literary form,
not subject**. Three planned subsystems removed.

**Grounding integrity 0.952 → 1.000 across 4,681 spans**, with **226 real failures** found and
fixed — including «hình 1a» matching only «hình 1» at scale.

**Discipline:** five near-verbatim SGK test fixtures replaced with invented text (D4).
**No LLM was called anywhere in this lane.**

## 8. Lane E2 — VisualSpec + one renderer across three subjects · PR #86 · **DONE, with a
retraction**

CI pass on `bcaf373`, `flutter analyze` clean, **973 Dart tests pass / 42 skipped**.

**§19 proven — one renderer, three subjects, two independent semantic paths:**

| lesson | family | path into the renderer |
|---|---|---|
| KHTN 6 Bài 17 · tách chất | `process` | typed semantic layer (`tsl-enumerated-steps-v1`) |
| KHTN 7 p20 · nguyên tố hoá học | `sequence` | document structure |
| Ngữ văn 9 p82 · nói và nghe | `sequence` | document structure |
| Vật lí 10 p88 · thực hành tổng hợp lực | `sequence` | document structure |

A grade-6 chemistry procedure and a grade-9 literature speaking task share no vocabulary, no
layout and no pedagogy — only a **shape**, which is all the renderer can see.

**Discipline that held:** **0 runtime model calls**, enforced by an import-set test. 5 specs /
6 sections / 19,289 bytes precomputed; two builds byte-identical. Correction edits the claim, the
graph or the spec — **never pixels** — and a node cannot be added without a `sourceRef`.
Measured on `tool/corpus/tc_gold/` — 54 human-annotated pages across 10 subjects, **committed**,
so a clean clone reproduces it.

**The retraction is the more valuable result.** See `04-FAILURES-AND-FALSIFICATIONS.md` §6.

## 9. Lane A4 — multi-signal verification · PR #88 · **DONE**

CI PASS, Python **321 passed / 8 skipped**. Touches only `tool/corpus/verify/**` plus tests and
two docs — **no `lib/**`, no `repair/**`, no `mathfix/**`, no `legacy/**`**.

| Signal | Detection recall | Correction precision | **False correction rate** | Proposals / 1,000 clean tokens |
|---|---|---|---|---|
| **Cross-corpus (strict)** | 0.500 | 0.938 | **0.063** | **0.92** |
| Cross-corpus (recall policy) | 0.644 | — | 0.092 | 2.90 |
| **LLM semantic** | **0.717 — best in lane** | — | **1.000** | 13 proposals on 60 already-correct rows, **all wrong**; 26.7 % of rows flagged |

Proper-noun false correction **0.000** at all three cross-corpus policies. Router human-review
rate **0.0900** over 1,200 real SDM blocks (LLM alone 0.416, cross-corpus alone 0.993, external
**0.000**).

**Which signal earned a place:**
- **Unreservedly:** `A.enumerator` + `D.section_sequence` (the only propose-and-verify pair) ·
  `B.page_furniture` (deletion-only) · **edge position**.
- **Conditionally:** `D.cross_corpus` — on the holdout, **but not on History prose**.
- **Detector only:** `G.llm_semantic`.
- **Did not earn a pipeline place:** `H.external` — consult rate **0.000**. The question a
  Trusted Corpus asks is **source-bound**: «what does *this page* say», which no external
  authority can answer.
- **Not re-opened:** `F.third_stack`.

**Denominators — A4 took R13 seriously.** It measures over **OCR lines and SDM blocks, never the
TSL**, so its router set still contains the **77 `role=empty` blocks (6.4 %)** that vanish
downstream. Index excludes the 13 evaluated books.

**The correction workflow (schema and triage only, no UI):**
`CorrectionRecord{record_id, source_block_id, original, proposed, reason, reporter_type,
source_evidence, evidence[], corpus_version, reported_at, status, validation, reviewer,
reviewed_at, resulting_corpus_version, prior_record_id}` →
`REPORTED → VALIDATING | NEEDS_SOURCE | ACCEPTED | REJECTED`. **A report without a page reading
is a detection, not a correction**, and users never overwrite canonical truth.

---

## 10. The composition check — a deliverable nobody planned

Because merging is a Founder gate, composition was verified in a **throw-away worktree** built
from `integration/round5-2026-09-06` with all nine lane branches merged in. No PR was touched, no
branch pushed, the worktree is disposable. Gitignored assets (321 pack files, 24 fixtures) were
synced from the main checkout first, so a missing-asset failure could not be mistaken for a defect.

| Check | Result |
|---|---|
| Git merge, 9 lane branches | **0 conflicts** |
| `flutter analyze` | **No issues found** |
| Python suite | **623 tests OK** (19 skipped) |
| Dart suite | **1061 tests, All tests passed** (3 skipped) |

**Recommendation adopted as standing procedure: run the composition check at the end of every
round.** Nine green CI badges did not mean the round worked; running them together is what found
out. It costs one throw-away worktree and roughly ten minutes. The three defects it found are in
`04-FAILURES-AND-FALSIFICATIONS.md` §7.
