#!/usr/bin/env python3
"""TC-v1 — CASCADE / ENSEMBLE simulator: agreement gates between independent stacks.

Why (Founder order H): no single parser wins every layout, and an LLM/VLM is
never automatically source truth. A block is TRUSTED only when two
independent analyses AGREE on its text and on its position in the reading
order; disagreement → UNKNOWN → the block is withheld (fail closed). This
script builds "virtual candidates" from the real bake-off outputs and scores
them with tc_score, so TLSR / false-trust / CTE of each cascade are measured
on the same gold set, not estimated.

Cascades (primary ▸ verifier(s)):
  docling>xycut     Docling layout (Apple Vision OCR) verified by the WAL-206 XY-cut
                    (same OCR, independent layout analysis)
  docling>marker    Docling verified by Marker/Surya (independent OCR + layout)
  docling>vlm       Docling verified by the local VLM transcription (Qwen2.5-VL-3B)
  marker>vlm        Marker verified by the VLM
  docling>marker+vlm  Docling verified by BOTH (3-way agreement)
  xycut>docling     WAL-206 XY-cut (its own trust) additionally verified by Docling

Agreement rule per primary block P (text ≥ 12 chars):
  text   — a verifier block V exists whose normalised text contains P's text at
           similarity ≥ TEXT_SIM (rapidfuzz partial ratio) or equals it at ≥ TEXT_SIM
  order  — the verifier blocks matched to P and to the previous trusted primary
           block are in the same order (non-decreasing), or are the same V block
  role   — if the primary says QUESTION and the verifier has a role concept that
           says HEADING, the block is NOT trusted (heading-as-question guard)
Blocks shorter than 12 chars (headings like "Giải", page numbers) are trusted
when found verbatim. Anything else → trusted=False (withheld).

Usage: <bake-off venv python> tool/corpus/tc_cascade.py [--ver tc-v1] [--json out] [--md out]
"""
import argparse
import copy
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tc_sdm  # noqa: E402
import tc_score  # noqa: E402

TEXT_SIM = 92.0
try:
    from rapidfuzz import fuzz
except Exception:  # pragma: no cover
    fuzz = None


def sim(a, b):
    if fuzz is None:
        return 100.0 if a == b else 0.0
    if not a or not b:
        return 0.0
    if len(b) > len(a) * 1.3:
        return fuzz.partial_ratio(a, b)
    return fuzz.ratio(a, b)


def _stream(ver):
    """Verifier as one reading-order text stream (block boundaries kept as offsets → roles)."""
    parts, roles, pos = [], [], 0
    for v in ver['blocks']:
        k = tc_score.norm_key(v['text'])
        if not k:
            continue
        parts.append(k); roles.append((pos, pos + len(k), v['role'])); pos += len(k) + 3
    return '   '.join(parts), roles


def verify(primary, verifiers):
    """Return a copy of `primary` with trusted flags set by agreement with every verifier.
    Text: the primary block must align (partial ratio ≥ TEXT_SIM) inside the verifier's
    reading-order stream. Order: alignment offsets must not go backwards (one-block tolerance,
    so a single displaced box withholds only itself, not everything after it)."""
    out = copy.deepcopy(primary)
    streams = [_stream(v) for v in verifiers]
    last2 = [[-1, -1] for _ in verifiers]
    stats = Counter()
    for p in out['blocks']:
        pk = tc_score.norm_key(p['text'])
        if not pk or p['role'] == 'FIGURE':
            p['trusted'] = None if p['role'] == 'FIGURE' else False
            continue
        ok_all = True
        for vi, (st, roles) in enumerate(streams):
            if fuzz is None or not st:
                ok_all = False; stats['text_disagree'] += 1; break
            if len(pk) >= 12:
                al = fuzz.partial_ratio_alignment(pk, st)
                score, start = (al.score, al.dest_start) if al else (0.0, -1)
            else:
                idx = (' ' + st + ' ').find(' ' + pk + ' ')
                score, start = (100.0, idx) if idx >= 0 else (0.0, -1)
            if score < TEXT_SIM:
                ok_all = False; stats['text_disagree'] += 1; break
            if start < min(last2[vi]):
                ok_all = False; stats['order_disagree'] += 1; last2[vi] = [last2[vi][1], start]; break
            vrole = next((r for a, b, r in roles if a <= start < b), None)
            if p['role'] == 'QUESTION' and vrole == 'HEADING':
                ok_all = False; stats['role_conflict'] += 1; break
            last2[vi] = [last2[vi][1], start]
        if ok_all and primary['candidate'] == 'current-xycut' and p['trusted'] is False:
            ok_all = False; stats['primary_untrusted'] += 1
        p['trusted'] = bool(ok_all)
        stats['trusted' if ok_all else 'withheld'] += 1
    out['meta'] = dict(cascade=True, stats=dict(stats))
    return out


import re as _re
MATH = _re.compile(r'\d\s*[<>=×÷:+−]\s*[\d?]|[a-zA-Z]\s*[²³]|√|\d\s*/\s*\d|\b[xy]\s*[=≠]|∫|≥|≤|≠')


def math_guard(sdm):
    """Deterministic rule: a block that carries math tokens but was NOT recognised as a FORMULA/TABLE
    by the parser is withheld — every text-line OCR stack flattens fractions, exponents and
    comparison symbols the same way, so agreement between stacks cannot catch it."""
    out = copy.deepcopy(sdm); n = 0
    for b in out['blocks']:
        if b.get('trusted') and b['role'] not in ('FORMULA', 'TABLE') and MATH.search(b['text'] or ''):
            b['trusted'] = False; n += 1
    out['meta'] = dict(out.get('meta') or {}); out['meta'].setdefault('stats', {})['math_guard_withheld'] = n
    return out


CASCADES = [
    ('docling>xycut', 'docling-ocrmac', ['current-xycut']),
    ('docling>marker', 'docling-ocrmac', ['marker']),
    ('docling>vlm', 'docling-ocrmac', ['vlm-mlx']),
    ('marker>vlm', 'marker', ['vlm-mlx']),
    ('marker>docling', 'marker', ['docling-ocrmac']),
    ('docling>marker+vlm', 'docling-ocrmac', ['marker', 'vlm-mlx']),
    ('xycut>docling', 'current-xycut', ['docling-ocrmac']),
    ('docling>xycut+mathguard', 'docling-ocrmac', ['current-xycut']),
    ('marker>docling+mathguard', 'marker', ['docling-ocrmac']),
    ('docling>marker+vlm+mathguard', 'docling-ocrmac', ['marker', 'vlm-mlx']),
]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ver', default='tc-v1'); ap.add_argument('--json', default=None); ap.add_argument('--md', default=None)
    a = ap.parse_args()
    golds = tc_sdm.all_gold()
    rows = []
    for g in golds:
        for name, prim, vers in CASCADES:
            P = tc_sdm.load_sdm(prim, g['book'], g['page'], a.ver)
            Vs = [tc_sdm.load_sdm(v, g['book'], g['page'], a.ver) for v in vers]
            if P is None or P.get('error') or any(v is None or v.get('error') for v in Vs):
                rows.append(dict(book=g['book'], page=g['page'], candidate=name, error='not run')); continue
            S = verify(P, Vs); S['candidate'] = name
            if name.endswith('+mathguard'):
                S = math_guard(S)
            r = tc_score.score(g, S); r['candidate'] = name; r['cascade_stats'] = S['meta']['stats']
            rows.append(r)
    agg = {}
    for name, _, _ in CASCADES:
        rs = [r for r in rows if r['candidate'] == name and not r.get('error')]
        if not rs:
            continue
        L = sum(r['learning_blocks'] for r in rs); T = sum(r['trusted_blocks'] for r in rs); W = sum(r['false_trusted'] for r in rs)
        cte = Counter()
        for r in rs:
            cte.update({k: v for k, v in r['cte'].items() if k != 'lesson_attach_wrong'})
        # CTE among TRUSTED blocks only: recompute from wrong_examples classes
        agg[name] = dict(pages=len(rs), learning_blocks=L, trusted=T, coverage=round(T / max(1, L), 3), tlsr=round(sum(r['tlsr'] * r['learning_blocks'] for r in rs) / max(1, L), 3),
                         false_trusted=W, ftr=round(W / max(1, T), 4), safe_rejected=sum(r['safe_rejected'] for r in rs),
                         wrong_kinds=dict(Counter(k for r in rs for _, ks in r['wrong_examples'] for k in ks)), cte_all_output=dict(cte),
                         found=round(sum(r['found'] for r in rs) / len(rs), 3), order=round(sum(r['order'] for r in rs if r['order'] is not None) / max(1, sum(1 for r in rs if r['order'] is not None)), 3),
                         text_acc=round(sum(r['text_acc'] for r in rs if r['text_acc'] is not None) / max(1, sum(1 for r in rs if r['text_acc'] is not None)), 3),
                         gate=dict(sum((Counter(r['cascade_stats']) for r in rs), Counter())))
    out = dict(rows=rows, aggregate=agg)
    if a.json:
        json.dump(out, open(a.json, 'w'), ensure_ascii=False, indent=1)
    L = ['# TC-v1 cascade / ensemble simulation (MEASURED on the gold set)', '',
         '| cascade | pages | learning blocks | trusted (coverage) | TLSR | false trusted | FTR | withheld (safe) | wrong kinds among trusted | gate stats |', '|---|---|---|---|---|---|---|---|---|---|']
    for n, v in agg.items():
        L.append(f"| {n} | {v['pages']} | {v['learning_blocks']} | {v['trusted']} ({v['coverage']:.3f}) | {v['tlsr']:.3f} | {v['false_trusted']} | {v['ftr']:.4f} | {v['safe_rejected']} | {v['wrong_kinds']} | {v['gate']} |")
    md = '\n'.join(L) + '\n'
    if a.md:
        open(a.md, 'w').write(md)
    print(md)


if __name__ == '__main__':
    main()
