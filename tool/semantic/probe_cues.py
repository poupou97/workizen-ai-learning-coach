#!/usr/bin/env python3
"""Lane E1 · DISCOVER step 2 — measure a named cue set against the corpus.

`discover_markers.py` ranks what recurs; this probe asks the follow-up question for a
specific candidate cue ("does 'so sánh' actually exist corpus-wide, or did I imagine
it?"). It exists so that no cue enters `ontology.py` on intuition: every cue in the
ontology must have a measured lesson count printed by this probe.

    python3 tool/semantic/probe_cues.py "so sánh" "giống nhau" "nguyên nhân"
"""
import argparse
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus_io as cio  # noqa: E402


def probe(cues, layer='units'):
    """Return {cue: {'lessons': n, 'subjects': n, 'books': n, 'hits': n}}."""
    pats = {c: re.compile(re.escape(cio.norm(c))) for c in cues}
    lessons = collections.defaultdict(set)
    subjects = collections.defaultdict(set)
    books = collections.defaultdict(set)
    hits = collections.Counter()
    total = set()
    if layer == 'units':
        stream = ((b, s or '?', cio.lesson_key(b, l), [u['text'] for u in us])
                  for b, s, l, us in cio.iter_units_lessons())
    else:
        stream = ((les['book'], les['book'], cio.lesson_key(les['book'], les['lesson']),
                   [x['text'] for x in les['blocks']]) for les in cio.iter_tsl())
    for book, subject, lkey, texts in stream:
        total.add(lkey)
        blob = ' \n '.join(cio.norm(t) for t in texts)
        for c, p in pats.items():
            n = len(p.findall(blob))
            if n:
                hits[c] += n
                lessons[c].add(lkey)
                subjects[c].add(subject)
                books[c].add(book)
    return {c: {'lessons': len(lessons[c]), 'pct': round(100.0 * len(lessons[c]) / max(1, len(total)), 1),
                'subjects': len(subjects[c]), 'books': len(books[c]), 'hits': hits[c]}
            for c in cues}, len(total)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('cues', nargs='+')
    ap.add_argument('--layer', choices=['units', 'tsl'], default='units')
    args = ap.parse_args(argv)
    res, total = probe(args.cues, args.layer)
    print('layer=%s denominator_lessons=%d' % (args.layer, total))
    for c in sorted(res, key=lambda x: -res[x]['lessons']):
        r = res[c]
        print('%6d %5.1f%% s=%2d b=%3d hits=%-7d %s'
              % (r['lessons'], r['pct'], r['subjects'], r['books'], r['hits'], c))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
