# Lane E1 · §27 EARLY FOUNDER CHECKPOINT — `SOURCE → SEMANTIC → VISUAL SPEC → DEVICE/UI`

**READY FOR FOUNDER REVIEW — nothing merged.** Branch `e1/round5-semantic-foundation`, base
`integration/round5-2026-09-06`. Research + tooling only; `lib/**` untouched.
Tool suite **271 tests, OK (1 skipped)**.

Published early and deliberately rough, per §27 and §32: the semantic foundation and the
provenance bridge come **before** the census, and Lane E2 needs the VisualSpec contract now
rather than a perfect one later.

---

## 1. What is proved, in one line each

| Claim | Verdict | Evidence |
|---|---|---|
| One extractor can build a semantic graph for **two different subjects with no subject branch** | **PROVEN (n = 2 lessons)** | `tool/semantic/extract.py`; asserted by a test that parses the AST, strips comments and fails on `subject ==` / `book ==` / `khtn` / `lich-su` |
| Visual families are **compiled projections** of one graph, not separate data models | **SUPPORTED (n = 6 compilers)** | `compiler_audit()` measured at runtime: every compiler read only `nodes` / `relations` / `claims` |
| A relation can be **grounded in the text that asserts it**, not in its endpoints | **PROVEN** | `causes` edges carry the connective span; a `causes` with no connective is not emitted |
| A semantic object can carry provenance strong enough to decide **«may SAM say “sách viết…”?»** | **PROVEN** | `provenance_of()` projects a claim into the existing `Provenance` shape; `citableAsTextbookFact` becomes computable — today it is not, because `SemanticData` carries no provenance at all |
| The generic rule reaches a **hand-checked** result without being tuned to the lesson | **PROVEN (n = 1)** | `e1-prose-dated-events-v1` extracts **7/7** dated events on LS&ĐL 5 Bài 8, matching Lane C's hand-checked 7/7 — and the same rule runs on Science, where it correctly yields 0 |
| Anything here is **learner-ready** | **NO — 0, by construction** | `learnerVisible = 0` on every lesson: no validator ran, so no claim is `validated`. `THRESHOLDS.json` still does not exist |

---

## 2. The end-to-end path, on real corpus data

One extractor, one set of compilers, run over **two subjects in two books**:

```
SOURCE                     SEMANTIC                          VISUAL SPEC
Trusted Structured    →    SemanticGraphCandidate       →    VisualSpec (per family)
Lesson (TSL block)         nodes · relations · claims        elements + lineage
```

| | KHTN 6 · Bài 17 (tc2-p1) | LS&ĐL 5 · Bài 8 (tc2-p1) | LS&ĐL 5 · Bài 8 (tc2-r5) |
|---|---|---|---|
| source blocks (trusted) | 60 | 34 | 36 |
| withheld regions | 4 | 17 | 15 |
| **nodes** | 43 | 21 | 12 |
| **relations** | 30 | 10 | 6 |
| **claims** | 68 | 36 | 18 |
| claims citable as textbook fact | 48 | 29 | 13 |
| **claims learner-visible** | **0** | **0** | **0** |
| primitives | Statement 20 · Step 5 · Entity 14 · Figure 4 | Statement 5 · Entity 9 · **Event 7** | Statement 5 · Entity 7 |
| relations | next 11 · hasPart 14 · depicts 2 · causes 2 · hasProperty 1 | next 2 · hasPart 7 · hasProperty 1 | next 2 · hasPart 3 · hasProperty 1 |
| **families compiled** | PROCESS · HIERARCHY · LABELED_FIGURE · CAUSAL · DEFINITION | **TIMELINE** · HIERARCHY · DEFINITION | HIERARCHY · DEFINITION |

Outputs (gitignored, D4): `poc-out/round5/semantic/poc/<pipeline>/<book>/bai-<n>.{graph,<family>.visualspec}.json`.
Reproduce with `python3 tool/semantic/run_poc.py`.

### One lineage row, verbatim from the output

```json
{ "visualElement": "evt:Hai Bà Trưng|40 - 43#t0",
  "claim": "cl:c8066b37d399020b",
  "claimStatus": "proposed",
  "support": "sourceStated",
  "derivation": "e1-prose-dated-events-v1",
  "sourceBlocks": ["05-sgk-lich-su-va-dia-li-5:p039:tc2-p1:000"],
  "sourceSpans": [{ "start": 0, "end": 22 }],
  "sourceRef": [{ "book": "05-sgk-lich-su-va-dia-li-5", "pagePdf": 39,
                  "pagePrinted": 37, "bbox": [0.0755, 0.0683, 0.835, 0.08] }],
  "trustedLearningSource": {
    "trust": ["trustedStructuredLesson"],
    "gate": "NONE — THRESHOLDS.json does not exist; trusted computes to 0" } }
```

That is the whole §6 chain as data: **visual element → claim → status → derivation rule →
source block → character span → page (both numberings) → bbox → trust → and an honest
terminus saying no gate exists.**

Note where this row lives: on the **lineage artefact**, not on the spec. The renderer receives
`to_json()`, which carries no `book`, no `lesson`, no page and no subject at any depth — see
`09-E2-RECONCILIATION.md` §1. The element id above is the reason that reconciliation matters: it
used to read `evt:05-sgk-lich-su-va-dia-li-5|8|Hai Bà Trưng|40 - 43#t0`, so a renderer could have
recovered the lesson by parsing a string, through a door that field-level guards do not watch.

---

## 3. The finding the Founder should see first

> **A visual family can be destroyed by the source pipeline, with no semantic rule at fault.**

The same lesson (LS&ĐL 5 Bài 8), the same rules, two pipeline builds:

| build | blocks | Event nodes | TIMELINE compiles? |
|---|---|---|---|
| `tc2-p1` (round 4) | 34 | **7** | **yes** |
| `tc2-r5` (round 5) | 36 | **1** | **no** |
| `tc2-p2` / `tc2-p3` (round-5 legacy) | **6** | 0 | no |

The single block `…:p039:tc2-p1:000` carries **all seven** of the lesson's dated events. In the
round-5 builds it is not present as a trusted block. A round-5 build has **more** trusted blocks
overall (36 vs 34) and **fewer** visual families, because block counts and semantic yield are not
the same quantity.

**Consequence for the roadmap:** «coverage», «false trust» and «blocks served» do not predict
whether a lesson can be visualised. If a pipeline change is judged only on the DATA ACCURACY
SCOREBOARD, it can silently delete the visual layer. Round 5 needs a **semantic-yield regression
check** beside the accuracy one. Lane E1 can supply it — `run_poc.py` already computes it per
lesson — but it must run on every pipeline change, which is A1's and D's territory, not E1's.

### And a second, smaller one with the same shape

Bài 17's filtering procedure is governed by a block reading **«Chuẩn bị: … Tiền hành:»** — OCR's
version of «Tiến hành». Round 4 lists this exact slip among the four that survive *because both
OCR stacks make the same error*. Matching the accented spelling only, the lesson yields **zero**
Step primitives and loses PROCESS entirely. Comparing tone-stripped restores it (0 → 5 Steps).

**One tone slip can delete a whole visual family.** That raises the stakes of Lane A1's Vietnamese
fidelity work beyond display fidelity: it is a structural dependency, not a cosmetic one.

---

## 4. What is deliberately NOT claimed

- **Nothing is learner-ready.** Every claim is `proposed`. `learnerVisible = 0` on all three runs.
- **n = 2 lessons.** The reuse claim is proved on two subjects, not on K-12. The census (P0.3)
  is what turns this into a rate, and it will keep REPRESENTABLE / EXTRACTABLE / GROUNDABLE /
  VALIDATABLE / VISUALIZABLE / LEARNER_READY as **separate** counts.
- **No renderer.** Lane E2 owns that. This lane produces the spec; §5 of
  `03-VISUALSPEC-CONTRACT.md` is what E2 consumes.
- **Precision is measured, not assumed.** Known false positives are recorded in
  `05-KNOWN-DEFECTS.md` rather than tuned away.
- **No LLM was called anywhere in this lane.** Every rule is a deterministic regex over trusted
  blocks, and every claim names the rule id that produced it.

---

## 5. Where the rest lives

| Document | Answers |
|---|---|
| `01-AUDIT-CLASSIFICATION.md` | the audit table; §10 KEEP / EVOLVE / ADAPT / DEPRECATE; the bridge gaps |
| `02-SEMANTIC-FOUNDATION.md` | §5 `SemanticClaim`, §6 the provenance bridge, §7 `SourceGrounding`, the enum delta |
| `03-VISUALSPEC-CONTRACT.md` | what Lane E2 renders, and the family-frequency table it needs |
| `04-BAI17-REPLACEMENT.md` | §24 what replaces `khtn6_bai17.dart` and the one-row registry at K-12 scale |
| `05-KNOWN-DEFECTS.md` | every defect found, including the ones still open |
| `06-CENSUS.md` | P0.3 — the 3,679 census with tiers and denominators |
