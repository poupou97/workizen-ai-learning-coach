#!/usr/bin/env python3
"""TC-v1 — render source PDF pages for gold annotation / Founder review.

Why: gold truth for the Trusted-Corpus study must be written from the
RENDERED PAGE IMAGE, never from any extractor's output. This helper renders
one page (PyMuPDF) and, optionally, overlays a normalised coordinate grid
(0.0–1.0, 10 % ticks) so a human/VLM annotator can write approximate block
bounding boxes by eye without ever seeing OCR boxes.

Usage:
  python3 tool/corpus/tc_render.py <book> <pdfPage> [--dpi 150] [--grid] [--out DIR]
  python3 tool/corpus/tc_render.py --crop <book> <pdfPage> x y w h [--dpi 200] [--out DIR]
Output: <out>/<book>-p<NNN>[-grid|-crop-...].png   (default out: poc-out/trusted-corpus/tc-v1/renders)
Never writes into the repo; never copies a whole PDF.
"""
import argparse
import os
import sys

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
PDF = f'{ROOT}/poc-out/pdf'


def pdf_path(book):
    p = f'{PDF}/{book[:2]}/{book}.pdf'
    if os.path.exists(p):
        return p
    p = f'{PDF}/{book}.pdf'
    return p if os.path.exists(p) else None


def render(book, page, dpi=150, grid=False, out=None, crop=None):
    import fitz
    pdf = pdf_path(book)
    if not pdf:
        raise SystemExit(f'no pdf for {book}')
    doc = fitz.open(pdf)
    pg = doc[page - 1]
    clip = None
    if crop:
        x, y, w, h = crop
        r = pg.rect
        clip = fitz.Rect(r.x0 + x * r.width, r.y0 + y * r.height, r.x0 + (x + w) * r.width, r.y0 + (y + h) * r.height)
    pm = pg.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False, clip=clip)
    out = out or f'{ROOT}/poc-out/trusted-corpus/tc-v1/renders'
    os.makedirs(out, exist_ok=True)
    suffix = '-grid' if grid else ('-crop-%.2f-%.2f-%.2f-%.2f' % tuple(crop) if crop else '')
    path = f'{out}/{book}-p{page:03d}{suffix}.png'
    if grid:
        from PIL import Image, ImageDraw
        img = Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
        d = ImageDraw.Draw(img)
        for i in range(1, 10):
            x = int(pm.width * i / 10); y = int(pm.height * i / 10)
            d.line([(x, 0), (x, pm.height)], fill=(255, 0, 0), width=1)
            d.line([(0, y), (pm.width, y)], fill=(255, 0, 0), width=1)
            d.text((x + 2, 2), f'{i/10:.1f}', fill=(255, 0, 0))
            d.text((2, y + 2), f'{i/10:.1f}', fill=(255, 0, 0))
        for i in range(1, 20):
            x = int(pm.width * i / 20); y = int(pm.height * i / 20)
            d.line([(x, 0), (x, 12)], fill=(0, 0, 255), width=1)
            d.line([(0, y), (12, y)], fill=(0, 0, 255), width=1)
        img.save(path)
    else:
        pm.save(path)
    doc.close()
    return path


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('args', nargs='+')
    ap.add_argument('--dpi', type=int, default=150)
    ap.add_argument('--grid', action='store_true')
    ap.add_argument('--crop', action='store_true')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    if a.crop:
        book, page = a.args[0], int(a.args[1])
        crop = tuple(float(v) for v in a.args[2:6])
        print(render(book, page, a.dpi, out=a.out, crop=crop))
    else:
        book, page = a.args[0], int(a.args[1])
        print(render(book, page, a.dpi, a.grid, a.out))
