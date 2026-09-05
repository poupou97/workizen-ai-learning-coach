# Pipeline requests from the legacy reprocess (Lane D → Lane A-pipeline)

Round 4, batch 1. Every item below is a **failure mechanism observed on a real page**, with the block ids to
reproduce it and the file Lane D suspects. Lane D does not edit pipeline code — these are requests, and each
one is written so it can be turned into a test.

Where a request has already been addressed on `lane-a/round4-pipeline-failure-classes` @ `206a103`, that is
stated: batch 1 was re-run on that build (`tc2-p2`) and the result measured, so several of these are *closed
by measurement* rather than by reading the diff.

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

## R5 — a caption is truncated to its first line · **OPEN** · P1

`06-sgk-khoa-hoc-tu-nhien-6:p039:*:020`, role `caption`, confidence 0.92, served as
`Hình 11.5 Thí nghiệm xác định` — the second line of the caption is missing.

**Suspected:** caption assembly in `tool/corpus/tc2_sdm.py` (you added `tool/tests/test_tc2_captions.py` —
this looks like a missing continuation case: a caption whose text wraps below the figure).

**Request:** a caption block must contain every line of the caption or be withheld; a truncated caption is a
false claim about what a figure shows. This is also the class batch 1 could **not** measure — only 2 of 74
audited NEW rows were caption-kind — so a fix here needs its own sampling, see R9.

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
3. **Caption sampling.** Batch 2 will sample caption-kind blocks by quota rather than proportionally, so R5 can
   be measured rather than asserted. If your caption work lands first, say so and Lane D will size the sample
   to it.

---

## Contact

Lane D owns `tool/corpus/legacy/**`, `poc-out/round4/legacy/`, `docs/research/legacy-reprocess/**` and calls
the pipeline as-is. When your PR is green, Lane D re-runs batch 1 on the merged build and republishes the
delta — no coordination needed beyond telling Lane D the pipeline id to run.
