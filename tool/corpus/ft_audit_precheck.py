#!/usr/bin/env python3
"""Round 3 · A2 — DETERMINISTIC PRE-CHECKS for the false-trust audit sample (protocol
docs/research/FALSE-TRUST-AUDIT-PROTOCOL.md §3). Adds machine-computed hints to every row so the
annotator judges from the page render with the arithmetic already done; it NEVER fills an annotation
field — every OK/WRONG is still a human/annotator decision from the crop.

Per row it adds (all under `precheck`, plus three top-level context fields):
  layoutFamily      page layout family from the K-12 census (single | two_col | sparse | null)
  subject           subject of the book (curriculum-structure.json)
  activityFamily    = family (pack activity family / samUnits / tslBai17)
  precheck.ocrSim   difflib ratio between the served text and the matched OCR lines (normalised)
  precheck.ocrExact normalised served text == normalised matched OCR text
  precheck.toneOnly served and OCR text equal once diacritics are stripped but not before (tone slip)
  precheck.enumeratorServed / enumeratorOcr / enumeratorDropped   «1.» «a)» «•» at the start
  precheck.hasNumbers / hasMath   digits present; operators, fractions, units, formulas present
  precheck.pageInLessonRange      printed page ∈ [pageStart(lesson), pageStart(next lesson)) per the
                                  curriculum structure (None when the lesson or page is unknown)
  precheck.lessonRange            the [start, end) printed range used
  precheck.sdmStatus / sdmReasons TC-v2 SDM verdict for the same text where a page overlaps
  precheck.multiLine              matched OCR lines > 1 (reading-order judgement applies)

Usage:
  python3 tool/corpus/ft_audit_precheck.py poc-out/b-lane/ft-audit/sample-20260905.jsonl \
      --out poc-out/round3/ft-audit/precheck-20260905.jsonl
"""
import argparse
import collections
import difflib
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('TC_ROOT', os.path.abspath(os.path.join(HERE, '..', '..')))
sys.path.insert(0, HERE)
from ft_audit_sample import norm, ocr_lines  # noqa: E402

ENUM_RE = re.compile(r'^\s*(\d{1,2}[.)]|[a-zđ][.)]|[·•\-–]|HĐ\s*\d|\(\d\))\s*', re.I)
MATH_RE = re.compile(r'[=<>×÷+±/^²³%]|\d\s*/\s*\d|\b(?:cm|m|kg|g|km|ml|l|°C|mm)\b|\d+[.,]\d+')


def strip_diacritics(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.replace('đ', 'd').replace('Đ', 'D')


def ocr_text_for(row):
    src = row.get('source') or {}
    idx = src.get('lineIndices') or []
    if not idx or not row.get('pagePdf'):
        return None
    lines = ocr_lines(row['book'], row['pagePdf'])
    if not lines:
        return None
    return ' '.join(lines[i].get('text', '') for i in idx if i < len(lines))


def load_layout_census():
    p = f'{ROOT}/poc-out/k12-census-exports/layout-census-pages.json'
    return json.load(open(p)) if os.path.exists(p) else {}


def load_curriculum():
    p = f'{ROOT}/poc-out/graph/curriculum-structure.json'
    if not os.path.exists(p):
        return {}, {}
    subj, ranges = {}, {}
    for d in json.load(open(p))['documents']:
        subj[d['sourceDocumentId']] = d.get('subject')
        ls = sorted([l for l in d.get('lessons') or [] if l.get('pageStart') is not None], key=lambda l: l['pageStart'])
        r = {}
        for i, l in enumerate(ls):
            no = l.get('lessonNo') if l.get('lessonNo') is not None else l.get('number')
            end = ls[i + 1]['pageStart'] if i + 1 < len(ls) else l['pageStart'] + 12
            r[no] = (l['pageStart'], end)
        ranges[d['sourceDocumentId']] = r
    return subj, ranges


def precheck_row(row, layout, subj, ranges):
    book, pdf, printed = row.get('book'), row.get('pagePdf'), row.get('pagePrinted')
    row['layoutFamily'] = (layout.get(book) or {}).get(str(pdf)) if pdf else None
    row['subject'] = subj.get(book)
    row['activityFamily'] = row.get('family')
    served = row.get('text') or ''
    pc = {}
    ocr = ocr_text_for(row)
    if ocr is not None and served:
        a, b = norm(served), norm(ocr)
        pc['ocrSim'] = round(difflib.SequenceMatcher(None, a, b).ratio(), 3)
        pc['ocrExact'] = a == b
        pc['toneOnly'] = (a != b) and (strip_diacritics(a) == strip_diacritics(b))
        m_ocr = ENUM_RE.match(ocr)
        pc['enumeratorOcr'] = m_ocr.group(1) if m_ocr else None
    else:
        pc['ocrSim'] = None; pc['ocrExact'] = None; pc['toneOnly'] = None; pc['enumeratorOcr'] = None
    m_s = ENUM_RE.match(served)
    pc['enumeratorServed'] = m_s.group(1) if m_s else None
    pc['enumeratorDropped'] = bool(pc['enumeratorOcr']) and not pc['enumeratorServed']
    pc['hasNumbers'] = bool(re.search(r'\d', served))
    pc['hasMath'] = bool(MATH_RE.search(served))
    pc['multiLine'] = len((row.get('source') or {}).get('lineIndices') or []) > 1
    lesson = row.get('lesson')
    rng = (ranges.get(book) or {}).get(lesson) if lesson is not None else None
    if row.get('family') == 'tslBai17':
        rng = (60, 64)   # TSL boundary (pdf 61–65 → printed 60–64), header-attached
    pc['lessonRange'] = list(rng) if rng else None
    pc['pageInLessonRange'] = (rng[0] <= printed < rng[1]) if (rng and printed is not None) else None
    sdm = (row.get('source') or {}).get('sdm') or {}
    pc['sdmStatus'] = sdm.get('trust') if sdm.get('matched') else None
    pc['sdmReasons'] = sdm.get('reasons') if sdm.get('matched') else None
    pc['sdmRole'] = sdm.get('role') if sdm.get('matched') else None
    row['precheck'] = pc
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jsonl')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.jsonl, encoding='utf-8') if l.strip()]
    layout = load_layout_census(); subj, ranges = load_curriculum()
    for r in rows:
        precheck_row(r, layout, subj, ranges)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    c = collections.Counter()
    for r in rows:
        pc = r['precheck']
        c['rows'] += 1
        c['ocrExact'] += 1 if pc['ocrExact'] else 0
        c['toneOnly'] += 1 if pc['toneOnly'] else 0
        c['enumeratorDropped'] += 1 if pc['enumeratorDropped'] else 0
        c['ocrSim<0.9'] += 1 if (pc['ocrSim'] is not None and pc['ocrSim'] < 0.9) else 0
        c['pageOutOfRange'] += 1 if pc['pageInLessonRange'] is False else 0
        c['pageRangeUnknown'] += 1 if pc['pageInLessonRange'] is None else 0
        c['hasMath'] += 1 if pc['hasMath'] else 0
        c['sdmWithheld'] += 1 if pc['sdmStatus'] and pc['sdmStatus'] != 'TRUSTED' else 0
        c['layout:' + str(r['layoutFamily'])] += 1
    print(json.dumps(c, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
