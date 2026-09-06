# 09 · ARCHITECTURE AND DATA CHANGES

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**None of these changes is merged.** Every one lives on an open PR.

---

## 1. NEW SUBSYSTEMS

| Subsystem | Path | WS / PR | State |
|---|---|---|---|
| **Conservation ledger** — four dispositions, the invariant, and a check that **exits non-zero** | `tool/corpus/accounting/**` (new): `dispositions.py` · `ledger.py` · `lesson_identity.py` · `golden-slices.json` | A · #91 | **DONE** |
| **Recognition harness** — census, targeted re-crop, consensus rule, contact sheets | `tool/corpus/recognition/**` (new) + `tool/ocr/ocr_crop.swift` | B · #92 | **DONE** |
| **ValidatedRepair + TSL projection** | `tool/corpus/repair/validated.py` · `repair/tsl_projection.py` · `repair/ledger.py::entry_from_json` | C · #90 | **DONE** |
| **App-side repair contract** | `lib/core/lesson_model/repair_record.dart` · `WithheldBlock.repair` · `LessonBlock.unsupported` · `unsupportedBlockTypes` · `strictBlockTypes` | C · #90 | **DONE** |
| **Fixture lineage gate** — L1…L6, `--require-repair` | `tool/evidence/fixture_lineage.py` (16 tests) | D · #93 | **DONE** |
| **Golden delivery driver** · **learning-view census** | `tool/evidence/golden_delivery.py` · `tool/evidence/learning_view_census.py` | D · #93 | **DONE** |
| **Workspace Option B** (flag and options A/C **removed**) | `lib/features/lesson_workspace/**` | D · #93 | **DONE** |

---

## 2. THE ROOT-CAUSE FIX — one line of ordering, three findings explained

**Where:** `tool/corpus/tc2_sdm.py`, `assign_role`.

The **letterless test ran second**, before the rules for TABLE, FORMULA, page furniture, figure text
and the printed `?` answer slot. **Every letterless region reached `empty` before anything could
name it.**

| measured consequence | value |
|---|---|
| Docling FORMULA regions that never reached the `formula` role | **17 of 18** |
| occurrences of `role.value == 'formula'` in 1,655 blocks | **1** |

**One mechanism explains R13's disappearance, Lane A2's `empty_block` finding, and the
`7 8 2 8 7 - 2 8 5 8` misdescription — together.**

**The fix asks nothing new.** `letterless_role()` restores the order **for letterless text only**,
using the pipeline's own existing vocabulary **with the guards that vocabulary already carries** — a
`formula` without a validated structure is still withheld (`formula_unvalidated`, Founder STEM §4).
Only when no structural evidence names a region does it stay `empty`, **and then its evidence says
which of the six classes it is** instead of claiming there was nothing there.

**And `tool/corpus/tc2_tsl.py` no longer `continue`s past a furniture role. That `continue` *was*
the disappearance.** Every region that is neither served nor withheld is now recorded in a new
`excluded[]` with `disposition`, `reason`, `bbox` and role evidence, and **each document states its
own `conservation` arithmetic.**

---

## 3. `CONNECT ≠ TRUST` — enforced in five places, none of them a policy

| where | mechanism |
|---|---|
| `repair/validated.py` | **`disposition` is a class attribute, not a field** — it may only read `VALIDATED_REPAIR`. `from_entry` raises `TrustEscalation` on a `restore` row; `from_json` raises on any other disposition, **so serialisation cannot launder one either** *(PROVEN — line 167)* |
| `repair/tsl_projection.py` | **there is no promotion mechanism at all**; a laboratory restore is *capped*, with the reason written in three places |
| `tsl_to_lesson_document.py` | `repair_of()` **refuses rather than sanitises**; **a served block carrying a repair is itself a refusal** — that is the shape of an ungated restore |
| `check_document` | searches the **whole serialised document** for each proposed value — *the weak version reads the fields we chose to emit and finds nothing because we chose not to emit them* |
| `lib/core/lesson_model/` | `repair` is a field **only on `WithheldBlock`**; a null `ValidatedRepairRef` **rejects the whole document** *(PROVEN — lines 236 / 263 / 608)* |

**What a repaired region gains is not text — it is that it becomes *visible and countable*.**
That is the end of the state where validated output was invisible.

**`ValidatedRepair` retains all ten required things**, and reuses rather than reinvents:
`original_observations` and `candidate` are **round 5's own frozen dataclasses**; `source_grounding`
**is Lane E1's `SourceGrounding`, imported**, with a test asserting `isinstance` and byte-equal
`to_json()`. **No fourth provenance universe.** `ledger.entry_from_json` was added because the
ledger had a write side and a raw read side **but no way back to the typed row — that gap is exactly
how a fourth universe starts.**

---

## 4. THE BRIDGE — one honest reason code, one deliberate non-change

**Done:** `KNOWN_UNCARRIED_ROLES = {'formula': 'no_carrier:formula'}` *(PROVEN — line 112)*, counted
separately as `noCarrierWithheld`. It replaces `unknown_role:formula` — *a reason code saying «the
machine does not know what this is» about a role the machine itself assigned at confidence 0.95.*
**Round 5 named that exact sin at the other end of the pipeline** (`empty_block` on a block reading
`7 8 2 8 7 - 2 8 5 8` «misstates what was lost»). Behaviour-neutral for the app: `withheld_card.dart`
matches `reason.contains('formula')` **before** `unknown_role`, so the child-facing words are
unchanged.

**Deliberately not done — a *servable* structured block kind.** It needs app-side rendering **and** a
Founder trust decision, and **round 5's harm was precisely a flattened expression shown as
arithmetic the book does not contain.** The honest position today is the one that already works end
to end: **withheld region + page crop + provenance**, with the structure countable as
`structuredKind`. Extending `KNOWN_UNCARRIED_ROLES` to `footnote`/`activity`/`option` (64/50/4)
**changes what a child reads** and needs a wording decision first — **a coordination item, not a
unilateral one.**

---

## 5. THE APP'S FAIL-CLOSED RULE — scoped, not weakened

`lesson_document.dart:1017` — one bad block rejects the entire lesson. **That stays, for every
integrity violation.** But it also meant a pack built by a newer bridge makes a whole lesson
disappear — *a **shipping** rule («pack and app must ship together»), not a safety rule.*

`LessonBlock.unsupported()` lowers **exactly that one case** to the block: an **unknown `type`**
becomes a `WithheldBlock` with reason `unsupported_block_type:<type>`, counted in
`unsupportedBlockTypes`. It cannot become a way for bad content to survive because:

- the result is a `WithheldBlock` — **a type with no text field**; not a byte of the unknown block's
  `text` or `latex` is readable, asserted by a test that greps the serialised document;
- `trust` is **forced** to `withheld` regardless of what the pack claimed;
- it is **counted**, so a newer-pack event is **visible** rather than a lesson quietly getting
  poorer — **the R13 lesson applied on the app side**;
- **every integrity violation still rejects the whole document** — six such cases asserted, including
  an unknown type carrying a `repair`;
- `strictBlockTypes: true` restores all-or-nothing for a packaging gate.

---

## 6. DATA CHANGES

| Change | Amount | Rationale |
|---|---|---|
| **82 previously unaccounted regions given a disposition** | **50 EXCLUDED_WITH_REASON · 32 WITHHELD with a truthful reason** | *A page number is a defined non-learning region. A block of digits is not.* |
| **Served set** | **byte-identical** in every population (285 / 234 / 43) | no guard weakened, no coverage bought |
| **Withheld counts rise** | 135→144 · 124→147 · 30→37 | always-refused regions became **visible**; **rates before and after are not comparable without saying so** |
| **Two regions demoted SERVED → WITHHELD** on Golden #1 | 2 | WS-C honouring a fail-closed ledger ruling — **a separate movement, never folded into the accounting fix** |
| **Toán exercises removed from the shipped packs** | `toanExercises` → **0** *(PROVEN)* | round 5's fail-closed rule reaching an APK for the first time |
| **Pack attachment rule corrected** | `capped-toc-v1` → **`capped-toc-v2`** *(PROVEN)* | the stamp finally matches the code |
| **Golden #1 replaces a synthetic fixture with a real one** | 23 `[MẪU]` blocks → **34 real SGK blocks + 17 reasoned gaps** | `FIXTURE ≠ TRUSTED CORPUS` |
| **The lesson title derived from the printed table of contents** | 1 field | WS-C's document carried the OCR-broken «THỜI KĨ BẮC THUỘC»; `lesson-title-v1` derives the real title and records `titleDerivation`. **It changed nothing else — timeline events 0 → 0.** |

**Data versioning held.** Round 5's published figures are unchanged and reproducible; every
correction sits **beside** them marked `HISTORICAL CORRECTION TO ROUND 5`. `entry_id` is derived
from block/class/disposition/stage/observations/candidate/reasons/prior and **never** from the
validation, **so historical ledgers keep their identities and stay joinable.**

---

## 7. TWO FINDINGS ABOUT THE MEASURING SYSTEM ITSELF

**(a) Two hash methods coexist and give different numbers.** The committed bridge hashes **file
bytes** (`sha256_file`); the round-6 repair path hashes **canonical JSON**
(`sort_keys`, compact, `ensure_ascii=False`). **A reviewer running `shasum -a 256` on a repair-path
artefact gets a different number and concludes the artefact was tampered with.** The lineage gate
now computes **both** and **names which one matched** — and `hashMethod` travels **with every hash**,
as a field rather than a convention.

**(b) The pipeline name does not identify a generation.** Golden #1's source gives **three different
answers**: the directory says `tc2-r5`, the `pipeline` field says `tc2-p1`, and the block
`provenance.sdm_version` says **`sdm-v3`** — **which is the authoritative one, because it fixes the
structure of the blocks.** `generation_check()` records the discrepancy **on the artefact**, names
`sdmVersion` as authoritative, and **does not reconcile the labels — renaming either would rewrite
provenance.**

*The base was chosen on the SDM version, not on the pipeline string. And the `tc2-p2`/`tc2-p3`
copies of Bài 8 are a partial attach of 9 blocks that **does not contain `p039:000` at all** —
choosing a base because it omits the hard case would have been manufacturing the result.*

---

## 8. ARCHITECTURE PRECEDENTS — carried forward and extended

Round 5 established four; round 6 kept all four and added three.

**Carried:** no constructor from a presentation form *(asserted by a test that `from_text` /
`from_latex` / `from_summary` / `from_string` / `from_display` do **not exist**)* · identity
redaction at the render boundary · every provenance-bearing type needs a round-trip test asserting
grounding **never strengthens** · a plugin loader must fail loudly.

**Added by round 6:**

1. **A cap is part of the provenance and may not be dropped.**
   `assert_repair_not_strengthened` closes the disposition axis **and** the `servable` flag **and**
   refuses a dropped **cap** — *dropping a cap drops the reason a repair was held back.* It delegates
   the grounding half to E1's own `assert_not_strengthened`: **one implementation, not two.** The
   Dart side carries the same guard.
2. **A test must assert the honesty property, not the data shape.** *«Does this lesson have events»*
   is satisfied by an app faithfully drawing bad data. *«Has anyone been granted trust»* is not.
3. **A canary that fires on real book text guards nothing.** Replace keyword leak checks with
   **structural counts** — e.g. the number of `WithheldBlock`s the app builds must equal the number
   the artefact declares.

---

## 9. WHAT DID **NOT** CHANGE — and why that is correct

- **No production trust threshold.** `THRESHOLDS.json` still does not exist. **`trusted: 0` is
  asserted in code, not measured** — and there is no code path in the round-6 branches that could
  implement a threshold.
- **No rich text.** 0 Dart files with `RichText`/`TextSpan`/`Text.rich`; no math, markdown, LaTeX,
  SVG or WebView dependency. **Accepted as is** — the page crop with provenance is the honest path
  and costs zero app work.
- **No renderer family added.** The census found **`conceptMap` 0** and **`timeline` 0** real
  instances — *two of four families have no data at all.* **FORMS BEFORE RULES applied to a licence
  the plan had already granted.**
- **No dependency added for recognition.** Same Apple Vision engine that ships on iOS, plus PyMuPDF
  and numpy already present.
- **No LLM anywhere in the corpus path.** CodeFormulaV2 was run **as a measured candidate** and
  rejected; even at zero cost its output could only ever be a `RepairCandidate`.
- **`rederive_trust` still does not pass `formula_structured`** — pre-existing, **fail-closed** (it
  can only add a withhold, never remove one), **deliberately not changed**, recorded.
- **`repair/run_gold.py::PERMISSION_REASONS` not extended** with the new `unread:*` codes — arguably
  correct (*a lost arithmetic expression is a fidelity failure, not a permission one*), but it is a
  behaviour change in another workstream's file and was **left for that workstream to decide.**
