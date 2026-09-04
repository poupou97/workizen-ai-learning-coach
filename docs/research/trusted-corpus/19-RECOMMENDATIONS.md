# 19 — Recommendations (ordered; each with the evidence that justifies it)

1. **Adopt the Structured Document Model as the source layer (11); demote Markdown/units to projections.** Evidence: every failure class measured here is invisible in the current unit/Markdown representation; every candidate normalised into the SDM in one afternoon (`tc_sdm.py`).
2. **Replace page-level trust with block-level trust from an agreement cascade (10): Docling + Apple Vision as primary, the WAL-206 XY-cut as the independent verifier, deterministic guards on top.** Evidence: XY-cut page gate trusts 3/50 Toán 5 pages; the cascade keeps 77–85 % of blocks with FTR 12 % on hard pages, 0 % on prose; runs in ≈ 3.4 s/page on the existing Mac.
3. **Build the role layer before routing anything as a question (07).** Target: question precision ≥ 0.95 on the gold set, with lexicon for objectives ("… được"), instructions (Bước, Chuẩn bị), model answers ("M:"), answer slots ("?"), stage labels, SGV teacher text. Until then, no auto-labelled question is graded (consistent with WAL-204/206 rules).
4. **Write the guards from the measured error classes (09) and make each one a rule with a reason code:** math guard (done in simulation), empty-block/header guard, box-boundary guard using colour under the bbox (census signal exists), figure-dependence guard ("hình 6", "Hình 7.7"), answer-leak guard, enumerator-preservation (restore "1."/"a)" from OCR lines when Docling drops them), page-feature guard (diagram/map/timeline pages → FIGURE only).
5. **Fix lesson attachment at the source: header-based attachment with `heading_path`, `continues` for cross-page text, "no lesson" for front/back matter and theme openers, TOC repair for the PARTIAL books.** Evidence: 10/38 gold pages attach wrongly today; 6 of them are fixed by headers alone.
6. **Do not reprocess the whole corpus yet (12).** Run a versioned slice (Science family, 2,680 pages, ≈ 2.5 h) after 2–4 exist, re-run the WAL-206 funnel on both sources, and let the +N lessons number decide the next step. Keep everything under `poc-out/trusted-corpus/tc-v2/`.
7. **Ship from the trusted subset; keep math and visual lessons image-first.** Evidence: formula blocks are flattened identically by every stack; elementary pages are pictures; the products' Surfaces can show a page crop with provenance long before text extraction of those pages is trustworthy.
8. **Get a GPU box (or a rented one) for Marker/Surya 2 as the third stack and for table/formula objects.** Evidence: marker ▸ docling FTR 0.065 and tables/formulas 1.00/1.00, but 129 s/page here. Decide the GPL question first.
9. **Extend the gold set before tuning any gate on it**: second human read of 10 pages; 20 SGV pages; 10 cross-page lesson boundaries; then re-measure. A false-trust claim below 1 % needs ≥ 3,000 validated blocks — plan a statistical audit on shipped lessons instead of a bigger gold set.
10. **Re-run the K-12 activity-pattern census only on role-labelled SDM output** (15), publish old and new counts side by side, and keep the 27-pattern registry as a hypothesis list (WAL-203), not a backlog.
11. **Record the decisions**: SDM-as-source, block-level trust, image-first for math/visual, and "trusted subset, not whole corpus" are ecosystem-level decisions — file them as PROPOSED per `canonical/KNOWLEDGE_UPDATE_PROTOCOL.md`; this study does not decide them.

## What to stop doing (evidence-backed)

- Stop improving the naive/XY-cut extractor for coverage — its ceiling is the page-level gate and a regex role labeller (02, 07).
- Stop counting "PDFs converted to Markdown" or "lessons with ≥ 1 unit" as progress (K); count trusted blocks and false-trust audits.
- Stop treating the Fable/registry pattern counts as facts about the books (15).
- Do not add MinerU, Marker or PyMuPDF as project dependencies on the strength of this study — only Docling + ocrmac earned a place, and only inside the offline corpus tooling (licences: 05).
