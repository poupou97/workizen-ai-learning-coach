# VISUAL-SPEC v1 — the intermediate representation, as it settled (Lane E2, round 5)

**READY FOR FOUNDER REVIEW — nothing merged.** `lib/core/visual_spec/**` ·
`lib/features/lesson_workspace/visual_grammar/**` · 48 lane tests · full suite
**968 passed / 42 skipped / 0 failed** · `flutter analyze` clean.

> **BAD:** `if lesson == "KHTN6_BAI17": draw_process(...)`
> **GOOD:** `ProcessVisualSpec → ProcessRenderer`

The design rule I held to: *the renderer must not be able to know which lesson it is drawing.*
Not "must not check" — **must not be able to**. `VisualSpec` carries no `book`, no `lessonNo`,
no `slotKey`; `VisualRenderContext` carries no `LessonDocument`. There is nothing to compare
against, so the anti-pattern cannot be typed. Two tests scan the source and fail the build if
either fact stops being true.

## The shape

```
VisualSpec { specVersion, primary: VisualSection, secondary: [VisualSection], compiledBy }
  VisualSection { id, family: String, title, titleProvenance,
                  nodes[], edges[], groups[], ordering[], emphasis[],
                  trust, childSummary }
    VisualNode { id, label?, detail?, badge?, status, provenance, confidence? }
    VisualEdge { fromId, toId, label?, kind, status, provenance }
    VisualGroup{ id, label, nodeIds[], axis: row|column|cluster, provenance? }
      ProvenanceRef { blockIds[], derivationRule, trust, claimId?, charSpan? }
```

Five decisions worth defending, and one thing I deliberately did **not** build.

**1 · `family` is a string, not an enum.** This is the whole difference between a list of four
pictures and a language. Today a fifth family means editing a `sealed class` in `core/` and four
exhaustive `switch`es in three files. Here it is one entry in `visual_registry.dart`.

**2 · `InferenceStatus` on every node and edge — and the compiler *verifies* it.**
`stated` · `derivedDeterministic` · `inferred` · `withheld`. The compiler does not trust the
semantic layer's word: it reads the source block's text and checks whether the label is actually
in it (`isVerbatimIn`, tone-preserving — «phẫu» ≠ «phễu», per round 4 §5b). A label that is not
in the book's own words is marked `inferred` and the child is told so, next to the text.
A sequencing arrow is **never** `stated`: the book prints steps adjacently; the arrow is SAM's
arrangement.

**3 · `blockIds` is a list.** A relation is routinely stated across two blocks. The old
`ConceptRelation.sourceBlockId` could hold one, so half the source was dropped.

**4 · Absence has two different meanings and two different encodings.** In a grid
(`axis: row` × `axis: column`), a **missing node** means *the book does not say*; a node with
`status: withheld` means *SAM could not read it*. Collapsing those two into one blank is the
kind of small lie this lane exists to prevent.

**5 · Composition is `primary` + `secondary[]`, and nothing more.** A lesson needing Timeline +
CauseEffect + hierarchy gets three sections with a stated primary. I did not build a layout
language, nesting, or cross-section links — the real lessons have not asked for them yet.

**Not built: `ConceptMapRenderer`.** The Founder's own baseline says ConceptMap has a renderer
and **zero producer**. Building a second one would be building for data that does not exist.
The compiler emits `conceptMap` sections and the registry has no binding for them, so the app
fails closed with «SAM có dữ liệu … nhưng chưa biết vẽ thành hình» — which is true, and visible.

## Identity leaks through values, not field names

The first version of this document claimed the anti-pattern was *untypable* because `VisualSpec`
has no `book` / `lessonNo` / `slotKey` field and `VisualRenderContext` carries no
`LessonDocument`, both pinned by source scans. **That claim was nominal.** Lane E1's guard work
surfaced the channel both lanes had missed, and an audit of all 5 built specs confirmed it here:
every element a renderer holds carried

    06-sgk-khoa-hoc-tu-nhien-6:p062:synthetic:015

in `ProvenanceRef.blockIds` — on nodes, edges, groups and `titleProvenance` alike. One
`startsWith` and a renderer branches on lesson identity while every field-name guard stays green.

**Fixed structurally.** At the render boundary, `VisualRenderContext` replaces each `blockIds`
value with an opaque handle (`h0`, `h1`, …) and keeps the handle→ref map itself; `pageOf` and
`openSource` resolve it. The renderer does not *refrain* from reading identity — it has nothing
left to read. The artefact on disk keeps the real block ids, because the provenance chain must
stay auditable; only the renderer's view is redacted.

Verified by mutation: disabling the redaction fails 2 of the 6 guard tests. The suite also pins
that the leak still exists in the artefact (so the guard cannot go vacuous) and constrains
compiler-minted ids by **shape**, closing a second latent channel — `VisualSection.id` is copied
from `SemanticData.id`, so an upstream `khtn6-bai17-process` would otherwise flow straight
through.

**One channel remains open by necessity, and is not a defect:** `title`, `label`, `detail` and
`badge` carry the book's own words, which may say «Bài 22». That is *content the child reads*,
not an identifier — it cannot be redacted without deleting the lesson from the screen.

## No constructor from a presentation form

Lane A2's precedent (PR #84): `MathExpression` has `from_json` and deliberately no `from_latex`.
The same hole exists one layer up. There is no `VisualSpec.fromSvg`, `.fromMermaid`,
`.fromMarkdown`, `.fromRendered…` — a string meant for drawing must never become structure,
because that is exactly how unvalidated content launders itself into "a diagram with a source".
`no_presentation_constructor_test.dart` scans for it and fails the day one appears.

The same test pins the **import set** of `lib/core/visual_spec/**` to `lesson_model` plus
`dart:convert`. That is what makes "0 runtime model calls" unwriteable rather than promised:
adding one would require adding an import, and the test names it.

## Versioned separately from the lesson pack — on purpose

`LessonDocument.fromJson` is a sealed union that rejects the **whole document** on an unknown
block kind. So a new visual family shipped inside a pack would blank the lesson on an older app.
This lane therefore adds **no block kind**. Specs live in their own artefact with their own
version; an unknown family costs the picture, never the lesson. Lane B and Lane D can ship the
spec artefact and the app independently.

## Precompute — measured, not asserted

`dart run tool/visual_spec/build_specs.dart`

| measure | value |
|---|---|
| runtime model calls | **0** — enforced by the import-set test, not by policy |
| artefact | 5 specs · 6 sections · **19,289 bytes** (~3.9 KB/lesson) |
| deterministic replay | two independent builds are **byte-identical** (`cmp`) |
| cacheability | one file, content-addressable; `builtAt` is fixed so the artefact hashes stably |
| runtime cost | parse + render only; no I/O per element, no per-frame lookup |
| fail-closed load | one bad spec rejects the **whole** artefact — half an artefact silently missing pictures is the worse failure |

Denominator note (per D5): 5 specs is against **48 documents read on this machine**, not against
3,679 canonical or 3,381 ranged. It is a POC count and nothing else.

## Human correction (§22) — the surface is the claim, never the pixels

Every learner-visible element resolves to `blockIds` + `derivationRule` + `status`, so a wrong
picture is always traceable to one of four causes, each with a different fix **upstream**:

| What is wrong | What gets edited | Who owns it |
|---|---|---|
| A relation the book never states | the **edge** — delete it, or set `status: inferred` | semantic graph (E1 / A / C) |
| The wrong kind of picture | `VisualSection.family` | the compiler's family choice |
| A missing event or step | add a **node with a `sourceRef`** — a node without one cannot be added; the parser rejects it | semantic graph |
| A right relation explained wrongly to the child | the **rule's entry** in `derivation_lexicon.dart` | this lane |

Then the artefact is rebuilt and the renderer regenerates. Three properties make this a
workflow rather than a wish: the compiler is **deterministic** (a rebuild changes only what the
edit changed), the artefact is **separate from the pack** (a correction does not touch shipped
lesson content), and a correction **cannot invent** — `VisualSpec.fromJson` rejects any node
without provenance, so "add a node" always means "add a node plus its source block".

**No CMS.** The bounded workflow is: edit the semantic structure (JSON, reviewed like code) →
rebuild → diff the artefact → the diff is the review surface. A Flutter screen is never the
correction surface, because a pixel edit cannot carry a `sourceRef`.

## Mounting it (Lane B, six lines, no file of theirs changed)

```dart
VisualSpecView(
  spec: spec,                                    // from the artefact
  pageLabel: (id) {                              // machine id → child words
    final b = doc.blockById(id);
    return b == null ? 'sách' : doc.sourceLineForBlock(b);
  },
  onOpenSource: (ref) => showSourceSheet(context, doc: doc,
      block: doc.blockById(ref.primaryBlockId)!, onShowInRead: …),
)
```

**Suggested fallback for regions this lane cannot draw natively** (formula, table, diagram —
which the gold adapter already marks `withheld`): the existing **page crop** in
`withheld_card.dart` already renders to the child today *with provenance*, and needs no new
dependency. The spec carries `blockIds`, so the host can resolve a withheld node to its crop.
That path is Lane B's to wire; this lane deliberately did not reach into it.
