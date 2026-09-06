#!/usr/bin/env python3
"""Which rectangle to hand the recogniser — pure geometry, no raster, no dependency.

The failing digit is not anywhere on the page: it is in a box the detector already computed.
`tool/corpus/mathfix/detect.py` finds a printed vinculum from the raster and reports the bar
plus the ink extents above and below it, whether or not the OCR read either half. So the crop
is fully determined by things already measured, and this module only turns them into boxes.

Three boxes per fraction region, on purpose:

    numerator   the strip above the bar        — asks one question, gets one answer
    denominator the strip below the bar        — same
    region      both halves and the bar        — asks whether the two answers STACK

The third one is not redundant. A numerator crop that reads `3` and a denominator crop that
reads `10` do not yet prove the page prints `3/10`: they prove two boxes each hold a digit run.
The region crop is an independent observation of the same fact, and `consensus` requires it,
because round 5's costliest lesson was that completeness and honesty do not prove identity.

Coordinates are the corpus convention throughout: normalised to the page, `y` growing DOWNWARD,
`(x0, y0, x1, y1)`. That is what `tool/ocr/ocr_pdf.swift` writes and what `mathfix.tokens`
reads, so nothing here converts anything.
"""
from dataclasses import dataclass

# Calibrated against the printed page, in multiples of the page's OWN median text height, so a
# book set in a different point size gets the same treatment. Measured on Toán 5 tập một p22 and
# Toán 4 tập hai p83, the two fraction-dense pages round 5 hand-checked.
X_PAD_BARS = 0.40        # widen each side by this share of the bar's length.
#   A printed vinculum is drawn about as long as the wider half, so 0.40 admits a numerator that
#   overhangs the rule without reaching the neighbouring fraction: on the «1 Tính» row of Toán 5
#   tập một p22 six fractions sit within 0.10 of page width of each other, and at 0.9 the crop of
#   `3/10` already contains a digit of `5/21`.
Y_PAD_HEIGHTS = 1.50     # how far above/below the bar to include, in median text heights.
#   `detect.STRIP_H` is 1.35 — the window the DETECTOR searched. The crop is deliberately a
#   little taller: a digit whose token the OCR never emitted has no measured height, so the
#   detector's own strip is a lower bound on where its ink can be.
HALF_GAP = 0.10          # keep this much of a text height between a half's crop and the bar.
#   Without it the bar's own ink sits at the very edge of the numerator crop and Vision reads the
#   pair as `3-`; measured on Toán 5 tập một p22 region 28.


@dataclass(frozen=True)
class CropBox:
    """One rectangle to recognise, and what it is being asked about."""
    kind: str                # 'numerator' | 'denominator' | 'region'
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def bbox(self):
        return (self.x0, self.y0, self.x1, self.y1)

    @property
    def is_degenerate(self):
        return self.x1 <= self.x0 or self.y1 <= self.y0


def _clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def _x_window(bar_x0, bar_len, x_pad_bars=X_PAD_BARS):
    pad = x_pad_bars * bar_len
    return _clamp(bar_x0 - pad), _clamp(bar_x0 + bar_len + pad)


def fraction_boxes(bar, text_height, x_pad_bars=X_PAD_BARS, y_pad_heights=Y_PAD_HEIGHTS,
                   half_gap=HALF_GAP):
    """The three crops for one detected fraction region.

    `bar` is `(x0, y0, length, thickness)` — exactly the four numbers
    `mathfix.runner._region_row` already writes for every region it finds, extractable or not.
    `text_height` is the page's median OCR line height; a page with no OCR at all has none, and
    the bar's own length stands in, the same fallback `mathfix.detect` uses.
    """
    bx0, by0, blen, bthick = bar
    by1 = by0 + bthick
    mh = text_height if text_height and text_height > 0 else 0.80 * blen
    x0, x1 = _x_window(bx0, blen, x_pad_bars)
    gap = half_gap * mh
    pad = y_pad_heights * mh
    return [
        CropBox('numerator', x0, _clamp(by0 - pad), x1, _clamp(by0 - gap)),
        CropBox('denominator', x0, _clamp(by1 + gap), x1, _clamp(by1 + pad)),
        CropBox('region', x0, _clamp(by0 - pad), x1, _clamp(by1 + pad)),
    ]


def token_box(token_bbox, text_height, x_pad_heights=0.25, y_pad_heights=0.35):
    """The crop for a region named by an OCR token rather than by a raster bar.

    Used by the non-fraction classes — a destroyed exponent, a Roman numeral, a mis-read Ω.
    There the OCR *did* emit something; what is in doubt is whether the glyph it named is the
    glyph on the page. `token_bbox` is `(x, y, w, h)` as `mathfix.tokens.Token` carries it.
    """
    x, y, w, h = token_bbox
    mh = text_height if text_height and text_height > 0 else h
    px, py = x_pad_heights * mh, y_pad_heights * mh
    return CropBox('token', _clamp(x - px), _clamp(y - py), _clamp(x + w + px), _clamp(y + h + py))


def crop_pixels(box, page_pt, scale):
    """How many pixels the crop will be at `scale`, given the page size in points.

    Reported beside every reading, because it is the honest denominator of «higher resolution»:
    every SGK page in this corpus is a 100 ppi scan, so `scale` above 1.39 (100 ppi / 72 pt)
    is interpolation, not information.
    """
    pw, ph = page_pt
    return (max(8, int(round((box.x1 - box.x0) * pw * scale))),
            max(8, int(round((box.y1 - box.y0) * ph * scale))))


NATIVE_SCALE_FROM_PT = 100.0 / 72.0   # the corpus scans are 100 ppi; 1 pt = 100/72 source pixels


def native_pixels(box, page_pt):
    """The crop's size in SOURCE pixels — the information actually available in it."""
    return crop_pixels(box, page_pt, NATIVE_SCALE_FROM_PT)
