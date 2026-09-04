#!/usr/bin/env python3
"""Trusted-Corpus study (TC-v1) — K-12 LAYOUT CENSUS over the whole SGK/SGV corpus.

Why: the Founder's question is not "does OCR work" but "what layouts exist,
how many pages carry each, and which of them can be trusted". This census
measures page-level layout FEATURES from two independent signals:

  (a) OCR line geometry  — poc-out/graph/ocr-body/<book>/pNNN.json
      (Apple Vision, one box per line, normalised x/y/w/h, conf)
  (b) a low-resolution render of the source PDF page (PyMuPDF, 30 dpi)
      — ink outside OCR boxes (figures/diagrams), coloured backgrounds
      under text lines (activity boxes / sidebars / elementary visual
      layouts), colour share of the page.

Every feature is a boolean or a share per page; a page may carry MANY
features. The report NEVER sums feature counts into a total — it reports
overlaps as a feature matrix and a "layout family" signature per page.

Features per page
  sparse        < 3 OCR lines or < 40 chars (image-only / cover / blank)
  native_text   the PDF page has a text layer (measured on the PDF itself)
  columns       1 / 2 / 3 — number of text columns in the body band,
                from an x-coverage profile (empty vertical band, both sides
                populated, few lines crossing the band)
  table         ≥ 4 aligned rows × ≥ 3 cells of short tokens
  formula       ≥ 3 lines with math tokens (fractions, =, ×, ÷, √, ², …)
  sidebar       a labelled box (Em có biết / Lưu ý / Ghi nhớ …) or a narrow
                right-side stack of ≥ 3 lines beside wide body lines
  figure        ink outside (dilated) OCR boxes ≥ 4 % of page area
  diagram       figure AND ≥ 8 short scattered labels (≤ 3 words)
  colored_box   ≥ 10 % of OCR lines sit on a coloured background
  color_heavy   ≥ 25 % of page pixels are saturated colour (elementary
                visual layouts)
  continuation  first body line begins lower-case (cross-page paragraph)
  overlap       > 5 % of OCR boxes overlap (rotated text / bad OCR)
  low_conf      mean OCR confidence < 0.75
  mixed         figure AND ≥ 10 text lines

Output: poc-out/trusted-corpus/<ver>/census/pages.jsonl (one row per page)
        poc-out/trusted-corpus/<ver>/census/summary.json
Usage:  python3 tool/corpus/tc_layout_census.py [--ver tc-v1] [--books N] [--workers 6]
Deterministic; resumable (existing rows in pages.jsonl are skipped).
"""
import argparse
import glob
import json
import os
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OCR = f'{ROOT}/poc-out/graph/ocr-body'
PDF = f'{ROOT}/poc-out/pdf'
STRUCT = f'{ROOT}/poc-out/graph/curriculum-structure.json'

SIDEBAR_LABEL = re.compile(r'^(Em có biết|EM CÓ BIẾT|Lưu ý|LƯU Ý|Ghi nhớ|GHI NHỚ|Chú ý|CHÚ Ý|Mở rộng|MỞ RỘNG|Kết nối|KẾT NỐI|Em cần biết|EM CẦN BIẾT|Bạn có biết|Có thể em chưa biết)\b')
MATH = re.compile(r'(\d\s*[/:]\s*\d|[=×÷√∑∫≤≥≠±²³°]|\^|\b[xyab]\s*[=+\-]\s*\d|\bcm2\b|\bm2\b|\bkm2\b|\d\s*[+\-]\s*\d\s*=)')
DIGITS = re.compile(r'^\d{1,4}$')


def pdf_path(book):
    grade = book[:2]
    p = f'{PDF}/{grade}/{book}.pdf'
    if os.path.exists(p):
        return p
    p2 = f'{PDF}/{book}.pdf'
    return p2 if os.path.exists(p2) else None


def columns_of(lines):
    """Count text columns in the body band from an x-coverage profile."""
    body = [l for l in lines if 0.10 < l['y'] < 0.90 and l['w'] > 0.04]
    if len(body) < 8:
        return 1, []
    bins = 200
    cov = [0] * bins
    for l in body:
        a, b = int(l['x'] * bins), min(bins - 1, int((l['x'] + l['w']) * bins))
        for i in range(a, b + 1):
            cov[i] += 1
    thr = max(1, 0.03 * len(body))
    gaps, i = [], 0
    while i < bins:
        if cov[i] <= thr:
            j = i
            while j < bins and cov[j] <= thr:
                j += 1
            x0, x1 = i / bins, j / bins
            if 0.22 < x0 and x1 < 0.80 and (x1 - x0) >= 0.015:
                gaps.append(((x0 + x1) / 2, x1 - x0))
            i = j
        else:
            i += 1
    good = []
    for gx, gw in gaps:
        left = [l for l in body if l['x'] + l['w'] <= gx + 0.005]
        right = [l for l in body if l['x'] >= gx - 0.005]
        cross = [l for l in body if l['x'] < gx - 0.02 and l['x'] + l['w'] > gx + 0.02]
        if len(left) >= 4 and len(right) >= 4 and len(cross) <= 0.15 * len(body):
            good.append(round(gx, 3))
    return min(3, 1 + len(good)), good


def table_of(lines):
    rows = defaultdict(list)
    for l in lines:
        if len(l['text'].split()) <= 3 and l['w'] < 0.3:
            rows[round(l['y'] / 0.012)].append(l)
    aligned = [r for r in rows.values() if len(r) >= 3]
    return len(aligned) >= 4


def sidebar_of(lines):
    if any(SIDEBAR_LABEL.match(l['text'].strip()) for l in lines):
        return True
    wide = [l for l in lines if l['w'] > 0.5]
    narrow_right = [l for l in lines if l['x'] > 0.58 and l['w'] < 0.35 and 0.1 < l['y'] < 0.9]
    if len(wide) >= 3 and len(narrow_right) >= 3:
        # side-by-side: narrow-right lines whose y-band overlaps a left-side (x<0.5, w<0.45) line
        left = [l for l in lines if l['x'] < 0.45 and l['x'] + l['w'] < 0.6 and l['w'] > 0.12]
        beside = 0
        for r in narrow_right:
            if any(abs(r['y'] - a['y']) < 0.03 for a in left):
                beside += 1
        return beside >= 3
    return False


def render_features(pdf, page_no, lines):
    """Low-res render (30 dpi): ink outside OCR boxes, coloured background under lines, colour share."""
    try:
        import fitz
        import numpy as np
    except Exception as e:  # pragma: no cover
        return dict(render_error=str(e))
    try:
        doc = fitz.open(pdf)
        if page_no - 1 >= doc.page_count:
            return dict(render_error='page out of range')
        pg = doc[page_no - 1]
        native_chars = len(pg.get_text('text').strip())
        pm = pg.get_pixmap(dpi=30, colorspace=fitz.csRGB, alpha=False)
        img = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3).astype(np.int16)
        doc.close()
    except Exception as e:
        return dict(render_error=str(e)[:80])
    h, w = img.shape[:2]
    mx = img.max(axis=2); mn = img.min(axis=2)
    sat = (mx - mn)
    ink = (mx < 200) | (sat > 60)          # dark or coloured pixel
    colored = (sat > 60) & (mx > 120)      # coloured (not dark) pixel
    textmask = np.zeros((h, w), dtype=bool)
    for l in lines:
        x0 = max(0, int((l['x'] - 0.006) * w)); x1 = min(w, int((l['x'] + l['w'] + 0.006) * w) + 1)
        y0 = max(0, int((l['y'] - 0.004) * h)); y1 = min(h, int((l['y'] + l['h'] + 0.004) * h) + 1)
        textmask[y0:y1, x0:x1] = True
    # margins excluded (binding shadow / page edge)
    m = np.zeros((h, w), dtype=bool); m[int(0.02 * h):int(0.98 * h), int(0.02 * w):int(0.98 * w)] = True
    fig_share = float((ink & ~textmask & m).sum()) / float(m.sum())
    color_share = float((colored & m).sum()) / float(m.sum())
    on_color = 0
    for l in lines:
        x0 = int(l['x'] * w); x1 = min(w, int((l['x'] + l['w']) * w) + 1)
        y0 = int(l['y'] * h); y1 = min(h, int((l['y'] + l['h']) * h) + 1)
        if y1 <= y0 or x1 <= x0:
            continue
        patch_sat = sat[y0:y1, x0:x1]; patch_mx = mx[y0:y1, x0:x1]
        bg = (patch_mx > 140)
        if bg.sum() == 0:
            continue
        if float((patch_sat[bg] > 45).mean()) > 0.5:
            on_color += 1
    return dict(native_chars=native_chars, fig_share=round(fig_share, 4), color_share=round(color_share, 4),
                on_color_share=round(on_color / max(1, len(lines)), 3))


def census_page(args):
    book, fp, pdf = args
    page_no = int(re.search(r'p(\d+)\.json', fp).group(1))
    try:
        j = json.load(open(fp))
    except Exception as e:
        return dict(book=book, page=page_no, error=str(e)[:80])
    lines = [l for l in j.get('lines', []) if l.get('w', 0) > 0 and l.get('text', '').strip()]
    chars = sum(len(l['text']) for l in lines)
    row = dict(book=book, page=page_no, n_lines=len(lines), chars=chars,
               conf=round(statistics.mean(l.get('conf', 1) for l in lines), 3) if lines else 0.0)
    row['sparse'] = len(lines) < 3 or chars < 40
    if not row['sparse']:
        ncol, gaps = columns_of(lines)
        row['columns'] = ncol; row['col_gaps'] = gaps
        row['table'] = table_of(lines)
        row['formula'] = sum(1 for l in lines if MATH.search(l['text'])) >= 3
        row['sidebar'] = sidebar_of(lines)
        short = [l for l in lines if len(l['text'].split()) <= 3 and not DIGITS.match(l['text'].strip())]
        row['short_labels'] = len(short)
        body = sorted([l for l in lines if 0.08 < l['y'] < 0.92], key=lambda l: (l['y'], l['x']))
        row['continuation'] = bool(body) and body[0]['text'].strip()[:1].islower()
        # overlap share (same rule as layout_extract)
        n = 0
        bs = sorted(lines, key=lambda b: b['y'])
        for i, a in enumerate(bs):
            for b in bs[i + 1:i + 6]:
                if b['y'] > a['y'] + a['h']:
                    break
                ix = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x'])
                iy = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])
                if ix > 0 and iy > 0.5 * min(a['h'], b['h']) and ix > 0.3 * min(a['w'], b['w']):
                    n += 1
        row['overlap'] = n / max(1, len(lines)) > 0.05
        row['low_conf'] = row['conf'] < 0.75
    else:
        row.update(columns=0, col_gaps=[], table=False, formula=False, sidebar=False, short_labels=0,
                   continuation=False, overlap=False, low_conf=False)
    if pdf:
        row.update(render_features(pdf, page_no, lines))
    fig = row.get('fig_share', 0.0) >= 0.04
    row['figure'] = fig
    row['diagram'] = fig and row['short_labels'] >= 8
    row['colored_box'] = row.get('on_color_share', 0.0) >= 0.10
    row['color_heavy'] = row.get('color_share', 0.0) >= 0.25
    row['mixed'] = fig and row['n_lines'] >= 10
    row['native_text'] = row.get('native_chars', 0) > 20
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ver', default='tc-v1')
    ap.add_argument('--books', type=int, default=0, help='limit number of books (0 = all)')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--only', default='', help='comma-separated book ids')
    a = ap.parse_args()
    out_dir = f'{ROOT}/poc-out/trusted-corpus/{a.ver}/census'
    os.makedirs(out_dir, exist_ok=True)
    out_path = f'{out_dir}/pages.jsonl'
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            try:
                r = json.loads(line); done.add((r['book'], r['page']))
            except Exception:
                pass
    books = sorted(os.listdir(OCR))
    if a.only:
        books = [b for b in books if b in set(a.only.split(','))]
    if a.books:
        books = books[:a.books]
    jobs = []
    for b in books:
        pdf = pdf_path(b)
        for fp in sorted(glob.glob(f'{OCR}/{b}/p*.json')):
            pn = int(re.search(r'p(\d+)\.json', fp).group(1))
            if (b, pn) not in done:
                jobs.append((b, fp, pdf))
    print(f'books={len(books)} pages_todo={len(jobs)} already={len(done)}', flush=True)
    t0 = time.time()
    with open(out_path, 'a') as out, Pool(a.workers) as pool:
        for i, row in enumerate(pool.imap_unordered(census_page, jobs, chunksize=16)):
            out.write(json.dumps(row, ensure_ascii=False) + '\n')
            if i % 2000 == 0:
                print(f'{i}/{len(jobs)} {time.time() - t0:.0f}s', flush=True)
    print(f'done {len(jobs)} pages in {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
