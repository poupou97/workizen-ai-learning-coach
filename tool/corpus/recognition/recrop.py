#!/usr/bin/env python3
"""The targeted re-crop experiment, one page at a time.

What it does, and in this order, because the order is the honesty:

 1. take the fraction regions `tool/corpus/mathfix/detect.py` already finds from the RASTER —
    including every region whose digits the OCR destroyed, which is the whole population of
    interest (274 of 336 in round 5);
 2. ask Apple Vision about the numerator box, the denominator box and the whole region, at
    several scales — twelve untrusted observations per region;
 3. let `consensus` refuse or accept;
 4. record what the ORIGINAL whole-page OCR said about the same region, so every row can be
    read as before -> after, and so a region the baseline already read becomes a CONTROL rather
    than a recovery.

The control set is the part that keeps the number honest. On regions the whole-page OCR already
read correctly, the re-crop must return the same value; a disagreement there is a candidate
false recognition and is counted as one until a look at the printed crop says otherwise. Without
it, «recovered 200 digits» is unfalsifiable.
"""
import json
import os
import sys
from dataclasses import asdict, dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathfix import detect as D                                  # noqa: E402
from mathfix.inkmask import InkMask                              # noqa: E402
from mathfix.tokens import load_tokens, median_height            # noqa: E402
from recognition import boxes as B                               # noqa: E402
from recognition import consensus as C                           # noqa: E402
from recognition import vision as V                              # noqa: E402

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OUT = f'{ROOT}/poc-out/round6/recognition'

CONTROL = 'control'          # the baseline OCR read both halves: the re-crop must agree
RECOVERY = 'recovery'        # the baseline could not: this is what the round is trying to reach


@dataclass
class RegionRow:
    key: str
    book: str
    page: int
    bar: list
    population: str
    baseline_reason: str
    baseline_value: str = None
    recrop_verdict: str = ''
    recrop_value: str = None
    recrop_reason: str = ''
    agreement: str = ''                    # 'same' | 'differs' | 'baseline_only' | 'recrop_only' | 'neither'
    numerator: dict = field(default_factory=dict)
    denominator: dict = field(default_factory=dict)
    region_scale: float = None
    crop_native_px: list = field(default_factory=list)


def _reading_row(r):
    return dict(verdict=r.verdict, value=r.value, scales=list(r.agreeing_scales),
                per_scale={str(k): v for k, v in r.per_scale.items()}, note=r.note)


def page_rows(book, page, scales=V.DEFAULT_SCALES, dpi=300, limit=None):
    """Every detected fraction region on one page, before and after the re-crop."""
    mask = InkMask.from_pdf(V.pdf_path(book), page, dpi=dpi)
    tokens = load_tokens(book, page)
    regions = D.find_fraction_regions(mask, tokens)
    mh = median_height(tokens) or 0.018
    page_pt = V.page_size_pt(book, page)
    if limit:
        regions = regions[:limit]

    jobs, meta = [], {}
    for i, r in enumerate(regions):
        key = f'{book}:p{page:03d}:r{i:03d}'
        bar = [r.bar.x0, r.bar.y0, r.bar.length, r.bar.thickness]
        bxs = B.fraction_boxes(bar, mh)
        prefix = f'{i:03d}|'
        jobs.extend(V.make_jobs(book, page, bxs, scales=scales, key_prefix=prefix))
        meta[i] = (key, r, bar, {b.kind: b for b in bxs}, prefix)

    results = V.run(jobs)

    rows = []
    for i, (key, r, bar, bxs, prefix) in meta.items():
        num = C.read_half(V.by_scale(results, prefix, 'numerator'))
        den = C.read_half(V.by_scale(results, prefix, 'denominator'))
        reg = V.by_scale(results, prefix, 'region')
        fr = C.read_fraction(key, V.by_scale(results, prefix, 'numerator'),
                             V.by_scale(results, prefix, 'denominator'), reg)
        baseline = (f'{r.numerator.stripped}/{r.denominator.stripped}'
                    if r.extractable else None)
        row = RegionRow(
            key=key, book=book, page=page, bar=[round(v, 5) for v in bar],
            population=CONTROL if r.extractable else RECOVERY,
            baseline_reason=r.reason or 'ok', baseline_value=baseline,
            recrop_verdict=fr.verdict, recrop_value=fr.value if fr.ok else None,
            recrop_reason=fr.reason, region_scale=fr.region_agreement_scale,
            numerator=_reading_row(num), denominator=_reading_row(den),
            crop_native_px=list(B.native_pixels(bxs['region'], page_pt)))
        row.agreement = _agreement(row.baseline_value, row.recrop_value)
        rows.append(row)
    return rows


def _agreement(baseline, recrop):
    if baseline and recrop:
        return 'same' if baseline == recrop else 'differs'
    if baseline:
        return 'baseline_only'
    if recrop:
        return 'recrop_only'
    return 'neither'


def write(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        json.dump(dict(rows=[asdict(r) for r in rows]), fh, ensure_ascii=False, indent=1)
    return path
