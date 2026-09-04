#!/usr/bin/env python3
"""TC-v1 — census augmentation: LOCAL side-by-side regions (OCR geometry only).

Why: a page can be globally single-column and still contain rows where two
text blocks sit side by side (exercise pairs "a) … b) …", a text box beside
a figure, two boxes "EM ĐÃ HỌC | EM CÓ THỂ"). Those rows are exactly what a
naive top→bottom line sort interleaves (WAL-204). The global `columns`
feature of tc_layout_census.py misses them by design, and the WAL-206
census ("30.6 % two-column") counted them. Both are reported, separately.

Adds to every row of pages.jsonl:
  sbs_rows    number of y-bands (≥ 1 line height) containing ≥ 2 lines that
              are horizontally separated by ≥ 3 % of the page width
  sbs_share   sbs_rows / number of y-bands with text
  side_by_side  sbs_rows ≥ 3 and sbs_share ≥ 0.15   (a real local multi-column region)
Usage: python3 tool/corpus/tc_census_augment.py [--ver tc-v1]
"""
import argparse
import json
import os
import re
import statistics

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OCR = f'{ROOT}/poc-out/graph/ocr-body'
DIGITS = re.compile(r'^\d{1,4}$')


def sbs(lines):
    body = [l for l in lines if 0.06 < l['y'] < 0.94 and not DIGITS.match(l['text'].strip())]
    if len(body) < 4:
        return 0, 0.0
    med_h = statistics.median(l['h'] for l in body) or 0.01
    body.sort(key=lambda l: l['y'])
    bands, cur = [], [body[0]]
    for l in body[1:]:
        if l['y'] - cur[-1]['y'] < 0.8 * med_h:
            cur.append(l)
        else:
            bands.append(cur); cur = [l]
    bands.append(cur)
    n = 0
    for band in bands:
        if len(band) < 2:
            continue
        xs = sorted((l['x'], l['x'] + l['w']) for l in band)
        sep = False; end = xs[0][1]
        for x0, x1 in xs[1:]:
            if x0 - end >= 0.03:
                sep = True
            end = max(end, x1)
        if sep:
            n += 1
    return n, n / len(bands)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ver', default='tc-v1'); a = ap.parse_args()
    path = f'{ROOT}/poc-out/trusted-corpus/{a.ver}/census/pages.jsonl'
    rows = [json.loads(l) for l in open(path)]
    for i, r in enumerate(rows):
        try:
            j = json.load(open(f"{OCR}/{r['book']}/p{r['page']:03d}.json"))
            lines = [l for l in j.get('lines', []) if l.get('w', 0) > 0 and l.get('text', '').strip()]
            n, share = sbs(lines)
        except Exception:
            n, share = 0, 0.0
        r['sbs_rows'] = n; r['sbs_share'] = round(share, 3)
        r['side_by_side'] = n >= 3 and share >= 0.15
        if i % 10000 == 0:
            print(i, flush=True)
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    os.replace(tmp, path)
    print('side_by_side pages', sum(1 for r in rows if r['side_by_side']), '/', len(rows))


if __name__ == '__main__':
    main()
