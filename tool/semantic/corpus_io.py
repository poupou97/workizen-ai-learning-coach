#!/usr/bin/env python3
"""Lane E1 — read-only loaders for the corpus layers, with the denominator attached.

Every loader returns records that carry `book`, `lesson`, and a *source id* so that
any semantic claim built later can point back at the block it came from. Nothing in
this module infers anything.
"""
import csv
import glob
import json
import os
import re

import corpus_paths as cp

# ---------------------------------------------------------------------------
# canonical lesson census — the 3,679 product denominator
# ---------------------------------------------------------------------------


def load_canonical_lessons(path=None):
    """[{book, grade, subject, lesson, title, gate, ...}] — one row per canonical lesson."""
    path = path or cp.all_lessons_csv()
    out = []
    with open(path, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            try:
                lesson = int(r['lessonNo'])
            except (TypeError, ValueError):
                continue
            out.append({
                'book': r['sourceDocumentId'],
                'grade': int(r['grade']),
                'subject': r['subject'],
                'lesson': lesson,
                'title': r.get('title', ''),
                'structured': r.get('structured') == 'True',
                'semanticMappable': r.get('semanticMappable') == 'True',
                'gate': r.get('gate', ''),
            })
    return out


def lesson_key(book, lesson):
    return '%s#%s' % (book, lesson)


# ---------------------------------------------------------------------------
# tier A — Trusted Structured Lesson
# ---------------------------------------------------------------------------


def tsl_files(root=None):
    root = root or cp.tsl_dir()
    return sorted(glob.glob(os.path.join(root, '*', '*.tsl.json')))


def load_tsl(path):
    """One TSL lesson, normalised to {book, lesson, title, blocks[], figures[], withheld[]}.

    A TSL block is FLAT: {id, page, page_printed, order, role{value,coarse,...}, text,
    bbox, heading_path[], refers_figure, enumerator_restored, provenance{}}.
    There is no nesting, no table grid, no stem→option link. That is a measured fact
    about the source layer, not an omission here — see STRUCTURE-GAPS.
    """
    with open(path, encoding='utf-8') as fh:
        d = json.load(fh)
    blocks = []
    for b in d.get('blocks', []):
        role = b.get('role') or {}
        blocks.append({
            'id': b.get('id'),
            'page': b.get('page'),
            'page_printed': b.get('page_printed'),
            'order': b.get('order'),
            'role': role.get('value'),
            'coarse': role.get('coarse'),
            'role_conf': role.get('confidence'),
            'text': b.get('text') or '',
            'heading_path': b.get('heading_path') or [],
            'refers_figure': bool(b.get('refers_figure')),
            'bbox': b.get('bbox'),
        })
    return {
        'book': d.get('book'),
        'lesson': d.get('lesson'),
        'title': d.get('title') or '',
        'sourceability': d.get('sourceability'),
        'blocks': blocks,
        'figures': d.get('figures', []),
        'withheld': d.get('withheld', []),
        'stats': d.get('stats', {}),
        'path': path,
    }


def iter_tsl(root=None):
    for path in tsl_files(root):
        yield load_tsl(path)


# ---------------------------------------------------------------------------
# tier B — role-tagged line units for the whole corpus
# ---------------------------------------------------------------------------

_BOOK_RE = re.compile(r'^(\d{2})-(sgk|sgv)-(.+)$')


def book_grade(book):
    m = _BOOK_RE.match(book or '')
    return int(m.group(1)) if m else None


def book_is_sgv(book):
    m = _BOOK_RE.match(book or '')
    return bool(m and m.group(2) == 'sgv')


def units_files(root=None):
    root = root or cp.units_k12_dir()
    return sorted(glob.glob(os.path.join(root, '*.json')))


def load_units(path):
    with open(path, encoding='utf-8') as fh:
        d = json.load(fh)
    book = d.get('sourceDocumentId')
    out = []
    for u in d.get('units', []):
        if u.get('lesson') is None:
            continue
        out.append({
            'book': book,
            'lesson': u['lesson'],
            'id': u.get('id'),
            'role': u.get('role'),
            'text': u.get('text') or '',
            'page': u.get('pagePdf'),
        })
    return book, d.get('subject'), out


def iter_units_lessons(root=None, sgk_only=True):
    """Yield (book, subject, lesson, [unit,...]) grouped per lesson, in file order."""
    for path in units_files(root):
        book, subject, units = load_units(path)
        if sgk_only and book_is_sgv(book):
            continue
        by = {}
        for u in units:
            by.setdefault(u['lesson'], []).append(u)
        for lesson in sorted(by):
            yield book, subject, lesson, by[lesson]


# ---------------------------------------------------------------------------
# normalisation shared by the discovery and detection steps
# ---------------------------------------------------------------------------

_WS = re.compile(r'\s+')
_PUNCT = re.compile(r'[^0-9a-zA-ZÀ-ỹ%°/+\-=<>()\.,;:?]+')


def norm(text):
    t = (text or '').lower()
    t = _PUNCT.sub(' ', t)
    return _WS.sub(' ', t).strip()


def words(text):
    return [w for w in norm(text).split(' ') if w]
