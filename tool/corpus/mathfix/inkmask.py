#!/usr/bin/env python3
"""A binary ink raster of one printed page.

Why a hand-rolled mask rather than numpy: this is the lane's independent signal — the thing that
says a fraction bar is really on the page — so its rules must be pinned by tests that run on the CI
runner, which has neither numpy nor PyMuPDF (`.github/workflows/ci.yml` installs Flutter and calls
`python3 -m unittest discover -s tool/tests`). `from_ascii` builds exactly the structure
`from_pdf` builds, so every geometric rule in `bars`/`detect`/`validate` is pinned on a picture a
reader can see in the test file. `from_pdf` imports PyMuPDF and numpy lazily and is used only by
the CLI, where a page is 3282 × 4608 pixels and pure-Python thresholding would cost minutes.

The scans that run over a WHOLE page (`row_runs`) go through `re.finditer` on the row's bytes, so
they are a C-speed scan rather than 15 million Python iterations; the scans that run over a small
box (`column_coverage`, `ink_extent`) stay plain loops, because there the box is ~100 × 80 px and
clarity is worth more than the microseconds.

Coordinates: pixels internally, normalised 0..1 at the region level. Half-open boxes throughout:
`[x0, x1) × [y0, y1)`.
"""
import re

_RUN = re.compile(b'\x01+')


class InkMask:
    """`rows` is every dark pixel. `neutral_rows` is the dark pixels that are also near-GREY.

    Two layers, because they answer different questions. A printed rule is always neutral ink, so
    `find_bars` reads `neutral_rows` and an illustration's coloured edge — a green grass band, the
    brim of a yellow hat — can never be mistaken for a vinculum. But a printed DIGIT may be
    coloured (Toán 5 tập một p22 prints the «× 5» of a common-denominator step in red and the
    «× 2» in blue), so `ink-accounted` must see all of it or a dropped coloured digit would go
    unnoticed. One mask for shapes, the other for ink.
    """

    __slots__ = ('rows', 'neutral_rows', 'width', 'height')

    def __init__(self, rows, width, height, neutral_rows=None):
        self.rows = rows                                   # list of bytes, one per raster row, 1 = ink
        self.neutral_rows = neutral_rows if neutral_rows is not None else rows
        self.width = width
        self.height = height

    # ---------------------------------------------------------------- constructors
    @classmethod
    def from_ascii(cls, art):
        """'#' (or any non-'.', non-space char) is ink; '.' and ' ' are paper.

        Every line is padded to the widest line, so a picture in a test may end early.
        """
        lines = [ln for ln in art.splitlines() if ln != '']
        width = max((len(ln) for ln in lines), default=0)
        rows = []
        for ln in lines:
            r = bytearray(width)
            for i, ch in enumerate(ln):
                if ch not in ('.', ' '):
                    r[i] = 1
            rows.append(bytes(r))
        return cls(rows, width, len(rows))

    @classmethod
    def from_pdf(cls, pdf_path, page, dpi=300, threshold=160, max_chroma=55):
        """Render one PDF page and threshold it. Requires PyMuPDF + numpy (CLI only, imported lazily).

        `threshold` is a grey level: a pixel darker than it is ink. 160/255 was chosen against the
        real books — the printed vinculum in the Toán pages sits at ≈ 30-60 grey and the tinted
        exercise boxes at ≈ 225-240, so the whole tint band stays paper and no box background is
        ever read as a rule.

        `max_chroma` (max channel − min channel) separates printed ink from illustration. On an
        unbiased 12-page sample of ordinary Toán pages, 4 of the 7 detected regions were parts of
        PICTURES — a grass band, a speech-bubble tail, the brim of a hat — every one of them
        strongly coloured. Neutral ink is what a press uses for a rule.
        """
        import numpy as np                                 # noqa: PLC0415  (optional dependency)
        import pymupdf                                     # noqa: PLC0415  (optional dependency)
        doc = pymupdf.open(pdf_path)
        pix = doc[page - 1].get_pixmap(dpi=dpi)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.stride)
        arr = arr[:, :pix.width * pix.n].reshape(pix.height, pix.width, pix.n)
        rgb = arr[:, :, :3].astype(np.int16)
        dark = rgb.sum(axis=2) < threshold * 3
        chroma = rgb.max(axis=2) - rgb.min(axis=2)
        w, h = pix.width, pix.height
        buf = dark.astype(np.uint8).tobytes()
        nbuf = (dark & (chroma <= max_chroma)).astype(np.uint8).tobytes()
        rows = [buf[y * w:(y + 1) * w] for y in range(h)]
        nrows = [nbuf[y * w:(y + 1) * w] for y in range(h)]
        doc.close()
        return cls(rows, w, h, neutral_rows=nrows)

    # ---------------------------------------------------------------- queries
    def ink(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return bool(self.rows[y][x])

    def any_ink(self, x0, y0, x1, y1):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.width, x1), min(self.height, y1)
        for y in range(y0, y1):
            if b'\x01' in self.rows[y][x0:x1]:
                return True
        return False

    def column_coverage(self, x0, y0, x1, y1):
        """Share of the columns of `[x0, x1)` that carry ink anywhere in `[y0, y1)`.

        The discriminator between a numerator (a digit: several adjacent columns) and the vertical
        stroke of a «+» (one narrow column band) — see `detect.MIN_SIDE_COVER`.
        """
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.width, x1), min(self.height, y1)
        if x1 <= x0 or y1 <= y0:
            return 0.0
        acc = bytearray(x1 - x0)
        for y in range(y0, y1):
            row = self.rows[y]
            for i in range(x1 - x0):
                if row[x0 + i]:
                    acc[i] = 1
        return sum(acc) / (x1 - x0)

    def ink_extent(self, x0, y0, x1, y1):
        """(left, right) pixel columns of the ink inside the box, or None when there is none.

        Half-open on the right, so `ink_extent` composes with the box arguments it was given.
        """
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.width, x1), min(self.height, y1)
        left = right = None
        for y in range(max(0, y0), y1):
            row = self.rows[y][x0:x1]
            i = row.find(b'\x01')
            if i < 0:
                continue
            j = row.rfind(b'\x01')
            left = x0 + i if left is None else min(left, x0 + i)
            right = x0 + j if right is None else max(right, x0 + j)
        return None if left is None else (left, right + 1)

    def row_runs(self, y, x0, x1, min_len=1, neutral=False):
        """[(start, length)] of contiguous ink runs in row `y` restricted to `[x0, x1)`.

        `min_len` filters inside the C scan, which matters: `find_bars` calls this once per raster
        row of a 4608-row page and only ever wants runs above a length floor. `neutral=True` reads
        the near-grey layer — what a printed rule is made of.
        """
        if not (0 <= y < self.height):
            return []
        x0, x1 = max(0, x0), min(self.width, x1)
        if x1 <= x0:
            return []
        seg = (self.neutral_rows if neutral else self.rows)[y][x0:x1]
        out = []
        for m in _RUN.finditer(seg):
            ln = m.end() - m.start()
            if ln >= min_len:
                out.append((x0 + m.start(), ln))
        return out
