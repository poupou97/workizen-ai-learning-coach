# ROUND 4–7 CANONICAL RECORD AUDIT

**Founder task order 43, deliverable 2.** Audited 2026-09-06 against
`integration/round7-2026-09-06` @ `b15bb1e`, from an isolated worktree on branch
`audit/canonical-record`.

**The question this answers is not «can we rebuild the ZIPs».** It is: *is the knowledge that
rounds 4–7 produced in the repository, or is it somewhere that can vanish?* Under the standing
rule — [`docs/governance/REPOSITORY-SOURCE-OF-RECORD.md`](../governance/REPOSITORY-SOURCE-OF-RECORD.md)
— **REPO = CANONICAL RECORD · DESKTOP / ZIP / scratchpad = REVIEW SNAPSHOT ONLY**, and a deleted
review copy is only a project-record loss if something important existed nowhere else.

---

## THE ANSWER, FIRST

**Did the Founder's deletion of the Desktop ZIPs cost the project any record?**

**No — but that was not true when the audit began, and it is not true because the ZIPs were
rebuilt.** It is true now because this audit found **45 documents that existed only inside those
ZIPs and inside a session-scoped scratchpad**, and committed them.

The distinction matters and is the whole finding:

| | |
|---|---|
| The **contents** of the round-4 report ZIP | Were already in git, and are still. The registry's «LOST, NOT RECOVERABLE» row costs bytes, not knowledge — checked category by category below. |
| The **contents** of the round-5, 6 and 7 review ZIPs | Were **not** all in git. The fifteen archive documents per round were authored *for the archive*, in a content directory the builder reads with `content_dir = dirname(spec_path)`, and were never committed. Two of the three surviving copies were luck: the ARCHIVE-REGISTRY says so in its own words — *«inputs that happened to still exist in a session-scoped scratchpad»*. |
| The **identities** of all five ZIPs | Preserved throughout in [`ARCHIVE-REGISTRY.md`](ARCHIVE-REGISTRY.md). A rebuild restores contents, not identity, and the registry is what keeps a rebuilt hash from reading as tampering. |

So: **the deletion cost nothing, and the process that made that true was a coincidence.** Had the
session rolled before this audit ran, rounds 5–7 would have lost their acceptance cards,
falsification registers, plan-vs-actual records and roadmaps. That is the exact hazard order 43
was written to close, and it was live at the moment the order was issued.

**Real GAPs found: 10.** Four are closed in this PR; six remain and are named with what it
would take to close them. **No PARTIAL was turned into DONE.**

---

## HOW «PRESENT» WAS DECIDED

A row is **DONE** only if the named file was opened and found to *carry the thing*. A path that
exists but does not carry the decision is a **GAP**, not a PASS. Where a document was checked and
the category is genuinely absent by design — a threshold that deliberately does not exist — the
row says so rather than scoring it as a miss.

**Status vocabulary** (order 43, unchanged): `DONE` · `PARTIAL` · `FAILED` · `FALSIFIED` ·
`BLOCKED` · `DEFERRED` · `NOT STARTED`.

**Reachability** is a separate axis from status, and it is where round 7 differs from rounds 4–6:

- **canonical** — on `integration/round7-2026-09-06`.
- **canonical (unmerged branch)** — committed and pushed, but reachable only from a `ws-*` branch.
  This is a **weaker form of canonical**: durable in git, invisible to a reader who checks out the
  integration branch. For round 7 this is **by design** — `ROUND7-PLAN.md` ends «DO NOT MERGE.
  STOP AT THE TRUST-ACTIVATION FOUNDER GATE» — so it is merge debt, not negligence. It is still
  recorded, because the plan's own deliverable paths dangle on the branch that quotes them.
- **out of repo** — a real gap unless it is restricted evidence with adequate metadata.

---

## MATRIX

`REPRO?` — can a reader re-derive the numbers from what is committed?
`EXT-EV?` — does the record depend on evidence outside git?

### ROUND 4 — PROVE + EXPERIENCE + DISCOVER + LEGACY REPROCESS

| DOCUMENT / DECISION | CANONICAL REPO PATH | COMMIT | STATUS | REPRO? | EXT-EV? | GAP? |
|---|---|---|---|---|---|---|
| Consolidated report | `docs/research/ROUND4-CONSOLIDATED-REPORT-2026-09-06.md` | `05a0927` | **DONE** — five product scores, five Founder questions, legacy scoreboard, device evidence, open P0s | No — 0 code fences, 0 `tool/` references | Yes — `poc-out/` | — |
| Research plan | `docs/research/ROUND4-PLAN.md` | `2e42487` | **DONE** — lane × *Owns* / *Never touches* ownership matrix | n/a | No | Plan of ownership, not of experiments |
| Task order (authority) | `docs/founder-orders/32-master-task-order-học-cùng-sam-round-4.md` | `337ab56` | **DONE** — verbatim, incl. §16 gates and §13 licence | n/a | No | Committed 2026-09-06, four rounds late |
| Founder decisions | order 32 §1 §7 §16 | `337ab56` | **DONE** — `SCALE-WIRED != TRUSTED`, Golden Slice #2 approved, non-autonomous list | n/a | No | Report carries **requests**, not decisions — 7 open P0s |
| Acceptance criteria | order 32 §16; `docs/research/lane-c/05-GOLDEN-SLICE-2-GATE.md` | `337ab56` · `9e17e7b` | **DONE at lane level** — Bài 8 attach ≥ 0.85 → 0.95 ✓ | Partial | Yes | Round 4 **deliberately set none** at round level: «*No acceptance threshold is set*» (`PIPELINE-…:8`) |
| Methodology | `docs/research/PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md` §0 §12; `legacy-reprocess/ROUND4-BATCH-1-REPORT.md` §2 | `1429fcf` · `bea004c` | **DONE** — gold set, same scorer, dev 38 / held-out 16; D5 denominators | Yes | Yes | — |
| Gates | `ROUND4-CONSOLIDATED-REPORT:22` | `05a0927` | **DONE, as a stated absence** — «**There is no gate to cross**… `trusted` computes to **0 by construction**» | Yes | No | — |
| Threshold definitions | `docs/research/legacy-reprocess/THRESHOLDS.example.json` | `6e1b7b7` | **DONE by design** — template, every operative field `null`, «A TEMPLATE, not a decision» | Yes | No | Honest absence, enforced in code |
| Architecture conclusions | `ROUND4-CONSOLIDATED-REPORT:16`; `lane-c/06-HISTORY-ABSTRACTIONS.md` | `05a0927` · `9e17e7b` | **DONE** — document layer generalises, semantic layer does not | Yes | No | — |
| Measured results | report + `PIPELINE-…` + `LEGACY-REPROCESS-SCOREBOARD.{md,json}` | `05a0927` · `1429fcf` · `0113019` | **DONE** — Wilson intervals throughout (FTR 0.0957 → 0.0734; coverage 439 → 354) | Partial | Yes | — |
| Provenance | `ROUND4-BATCH-1-REPORT.md` §2; device manifests | `bea004c` · `b5be5c2` | **DONE** — tool versions, code shas, sha256 of all 62 outputs | Yes | Yes | Report itself records a provenance **bug**: «every pack built today stamped a rule it was not built with» |
| Reproduction instructions | `PIPELINE-…` §11 «Stable CLI» | `1429fcf` | **PARTIAL** — 6-step runnable block, but rooted at `R=/Users/alexnguyen/projects/…` and reads `poc-out/` | No, not from a clean clone | Yes | **GAP-7** |
| Licensing (D4) | order 32 §13; `ROUND4-PLAN.md:13`; `PIPELINE-…:9`; `lane-c/05:5` | `337ab56` · `2e42487` · `1429fcf` | **DONE** at plan and lane level | n/a | Yes | **GAP-8** — absent from the consolidated report, the document the Founder reads |
| Known limitations | `PIPELINE-…` §10; `ROUND4-BATCH-1-REPORT.md` §12; `LEGACY-…SCOREBOARD.md` «What this scoreboard does not say» | `1429fcf` · `bea004c` · `0113019` | **DONE** | n/a | No | — |
| Round verdict | order 33 line 4: «**Founder ACCEPT Round 4.**» | `337ab56` | **DONE — but recorded outside round 4** | n/a | No | **GAP-9** — no round-4 artefact records its own acceptance; the report still ends «READY FOR FOUNDER REVIEW» |
| Negative / FALSIFIED | `ROUND4-CONSOLIDATED-REPORT:16-19`; `lane-c/02-ASSUMPTION-LEDGER.md:30` | `05a0927` · `373c8b3` | **DONE** — A25 and A26 falsified; legacy rescue **PARTIAL**; ledger PROVEN 5 / FALSIFIED 14 / UNTESTED 4 | Yes | Partial | — |
| Device evidence | `docs/design/track-b-evidence/round4/` (32 frames + manifest); `docs/research/lane-c/evidence/round4-device/` | `2f4a9cd` · `b5be5c2` | **DONE** — frames committed; Lane C walk honestly `QUEUED` (device locked), 0 PASS claimed | Yes | No | — |
| Archive documents | — | — | **FAILED — not recoverable** | No | — | Pre-format `ROUND4-REPORT` ZIP ×2, `bf0d27a9…`. No content directory ever existed. **Contents were repo documents; nothing unique lost** |

### ROUND 5 — DATA ACCURACY: REPAIR → VALIDATE → RESTORE

| DOCUMENT / DECISION | CANONICAL REPO PATH | COMMIT | STATUS | REPRO? | EXT-EV? | GAP? |
|---|---|---|---|---|---|---|
| Consolidated report | `docs/research/ROUND5-CONSOLIDATED-REPORT-2026-09-06.md` (1,034 lines) | `bab657a` | **DONE** — nine lanes, every number re-verified by the coordinator, not relayed | Partial (12 `tool/` refs) | Yes | Never references §16, `ROUND5-PLAN.md` or order 33 — **GAP-8** |
| Research plan | `docs/research/ROUND5-PLAN.md` | `c92c08e` | **DONE** — lane ownership + standing limits (no trust threshold, no mass reprocess, no unrestricted LLM) | n/a | No | — |
| Task order (authority) | `docs/founder-orders/33-…-round-5.md`, §16 at line 552 | `337ab56` | **DONE** — full verbatim text | n/a | No | — |
| Founder decisions | orders 33 · 34 · 35 · 36; D3/D4/D5 in `FALSE-TRUST-AUDIT-PROTOCOL.md:5`, `METRIC-DENOMINATORS.md:3,52` | `337ab56` · `7405e46` · `62679a1` | **DONE** — incl. «STOP treating flattened OCR text as canonical» | n/a | No | — |
| Acceptance criteria | order 33 §16 **and** `docs/research/ROUND5-ACCEPTANCE-CRITERIA.md` | `337ab56` · `8ae8b9a` | **DONE ×2 — reconstruction verified byte-equal to the order after whitespace normalisation** | n/a | No | **GAP-10** — the reconstruction's own rationale («the criteria had only ever existed in the conversation») is now **stale**: it was written at 11:19, the orders landed at 15:21 the same day |
| Methodology | `FALSE-TRUST-AUDIT-PROTOCOL.md` §1–§5; `DATA-ACCURACY-FRAMEWORK.md`; `METRIC-DENOMINATORS.md`; `THIRD-SIGNAL-LAYER.md:78` | `7405e46` · `f2f8617` · `62679a1` · `831573a` | **DONE** — sampling design, ablation not assertion, D5 template («A number without all three parts is not reportable») | Yes | Yes | — |
| Gates | `TRUST-GATE-SENSITIVITY.md:303` | `3a160fd` | **DONE, as a stated absence** — «It sets no acceptance threshold… `test_thresholds.py` asserts the repository has none» | Yes | Yes | Semantic-yield gate **proposed, not built** |
| Threshold definitions | `THIRD-SIGNAL-LAYER.md:112` (arbitration, numeric); `FALSE-TRUST-AUDIT-PROTOCOL.md:72` (bars, PROPOSED) | `831573a` · `7405e46` | **DONE** — every arbitration constant named; production trust bar **absent by design** | Yes | Yes | — |
| Architecture conclusions | `ROUND5-CONSOLIDATED-REPORT:274` §8.1; `THIRD-SIGNAL-LAYER.md:19`; report §11.4 | `bab657a` · `831573a` | **DONE** — «**REPAIR is built and NOT CONNECTED**»; the two «independent» stacks share an OCR engine; 6 primitives carried 224 lessons | Partial | Yes | — |
| Measured results | report §2–§11; `DATA-ACCURACY-SCOREBOARD-LANE-D.md`; `ACCURACY-RECOVERY-RESULT.md`; `VIETNAMESE-REPAIR-RESULT.md` | `bab657a` · `2798adb` · `1733ff7` · `6652d58` | **DONE** — false trust 0.619 → 0.318; teaching-critical 0.476 → 0.100; over-withhold 0.400 → **0.633** | Partial | Yes | — |
| Provenance | `DATA-ACCURACY-SCOREBOARD-LANE-D.md:93` §2a | `2798adb` | **DONE — and the finding is a provenance failure**: «950 of 6,176 page verdicts differ… **896 unexplained**» | Yes | Yes | — |
| Reproduction instructions | four «Reproduce» sections: `ACCURACY-RECOVERY-RESULT.md:503`, `VIETNAMESE-REPAIR-RESULT.md:279`, `TRUST-GATE-SENSITIVITY.md:274`, `FALSE-TRUST-AUDIT-PROTOCOL.md:84` | `1733ff7` · `6652d58` · `3a160fd` · `7405e46` | **PARTIAL** — commands committed, **every input under gitignored `poc-out/`** | No, not from a clean clone | Yes | **GAP-7.** Counter-example proving it is soluble: `tool/corpus/tc_gold/` (54 annotated pages) **is** committed, and the report says so |
| Licensing (D4) | `METRIC-DENOMINATORS.md:50-57`, + 6 restatements | `62679a1` | **DONE** — and D4 is *the stated reason* the reproduction inputs are absent | n/a | Yes | — |
| Known limitations | 6 dedicated sections incl. `FALSE-TRUST-AUDIT-RESULT:253` «what a second annotator should re-check first» | `9c211bd` etc. | **DONE** | n/a | Yes | — |
| Round verdict | `ROUND5-ACCEPTANCE-CRITERIA.md:25` — «**8 PASS · 1 PARTIAL · 1 FAIL**», with a coordinator self-correction | `8ae8b9a` | **PARTIAL** — the *grade* is canonical; **no Founder acceptance of round 5 exists anywhere.** Round 6 opened on round-5 evidence without a verdict statement | n/a | No | Recorded as fact, not scored as loss: the verdict was **never issued**, so nothing is missing from the repo |
| Negative / FALSIFIED | report `:893` `:562` `:907` `:934`; `ACCURACY-RECOVERY-RESULT.md:306`; `VIETNAMESE-REPAIR-RESULT.md:259` | `bab657a` · `1733ff7` · `6652d58` | **DONE — strongest category of the round.** Edge-refinement falsified at 0.5×; Lane C falsified its own round-4 rule; LLM FCR **1.000** → «detector only, never a proposer»; demotion precision 0.250 | Yes | Partial | — |
| Device evidence | `docs/design/track-b-evidence/round5/` (38 files + manifest) | `71b3638` | **DONE** | Yes | No | — |
| **Archive documents (15)** | **`docs/research/round-archives/round05/`** | **`8c88b0b`** | **DONE — canonicalised by this audit** | Yes | No | **GAP-1, CLOSED.** Existed only in the ZIP and a scratchpad |

### ROUND 6 — VERIFIED ACCURACY → REAL PRODUCT

| DOCUMENT / DECISION | CANONICAL REPO PATH | COMMIT | STATUS | REPRO? | EXT-EV? | GAP? |
|---|---|---|---|---|---|---|
| Consolidated report | `docs/research/ROUND6-CONSOLIDATED-REPORT-2026-09-06.md` | `d5a9946` | **DONE** — 16 sections, gates graded | **No — 0 commands, 0 `tool/` refs, 0 `poc-out` refs** | Yes | **GAP-6** — cites only 3 of its own workstream documents; no path from report to evidence for gates B, C or E |
| Research plan | `docs/research/ROUND6-PLAN.md` | `51711c0` | **DONE** — gates fixed *before* the round; carries the golden-delivery addendum with coordinator verification the order lacks | n/a | No | — |
| Task orders | `docs/founder-orders/39` · `40` · `41` | `337ab56` | **DONE** — round-6 master, golden-delivery decision, close decision | n/a | No | — |
| Founder decisions | order 39 §Workspace UX (OPTION B); order 40 (Golden #1/#2/regression) | `337ab56` | **DONE** — «*do NOT claim Math structure reaches child until that path actually exists*» | n/a | No | The consolidated report never cites order 40 or 41 |
| Acceptance criteria | `ROUND6-PLAN.md:24-30` GATE A–E, graded `ROUND6-CONSOLIDATED-REPORT:29-39` | `51711c0` · `d5a9946` | **DONE** — «**4 PASS · 1 TRUTHFUL ZERO**» | n/a | Yes | Neither `TRUTH-ACCOUNTING-ROUND6.md` nor `REPAIR-INTEGRATION-ROUND6.md` self-grades its gate — one witness each |
| Methodology | `TRUTH-ACCOUNTING-ROUND6.md:34-50` (four-disposition conservation + determinism control); `RECOGNITION-FAILURE-CENSUS:39` (three denominators, never summed) | `1df09c7` · `9ee4fe2` | **DONE** | Partial | Yes | — |
| Gates | round gates A–E + 12 cross-round product gates (`report:311-327`) + round-7 gates (order 41) | `d5a9946` · `337ab56` | **DONE** | n/a | Yes | — |
| Threshold definitions | — | — | **NOT STARTED, by design and stated** — «`eligible for teaching` cannot exceed 0 because **no production trust threshold has been set**, and setting one is a Founder gate» | n/a | No | — |
| Architecture conclusions | `report:275`; `TRUTH-ACCOUNTING-ROUND6.md:134`; `REPAIR-INTEGRATION-ROUND6.md:25-37` | `d5a9946` · `1df09c7` · `f2ce138` | **DONE** — «detect, account, recognise, repair, validate and carry — and it may not *serve*»; `role.value == 'formula'` occurred **once in 1,655 blocks** | Yes | Yes | — |
| Measured results | `TRUTH-ACCOUNTING-ROUND6.md:435`; `REPAIR-INTEGRATION-ROUND6.md:8`; `RECOGNITION-RECROP-RESULTS` §3 | `1df09c7` · `f2ce138` · `371b6b0` | **DONE** — 1,878 regions · UNACCOUNTED 138 → 0; 9 validated repairs, **0 trusted**; digit recall 0.500 / 0.403 / 0.061 / 0.038 / 0.181 | Partial | Yes | — |
| Provenance | `REPAIR-INTEGRATION-ROUND6.md:156-166` — the eleven-field chain **and** `hashMethod`, «because `shasum -a 256` on the file does not reproduce these numbers» | `f2ce138` | **DONE — the best provenance record in the repo** | Yes | Yes | — |
| Reproduction instructions | `REPAIR-INTEGRATION-ROUND6.md:145`; `RECOGNITION-FAILURE-CENSUS:147`; `RECOGNITION-RECROP-RESULTS:456`; `TRUTH-ACCOUNTING-ROUND6.md:325` | `f2ce138` · `9ee4fe2` · `371b6b0` · `1df09c7` | **PARTIAL** — present in workstream docs; **the golden-slice runner that produced the headline 138 → 0 has no committed command line** | Partial | Yes | **GAP-7** |
| Licensing (D4) | `REPAIR-INTEGRATION-ROUND6.md:135`; `ROUND6-WS-D-GOLDEN-DELIVERY.md:256`; `report:325` | `f2ce138` · `eeb38c1` · `d5a9946` | **PARTIAL** | n/a | Yes | **GAP-8** — round 6 produced the SGK crops and **never classified them**; the round-**7** report is the first to say LICENSING-DISTRIBUTION BLOCKED. Orders 40 and 41 carry no licensing statement at all |
| Known limitations | `report:130` STILL HYPOTHESIS · `:189` regressions; `RECOGNITION-FAILURE-CENSUS:110` «classes this census cannot observe» | `d5a9946` · `9ee4fe2` | **DONE** — incl. «inventing [table ground truth] to fill a census row would be worse than the gap» | n/a | Yes | — |
| Round verdict | `docs/founder-orders/41-…:3,10-25` — «**ROUND 6 IS ACCEPTED AS CLOSED**», A PASS · B PASS · C PASS · D TRUTHFUL ZERO · E PASS | `337ab56` | **DONE** — Founder-issued, and it matches the coordinator's independent grade | n/a | No | Chain of authority terminates in a session transcript that is not in the repo and is not hashed |
| Negative / FALSIFIED | `report:114-127` «FALSIFIED — including three of my own statements» (11 items) | `d5a9946` | **DONE** — Ω unreachable 0/22 at every scale; CodeFormulaV2 rejected on measurement; «**Nothing was promoted from PARTIAL to DONE**» | Partial | Yes | — |
| Device evidence (GATE E) | **`docs/design/track-b-evidence/round6/MANIFEST.json` + `steps.json`** | **`8c88b0b`** | **PARTIAL — metadata canonicalised by this audit; the 7 frames stay out under D4** | Yes (hashes now full) | Yes | **GAP-2, CLOSED.** GATE E was graded PASS on evidence whose manifest was Desktop-only and whose hashes the repo carried only as 8-hex prefixes |
| Merge-debt audit | `docs/research/ROUND6-MERGE-DEBT-AUDIT.md` | `657192a` | **DONE** — «MERGE #79; #73 is a strict ancestor» | **No — no git command; every ancestry claim asserted** | No | Verified independently by this audit: the claim holds |
| **Archive documents (15)** | **`docs/research/round-archives/round06/`** | **`8c88b0b`** | **DONE — canonicalised by this audit** | Yes | No | **GAP-1, CLOSED** |
| Unmerged branches `ws-a/round6-truth-accounting`, `ws-c/round6-rescue-1115` | — | — | **Zero unique knowledge.** `git cherry` returns `-` for every commit; both are strictly behind the integration branch | n/a | No | Safe to close as subsumed |

### ROUND 7 — TRUST GATE CALIBRATION (STOPPED AT THE FOUNDER GATE)

| DOCUMENT / DECISION | CANONICAL REPO PATH | COMMIT | STATUS | REPRO? | EXT-EV? | GAP? |
|---|---|---|---|---|---|---|
| Consolidated report | `docs/research/ROUND7-CONSOLIDATED-REPORT-2026-09-06.md` | `74d9db6` | **DONE** — gates graded, four workstreams summarised, **branch heads recorded** (`WS-M a6cae3b · WS-T 5e706c9 · WS-R 7d37521 · WS-S 36e4c50`) | **No — 0 commands** | Yes | The heads make the unmerged work *locatable*; this is what keeps GAP-5 from being a loss |
| Research plan | `docs/research/ROUND7-PLAN.md` | `1e31512` | **DONE** — five gates fixed before the round; «NO THRESHOLD THEATRE» | n/a | No | **GAP-5** — all four of its named deliverable paths dangle on this branch |
| Task orders | `docs/founder-orders/41` · `42` · `43` | `337ab56` · `79984f9` | **DONE** — round-7 preparation, title fidelity, closeout | n/a | No | — |
| Founder decisions | order 42 (preserve source verbatim); order 43 (repository = source of record; no round 8; no activation) | `337ab56` · `79984f9` | **DONE** | n/a | No | — |
| Acceptance criteria | `ROUND7-PLAN.md` gates A–E, graded `report:28-38` | `1e31512` · `74d9db6` | **DONE** — **4 PASS · 1 PREPARED, UNACTIVATED**; D «not attemptable this round» | n/a | Yes | — |
| Methodology | `TRUST-CALIBRATION-BLIND-PROTOCOL-v1.md` | `be41f55` | **DONE** — the round's richest methodology: contamination rule, 44 books excluded, seed `20260906`, BLIND-CORE 2,536 / BLIND-TEACHING 1,770, sealed key, both-sides auditing | Yes | Yes | **canonical (unmerged: `ws-t`)** — **GAP-5** |
| Gates | `report:28-38`; freeze chain §2 | `74d9db6` | **DONE** | Partial | Yes | The `freeze.py verify` tool the report cites is **absent from the branch that cites it** |
| Threshold definitions | `TRUST-CALIBRATION-POLICY-v1.md` | `5e706c9` | **DONE** — six bounds with Wilson uppers; BOUND-4 the only passable one, at «45 % of lessons carrying a teaching-critical error», **not recommended** | Yes | Yes | **canonical (unmerged: `ws-t`).** Integration carries BOUND-2/4/5 headlines only; BOUND-0/1/3 and every interval are unmerged-only — **GAP-5** |
| Architecture conclusions | `report:244-248` — «**Calibration is finished and it is not the answer**» | `74d9db6` | **DONE** | n/a | No | — |
| Measured results | `report`; `METRIC-REGISTRY-ROUND7.md` (18 metrics, 18/18 re-derive); `STRUCTURED-GAP-ROUND7.md`; `ROUND6-DEBT-TRIAGE.md` | `74d9db6` · `a6cae3b` · `36e4c50` · `7d37521` | **DONE** — headlines canonical, derivations unmerged | Yes on `ws-*` | Yes | **GAP-5** |
| Provenance | freeze chain in `report:56-58`; `tool/corpus/thresholds/frozen/` | `74d9db6` · `5e706c9` | **PARTIAL** — integration truncates all three frozen hashes to **8 hex characters**; the full 64-hex values and `LEDGER.jsonl` are on `ws-t` | Yes on `ws-t` | Yes | An 8-hex prefix is not a verifiable provenance record — **GAP-5** |
| Reproduction instructions | runbooks in the four `ws-*` documents | `a6cae3b` · `5e706c9` · `36e4c50` · `7d37521` | **PARTIAL** — **zero commands in all five round-7 documents on the integration branch** | No, from integration | Yes | **GAP-5 + GAP-7** |
| Licensing (D4) | `report:85` — «**LICENSING-DISTRIBUTION BLOCKED.** … *TECHNICALLY POSSIBLE != DISTRIBUTION RIGHT*»; `:153`; order 42:13 | `74d9db6` · `337ab56` | **DONE — the strongest licensing record of any round** | n/a | Yes | — |
| Known limitations | `report` §STILL HYPOTHESIS; blind protocol «Disjointness… is **argued** and **not proven**. This is the weakest link in the blindness claim» | `74d9db6` · `be41f55` | **DONE** — but the self-declared weakness is unmerged-only | n/a | Yes | **GAP-5** |
| Round verdict | order 43:6-11 — «Round 7 được ACCEPTED… **CALIBRATION IS FINISHED. THE NEXT BOTTLENECK IS RECOGNITION + ROLE DISAMBIGUATION**» | `79984f9` | **DONE** | n/a | No | The report carries the substance in its own words and ends «READY FOR FOUNDER REVIEW» — pre-acceptance. `eligible = 0` appears in the plan and orders but **not once in the report** |
| Negative / FALSIFIED | `ROUND7-HISTORICAL-CORRECTIONS.md` C1–C5 | `2caafe5` | **DONE — the most valuable document of the round.** C1 falsifies round 6's «cheapest win on the board» — «a servable type is recommended for **ZERO** of the 118»; C2 a rate published without its denominator; C3 the same container-shape defect three times across three rounds; C5 resolves 3,679 / 3,381 as a **definition**, not a conflict | Yes | Partial | — |
| Device evidence | `round07/NO-DEVICE-FRAMES-THIS-ROUND.md` | `8c88b0b` | **BLOCKED — correctly.** No device walk; the Nokia was in personal use. `report:84` «**HARDWARE UNVERIFIED**» | n/a | No | An *absence* is recorded as a document rather than as silence — the right pattern |
| Merge-debt re-audit | `docs/research/ROUND7-MERGE-DEBT-REAUDIT.md` | `457a970` | **DONE** | Partial | No | — |
| Archive registry | `docs/research/ARCHIVE-REGISTRY.md` | `79e199a` → **`c02a878`** | **DONE** — semantics corrected; **D4 classification restored by this audit** | n/a | Yes | **GAP-3, CLOSED** |
| **Archive documents (15)** | **`docs/research/round-archives/round07/`** | **`8c88b0b`** | **DONE — canonicalised by this audit** | Yes | No | **GAP-1, CLOSED.** Includes the archive builder's **independent** grading of the five gates, which agrees with the coordinator on all five — a second witness that existed nowhere in git |

---

## GAP REGISTER — 10 real gaps

A **real GAP** is information that existed only in a ZIP, on the Desktop, in a scratchpad or in
the chat — or a canonical claim the repository cannot support.

### CLOSED IN THIS PR (4)

**GAP-1 · 45 round-archive documents existed only in a ZIP and a session-scoped scratchpad.**
*What was missing:* fifteen documents each for rounds 5, 6 and 7 — `00-START-HERE`,
`01-ROUND-OBJECTIVE`, `02-PLAN-VS-ACTUAL`, `03-WORK-COMPLETED`, `04-FAILURES-AND-FALSIFICATIONS`,
`05-METRICS-BEFORE-AFTER`, `06-PRODUCT-REALITY`, `07-TEST-CI-PR-EVIDENCE`, `08-DEVICE-EVIDENCE`,
`09-ARCHITECTURE-DATA-CHANGES`, `10-OPEN-RISKS-BLOCKERS`, `11-FOUNDER-ACCEPTANCE-CARD`,
`12-NEXT-ROUND-PLAN`, `13-REMAINING-ROADMAP`, `14-JIRA-CONFLUENCE-STATUS`. Every one is on order
43 §1's mandatory list. The acceptance cards are **independent second gradings** of each round's
gates, which exist nowhere else.
*Where it lived:* inside the review ZIPs, and in `scratchpad/round0{5,6,7}-content/` — the
scratchpad the ARCHIVE-REGISTRY itself describes as *«wiped when the session rolls»*.
*May it be canonicalised?* **Yes.** Scanned: no quoted passage exceeds 100 characters; the only
SGK strings are lesson titles and UI text, which D4 explicitly permits. Same envelope as the
consolidated reports already committed. Secret sweep clean.
*Done:* committed to `docs/research/round-archives/` (`8c88b0b`), 82 files, with a README naming
every exclusion.

**GAP-2 · The round-6 device evidence manifest existed only on the Desktop.**
*What was missing:* `MANIFEST.json` and `steps.json` for GATE E — the gate the round-6 report
grades **PASS**. Rounds 3, 4 and 5 had theirs committed; round 6 did not. The repo carried the APK
and fixture hashes only as 8-hex prefixes.
*Where it lived:* `~/Desktop/wal-evidence/round6-ws-d/`.
*May it be canonicalised?* **The metadata yes, the frames no.** The seven PNGs render verbatim SGK
text and stay out under D4.
*Done:* `docs/design/track-b-evidence/round6/` (`8c88b0b`) — full sha256 for the APK, all twelve
packs, the fixture and every frame, plus the `retentionRules` block («*a PASS without an existing
frame is downgraded to UNVERIFIED*»).

**GAP-3 · `ARCHIVE-REGISTRY.md` lost its D4 classification.**
*What was missing:* the sentence explaining that the ZIPs cannot be in Git because they carry
verbatim SGK page images restricted under D4. Present in the file's first version; removed by the
2026-09-06 semantics rewrite and not replaced, leaving five ZIP identities with **no licensing
classification and no stated reason for exclusion** — the two things order 43 §4 requires.
*Done:* restored (`c02a878`), with round 7's crops marked LICENSING-DISTRIBUTION BLOCKED. No hash
touched.

**GAP-4 · `HOC-CUNG-SAM-ROUNDS-INDEX.md` — round verdicts for rounds 3–7 — was Desktop-only.**
*What was missing:* the per-round VERDICT · NORTH STAR · KEY RESULT · PRODUCT DELIVERY · MERGE
STATUS · NEXT BOTTLENECK table, plus the **untruncated** round-4 ZIP hash
(`bf0d27a929f6c7e377ea4cb0b5396f3760360ce1488217282ae61dd2cc4ccb22`, which `ARCHIVE-REGISTRY.md`
carries only as `bf0d27a9…`). `tool/reporting/README.md` step 4 still instructs agents to write
round verdicts to this Desktop path.
*Done:* `docs/research/round-archives/ROUNDS-INDEX.md` (`8c88b0b`), with a prepended banner
superseding its «per-round ZIPs are canonical» line. Original text left intact.

### OPEN (6)

**GAP-5 · Six round-7 documents are canonical only on unmerged branches.**
`METRIC-REGISTRY-ROUND7.md` (`a6cae3b`) · `STRUCTURED-GAP-ROUND7.md` (`36e4c50`) ·
`ROUND6-DEBT-TRIAGE.md` (`7d37521`, byte-identical on `ws-r` and `ws-s`) ·
`TRUST-CALIBRATION-{POLICY,BLIND-PROTOCOL,ROUND7-REPORT}-v1.md` (`5e706c9`, `be41f55`) —
**125 KB.** `ROUND7-PLAN.md` names all four paths as deliverables and **all four dangle** on the
branch that names them.
*Severity:* this is **merge debt, not record loss.** Everything is pushed to `origin`, and
`ROUND7-CONSOLIDATED-REPORT:202` records the four branch heads, so a reader can find it. But a
reader on the integration branch sees a plan pointing at nothing.
*The sharpest instance:* `ROUND6-DEBT-TRIAGE.md` is 476 lines and is the deliverable order 41 §8
demanded («*Classify each: ROUND7-P0 / ROUND7-P1 / DEFERRED WITH REASON. No silent dropping*»).
Integration summarises it in **one line**. `grep -rl 'ROUND7-P0' docs/` on integration returns the
plan and the order — **the instruction survives, the answer does not.** Rows C-1…X-4, the R-5
population contract, the GATE E invariant re-verification and hand-offs HO-1…HO-5 are
unmerged-only.
*May it be canonicalised?* Yes — by merging, which is a **Founder gate**. `ROUND7-PLAN.md` ends
«DO NOT MERGE», so this audit did not.
*Done about it:* recorded here and routed to `MERGE-DEBT-RECONCILIATION-PLAN.md`.

**GAP-6 · No consolidated report can reach its own evidence.**
Machine-counted: ROUND4 report — 0 `tool/` refs, 0 `poc-out` refs, 0 commands. ROUND6 — 0 / 0 / 0.
ROUND7 — 0 / 0 / 0, and one repo path. ROUND5 is the best at 12 `tool/` refs and still 0 commands.
The round-6 report never names `REPAIR-INTEGRATION-ROUND6.md`, either `RECOGNITION-*` document, or
either `ROUND6-WS-D-*` document. A Founder reading only the report has no path to the artefact.
*May it be canonicalised?* Yes — an evidence index per report, no restricted material involved.
*Done about it:* recorded. Not fixed here: editing four consolidated reports is a documentation
change to other lanes' primary artefacts, and this audit's remit was to measure, not rewrite.

**GAP-7 · Reproduction instructions do not execute from a clean clone.**
Every «Reproduce» section across rounds 4–7 reads inputs from gitignored `poc-out/` (14 GB) or from
`/Users/alexnguyen/projects/…` absolute paths. This is **structural, and D4 is the cause** —
committing the inputs is forbidden. Two consequences are unmitigated: no committed statement of the
trade-off, and **no hash layer** over `poc-out/` or `nguon-chi-thuc/` (9.8 GB), so the manifests
carry counts but no digests and a corpus change cannot be detected from git alone.
*The counter-example proving it is soluble:* `tool/corpus/tc_gold/` — 54 hand-annotated pages,
committed, and the round-5 report says «*so a clean clone reproduces it*».
*May it be canonicalised?* The **inputs no** (D4, size). A **derived-statistics or hash-manifest
layer yes** — and that is the fix worth making.
*Done about it:* recorded, with the tc_gold precedent named.

**GAP-8 · Licensing classification is missing from the documents that most need it.**
The round-4 consolidated report carries **no** D4 statement. Round 6 **produced** the SGK crops and
never classified them — orders 40 and 41, which decide golden delivery and close the round, carry
no licensing statement at all; the round-**7** report is the first to say
LICENSING-DISTRIBUTION BLOCKED.
*Note:* D4 itself is well recorded — defined verbatim at
`docs/founder-orders/30-…:67-80`, operationalised at `METRIC-DENOMINATORS.md:50-57`, and
**enforced by test** (`lesson_document_test.dart:143` asserts `provenance.distribution` contains
`D4`). The gap is placement, not existence.
*May it be canonicalised?* Yes.
*Done about it:* recorded; restored where it had regressed (GAP-3).

**GAP-9 · Round-4 and round-5 artefacts do not record their own adjudication.**
The round-4 verdict («Founder ACCEPT Round 4») lives only in the round-**5** order; the round-4
report still ends «READY FOR FOUNDER REVIEW». A reader opening the round-4 folder would conclude
the round was never adjudicated. **Round 5 has no Founder verdict at all** — round 6 opened on its
evidence without one. Round 5's grade (8·1·1) exists only in `ROUND5-ACCEPTANCE-CRITERIA.md`, and
the substantive assessment it quotes — «*succeeded as a research round, failed as a delivery
round*» — appears in the repository exactly once, as a back-quotation from a chat message.
*May it be canonicalised?* The round-4 pointer **yes**. The round-5 Founder verdict **cannot be
canonicalised because it was never issued** — that is a fact to record, not a hole to fill. This
audit will not invent one.
*Done about it:* recorded here as the canonical statement of both.

**GAP-10 · Round-5 documents cite a gap that the founder-orders commit already closed.**
`ROUND5-ACCEPTANCE-CRITERIA.md:3-7` says the §16 criteria «*had only ever existed in the
conversation that issued them*». That was **true when written** — the file landed at 11:19:41,
`docs/founder-orders/` at 15:21:49 the same day — and is **stale now**: order 33 §16 is committed
at line 552, and the reconstruction is **byte-equal to it**. The stale claim propagated to
`ROUND6-CONSOLIDATED-REPORT:197`, `REPOSITORY-SOURCE-OF-RECORD.md:32` and
`founder-orders/README.md:9`, where it serves as the *motivating example* for a governance rule.
*The rule is right; its cited evidence has expired.* This is precisely the hazard the workspace
`CLAUDE.md` names: *«When you close a founder question, grep the workspace for anything still
citing it as open — that sweep is part of closing it.»*
*May it be canonicalised?* Yes — a one-line tense correction plus a back-link from
`ROUND5-ACCEPTANCE-CRITERIA.md` to order 33.
*Done about it:* recorded. Not edited here — three of the four files belong to other lanes working
concurrently, and a same-file edit is how round 6 collected three collisions.

---

## EXTERNAL-EVIDENCE DEPENDENCY — metadata sufficiency

Order 43 §4 requires eight things for any evidence body kept out of Git.

| Requirement | `poc-out/` + SGK corpus (14 GB + 9.8 GB) | Device evidence | Review ZIPs |
|---|---|---|---|
| (a) manifest | **DONE** — `docs/ingest-manifests/` ×13, `trusted-corpus/MANIFEST.md`, `pre-autonomy-audit/MANIFEST.md` | **DONE for rounds 3–6** (round 6 by this PR); round 7 has none because no walk happened, recorded as a document | **DONE** — `ARCHIVE-REGISTRY.md` |
| (b) provenance | **DONE** — per-script «source of truth» tables, `ingestionCommit` | **DONE** — git sha + branch + dirty flag + fixture generator + device `getprop` | **DONE** |
| (c) hash / SHA | **GAP-7** — counts, no digests | **DONE** — APK, packs, fixture, per-frame sha256; `hashMethod` documented | **DONE** — original *and* rebuilt, all five |
| (d) source / status | **DONE** — `docStatus`, anomaly lists | **DONE** — PASS / FAIL / SKIP / UNVERIFIED / QUEUED / downgraded | **DONE** — LOST / REBUILT / ORIGINAL |
| (e) reproduction | **PARTIAL** — strong in workstream docs, **absent from every consolidated report** (GAP-6) | **DONE** — `tool/evidence/retain.py` + adb checklists | **DONE** — `build_round_archive.py` + all three specs now committed |
| (f) licensing classification | **DONE** — D4 defined, restated, enforced by test | **DONE** — `retentionRules` in every manifest | **DONE** — restored (GAP-3) + `classification` in each spec |
| (g) relation to report | **DONE** — MANIFEST tables + per-doc D4 lines | **DONE** — steps → expect → result | **DONE** — round verdicts now in-repo (GAP-4) |
| (h) reason not in Git | **DONE** — `.gitignore:1-16` gives three ranked reasons, copyright first | **DONE** — `retentionRules[1]` | **DONE** — restored (GAP-3) |

**Restricted evidence was not copied into Git to close any gap.** Excluded and stated: 7 round-6
device frames · round-6/7 artefact trees (1.3 MB + 5.8 MB of lesson fixtures and packs) · all SGK
pages and crops · `poc-out/` · `nguon-chi-thuc/`. Not duplicated because already in git elsewhere:
`tool/corpus/thresholds/frozen/` on `ws-t` (verified byte-identical) and
`tool/corpus/accounting/golden-slices.json`.

---

## WHAT THIS AUDIT CHANGED

| Commit | Change |
|---|---|
| `8c88b0b` | 82 files — the 45 round-archive documents, their evidence and manifests, `ROUNDS-INDEX.md`, and the round-6 device evidence metadata |
| `c02a878` | `ARCHIVE-REGISTRY.md` — D4 classification and reason-not-in-Git restored |
| *(this file)* | The audit |

**No status was promoted.** Round 5 criterion 4 remains **FAIL** and criterion 5 **PARTIAL**;
round 6 gate D remains a **TRUTHFUL ZERO**; round 7 gate D remains **PREPARED, UNACTIVATED**;
WS-S's S5 remains **PARTIAL**; round-7 hardware remains **UNVERIFIED**; `trusted = 0` and
`eligible for teaching = 0` are unchanged. The round-4 archive remains **LOST, NOT RECOVERABLE**.

**DO NOT MERGE.** Nothing here activates anything, and no round 8 is opened.
