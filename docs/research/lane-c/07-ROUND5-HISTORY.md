# 07 — LANE C round 5 (§11): Bài 8 on the current pipeline, the verbatim gate, and what the deliberate stress tests falsified

**READY FOR FOUNDER REVIEW — nothing merged.** Base `integration/round5-2026-09-06`. Bounded to LS&ĐL 5; the two rules stay **PROPOSED and History-only**; nothing entered the universal bridge. `flutter analyze` clean · `flutter test` 928 passed / 42 skipped / 0 failed (the skipped ones need the gitignored real fixtures, absent in a worktree) · Lane C Python tests 31 passed / 2 skipped. Denominators are stated per table and never summed (D5). D4: no SGK text in the repo — the verbatim ledger records verdicts and single differing tokens only.

Evidence (gitignored): `poc-out/round5/lane-c/tc2-lsdl5/v1/` — `root/…/tc2-r5/{manifest,attach,sdm,lessons}`, `lesson-document/`, `lesson-document-all/` (28 lessons), `history-rules-v2/`, `report/{round5-rerun,tone-repair-probe,history-stress,repair-plugin}.{json,md}`, `report/repair-ledger.jsonl`. Repo copies: `data/lsdl5-round5-rerun.md`, `data/lsdl5-tone-repair-probe.md`, `data/lsdl5-history-stress.md`, `data/lsdl5-repair-plugin.md`, `data/lsdl5-bai8-verbatim-ledger.json`. Scripts: `tool/research/lane_c/{round5_rerun,tone_repair_probe,history_stress,repair_plugin,history_rules}.py`.

**Method note that makes every number below attributable:** the round-5 run reuses **round 4's raw Docling/XY-cut candidate files** and re-runs only `tc2_sdm → tc2_attach → tc2_tsl → tsl_to_lesson_document`. Every difference is therefore pipeline *code* (`sdm-v2` → `sdm-v3`), never OCR noise. `tool/corpus/**` was not edited; the run is sandboxed with `TC_ROOT` and `--out`.

---

## 1. What changed for Bài 8 and for the book

| measure | round 4 | round 5 |
|---|---|---|
| lessons with a TSL (LS&ĐL 5) | 23 / 28 | **28 / 28** (the `Ã` fix landed) |
| headers detected | 23 (TOC-confirmed 6) | **28 (TOC-confirmed 10)** |
| book learning blocks | 1 483 = 1 263 trusted + 220 withheld | 1 472 = **1 020 trusted + 452 withheld** |
| chapters | 0 | **6 «Chủ đề»** (Bài 8 sits in Chủ đề 3) |
| Bài 8 boundary | 38–41, conf 0.95, source `both` | unchanged |
| Bài 8 learning | 51 = 34 + 17 | 51 = **36 trusted + 15 withheld** |
| Bài 8 trusted roles | heading 8 · stage_label 5 · body 14 · question 4 · caption 3 | heading 5 · **objective 1** · body 15 · stage_label 5 · question 3 · **attribution 4** · caption 3 |
| Bài 8 withheld reasons | colour 14 · agree_text 3 · agree_order 2 · box_boundary 1 | **agree_tones 7** · colour 4 · agree_text 3 · figure_dependent 1 · box_boundary 1 · agree_order 1 |

Book-level withhold reasons moved as much as the totals: `agree_tones` **0 → 179**, `agree_order` 21 → 63, `agree_numbers` 0 → 22, `line_structure` 0 → 4, `chem_guard` 0 → 1, while `page_feature:color_heavy` fell 23 → 10. **Trusted text fell by 243 blocks book-wide.** That is the round-4 third signal doing exactly what it was built to do, and it is the reason round 5's priority is repair, not more withholding.

**The five Lane C requests from round 4 all landed.** Block-level colour released the whole white column of the opener page (p038: 7 / 21 learning blocks trusted → **13 / 21**, and 0 / 15 of its learning TEXT → 9 / 15; colour withholds 14 → 4); the `Ã` character class found the five missing headers; the `attribution` role exists (4 trusted on Bài 8, **36** across the book, from which `story-attribution-v1` derives 31 attributions); the `figure_dependent` guard now catches «quan sát các hình từ 1 đến 3»; `Chủ đề` chapters parse; both gold errata are fixed.

### The 10 blocks that came back and the 8 that left

Newly trusted on p038: the two objectives, the KHỞI ĐỘNG question, all four poem lines and **the Hồ Chí Minh attribution** — the entire lesson head that round 4 lost to a page-level colour flag. Plus the story-box badge on p039.

Newly withheld: the lesson banner (`p038:003`), the section heading (`p038:018`), the Trưng Vương story title (`p039:009`), the figure-dependent question (`p039:003`), the Ngô Quyền conclusion (`p041:001`), the VẬN DỤNG question (`p041:021`), a LUYỆN TẬP question (`agree_order`) — and, decisively, **`p039:000`, the single block that carried all seven dated events.**

### The consequence for the two rules, measured

| | round 4 (v1, round-4 document) | round 5 (v1, round-5 document) | round 5 (**v2, verbatim gate ON**) |
|---|---|---|---|
| `prose-dated-events-v1` events | 7 | **0** | 0 |
| `story-attribution-v1` attributions | 3 (2 complete) | 4 (0 complete) | **3** (0 complete, 1 withheld by the gate) |
| `history-tutor-v1` steps | 7 | 0 | 0 |

`history_rules.py --no-gate` on the round-4 document still reproduces 7 / 3 / 2 / 7 exactly, so the round-4 numbers stay verifiable.

**Why the events vanished.** `p039:000` is withheld for `agree_tones` on **one token**: the primary reads «Bạch **Đằng**», the verifier reads «đăng». The human read of the printed page (below) says the **primary is right and the verifier is wrong**. Fail-closed is correct behaviour with only two stacks — and it costs the whole timeline. This is the single sharpest case in the round for the DETECT → REPAIR → VALIDATE → RESTORE strategy.

---

## 2. The verbatim ledger, and the false-trust / false-withhold scoreboard

Round 4 falsified **A26**: two OCR stacks agreeing (`text_sim = 100`) does not mean the text is verbatim. So Lane C read the four printed page renders again and recorded, per block, what the **print** says (`data/lsdl5-bai8-verbatim-ledger.json` — verdict plus the differing tokens, never the sentence). It is the only signal that can decide the two cells below.

| cell (denominator: the 51 Bài 8 learning blocks the human read judged) | round 4 | round 5 |
|---|---|---|
| correct served (trusted ∧ verbatim) | 26 | **30** |
| **FALSE TRUST** (trusted ∧ the print differs) | 8 | **6** |
| **FALSE WITHHELD** (withheld ∧ verbatim) | 14 | **10** |
| correct withheld (withheld ∧ the print differs) | 3 | 5 |

Both error classes fell, and the movement is real rather than a trade: correct-served rose by 4 while false-trust fell by 2 and false-withheld by 4.

The six remaining false-trust blocks are all **display-font headings and badges**: `p038:006` «Sưu tẩm», `p039:001` «cuộc đầu tranh», `p039:008` «Lích sử», `p040:002` «LÝ BĨ», `p040:008` «ĐẠI PHẢ … NAM HÃN», and `p041:002` — the attribution. `agree_tones` is silent on every one of them because **both stacks make the same slip**. A26 is confirmed a second time, on new data.

**The p38 anchor, precisely.** Round 4 lost «Âu Lạc (179 TCN)» to a page-level colour flag. Round 5 releases the colour flag and the block is withheld for `agree_text` at similarity 70 — but the human read says the block is **verbatim**, and the verifier's raw output shows why: on p038 the XY-cut stack merged the body column and the «Em có biết?» sidebar column into one block. It is a linearisation artefact, not a disagreement. Separately, the year itself **is now reachable from a trusted block**: the newly trusted objective `p038:005` carries «(ví dụ: 179 TCN, 40, 248, 542, 938,...)» verbatim — but as a curriculum example with no actor, which `prose-dated-events-v1` correctly refuses to promote to an event.

**The attribution, precisely.** `p041:002` still reads «Bạch Đăng» for the printed «Bạch Đằng» and «Văn hóa» for «Văn hoá», still at `text_sim` = 100, and `agree_tones` still does not fire. It is **not** verbatim-verified. Under the v2 gate it is withheld and never quoted; the honest child-facing line remains publisher + year, which are exact.

---

## 3. Bounded implementation: the verbatim gate (both rules stay PROPOSED, History-only)

`history_rules.py` v2 adds a gate that the rules must pass **before** they emit anything:

- an event is emitted only when its source block is `verifiedAgainstPrint`; otherwise it is recorded in `eventsWithheld` with the reason and the slips the print shows (nothing is silently lost);
- an attribution is emitted only when its own block is verified; a **story title** that is not verified is never quoted back at the child — the block id stays for provenance, `title` becomes `null`, and the story is marked incomplete;
- every event keeps its `charSpan` into its block and every attribution its `charSpan`, page, printed page and bbox, as in round 4;
- with no ledger the rules run **v1** and reproduce the round-4 output byte for byte.

The gate is enforced a second time in Dart (`lib/core/lesson_model/timeline_verbatim.dart`): `TimelineValidator.servableEvents` and `deriveStoryAttributions` drop anything unverified, and `TimelineView` states the truth in both directions — with the gate **off** it says the timeline has not been checked against the print (silence would be the A26 lie), with the gate **on** it counts what it held back. Announced Lane B file: `lib/features/lesson_workspace/views/timeline_view.dart`.

**Reported, not fixed (CLAUDE.md rule 5):** `LessonDocument` does not preserve `provenance.historyRules`, so the Dart index must be passed in by whoever loads the fixture — the gate cannot arm itself from the document yet. Owner: A-runtime.

---

## 4. Can the losses be repaired? Lane C on Lane A1's framework

Lane A1 published `tool/corpus/repair/` (DETECT → REPAIR → VALIDATE → RESTORE with a plugin registry) but no Vietnamese repairer yet. Lane C registered **from its own package**, editing nothing under `tool/corpus/`, three fail-closed repairers and one validator that may not validate its own generator's layer:

| repairer | layer | what it proposes |
|---|---|---|
| `lanec.tone-corroboration-v1` | D (in-corpus consistency) | `agree_tones` fired, but an independent signal corroborates the **primary** ⇒ propose the value **unchanged**. A repair of the *disposition*, not of the text. |
| `lanec.tone-majority-v1` | D | the primary's form is the minority for its context ⇒ propose the dominant majority, **per token span** |
| `lanec.column-linearisation-v1` | B (layout) | `agree_text` fired, but the primary's tokens are a **subsequence** of the verifier's whole-page stream ⇒ the stacks never disagreed |

Validator `lanec.history-text-validator-v1`: one objection rejects; otherwise the candidate needs support from a layer other than its generator's, else `insufficient` (never a soft yes).

**Result on all 52 Bài 8 learning blocks (16 withheld in, 36 trusted in):**

| outcome | n | the ones that matter |
|---|---|---|
| withheld → **restorable** (VALIDATED_REPAIR) | **6 / 16**, all print-confirmed | **`p039:000` — the events block, text unchanged**; **`p038:023` + `p038:024` — the 179 TCN column, text unchanged**; `p041:001`; two heading repairs |
| withheld, stays withheld | 10 / 16 | the four colour-heavy question/sidebar blocks (no text repairer applies), `p039:009` (neither stack is right), `p040:003`, `figure_dependent`, `agree_order` |
| trusted → **demoted to WITHHELD** | **2 / 36** | **`p041:002`, the attribution**, and `p040:008` |
| trusted → repaired and revalidated | 3 / 36 | `p038:006`, `p039:001`, `p040:002` — single-token slips fully covered |

**Feeding the restored blocks back through `prose-dated-events-v1` with the gate ON yields 8 events** — the seven of round 4 **plus «Âu Lạc (179 TCN)»**, the anchor round 4 could not reach. The deciding signal is layer **E, the human print read**; layer D alone proposed the right change but cannot validate itself, and layer B alone explains the column case but still needs an independent confirmation.

**The attribution is the counter-example that justifies the whole framework.** The layer-D signal proposes «Đăng»→«Đằng» for the river (support 7) *and* «Đăng»→«Đặng» for the author «Đăng Khoa» (support 3). The second is wrong — it rewrites a person's name. Once the human signal is checked **per occurrence** (the ledger records the left context «Bạch —») and **for completeness** (the repair leaves «Văn hóa» → «Văn hoá» uncovered), it objects twice and the candidate is rejected. The block is then demoted from TRUSTED to WITHHELD. So: **the attribution does not become verbatim-verified**, and the honest outcome is that it stops being served rather than being half-corrected.

`p038:027` shows A1's `covers_reasons` contract working as written: a validated `agree_text` repair still leaves `page_feature:color_heavy` uncovered, so the block stays withheld.

### The signal on its own, measured (`tone_repair_probe.py`)

Two rule variants × two evidence scopes, all reported — not one tuned point. Ground truth is the human ledger; nothing is ever applied.

| rule | scope | candidates | correct | false corrections | missed | precision | recall | **false-correction rate** |
|---|---|---|---|---|---|---|---|---|
| strict-unattested | lesson | 1 | 1 | 0 | 14 | 1.000 | 0.067 | 0.000 |
| strict-unattested | book | 1 | 1 | 0 | 14 | 1.000 | 0.067 | 0.000 |
| dominant-majority | lesson | 6 | 6 | 0 | 9 | 1.000 | 0.400 | 0.000 |
| dominant-majority | **book** | 9 | 8 | **1** | 7 | 0.889 | 0.533 | **0.111** |

Denominator: the 15 token slips the print shows in Bài 8. Two structural limits, reported rather than hidden: the probe strips **tone marks only**, so «HÂN» vs «HÁN» (a vowel-quality difference) is invisible to it; and «hóa» vs «hoá» is not a tone error at all but the book's **orthographic convention** — measured across the book's trusted text, the old style leads 265 to 42, which is a separate, cheap, deterministic signal Lane A1 could add.

**For Lane A1:** a false-correction rate of 0.111 at the best recall point, with the false correction landing on a **proper name**, is the empirical case for «a repair is never trusted by default». One signal is not enough; the independent-layer rule is what saved it.

---

## 5. Deliberate falsification on the other 27 lessons (§11 item 3)

### T1 — does `prose-dated-events-v1` survive a different date style? **NO.**

Across the 28 bridged lessons the book prints **112 date mentions in eight forms**. The rule accepts one of them.

| form | occurrences | accepted? |
|---|---|---|
| `narrative-year` («năm 1945») | 54 | counted, never promoted (by design) |
| `paren-year` («(1288)») | 21 | **yes — the only accepted form** |
| `century` («thế kỉ XIX») | 13 | no |
| `reign-period` («thời Trần») | 12 | no |
| `decade-range` («1418 - 1427», outside parentheses) | 8 | no |
| `bare-tcn` («208 TCN») | 2 | no |
| `narrative-year-tcn` («Năm 208 TCN») | 1 | counted, never promoted |
| `century-tcn` («thế kỉ III TCN») | 1 | no |

Total events extracted over the whole book: **3** (mis-promotions: 0 — the rule is precise where it fires). Bài 5 alone («NHÀ NƯỚC VĂN LANG, NHÀ NƯỚC ÂU LẠC») prints a TCN year, a TCN century and a narrative TCN year and yields nothing. **The rule is a Bài-8 shape, not a History shape**, and it must not be generalised.

### T2 — does `story-attribution-v1` survive a quoted document instead of a story? **In form yes, in substance no.**

31 attributions found across the book — 30 `(Theo …)` and **1 quoted document** (Bài 14, p066: a Hồ Chí Minh quotation closed by «NXB Chính trị quốc gia Sự thật, 2018»), which the rule handles without a change. But:

- **2 of 31 stories are `complete`.** 29 carry at least one withheld paragraph.
- **17 of 31 never find a title heading** (the walk-back hits a caption, a question or a page break first).
- The book prints only **one** «TƯ LIỆU» box (Bài 3) — so the round-3 expectation that TƯ LIỆU is a major History shape in *this* book is not borne out; the quoted document arrives as a plain paragraph closed by an attribution.
- Story titles are a **systematic false-trust class**: of the 14 titles the rule found, an independent in-corpus signal objects to **5** — and on Bài 8, where the print was read, the objection was right both times («LÝ BĨ», «NAM HÃN»).

### T3 — does lesson identity survive a two-lesson spread? **Yes at page granularity; a chapter banner leaks.**

On all 24 header pages the «BÀI N» banner sits at the top with **0** learning blocks above it, so no lesson loses its tail to the next one. But **5 pages carry two lessons** (27, 38, 78, 95, 111 — every theme-opener page), and on each the block the *previous* lesson keeps is the **next chapter's «Chủ đề N» banner**: withheld on 3, and **trusted and served inside the wrong lesson on 2** (Bài 17 carries «Chủ đề 4 CÁC NƯỚC LÁNG GIỀNG», Bài 25 carries «Chủ đề 6 …»). A child finishing Bài 17 reads the heading of the next chapter as part of the lesson.

**Contradiction to report, not fixed (owner: A-pipeline `tc2_attach`):** a chapter banner on a lesson's first page belongs to the chapter or to the new lesson, never to the previous one.

---

## 6. The `TimelineValidator` verdict — **DO NOT REGISTER. Evidence Reality stays 0.**

The question was whether `timeline-order-v1` can be honestly registered in Lane A-runtime's validator registry, at the bar Lane A-runtime used (deterministic · evidence-carrying · no invented answer set). Three findings decide it, and only the third would be fixed by more work.

1. **Its domain is currently empty.** On the shipped pipeline `prose-dated-events-v1` yields **0** events for Bài 8 and **3** for the whole book. A registered validator whose answer set is empty can never fire; registering it would add a name to the registry and nothing to a child.

2. **The book does not state a unique answer set for its own exercise.** LUYỆN TẬP 1 prints a four-slot timeline: `Sự kiện` = [Khởi nghĩa Hai Bà Trưng] [?] [?] [?] and `Thời gian` = [40 – 43] [?] [?] [938]. The book names slot 1 and the year of slot 4 and leaves the two middle slots open, while the prose lists **seven** candidate events and the objective lists five example years («179 TCN, 40, 248, 542, 938»). Any grader that scored the middle slots would be **inventing an answer set** — the exact thing the bar forbids. (Read on the print: `data/lsdl5-bai8-verbatim-ledger.json` → `exercise_answer_set`.)

3. **Even after repair, its facts would rest on a `VALIDATED_REPAIR`, not on an original observation.** The 8 events are recoverable only through the repair loop, and a repair's disposition is `VALIDATED_REPAIR` — eligible to be restored, not automatically `TRUSTED`. A registered validator must not stand on a disposition the Founder has not accepted for serving.

**What `timeline-order-v1` may keep doing, unregistered:** exactly what it does now — a pure function the History view and the tests call for the «Thử xếp thứ tự» participation exercise, returning typed checks that quote «sách viết …» with the source block ids, writing no `LearningEvent` and no evidence. That is honest and needs no registry entry.

**What would change the verdict** (all three, not any one): the events restored under a Founder-accepted disposition; a lesson whose printed exercise states its own answer set (a timeline whose slots the book fills, or an SGV key paired by section context per H6); and a QUESTION-precision measurement on History gold ≥ 0.95, which today stands at n = 7 across four pages. Until then: **Evidence Reality 0 / 0 for History**, and the honest child-facing wording stays «không phải bài kiểm tra».

---

## 7. Requests and contradictions (reported, not resolved — CLAUDE.md rule 5)

| # | to | what |
|---|---|---|
| 1 | **A1 (repair)** | Take Lane C's three repairers, or their shapes: the **corroboration** repairer (an `agree_tones` block whose primary is corroborated is a disposition repair, not a text repair) and the **column-linearisation** signal (`agree_text` where the primary's tokens are a subsequence of the verifier's page stream) between them make 6 of 16 withheld Bài 8 blocks restorable, print-confirmed. Measured false-correction rate of the tone-majority signal alone: **0.111**, on a proper name. |
| 2 | **A1 (Vietnamese)** | The book's **orthographic convention** («oà/oá/uỷ» 265 vs «òa/óa/ủy» 42 in trusted text) is a cheap deterministic signal that the tone-only comparison structurally cannot see, and it is the uncovered half of the Bài 8 attribution. |
| 3 | **A-pipeline (attach)** | A «Chủ đề N» chapter banner on a lesson's first page is attached to the **previous** lesson on 5 pages, served trusted inside the wrong lesson on 2. |
| 4 | **A-pipeline (guards)** | `agree_tones` withheld `p038:018` for a token pair («kì»/«ki») that is not the block's actual slip («đầu» for «đấu») — the right outcome for the wrong reason; worth knowing when the guard's precision is measured. |
| 5 | **A-runtime / Lane B** | `LessonDocument` drops `provenance.historyRules`, so the Dart verbatim gate cannot arm itself from the document. |
| 6 | **Founder** | The two rules remain PROPOSED and History-only. T1 says `prose-dated-events-v1` must **not** be generalised: it covers 21 of 112 printed date mentions in its own book. |
| 7 | **Founder** | `timeline-order-v1` should **not** be registered (§6). The first real validator outside the Toán Deep path is not this one. |

## 8. Device

The Nokia was **not free**: a read-only check (never woken, never unlocked, no input) found the display on and `ai.workizen.learningcoach/.MainActivity` in the foreground — another lane's walk or the Founder's own session. Lane C stopped there and installed nothing. The Lane B surface change from this round is one added line in `TimelineView` (the «chưa đối chiếu bản in» note); the device loop belongs to Lane B in round 5 and can walk it.
