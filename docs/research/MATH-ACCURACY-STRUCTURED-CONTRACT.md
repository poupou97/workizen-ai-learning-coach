# The structured STEM contract — what A2 produces, what A1 and B must provide · 2026-09-06

**READY FOR FOUNDER REVIEW — nothing merged.** Lane A2, branch `a2/round5-math-formula-accuracy`.
This is the interface half of the STEM P0: two requests (one to Lane A1, one to Lane B) and one
schema. It is deliberately short and deliberately additive — nothing here asks any lane to change
behaviour, only to carry something it already has or to render something it will be given.

Implemented in `tool/corpus/mathfix/nodes.py`, `expression.py`, `build.py`, `glyphs.py`; pinned by
`tool/tests/test_mathfix_nodes.py` and `test_mathfix_glyphs.py`.

---

## 1 · Request to Lane A1 — per-line geometry on the SDM block (§2)

**The gap, in one line of code.** `tool/corpus/tc2_sdm.py:1060` computes `under` — the OCR lines
whose centre falls inside the block's bbox — hands it to `verse_layout` at `:1110` for a single
boolean, and discards it. The emitted block (`:1136-1141`) has `text`, `text_docling`, `bbox`,
`cells` and no line array. **The 2-D geometry that proves a fraction is a fraction is read, used to
decide whether a poem is a poem, and thrown away one step before the guards run.**

That is why R2's request (c) — *«withhold when a block's text has fewer numeric tokens than the
stacked-fraction regions its bbox overlaps»*
(`docs/research/legacy-reprocess/PIPELINE-REQUESTS-FROM-LEGACY.md:71-77`, OPEN·P0) — cannot be
implemented where the guards live.

**Asked for: one additive field, `lines`, on every SDM block.** No behaviour change; the flat `text`
stays exactly as it is, as a projection.

```jsonc
"lines": [                       // the OCR lines under this block, in file order
  {"text": "3",  "bbox": [0.3408, 0.4244, 0.0184, 0.0131], "index": 34, "conf": 1.0,
   "source": "apple-vision-ocr-line"}
]
```

* `bbox` — `[x, y, w, h]`, normalised, y down: the same convention the block's own `bbox` uses.
* `index` — the line's index in `poc-out/graph/ocr-body/<book>/pNNN.json`, so a consumer can rejoin
  the source.
* `source` — which stack read it. Optional; defaults to `apple-vision-ocr-line`.
* `conf` — the stack's own confidence, unchanged.

**A2 already reads it.** `mathfix/expression.py:geometry_from_sdm_block` uses `block['lines']` when
present and falls back to the OCR body file otherwise, so neither lane is blocked and the two do not
fork the geometry: when A1 ships the field, A2 starts using it with no change on this side.

**Why additive rather than a new structure:** the field costs one list per block, is pure data, and
is reversible by deleting it. It also serves A1 and A3 directly — «this block has 2 numeric tokens
and its bbox overlaps 2 stacked-fraction regions» is exactly the kind of check the guards cannot do
today, and the same field answers it for Vietnamese line-structure questions.

## 1b · Request to Lane A1 — `formula_structured`, the guard exemption (§4)

`tool/corpus/tc2_sdm.py:674,676,678` currently exempt a block from `math_guard`, `unit_guard` and
`chem_guard` when `role in ('formula', 'table', 'figure', 'empty')`, and `:290-291` gives a
Docling-labelled formula block **confidence 0.95 with no verification of any kind**. The exemption
trusts a label while the content arrives as a flat string.

Asked for: the exemption is earned by a **validated structure**, not a role name —

```python
role == 'formula' and block.get('formula_structured') is True
```

where `formula_structured` is set **only** by a `MathExpression` whose disposition is
`VALIDATED_REPAIR`. A `formula`-role block without it is guarded like any other block.

This matters more than it looks. On the 38 gold pages Docling scored formula-role **0**
(`docs/research/trusted-corpus/05-PARSER-BAKEOFF.md:32`), so the branch is dead — but on the legacy
batch-1 Toán pages Docling emitted **15** formula labels, and 14 of them were saved from the
exemption only by the `empty` test firing first at `tc2_sdm.py:276`. The exemption is safe by
accident, and enabling Docling's formula enrichment would silently mint trusted formulas.

---

## 2 · The canonical object

```jsonc
{
  "sourceBlockId": "05-sgk-toan-5-tap-mot:p022:tc2-p2:020",
  "book": "05-sgk-toan-5-tap-mot", "pagePdf": 22, "pagePrinted": 21,
  "bbox": [0.74, 0.76, 0.12, 0.03],
  "crop": "crops/…-withheld-020.png",     // the fallback that survives a refusal
  "ast": { "kind": "ADD",
           "left":  {"kind": "FRACTION", "num": {"kind":"NUM","literal":"3"},
                                          "den": {"kind":"NUM","literal":"10"}},
           "right": {"kind": "FRACTION", "num": {"kind":"NUM","literal":"5"},
                                          "den": {"kind":"NUM","literal":"21"}} },
  "latex": "\\frac{3}{10} + \\frac{5}{21}",   // DERIVED from the ast, never parsed back
  "textProjection": "3/10 + 5/21",            // a courtesy for logs and diffs; never a source
  "originalText": "b) 10 +",                  // the observation, kept beside the proposal
  "observations":   [ {"text":"3","bbox":[…],"source":"apple-vision-ocr-line","index":34} ],
  "sourceGeometry": [ … ],                    // every OCR line under the block (§1)
  "ruleId": "math-line-v1",
  "recognition": [],                          // each candidate + which recogniser produced it
  "validations": [ {"validator_id":"operator-raster-v1","verdict":"PASS","evidence":{…}} ],
  "provenance": {"lane":"A2","pipeline":"tc2-p2","detector":"mathfix.stacked-fraction-raster-v1"},
  "disposition": "VALIDATED_REPAIR",          // or WITHHELD; TRUSTED is a separate Founder act
  "reasons": []
}
```

### Node kinds

| kind | fields | LaTeX |
|---|---|---|
| `NUM` | `literal` — exactly as printed («0,7», «1 360») | the literal, comma protected |
| `SYM` | `name` | the name |
| `FRACTION` | `num`, `den` | `\frac{…}{…}` |
| `POWER` | `base`, `exp` | `{…}^{…}` |
| `ADD` `SUB` `MUL` `DIV` `EQ` | `left`, `right` | `+ - \times \div =` |
| `UNIT` | `symbol`, `exp`, `den?` | `m`, `m^{2}`, `m/s^{2}` |
| `QUANTITY` | `magnitude`, `unit` | `3 \times {10}^{8}\ \mathrm{m/s}` |
| `ITEM` | `label`, `body` — an enumerated item | `\text{b)}\ …` |
| `ROW` | `items` — several items on one printed line | `\qquad`-separated |

Three properties are enforced in code, not asserted:

1. **The AST is canonical.** `latex` and `text` are computed properties with no setter. There is
   `from_json`; there is **no** `from_latex` and no parser. A rendering string cannot become
   structure, so a model-generated or hand-edited LaTeX cannot launder itself into truth.
2. **A source observation is never overwritten.** `originalText` sits beside `ast`, never in place
   of it, and `observations` are frozen records.
3. **Nothing here is servable.** `disposition` starts at `REPAIRED_CANDIDATE`; the best a validator
   can do is `VALIDATED_REPAIR`. `TRUSTED` is a separate, Founder-gated act that does not exist.

### A refusal is an object too

A region the lane finds and cannot read still produces a `MathExpression` — with `ast: null`,
its `bbox`, its `crop`, and a named `reason`. That is what makes «withhold» honest: today
**14 of 15** Docling formula regions on the Toán pages are filed as role `empty`, reason
`empty_block`, evidence *«no letters»* (audit §3 C4), one of them carrying the text
`'7 8 2 8 7 - 2 8 5 8'`. Nothing downstream can know a formula was refused there.

---

## 3 · Request to Lane B — what a renderer needs (§9)

**Lane A2 does not own `lib/**` and has written none of it.** This is the contract, for Lane B to
accept, amend or refuse.

**What the app has today** (audit §2): no `formula` member in the sealed `LessonBlock` union
(`lib/core/lesson_model/lesson_document.dart:154`, and `fromJson` returns `null` for an unknown
type at `:343`, taking the whole document with it); no `RichText`, `TextSpan` or `Text.rich`
anywhere in 147 Dart files; no math/markdown/LaTeX/SVG/WebView dependency in `pubspec.yaml:35-42`.
A formula reaching the reading view renders as `Text` (`smart_book_view.dart:440`) or, when
withheld, as a `WithheldCard` whose crop **already renders** (`withheld_card.dart:182-201`).

**Option A — image fallback only. Zero app work, available today.**
The withheld path already shows the child the printed formula as a page crop, behind a button, with
the caption «Ảnh chụp trang sách — chỉ để con đối chiếu». A `VALIDATED_REPAIR` could ship its crop
by the same route while its AST goes to pedagogy. Nothing new is needed; nothing new can break.

**Option B — a `FormulaBlock` rendered from the AST. No LaTeX engine, no new dependency.**
K-9 arithmetic needs exactly four constructs, and every one is a Flutter primitive:

| node | widget |
|---|---|
| `FRACTION` | a `Column` of numerator, a 1-2 px `Container` rule, denominator, baseline-aligned |
| `POWER` | a `Row` with the exponent in a smaller style, top-aligned |
| `ADD/SUB/MUL/DIV/EQ` | a `Row` with the operator glyph and symmetric padding |
| `UNIT` / `QUANTITY` | a `Row`; `UNIT.exp` renders as a superscript, `UNIT.den` after a solidus |

`ROW` and `ITEM` are a `Wrap` and a label. That is the whole renderer. **`latex` is provided for
interchange and for a future engine; it is not required to draw any of this.**

What Lane B needs from A2, and nothing more:
* the `ast` JSON above (kinds are closed and versioned with the lane),
* `bbox` + `crop` for the fallback,
* `disposition` — anything that is not `TRUSTED` renders as the source fallback, never as text.

What A2 needs from Lane B: a decision between A and B, and — if B — the block type name and where
in the `LessonBlock` union it sits. **The bridge (`tsl_to_lesson_document.py:70-81`) has no
`formula` key today, so a formula role becomes `unknown_role:formula` and is withheld**; adding the
key is only worth doing once there is something on the other side to receive it.

**Accessibility, deliberately deferred**: the app has two `Semantics(` widgets, neither on content,
no `semanticsLabel` anywhere, no TTS implementation and no export surface (audit §8 I). So there is
no MathML consumer today. The AST is the right place to generate one from when a consumer appears —
which is another reason for the AST, not LaTeX, to be canonical.

---

## 4 · Chemistry (§7) — the model, declared, not yet built

`CHEM` (`tc2_sdm.py:246`) is a shape regex that never checks whether its letters name an element,
and it fires **173 times** in the round-4 review set with **≥40 non-chemical matches** — `VD2` (a
teacher's-book cross-reference), `S2` (the ohm sign **Ω** misread, in physics), `I1` (Roman **II**
in a physics heading, the Founder's named defect), `A3` (a paper size), `E5` (a fuel grade). The
structured model below is what would replace shape-matching; it is **research-only** until a
recogniser and an independent validator exist for it.

```jsonc
"ChemicalFormula": { "terms": [ {"element": "Ag", "subscript": 1},
                                {"element": "N",  "subscript": 1},
                                {"element": "O",  "subscript": 3} ],
                     "charge": 0, "coefficient": 1 }
"ChemicalReaction": { "lhs": [ChemicalFormula…], "rhs": [ChemicalFormula…],
                      "arrow": "->" | "<->" | "^" | "v" }
```

The validators that would earn a restore, none of which is world knowledge dressed up as evidence:
* **element-symbol closure** — every `element` must be a real symbol from a fixed table; `VD`, `I1`
  and `A3` are not, so the false positives disappear by construction;
* **subscript raster geometry** — the digit must sit *below* the baseline, the same check that
  separates a real exponent from a degree sign in physics;
* **charge/coefficient balance** for a reaction — deterministic, and stated by the page itself.

Until those exist, chemistry stays withheld with its crop, and the audit's recommendation stands:
the fix that generalises is the same as §1b — **key on structure, not on shape.**
