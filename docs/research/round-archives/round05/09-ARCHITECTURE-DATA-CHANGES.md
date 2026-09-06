# 09 · ARCHITECTURE AND DATA CHANGES

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**None of these changes is merged.** Every one lives on an open PR. This file records what the
round *built*, what it *proved about the shape* of the system, and what it *removed from the
plan*.

---

## 1. NEW SUBSYSTEMS

| Subsystem | Path | Lane / PR | State |
|---|---|---|---|
| **Repair framework** — `DETECT → REPAIR candidate → VALIDATE → RESTORE or WITHHOLD` with a **plugin registry** and a **repair ledger** | `tool/corpus/repair/**` | A1 · #83 | built, CI-green, **not imported by anything outside itself and the tests** |
| **Math / formula accuracy** — canonical `MathExpression` AST + six deterministic validators | `tool/corpus/mathfix/**` | A2 · #84 | built, holdout-verified; **no bridge carrier to the app** |
| **Multi-signal verification + router** | `tool/corpus/verify/**` | A4 · #88 | built; registers into A1's package |
| **Trust-gate instrument** — `evidence.py · gate.py · sweep.py · run.py` + `THRESHOLDS.example.json` | `tool/corpus/thresholds/**` | A3 · #80 | built, 25 tests; **no threshold chosen** |
| **Semantic foundation** — 6 primitives · 6 relations, six compilers, `compiler_audit()` | E1 · #85 | | built, 285 tests |
| **VisualSpec + shared renderers** — one renderer across three subjects | E2 · #86 | | built, 973 Dart tests |
| **Assist layer** (workspace options A / B / C behind `--dart-define=WAL_ASSIST`) | `lib/features/**` | B · #87 | built, device-measured, **B selected** |

---

## 2. STRUCTURAL HOLES FOUND, WITH THE LINE THAT CAUSES THEM

| Hole | Location | Consequence | State |
|---|---|---|---|
| **R13 — line geometry read, then discarded one step before the guards** | `tool/corpus/tc2_sdm.py:1060`, spent on a verse boolean at `:1110` | The evidence a repair needs is thrown away before anything can use it | **OPEN** — round-6 workstream A |
| **R13 — formula-labelled blocks die as `empty` for "no letters"** | `tool/corpus/tc2_sdm.py:276-277` | **14 of 15** Docling formula blocks on the Toán pages, one carrying `7 8 2 8 7 - 2 8 5 8`. The reason code **misstates what was lost**. **4 validated math restores are blocked by `empty_block` alone** | **OPEN** |
| A `FORMULA` role bought trust 0.95 and waived the math/unit/chem guards | was `tool/corpus/tc2_sdm.py:290-291` | The day Docling formula enrichment is switched on, formula recognition would silently become trusted teaching content | **CLOSED** — see §3 |
| **Bridge has no `formula` role** | `tool/corpus/tsl_to_lesson_document.py` — `ROLE_MAP` has 11 keys, `formula` appears **0 times** *(PROVEN)* | A validated `MathExpression` **cannot reach the app** | **OPEN** |
| Provenance dropped on the pack path | `tool/ui/build_lesson_index.py` | 41 geometry-rebuilt expressions shipped as if printed | **FIXED, fail-closed** — see §4 |
| **R15 — attach provenance does not reproduce** | attach artefact vs a fresh run | **950 of 6,176** page verdicts differ, **896 unexplained**; the **pack build** depends on it | **OPEN — Founder decision** |

---

## 3. THE LATENT FORMULA-TRUST HOLE, CLOSED BY CONSTRUCTION

**Before** (`integration/round5-2026-09-06`, `tc2_sdm.py:290-291`):

```python
if b['role'] == 'FORMULA':
    return 'formula', 'native', 0.95, ['docling formula']
```

A **label** bought confidence 0.95, and `role_guards` then waived the math/unit/chem guards for
that role.

**After** (`a1/round5-repair-framework`, `tc2_sdm.py:380-390`):

```python
structured = bool(b.get('formula_structured'))
return ('formula', 'native', 0.95 if structured else 0.60,
        ['docling formula'] + ([] if structured else ['structure NOT validated: label only']))
```

Four regression tests pin it (`tool/tests/test_repair_vi_defects.py`, `class FormulaTrustHole`).

**A convergence worth recording.** A1 gates the exemption on a `formula_structured` flag; A2,
working independently in another worktree, sets `formula_structured` **only** from a validated
structure. **Two lanes arrived at the same contract from opposite ends without coordination.**
The hole is closed **by construction rather than by luck**.

---

## 4. DATA CHANGES — what left the corpus and the packs, and why

| Change | Amount | Rationale |
|---|---|---|
| **Geometry-rebuilt expressions removed from the packs** (fail-closed) | **−41 of 248 activities**; **10 lessons lose their exercise list entirely**; 10 grades byte-identical | The rows are stamped `status: 'INFERRED'`, `method: 'geometric-fraction-rebuild-v1'` upstream — «dựng từ hình học ⇒ KHÔNG phải nguyên văn» — but shipped carrying a `skillCaseId` as if printed. The pack schema has **no provenance field** and the app **cannot display an INFERRED caveat**, so shipping a caveat the UI cannot show is not a caveat. **Nothing deleted upstream; every drop counted and logged; the rows return when provenance can travel with them.** |
| Colophon rows removed | −8 | correctness |
| One guard fix restoring a region | +1 | **and it was wrong (0/1)** — see `04-…` §1 |
| **Trusted text withdrawn on LS&ĐL 5 by `agree_tones`** | **1,263 → 1,020** book-wide (−243) | The round-4 third signal doing what it was built to do — and the reason round 5's priority is **repair**, not more withholding |
| Grounding integrity repaired | **0.952 → 1.000 across 4,681 spans**, **226 real failures** fixed | including «hình 1a» matching only «hình 1» at scale |
| Near-verbatim SGK test fixtures replaced with invented text | 5 fixtures | Founder rule **D4** |

**Data versioning held.** Every value carries a disposition (ORIGINAL OBSERVATION · REPAIRED
CANDIDATE · VALIDATED REPAIR · TRUSTED · WITHHELD · LEGACY · SUPERSEDED); **no source observation
was overwritten**; the OLD baseline reproduced **three times** field for field.

---

## 5. PACK / SNAPSHOT ARCHITECTURE — discipline enforced in code, not in prose

`packs.py` now guarantees:

- a snapshot **never overwrites**;
- a **rebuild refuses** unless a snapshot matches the packs on disk by **sha256**;
- a **restore re-checks every hash**.

Three snapshots under `poc-out/round5/legacy/` — `packs-before-round5`, `-before-inferred-fix`,
`-before-a1` — each with `SHA256SUMS`, full `buildProvenance`, baseline metrics, pipeline version
and a README.

**Result:** pack `verify` **0/12 FAIL → 12/12 PASS**; the provenance rebuild's **content delta was
exactly zero** (248/248 unchanged, 12/12 hashes identical), confirmed by byte-comparing canonical
JSON **independently of the tool**. The zero delta has a cause worth stating: `range_mismatch` is
**counted, never dropped**, so `capped-toc-v2` can only change the diagnosis, not the output.

---

## 6. ARCHITECTURE PRECEDENTS ADOPTED ECOSYSTEM-WIDE

1. **No constructor from a presentation form.** `MathExpression` has `from_json` but
   **deliberately no `from_latex`**; `latex` and `text` are computed properties with no setter.
   A rendering string cannot become structure, so **model-generated LaTeX cannot launder itself
   into truth**. Routed to E1 (SemanticClaim) and E2 (VisualSpec) as a rule: **any
   `from_<rendered>` factory in the semantic layer is the hole through which unvalidated content
   becomes trusted.** Related: `3×10°` has **no representation at all** in the AST — there is no
   degree node — so the impossible transformation is *impossible*, not merely flagged.
2. **Identity redaction at the render boundary.** `VisualRenderContext` replaces each `blockIds`
   value with an opaque handle (`h0`, `h1`, …) and keeps the map itself; `pageOf` / `openSource`
   resolve handles. **The artefact on disk keeps the real block ids** — that chain must stay
   auditable. A renderer no longer *should not* read identity; **it has nothing left to read.**
   Verified by mutation.
3. **Every provenance-bearing type needs a round-trip test asserting grounding never
   strengthens.** Serialisation is a provenance-laundering channel — proved by a real regression
   (`inheritedFromEntity` → `cellStated` across a save/load).
4. **Explanations key on the rule id, never the type.** A sentence can be true in type and false
   in content, and no test catches it.
5. **A plugin loader must fail loudly.** Registration by import side effect silently returns an
   empty list after a registry reset; `load_plugins` now verifies its manifest against the
   registry and raises `RegistrationIncomplete`.

---

## 7. THREE PLANNED SUBSYSTEMS REMOVED BY EVIDENCE

E1's census refuted them rather than descoping them:

| Planned | Verdict |
|---|---|
| `ToánGraph` | **unnecessary** — what is per-domain is **notation** (MATH_AST), not subject |
| `HistoryGraph` | **unnecessary** — `Event` + `atTime` already carried LS&ĐL at **7/7** |
| `ScienceGraph` | **unnecessary** — the core primitives sufficed |

Also **absent from the core** and therefore not needed to represent what a lesson *contains*:
`Method`, `SkillCase`, `CurriculumEdge`, `ConceptMap`.

**What E1 says must change instead, all of it outside the ontology:** claim-bearing
`SemanticData` (today the base carries **no `Provenance`**, so `citableAsTextbookFact` is
undecidable for everything on Trực quan) · a bridge carrier for validated structured nodes **plus
a per-block failure mode** · the four subtypes move to the visual side · a **semantic-yield
gate** · and `khtn6_bai17.dart`'s **122 hardcoded `const` lines** become versioned data +
compiled artefacts + a ~10-row rule registry + a small curated overlay.

---

## 8. THE FORWARD-COMPATIBILITY CONSTRAINT NOBODY HAD WRITTEN DOWN

`lib/core/lesson_model/lesson_document.dart:1017-1018` — `if (blk == null) return null;
// một block hỏng ⇒ không tài liệu nửa vời` *(PROVEN — re-read by the archive builder)*.

This is **deliberate fail-closed design, documented at `:9`**, not a defect. Its consequence had
not been stated before this round:

> **A pack that emits a new block kind blanks the lesson on an older app. Packs and app must ship
> together.**

That single line constrains every future pipeline change that wants to introduce a block kind —
including the `formula` carrier that a validated `MathExpression` needs.

---

## 9. WHAT DID **NOT** CHANGE — and why that is correct

- **No production trust threshold.** `THRESHOLDS.json` still does not exist. A3 built the
  instrument and the curve and **chose no point**, deliberately.
- **No architecture fork.** E1's GO WITH ARCHITECTURE CHANGE is a **recommendation**, filed with
  its evidence, not executed.
- **No destructive migration.** Every removal is fail-closed and reversible; nothing was deleted
  upstream.
- **No universal rule accepted from a single lesson.** Lane C's two rules stayed **PROPOSED and
  History-only**; nothing entered the universal bridge.
- **No LLM in the app, and none in the corpus.** A4 measured the LLM and confined it to
  **detector only**; E1 called none at all; E2 enforces **0 runtime model calls** by an import-set
  test.
