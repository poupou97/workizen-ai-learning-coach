# The blind evaluation protocol — frozen population, sealed key, predeclared bound

Round 7 · WS-T · step **B**, plus the runbook for **C–E** which are **not run this round** ·
2026-09-06 · **status: FROZEN AND UNEXECUTED.**

> `python3 tool/corpus/thresholds/freeze.py verify` → the chain, and the proof of order.

---

## 1 · There was no pre-existing blind population, and finding that out is a result

The first thing this workstream looked for was an annotated population the candidate policy had
never seen. **There is not one.** Every labelled population in this repository was consumed by the
derivation:

- **The reference plane's own «held out» rows are not a holdout.** The evidence file marks 181 of
  its 643 rows `held_out: true` (a second gold set). Lane A3's **published curve was computed over
  all 643** — the baseline 354 served / coverage 0.5505 / 26 wrong / FTR 0.0734 reproduces only on
  the pooled set. Splitting it now gives 462 / 255 served / 20 wrong / 0.0784 and
  181 / 99 served / 6 wrong / 0.0606, neither of which is the published number. **Pooling them
  spent them**, and this workstream refuses to re-label them a holdout after the fact.
- **The round-3 484-row audit and both legacy batch-1 audits** are Lane A3's audit plane.
- **The 97-row independent audit** is a Founder-designated *evaluation* set — and round 5 §8.3
  went further and used its OVER/SAFE labels to **route restores**. Measured on, and acted on.

So blindness is obtained the only honest way left.

---

## 2 · What makes the frozen population blind

**It carries lesson identities and nothing else. No signals exist for it. No verdicts exist for
it. Nobody has decided anything about it.**

The pipeline runs on these lessons, and their annotation is produced, **only after approval**.
The candidate policy therefore could not have been fitted to them *even in principle*, and the
freeze ledger proves the policy hash existed first: the population entry embeds it.

Publishing the identities does not break blindness — a sample drawn without reference to any gate
outcome is publishable. What must never exist before approval is an artefact saying which of them
a threshold **admits**, and `freeze.py` refuses to record one.

### Contamination rule

A book is excluded if any artefact in this repository has **produced truth labels from it, or
tuned anything against it**: the gold pages, every annotated audit, every per-book pipeline
output directory of rounds 3–6, and the named research slices. Corpus-wide OCR and layout scans do
**not** contaminate and are not grounds for exclusion — a scan produces no truth.

**44 books excluded.** The eligible universe: **203 SGK books · 2,777 lessons · 2,536
page-anchored.**

Independent re-derivation of the Founder's two denominators from the same join, agreeing exactly
with round 6 §6: **238 SGK books with lessons · 3,679 lessons · 3,381 page-anchored.** Neither is
used as a denominator for any rate in this workstream.

### The draw

| | |
|---|---|
| **Sampling unit** | a page-anchored SGK lesson — a **cluster**, because the bound is a promise about a lesson and the within-lesson clustering of errors must be observable rather than assumed |
| **Stratification** | proportional on grade band × subject family, largest-remainder allocation |
| **Seed** | `20260906`, the date — the same convention the round-3 sampler used, and not a number anyone could have searched for a favourable draw with |
| **Size** | 120 lessons, sized from the recommended bound's requirement of ≥ 1,092 audited trusted blocks |
| **Order** | frozen with the population. A cheaper bound is evaluated on a **prefix** of that order, never on a subset chosen later |

### Two populations, both frozen before anything was applied

| | eligible pool | draw |
|---|---|---|
| **BLIND-CORE** | 2,536 lessons / 192 books | proportional over everything |
| **BLIND-TEACHING** | 1,770 lessons / 119 books | restricted to the four families the product teaches |

The second exists because of a bias worth naming: **the proportional draw is 31 % arts, music and
physical education**, since the books nobody has worked on are largely the books nobody teaches
core content from. A generalisation proved on that population would be a generalisation about the
wrong material. The restriction is stated in terms of the product's teaching scope and makes no
reference to any policy outcome; both were frozen before any application, so neither can have been
swapped in after seeing a result.

**Known weakness, recorded rather than smoothed over:** the 97-row set exists only as a published
summary table, so its rows cannot be enumerated. Disjointness from it is **argued** — its working
set was among the books already excluded — and **not proven**. This is the weakest link in the
blindness claim.

---

## 3 · Steps C–E — built, tested, and not run

### C · APPLY — `apply.py`, inert by design

Every path refuses without an approval artefact carrying `policy_sha256` matching the frozen
policy, `population_sha256` matching a frozen population, the candidate name, `decision:
"ACTIVATE"`, and who approved it and when. **A hash mismatch is a refusal, not a warning:** if the
policy was edited after approval, the thing approved is not the thing that would run.

Four further refusals, each present because it is a way this goes wrong quietly:

1. a candidate naming a clause with **no implementation** — applying it would silently admit on
   the clauses that do run;
2. an evidence row **outside the frozen population** — otherwise the population can be quietly
   widened to whatever produces a better number;
3. a row that **already carries a verdict** — truth must not exist before admission;
4. `trusted ⊆ served` is **asserted on the output**, not assumed.

### D · AUDIT — `audit_sheet.py`, a worklist and a sealed key

The annotator sees the served text and a page reference. **They do not see whether the row was
admitted.** If the sheet says «this one is trusted», every subsequent judgement is anchored and
the false-trust rate measures the anchor. Round 3 learned the weak form of this (its similarity
pre-check was «shown as a hint, never as a verdict»); round 6 learned the strong form when a
keyword canary fired on legitimate book text and taught its reader that red is normal.

The admission status goes to a **sealed key** in a separate file, joined only at measurement.
Rows are interleaved by a seeded shuffle so neither position nor order leaks the gate. A test
asserts the worklist carries no admission flag, no guard list and no role confidence.

**Both sides are audited.** Admitted rows measure false trust and teaching-critical error;
refused rows measure **over-withholding** — the larger pool in the 97-row audit (19 of 30 refused
wrongly), and the harm defect 8 identified, where withholding one member of a structure leaves the
served remainder wrong rather than merely smaller. *A protocol that audits only what a threshold
admits cannot see the harm the threshold causes by refusing.*

The six verdict fields are the round-3 false-trust audit protocol's, unchanged, so the numbers are
comparable with what has already been published rather than a new scale.

### E · MEASURE — `measure.py`, bound from the ledger

`--bound` names one of the bounds **inside the frozen policy payload** and nothing else. There is
no flag that sets a threshold value, because a bound settable at measurement time is a bound
choosable after seeing the result. The tool re-hashes the payload against the ledger and refuses
if it was edited.

Four numbers, never one:

- **false trust** among admitted rows;
- **teaching-critical error** among admitted rows, reported **separately and never summed** — on
  the reference plane 5 blocks are teaching-critical without being counted false trust at all;
- **over-withholding** among refused rows;
- **lesson incidence** — P(a lesson contains ≥ 1 teaching-critical error among its admitted
  blocks), **measured rather than extrapolated**, because errors cluster.

Every rate carries a Wilson 95 % interval and **the decision uses the upper bound.** A point
estimate of zero at small n is not evidence of zero: 0 observed in 100 gives an upper bound of
0.037, which fails a bound of 0.0035. An `UNSURE` verdict on an admitted row fails the bound too —
an undecided row is not a clean row.

### Gate C evidence — the dry run

```
$ python3 tool/corpus/thresholds/measure.py --dry-run
DRY RUN · bound BOUND-2 read from frozen policy 0dfc503266854b08… · fabricated rows only
  clean, but too small to decide       admitted=  300  tc=0.0    (<= 0.0126)  -> TRUTHFUL ZERO
  clean, audited to the required size  admitted= 1500  tc=0.0    (<= 0.0026)  -> PASS
  1 in 50 teaching-critical            admitted= 1500  tc=0.04   (<= 0.0511)  -> TRUTHFUL ZERO
  1 in 8 teaching-critical             admitted= 1500  tc=0.25   (<= 0.2725)  -> TRUTHFUL ZERO
```

One PASS and three distinct refusal modes, on fabricated rows, reading no real content and
admitting nothing. **The machinery is proven to discriminate rather than merely to refuse.**

---

## 4 · The order, and why it is provable rather than asserted

`freeze.py` keeps an append-only SHA-256 chain in which each entry carries the hash of the one
before it.

```
seq 1  policy      0dfc5032…   prev=null
seq 2  population  dbadf4ad…   prev=0dfc5032…   binds_policy=0dfc5032…
seq 3  population  69d1cacc…   prev=dbadf4ad…   binds_policy=0dfc5032…
```

An `admitted` entry claiming to precede the policy is arithmetically impossible: it would have to
contain a hash that did not exist. The ledger additionally **refuses at write time** to freeze a
population before a policy, or anything post-approval before an approval — and refuses any payload
naming a lesson or book identity in an admission context. `verify` recomputes every payload hash
and the whole chain; git commit timestamps are a second, independent witness to the same order.

Current chain: **no approval entry, no admitted entry.** A test asserts that.

---

## 5 · The runbook, for the moment approval arrives

```
# 0. verify nothing moved
python3 tool/corpus/thresholds/freeze.py verify

# 1. record the approval (freezes an `approval` entry; without it, everything below refuses)
python3 tool/corpus/thresholds/apply.py --record-approval approval.json

# 2. materialise signals for the frozen population — pipeline run, no verdicts
#    (WS-owner of the pipeline; the evidence schema is the one derive.py consumes)

# 3. C — apply the approved candidate
python3 tool/corpus/thresholds/apply.py --candidate 'C2 · PROSE' \
    --evidence <rows> --approval approval.json --out poc-out/round7/ws-t/admitted

# 4. D — blind worklist + sealed key
python3 tool/corpus/thresholds/audit_sheet.py --evidence <rows> \
    --admitted poc-out/round7/ws-t/admitted/admitted.jsonl --seed <recorded> \
    --out-dir poc-out/round7/ws-t/audit

# 5. annotate the worklist against page renders. The annotator never opens the sealed key.

# 6. E — measure against the predeclared bound
python3 tool/corpus/thresholds/measure.py --annotated <filled worklist> \
    --key poc-out/round7/ws-t/audit/SEALED-KEY.json --bound BOUND-2 \
    --out poc-out/round7/ws-t/measurement.json
```

**Stop condition, predeclared:** measured teaching-critical or false trust above the frozen bound
⇒ `trusted = 0`, `eligible = 0`, and a truthful zero is reported. Steps F and G do not follow
automatically from a PASS: a PASS means the bound held **on this population**, and is neither
permission to scale nor a claim about any lesson that was not audited.
