# NEXT RESEARCH DIRECTION — RECOGNITION + ROLE DISAMBIGUATION

**Status: DIRECTION ONLY.** Not a round plan, not a POC, not an implementation. Written under
Founder task order 43, which accepted round 7 and closed calibration. **No Round 8 is opened here.**

---

## Why this and not calibration

Round 7 measured the thing that decides the direction:

> **All 12 teaching-critical errors in the served set fall into exactly two mechanisms — digit
> corruption (6) and a non-question served as a question (6) — and neither is visible to any
> signal a gate can read.**

Three of the six digit corruptions survive **character-exact agreement between two independent OCR
stacks**, plus every other clause in the policy. No signal combination bounds teaching-critical
error below **≈0.021**, against BOUND-2's required **0.0035** — a factor of six. At the 30 trusted
blocks a real lesson delivered in round 6, ≈0.021 means **about half of all lessons carrying one**.

**The gate is built, frozen and correct. It has nothing to read.** More calibration cannot move
this; a new *signal* is the only thing that can.

---

## What is already known, so it is not rediscovered

| Finding | Round | Consequence for this direction |
|---|---|---|
| «274 = the OCR never read the digit» is **two** failures: **DIGIT LOSS 312/548** and **SEGMENTATION 196/548** | 7 | A third of that population *was* recognised and glued into another token. These need different signals. |
| Targeted re-crop recovered **17 of 47** unreadable fraction regions on Bài 61, **17/17 correct**, 0 of 38 controls disagreeing | 7 | The lever works where the glyph is in the engine's repertoire but not isolated. |
| **Ω → `S2`: 0 of 22, at every scale** | 7 | Re-crop recovers what the engine *could* read and did not isolate. It recovers **nothing** outside the repertoire. That class needs a different mechanism entirely. |
| Every SGK page is a **100 ppi scan**; recovery is **not monotonic in scale** | 7 | **Scale is not the lever — segmentation is.** Do not pursue resolution. |
| Holdout digit recall **0.181** against DEV's **0.500** | 7 | The honest generalisation expectation is far below development numbers. |
| **A recovered digit does not become a repaired block** (10 → 10, Δ 0) | 7 | The recogniser *adds* an observation where the destroyed one must be **superseded**. A supersession contract is a prerequisite, not an afterthought. |
| **Option letters «A.»–«D.» are restored *after* `agreement()` runs** | 7 | **The one part that identifies the answer is the part no agreement measurement covers.** A structural blind spot, not a tuning gap. |
| Role error moved the **wrong way**, 0.116 → 0.151, while false trust improved | 5–6 | Role and trust are not the same axis. Tightening one can worsen the other. |
| Tightening role confidence to a 0.70 floor moved teaching-critical **0.0339 → 0.0407** and removed **every** block of continuous prose | 7 | Confidence thresholds are not a role signal. |
| **No pre-existing blind population existed** — A3's curve pooled all 643 rows including the 181 «held out» | 7 | Two blind populations are now frozen and hashed. Use them; do not build new ones to suit a rule. |

---

## The nine areas, with what would count as evidence

The Founder named nine. For each, the question is not «can we build something» but **«what measurement would tell us whether it works».**

1. **Digit recognition / digit corruption** — the 312/548 DIGIT LOSS class. Evidence: digit recall **on the frozen blind population**, with **false recognition reported beside it**.
2. **OCR character corruption** — the class where a glyph is read as a different valid glyph (`⁸`→`°`, `II`→`I1`, `Ω`→`S2`, `×`→`-`). Evidence: detection rate **separated by whether the true glyph is in the engine's repertoire**, because round 7 showed those two subclasses behave completely differently.
3. **Question vs non-question role classification** — six of twelve teaching-critical errors. Existing lexical checks in `content_quality_gate.py` (objective-not-question, heading-as-question, lead-in, pronunciation) are a starting inventory, **not a baseline** until measured on a real population.
4. **Structural / semantic role recognition** — beyond question/non-question: the roles the layer currently cannot name at all, which round 6 showed it silently dropped as `empty`.
5. **Failures where dual-OCR character-exact agreement is still wrong** — the hardest and most valuable class: **3 of 6 digit corruptions**. Evidence: any signal that separates them at all. This is where the round's headline sits.
6. **A new signal that sees what the threshold cannot** — the whole point. Evidence: teaching-critical bounded **below 0.0035 on the frozen blind population, or a measured statement that it cannot be.**
7. **Population-real evaluation** — see the test-design rule below.
8. **Cross-engine disagreement / uncertainty** — *only if it provides genuinely new signal.* Round 4 falsified `OCR_A == OCR_B ⇒ TEXT == TRUE`, and round 7 showed agreement is blind to the option letter. Treat this as a hypothesis to falsify, not a resource.
9. **Distinguishing recognition failure from reasoning failure** — a block can be misread, or read correctly and misclassified. Conflating them has already cost this project one wrong root-cause diagnosis.

---

## Two standing principles this direction must obey

### ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION

`0/0 present` **must not auto-PASS** when the expected population should be > 0. A gate must check
the **existence obligation**, not only consistency among what happens to be there.

This is not abstract. Round 7 found `fixture_lineage` L5 counting crop *references*, so a document
with **no crops at all** printed `0/0 present · PASS` — **the gate was green because the thing it
guards was absent.** The same shape appeared as a metric that could not distinguish «not
applicable» from «never asked», and as a plugin loader that silently returned an empty signal list.

### Test populations must contain the failing case

Round 7's other structural finding: **the tests were not missing, the populations were.** The
`titleCase` tests were fed only ALL-CAPS strings — only their own precondition — so a mixed-case
title had never been put in front of the rule, and it stayed green for four rounds. Three more
tests across three layers encoded expectations formed when synthetic data supplied content that
real, honestly-withheld data does not; **every one passed or skipped on a clean clone.**

So: **no rule is validated on a synthetic fixture built to satisfy its own premise.** Where a suite
depends on a population, it should carry a **population-adequacy guard** that goes red when the
population degenerates — the pattern round 7 established for titles.

---

## Prerequisites that are not research

These are known blockers, not questions:

- **A supersession contract** — a recovered observation must be able to *replace* a destroyed one, carrying original observation, engine, agreeing scales and region evidence. Without it, a validator judges two overlapping expressions.
- **The frozen blind populations** (`BLIND-CORE`, `BLIND-TEACHING`, 120 rows each) already exist and are hashed. Any new signal is measured against them, and the freeze order stays auditable.
- **Merge-debt reconciliation** — the Founder's order is explicit that no new research round opens on the current four-layer stack.

---

## What this direction explicitly does NOT authorise

No Round 8 implementation · no threshold activation · no new POC started to keep an agent busy ·
no device work while the Founder is using the phone · no relaxation of D4 on SGK pages or crops.

`trusted = 0` · `eligible for teaching = 0` · **TECHNICALLY VALIDATED != HARDWARE VERIFIED !=
DISTRIBUTION RIGHT.**
