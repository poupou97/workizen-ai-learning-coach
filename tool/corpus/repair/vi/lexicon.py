#!/usr/bin/env python3
"""Round 5 · reading the bounded Vietnamese lexicon (layer A's evidence store).

The API answers only in terms of **support** - on how many distinct pages, in how many distinct books, a
word form or a two-word sequence is attested - because that is the only reading of an OCR-derived table
that is honest. A raw count would let one page of one badly-set display font vote as loudly as a hundred
ordinary pages.

`exclude_book` subtracts the book under repair, so layer A never confirms a word using the very document it
is judging. In-document evidence is layer D's job and is reported separately, which is what makes
«two independent layers agree» mean something.

Build the tables with `repair/vi/lexicon_build.py`; provenance and licence are recorded in that module and
carried in the JSON.
"""
from __future__ import annotations

import functools
import json
import os
import unicodedata

DEFAULT_DIR = os.environ.get('VI_LEXICON_DIR',
                             os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
                             + '/poc-out/round5/lexicon')


def nfc(s):
    return unicodedata.normalize('NFC', s or '')


class Support:
    """(pages, books) support of one form, with the book under repair already subtracted."""

    __slots__ = ('pages', 'books', 'in_book')

    def __init__(self, pages=0, books=0, in_book=0):
        self.pages = int(pages); self.books = int(books); self.in_book = int(in_book)

    def __repr__(self):
        return f'Support(pages={self.pages}, books={self.books}, in_book={self.in_book})'

    def __bool__(self):
        return self.pages > 0

    def to_json(self):
        return dict(pages=self.pages, books=self.books, in_book=self.in_book)


class VietnameseLexicon:
    def __init__(self, table, clean=None, book_counts=None):
        self.table = table
        self.clean = clean or dict(unigram={}, bigram={})
        self._book_counts = book_counts or {}          # book -> (unigram Counter, bigram Counter)
        self.meta = {k: v for k, v in table.items() if k not in ('unigram', 'bigram')}

    # ------------------------------------------------------------------ loading
    @classmethod
    def load(cls, directory=None):
        d = directory or DEFAULT_DIR
        table = json.load(open(f'{d}/corpus.json', encoding='utf-8'))
        clean = None
        if os.path.exists(f'{d}/clean.json'):
            clean = json.load(open(f'{d}/clean.json', encoding='utf-8'))
        return cls(table, clean)

    def register_book_counts(self, book, unigram, bigram):
        """Give the lexicon the per-book counts so `exclude_book` is exact rather than approximated."""
        self._book_counts[book] = (unigram, bigram)

    def ensure_book(self, book):
        if book not in self._book_counts:
            from . import lexicon_build
            self._book_counts[book] = lexicon_build.book_counts(book)
        return self._book_counts[book]

    # ------------------------------------------------------------------ support
    def unigram(self, token, exclude_book=None):
        t = nfc(token).lower()
        pages, books = self.table['unigram'].get(t, (0, 0))
        in_book = 0
        if exclude_book:
            uni, _ = self.ensure_book(exclude_book)
            in_book = uni.get(t, 0)
        return Support(max(0, pages - in_book), max(0, books - (1 if in_book else 0)), in_book)

    def bigram(self, a, b, exclude_book=None):
        key = f'{nfc(a).lower()}\t{nfc(b).lower()}'
        pages = self.table['bigram'].get(key, 0)
        in_book = 0
        if exclude_book:
            _, bi = self.ensure_book(exclude_book)
            in_book = bi.get((nfc(a).lower(), nfc(b).lower()), 0)
        return Support(max(0, pages - in_book), 0, in_book)

    def clean_unigram(self, token):
        pages, files = self.clean.get('unigram', {}).get(nfc(token).lower(), (0, 0))
        return Support(pages, files)

    def clean_bigram(self, a, b):
        return Support(self.clean.get('bigram', {}).get(f'{nfc(a).lower()}\t{nfc(b).lower()}', 0), 0)

    def attested(self, token, min_pages=2, min_books=2, exclude_book=None):
        s = self.unigram(token, exclude_book=exclude_book)
        return s.pages >= min_pages and s.books >= min_books

    def context_support(self, left, token, right, exclude_book=None):
        """Bigram page-support of the token in its actual neighbourhood: left·token + token·right.
        `None` neighbours are skipped (a block edge is not evidence against a reading)."""
        total = 0
        parts = {}
        if left:
            s = self.bigram(left, token, exclude_book=exclude_book)
            parts['left'] = s.pages; total += s.pages
        if right:
            s = self.bigram(token, right, exclude_book=exclude_book)
            parts['right'] = s.pages; total += s.pages
        return total, parts


@functools.lru_cache(maxsize=2)
def load(directory=None):
    return VietnameseLexicon.load(directory)
