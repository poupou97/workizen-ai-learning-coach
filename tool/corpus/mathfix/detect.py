#!/usr/bin/env python3
"""Formula REGION detection — from the printed page first, from the OCR second.

The false-trust audit's worst class is Toán, and the round-3 failure that made it worst was
arithmetic served that was *never on the page*: an expression assembled out of the fragments a
flattened OCR line happened to leave behind. So the region is found the other way round here.

  1. The page raster gives horizontal ink runs (`bars`).
  2. A run is a VINCULUM candidate when the page shows, within the run's own x-extent,
     ink above it and ink below it that is DETACHED from it — the printed picture of a fraction.
     That single geometric fact separates a fraction bar from a «+» (whose stroke is attached), a
     lone «−» (nothing above or below), an underline (nothing below) and an «=» (whose neighbour is
     another bar, not a digit).
  3. Only then do the OCR tokens get a say, and only to name the two halves. A half is named ONLY
     by a bare digit run sitting in the strip, and ONLY when exactly one candidate is there.

The consequence that matters: a region whose digits the OCR destroyed is still FOUND. It is
reported `extractable=False` with a reason, so the pipeline can withhold that region and keep its
crop — the printed formula survives as an image — instead of serving the fragment beside it.

Nothing in this module proposes a value; that is `extract`.
"""
import re
from dataclasses import dataclass

from . import bars as BARS
from .tokens import Token, median_height

# ---- calibrated on the real pages (Toán 4 tập hai p080-083 / p116-122, Toán 5 tập một p020-024,
#      300 dpi). The numbers below are ratios of the page's OWN text height or of the bar's own
#      length, never absolute pixels, so a book set in a different point size behaves the same.
STRIP_H = 1.35           # how far above/below the bar to look, in median text heights
MIN_SIDE_COVER = 0.15    # share of the bar's columns that must carry ink on each side
MIN_DETACH = 0.10        # blank gap between the bar and that ink, in median text heights
SIDE_CENTRE_TOL = 0.45   # |centre(ink) − centre(bar)| may not exceed this share of the bar length
NEIGHBOUR_BAR_LEN_TOL = 0.35   # a neighbour whose length is this close is «another bar», i.e. an «=»
TOKEN_OVERLAP = 0.35     # share of a token's width that must sit over the bar to be its half


@dataclass
class FractionRegion:
    """A printed stacked fraction, whether or not its digits survived the OCR."""
    bar: BARS.Bar
    kind: str                    # 'stacked_fraction' | 'bar_region_unreadable'
    numerator: Token = None
    denominator: Token = None
    ink_above: tuple = None      # (x0, x1) normalised extent of the ink above the bar
    ink_below: tuple = None
    extractable: bool = False
    reason: str = ''

    @property
    def bbox(self):
        """The region's own box: the bar plus the ink strips that make it a fraction."""
        x0 = self.bar.x0
        x1 = self.bar.x1
        if self.ink_above:
            x0, x1 = min(x0, self.ink_above[0]), max(x1, self.ink_above[1])
        if self.ink_below:
            x0, x1 = min(x0, self.ink_below[0]), max(x1, self.ink_below[1])
        y0 = min([self.bar.y0] + [t.y0 for t in (self.numerator,) if t])
        y1 = max([self.bar.y1] + [t.y1 for t in (self.denominator,) if t])
        return (x0, y0, x1, y1)


BARLEN_STRIP = 0.80      # fallback strip height, in bar lengths, when the page has no OCR line


def _strip_px(mask, tokens, bar):
    """How tall the numerator/denominator strip is, and how wide the detachment gap, in pixels.

    Both come from the page's OWN median text height, so a book set in a different point size is
    measured the same way. A page whose OCR produced nothing at all has no text height to use, and
    then the bar's own length stands in for it — a printed vinculum is drawn about as long as the
    digits it separates are tall.
    """
    mh = median_height(tokens)
    base = mh * mask.height if mh > 0 else BARLEN_STRIP * (bar.px1 - bar.px0)
    return max(2, int(round(STRIP_H * base))), max(1, int(round(MIN_DETACH * base)))


def _side(mask, bar, strip_h, detach_px, above):
    """(ink_extent, ok) for the strip above/below a bar. `ok` is False when the side disqualifies it."""
    if above:
        y1 = bar.py0 - detach_px
        y0 = y1 - strip_h
        touch = (bar.py0 - detach_px, bar.py0)
    else:
        y0 = bar.py1 + detach_px
        y1 = y0 + strip_h
        touch = (bar.py1, bar.py1 + detach_px)
    if mask.any_ink(bar.px0, touch[0], bar.px1, touch[1]):
        return None, False                      # attached ink: a «+», a «±», a boxed rule
    cover = mask.column_coverage(bar.px0, y0, bar.px1, y1)
    if cover < MIN_SIDE_COVER:
        return None, False
    ext = mask.ink_extent(bar.px0, y0, bar.px1, y1)
    if ext is None:
        return None, False
    centre = (ext[0] + ext[1]) / 2.0
    if abs(centre - (bar.px0 + bar.px1) / 2.0) > SIDE_CENTRE_TOL * (bar.px1 - bar.px0):
        return None, False
    return ext, True


def _neighbour_is_a_bar(bar, others, strip_h, detach_px):
    """True when a bar of similar length sits in either strip — the two rules of an «=» or «≡»."""
    for o in others:
        if o is bar:
            continue
        near_above = bar.py0 - detach_px - strip_h <= o.py1 <= bar.py0
        near_below = bar.py1 <= o.py0 <= bar.py1 + detach_px + strip_h
        if not (near_above or near_below):
            continue
        lo, hi = max(bar.px0, o.px0), min(bar.px1, o.px1)
        if hi - lo <= 0:
            continue
        a, b = bar.px1 - bar.px0, o.px1 - o.px0
        if abs(a - b) <= NEIGHBOUR_BAR_LEN_TOL * max(a, b):
            return True
    return False


def _half_candidates(tokens, bar, y0, y1, mask):
    """Digit-run tokens lying in the strip and overlapping the bar horizontally."""
    out = []
    for t in tokens:
        if not t.is_digit_run:
            continue
        ty0, ty1 = t.y0 * mask.height, t.y1 * mask.height
        if ty1 <= y0 or ty0 >= y1:
            continue
        tx0, tx1 = t.x0 * mask.width, t.x1 * mask.width
        lo, hi = max(bar.px0, tx0), min(bar.px1, tx1)
        if hi - lo < TOKEN_OVERLAP * max(1.0, tx1 - tx0):
            continue
        out.append(t)
    return out


def find_fraction_regions(mask, tokens, bar_params=None):
    """Every printed stacked-fraction region of the page, extractable or not.

    `bar_params` overrides the `bars.find_bars` shape bounds (tests draw tiny pages, where a
    vinculum is a large share of the width).
    """
    params = bar_params or {}
    found = BARS.find_bars(mask, **params)
    regions = []
    for bar in found:
        strip_h, detach_px = _strip_px(mask, tokens, bar)
        above, ok_a = _side(mask, bar, strip_h, detach_px, above=True)
        below, ok_b = _side(mask, bar, strip_h, detach_px, above=False)
        if not (ok_a and ok_b):
            continue
        if _neighbour_is_a_bar(bar, found, strip_h, detach_px):
            continue
        nums = _half_candidates(tokens, bar, bar.py0 - detach_px - strip_h, bar.py0, mask)
        dens = _half_candidates(tokens, bar, bar.py1, bar.py1 + detach_px + strip_h, mask)
        r = FractionRegion(bar=bar, kind='bar_region_unreadable',
                           ink_above=(above[0] / mask.width, above[1] / mask.width),
                           ink_below=(below[0] / mask.width, below[1] / mask.width))
        if nums or dens:
            r.kind = 'stacked_fraction'
        if len(nums) > 1:
            r.reason = 'numerator_ambiguous'
        elif len(dens) > 1:
            r.reason = 'denominator_ambiguous'
        elif not nums:
            r.reason = 'numerator_token_missing'
        elif not dens:
            r.reason = 'denominator_token_missing'
        else:
            r.numerator, r.denominator = nums[0], dens[0]
            r.extractable = True
        regions.append(r)

    # A digit may belong to exactly one fraction. «5» cannot be the denominator of the fraction
    # above it and the numerator of the fraction below it: one of the two readings is wrong and
    # nothing here can say which, so both fail closed.
    seen = {}
    for r in regions:
        for t in (r.numerator, r.denominator):
            if t is not None:
                seen.setdefault(t.index, []).append(r)
    for shared in (v for v in seen.values() if len(v) > 1):
        for r in shared:
            r.extractable = False
            r.reason = 'token_shared'
    return regions


# ---------------------------------------------------------------- line-level census
# Not repaired by this lane — reported, so the Founder can see how much of a Toán page is formula
# at all, and so «formula/number/unit» error can be attributed to a kind rather than to a page.
_OPERATOR = re.compile(r'[+\-−×÷=<>≤≥≠:]')
_DIGIT = re.compile(r'\d')
_WORD = re.compile(r'[A-Za-zÀ-ỹ]{2,}')
_PURE_NUMBER = re.compile(r'^[\d\s.,]+$')


def classify_token(t):
    """The formula kind of one OCR line, or None when the line is prose.

    · `numeric_answer`            a bare number or quantity standing alone
    · `display_formula_fragment`  operators and digits with no prose around them — the shape a
                                  flattened display formula leaves behind
    · `inline_expression`         arithmetic embedded in a sentence
    """
    s = t.stripped
    if not s:
        return None
    words = _WORD.findall(s)
    has_digit = bool(_DIGIT.search(s))
    has_op = bool(_OPERATOR.search(s))
    if _PURE_NUMBER.match(s) and has_digit:
        return 'numeric_answer'
    if not has_digit and not has_op:
        return None
    if len(words) <= 1 and (has_op or has_digit):
        return 'display_formula_fragment' if has_op else 'numeric_answer'
    if has_op and has_digit:
        return 'inline_expression'
    return None
