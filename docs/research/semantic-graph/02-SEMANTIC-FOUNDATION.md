# Lane E1 · P0.1 — the minimal Semantic Foundation

`tool/semantic/graph.py`. Research candidate; **no production migration**. 42 tests in
`tool/tests/test_semantic_foundation.py`.

The chain, and where this module sits:

```
SourceBlock(s) → SemanticClaim → Validation → SemanticNode/Relation → VisualElement
     ↑ TSL          ↑ here          ↑ absent        ↑ here                ↑ Lane E2
```

"Validation" is deliberately **not implemented as an approval**. A claim leaves here as
`proposed` unless a *named* validator ran. There is no code path that promotes a claim by
confidence, by agreement or by volume.

---

## 1. §5 — `SemanticClaim` is first-class

The rule this type exists to enforce:

> `A --CAUSES--> B` must not become truth merely because A and B are both source-grounded.
> **The relationship itself needs grounding and status.**

So a claim's `subject` is a node **or a relation**, and a `SemanticRelation` cannot be constructed
with a node-kind claim — it raises. In `extract.py` that means:

| relation | grounded in | not grounded in |
|---|---|---|
| `next` | the **enumerator** («1.», «·», «Bước 2») — what the page prints to assert order | the step texts |
| `causes` | the **connective span** («… nên …», «dẫn đến») | the two clauses |
| `atTime` | the **parenthesised date** | the event name |
| `hasPart` | the printed **heading nesting** | the two headings |
| `depicts` | the **figure reference** inside the prose | the figure or the sentence |

A `causes` edge whose clauses are grounded but whose connective is not **is not emitted**. That is
a test (`test_no_causal_edge_without_a_connective`), not a convention.

### The enum audit — reuse, and the exact delta

`KnowledgeOrigin` (`lib/core/knowledge/provenance.dart:15`) already covers four of the Founder's
seven listed support kinds:

| Founder's §5 list | existing value | verdict |
|---|---|---|
| SOURCE_STATED | `sourceStated` | exists |
| SOURCE_DEMONSTRATED | `sourceDemonstrated` | exists |
| DETERMINISTIC_DERIVED | `systemDerived` | exists |
| MODEL_PROPOSED | `llmInferred` | exists (narrower name, same role) |
| HUMAN_CURATED | — | **MISSING — the one value worth adding** |
| CONFLICT | — | **wrong axis** |
| WITHHELD | — | **wrong axis** |

**CONFLICT and WITHHELD answer «what happened to this claim», not «where did it come from».**
Folding them into `KnowledgeOrigin` would make `citableAsTextbookFact` (`provenance.dart:83`)
undecidable, because a *withheld* `sourceStated` claim would lose the fact that the **source** said
it — and that is exactly the fact you need to decide whether it may be restored later.

So the foundation keeps two orthogonal fields:

```
support : KnowledgeOrigin  + humanCurated              (+1 value)
status  : proposed | validated | conflict | withheld | superseded   (+1 small enum)
```

**Total enum delta: one value and one enum.** `sourceSequence` — which the Founder's list omits and
which is load-bearing (TOC order is not a prerequisite) — is kept.

`status` also gives the round-5 data-versioning dispositions somewhere to live: `superseded` is how
a repaired claim replaces an earlier one without overwriting the source observation.

### `TRACE ≠ EVIDENCE`, in the type

`learner_visible` is `status == 'validated'` **and** no grounding is withheld. Today that is
**0 claims out of 122** across the checkpoint. A `proposed` claim is a trace. There is no flag to
flip.

---

## 2. §7 — `SourceGrounding`, stronger than `sourceBlockId`

Today a `ProcessStep` carries `sourceBlockId` — a bare string. It cannot answer «show me the
print»: no page, no geometry, no span. Resolving it means walking back through
`LessonDocument.blockById` → `block.sourceRef`, which the semantic object has no reference to.

`SourceGrounding` carries, reusing `SourceRef`'s field names exactly:

```
book · blockId · pagePdf · pagePrinted · bbox · span{start,end} · figureId
     · extraction · pipeline · ocrConf · agreementScore · trust(ContentTrust) · quote
```

and **refuses to exist with only a block id**. Character offsets are *not* required everywhere —
for a figure or a diagram region the appropriate evidence is page geometry — so `locator_kind`
reports which of `text-span` / `figure-region` / `page-geometry` / `page` this grounding actually
achieved. Measured on Bài 17: **22 text-span, 46 page-geometry**.

Both page numberings are carried because they differ and confusing them cites the wrong page to a
child (Bài 8: PDF 39 = printed 37).

---

## 3. §6 — the provenance bridge

Two worlds exist and **nothing joins them** (`01-AUDIT-CLASSIFICATION.md` §1.3):

```
content world     SourceRef · ContentTrust · derivation        lesson_document.dart, content_trust.dart
knowledge world   Provenance · KnowledgeOrigin · Lineage       knowledge/provenance.dart, lineage.dart
```

The bridge is **one total function**, `provenance_of(claim) → Provenance`-shaped dict. It does not
merge the two worlds; the claim simply speaks both languages:

| `Provenance` field | filled from |
|---|---|
| `origin` | `claim.support` |
| `sourceId` | `grounding.block_id` — a block id, **never a file path** (`provenance.dart:60-62`) |
| `extractionMethod` | `claim.derivation` (the rule id) |
| `confidence` | `claim.confidence` |
| `pageStart` / `pageEnd` | min/max `page_printed` across all groundings |
| `_contentTrust` / `_claimStatus` | carried across so the knowledge world can *see* the content world's verdict without importing it |

**What this makes possible for the first time:** `citableAsTextbookFact` becomes computable for a
semantic object. Today it is undecidable for everything on the Trực quan tab, because
`SemanticData` carries no `Provenance` at all. On the checkpoint, **48 of 68** Bài 17 claims and
**29 of 36** Bài 8 claims compute as citable — and *none* of them are learner-visible, which is
exactly the distinction the two axes were separated to preserve.

`lineage_of()` materialises the full §6 chain as data so it can be asserted in a test:

```
VisualElement → VisualSpec element → SemanticClaim → status → support → derivation
              → SourceBlock → SourceSpan → SourceRef{book,pagePdf,pagePrinted,bbox}
              → TrustedLearningSource{trust[], gate}
```

…with an honest terminus: `"gate": "NONE — THRESHOLDS.json does not exist; trusted computes to 0"`.
**The bridge does not fake a unified provenance system.** It gives the pedagogy layer a value in
the pedagogy layer's own vocabulary and stops.

### Minimal migration path

See `04-BAI17-REPLACEMENT.md` §4. Steps 1–4 are pure additions (`SourceGrounding` beside
`SourceRef`; grounding on the four leaf types **and on `ComparisonDimension`, which has none**;
`claims` on `SemanticData`; the two enum changes) and could be taken without changing a pixel.
Steps 5–7 change shipped content and are Founder gates.

---

## 4. No `from_<presentation>` constructor, ever

Adopted from Lane A2 (PR #84) rather than re-derived. A2's `MathExpression` has `from_json` and
deliberately **no** `from_latex`: `latex` and `text` are computed properties with no setter, so a
rendering string cannot become structure.

The same rule binds here, and a test walks the AST of every module in `tool/semantic/` and fails on
any `from_*` outside an allowlist (`from_json`, `from_tsl_block`). A `SemanticClaim.from_markdown`
or a `VisualSpec.from_svg` would be exactly the hole through which a model's output launders itself
into TrustedText.

`from_tsl_block` is allowed because a TSL block is **not a rendering** — it is the validated source
record, carrying the page, bbox and pipeline that make the claim auditable.

---

## 5. §25 — the boundary

| | Semantic Graph (this lane) | Pedagogy Runtime (existing) |
|---|---|---|
| answers | what knowledge and relationships **exist** | what SAM **may teach**, how, what counts as evidence |
| fails | open — a missing claim is an absent visual | **closed** — refusal codes, `EvidencePolicy.none` |
| may say «sách viết…» | computes `citableAsTextbookFact`; **does not act on it** | owns that decision |

E1 adds **no** path by which a `proposed` claim can reach a learner. The graph never becomes
pedagogy truth.
