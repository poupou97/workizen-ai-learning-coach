#!/usr/bin/env python3
"""Round 5 · Lane A4 — probe the cross-corpus signal on ad-hoc text.

    python3 tool/corpus/verify/probe.py "Năm 1010, Lý Thái Tô dời đô về Thăng Long." [--pairs "thái tổ" …]

Answers the only two questions that matter when a number surprises you: *what does the corpus actually say
about this phrase*, and *what would the signal do with it*. Runs its own context scan (≈2 min) over the
held-out corpus, so what it prints is what the measurement saw.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from verify import crosscorpus as xc, evalsets as es, index as ix, paths  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('texts', nargs='+')
    ap.add_argument('--pairs', nargs='*', default=[])
    ap.add_argument('--policy', default='recall', choices=sorted(dict(strict=1, default=1, recall=1)))
    ap.add_argument('--index', default=f'{paths.OUT}/xcorpus-index-heldout.json')
    a = ap.parse_args()

    idx = ix.CrossCorpusIndex.load(a.index)
    pol = dict(strict=xc.STRICT, default=xc.DEFAULT, recall=xc.RECALL)[a.policy]
    v = xc.CrossCorpusVerifier(idx, None, pol)
    keys = set()
    for t in a.texts:
        keys |= v.context_keys(t)
    for p in a.pairs:
        w = p.split()
        keys.add(tuple(ix.key_of(x) for x in w))
    ho, extra = es.held_out_books()
    scan = ix.ContextScan(keys, max_occ=6).run(paths.OCR_BODY, exclude_books=list(ho) + list(extra))

    for p in a.pairs:
        w = tuple(ix.norm_token(x) for x in p.split())
        occ = scan.occurrences(w)
        print(f'{p!r:34s} count={scan.count(w):6d} books≥{len({o["book"] for o in occ})}')
    v2 = xc.CrossCorpusVerifier(idx, scan, pol)
    for t in a.texts:
        print('\n---', t)
        for f in v2.analyse(t):
            print('   ', json.dumps({k: x for k, x in f.to_json().items()
                                     if k not in ('supporting', 'contradicting')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
