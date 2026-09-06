# JIRA RECONCILIATION — project WAL against repository truth · 2026-09-06

Executed under `docs/founder-orders/45-founder-task-jira-reconciliation-and-next-work-selection.md`.
Board: `workizen.atlassian.net` · project **WAL**. Repository truth taken from `main` at `58e9709`
(rounds 4–7 merged that morning at `14df3ec`, 306 commits).

**The rule this pass obeyed.** The repository is the canonical source of record; Jira is the
execution layer and must reflect it. Never the other way round. **No status was inferred from a
title or a commit message** — every transition below cites a file that exists on `main`, a
measured result inside it, or a Founder order that decided it.

---

## The gap that made this necessary

Before this pass the newest update anywhere in WAL was **2026-09-05T16:29** (WAL-209/210). Since
then the project ran **rounds 5, 6 and 7** plus a full merge-debt reconciliation — nine lanes, four
workstreams, four more workstreams, PRs #79–#97, and 306 commits onto `main`. The repository had
already measured its own invisibility and written it down twice:

> `docs/research/round-archives/round05/14-JIRA-CONFLUENCE-STATUS.md` — "**No Jira issue was
> created, transitioned or commented for any of the nine round-5 lanes.**"
>
> `docs/research/round-archives/round06/14-JIRA-CONFLUENCE-STATUS.md` — JQL `updated >= "2026-09-06"`
> returned "**0 issues. Empty result set.**" … "Two consecutive rounds have now closed without a
> single tracker artefact."

A cross-check confirms the scale: **`grep -c "WAL-"` returns 0** for all four consolidated round
reports, all four round plans, `NEXT-RESEARCH-DIRECTION.md`, both merge-debt documents and
`ROUND4-7-CANONICAL-RECORD-AUDIT.md`. The highest WAL key mentioned anywhere in `docs/` was
**WAL-210**. Rounds 4–7 are entirely un-keyed.

---

## JIRA BEFORE → JIRA RECONCILED

| | Before | After |
|---|---|---|
| Total issues | **210** | **222** |
| Done | 147 | **155** |
| In Progress | 22 | 26 |
| Ideas | 34 | 31 |
| Ready | 5 | 9 |
| QA | 2 | 1 |
| Newest activity | 2026-09-05T16:29 | 2026-09-06 |

Issues created: **12** (WAL-211 … WAL-222). Statuses changed: **13**. Descriptions rewritten
against repository truth: **6**. Comments with evidence added: **8**. Issue links created: **3**.
Issues closed as duplicate: **0** — none were found.

---

## Classification — counts per category

| # | Category | Count | Notes |
|---|---|---|---|
| 1 | Truly DONE | **147** | Pre-existing Done. Two annotated rather than reopened — see WAL-209/210 below. |
| 2 | DONE but Jira not updated | **3** | WAL-204, WAL-56, WAL-89 |
| 3 | IN PROGRESS / QA but actually finished | **2** | WAL-206, WAL-207 |
| 4 | TODO / READY still valid | **51** | 30 tasks + 21 open epics, left untouched |
| 5 | SUPERSEDED | **0 closed** | 4 issues carry a recorded supersession note instead — closing them would have destroyed the evidence chain |
| 6 | DUPLICATE | **0** | Searched; none found |
| 7 | BLOCKED | **4** | WAL-10, WAL-13, WAL-43, WAL-202 |
| 8 | Description no longer matches architecture/research truth | **3** | WAL-192, WAL-203, WAL-205 — rewritten |
| 9 | Repo work with no Jira issue | **12 created** | WAL-211 … WAL-222 |

---

## Classification table — every issue acted on or individually examined

| Issue | Cat | Repository evidence | Action taken |
|---|---|---|---|
| **WAL-204** Pattern-driven scale falsification | 2 | `docs/research/WAL-204-P0-PATTERN-ROUTER-RESULT.md` — title line "**RESULT = FAIL**"; 0 device-valid new lessons against a ≥50 bar; `docs/founder-orders/27-founder-decision-wal-204-fail-accepted.md` | **Ideas → Done.** Summary prefixed `[FALSIFIED · FAIL ACCEPTED]`; description rewritten to lead with the FAIL verdict, the bar, the three measured causes, and the fact that the WAL-206 re-run also failed at +3. **A Done status here records a completed experiment with a FAILED result — never a success.** |
| **WAL-206** Layout-aware K–12 extraction | 3 | `docs/research/WAL-206-LAYOUT-EXTRACTION-RESULT.md`; code on `main`: `tool/corpus/layout_extract.py`, `layout_gold.py`, `layout_units.py`, `content_quality_gate.py`, `wal206_funnel.py`; PR #54 | **QA → Done.** Both verdicts kept separate and unmerged: the ordered re-run **FAILED** (+3 vs ≥50); the layout blocker is **SOLVED for the classes we can see** (reading order 0.99). Recorded that the original WAL-204 page is *fail-closed, not solved*. |
| **WAL-207** Learning Views research | 3 | `docs/research/learning-views/` (21 docs), PR #55 + reconciliation PR; `docs/founder-orders/29-founder-decision-post-wal-207-tc-v1.md` | **QA → Done.** Description now carries all eight of order 29's decisions, including the Short-Answer deferral and "no major Learning Views implementation yet", plus the 6 measurements still UNMEASURED. |
| **WAL-209** TC-v2 Science Slice | 1 | Code on `main` (`tc2_sdm.py`, `tc2_tsl.py`, `tc2_attach.py`); but `docs/research/architecture-review/JIRA-STATUS.md` says the author left it at Code Review, "not Done (Founder gate)" | **Left Done; comment added.** Four Founder gates are still open: **D-135…D-138 are PROPOSED, not ratified** (knowledge-base PR #1 unmerged), the 10 items in `DECISIONS-REQUESTED.md` are unanswered, and the order-29 §9 Architecture Review has not happened. |
| **WAL-210** B-lane gates before growth | 1 | `docs/research/CHECKPOINT-2026-09-05-DUAL-TRACK.md` — "Nothing merged; WAL-210 → Code Review"; `FALSE-TRUST-AUDIT-PROTOCOL.md` — "thresholds PROPOSED, nothing decided" | **Left Done; comment added.** Item 10b **did not meet its gate**: held-out QUESTION precision **0.938 vs 0.95 required**; ACTIVITY 0.333, "detectable, not usable". Its decision D5 (denominator 3,679) is superseded in measurement by round 6's 3,650 — any figure must name its denominator. |
| **WAL-192** Tin học MCQ chain | 8 | `SAM-EDUCATION-DATA-ARCHITECTURE-REVIEW.md` §"Case C": Epistemic **PROVEN narrowly** (2/9 HIGH_CONFIDENCE), Maturity **BACKEND_ONLY**, no Surface, validator unwired | **Description rewritten; status deliberately unchanged.** Records both FALSIFIED hypotheses (`A/B/C/D shape → gradable`; `activity exists → valid evidence`) and that the gate decision Founder order 22 §24 asked for **has never been recorded anywhere**. That decision is product direction, so it is left to the Founder. |
| **WAL-203** Activity Pattern Registry | 8 | Founder order 27 §8: "Do not blindly trust the previous 27-pattern counts after changing extraction" | **Description rewritten**, summary prefixed `[REGISTRY · COUNTS STALE]`. Extraction has changed twice since these counts (WAL-206, then the SDM architecture). Records the known-wrong SELECT_MCQ count (397 → 287 after the bare-"chọn" false positive was fixed). |
| **WAL-205** Activity Pattern Expansion | 8, 7 | Founder orders 27 (preserve, do not implement) and 29 §3 (Short-Answer Surface **DEFERRED**) | **Description rewritten**, summary prefixed `[BACKLOG · BLOCKED]`. Records that WAL-206's 96-content-valid/+76 EXPLAIN_SHORT variant is **evidence, not a PASS**, and that the gating measurement is now WAL-215. Linked: WAL-215 blocks WAL-205. |
| **WAL-202** KST/Learning Frontier | 7 | Blocked on WAL-199, which is in Ideas with no repository evidence of having run | **Left unchanged; comment added** noting the block is real and that the measured bottleneck has moved. |
| **WAL-56** E12 Teaching Philosophy | 2 | 3/3 children Done; the Character + Pedagogical Constitutions exist as documents | **In Progress → Done.** A finite doctrine deliverable that exists. |
| **WAL-89** E16 Authoritative AI Curriculum | 2 | 4/4 children Done; QĐ 2422 extraction, source registry, Knowledge Pack POC all delivered | **In Progress → Done.** Finite scope, tied to two specific state documents. |
| **WAL-7, WAL-94, WAL-75, WAL-195** epics | 4 | All four sat in **Ideas** — a "To Do" category — while 4/4, 11/11, 11/12 and 3/4 of their children were Done | **Ideas → In Progress.** "Not started" was factually wrong for all four. None promoted to Done: each area is genuinely incomplete. |
| **WAL-176** Golden Student Journey | 4 | All 3 children Done — but round 7 §8: "**What can a CHILD use now that they could not before this round? — NOTHING**" | **Deliberately left In Progress; comment added.** Closing it would read as a claim that the journey works on trusted content. Nothing supports that. |

---

## Issues created, and why each one exists

Twelve, under two epics. The order was explicit that forty would be wrong, and that issues are
created only where real untracked work exists.

### E24 · Recognition + Role Disambiguation — **WAL-211** (In Progress)

The measured next bottleneck, accepted by the Founder in order 43: *"CALIBRATION IS FINISHED. THE
NEXT BOTTLENECK IS RECOGNITION + ROLE DISAMBIGUATION."* Direction:
`docs/research/NEXT-RESEARCH-DIRECTION.md`. It was tracked nowhere. Success is teaching-critical
error bounded **below 0.0035 on the frozen blind populations — or a measured statement that it
cannot be**. The epic explicitly forbids calibration work, threshold activation, coverage-as-proxy,
a Round 8, and device work while the Founder is using the phone.

| Key | Status | Why it exists |
|---|---|---|
| **WAL-213** Supersession contract | **Ready** | Not research — a named prerequisite. Round 7 measured that **a recovered digit does not become a repaired block** (`10 → 10, Δ 0`); the recogniser *adds* an observation where the destroyed one must be superseded. Everything else is measured wrong until this exists. |
| **WAL-214** DIGIT LOSS vs SEGMENTATION | **Ready** | Round 5's single "274" number is **two** failures: 312/548 DIGIT LOSS and 196/548 SEGMENTATION. One needs a recogniser, the other a splitter. Reporting them together hid a third of the population. Measured on the existing frozen `BLIND-CORE`/`BLIND-TEACHING`. |
| **WAL-215** Question vs non-question | **Ready** | Six of twelve teaching-critical errors. The lexical checks in `content_quality_gate.py` are an inventory, **not a baseline**, until measured. Records what already failed: the icon/colour signal (0.938 vs 0.95), the 0.70 confidence floor (made it worse and removed all prose), and that role error moved the wrong way while trust improved. **Blocks WAL-205.** |
| **WAL-216** Option letters after `agreement()` | Ideas | The one part that identifies the answer is the part no agreement measurement covers — a structural blind spot, not a tuning gap. |
| **WAL-217** Character corruption by repertoire | Ideas | `Ω → S2`: **0 of 22 recovered at every scale**, while in-repertoire glyphs recover 17/17. Averaging the two would hide the second population entirely. |

### E25 · Rounds 5–7 execution record — **WAL-212** (In Progress)

A backfilled record so a board reader is not misled about what happened. It does not restate the
repository; it points at it.

| Key | Status | Why |
|---|---|---|
| **WAL-219** Round 5 | **QA** | 8 PASS · 1 PARTIAL · 1 FAIL, full verdict table transcribed. **QA, not Done: round 5 has no Founder acceptance and merging its code did not create one.** A Founder gate is outstanding. |
| **WAL-220** Round 6 | Done | 4 PASS · 1 TRUTHFUL ZERO. Accepted by Founder order 41. Gate D remains a truthful zero, blocked on a Founder decision, not on engineering. |
| **WAL-221** Round 7 | Done | Accepted by Founder order 43. Records BOUND-4's consequence — 45 % of lessons carrying a teaching-critical error, "not sayable to a parent" — and §8's "NOTHING". |
| **WAL-222** Merge-debt reconciliation | Done | 306 commits, 20 PRs → 0, 4 stacked layers → 0. **A governance and integration action, not product delivery. No APK changed.** |

### Standalone

| Key | Status | Why |
|---|---|---|
| **WAL-218** CI GREEN != GOLDEN CHAIN VERIFIED | **Ready** | Real, untracked, and actively dangerous. **9 tests skip on CI while the suite prints "All tests passed"** (1106/16 local with the fixture, 1097/25 on CI). Among the skipped: *a validated repair stays withheld*, *no repaired text reaches a child*. Generalises to the standing principle **ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION** — `0/0 present · PASS`. D4 is not relaxed to fix it; the reporting changes, not the fixture. |

---

## Product truth, verified intact after the pass

Every one of these survives in status and in wording, and several are now stated on the board for
the first time:

- **`trusted = 0` · `eligible for teaching = 0`** — stated on WAL-211, WAL-212, WAL-204, WAL-206, WAL-209.
- **R-1 = HARDWARE UNVERIFIED** — no device walk; the Nokia was in personal use (WAL-221, WAL-222).
- **SGK crops = LICENSING-DISTRIBUTION BLOCKED / D4** (WAL-221, WAL-222).
- **Round 5 = 8 PASS · 1 PARTIAL · 1 FAIL with NO Founder acceptance** — WAL-219 is in QA precisely so this cannot be read as accepted.
- **The rounds 4–7 merge was governance, not delivery. No APK changed** (WAL-222).
- **CI GREEN != GOLDEN CHAIN VERIFIED** (WAL-218, WAL-222).
- **Nothing was promoted from PARTIAL to DONE**, and no research result became a product result. WAL-204 closed as FALSIFIED; WAL-206 closed with its FAIL intact beside its success; round 6's PARTIAL/DEFERRED/NOT STARTED and round 7's S5 PARTIAL are transcribed verbatim.

---

## Deliberately left alone, and why

Left unreconciled on purpose is a result, not an omission — a wrong Jira status is worse than an
unreconciled one.

- **The other 15 epics that sit In Progress since 2026-09-01.** I checked all 17 against their
  children rather than assuming staleness. Most are **not** stale in the sense of "finished": their
  titles name product capabilities that are demonstrably incomplete. WAL-2 Educational Knowledge
  Architecture — its source architecture is the unratified D-135…D-138. WAL-3 Student Knowledge
  Model — misconception, forgetting and transfer are all MISSING in code
  (`docs/research/SAM-LEARNING-CURRENT-TRUTH.md`). WAL-4 Adaptive Learning Engine — adaptive
  difficulty MISSING. WAL-9 Research & Validation — research plainly continues. **In Progress is the
  correct status for these**, and closing them to tidy the board would have converted an
  out-of-date tracker into a false one.
- **WAL-176 Golden Student Journey** — all children Done, product outcome not reached. Genuinely
  ambiguous; commented and left.
- **WAL-192** — the POC ran; the Founder gate decision it needs is product direction, not
  housekeeping.
- **WAL-30 Generative Tutor (In Progress)** — its gate (WAL-101 eval harness) is Done, but every
  recent Founder decision forbids LLM realisation for now. Whether "In Progress" or "Blocked" is
  right depends on a Founder intent I cannot read from the repository. Left.
- **WAL-197 – WAL-201 (Ready)** — the ARCH census/audit tickets. No repository evidence that any of
  them ran; they read as still-valid TODO. Left in Ready.
- **The P2 deferred blocks (WAL-154–162, WAL-121–124, WAL-146)** — correctly parked, correctly
  labelled `deferred-ready` / `research-later`. Untouched.
- **Confluence was not modified.** The round-5 and round-6 archives identify four pages as
  *actively wrong* — `19 — Coverage Dashboard` above all, publishing coverage on a denominator R13
  invalidated. Fixing or banner-ing them is a live risk, but the archives raised it as a **Founder
  decision with three options**, and order 45 scoped this task to Jira. Flagged, not touched.

---

## TOP 5 NEXT ISSUES — by the order's priority ladder

| Rank | Issue | Ladder rung | Why it is here |
|---|---|---|---|
| **1** | **WAL-213** Supersession contract | P0 recognition + role | A named prerequisite, not research. While a recovered observation sits *beside* the destroyed one instead of replacing it, a validator is judging two overlapping expressions — so every measurement in WAL-214 and WAL-215 is unsound before it starts. Cheapest thing on the board that unblocks the most. |
| **2** | **WAL-215** Question vs non-question | P0 recognition + role | Six of twelve teaching-critical errors, and the measurement that gates the Short-Answer Surface (WAL-205) under order 29 §3. The failure it addresses — a child asked to answer a heading — is the one that most directly harms a learner. |
| **3** | **WAL-214** DIGIT LOSS vs SEGMENTATION | P0 recognition + role | The other six. The split is already measured; what is missing is per-mechanism recall on the frozen blind populations **with false recognition reported beside it**. |
| **4** | **WAL-196** Founder Architecture Review + ratify D-135…D-138 | P0 blocker to trusted content reaching a learner | This is the gate that keeps `trusted = 0` structurally: SDM-as-source, block-level trust, image-first, trusted-subset are all still **PROPOSED**. **Founder-only** — an agent cannot clear it, but nothing downstream is architecturally settled until it is. |
| **5** | **WAL-218** CI GREEN != GOLDEN CHAIN VERIFIED | P1 verification gap risking false-green | Nine skipped tests include *no repaired text reaches a child*. Every future recognition result will be validated by a suite that can currently report success while its highest-value guards do not run. |

**Chosen to run next: WAL-213.** Not because it is the largest, but because it is the only one of
the five whose absence silently corrupts the others. WAL-214 and WAL-215 both produce numbers about
blocks; until a recovered observation can supersede a destroyed one, those numbers describe a block
that holds two contradictory texts at once. Round 7 already paid for this once — `10 → 10, Δ 0` —
and the direction document lists it under "prerequisites that are not research" for exactly that
reason.

**Not chosen, deliberately:** no Round 8 is opened. A round is an execution container; the
bottleneck is the goal. No calibration work is created — that line is closed. No threshold is
activated and no coverage target is set.
