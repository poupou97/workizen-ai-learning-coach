#!/usr/bin/env python3
"""Lane E1 — grounding integrity, and a seeded holdout sample for a human read.

TWO DIFFERENT THINGS, kept apart on purpose:

1. `integrity` — MECHANICAL, over every claim in every TSL-backed lesson. Does the
   grounding actually point where it says it does? A span must lie inside the block,
   the recorded quote must be exactly the characters at that span, and a text-span claim
   must not start or end in the middle of a word. This catches the class of defect that
   produced event titles like «ăm» and causes like «h 17.1, …» — and it catches them
   everywhere, not only where someone happened to look.

   Integrity is NOT precision. A claim can point exactly at the right characters and
   still be a wrong claim about the lesson.

2. `holdout` — a SEEDED SAMPLE for a human to read. The rules were written while looking
   at KHTN 6 Bài 17 and LS&ĐL 5 Bài 8; those two lessons are EXCLUDED here, so whatever
   this sample says is a statement about lessons the rules were not written against.
   The output is written to poc-out (D4) for reading, and only the VERDICT COUNTS come
   back into the repo.

    python3 tool/semantic/verify.py integrity
    python3 tool/semantic/verify.py holdout --n 30 --seed 20260906
"""
import argparse
import collections
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus_io as cio  # noqa: E402
import corpus_paths as cp  # noqa: E402
import extract as ex  # noqa: E402

SEEN_BY_AUTHOR = {('06-sgk-khoa-hoc-tu-nhien-6', 17), ('05-sgk-lich-su-va-dia-li-5', 8)}
WORD_CH = re.compile(r'\w', re.UNICODE)


def _mid_word(text, i):
    """True if position i splits a word (both sides are word characters)."""
    if i <= 0 or i >= len(text):
        return False
    return bool(WORD_CH.match(text[i - 1]) and WORD_CH.match(text[i]))


def integrity(limit=None):
    checks = collections.Counter()
    failures = []
    n_lessons = 0
    for les in cio.iter_tsl():
        n_lessons += 1
        if limit and n_lessons > limit:
            break
        by_id = {b['id']: b for b in les['blocks']}
        g = ex.extract(les)
        for claim in g.claims.values():
            for gr in claim.grounding:
                checks['groundings'] += 1
                block = by_id.get(gr.block_id)
                if block is None:
                    checks['block_missing'] += 1
                    failures.append((les['book'], les['lesson'], claim.derivation,
                                     'block_missing', gr.block_id))
                    continue
                text = block['text'] or ''
                if gr.span is None:
                    checks['no_span_page_geometry'] += 1
                    continue
                checks['spans'] += 1
                s, e = gr.span
                if e > len(text):
                    checks['span_out_of_range'] += 1
                    failures.append((les['book'], les['lesson'], claim.derivation,
                                     'span_out_of_range', '%d..%d of %d' % (s, e, len(text))))
                    continue
                if gr.quote is not None and text[s:e] != gr.quote:
                    checks['quote_mismatch'] += 1
                    failures.append((les['book'], les['lesson'], claim.derivation,
                                     'quote_mismatch', repr(gr.quote)[:60]))
                    continue
                if _mid_word(text, s) or _mid_word(text, e):
                    checks['span_splits_a_word'] += 1
                    failures.append((les['book'], les['lesson'], claim.derivation,
                                     'span_splits_a_word', repr(text[max(0, s - 8):e + 8])[:70]))
                    continue
                checks['span_ok'] += 1
    bad = (checks['block_missing'] + checks['span_out_of_range']
           + checks['quote_mismatch'] + checks['span_splits_a_word'])
    by_rule = collections.Counter((f[2], f[3]) for f in failures)
    return {
        'lessons': n_lessons,
        'counts': dict(checks),
        'integrityFailures': bad,
        'spanIntegrityRate': (round(1.0 - bad / checks['spans'], 4)
                              if checks['spans'] else None),
        'failuresByRuleAndKind': {'%s|%s' % k: v for k, v in by_rule.most_common()},
        'examples': failures[:25],
        'note': 'integrity is NOT precision — a claim can point at exactly the right '
                'characters and still be a wrong claim about the lesson',
    }


def holdout(n=30, seed=20260906):
    """A seeded sample of claims from lessons the rules were NOT written against."""
    rng = random.Random(seed)
    pool = []
    for les in cio.iter_tsl():
        if (les['book'], les['lesson']) in SEEN_BY_AUTHOR:
            continue
        by_id = {b['id']: b for b in les['blocks']}
        g = ex.extract(les)
        for claim in g.claims.values():
            gr = claim.grounding[0]
            block = by_id.get(gr.block_id)
            pool.append({
                'lesson': '%s#%s' % (les['book'], les['lesson']),
                'rule': claim.derivation,
                'kind': claim.kind,
                'assertion': claim.assertion,
                'support': claim.support,
                'quote': gr.quote,
                'blockText': (block['text'] or '')[:300] if block else None,
                'page_printed': gr.page_printed,
                'locator': gr.locator_kind,
            })
    rng.shuffle(pool)
    # stratify: at most ceil(n/#rules) per rule, so a high-volume rule cannot own the sample
    by_rule = collections.defaultdict(list)
    for row in pool:
        by_rule[row['rule']].append(row)
    per = max(1, n // max(1, len(by_rule)))
    sample = []
    for rule in sorted(by_rule):
        sample.extend(by_rule[rule][:per])
    for row in pool:
        if len(sample) >= n:
            break
        if row not in sample:
            sample.append(row)
    return {'seed': seed, 'requested': n, 'poolSize': len(pool),
            'excludedLessons': sorted('%s#%s' % k for k in SEEN_BY_AUTHOR),
            'byRule': {k: len(v) for k, v in sorted(by_rule.items())},
            'sample': sample[:n]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['integrity', 'holdout'])
    ap.add_argument('--n', type=int, default=30)
    ap.add_argument('--seed', type=int, default=20260906)
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args(argv)
    out = cp.out_dir()
    if args.mode == 'integrity':
        res = integrity(limit=args.limit)
        path = os.path.join(out, 'integrity.json')
    else:
        res = holdout(n=args.n, seed=args.seed)
        path = os.path.join(out, 'holdout-sample.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    if args.mode == 'integrity':
        print(json.dumps({k: v for k, v in res.items() if k != 'examples'},
                         ensure_ascii=False, indent=1))
    else:
        print(json.dumps({k: v for k, v in res.items() if k != 'sample'},
                         ensure_ascii=False, indent=1))
    print('-> %s' % path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
