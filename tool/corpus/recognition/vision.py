#!/usr/bin/env python3
"""The only place that runs a recogniser. Everything else in this package is pure Python.

`tool/ocr/ocr_crop.swift` is Apple Vision — the same engine `tool/ocr/ocr_pdf.swift` used to
produce the corpus, and the same engine the product runs on iOS, so a number measured here
transfers instead of having to be re-measured on the device. It is invoked once per batch of
crops, never once per crop: process start-up dominates otherwise.

Nothing in this module decides anything. It renders, it asks, it records what came back, and
`consensus` decides. That separation is the point: the recogniser is a candidate producer and
never a source of truth.
"""
import json
import os
import subprocess
import tempfile

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
BIN = os.environ.get('OCR_CROP_BIN', f'{ROOT}/poc-out/bin/ocr_crop')
SRC = f'{os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}/ocr/ocr_crop.swift'
PDF_DIR = f'{ROOT}/poc-out/pdf'

#: the scales the experiment asks at. Not a resolution ladder — the source is a 100 ppi scan, so
#: these resample the same pixels and move Vision's own segmentation. Chosen after the sweep on
#: Toán 5 tập một p22 showed the answer is not monotonic in scale (3 and 12 miss the numerator
#: `3`; 6 and 20 read it), which is exactly why more than one is asked and why agreement counts.
DEFAULT_SCALES = tuple(float(x) for x in
                       os.environ.get('RECOG_SCALES', '6,10,14,20').split(',') if x.strip())
#   Overridable so the scale ladder itself can be measured rather than assumed: the largest
#   addressable refusal group is INSUFFICIENT_AGREEMENT (one scale read it, no second), and
#   whether more scales convert those without raising the false-recognition rate is a question
#   with an answer, not a preference.


def ensure_binary():
    """Compile `ocr_crop.swift` on first use. macOS only; the corpus never enters CI."""
    if os.path.exists(BIN) and os.path.getmtime(BIN) >= os.path.getmtime(SRC):
        return BIN
    os.makedirs(os.path.dirname(BIN), exist_ok=True)
    subprocess.run(['swiftc', '-O', '-o', BIN, SRC], check=True)
    return BIN


def pdf_path(book):
    p = f'{PDF_DIR}/{book[:2]}/{book}.pdf'
    return p if os.path.exists(p) else f'{PDF_DIR}/{book}.pdf'


def page_size_pt(book, page):
    import pymupdf                                   # local: the library must import without it
    with pymupdf.open(pdf_path(book)) as doc:
        r = doc[page - 1].rect
        return (r.width, r.height)


def make_jobs(book, page, boxes, scales=DEFAULT_SCALES, key_prefix='',
              languages=('en-US',), language_correction=False):
    """One job per (box, scale). The id carries the box kind and the scale, so a result never
    has to be matched back by position."""
    pdf = pdf_path(book)
    jobs = []
    for box in boxes:
        if box.is_degenerate:
            continue
        for scale in scales:
            jobs.append(dict(id=f'{key_prefix}{box.kind}@{scale:g}', pdf=pdf, page=page,
                             bbox=list(box.bbox), scale=float(scale), pad=0.0,
                             languages=list(languages), languageCorrection=bool(language_correction)))
    return jobs


def run(jobs, out_path=None):
    """Ask Vision. Returns `{job_id: result}`; a job that failed keeps its error."""
    if not jobs:
        return {}
    ensure_binary()
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh:
        json.dump(dict(defaults=dict(level='accurate', minTextHeight=0.0), jobs=jobs), fh)
        job_path = fh.name
    out = out_path or tempfile.mktemp(suffix='.json')
    try:
        subprocess.run([BIN, job_path, out], check=True, capture_output=True)
        with open(out) as fh:
            payload = json.load(fh)
    finally:
        os.unlink(job_path)
        if not out_path and os.path.exists(out):
            os.unlink(out)
    return {r['id']: r for r in payload.get('results', [])}


def by_scale(results, key_prefix, kind):
    """`{scale: [line, ...]}` for one box, the shape `consensus` wants."""
    out = {}
    for jid, res in results.items():
        if not jid.startswith(f'{key_prefix}{kind}@'):
            continue
        out[float(jid.rsplit('@', 1)[1])] = res.get('lines') or []
    return out
