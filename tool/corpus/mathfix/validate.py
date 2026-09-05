#!/usr/bin/env python3
"""Deterministic validation — the only thing that may turn a candidate into a restored formula.

Round 4 falsified «OCR_A == OCR_B ⇒ TEXT == TRUE»: two stacks make the same error. So agreement is
not a validator here. Each check below is a signal that did NOT produce the candidate:

  `vinculum-raster-v1`   the printed bar is really there, and is drawn LONGER than both halves —
                         the typographic fact that makes a fraction a fraction. Detection only
                         asked whether ink sat above and below; this asks about the bar's own size
                         relative to what it separates.
  `ink-accounted-v1`     inside the region's own box, every column of printed ink is covered by an
                         observation that contributed to the value. This is the check that catches
                         a DROPPED DIGIT: on Toán 5 tập một p23 the OCR read «14/5» as «4», and
                         29.6 % of the bar's width is ink no token accounts for. Bounding-box vs
                         source comparison, exactly as ordered.
  `digit-provenance-v1`  no character was invented (multiset, not substring — so a value that
                         reordered or duplicated printed digits fails).
  `arith-selfcheck-v1`   where the book states both sides of an equality, the restored arithmetic
                         must be true. NOT_APPLICABLE is not a pass, and is reported as such.

A candidate is RESTORED only when every applicable validator PASSes. One FAIL, or a rule with no
applicable validator at all, and the region stays WITHHELD with its crop.
"""
import re
from dataclasses import dataclass
from fractions import Fraction

# ---- calibrated against the real pages, and stated as ratios of the bar's own length
MIN_BAR_OVERHANG = 1.02      # the vinculum must be at least this much longer than the wider half
MAX_INK_UNACCOUNTED = 0.10   # share of the region's glyph ink that may be covered by nothing
MAX_UNACCOUNTED_RUN = 0.25   # the widest UNBROKEN run of it, in bar lengths — see `widest_unaccounted_run`
BOX_MARGIN_X = 0.02          # OCR box jitter allowance, in bar lengths
BOX_MARGIN_Y = 0.30          # ditto vertically, in text heights (accents and descenders)


@dataclass(frozen=True)
class ValidationResult:
    verdict: str            # 'PASS' | 'FAIL' | 'NOT_APPLICABLE'
    evidence: dict
    validator_id: str


# ---------------------------------------------------------------- 1 · the bar is really a vinculum
def vinculum_raster(region, mask):
    bar = region.bar
    barlen = bar.px1 - bar.px0
    runs = [r for r in mask.row_runs(bar.py0 + (bar.py1 - bar.py0) // 2, bar.px0 - 2, bar.px1 + 2)
            if r[1] >= 0.6 * barlen]
    if len(runs) != 1:
        return ValidationResult('FAIL', dict(reason='bar_is_not_one_run', runs=len(runs)),
                                'vinculum-raster-v1')
    above = region.ink_above_wide or region.ink_above
    below = region.ink_below_wide or region.ink_below
    if not (above and below):
        return ValidationResult('FAIL', dict(reason='no_ink_on_one_side'), 'vinculum-raster-v1')
    widest = max((above[1] - above[0]), (below[1] - below[0])) * mask.width
    overhang = barlen / widest if widest else 0.0
    ok = overhang >= MIN_BAR_OVERHANG
    return ValidationResult('PASS' if ok else 'FAIL',
                            dict(bar_px=barlen, widest_half_px=round(widest, 1),
                                 overhang=round(overhang, 3), floor=MIN_BAR_OVERHANG),
                            'vinculum-raster-v1')


# ---------------------------------------------------------------- 2 · nothing printed was dropped
def _px_boxes(boxes, mask, mx, my):
    out = []
    for b in boxes:
        out.append((b[0] * mask.width - mx, b[1] * mask.height - my,
                    b[2] * mask.width + mx, b[3] * mask.height + my))
    return out


def _scan(mask, bbox, token_boxes, bar_boxes, text_height, bar_len):
    """(glyph ink px, unaccounted px, widest unbroken unaccounted run px) inside `bbox`.

    Both the count and the ratio exclude ink covered by a `bar_box`, and that is the whole point:
    a vinculum is a solid 9-pixel-thick run, several times the ink of the digits it separates, so
    leaving it in would dilute a whole dropped digit down to a few per cent and the check would
    never fire. What is being asked is «of the printed glyphs in this region, how much did no OCR
    token read?» — the bar is not a glyph.

    Rows are scanned through `row_runs`, so this is a C-speed scan per row rather than a per-pixel
    Python loop over the box.
    """
    px0, px1 = int(bbox[0] * mask.width), int(bbox[2] * mask.width)
    mx = BOX_MARGIN_X * bar_len * mask.width
    my = BOX_MARGIN_Y * text_height * mask.height
    py0 = max(0, int(bbox[1] * mask.height - my))
    py1 = min(mask.height, int(bbox[3] * mask.height + my))
    toks = _px_boxes(token_boxes, mask, mx, my)
    rules = _px_boxes(bar_boxes, mask, mx, my)
    glyph = unaccounted = widest = 0
    for y in range(py0, py1):
        on_tok = [b for b in toks if b[1] <= y < b[3]]
        on_rule = [b for b in rules if b[1] <= y < b[3]]
        run = 0
        for start, ln in mask.row_runs(y, px0, px1):
            for x in range(start, start + ln):
                if any(b[0] <= x < b[2] for b in on_rule):
                    run = 0
                    continue
                glyph += 1
                if any(b[0] <= x < b[2] for b in on_tok):
                    run = 0
                else:
                    unaccounted += 1
                    run += 1
                    widest = max(widest, run)
            run = 0
    return glyph, unaccounted, widest


def ink_accounted(mask, bbox, token_boxes, bar_boxes, text_height, bar_len):
    """(share, glyph px, unaccounted px) — how much of the printed glyph ink no token read."""
    glyph, un, _ = _scan(mask, bbox, token_boxes, bar_boxes, text_height, bar_len)
    return (un / glyph if glyph else 0.0), glyph, un


def widest_unaccounted_run(mask, bbox, token_boxes, bar_boxes, text_height, bar_len):
    """The widest UNBROKEN horizontal run of unaccounted ink, in bar lengths.

    Area is the wrong unit for a dropped operator. On Toán 5 tập một p22 the «−» of «20/18 − 2/5»
    is 3.75 % of the block's glyph ink — under any ceiling one would dare set — but it is an
    unbroken 42-pixel run, 45 % of a bar. Area says «rounding error»; shape says «a printed mark
    nobody read». Shape is right, and round 3 already paid for the other answer: «2/5 + 1/4» was
    served for a printed «2/5 − 1/4».
    """
    _, _, widest = _scan(mask, bbox, token_boxes, bar_boxes, text_height, bar_len)
    return widest / (bar_len * mask.width) if bar_len else 0.0


def ink_accounted_v1(candidate, mask, bbox, text_height, bar_len):
    toks, rules = [], []
    for o in candidate.original_observations:
        x, y, w, h = o['bbox']
        (rules if o['kind'] == 'raster_bar' else toks).append((x, y, x + w, y + h))
    glyph, un, widest = _scan(mask, bbox, toks, rules, text_height, bar_len)
    share = (un / glyph) if glyph else 0.0
    run = widest / (bar_len * mask.width) if bar_len else 0.0
    ok = share <= MAX_INK_UNACCOUNTED and run <= MAX_UNACCOUNTED_RUN
    return ValidationResult('PASS' if ok else 'FAIL',
                            dict(unaccounted_share=round(share, 4), glyph_ink_px=glyph,
                                 unaccounted_px=un, widest_unaccounted_run=round(run, 4),
                                 ceiling=MAX_INK_UNACCOUNTED, run_ceiling=MAX_UNACCOUNTED_RUN),
                            'ink-accounted-v1')


# ---------------------------------------------------------------- 3 · no character was invented
def digit_provenance_v1(candidate):
    from .extract import digit_provenance
    missing = digit_provenance(candidate)
    return ValidationResult('PASS' if not missing else 'FAIL',
                            dict(invented=''.join(sorted(set(missing)))),
                            'digit-provenance-v1')


# ---------------------------------------------------------------- 4 · the arithmetic is true
_ENUM = re.compile(r'^\s*[a-eA-E]\s*[)\].]\s*')
_TERM = re.compile(r'^\s*(\d+)\s*/\s*(\d+)|^\s*(\d+(?:[.,]\d+)?)')
_OP = re.compile(r'^\s*([+\-–—−×x*÷:])')


def _eval_side(s):
    """Exact value of a simple printed arithmetic side, or None when it is not one.

    Left-to-right with no precedence is NOT used: precedence is honoured, because the printed
    expressions this touches are ordinary school arithmetic. A side that does not parse completely
    returns None, and the validator then reports NOT_APPLICABLE rather than inventing a reading.
    """
    terms, ops = [], []
    rest = s
    while True:
        m = _TERM.match(rest)
        if not m:
            return None
        if m.group(1) is not None:
            if int(m.group(2)) == 0:
                return None
            terms.append(Fraction(int(m.group(1)), int(m.group(2))))
        else:
            terms.append(Fraction(m.group(3).replace(',', '.')))
        rest = rest[m.end():]
        if not rest.strip():
            break
        m = _OP.match(rest)
        if not m:
            return None
        ops.append(m.group(1))
        rest = rest[m.end():]
    # × ÷ first, then + −
    i = 0
    while i < len(ops):
        if ops[i] in ('×', 'x', '*', '÷', ':'):
            b = terms.pop(i + 1)
            a = terms.pop(i)
            if ops[i] in ('÷', ':') and b == 0:
                return None
            terms.insert(i, a * b if ops[i] in ('×', 'x', '*') else a / b)
            ops.pop(i)
        else:
            i += 1
    acc = terms[0]
    for op, t in zip(ops, terms[1:]):
        acc = acc + t if op == '+' else acc - t
    return acc


def arith_selfcheck_v1(candidate):
    v = _ENUM.sub('', candidate.proposed_value or '')
    sides = [s for s in re.split(r'=', v) if s.strip()]
    if len(sides) < 2:
        return ValidationResult('NOT_APPLICABLE', dict(reason='the page states no equality'),
                                'arith-selfcheck-v1')
    vals = [_eval_side(s) for s in sides]
    if any(x is None for x in vals):
        return ValidationResult('NOT_APPLICABLE', dict(reason='a side does not parse as arithmetic'),
                                'arith-selfcheck-v1')
    ok = all(x == vals[0] for x in vals)
    return ValidationResult('PASS' if ok else 'FAIL',
                            dict(sides=[str(x) for x in vals]), 'arith-selfcheck-v1')


# ---------------------------------------------------------------- the verdict
def overall_verdict(results):
    """RESTORE requires at least one PASS and no FAIL.

    A candidate whose every validator returned NOT_APPLICABLE is NOT restored: «nothing
    contradicted it» is not evidence, and this is the one place where that could quietly become the
    default. An empty result list is a WITHHOLD for the same reason.
    """
    if any(r.verdict == 'FAIL' for r in results):
        return 'WITHHOLD'
    if not any(r.verdict == 'PASS' for r in results):
        return 'WITHHOLD'
    return 'RESTORE'


def validate(candidate, mask, bbox, text_height, bar_len):
    """Every applicable check, plus the single overall verdict."""
    if not candidate.proposed_value:
        return 'WITHHOLD', []
    results = [ink_accounted_v1(candidate, mask, bbox, text_height, bar_len),
               digit_provenance_v1(candidate),
               arith_selfcheck_v1(candidate)]
    for r in candidate.regions:
        results.append(vinculum_raster(r, mask))
    return overall_verdict(results), results
