#!/usr/bin/env python3
"""Lane E1 — resolve the (gitignored) corpus roots.

Corpus data lives ONLY under the main checkout's gitignored `poc-out/`. Nothing here
reads or writes anything inside the repo tree, and nothing here copies corpus text
into the repo. Override with WAL_POC_OUT for a different checkout / a test fixture.
"""
import os

DEFAULT_POC_OUT = '/Users/alexnguyen/projects/workizen-ai-learning-coach/poc-out'


def poc_out() -> str:
    return os.environ.get('WAL_POC_OUT', DEFAULT_POC_OUT)


def p(*parts) -> str:
    return os.path.join(poc_out(), *parts)


# --- the four corpus layers this lane censuses -------------------------------
# tier A source: Trusted Structured Lesson (238 Science lessons, tc2-p1)
def tsl_dir() -> str:
    return p('trusted-corpus', 'tc-v2', 'tc2-p1', 'lessons')


# tier B source: role-tagged line units for the whole K-12 corpus
def units_k12_dir() -> str:
    return p('units-k12')


# the canonical lesson census (3,679 rows) — the product denominator
def all_lessons_csv() -> str:
    return p('k12-census-exports', 'all-lessons.csv')


# raw per-page OCR lines (untrusted), 531 books
def ocr_body_dir() -> str:
    return p('graph', 'ocr-body')


def out_dir(*parts) -> str:
    d = p('round5', 'semantic', *parts)
    os.makedirs(d, exist_ok=True)
    return d


def out_file(name: str) -> str:
    return os.path.join(out_dir(), name)
