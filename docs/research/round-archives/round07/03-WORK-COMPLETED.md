# 03 · WORK COMPLETED — four workstreams, what each built, and its PR

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

---

## 0. The PR table — four open, none merged, no threshold activated

*(**PROVEN** — GitHub API, 2026-09-06; raw output in `evidence/round7-pull-requests.json` and
`evidence/round7-ci-status.txt`.)*

| PR | Branch | Head *(re-resolved)* | Workstream | CI | State |
|---|---|---|---|---|---|
| **#94** | `ws-m/round7-metric-truth` | `a6cae3b` | M · metric truth | **PASS** | **OPEN** |
| **#95** | `ws-s/round7-structured-gap` | `36e4c50` | S · structured gap | **PASS** | **OPEN** |
| **#96** | `ws-t/round7-trust-calibration` | `5e706c9` | T · trust calibration | **PASS** | **OPEN** |
| **#97** | `ws-r/round7-debt` | `7d37521` | R · round-6 debt | **PASS** | **OPEN** |

Plus **#89–#93** (round 6), **#79–#88** (round 5) and **#73** (round 4) — **all re-checked in the
same pass, all still OPEN with `mergedAt: null`.**

---

## 1. WS-M — METRIC TRUTH · PR #94 · **DONE, GATE A MET**

**Built:** `tool/metrics/**` (new — `metric_registry.py`, `metric_leaves.py`,
`metric_container_lint.py`, `cli.py`), `tool/tests/test_metric_registry.py`, plus a fix inside
`tool/corpus/accounting/ledger.py`.

**The permanent rule, now enforced in code rather than asserted in doctrine:**

> **No important derived metric is accepted unless it can be re-derived from leaf records.**

**The registry:** 18 metrics, nine fields each — semantic quantity · unit · leaf population ·
grouping key · denominator · aggregation · exclusions · source artefact/version · **a runnable
re-derivation command**. `verify` on the 2026-09-06 artefacts: **18 of 18 re-derive to their
recorded values.**

**Re-derivations that landed exactly** *(MEASURED)*: the recognition REGION census — `312 DIGIT
LOSS (0.569) · 196 SEGMENTATION (0.358) · 40 FRACTION STRUCTURE (0.073)` **of 548** — re-derived
from the 784 leaf rows **to four decimals**; and WS-D's census — 238 lessons · 11,971 TSL served ·
2,032 withheld · 3,864 figures — re-derived from the 238 TSLs, **all four exact**.

**«Total activities» resolved by deprecation** — see `02-PLAN-VS-ACTUAL.md` §2. The phrase itself
is deprecated. **A container lint now makes the `len()`-on-a-dict defect fail by name.**

**And WS-M applied its own rule to itself:** a defect it found in its own path was recorded as
*«not re-derivable — itself a GATE A violation inside the workstream that owns GATE A»*, rather
than quietly fixed.

---

## 2. WS-T — TRUST CALIBRATION · PR #96 · **DONE; GATES B and C MET, D NOT ATTEMPTED**

**Built:** `tool/corpus/thresholds/**` — `policy.py`, `derive.py`, `candidates.py`, `freeze.py`,
`population.py`, `apply.py` (inert), `audit_sheet.py`, `measure.py` — and the five frozen payloads
now archived at `metrics/frozen-calibration/`. **52 new tests.**

> **NOTHING WAS ACTIVATED. NO THRESHOLD WAS APPLIED. NO CONTENT WAS ADMITTED.** `trusted` is still
> 0, and this workstream **added no code path that could change that** without a Founder approval
> artefact naming a frozen policy by hash.

### The design guarantee

**`TRUST = SERVED ∩ admit(…)`**, so **`trusted ⊆ served` by construction**. Activation **cannot
serve one block** the pipeline withholds today; round 6's byte-identical served set survives it;
**no waiver can manufacture trust.** Property-tested over randomised rows and asserted again on
`apply.py`'s output. **[TV]**

### The order, provable by artefact

*(PROVEN — the archive builder read `LEDGER.jsonl`: three lines and no more.)*

```
seq 1  policy      0dfc5032…                       frozen 06:41:54Z
seq 2  population  dbadf4ad…  binds 0dfc5032…      frozen 06:47:21Z   (BLIND-CORE)
seq 3  population  69d1cacc…  binds 0dfc5032…      frozen 06:47:21Z   (BLIND-TEACHING)
```

**No `approval` entry. No `admitted` entry.** The chain **refuses at write time** to freeze a
population before a policy, or an admitted set before an approval — and **an `admitted` write with
no recorded approval is refused with a `PermissionError`**, confirmed adversarially by the
coordinator. *It is a refusal, not a discouragement.*

### What was measured, and it is the round's result

- **All 12 teaching-critical errors fall into exactly two mechanisms** — digit corruption (6) and a
  non-question served as a question (6). **3 of the 6 digit corruptions survive character-exact
  agreement between two independent OCR stacks**, the role-confidence floor, the figure refusal,
  the order check **and** the subject exclusion. **They pass everything.**
- **No signal combination bounds teaching-critical error below ≈0.021** at any coverage — 0.0233 at
  36 % of served, best 0.0213 at 53 %.
- **The child-facing consequence:** at that rate and 30 trusted blocks per lesson,
  **P(≥1 teaching-critical error) ≈ 0.48** — **under an assumption of independence**, stated as an
  assumption. Measured at page level: **0.1026 observed vs 0.0975 expected** on 39 pages carrying 4
  events — **no measurable clustering at this n**, and far too few events to detect it either way.
- **No single false-trust number exists for this system** — the same quantity measures **0.073 ·
  0.090 · 0.365 · 0.650 · 0.727** across five annotated populations, and the reference and audit
  planes **do not even agree on whether teaching-critical error is a subset of false trust.**
- **The derivation reproduces round 5's published baseline exactly** — 643 rows, 354 served,
  coverage 0.5505, 26 wrong, FTR 0.0734 — **asserted as a test**, so the candidates are
  re-decisions of a published scoreboard rather than a new measurement.

### The recommendation, with its own prediction sealed in

**C2 · PROSE under BOUND-2** — 90 % of lessons clean ⇒ per-block teaching-critical ≤ **0.0035**,
audit ≥ **1,092 rows**. **The recommendation carries its own predicted outcome — a TRUTHFUL ZERO —
and that prediction is sealed inside the frozen payload, so it cannot be revised after the result
is known.**

**BOUND-4 is the only passable bound, and its consequence — 45 % of lessons carrying a
teaching-critical error — is «not sayable to a parent».** If a non-zero result is required, the only
honest route is **BOUND-5: per-lesson certification of a bounded slice. That is not a threshold and
must never be reported as one.**

---

## 3. WS-S — STRUCTURED CONTENT GAP · PR #95 · **DONE, with S5 PARTIAL**

**Built:** `tool/corpus/structured_gap_census.py`, `BlockGroup` in `lib/core/lesson_model/`, group
machinery in the bridge — **both switches off by default.**

> **NOTHING BECAME SERVABLE.** With both switches off, all **238** lessons emit **byte-identical**
> documents to the pre-change bridge — **0 differences, measured, not asserted.**

### The one-sentence answer

Of the 118, **a servable type is recommended for none of them** — and the same investigation found
that **31 mutilated structures are served to children today**, two of them multiple-choice
questions, **one mutilated by this very type gap.**

| variant | mutilated | served | blocks un-withheld |
|---|---|---|---|
| **TODAY** | **31** | 11,833 | 0 |
| `+option` | 30 | 11,837 | 4 |
| `+activity` | **31** | 11,883 | 50 |
| `+footnote` | **31** | 11,897 | 64 |
| `+all three` | 30 | 11,951 | 118 |
| **TODAY + group rule** | **0** | 11,761 | 0 |

**Adding all three types removes one of thirty-one. The group rule removes all thirty-one and needs
no new type at all.** Re-derived two independent ways — arithmetic on a disposition table, then the
bridge run over all 238 lessons — **and the two paths agree exactly.**

### The `option` finding — three independent reasons not to add the type

**(a) It converts a LOUD mutilation into a QUIET one.** Today a child sees four blank cards under a
question, then «Hãy chọn đáp án đúng nhất.» — visibly broken. With the type, the day a threshold
withholds one option of four the app serves **a three-option question that looks complete.** *The
type does not remove the danger; it removes the evidence of it.*

**(b) The option letters were never covered by the agreement score the trust gate reads.** *(PROVEN
from the artefact and the source order.)*

```
text_docling : "Kim loại và phi kim"          ← the primary stack's output
text         : "A. Kim loại và phi kim"       ← after enumerator restoration
enumerator_restored : true
agreement    : {"text_sim": 100.0, ...}
```

`agreement()` runs at `tc2_sdm.py:1193`; the enumerator is prepended at `:1221` — **after**. So
`text_sim = 100.0` certifies the option's *words* and says **nothing about the «A.»**.
**On a multiple-choice question the letter IS the answer's identity, and it is precisely the part
no agreement measurement covers.**

**(c) The two stacks do not agree on the order of options C and D, and no guard fired.** Verifier
ids align **c005, c006, c008, c007**; option C and the trailing directive both align to `c008`;
`order_ok` is `true` for every one and `agree_order` did not fire. A **2×2 grid** — the two-column
linearisation hazard round 5 measured. *(OBSERVED — `verifier_pos` is not persisted, so WS-S marked
this OBSERVED rather than PROVEN, which is the right call.)*

**The recommended order is explicit: rule first, letters brought inside the agreement measurement
second, type last — and the type is a Founder gate either way.**

### `footnote` — 64 blocks · **RECOMMEND AGAINST**

Only **10 of 64** have a machine-resolvable referent in text a child can see. **34** have a
well-formed «(N)» mark; **14 have the mark itself OCR-mangled**; 12 are «(\*)»; 4 have no mark.

**And a large part of the bucket is not footnotes at all**: five blocks are the **procedure steps of
an experiment** — *with their reading order inverted, step (4) before step (3)* — six are a **figure
callout legend**, three more are figure callouts, one is **a chemical equation whose subscripts OCR
destroyed**. **A role error is the one thing a new block type cannot fix — it renders the mistake
more confidently.**

*A negative kept with its evidence:* `footnote ⊂ referent` is a **fifth group kind that does not
exist**, and it is the right shape for this content — **but the anchor resolution it needs measures
10/34 = 0.294** and cannot be attempted on the other 30. **Recorded as a measured negative, not as
future work with a number attached to it.**

### `activity` — 50 blocks · **it IS a mapping gap · DEFER, with a named precondition**

The brief's hypothesis is **confirmed**: the block type exists and already carries **2,887** blocks;
the TSL role literally named `activity` has **no `ActivityKind` member**, and that is the entire
gap. **It is the only one of the three that is genuinely cheap.**

**And it is still deferred, for one measured reason: five of the fifty are the publisher's
colophon** — «Trình bày bìa: NGUYỄN BÍCH LA» — in five books. **That is round 5's defect 6, unfixed,
sitting inside the bucket.**

| where imprint text sits | blocks | **served to a child today** |
|---|---|---|
| role `heading` | 17 | **yes** |
| role `body` | 5 | **yes** |
| role `activity` | 5 | no — withheld by the type gap |

**22 back-matter blocks already reach children as headings and paragraphs.** **Precondition:**
defect 6 closed at the lesson boundary, or an explicit back-matter exclusion.

### And the reason code still lies — deliberately not changed

`unknown_role:footnote` says «the machine does not know what this is» about a block whose role the
machine assigned **at confidence 0.90 by lexicon** — the sin round 6 named for `formula`. **WS-S did
not apply the fix, for a measured reason:** renaming to `no_carrier:*` drops those blocks through to
the default child-facing wording **«SAM chưa chắc đọc đúng»**, which asserts an OCR doubt that does
not exist (`text_sim` median 100.0). **Changing the reason without changing the wording makes the
child-facing text less truthful, not more.** Filed as **one** coordination item, with the wording
already drafted — *not two changes in two rounds.*

---

## 4. WS-R — ROUND-6 DEBT · PR #97 · **DONE, one DEFERRED, one BLOCKED**

**30 rows triaged. Nothing dropped.** `flutter analyze` clean · Dart **1,100 passed / 2 skipped** ·
Python **756 OK / 15 skipped**.

### R-1 — the 17 crop-less gaps · **DONE at the artefact · [HU] on the device**

**The root cause was structural, not an oversight.** `tsl_projection.py --lesson-document` is the
**only** path that stamps the full repair chain — and it called the bridge with **no `crops=`
argument**. The other path, `golden_delivery.py --tsl`, renders crops and stamps **no** repair
chain. **Round 6 faced a forced choice between lineage and page images, chose lineage — correctly —
and the choice was not visible as a choice from inside either tool.**

**And the gate that should have caught it was vacuous:** L5 checked *«every crop a block
REFERENCES exists»*, so a document referencing none printed **`0/0 present · PASS`**. **The gate was
green precisely because the thing it guards was missing.** Fixed by **L5b CROP COVERAGE**, which
measures the *population* — every withheld region with a page and bbox must carry a crop —
FAIL when missing, and `--allow-missing-crops` downgrades to **UNKNOWN, never to PASS**.

*(PROVEN by the archive builder from the bytes: 17 of 17 withheld regions carry a crop; 22 crops on
disk; 5 figure `ImageBlock`s carrying no text; **withheld and served-text id sets identical to round
6**; `trusted 0`; 6/6 repairs `servable: false`.)*

**L2b corrected, not loosened.** Two hash methods legitimately coexist (bytes vs canonical JSON), and
L2b compared one string to one — **failing on a document built from exactly the TSL it demanded**. A
cross-method match is now accepted **only when both sides are digests recomputed this run from the
file at `tslPath`**, and the row **names which method each side used.**

### R-2 — the Next Action contradiction · **DONE · [HU]**

**One mistake wearing two faces: a trace of what was OPENED read as evidence of what was LEARNED.**
R5's only evidence was `viewsSeen`, set **the instant a tab is entered**; Bài 8's timeline is
honestly withheld so it has **one** available way of learning; opening it covered the set on the
first tap. **The file's own header already said `viewsSeen` is «DẤU VẾT UI … không phải bằng
chứng». The rule read it as evidence anyway.**

Fixed: R5 yields `keepGoing`, says «đã **mở**» not «đã **đi qua**», states plainly that opening is
not understanding, and **never instructs leaving**. The only path on which SAM proposes another
lesson remains **evidence that has been marked.** The «Đã mở» row now **names the ways the lesson
lacks** instead of drawing «○» for things that do not exist.

**The load-bearing test is structural, not a keyword check** — round 6 established a keyword canary
fires on real book text and guards nothing. **4 lesson shapes × 4 evidence standings × all 8 subsets
of `viewsSeen` = 128 cases, swept not sampled.** The on-screen test **counts ●/○ marks against the
number of available ways.**

### R-3 — the lowercased proper noun · **DONE · [HU]**

**Confirmed a display defect, not data** *(and the archive builder re-confirmed it: the fixture's
title carries the capital B)*. `titleCase` lowercased the **whole string** then re-capitalised
sentence starts — written for ALL-CAPS titles, **its precondition never checked.**

**The correct rule already existed in the repo, in one of seven places.** `source_sheet._humanCase`
guarded on `s == s.toUpperCase()`; six other sites called `titleCase` directly. There is now **one**
rule, and a source test forbids a second.

### R-4 — `si_expected_exponent` · **ANSWERED; the premise was wrong**

| population | count | what it is |
|---|---|---|
| lines printing **no** SI relation | **166** | **inapplicable — the correct answer, and not an abstention** |
| lines printing one where the recogniser read **nothing** | **5** | **nothing to check. The validator was never asked.** |
| lines printing a **negative** relation | **1** | declined **on purpose** — a bare-digit reading cannot carry a minus |

**Two real defects fixed:** an anchor `^\s*1\s*` that contradicted the function's own docstring and
discarded a mid-sentence relation (applicable rows **4 → 5**); and a `run` that recorded
`NOT_APPLICABLE` whenever the recogniser produced no candidate, **conflating «no relation printed»
with «nothing to check» — one bucket carrying two causes, which is exactly how round 6's sentence
went wrong.** `validate` is now four-valued and every row carries `si_applicable`, **the denominator
the rate must be read against.**

**It remains at 0 PASS and 0 FAIL, and nothing here moves that** — firing it needs a digit recovered
on one of those five lines, and round 6 measured all five unreadable at every scale. **→ R-5.**

### R-5 — recognition generalisation · **DEFERRED, with a protocol rather than an intention**

**Round 7 has four workstreams and none of them is recognition.** *An item with no owner and no
budget is deferred, not scheduled.*

**And the deferral came with the finding that makes it measurable later:** four of round 6's five
recall numbers have **a denominator containing regions the recogniser is defined to refuse.** *A
rate whose denominator includes the out-of-scope population is not a generalisation measure; it is a
measure of how the detector was pointed.* The **POPULATION CONTRACT** — two denominators
(`DETECTED` / `APPLICABLE`), a scope predicate that is **code, hashed before the draw**, a control
set in every draw, and `APPLICABLE` established by hand **before** scoring — is specified in full.

---

## 5. The composition check — third round running

Verified in a throw-away worktree, all four branches merged. **The Golden #1 fixture was
REGENERATED inside the composed tree, never rsynced** — see `04-…` §8.

| Check | Result |
|---|---|
| Git merge, 4 branches | **0 conflicts** |
| Fixture regeneration in-tree | **L5b 17/17 · VERDICT PASS · placed +22 crops** |
| `flutter analyze` | **No issues found** |
| Python suite | **866 tests OK** (18 skipped) |
| Dart suite | **1106 tests — All tests passed** |

**It did not compose on the first attempt, and the failure was the best possible one** — §7 of
`04-FAILURES-AND-FALSIFICATIONS.md`.
