# Round 5 · Lane D — pack rebuild, legacy batch 2, and the defects that survived a third build

**Status: measurement. Nothing merged, nothing deployed, nothing promoted to trusted.**
No threshold is set. `trusted` and `eligible for teaching` are **0** and the tool prints why.

Founder rules this report is written under: legacy content is **never** a trusted teaching source ·
**REPROCESSED ≠ TRUSTED** and **RESTORED ≠ TRUSTED** · nothing is deleted · no manual prettifying —
reprocess from the ORIGINAL SOURCE · no mass reprocess · what the pipeline cannot process is
**WITHHELD, never guessed** · every number carries its denominator (D5) · verbatim SGK stays internal (D4).

> ⚠️ **Operational state of this Mac:** the packs in the main checkout are still the OLD ones — they
> stamp `capped-toc-v1`, fail verify 12/12, and still carry all 41 INFERRED expressions. Lane D built
> and measured the corrected packs inside its own worktree and did not touch the main checkout. Until
> this PR is merged and the packs rebuilt there, **no APK built on this Mac carries the round-5
> corrections.** Details and the exact commands: [`ROUND5-LANE-D-EVIDENCE.md`](ROUND5-LANE-D-EVIDENCE.md).

Companions: [`ROUND5-LANE-D-EVIDENCE.md`](ROUND5-LANE-D-EVIDENCE.md) (where every number comes from),
[`LEGACY-REPROCESS-SCOREBOARD.md`](LEGACY-REPROCESS-SCOREBOARD.md) (standing counts),
[`PIPELINE-REQUESTS-FROM-LEGACY.md`](PIPELINE-REQUESTS-FROM-LEGACY.md) (what this asks the pipeline lanes for),
[`../DATA-ACCURACY-SCOREBOARD-LANE-D.md`](../DATA-ACCURACY-SCOREBOARD-LANE-D.md) (the five directions, BEFORE → AFTER),
[`ROUND4-BATCH-1-REPORT.md`](ROUND4-BATCH-1-REPORT.md) (what this round inherits).

---

## 0. The five directions, in one screen

The Founder judges this round on five directions **at once**. A batch that only lowers false trust
while withholding more is not a good result.

| direction | round 4 (batch 1, `tc2-p2`) | round 5 (batch 2, six new lessons) | reading |
|---|---|---|---|
| **FALSE TRUST ↓** | 0.297 [0.199, 0.418] | **0.318** [0.218, 0.438] vs OLD **0.619** | ✅ vs the product it replaces; **flat** vs round 4 on a harder batch |
| **TEACHING-CRITICAL ↓** | 0.176 [0.062, 0.410] | **0.100** [0.043, 0.214] vs OLD 0.476 | ✅ |
| **CORRECT SERVED ↑** | 221 blocks served, ≈ 155 correct | **239 served, ≈ 163 correct** (of 378 learning blocks) | ✅ in blocks; the share served is 63 % |
| **OVER-WITHHOLD ↓** | 12/30 = 0.400 | **19/30 = 0.633** [0.455, 0.781] | ❌ **worse** — the round's clearest failure |
| **RESTORE PRECISION ↑** | not measured | **3/6 = 0.500** [0.188, 0.812] | ⚠️ first measurement; half the restores are wrong |

Two of five moved the wrong way or barely moved. **This is not a good round on the Founder's own
criterion, and the reason is one mechanism**: the build refuses far more than it repairs, and when
it does hand something back, it is right half the time.

---

## 1. Pack rebuild (§13) — snapshot, rebuild, verify, delta, audit

### 1.1 Why a rebuild was owed

`tool/ui/pack_provenance.py` derives `attachmentRule` from `tool/ui/lesson_attach.RULE`, which round 4
moved to `capped-toc-v2`. Every pack on disk stamped `capped-toc-v1`. **`pack_provenance.py verify`
failed 12 of 12** — a manifest describing a rule the pack was not built with.

### 1.2 The snapshot, and how the OLD baseline stays reproducible

`tool/corpus/legacy/packs.py` enforces the order in code: `snapshot` refuses to overwrite; `rebuild`
refuses unless a snapshot describes the packs actually on disk (sha256-checked); `restore` puts them
back, checking every hash.

| snapshot | what it preserves | verify at snapshot |
|---|---|---|
| `poc-out/round5/legacy/packs-before-round5/` | the 12 packs exactly as they stood before this round | **0/12 — FAIL** (`capped-toc-v1` ≠ `capped-toc-v2`) |
| `poc-out/round5/legacy/packs-before-inferred-fix/` | the 12 packs after the provenance repair, before the §3 fail-closed change | 12/12 — PASS |

Each holds `packs/`, `SHA256SUMS`, `MANIFEST.json` (per-pack sha256, full `buildProvenance`, the
verify result at snapshot time), `BASELINE-METRICS.json` (per grade, per activity family, openable
lessons, catalogue lessons) and `PIPELINE-VERSION.json` (repo HEAD, builder commit, `lesson_attach`
commit + rule, provenance schema, interpreter, platform), plus a README with the exact commands.

**The OLD baseline is reproducible, and it was actually reproduced during this round** — twice by
`restore` (to re-observe the failure, and as the mutation check in §1.6; both passed every sha256),
and once by re-deriving the metrics straight from the snapshotted packs: `perGrade`, `totals` and
`grades` come back **identical to the stored `BASELINE-METRICS.json`**, field for field.

```bash
python3 tool/corpus/legacy/packs.py restore poc-out/round5/legacy/packs-before-round5
python3 tool/corpus/legacy/packs.py metrics --out /tmp/old-metrics.json   # == BASELINE-METRICS.json
python3 tool/ui/pack_provenance.py verify assets/pack/lesson-index-g*.json  # exits 1, as it did
```

### 1.3 Verify — PASS

All 12 rebuilt with default flags, `rc=0`, and `pack_provenance.py verify` returns **12/12 OK**,
exit 0. Pack versions `g<N>-20260905T1630Z-1a6ea706`, builder `build_lesson_index.py@1a6ea70`
(clean, not `-dirty`: the packs were rebuilt again after the builder was committed, so no pack
claims a version its code did not have).

### 1.4 The content delta of the provenance rebuild — **exactly zero**, and that is the finding

| | value |
|---|---|
| activities before / after | 248 / 248 |
| unchanged | **248 (100 %)** |
| content-changed · moved-lesson · appeared · disappeared | 0 · 0 · 0 · 0 |
| grades whose `contentHash` is identical | **12 / 12** |

Verified independently of the tool by stripping `buildProvenance` from both sides and comparing the
canonical JSON byte for byte: identical on all twelve, same length.

**This is surprising in the direction nobody looks for.** The old packs were built at `07a24504`,
where `lesson_attach.RULE` really was `capped-toc-v1`; since then the rule gained a systematic TOC
offset (61 changed lines) and the builder changed too — and **none of it moved a single served
activity.** The reason is in `lesson_attach` line 46: for families whose lesson key comes from an
upstream extractor, the TOC range is a cross-check that is *counted* (`range_mismatch`) and **never
a drop**. So `capped-toc-v2` can only change the diagnosis, not the content.

What it did change is worth having: on `05-sgk-tieng-viet-5-tap-hai` the offset is **−2**, and
**31 rows changed verdict** — 28 `range_mismatch` → `range_ok`, 3 the other way. Flagged rows on
grade 5 fell 48 → 23.

### 1.5 Blind audit of that delta

The content delta is empty, so there is no served block to audit. Refusing to look further because
of that would be the papering-over the order forbids, so the **diagnostic** delta was audited
instead: for each of the 31 reclassified rows, the top strip of the printed page was rendered and a
**different session** read the printed lesson badge without seeing the claimed lesson.

| | value |
|---|---|
| rows rendered and read blind | 31 (28 restored to `range_ok`, 3 newly flagged) |
| pages showing a lesson badge | 27 |
| **restore precision (flag level)** | **27 / 27 = 1.000** [0.875, 1.000] · worst case 27/28 = 0.964 |
| new-flag precision | **unmeasurable** (n = 0 judgeable) |

On every row where the page states its own lesson, the v2 offset agrees with the page. Four rows
print no badge at all — a poem-body page and three `ĐỌC MỞ RỘNG` section pages — and they are scored
`no-badge-unjudgeable` rather than as disagreements, because "no badge" does not mean "another
lesson". **All three newly-flagged rows are among those four**, so the new flags cannot be validated
by this method at all, and the report says so rather than quoting the 0.964 that a harsher rule
would have produced.

### 1.6 The second rebuild — INFERRED expressions fail closed (Founder §3)

Verified before acting: `tool/extract/rebuild_fractions.py:124` stamps every row `status: INFERRED`,
`method: geometric-fraction-rebuild-v1`; `poc-out/units/exercise-case-map.json` holds **41 rows, all
INFERRED**; `build_lesson_index.py` copied only `expr/skillCaseId/page/book`, so **all 41 reached the
shipped packs** carrying a `skillCaseId` and no provenance — arithmetic rebuilt from geometry,
indistinguishable from what is printed, on the path a child is taught from.

**Choice: fail closed.** The pack schema has no provenance field for an activity and the app cannot
show an INFERRED caveat, so a non-verbatim upstream record is not emitted at all. Nothing is deleted
upstream; every drop is logged with status, method, skillCaseId and page.

| grade | dropped | lessons that lose their exercise list **entirely** |
|---|---|---|
| g4 | 26 | Toán 4 tập hai Bài 60 (×14), 61 (×5), 63, 64, 66, 73 (×4) |
| g5 | 15 | Toán 5 tập một Bài 6 (×7), 29; Toán 5 tập hai Bài 69 (×6), 75 |
| **total** | **41 of 248 activities (16.5 %)** | **10 lessons — `toanExercises` is now empty in every pack** |

10 of 12 grades stay byte-identical. **This is a coverage loss that is a correctness gain**, and it
belongs in the OLD → NEW ledger as such: the product used to serve 41 expressions it had constructed,
one of which round 3 caught serving `2/5 + 1/4` for the printed `2/5 − 1/4`.

**A test was pinning the defect.** `lesson_index_test.dart` asserted
`expect(idx.exercisesForToan(6), isNotEmpty, reason: 'B6 có bài tập thật')`. Bài 6's seven "real
exercises" are seven INFERRED reconstructions. The assertion was replaced by the rule it should have
been: a pack-gated FILE THẬT test that fails when any pack carries a `toanExercises` entry whose
upstream record is INFERRED without `status` and `method`. **Mutation-checked**: restored the pre-fix
packs, the test reported all 41 leaks; rebuilt, it passes.

### 1.7 Defect 6 asked of the shipped packs — **it does not reach them**

The coordinator asked whether «imprint / back matter → lesson heading» lands in the rebuilt packs.
`regression.py pack-scan` answers deterministically, delegating the range half to the builder's own
`lesson_attach` rule rather than re-implementing it:

| | before the §3 fix | after |
|---|---|---|
| activities scanned | 248 | 207 |
| **imprint / back-matter activities** | **0** | **0** |
| activities past their book's last lesson start | 1 (Toán 5 Bài 29, p135, `range_mismatch`) | **0** |

**Defect 6 lives in the research pipeline (the TSL), not in the pack path.** The packs are built from
`poc-out/units` and the curriculum, and the imprint page never enters that route. The one past-last
activity was itself an INFERRED expression and left with the rest.

### 1.8 Tests

**948 Dart tests pass, 15 skipped** (`flutter test`), including the three pack-gated ones
(`default_build_guard_test`, `architecture_gate_test`, `lesson_index_test`). **289 Python tests pass**
(`python3 -m unittest discover -s tool/tests`), 60 of them new in this lane.

---

## 2. Batch 2 — the five failure classes, `ORIGINAL → OLD → NEW`

Six lessons, 34 pages, every step `rc=0`. Chosen by the classes the Founder named, not by convenience.
**History/Geography had never been measured on either side.**

| lesson | class | OLD served | NEW trusted / withheld |
|---|---|---|---|
| LS&ĐL 4 Bài 12 «Thăng Long – Hà Nội» | **History/Geography**, two-column, figure/caption | 2 | 24 / 22 |
| LS&ĐL 5 Bài 9 «Triều Lý…» | **History/Geography**, prose | 2 | 35 / 19 |
| Khoa học 4 Bài 6 «Gió, bão…» | **Science**, figure/caption | 9 | 33 / 22 |
| KHTN 9 Bài 5 «Khúc xạ ánh sáng» | **Science**, high-formula, two-column | 13 | 74 / 31 |
| Toán 4 tập một Bài 37 «Ôn tập chung» | **Math/high-formula**, last lesson of book | 29 | 31 / 27 |
| TV5 tập một Bài 5 «Tiếng hạt nảy mầm» | **Vietnamese text**, poem | 25 | 42 / 18 |
| **total** | | **80** | **239 / 139 (63 % served)** |

### 2.1 OLD vs NEW per failure class

Rate = WRONG / (OK + WRONG) among **served** rows — the share of what each side showed a child that
is wrong. Wilson 95 %. NA/UNSURE excluded and counted beside. The two sides are **different block
sets**; what is comparable is the share, read beside how much each side served.

| failure class | OLD (n = 43) | NEW (n = 67) | direction |
|---|---|---|---|
| display fidelity | 25/42 = **0.595** [0.445, 0.730] | 11/67 = **0.164** [0.094, 0.271] | better |
| teaching-critical | 10/21 = **0.476** [0.283, 0.676] | 5/50 = **0.100** [0.043, 0.214] | better |
| reading order | 10/22 = **0.455** [0.269, 0.653] | 0/30 = **0.000** [0.000, 0.114] | better |
| role fidelity | 5/43 = 0.116 [0.051, 0.245] | 10/66 = **0.151** [0.084, 0.257] | **not better** |
| lesson attachment | 2/43 = 0.046 [0.013, 0.155] | 1/66 = **0.015** [0.003, 0.081] | better |
| formula / number / unit (tagged) | 5/42 = 0.119 [0.052, 0.250] | 1/67 = **0.015** [0.003, 0.080] | better |
| figure / caption (where it applies) | — (n = 0) | 2/6 = 0.333 [0.097, 0.700] | n too small — see §2.4 |
| **false trust (derived, 5 criteria)** | 26/42 = **0.619** [0.468, 0.750] | 21/66 = **0.318** [0.218, 0.438] | better |
| false trust (annotator's own field) | 20/43 = 0.465 | 6/67 = **0.090** [0.042, 0.182] | better |

Per lesson, the spread is the story:

| lesson | NEW false trust (derived) |
|---|---|
| Khoa học 4 Bài 6 | **0.091** [0.016, 0.377] |
| KHTN 9 Bài 5 | 0.250 [0.089, 0.532] |
| LS&ĐL 4 Bài 12 | 0.273 [0.097, 0.566] |
| TV5 tập một Bài 5 | 0.300 [0.108, 0.603] |
| LS&ĐL 5 Bài 9 | 0.417 [0.193, 0.680] |
| **Toán 4 tập một Bài 37** | **0.600** [0.313, 0.832] |

**History/Geography, measured for the first time.** The OLD product served **one to two blocks per
lesson** — a `suSources` excerpt and its attribution. There was almost nothing to rescue; the pipeline
now produces 24 and 35 trusted blocks where the product had two. That reframes the question for this
subject from "did we rescue it" to "the pipeline now produces content where the product had none, and
none of it is trusted". LS&ĐL 5 Bài 9 also carries the batch's **worst display rate (0.417)** —
proper nouns and tone marks in historical prose (`Lý Thái Tổ` → `Lý Thái Tô`, `bản sắc` → `bán sắc`).

**Toán 4 tập một Bài 37 is the worst lesson in the batch** and is the last lesson of its book:
role 0.500, attachment 0.250, false trust 0.600. Its imprint page is served (§3).

### 2.2 What the withholding costs — **the round's clearest failure**

All 30 withheld regions were reviewed. **19 of 30 = 0.633 [0.455, 0.781] were judged OVER-withheld**:
clean, legible text refused for a reason that did not apply to it. Round 4 measured 0.400 on a
different sample; this build refuses more, and more of what it refuses is fine.

The pattern is siblings of served blocks being refused: an objective bullet refused while its sibling
is served; a `Tiến hành` step refused while its `Chuẩn bị` is served; `26 000 + 9 015 × 6` refused
while `78 060 : (10 − 7) + 300 045` is served. Two guard misfires stand out: the Physics section
title `II – Định luật khúc xạ ánh sáng` blocked by **`chem_guard`**, and several plain paragraphs
refused on `agree_tones` alone.

The 11 safe refusals are genuine: figure-dependent questions, a medal table with empty cells, the two
verse stanzas of the poem, a lone word-bank chip, two degenerate boxes over blank watermark strips.

### 2.3 Withholding that is not safe — orphaned siblings (Founder defect 8)

`tool/corpus/legacy/orphan.py` detects, independently of the pipeline and of Lane A1, the structures a
withhold mutilated. **These count as teaching-critical, not as "safely withheld".**

| batch | structures mutilated | kinds | withheld regions that orphan a sibling |
|---|---|---|---|
| **batch 2** (evaluation set) | **9** | `SPLIT_ENUMERATED_RUN` 5 · `SPLIT_CAPTION_SET` 3 · `SPLIT_OPTION_GROUP` 1 | **12 / 139 = 0.086** [0.050, 0.145] |
| **batch 1 re-run** (independent holdout) | **13** | `SPLIT_ENUMERATED_RUN` 4 · `SPLIT_CAPTION_SET` 6 · `SPLIT_OPTION_GROUP` 1 · `OPTIONS_WITHOUT_QUESTION` 1 | **12 / 126 = 0.095** [0.055, 0.159] |

The rate holds on a holdout of different lessons in different books — the detector generalises.

The Founder's own example is located exactly: **Toán 4 tập một Bài 37, pdf p130** serves options
`A. 1 số chẵn`, `B. 2 số chẵn`, `C. 3 số chẵn` and **withholds the fourth** (`agree_order`). A child
choosing the best of three answers when the right one was D is not seeing a smaller question; it is
seeing a wrong one.

**The first implementation of this detector missed that case.** It grouped siblings on the TSL's
`order` field — which is numbered separately for the served list and the withheld list, so the served
options are `order` 11, 12, 13 and the withheld fourth is `order` 17. The grouping is now on the
page-level index in the block id (011–014), and a test pins both the fix and the bug it replaces.

### 2.4 Figure/caption — the class round 4 could not measure

A quota sample of **all 20 `caption` blocks** across the batch's four figure-bearing lessons
(seed 20260907). Rates are **within the caption class** and are never pooled.

| measure | value |
|---|---|
| display fidelity WRONG | 5/18 = 0.278 [0.125, 0.509] |
| role fidelity WRONG | 1/20 = 0.050 |
| derived false trust | 6/14 = 0.429 [0.214, 0.674] |
| **detached from their figure (`figure_relation`)** | **10/19 = 0.526** |

Round 4 described captions that are character-perfect and teach nothing but had no field for them.
`figure_relation` is now that field (`audit.py`). Two readings were reported by the annotator and both
belong here: under "meaningless on its own" **10 of 19** are DETACHED (bare `Hình 1`…`Hình 7` labels
with no descriptive text, plus three chips split from their caption); under the literal "carries a
figure number" reading only **3** are. The distinction that matters: for seven of them **the printed
page carries no caption text at all**, so nothing was lost by extraction — a text-only pipeline is
serving a bare figure number as content. Only one row (`Hình 5.4`) is a proven split.

### 2.5 Method

`ORIGINAL SOURCE (PDF + Apple-Vision OCR) → tc2_run → tc2_sdm → tc2_attach → tc2_tsl →
tsl_to_lesson_document`, called as-is; Lane D never edits pipeline code. Containment is a shadow
`TC_ROOT` under `poc-out/round5/legacy/batch-2/tcroot/` with read-only symlinks to the corpus — every
byte the pipeline writes lands inside the batch directory, and the round-4 outputs are untouched
beside it. The run manifest records commands, exit codes, timings, tool versions, both code shas and
the sha256 of all 57 outputs.

Three annotators, each in a separate session, judged only from page renders and were forbidden the
sample files: OLD (43 rows), NEW (97 rows = 67 trusted + 30 withheld), caption quota (20 rows).

### 2.6 The REPAIRED stage is **empty**

`ORIGINAL → OLD → NEW` ran. **REPAIRED did not.** Lane A1's repair framework landed as scaffolding
(`origin/a1/round5-repair-framework`, engine + registry + ledger + 235 test lines, no repairer
plugins) and Lane A2's math repairer had not appeared on `origin` when this batch was measured. The
column is left explicitly empty rather than implied, and every restore number below says which
mechanism produced it.

---

## 3. The regression corpus — three surviving defects, on a third build

`tool/corpus/legacy/regression.py` turns each named defect into a deterministic probe over the
pipeline's own output, so "did the round fix it?" is answered by the build. Verdicts are
PRESENT / PARTIAL / FIXED / CHANGED / ABSENT. **CHANGED exists on purpose**: "the text is different
now" is not "the text is right now". **ABSENT exists so an empty run cannot read as a clean one.**

Batch 1 was re-run from the original source on the current build (`tc2-p2r` = PR #77's final head,
including the 14 post-review fixes — **not** the `cb60cde` round 4 measured).

| # | defect | round 4 `tc2-p2` | round 5 `tc2-p2r` | evidence |
|---|---|---|---|---|
| R1 | a book's **imprint page** served as the last lesson's body | PRESENT | **PRESENT** | pdf p121 attached, 23 trusted blocks, 8 of them imprint text: `…:p121:*:{001,004,005,006,007,019}` as `body`/`heading` |
| R2 | **fraction fragment** served as content | PRESENT | **PRESENT** | `…:p022:*:002` = `10`; `…:p022:*:016` = `b) 10 +` for printed `b) 3/10 + 5/21` |
| R3 | **tone slips in the lesson title** | PRESENT | **PRESENT** | `…:p021:*:001` = `CỘNG, TRỪ HẠI PHẬN SỐ KHÁC MẪU SỐ`, role `heading`, confidence 0.88 |
| R7c | **verse joined into prose** | CHANGED | **PARTIAL** | 7 regions now withheld with a `line_structure` reason — but 3 long single-run body blocks are still served, and the blind restore audit judged one of them (a four-line stanza) WRONG on this very build |

**Three of the three survive a third build.** R7c improved but is not closed — and the probe first
said FIXED. It called the class closed because *some* verse is withheld; the blind audit then found a
stanza served as one prose run on the same build. The probe now returns PARTIAL. **A probe that
reports FIXED while the class still fires is worse than no probe**, and this one nearly did.

**R1 generalises to a second book.** `regression.py tail-scan` asks the class of every lesson in a
batch: which attached pages carry no printed page number, and do any serve imprint text.
**Toán 4 tập một Bài 37 (a book never touched before) serves pdf p133 — its colophon — as trusted
`body`/`heading`**: the publisher's name, the CEO's name, the copyright line, the product code
`Mã số: G1HH4T001h26`. Round 4's back-cover fix moved one page of one book; the mechanism is intact.
The independent NEW-side annotator found the same row without being told to look
(`n20260906-0075`, the colophon code served as a Bài 37 heading).

---

## 4. Restore — the round's headline, measured on the only restores that happened

No repairer ran, so every restore here comes from a **guard change**, not a repair. The two are
different events and are never summed.

Base = batch 1 on `tc2-p1` (whose 30 withheld regions carry the round-4 OVER/SAFE review).
Re-run = the same lessons on `tc2-p2r`.

| measure | value |
|---|---|
| reviewed withheld regions | 30 |
| **restored** (served again) | **6** |
| falsely withheld, per the earlier audit | 12 |
| **falsely-withheld recovered** | **4 / 12 = 0.333** [0.138, 0.609] |
| restored that the earlier audit had called a **SAFE** refusal | **2** |
| **RESTORE PRECISION** (fresh blind judgement of what is served **now**) | **3 / 6 = 0.500** [0.188, 0.812] |
| falsely-withheld recovered **and** correct | **3** |

**The earlier audit's verdict on the refusal predicted the outcome almost perfectly.** Of the 4
restores it had called over-withheld, 3 came back correct. Of the 2 it had called safe refusals,
**both came back wrong**:

| id | what came back | verdict |
|---|---|---|
| `n20260906-0062` | a complete instruction sentence, character-exact | CORRECT |
| `n20260906-0083` | the section heading `CÂU ĐƠN VÀ CÂU GHÉP`, role `heading` | CORRECT |
| `n20260906-0082` | a passage paragraph, character-exact | CORRECT |
| `n20260906-0065` | **four verse lines served as one prose run** | WRONG |
| `n20260906-0066` | a lone `G:` marker — stranded page furniture | WRONG (was a SAFE refusal) |
| `n20260906-0100` | the bare label `Tiến hành:` as role `instruction`, the steps left outside | WRONG (was a SAFE refusal) |

**The operational reading: an over-withheld region is a good restore candidate; a region the audit
called a safe refusal is not.** That is a rule the repair lanes can use, and it comes with the
Founder's warning attached — half of these restores raised coverage with content that is wrong.

**The measurement nearly did not happen honestly.** The first sheets rendered `(no text recorded)` on
all six panels: `restore.py` accepted `new_block` only as a dict while `rerun.py` writes it as an id
string. The blind annotator **refused to score a precision on blank panels** and said so, rather than
assuming the benign reading. That is why there is no fake 6/6 in this report. Fixed, tested, re-judged.

---

## 5. Evaluation-set discipline

The 97-row audit is this lane's own batch-2 NEW annotation, now binding as an **evaluation set**.

- **Nothing was tuned to it.** Lane D changed no pipeline rule at all this round. The one content
  change (§1.6) is a Founder order about provenance, decided on the upstream file's own `status`
  field, not on any of the 97 rows.
- **Generalisation is shown on an independent holdout.** The orphan detector was built from defect 8
  and measured on batch 2 (0.086) **and** on batch 1's six different lessons in four different books
  (0.095) — a set no rule here was derived from. Both numbers are reported side by side in §2.3.
- Every named defect that falls in Lane D's scope is now a probe in `regression.py` (R1, R2, R3, R7c)
  or in `orphan.py` (defect 8) or in `pack-scan` (defect 6 on the shipped surface).

---

## 6. Did round 5 rescue more legacy data? — **partially, and it withheld more than it repaired**

**Yes, against the product it replaces.** On six lessons never measured before, false trust falls
0.619 → 0.318, teaching-critical 0.476 → 0.100, reading order 0.455 → 0.000, formula/number/unit
0.119 → 0.015, and the pipeline serves 239 blocks where the product served 80.

**No, against round 4.** False trust is 0.318 where round 4's batch measured 0.297; over-withholding
went 0.400 → 0.633. The build refuses more, and more of what it refuses is clean text.

**No on the defects that matter most.** Three named defects survive a third build, the imprint
mechanism generalises to a second book, and the verse defect is only partly closed.

**And withholding is not free in the way round 4 assumed.** 9 structures in batch 2 and 13 in batch 1
are mutilated by their own safety mechanism — a multiple-choice missing an option, an enumerated run
with a hole, a caption split from its figure. Those are teaching-critical errors *caused by the
guard*, and until this round they were counted as safe.

**Reprocessing made the legacy corpus safer and smaller again. It still did not make it teachable.**
0 lessons trusted, 0 eligible for teaching, and the pipeline cannot raise either.

---

## 7. What is still not measured

- **The REPAIRED stage.** No repairer ran; RESTORE PRECISION is measured on 6 guard-change restores,
  n = 6, interval [0.188, 0.812]. It is a first reading, not a rate.
- **The OLD side of batch 2 rests on a single annotator** (43 rows). No second annotation, no κ for
  this batch. Round 4's κ on the shared classes (false trust 1.000, role 0.423–0.713) is the only
  agreement evidence, and it was measured on other rows.
- **Role is unstable in every measurement so far** and is again the class that did not improve
  (0.116 → 0.151). Lane A3's role spec is the right place for it; role rates here are
  annotator-dependent and should not gate anything.
- **Figure/caption is a quota sample of 20 blocks in four lessons**, and its headline (`figure_relation`
  0.526) depends on a rubric reading the annotator flagged. Both readings are in §2.4.
- **12 lessons of 243 in scope, of 3,679 canonical.** Nothing here supports a claim about the corpus.
- **No teaching claim of any kind.** `eligible for teaching` is 0.
