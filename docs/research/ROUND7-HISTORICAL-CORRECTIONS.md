# Round 7 — HISTORICAL CORRECTIONS

Per the permanent reporting rule: **round N's report and archive stay exactly as published;
corrections are recorded here, beside them, never applied silently.** Round 6's report and
`HOC-CUNG-SAM-ROUND-06-2026-09-06-v2.zip` are unchanged.

---

## C1 · HISTORICAL CORRECTION TO ROUND 6 — «the cheapest win on the board» was wrong

**Published (round 6, §12, repeated by me to the Founder):** the 118 blocks withheld only
because the app lacks a matching type are *«a model gap, not a data gap, and the cheapest
win on the board»*.

**Corrected (WS-S, round 7):** measured, and it is not a win at all.

- **Of the 118, a servable type is recommended for ZERO.**
- **114 of them gain nothing**: exactly **one** structural group across 238 lessons contains
  a gap block, so the 64 `footnote` and 50 `activity` blocks belong to **no group**.
- **Adding all three types removes 1 of 31 mutilated structures.** The real lever is the
  all-or-nothing sibling rule: **31 → 0**, at a cost of 72 blocks (11,833 → 11,761 served).

I relayed the round-6 phrasing to the Founder without measuring it. The claim was
plausible, cheap-sounding and wrong, and it is exactly the kind of number this round's own
permanent rule exists to catch: **it was never re-derived from leaf records.**

**Also falsified:** round 6's «these blocks passed every trust gate». They passed the **TSL**
gate and became `trustedStructuredLesson` — which is a schema label, not a trust grant.

---

## C2 · HISTORICAL CORRECTION TO ROUND 6 — a rate published without its denominator

**Published (round 6, §4):** «**DIGIT LOSS 312 (57 %)** vs **SEGMENTATION 196 (36 %)**».

**Correction:** the denominator, **548**, is missing. It should read **312 / 548 = 0.569**
and **196 / 548 = 0.358**. The Founder's standing rule since 2026-09-05 is that *every metric
states its denominator explicitly*, and this one did not. The percentages themselves are
correct.

---

## C3 · HISTORICAL CORRECTION TO ROUND 3 — two live occurrences of the container-shape defect

Found by WS-M's sweep, assigned to the coordinator, and **fixed forward here**. The published
round-3 census outputs are **not** rewritten.

**`tool/research/lane_c/subject_family_census.py:143`** — iterated `p.get(key)` directly. For
`toanExercises`, a **dict keyed by lesson number**, that yields lesson-number *strings*, each
failing `isinstance(e, dict)` and being filed as a phantom `_non_dict_entries`. The comment
sitting on the line — «some packs carry bare ids (e.g. toanExercises)» — **was a misdiagnosis
of this very bug**, written into the code as if it were a property of the data.

**`tool/research/lane_c/second_lesson_candidates.py:240`** — *did* check the shape, but
flattened **one level short**: `list(xs.values())` yields **lists**, so `isinstance(e, dict)`
was always False and `pack_wiring['toanExercises']` was **0 for every candidate**.

Both now flatten to leaf records. Same root cause as the round-6 archive incident and as my
own round-3 misreading: **`len()` on a keyed container returns keys, not leaves.** Three
independent occurrences of one defect across three rounds.

---

## C4 · Clarification, not a correction — Lane D and WS-S measured different surfaces

Round 6 (Lane D): «**defect 6 on the shipped packs: ABSENT (0 of 207)**».
Round 7 (WS-S): «**22 imprint blocks are served to children today**» as `heading` (17) and
`body` (5), with 5 more held back only by the type gap.

**Both are true.** Lane D measured the **pack** surface; WS-S measured the **lesson path /
TSL** surface. Neither figure is wrong and neither supersedes the other — but «defect 6 is
absent» must never be quoted without naming the surface, or it reads as «defect 6 is fixed»,
which it is not. **Defect 6 is open on the lesson path.**

---

## C5 · The denominator question is resolved — as a definition, not a conflict

**Verified independently by the coordinator, re-derived from `assets/pack/` — an artefact
that does not depend on WS-A's `all-lessons.csv`:**

| grouping key over `pack.subjects[*][*].lessons[*]` | count |
|---|---|
| leaf rows | **3,679** |
| distinct `(sourceDocumentId, no)` | **3,240** |
| distinct `(sourceDocumentId, no, pageStart, title)` | **3,650** |
| rows carrying `pageStart` | **3,381** |

**All four are one leaf population under four grouping keys.** `3,679` and `3,650` were never
two artefacts disagreeing, and `3,381 ranged` is exactly the `pageStart` subset — the
Founder's two denominators never conflicted. `3,240` remains the dangerous one: it **deletes
410 real lessons** to key collision.

*(Note the field is `no`, not `number` — my first re-derivation attempt used `number`, got 238
and 3,497, and was wrong. Recorded because the failure mode is the subject of this document.)*

**`3,679` remains HISTORICAL BASELINE ONLY** until the Founder chooses a grouping key. This is
now a **definition** decision, not a data conflict.
