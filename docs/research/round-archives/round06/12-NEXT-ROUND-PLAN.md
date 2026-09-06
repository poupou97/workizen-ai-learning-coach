# 12 · NEXT ROUND PLAN — Round 7

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**
>
> **Round 7 is PROPOSED, not committed.** No `ROUND7-PLAN.md` exists in the repository at the time
> this archive was built. What follows is §13 of the round-6 consolidated report — a proposal from
> the coordinator — plus this archive's own reading of what round 6's evidence obliges. **Nothing
> here creates an obligation, and the Founder has not signed it.**

---

## 1. THE PROPOSED NORTH STAR

> **TRUSTED CONTENT REACHES THE LEARNER — under a Founder-set threshold.**

| | |
|---|---|
| **WHY NOW** | Round 6 proved the whole chain end to end and stopped at **the one gate no lane may open**. |
| **PROBLEM** | Validated content is **visible and countable but unservable**; `trusted = 0` by construction. |
| **OBJECTIVE** | A Founder-set threshold, applied to the Golden slices, **with false trust measured against it**. |
| **MEASURABLE TARGET** | `eligible for teaching > 0` **with a stated, measured false-trust rate on a blind holdout**. |
| **DELIVERABLE** | Threshold policy + the trust gate wired + **a blind audit of everything it admits**. |
| **DEPENDENCIES** | **A Founder decision on the threshold. Nothing else.** |
| **RISKS** | Setting it **to reach a number** rather than to reflect evidence. |
| **MITIGATION** | The threshold is chosen from **Lane A3's round-5 trade-off curve, *before* seeing which lessons it admits.** |
| **STOP CONDITION** | Measured false trust above the chosen bound ⇒ **report the truthful zero again.** |
| **FOUNDER GATE** | **The threshold itself.** |

**The mitigation is the load-bearing clause.** A3 built that curve in round 5 and deliberately chose
no point on it. *Choosing the point before seeing the lessons is what separates a threshold from a
rationalisation.*

**And the stop condition matters as much as the target.** Round 6 established that a truthful zero
is reportable. **Round 7 must be allowed to report a second one** — otherwise its target becomes a
pressure to lower a gate, which is the failure mode round 5 measured at restore precision 0.000.

## 2. SECONDARY, NON-COMPETING

| Item | Why it is cheap, and what it is worth |
|---|---|
| **The 118-block model gap** | `footnote` 64 · `activity` 50 · `option` 4 — **withheld because the app has no matching type, not because the text is untrustworthy.** Three block types in `lib/core/lesson_model/**`. **The cheapest win on the table.** And the 4 `option` blocks are **defect #8**: a mutilated multiple-choice set, where withholding is *not* safe. |
| **Canonical identity ruling** | Four questions pending. Until they are answered, **every «/ 3,679» figure in every round is provisional.** |
| **Recognition generalisation** | Holdout digit recall **0.181** against DEV's 0.500 — *the honest expectation is much lower than the development figure.* |

## 3. WHAT ROUND 6 HANDS ROUND 7 — a map of its own open items

| Round-6 open item | Where it should land in round 7 | Named in the proposal? |
|---|---|---|
| The trust threshold | **the North Star itself** | **yes** |
| 118-block model gap | secondary | **yes** |
| Canonical identity — four rulings | secondary | **yes** |
| Recognition generalisation | secondary | **yes** |
| **G1 — the 17 gaps have no page crops** | — | ⚠ **not named.** A one-line re-run of WS-C's bridge with crops; **the device walk's one FAIL.** |
| **The Next Action contradiction** («Về mục lục» on a lesson just opened) | — | ⚠ **not named.** Born in `lib/core/agenda/**`, returned to its owner. |
| **The lowercased historical proper noun** | — | ⚠ **not named.** A display-layer rule; *(PROVEN to be a display defect, not data)*. |
| **Merge debt** | — | ⚠ **not named in §13**, but the Part II audit stands: **merge #79, close #73, hold the rest.** |
| **The ephemeral-worktree near-miss** | — | ⚠ **not named.** An artefact a gate depends on must be copied out of an ephemeral worktree **at the moment the gate is claimed.** |
| **The undefined *total activities* metric** | — | ⚠ **not named.** `toanExercises` 41 → 0 is settled; *activities* is a derived total with no written definition, and three different sums are in circulation (248, 217, 161). One line in a doc fixes it. |
| `si_expected_exponent` abstains on all 171 | — | ⚠ **not named.** *An independent validator that never fires is not yet an independent validator.* |
| The unbuilt recognition fixes (`ink-accounted-v1` wiring; «a half crop must hold a number and nothing else»; denominator ink-width; in-corpus template recogniser for Ω) | secondary, under recognition generalisation | partially — **and the second owes a fresh holdout**, because HOLDOUT-3 has now been looked at |

**Nine items are not explicitly carried into the round-7 proposal.** They are recorded here so they
cannot be lost between rounds — which is the point of keeping a per-round archive.

## 4. WHAT ROUND 7 SHOULD NOT DO — on round 6's own evidence

- **Do not add a renderer family.** The census says `conceptMap` **0** and `timeline` **0** real
  instances across 238 lessons. **Two of four families have no data at all.**
- **Do not build a rule from HOLDOUT-3's errors without drawing a fresh holdout.** *Inventing that
  draw at the end of a round is how a holdout stops meaning anything.*
- **Do not compare an over-withhold rate across the accounting fix** without saying that the base
  grew.
- **Do not size a plan on DEV recognition numbers.** 0.500 is the development figure; **0.181 is the
  holdout.**
- **Do not adopt eight scales for the recall.** +17 % recall costs **false recognition 0.049 →
  0.083** on the holdout.
- **Do not treat `3,650` as an approved denominator.** It is a measurement.
- **Do not let a fifth round compose on an unmerged fourth.** *Round 7 would compose a composition.*

## 5. THE EARLY-CHECKPOINT DISCIPLINE, WORTH REPEATING

Round 6's plan required a Founder checkpoint **as soon as three things were proven**, rather than at
round end. **Whatever round 7's shape, it should carry the same clause** — and its natural trigger
is: *the threshold is set, the first lesson crosses it, and the blind audit of what it admitted has
begun.*

## 6. THE ONE-LINE BRIEF FOR ROUND 7

> **Round 6 built everything needed to serve trusted content and then, correctly, did not serve it.
> Round 7 is the round where a human decides how much risk a child may be exposed to — and the
> engineering's job is to measure that risk honestly enough that the decision is a real one.**
