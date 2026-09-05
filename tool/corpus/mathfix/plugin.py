#!/usr/bin/env python3
"""The Lane A2 repairer, registered against Lane A1's repair registry.

Failure class: **`formula_flattened`** — a printed expression whose structure the text extractors
flattened. The repairer proposes; four deterministic checks, none of which produced the proposal,
decide. Nothing here can serve anything: a validated candidate becomes `VALIDATED_REPAIR`, and
whether a `VALIDATED_REPAIR` is ever `TRUSTED` is a separate, Founder-gated act that does not exist.

What this plugin claims to cover, and what it does not:

    covers   math_guard · unit_guard · agree_text · agree_numbers
             — «this block carries arithmetic the pipeline would not vouch for», and «the two OCR
               stacks disagreed about its text or its numbers». The page itself settles both.
    does NOT cover  agree_order (the block's place in the page's reading order is not a question the
             raster of one block can answer) · low_ocr_conf · any role, figure or page-feature guard.

A block withheld for a reason outside the covered set stays withheld: A1's engine keeps it, because
`covers_reasons` is what it subtracts. That is the intended behaviour and there is a test for it.
"""
from . import detect as D
from . import extract as E
from . import validate as V
from .adapter import MODEL, REGISTRY
from .tokens import median_height

FAILURE_CLASS = 'formula_flattened'
REPAIRER_ID = 'mathfix.math-line-v1'
VALIDATOR_ID = 'mathfix.deterministic-v1'
COVERS_REASONS = ('math_guard', 'unit_guard', 'agree_text', 'agree_numbers')

# Confidence is a repairer's own report of how much structure it had to work with. It is NOT a
# probability of correctness and NOTHING may threshold on it: the verdict comes from the validators.
_CONFIDENCE = 0.6


class PageContext:
    """The page evidence a repairer needs, prepared once per page by the caller.

    Passed in `RepairContext.extra['mathfix_page']`. Building it needs a page raster (PyMuPDF), so
    it is the CALLER's job — a plugin that reached out and rendered a PDF on its own would be a
    plugin with a side effect.
    """

    def __init__(self, mask, tokens, regions=None):
        self.mask = mask
        self.tokens = tokens
        self.regions = regions if regions is not None else D.find_fraction_regions(mask, tokens)
        self.text_height = median_height(tokens) or 0.018

    def within(self, bbox, pad=0.004):
        x, y, w, h = bbox
        toks = [t for t in self.tokens if x - pad <= t.cx <= x + w + pad and y - pad <= t.cy <= y + h + pad]
        regs = [r for r in self.regions
                if x - pad <= r.bar.cx <= x + w + pad and y - pad <= r.bar.cy <= y + h + pad]
        return toks, regs


def _observations(ctx, cand):
    """The candidate's own citations, as framework Observations — never the block's stored text.

    Each OCR line and each raster bar that contributed a character becomes one immutable
    `Observation`, so the trace names exactly what was read and where, not «the block said X».
    """
    out = []
    for o in cand.original_observations:
        src = 'apple-vision-ocr-line' if o['kind'] == 'ocr_line' else 'page-raster-300dpi'
        out.append(MODEL.Observation(block_id=ctx.block_id, source=src, value=o.get('text', ''),
                                     provenance=dict(bbox=list(o['bbox']),
                                                     ocr_index=o.get('index'), conf=o.get('conf'))))
    return out


def _signals(results):
    """The validator readings, as framework Signals on the Founder's layer letters.

    Layer B is layout/geometry (the printed bar), layer C the deterministic checks. A validator that
    returned NOT_APPLICABLE ABSTAINS — it is recorded, never counted as support.
    """
    layer = {'vinculum-raster-v1': 'B', 'ink-accounted-v1': 'B', 'operator-raster-v1': 'B',
             'structure-grammar-v1': 'C', 'digit-provenance-v1': 'C', 'arith-selfcheck-v1': 'C'}
    out = []
    for r in results:
        verdict = {'PASS': MODEL.SignalVerdict.SUPPORTS,
                   'FAIL': MODEL.SignalVerdict.OBJECTS,
                   'NOT_APPLICABLE': MODEL.SignalVerdict.ABSTAINS}[r.verdict]
        out.append(MODEL.Signal(signal_id=f'{layer[r.validator_id]}.{r.validator_id.replace("-", "_")}',
                                verdict=verdict,
                                strength=(1.0 if verdict == MODEL.SignalVerdict.SUPPORTS else 0.0),
                                detail=dict(r.evidence)))
    return out


def _prepare(ctx):
    page = ctx.extra.get('mathfix_page') if getattr(ctx, 'extra', None) else None
    bbox = (ctx.page or {}).get('bbox')
    if page is None or not bbox:
        return None, None, None
    toks, regs = page.within(bbox)
    return page, toks, regs


def propose(ctx):
    """The repairer. Returns 0 or 1 candidate — a repairer with nothing to say says nothing."""
    page, toks, regs = _prepare(ctx)
    if page is None or not regs:
        return ()
    cand = E.math_line_candidate(toks, regs, page.mask)
    if not cand.proposed_value:
        return ()
    bbox = ctx.page['bbox']
    bb = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
    bar_len = sorted(r.bar.length for r in regs)[len(regs) // 2]
    _, results = V.validate(cand, page.mask, bb, median_height(toks) or page.text_height, bar_len)
    return (MODEL.RepairCandidate(
        block_id=ctx.block_id,
        failure_class=FAILURE_CLASS,
        original_observations=_observations(ctx, cand),
        proposed_value=cand.proposed_value,
        rule_id=cand.rule_id,
        supporting_signals=_signals(results),
        confidence=_CONFIDENCE,
        provenance=dict(covers_reasons=COVERS_REASONS, lane='A2',
                        detector='mathfix.stacked-fraction-raster-v1'),
        detected=dict(fraction_regions=len(regs),
                      extractable=sum(1 for r in regs if r.extractable),
                      region_reasons=sorted({r.reason for r in regs if r.reason}))),)


def validate_candidate(candidate, ctx):
    """The validator. Re-runs the deterministic checks against the PAGE, not against the candidate's
    own report of them, so a malformed or hand-built candidate cannot validate itself."""
    page, toks, regs = _prepare(ctx)
    if page is None or not regs:
        return MODEL.ValidationResult(VALIDATOR_ID, MODEL.Verdict.INSUFFICIENT,
                                      detail=dict(reason='no page evidence for this block'))
    cand = E.math_line_candidate(toks, regs, page.mask)
    if cand.proposed_value != candidate.proposed_value:
        return MODEL.ValidationResult(
            VALIDATOR_ID, MODEL.Verdict.REJECTED,
            evidence=[dict(check='reproducibility', expected=cand.proposed_value,
                           got=candidate.proposed_value)],
            detail=dict(reason='the page does not reproduce this value'))
    bbox = ctx.page['bbox']
    bb = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
    bar_len = sorted(r.bar.length for r in regs)[len(regs) // 2]
    verdict, results = V.validate(cand, page.mask, bb, median_height(toks) or page.text_height, bar_len)
    evidence = [dict(check=r.validator_id, verdict=r.verdict, **r.evidence) for r in results]
    if any(r.verdict == 'FAIL' for r in results):
        out = MODEL.Verdict.REJECTED
    elif verdict == 'RESTORE':
        out = MODEL.Verdict.VALIDATED
    else:
        out = MODEL.Verdict.INSUFFICIENT
    return MODEL.ValidationResult(VALIDATOR_ID, out, evidence=evidence,
                                  detail=dict(applicable=[r.validator_id for r in results
                                                          if r.verdict != 'NOT_APPLICABLE']))


_REGISTERED = False


def register(registry=None):
    """Register with Lane A1's registry (or the stand-in). Idempotent."""
    global _REGISTERED
    reg = registry or REGISTRY
    if _REGISTERED and registry is None:
        return reg
    reg.repairer(FAILURE_CLASS, REPAIRER_ID)(propose)
    reg.validator(FAILURE_CLASS, VALIDATOR_ID)(validate_candidate)
    if registry is None:
        _REGISTERED = True
    return reg
