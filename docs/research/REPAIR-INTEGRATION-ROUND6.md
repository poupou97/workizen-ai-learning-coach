# REPAIR → PRODUCT INTEGRATION — round 6, workstream C

**Question this workstream was given:** round 5 built and validated a repair path and it did not
reach the product. Connect it — **without** setting a production trust threshold, which is a
Founder gate.

**Answer:** connected, and measured on a real lesson. **9 validated repairs, 6 crossed into a
production-shaped Trusted Structured Lesson and then into a LessonDocument, 0 of them trusted.**

---

## 0. The fact this exists to change

Round 5 §8.1, verified structurally by the coordinator rather than accepted from a report:

> **no file outside `tool/corpus/repair/` and `tool/tests/` imports the `repair` package at all.**

So round 5's "no served text changed anywhere" was a certainty of the wiring, not a measurement.
The repair path was a validated laboratory with a measured false-correction rate and **no
connection to the product**.

It is connected now. `tool/corpus/tsl_to_lesson_document.py` and `tool/tests/test_repair_integration.py`
import it; `lib/core/lesson_model/repair_record.dart` consumes what it emits.

## 1. CONNECT ≠ TRUST — how it is enforced, and why not by discipline

The whole risk of this workstream is that connecting becomes trusting. It is prevented in five
places, none of which is a policy anyone has to remember:

| where | the mechanism |
|---|---|
| `repair/validated.py` | `ValidatedRepair.disposition` is a **class attribute, not a field**: it may only ever read `VALIDATED_REPAIR`. There is no argument, flag or setter that produces `TRUSTED`. `from_entry` raises `TrustEscalation` on a `restore` row. `from_json` raises on any other disposition, so serialisation cannot launder one either. |
| `repair/tsl_projection.py` | **there is no promotion mechanism at all.** `check_projection` asserts no record carries another disposition, nothing is promoted into the served set, and no repaired value appears inline on a region. A laboratory restore is *capped*, with the reason written in three places. |
| `tsl_to_lesson_document.py` | `repair_of()` **refuses rather than sanitises**: a record claiming `TRUSTED`, claiming `servable`, missing its validator, or carrying any of `proposedValue / text / value / latex / textProjection / candidate / originalObservations / structuredValue` is a `BridgeRefusal` — nothing is written. A **served** block carrying a repair is also a refusal: that is the shape of an ungated restore. |
| `check_document` | searches the **whole serialised document** for each proposed value. The weak version of this check reads the fields we chose to emit and finds nothing because we chose not to emit them; the strong version means a future field, a nested provenance dict or a careless `**record` cannot open the door quietly. |
| `lib/core/lesson_model/` | `repair` is a field **only on `WithheldBlock`** — a served block has nowhere to put it, so no path exists by which a repaired value gets served. `ValidatedRepairRef.fromJson` returns `null` for any other disposition and for any forbidden key, and a null there **rejects the whole document**. |

A repaired region therefore lands in the TSL and in the app **still withheld, still text-less** —
what it gains is that it is **visible and countable**. That is the end of the state where validated
output is invisible.

## 2. The chain, end to end

```
OriginalObservation ─┐
                     ├─► RepairCandidate ─► Deterministic Validator ─► ValidatedRepair
supporting Signals ──┘                                                      │
                                                                            ▼
                                                        Trust / Disposition  (VALIDATED_REPAIR — capped here)
                                                                            │
                                     repair/tsl_projection.py ──────────────┤
                                                                            ▼
                                                        Trusted Structured Lesson  (withheld region + record)
                                                                            │
                              tsl_to_lesson_document.py ────────────────────┤
                                                                            ▼
                                                             LessonDocument  (WithheldBlock.repair)
                                                                            │
                                                                            ▼
                                                        Learning View  (page crop + provenance — WS-D)
```

`ValidatedRepair` retains all ten things the round-6 plan requires:

| required | field |
|---|---|
| original observation | `original_observations` — round-5 `model.Observation`, both stacks, unmodified |
| candidate | `candidate` — round-5 `model.RepairCandidate` |
| source grounding | `source_grounding` — **Lane E1's `semantic.graph.SourceGrounding`**, imported |
| failure class | `failure_class` |
| repair method | `repair_method` (rule id) + `supporting_layers` |
| validator + version | `validator_id` + `validator_version` |
| validation result | `validation` — round-5 `model.ValidationResult` |
| repair version | `repair_version` + `framework_version` + `integration_version` |
| provenance | `provenance` + `source_version` (pipeline · sdm · hashes · ledger run) |
| disposition | `disposition` — `VALIDATED_REPAIR`, and only that |

**No fourth provenance universe.** The observation/candidate/validation types are round 5's own
frozen dataclasses, carried whole. The grounding **is** E1's type — imported, and a test asserts
`isinstance` and byte-equal `to_json()`, so "reuse" is checked rather than claimed. The disposition
strings are `repair.model.Disposition`, and the Dart enum asserts the same ten wire strings.
`ledger.entry_from_json` was added because the ledger had a write side and a raw read side but no
way back to the typed row — that gap is exactly how a fourth universe starts.

## 3. GOLDEN #1 — LS&ĐL 5 Bài 8, the Founder's sharp case

The block `p039:000` carries **all seven dated events** of the lesson. Round 5 withheld it on one
token: «Bạch **Đằng**» (primary) vs «Bạch **Đăng**» (verifier), and the print says the primary is
right. One tone disagreement removed every timeline event from the lesson.

**Round 6 result: repaired and validated, and still withheld — visible and countable.** Lineage,
as recorded on the artefact:

```
observations   …#docling-ocrmac#fa1c52454849a415   "Hai Bà Trưng (40 - 43) … Chiến thắng Bạch Đằng …"
               …#current-xycut#86d87bfbbce2c26c    "… Chiến thắng Bạch Đăng …"
candidate      …:p039:tc2-p1:000#lanec.tone-corroboration-v1#5c31cd1ca2f4466c
               proposed == observed  →  changed = false   (a DISPOSITION repair: nothing is rewritten)
signals        D.in_corpus_majority ABSTAINS · E.human_print_read SUPPORTS 1.0
validator      lanec.history-text-validator-v1 / v1  →  validated
               evidence: {kind: "independent signal layer", value: "E"}
ledger entry   0e2f6feaa5a26e01
grounding      05-sgk-lich-su-va-dia-li-5 · pagePdf 39 · pagePrinted 37 · bbox [0.0755,0.0683,0.835,0.08]
disposition    VALIDATED_REPAIR · servable false · trusted 0
in the document type "withheld" · trust "withheld" · reasons ["agree_tones"] · NO `text` field
```

**No lesson identity is named anywhere.** There is no `if lesson == 8`, no book allow-list, and no
special case in `repair/`, in the bridge or in the app. The join is `block_key`, the same
pipeline-agnostic normalisation the bridge already used.

### Lane C's *opposite* result survives too

| block | what happens | why it matters |
|---|---|---|
| `p039:000` | restored to `VALIDATED_REPAIR`, withheld | a validated repair is visible |
| `p038:023` | `VALIDATED_REPAIR`, withheld | «Âu Lạc (179 TCN)», the anchor round 4 lost |
| `p041:002` | **WITHHELD**, `detected_unrepaired:vi_tone_disagreement`, no text | the attribution: the majority signal proposed «Đặng Khoa», two independent signals objected, the candidate was **rejected** — so it stops being served rather than being half-corrected |

The second row is the one that proves the integration is not a coverage exercise. See §5.

### The lesson, before and after

| | source TSL | projected TSL |
|---|---|---|
| served blocks | 36 | 34 |
| withheld regions | 15 | 17 |
| validated repairs recorded | — | **9** |
| …carried on a withheld region | — | **6** |
| …**trusted** | — | **0** |
| violations (a repair being served) | — | **0** |
| demotions (detected, unrepaired, still served) | — | **2** |
| served text changed | — | **none** (asserted) |

### Artefacts (gitignored — INTERNAL / RESEARCH ONLY, Founder D4)

```
poc-out/round6/ws-c/golden1/lsdl5-bai08.tsl.json        projected TSL
poc-out/round6/ws-c/golden1/lsdl5-bai08.lesson.json     LessonDocument
poc-out/round6/ws-c/golden1/projection-report.json      the run's own report
```

Reproduce:

```
PYTHONPATH=tool/corpus python3 -m repair.tsl_projection \
  --tsl poc-out/round5/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/tc2-r5/lessons/05-sgk-lich-su-va-dia-li-5/bai-08.tsl.json \
  --ledger poc-out/round5/lane-c/tc2-lsdl5/v1/report/repair-ledger.jsonl \
  --out poc-out/round6/ws-c/golden1/lsdl5-bai08.tsl.json \
  --lesson-document poc-out/round6/ws-c/golden1/lsdl5-bai08.lesson.json \
  --subject "Lịch sử và Địa lí" --grade 5
```

## 4. Fixture version safety

Every record and the document carry the chain:
`sourceTslSha256 → projectedTslSha256 → ledgerRun → pipeline → sdmVersion → repairVersion →
frameworkVersion → projection → generator → sourceTslPath → ledgerPath`.

**`hashMethod` travels with every hash**, because `shasum -a 256` on the file does **not** reproduce
these numbers and a hash a reader cannot reproduce looks like tampering:

```
sha256(json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False))
```

Canonical JSON is the right choice — it survives reformatting and key reordering where a raw byte
hash does not — so the method is a field, not a convention.

### FINDING — an artefact that misstates its own generation

GOLDEN #1's source lesson gives **three different answers** about which generation it is:

| label | says | is it trustworthy? |
|---|---|---|
| directory | `tc2-r5` | a filing decision |
| `pipeline` field | `tc2-p1` | copied from whatever `tc2_tsl.build_book` was invoked with |
| block `provenance.sdm_version` | **`sdm-v3`** | **authoritative** — it fixes the structure of the blocks |

This is exactly why «do not silently mix generations» is a rule. `generation_check()` now records
the discrepancy **on the artefact**, names `sdmVersion` as authoritative, and does **not** reconcile
the labels: renaming either would rewrite provenance. The base was chosen on the SDM version
(sdm-v3, current) and *not* on the pipeline string; the `tc2-p2`/`tc2-p3` copies of "bai-08" are a
partial attach of 9 blocks that **does not contain `p039:000` at all**, and choosing a base because
it omits the hard case would be manufacturing the result.

### The cap did not fire here, and that is not because capping never fires

Lane C's ledger `run` block carries only `{lane, book, lesson}` — no `baseline`/`pipeline` — so
`samePipelineAsLedger` is **false** and the projection stayed in its advisory mode; and Lane C
recorded no `restore` row, so there was nothing to cap. **A `run_gold.py`-style ledger WOULD be
capped**: it restores in place (`Outcome.restore_entry` → `TRUSTED`), and every such row is turned
into `VALIDATED_REPAIR` + `caps: ['trust_gate:founder_decision_absent']`, with the cap written onto
the region's reasons as well. Verified on KHTN 7 Bài 20 against `tc2-p3-lin`: 1 repair crossed,
`cappedLaboratoryRestores: 1`.

## 5. Doctrine that shaped the design

**Never weaken a guard for coverage.** Round 5's decisive evidence: guard relaxation restored 1 of
19 falsely-withheld regions at precision **0.000**; deterministic repair restored 10 of 10, holdout
8 of 8. Nothing in this workstream touches a guard. The only thing that moves is the *disposition*,
and only when a validator ruled.

**…and its mirror, which cost a design revision.** The projection's first draft kept a served block
served when the ledger said `WITHHELD`/`SUSPECT`/`CONFLICT`, to avoid changing accounting. That is
*overriding a fail-closed ruling to protect coverage* — the same sin from the other side. The
default is now `on_detected_unrepaired='withhold'`: **the ledger is honoured**. It can only remove
text from the served set, so it cannot serve anything wrong — but it can withdraw something right,
so:

> **FALSE-DEMOTION EXPOSURE is published beside the restores, never folded into them.** GOLDEN #1:
> **2 blocks demoted.** Round-5 prior for the comparable act: demotion precision **0.250** on 4
> blocks. `false_correction_rate` is the correct P0 for a *repairer* and is blind to a *detector*.

A demotion is applied **only** when the served text still equals the observation the ledger ruled
on; otherwise the join is unverified and nothing is done.

**A served block that carries a repair is four different things, not one.** Conflating them is how
a lane fools itself, so `classify_served` names them:

| kind | meaning | action |
|---|---|---|
| `repair_served` | the served text **is** the proposal — an ungated repair is on the path to a child | **VIOLATION** · refuse (default), or demote |
| `restore_served` | the ledger restored a withheld block and this TSL was built from that pipeline | **VIOLATION** · refuse (default), or demote |
| `served_unrepaired` | the served text is the **original observation** and a validator judged it wrong | FINDING · pre-existing false trust; acting changes WS-A accounting |
| `join_unverified` | the served text is neither — this TSL is not the text the ledger saw | FINDING · **no claim, no action** |

**No constructor from a presentation form.** A2's `MathExpression` has `from_json` and deliberately
no `from_latex`. `ValidatedRepair` has `from_json` requiring the whole trace, and a test asserts
`from_text` / `from_latex` / `from_summary` / `from_string` / `from_display` do not exist.

**Serialisation launders provenance.** E2 found a round trip *upgrading* a grounding.
`assert_repair_not_strengthened` closes the disposition axis and the `servable` flag, refuses a
dropped **cap** (dropping a cap drops the reason a repair was held back), and delegates the
grounding half to E1's own `assert_not_strengthened` — one implementation, not two. The Dart side
has the same guard as `ValidatedRepairRef.notStrengthened`.

**LLM.** Nothing in this workstream calls one, proposes with one, or lets one rule. Round-5
evidence: recall 0.717, false-correction rate **1.000**.

## 6. The three structural obstacles

### Obstacle 1 — the bridge had no carrier for structured content · PARTIAL

`ROLE_MAP` had 11 keys and no `formula`, so a formula region fell to `unknown_role:formula` — a
reason code saying «the machine does not know what this is» about a role the machine assigned at
confidence 0.95. Round 5 named that exact sin at the other end of the pipeline (`empty_block` on a
block reading `7 8 2 8 7 - 2 8 5 8` «misstates what was lost»).

**Done:** `KNOWN_UNCARRIED_ROLES = {'formula'}` → reason `no_carrier:formula`, counted separately as
`noCarrierWithheld`. Behaviour-neutral for the app today: `withheld_card.dart` matches
`reason.contains('formula')` **before** `unknown_role`, so the child-facing words are unchanged.
The structure itself crosses corpus-side in `repairs[].structuredValue` and is countable on the
block as `structuredKind` — never as a rendering.

**Not done, and deliberately:** a **servable** structured block kind. It needs app-side rendering
(WS-D) *and* a Founder trust decision, and the round-5 harm was precisely a flattened expression
shown as arithmetic the book does not contain. The honest position today is the one that already
works end to end: **withheld region + page crop + provenance**, with the structure countable.
Extending `KNOWN_UNCARRIED_ROLES` to `footnote` / `activity` / `option` (64 / 50 / 4 blocks
corpus-wide) would change what a child reads and needs a WS-D wording change first — a coordination
item, not a unilateral one.

### Obstacle 2 — the app fails closed on the whole document · DONE, scoped

`lesson_document.dart:1017` — one bad block rejects the entire lesson. That is deliberate
fail-closed design and it stays, for every **integrity violation**. But it also means a pack built
by a newer bridge makes a whole lesson disappear — that is a *shipping* rule («pack and app must
ship together»), not a safety rule.

`LessonBlock.unsupported()` lowers exactly that one case to the block: an **unknown `type`** becomes
a `WithheldBlock` with reason `unsupported_block_type:<type>`, counted in
`LessonDocument.unsupportedBlockTypes`. It cannot become a way for bad content to survive because:

* the result is a `WithheldBlock`, a type with **no text field** — not a byte of the unknown block's
  `text` or `latex` is readable, asserted by a test that greps the serialised document;
* `trust` is **forced** to `withheld` regardless of what the pack claimed;
* it is **counted**, so a newer-pack event is visible rather than a lesson quietly getting poorer —
  the R13 lesson applied on the app side;
* **every integrity violation still rejects the whole document**: withheld trust on a text block, a
  heading without text, a withheld region without a reason, a missing `sourceRef`, an unknown type
  carrying a `repair`. Six such cases are asserted.
* `strictBlockTypes: true` restores all-or-nothing for a packaging gate.

### Obstacle 3 — the app has no rich text · ACCEPTED AS IS

0 of 147 Dart files contain `RichText`/`TextSpan`/`Text.rich`; no math/markdown/LaTeX/SVG/WebView
dependency. Nothing here adds one. The rendering path is the page crop with provenance that already
works, which for a validated STEM region costs zero app work and is honest. WS-D owns the view.

## 7. HISTORICAL CORRECTION TO ROUND 5 — the dispose row's verdict

**The defect.** `engine.run_block` wrote the dispose row's `validation` as `_merge()` over **every**
candidate a block produced, not the one that won. So a block whose disposition is
`VALIDATED_REPAIR` could carry, on the same row, a merged verdict of `rejected` — because a
*different* rule's candidate had been rejected earlier in the loop. Found on LS&ĐL 5 Bài 8
`p038:018`: `lanec.tone-majority-v1` validated, `lanec.tone-corroboration-v1` had been rejected, and
the row reads «VALIDATED_REPAIR … rejected». A reader taking the verdict at face value concludes the
repair failed.

It is the same family as R13's disappearance with no reason code and E2's self-strengthening
grounding: **a component reporting something other than what happened, with no test able to see it.**

**The fix (fix forward, preserve history, mark the correction).** The dispose row now carries the
ruling of the **winning** candidate. With no winner, the merge over all is kept — nothing won, and
saying so is honest. `entry_id` is derived from block/class/disposition/stage/observations/
candidate/reasons/prior and **never** from the validation, so historical ledgers keep their
identities and stay joinable.

**The delta, measured over all 20 round-5 ledgers on disk:**

| | |
|---|---|
| dispose rows with disposition `VALIDATED_REPAIR` | **317** |
| …whose recorded verdict was not the winning candidate's ruling | **12 = 0.0379** (3 distinct blocks) |
| direction of every one of them | `rejected` → `validated` |
| in Lane C's LS&ĐL 5 Bài 8 ledger | 12 |
| in the 19 Lane A1 pipeline ledgers | **0 of 305** — A1 registers one repairer per failure class, so the multi-candidate case never arises there |

**No published round-5 metric changes.** `Ledger.false_correction_report` and `run_gold`'s
scoreboard read `disposition` and `final_value`, never the dispose row's `validation`; Lane C's own
table lists per-candidate verdicts (`rejected, validated`) rather than the merged one. What changes
is what a **reader of a dispose row** sees — which is exactly what a downstream integrator consumes.
**Round 5's report stands as published.** The join in `tsl_projection._final_rows` also pairs the
dispose row with the `validate` row for the same candidate id, so a *historical* ledger is read
correctly without being rewritten.

## 8. Where the code is

| file | what |
|---|---|
| `tool/corpus/repair/validated.py` | `ValidatedRepair`, `assert_repair_not_strengthened`, `grounding_for`, `resolve_validator` |
| `tool/corpus/repair/tsl_projection.py` | the TSL → TSL join, `check_projection`, `generation_check`, CLI |
| `tool/corpus/repair/ledger.py` | `entry_from_json` |
| `tool/corpus/repair/engine.py` | the dispose-row ruling fix (§7) |
| `tool/corpus/tsl_to_lesson_document.py` | `repair_of`, `KNOWN_UNCARRIED_ROLES`, `repair_summary`, the value-leak assertion |
| `lib/core/lesson_model/repair_record.dart` | `RepairDisposition`, `ValidatedRepairRef` |
| `lib/core/lesson_model/lesson_document.dart` | `WithheldBlock.repair`, `LessonBlock.unsupported`, `unsupportedBlockTypes`, `strictBlockTypes` |
| `tool/tests/test_repair_integration.py` | 30 tests, incl. GATE C on the real lesson |
| `test/core/lesson_model/repair_record_test.dart` | 12 tests, the app-side contract |

## 9. What this does NOT claim

* **No repair became trusted.** `trusted = 0` is an invariant asserted in code, not a measurement.
* **No child is better served yet.** A validated repair that is visible and withheld does not put a
  word on a screen. `RESTORED ≠ TRUSTED`, and `VISIBLE ≠ SERVED`.
* **The projection does not measure repair quality.** Restore precision, false-correction rate and
  false-demotion rate are measured upstream, by the lanes that own the repairers.
* **Setting the production trust threshold is untouched**, and there is no code path in this branch
  that could implement it.
