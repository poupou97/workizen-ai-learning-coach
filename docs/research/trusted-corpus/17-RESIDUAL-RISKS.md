# 17 — Residual Risks (after the best measured cascade)

Ordered by expected harm to a child × likelihood, with the evidence line that supports each.

| # | risk | evidence | status |
|---|---|---|---|
| 1 | **Shared-mode errors that agreement cannot see** — math notation flattened identically by every OCR stack (fractions, exponents, <, >, ≠, ∫), adjacent coloured boxes merged identically by two layout models, one stack dropping a header while the other keeps it | 08 §3: ~14 of 18 residual false-trusted blocks (first 24 pages; 21 on 32) in marker ▸ docling; math guard removed 8 in docling ▸ xycut | open — needs deterministic guards + a formula-capable path, or image-first delivery of math |
| 2 | **False trust is measured at 5–7 % on hard pages, not 0.1 %** — and 38 pages cannot certify a rate below ~1 % | 08 §5; a 0.1 % claim needs ≥ 3,000 validated blocks | open — bounded validation on the lessons actually shipped |
| 3 | **No role layer exists**; the only question labeller (XY-cut) has 0.69 precision; every layout parser returns questions, objectives, answers and sidebars as "text" | 07 | open — build + measure ≥ 0.95 before any auto-labelled question is graded |
| 4 | **Lesson attachment**: 10/38 gold pages attach wrongly by TOC range (partial TOCs, missing lessons, non-lesson pages, two lessons on one page) | 02 §5, 09 #8–9 | open — header-based attachment + TOC repair + "no lesson" rule |
| 5 | **Semantic reading order** geometry cannot see: timelines (boxes above/below an arrow), 2-D worked schemes, bubbles that precede a section | 06 table; LS&ĐL 8 p71 fails for every candidate | open — feature-gated withholding; these pages stay FIGURE-only |
| 6 | **Elementary visual pages** (grades 1–3): the content is pictures; text blocks are fragments, "? ? ?" slots and symbols | family table: colour-heavy pages TLSR 0.36–0.45, FTR 0.22–0.30 | open — image-first Surfaces, not text extraction |
| 7 | **Compute on one Mac**: Docling ≈ 3.5–4 s/page (≈ 60–70 h for 62,729 pages), Marker ≈ 129 s/page (≈ 94 days) | 16 | manageable for Docling; Marker needs a GPU box |
| 8 | **Gold quality**: single VLM annotator, bbox by eye, three lesson numbers needed TOC notes, one corrected | 04 limits | mitigate with a second (human) read of 10 pages before any gate is tuned on it |
| 9 | **Scorer limitations** as evidence: anchor matching, block-extension window, 3-char rule — two of 18 "false trusted" in the best cascade were scorer-side | 08 §3 | disclosed; numbers are upper bounds on false trust by ≈ 1 point |
| 10 | **Licences**: MinerU and PyMuPDF are AGPL-3.0, Marker GPL-3.0 (commercial licence available), Docling MIT, Apple Vision OS-bound (macOS/iOS only — no Linux batch farm without changing OCR) | 05 table | decision needed before any pipeline is productised |
| 11 | **OCR ceiling**: ~100-ppi scans; tone-mark slips on decorative fonts ("EM CÓ THẾ"), "hoá/hóa" normalisation by Apple's language model — cannot be fixed downstream | 02 §4, 05 | accept + measure; re-scanning is out of scope |
| 12 | **VLM as verifier**: 3B model ignored the structured format on 20/22 pages; hallucination not observed but not tested at scale; larger models do not fit the Mac | 05, 10 | do not rely on a VLM for truth; text-only verification at most |
| 13 | **Activity-pattern census drift**: any pipeline change changes the units the taxonomy counted; the current 27-pattern counts are not stable | 15 | re-run the census after adoption; do not implement patterns from the old counts |
| 14 | **SGV leakage**: teacher prompts and model answers are indistinguishable from learner content without an SGV lexicon and `answer_of` relations | 14 | fail-closed answer-leak guard is mandatory before any SGV block reaches a Surface |
| 15 | **Derived-data governance**: all outputs are derivative works of copyrighted SGK/SGV; they live only under gitignored `poc-out/` and the Desktop bundle contains page crops for review | TEXTBOOK-LICENSING-QUESTIONS.md | unchanged; no raw PDFs anywhere in deliverables |

## The single biggest residual risk

**Silent agreement on a shared error.** Two independent-looking stacks (same OCR, or two layout models trained on the same kind of documents) agree on the wrong text or the wrong block boundary, the gate says TRUSTED, and SAM teaches "200 300" or a paragraph that contains a sidebar sentence. Everything else in this list can be withheld by a rule; this one can only be bounded by (a) guards written from the error classes measured here, (b) a verifier that is structurally different (image-first, or a human) for the block classes where guards do not exist, and (c) measuring false trust continuously on shipped lessons rather than assuming it from a gold set.
