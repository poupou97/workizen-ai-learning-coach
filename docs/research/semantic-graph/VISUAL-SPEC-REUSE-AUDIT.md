# VISUAL-SPEC — reuse audit of today's Visual layer (Lane E2, round 5)

**READY FOR FOUNDER REVIEW — nothing merged.** Audited at `integration/round5-2026-09-06`
(`b6f7fef`): `lib/features/lesson_workspace/visual_view.dart` (883 lines, Lane B),
`views/timeline_view.dart` (374 lines, Lane C), `lib/core/lesson_model/semantic_data.dart`
(322 lines). *Reuse before adding* — this is what can be lifted, what cannot, and why.

## Headline

**The good news first, because it is real and it is not what I expected to find: there is no
`if (lesson == …)` anywhere in the Visual layer.** Every branch is on a *data shape*
(`ProcessSemantic`, `ComparisonSemantic`, …), never on a lesson identity. Lesson-specific
knowledge is quarantined in `lib/core/curriculum/khtn6_bai17.dart` behind a registry, on the
**pedagogy** side. The visual layer already obeys the letter of the Founder's rule.

**The bad news is that it obeys the letter and not the spirit.** Three things make today's
layer a *closed list of four pictures* rather than *a language 3,679 lessons compile into*:

| # | Finding | Where |
|---|---|---|
| **1** | The family set is **closed at compile time** — a `sealed class` plus four exhaustive `switch`es across three files. A fifth family means editing core types, not registering a renderer. | `semantic_data.dart:16`, `visual_view.dart:70/262/281/301` |
| **2** | The child-facing explanation is keyed on the **Dart type**, not on the rule that produced the data — so a rule-specific sentence is asserted over every instance of that type. | `visual_view.dart:296–311` |
| **3** | The provenance chain **stops at one block id**, and an inferred relation is indistinguishable from a stated one. | `semantic_data.dart` (`ConceptRelation`, `ComparisonDimension`) |

---

## 1 · Generic — liftable as-is

These are already pure functions of typed data. Lane E2 lifted the *ideas* into the spec-driven
renderer; the code stays where it is (Lane B owns it).

| Piece | Why it is generic |
|---|---|
| `VisualView.shapesOf(doc)` | Derives the tab set from `doc.semantic`. Tabs exist only for shapes the lesson actually has — **the fail-closed default is already right**. |
| `VisualView.hubOf(ConceptMapSemantic)` | Most-frequent entity, ties broken by first appearance. Deterministic, re-checkable, no lesson knowledge. Reused verbatim as the `emphasis` computation in `semantic_to_spec.dart`. |
| `_process`, `_processStrip`, `_processNode` | Pure over `ProcessStep[]`. Withheld steps render as real gaps with a page reference — the honest behaviour, lifted directly. |
| `_comparisonTable` | Pure over entities × dimensions. `null` renders as «— (sách không nói)» rather than being filled in. |
| `_openSource` / `_pageOf` | block id → block → printed-page line. This is the whole provenance plumbing today, and it works. |
| `_ArrowPainter`, `_SpokePainter`, `_TimelinePainter` | Layout only. No content. |
| `TimelineView._addsSomething` | Suppresses a third line that repeats «name + year» — found on the real device in round 4. A *rendering* decision that does not touch data. Lifted into the compiler as `_addsSomething`. |

## 2 · Hardcoded — generic in shape, wrong in the general case

| Piece | What it hardcodes | Consequence |
|---|---|---|
| **`_why(s)`** (`visual_view.dart:296`) | Per-**type** prose describing a specific *rule*. `ProcessSemantic` ⇒ «các bước đánh dấu «·» theo thứ tự»; `ComparisonSemantic` ⇒ «Phần "Em đã học" của sách liệt kê từng cách kèm chú thích trong ngoặc». | The first sentence describes `tsl-enumerated-steps-v1`. The second describes **Bài 17's own «Em đã học» section**. A Process from a numbered Tin học procedure would be told, in a child's words, that the book used bullet marks. **No test catches this: the type is right, the text renders, the sentence is false.** |
| `_subtitle(s)` (`:277`) | Unit nouns per type + the constant tail «chữ sách, SAM chỉ xếp lại». | That tail is a **provenance claim asserted in code**. It renders identically over `fixtureSynthetic` data, where no sentence is the book's. The claim is decoupled from the trust value sitting right next to it. |
| The empty-state copy (`:180`) | «SAM chỉ vẽ sơ đồ khi sách viết rõ **từng bước hoặc từng cách**» | Enumerates exactly the two families Bài 17 has. Timeline has existed since round 4; the sentence has been quietly false ever since. |
| `VisualView.summaryBlocks` (`:47`) | Matches the stage label `em đã học`. | A KHTN-series convention in the **view** layer. Subject-specific, not lesson-specific — but it is a lexicon, and lexicons belong upstream. |
| `TimelineView` labels | «NGUỒN KỂ CHUYỆN», «THỬ XẾP THỨ TỰ» | History-specific framing, and the order exercise fuses a **learning activity** into a renderer. |
| Layout constants | `72.0` row height, `w*0.22`/`w*0.62`, `clamp(96, 720)`, 30-char title truncation | Fine as layout; noted only because they encode an assumption of few, short nodes. |

## 3 · Fixture-specific — text that describes one lesson

- `_why` for Process **and** Comparison, as above. Both describe Bài 17's own page structure.
- `_subtitle`'s «chữ sách» over synthetic fixtures.

## 4 · Lesson-specific — none in the visual layer

Confirmed by grep across `lib/`: no `lessonNo ==`, `slotKey ==`, or `book ==` in any view.
`khtn6_bai17.dart` is a hand-curated **pedagogy** binding reached through
`SemanticBindingRegistry`, i.e. one hand-written Dart file per lesson. That approach does not
scale to 3,679 lessons, but it is not the visual layer's problem and Lane E2 did not touch it.

## 5 · Two defects the audit found in the data path

**5a · Provenance already on disk is thrown away.** The LS&ĐL fixture's timeline events carry
`charSpan`, `yearStart`, `yearEnd`, `era`. `TimelineEvent.fromJson` reads none of them; the app
then **re-parses the year out of the `when` string at render time** (`timeline_date.dart`). The
pipeline computed it, the model dropped it, the UI recomputed it. `ProvenanceRef.charSpan` in
the new spec carries it through.

**5b · A comparison cell could reach a child ungrounded.** `ComparisonDimension.values` was
`List<String?>` — text with no path back to a block. Fixed in this PR (§8): every cell is now
`ComparisonValue{text, sourceBlockId, grounding}`, backward compatible, fail-closed, and
`ComparisonDimension.values` survives as a getter so Lane B and Lane C compile unchanged.

Its own regression test then caught a second bug: a **save/load round trip upgraded a cell's
grounding from `inheritedFromEntity` to `cellStated`** — evidence strengthening itself through
a file write. `grounding` is now serialised and honoured on parse.

## 6 · What this implies for the spec

| Audit finding | Answer in `VisualSpec` |
|---|---|
| Closed family set | `family` is an open **string**; renderers register in a table (`visual_registry.dart`). One entry adds a family. |
| Explanation keyed on type | `derivation_lexicon.dart` keys on the **rule id**, with a generic fallback that asserts nothing about how the book is laid out. |
| One block id per element | `ProvenanceRef.blockIds` is a **list**, plus optional `charSpan` and `claimId`. |
| Stated vs inferred indistinguishable | `InferenceStatus{stated, derivedDeterministic, inferred, withheld}` on every node and edge — and the compiler **verifies** it against the block's own text rather than trusting the layer above. |
| No composition | `VisualSpec{primary, secondary[]}`. |
| Provenance asserted in code | Every learner-visible string is either book text carried with its source, or a rule-keyed sentence from the lexicon. |
