#!/usr/bin/env python3
"""Round 3 · A2 — CONTACT SHEETS for the false-trust annotator. Each PNG stacks a few sample rows,
every one re-rendered from the SGK PDF at 170 dpi around the matched region (red box) and labelled
with its `sampleId`; rows without a bbox (Toán expressions rebuilt from geometry) get the whole page.
Sheets are capped at ~1500 px tall so tone marks stay legible when viewed.

INTERNAL / RESEARCH ONLY (Founder D4): page renders never leave poc-out/.

Usage:
  python3 tool/corpus/ft_audit_sheets.py poc-out/round3/ft-audit/precheck-20260905.jsonl \
      --out poc-out/round3/ft-audit/sheets [--ids s20260905-0001 ...]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('TC_ROOT', os.path.abspath(os.path.join(HERE, '..', '..')))
sys.path.insert(0, HERE)
from ft_audit_sample import pdf_path  # noqa: E402

_docs = {}


def render(row, dpi=170):
    import fitz
    from PIL import Image, ImageDraw
    book, pdf = row['book'], row.get('pagePdf')
    bbox = (row.get('source') or {}).get('bbox') or row.get('bbox')
    path = pdf_path(book)
    if not path or not pdf:
        return None
    if book not in _docs:
        _docs[book] = fitz.open(path)
    doc = _docs[book]
    if pdf < 1 or pdf > len(doc):
        return None
    pg = doc[pdf - 1]; r = pg.rect
    if bbox:
        x, y, w, h = bbox
        px = 0.02 if w > 0.25 else 0.06          # tiny boxes get more horizontal context
        py = 0.02 if h > 0.05 else 0.03
        x0, y0 = max(0.0, x - px), max(0.0, y - py); x1, y1 = min(1.0, x + w + px), min(1.0, y + h + py)
        clip = fitz.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)
        pm = pg.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False, clip=clip)
        img = Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
        d = ImageDraw.Draw(img)
        sx = pm.width / clip.width; sy = pm.height / clip.height
        bx0 = (r.x0 + x * r.width - clip.x0) * sx; by0 = (r.y0 + y * r.height - clip.y0) * sy
        d.rectangle([bx0, by0, bx0 + w * r.width * sx, by0 + h * r.height * sy], outline=(220, 0, 0), width=3)
        return img
    pm = pg.get_pixmap(dpi=120, colorspace=fitz.csRGB, alpha=False)
    return Image.frombytes('RGB', (pm.width, pm.height), pm.samples)


def sheet(batch, out_png, max_w=1000):
    from PIL import Image, ImageDraw, ImageFont
    imgs = []
    for row in batch:
        im = render(row)
        if im is None and row.get('crop') and os.path.exists(f"{ROOT}/{row['crop']}"):
            im = Image.open(f"{ROOT}/{row['crop']}").convert('RGB')
        if im is None:
            im = Image.new('RGB', (600, 60), (255, 255, 255))
        if im.width > max_w:
            im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
        imgs.append((row['sampleId'], im))
    H = sum(im.height + 34 for _, im in imgs) + 10
    W = max(im.width for _, im in imgs) + 20
    canvas = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22)
    except Exception:  # noqa: BLE001
        font = ImageFont.load_default()
    y = 5
    for sid, im in imgs:
        d.rectangle([0, y, W, y + 28], fill=(30, 30, 30))
        d.text((10, y + 3), sid, fill=(255, 255, 0), font=font)
        y += 30
        canvas.paste(im, (10, y))
        y += im.height + 4
    canvas.save(out_png)
    return W, H


def est_height(row):
    """Rough rendered height (px) to pack sheets without rendering twice."""
    bbox = (row.get('source') or {}).get('bbox') or row.get('bbox')
    if not bbox:
        return 1500
    h = bbox[3] + (0.04 if bbox[3] > 0.05 else 0.06)
    w = bbox[2] + (0.04 if bbox[2] > 0.25 else 0.12)
    px_w = w * 1411; px_h = h * 1900          # 170 dpi ≈ 1411 × 1900 px for an A4-ish page
    scale = min(1.0, 1000 / max(1, px_w))
    return int(px_h * scale) + 34


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jsonl')
    ap.add_argument('--out', required=True)
    ap.add_argument('--ids', nargs='*')
    ap.add_argument('--max-h', type=int, default=1500)
    a = ap.parse_args()
    out = a.out if os.path.isabs(a.out) else f'{ROOT}/{a.out}'
    os.makedirs(out, exist_ok=True)
    rows = [json.loads(l) for l in open(a.jsonl, encoding='utf-8') if l.strip()]
    if a.ids:
        want = set(a.ids); rows = [r for r in rows if r['sampleId'] in want]
    manifest, batch, h, n = [], [], 0, 0

    def flush():
        nonlocal batch, h, n
        if batch:
            name = f'sheet-{n:03d}'
            W, H = sheet(batch, f'{out}/{name}.png')
            manifest.append(dict(sheet=name, ids=[r['sampleId'] for r in batch], w=W, h=H))
            n += 1; batch = []; h = 0

    for r in rows:
        eh = est_height(r)
        if batch and h + eh > a.max_h:
            flush()
        batch.append(r); h += eh
        if eh >= a.max_h:
            flush()
    flush()
    json.dump(manifest, open(f'{out}/manifest.json', 'w'), indent=1)
    print(f'{len(manifest)} sheets → {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
