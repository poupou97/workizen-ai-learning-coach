# Role-layer signal experiment — can an icon / box-colour signal lift QUESTION precision to 0.95 and make ACTIVITY detectable? (MEASURED, 2026-09-05)

WAL-210 item 10b · bounded research, deterministic, no LLM · script `tool/corpus/role_signal_experiment.py` · outputs `poc-out/b-lane/role-signal/` (features.jsonl, results-v1/v2/v3.{json,md}) · gold: the 54 TC-v2 pages (38 dev + 16 held-out, read from the `research/tc-v2-science-slice` branch) + a new **KHTN 6 Bài 17** gold (4 pages, 73 blocks, `tool/corpus/tc_gold_bai17/`, anchors + roles + bboxes only per D4).

**Verdict up front — the Short-Answer gate (QUESTION precision ≥ 0.95) is NOT met.** Best held-out QUESTION precision with the signal is **0.938 (15/16 predictions)**, science 0.929, Bài 17 0.857. ACTIVITY goes from 0.00/0.00 to **0.333/0.333 (held-out), 0.286/0.200 (science), 0.222/0.400 (Bài 17)** — detectable, not usable. Nothing was forced; the rules are printed with the dev evidence they were frozen on.

## 1. Setup

- **Pipeline blocks:** TC-v2 `sdm-gold` pages (Docling + Apple Vision ▸ XY-cut verifier ▸ deterministic Role Layer, unchanged). **Baseline** = the pipeline's own fine role mapped to the six canonical roles exactly as `tc2_score.py`; matching = `tc_score.match`. The harness reproduces `metrics/gold-scores.json` to the third decimal before any signal is added (QUESTION dev 0.893/0.750, held-out 0.833/0.938, science 0.889/0.870; ACTIVITY 0/0 everywhere).
- **Image features per block** (72-dpi PyMuPDF render, numpy, no learned model):
  - *left strip* (x − 7.5 % … x − 0.3 % of page width, the block's own line band): a compact saturated blob 0.5–3 × the line height with aspect 0.35–2.5 → `icon_present`, mean hue → `icon_bucket` ∈ {orange 10–50°, green 70–170°, blue 185–250°, other};
  - *box tint* (bbox grown 1.2 % / 0.6 %): pale-tinted pixel share `tint_share` and median hue `tint_bucket`;
  - *inheritance*: blocks in the same tinted box (same bucket, `tint_share ≥ 0.3`, vertically contiguous ≤ 0.12 page heights, x-overlap) inherit the box's top-most icon — the KNTT icon marks the box, not each line.
- **Sets:** dev = 38 TC-v1 pages (rules were frozen on these); held-out = 16 TC-v2 pages (never looked at while writing rules); science = 23 pages from the six Science books or their SGV (11 of its 18 SGK pages are ALSO held-out, so it is not an independent third set); **Bài 17** = 4 new pages, neither dev nor held-out.

## 2. The rules and the evidence they were frozen on (dev pages only)

| gold role (dev) | n | own icon | effective icon | orange | blue | green | tinted box | tint orange | tint blue |
|---|---|---|---|---|---|---|---|---|---|
| QUESTION | 100 | 18 | 25 | 7 | 13 | 1 | 28 | 22 | 3 |
| ACTIVITY | 5 | 1 | 1 | 1 | 0 | 0 | 4 | 3 | 0 |
| OBJECTIVE | 10 | 2 | 2 | 0 | 1 | 0 | 1 | 0 | 1 |
| SIDEBAR | 23 | 5 | 9 | 1 | 2 | 3 | 17 | 2 | 6 |
| HEADING | 118 | 38 | 38 | 9 | 16 | 4 | 31 | 5 | 5 |
| BODY | 138 | 6 | 6 | 0 | 3 | 1 | 16 | 2 | 6 |

Reading: on dev (mostly non-Science books) icons are common on HEADINGS (circled roman numerals are blue icons) and appear on questions in three colours — the KNTT hand = activity convention is a Science-family convention, and dev has only 5 activity blocks. The rules were therefore written from the convention, not fitted:

- **R1** pipeline question | instruction | body **+ orange icon** (own or inherited) → ACTIVITY
- **R2** pipeline body | instruction **+ blue icon** → QUESTION
- **R3** pipeline question with **no icon, not in a tinted box, not ending in "?"** → BODY
- **v1** = R1 + R2 + R3, frozen before held-out scoring. **v2** = R3 removed after its dev result (2 hits / 22 misses) — the held-out numbers for v2 are a *second look*. **v3** = v2 + "an inherited icon never overrides the instruction lexicon", written after the Bài 17 result — Bài 17's v3 numbers are *in-sample*.

## 3. Results — six roles, precision / recall without → with the signal

### Held-out (16 pages; the only clean test)

| role | without | v1 (frozen) | v2 (second look) | v3 (post-hoc) | gold n |
|---|---|---|---|---|---|
| **QUESTION** | 0.833 / 0.938 | 0.933 / 0.875 | **0.938 / 0.938** | 0.938 / 0.938 | 16 |
| **ANSWER** | 0.800 / 0.400 | 0.800 / 0.400 | 0.800 / 0.400 | 0.800 / 0.400 | 10 |
| **ACTIVITY** | 0.000 / 0.000 | 0.333 / 0.333 | 0.333 / 0.333 | 0.333 / 0.333 | 6 |
| **INSTRUCTION** | 1.000 / 0.500 | 1.000 / 0.500 | 1.000 / 0.500 | 1.000 / 0.500 | 6 |
| **OBJECTIVE** | 0.706 / 0.923 | 0.706 / 0.923 | 0.706 / 0.923 | 0.706 / 0.923 | 13 |
| **SIDEBAR** | 0.958 / 0.852 | 0.958 / 0.852 | 0.958 / 0.852 | 0.958 / 0.852 | 27 |

Rules fired on held-out: R1 2 hits / 1 miss; R2 and R3 never fired (v1: R3 1 miss).

### Science (23 pages; overlaps held-out)

| role | without | v1 | v2 / v3 | gold n |
|---|---|---|---|---|
| **QUESTION** | 0.889 / 0.870 | 0.912 / 0.674 | **0.929 / 0.848** | 46 |
| **ACTIVITY** | 0.000 / 0.000 | 0.286 / 0.200 | 0.286 / 0.200 | 10 |
| **INSTRUCTION** | 0.500 / 0.500 | 0.500 / 0.500 | 0.500 / 0.500 | 6 |
| **OBJECTIVE** | 0.696 / 0.941 | same | same | 17 |
| **SIDEBAR** | 0.964 / 0.818 | same | same | 33 |
| ANSWER | 0.800 / 0.400 | same | same | 10 |

### Dev (38 pages; the tuning set — shown for completeness)

QUESTION 0.893/0.750 → v1 0.850/0.510 → v2/v3 0.845/0.710; ACTIVITY 0/0 → 0.091/0.200 (R1: 1 hit / 7 misses — orange icons on non-Science pages are not hand icons); R2 2 hits / 4 misses; other roles unchanged.

### KHTN 6 Bài 17 «Tách chất khỏi hỗn hợp» (Founder addendum; pdf 61–64, 73 gold blocks, all 73 matched)

| role | without | v1 / v2 | v3 (in-sample) | gold n |
|---|---|---|---|---|
| **QUESTION** | 0.727 / 0.889 | 0.857 / 0.667 | 0.857 / 0.667 | 9 |
| **ANSWER** | — | — | — | 0 |
| **ACTIVITY** | — / 0.000 | 0.167 / 0.400 | 0.222 / 0.400 | 5 |
| **INSTRUCTION** | 1.000 / 0.333 | — / 0.000 | 1.000 / 0.333 | 9 |
| **OBJECTIVE** | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 | 2 |
| **SIDEBAR** | 0.800 / 0.444 | 0.800 / 0.444 | 0.800 / 0.444 | 9 |
| HEADING | 0.688 / 1.000 | same | same | 11 |
| BODY | 0.412 / 0.875 | 0.583 / 0.875 | same | 8 |
| CAPTION | 1.000 / 0.556 | same | same | 9 |

Bài 17 gold distribution: question 9 · activity 5 · instruction 9 · objective 2 · sidebar 9 · heading 11 · body 8 · caption 9 · figure_label 7 · page_number 4. Without the signal the pipeline's 11 "questions" on these pages include the hand-icon opening activity (p61), the "Quan sát và trả lời câu hỏi" lead-in and a rhetorical body lead-in ending in "?" (p63): **precision 0.727 on the showcase lesson, i.e. 3 of 11 asked "questions" are not questions.** With v3: 2 of the 5 activities found (the two box titles with their own icon), 7 R1 misses = the instruction/step lines inside the two hand-icon boxes that the pipeline labels body (5) plus box titles read as headings (3 ACTIVITY→HEADING).

## 4. What the measurement says

1. **The signal exists and is real, but it marks the box, not the line.** Every R1 hit is a block with its *own* icon (KH5 p42/p43, Vật lí 10 p89, Bài 17 box titles). Activity *contents* (steps, closing tasks, numbered questions inside a hand-icon box) only get the icon by inheritance, and inheritance through a pale tint is unreliable: KHTN 7 p32's numbered questions sit in a box with `tint_share` 0.18–0.28 (below the 0.3 bar), and KHTN 9 p38/p46's activity contents inherit nothing because the box title was not the matched block. A proper **box-boundary detector** (rectangle of tinted background from the page image, blocks assigned by containment) is the missing primitive — the same box_boundary guard TC-19 #4 asked for, used positively.
2. **QUESTION precision moves 0.83 → 0.94 on held-out on n = 16 predictions** — one false question fewer. At that n the 95 % lower bound is ≈ 0.72; the gate cannot be *certified* on this gold whatever the point estimate. TC-19 #9's ≥ 300 science gold questions remain the precondition.
3. **R3 is wrong as written.** "Directive sentence, no icon, no tint, no ?" removes 22 real questions on dev and 8 on science: bare numbered questions under a "Câu hỏi" stage label carry neither icon nor tint. Dropped in v2 — a legitimate dev-set correction, but every later number is a second look at held-out.
4. **The remaining false questions are not icon-shaped:** worked-example lead-ins and question-form headings (Toán/Vật lí), the rhetorical "…làm thế nào…?" lead-in inside body prose (Bài 17 p63), "Quan sát và trả lời câu hỏi:" lead-ins. Typography (bold/italic) and box structure are the signals; colour alone does not carry them.
5. **ACTIVITY is now detectable (0 → 0.22–0.33) but nowhere near the ≥ 0.8 the audit's G4 asks for.** The dev set has 5 activity blocks and held-out 6: the gold itself cannot support an ACTIVITY claim either way.

## 5. What would be needed (not done here, not decided)

- A deterministic **box detector** on the page image (tinted/outlined rectangles) feeding both the Role Layer (activity/question/sidebar by box + icon) and the existing box_boundary guard; then re-measure on a **fresh** held-out set — v2/v3 have already consumed this one.
- **≥ 300 science gold QUESTION blocks and ≥ 50 ACTIVITY blocks**, two annotators, before any 0.95 claim; the Bài 17 gold written here (single annotator, anchors only) is a start, not that set.
- Until then: Short-Answer stays DEFERRED; no auto-labelled question is graded; the Role Layer keeps its blocker role (objectives, sidebars, answer keys, figure-dependent prompts), which this experiment did not change (OBJECTIVE / SIDEBAR / ANSWER rows identical with and without the signal).

## 6. Reproduce

```
env TC_ROOT=<main checkout> python3 tool/corpus/role_signal_experiment.py --rules v1 \
  --gold-dir poc-out/b-lane/tc-gold-branch/tool/corpus/tc_gold --bai17-gold tool/corpus/tc_gold_bai17
# --rules v2 | v3 for the other configurations; results-<rules>.md/json + features.jsonl under poc-out/b-lane/role-signal/
```
