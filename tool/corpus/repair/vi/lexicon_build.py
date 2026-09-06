#!/usr/bin/env python3
"""Round 5 · build the bounded Vietnamese lexicon used by third-signal layer A.

**Provenance and licence, stated up front (Founder §3: «if you vendor data, record licence and
provenance»).** Nothing is vendored. Two tables are *derived*, both from data this project already owns:

| table | source | licence | what it is |
|---|---|---|---|
| `corpus` | `poc-out/graph/ocr-body` - this project's own Apple Vision OCR of the 531-book K-12 PDF set (62,729 pages) | internal research data, never distributed; the tables hold **counts of word forms**, no sentences and no page text | per-token and per-bigram **page** and **book** support |
| `clean` | the human-typed Vietnamese in this repository: `docs/**/*.md`, `lib/**/*.dart`, `test/**/*.dart`, `assets/**/*.json` | our own authored files | the same shape, from text no OCR ever touched |

The `corpus` table is OCR-derived, so it contains OCR errors — that is the obvious objection and it is
answered by *support*, not by faith: a real Vietnamese word appears on thousands of pages in hundreds of
books; a display-font OCR slip appears on a handful of pages of one book. Every consumer therefore asks
for **page support and book support**, never for a raw count, and layer A always subtracts the support
contributed by the book under repair (`VietnameseLexicon.support(..., exclude_book=...)`) so the signal is
external to the document it judges. The `clean` table is the independent cross-check on the shape of the
`corpus` one, and is reported next to it.

Usage:
  python3 tool/corpus/repair/vi/lexicon_build.py --out poc-out/round5/lexicon
  python3 tool/corpus/repair/vi/lexicon_build.py --out poc-out/round5/lexicon --limit-books 20   # smoke run
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OCR_BODY = f'{ROOT}/poc-out/graph/ocr-body'

#: a Vietnamese word token: letters only (a digit run is data, not a word - layer C owns those).
TOKEN = re.compile(r'[A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+')

MIN_PAGES_UNIGRAM = 2      # a form seen on a single page of the whole 62,729-page corpus is not evidence
MIN_PAGES_BIGRAM = 2

LEXICON_VERSION = 'vi-lex-v1'


def nfc(s):
    return unicodedata.normalize('NFC', s or '')


def tokens(text):
    return [t.lower() for t in TOKEN.findall(nfc(text))]


# ---------------------------------------------------------------- corpus pass
def iter_pages(limit_books=None, books=None):
    """(book, page_no, text) for every OCR'd page. Text is the page's OCR lines joined - it never leaves
    this process; only counts are written out."""
    dirs = sorted(d for d in glob.glob(f'{OCR_BODY}/*') if os.path.isdir(d))
    if books:
        want = set(books)
        dirs = [d for d in dirs if os.path.basename(d) in want]
    if limit_books:
        dirs = dirs[:limit_books]
    for d in dirs:
        book = os.path.basename(d)
        for f in sorted(glob.glob(f'{d}/p*.json')):
            try:
                rec = json.load(open(f, encoding='utf-8'))
            except Exception:
                continue
            lines = rec.get('lines') or []
            yield book, rec.get('pdf_page'), ' '.join(l.get('text', '') for l in lines)


def build_corpus(limit_books=None, progress=None):
    uni_pages = Counter(); uni_books = defaultdict(set)
    bi_pages = Counter()
    n_pages = n_books = 0
    seen_books = set()
    for book, page, text in iter_pages(limit_books=limit_books):
        n_pages += 1
        if book not in seen_books:
            seen_books.add(book); n_books += 1
            if progress and n_books % 25 == 0:
                progress(n_books, n_pages)
        toks = tokens(text)
        for t in set(toks):
            uni_pages[t] += 1
            uni_books[t].add(book)
        for a, b in set(zip(toks, toks[1:])):
            bi_pages[(a, b)] += 1
    uni = {t: [c, len(uni_books[t])] for t, c in uni_pages.items() if c >= MIN_PAGES_UNIGRAM}
    bi = {f'{a}\t{b}': c for (a, b), c in bi_pages.items() if c >= MIN_PAGES_BIGRAM}
    return dict(version=LEXICON_VERSION, source='poc-out/graph/ocr-body (apple-vision-accurate-vi)',
                licence='internal research data; counts only, never distributed',
                pages=n_pages, books=n_books,
                min_pages_unigram=MIN_PAGES_UNIGRAM, min_pages_bigram=MIN_PAGES_BIGRAM,
                unigram=uni, bigram=bi)


# ---------------------------------------------------------------- clean pass
CLEAN_GLOBS = ('docs/**/*.md', 'lib/**/*.dart', 'test/**/*.dart', 'tool/**/*.py', 'assets/**/*.json')
VI_ONLY = re.compile(r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]')


def build_clean(root=ROOT):
    """The same shape from text no OCR ever touched: this repository's own Vietnamese. Small (it is a
    codebase, not a library), and used as a cross-check on the corpus table, never as its replacement."""
    uni_pages = Counter(); uni_files = defaultdict(set); bi_pages = Counter(); n_files = 0
    for pat in CLEAN_GLOBS:
        for f in glob.glob(os.path.join(root, pat), recursive=True):
            if '/poc-out/' in f or '/.git/' in f or '/build/' in f:
                continue
            try:
                text = open(f, encoding='utf-8', errors='ignore').read()
            except Exception:
                continue
            if not VI_ONLY.search(text.lower()):
                continue
            n_files += 1
            toks = [t for t in tokens(text)]
            for t in set(toks):
                uni_pages[t] += 1; uni_files[t].add(f)
            for a, b in set(zip(toks, toks[1:])):
                bi_pages[(a, b)] += 1
    return dict(version=LEXICON_VERSION, source='this repository (docs, lib, test, tool, assets)',
                licence='our own authored files', pages=n_files, books=1,
                min_pages_unigram=1, min_pages_bigram=1,
                unigram={t: [c, len(uni_files[t])] for t, c in uni_pages.items()},
                bigram={f'{a}\t{b}': c for (a, b), c in bi_pages.items()})


def book_counts(book):
    """Per-book unigram/bigram page support, computed on demand (a book is ~150 pages) so layer A can
    subtract the document under repair from the global support without storing a per-book table."""
    uni = Counter(); bi = Counter()
    for _, _, text in iter_pages(books=[book]):
        toks = tokens(text)
        for t in set(toks):
            uni[t] += 1
        for a, b in set(zip(toks, toks[1:])):
            bi[(a, b)] += 1
    return uni, bi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, help='directory to write corpus.json / clean.json into')
    ap.add_argument('--limit-books', type=int, default=None)
    ap.add_argument('--clean-only', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    clean = build_clean()
    json.dump(clean, open(f'{a.out}/clean.json', 'w'), ensure_ascii=False)
    print(f'clean: files={clean["pages"]} unigrams={len(clean["unigram"])} bigrams={len(clean["bigram"])}')
    if a.clean_only:
        return
    corpus = build_corpus(limit_books=a.limit_books,
                          progress=lambda b, p: print(f'  … {b} books / {p} pages', flush=True))
    json.dump(corpus, open(f'{a.out}/corpus.json', 'w'), ensure_ascii=False)
    print(f'corpus: books={corpus["books"]} pages={corpus["pages"]} '
          f'unigrams={len(corpus["unigram"])} bigrams={len(corpus["bigram"])}')


if __name__ == '__main__':
    sys.exit(main())
