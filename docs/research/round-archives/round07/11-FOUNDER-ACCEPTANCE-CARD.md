# 11 · FOUNDER ACCEPTANCE CARD — round 7's original gates, graded

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**The five gates were fixed in `ROUND7-PLAN.md` (`1e31512`), in the repository, before any work.
They are not redefined here.**

---

## 1. THE FIVE GATES — graded independently

| Gate | Requirement *(verbatim from the plan)* | Coordinator | **Archive builder** | §|
|---|---|---|---|---|
| **A · METRIC TRUTH** | No ambiguous major metric remains; every critical total **re-derivable from leaf records by a committed command** | PASS | **PASS** | 2.1 |
| **B · TRUST CALIBRATION** | Policy and bound **frozen and hashed before** any admitted lesson is inspected, **provable by artefact order** | PASS | **PASS — and it is the strongest-evidenced gate of any round so far** | 2.2 |
| **C · BLIND VALIDATION** | Audit machinery exists, **proven on a dry run that does not use the frozen bound to admit anything** | PASS | **PASS** | 2.3 |
| **D · TRUST DELIVERY** | **Not attemptable this round.** The honest outcome is a **prepared, unactivated gate** | PREPARED, UNACTIVATED | **PREPARED, UNACTIVATED — neither PASS nor FAIL, as the plan defines it** | 2.4 |
| **E · NO REGRESSION** | Round 6's invariants hold | PASS (one item hardware-unverified) | **PASS, with one invariant NOT RE-RUN and one HARDWARE UNVERIFIED — both named** | 2.5 |

### TALLY — **4 PASS · 1 PREPARED, UNACTIVATED**

**Agreement with the coordinator on all five.**

---

## 2. THE GRADING, GATE BY GATE

### 2.1 GATE A — **PASS**

**18 metrics · 18/18 re-derive** to their recorded values by committed command, each carrying nine
fields including a **runnable re-derivation**. Two independent re-derivations landed **exactly** —
the recognition REGION census to four decimals, and WS-D's 238-lesson census on all four figures.

**«Total activities» is resolved, and resolved honestly — by deprecation.** 248 **SUPERSEDED** (a
correct earlier value of a named metric), 217 **DEPRECATED** (*a sum of two different units*), 161
**DEPRECATED** (*three of seven families under a whole-corpus name, dropping 87 rows*). **The phrase
itself is deprecated.**

**Why not PARTIAL:** the gate asks that **no ambiguous major metric remains**. The 97-row set's
internal denominators **are** still ambiguous — but that was **found by this workstream, referred to
it, and deliberately excluded from use as a bound anchor**. *A gate that surfaces a new ambiguity and
names it has done its job; carrying the new finding forward is round 8's, not a demotion of round
7's.*

### 2.2 GATE B — **PASS**, and it is the strongest-evidenced gate this project has produced

The requirement is **provability by artefact order**, and the artefact is three lines long:

| seq | kind | sha256 | binds policy | frozen |
|---|---|---|---|---|
| 1 | policy | `0dfc5032…` | — | **06:41:54Z** |
| 2 | population BLIND-CORE | `dbadf4ad…` | `0dfc5032…` | **06:47:21Z** |
| 3 | population BLIND-TEACHING | `69d1cacc…` | `0dfc5032…` | **06:47:21Z** |

**No `approval` entry. No `admitted` entry.** *(PROVEN — the archive builder read the file: three
lines and no more.)*

**Three properties make this a proof rather than a claim:**

1. **The policy precedes the populations by six minutes, and both populations embed its hash.** The
   order cannot be reconstructed favourably after the fact.
2. **The chain refuses at write time** — a population before a policy, or an admitted set before an
   approval, is rejected. **An `admitted` write with no recorded approval raises a
   `PermissionError`**, confirmed **adversarially**. *A refusal, not a discouragement.*
3. **The recommendation seals its own prediction.** C2's predicted outcome — **a truthful zero** —
   is **inside the frozen payload**, so it cannot be revised once the result is known.

**And the identity discipline holds, with its wording exact:** **0 identity-shaped strings in all
three calibration documents** *(PROVEN)*. The frozen **populations** name their 120 lessons each
with **titles hashed** — that is the evaluation frame, frozen before anything could be admitted, and
the claim is «no identity in an **admission** context». **«Zero lesson identities anywhere» would be
false, and neither the workstream nor this archive says it.**

> *«A policy chosen after seeing the admitted set is not a policy, it is a selection.»* **Round 7
> made that unfalsifiable-by-construction rather than promised.**

### 2.3 GATE C — **PASS**

The machinery exists — `apply.py` (inert), `audit_sheet.py` (worklist + **sealed key**),
`measure.py` — with **52 tests**, and the dry run demonstrates **one PASS and three refusal modes**
on fabricated rows. **It admitted nothing**, which is precisely what the gate required.

**The gate asked for a dry run that does not use the frozen bound to admit anything. It got one, and
the machinery refuses to do otherwise.**

### 2.4 GATE D — **PREPARED, UNACTIVATED.** Not a PASS. Not a FAIL. **The plan says so.**

> **D · TRUST DELIVERY** — **not attemptable this round.** Reaches a device only after Founder
> activation. **Round 7's honest outcome is a prepared, unactivated gate.**

**This archive grades it exactly as the plan defines it, and refuses to convert it into either.**

- Calling it **PASS** would be redefining a gate after seeing results — the error this archive
  exists to prevent, and the one round 6's card refused for Gate D as well.
- Calling it **FAIL** would be **penalising a workstream for obeying a hard stop written in
  advance.** *Round 7's central instruction was to stop here.*

**What the round actually delivered against it:** a gate that is built, frozen, tested, refusing —
and **measured to be insufficient**. Activating it would **not** fix the content, because
`TRUST = SERVED ∩ admit(…)` means activation **cannot serve one new block**, and no bound reaches
the required rate. **The honest outcome is stronger than a PASS would have been: the round knows why
the gate would not help.**

### 2.5 GATE E — **PASS**, with two items named rather than absorbed

| invariant | result |
|---|---|
| served set unchanged | **HOLDS** — 35 served text blocks before and after, **id set identical**; the 5 new blocks are figure images carrying **no text** *(PROVEN by the archive builder)* |
| repair records only on withheld blocks | **HOLDS** — 6 of 6 *(PROVEN)* |
| `trusted = 0` | **HOLDS** — `provenance.repair.trusted = 0`, every `repair.servable = false` *(PROVEN)* |
| no withheld block carries `text` | **HOLDS** — 0 of 17 *(PROVEN)* |
| honesty guard — inject a `TimelineSemantic` into the **published artefact** | **RED**, as required |
| honesty guard — serve `p039:000` as a paragraph with its text | **RED**, 7 failures |
| **`UNACCOUNTED = 0`** | **NOT RE-RUN** — the conservation audit needs a batch of SDM artefacts and belongs to an accounting lane that **does not exist this round**. *Nothing in the round changes region dispositions: the withheld set is byte-identical and the served set unchanged, which is the property the audit measures.* **Recorded as not re-run, not as holding.** |
| **the R-1 fix on hardware** | **[HU] HARDWARE UNVERIFIED** — no device walk, no frames |

**Why still PASS:** every invariant the gate names either **holds and was verified**, or is
**explicitly recorded as not re-run with the reason and the argument for why it is unaffected**. *A
gate graded on what was checked, with the unchecked item named, is graded honestly. A gate graded
PASS while quietly not re-running something is not.*

---

## 3. THE STANDING RULES — all held

| Rule | Held? |
|---|---|
| **Never turn PARTIAL into DONE** | **YES** — S5 PARTIAL · R-3b PARTIAL · R-5 DEFERRED · D not attemptable. WS-S wrote its own guard sentence: *«S5 is PARTIAL and stays PARTIAL.»* |
| **NO THRESHOLD THEATRE** | **YES** — nothing activated; the recommendation **predicts its own truthful zero** |
| **Re-derive a number a second way before recording a disagreement** | **YES, and it paid twice** — WS-T's clustering claim and WS-S's anchor count were both withdrawn **by their authors, inside the round** |
| **Every metric states its denominator** | **YES**, and round 6's failure to do so is corrected as **C2** |
| Composition check with real assets | **YES** — and the fixture was **regenerated, not rsynced** |
| FORMS BEFORE RULES | **YES** — the 118 were **counted before being decided**, and the count reversed the decision |
| Nothing vanishes without an explicit deferral and a reason | **YES** — **30 rows triaged, every one with a verdict and an owner** |
| **DO NOT MERGE** | **YES** — 16 PRs open across four rounds *(PROVEN)* |

---

## 4. THE ARCHIVE BUILDER'S RECOMMENDATION TO THE FOUNDER

**ACCEPT round 7. Decline activation — and note that the recommendation itself predicts you will.
Then fund round 8, which needs no decision from you to start.**

**Reasoning in one paragraph.** Round 7 was asked to build a trust gate and stop before using it. It
did both, and then did something better than either: **it measured that using the gate would not
help.** All twelve teaching-critical errors reduce to two mechanisms that survive character-exact
agreement between two independent OCR stacks; no bound reaches the required rate by a factor of six;
and the only passable bound implies **45 % of lessons carrying a teaching-critical error — «not
sayable to a parent»**. **The gate is not the blocker and now we know it, which is worth more than
a non-zero trusted count would have been.**

**Three decisions are genuinely yours and none of them is «approve the threshold»:**

1. **The all-or-nothing sibling rule** — 31 mutilated structures → 0, at 72 blocks a child reads
   today. *The same shape of trade as round 6's lost timeline.*
2. **ALL-CAPS titles** — 108 shouted titles, or 108 quiet assertions that a proper noun is not one.
3. **The merge debt** — merge #79 and close #73, **or state the no-merge policy**, because at four
   layers and 259 commits the integration branches no longer function as a delivery path.

**And one thing to grant when you can: the device.** Three finished fixes are unproven where it
counts, and **round 7 is the first round since round 3 to close with no device evidence at all.**

---

## 5. WHAT THIS ROUND PROVED ABOUT THE PROCESS, NOT THE PRODUCT

Worth recording because it is the third consecutive round in which the process caught its own
authors:

- **The anti-rot guard fired on the coordinator**, who had repaired defects its baseline still
  asserted were live — and the resolution **improved on both parties' positions**, with the weaker
  half of WS-M's own argument **withdrawn** rather than defended.
- **«Re-derive a number a second way» — a rule that entered the project because of the round-6
  archive's own counting error — caught two claims inside round 7**, both withdrawn by their authors
  before publication.
- **Three of the coordinator's own statements to the Founder were falsified in this round's own
  report.**
- **A gate was found green because the thing it guards was absent**, and the fix asserts **both** the
  vacuous PASS and the correct FAIL on the same document, so the gap cannot silently return.

> **A project whose checks catch its own most senior participants is working. That is the honest
> reading of round 7, and it is the reason its truthful zero can be believed.**
