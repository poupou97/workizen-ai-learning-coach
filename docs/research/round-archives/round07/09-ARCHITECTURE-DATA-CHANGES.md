# 09 · ARCHITECTURE AND DATA CHANGES

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**None of these changes is merged, and no threshold was activated.**

---

## 1. NEW SUBSYSTEMS

| Subsystem | Path | WS / PR | State |
|---|---|---|---|
| **Metric Definition Registry** + container lint + regression baseline + anti-rot guard | `tool/metrics/**` (new) | M · #94 | **DONE — 18/18 re-derive** |
| **Trust calibration**: policy, derivation, candidates, freeze chain, blind populations, audit sheet, measurement | `tool/corpus/thresholds/**` + `frozen/**` | T · #96 | **DONE — frozen, inert, refusing** |
| **`BlockGroup`** + structural-group machinery + the all-or-nothing sibling rule | `lib/core/lesson_model/`, the bridge | S · #95 | **PARTIAL — built and switched OFF** |
| **Crop rendering on the repair path** + **L5b CROP COVERAGE** + **L2b** hash reconciliation | `tool/corpus/repair/tsl_projection.py`, `tool/evidence/fixture_lineage.py` | R · #97 | **DONE** |
| **One lesson-title casing rule** where there were seven call sites | `lib/core/display/lesson_title.dart` | R/S · #97/#95 | **DONE** |
| **Four-valued `si_expected_exponent`** + `si_applicable` denominator | `tool/corpus/repair/validators/**` | R · #97 | **DONE — still 0 PASS / 0 FAIL** |

---

## 2. THE TRUST GATE — built to refuse, not to be trusted to behave

**`TRUST = SERVED ∩ admit(…)`.** `trusted ⊆ served` holds **by construction**, so:

- **activation cannot serve one block** the pipeline withholds today;
- **round 6's byte-identical served set survives activation**;
- **no waiver can manufacture trust.**

Property-tested over randomised rows, and asserted again on `apply.py`'s output. **[TV]**

### The freeze chain is an append-only artefact, not a convention

| seq | kind | sha256 | binds policy | frozen (UTC) |
|---|---|---|---|---|
| 1 | **policy** | `0dfc5032…` | — | **06:41:54Z** |
| 2 | **population** BLIND-CORE | `dbadf4ad…` | `0dfc5032…` | **06:47:21Z** |
| 3 | **population** BLIND-TEACHING | `69d1cacc…` | `0dfc5032…` | **06:47:21Z** |

**Three entries. No `approval`. No `admitted`.** *(PROVEN — the archive builder read the file.)*

**It refuses at write time**: a population cannot be frozen before a policy; an admitted set cannot
be frozen before an approval; **an `admitted` write with no recorded approval raises a
`PermissionError`** — confirmed adversarially. *And it refuses any payload naming a lesson identity
in an admission context.*

> **The policy exists six minutes before the populations, and both populations carry the policy's
> hash. That ordering is Gate B, and it is a property of a file rather than of a promise.**

---

## 3. THE STRUCTURED-GAP MACHINERY — built, measured, and deliberately inert

**`BlockGroup`** in `lib/core/lesson_model/` plus group machinery in the bridge, **both switches off
by default**. With them off, **all 238 lessons emit byte-identical documents** — *0 differences,
measured, not asserted.* `ROLE_MAP` **untouched**; `LessonBlock.knownTypes` **unchanged**; **the
group rule can only ever withhold.**

**What the rule would do:** **31 mutilated structures → 0**, at **72 blocks** (served 11,833 →
11,761). **Adding all three block types instead removes 1 of 31.**

**Why it is off:** switching it on removes 72 blocks a child reads today — *the same shape of trade
as round 6's lost timeline, and the same person's decision.*

### And a sequencing rule that came out of the measurement

> **rule first · option letters brought inside the agreement measurement second · type last — and
> the type is a Founder gate either way.**

Because with the rule *and* the type, the MCQ becomes a complete, served, four-option question
**whose four option letters are outside every measurement the trust gate makes** (§4 of
`04-FAILURES-AND-FALSIFICATIONS.md`). **The rule is a precondition, not a sufficient condition.**

---

## 4. THE LINEAGE GATE — a vacuous check replaced by a population check

| | before | after |
|---|---|---|
| **L5** | *«every crop a block REFERENCES exists»* → a document referencing none printed **`0/0 present · PASS`** | unchanged, but no longer load-bearing alone |
| **L5b CROP COVERAGE** | — | **every withheld region carrying a page and bbox must carry a crop.** **FAIL** when missing; `--allow-missing-crops` downgrades to **UNKNOWN, never to PASS** |
| **L2b** | compared one hash string to one — **failing on a document built from exactly the TSL it demanded**, because two hash methods legitimately coexist | a cross-method match is accepted **only when both sides are digests recomputed this run from the file at `tslPath`**, and the row **names which method each side used** |

**The root cause R-1 fixed was structural, not an oversight:** `tsl_projection --lesson-document` is
the **only** path that stamps the full repair chain, and it called the bridge with **no `crops=`
argument**; `golden_delivery --tsl` renders crops and stamps **no** repair chain. **Round 6 faced a
forced choice between lineage and page images, chose lineage — correctly — and the choice was not
visible as a choice from inside either tool.** Now one path does both.

---

## 5. DATA CHANGES

| Change | Amount | Note |
|---|---|---|
| **Golden #1 regenerated** | 52 → **57 blocks** | **+5 figure `ImageBlock`s carrying no text**; withheld and served-text id sets **identical**; `trusted` still 0 *(PROVEN)* |
| **Page crops placed** | 0 → **22** | 17 withheld-region + 5 figure. **[LB] — verbatim SGK page images, D4** |
| `bookTitle` / `subject` shortened (WS-D's **G2**) | 1 field | «Lịch sử và Địa lí 5» → «LS&ĐL 5», by defaulting `book_meta` to the curriculum structure |
| **Served content** | **unchanged, everywhere** | 238/238 documents byte-identical; no threshold applied; **nothing became servable** |
| **`trusted`** | **0 → 0** | asserted in code, not measured |

**Round 6's report and its v2 archive are unchanged.** Corrections are recorded **beside** them as
C1–C5 in `ROUND7-HISTORICAL-CORRECTIONS.md`.

**One correction is a live assertion rather than a note:** the round-3 census scripts were repaired,
so **the published round-3 census outputs are no longer reproducible from the fixed code** — filed
in `REPAIRED_FINDINGS` on the principle that **a repair is also a change to what old numbers mean.**

---

## 6. ARCHITECTURE PRECEDENTS — carried forward and extended

**Carried:** no constructor from a presentation form · identity redaction at the render boundary ·
grounding may never strengthen across a round trip · a plugin loader must fail loudly · a test must
assert the honesty property, not the data shape · **re-derive a number a second way before recording
a disagreement** *(which caught two findings inside this round)*.

**Added by round 7:**

1. **No important derived metric is accepted unless it can be re-derived from leaf records.**
   Enforced by a registry with **a runnable re-derivation command per metric**, a **container lint**
   that makes `len()`-on-a-keyed-container fail **by name**, and an **anti-rot guard** requiring a
   disappeared baselined finding to be removed **in the same commit**.
2. **Order is proved by artefact, not asserted by prose.** A hash chain that **refuses at write
   time** beats a documented procedure. *A policy chosen after seeing the admitted set is not a
   policy, it is a selection.*
3. **A gate must measure its population, not its references.** L5's `0/0 PASS` is the general
   failure: **a gate can be green precisely because the thing it guards is absent.**
4. **A metric must be able to distinguish «not applicable» from «not asked».** One bucket carrying
   two causes produced a wrong published sentence.
5. **A test's population must contain the case the rule is about.** *The tests were not missing; the
   populations were.*
6. **An activation precondition should be a function, not a promise** —
   `titlesLosingCapitals(transform, titles)` must return empty on the real population.
7. **Deferral requires a protocol, not an intention.** R-5 is deferred **with a population
   contract**: two denominators (`DETECTED` / `APPLICABLE`), a scope predicate that is **code,
   hashed before the draw**, a control set in every draw, and `APPLICABLE` established by hand
   **before** scoring.

---

## 7. WHAT DID **NOT** CHANGE — and why that is correct

- **No threshold activated**, and there is **no code path in any round-7 branch that could activate
  one** without an approval artefact naming a frozen policy by hash.
- **Nothing became servable.** 238/238 byte-identical; the group rule **can only withhold**.
- **`ROLE_MAP` untouched**; no block type added; `unknown_role:*` **deliberately not renamed** —
  because renaming it without changing the child-facing wording would make that wording **less**
  truthful, asserting an OCR doubt that does not exist (`text_sim` median 100.0). **Filed as one
  coordination item with the wording drafted, not as two changes in two rounds.**
- **No rich text.** 0 of the **162** Dart files under `lib/` use `RichText` or `TextSpan`. **A
  `footnote` type would render as a paragraph that has been moved — a presentation form becoming
  structure**, which round 6 forbade explicitly.
- **`LessonDocument.titleCase` still exists** but is now **unused outside its own file** and guarded
  by a source test. **HO-1: it should delegate or go — one line, and it belongs to another
  workstream's file.** *Recorded rather than reached across a boundary for.*
- **The two hash methods still coexist.** L2b reconciles them **for the same file**; **nothing has
  decided which is canonical** — filed as **N-3**, a version-identity question.
- **`rederive_trust` still does not pass `formula_structured`** — pre-existing, fail-closed,
  reassigned, **not silently fixed**.
