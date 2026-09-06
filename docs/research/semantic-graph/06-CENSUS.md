# Lane E1 · P0.3 — the K-12 semantic/visual census, with honest tiers

Reproduce: `python3 tool/semantic/census.py` → `poc-out/round5/semantic/census-{rows,summary}.json`.
No LLM was called. Every number below is a deterministic rule over corpus data.

---

## 0. ⚠️ A denominator contradiction — REPORTED, NOT FIXED

`poc-out/k12-census-exports/all-lessons.csv` has **3,679 rows** but only **3,240 distinct
`(sourceDocumentId, lessonNo)` identities**: **154 keys are duplicated across 439 rows**, almost
all title-less rows in GDTC / Âm nhạc / Mĩ thuật-style books (e.g. `01-sgk-giao-duc-the-chat-1`
lesson 1 appears **7 times**).

A *per-lesson* census can only address the 3,240. So:

- **3,679 canonical rows** stays D5's product-coverage denominator. This lane does not change it.
- **3,240 distinct lesson keys** is the denominator of every per-lesson rate in this document,
  and it is stated on every one.

Per workspace rule 5 this is reported rather than resolved. It is a Founder gate: either the
duplicates are real distinct lessons that need a compound key, or the canonical count is inflated
by 439.

---

## 1. Denominators

| id | value | what it counts |
|---|---:|---|
| canonical rows | **3,679** | rows in the canonical export (D5) |
| **censused lessons** | **3,240** | distinct `(book, lessonNo)` — the denominator below |
| units-backed | **1,784** | censused lessons with role-tagged line units (`poc-out/units-k12/`, SGK only) = **55.1 %** of 3,240 |
| TSL-backed | **224** | censused lessons with a Trusted Structured Lesson = **6.9 %** of 3,240 |

The 224 is smaller than the 238 Science TSLs on disk because **14 TSL lessons are not in the
canonical list at all** — an independent confirmation of the known canonical shortfall for
KHTN 7/8 recorded in `METRIC-DENOMINATORS.md`.

---

## 2. Tiers

| tier | lessons | % of 3,240 | meaning |
|---|---:|---:|---|
| **A** source/semantic evidence strong | **222** | 6.9 % | a TSL exists; claims built from trusted blocks |
| **B** candidate / hypothesis | **368** | 11.4 % | line-level units only; cues only |
| **C** insufficient source | **1,384** | 42.7 % | no units and no TSL — nothing to read |
| **D** domain extension required | **1,266** | 39.1 % | has source, but its object needs a node the core lacks |
| **E** exception / unknown | see §6 | | clustered rather than counted as a residue |

**42.7 % of the corpus has no readable source at all.** That is the largest single number in this
census and it is not a grammar problem — see §6.

---

## 3. The six ladder levels — SEPARATE counts, never summed

### 3.1 REPRESENTABLE — a family cue appears (denominator: 1,784 units-backed)

A cue match is a **hypothesis about the content**. It is not extraction and never becomes one.

| family | lessons | % of 1,784 |
|---|---:|---:|
| QUANTITY | 1,245 | 69.8 % |
| LABELED_FIGURE | 1,015 | 56.9 % |
| HIERARCHY | 960 | 53.8 % |
| COMPARISON | 960 | 53.8 % |
| DEFINITION | 939 | 52.6 % |
| CAUSAL | 745 | 41.8 % |
| PROCESS | 654 | 36.7 % |
| TIMELINE | 484 | 27.1 % |
| SPATIAL | 248 | 13.9 % |

- **1,404 of 1,784 (78.7 %) show cues for more than one family** — multiple visual patterns per
  lesson is the norm, not the exception.
- **130 of 1,784 (7.3 %) show no cue for any family.**

### 3.2 EXTRACTABLE — the arity was actually BUILT (denominator: 224 TSL-backed)

| family | lessons | % of 224 |
|---|---:|---:|
| HIERARCHY | **204** | 91.1 % |
| DEFINITION | 154 | 68.8 % |
| PROCESS | 104 | 46.4 % |
| CAUSAL | 85 | 37.9 % |
| LABELED_FIGURE | 75 | 33.5 % |
| TIMELINE | 3 | 1.3 % |
| COMPARISON · CONCEPT_MAP · QUANTITY · SPATIAL | **0** | — |

> **The four zeros mean "no extractor exists", not "the corpus lacks it."** The census emits
> `familiesWithNoExtractor` beside the table precisely so the zero cannot be misread. COMPARISON
> shows cues in 53.8 % of units-backed lessons and is extracted in 0 %, because E1 wrote no
> comparison rule. That is a gap in this lane, not a fact about the books.

- **220 of 224 (98.2 %) yield at least one family.** Only **4** yield none.
- **191 of 224 (85.3 %) yield two or more families.**
- Distribution: 3 families → 80 lessons · 2 → 51 · 4 → 46 · 1 → 29 · 5 → 14 · 0 → 4.

### 3.2a Grounding integrity — a check the census would not have caught

`python3 tool/semantic/verify.py integrity` re-derives every claim over all **238 TSL lessons**
and asks a mechanical question: *does each grounding point where it says it does?* The span must
lie inside its block, the recorded quote must be exactly the characters at that span, and no span
may begin or end mid-word.

| | before the fixes | after |
|---|---:|---:|
| groundings checked | 12,426 | 12,349 |
| of which carry a character span | 4,720 | 4,681 |
| **span integrity** | **0.9521** (226 failures) | **1.0000** (0 failures) |

The 226 failures were three defects, each invisible to the census because the census counts
*whether a family was built*, not *whether its evidence is sound*:

- **`e1-definition-v1`, 173 failures** — a `.strip()`ed quote paired with an *unstripped* span, so
  the recorded characters were not the characters at the recorded offsets; and a length-bounded
  group (`{6,140}`) that ends wherever the budget runs out, mid-word.
- **`e1-figure-reference-v1`, 39 failures** — «hình 1a» matched only «hình 1». That split the word
  *and* anchored the reference to figure 1 instead of 1a. Science figure numbers almost always
  carry a letter suffix, so this was wrong at scale, quietly.
- **`e1-causal-connective-v1`, 14 failures** — the same mid-word class.

**Integrity is not precision.** A claim can point at exactly the right characters and still be a
wrong claim about the lesson; row 22 of the scoreboard stays blank. But a grounding that is one
character off is not a grounding a reviewer can check at all, so this had to be 1.000 before any
precision study would mean anything.

### 3.3 GROUNDABLE (denominator: 224)

**220 / 220** of the lessons with any extractable family are groundable — by construction, not by
luck: `SourceGrounding` raises if a claim carries only a block id. On the checkpoint pair the
locator mix was **page-geometry 46 · text-span 22** (Bài 17) — i.e. **32 %** of groundings resolve
to a character span, the rest to page + bbox, which is the appropriate evidence for a figure or a
heading.

### 3.4 VALIDATABLE (denominator: 224)

**1 family** has a named deterministic validator anywhere in the repo: TIMELINE
(`timeline-order-v1`, `lib/core/lesson_model/timeline_validator.dart:55`). The other five have
**none**. So at most **3 lessons** (the TIMELINE-extractable ones) are validatable today.

### 3.5 VISUALIZABLE (renderer exists in the app today)

| family | renderer | data reaching it |
|---|---|---|
| PROCESS | `visual_view.dart:396` | real corpus, **1 lesson** |
| COMPARISON | `visual_view.dart:540` | real corpus, **1 lesson** |
| TIMELINE | `views/timeline_view.dart:22` | **synthetic only** |
| CONCEPT_MAP | `visual_view.dart:609` | **zero producers** |
| HIERARCHY · LABELED_FIGURE · CAUSAL · DEFINITION · QUANTITY · SPATIAL | **none** | — |

**HIERARCHY is the highest-yield extractable family (204 lessons) and has no renderer at all.**
LABELED_FIGURE is the highest-cue family (56.9 %) and has no renderer. Meanwhile the two families
that DO have renderers reach one lesson each. That mismatch is the single clearest instruction to
Lane E2.

### 3.6 LEARNER_READY

**0.** Not "small" — zero, by construction. Every claim is `proposed`; `status='validated'`
requires a named validator; `THRESHOLDS.json` does not exist, so `ContentTrust.trustedCorpus` is
unreachable. Round 4's Source Trust 0/97 is unchanged by anything in this lane.

---

## 4. Domain extensions — what the census actually proves

Signal: a deterministic pattern in the lesson's own text. Denominator **1,784 units-backed** for
the first three, and the whole censused set for the tier assignment.

| extension | lessons | % of 1,784 | verdict |
|---|---:|---:|---|
| **MATH_AST** | 1,182 | 66.3 % | **PROVEN NECESSARY.** Also 1,096 lessons where it is the *only* thing standing between the lesson and any representation. |
| **PHYS_QUANTITY** | 716 | 40.1 % | **PROVEN NECESSARY**, but see below — it overlaps MATH_AST heavily and may not need a separate node kind. |
| **LIT_TEXT** | 265 | 14.9 % | **PROVEN NECESSARY** and *cannot be found on the Science slice at all* — Lane C's `story-attribution-v1` is the only existing instance. |
| **CHEM_REACTION** | 139 | 7.8 % | **PROVEN NECESSARY**, small. |
| **HIST_EVENT** | — | — | **NOT PROVEN.** `Event` + `atTime` are already core and already carried LS&ĐL 5 Bài 8 at 7/7. History needs no separate graph — at most a role tag on `Entity`. |
| **GEO_SPATIAL** | — | — | **NOT PROVEN as an extension.** SPATIAL shows cues in 248 lessons but the blocker is a *renderer and a map asset*, not a missing node kind. |
| **SCI_PROCESS** | — | — | **NOT PROVEN.** `Step` + `next` + the procedural governor carried Science without an Observation/Hypothesis node. |

> **Three of seven candidate extensions are proven necessary as new NODE KINDS
> (MATH_AST, LIT_TEXT, CHEM_REACTION). PHYS_QUANTITY is proven necessary as data but is probably
> `Quantity` — already a core primitive — plus a unit vocabulary. Three are refuted: History,
> Geography and Science needed no extension at all; they needed the core plus a renderer.**
>
> That is the answer to «CORE + EXTENSIONS vs ToánGraph / HistoryGraph / ScienceGraph»: the
> subject-shaped architectures are unnecessary. What is genuinely per-domain is *notation*
> (math, chemistry) and *literary form* — not subject.

---

## 5. Subject × family and grade × family

### Cue frequency by subject (denominator: that subject's units-backed lessons)

| subject | lessons | units | FIG | HIER | COMP | DEFN | CAUS | PROC | TIME | QUANT | SPAT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Toán | 574 | 280 | 100 | 48 | 99 | 108 | 64 | 32 | 53 | **235** | 28 |
| Công nghệ | 319 | 225 | **221** | **201** | 135 | 148 | 126 | **155** | 53 | 184 | 13 |
| Tiếng Việt | 259 | 75 | 1 | 26 | 30 | 39 | 24 | 26 | 15 | 24 | 3 |
| Chuyên đề | 233 | 175 | 139 | 128 | 132 | 141 | 104 | 93 | 56 | 149 | 32 |
| Tin học | 204 | 151 | 134 | 105 | 108 | 98 | 62 | 96 | 42 | 111 | 11 |
| KHTN | 146 | 118 | 118 | 81 | 98 | 93 | 69 | 38 | 27 | 100 | 8 |
| Khoa học | 121 | 74 | 59 | 59 | 59 | 45 | 32 | 28 | 21 | 54 | 9 |
| LS&ĐL | 94 | 56 | 54 | 27 | 25 | 28 | 33 | 3 | **48** | 41 | **48** |
| Địa lí | 96 | 33 | 25 | 29 | 25 | 20 | 16 | 5 | 18 | 26 | **27** |
| Vật lí | 85 | 31 | 30 | 16 | 26 | 28 | 20 | 11 | 9 | 30 | 16 |
| **Sinh học** | **90** | **0** | — | — | — | — | — | — | — | — | — |

Two things to notice. **Công nghệ** — not Science — has the highest LABELED_FIGURE and PROCESS
cue counts in the whole corpus (221 and 155), and it has no TSL and no renderer. And **Sinh học
has 90 canonical lessons and zero units**: it is invisible to this census entirely.

### Extractable by subject (denominator: that subject's TSL-backed lessons)

| subject | TSL | HIER | DEFN | PROC | FIG | CAUS | TIME |
|---|---:|---:|---:|---:|---:|---:|---:|
| KHTN | 135 | 132 | 113 | 72 | 45 | 60 | 2 |
| Khoa học | 61 | 45 | 17 | 27 | 34 | 20 | 0 |
| LS&ĐL | 28 | 27 | 24 | 5 | 0 | 5 | 1 |

**HIERARCHY extracts at 96–98 % in every subject that has a TSL** — the single most portable
signal found, because it comes from the heading nesting the book itself prints.

### Grade × family (cue frequency, units-backed)

| grade | FIG | HIER | COMP | PROC | TIME | QUANT | CAUS | DEFN | SPAT |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | 10 | 11 | 1 | 0 | 35 | 12 | 8 | 0 |
| 2 | 11 | 19 | 19 | 10 | 13 | 58 | 17 | 25 | 2 |
| 3 | 36 | 47 | 47 | 20 | 16 | 88 | 26 | 30 | 3 |
| 4 | 54 | 41 | 41 | 35 | 30 | 57 | 35 | 38 | 26 |
| 5 | 38 | 31 | 28 | 16 | 19 | 34 | 27 | 24 | 11 |
| 6 | 96 | 78 | 86 | 52 | 41 | 106 | 53 | 74 | 10 |
| 7 | 64 | 45 | 57 | 51 | 21 | 77 | 41 | 57 | 10 |
| 8 | 77 | 65 | 65 | 52 | 44 | 85 | 57 | 63 | 28 |
| 9 | 102 | 83 | 87 | 61 | 39 | 111 | 65 | 103 | 16 |
| 10 | 187 | 185 | 185 | 133 | 90 | 212 | 140 | 181 | 65 |
| 11 | 179 | 180 | 179 | 109 | 71 | 193 | 136 | 178 | 36 |
| 12 | 166 | 176 | 155 | 114 | 100 | 189 | 136 | 158 | 41 |

The family mix is **remarkably stable across grades** — the same nine families in the same rough
proportions from grade 1 to grade 12. That is evidence for a single grammar rather than per-stage
ones. G10–12 dominate in absolute terms simply because they hold 1,601 of the 3,240 lessons.

---

## 6. How few primitives and relationships actually suffice

`DISCOVER → CLUSTER → MINIMIZE → VALIDATE`, run over the corpus (`tool/semantic/discover_markers.py`,
`probe_cues.py`, `ontology.py`).

**Six primitives** carried every lesson tested: `Entity` · `Statement` · `Step` · `Event` ·
`Quantity` · `Figure`, plus `Formula` as the carrier for validated structured notation (Lane A2's
AST, not E1's).

Refuted as primitives — each expressible by composition, and no lesson was found needing them:
`Property` (= `Entity --hasProperty--> Statement|Quantity`) · `TimePoint` (a field of `Event`) ·
`Place` (= `Entity` + `locatedAt`) · `Person` (= `Entity` + a role tag).

**Nine relations** were declared; **six carried all the measured work**. Edge counts below
are over the two distinct checkpoint lessons (KHTN 6 Bài 17 + LS&ĐL 5 Bài 8, `tc2-p1`):

| relation | edges built | verdict |
|---|---:|---|
| `hasPart` | 21 | **essential** — the highest-yield signal in the corpus |
| `next` | 13 | **essential** |
| `atTime` | 7 (carried as claims on `Event`) | essential |
| `hasProperty` | 2 | essential |
| `depicts` | 2 | essential |
| `causes` | 2 | essential |
| `isA` | 0 | **not yet separable from `hasPart`** — no rule distinguished them |
| `contrastsWith` | 0 | **unproven** — no extractor written |
| `locatedAt` | 0 | **unproven** — no extractor written |

> **Answer: 6 primitives and 6 relations sufficed for everything actually built, across two
> subjects and 224 lessons.** The three unused relations are unproven, not refuted — `isA` in
> particular may collapse into `hasPart`, which would make it **6 and 5**. Against that small core,
> **10 visual families** are projections, and 6 of them are already compiled by rules that read
> only `nodes`, `relations` and `claims`.

The Founder's candidate list was not copied: `Method`, `SkillCase`, `CurriculumEdge`,
`LearningActivity` and `ConceptMap` are all **absent** from the core, because nothing in the corpus
required them to represent what a lesson contains. They belong to the pedagogy layer (§25), which
is a different question.

---

## 7. What this census does **not** say

- It does **not** say «X % of K-12 is supported». Nothing is supported: LEARNER_READY = 0.
- It does **not** treat a cue as a capability. REPRESENTABLE (1,784 denominator) and EXTRACTABLE
  (224 denominator) are different measurements over different corpora and are never divided into
  each other.
- It does **not** measure precision. The rules were written while looking at Bài 17 and Bài 8;
  their false-positive rate on a holdout is unmeasured, and `05-KNOWN-DEFECTS.md` lists the ones
  already found by eye. **A precision study on a holdout the rules were not written against is the
  next thing this lane owes.**
- It cannot see **Sinh học** (90 lessons, 0 units) or the 1,384 tier-C lessons at all.
