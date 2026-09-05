#!/usr/bin/env python3
"""Horizontal ink runs on a printed page — the candidate vinculums.

A printed fraction bar, a minus sign, an underline, a table rule and a box border are the same
thing to a raster: a short-to-long run of dark pixels a few pixels thick. This module finds them
all and filters only on SHAPE (length, thickness). What separates a vinculum from a minus sign is
what sits above and below it, and that decision belongs to `detect`, which has the OCR tokens too.

Keeping the split honest matters: the length/thickness bounds here are the only place a printed
mark is discarded before anything looks at it, so they are deliberately generous, and the reason a
mark was discarded is always «too long to be a vinculum» or «too thick», never «it did not look
like maths».
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Bar:
    """A horizontal ink run. Pixel bounds are half-open; normalised bounds are derived."""
    px0: int
    px1: int
    py0: int
    py1: int
    mask_w: int
    mask_h: int

    @property
    def x0(self):
        return self.px0 / self.mask_w

    @property
    def x1(self):
        return self.px1 / self.mask_w

    @property
    def y0(self):
        return self.py0 / self.mask_h

    @property
    def y1(self):
        return self.py1 / self.mask_h

    @property
    def cx(self):
        return (self.px0 + self.px1) / 2.0 / self.mask_w

    @property
    def cy(self):
        return (self.py0 + self.py1) / 2.0 / self.mask_h

    @property
    def length(self):
        return (self.px1 - self.px0) / self.mask_w

    @property
    def thickness(self):
        return (self.py1 - self.py0) / self.mask_h


# Calibrated on the real books (Toán 4 tập hai, Toán 5 tập một, at 300 dpi), not guessed:
#   · the four printed fraction bars of Toán 5 tập một p23 measure 0.021-0.030 of the page width
#     and 9 px ≈ 0.0020 of the page height;
#   · the minus and plus signs on the same line measure 0.013 and are the same thickness — which is
#     why length alone can never separate them (see `detect`);
#   · a table rule or the border of a tinted exercise box on those pages spans 0.30-0.95 of the page.
MIN_LEN = 0.008          # shorter than this is a hyphen inside a word, or glyph noise
MAX_LEN = 0.150          # longer than this is a rule, a border or an underline, never a vinculum
MAX_THICK = 0.0045       # ≈ 20 px at 300 dpi on an A4 page: thicker is a filled shape
_OVERLAP = 0.5           # two runs on consecutive rows are the same bar when they overlap this much


def find_bars(mask, min_len_frac=MIN_LEN, max_len_frac=MAX_LEN, max_thick_frac=MAX_THICK):
    """Every horizontal ink run of the mask whose shape could be a vinculum.

    Runs on consecutive rows that overlap horizontally by `_OVERLAP` of the shorter one are merged
    into a single bar, so a 9-pixel-thick printed rule is ONE object rather than nine.
    """
    min_len = max(1, int(round(min_len_frac * mask.width)))
    max_len = max_len_frac * mask.width
    max_thick = max_thick_frac * mask.height

    open_bars = []      # bars still growing downward
    done = []
    for y in range(mask.height):
        runs = mask.row_runs(y, 0, mask.width, min_len=min_len)
        still_open = []
        used = set()
        for b in open_bars:
            if b['y1'] != y - 1:
                done.append(b)
                continue
            best = None
            for i, (s, ln) in enumerate(runs):
                if i in used:
                    continue
                lo, hi = max(b['x0'], s), min(b['x1'], s + ln)
                if hi - lo >= _OVERLAP * min(b['x1'] - b['x0'], ln):
                    best = i
                    break
            if best is None:
                done.append(b)
            else:
                s, ln = runs[best]
                used.add(best)
                b['x0'] = min(b['x0'], s)
                b['x1'] = max(b['x1'], s + ln)
                b['y1'] = y
                still_open.append(b)
        for i, (s, ln) in enumerate(runs):
            if i not in used:
                still_open.append(dict(x0=s, x1=s + ln, y0=y, y1=y))
        open_bars = still_open
    done.extend(open_bars)

    out = []
    for b in done:
        length = b['x1'] - b['x0']
        thick = b['y1'] - b['y0'] + 1
        if length < min_len or length > max_len or thick > max_thick:
            continue
        out.append(Bar(px0=b['x0'], px1=b['x1'], py0=b['y0'], py1=b['y1'] + 1,
                       mask_w=mask.width, mask_h=mask.height))
    out.sort(key=lambda b: (b.py0, b.px0))
    return out
