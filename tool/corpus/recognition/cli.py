#!/usr/bin/env python3
"""Workstream B CLI — census first, then the re-crop experiment.

  python3 tool/corpus/recognition/cli.py lines   [--books-glob '*'] [--max-pages N]
  python3 tool/corpus/recognition/cli.py regions --book B --pages 20-24
  python3 tool/corpus/recognition/cli.py recrop  --book B --pages 20-24 [--sheet]
  python3 tool/corpus/recognition/cli.py sample  --books toan-sgk --sample 20 --seed 20260906

Everything is written under `poc-out/round6/recognition/`. The corpus never enters the repo.
"""
import argparse
import glob
import json
import os
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recognition import census as CE          # noqa: E402
from recognition import recrop as RC          # noqa: E402
from recognition import vision as V           # noqa: E402

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OCR_BODY = f'{ROOT}/poc-out/graph/ocr-body'
OUT = f'{ROOT}/poc-out/round6/recognition'


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


def book_pages(book):
    return sorted(int(os.path.basename(p)[1:4]) for p in glob.glob(f'{OCR_BODY}/{book}/p*.json'))


def has_pdf(book):
    return os.path.exists(V.pdf_path(book))


# ---------------------------------------------------------------- LINE census
def cmd_lines(a):
    books = sorted(b for b in os.listdir(OCR_BODY) if glob.fnmatch.fnmatch(b, a.books_glob))
    findings, lines_by_book = [], defaultdict(list)
    n_lines = n_pages = 0
    for book in books:
        for path in sorted(glob.glob(f'{OCR_BODY}/{book}/p*.json')):
            page = int(os.path.basename(path)[1:4])
            try:
                with open(path) as fh:
                    doc = json.load(fh)
            except Exception:
                continue
            n_pages += 1
            for ln in doc.get('lines') or []:
                text = ln.get('text') or ''
                n_lines += 1
                if a.diacritics:
                    lines_by_book[book].append(text)
                findings.extend(CE.line_findings(
                    book, page, text,
                    bbox=(ln.get('x'), ln.get('y'), ln.get('w'), ln.get('h'))))
        if a.max_books and len(lines_by_book) >= a.max_books:
            break
    by_cls = Counter(f.cls for f in findings)
    by_rule = Counter(f.rule_id for f in findings)
    payload = dict(
        denominator=dict(books=len(books), pages=n_pages, ocr_lines=n_lines),
        by_class=dict(by_cls), by_rule=dict(by_rule),
        books_touched={c: len({f.book for f in findings if f.cls == c}) for c in by_cls},
        examples={c: [dict(book=f.book, page=f.page, matched=f.matched, text=f.text[:160],
                           note=f.note)
                      for f in findings if f.cls == c][:12] for c in by_cls},
        findings=[dict(cls=f.cls, rule=f.rule_id, book=f.book, page=f.page, matched=f.matched,
                       text=f.text[:200], note=f.note, bbox=f.bbox) for f in findings],
    )
    if a.diacritics:
        uni = CE.diacritic_candidates(CE.diacritic_index(lines_by_book))
        big = CE.diacritic_bigram_candidates(CE.diacritic_bigram_index(lines_by_book))

        def roll(cands):
            return dict(
                books_with_candidates=len(cands),
                total_bare_occurrences=sum(n for rows in cands.values() for _, n, _, _ in rows),
                distinct_forms=sum(len(rows) for rows in cands.values()),
                top={b: rows[:8] for b, rows in sorted(cands.items(), key=lambda kv: -sum(
                    r[1] for r in kv[1]))[:10]})
        # The unigram roll-up is kept as the FALSIFIED baseline, not as a count: see
        # `census.diacritic_candidates`. Reporting only the survivor would hide the measurement
        # that killed the first rule, and that measurement is the finding.
        payload['diacritic'] = dict(unigram_falsified=roll(uni), bigram=roll(big))
    os.makedirs(OUT, exist_ok=True)
    path = f'{OUT}/line-census{a.suffix}.json'
    with open(path, 'w') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps(payload['denominator'], indent=1))
    print(json.dumps(payload['by_class'], indent=1))
    print('->', path)


# ---------------------------------------------------------------- REGION census
def cmd_regions(a):
    from mathfix import detect as D
    from mathfix.inkmask import InkMask
    from mathfix.tokens import load_tokens
    pairs = [(a.book, p) for p in (parse_pages(a.pages) or book_pages(a.book))]
    cen = CE.RegionCensus()
    rows = []
    for book, page in pairs:
        try:
            mask = InkMask.from_pdf(V.pdf_path(book), page, dpi=a.dpi)
            tokens = load_tokens(book, page)
        except Exception as exc:
            rows.append(dict(book=book, page=page, error=str(exc)))
            continue
        regions = D.find_fraction_regions(mask, tokens)
        for i, r in enumerate(regions):
            key = f'{book}:p{page:03d}:r{i:03d}'
            cls, note = CE.classify_region(r, tokens, mask.height)
            if cls is None:
                cen.add('READ_BY_BASELINE', key)
                continue
            cen.add(cls, key, note)
        rows.append(dict(book=book, page=page, regions=len(regions)))
    payload = dict(pages=len(pairs), regions=cen.total, by_class=dict(cen.by_class),
                   examples={k: v for k, v in cen.examples.items()}, pages_rows=rows)
    os.makedirs(OUT, exist_ok=True)
    path = f'{OUT}/region-census{a.suffix}.json'
    with open(path, 'w') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps(payload['by_class'], indent=1))
    print('->', path)


# ---------------------------------------------------------------- the experiment
def cmd_recrop(a):
    pages = parse_pages(a.pages) or book_pages(a.book)
    all_rows = []
    for page in pages:
        try:
            rows = RC.page_rows(a.book, page, dpi=a.dpi)
        except Exception as exc:
            print(f'p{page}: {exc}')
            continue
        all_rows.extend(rows)
        print(f"p{page:3d} regions={len(rows)} "
              f"recovered={sum(1 for r in rows if r.population == RC.RECOVERY and r.recrop_value)} "
              f"control_same={sum(1 for r in rows if r.agreement == 'same')} "
              f"control_differs={sum(1 for r in rows if r.agreement == 'differs')}")
    path = RC.write(all_rows, f'{OUT}/recrop-{a.book}{a.suffix}.json')
    print('->', path)


def cmd_sample(a):
    """A seeded page sample drawn AFTER the rules were frozen — the holdout."""
    books = sorted(b for b in os.listdir(OCR_BODY)
                   if glob.fnmatch.fnmatch(b, a.books_glob) and has_pdf(b))
    pairs = [(b, p) for b in books for p in book_pages(b)]
    random.Random(a.seed).shuffle(pairs)
    out = sorted(pairs[:a.sample])
    path = f'{OUT}/sample{a.suffix}.json'
    os.makedirs(OUT, exist_ok=True)
    with open(path, 'w') as fh:
        json.dump(dict(books_glob=a.books_glob, seed=a.seed, n=len(out),
                       pages=[list(x) for x in out]), fh, indent=1)
    for b, p in out:
        print(b, p)
    print('->', path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('lines', 'regions', 'recrop', 'sample'):
        s = sub.add_parser(name)
        s.add_argument('--book')
        s.add_argument('--books-glob', default='*')
        s.add_argument('--pages')
        s.add_argument('--dpi', type=int, default=300)
        s.add_argument('--sample', type=int, default=20)
        s.add_argument('--seed', type=int, default=20260906)
        s.add_argument('--suffix', default='')
        s.add_argument('--max-books', type=int, default=0)
        s.add_argument('--diacritics', action='store_true')
    a = ap.parse_args(argv)
    return dict(lines=cmd_lines, regions=cmd_regions, recrop=cmd_recrop, sample=cmd_sample)[a.cmd](a)


if __name__ == '__main__':
    main()
