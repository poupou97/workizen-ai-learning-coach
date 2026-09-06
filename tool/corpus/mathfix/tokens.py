#!/usr/bin/env python3
"""OCR lines as geometry.

The lane's doctrine is that a flattened expression must not be re-read as prose, so an OCR line is
treated here as a *placed observation* — a box on the page carrying some characters — and never as
a sentence. `Token` is that observation; nothing in this package mutates one.
"""
import json
import os
import re
from dataclasses import dataclass

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OCR_BODY = f'{ROOT}/poc-out/graph/ocr-body'

_DIGIT_RUN = re.compile(r'^\d{1,4}$')


@dataclass(frozen=True)
class Token:
    """One OCR line, in normalised page coordinates (`y` grows downward)."""
    text: str
    x: float
    y: float
    w: float
    h: float
    conf: float
    index: int

    @property
    def x0(self):
        return self.x

    @property
    def x1(self):
        return self.x + self.w

    @property
    def y0(self):
        return self.y

    @property
    def y1(self):
        return self.y + self.h

    @property
    def cx(self):
        return self.x + self.w / 2.0

    @property
    def cy(self):
        return self.y + self.h / 2.0

    @property
    def stripped(self):
        return (self.text or '').strip()

    @property
    def is_digit_run(self):
        """A bare run of 1-4 digits — the only thing this lane will read as a fraction half.

        Deliberately narrow: «3,1» and «7 +» are NOT fraction halves, because admitting them would
        mean deciding where the number ends, which is the speculative step the order forbids.
        """
        return bool(_DIGIT_RUN.match(self.stripped))


def load_tokens(book, page, root=None):
    """The Apple-Vision OCR lines of one page, as Tokens. Raises FileNotFoundError when absent."""
    base = f'{root or OCR_BODY}/{book}/p{page:03d}.json'
    with open(base) as fh:
        doc = json.load(fh)
    out = []
    for i, ln in enumerate(doc.get('lines') or []):
        out.append(Token(text=ln.get('text') or '', x=float(ln['x']), y=float(ln['y']),
                         w=float(ln['w']), h=float(ln['h']),
                         conf=float(ln.get('conf', 1.0)), index=i))
    return out


def median_height(tokens):
    """The page's own text height — every vertical tolerance in this package is a multiple of it,
    so nothing is calibrated to one book's point size."""
    hs = sorted(t.h for t in tokens if t.stripped)
    return hs[len(hs) // 2] if hs else 0.0
