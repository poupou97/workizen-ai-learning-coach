#!/usr/bin/env python3
"""`MathExpression` — the canonical object the Founder's §1 asks for.

    MathExpression{ sourceBlockId, source page, bbox, source line/token geometry,
                    raw observations, latex, structured AST, validation evidence,
                    provenance, disposition }

Three rules are enforced in code rather than asserted in prose:

  1. **The AST is canonical.** `latex` and `text` are computed properties, not fields. There is no
     setter and no `from_latex`, so a rendering string can never become the structure.
  2. **A source observation is never overwritten.** `observations` is a tuple of frozen records and
     the original block text is kept beside the proposal, never in place of it.
  3. **Nothing is servable until an independent validator says so.** `disposition` starts at
     `REPAIRED_CANDIDATE`; `validate()` may move it to `VALIDATED_REPAIR` or `WITHHELD`, and only a
     separate, Founder-gated act could ever make it `TRUSTED` — which this module cannot do.

`source_geometry` is the field §2 asks Lane A1 to expose on the SDM block. Its shape is declared in
`docs/research/MATH-ACCURACY-STRUCTURED-CONTRACT.md`; `from_sdm_block` reads A1's field when it is
present and falls back to the OCR body file otherwise, so this lane is not blocked and does not
fork the geometry.
"""
from dataclasses import dataclass, field

from . import nodes as A

REPAIRED_CANDIDATE = 'REPAIRED_CANDIDATE'
VALIDATED_REPAIR = 'VALIDATED_REPAIR'
WITHHELD = 'WITHHELD'


@dataclass(frozen=True)
class TokenGeometry:
    """One placed observation: what a source read, and where. Immutable, forever."""
    text: str
    bbox: tuple             # (x, y, w, h), normalised, y down
    source: str             # 'apple-vision-ocr-line' | 'page-raster-300dpi' | …
    index: int = -1
    conf: float = 1.0

    def to_json(self):
        return dict(text=self.text, bbox=[round(v, 6) for v in self.bbox],
                    source=self.source, index=self.index, conf=self.conf)


@dataclass
class MathExpression:
    """One printed expression, with everything needed to audit or to refuse it."""
    source_block_id: str
    book: str
    page_pdf: int
    page_printed: int = None
    bbox: tuple = None                       # the region's own box on the page
    crop: str = None                         # the fallback that survives a refusal
    ast: A.Node = None
    observations: tuple = ()                 # TokenGeometry — never rewritten
    source_geometry: tuple = ()              # every OCR line under the block, as handed to us
    original_text: str = None                # what the block said BEFORE any repair
    rule_id: str = None
    recognition: tuple = ()                  # each candidate + which recogniser produced it
    validations: tuple = ()                  # ValidationResult-shaped dicts
    provenance: dict = field(default_factory=dict)
    disposition: str = REPAIRED_CANDIDATE
    reasons: tuple = ()

    # ---- projections. Properties, not fields: they cannot be set, so they cannot become truth.
    @property
    def latex(self):
        return self.ast.to_latex() if self.ast else None

    @property
    def text(self):
        return self.ast.to_text() if self.ast else None

    @property
    def servable(self):
        """Never true here. A VALIDATED_REPAIR is eligible; TRUSTED is a separate Founder act."""
        return False

    def to_json(self):
        return dict(
            sourceBlockId=self.source_block_id, book=self.book,
            pagePdf=self.page_pdf, pagePrinted=self.page_printed,
            bbox=list(self.bbox) if self.bbox else None, crop=self.crop,
            ast=self.ast.to_json() if self.ast else None,
            latex=self.latex, textProjection=self.text,
            originalText=self.original_text,
            observations=[o.to_json() for o in self.observations],
            sourceGeometry=[o.to_json() for o in self.source_geometry],
            ruleId=self.rule_id,
            recognition=[dict(r) for r in self.recognition],
            validations=[dict(v) for v in self.validations],
            provenance=dict(self.provenance),
            disposition=self.disposition, reasons=list(self.reasons))

    # ---- disposition
    def record(self, validations):
        """Apply validator results. One rejection withholds; no confirmation withholds."""
        self.validations = tuple(validations)
        verdicts = [v.get('verdict') for v in validations]
        if 'FAIL' in verdicts:
            self.disposition = WITHHELD
            self.reasons = tuple(v['validator_id'] for v in validations if v.get('verdict') == 'FAIL')
        elif 'PASS' in verdicts:
            self.disposition = VALIDATED_REPAIR
            self.reasons = ()
        else:
            self.disposition = WITHHELD
            self.reasons = ('no_validator_confirmed',)
        return self.disposition


def withheld(source_block_id, book, page_pdf, *, bbox=None, crop=None, reasons=(),
             original_text=None, source_geometry=(), **kw):
    """A region the lane found and refused. It keeps its box and its crop, and carries no AST.

    This is the object that makes «withhold» honest: the region is *named*, so a consumer knows a
    formula was refused here — instead of the block being filed as «empty — no letters», which is
    what happens to 14 of 15 Docling formula regions today (see the audit, §3 C4).
    """
    return MathExpression(source_block_id=source_block_id, book=book, page_pdf=page_pdf,
                          bbox=bbox, crop=crop, ast=None, reasons=tuple(reasons),
                          original_text=original_text, source_geometry=tuple(source_geometry),
                          disposition=WITHHELD, **kw)


def geometry_from_sdm_block(block, ocr_tokens=None):
    """The per-line geometry under one SDM block.

    Reads Lane A1's additive `lines` field when the block carries it (§2), and falls back to the
    OCR body file otherwise. One reader, so the two lanes cannot drift: when A1 ships the field this
    function starts using it with no change here.
    """
    lines = block.get('lines')
    if lines:
        return tuple(TokenGeometry(text=l.get('text', ''),
                                   bbox=tuple(l['bbox']) if 'bbox' in l
                                   else (l['x'], l['y'], l['w'], l['h']),
                                   source=l.get('source', 'apple-vision-ocr-line'),
                                   index=l.get('index', -1), conf=l.get('conf', 1.0))
                     for l in lines)
    bb = block.get('bbox')
    if not bb or not ocr_tokens:
        return ()
    x, y, w, h = bb
    return tuple(TokenGeometry(text=t.text, bbox=(t.x, t.y, t.w, t.h),
                               source='apple-vision-ocr-line', index=t.index, conf=t.conf)
                 for t in ocr_tokens
                 if x - 0.004 <= t.cx <= x + w + 0.004 and y - 0.004 <= t.cy <= y + h + 0.004)
