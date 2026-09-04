# 10 — Cascade / Ensemble Options (agreement gates, fail closed)

**Principle (Founder order H).** Neither an LLM/VLM nor any single parser is source truth. A block becomes TRUSTED only when independent analyses agree on its text and its place in the reading order; disagreement → WITHHELD (safe failure); a deterministic guard can also withhold. Simulator: `tool/corpus/tc_cascade.py` — it builds "virtual candidates" from the real bake-off outputs and scores them with the same scorer, so every number is measured on the gold set.

Agreement rule per primary block: text aligns inside the verifier's reading-order stream at ≥ 92 % (rapidfuzz partial ratio) — offsets must not go backwards (one-block tolerance so a displaced box withholds only itself) — a primary QUESTION whose verifier position is a HEADING is withheld (`role_conflict`). **Math guard:** a trusted block carrying math tokens (`3x⁷`, `1/5`, `200 < 300`, `x ≠ −1`, `∫`) that no parser labelled FORMULA/TABLE is withheld, because every text-line OCR flattens notation the same way and agreement cannot see it.

## Measured (gold set; Marker/VLM on the pages they completed)

| cascade | pages | coverage | TLSR | false-trusted | FTR | withheld | gate: text / order disagreements |
|---|---|---|---|---|---|---|---|
| docling ▸ xycut | 38 | 0.810 | 0.699 | 51 | 0.136 | 65 | 93 / 88 |
| docling ▸ xycut + math guard | 38 | 0.766 | 0.673 | 43 | 0.121 | 85 | + 20 math |
| docling ▸ marker | 32 | 0.815 | 0.700 | 45 | 0.140 | 52 | 166 / 61 |
| docling ▸ vlm | 31 | 0.773 | 0.657 | 44 | 0.150 | 66 | 179 / 62 |
| **marker ▸ docling** | 32 | 0.817 | **0.764** | 21 | **0.065** | 53 | 76 / 8 |
| marker ▸ docling + math guard | 32 | 0.797 | 0.744 | 21 | 0.067 | 61 | + 8 math |
| marker ▸ vlm | 31 | 0.784 | 0.728 | 21 | 0.071 | 63 | 97 / 5 |
| docling ▸ marker + vlm (3-way) | 31 | 0.699 | 0.607 | 35 | 0.132 | 94 | 230 / 90 |
| xycut ▸ docling | 38 | 0.403 | 0.331 | 33 | 0.177 | 267 | XY-cut's own gate withholds 433 first |

Reference single stacks: docling alone FTR 0.143 / TLSR 0.814; marker alone FTR 0.093 / TLSR 0.863 (32 p); current xycut FTR 0.119 / TLSR 0.193.

## Readings

1. **Agreement halves false trust but does not eliminate it.** Best measured: marker ▸ docling, FTR 6.5 % at 82 % coverage (≈ 5 % after scorer-side corrections, 08 §3). The residue is shared failure modes (math, merged boxes, dropped headers), which agreement cannot see by construction.
2. **The verifier's independence matters more than its quality.** Docling ▸ XY-cut (same OCR) leaves FTR 0.136; Marker ▸ Docling (different OCR and layout model) 0.065. The VLM as verifier (different modality) performs like Docling as verifier of Marker (0.071), at 81 s/page.
3. **3-way agreement is worse, not better:** the 3B VLM's block segmentation differs, so its disagreements are mostly segmentation noise; it withholds good blocks (coverage 0.699, TLSR 0.607) without removing the shared-mode errors (FTR 0.132). A verifier must be structurally comparable or must verify *text only*.
4. **Deterministic guards are the only thing that removed shared-mode errors** (math guard −8 false-trusted). This is where the ecosystem should invest: rules that can be audited, not more models voting.
5. **Cost-feasible pair on one Mac: Docling primary, XY-cut verifier** (≈ 4 s/page total). The Marker verifier costs ≈ 130 s/page here; feasible only on a GPU (Surya on CUDA is reported at ~1–2 s/page — ESTIMATED, not measured here).

## Proposed cascade (to build, not built) — "TC pipeline v1"

```
PDF page (render 200–300 dpi)
  ├─ A. Docling layout model + Apple Vision text   (2–4 s)   → SDM blocks with bbox, order, native labels
  ├─ B. WAL-206 XY-cut on the same OCR lines        (0.02 s) → independent regions, order, QUESTION/SIDEBAR hints
  ├─ C. (when a GPU exists) Marker/Surya 2           (~1–2 s GPU) → independent OCR + layout, tables, equations
  ▼
  Role layer (deterministic): stage labels, directive lexicon, box colour under bbox (census signal), "M:"/"?"
  answer slots, caption_of / options_of / continues relations, header-based lesson attachment
  ▼
  Gates (each writes a reason):  text+order agreement A⟷B (and A⟷C when available) · math guard ·
  box-boundary guard (bbox spans two background colours) · empty-block guard · figure-dependence guard
  ("hình 6") · answer-leak guard · role conflict · page feature guard (03: diagram/map/timeline pages →
  FIGURE blocks only, no prose)
  ▼
  TRUSTED → Trusted Learning Source (SDM subset)            WITHHELD/CONFLICT → review queue with page crop
  ▼
  LearningActivity → Pedagogy → SAM (projections carry block ids; never Markdown as truth)
```

Expected on the gold set (MEASURED components, ESTIMATED combination): coverage ≈ 0.70–0.77 of learning blocks, FTR ≈ 5–8 % on hard pages, ≈ 0 on plain prose pages, and the withheld 25–30 % concentrated in math notation, elementary visual pages, timelines/diagrams and dense box pages. What is **not** expected: < 0.1 % false trust without a human or a structurally different verifier for math and boxes.

## Escalation paths for the withheld share (options, not decisions)

- Math pages: a formula-aware recogniser (Marker/Surya Equation blocks, or a math-OCR model) verified against the text-line OCR; or **do not extract formulas as text at all** — deliver the page crop to the learner (image-first Surface) and only the surrounding prose as text.
- Diagrams / timelines / maps: keep as FIGURE + labels; never as prose; questions that reference them are figure-dependent by rule.
- Elementary visual pages (grade 1–2): image-first; text blocks limited to instructions.
- Box-dense pages: colour-segmentation-based region detection (the census already measures colour under lines) as a third independent geometry signal.
- Human review: only for the WITHHELD queue on lessons the product actually ships (22-… in 18).
