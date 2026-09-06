#!/usr/bin/env python3
"""The hand-check contact sheet — the only thing that decides whether a reading is correct.

Round 5's two false corrections were found by looking at the printed page, not by a metric, and
this lane inherits that: a recovered digit is CORRECT only when someone reads the printed crop
and says so. The sheet exists so that judgement is cheap and blind-ish — one tile per region,
cropped at reading size, labelled with the region key, what the whole-page OCR had, and what the
re-crop proposes.

The judge answers one question per tile: **does the book print this fraction?**
"""
import os

import pymupdf
from PIL import Image, ImageDraw

from . import boxes as B


def sheet(book, page, rows, pdf, out_path, cols=4, dpi=300, only=None):
    """`rows` are `recrop.RegionRow`s; `only` filters by population or verdict."""
    doc = pymupdf.open(pdf)
    pg = doc[page - 1]
    W, H = pg.rect.width, pg.rect.height
    keep = [r for r in rows if not only or only(r)]
    tiles, labels = [], []
    for r in keep:
        box = B.fraction_boxes(r.bar, None)[2]         # the region box, bar-derived
        padx, pady = 0.010, 0.006
        clip = pymupdf.Rect(max(0.0, box.x0 - padx) * W, max(0.0, box.y0 - pady) * H,
                            min(1.0, box.x1 + padx) * W, min(1.0, box.y1 + pady) * H)
        pix = pg.get_pixmap(dpi=dpi, clip=clip)
        tiles.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
        labels.append(f"{r.key.rsplit(':', 1)[1]} base={r.baseline_value or '-'} "
                      f"recrop={r.recrop_value or r.recrop_verdict}")
    if not tiles:
        return None
    tw = max(t.width for t in tiles) + 12
    th = max(t.height for t in tiles) + 30
    rowsn = (len(tiles) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * tw, rowsn * th), 'white')
    draw = ImageDraw.Draw(canvas)
    for i, (t, lab) in enumerate(zip(tiles, labels)):
        cx, cy = (i % cols) * tw, (i // cols) * th
        canvas.paste(t, (cx + 6, cy + 24))
        draw.text((cx + 6, cy + 6), lab, fill='black')
        draw.rectangle([cx + 2, cy + 2, cx + tw - 4, cy + th - 4], outline='#bbbbbb')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path)
    return out_path
