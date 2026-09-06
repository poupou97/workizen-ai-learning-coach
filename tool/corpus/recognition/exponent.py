#!/usr/bin/env python3
"""The second failure class: a power-of-ten exponent destroyed at recognition.

`3×10⁸ m/s` is served as `3×10° m/s` — TRUSTED, on three blocks, today. Round 5 could detect it
and could not repair it, and said exactly why: *«the exponent's value is not in the text —
recovering it needs a recogniser on the printed region»*. This is that recogniser, on that region,
with an independent validator in front of it.

The chain, and every step is refusable:

  1. `mathfix.sci_notation.find_destroyed_exponents` finds the LINE and the character span. This
     is round 5's detector, unchanged; nothing here re-detects.
  2. the span is turned into a crop box. Vision line boxes have no per-character geometry, so the
     span's position inside the line is estimated by character proportion and the box is padded
     generously — an estimate that is allowed to be loose because the recogniser reads what is in
     the box and the box is never itself evidence.
  3. Vision reads that box at several scales, with language correction OFF.
  4. a reading is a CANDIDATE only when >=2 scales return the same `10<digits>` where the page
     pass returned `10°`.
  5. `si_expected_exponent` — the page's OWN printed prefix relation, `1 kJ = 10ⁿ J` ⇒ n=3 — is
     an INDEPENDENT validator that did not produce the candidate. Where it applies and disagrees,
     the candidate is refused. Where it does not apply it ABSTAINS, and abstention is never a pass:
     the reading is reported as recovered **at recognition level** and not as a validated repair.

That last distinction is the whole report. A digit that is now read is a recognition result. It is
not a repair, it is not trusted, and it does not reach a child.
"""
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathfix import sci_notation as SN                 # noqa: E402
from mathfix.tokens import load_tokens                 # noqa: E402
from recognition import vision as V                    # noqa: E402

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
OUT = f'{ROOT}/poc-out/round6/recognition'

SCALES = (8.0, 14.0, 20.0, 28.0)
#: what a recovered reading looks like: the literal ten, then the exponent digits that the page
#: pass turned into a degree sign. `10°` coming back unchanged is NOT a reading — it is the same
#: failure at a different scale, and counting it as an observation would be counting the defect.
RECOVERED = re.compile(r'(?<!\d)10\s?(\d{1,2})(?!\d)')
STILL_BROKEN = re.compile(r"10\s*[°'′]")

PAD_LEFT_CHARS = 1.0        # widen the estimated span by this many character widths on each side
PAD_RIGHT_CHARS = 1.0
PAD_ABOVE = 0.6             # in line heights: a superscript sits above the line's own box
PAD_BELOW = 0.4


def crop_box(token, finding):
    """The box to re-read, estimated from the line box and the match's character span."""
    n = max(1, len(token.text))
    x0 = token.x + token.w * max(0.0, finding.start - PAD_LEFT_CHARS) / n
    x1 = token.x + token.w * min(float(n), finding.end + PAD_RIGHT_CHARS) / n
    return (max(0.0, x0), max(0.0, token.y - PAD_ABOVE * token.h),
            min(1.0, x1), min(1.0, token.y + (1.0 + PAD_BELOW) * token.h))


#: `(2 + x)^100` is not a power of ten, and `-35/10 ; -1/10` is not one either. Both were RECOVERED
#: by the first version of this rule and both were wrong, so the shape rule carries their scars:
#: an exponent may not be preceded by a closing bracket or a letter, and `10` followed by a lone
#: `0` is refused outright — `10^0` is 1 and no book writes it in scientific notation.
NOT_A_POWER = re.compile(r'[)\]A-Za-z]\s*$')


def _exponent_in(text):
    """The exponent this ONE line offers, or None.

    Per line, never over a joined page: the first version searched `' '.join(texts)` and read
    `10` out of the two separate lines `-35 -1` / `10` / `10` on Toán 6 tập hai p31, where the
    page prints two stacked fractions. A regex that may span a line break is not reading a
    superscript, it is reading a coincidence.
    """
    for m in RECOVERED.finditer(text or ''):
        if NOT_A_POWER.search((text or '')[:m.start()]):
            continue
        if m.group(1) == '0':
            continue
        return m.group(1)
    return None


def read(readings, min_agreeing=2):
    """`{scale: [text, ...]}` -> (verdict, exponent, agreeing scales).

    Verdicts: `RECOVERED` · `CONFLICT` · `INSUFFICIENT_AGREEMENT` · `STILL_BROKEN` · `UNREAD`.
    """
    votes = {}
    broken = 0
    for scale, texts in sorted(readings.items()):
        got = next((v for v in (_exponent_in(t) for t in texts) if v), None)
        if got:
            votes[scale] = got
        elif any(STILL_BROKEN.search(t or '') for t in texts):
            broken += 1
    if not votes:
        return ('STILL_BROKEN' if broken else 'UNREAD'), None, ()
    counts = Counter(votes.values())
    if len(counts) > 1:
        return 'CONFLICT', None, tuple(sorted(votes))
    value = next(iter(counts))
    agreeing = tuple(s for s, v in sorted(votes.items()) if v == value)
    if len(agreeing) < min_agreeing:
        return 'INSUFFICIENT_AGREEMENT', value, agreeing
    return 'RECOVERED', value, agreeing


def validate(value, line_text):
    """The independent check: PASS · FAIL · NOT_APPLICABLE. Never a generator."""
    expected = SN.si_expected_exponent(line_text)
    if expected is None:
        return 'NOT_APPLICABLE', None
    return ('PASS' if str(expected) == str(value) else 'FAIL'), expected


def run(findings, scales=SCALES, out_name='exponent'):
    """`findings` are `(book, page)` pairs; every destroyed exponent on those pages is re-read."""
    jobs, meta = [], {}
    for book, page in sorted(set(findings)):
        try:
            tokens = load_tokens(book, page)
        except FileNotFoundError:
            continue
        if not os.path.exists(V.pdf_path(book)):
            continue
        for t in tokens:
            for j, f in enumerate(SN.find_destroyed_exponents(t.text)):
                key = f'{book}:p{page:03d}:t{t.index:03d}:{j}'
                meta[key] = (book, page, t.text, f)
                box = crop_box(t, f)
                for s in scales:
                    jobs.append(dict(id=f'{key}@{s:g}', pdf=V.pdf_path(book), page=page,
                                     bbox=list(box), scale=float(s), pad=0.0,
                                     languages=['en-US'], languageCorrection=False))
    results = V.run(jobs)

    rows = []
    for key, (book, page, text, f) in meta.items():
        readings = {}
        for s in scales:
            r = results.get(f'{key}@{s:g}') or {}
            readings[s] = [(ln.get('text') or '') for ln in (r.get('lines') or [])]
        verdict, value, agreeing = read(readings)
        vv, expected = validate(value, text) if value else ('NOT_APPLICABLE', None)
        rows.append(dict(key=key, book=book, page=page, line=text, matched=f.matched,
                         verdict=verdict, exponent=value, agreeing_scales=list(agreeing),
                         si_validator=vv, si_expected=expected,
                         readings={str(k): v for k, v in readings.items()}))
    payload = dict(findings=len(rows), scales=list(scales),
                   by_verdict=dict(Counter(r['verdict'] for r in rows)),
                   by_validator=dict(Counter(r['si_validator'] for r in rows)), rows=rows)
    os.makedirs(OUT, exist_ok=True)
    path = f'{OUT}/{out_name}.json'
    with open(path, 'w') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps(payload['by_verdict'], indent=1))
    print(json.dumps(payload['by_validator'], indent=1))
    print('->', path)
    return path


def pages_from_census(census_path):
    with open(census_path) as fh:
        doc = json.load(fh)
    return [(f['book'], f['page']) for f in doc['findings'] if f['cls'] == 'SUPERSCRIPT']


# ---------------------------------------------------------------- identity, not coverage
#
# Two of the four false recognitions in the first run were the SAME failure, and it is round 5's
# failure with a different glyph: the page prints `10^-5` and `10^-10`, the recogniser returns
# `105` and `1010`, and every text-level check passes because the magnitude is right. The minus is
# a printed mark nobody read. Ink-accounting would not see it; provenance would not see it; only
# looking at the pixels where the sign should be sees it.
#
# So: before accepting an exponent, ask the raster whether a small detached horizontal bar sits in
# the superscript band. This does not READ the sign — it refuses to pretend the sign is absent.

SIGN_BAND_TOP = 0.10          # in line heights, measured down from the token's own box top
SIGN_BAND_BOTTOM = 0.62       # …to here: above the x-height, where a superscript lives
SIGN_MIN_LEN = 0.10           # a run shorter than this share of the line height is a speck
SIGN_MAX_LEN = 0.70           # …and one longer than this is a rule, a fraction bar or an em dash
SIGN_MAX_THICK = 0.18         # a minus is thin; a digit stroke is not
SIGN_DETACH = 0.06            # blank rows required above and below, in line heights


def superscript_sign(mask, token, finding, pad_chars=0.3, after_ten_chars=2.5):
    """True when the superscript band holds a detached horizontal bar — a printed minus.

    Returns None when the band cannot be judged (no ink at all), and abstention is not a pass:
    `run` treats None as «unjudgeable» and keeps the reading, because a guard that refused every
    exponent would be safe and useless — round 5's own words about `operator-raster-v1`.
    """
    n = max(1, len(token.text))
    # Only the window BETWEEN the ten and the exponent, never the whole match. Measured: with the
    # window over the whole match the guard fires on 9 of 18 readings, and on `152-10^6 km`,
    # `6,63-10^14` and `1,013.10^5 Pa` what it finds is the printed multiplication mark to the LEFT
    # of the ten. A sign that changes an exponent sits to its RIGHT.
    x0 = token.x + token.w * max(0.0, finding.start + after_ten_chars) / n
    x1 = token.x + token.w * min(float(n), finding.end + pad_chars) / n
    lh = token.h
    px0, px1 = int(x0 * mask.width), int(x1 * mask.width)
    y0 = int((token.y + SIGN_BAND_TOP * lh) * mask.height)
    y1 = int((token.y + SIGN_BAND_BOTTOM * lh) * mask.height)
    lh_px = max(1.0, lh * mask.height)
    lo, hi = SIGN_MIN_LEN * lh_px, SIGN_MAX_LEN * lh_px
    thick_max = max(1, int(SIGN_MAX_THICK * lh_px))
    detach = max(1, int(SIGN_DETACH * lh_px))
    if not mask.any_ink(px0, y0, px1, y1):
        return None
    for y in range(y0, max(y0 + 1, y1)):
        # `row_runs` returns (start, LENGTH), not (start, end) — reading it as an end coordinate
        # is what made the first version of this guard silently never fire, on 18 of 18 readings.
        for a, ln in mask.row_runs(y, px0, px1, min_len=int(lo)):
            b = a + ln
            if not (lo <= ln <= hi):
                continue
            thick = 0
            while thick <= thick_max and mask.any_ink(a, y + thick, b, y + thick + 1):
                thick += 1
            if thick > thick_max:
                continue
            if mask.any_ink(a, y - detach - 1, b, y) or mask.any_ink(a, y + thick, b, y + thick + detach + 1):
                continue                      # ink continues through: a digit stroke, not a sign
            return True
    return False


def rescore(path, out_name='exponent-guarded'):
    """Re-judge a finished run with the shape rules and the raster sign check.

    Re-judging rather than re-running is deliberate: the recogniser's answers are unchanged and
    stored, so the effect of each guard is measured on exactly the same observations. A guard
    evaluated on fresh observations cannot be told apart from noise.
    """
    from mathfix.inkmask import InkMask
    with open(path) as fh:
        doc = json.load(fh)
    cache, rows = {}, []
    for r in doc['rows']:
        readings = {float(k): v for k, v in r['readings'].items()}
        verdict, value, agreeing = read(readings)
        sign = None
        if verdict == 'RECOVERED':
            key = (r['book'], r['page'])
            if key not in cache:
                try:
                    cache[key] = (InkMask.from_pdf(V.pdf_path(r['book']), r['page'], dpi=300),
                                  load_tokens(r['book'], r['page']))
                except Exception:
                    cache[key] = (None, None)
            mask, tokens = cache[key]
            if mask is not None:
                idx = int(r['key'].split(':t')[1].split(':')[0])
                tok = next((t for t in tokens if t.index == idx), None)
                fs = SN.find_destroyed_exponents(tok.text) if tok else []
                j = int(r['key'].rsplit(':', 1)[1])
                if tok is not None and j < len(fs):
                    sign = superscript_sign(mask, tok, fs[j])
            if sign is True:
                verdict = 'REFUSED_SIGNED_EXPONENT'
        vv, expected = validate(value, r['line']) if value else ('NOT_APPLICABLE', None)
        rows.append(dict(r, verdict=verdict, exponent=value, agreeing_scales=list(agreeing),
                         raster_sign=sign, si_validator=vv, si_expected=expected))
    payload = dict(doc, rows=rows, by_verdict=dict(Counter(x['verdict'] for x in rows)),
                   by_validator=dict(Counter(x['si_validator'] for x in rows)),
                   guards=['per-line match', 'not-a-power-of-ten shape', 'raster superscript sign'])
    out = f'{OUT}/{out_name}.json'
    with open(out, 'w') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps(payload['by_verdict'], indent=1))
    print('->', out)
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'rescore':
        rescore(sys.argv[2] if len(sys.argv) > 2 else f'{OUT}/exponent.json')
    else:
        src = sys.argv[1] if len(sys.argv) > 1 else f'{OUT}/line-census-all.json'
        run(pages_from_census(src))
