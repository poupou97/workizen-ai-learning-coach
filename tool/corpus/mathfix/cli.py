#!/usr/bin/env python3
"""Lane A2 CLI — census, projection and the hand-check contact sheet.

  python3 tool/corpus/mathfix/cli.py census  --book 05-sgk-toan-5-tap-mot --pages 20-24
  python3 tool/corpus/mathfix/cli.py census  --books toan-sgk --sample 60 --seed 20260906
  python3 tool/corpus/mathfix/cli.py project --sdm <dir> --book <book> --pages 20-24
  python3 tool/corpus/mathfix/cli.py crops   --book <book> --page 23 --out DIR

Everything is written under `poc-out/round5/mathfix/`. Corpus never enters the repo.
Requires PyMuPDF + numpy (the page raster); the library itself does not.
"""
import argparse
import glob
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathfix import runner as R          # noqa: E402
from mathfix.tokens import OCR_BODY      # noqa: E402

OUT = R.OUT


def parse_pages(spec):
    out = []
    for part in (spec or '').split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def toan_books(grades=range(1, 10)):
    pre = tuple(f'{g:02d}-sgk-toan' for g in grades)
    return sorted(b for b in os.listdir(OCR_BODY) if b.startswith(pre))


def book_pages(book):
    return sorted(int(os.path.basename(p)[1:4])
                  for p in glob.glob(f'{OCR_BODY}/{book}/p*.json'))


def cmd_census(a):
    books = [a.book] if a.book else toan_books()
    pairs = [(b, p) for b in books for p in (parse_pages(a.pages) or book_pages(b))]
    if a.sample:
        random.Random(a.seed).shuffle(pairs)
        pairs = sorted(pairs[:a.sample])
    os.makedirs(a.out or OUT, exist_ok=True)
    rows = []
    for book, page in pairs:
        try:
            rep = R.page_report(book, page, dpi=a.dpi)
        except Exception as exc:                    # a page with no OCR / no PDF is recorded, not hidden
            rows.append(dict(book=book, page=page, error=str(exc)))
            continue
        R.write_report(rep, a.out)
        rows.append(dict(book=book, page=page, regions=len(rep['regions']),
                         extractable=sum(1 for r in rep['regions'] if r['extractable']),
                         reasons=_count(r['reason'] for r in rep['regions'] if not r['extractable']),
                         token_kinds=rep['token_kinds']))
        print(f"{book} p{page:3d}  regions={rows[-1].get('regions')} "
              f"extractable={rows[-1].get('extractable')}")
    path = os.path.join(a.out or OUT, 'census.json')
    with open(path, 'w') as fh:
        json.dump(dict(pages=len(pairs), rows=rows), fh, ensure_ascii=False, indent=1)
    print('->', path)


def _count(it):
    out = {}
    for x in it:
        out[x or 'ok'] = out.get(x or 'ok', 0) + 1
    return out


def cmd_project(a):
    pages = parse_pages(a.pages) or book_pages(a.book)
    out = []
    for page in pages:
        sdm_path = f'{a.sdm}/{a.book}/p{page:03d}.sdm.json'
        if not os.path.exists(sdm_path):
            print(f'no sdm for p{page}: {sdm_path}')
            continue
        with open(sdm_path) as fh:
            sdm = json.load(fh)
        rep = R.page_report(a.book, page, sdm=sdm, dpi=a.dpi)
        R.write_report(rep, a.out)
        for b in rep['blocks']:
            out.append(b)
            print(f"p{page:3d} {b['block_id'][-3:]} {b['status']:8s} eligible={b['eligible']!s:5s} "
                  f"{b['verdict']:8s} {b['disposition']:16s} {b['candidate_reason'] or b['proposed_value']}")
    path = os.path.join(a.out or OUT, f'projection-{a.book}.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        json.dump(dict(book=a.book, blocks=out), fh, ensure_ascii=False, indent=1)
    print('->', path)


def cmd_crops(a):
    """Render each detected region as a crop, so a withheld region keeps the printed formula."""
    import pymupdf
    rep = R.page_report(a.book, a.page, dpi=a.dpi)
    d = a.out or f'{OUT}/crops'
    os.makedirs(d, exist_ok=True)
    doc = pymupdf.open(R.pdf_path(a.book))
    pg = doc[a.page - 1]
    W, H = pg.rect.width, pg.rect.height
    for i, r in enumerate(rep['regions']):
        x0, y0, x1, y1 = r['bbox']
        pad = 0.006
        clip = pymupdf.Rect((x0 - pad) * W, (y0 - pad) * H, (x1 + pad) * W, (y1 + pad) * H)
        p = f"{d}/{a.book}-p{a.page:03d}-region-{i:02d}.png"
        pg.get_pixmap(dpi=220, clip=clip).save(p)
    print(f'{len(rep["regions"])} crops -> {d}')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('census', 'project', 'crops'):
        s = sub.add_parser(name)
        s.add_argument('--book')
        s.add_argument('--pages')
        s.add_argument('--page', type=int)
        s.add_argument('--sdm')
        s.add_argument('--sample', type=int)
        s.add_argument('--seed', type=int, default=20260906)
        s.add_argument('--dpi', type=int, default=300)
        s.add_argument('--out')
    a = ap.parse_args(argv)
    return dict(census=cmd_census, project=cmd_project, crops=cmd_crops)[a.cmd](a)


if __name__ == '__main__':
    main()
