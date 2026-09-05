# Pipeline requests from the legacy reprocess (Lane D → Lane A-pipeline)

Round 4, batch 1. Every item below is a **failure mechanism observed on a real page**, with the block ids to
reproduce it and the file Lane D suspects. Lane D does not edit pipeline code — these are requests, and each
one is written so it can be turned into a test.

**Status as of Lane A-pipeline's shipped build (PR #77 @ `cb60cde`).** Batch 1 was re-run on that build and
the result measured, so each item below is closed or left open **by measurement**, not by reading the diff.

| # | request | status on PR #77 |
|---|---|---|
| R1 | back cover / imprint attached to the last lesson | **PARTLY FIXED** — back cover unattached; imprint page still served as Bài 73 body |
| R2 | number guard misses fraction fragments | **OPEN** — `b) 10 +` still served |
| R3 | tone guard misses all-caps headings | **OPEN** — the Toán 5 Bài 6 lesson title still served with its terms corrupted |
| R4 | dropped circled numerals disable the role layer | **IMPROVED** — role 0.216 → 0.125; the specific rows are withheld rather than re-roled |
| R5 | caption assembly (chip split, first-line cut) | **OPEN** — both blocks unchanged |
| R6 | a block's bbox does not cover its own text | **not re-measured** — needs the invariant test, see below |
| R7 | lines rotated within a Ghi nhớ block | **OPEN** — still served rotated |
| **R7b** | `page_feature:color_heavy` is a page-level veto | **FIXED** — 4 of the 6 colour-vetoed regions are served again, including the Bài 25 poem and the Bài 1 passage |
| **R7c** | verse lines joined into prose *(new — uncovered by the R7b fix)* | **OPEN** |
| R8 | block ids carried the wrong pipeline label | **CLOSED** |

## ROUND 5 UPDATE (2026-09-06) — re-measured on `tc2-p2r`, and four new requests

Batch 1 was re-run from the original source on the **current** build — PR #77's *final* head including
its 14 post-review fixes, which is **not** the `cb60cde` the table above measures — and batch 2 added six
lessons in five new failure classes. Status below is by measurement, from
`tool/corpus/legacy/regression.py` (deterministic probes) and blind page-render audits.

| # | status on `tc2-p2r` | evidence |
|---|---|---|
| **R1** | **STILL OPEN, and it GENERALISES** | pdf p121 still attached to Bài 73 with 8 imprint blocks served. New: **Toán 4 tập một Bài 37** — a book never touched before — serves its colophon page (pdf p133, no printed page number) as trusted `body`/`heading`, including `Mã số: G1HH4T001h26` and the publisher's CEO. Round 4's back-cover fix moved one page of one book; the `continuation` mechanism is intact. `regression.py tail-scan` reproduces it on any batch. |
| **R2** | **STILL OPEN** | `05-sgk-toan-5-tap-mot:p022:*:002` = `10`, `:016` = `b) 10 +`, unchanged |
| **R3** | **STILL OPEN** | `…:p021:*:001` = `CỘNG, TRỪ HẠI PHẬN SỐ KHÁC MẪU SỐ`, role `heading`, confidence 0.88, unchanged |
| **R5** | **OPEN, and now measurable** | a 20-block caption quota sample across four lessons: display 5/18 = 0.278, and **10 of 19 captions are DETACHED from their figure**. Seven of those are bare `Hình N` labels where **the page prints no caption text at all** — a text-only pipeline serving a figure number as content. Only one (`Hình 5.4`) is a proven chip/caption split. |
| **R7c** | **PARTLY FIXED** | `1960d85` added a `line_structure` withhold and 7 regions now use it — but 3 long single-run body blocks are still served, and the blind restore audit judged one of them (a four-line stanza of the Bài 25 poem) served as **one prose run**. Withholding some verse is not withholding verse. |

### R9 (new · P0) — `chem_guard` blocks a Physics section heading
`09-sgk-khoa-hoc-tu-nhien-9` Bài 5: the section title `II – Định luật khúc xạ ánh sáng` is withheld by
`chem_guard`. A chemistry guard firing on a physics heading is a pure over-withhold: the block carries no
formula, no unit and no chemical name. **Request:** the chemistry guard should require a chemical token,
not merely a science book; and a `heading`-role block with no numeric or symbolic content should not be
reachable by a formula guard at all.

### R10 (new · P0) — withholding one member of a structure serves a MUTILATED structure
The Founder's evaluation-set defect 8, located exactly: **Toán 4 tập một Bài 37, pdf p130** serves options
`A. 1 số chẵn`, `B. 2 số chẵn`, `C. 3 số chẵn` and withholds the fourth (`…:p130:*:014`, role `option`,
reason `agree_order`). The served question is **wrong**, not smaller.

Measured independently of the pipeline by `tool/corpus/legacy/orphan.py`:
**9 mutilated structures in batch 2** (5 split enumerated runs, 3 split caption sets, 1 split option group)
and **13 in the batch-1 holdout**; **12/139 = 0.086** of withheld regions orphan a sibling in batch 2,
**12/126 = 0.095** in the holdout — the rate generalises.

**Request:** a group-aware disposition — withhold the whole group or restore the whole group, never serve a
partial one — for OPTION ⊂ QUESTION, caption ↔ figure, table rows and enumerated steps. Lane D's detector
is deliberately independent, so it can keep scoring the fix from outside.

*Note for whoever builds the grouping:* the TSL's `order` field is numbered **separately** for the served
and withheld lists. On the page above the served options are `order` 11, 12, 13 and the withheld fourth is
`order` 17. Group on the page-level index in the block id instead — Lane D's first implementation used
`order` and walked straight past this defect.

### R11 (new · P1) — over-withholding is now the larger pool, and its shape is «siblings»
**19 of 30 reviewed withheld regions in batch 2 (0.633) are over-withheld**, up from 12/30 (0.400) in
round 4. The pattern is consistently a sibling of a served block: an objective bullet refused while its
sibling is served, a `Tiến hành` step refused while its `Chuẩn bị` is served, `26 000 + 9 015 × 6` refused
while `78 060 : (10 − 7) + 300 045` is served. Several plain paragraphs and section titles are refused on
`agree_tones` alone. **Request:** treat a guard that fires on one member of a homogeneous run and not on
its neighbours as evidence about the guard, not about the block.

### R12 (new · P1) — a restored region needs a fresh verdict, and the old one predicts it
Of 6 regions this build serves again after `tc2-p1` withheld them, **RESTORE PRECISION is 3/6 = 0.500**.
The split is not random: of the 4 the earlier audit had called **over-withheld**, 3 came back correct; of
the 2 it had called **safe refusals, both came back wrong** (a stranded `G:` marker and the bare label
`Tiến hành:` served as an `instruction` with its steps left outside the box). **Request:** when a guard is
loosened, prefer the regions a review called over-withheld; a region a review called a safe refusal should
need a positive signal before it is served again.

---

Overall on batch 1: derived false trust 0.365 → 0.297, attachment 0.108 → 0.034, role 0.216 → 0.125, at a
coverage cost of 287 → 221 served blocks. Numbers and denominators in `ROUND4-BATCH-1-REPORT.md` §7.

Evidence: `poc-out/round4/legacy/batch-1/audit/` (annotated rows + contact sheets) and
`poc-out/round4/legacy/batch-1-rerun-tc2-p2-preview/delta/delta.md` (row-level re-run outcome).
Reproduce a run with:

```
python3 tool/corpus/legacy/run_batch.py --batch tool/corpus/legacy/batches/batch-1.json \
    --pipeline <id> --version <suffix> [--corpus <other checkout> --corpus-ref <ref>]
python3 tool/corpus/legacy/rerun.py --rerun-dir poc-out/round4/legacy/batch-1-<suffix>
```

---

## R1 — a book's imprint / colophon page is still served as the last lesson · **OPEN** · P0

The last lesson of a book collects the book's tail. On `tc2-p1` this was 8 of 8 attachment-WRONG audited rows;
`tc2-p2` fixed the back cover and left the imprint page.

| page | `tc2-p1` | `tc2-p2` |
|---|---|---|
| `04-sgk-toan-4-tap-hai` p122 (back cover: publisher's book list) | `kind=page`, `lesson=73` | `kind=back_cover`, `lesson=None` ✅ |
| `04-sgk-toan-4-tap-hai` p121 (imprint: “Biên tập…”, “Trình bày bìa…”, “Cơ sở in:”) | `kind=page`, `lesson=73`, `method=continuation`, conf 0.95 | **unchanged — still `lesson=73`** |

Blocks still served as trusted `body`/`activity` of Bài 73 on `tc2-p2`:
`04-sgk-toan-4-tap-hai:p121:*:005`, `:007`, `:009`, `:019`.

**Suspected:** `tool/corpus/tc2_attach.py` → `page_info()`. It already computes `_tail` (last 12 % of the book)
and recognises back matter and covers; a colophon has neither a “Tài liệu tham khảo”-style marker nor cover
marks, so it falls through to `kind='page'` and the `continuation` rule hands it to the current lesson.

**Request:** in the book tail, treat publishing-credit pages as non-lesson — e.g. a page whose lines are
dominated by imprint phrases (“Chịu trách nhiệm xuất bản”, “Biên tập”, “Trình bày bìa”, “Cơ sở in”, “In … bản”,
an ISBN, a price) → `kind='back_matter'`. A cheap independent guard: `continuation` should not carry a lesson
past the last page that has a printed page number belonging to the lesson's TOC range.

---

## R2 — the number guard misses fraction *fragments* · **OPEN** · P0

Two blocks are still served as trusted `body` on `tc2-p2` after being judged teaching-critical WRONG:

| block | printed | served |
|---|---|---|
| `05-sgk-toan-5-tap-mot:p022:*:002` | the `10` of `3/10` in a stacked fraction | `10` — a lone denominator as a content block |
| `05-sgk-toan-5-tap-mot:p022:*:016` | `b) 3/10 + 5/21` | `b) 10 +` — both fractions destroyed, operator kept |

**Suspected:** `tool/corpus/tc2_sdm.py`, the math / number guard. `agree_numbers` does fire on this page
(1 block), so the guard exists and is reachable; these two blocks slip through because a *single* number and a
*trailing operator* are not the digit-run pattern the guard looks for.

**Request:** withhold, never guess, when (a) a block's entire text is a bare integer that sits inside a
stacked-fraction region, or (b) a block ends with a dangling arithmetic operator, or (c) a block's text has
fewer numeric tokens than the number of stacked-fraction regions its bbox overlaps. All three are
withhold-only rules; none of them repairs anything.

---

## R3 — the tone guard misses all-caps headings, including a lesson title · **OPEN** · P0

`05-sgk-toan-5-tap-mot:p021:*:001`, role `heading`, confidence 0.88 — the lesson title is served with tone
slips that turn the key mathematical terms into other words (`HAI PHÂN` → `HẠI PHẬN`). It is served
**identically on `tc2-p2`** even though `agree_tones` withheld 2 other blocks in the same lesson.

**Suspected:** `tool/corpus/tc2_sdm.py`, the tone-mark agreement guard (commit `9d9816d`). Either all-caps
text is normalised before comparison, or both extractors agree on the same wrong tones and agreement-based
guards cannot see it.

**Request:** the guard should be able to fire on a block where the extractors *agree*, using a Vietnamese
non-word signal rather than only cross-extractor disagreement — and it matters most on headings, which are
short, high-confidence and are read as the name of the thing being taught. Withhold, never repair.

---

## R4 — exercise instructions are served as `body` because OCR drops the circled numeral · **OPEN** · P1

Role was the one class where the new pipeline is not better than the old product (0.164 → 0.216 on
`tc2-p1`). Nine of the 16 role-WRONG rows are exercise instructions served as `body`:

`04-sgk-toan-4-tap-hai:p081:*:022`, `04-sgk-toan-4-tap-hai:p082:*:008`,
`05-sgk-toan-5-tap-mot:p022:*:006`, `05-sgk-toan-5-tap-mot:p023:*:000`.

Three audited rows record the cause directly: the **circled exercise numeral is dropped** — the served text is
`Tính.` where the page shows a circled `1` then `Tính.`. The role layer has no “this is exercise n” signal
because the enumerator never reaches it.

**Suspected:** OCR/candidate layer (`tc2_run.py`) losing the glyph, then `tc2_sdm.py`'s role layer having
nothing to key on. Note the numeral survives in some blocks (`2 Viết phép tính…`), so it is not systematic.

**Request:** recover the enumerator before the role decision — take it from whichever raw candidate kept it, or
detect the small circled-digit region left of the first baseline (it is already a figure-like region on the
page). If the enumerator cannot be recovered, the role should not be asserted as `body` at high confidence.

---

## R5 — caption assembly: captions split from their number, and cut after the first line · **OPEN** · P1

Role-proportional sampling drew only 2 caption rows of 74, so a **quota sample of the `caption` role** was
drawn separately (seed 20260907; all 8 caption blocks of KHTN 6 Bài 11). Within that class, **2 of 8 are
display-WRONG (0.250 [0.071, 0.591])**, by two different mechanisms:

| block | printed | served |
|---|---|---|
| `06-sgk-khoa-hoc-tu-nhien-6:p037:*:016` | `Hình 11.1  Oxygen có ở khắp nơi trên Trái Đất` (one caption line) | `Hình 11.1` **alone** — the caption text after the chip is a separate block, so neither block carries the whole caption |
| `06-sgk-khoa-hoc-tu-nhien-6:p039:*:020` | a two-line caption under the experiment figure | `Hình 11.5 Thí nghiệm xác định` — **cut after the first line** |

**Suspected:** caption assembly in `tool/corpus/tc2_sdm.py` (you added `tool/tests/test_tc2_captions.py`).
The first case looks like the tinted “Hình N.N” chip being segmented as its own region; the second like a
missing wrap-continuation.

**Request:** a caption block must contain the figure number **and** every line of the caption, or be withheld.
A caption that names a figure it does not describe — or describes a figure it does not name — is a false claim
about what the child is looking at.

**And one the audit cannot score at all:** 5 of those 8 caption blocks are sub-panel labels (`a) …`, `b) …`,
`c) …`) served as standalone captions **with no reference to the figure they label** —
`…:p037:*:012`, `…:p037:*:015`, `…:p038:*:004`, `…:p038:*:006`, `…:p040:*:013`, `…:p040:*:017`.
Every one is character-perfect, so every fidelity field says OK. “a) Rác thải” with no figure attached teaches
nothing. **Request:** a caption/sub-label block should carry the id of the figure region it belongs to (the SDM
already computes figure regions), so a consumer can refuse to serve a label without its figure.

---

## R6 — a block's bbox does not cover the text it serves · **OPEN** · P1

`05-sgk-tieng-viet-5-tap-hai:p013:*:018`: two side-by-side hint chips are concatenated into one block while the
bbox covers only the first chip. Every downstream consumer that crops from the bbox — the Reader, evidence
crops, this audit's own contact sheets — will show a crop that does not contain the served text.

**Request:** an invariant with a test — *a trusted block's bbox contains every source line it serves*. When it
does not, either split the block or withhold it. This is cheap to assert in `tc2_tsl.py` at emit time and
would have caught the row mechanically instead of by eye.

---

## R7 — lines rotated *within* a block (a Ghi nhớ rule read out of order) · **NEW on `tc2-p2`** · P1

`05-sgk-tieng-viet-5-tap-mot:p125:tc2-p2:004` is one of only 3 blocks `tc2-p2` serves that `tc2-p1` did not.
It is a Ghi nhớ rule whose two lines are served second-line-first, plus a tone slip (`đến` → `đên`).

**Suspected:** the LIS re-sequencing (commit `7140c35`) orders *blocks*; this is line order *inside* a block.

**Request:** apply the same order-agreement check to the lines within a block, and withhold when the two
candidates disagree on line order. A rule box that starts mid-sentence is a teaching-critical failure even when
every character is right.

---

## R7b — `page_feature:color_heavy` is a page-level veto that refuses the lesson's own reading · **OPEN** · P0

All 30 withheld regions of the batch were reviewed. Every refusal is **safe** — but **12 of 30 = 0.400
[0.245, 0.578] are OVER-withheld**: clean text refused for a reason that did not apply to it. The largest
single mechanism is a page-level flag:

| rows | reason | what it refused |
|---|---|---|
| 5 | `page_feature:color_heavy` | stanzas of the Bài 25 poem and a paragraph of the Bài 1 reading passage — **the text the lesson is about**, single-column, clean, on a page with a colourful banner |
| 4 | `agree_order` on short labels | a section title (`CÂU ĐƠN VÀ CÂU GHÉP`), a rule box, plain instructions |
| 3 | `agree_text` on plain prose | a `Chuẩn bị:` sentence, a sidebar paragraph, a plain question |

Examples: `n20260906-0063`, `-0065` (Bài 25 poem stanzas), `-0081`, `-0082` (Bài 1 opening task and passage
paragraph), `-0062` (plain instruction). Full notes in
`poc-out/round4/legacy/batch-1/audit/annotated-new-20260906.jsonl` (rows with `servedAsTrusted = false`).

This is also visible from the other side in the `tc2-p2` re-run: **23 % of the rows previously judged OK are no
longer served.**

**Request:** `color_heavy` and `diagram` are properties of a *region*, not of a page. A page-level flag should
raise the bar for blocks that overlap the colourful or diagrammatic regions, not veto every block on the page.
`agree_order` on a block of one or two lines has no order to disagree about and should not fire at all. Neither
change weakens fail-closed: both replace a blanket refusal with a targeted one.

**And a standing number to report:** per guard, the share of what it withholds that was actually fine. Batch 1
gives a first reading — `page_feature:color_heavy` is the least precise guard measured so far.

---

## R7c — verse lines joined into a prose run · **NEW, uncovered by the R7b fix** · P1

The block-level colour change did its job: the Bài 25 poem comes back. But it comes back as prose.

| block | printed | served |
|---|---|---|
| `05-sgk-tieng-viet-5-tap-mot:p123:tc2-p2:*` (2 blocks) | five and four **verse lines**, one per printed line | all lines joined into a single run with no line breaks |

Every character is right and every line is in printed order, so all six audit fidelity fields except display
say OK — and the poem of a poetry lesson is served as a paragraph. On `tc2-p1` this was invisible because the
colour veto withheld the whole stanza; **the fix is what made the defect observable**, which is the good case,
not the bad one.

**Request:** keep the line structure of a block whose lines are short, left-aligned and vertically regular
(a stanza), or mark the block `verse` so a consumer can render its lines. Joining is the wrong default for any
block inside a reading lesson's poem region. Blocks affected are listed in
`poc-out/round4/legacy/batch-1-rerun-tc2-p2/audit/annotated-p2-new-claims.jsonl` (`p2new-0002`, `p2new-0003`).

**Also seen on the same recovered content:** `p2new-0008`, a passage paragraph cut mid-sentence at
«… kéo về phá», and `p2new-0000`, a warm-up task served as `body` rather than an instruction.

---

## R8 — block ids carried the wrong pipeline label · **CLOSED, confirmed by re-run**

On the base build, `tc2_sdm.py` built ids from the module constant (`PIPELINE_ID = 'tc2-p1'`), so a run under
`--pipeline legacy-b1` emitted ids reading `…:tc2-p1:…` — two different builds' blocks were
indistinguishable by id. Your line 844 now uses the `pipeline` argument, and the re-run's ids read
`…:tc2-p2:…`. Confirmed on real output; no action needed.

---

## R9 — measurement requests (not code changes)

1. **Guard precision.** On batch 1, `tc2-p2` withholds 74 blocks that `tc2-p1` served. Read against the audit,
   roughly 48 of those were false trust and roughly 26 were correct content (point estimates, wide CIs). Guards
   are doing almost all the improvement — the interesting number for each new guard is not how often it fires
   but **what share of what it withholds was actually fine**. `withheld_by_reason` in the TSL stats already
   makes this computable per reason; a per-guard precision line in your scorer would make it standing.
2. **No served text changed.** Across all 74 audited rows, `tc2-p2` changed **zero** texts — it only withheld.
   If a later build starts repairing text, tell Lane D: the re-run delta's verdict-transfer rule (identical
   text, same region) silently stops applying and the batch needs re-annotation.
3. **Caption sampling is now available.** `audit.py sample-kind --kinds caption` draws a quota sample of one
   role (`poc-out/round4/legacy/batch-1/audit/kind-sample-caption-20260907.jsonl`); it is what produced R5's
   numbers. When your caption work lands, Lane D re-draws the same quota on the new build and reports the
   within-class delta. Rates from it are within-class only and are never pooled with the batch rates.

---

## Contact

Lane D owns `tool/corpus/legacy/**`, `poc-out/round4/legacy/`, `docs/research/legacy-reprocess/**` and calls
the pipeline as-is. When your PR is green, Lane D re-runs batch 1 on the merged build and republishes the
delta — no coordination needed beyond telling Lane D the pipeline id to run.
