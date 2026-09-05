# THIRD SIGNAL LAYER — what each signal is, and what each one actually contributed

Round 5 · Lane A1 · 2026-09-06 · code `tool/corpus/repair/signals/**`, `tool/corpus/repair/vi/**`
· measured by `tool/corpus/repair/run_gold.py` on the 54 gold pages / 643 learning blocks
· **MEASUREMENT. No production trust threshold is set here and no pipeline guard was loosened.**

---

## 0. The structural finding that reframes round 4

Round 4 falsified **A26** — «two OCR stacks agreeing means the text is verbatim» — empirically. Round 5 can
say *why*, and it is not subtle:

| stack | layout | **text recogniser** |
|---|---|---|
| `docling-ocrmac` (primary) | Docling 2.126 layout model | **Apple Vision** via `ocrmac`, `recognition='accurate'`, `lang=['vi-VT','en-US']`, `images_scale=2.0` |
| `current-xycut` (verifier) | WAL-206 XY-cut | **Apple Vision**, `poc-out/graph/ocr-body`, `extraction_method: apple-vision-accurate-vi` |

**The two "independent" stacks share their OCR engine.** They differ in render scale and in how they group
lines into blocks — nothing else. So `agree_text` and `agree_tones` were never text-agreement gates; they are
**layout**-agreement gates that happen to compare strings. Two readings of the same ink by the same
recogniser cannot be independent evidence about that ink, which is exactly what round 4 measured
(«Tiền hành», «phẫu», «Em cô thể» pass every agreement gate) and exactly why a *third* signal is needed
rather than a better comparison of the two.

Recorded in code on every observation (`repair/context.py: SOURCE_STACKS`), so a reader of the ledger sees
it rather than having to be told.

The same fact bounds signal **F**: a third stack is only worth adding if it is a **different recogniser**.
Adding a third consumer of Apple Vision would add cost and no independence. See §6.

---

## 1. The layers

| layer | signal id | what it is | data it needs |
|---|---|---|---|
| **A** | `A.vi_syllable` | deterministic Vietnamese phonotactics: at most one tone mark per syllable, the tone sits on a vowel, the onset is one of the 28 initial spellings | **none** |
| **A** | `A.vi_lexicon` | is this form attested on ≥ 8 pages in ≥ 4 books, **with the book under repair subtracted** | corpus table |
| **A** | `A.vi_collocation` | does this form occur next to *these* neighbours elsewhere in the corpus | corpus table |
| **A** | `A.vi_sweep` | whole-block: is **every** Vietnamese word in the proposed text legal and attested | corpus table |
| **B** | `B.verifier_reading` | the proposal is what the *other* stack read | the two observations |
| **B** | `B.closed_vocabulary` | the block's role makes its text a closed set (stage labels, «Hình N») | none |
| **B** | `B.ocr_confidence` | Apple Vision's own line confidence | OCR lines |
| **C** | `C.numeric` | a text repair may not move a digit or an operator — **Lane A2's slot**, with a fail-closed default | none |
| **D** | `D.in_block` | the same block prints this word this way, where both stacks agree | the block |
| **D** | `D.in_page` | the same **page** prints it this way in a block the pipeline trusts, and never prints the observed reading | the page |
| **D** | `D.in_document` | the rest of the **book** prints this word, and this two-word sequence, elsewhere | the book's OCR |
| **D** | `D.toc_title` | a lesson title against the TOC's reading of the same title | the TOC |
| **E** | review queue | **an output**, never a verdict — 273 rows, ranked | — |
| **F** | — | a third OCR stack — **not added**; §6 |

Layer A subtracts the book under repair; layer D *is* the book under repair. That is what makes «two
independent layers agree» mean something rather than being the same evidence counted twice.

## 2. The lexicon — provenance and licence

**Nothing is vendored.** Two tables, both derived from data this project already owns
(`tool/corpus/repair/vi/lexicon_build.py`, which records this in the JSON itself):

| table | source | licence | size |
|---|---|---|---|
| `corpus` | this project's own Apple Vision OCR of the 531-book K-12 set — **62,729 pages** | internal research data; **counts of word forms only**, no sentences, never distributed | 41,383 unigrams (page-support ≥ 2) · 747,282 bigrams |
| `clean` | the human-typed Vietnamese in this repository (`docs/**/*.md`, `lib/**`, `test/**`, `tool/**`) | our own authored files | 12,978 unigrams · 241,987 bigrams, 625 files |

The `corpus` table is OCR-derived and therefore contains OCR errors. That objection is answered by
**support**, not by faith — every consumer asks for page-support and book-support, never a raw count, and the
book under repair is always subtracted. It is also answered by *measurement*, because the table is fooled in
a way worth naming:

> **«thủỷ» is attested on 743 pages of 160 books** — more than the correct «thủy» (276 / 96). Apple Vision
> produces the double-hook slip so consistently across the whole SGK series that frequency alone prefers it.
> Only `A.vi_syllable` — pure phonology, no data — catches it, because two tone marks in one syllable is
> illegal Vietnamese whatever a corpus says.

That is the single strongest argument for keeping a deterministic sub-signal beside a statistical one.

## 3. Per-signal contribution — by ablation, not by assertion

«Contribution» is answered the only honest way: for every validated repair, remove one layer's signals and
re-run the **real** validator. `ablate_lost` = the repair would not have validated without that layer.

**54 gold pages, `tc2-p3-lin` (67 candidates, 43 validated):**

| layer | consulted | supports | objects | abstains | validated with | **necessary (`ablate_lost`)** | right | wrong |
|---|---|---|---|---|---|---|---|---|
| **A** | 67 | 62 | 5 | 0 | 43 | **41 / 43** | 23 | 5 |
| **B** | 67 | 38 | 0 | 29 | 30 | **28 / 43** | 17 | 3 |
| **C** | 35 | 0 | 0 | 35 | 0 | **0** | 0 | 0 |
| **D** | 35 | 26 | 0 | 9 | 15 | **13 / 16** | 7 | 2 |

Per sub-signal (`signal_contribution_by_signal` in every run's `repair-report.json`), on the
Vietnamese-only variant: `A.vi_lexicon` and `A.vi_syllable` support 33/33 candidates, `A.vi_collocation`
26/33 (it is the discriminating one and abstains when the corpus has nothing to say), `D.in_document` 26/33,
`D.in_page` 4/37, `D.in_block` 1/33, `B.closed_vocabulary` 0/46, `B.ocr_confidence` 0/29,
`C.numeric` 0/35.

**Read honestly:**
- **A and D are the engine.** Neither alone is enough by policy (a text change needs a layer outside A), and
  ablation confirms it: removing A loses 41 of 43 repairs, removing D loses 13 of 16 in the Vietnamese lane.
- **B earns its place only through `B.verifier_reading`** and, in the linearisation lane, through the
  page-stream check. `B.closed_vocabulary` fired **0 times in 46 opportunities** on these pages and
  `B.ocr_confidence` **0 in 29** — Apple Vision reports 1.0 on the display-font blocks it gets wrong, so its
  confidence is not a fidelity signal at all. Both are kept because they are cheap and deterministic, but
  neither is doing work today and this document says so rather than implying a four-layer system is
  four-layers useful.
- **C abstained 35/35** — correctly. Its default provider only guarantees that no repair moved a digit;
  positive numeric evidence is Lane A2's to add (`repair/signals/numeric.register_provider`).

## 4. Detection thresholds — and what they are not

`repair/repairers/vi_text.py: Config` holds every number: `min_uni_pages=8`, `min_uni_books=4`,
`ctx_min=3`, `ctx_ratio=4.0`, `agree_ctx_min=20`, `agree_ratio=25.0`, `agree_obs_max=2`,
`max_issues_per_block=6`. All were **calibrated on the 38-page dev split**; the 16 held-out pages informed
none of them (one exception, disclosed in `VIETNAMESE-REPAIR-RESULT.md` §5).

These are **arbitration thresholds inside the repair framework**. None of them is a production trust
threshold, none of them relaxes a pipeline guard, and none of them decides whether the corpus may teach a
child. That gate still does not exist and this lane did not create one.

## 5. The bar is deliberately asymmetric

| the block is… | the risk of getting it wrong | the bar |
|---|---|---|
| **withheld** (the stacks disagree on a token) | a wrong *restore* — a block nobody was reading becomes readable and wrong | layer A decisive (ratio 4, ≥ 3 pages) **plus one more layer** |
| **served** (both stacks agree, and are wrong) | a wrong *correction* — a right word becomes a different wrong word | the observed collocation must be essentially unattested **and** an alternative must dominate by 25×, **or** the observed reading must be illegal / never attested, **and** the document, the page or the block must agree |
| a **proper noun** | a person's or a place's name rewritten | corpus frequency **may never** carry it: the document, page or block must print the proposed spelling, or the observed one must be illegal |

The proper-noun rule exists because Lane C measured the failure it prevents: a corpus tone-majority signal
proposed rewriting **«Đăng Khoa» → «Đặng Khoa»**. A name is not a dictionary word and «commoner in the
corpus» says nothing about which person a page is naming. Its false-correction rate is reported separately.

## 6. Signal F — a third OCR stack: evaluated, **not added**

The Founder's instruction was to add one only on evidence. The evidence:

1. **Independence, not count, is what is missing.** The two current stacks share Apple Vision (§0), so the
   marginal value of a third *Apple Vision consumer* is zero by construction. Only a different recogniser
   (Tesseract `vie`, PaddleOCR, a VLM) would be evidence.
2. **What is installed:** `tesseract 5` is present on this machine with **`eng`, `osd`, `snum` only** — no
   `vie` traineddata; `pytesseract`, `easyocr` and `paddleocr` are absent. A bounded evaluation therefore
   costs a `tesseract-lang` install (~1 GB) plus a wrapper, before a single page is measured.
3. **What the corpus says the ceiling is.** TC-08 already measured Tesseract-class alternatives indirectly:
   MinerU, which does not do Vietnamese OCR, had FTR **0.638**; the VLM 0.267. The only stacks that beat
   Apple Vision on this corpus were Marker and Docling — both of which use it.
4. **Cost/benefit as it stands:** a third stack helps exactly the class where A and D both abstain — the
   «valid word, wrong word» sub-class where the corpus is itself fooled («Cộng hoà» → «Cộng hoa»,
   cộng·hoa 268 pages vs cộng·hoà 303). That is **1 of the 4 named audit defects**, and on the gold set
   about 90 review-queue rows. A cheap first probe would be **Tesseract `vie` on the 91 `agreed_error`
   queue rows only** — a bounded, ~100-page run — before any pipeline integration.

**Recommendation: do not add a third stack this round.** Run the bounded 91-row Tesseract-`vie` probe first
and decide on its measured disagreement rate with Apple Vision. Stopping here, as instructed.

## 7. Layer E — the human queue, as an output

`poc-out/round5/pipeline/tc2-p3-lin/human-review-queue.jsonl`, **273 rows**, ranked so a person's time buys
the most accuracy:

| priority | kind | rows | what it is |
|---|---|---|---|
| 1 | `agreed_error_trusted` | **91** | a block the pipeline is **serving now** that the machine believes is wrong and could not repair. Every row is a live false-trust claim |
| 2 | `unresolved_teaching` | 32 | a withheld question / instruction / rule a human could restore |
| 3 | `unresolved` | 150 | a withheld block, elsewhere |

Each row carries the block id, page, role, both readings, the candidate (if any) and the signals for and
against — a reviewer never re-derives the machine's case. No page image and no verbatim SGK beyond the
block; it stays in `poc-out/`.
