#!/usr/bin/env python3
"""Lane A2's provider for Lane A1's third-signal **layer C** (`repair.signals.numeric`).

A1 owns the interface and a fail-closed default: *any* proposal that changes the digit or operator
sequence of the observed text OBJECTS, because a Vietnamese diacritic repair must never move a digit.
That default is right for a text lane and wrong for this one — every fraction restoration changes
the digit sequence, by construction. A1 left the slot for the lane that can prove the difference.

The rule this provider follows, and the only one it can honestly follow:

    **Support only from the page. Object from the strings. Never relax without evidence.**

  · With page evidence in the context (`extra['mathfix_page']` plus the block's bbox) the provider
    re-derives the expression from the raster and the OCR geometry and answers with the verdict of
    the six deterministic checks. That is a positive signal, and it is the only thing that produces
    one here.
  · Without page evidence it can still say what is deterministically FALSE of two strings — an
    invented digit, an operator that changed identity or vanished — and OBJECTS. Where it has
    nothing to add it returns `None` and A1's fail-closed default stands.

So this provider is never more permissive than the default unless it has looked at the page. That
matters after `c) 16/21 × 3/5` came back as `16/21 - 3/5` with a clean audit trail: an operator can
change identity while every digit stays put, and a rule that only counts digits would wave it past.
"""
from collections import Counter

from . import extract as E
from . import validate as V
from .nodes import OP_OF_MARK
from .tokens import median_height

SIGNAL_ID = 'C.numeric'
PROVIDER_ID = 'mathfix.numeric-v1'


def _digits(text):
    return Counter(c for c in (text or '') if c.isdigit())


def _operators(text):
    return Counter(OP_OF_MARK[c] for c in (text or '') if c in OP_OF_MARK)


def _page_of(ctx):
    extra = getattr(ctx, 'extra', None) or {}
    page = extra.get('mathfix_page')
    bbox = (getattr(ctx, 'page', None) or {}).get('bbox')
    return (page, bbox) if (page is not None and bbox) else (None, None)


def provider(observed_text, proposed_text, ctx=None, model=None):
    """`(observed, proposed, ctx) -> Signal | None`. See the module docstring for the contract."""
    if model is None:
        from .adapter import MODEL as model
    sv = model.SignalVerdict

    page, bbox = _page_of(ctx)
    if page is not None:
        toks, regs = page.within(bbox)
        if not regs:
            return None                       # no printed fraction here: not this lane's to judge
        cand = E.math_line_candidate(toks, regs, page.mask)
        if cand.proposed_value != proposed_text:
            return model.Signal(SIGNAL_ID, sv.OBJECTS, 1.0,
                                dict(provider=PROVIDER_ID, reason='the page does not reproduce this value',
                                     page_value=cand.proposed_value, proposed=proposed_text))
        bb = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
        bar_len = sorted(r.bar.length for r in regs)[len(regs) // 2]
        verdict, results = V.validate(cand, page.mask, bb, median_height(toks) or page.text_height,
                                      bar_len)
        detail = dict(provider=PROVIDER_ID,
                      checks={r.validator_id: r.verdict for r in results},
                      applicable=[r.validator_id for r in results if r.verdict != 'NOT_APPLICABLE'])
        if any(r.verdict == 'FAIL' for r in results):
            return model.Signal(SIGNAL_ID, sv.OBJECTS, 1.0, detail)
        if verdict == 'RESTORE':
            return model.Signal(SIGNAL_ID, sv.SUPPORTS, 1.0, detail)
        return model.Signal(SIGNAL_ID, sv.ABSTAINS, 0.0, detail)

    # ---- no page: say only what is false of the two strings, and otherwise fall through
    od, pd = _digits(observed_text), _digits(proposed_text)
    invented = {c: n for c, n in (pd - od).items()}
    if invented:
        return model.Signal(SIGNAL_ID, sv.OBJECTS, 1.0,
                            dict(provider=PROVIDER_ID, reason='a digit that is not in the observation',
                                 invented=invented))
    oo, po = _operators(observed_text), _operators(proposed_text)
    if oo != po:
        return model.Signal(SIGNAL_ID, sv.OBJECTS, 1.0,
                            dict(provider=PROVIDER_ID,
                                 reason='an operator changed identity or vanished',
                                 observed=dict(oo), proposed=dict(po)))
    return None                                # A1's fail-closed default stands


def register(numeric_module=None):
    """Install the provider in A1's `repair.signals.numeric`. Returns False when it is not present."""
    mod = numeric_module
    if mod is None:
        try:
            from repair.signals import numeric as mod       # noqa: PLC0415
        except Exception:
            return False
    mod.register_provider(provider)
    return True
