# 04 — Mode 1 · Smart Book / Đọc như sách — Research

**Research question (Founder §3):** PDF → Structured Document → Native Smart Book, versus PDF → PDF
Viewer, versus PDF → Markdown → generic renderer?

## 1. The three routes, compared on SAM's actual inputs

SAM's inputs are **scanned PDFs with no text layer** (WAL-206 §1), Apple-Vision OCR lines,
XY-cut layout blocks with roles and trust, and a TOC-derived lesson range. Everything below is
conditioned on that.

| Criterion | A · PDF Viewer (page images) | B · PDF → Markdown → generic renderer | C · PDF → Structured Document → native Smart Book |
|---|---|---|---|
| Fidelity to the book | Perfect by definition (it *is* the page) | Lossy: columns, side boxes, tables, figures flattened; Markdown has no notion of "sidebar" or "activity" | High **only where blocks are trusted**; roles exist for text, **none for image/table/formula/activity today** |
| Trust / provenance | Page-level only; cannot cite a block | Provenance lost at conversion unless every line carries page/bbox metadata (Markdown cannot) | Per-block `book · page · region path · order · bbox · ocrConf · trusted` already exist (`poc-out/layout/*/pNNN.json`) |
| Responsive / accessibility / font size | No reflow; zoom only; screen readers see nothing (no text layer) | Good | Good |
| "Ask SAM about this block" | Possible only by page | Possible by paragraph but unanchored | Possible by block **with** bbox anchor → source region image |
| Offline size (Q17–18) | ~20 MB per book PDF (MEASURED: `05-sgk-toan-5-tap-mot.pdf` 20.2 MB) | Small text | Small text + figure crops (0.5–4 MB each) — images dominate |
| Failure mode when extraction is wrong | None (nothing extracted) | **Silent**: wrong text looks right | **Explicit** if trust is honoured: untrusted block ⇒ show page region image |
| Reuse by Mode 2/3 | None | Weak (unstructured) | Strong (typed blocks are the input to bindings) |
| Verdict | Required as **fallback and anchor**, not as the primary journey | **REJECT** as the primary model (loses roles, provenance, fails silently — the exact WAL-204 failure) | **ADOPT WITH CHANGES**: trusted-fragment reconstruction now; full block model PENDING TRUSTED-CORPUS FINDINGS |

Why B is rejected on evidence, not taste: WAL-204 displayed extractor text and it was "column-
scrambled … a section heading attached as a question" on the device; the fix (WAL-206) was
*more* structure (roles, regions, trust), not a text format. A Markdown intermediate would
discard exactly that structure.

## 2. What "native Smart Book" can mean today — measured

Mode 1's block list on the concept board (Heading · Paragraph · Image · Caption · Table · Formula ·
Question · Activity · Source Reference) mapped to what exists:

| Board block | WAL-206 role / SAM object | Status | Note |
|---|---|---|---|
| Heading | `heading` | AVAILABLE (0.90 role accuracy on gold) | OCR errors in headings observed ("SỨC KHOE") — headings need a confidence display rule |
| Paragraph | `body` | AVAILABLE where `trusted` | 30.6% of pages two-column; passage fidelity 0.86 on gold |
| Caption | `caption` | AVAILABLE | floating-label rule; captions exist, the **figure they belong to does not** |
| Image / Figure | — (no role); `SourceAsset` crops exist only by human curation (3 in packs) | **MISSING extractor** | The layout JSON has bbox for text blocks only; a figure region = "the space with no text" is a HYPOTHESIS, not a capability |
| Table | `layout.tableLike ⇒ untrusted` | **FAIL-CLOSED** by design | Correct behaviour: show the page region image labelled "Bảng trong sách" |
| Formula | — | **MISSING** | No formula index exists; ADR-006 lists "formula index" as a target |
| Question | `question` | AVAILABLE (with Q1–Q8 content gate) | The gate removes lead-ins, deictic prompts, objective boxes |
| Activity ("Hoạt động", "Em có biết?") | `sidebar` (side box) | PARTIAL | Side boxes are split from body (fixed on device: "1 gam (g) = 0,001 kg"); "Em có biết?" is a sidebar semantically but not labelled |
| Source Reference | block provenance | AVAILABLE | every block carries book/page/bbox |

MEASURED on the board's nearest real lesson (Khoa học 4 Bài 23, PDF pp.84–93): only p090 is a
trusted page; 8/10 pages untrusted; 0 units in `units-layout`. So for that lesson, Mode 1 today
would show **a page-image reader with (perhaps) a few trusted headings/questions** — which is
honest, and is what the child should see rather than reflowed OCR noise.

For the six device-valid KHTN 6 lessons of WAL-206 §5 (Bài 6, 10, 14, 15, 16, 17), passages are
"coherent, matches print"; those are the candidates for a first Trusted-Fragments Mode 1.

## 3. Prior art that changes a SAM decision

- **PreTeXt** (FROM-REFERENCE — https://pretextbook.org/doc/guide/html/philosophy.html): "you
  explicitly specify the logical parts of your document and not how these parts should be
  displayed"; a single source converts to HTML, PDF, EPUB, braille. **Decision it changes:** the
  Trusted Structured Lesson must be *semantic* (roles), never presentational — Mode 1/2/3 are
  "conversions". SAM already does this at block level; the gap is non-text roles.
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

## 4. The honest Mode 1 (proposed shape, HYPOTHESIS)

"**Trusted Fragments over a Source Page**":

1. Render the lesson's page range as **source page images** (the anchor; available for all 531
   books because OCR already rasterised every page — PENDING TRUSTED-CORPUS FINDINGS on
   image licensing/size).
2. Overlay **trusted blocks** as native, reflowable text in reading order — heading, body,
   question, caption, sidebar — with per-block provenance and confidence; untrusted blocks and
   tableLike regions stay as image regions labelled «Bảng/Hình trong sách».
3. Allowed improvements: font size, zoom, highlight, bookmark, annotation, «Hỏi SAM về đoạn này»
   (carries the block id into the LearningContext), «Xem trang gốc».
4. Emits **TRACE only** (`intent = lookup`; no `LearningEvent`).
5. **Never** hides uncertainty: a page with `trusted=false` shows the page image first and the
   fragments second, with a small line «SAM chưa đọc chắc trang này — con xem trang gốc nhé».

This is reachable with existing types (`SourceAsset` for page images, layout blocks for
fragments) and fails closed by construction. Whether it is *better for the child* than the page
image alone is an unmeasured HYPOTHESIS (test on the six KHTN 6 lessons).

## 5. Answers to Q7 and Q8

- **Q7 — Can Mode 1 replace the PDF Viewer in the primary journey?** There is no PDF viewer in
  the journey today; the question is really "can the child see the book at all". Answer: Mode 1
  as *Trusted Fragments over a Source Page* can be the primary reading view **because it contains
  the page image**; a text-only reconstruction cannot replace the page until non-text blocks exist
  and the Trusted-Corpus study confirms fidelity per subject.
- **Q8 — When should the original PDF remain accessible?** Always, as a *page region image* inside
  Mode 1 (not as a separate PDF viewer): for every untrusted/tableLike/figure region; for
  «Xem trang gốc» from any block, Mode 2 node, or SAM utterance (provenance drill-down, the
  existing Source screen #17); for parents checking «sách nói thế thật không».

## 6. What NOT to copy

- Re-typesetting the book (pixel-perfect) — the Founder excluded it; the extractor cannot support it.
- Markdown as the canonical intermediate (loses roles and provenance).
- DeepTutor-style LLM-written prose blocks "in the style of the book".
- H5P-style hand-authored chapters as the source of truth.

## 7. PENDING TRUSTED-CORPUS FINDINGS

Text fidelity per subject family; whether figure regions can be derived from text-free areas;
table cell extraction feasibility; formula detection; page-image licensing/size policy; lesson
boundary confidence. `12` §6 lists the reconciliation checklist.
