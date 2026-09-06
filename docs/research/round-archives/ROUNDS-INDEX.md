> **CANONICALISED COPY — committed 2026-09-06 under Founder task order 43.**
>
> This file previously existed **only** on the Founder's Desktop, beside the review ZIPs it
> indexes. It carries the per-round VERDICT · NORTH STAR · KEY RESULT · PRODUCT DELIVERY · MERGE
> STATUS · NEXT BOTTLENECK for rounds 3–7 — a project record that had no home in the repository.
> `tool/reporting/README.md` step 4 still points at the Desktop path; the repository copy is now
> the record and the Desktop copy is a review convenience.
>
> **Semantics note, added not applied:** the line below reading «Per-round ZIPs are canonical» was
> written before the governance clarified on 2026-09-06. It is **superseded** by
> [`docs/governance/REPOSITORY-SOURCE-OF-RECORD.md`](../../governance/REPOSITORY-SOURCE-OF-RECORD.md):
> **REPO = CANONICAL RECORD · DESKTOP / ZIP = REVIEW SNAPSHOT ONLY.** The original wording is left
> intact below — no history is rewritten and no hash is deleted.

---

# HỌC CÙNG SAM — ROUNDS INDEX

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** Every per-round archive listed here contains
> verbatim SGK text and/or SGK page crops — internal research material under Founder rule **D4**.
> Round 7's 22 page crops are additionally **LICENSING-DISTRIBUTION BLOCKED**.

**Per-round ZIPs are canonical. There is no giant master ZIP and none will be made** — a single
combined archive would have to be rebuilt every round, and would let a later round silently
overwrite an earlier round's evidence.

Last updated: **2026-09-06** (round 7 added; **this file was rebuilt after the Desktop loss — see
the banner below**).

---

## ⚠ 2026-09-06 — THE EARLIER ARCHIVES WERE LOST FROM THE DESKTOP, AND TWO WERE REBUILT

**Discovered while building the round-7 archive.** Every file previously on the Desktop except the
round-7 ZIP was gone — **not in the Trash, and not found anywhere under the home directory.** The
archive builder did not delete them and cannot say what did. `~/Desktop/wal-evidence/` was
untouched.

| File | Size | Recorded SHA-256 | Now |
|---|---|---|---|
| `HOC-CUNG-SAM-ROUND-05-2026-09-06.zip` | 11,607,777 B | `30f2912cd165c5b9bf67ea32ab427c92a97282714356effe657e748eb8a77a4c` | **REBUILT** (new hash below) |
| `HOC-CUNG-SAM-ROUND-06-2026-09-06-v2.zip` | 2,160,729 B | `7d0bea5d28058d4161bda37653f0fa874c8953ae0f8173b9898de6b05f1b51e2` | **REBUILT** (new hash below) |
| `HOC-CUNG-SAM-ROUND-06-2026-09-06.zip` (v1, superseded) | 2,159,003 B | `a2e7495ca5467049d9d9efebfeb32cd031bafbf7f256142647e60696e07bedf5` | **NOT rebuilt** — it was superseded by v2 and its only value was as a record of a corrected error, which v2 already documents |
| `HOC-CUNG-SAM-ROUND4-REPORT-20260905-2227.zip` | 9,708,496 B | `bf0d27a929f6c7e377ea4cb0b5396f3760360ce1488217282ae61dd2cc4ccb22` | **NOT rebuilt — CANNOT BE.** A pre-format report ZIP; the archive builder never held its inputs |
| `HOC-CUNG-SAM-ROUND4-REPORT-LATEST.zip` | 9,708,496 B | byte-identical copy of the above | **NOT rebuilt — CANNOT BE** |
| `HOC-CUNG-SAM-ROUNDS-INDEX.md` | 11,135 B | — | **this file, rebuilt** |

**Why two were rebuilt immediately rather than reported and left:** their build inputs live in a
**session-scoped scratchpad that is cleaned when the session rolls.** Waiting risked losing the
ability to rebuild at all. **Regenerating is reversible; not regenerating might not have been.**

**A rebuilt archive is a new artefact carrying old information.** Its SHA-256 differs from the
original **and must** — the manifest records build time and commit, so a rebuild is never
byte-identical. **Each rebuilt ZIP carries `manifests/REGENERATION-NOTE.md` stating the original's
name, size and hash**, so the mismatch can never be mistaken for tampering. *If the Founder would
rather hold nothing than a re-derived copy, delete them.*

**Round 4's report ZIP is genuinely unrecoverable from this workspace.** Its source of record
remains `docs/research/ROUND4-CONSOLIDATED-REPORT-2026-09-06.md` in git, which is also copied inside
the round-5 archive under `reports/context-previous-rounds/`.

---

## Rounds

| ROUND | DATE | VERDICT | NORTH STAR | KEY RESULT | PRODUCT DELIVERY | ZIP NAME | MERGE STATUS | NEXT BOTTLENECK |
|---|---|---|---|---|---|---|---|---|
| **7** | **2026-09-06** | **THE GATE IS BUILT, AND THE ANSWER IS THAT CALIBRATION WAS NEVER THE BLOCKER.** Gates fixed before the round: **A METRIC TRUTH PASS · B TRUST CALIBRATION PASS · C BLIND VALIDATION PASS · D TRUST DELIVERY — PREPARED, UNACTIVATED** (by design; graded neither PASS nor FAIL) **· E NO REGRESSION PASS** — 4 PASS + 1 prepared; graded independently, agreeing on all five | **TRUSTED CONTENT REACHES THE LEARNER WITHOUT LOWERING THE EVIDENCE BAR** → **not reached — and the round proved why, which is the result** | **All 12 teaching-critical errors reduce to two mechanisms — digit corruption (6) and a non-question served as a question (6) — and neither is visible to any signal a gate can read.** **3 of 6 digit corruptions survive character-exact agreement between two independent OCR stacks.** No signal combination bounds teaching-critical error below **≈0.021**; a 90 %-clean promise needs **0.0035** — a factor of six; at 30 blocks/lesson, **≈48 % of lessons carry one**. The freeze chain is provable: **3 entries, no approval, no admitted**, and an `admitted` write without approval is **refused with a `PermissionError`**. **A servable type is recommended for 0 of 118 blocks**; the real lever is the sibling rule **31 mutilated structures → 0** at 72 blocks | **NOTHING.** Nothing was activated; `trusted` still 0; not one block changed on any screen. The 17 gaps now carry page crops **[HARDWARE UNVERIFIED — no device walk, no frames]**; the 22 crops are **[LICENSING-DISTRIBUTION BLOCKED — verbatim SGK, D4]**. **PARENT: nothing new. SAM: nothing new.** | `HOC-CUNG-SAM-ROUND-07-2026-09-06.zip` — **73 files · 6,248,822 bytes (6.0 MB)** · sha256 `1a8db62260807943542d62a0974a1607b4d16a5da2efe3618f436141af33d595` · built from `74d9db6`. **Original, not rebuilt.** | **NOTHING MERGED. NO THRESHOLD ACTIVATED.** #94–#97 open and CI-green; **#73 through #93 all still open — 16 PRs across four rounds.** Merge debt re-verified: **four layers, 259 commits ahead of `main`** (the report's 254 was measured four commits earlier). Recommendation unchanged: **merge #79 · close #73 as subsumed · hold the rest** | **RECOGNITION AND ROLE DISAMBIGUATION — not calibration.** Measured, not assumed. The gate is finished and waiting on evidence it cannot currently get |
| **6** | **2026-09-06** | **DELIVERED, HONESTLY — AND THE CHILD PAID FOR IT.** **A ACCOUNTING PASS · B RECOGNITION PASS · C REPAIR PASS · D TEACHING — TRUTHFUL ZERO · E DEVICE PASS** (4 PASS + 1 truthful zero) | **MAKE VERIFIED ACCURACY REACH THE LEARNER** → **reached — and the first thing it did was take something away** | **Silent loss 138 → 0** across 29 ledgers / 1,878 regions with **the served set byte-identical** — root cause **rule order**, swallowing **17 of 18** Docling FORMULA regions. Recognition read a defect round 5 called unreachable; **Bài 61 17/47 recovered, 17/17 correct, 0 of 38 controls disagreeing**. **9 validated repairs, 6 crossed into the app, `trusted: 0`.** Canonical identity: **3,679 rows / 3,240 keys / 3,650 canonical — and 3,240 deletes 410 real lessons** | **A real History lesson, minus its timeline.** LS&ĐL 5 Bài 8: **23 `[MẪU]` blocks → 34 real SGK blocks** + 17 reasoned gaps — but **7 timeline events → 0** and the 7-step SAM script gone, because the block carrying them is honestly withheld. **41 fabricated Toán expressions stopped shipping (g4 26 · g5 15; activities 248 → 207) ⇒ the app offers 0 Toán exercises** — a truthful zero. Workspace Option B: pinned chrome **411 → 281 dp, equal in all three views**; labels 7 → 4. **PARENT: nothing new. SAM: nothing new.** | **`HOC-CUNG-SAM-ROUND-06-2026-09-06-v2.zip` — REBUILT 2026-09-06: 83 files · 2,162,078 bytes · sha256 `5894c19cb88d9cc1449fb0e35e2c2f58574e05d30c9b537a4bae6dd62875b79d`.** Original v2: 82 files · 2,160,729 B · `7d0bea5d…`. Carries `manifests/REGENERATION-NOTE.md`. v1 (`a2e7495c…`) mis-reported the pack rebuild as 217→207 / 10→0, corrected in v2 to **248 → 207 / 41 → 0**; **not rebuilt** | **NOTHING MERGED.** #89–#93 open, all CI green | **THE TRUST DECISION** — *superseded by round 7, which measured that calibration was never the blocker* |
| **5** | **2026-09-06** | **PARTIAL — CAPABILITY PROVEN, NOTHING DELIVERED TO A CHILD.** Acceptance **8 PASS · 1 PARTIAL · 1 FAIL** on the ten criteria — reconstructed at the time, and **since confirmed exactly**: round 6 committed the Founder's §16 as `ROUND5-ACCEPTANCE-CRITERIA.md` and the settled tally is the same 8 · 1 · 1 | **DATA ACCURACY: `REPAIR → VALIDATE → RESTORE`** — coverage must recover **without loosening a guard** → **PARTIAL** | **Validated repair works and guard relaxation does not**: A2 restored **10/10** correct (holdout **8/8**) behind deterministic validators, while relaxing a guard restored **1 of 19** at precision **0/1 = 0.000**. Plus **R13**: blocks vanish with no reason code — corrected served share **0.632→0.589** (eval), **0.613→0.523** (holdout), **0.211→0.078** on Toán 4 t2 Bài 61 | **Presentation only, on the test device.** Trực quan reached the concept board (70–80 %→**85–90 %**): real mindmap + process flow. Workspace density 820→**712** px (peek) / **634** px (collapsed); 7→**4** view labels; **5 device-found defects fixed and re-walked**. **Zero accuracy corrections reached any build** | **`HOC-CUNG-SAM-ROUND-05-2026-09-06.zip` — REBUILT 2026-09-06: 118 files · 11,609,135 bytes · sha256 `90b5acb8068b45d657418ad56a60d624e841c8f842e7d59ba0be767acc6ca979`.** Original: 117 files · 11,607,777 B · `30f2912c…`. Carries `manifests/REGENERATION-NOTE.md` | **NOTHING MERGED.** #79 base + #80–#88, all CI green | **RECOGNITION, not reasoning** — **274 of 336** unrepairable fractions (82 %) failed because *the OCR never read the digit* |
| **4** | 2026-09-06 *(report)* / lanes 2026-09-05 | **ACCEPTED** by the Founder — recorded in `ROUND5-PLAN.md`: «Base: `integration/round4-2026-09-05` (round 4, **Founder-accepted**, unmerged)» | PROVE + EXPERIENCE + DISCOVER + LEGACY REPROCESS | False trust on the audited legacy batch **OLD 0.727 → tc2-p1 0.365 → tc2-p2 0.297**. The round's central trade: **85 more blocks withheld to deliver 16 fewer wrong ones** (gold coverage 0.683→0.551). A correctness review found **14 pipeline defects**, one silently truncating an entire book. **A26 falsified twice: two OCR stacks agreeing ≠ verbatim** | Experience Fidelity **70–80 %→80–85 %**; reading room **57 %→73 %** of the screen; pedagogy **5/17→7/17** on device. Source Trust **0/97** | **LOST 2026-09-06 and NOT RECOVERABLE** — `HOC-CUNG-SAM-ROUND4-REPORT-20260905-2227.zip`, 58 files · 9,708,496 B · sha256 `bf0d27a929f6…`. A **pre-format report ZIP**; the archive builder never held its inputs. **Source of record: `docs/research/ROUND4-CONSOLIDATED-REPORT-2026-09-06.md` in git, also inside the round-5 archive** | **NOT MERGED to `main`.** PR **#73** open; its five lane PRs merged into the round-4 integration branch | **Two:** (a) **no gate to cross** — `THRESHOLDS.json` does not exist; (b) **the fidelity floor needs a third signal** |
| **3** | 2026-09-05 | **ACCEPTED and MERGED** — the Founder authorised the merge to `main` *(PR #68 merged 2026-09-05T09:27:39Z)* | PROVE + EXPERIENCE + DISCOVER | **The false-trust audit that reframed the project.** 484/484 rows annotated: display fidelity **0.698**, teaching-critical **0.505**, **false trust 0.710**; Toán worst at **0.878**. **The shipped Scale content (113 lessons) is not trustworthy for teaching — 1 in 3 served blocks has a teaching-critical error.** Against that, the golden lesson's TSL stratum measured **0/60** | The golden-slice experience shipped to `main`: mode picker with per-view counts, Smart Book navigation, typed Visual family, a visible tutor loop («Runtime kiểm được 5/17 bước»), trust sheet in a child's words. **33 frames on the Nokia, 0 downgraded** | **NO ARCHIVE** — the per-round format did not exist yet. Source of record: `docs/research/ROUND3-CONSOLIDATED-REPORT-2026-09-05.md`, included in the round-5 archive | **MERGED to `main`** (PR #68, plus #60–#67) | The shipped Scale content is not trustworthy → **fix the pipeline's failure classes before scaling** |
| 1–2 | — | — | — | — | — | — | — | — |

**Rounds 1–2 are deliberately blank.** No consolidated report for them exists in the repository, and
the archive builder does not invent rows. **Status: NOT CAPTURED.**

---

## How to use an archive

Open the ZIP and read `ROUND-0N/00-START-HERE.md` first — it is written to be understood in 2–5
minutes. `15-FILE-MANIFEST.md` carries a SHA-256 for every file, so any file can be checked
individually years later. **If `manifests/REGENERATION-NOTE.md` is present, the archive is a rebuild
— read it before citing the ZIP's own hash.**

## How the next round's archive gets made

```
python3 tool/reporting/build_round_archive.py \
    --spec <round-content-dir>/archive-spec.json \
    --repo <repo root> \
    --out ~/Desktop
```

The tool refuses to overwrite an existing archive (it writes `-v2`, `-v3` …), refuses to build if
**any file** is missing or zero-byte, generates the manifest from the staged bytes, and then
re-verifies the finished ZIP against it. See `tool/reporting/README.md`.

**When a published archive turns out to be wrong, regenerate as `-vN` and keep the earlier one.**
Round 6 did this once: v1 carried a counting error, v2 carries the correction *and the record of
what was corrected*. **A superseded archive is still evidence — of what was believed at the time.**

**After each build, add one row above** — ROUND · DATE · VERDICT · NORTH STAR · KEY RESULT ·
PRODUCT DELIVERY · ZIP NAME (with file count, size, SHA-256) · MERGE STATUS · NEXT BOTTLENECK.

---

## Standing facts across all rounds

- **`trusted` = 0 and `eligible for teaching` = 0 in every round so far.** Round 7 measured *why*:
  no threshold can bound teaching-critical error below ≈0.021 against a requirement of 0.0035,
  because the two mechanisms that cause it are invisible to every signal a gate can read.
  **Calibration is finished and it was never the blocker.**
- **Source Trust has been 0 / 97 since round 3**, and `PEDAGOGY REALITY` 7/17 since round 4.
- **Merge debt:** rounds 4, 5, 6 and 7 are all unmerged — **16 open PRs, four stacked integration
  layers, 259 commits ahead of `main`.** Round 7 did compose a composition, as round 6 warned.
- **One product gate is PRODUCT-INTEGRATED (Device UX)** — and round 7 could not verify even that
  one on hardware.
- **Never turn PARTIAL into DONE.** Allowed statuses: DONE · PARTIAL · FAILED · FALSIFIED · BLOCKED
  · DEFERRED · NOT STARTED.
- **Round 7 added a three-way status legend** for claims that are true in different ways:
  **TECHNICALLY VALIDATED** · **HARDWARE UNVERIFIED** · **LICENSING-DISTRIBUTION BLOCKED**. A claim
  can be PROVEN in an artefact and still be HARDWARE UNVERIFIED — round 7's R-1 is exactly that.
- **Rounds 5, 6 and 7 each closed with no Jira or Confluence artefact of any kind.**
- **Desktop archives are not backed up.** The 2026-09-06 loss above is the evidence; two of five
  files were recoverable only because a volatile scratchpad happened to still hold their inputs.
  **This is worth a Founder decision.**
