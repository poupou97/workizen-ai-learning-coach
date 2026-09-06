#!/usr/bin/env python3
"""Round 5 · Lane A4 — build the held-out index + context scan, and measure the cross-corpus signal.

    python3 tool/corpus/verify/run_xcorpus.py [--rebuild] [--per-book 40]

Writes only under `poc-out/round5/verify/`. Reads the corpus read-only.

The measurement is deliberately structured so no number can flatter itself:

* the index and the context scan **exclude every book being evaluated** (Lane C's LS&ĐL 5 and the 12
  holdout books), so a book can never verify itself;
* the injection holdout is measured **twice** — once on the corrupted rows (detection recall, correction
  precision) and once on the *same rows uncorrupted* (**false correction rate**, the P0 metric, where the
  right answer for every token is «propose nothing»);
* three policies are reported side by side (STRICT · DEFAULT · RECALL), never one tuned point.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from verify import crosscorpus as xc, evalsets as es, index as ix, paths  # noqa: E402

HELD_INDEX = f'{paths.OUT}/xcorpus-index-heldout.json'
SCAN_CACHE = f'{paths.OUT}/context-scan.json'


def build_held_index(excluded, rebuild=False):
    if os.path.exists(HELD_INDEX) and not rebuild:
        idx = ix.CrossCorpusIndex.load(HELD_INDEX)
        if set(idx.meta.get('excluded') or ()) == set(excluded):
            return idx
    books = [b for b in sorted(os.listdir(paths.OCR_BODY))
             if os.path.isdir(os.path.join(paths.OCR_BODY, b)) and b not in set(excluded)]
    t0 = time.time()
    idx = ix.CrossCorpusIndex.build(paths.OCR_BODY, books=books)
    idx.meta['excluded'] = sorted(excluded)
    idx.meta['build_seconds'] = round(time.time() - t0, 1)
    idx.save(HELD_INDEX)
    return idx


def collect_texts():
    """Every text the lane will ask the corpus about, in one place, so a single scan answers all of them."""
    holdout_books, extra = es.held_out_books()
    excluded = sorted(set(holdout_books) | set(extra))
    clean = es.holdout_lines(holdout_books, per_book=ARGS.per_book)
    corrupt = es.inject(clean)
    lanec = es.lanec_bai8()
    poc = es.poc_cases()
    texts = ([c['observed'] for c in poc] + [c['correct'] for c in poc]
             + [r['text'] for r in lanec]
             + [r['text'] for r in clean] + [r['corrupted'] for r in corrupt])
    return dict(holdout_books=holdout_books, excluded=excluded, clean=clean, corrupt=corrupt,
                lanec=lanec, poc=poc, texts=texts)


def run_scan(idx, texts, excluded, rebuild=False):
    v = xc.CrossCorpusVerifier(idx, None, xc.RECALL)
    keys = set()
    for t in texts:
        keys |= v.context_keys(t)
    t0 = time.time()
    scan = ix.ContextScan(keys, max_occ=6, ngram=2)
    scan.run(paths.OCR_BODY, exclude_books=excluded)
    return scan, dict(keys=len(keys), seconds=round(time.time() - t0, 1))


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument('--rebuild', action='store_true')
    ap.add_argument('--per-book', type=int, default=40)
    ARGS = ap.parse_args()

    d = collect_texts()
    print(f"holdout books: {len(d['holdout_books'])} · excluded from the index: {len(d['excluded'])}")
    print(f"clean rows {len(d['clean'])} · corrupted rows {len(d['corrupt'])} · "
          f"Lane C rows {len(d['lanec'])} · POC {len(d['poc'])}", flush=True)

    idx = build_held_index(d['excluded'], rebuild=ARGS.rebuild)
    print('index:', {k: idx.meta[k] for k in ('books', 'pages', 'distinct_forms') if k in idx.meta},
          flush=True)
    scan, sm = run_scan(idx, d['texts'], d['excluded'], rebuild=ARGS.rebuild)
    print('context scan:', sm, flush=True)

    out = dict(index=idx.meta, scan=sm, holdout_books=d['holdout_books'])
    os.makedirs(paths.OUT, exist_ok=True)
    with open(f'{paths.OUT}/xcorpus-run-meta.json', 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    # hand the loaded objects to the measurement module
    from verify import measure
    measure.run_all(idx, scan, d)


if __name__ == '__main__':
    main()
