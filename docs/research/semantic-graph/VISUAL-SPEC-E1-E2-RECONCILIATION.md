# VISUAL-SPEC — E1 ↔ E2 interface reconciliation (reported, not resolved)

**Status: CONTRADICTION REPORTED — for the Founder to settle. Nothing merged, nothing silently
forked.** Per the workspace rule: when two lanes disagree, report it and propose a
reconciliation; do not resolve doctrine unilaterally.

Lane E1 published `docs/research/semantic-graph/03-VISUALSPEC-CONTRACT.md` (schema
`visual-spec/v0`, producer, Python) while Lane E2 built `visual-spec-v1` (consumer, Dart).
**These are two different objects with the same name.** They agree on far more than they
disagree on, but they must be made one before either ships.

## Where they already agree (no action needed)

| Rule | E1 | E2 |
|---|---|---|
| No drawable element without a source | rule 1 — `claim` required | `ProvenanceRef` required; parser rejects a node without it |
| A withheld member must be *drawn as a gap*, never omitted | rule 3 (`role: gap`) | `InferenceStatus.withheld` node, rendered as a real gap with a page reference |
| The trust chip is not optional | rule 4 | **fixed in this PR** — see below |
| Tapping must reach the **printed** page, not the PDF page | rule 5 | `pageLabel` resolves through `sourceLineForBlock`, which prefers printed |
| Do **not** build CONCEPT_MAP | §5 | not built; the app fails closed with a true sentence |

**One real defect E1's contract caught in E2's work, now fixed:** `VisualSpecView` rendered no
trust chip at all. It now renders `fixtureChipLabel(spec.trust)` unconditionally, reading the
**weakest** trust across primary *and* secondary sections, with three tests — including a source
scan proving there is no parameter that could disable it.

## Disagreement 1 — lesson identity inside the spec (**the one that matters**)

E1's object carries `"lesson": {"book": …, "lesson": 17, "title": …, "subject": …, "grade": 6}`.

E2's carries none of it, deliberately: if `spec.lesson.lesson == 17` is reachable from a
renderer, then `if lessonId == BAI17` is typable again, and the named anti-pattern is back —
enforced only by discipline rather than by the type system.

**Proposed reconciliation:** lesson identity lives in the **artefact envelope**
(`VisualSpecArtifact.specs` is keyed `book#lessonNo`), never in the object handed to a renderer.
E1 keeps the field for its own tooling and file naming; the renderer-facing object drops it.
This costs E1 nothing and preserves the guarantee.

## Disagreement 2 — two `status` vocabularies that are actually two axes

| | E1 | E2 |
|---|---|---|
| field | `status: proposed \| validated \| conflict \| withheld \| superseded` | `status: stated \| derivedDeterministic \| inferred \| withheld` |
| question answered | *has this claim been validated?* | *how does this visual element relate to the source text?* |

They are **orthogonal, and both are needed.** An element can be `validated` yet `inferred`
(a true relation the book never writes as one sentence), or `proposed` yet `stated`
(verbatim book text nobody has checked yet).

**Proposed reconciliation:** carry both — E1's as `claimStatus`, E2's as `inferenceStatus`.

⚠️ **Read E2's `stated` narrowly.** It means *this label is verbatim in its source block*, a
textual fact the compiler verifies by reading the block. It does **not** mean validated, and it
must never be rendered to a child as «sách viết» while E1's rule 2 holds that every element is
`proposed`. That is exactly why the trust chip is now unconditional.

## Disagreement 3 — `PROCESS` + `layout` vs `process` / `sequence` as separate families

E1 has one family axis plus a `layout` axis: `family: PROCESS, layout: sequence`.
E2 has two families served by **one renderer**: `process` (do these in this order) and
`sequence` (the book prints these in this order).

The split is not cosmetic. E2's `numbered-section-sequence-v1` measured **3 of 6** hits on gold
pages as teacher-book material, one of which («1. KIẾN THỨC · 2. KĨ NĂNG · 3. PHẨM CHẤT») is a
competency list where order carries no meaning. Calling that a PROCESS would tell a child to do
it in order. The `sequence` family exists so the child-facing sentence can be weaker than the
layout.

E1's own commit `3124de8` — *«an enumeration is not a procedure»* — reaches the same conclusion
independently, which is good evidence the distinction is real.

**Proposed reconciliation:** keep the distinction at the family level (E2's shape), and let
`layout` stay E1's free axis. Two families, one renderer, is already proven.

## Disagreement 4 — flat `elements[]` vs typed `nodes / edges / groups`

E1: one flat list, `role: node|edge|cell|header|label|gap`, placement in `slot{group, order}`.
E2: typed lists, plus `ordering`, `emphasis`, and `groups.axis: row|column|cluster`.

E1's is the better **wire format** (renderer-agnostic, easy to emit). E2's is the better
**renderer input** (an edge pointing at a non-existent node is rejected at parse; a grid cell is
the intersection of a row and a column, so a *missing* cell means «sách không nói» while a
`withheld` node means «SAM chưa đọc được» — two different truths that a flat list collapses).

**Proposed reconciliation:** keep both and write one adapter, `visual-spec/v0 → visual-spec-v1`,
~80 lines. E2's `ProvenanceRef.claimId` already exists precisely to carry E1's `claim`.
Trivial mapping: family case (`PROCESS` ↔ `process`) — settle on lowerCamel.

## What E1's interim census changes for E2's next renderers

E1 ranks, against a stated denominator of **1,906 role-tagged lessons** (never `/3,679`):
**HIERARCHY** (43–46 %, no renderer exists) → **PROCESS** (18–26 %, built here) →
**LABELED_FIGURE** (84.6 % cue, and the only family that puts the book's own artwork into Trực
quan — the round-4 gap) → **TIMELINE** (2–9 %, a renderer exists but has only ever run on
synthetic data).

E2 built PROCESS/`sequence` and correctly skipped CONCEPT_MAP. **HIERARCHY and LABELED_FIGURE
are the census-justified next two**, and neither is speculative work now. LABELED_FIGURE is also
the cheapest: `withheld_card.dart` already renders page crops to a child **with provenance**, and
needs no new dependency.

## Requested decision

1. Does lesson identity leave the renderer-facing object? (E2 recommends **yes**.)
2. Are both status axes carried? (E2 recommends **yes**, renamed `claimStatus` +
   `inferenceStatus`.)
3. Is `sequence` a family distinct from `process`? (E2 recommends **yes**; E1's own
   «an enumeration is not a procedure» commit agrees.)
4. Who owns the v0 → v1 adapter, and does it live in `tool/` (build time) or `lib/` (load time)?
   E2 recommends **build time**, so the app only ever parses one schema.
