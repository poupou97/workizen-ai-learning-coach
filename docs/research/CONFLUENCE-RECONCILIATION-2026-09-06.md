# CONFLUENCE RECONCILIATION — space WAL against repository truth · 2026-09-06

Executed under `docs/founder-orders/46-founder-addendum-confluence-reconciliation-authorized.md`.
Site `workizen.atlassian.net` · space **WAL** (`spaceId 18612229`). Repository truth taken from
`main` at `1ca43b4` (rounds 4–7 merged that morning at `14df3ec`, 306 commits; Jira reconciled the
same day at `71d95df`).

**The rule this pass obeyed.** The repository is the canonical source of record; Confluence is a
presentation / knowledge layer and may never override it. **No page was allowed to keep a number
that the repository contradicts, and no page was allowed to acquire a number that the repository
does not carry.** Every figure written to a page in this pass was either re-generated live on
2026-09-06 or re-derived independently here — none was copied from a page, a report summary, or a
prior Confluence version.

---

## The gap that made this necessary

Confluence WAL had not been touched since **2026-09-02**. Since then the project ran **rounds 5, 6
and 7**, merged **306 commits**, and reconciled Jira. The round-5, round-6 and round-7 archives had
each recorded the same finding and each declined to act on it, because the archive task's scope was
the archive:

> `docs/research/round-archives/round07/14-JIRA-CONFLUENCE-STATUS.md` — "**The pages that are now
> actively wrong** … not merely stale — **wrong in a way a reader cannot detect from the page**."

Four pages were named: `19 — Coverage Dashboard`, `15 — Current Status`,
`03 — Educational Knowledge Model`, `11 — UI/UX & Design System`. The archive's recommendation,
unchanged across three archives, was **option 2 with the two banners from option 3**. Founder
order 46 authorised the whole reconciliation instead.

---

## PAGES AUDITED — 23 of 23

Every page in the space. **20 content pages (`00` … `19`)** · **1 space homepage** ·
**2 stock Confluence templates**.

| | count |
|---|---|
| **Pages audited** | **23** |
| **Pages updated** | **21** |
| Of those, updated because content was **actively wrong** | **7** |
| Of those, updated with a **status banner + verified additions**, body preserved | **13** |
| Of those, **space homepage** placeholder replaced, macros preserved | **1** |
| **Pages carrying an explicit HISTORICAL / SUPERSEDED marker after this pass** | **6** — `00` · `07` · `11` · `15` · `18` · `19` |
| **Pages left untouched** | **2** (stock templates) |
| **Remaining conflicts** | **0 unresolved** — 4 open questions recorded, all Founder-only |

Of the six, only **`18`** is historical as a whole page. On `00`, `07`, `11`, `15` and `19` the
marker scopes a *named block* — a superseded status line, a dated measurement set, an audit
verdict, a snapshot, a corrected figure — while the rest of the page is CURRENT.

---

## The seven pages whose content was wrong

A page is listed here only when it asserted something the repository contradicts — not merely
because it was old.

### `19 — Coverage Dashboard` — the flagged page, and the worst of them

The single most quotable artefact in the space, and its headline invites the one question the
project cannot answer: *«SAM thực sự hiểu bao nhiêu % chương trình?»*

| What it said | What the repository says | Verified how |
|---|---|---|
| **Tầng 0 OCR = 8 books · 1,464 pages** | **531 books · 62,729 pages** | `poc-out/graph/ocr-body` counted directly on disk: **531 directories, 62,729 files**; and `SNAPSHOT-K12.json` `corpus.documents 531` / `corpus.pages 62729` |
| no denominator discipline for lesson counts | **3,679 · 3,650 · 3,381 · 3,240 are ONE leaf population under FOUR grouping keys** | re-derived here from the 12 `assets/pack/lesson-index-g*.json`, independently of `tool/metrics`: rows **3,679** · `(doc,no,pageStart,title)` **3,650** · with `pageStart` **3,381** · `(doc,no)` **3,240** · true-duplicate excess **29**. `3,679 − 29 = 3,650` exactly |
| «Tầng 3 — Validated 🟢 GREEN 30/30» as the final layer | SCALE GATE is an **extraction** gate, not a trust gate | `python3 tool/extract/coverage_report.py` re-run 2026-09-06: `scaleGate GREEN, checksPassed 30, checksFailed 0` — **still true, and re-labelled rather than removed** |
| **no mention of trust at all** | **`trusted = 0` · `eligible for teaching = 0`** | round 6 §1 Gate D; round 7 §2, §9 |

**The Tầng 0 figure is the instructive one.** «8 cuốn · 1.464 trang» was **true when written** —
04:34 on 2026-09-02 — and stopped being true **the same day**, when K-12 ingestion finished at
18:41. It then stood for four days, understating the corpus by roughly **43×**. It is recorded on
the page as a dated correction, not deleted.

**What the page now carries that it did not:** a **Tầng 4 — TRUST** with `trusted = 0`; the
four-grouping-key table with `3,679` marked **HISTORICAL BASELINE ONLY** and `3,240` marked **not a
lesson count** (it deletes 410 real lessons to key collision); the ruling that **«total activities»
is DEPRECATED** (248 SUPERSEDED · 217 and 161 DEPRECATED) replaced by `ACTIVITY_LEAF_COUNT` **207**
and `LEARNER_ACTIVITY_LEAF_COUNT` **171**, both re-derived here; **SCALE GATE GREEN ≠ TRUST GATE
GREEN**; **CI GREEN ≠ GOLDEN CHAIN VERIFIED** with the 1106/16 vs 1097/25 split; and **D4**.

**What was NOT done to it.** Its true-at-the-time semantic figures — 2,584 ContentUnits, 569
objectives, 29/54 rules, 29 methods, 1,109 Q-matrix exercises, 4 `BUILDS_ON` + 1 `REQUIRES`,
`llmInferred = 0` — were **re-generated and found unchanged**, so they were left standing. The
30/30 GREEN was **not** downgraded: it is true, and what was wrong was the inference a reader would
draw from it.

### `15 — Current Status`

Stopped at 2026-09-02 and predated rounds 3–7. Rewritten as a current status; the whole
2026-09-02 snapshot is **preserved verbatim inside an expand, labelled HISTORICAL**, including its
«323 test xanh» and its five open Founder questions.

Now states: the rounds 4–7 merge was **governance and integration, not delivery — no APK changed**;
the four round verdicts with **round 5 as `8 PASS · 1 PARTIAL · 1 FAIL` and no Founder acceptance**;
`trusted = 0`; **R-1 HARDWARE UNVERIFIED**; **SGK crops LICENSING-DISTRIBUTION BLOCKED under D4**;
and the CI skip split.

### `03 — Educational Knowledge Model`

Predated the source layer, the repair/disposition layer and the trust gate. Original doctrine kept
verbatim; **one correction** (it said provenance had *4* levels; the code has *5* —
`sourceDemonstrated` was added). Added: **D-135…D-138 as PROPOSED, not ratified**; the round-5
`0/1 = 0.000` vs `10/10` restore result; a `ValidatedRepair` crossing the pipeline **without
becoming trusted**; and WS-S's finding that a servable type is recommended for **zero of the 118**
blocks.

### `11 — UI/UX & Design System`

An audit record from 2026-09-02. **Its verdict `KEEP 10 · MODIFY 20 · REPLACE 6 · SPLIT 1 ·
MERGE 1` was a true finding at its time and was NOT edited** — it is marked HISTORICAL and the
re-audit that superseded it (`KEEP 9 · MODIFY 21 · …`) is named beside it. A CURRENT section was
added above it: Workspace **Option B** shipped, chrome **411 dp → 281 dp**, view labels **7 → 4**,
the **PRESERVE SOURCE VERBATIM** title rule with its named casualties, and **NOTHING NEW for a
child after round 7**.

### `00 — Start Here`

Its quick status read «UI: **chưa có màn hình nào**». False since roughly 2026-09-01: `main` carries
**20 feature areas · 66 Dart files under `lib/features/` · 30 screens**. Replaced with a verified
status table, plus the **REPOSITORY = CANONICAL SOURCE OF RECORD** rule and a reading order.

### `08 — Student Experience`

Read «**NOT STARTED** — `lib/features/*` rỗng». False, same evidence. Rewritten with the measured
product scores; the two goal loops kept verbatim.

### `09 — Parent Experience`

Read «Domain đã có · **UI chưa có**». False: `lib/features/parent/` holds `parent_tonight_screen`,
`parent_area`, `family_manager_screen`, with tests. Corrected — **and paired with the fact that
rounds 6 and 7 both delivered `PARENT: NOTHING NEW`**, and that BOUND-4's 45 % is *not sayable to a
parent*.

---

## The thirteen pages that were old but true — banner, not rewrite

Bodies preserved; each gained a dated status banner and, where the repository had something to add,
a short verified section. **No verdict, score or research finding on any of these was altered.**

| Page | Marker | What the repository check added |
|---|---|---|
| `01 — Product Vision` | CURRENT | nothing — doctrine intact, banner only |
| `02 — Product Architecture` | CURRENT + addition | the SDM → TSL → trust-gate chain that sits *before* the diagram's first box, and that it is **PROPOSED** |
| `04 — Student Knowledge Model` | CURRENT + addition | measured code state: forgetting · in-case difficulty · interleaving all **0 references in `lib/`**; misconception and transfer **now have code**, so the 2026-09-02 capability audit is itself partly stale |
| `05 — Adaptive Learning Engine` | CURRENT | seven `lib/core/adaptive/` files confirmed; no DKT; no difficulty axis |
| `06 — AI Tutor / TutorScope` | CURRENT | «Generative Tutor chưa bắt đầu» **machine-verified**: `pubspec.yaml` carries **no network or LLM dependency**; per-condition status of the WAL-30 gate |
| `07 — Camera Tutor` | HISTORICAL measurements + addition | its red cell stands (**no real phone photos**); adds the phone-sim proxy (**5/5 → 2/5 → 1/5 → 0/5**, and Vision confidence ≈ 1.00 even at L3, so **OCR confidence is unusable as a fail-closed gate**), plus rounds 6–7 recognition results |
| `10 — AI Lab` | CURRENT | «NOT STARTED» **re-verified**: 0 `aiLab` references in `lib/` |
| `12 — Research` | index superseded | 6 documents listed; `docs/research/` holds **288** `.md` files. Original table kept; entry points and seven new negative results added |
| `13 — ADR / Decisions` | CURRENT + completion | listed ADR-001…005; repo has **ADR-001…010**. Five added. Founder decisions **D1–D6** recorded; **D-135…D-138 recorded as PROPOSED** |
| `14 — Safety / Privacy` | CURRENT + update | **D4 quoted in full**; ADR-010 safety boundary **is now code**; WAL-44 gap narrowed but open |
| `16 — SAM Teaching Philosophy` | CURRENT | banner only; notes the charter is currently being enforced at its most expensive — silence at the source |
| `17 — AI Curriculum (QĐ 2422)` | CURRENT + one item closed | open item ① closed: ADR-008 is **ACCEPTED** with `lib/core/curriculum/ai_curriculum.dart` + test. ②③④ remain open |
| `18 — Learning Science Research` | **HISTORICAL** | preserved verbatim; its Jira statuses dated to 2026-09-02 and flagged as superseded by the 2026-09-06 reconciliation |

**Space homepage** — the stock «In a sentence or two, describe the purpose of this space»
placeholder was replaced with a real description and the source-of-record rule. **All four macros
(live search, label list, recent updates) were preserved byte-for-byte**, including their
`data-local-id` and `data-parameters`.

**Left untouched: 2.** `Template - How-to guide` and `Template - Troubleshooting article` are stock
Confluence templates, not project content.

---

## Numbers re-derived before they were written — and one that was not needed

The order warned that this project has been bitten by figures that were the right type and the
wrong quantity. Every number placed on a page was checked first.

| Figure | Method | Result |
|---|---|---|
| Tầng 0 OCR | `ls`/`find` over `poc-out/graph/ocr-body` | **531 books · 62,729 pages** — matches `SNAPSHOT-K12.json` |
| Tầng 1 structure | `tool/extract/coverage_report.py` re-run | **531 scanned · 7,199 lessons seen** |
| Four lesson denominators | independent walk of `pack.subjects[*][*].lessons[*]` written here, not `tool/metrics` | **3,679 · 3,650 · 3,381 · 3,240 · 29** — every figure identical to WS-M's |
| Activity leaf counts | same walk, per family | `ACTIVITY_LEAF_COUNT` **207** · `LEARNER_ACTIVITY_LEAF_COUNT` **171** · `sourceAssets` **36** · `toanExercises` **0** |
| Pack book rows | same walk | **238 rows = 238 distinct `sourceDocumentId`** — measured equal, not assumed |
| SCALE GATE | `coverage_report.py` runs `verify_corpus_gates.py` and records its exit code | **30/30 GREEN**, 2026-09-06 |
| Semantic layer | same run | 2,584 · 569 · 29/54 · 29 · 1,109 · 4+1 · 0 — **unchanged since 2026-09-04, so left standing** |
| `lib/` capability claims | direct counts on `main` | 20 feature areas · 66 files · 30 screens · 10 ADRs · 0 `aiLab` · 0 `difficulty` · 0 `forgetting` · 0 `interleav` · no LLM dependency in `pubspec.yaml` |

**Three figures were deliberately NOT reconciled into one another**, because they are different
populations and dividing them would manufacture a coverage claim: `7,199` (structure-scan lessons
with a number, 531 books, SGK + SGV) · `7,626` (`curriculum-structure.json` lesson records) ·
`3,679` (SGK lesson rows in the product packs). The page now says so explicitly.

---

## What was NOT done — the prohibitions, and where each one bit

- **No historical research truth was rewritten.** `11`'s 38-screen audit verdict, `18`'s five
  findings, `07`'s 2026-09-01 scan measurements and `19`'s 2026-09-02 Tầng 0 figure all stand as
  what was believed at the time, each with a banner and, where superseded, a named successor.
- **Nothing was promoted.** No PARTIAL, FAIL, FALSIFIED or UNVERIFIED became DONE or PASS. Round 5
  is stated on `15` as **8 PASS · 1 PARTIAL · 1 FAIL with no Founder acceptance**, and the sentence
  «merging its code did not create one» is on the page. Round 7's Gate D is stated as **PREPARED,
  UNACTIVATED**, WS-S's S5 as **PARTIAL**, R-1 as **HARDWARE UNVERIFIED**.
- **No Founder decision was changed.** D1–D6 and D-135…D-138 are transcribed, never edited;
  D-135…D-138 are labelled **PROPOSED**, and the pages say ratification is Founder-only.
- **The 30/30 GREEN was not deleted to be safe.** Deleting a true green would have been its own
  falsification. It was re-run, kept, and *re-scoped* — the page now says what it does and does not
  certify.
- **No page was mass-edited for tidiness.** Thirteen pages kept their bodies.

---

## A rendering defect found and fixed in passing

Four pages — `11`, `15`, `18`, `19` — had been created by pasting Markdown into a single ADF
paragraph. Their stored body was one `<p>` containing literal `#`, `**` and `|` characters, so
**they had never rendered as headings or tables for any reader**. Every table on the coverage
dashboard was showing as a run-on line of pipes. They are now real structured pages. **No wording
was changed by the conversion** beyond the edits recorded above.

---

## REMAINING CONFLICTS

**No page in space WAL now contradicts the repository.** Four questions remain open, and every one
of them is Founder-only — they are recorded on the pages as open, not resolved:

| # | Open question | Where it is stated | Why an agent may not close it |
|---|---|---|---|
| 1 | **Which grouping key is the lesson denominator?** `3,679` / `3,650` / `3,381` / `3,240` | `19`, `15` | A definition question about the product's own claim. `3,679` stays HISTORICAL BASELINE ONLY until it is answered; every coverage figure must name its key meanwhile |
| 2 | **Ratify D-135…D-138** (SDM-as-source · block-level trust · image-first · trusted subset) | `03`, `13`, `02` | Founder-only; knowledge-base PR #1 unmerged. **This is the gate that keeps `trusted = 0` structurally** (WAL-196) |
| 3 | **Activate a production trust threshold, and under which bound** | `19`, `15`, `14` | BOUND-4 implies 45 % of lessons carrying a teaching-critical error; BOUND-5 is per-lesson certification of a bounded slice and **is not a threshold and must never be reported as one** |
| 4 | **WAL-43 Legal Gate** and the D4 licensing position | `14`, `19` | Founder + lawyer |

**One self-inflicted risk is recorded rather than hidden.** This pass wrote «reconciled 2026-09-06»
banners onto 21 pages. Those banners are true today and will decay exactly as the 2026-09-02
figures did — the Tầng 0 number was accurate for **fourteen hours**. A banner is a claim with a
date on it, not a guarantee, and the honest reading of a CURRENT banner is *«checked then»*, never
*«true now»*.

---

## Method note — how a page's verdict was chosen

For each page, in order: read the page → identify every claim that could be checked against the
repository → check it → then classify.

```
claim contradicted by repo   → CORRECT IT, and record what it said and when it stopped being true
claim true at its time, now superseded → HISTORICAL banner + name the successor; do NOT edit
claim still true, page merely old      → banner, body untouched
claim not checkable from the repo      → leave it, say so
```

**A page that is merely old but still true got a banner, not a rewrite.** That rule decided
thirteen of the twenty content pages.
