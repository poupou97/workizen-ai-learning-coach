# Trust-gate sensitivity — the trade-off curve, not a threshold

Round 5 · Lane A3 · Founder order §8 · 2026-09-06 ·
**status: RESEARCH INFRASTRUCTURE + MEASUREMENT. No production threshold is set, no point on the curve is
chosen, no gate is claimed to be met. `THRESHOLDS.json` does not exist and this lane did not create it.**

Round 4's answer to "what is the biggest bottleneck?" was *there is no gate to cross*: the pipeline can
measure, withhold and prove, but `trusted` computes to 0 by construction because no threshold record
exists. This document does not fix that by picking a number. It builds the instrument that makes the number
decidable, runs it, and hands over the curve.

Tooling: `tool/corpus/thresholds/` (`evidence.py` · `gate.py` · `sweep.py` · `run.py`), 25 unit tests in
`tool/tests/test_thresholds.py`, candidate scenarios in `THRESHOLDS.example.json`. Outputs:
`poc-out/round5/lane-a3/{gold,audit-round3-484,audit-legacy-b1-new}/`.

---

## 1. Method

A **gate** is a declarative predicate over signals a block already carries — its guards, the two-stack text
agreement, OCR confidence, role and role confidence, tone disagreements, and (on the audit plane) subject,
layout family and whether the row carries mathematics. It decides SERVE or WITHHOLD and nothing else. It
cannot repair, cannot learn, and cannot look at the text. That is deliberate: it makes the cost of a
decision attributable to the decision.

**Evidence rows are frozen facts, not a re-run.** `evidence.py` reads pipeline output that already exists
on disk and writes one row per block: what could be observed about it, and what is true of it.

- **Gold plane** — the 54 gold pages joined to the pipeline's own SDM blocks (`tc2-p2`,
  `poc-out/round4/pipeline/tc2-p2/sdm-gold`). Truth is `tc_score.score`'s own wrongness definition
  (character error > 10 % with ≥ 3 edits · splice · a non-question served as a question · same-column order
  inversion), reproduced **block by block** and then **asserted equal, page by page**, to the aggregates the
  scorer returns. If the two ever drift the extractor raises instead of reporting. The result reproduces the
  published round-5 baseline exactly: **643 learning blocks · 354 served · coverage 0.5505 · 26 false
  trusted · FTR 0.0734.**
- **Audit plane** — the annotated false-trust samples. Truth is the annotator's per-class verdict against a
  page render. It reproduces the published rates exactly too: round-3 484-row sample **312 / 480 = 0.650**;
  legacy batch-1 NEW **27 / 74 = 0.365**.

Populations are never pooled (D5): `run.py --filter audit_source=…` forces one sample at a time.

**The gold plane is the only plane that can measure RESTORE**, because it is the only one with ground truth
on the *withheld* side. The audit plane is almost entirely served rows, so it answers the opposite and
equally useful question: *what would this gate remove from the content the product ships today, and how
much of what it removes is actually right?*

**Two words that must not be confused.** This document uses **restored** for "a block a candidate gate would
serve that the pipeline withholds today". **Waiving a guard is not a repair.** Round 5's doctrine is
`DETECT → REPAIR candidate → VALIDATE → RESTORE or WITHHOLD`, and nothing in this simulator validates
anything. A restore measured here is a *coverage decision made against measured risk*, not a validated
repair. Lane A1's ledger is what turns one into the other; §5 says what the simulator needs from it.

---

## 2. What the guards cost, one at a time

Before any curve: what is each guard actually refusing? "Sole reason" means this guard fired and no other
denying guard did, so the block is withheld *because of it*. Clean / wrong is measured against gold —
i.e. **fidelity**, whether the served string is what the page prints.

| guard | class | fires | sole reason | sole & clean | sole & wrong | clean share |
|---|---|---|---|---|---|---|
| `agree_tones` | fidelity | 68 | 60 | **58** | 2 | 0.967 |
| `agree_text` | fidelity | 51 | 38 | **35** | 3 | 0.921 |
| `teacher_text` | **policy** | 42 | 26 | 26 | 0 | 1.000 |
| `agree_order` | fidelity | 30 | 27 | 24 | 3 | 0.889 |
| `figure_text` | **policy** | 37 | 24 | 16 | 8 | 0.667 |
| `empty_block` | structural | 14 | 14 | 10 | 4 | 0.714 |
| `agree_numbers` | fidelity | 22 | 8 | 8 | 0 | 1.000 |
| `figure_dependent` | **policy** | 14 | 13 | 8 | 5 | 0.615 |
| `math_guard` | fidelity | 15 | 8 | 4 | 4 | 0.500 |
| `answer_leak` | **policy** | 5 | 5 | 3 | 2 | 0.600 |
| `chem_guard` | fidelity | 4 | 3 | 3 | 0 | 1.000 |
| `page_feature:diagram` | **policy** | 5 | 4 | 3 | 1 | 0.750 |
| `box_boundary` | policy | 4 | 1 | 1 | 0 | 1.000 |
| `furniture` | structural | 3 | 1 | 1 | 0 | 1.000 |
| `page_feature:color_heavy` | policy | 1 | 0 | 0 | 0 | — |

`unit_guard`, `low_ocr_conf`, `line_structure` and `role_conflict` never fire on a gold learning block.

**The guards divide into two kinds and the curve must not blur them.**
*Fidelity guards* answer "is the served string what the page prints?" — waiving one is a real
coverage/accuracy trade. *Policy guards* answer "may a child be shown this at all?" — and the gold plane
**cannot answer that question**. A `teacher_text` block scores "clean" because it is a faithful copy of the
teacher's book; serving it to a child is still forbidden. Every "clean" in the policy rows means *faithful*,
never *permitted*.

**The headline number of this table: 231 of the 273 withheld matched learning blocks are clean — an
over-withhold rate of 0.846.** 215 of those 231 have gold text, so the judgement rests on a character
comparison rather than on the weaker anchor-only evidence. Round 4 measured the same thing on the legacy
batch by hand and got 12 of 30 (0.400); the gold set, being harder and more heavily guarded, is worse.

---

## 3. The curve

Coverage = served ÷ 643 learning blocks. "Wrong" = the scorer's own definition. "TC" = teaching-critical
served (the pipeline's own `corrupted_data` + `nonquestion_as_question` classes). Restore precision =
clean ÷ restored, against the pipeline's decision as baseline. Rendered charts:
`poc-out/round5/lane-a3/gold/curve-coverage-vs-ftr.svg` and `curve-correct-vs-wrong.svg`.

| gate | coverage | correct served | **wrong served** | FTR | TC served | withheld | false withheld | restored | restore precision |
|---|---|---|---|---|---|---|---|---|---|
| **pipeline today** (reference) | **0.551** | 328 | **26** | 0.0734 | 12 | 289 | 231 | — | — |
| + role-confidence floor 0.90 | 0.168 | 103 | 5 | 0.0463 | 4 | 535 | 456 | 0 | — |
| + role-confidence floor 0.70 | 0.420 | 254 | 16 | 0.0593 | 11 | 373 | 305 | 0 | — |
| + character-exact agreement | 0.502 | 301 | 22 | 0.0681 | 9 | 320 | 258 | 0 | — |
| waive `agree_tones` | 0.644 | 386 | 28 | 0.0676 | 15 | 229 | 173 | 60 | **0.967** |
| … + `agree_text` | 0.703 | 421 | 31 | 0.0686 | 16 | 191 | 138 | 98 | 0.949 |
| … + `agree_order` | 0.745 | 445 | 34 | 0.0710 | 17 | 164 | 114 | 125 | 0.936 |
| … + `agree_numbers` | 0.761 | 455 | 34 | 0.0695 | 19 | 154 | 104 | 135 | 0.941 |
| … + `math_guard` + `chem_guard` | 0.782 | 464 | 39 | 0.0775 | 20 | 140 | 95 | 149 | 0.913 |
| … + `teacher_text` (**policy**) | 0.848 | 505 | 40 | 0.0734 | 20 | 98 | 54 | 191 | 0.927 |
| … + `figure_text` (**policy**) | 0.904 | 526 | 55 | 0.0947 | 26 | 62 | 33 | 227 | 0.872 |
| … + `figure_dependent` + `answer_leak` (**policy**) | 0.933 | 538 | 62 | 0.1033 | 31 | 43 | 21 | 246 | 0.854 |
| every guard waived but the structural ones | 0.949 | 546 | **64** | 0.1049 | 31 | 33 | 13 | 256 | 0.852 |

**The shape, in one paragraph.** Coverage moves 0.551 → 0.949, a factor of 1.72. The false-trust *rate*
moves 0.073 → 0.105, a factor of 1.43. The *number* of wrong blocks a child could meet moves 26 → 64, a
factor of 2.46. Those three multipliers are the whole argument, and which one the Founder cares about is a
decision, not a measurement: a rate says the gate is barely buying accuracy for what it costs in coverage;
a count says the gate is keeping 38 wrong blocks away from a child.

**The reference point is not on the Pareto frontier.** Waiving `teacher_text` alone serves **26 more blocks
with exactly zero additional wrong ones** — by the gold plane's arithmetic, today's gate is dominated. It is
dominated by a *policy* guard, so the domination is an artefact of measuring fidelity rather than
permission. That is the sharpest illustration in this document of why the two guard classes must be
reported apart: a curve that mixes them will always seem to say "loosen".

---

## 4. Three regions worth attention (described, not chosen)

**Region I — coverage 0.55 → 0.76, wrong 26 → 34, restore precision 0.94.**
Waiving the four two-stack agreement guards. **135 blocks restored, 127 of them clean, 8 wrong.** Every
guard here is a fidelity guard, so the trade is real and legible: about 16 correct blocks recovered per
wrong block admitted. Teaching-critical served rises 12 → 19, which is the part that should give pause —
the wrong blocks admitted here are not evenly harmless. The whole of this region depends on Lane A1: it is
only reachable honestly if the tone and text disagreements are *resolved by a third signal*, not merely
ignored. Waiving `agree_tones` without a lexicon is the round-4 finding `OCR_A == OCR_B ⇏ TEXT == TRUE`
run in reverse.

**Region II — coverage 0.76 → 0.85, wrong 34 → 40.**
The elbow, and the least honest stretch of the curve. Two thirds of the coverage gained here is
`teacher_text`: 26 blocks of a teacher's book that are faithful copies and are forbidden content. The
fidelity part of this region is `math_guard` (sole reason on 8 blocks, 4 clean and 4 wrong — the only guard
in the corpus where waiving is a coin flip) and `chem_guard` (3 blocks, all clean). This is Lane A2's
region: with a structured formula representation, `math_guard` stops being a coin flip and becomes a check.

**Region III — coverage 0.85 → 0.95, wrong 40 → 64.**
Waiving `figure_text`, `figure_dependent`, `answer_leak` and the page-feature guards. Restore precision
falls to 0.85, teaching-critical served rises 20 → 31, and the FTR crosses 0.10 for the first time. Note
what is *inside* this region, though: `figure_text` alone withholds 16 clean blocks, and the role spec
(§SPEECH_BUBBLE, §FORMULA) shows what some of them are — a grade-3 word problem, two multiplication tables,
three speech bubbles carrying a Toán 5 problem's data and its question. **Region III is where the role
definitions, not the threshold, decide the outcome.** The right response to it is a better role layer, not
a looser gate.

**Two knobs that look like controls and are not.**
- **OCR confidence is dead.** Every matched gold block that carries the signal has `ocr_conf = 1.0`
  (626 of 627; one block carries none). A floor at any value between 0 and 1 changes nothing — the sweep is
  flat at 0.5505 for every setting. The signal carries no information here and must not be offered as a dial.
- **A text-agreement floor on top of today's guards buys almost nothing** — 0.551 → 0.502 coverage for
  26 → 22 wrong — because `agree_text` already encodes it categorically. Numeric floors and categorical
  guards are not additive; stacking them mostly re-withholds the same blocks.
- **Role confidence is a step function, not a dial.** The role layer emits 12 discrete confidences; the
  0.60 → 0.70 step alone removes 84 served blocks (74 correct, 10 wrong) because 0.60 is the `body`
  fallback — "we could not tell". Tightening role confidence is really a decision to stop serving blocks
  whose role is unknown, and it should be described that way.

---

## 5. What moves the curve — and what the simulator needs to get sharper

The curve is a picture of *today's* signals. Every lane in round 5 changes it.

**Lane A1 (repair framework · third signal · Vietnamese text) — the largest single mover.**
`agree_tones` is the biggest over-withholder in the corpus: 68 fires, sole reason on 60 blocks, **58 of them
clean (0.967)**. A Vietnamese lexicon that resolves tone disagreements does not "loosen" anything — it
converts a withhold-on-doubt into a decision on evidence, and moves coverage 0.551 → 0.644 in one step.
`agree_text` (35 clean of 38) and `agree_order` (24 of 27) are the next two. **What the simulator needs from
A1:** (a) a per-block **disposition** — ORIGINAL OBSERVATION / REPAIRED CANDIDATE / VALIDATED REPAIR — so a
gate can be written over *validation status* instead of over *guard absence*, which is the difference
between a repair and a waiver; (b) the **false-correction rate per signal**, so that a restored block
carries a measured risk rather than an assumed one; (c) the repair ledger keyed by the same block id the
evidence rows use, so the two join without a heuristic.

**Lane A2 (math / formula / number).** `math_guard` is the only guard whose sole-withheld blocks split
evenly (4 clean, 4 wrong): the guard is behaving exactly like a detector with no discrimination, which is
what a guard becomes when the thing it guards has been flattened. **What the simulator needs from A2:**
a per-block **`formula_structured`** flag. The role spec's §FORMULA ⚠ is the same finding from the other
side — `formula` and `table` waive the math guards *by role name*, while the content arrives as a flattened
string. With a structure flag the exemption becomes conditional and the gate gains a signal it does not have
today. A2 also owns the FORMULA→`empty` hole: 8 printed comparisons on `02-sgk-toan-2-tap-hai` p48 are
withheld as "empty blocks".

**Lane A3 (this lane) — the role definitions.** Scenario F in `THRESHOLDS.example.json` keys on a role, and
role is the least reproducible class measured so far (κ 0.423–0.713 before the spec). Six of the 26 wrong
blocks the pipeline serves on the gold set are `nonquestion_as_question`, and 6 of the 12 teaching-critical
served blocks sit on the `question` role: **role errors are not a separate failure class from false trust,
they are a component of it.** Q-ROLE-1 and Q-ROLE-2 (`ROLE-DEFINITION-SPEC-v1.md` §9) change what the role
row of the scoreboard means and therefore what a role-keyed gate would do.

**Lane D (pack rebuild).** The audit plane measures the packs currently shipped. A rebuild moves that
baseline, and `pack_provenance.py` already fails verification on the packs on disk. Any audit-plane number
in this document is a statement about `g*-20260905T0413Z-320ae88e` + samUnits, not about whatever is
rebuilt.

**A missing primitive neither lane owns.** The role-signal experiment (§5) asked for a deterministic
**box detector** on the page image. It would feed the role layer *and* the `box_boundary` guard, which today
fires on 4 blocks. Without it, SIDEBAR stays at precision 0.738 and the sidebar/body/objective confusions in
§4 of the role spec stay where they are.

**What the simulator still cannot do, and should not be asked to.**
1. **Restore precision exists only on the gold plane.** The three audit samples contain 34 withheld rows in
   total. Nothing here measures over-withholding on shipped content at scale.
2. **The gold set is 54 deliberately hard pages, not a sample.** No rate in §3 transfers to the corpus. A
   gate chosen on this curve would be chosen on hard pages, which is conservative in an unquantified way.
3. **Teaching-critical is narrower here than in the audit protocol.** The gold plane counts corrupted digits
   and non-questions-asked-as-questions; the audit protocol also counts truncation, in-sentence
   contamination and term-level tone slips. The two are not comparable and are not summed.
4. **Nothing here measures what a child would do with the text.** It measures whether the text is what the
   book says — the same limitation the round-3 audit recorded in its §9.

---

## 6. Denominators (D5)

| denominator | value | what it is used for here |
|---|---|---|
| gold pages / learning blocks | **54 pages / 643 blocks** | every rate in §2, §3, §4. The only plane with withheld-side truth. |
| round-3 audit sample | **484 rows** (480 served) of 3,334 served blocks / 2,798 activities | the audit-plane reference point (FTR 0.650) and scenarios H–K |
| legacy batch-1 NEW | **74 rows** | the audit-plane legacy reference (FTR 0.365) |
| canonical historical lessons | **3,679** | **not used.** No number in this document is divided by it. |
| ranged lessons | **3,381** | **not used.** |
| legacy lessons in scope | **243** | **not used** as a denominator here; it is Lane D's. |
| re-annotation sample | **26 rows** | `ROLE-DEFINITION-SPEC-v1.md` §8 only |

The 3,679 / 3,381 pair remains two different measurements of two different things
(`METRIC-DENOMINATORS.md` D5) and neither is a denominator for a block-level gate. A gate binds on blocks; a
lesson-level record (Lane D's `docs/research/legacy-reprocess/THRESHOLDS.example.json`, a single
`max_false_trust_rate`) binds on lessons and **consumes** a block gate's output. Whether the product's
promise is expressed per block or per lesson is itself one of the questions below.

---

## 7. What the Founder has to decide before any of this becomes a threshold

1. **The cost asymmetry.** How many correct blocks withheld are worth one wrong block served? Every point on
   the curve is an implicit answer. Region I trades roughly 16 correct for 1 wrong; Region III trades
   roughly 2 correct for 1 wrong. Without a stated exchange rate the curve cannot be reduced to a point, and
   this lane will not invent one.
2. **One gate or several?** Reading text, a question offered to a child, and a number quoted as fact are
   three different risks. Scenario F shows a question surface would need its own, much tighter gate (42
   blocks at 0.065 coverage). TC-19 #3's ≥ 0.95 QUESTION precision is a *second* gate, not a stricter
   setting of the first, and it is not met (trusted-QUESTION precision 0.903 at n = 72).
3. **Are policy guards waivable at all?** `teacher_text` and `answer_leak` are the difference between
   "faithful" and "permitted". The simulator can waive them; doctrine may not. If they are never waivable,
   the honest curve stops at coverage ≈ 0.78 and the elbow in Region II disappears.
4. **Display-only or teaching-critical — same gate?** Round 3 measured them separately on purpose
   (display-only false trust 0.293 vs teaching-critical 0.333 on the shipped sample). A gate that treats a
   tone slip and a wrong fraction identically is a policy choice, not a technical one.
5. **What does `restored` have to prove?** Round 5's doctrine says a repair is never trusted by default.
   Does a block restored by *waiving a guard* — which validates nothing — count as restored, or must every
   restored block carry an independent confirming signal? The answer decides whether Region I is available
   at all before Lane A1 ships.
6. **Which denominator does the promise bind on** — blocks, lessons, or a lesson's teaching-critical blocks
   only? Lane D's lesson record and this block simulator answer different questions and must not be merged
   until this is settled.
7. **Q-ROLE-1 and Q-ROLE-2** (`ROLE-DEFINITION-SPEC-v1.md` §9). Any role-keyed gate inherits them.

---

## 8. Reproduce

```
python3 tool/corpus/thresholds/evidence.py gold \
    --sdm  poc-out/round4/pipeline/tc2-p2/sdm-gold \
    --out  poc-out/round5/lane-a3/evidence-gold-tc2-p2.jsonl
python3 tool/corpus/thresholds/run.py \
    --evidence  poc-out/round5/lane-a3/evidence-gold-tc2-p2.jsonl \
    --scenarios THRESHOLDS.example.json \
    --out-dir   poc-out/round5/lane-a3/gold

python3 tool/corpus/thresholds/evidence.py audit \
    --annotated round3-484=poc-out/round3/ft-audit/annotated-20260905.jsonl \
    --annotated legacy-b1-old=poc-out/round4/legacy/batch-1/audit/annotated-old-20260906.jsonl \
    --annotated legacy-b1-new=poc-out/round4/legacy/batch-1/audit/annotated-new-20260906.jsonl \
    --out poc-out/round5/lane-a3/evidence-audit.jsonl
python3 tool/corpus/thresholds/run.py --plane audit --filter audit_source=round3-484 \
    --evidence poc-out/round5/lane-a3/evidence-audit.jsonl \
    --scenarios THRESHOLDS.example.json --out-dir poc-out/round5/lane-a3/audit-round3-484

python3 -m unittest discover -s tool/tests -p "test_*.py"
```

Paths are relative to the main checkout (`TC_ROOT`). The extractor asserts its own agreement with
`tc_score.score` on every page, so a run that finishes is a run whose numbers match the published
scoreboard.

---

## 9. What this document does not do

It sets no acceptance threshold. It marks no point on the curve as recommended, preferred, or reasonable. It
does not create `THRESHOLDS.json`, and `tool/tests/test_thresholds.py` asserts the repository has none. It
declares no gate met — in particular, the ≥ 0.95 QUESTION-precision bar of TC-19 #3 is **not** met, and
Source Trust remains **0 / 97** because nothing has crossed a production-trusted path that does not yet
exist.
