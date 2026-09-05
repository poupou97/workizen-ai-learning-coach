# DATA ACCURACY FRAMEWORK — `WRONG → DETECT → WITHHOLD → REPAIR → VALIDATE → RESTORE`

Round 5 · Lane A1 · `tool/corpus/repair/` · framework version `repair-v1` · **published first so the other
lanes can build on it.** Contract tests: `tool/tests/test_repair_framework.py` (27) · regression cases from the Founder's 97-row audit: `tool/tests/test_repair_vi_defects.py` (25).

> **Read this if you are Lane A2 (maths) or Lane D (legacy).** A2 registers a repairer + validator for the
> formula/number/unit classes; D consumes the ledger. Neither needs to edit `repair/` — registration is by
> decorator from your own package.

---

## 1. Why this exists

Round 4's long-term shape was `WRONG → WITHHOLD → DONE`: coverage 0.683 → 0.551 to move false-trusted 42 →
26. That trade cannot be repeated — it ends at an accurate corpus with nothing in it. Round 5's shape is:
detect the failure, propose a **repair**, prove it with a **signal independent of the source that made the
error**, and only then **restore** the block. A repair that cannot be proved leaves the block withheld.

Two rules are absolute and are enforced in code, not in prose:

1. **No repair defaults to TRUSTED.** A `RepairCandidate`'s disposition is `REPAIRED_CANDIDATE` and stays
   that way until a validator says `validated`. An LLM-produced candidate is exactly as untrusted as a
   rule-produced one.
2. **A source observation is never overwritten.** `Observation` is a frozen dataclass whose `provenance`
   mapping raises on write. A repaired value lives in the *ledger*, beside the observations it came from —
   it never replaces them.

## 2. The dispositions (`model.Disposition`)

| disposition | meaning | may be served to a child |
|---|---|---|
| `ORIGINAL_OBSERVATION` (alias `RAW`) | what one source actually produced; immutable, forever | no |
| `REPAIRED_CANDIDATE` (alias `CORRECTION_PROPOSED`) | a proposal, from any generator including an LLM | **no** |
| `VALIDATED_REPAIR` | a candidate an independent validator confirmed | not until restored |
| `TRUSTED` | eligible to be served — still behind the (non-existent) Founder trust gate | yes |
| `WITHHELD` | detected wrong, or not confirmed | no |
| `SUSPECT` | a failure was **detected** on a served block and no repair was confirmed | no |
| `CONFLICT` | signals actively contradict each other and neither side is decisive | no |
| `HUMAN_VERIFIED` | a person ruled on it — evidence with provenance, never an override | (as recorded) |
| `LEGACY` | produced by a superseded pipeline; kept for comparison | no |
| `SUPERSEDED` | replaced by a later disposition; kept, never deleted | no |

`Disposition.SERVABLE == {TRUSTED}`. Nothing else is servable, and `check()` refuses an unknown string.

**Mapping, not duplication** (Founder ACCURACY RECOVERY addendum). `RAW` and `CORRECTION_PROPOSED` are the
addendum's names for states this model already expressed, so they are **aliases** — a ledger reader written
against either vocabulary works. `SUSPECT`, `CONFLICT` and `HUMAN_VERIFIED` had **no** equivalent and were
added. What was already covered elsewhere and is deliberately *not* duplicated: both stacks' text,
`agreement`, `guards`, `trust` and `ocr_conf` live on the SDM block; `provenance`, `reasons` and `status`
live on the TSL. The framework references them rather than copying them.

**Contradicting evidence is first class.** `RepairCandidate.supporting()` / `.contradicting()` /
`.abstaining()`, and `to_json()` emits `supporting_evidence` and `contradictory_evidence` side by side. A
candidate is not a bag of reasons to say yes.

**No trust ladder.** There is no `LLM < Internet < Human` precedence anywhere in this model, and none should
be added. A signal counts by its **layer** (independence), its evidence and its provenance — not by who
produced it. A human signal is `Signal('E.human', …)` with provenance like everything else, and it can be
contradicted.

## 3. The types (`repair/model.py`)

```python
Observation(block_id, source, value, provenance)          # frozen; .observation_id is content-addressed
Signal(signal_id, verdict, strength, detail)              # verdict: supports | objects | abstains
                                                          # signal_id: "<layer>.<name>", layer in A..F
RepairCandidate(block_id, failure_class, original_observations, proposed_value, rule_id,
                supporting_signals, confidence, provenance, detected)
ValidationResult(validator_id, verdict, evidence, detail) # verdict: validated | rejected | insufficient
LedgerEntry(block_id, failure_class, disposition, observations, candidate, validation,
            final_value, reasons, stage, prior_entry_id)  # stage: detect | validate | dispose | restore
```

`RepairCandidate.independent_support(exclude_layers=...)` returns the signal **layers** that support the
candidate, minus the ones you name. The Founder's rule — *a trusted repair must be confirmed by an
independent signal or source* — is a statement about that set, so a validator should ask the candidate
rather than invent its own arithmetic:

```python
if candidate.independent_support(exclude_layers=(generator_layer,)) and not candidate.objections():
    return ValidationResult(vid, Verdict.VALIDATED, evidence=[...])
```

## 4. The signal layers (Founder priority order)

| layer | what it is | who owns it |
|---|---|---|
| **A** | Vietnamese lexical / orthographic (syllable legality, diacritic placement, lexicon + frequency) | A1 |
| **B** | source / layout / context constraints (bbox, column, box tint, role, neighbours) | A1 |
| **C** | deterministic number / unit / formula checks | **A2** (`tool/corpus/mathfix/`) |
| **D** | cross-page / heading / TOC / in-document consistency | A1 |
| **E** | independent human review — an *output*, a queue, never an automatic verdict | A1 emits, Founder decides |
| **F** | a third OCR / parser stack — **only where evidence shows benefit** | measured proposal only |

A signal that has nothing to say returns `abstains`, and that is *recorded*: per-signal contribution cannot
be measured unless we know when a signal was silent. `Signal.strength` is that signal's own evidence weight;
**it is never a probability of correctness and no threshold on it is a production trust threshold.**

## 5. Registering a plugin (this is all Lane A2 needs)

```python
# tool/corpus/mathfix/plugin.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))      # tool/corpus on the path
from repair import registry, model

FC = 'formula_flattened'

@registry.repairer(FC, repairer_id='mathfix.fraction-v1')
def propose(ctx):
    primary = ctx.primary()                       # ctx.observations are frozen; you cannot write to them
    ...
    yield model.RepairCandidate(
        block_id=ctx.block_id, failure_class=FC,
        original_observations=ctx.observations,   # cite every observation you looked at
        proposed_value='1/5 giờ', rule_id='mathfix.fraction-v1',
        supporting_signals=(model.Signal('C.numeric', 'supports', 0.9, dict(check='digit-run equality')),),
        confidence=0.8,
        provenance=dict(covers_reasons=('math_guard',)),   # which withhold reasons this repair answers
        detected=dict(observed='1 5 giờ', kind='fraction flattened'))

@registry.validator(FC, validator_id='mathfix.deterministic-v1')
def validate(candidate, ctx):
    if candidate.objections():
        return model.ValidationResult('mathfix.deterministic-v1', model.Verdict.REJECTED)
    if not candidate.independent_support(exclude_layers=('C',)):
        return model.ValidationResult('mathfix.deterministic-v1', model.Verdict.INSUFFICIENT)
    return model.ValidationResult('mathfix.deterministic-v1', model.Verdict.VALIDATED,
                                  evidence=[dict(kind='bbox digit recount', value=...)])
```

Then run it:

```python
from repair import engine, ledger
eng = engine.RepairEngine(ledger.Ledger('poc-out/round5/…/repair-ledger.jsonl', run=dict(lane='a2')))
out = eng.run_block(engine.RepairContext(block_id=..., observations=(...,),
                                         disposition='WITHHELD', withhold_reasons=('math_guard',)))
if out.restorable:
    eng.restore(out)          # a separate act: repairing and serving are two things, and both are logged
```

**`provenance['covers_reasons']`** is the contract that makes restoring safe: a repair restores a block only
if *every* reason the block was withheld for is covered. A block withheld for `agree_tones` **and**
`math_guard` is not restored by a text repair alone — the engine reports `residual_withhold` and the block
stays withheld. That is why a maths plugin and a text plugin can safely run on the same corpus.

## 6. Engine policy, in full (`repair/engine.py`)

1. Repairers propose. Every proposal is written to the ledger at stage `detect`, disposition
   `REPAIRED_CANDIDATE`.
2. Validators rule. **Unanimity among non-abstainers**: one `rejected` kills the candidate; a candidate
   with no `validated` verdict stays a candidate. `insufficient` is never a soft yes. No validator at all
   ⇒ not validated. Written at stage `validate`.
3. Disposition, fail-closed, at stage `dispose`:
   - withheld block + validated repair covering **every** withhold reason → `VALIDATED_REPAIR`,
     `restorable=True`;
   - withheld block + validated repair leaving a reason uncovered → `WITHHELD` (`residual_withhold`);
   - **trusted** block where a failure was detected but nothing validated → **`WITHHELD`**. Accuracy first:
     a detected error that cannot be repaired is not served;
   - nothing detected → the pipeline's own disposition, and no ledger row (the framework is silent where it
     has nothing to say).
4. `restore(outcome)` writes a `TRUSTED` row that *supersedes* the `VALIDATED_REPAIR` row and names it in
   `prior_entry_id`. The earlier row is still there.

## 7. The ledger (`repair/ledger.py`)

Append-only JSONL, one row per step. `append` refuses an `entry_id` it has already written; there is no
update and no delete; a later disposition is a **new** row naming its predecessor. Read it with
`ledger.read(path)` — plain `json.loads` per line, no import of this package required.

Every row carries: `observations[]` (with their own `disposition`), `candidate` (rule id, proposed value,
confidence, **supporting_signals with layer**, provenance, what was `detected`), `validation` (verdict +
evidence), `final_value`, `reasons`, `stage`, `prior_entry_id`, `framework_version`, `ts`, and the `run`
block the ledger was opened with. That is the Founder's full trace,
`source → observation → failure → repair → validation → final disposition`, in one line of JSON.

## 8. Measuring a signal's contribution (`engine.SignalContribution`)

`observe(candidate, validated, correct=None)` then `table()` gives, per layer: `consulted`, `supports`,
`objects`, `abstains`, `validated_with`, `right`, `wrong`, and **`decisive`** — how often that layer was the
*only* supporting layer, i.e. how often the repair would not have been validated without it. Pass
`validator_rule` to `table()` to ablate a layer and count what a run would have lost without it.

## 9. Structural groups — the group is the unit of disposition

`repair/groups.py`. Founder audit defect 8: *withholding one option of a multiple-choice question leaves the
served question **wrong**, not merely smaller.* So for blocks with structural siblings the group, not the
block, is what gets a disposition:

```python
from repair import groups
gs = groups.structural_groups(sdm)                 # question_options · figure_caption · table_rows · procedure_steps
mut = groups.mutilated(gs, servable_by_id)         # groups that WOULD be served incomplete — a defect in itself
groups.apply_group_rule(gs, servable_by_id, reasons, ledger=lg)   # serve the whole group or none of it
```

Groups are derived deterministically from the SDM's own roles and reading order; a block in no group keeps
its own disposition exactly as before. `apply_group_rule` writes one immutable ledger row per group it
resolves, keyed by `group_id`, so a group decision is as traceable as a block decision.

Measured on the 54 gold pages: **tc2-p2 serves 7 mutilated structures**; the rule takes that to 0 at a cost
of 20 blocks. Over-withholding can therefore *raise* the teaching-critical rate, not only lower coverage.

## 10. Extension points — use these instead of forking

| you need | call | note |
|---|---|---|
| a repairer for your failure class | `registry.repairer(fc, id)` | §5 |
| a validator | `registry.validator(fc, id)` | §5 |
| a deterministic numeric check | `repair.signals.numeric.register_provider(fn)` | **Lane A2's slot**; the default only guarantees no repair moved a digit |
| an extra signal on every token a repairer is about to change | `registry.token_signal_provider(id)` → `fn(observed, proposed, ctx)` | **Lane A4**: cross-corpus, LLM-as-anomaly (candidate only), external authority |
| an extra signal per candidate block | `registry.block_signal_provider(id)` → `fn(observed_text, proposed_text, ctx)` | as above |
| the ledger, joined to the SDM | `ledger.read(path)`; `block_id` is **byte-identical** to the SDM/TSL block `id` | **Lane D / A3** |
| per-block disposition for a gate | `repair-dispositions.jsonl` per run: `block_id · disposition · servable · trust · reasons · repair` | a gate must key on *validation*, never on the absence of a guard |
| per-signal false-correction attribution | `engine.SignalContribution.by_signal()` → `false_corrections`, `false_correction_rate` per `signal_id` | **P0 metric** |

A provider that returns an `objects` Signal **vetoes** the repair, exactly like a built-in one; a provider
that raises is caught and ignored rather than taking the run down. If a hook you need is missing, ask for it
— do not fork the framework.

## 11. What this framework does **not** do

- It does not set, imply or store a production trust threshold. `TRUSTED` here means «this repair was
  confirmed», not «this corpus may teach a child». The second gate does not exist and A1 did not create it.
- It does not loosen a guard. A withhold reason is answered by *evidence*, or it stands.
- It does not let an LLM be truth. An LLM may generate a `RepairCandidate` offline; it can never be a
  validator's independent signal, and nothing in `repair/` calls a model.
