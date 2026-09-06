#!/usr/bin/env python3
"""The other two named defects — a Roman section number and the ohm sign — re-read on the crop.

    `II – Định luật khúc xạ ánh sáng`  served as  `I1 - Định luật khúc xạ ánh sáng`
    `1 MΩ = 1 000 000 Ω`               served as  `1 MS = 1 000 000 S2`

Round 5 attributed both to recognition and said why nothing downstream can reach them: *«Both OCR
stacks agree on the wrong character, so agreement proves nothing»*. A second stack is not the
answer; a second LOOK at the same printed glyph is.

Each class gets a recogniser and an independent validator that did not produce the candidate:

  ROMAN  the crop is re-read at several scales, and a candidate is accepted only when the numeral
         it proposes FITS THE SEQUENCE the same book prints elsewhere. `II` after a correctly-read
         `I` in the same lesson is evidence; `II` on its own is a reading. This is the signal round
         5 named and nothing consulted — «the corpus carries its own evidence».
  OHM    the crop must return the ohm sign itself, at two scales, inside a unit context the page
         pass already established. Nothing infers Ω from `S2`: a substitution table would produce
         the right answer for the wrong reason and would be a guess with a nice pedigree.

Neither produces a repair. Both produce a reading, and a reading is a recognition result.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathfix.tokens import load_tokens                  # noqa: E402
from recognition import census as CE                    # noqa: E402
from recognition import vision as V                     # noqa: E402

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OUT = f'{ROOT}/poc-out/round6/recognition'

SCALES = (6.0, 10.0, 16.0, 24.0)
ROMAN_OK = re.compile(r'^(I{1,3}|IV|V|VI{0,3}|IX|X)$')
ROMAN_VALUE = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8,
               'IX': 9, 'X': 10}
#: a section heading the page pass read CORRECTLY — the sequence evidence the validator uses.
ROMAN_CLEAN = re.compile(r'^\s*(I{1,3}|IV|V|VI{0,3}|IX|X)\s*[-–—.)]\s+\S')
OHM_OK = re.compile(r'[Ωω]')


def _crop(token, start, end, pad_chars=1.5, pad_v=0.45):
    n = max(1, len(token.text))
    x0 = token.x + token.w * max(0.0, start - pad_chars) / n
    x1 = token.x + token.w * min(float(n), end + pad_chars) / n
    return (max(0.0, x0), max(0.0, token.y - pad_v * token.h),
            min(1.0, x1), min(1.0, token.y + (1.0 + pad_v) * token.h))


def read_roman(per_scale_texts, min_agreeing=2):
    votes = {}
    for scale, texts in sorted(per_scale_texts.items()):
        for t in texts:
            # The separator is optional: the books set section numbers both as `II - Title` and as
            # `II CHUẨN BỊ`, and requiring a dash refused every reading of the second form even
            # where the crop had returned a clean `II`. Measured: 102 of 106 UNREAD before, and
            # the crop had in fact read the numeral in a large share of them.
            m = re.match(r'^\s*([IVXilL|1]{1,4})\s*(?:[-–—.)]|\s|$)', t or '')
            if not m:
                continue
            # `l` and `|` are the SAME printed stroke as `I` — a case ambiguity of one glyph, not
            # a different glyph. `1` is deliberately NOT mapped: that substitution is the very
            # confusion under investigation, and assuming it would make the recogniser conclude
            # what it was asked to test.
            cand = (m.group(1).replace('l', 'I').replace('|', 'I').replace('i', 'I')
                    .replace('L', 'I'))
            if ROMAN_OK.match(cand):
                votes[scale] = cand
                break
    if not votes:
        return 'UNREAD', None, ()
    counts = Counter(votes.values())
    if len(counts) > 1:
        return 'CONFLICT', None, tuple(sorted(votes))
    value = next(iter(counts))
    agreeing = tuple(sorted(votes))
    if len(agreeing) < min_agreeing:
        return 'INSUFFICIENT_AGREEMENT', value, agreeing
    return 'RECOVERED', value, agreeing


def sequence_validator(value, book_sequence, page):
    """Does `value` fit the section sequence this book prints, read from the pages before it?

    PASS when the numeral immediately follows the last correctly-read one at or before this page,
    or is `I` and nothing precedes it. FAIL when it cannot. NOT_APPLICABLE when the book gives no
    correctly-read heading to compare with — abstention, and abstention is not a pass.
    """
    before = [v for p, v in book_sequence if p <= page]
    if not before:
        return 'NOT_APPLICABLE', None
    last = before[-1]
    want = ROMAN_VALUE.get(last, 0) + 1
    got = ROMAN_VALUE.get(value)
    if got is None:
        return 'FAIL', last
    return ('PASS' if got in (want, ROMAN_VALUE.get(last)) else 'FAIL'), last


def book_roman_sequence(book, pages=None):
    """Every correctly-read Roman section heading in the book, in page order.

    The WHOLE book, not just the pages that carry a defect: the evidence a broken heading is
    checked against is the heading before it, which is on another page by definition. Restricting
    the scan to the defect pages left the validator NOT_APPLICABLE on 105 of 106 findings — an
    independent signal that never fires is not an independent signal.
    """
    import glob
    if pages is None:
        pages = [int(os.path.basename(x)[1:4])
                 for x in glob.glob(f'{V.ROOT}/poc-out/graph/ocr-body/{book}/p*.json')]
    out = []
    for page in sorted(pages):
        try:
            for t in load_tokens(book, page):
                m = ROMAN_CLEAN.match(t.text or '')
                if m:
                    out.append((page, m.group(1)))
        except FileNotFoundError:
            continue
    return out


def read_ohm(per_scale_texts, min_agreeing=2):
    hits = tuple(sorted(s for s, texts in per_scale_texts.items()
                        if any(OHM_OK.search(t or '') for t in texts)))
    if not hits:
        return 'UNREAD', None, ()
    if len(hits) < min_agreeing:
        return 'INSUFFICIENT_AGREEMENT', 'Ω', hits
    return 'RECOVERED', 'Ω', hits


def run(census_path, cls, out_name, scales=SCALES, limit=None):
    """Re-read every finding of one class from the line census."""
    with open(census_path) as fh:
        findings = [f for f in json.load(fh)['findings'] if f['cls'] == cls]
    if limit:
        findings = findings[:limit]
    by_book = defaultdict(set)
    for f in findings:
        by_book[f['book']].add(f['page'])

    jobs, meta = [], {}
    for f in findings:
        book, page = f['book'], f['page']
        if not os.path.exists(V.pdf_path(book)):
            continue
        try:
            tokens = load_tokens(book, page)
        except FileNotFoundError:
            continue
        tok = next((t for t in tokens if (t.text or '') == f['text']), None)
        if tok is None:
            tok = next((t for t in tokens if f['matched'] and f['matched'] in (t.text or '')), None)
        if tok is None:
            continue
        i = (tok.text or '').find(f['matched']) if f['matched'] else 0
        i = max(0, i)
        key = f'{book}:p{page:03d}:t{tok.index:03d}'
        if key in meta:
            continue
        meta[key] = (book, page, tok, i, len(f['matched'] or ''))
        box = _crop(tok, i, i + max(1, len(f['matched'] or '')))
        for s in scales:
            jobs.append(dict(id=f'{key}@{s:g}', pdf=V.pdf_path(book), page=page, bbox=list(box),
                             scale=float(s), pad=0.0, languages=['en-US'],
                             languageCorrection=False))
    results = V.run(jobs)

    sequences = {}
    rows = []
    for key, (book, page, tok, i, n) in meta.items():
        texts = {}
        for s in scales:
            r = results.get(f'{key}@{s:g}') or {}
            texts[s] = [(ln.get('text') or '') for ln in (r.get('lines') or [])]
        if cls == CE.ROMAN_NUMERAL:
            verdict, value, agreeing = read_roman(texts)
            if book not in sequences:
                sequences[book] = book_roman_sequence(book)
            vv, ref = sequence_validator(value, sequences[book], page) if value else ('NOT_APPLICABLE', None)
        else:
            verdict, value, agreeing = read_ohm(texts)
            vv, ref = ('NOT_APPLICABLE', None)
        rows.append(dict(key=key, book=book, page=page, page_pass=tok.text, matched_at=i,
                         verdict=verdict, value=value, agreeing_scales=list(agreeing),
                         validator=vv, validator_ref=ref,
                         readings={str(k): v for k, v in texts.items()}))
    payload = dict(cls=cls, findings=len(rows), scales=list(scales),
                   by_verdict=dict(Counter(r['verdict'] for r in rows)),
                   by_validator=dict(Counter(r['validator'] for r in rows)), rows=rows)
    os.makedirs(OUT, exist_ok=True)
    path = f'{OUT}/{out_name}.json'
    with open(path, 'w') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(cls, json.dumps(payload['by_verdict']), json.dumps(payload['by_validator']))
    print('->', path)
    return path


if __name__ == '__main__':
    src = f'{OUT}/line-census-all.json'
    which = sys.argv[1] if len(sys.argv) > 1 else 'roman'
    if which == 'roman':
        run(src, CE.ROMAN_NUMERAL, 'symbols-roman')
    else:
        run(src, CE.SYMBOL_CONFUSION, 'symbols-ohm', limit=int(sys.argv[2]) if len(sys.argv) > 2 else None)
