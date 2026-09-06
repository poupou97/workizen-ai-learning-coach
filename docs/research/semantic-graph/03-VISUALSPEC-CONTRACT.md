# Lane E1 → Lane E2 · the VisualSpec contract (v0)

**Status: PROPOSED, for Lane E2 (`e2/round5-visualspec-renderer`) to consume and push back on.**
Implementation: `tool/semantic/visualspec.py`. Live examples:
`poc-out/round5/semantic/poc/<pipeline>/<book>/bai-<n>.<family>.visualspec.json`.

---

## 1. §15 — Activity Patterns ≠ Visual Patterns

The repo already has a **27-pattern activity registry** (`docs/research/K12-ACTIVITY-PATTERN-REGISTRY.md`,
`tool/corpus/fable_activity_taxonomy.py`). It classifies **what the learner is asked to do**:
EXPLAIN_SHORT, ORAL_SHARE, OBSERVE, SELECT_MCQ, DRAW_CREATE…

A **visual family** classifies **what the content IS**: an ordered procedure, a dated sequence, a
part/whole nesting, a figure with callouts.

They are different axes and **27 activity patterns must never become 27 renderers**:

- One activity pattern maps to several families — `OBSERVE` (352 lessons) lands on
  LABELED_FIGURE, on COMPARISON, or on nothing, depending on what the page shows.
- One family serves many activity patterns — PROCESS renders for EXPERIMENT, for
  DIAGRAM_COMPLETE and for a plain expository procedure.
- Some activity patterns have **no** visual family at all (ORAL_SHARE, RESEARCH_PROJECT) and must
  not acquire one for symmetry's sake.

The registry is a good input to *which families to build first*. It is not a renderer list.

---

## 2. The object

```jsonc
{ "schema": "visual-spec/v0",
  "family": "PROCESS",              // one of the families below
  "layout": "sequence",             // sequence | grid | rail | tree | hubSpoke |
                                    // figureAnchored | cards
  "title":  "Các bước — theo thứ tự sách in",
  "compiler": "compileProcess@v0",  // which projection produced this
  "lesson": { "book": "...", "lesson": 17, "title": "...", "subject": "...", "grade": 6 },
  "elements": [ /* VisualElement */ ],
  "counts": { "elements": 8, "drawable": 8, "gaps": 0 },
  "trust": {
    "chipRequired": true,
    "reason": "no production trust gate exists (THRESHOLDS.json absent), so
               ContentTrust.trustedCorpus is unreachable by construction",
    "allElementsValidated": false,
    "contentTrustCeiling": "trustedStructuredLesson" },
  "lineage": [ /* one row per element — see §4 */ ] }
```

```jsonc
// VisualElement
{ "id": "step:...|0|1#n1",
  "role": "node",                   // node | edge | cell | header | label | gap
  "status": "proposed",             // proposed | validated | conflict | withheld | superseded
  "claim": "cl:8f2a…",              // REQUIRED for every role except `gap`
  "text": "· Gấp giấy lọc và đặt vào phễu (Hình 17.3).",
  "slot": { "group": 0, "order": 2 } }
```

**Renderer-agnostic on purpose.** No widget, no colour, no font, no pixel, no coordinate. `slot`
carries *relational* placement (order, group, row/col, depth, anchor, page geometry when the
evidence is a page region). How that becomes layout is entirely Lane E2's.

---

## 3. Five rules the renderer must hold

1. **No element without a claim.** Every drawable element names the `claim` it came from; a
   `VisualElement` with `role != "gap"` and no claim raises at construction time. A renderer that
   draws something not in `elements` is drawing something the source does not support.
2. **Status is not decoration — it gates.** `proposed` is a **TRACE**, not evidence. Only
   `validated` may be presented as what the book says. Today **every** element is `proposed`, so
   the honest presentation for v0 is "SAM sắp xếp theo sách, chưa kiểm định", never "sách viết".
3. **Never serve a mutilated structure.** Round 5's defect 8: withholding one option of a
   multiple-choice question leaves the *served* question wrong, not merely smaller. So a compiler
   emits a **`gap`** element where a member of an ordered structure is withheld, and the renderer
   **must draw the gap**. Silently omitting it is the teaching-critical failure the safety
   mechanism itself creates. (v0 compilers emit 0 gaps because they only read trusted blocks —
   this rule is the contract for when they read withheld ones, which is the correct fix for
   defect 8 and is not yet implemented.)
4. **The chip is not optional.** `trust.chipRequired` is `true` for every spec that can exist
   today, and `contentTrustCeiling` is `trustedStructuredLesson`. Removing the chip needs two
   separate Founder decisions (G1 thresholds + D4 licence). A renderer must not have a code path
   that omits it.
5. **Tapping an element must reach the print.** Every element's lineage row carries
   `sourceRef.pagePrinted` **and** `pagePdf` — they differ (Bài 8: PDF 39 = printed 37) and using
   the wrong one cites the wrong page to a child.

---

## 4. Lineage — what E2 gets for free

One row per element, already computed:

```
visualElement → claim → claimStatus → support (KnowledgeOrigin) → derivation (rule id)
              → sourceBlocks[] → sourceSpans[] → sourceRef[]{book,pagePdf,pagePrinted,bbox}
              → trustedLearningSource{trust[], gate}
```

This is what lets the trust sheet answer «vì sao SAM vẽ thế này» with a rule id and a page
instead of a slogan — and it is what `SemanticData` cannot do today, because it carries no
provenance at all (its leaf elements carry a bare `sourceBlockId`, and `ComparisonDimension`
carries nothing).

---

## 5. ⭐ Family frequency — INTERIM, publish-early per the brief

**This table is deliberately partial and will change.** It exists because E2 must choose 4–6
families now. Full census with tiers and denominators is P0.3 (`06-CENSUS.md`).

Two independent signals, kept apart because they have different denominators and different
meanings:

**(a) Cue frequency — how many lessons *talk like* a family.**
Denominator: **1,906 lessons that have role-tagged units** in `poc-out/units-k12/` (SGK only).
This is *not* 3,679 and must never be written as `/3,679`. A cue match is a hypothesis about the
content; it is not extractability.

| family | cue | lessons | % of 1,906 | subjects | books |
|---|---|---:|---:|---:|---:|
| LABELED_FIGURE | `hình` | 1,613 | 84.6 | 24 | 188 |
| HIERARCHY | `gồm` / `thuộc nhóm` / `bao gồm` / `phân loại` | 826–872 | 43–46 | 23 | 163–187 |
| COMPARISON | `khác nhau` / `so sánh` / `phân biệt` / `giống nhau` | 184–794 | 9.7–41.7 | 21–23 | 104–167 |
| CAUSAL | `kết quả` / `vì sao` / `nguyên nhân` / `dẫn đến` | 249–741 | 13–39 | 20–23 | 86–140 |
| DEFINITION | `gọi là` / `là gì` / `khái niệm` | 387–617 | 20–32 | 21–22 | 122–136 |
| SPATIAL | `vị trí` / `bản đồ` / `lược đồ` | 59–627 | 3–33 | 7–22 | 14–165 |
| PROCESS | `chuẩn bị` / `sau đó` / `các bước` / `tiến hành` / `bước 1` | 351–502 | 18–26 | 18–23 | 100–153 |
| QUANTITY | `đơn vị` / `công thức` / `phương trình` | 102–482 | 5–25 | 10–24 | 36–184 |
| TIMELINE | `năm <YYYY>` / `thế kỉ` / `TCN` | 37–168* | 2–9 | 9–15 | 27–62 |

\* A bare `năm` hits 49.5 % and is a **false friend** — it also means "five". Only a year counts.

**(b) Compiled families — how many lessons a family can actually be BUILT for.**
Denominator: **3 lesson-builds** (the checkpoint). Far too small to rank on; shown so the two
signals are never confused.

| family | compiled on | notes |
|---|---|---|
| HIERARCHY | 3 / 3 | from the printed heading nesting — the most robust signal found |
| DEFINITION | 3 / 3 | precision unmeasured; `X là Y` over-fires (see `05-KNOWN-DEFECTS.md`) |
| PROCESS | 1 / 3 | needs a procedural governor; one tone slip removes it |
| LABELED_FIGURE | 1 / 3 | needs a printed figure label block AND prose naming it |
| CAUSAL | 1 / 3 | needs an in-block connective |
| TIMELINE | 1 / 3 | and only on one of two builds of the same lesson |

### Recommendation to Lane E2 — build these four first

1. **HIERARCHY** (`tree`) — highest structural yield, grounded in heading nesting the book
   actually prints, works on every lesson tested, cross-subject. **No renderer exists today.**
2. **PROCESS** (`sequence`) — a renderer already exists (`visual_view.dart:396`) and real corpus
   data already reaches it; the E2 work is generalising it off Bài 17's hardcoded explanation
   string (`visual_view.dart:295-311`).
3. **LABELED_FIGURE** (`figureAnchored`) — the largest cue family by a wide margin (84.6 %), and
   the only family that puts the **book's own artwork** into Trực quan, which is precisely the
   round-4 gap («Trực quan is still text where the board is an illustrated mindmap»). Also the
   cheapest: the crops already ship for the Đọc tab (`smart_book_view.dart:531`).
4. **TIMELINE** (`rail`) — a renderer exists (`views/timeline_view.dart:22`) but has only ever
   run on **synthetic** data. The E1 path feeds it **corpus-derived** events for the first time.

**Fifth, if there is room: DEFINITION** (`cards`) — trivial to render, but measure precision
first; it is the family whose extraction is currently weakest.

**Do NOT build CONCEPT_MAP.** A renderer already exists (`visual_view.dart:609`) with **zero
producers**, and the learning-views research explicitly rejects "a generic mindmap of the lesson".
It should be reached by composing typed relations, not by adding a family.

---

## 6. What E1 owes E2 next

- the P0.3 census, which replaces §5(b)'s n = 3 with real per-family lesson counts and tiers;
- `gap`-emitting compilers (defect 8) once withheld regions are read as structure;
- precision numbers per rule, on a holdout the rules were not written against.
