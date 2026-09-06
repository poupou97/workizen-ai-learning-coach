# Lane E1 · §19 — the generalization scoreboard

**Every metric carries its denominator. Nothing is combined into one score.** A single number here
would hide exactly the distinctions the lane exists to make: a cue is not an extraction, an
extraction is not a grounding, a grounding is not a validation, and none of them is a child seeing
something true.

---

## The scoreboard

| # | Metric | Value | Denominator | Note |
|---|---|---|---|---|
| 1 | **Subject independence of the extractor** | **6 / 6 rules subject-agnostic** | 6 rules | zero subject branches, asserted by an AST-walking test |
| 2 | **Subjects carried by one extractor** | **3** (KHTN · Khoa học · LS&ĐL) | 3 subjects with a TSL | no per-subject rule, no per-subject config |
| 3 | **Compilers reading only graph fields** | **6 / 6** | 6 compilers | `compiler_audit()`, measured at runtime — the §10 "compiled projection" hypothesis |
| 4 | **Primitives sufficing** | **6** (+1 carrier) | everything built | `Entity · Statement · Step · Event · Quantity · Figure` (+ `Formula`) |
| 5 | **Relations sufficing** | **6 used, 3 declared-unused** | everything built | `isA` may collapse into `hasPart` → possibly 5 |
| 6 | **Visual families projected from that core** | **10 declared · 6 compiled** | 10 families | 4 have no extractor yet |
| 7 | **REPRESENTABLE** (≥1 family cue) | **1,654** = 92.7 % | **1,784 units-backed** | a hypothesis about content, not a capability |
| 8 | **REPRESENTABLE, multi-family** | **1,404** = 78.7 % | 1,784 units-backed | multiple visual patterns per lesson is the norm |
| 9 | **EXTRACTABLE** (≥1 family built) | **220** = 98.2 % | **224 TSL-backed** | |
| 10 | **EXTRACTABLE, multi-family** | **191** = 85.3 % | 224 TSL-backed | |
| 11 | **EXTRACTABLE, none** | **4** = 1.8 % | 224 TSL-backed | |
| 12 | **GROUNDABLE** | **220 / 220** | lessons with any extractable family | by construction — a grounding without a locator raises |
| 12a | **Span integrity** | **1.0000** (was 0.9521) | **4,681 spans across all 238 TSL lessons** | does each grounding point where it says it does? 226 failures found and fixed — see `06-CENSUS.md` §3.2a. **Integrity is not precision.** |
| 13 | **Grounding locator quality** | **38 % text-span · 62 % page-geometry** | 12,349 groundings, 238 lessons | spans where text is the evidence, geometry where the figure is |
| 14 | **VALIDATABLE** | **3 lessons · 1 family** | 224 TSL-backed | `timeline-order-v1` is the only validator in the repo |
| 15 | **VISUALIZABLE** (renderer exists) | **4 families**, of which **2** reach real corpus data — on **1 lesson each** | 10 families | |
| 16 | **LEARNER_READY** | **0** | any denominator | `THRESHOLDS.json` does not exist |
| 17 | **Claims citable as textbook fact** | **77 / 104** = 74 % | 104 claims on the two distinct checkpoint lessons | computable for the first time; **none is learner-visible** |
| 18 | **Corpus reachable at all** | **1,784** units-backed = 55.1 % · **224** TSL-backed = 6.9 % | **3,240 distinct lesson keys** | 42.7 % has never been read |
| 19 | **Domain extensions proven necessary** | **3 of 7** as new node kinds | 7 candidates | MATH_AST · LIT_TEXT · CHEM_REACTION; 3 refuted, 1 reducible |
| 20 | **Generic rule vs curated rule, head to head** | **7 / 7**, equal | 1 lesson (LS&ĐL 5 Bài 8, `tc2-p1`) | the generic `e1-prose-dated-events-v1` matched Lane C's hand-checked result, and also runs on Science where it correctly yields 0 |
| 21 | **Family survival across pipeline builds** | **24 / 28 unchanged · 4 lost a family · 0 gained** | 28 LS&ĐL lessons with two builds | every disagreement runs the same direction |
| 22 | **Holdout precision** | **NOT MEASURED** | — | the rules were written against Bài 17 and Bài 8. This blank is the most important row on the board. |
| 23 | **Inter-annotator agreement on families** | **NOT MEASURED** | — | no second annotator has looked at a family assignment |
| 24 | **LLM calls** | **0** | — | census, classification and generation are all deterministic |

---

## What the board says, in three sentences

**The grammar generalises further than the data does.** Six primitives, six relations and six
compilers carried three subjects with no per-subject code, and reproduced a hand-checked History
result while also running on Science — but they only ever ran on the 6.9 % of the corpus that has
a Trusted Structured Lesson, and 42.7 % of the corpus has never been read at all.

**Nothing is true yet.** LEARNER_READY is 0, VALIDATABLE is 3 lessons and one family, and holdout
precision is unmeasured. Everything above row 16 measures *capability to construct*, not *warrant
to show*.

**The two biggest numbers are not semantic problems.** 1,384 lessons have no source, and 1,096
need one node kind that is blocked on two bridge defects. Neither moves by improving the ontology.

---

## Recommendation

### **GO WITH ARCHITECTURE CHANGE**

The hypothesis — `Trusted Structured Lesson → Semantic Extraction → SemanticGraphCandidate →
Grounding + Validation → Validated Semantic Graph → Visual Pattern Selector → VisualSpec →
Controlled Renderer` — **survived every attempt made to falsify it**, and it survived on evidence
rather than on argument: one extractor across three subjects, six compilers that provably read only
the graph, and a generic rule matching a curated one 7/7. The Founder's framing is right, and the
alternative framings are measurably wrong: **per-subject graphs are unnecessary** (History and
Science needed no extension), and **`lesson text → LLM → mindmap` is not on the table** because
nothing here needed an LLM at all.

**The architecture changes required — all of them outside the ontology:**

1. **`SemanticData` must become claim-bearing.** It carries `id, title, trust, derivation` and no
   provenance; `ComparisonDimension` — the cell values a child reads — carries nothing at all.
   Until that is fixed, no visual on the Trực quan tab can answer «may SAM say “sách viết”?».
2. **The bridge needs a carrier for validated structured nodes, and a per-block failure mode.**
   `ROLE_MAP` has no `formula` key, and `lesson_document.dart:343` nulls the *whole document* on an
   unknown kind. Today Lane A2's validated math cannot reach a lesson, and the first attempt to
   send it deletes the lesson. This blocks the 1,096-lesson cluster — the largest addressable one.
3. **The four `SemanticData` subtypes move to the visual side.** They are compiled projections, not
   canonical semantics. `ConceptMapSemantic` should be deprecated as a type: it has existed for a
   whole round and produced nothing, because as a *semantic* type it has no extraction rule, while
   as a *projection* it is trivial.
4. **Pipeline changes need a semantic-yield gate.** 4 of 28 LS&ĐL lessons lost a visual family to a
   round-5 rebuild that *improved* on block counts. Accuracy metrics do not see this.
5. **`khtn6_bai17.dart` decomposes into versioned data + compiled artefacts + a ~10-row rule
   registry + a small curated overlay** — not 3,679 Dart files, and not 3,679 anything.

### Why not GO

Because three things are unmeasured and one of them could invalidate the family counts: **holdout
precision** (row 22), **inter-annotator agreement** (row 23), and the known over-firing of
`e1-definition-v1` (68.8 % of lessons "have a definition" is not credible). A GO would imply those
were checked. They were not.

### Why not MORE EVIDENCE

Because the load-bearing claims *were* checked, on real corpus data, deterministically, with a
falsifiable test attached to each: subject independence, projection-not-semantics, relation-level
grounding, and generic-matches-curated. Waiting for more evidence before fixing the bridge would
leave the largest addressable cluster blocked on two defects that are already located to the line.

---

## What this lane owes next, in order

1. **Precision on a holdout** the rules were not written against — rows 22 and 23. Nothing else
   should be built first.
2. **A COMPARISON extractor** — the largest cue family with no rule (53.8 % of units-backed).
3. **`gap`-emitting compilers**, so a withheld member makes a structure visibly incomplete rather
   than quietly smaller (round-5 defect 8, reproduced inside this lane).
4. **A human read of the 63 tier-E lessons** — the right size for curation, and where a genuinely
   new pattern would appear if one exists.
