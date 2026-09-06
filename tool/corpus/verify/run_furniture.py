#!/usr/bin/env python3
"""Round 5 · Lane A4 — learn page furniture per book and measure the **bbox-edge risk** signal.

    python3 tool/corpus/verify/run_furniture.py [--books N] [--book NAME ...]

Two measurements, both on real corpus data and both reported whatever they say:

1. **Furniture.** What recurs on a book's pages, whether the KHTN 9 watermark bleed is among it, and what
   deleting it would do to the Founder's named defect row.
2. **Edge risk.** The coordinator's hypothesis, tested as one number: *does a token's distance from the
   edge of its line predict whether it is an OCR error?* Ground truth at scale is unavailable, so the
   proxy is «the corpus has never written this word» (`count == 0` in the 62,729-page index) — noisy, but
   unbiased with respect to position, which is the only thing that matters for a positional hypothesis.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import tc_score  # noqa: E402
from verify import furniture as F, index as ix, paths  # noqa: E402

KHTN9 = '09-sgk-khoa-hoc-tu-nhien-9'
KHTN9_DEFECT = 'I1 - Định luật khúc xạ ánh sáng, Ô C S ỐNG'
KHTN9_PRINTED = 'II – Định luật khúc xạ ánh sáng'


def edge_risk(idx, books, ocr_root=None, per_book=250):
    """Unattested-token rate by position in the line. Buckets: first token · last token · interior."""
    ocr_root = ocr_root or paths.OCR_BODY
    c = Counter()
    for book in books:
        bdir = os.path.join(ocr_root, book)
        names = sorted(n for n in os.listdir(bdir) if n.endswith('.json'))[:per_book]
        for name in names:
            with open(os.path.join(bdir, name), encoding='utf-8') as fh:
                page = json.load(fh)
            for line in page.get('lines') or ():
                toks = ix.tokens_of(line.get('text'))
                if len(toks) < 3:
                    continue
                x, w = line.get('x', 0), line.get('w', 0)
                right_edge = x + w > 0.90          # the line runs into the page's right margin
                for i, t in enumerate(toks):
                    if len(t) < 2 or t.isdigit():
                        continue
                    where = 'first' if i == 0 else ('last' if i == len(toks) - 1 else 'interior')
                    c[f'{where}_n'] += 1
                    c['edge_page_n' if (right_edge and where == 'last') else 'other_n'] += 1
                    if idx.count(t) == 0:
                        c[f'{where}_unattested'] += 1
                        c['edge_page_unattested' if (right_edge and where == 'last')
                          else 'other_unattested'] += 1
    def rate(a, b):
        return round(c[a] / c[b], 5) if c[b] else None
    return dict(
        first=dict(n=c['first_n'], unattested=c['first_unattested'],
                   rate=rate('first_unattested', 'first_n')),
        last=dict(n=c['last_n'], unattested=c['last_unattested'],
                  rate=rate('last_unattested', 'last_n')),
        interior=dict(n=c['interior_n'], unattested=c['interior_unattested'],
                      rate=rate('interior_unattested', 'interior_n')),
        last_token_of_a_line_running_into_the_right_margin=dict(
            n=c['edge_page_n'], unattested=c['edge_page_unattested'],
            rate=rate('edge_page_unattested', 'edge_page_n')),
        everything_else=dict(n=c['other_n'], unattested=c['other_unattested'],
                             rate=rate('other_unattested', 'other_n')),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--books', type=int, default=8)
    ap.add_argument('--book', action='append', default=[])
    ap.add_argument('--index', default=f'{paths.OUT}/xcorpus-index-heldout.json')
    a = ap.parse_args()

    books = a.book or [KHTN9]
    if not a.book:
        allb = sorted(b for b in os.listdir(paths.OCR_BODY)
                      if os.path.isdir(os.path.join(paths.OCR_BODY, b)))
        step = max(1, len(allb) // max(a.books - 1, 1))
        books = [KHTN9] + [b for b in allb[::step] if b != KHTN9][:a.books - 1]

    out = dict(books={}, defect={}, edge_risk=None)
    for book in books:
        f = F.PageFurniture.learn(book)
        clusters = sorted(f.meta.get('cluster_index', {}).values(), key=lambda v: -v['pages'])[:10]
        out['books'][book] = dict(pages=f.pages, keys=len(f.fragments),
                                  clusters=f.meta.get('clusters'),
                                  top=[dict(pages=v['pages'], share=v['page_share'], kind=v['kind'],
                                            variants=v['variants'],
                                            surfaces=[s for s, _ in v['surfaces'][:5]],
                                            x=v['x'], y=v['y']) for v in clusters])
        print(f"\n{book}: {f.pages} pages · {f.meta.get('clusters')} furniture clusters "
              f"({len(f.fragments)} keys)")
        for v in clusters:
            print(f"   {v['pages']:4d}/{f.pages} ({v['page_share']:.2f}) {v['kind']:14s} "
                  f"var={v['variants']:3d} x={v['x']:.2f} y={v['y']:.2f} {[s for s, _ in v['surfaces'][:4]]}")
        if book == KHTN9:
            cleaned, removed = f.strip(KHTN9_DEFECT)
            out['defect'] = dict(observed=KHTN9_DEFECT, printed=KHTN9_PRINTED, cleaned=cleaned,
                                 removed=[dict(phrase=p, pages=r['pages'], share=r['page_share'])
                                          for p, r in removed],
                                 remaining_defect=(tc_score.norm_key(cleaned)
                                                   != tc_score.norm_key(KHTN9_PRINTED)))
            print(f'\n  FOUNDER DEFECT ROW\n   observed: {KHTN9_DEFECT!r}\n'
                  f'   printed : {KHTN9_PRINTED!r}\n   cleaned : {cleaned!r}\n'
                  f"   removed : {[(p, r['pages']) for p, r in removed]}")
            with open(f'{paths.OUT}/furniture-{book}.json', 'w', encoding='utf-8') as fh:
                json.dump(f.to_json(), fh, ensure_ascii=False, indent=1)

    if os.path.exists(a.index):
        idx = ix.CrossCorpusIndex.load(a.index)
        # The measurement must run on books the index does NOT contain. Measured on an included book every
        # rate is exactly 0 by construction — the book attests its own tokens — which is what the first
        # run of this script printed, and is a measurement bug, not a finding.
        from verify import evalsets as _es
        held, _ = _es.held_out_books()
        out['edge_risk'] = edge_risk(idx, held)
        out['edge_risk_books'] = held
        print('\n=== EDGE RISK (unattested-token rate by position in the line, HELD-OUT books only) ===')
        for k, v in out['edge_risk'].items():
            print(f'  {k:58s} n={v["n"]:7d} rate={v["rate"]}')

    with open(f'{paths.OUT}/furniture-report.json', 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
