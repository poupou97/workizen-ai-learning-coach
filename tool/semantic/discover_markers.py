#!/usr/bin/env python3
"""Lane E1 · DISCOVER — mine the corpus for recurring *relational* discourse markers.

The Founder's primitive list is a CANDIDATE list. This step does not read it. It asks
the corpus a narrower question:

    which short phrases recur across many DIFFERENT subjects and books, i.e. are part
    of the shared textbook grammar rather than of one topic?

Method (fully deterministic, no LLM):
  1. take every unit/block text in the corpus layer,
  2. emit normalised 1..4-grams,
  3. keep an n-gram only if it appears in >= MIN_SUBJECTS distinct subjects and
     >= MIN_BOOKS distinct books (this is the filter that removes topic vocabulary —
     "quang hợp" is frequent but lives in one subject; "vì sao" lives in all of them),
  4. rank by the number of distinct LESSONS it touches (the census denominator unit).

The output is a ranked marker list. Clustering markers into relation types is a
separate, recorded human step (see ontology.py: every cue there cites the marker rank
that justified it). No marker becomes a semantic claim by itself.

Usage:
    python3 tool/semantic/discover_markers.py --layer units --top 400
    python3 tool/semantic/discover_markers.py --layer tsl --top 400
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus_io as cio  # noqa: E402
import corpus_paths as cp  # noqa: E402

MAX_N = 4
MIN_SUBJECTS = 6
MIN_BOOKS = 20
MIN_LESSONS = 40


def ngrams(ws, max_n=MAX_N):
    for n in range(1, max_n + 1):
        for i in range(len(ws) - n + 1):
            yield ' '.join(ws[i:i + n])


def mine(records, max_n=MAX_N):
    """records: iterable of (subject, book, lesson_key, text). Returns marker stats."""
    subj = collections.defaultdict(set)
    books = collections.defaultdict(set)
    lessons = collections.defaultdict(set)
    total_lessons = set()
    for subject, book, lkey, text in records:
        total_lessons.add(lkey)
        ws = cio.words(text)
        if not ws:
            continue
        for g in set(ngrams(ws, max_n)):
            subj[g].add(subject)
            books[g].add(book)
            lessons[g].add(lkey)
    return subj, books, lessons, total_lessons


def rank(subj, books, lessons, total_lessons,
         min_subjects=MIN_SUBJECTS, min_books=MIN_BOOKS, min_lessons=MIN_LESSONS):
    rows = []
    n_total = max(1, len(total_lessons))
    for g, ls in lessons.items():
        if len(ls) < min_lessons:
            continue
        if len(subj[g]) < min_subjects or len(books[g]) < min_books:
            continue
        rows.append({
            'marker': g,
            'n_words': len(g.split(' ')),
            'lessons': len(ls),
            'pct_lessons': round(100.0 * len(ls) / n_total, 2),
            'subjects': len(subj[g]),
            'books': len(books[g]),
        })
    rows.sort(key=lambda r: (-r['lessons'], -r['subjects'], r['marker']))
    return rows


def records_units():
    for book, subject, lesson, units in cio.iter_units_lessons():
        lkey = cio.lesson_key(book, lesson)
        for u in units:
            yield subject or '?', book, lkey, u['text']


def records_tsl():
    for les in cio.iter_tsl():
        lkey = cio.lesson_key(les['book'], les['lesson'])
        for b in les['blocks']:
            yield les['book'], les['book'], lkey, b['text']


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--layer', choices=['units', 'tsl'], default='units')
    ap.add_argument('--top', type=int, default=400)
    ap.add_argument('--min-subjects', type=int, default=MIN_SUBJECTS)
    ap.add_argument('--min-books', type=int, default=MIN_BOOKS)
    ap.add_argument('--min-lessons', type=int, default=MIN_LESSONS)
    ap.add_argument('--min-words', type=int, default=1,
                    help='keep only n-grams of at least this many words (2+ = discourse)')
    args = ap.parse_args(argv)

    recs = records_units() if args.layer == 'units' else records_tsl()
    if args.layer == 'tsl':
        args.min_subjects, args.min_books = 1, 1
    subj, books, lessons, total = mine(recs)
    rows = rank(subj, books, lessons, total,
                args.min_subjects, args.min_books, args.min_lessons)
    if args.min_words > 1:
        rows = [r for r in rows if r['n_words'] >= args.min_words]
    out = {
        'layer': args.layer,
        'min_words': args.min_words,
        'denominator_lessons': len(total),
        'filters': {'min_subjects': args.min_subjects, 'min_books': args.min_books,
                    'min_lessons': args.min_lessons, 'max_n': MAX_N},
        'n_markers_kept': len(rows),
        'markers': rows[:args.top],
    }
    path = os.path.join(cp.out_dir('discover'), 'markers-%s.json' % args.layer)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print('layer=%s lessons=%d markers_kept=%d -> %s'
          % (args.layer, len(total), len(rows), path))
    for r in rows[:args.top]:
        print('%6d %5.1f%% s=%2d b=%3d  %s'
              % (r['lessons'], r['pct_lessons'], r['subjects'], r['books'], r['marker']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
