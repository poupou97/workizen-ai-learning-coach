FOUNDER DECISION — STEM STRUCTURED DATA

Audit accepted.

Founder confirms this is a real architecture gap.

P0 decision:

STOP treating flattened OCR text as the canonical representation
of mathematical/scientific expressions.

Do NOT attempt to solve this primarily by adding more regex guards.

==================================================
1. BUILD THE MISSING STRUCTURED STEM PATH
==================================================

Design and implement a bounded Round-5 POC:

SOURCE REGION
→ preserve line/token geometry
→ expression detection
→ specialized recognition candidate
→ canonical structured representation
→ deterministic validation
→ source cross-check
→ VALIDATED / WITHHELD
→ mobile rendering.

For Math introduce a bounded canonical model equivalent to:

MathExpression
- sourceBlockId
- source page
- bbox
- source line/token geometry
- raw observations
- latex
- structured AST
- validation evidence
- provenance
- disposition.

LaTeX = rendering/interchange representation.

Math AST = machine/pedagogy representation.

Neither OCR text nor LLM output is automatically truth.

==================================================
2. FIX STRUCTURE LOSS FIRST
==================================================

Before trying better OCR:

preserve per-line/per-token geometry through:

OCR
→ SDM
→ TSL
→ LessonDocument.

Do not discard geometry at the currently identified flattening points.

Flat text may remain as a projection,
but must no longer be the only representation.

==================================================
3. REMOVE THE UNSAFE LEGACY MATH PATH
==================================================

P0 audit/harden:

raw OCR
→ rebuild_fractions.py
→ build_lesson_index.py
→ toanExercises.

Do not allow INFERRED geometry-rebuilt expressions
to become trusted/shipped teaching content after their
INFERRED status and provenance are dropped.

Preserve status/provenance or fail closed.

Do not silently construct mathematical truth from geometry.

==================================================
4. CLOSE LATENT FORMULA TRUST HOLE
==================================================

A formula-labelled block must NOT automatically receive trust 0.95
and bypass math/unit/chem validation.

Before enabling any Docling formula enrichment:

FORMULA
must enter the structured STEM validation path.

Add regression tests now so future activation cannot accidentally
turn formula recognition into trusted teaching content.

==================================================
5. MATH POC
==================================================

Start with actual failures, not synthetic demos:

- `3/10 + 5/21 → 10 +`
- stacked fractions
- exponent `10⁸ → 10°`
- superscript/subscript
- + − × ÷ =
- dangling operators
- numbers split across geometry.

Compare bounded candidates for formula recognition.

Do not select a dependency only from benchmark claims.

Measure on our real Vietnamese textbook failures.

==================================================
6. PHYSICS
==================================================

Design bounded:

PhysicsExpression
= MathExpression
+ Symbol
+ Quantity
+ Unit.

At minimum POC must understand the difference between:

10⁸
10°
m/s
m/s²

and detect impossible structural transformations such as:

`3×10⁸ m/s`
→
`3×10° m/s`.

==================================================
7. CHEMISTRY
==================================================

Research/design bounded structured representation for:

ChemicalFormula
ChemicalReaction

including:
- element;
- coefficient;
- subscript;
- superscript/charge;
- reaction arrow.

Do not continue treating Chemistry as regex-shaped text only.

Implementation can remain research/POC until independently proven.

==================================================
8. MULTI-SIGNAL ACCURACY RECOVERY
==================================================

Structured STEM does not replace the Round-5 accuracy architecture.

Continue:

OCR/parser
+ structural validation
+ specialized domain validation
+ cross-corpus consistency
+ LLM anomaly/correction candidate
+ authoritative external verification where appropriate
+ human/user correction.

LLM/Internet/User Correction = evidence/correction sources.

None may silently overwrite canonical truth.

==================================================
9. MOBILE
==================================================

Research/POC mobile rendering using:

Text → native text
Math → LaTeX-capable renderer
Physics → Math renderer + semantic units
Chemistry → structured chemistry/scientific renderer
Unsupported/unvalidated → WITHHELD/source fallback.

Do not use Markdown/HTML/plain text as canonical STEM truth.

==================================================
10. SUCCESS CRITERIA
==================================================

Round-5 STEM POC must demonstrate on REAL failures:

1. structure survives OCR → SDM → TSL → LessonDocument;
2. `3/10 + 5/21` remains structurally correct;
3. `10⁸` cannot silently become `10°`;
4. validated expressions can be safely RESTORED;
5. mobile renders them correctly;
6. pedagogy receives AST/structured semantics rather than flattened text;
7. false correction is measured;
8. provenance remains end-to-end.

Report:

CURRENT
→ POC
→ BEFORE/AFTER accuracy
→ RESTORED expressions
→ FALSE CORRECTIONS
→ remaining failures
→ performance/cost
→ dependency/licence implications.

No mass corpus conversion.
No production trust threshold.
No merge.

Continue Round 5 autonomously.
READY FOR FOUNDER REVIEW.
