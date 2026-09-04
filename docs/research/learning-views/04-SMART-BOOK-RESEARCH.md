# 04 — Mode 1 · Smart Book / Đọc như sách — Research

> **Reconciled with TC-v1 (2026-09-05).** `TC-nn` = `docs/research/trusted-corpus/nn-….md`. Changes: §1 column C, §2 table (new TC-v1 column; two WAL-206 numbers superseded), §4 items 1–2 and new item 6, §5 Q7, §7 (was "PENDING", now resolved / still unmeasured).

**Research question (Founder §3):** PDF → Structured Document → Native Smart Book, versus PDF → PDF
Viewer, versus PDF → Markdown → generic renderer?

## 1. The three routes, compared on SAM's actual inputs

SAM's inputs are **scanned PDFs with no text layer** (WAL-206 §1; TC-03 §1: 0 of 62,729 pages has
one), Apple-Vision OCR lines, XY-cut layout blocks with roles and trust, and a TOC-derived lesson
range. Everything below is conditioned on that.

| Criterion | A · PDF Viewer (page images) | B · PDF → Markdown → generic renderer | C · PDF → Structured Document → native Smart Book |
|---|---|---|---|
| Fidelity to the book | Perfect by definition (it *is* the page) | Lossy: columns, side boxes, tables, figures flattened; Markdown has no notion of "sidebar" or "activity" | High **only where blocks are trusted**; roles exist for text, **none for image/table/formula/activity today**. TC-v1: a layout-model parser + independent verifier accepts 77–85 % of blocks with FTR 12 % on hard pages / 0 % on plain prose (TC-01, TC-10) |
| Trust / provenance | Page-level only; cannot cite a block | Provenance lost at conversion unless every line carries page/bbox metadata (Markdown cannot) | Per-block `book · page · region path · order · bbox · ocrConf · trusted` already exist (`poc-out/layout/*/pNNN.json`) — but `trusted` is decided by *page/region geometry* (TC-02 §3), not per block; block-level trust is TC-11's `trust{status, reasons[]}` (proposed, not built) |
| Responsive / accessibility / font size | No reflow; zoom only; screen readers see nothing (no text layer) | Good | Good |
| "Ask SAM about this block" | Possible only by page | Possible by paragraph but unanchored | Possible by block **with** bbox anchor → source region image |
| Offline size (Q17–18) | ~20 MB per book PDF (MEASURED: `05-sgk-toan-5-tap-mot.pdf` 20.2 MB) | Small text | Small text + figure crops (0.5–4 MB each) — images dominate; TC-16: SDM ≈ 30–40 KB/page, 200-dpi page render ≈ 330 KB |
| Failure mode when extraction is wrong | None (nothing extracted) | **Silent**: wrong text looks right | **Explicit** if trust is honoured: untrusted block ⇒ show page region image. TC-v1's residual failure is *silent agreement on a shared error* (flattened fractions, merged boxes) — bounded only by deterministic guards (TC-17) |
| Reuse by Mode 2/3 | None | Weak (unstructured) | Strong (typed blocks are the input to bindings) |
| Verdict | Required as **fallback and anchor**, not as the primary journey | **REJECT** as the primary model (loses roles, provenance, fails silently — the exact WAL-204 failure; TC-11 §6 says the same: "do not make Markdown the store") | **ADOPT WITH CHANGES**: trusted-fragment reconstruction now; full block model = TC-11's Structured Document Model (every candidate normalises into it, TC-11 §3) — adopted as the base of `12` §3 |

Why B is rejected on evidence, not taste: WAL-204 displayed extractor text and it was "column-
scrambled … a section heading attached as a question" on the device; the fix (WAL-206) was
*more* structure (roles, regions, trust), not a text format. A Markdown intermediate would
discard exactly that structure. TC-v1 measured the same page (KHTN 7 p32): naive order splices
the sidebar into the body — "false chemistry made from two true sentences" — while Docling on the
same OCR returns body, sidebar and A-B-C-D options cleanly (TC-02 §2).

## 2. What "native Smart Book" can mean today — measured

Mode 1's block list on the concept board (Heading · Paragraph · Image · Caption · Table · Formula ·
Question · Activity · Source Reference) mapped to what exists, with the TC-v1 measurement on 38
hard pages / 462 learning blocks (TC-04):

| Board block | WAL-206 role / SAM object | Status (WAL-206 gold, 9 pages) | TC-v1 (38 hard pages) |
|---|---|---|---|
| Heading | `heading` | AVAILABLE — "0.90 role accuracy" **superseded** | XY-cut precision 0.81 / recall 0.51; Docling 0.86 / 0.78; Marker 0.89 / 0.80 (TC-07). Marker drops some lesson titles as empty PageHeader blocks (TC-08 §3). OCR tone slips on decorative fonts remain ("EM CÓ THẾ", TC-02 §4) — a confidence display rule is still needed |
| Paragraph | `body` | AVAILABLE where `trusted`; passage fidelity 0.86 on gold | Contiguous-block fidelity XY-cut 0.847 → Docling 0.975; cross-column splices 17 → 6; text accuracy 0.907 → 0.954 (TC-05 §1). Plain-prose pages: TLSR 1.00, FTR 0 under the cascade (TC-05 §3). "30.6 % of pages two-column" = TC-03's 29.5 % *side-by-side regions* (same measurement, TC-03 §6) |
| Caption | `caption` | AVAILABLE; the **figure it belongs to does not exist** | Caption role XY-cut 0.85 / 0.74, Docling 0.90 / 0.79, Marker 0.95 / 1.00 (TC-07) — enough for the SDM `caption_of` relation |
| Image / Figure | — (no role); `SourceAsset` crops only by curation (3 in packs) | **MISSING extractor** | SDM `Figure{bbox, kind: photo|drawing|diagram|map|chart, labels[], caption → Block}` (TC-11 §2); page-level figure presence measured on all 62,729 pages (37.4 % figure, 19.0 % diagram — TC-03 §2); layout-model parsers return picture bboxes as native labels (TC-11 §3). **Figure bbox precision STILL UNMEASURED** (the gold scores text blocks; TC-04). Content stays an image region — never text (TC-10 escalation) |
| Table | `layout.tableLike ⇒ untrusted` | **FAIL-CLOSED** by design | Marker: TABLE 1.00 / 1.00 as objects (129 s/page here — GPU class); Docling 1.00 / 0.47 with cells returned as one flattened string (TC-07, TC-14); tables FTR 0.19 under the Mac cascade (TC-05 §3). On the Mac path a table stays «Bảng trong sách» (image) |
| Formula | — | **MISSING** | Only Marker labels FORMULA (0.81 / 1.00); every OCR stack flattens notation identically ("1 5 + 1 2 = 7 10", TC-09 #4); the math guard withholds such blocks (TC-10); verdict image-first (TC-19 #7). **Never a text block** |
| Question | `question` | AVAILABLE (with Q1–Q8 content gate) — **superseded as a role** | XY-cut is the only labeller: precision 0.69 / recall 0.79 — 11 headings and 23 objectives/instructions/answers/table headers emitted as questions (TC-07, TC-02 §3); no layout parser has a QUESTION concept. Until a role layer measures ≥ 0.95, a `question` block may be *read* as text but carries **no question affordance** (no prompt, no inline check) |
| Activity ("Hoạt động", "Em có biết?") | `sidebar` (side box) | PARTIAL | XY-cut sidebar 0.45 / 0.43 (TC-07); Docling separates side boxes cleanly (fidelity 0.975) but labels them `text`. SDM roles SIDEBAR · ACTIVITY · RULE · OBJECTIVE exist (TC-11 §2); assigning them is the unbuilt role layer |
| Source Reference | block provenance | AVAILABLE | SDM: `id = <doc>:p<NNN>:<parser>:<n>`, `bbox [x, y, w, h]` normalised, `provenance{extraction_method, ocr_conf, model versions, run id}` (TC-11 §2) |

MEASURED on the board's nearest real lesson (Khoa học 4 Bài 23, PDF pp.84–93): only p090 is a
trusted page; 8/10 pages untrusted; 0 units in `units-layout`. TC-v1 generalises this: on the
150-page pilot the XY-cut page gate trusted 50 of 150 pages (Toán 5: 3 of 50) while block-level
gating with Docling ▸ XY-cut kept 84.7 % of blocks (83.3 % with the math guard) — with an
ESTIMATED 5–10 % of those wrong on unannotated pages (TC-13 §1). So for that lesson, Mode 1 today
would show **a page-image reader with (perhaps) a few trusted headings/questions** — which is
honest, and is what the child should see rather than reflowed OCR noise.

For the six device-valid KHTN 6 lessons of WAL-206 §5 (Bài 6, 10, 14, 15, 16, 17), passages are
"coherent, matches print"; those are the candidates for a first Trusted-Fragments Mode 1 —
as a *measurement prototype* (see §4 item 6).

## 3. Prior art that changes a SAM decision

- **PreTeXt** (FROM-REFERENCE — https://pretextbook.org/doc/guide/html/philosophy.html): "you
  explicitly specify the logical parts of your document and not how these parts should be
  displayed"; a single source converts to HTML, PDF, EPUB, braille. **Decision it changes:** the
  Trusted Structured Lesson must be *semantic* (roles), never presentational — Mode 1/2/3 are
  "conversions". SAM already does this at block level; the gap is non-text roles. TC-11 §2 is
  exactly this: Markdown/units/packs are projections of a semantic block model.
- **DeepTutor Book Engine** (FROM-REFERENCE — `web/lib/book-types.ts`, `deeptutor/book/models.py`):
  a book is `Spine → Chapter → Page → Block{type, status, payload, source_anchors[]}` with 19
  `BlockType`s (text, callout, quiz, figure, timeline, flash_cards, concept_graph, …). **Decision
  it changes:** the *shape* (chapter/page/typed blocks with anchors and per-block status incl.
  `hidden`/`error`) is a good template for a lesson document; the *content generation* (LLM
  writes blocks; anchors are ≤300-char snippets; timeline/quiz anchors empty) is the opposite of
  SAM's trust rule. Copy the schema idea, not the pipeline.
- **H5P Interactive Book** (FROM-REFERENCE — `semantics.json`): chapters are lists of `H5P.Column`
  which embed other content types; progress indicators per page; MIT. **Decision it changes:**
  "lesson = composition of reusable blocks" is a proven authoring model — but it is an *authored*
  model, not an extracted one; SAM cannot author 3,679 lessons by hand. Composition applies to
  *surfaces*, not to the source.
- **Runestone interactive ebooks** (FROM-REFERENCE — https://runestoneinteractive.org/pages/research.html; Ericson & Miller 2020): interactive ebook elements (MCQ, Parsons, active code) show positive learning/attitude outcomes versus static ebooks in CS courses. **Decision it changes:** "interactivity inside the reading view" has evidence — but it is *practice inside the book*, i.e. Mode 3 surfaces embedded in Mode 1, not a separate app mode. Supports the "Hỏi SAM về đoạn này" and inline question ideas.
- **Caliper Reading Profile** (FROM-REFERENCE — https://www.imsglobal.org/spec/caliper/v1p2): `NavigationEvent`/`ViewEvent` with actions NavigatedTo/Viewed are separate from Assessment `Started/Completed/Submitted`. **Decision it changes:** Mode 1 telemetry is TRACE by an established standard's own vocabulary — "Viewed" is not "Completed". Confirms SAM's TRACE ≠ EVIDENCE.

## 4. The honest Mode 1 (proposed shape, HYPOTHESIS — confirmed in shape by TC-v1)

"**Trusted Fragments over a Source Page**":

1. Render the lesson's page range as **source page images** (the anchor; available for all 531
   books because OCR already rasterised every page). **TC-v1:** size measured — a 200-dpi review
   render ≈ 330 KB/page, ≈ 4 GB if 20 % of pages (TC-16); the reader-dpi/webp size is STILL
   UNMEASURED. Licensing is **not** measured by TC-v1 — it recommends image-first delivery of page
   crops with provenance (TC-19 #7) and records the derivative-work governance as unchanged
   (TC-17 #15); OQ8 stays a Founder/Legal decision (`17` §5 C6).
2. Overlay **trusted blocks** as native, reflowable text in reading order — heading, body,
   caption, sidebar, and `question`-role blocks *as plain text* (no prompt affordance until the
   role layer measures ≥ 0.95, TC-07) — with per-block provenance and confidence; WITHHELD /
   CONFLICT blocks and formula / table / diagram / timeline / map / colour-heavy regions stay as
   image regions labelled «Bảng / Hình / Công thức trong sách» (page-feature guard, TC-10;
   TC-18 Q15–16).
3. Allowed improvements: font size, zoom, highlight, bookmark, annotation, «Hỏi SAM về đoạn này»
   (carries the block id into the LearningContext), «Xem trang gốc».
4. Emits **TRACE only** (`intent = lookup`; no `LearningEvent`).
5. **Never** hides uncertainty: a page with `trusted=false` shows the page image first and the
   fragments second, with a small line «SAM chưa đọc chắc trang này — con xem trang gốc nhé».
6. **Source of the fragments.** Until the TC pipeline (TC-10) exists, fragments can only come
   from the XY-cut, whose trust is page-gated (TC-02 §3) with FTR 0.119 on hard pages (TC-08 §1)
   — acceptable for a *measurement prototype* on the six KHTN 6 lessons, not for a child
   (TC-18 Q1: "not safe enough"). Production Mode 1 consumes `TrustedLearningSource` (TC-11).

This is reachable with existing types (`SourceAsset` for page images, layout blocks for
fragments) and fails closed by construction. Whether it is *better for the child* than the page
image alone is an unmeasured HYPOTHESIS (test on the six KHTN 6 lessons).

## 5. Answers to Q7 and Q8

- **Q7 — Can Mode 1 replace the PDF Viewer in the primary journey?** There is no PDF viewer in
  the journey today; the question is really "can the child see the book at all". Answer: Mode 1
  as *Trusted Fragments over a Source Page* can be the primary reading view **because it contains
  the page image**; a text-only reconstruction cannot replace the page until non-text blocks exist.
  **TC-v1 answers per layout feature, not per subject:** prose / question / sidebar pages — text
  fragments trustworthy under a cascade (FTR 0 on plain prose, 0.087–0.091 on sidebar / question
  pages, TC-05 §3); formula (TLSR 0.55 / FTR 0.17), speech-bubble (0.48 / 0.25), colour-heavy
  elementary (0.36 / 0.30), table (FTR 0.19), diagram / map / timeline (semantic order wrong in
  every parser, TC-06) — **page image only**. Per subject that means Toán / Vật lí / KHTN are the
  least text-sourceable (4/554, 1/82, 4/145 lessons fully, TC-18 Q17) and Ngữ văn the most (figure
  12 %, formula 0.5 % of pages, TC-03 §4); per-subject text accuracy itself is STILL UNMEASURED.
- **Q8 — When should the original PDF remain accessible?** Always, as a *page region image* inside
  Mode 1 (not as a separate PDF viewer): for every untrusted/tableLike/figure region; for
  «Xem trang gốc» from any block, Mode 2 node, or SAM utterance (provenance drill-down, the
  existing Source screen #17); for parents checking «sách nói thế thật không». TC-v1 adds: for
  every formula, and for every block the guards withhold — the review queue carries the same crop
  (TC-10).

## 6. What NOT to copy

- Re-typesetting the book (pixel-perfect) — the Founder excluded it; the extractor cannot support it.
- Markdown as the canonical intermediate (loses roles and provenance; TC-11 §6).
- DeepTutor-style LLM-written prose blocks "in the style of the book" (TC-11 §6: no LLM/VLM re-guessing a block).
- H5P-style hand-authored chapters as the source of truth.

## 7. Reconciled with TC-v1 (was: PENDING TRUSTED-CORPUS FINDINGS)

| Item (as tagged 2026-09-04) | Outcome after TC-v1 |
|---|---|
| Text fidelity per subject family | **Partly.** MEASURED per layout feature (TC-05 §3: plain prose TLSR 1.00 / FTR 0; formula 0.55 / 0.17; speech-bubble 0.48 / 0.25; colour-heavy 0.36 / 0.30; tables FTR 0.19; sidebars 0.087; question blocks 0.091) and per subject only as fully-sourceable lesson counts (TC-18 Q17). Per-subject text accuracy **STILL UNMEASURED after TC-v1** — the 38-page gold has ≤ 10 pages per family (TC-04); a ≥ 20-page per-family gold (TC-19 #9) would close it. |
| Whether figure regions can be derived from text-free areas | **Yes at page level** (ink outside OCR boxes ≥ 4 % of page: 37.4 % of pages carry a figure, 19.0 % a diagram — TC-03 §2); layout-model parsers return picture bboxes natively (TC-11 §3); the SDM has a `Figure` object (TC-11 §2). Figure *bbox precision* **STILL UNMEASURED after TC-v1** — would need figure bboxes scored against the gold's `diagram` / `figure_label` blocks. |
| Table cell extraction feasibility | **MEASURED:** Marker 1.00 / 1.00 as objects (GPU class); Docling 1.00 / 0.47 with flattened cells; FTR 0.19 under the Mac cascade (TC-07, TC-14, TC-05 §3). |
| Formula detection | **MEASURED:** only Marker emits FORMULA (0.81 / 1.00); text is flattened identically by every stack; withhold by math guard, deliver image-first (TC-07, TC-09, TC-19 #7). |
| Page-image licensing / size policy | Size **MEASURED** (≈ 330 KB per 200-dpi page, TC-16; reader-dpi size STILL UNMEASURED). Licensing **not measured and not decided** by TC-v1 — Founder/Legal (OQ8). |
| Lesson boundary confidence | **MEASURED:** 28/38 gold pages attach correctly by TOC range; header-based attachment fixes 6 of the 10 failures; 4 non-lesson pages need a "no lesson" rule (TC-02 §5, TC-14 §2); the SDM carries `lesson{attach_method, confidence}` per block (TC-11 §2). |

`12` §6 is the applied checklist.
