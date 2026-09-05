# False-trust audit protocol — statistical audit of the content that actually ships (Founder D3)

WAL-210 item 10a · 2026-09-05 · tooling: `tool/corpus/ft_audit_sample.py`, `tool/corpus/ft_audit_score.py` · status: **PROTOCOL + TOOLING, thresholds PROPOSED, nothing decided**. Annotation of the shipped sample is the Founder's / an independent reviewer's job; the agent that built the tooling did not annotate it.

Founder decisions this implements: **D3** (audit the exact shipped content; no coverage expansion before G1/G2/G3; never lower a threshold to pass; report display-only fidelity, teaching-critical fidelity, role fidelity, lesson attachment and false trust **separately**), **D4** (verbatim SGK text and page crops are INTERNAL / RESEARCH ONLY — the sheet, the JSONL and the crops live only in gitignored `poc-out/b-lane/ft-audit/`), **D5** (every number carries its denominator, census and subset — see `METRIC-DENOMINATORS.md`).

## 1. What is audited — the population ("frame")

Every block a child would read from the DEFAULT packs (`assets/pack/lesson-index-g1…12.json`, `buildProvenance.experimental == false`; the sampler refuses an experimental pack), decomposed to the unit the rates are defined on:

| family | served blocks per activity | source link |
|---|---|---|
| khoaExperiments | title · Chuẩn bị · each Tiến hành step · Dự đoán · Quan sát | `poc-out/graph/ocr-body/<book>/pNNN.json` line span + bbox; TC-v2 SDM block on the same page where the six Science books overlap |
| tvReadings | passage · each question | TV5 unit id (`poc-out/units/<book>.json`) → pdf page → OCR line span |
| tvWritings | prompt | unit id → OCR line span |
| suSources | excerpt · attribution (samGloss is SAM's own text — excluded) | OCR line span |
| toanExercises | expression | exercise-case-map pdf page (no line span: the expression is rebuilt from geometry) |
| diaMaps | caption · each question | pdf page + bbox from the crop registry |
| sourceAssets | printed caption (each asset once) | pdf page |
| samUnits | every row of `assets/pack/sam-units.db` (grounding store, separate denominator) | unit id → pdf page → OCR line span |

Measured frame on 2026-09-05 (packs `g*-20260905T0432Z-07a2450e`): **3,334 served blocks in 2,798 activities** — khoaExperiments 212 · tvReadings 430 · tvWritings 54 · suSources 8 · toanExercises 41 · diaMaps 3 · sourceAssets 2 · samUnits 2,584 — in 25 strata (family × book). Manifest: `poc-out/b-lane/ft-audit/manifest-20260905.json`.

**Mandatory first stratum (Founder addendum):** KHTN 6 Bài 17 «Tách chất khỏi hỗn hợp» — every shipped default-pack activity of that lesson (**measured: 0** after the WAL-210 regeneration; the only Bài 17 entry on disk before it was a router `EXPLAIN_SHORT` reading) **plus** every block of its TC-v2 Trusted Structured Lesson (`lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json`, read-only: 60 TRUSTED blocks with text, 4 WITHHELD blocks listed for context without text). They are listed first in the sheet, with crops of pdf pages 61–64.

## 2. Sampling design

- **Unit** = served block (the rates are block rates). The sheet groups blocks by activity so the reviewer sees context; blocks from one activity are not independent, so the block-level interval is optimistic — the activity count is reported beside it.
- **Strata** = (family, book). **Allocation** = proportional to stratum size with a floor of 3 per stratum (capped at stratum size). **Selection** = `random.Random(seed)` over a deterministically ordered frame (family, book, lesson, pdf page, activity id, kind) — the same seed always reproduces the same sample. Default `--seed 20260905 --n 400`.
- Drawn sample 2026-09-05: **484 rows = 420 stratified + 64 Bài 17 TSL blocks**; 408/420 pack rows linked to an OCR line span (the 12 unlinked are Toán expressions rebuilt from geometry and a few passages whose page could not be resolved from the unit), 27 linked to a TC-v2 SDM block (the Science experiments — their SDM trust status and reason codes are shown to the reviewer as context, never as a verdict).
- Every row carries the pack's `packVersion` + `contentHash`, so a re-audit after any rebuild is a different, comparable sample of a different population.

## 3. What the reviewer marks (per row; values `OK` / `WRONG` / `UNSURE` / `NA`)

Judged from the page crop / full-page render — never from the served text alone:

1. **display_fidelity** — the served text equals the page text character-for-character (tone marks, enumerators, nothing spliced from another box).
2. **teaching_critical_fidelity** — numbers, formulas, units, terms, negations are correct (`NA` when the block carries none).
3. **role_fidelity** — the block is served in the right role (question / instruction / objective / sidebar / answer / body-passage / caption). The `kind` column is the role the pack or TSL assigned.
4. **lesson_attachment** — the activity is attached to the right lesson (judged once per `activityId`).
5. **false_trust** — the reviewer's overall verdict: served as trusted but wrong in a way that would mislead a learner.

The scorer also **derives** false trust from the first four (WRONG if any is WRONG, attachment via the block's activity) and reports both.

## 4. What the scorer reports (`ft_audit_score.py <sample.jsonl>`)

Per family and overall: each of the five rates as `WRONG / (OK + WRONG)` over judged served rows, with a **Wilson 95 % interval**, plus the counts of UNSURE, NA and unjudged rows and the sampled count — denominators are never collapsed: `k / n judged (of m sampled; population N in the manifest)`. Withheld TSL rows never enter a served denominator; they are counted as "withheld, reviewed" (safe-rejection audit).

**Validation on real data (2026-09-05):** run in `--from-gold` mode on the 54 TC-v2 gold pages, the scorer reproduces `metrics/gold-scores.json` exactly — all **50 / 439 = 0.1139** [0.0875, 0.1470], dev 36/323 = 0.1115, held-out 14/116 = 0.1207, science **19 / 190 = 0.100** [0.065, 0.151]. Output: `poc-out/b-lane/ft-audit/scorer-validation-gold.json`.

## 5. Sample size for a "< 1 % false trust" claim (formula, not a decision)

Wilson upper bound `U(k, n) = (p̂ + z²/2n + z·√(p̂(1−p̂)/n + z²/4n²)) / (1 + z²/n)`, `p̂ = k/n`, `z = 1.96`. With **k = 0** observed false-trusted blocks, `U(0, n) = z²/(n + z²) < 0.01 ⇔ n > 99·z² = 380.3 ⇒ n ≥ 381`. The exact one-sided bound (Clopper–Pearson) gives `(1 − 0.01)^n ≤ 0.05 ⇒ n ≥ ln 0.05 / ln 0.99 = 298.1 ⇒ n ≥ 299` (the "rule of three").

| k false-trusted observed | n judged needed (Wilson) | n (exact) |
|---|---|---|
| 0 | 381 | 299 |
| 1 | 563 | 473 |
| 2 | 726 | 628 |
| 3 | 878 | 773 |
| 4 | 1,025 | 913 |
| 5 | 1,166 | 1,049 |

The 420-row stratified sample therefore supports a < 1 % claim only if **zero** false-trusted blocks are found (Wilson) — and the TC-v2 gold, where the pipeline is best, runs at 10 %. Reading the numbers the other way: at the measured 0.10–0.32 hard-page rates a 420-block sample will find 40–130 failures, which is the point — the audit is expected to fail the bar and to say by how much, per family.

## 6. Denominators (D5)

- Rates: `k / n judged served blocks of the sample · seed 20260905 · subset <family × book>`; population: `3,334 served blocks / 2,798 activities · packs g*-20260905T0432Z-07a2450e`.
- The historical **3,679 canonical** and **3,381 ranged** are never divided into here; the learnable-lesson count after G2/G3 is **111 / 3,679** (PR-1 regeneration report) and is a coverage number, not a trust number.
- Bài 17 TSL rows: `k / 60 trusted TSL blocks · TC-v2 tc2-p1 · KHTN 6 Bài 17 only`.

## 7. Acceptance thresholds — PROPOSED for the Founder, not decided

| rate | proposed bar for a "trusted" label | rationale |
|---|---|---|
| false trust (derived) | Wilson upper bound **< 1 %** overall and per family that ships | the Founder's stated bar; the table above gives the n it needs |
| teaching-critical fidelity | **0 WRONG** in the judged sample (any WRONG blocks the family until fixed) | a wrong number/formula/negation teaches something false — no rate is acceptable |
| display-only fidelity | Wilson upper bound < 2 % | tone-mark and enumerator slips mislead less but erode trust |
| role fidelity | Wilson upper bound < 5 % for served roles; **≥ 0.95 precision** before any block is *asked* as a question (TC-19 #3, still not met — see the role-layer experiment) | a passage served as a question is the WAL-204/206 failure class |
| lesson attachment | 0 WRONG activities in the sample | the audit already found 3/32 wrong before G2; G2 now withholds ambiguous pages |

Rules that go with the bars: never lower a bar to pass; a family that fails ships nothing new until the failing class is fixed and re-sampled with a new seed; UNSURE rows count as neither side but are listed; a second annotator on ≥ 10 % of rows before any bar is called met.

## 8. How to run

```
# from the main checkout (poc-out/ and assets/pack/ present)
python3 tool/corpus/ft_audit_sample.py --seed 20260905 --n 400              # sheet + JSONL + crops (internal)
# reviewer fills the five fields in poc-out/b-lane/ft-audit/sample-20260905.jsonl
python3 tool/corpus/ft_audit_score.py poc-out/b-lane/ft-audit/sample-20260905.jsonl --md poc-out/b-lane/ft-audit/scores.md
python3 tool/corpus/ft_audit_score.py --from-gold --gold-dir <tc_gold dir>  # scorer self-check on the gold pages
```

Nothing in this protocol touches a TSL file (read-only), a pack, or a threshold.
