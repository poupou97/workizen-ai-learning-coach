#!/usr/bin/env python3
"""Is the printed operator the operator the OCR said it was?

Found by hand-checking a restore, not by reasoning: on Toán 4 tập hai p118 the book prints
`c) 16/21 × 3/5` and Apple Vision returns a token whose text is `'-'`. Every check this lane had
passed it — the ink was accounted for (the token's box covers the ×), no character was invented (the
«-» came from a real observation), the grammar parsed, the vinculums were real — and the candidate
came out `16/21 - 3/5`. **A false correction: multiplication served as subtraction.**

The gap it exposes is general. Ink-accounting proves *completeness* («nothing printed was dropped»)
and provenance proves *honesty* («nothing was invented»); neither proves **identity** — that the
glyph on the page is the glyph the recogniser named. The same gap produces `3×10⁸ → 3×10°`.

So this module reads the operator's own pixels and classifies the SHAPE:

    −   one horizontal bar, nothing above or below it
    +   one horizontal bar with a stroke crossing it
    =   two horizontal bars
    ×   no dominant horizontal bar — two diagonals
    :   no bar, two separated blobs

The classes are far apart in ink, so the test is a coarse count rather than a recogniser, and it
abstains (`None`) whenever the box holds too little ink to judge. Abstention is not a pass:
`validate.operator_raster_v1` treats an unjudgeable operator as NOT_APPLICABLE and the candidate
then needs its confirmation elsewhere.
"""
from . import nodes as A

BAR_RUN = 0.62          # a row whose longest run reaches this share of the ink width is a «bar» row
BAR_ASPECT = 2.0        # …and the whole group must be at least this much wider than it is thick.
#   Without the aspect test the run share alone calls every narrow blob a bar, because the width it
#   is measured against is the blob's own: the two dots of «:» each span 100 % of the ink width and
#   read as «two_bars», i.e. as «=». A printed rule is wide and thin; a dot is not.
MIN_INK_PX = 12         # below this the box holds a speck, not a glyph — abstain
PAD_Y = 0.35            # dilate the operator's box by this share of the text height, top and bottom
PAD_X = 0.02            # …and barely at all horizontally.
#   Both paddings are small on purpose, and horizontal padding almost zero: a printed operator sits
#   BETWEEN two fractions, so a generous x-window swallows the neighbour's vinculum and every «−»
#   then reads as «no_bar». Measured on Toán 4 tập hai p118: at PAD_X 0.12 the correct «8/11 − 19/33»
#   was refused because the window reached the vinculum of «8/11». The width the run is compared
#   against is the ink's own extent inside the box, never the OCR box, which is often far wider than
#   the glyph it names.

#: shape → the operators it can be. A shape not listed here matches nothing.
SHAPE_OPS = {
    'one_bar': (A.SUB,),
    'crossed_bar': (A.ADD,),
    'two_bars': (A.EQ,),
    'no_bar': (A.MUL, A.DIV),      # × and : are both «no dominant horizontal»; they are not
                                   # distinguished here, because confusing them is not a failure
                                   # this corpus produces and a finer rule would be a guess.
}


def classify(mask, box, text_height):
    """The printed shape inside `box` — 'one_bar' | 'crossed_bar' | 'two_bars' | 'no_bar' | None."""
    x0, y0, x1, y1 = box
    px = PAD_X * max(1e-6, x1 - x0)
    py = PAD_Y * (text_height or (y1 - y0))
    a0, a1 = int((x0 - px) * mask.width), int((x1 + px) * mask.width)
    b0, b1 = int((y0 - py) * mask.height), int((y1 + py) * mask.height)
    ext = mask.ink_extent(a0, b0, a1, b1)
    if ext is None:
        return None
    w = max(1, ext[1] - ext[0])
    rows = []
    ink = 0
    for y in range(max(0, b0), min(mask.height, b1)):
        runs = mask.row_runs(y, ext[0], ext[1])
        ink += sum(ln for _s, ln in runs)
        longest = max((ln for _s, ln in runs), default=0)
        rows.append((y, longest / w, bool(runs)))
    if ink < MIN_INK_PX:
        return None
    # group consecutive «bar» rows into bars, then drop groups that are not wide-and-thin
    widest = {y: max((ln for _s, ln in mask.row_runs(y, ext[0], ext[1])), default=0)
              for y, _s, _h in rows}
    bars, run = [], None
    for y, share, _has in rows:
        if share >= BAR_RUN:
            run = (run[0], y) if run else (y, y)
        elif run:
            bars.append(run)
            run = None
    if run:
        bars.append(run)
    bars = [b for b in bars
            if max(widest[y] for y in range(b[0], b[1] + 1)) >= BAR_ASPECT * (b[1] - b[0] + 1)]
    if not bars:
        return 'no_bar'
    if len(bars) >= 2:
        return 'two_bars'
    top, bottom = bars[0]
    above = any(has for y, _s, has in rows if y < top)
    below = any(has for y, _s, has in rows if y > bottom)
    return 'crossed_bar' if (above and below) else 'one_bar'


def matches(shape, op):
    """Does the printed shape admit this operator? An unjudgeable shape (None) admits nothing."""
    return shape is not None and op in SHAPE_OPS.get(shape, ())
