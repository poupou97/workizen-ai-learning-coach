# Lane E1 · §24 — what replaces `khtn6_bai17.dart` and the one-row registry at K-12 scale

**Constraint, verbatim: “Do NOT generate 3,679 Dart files.”** Also: do not migrate production.
This is a proposed decomposition with a measured basis, not a migration order.

---

## 1. What is actually in there

`lib/core/curriculum/khtn6_bai17.dart` — 122 lines, 100 % `const`, one lesson, zero functions,
zero parameters. Plus `semantic_binding_registry.dart:13`, a one-row closed constant.

Naïvely scaled that is 3,679 hand-written Dart files. But the file is not one kind of thing. Sorted
by what each part actually is:

| # | Part | Line | What it really is | Scales by |
|---|---|---|---|---|
| 1 | `LessonRef('06-sgk-khoa-hoc-tu-nhien-6', 17)` | `:32` | an **identifier** | already derivable from the corpus |
| 2 | `pageStart: 63, // trang IN (PDF 64; lệch −1…)` | `:92` | a **measured book fact** hand-copied | the pipeline already measures the printed↔PDF offset per book |
| 3 | `textbookTerms: {6: {'lọc','lắng','cô cạn','chiết','hỗn hợp'}}` | `:50-52` | **extractable data** — the terms are printed in the lesson | a deterministic rule + a glossary |
| 4 | `Concept`, `SkillCase`, `LearningStage` | `:38, :55, :65` | **curriculum data**, currently expressed as code | versioned data |
| 5 | `TeachingMethod` + its `Provenance(sourceStated, p.63)` | `:76-94` | a **claim about the book**, hand-asserted | a claim with `support='humanCurated'` |
| 6 | `hints` deliberately absent (`:74`) | — | a **pedagogical judgement** | stays human |
| 7 | `BindingCurriculum` + `SemanticBinding(confidence: 0.8, status:'PROPOSED')` | `:97, :107` | a **binding decision** | a registry keyed by lesson |
| 8 | `resolveBinding()` refusal codes | `semantic_binding.dart:172-222` | **generic machinery** | already lesson-agnostic — keep unchanged |

Only rows 5, 6 and 7 are genuinely human. Rows 1–4 are data that the corpus already contains or
that a rule can derive. That ratio is the whole answer.

---

## 2. The decomposition

| Layer | What goes there | Form | Who writes it | Scale |
|---|---|---|---|---|
| **Versioned data** | lesson identity, boundary, printed↔PDF offset, heading path, figure inventory, extracted terms | the TSL itself + a per-lesson `semantic-graph-candidate/v0` JSON, both already produced, both gitignored under `poc-out/` | pipeline | 3,679 rows, 0 Dart files |
| **Compiled artefacts** | one `VisualSpec` per (lesson × family) | `visual-spec/v0` JSON, built by `compile*()` | build step | derived; never hand-edited, never committed |
| **Schemas** | `SemanticClaim`, `SourceGrounding`, `SemanticNode/Relation`, `VisualSpec`, `VisualElement` | **Dart types — a fixed, small set** | humans, once | ~5 types total, not per lesson |
| **Registries** | which derivation rules exist; which validators exist; which families a renderer supports; which lessons carry a curated exception | small keyed tables | humans | one row per **rule**, not per lesson |
| **Generation pipeline** | TSL → graph → VisualSpec, plus the trust/lineage stamping | `tool/semantic/{extract,visualspec}.py` today | this lane | 6 rules today |
| **Curated exceptions** | rows 5–7 above: a human's claim about what the book teaches, and the pedagogical judgement of what SAM may do with it | data rows carrying `support='humanCurated'` + a curator id, **not code** | Founder / teacher | as few as possible, counted and reported |

### The shape of the change, in one line

> `khtn6_bai17.dart` is **not** a lesson. It is a **rule registry, a data row and a curated
> exception**, fused into one `const` file. Splitting those three apart is what makes 3,679
> tractable — the rule registry has ~10 rows forever, the data rows are generated, and only the
> curated exceptions grow with the corpus, which is exactly why the census must count them.

### What `SemanticBindingRegistry` becomes

Not `bindings = [3679 constants]`. A lookup over generated data, plus a **small curated overlay**:

```
bindingFor(lessonRef) =
    generated(lessonRef)            // from the lesson's semantic graph — data
    ⊕ curatedOverlay[lessonRef]     // 0 or 1 row, humanCurated, with a curator id
```

`resolveBinding()` (`semantic_binding.dart:172`) does **not** change: it is already generic and
already fail-closed with seven named refusal codes. The registry it reads is what changes shape.

### The one new thing this needs — the carrier gap

For a lesson whose teaching object is a **formula**, none of the above works today, for the two
reasons verified in `01-AUDIT-CLASSIFICATION.md` §3: `ROLE_MAP` has no `formula` key
(`tsl_to_lesson_document.py:70-81`), and the consumer's sealed union takes the **whole document**
down on an unknown kind (`lesson_document.dart:343` → `:1018`). So step one of any scaling plan is
a **carrier for validated structured nodes** in the bridge, and a per-block failure mode instead of
a per-document one. Both are outside E1's ownership; both are named here because §24 cannot be
answered without them.

---

## 3. What must NOT be generated

- **Hints and pedagogical scripts.** `khtn6_bai17.dart:74` leaves `hints` absent deliberately.
  Generating them is exactly «LLM says ⇒ graph truth», one layer up.
- **Prerequisite edges.** `prerequisite_edges.dart` holds **one** hand-vetted `sourceStated` edge
  in the entire repo, and `Provenance.citableAsDependency` (`provenance.dart:95`) requires
  `sourceStated`. TOC order is `sourceSequence` and is **not** a dependency. Generating 3,679
  lessons' worth of prerequisites would be inventing the single claim the type system most
  carefully forbids.
- **Concepts, as a canonical list.** `Concept` has one real instance. Minting 3,679 machine-named
  concepts produces a vocabulary nobody validated and every downstream layer would then trust.
- **A `.dart` file per lesson, in any form** — including "generated" ones. Generated Dart is still
  Dart: it must compile, be reviewed, and be regenerated on every rule change. Data does not.

---

## 4. Migration path — minimal, additive, no production change

| Step | Change | Risk |
|---|---|---|
| 1 | Add `SourceGrounding` **beside** `SourceRef` as a view over it | none — additive |
| 2 | Add `grounding` + `support` + `status` to the four leaf types that already carry `sourceBlockId`, **and to `ComparisonDimension`, which carries nothing** | low; fixes a real hole |
| 3 | Add `claims: [SemanticClaim]` to `SemanticData` | low; the object gains the provenance it never had |
| 4 | `KnowledgeOrigin` += `humanCurated`; add `ClaimStatus` | one enum value, one small enum |
| 5 | Move the two Python derivation rules behind `compile*()` and stop hardcoding Bài 17's title/dimension (`tsl_to_lesson_document.py:419, :424`) | medium — changes shipped fixture content |
| 6 | Replace the 1-row registry with `generated ⊕ curatedOverlay` | medium — needs step 5 first |
| 7 | Delete `khtn6_bai17.dart`'s rows 1–4, keep 5–7 as curated data rows | last, and only after the census says how many lessons need a curated row at all |

Steps 1–4 are pure additions and could be taken without changing a pixel. Steps 5–7 change shipped
content and are **Founder gates**, not lane decisions.

---

## 5. The number this answer is still missing

How many lessons need a **curated exception** at all? That is P0.3's job (`06-CENSUS.md`), and it
is the number that decides whether this decomposition is cheap or merely differently expensive. If
it is ~50, this works. If it is ~2,000, the grammar is wrong and the answer is to fix the
grammar — *«FIX THE LANGUAGE, NOT 100 INDIVIDUAL LESSONS»* — not to industrialise curation.
