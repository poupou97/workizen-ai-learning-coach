#!/usr/bin/env python3
"""Round 4 · Lane D (LEGACY REPROCESS) — shared paths + helpers.

Ownership: Lane D owns tool/corpus/legacy/** only. The pipeline (tool/corpus/tc2_*.py,
tsl_to_lesson_document.py, ft_audit_*.py) belongs to Lane A-pipeline and is CALLED, never edited.

Corpus data lives only in the main checkout's gitignored poc-out/ (absolute paths). Lane D writes
ONLY under poc-out/round4/legacy/ — versioned batches, never overwriting or deleting older outputs.
Verbatim SGK text stays in poc-out/ (Founder D4); documents in the repo quote ids and short titles.
"""
import hashlib
import json
import os
import re
import unicodedata

MAIN_ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
LEGACY_OUT = os.environ.get('LEGACY_OUT', f'{MAIN_ROOT}/poc-out/round4/legacy')
OCR = f'{MAIN_ROOT}/poc-out/graph/ocr-body'
PDF = f'{MAIN_ROOT}/poc-out/pdf'
UNITS = f'{MAIN_ROOT}/poc-out/units'
CURRICULUM = f'{MAIN_ROOT}/poc-out/graph/curriculum-structure.json'
BASELINE_113 = f'{MAIN_ROOT}/poc-out/p0-experiment/baseline-learnable.json'
SAM_UNITS_DB = f'{REPO_ROOT}/assets/pack/sam-units.db'
PACK_DIR = f'{REPO_ROOT}/assets/pack'
LAYOUT_CENSUS = f'{MAIN_ROOT}/poc-out/k12-census-exports/layout-census-pages.json'
FEATURE_CENSUS = f'{MAIN_ROOT}/poc-out/trusted-corpus/tc-v1/census/pages.jsonl'
CASE_MAP = f'{MAIN_ROOT}/poc-out/units/exercise-case-map.json'
ROUND3_ANNOTATED = f'{MAIN_ROOT}/poc-out/round3/ft-audit/annotated-20260905.jsonl'
BAKEOFF_PYTHON = f'{MAIN_ROOT}/.venv-bakeoff/bin/python'

DENOMINATORS = {
    'canonical': dict(value=3679, definition='SGK lessons with a lesson number in curriculum-structure.json (Grade 1–12, 301 SGK documents)', census='schema 1, reconciled 2026-09-04; re-derived 2026-09-05 (pre-autonomy audit a_layers.py)'),
    'ranged': dict(value=3381, definition='canonical lessons that also have a TOC pageStart', census='same census'),
    'baseline_learnable': dict(value=113, definition='lessons with ≥ 1 non-router activity in the default packs (poc-out/p0-experiment/baseline-learnable.json, 2026-09-04); 111 after the WAL-210 G2/G3 gates', census='PR-1 regeneration report 2026-09-05'),
}

# the five failure classes the Founder asked for, plus display fidelity (reported separately, never summed)
FAILURE_CLASSES = ('display', 'teaching_critical', 'reading_order', 'role', 'attachment', 'formula_number_unit', 'figure_caption')


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_json(obj):
    """Hash of the canonical JSON serialisation (sorted keys, no whitespace)."""
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def sha256_text(text):
    return hashlib.sha256((text or '').encode('utf-8')).hexdigest()


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def dump_json(obj, path, indent=1):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
        f.write('\n')
    os.replace(tmp, path)


def write_new_version(obj, path):
    """Versioned write: never overwrite an existing file — if `path` exists, write `path.vN` instead.
    Returns the path actually written."""
    if not os.path.exists(path):
        dump_json(obj, path)
        return path
    n = 2
    base, ext = os.path.splitext(path)
    while os.path.exists(f'{base}.v{n}{ext}'):
        n += 1
    p = f'{base}.v{n}{ext}'
    dump_json(obj, p)
    return p


def norm(t):
    t = unicodedata.normalize('NFC', (t or '')).lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', t)).strip()


def wilson(k, n, z=1.96):
    if not n:
        return None, None, None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return round(p, 4), round(max(0.0, (c - r) / d), 4), round(min(1.0, (c + r) / d), 4)


def fmt_rate(k, n):
    if not n:
        return '— (n = 0)'
    p, lo, hi = wilson(k, n)
    return f'{k} / {n} = {p:.3f} [{lo:.3f}, {hi:.3f}]'


def pdf_path(book):
    for p in (f'{PDF}/{book[:2]}/{book}.pdf', f'{PDF}/{book}.pdf'):
        if os.path.exists(p):
            return p
    return None


def book_label(book):
    """Human label from the book id (04-sgk-toan-4-tap-hai → Toán 4 tập hai)."""
    m = re.match(r'(\d{2})-(sgk|sgv)-(.+?)(?:-(tap-mot|tap-hai|tap-1))?$', book)
    if not m:
        return book
    subj = m.group(3)
    names = {'toan': 'Toán', 'tieng-viet': 'Tiếng Việt', 'khoa-hoc-tu-nhien': 'KHTN', 'khoa-hoc': 'Khoa học', 'lich-su-va-dia-li': 'LS&ĐL', 'hoa-hoc': 'Hoá học', 'vat-li': 'Vật lí'}
    label = subj
    for k, v in names.items():
        if subj.startswith(k):
            label = v + subj[len(k):].replace('-', ' ')
            break
    vol = {'tap-mot': ' tập một', 'tap-hai': ' tập hai', 'tap-1': ' tập một'}.get(m.group(4) or '', '')
    return f'{label}{vol}'


def subject_of(book):
    if '-toan-' in book:
        return 'Toán'
    if '-tieng-viet-' in book:
        return 'Tiếng Việt'
    if '-khoa-hoc-tu-nhien-' in book:
        return 'KHTN'
    if '-khoa-hoc-' in book:
        return 'Khoa học'
    if '-lich-su-va-dia-li-' in book:
        return 'LS&ĐL'
    if '-hoa-hoc-' in book:
        return 'Hoá học'
    if '-vat-li-' in book:
        return 'Vật lí'
    return 'other'
