# METRIC TRUTH — the registry, the «total activities» ruling, and the sweep

**Round 7 · WS-M · 2026-09-06.** Measurement and definition only. Nothing is activated,
no threshold is set, no published figure is rewritten. **DO NOT MERGE.**

---

## 0 · The rule, and why it is the rule

> ### NO IMPORTANT DERIVED METRIC IS ACCEPTED UNLESS IT CAN BE RE-DERIVED FROM LEAF RECORDS.

For every important metric, record all nine of:

**semantic quantity counted · unit · leaf population · grouping key · denominator ·
aggregation function · exclusions · source artefact/version · independent re-derivation
command or test.**

Do **not** trust a number because its type is correct, its range looks plausible, CI
passes, or a neighbouring metric agrees.

**The incident.** `toanExercises` in `assets/pack/lesson-index-g*.json` is a dict keyed by
lesson number whose values are lists of expressions:

```python
len(d['toanExercises'])                           # 10  ← lesson KEYS, wrong quantity
sum(len(v) for v in d['toanExercises'].values())  # 41  ← expressions, right quantity
```

Round 6 called `len()`, reported «10 toanExercises», and filed the settled figure
`41 → 0` as `NOT CAPTURED`. **The same mistake was made in round 3** — and, as §4 shows,
two round-3 occurrences of it are still live in the repository today.

**What generalises.** *A number that is the right type and the wrong quantity passes every
check that is not a re-derivation.* Same family as `empty_block` misstating what was lost,
and as a field-name guard blind to identity inside a value. No type check, no range check,
no CI job and no reviewer's eye catches it, because nothing about it is malformed. Only
counting the leaves a second way does.

**Corollary, and the reason §5 exists.** Reproducibility is not meaning. The `217` of §3
reconstructs to the digit and still counts no population at all.

---

## 1 · How to run it

```bash
python3 tool/metrics/cli.py verify        # re-derive every metric; non-zero on any mismatch
python3 tool/metrics/cli.py report        # the nine fields, per metric, with a live re-derivation
python3 tool/metrics/cli.py deprecated    # what «total activities» actually was
python3 tool/metrics/cli.py lint          # the container-shape lint over tool/
python3 -m unittest discover -s tool/tests   # 784 OK, 19 skipped
```

`verify` on the 2026-09-06 artefacts: **18 of 18 metrics re-derive to their recorded
value**, and every declared pack shape holds in every pack.

An artefact that is not on this machine reports **UNAVAILABLE and fails** — `assets/pack/`
and `poc-out/` are gitignored SGK derivative works, and **a missing artefact is never a
zero.**

---

## 2 · The registry

Full nine-field cards: `python3 tool/metrics/cli.py report`. Source of truth:
`tool/metrics/metric_registry.py`.

| metric | unit | grouping key | value | what it is |
|---|---|---|---:|---|
| `TOAN_EXERCISE_LEAF_COUNT` | expression | none — leaf rows | **0** | Toán expressions **shipped**. The truthful zero. |
| `LESSON_KEY_COUNT` | **container key** | lesson number within a grade | **0** | the quantity `len()` returns, given a name so it can never again be read as an item count. **Never publish as an activity count.** |
| `TOAN_EXERCISE_UPSTREAM_LEAF_COUNT` | exercise record | none — leaf rows | **41** | the «41» of «41 → 0», counted in the upstream source |
| `TOAN_EXERCISE_UPSTREAM_NON_VERBATIM_COUNT` | exercise record | none | **41** | all 41 are `INFERRED` / `geometric-fraction-rebuild-v1`. **41 of 41.** |
| `TOAN_EXERCISE_UPSTREAM_LESSON_KEY_COUNT` | lesson | `(book, lessonNo)` | **10** | the «10 lessons whose exercise list is now empty» |
| `ACTIVITY_LEAF_COUNT` | activity row | none — leaf rows | **207** | all seven families. The metric `248 → 207` belongs to. |
| `LEARNER_ACTIVITY_LEAF_COUNT` | activity row | none — leaf rows | **171** | six families; `sourceAssets` excluded |
| `SOURCE_ASSET_ROW_COUNT` | row | none | **36** | |
| `DISTINCT_SOURCE_ASSET_COUNT` | asset | `(asset, sourceDocumentId)` | **3** | 36 rows are 3 assets × 12 packs |
| `ACTIVITY_FAMILY_COUNT` | family | family name | **7** | the schema's declared families |
| `ACTIVITY_FAMILY_NONEMPTY_COUNT` | family | family name | **6** | of 7 — `toanExercises` is the empty one, on purpose |
| `SOURCE_LESSON_ROW_COUNT` | TOC row | none — rows | **3 679** | `SourceLessonRecord`s. HISTORICAL BASELINE ONLY. |
| `CANONICAL_LESSON_IDENTITY_COUNT` | lesson | `(doc, no, pageStart, title)` | **3 650** | `CanonicalLessonIdentity`. A MEASUREMENT. |
| `RANGED_LESSON_ROW_COUNT` | TOC row | none — rows | **3 381** | rows with a printed `pageStart` |
| `LESSON_PAIR_KEY_COUNT` | **key pair** | `(doc, no)` | **3 240** | published as a lesson count; **it is not one** |
| `TRUE_DUPLICATE_EXCESS_ROWS` | row | `(doc, no, pageStart, title)` | **29** | `3 679 − 29 = 3 650`, exactly |
| `PACK_BOOK_ROW_COUNT` | book row | none | **238** | ⚠ collision — see §6 |
| `PACK_DISTINCT_BOOK_COUNT` | book | `sourceDocumentId` | **238** | measured equal, not assumed |

### 2.1 · What the registry found on its way in

**Four published denominators are one leaf population under four grouping keys.** Every one
of `3 679 · 3 650 · 3 381 · 3 240` re-derives from `pack.subjects[*][*].lessons[*]`, the
same rows, read four ways. `3 679` and `3 650` were being carried as two figures needing a
Founder ruling to reconcile; **they need no reconciliation — they differ by grouping key,
not by artefact.** WS-A derived `3 650` from `all-lessons.csv`; WS-M re-derived it from the
packs, an independent artefact, and got `3 679 · 3 650 · 3 381 · 3 240 · 154 duplicated
keys · 439 excess rows · 29 true duplicates` — **every figure identical.** The Founder
questions that remain (are the 291 unanchored identities lessons? are the 63 TOC-less books
in the denominator? does `Chuyên đề` count?) are product questions, and none of them is the
`3 679`/`3 650` question.

**`sourceAssets` is 36 rows and 3 assets.** Every grade pack carries the *same* three
grade-5 crops. Only in grade 5 do they pass the app-side grade filter (`sourceAssetsFor`,
`lesson_index_source_assets_grade_test.dart`), so **a count of 36 overstates by 33 what any
learner can reach.** `VISIBLE ≠ SERVED`, appearing inside a metric rather than beside one.
The app fails closed correctly; the *metric* did not.

**«Activity» already had two family sets in the repository** — seven in
`tool/corpus/legacy/packs.py`, six in `tool/corpus/readiness_matrix.py` and
`tool/research/lane_c/` — differing by exactly those 36 rows; and an eighth-family variant
in `tool/corpus/ft_audit_sample.py` that includes `samUnits`, which is not a pack key at
all. Both pack-schema sets are now named metrics. Neither was chosen silently.

---

## 3 · «TOTAL ACTIVITIES» — RESOLVED BY DEPRECATION

Three totals were published over the same twelve pack files. **All three reconstruct
exactly** (`python3 tool/metrics/cli.py deprecated`, and asserted in
`tool/tests/test_metric_registry.py`).

| number | what it actually counts | verdict |
|---:|---|---|
| **248** | seven-family activity **leaf rows** on the pack build *before* the Founder §3 fail-closed change. `207 + 41`. A correct earlier **value of `ACTIVITY_LEAF_COUNT`**, not a different metric. | **SUPERSEDED** — still valid as the historical value of a named metric on a named build |
| **217** | `207` activity leaf **rows** `+ 10` `toanExercises` container **KEYS**. **A sum of two different units.** | **DEPRECATED** — it counts no population; it answers no question anyone can state |
| **161** | `tvReadings 66 + tvWritings 54 + toanExercises 41` — leaf rows of **three of seven families**, i.e. the Toán + Tiếng Việt subset, published under a whole-corpus name. Silently drops `suSources`, `khoaExperiments`, `diaMaps`, `sourceAssets` — **87 of the rows it purports to total**. | **DEPRECATED as a total.** The aggregation is sound; the family set is arbitrary and was never declared. No consumer in the repository asks for this subtotal. |

> ### The phrase «total activities» is DEPRECATED and must not enter round-7 metrics.
> It admits three answers, so it is not a metric. Write `ACTIVITY_LEAF_COUNT` (**207**,
> seven families) or `LEARNER_ACTIVITY_LEAF_COUNT` (**171**, six families) — chosen
> explicitly, and written **with its family set beside it**.

**`217` is the workstream's own worked example.** It is arithmetically reproducible to the
digit and semantically empty. Reproducibility is not meaning.

**A near-miss worth naming.** `207` is simultaneously the post-fail-closed seven-family
total *and* the pre-fail-closed non-Toán total — because `toanExercises` went to exactly
zero. That is an identity, not a coincidence, but it is precisely the shape of accidental
agreement that hides a grouping-key bug: *a neighbouring metric agreeing is not evidence.*

---

## 4 · The regression — and two more live occurrences of the same defect

`tool/tests/test_metric_registry.py` · **36 tests.** The incident is committed as a
regression in both directions:

- **the wrong route is BLOCKED** — `count_leaves()` raises `ContainerShapeError` on **any**
  mapping, not just this one, rather than returning a plausible integer;
- **the right route re-derives** on a fixture where every confusable count is a **different
  number** (7 leaves · 3 keys · 33 all-family · 25 six-family · 4 lesson rows), so no
  accidental agreement can rescue a wrong implementation;
- **a family that changes shape** (declared `list`, shipped `dict`) is refused, not counted;
- **a NEW container-shape finding anywhere in `tool/` fails CI**, and a baselined finding
  that has silently vanished fails too, so the baseline cannot rot.

**Mutation-checked.** Four mutations, all RED, restored tree green:
re-enable `len()`-on-a-mapping (2 failures) · compute `ACTIVITY_LEAF_COUNT` as keys + rows,
the 217 error (5) · disable lint rule B (4) · add one new `len()`-on-container site
anywhere under `tool/` (1).

### 4.1 · HISTORICAL CORRECTION TO ROUND 3 — two live occurrences

`tool/metrics/metric_container_lint.py` walks all of `tool/`. **Two findings, both real,
zero false positives.** Both are round-3-era research scripts, both still live, and both are
the round-6 incident **two rounds earlier**:

**① `tool/research/lane_c/subject_family_census.py`**

```python
for key in PACK_KEYS:              # PACK_KEYS includes 'toanExercises'
    for e in p.get(key) or []:     # iterating a DICT yields lesson-number STRINGS
        if not isinstance(e, dict):        # a str is not a dict …
            wired['_non_dict_entries'][key] += 1   # … so every leaf is filed as a phantom
            continue
```

The comment on that line reads *«some packs carry bare ids (e.g. toanExercises)»* — **a
misdiagnosis of this exact bug.** They are not bare ids; they are dict keys. Effect: the
subject-family pack-wiring census recorded **0** `toanExercises` for every family and **10
phantom `_non_dict_entries`**, against a true **41 leaves in 10 lessons**.

**② `tool/research/lane_c/second_lesson_candidates.py`**

```python
xs = pk.get(key) or []
if isinstance(xs, dict):
    xs = list(xs.values())         # yields LISTS of exercises …
for e in xs:
    if isinstance(e, dict) and …:  # … and every one is rejected here
        wiring[key] += 1
```

The shape check is present and the flatten stops **one level short**. Effect:
`pack_wiring['toanExercises']` is **0** for every candidate in the second-golden-lesson
census. *A shape check that stops one level early is worse than none, because it reads as if
the shape had been handled.*

**Reported, not silently repaired.** Both scripts produced **published** census outputs;
WS-M does not own those outputs, and rewriting the code now would change what a reader
finds without changing what was published. Both are baselined in `KNOWN_FINDINGS` with a
written verdict, so a **third** occurrence fails CI. **Recommended owner: the coordinator,
as a round-7 or round-8 debt item.**

---

## 5 · The sweep — round 6's important derived numbers, re-derived

Method: re-derive from the **leaf records** of the artefact, independently of the tool that
published the figure. `PROVEN` = re-derived first-hand here.

| # | published (round 6) | verdict | how |
|---|---|---|---|
| 1 | conservation: batch 2 `787 = 285+169+333+0`, batch 1 `814 = 234+170+410+0`, golden `277 = 43+43+191+0` | **PROVEN** | re-ran `ledger.py` over every TSL in the batch dirs: **814 and 787 reproduce exactly**, `UNACCOUNTED = 0` |
| 2 | «29 lesson ledgers · 1 878 input regions · 138 unaccounted → 0» | **PROVEN, with a re-derivation defect — now fixed** | `29 = 14+11+4` and `1 878 = 814+787+277`. But the *documented command* reproduced **681/611**, not 814/787 — see §5.1 |
| 3 | §9 withheld `135→144 · 124→147 · 30→37` | **PROVEN** | headline equals the per-lesson leaf sum in all seven stored ledgers; conservation identity holds on every one; `served` byte-identical before→after (196 · 232 · 40) |
| 4 | 82 lost regions = 31 + 20 + 13 + 18 | **PROVEN (arithmetic)** | sums exactly |
| 5 | recognition REGION census: `312 DIGIT LOSS (0.569) · 196 SEGMENTATION (0.358) · 40 FRACTION STRUCTURE (0.073)` of **548**; 784 regions; 236 readable; 387 blocks; 113 pages | **PROVEN** | re-derived from the 784 leaf rows of `study-sdm.json`: every count, every share, to four decimals |
| 6 | WS-D census: 238 lessons · 11 971 TSL served · 2 032 TSL withheld · 3 864 figures | **PROVEN** | re-derived from the 238 `tc2-p1` TSLs directly — all four exact |
| 7 | WS-D census: 12 071 served · 2 170 withheld · share 0.152 · form census summing to 14 241 | **PROVEN (arithmetic), mechanism INFERRED** | `14 003` TSL blocks `+ 238` (one `sourceRef` per lesson) `= 14 241`; `2 032 + 138 = 2 170`; `11 971 + 238 − 138 = 12 071`. Every identity closes |
| 8 | «118 blocks withheld only because the app lacks a type» — `footnote` 64 · `activity` 50 · `option` 4 | **PROVEN as a round-6 measurement, not a stale round-3 quote** | the four `unknown_role:*` / `table_without_cells` reasons **do not exist in any TSL**; they are emitted by `tsl_to_lesson_document.py`. `64+50+4+20 = 138`, which is exactly the served→withheld delta in ⑦ |
| 9 | `12 of 317` engine rows (0.0379); `281 → 234` (−16.7 %) | **PROVEN (arithmetic)** | `12/317 = 0.03785`; `47/281 = 0.1673` |
| 10 | «10 toanExercises» / `41 → 0` filed as NOT CAPTURED | **FALSIFIED — the original incident** | 41 upstream leaves, all `INFERRED`, 10 distinct `(book, lesson)`; 0 shipped |

### 5.1 · The one re-derivation defect found — FIXED

Round 6 published **two different accounting populations over the same batch dirs**, and
`ledger.py audit` had no way to say which it was computing:

| population | lessons | input regions | published in |
|---|---:|---:|---|
| `batch-spec.json` selection | 6 + 6 + 2 | 681 · 611 · 232 | §9's withheld counts |
| every TSL in the batch dir | 14 + 11 + 4 | 814 · 787 · 277 | §7's «1 878 · 138 → 0» |

`ledger_batch` always read the spec, so **running the documented command reproduced the
second pair and not the first.** Both sets of numbers are correct; only the re-derivation
path was ambiguous — which is exactly what GATE A forbids.

Fixed additively: **`--population spec|all-tsl`**, default `spec` so no existing invocation
changes its answer, and the population is now stamped into the output JSON and printed by
the `CONSERVATION HOLDS` line. `--population all-tsl` reproduces §7 exactly. Four tests.
**No published figure was rewritten.**

### 5.2 · Denominator hygiene, observed but not a defect

- The consolidated report writes «DIGIT LOSS **312 (57 %)** vs SEGMENTATION **196 (36 %)**»
  **without its denominator**. The census document states it (548, the unreadable
  population, not the 784 regions and not the 336 of round 5). **The number is right; the
  sentence is not portable.** State the denominator wherever the share travels.
- WS-D's «why blocks are withheld» table is a **multi-label** census: 124 blocks carry more
  than one reason, so the rows sum to more than the withheld total. Each row is correct as
  «distinct blocks carrying this reason»; **the column must never be summed.**

---

## 6 · Numeral collisions — different populations wearing the same number

Not errors. Traps, recorded so the next reader does not walk into one.

| numeral | population A | population B |
|---:|---|---|
| **238** | SGK **books** with a parseable TOC / shelf rows in the 12 packs (`PACK_BOOK_ROW_COUNT`) | TC-v2 repaired-ranged **lessons** in six Science books — the denominator of round 6's Learning View census |
| **207** | seven-family `ACTIVITY_LEAF_COUNT` **after** the §3 fail-closed change | the six-book **canonical lesson** count in `METRIC-DENOMINATORS.md`; and the pre-change non-Toán activity subtotal |
| **41** | `toanExercises` upstream leaf records | `math_guard` withheld blocks in the 238 TSLs |
| **10** | `toanExercises` container keys | lessons whose exercise list emptied |

**Always write the unit.** A numeral without one is a rumour.

---

## 7 · Status — PLANNED vs ACTUAL

| # | planned | status | actual |
|---|---|---|---|
| D1 | the permanent rule, enforced | **DONE** | §0; enforced by `count_leaves()` raising, by 36 tests, and by `cli.py verify` exiting non-zero |
| D2 | Metric Definition Registry under `tool/metrics/**` | **DONE** | 18 metrics, nine fields each, runnable re-derivation each; **18/18 re-derive** |
| D2a | `TOAN_EXERCISE_LEAF_COUNT` · `ACTIVITY_LEAF_COUNT` · `LESSON_KEY_COUNT` · `ACTIVITY_FAMILY_COUNT` | **DONE** | all four defined, plus 14 evidence-supported companions |
| D3 | resolve or deprecate «total activities» | **DONE** | §3 — 248 SUPERSEDED · 217 DEPRECATED (unit error) · 161 DEPRECATED (undeclared subset) · the phrase itself DEPRECATED |
| D4 | the incident as a committed regression, general | **DONE** | §4 — blocked route + leaf route + shape-change refusal + an AST lint over all of `tool/`, mutation-checked |
| D5 | sweep round 6's important derived numbers | **DONE** | §5 — ten items; nine PROVEN, one FALSIFIED (the original incident); one re-derivation defect found and fixed |
| D6 | new wrong numbers reported as `HISTORICAL CORRECTION`, originals left standing | **DONE** | §4.1 — two live round-3 occurrences; nothing rewritten, nothing silently repaired |

**GATE A · METRIC TRUTH.** No ambiguous major metric remains: «total activities» is
deprecated with all three values ruled on, and every critical total in §2 and §5 is
re-derivable from leaf records by a committed command. **Met, with §4.1's two round-3
census defects left open as reported findings under another owner.**

### PROVEN
The ten sweep verdicts in §5. The four lesson denominators are one population under four
grouping keys. `sourceAssets` is 36 rows and 3 assets. 41 upstream Toán records, all
`INFERRED`, 0 shipped — a decision, not a loss. Two live round-3 container-shape defects.

### FALSIFIED
«10 toanExercises» (it is 41). «`41 → 0` is NOT CAPTURED» (it is settled and re-derivable
today). «`3 679` and `3 650` are two figures awaiting reconciliation» (one population, two
grouping keys). «`ledger.py audit` reproduces round 6's §7 accounting totals» (it did not,
until §5.1).

### STILL HYPOTHESIS
That `ACTIVITY_LEAF_COUNT`'s seven-family definition is the one the **product** wants — the
registry records both sets rather than ruling, because that is a Founder question.
That the 238 extra bridge blocks in ⑦ are one `sourceRef` per lesson (the arithmetic closes
exactly; the mechanism is INFERRED, not read). That the two round-3 census defects changed
no downstream decision — the outputs were published and were **not** re-run here.

### Not for this workstream
`tool/corpus/thresholds/**` (WS-T) · `lib/**` and the 118-block model gap (WS-S) ·
round-6 debt (WS-R) · merge debt (coordinator).
