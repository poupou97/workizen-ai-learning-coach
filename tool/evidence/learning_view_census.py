#!/usr/bin/env python3
"""ROUND 6 · WS-D — LEARNING VIEW CENSUS: what can the three views actually be built on?

**FORMS BEFORE RULES.** Round 5 proved why the other order fails: E2's sequence rule
fired on 6 of 54 gold pages at learner-facing precision 0.500, and Toán / Tiếng Việt /
Tin học produced nothing at all. So before anyone adds a renderer family, measure the
FORMS that exist in the real corpus.

This is the census for the question WS-D owns: **for a real lesson, what does each of
the three Learning Views have to show?**

    📖 Đọc         always something — this is the floor
    ✨ Trực quan    only when the lesson yields typed `SemanticData`
    🦉 Học với SAM  only when the lesson yields a tutor script

It runs the SAME bridge the product uses (`tool/corpus/tsl_to_lesson_document.py`,
read-only, `--no-crops`) over every TSL it is pointed at, and counts what comes out.
Nothing here derives a new rule, invents a form, or writes into the corpus.

    python3 tool/evidence/learning_view_census.py \\
        [--lessons poc-out/trusted-corpus/tc-v2/tc2-p1/lessons] \\
        [--limit N] [--json <out>] [--md <out>]

WHAT IS MEASURED, per lesson (all machine-derived, none estimated):
  served / withheld block counts and the withheld reason histogram;
  block-type histogram (the FORM census as the app sees it);
  semantic kinds produced (process · comparison · conceptMap · timeline) and the
  derivation rule that produced each — this is the VISUAL GRAMMAR denominator;
  whether a tutor script exists.

DENOMINATORS ARE NAMED, NEVER MERGED. The census reports **lessons attempted**,
**lessons bridged**, and **lessons refused** separately, with the refusal reason. A rate
whose denominator is «the ones that worked» is the oldest way to make a pipeline look
better than it is.

Standard library only, plus the bridge. Read-only on every input.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))
import tsl_to_lesson_document as bridge  # noqa: E402

DEFAULT_LESSONS = os.path.join(
    ROOT, 'poc-out', 'trusted-corpus', 'tc-v2', 'tc2-p1', 'lessons')


def tsl_paths(root):
    out = []
    for dirpath, _dirs, files in os.walk(root):
        for f in sorted(files):
            if f.endswith('.tsl.json'):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


def census_one(path):
    """One lesson → a row, or a refusal row. Never raises."""
    rel = os.path.relpath(path, ROOT)
    try:
        with open(path, encoding='utf-8') as fh:
            tsl = json.load(fh)
    except (ValueError, UnicodeDecodeError) as e:
        return dict(tsl=rel, ok=False, refusal=f'unreadable: {e.__class__.__name__}')
    try:
        doc = bridge.convert(
            tsl,
            tsl_rel_path=rel,
            tsl_sha256=None,
            book_meta=bridge.book_meta_for(tsl.get('book')),
            chapters=None,
            crops=None,
        )
    except Exception as e:  # BridgeRefusal and anything else — both are answers
        return dict(tsl=rel, ok=False, book=tsl.get('book'), lesson=tsl.get('lesson'),
                    refusal=f'{e.__class__.__name__}: {e}'[:200])

    blocks = doc.get('blocks') or []
    types = collections.Counter(b.get('type') for b in blocks)
    reasons = collections.Counter(
        r for b in blocks if b.get('type') == 'withheld'
        for r in (b.get('reasons') or ([b['reason']] if b.get('reason') else []))
    )
    semantic = doc.get('semantic') or []
    kinds = collections.Counter(s.get('kind') or s.get('type') for s in semantic)
    # `derivation` is a plain rule id in this schema («tsl-enumerated-steps-v1»);
    # accept the dict form too rather than silently reporting zero rules.
    rules = collections.Counter()
    for x in semantic:
        d = x.get('derivation')
        rules[d.get('rule') if isinstance(d, dict) else d] += 1
    served = sum(n for t, n in types.items() if t != 'withheld')
    withheld = types.get('withheld', 0)
    return dict(
        tsl=rel, ok=True, book=doc.get('book'), lesson=doc.get('lesson'),
        blocks=len(blocks), served=served, withheld=withheld,
        types=dict(types), withheldReasons=dict(reasons),
        # Images are dropped when the bridge runs without crops, so the block-type
        # histogram UNDER-REPORTS them. The TSL's own figure count is the honest
        # number and is carried separately — never folded into `types`.
        figuresInTsl=len((tsl.get('figures') or [])),
        semanticKinds=dict(kinds), semanticRules=dict(rules),
        hasSemantic=bool(semantic), hasTutor=bool(doc.get('tutorScript')),
    )


def summarise(rows):
    ok = [r for r in rows if r['ok']]
    refused = [r for r in rows if not r['ok']]
    by_book = collections.defaultdict(lambda: dict(
        lessons=0, withSemantic=0, withTutor=0, served=0, withheld=0))
    kinds, rules, reasons, types = (collections.Counter() for _ in range(4))
    figures = 0
    for r in ok:
        b = by_book[r['book']]
        b['lessons'] += 1
        b['withSemantic'] += int(r['hasSemantic'])
        b['withTutor'] += int(r['hasTutor'])
        b['served'] += r['served']
        b['withheld'] += r['withheld']
        kinds.update(r['semanticKinds'])
        rules.update(r['semanticRules'])
        reasons.update(r['withheldReasons'])
        types.update(r['types'])
        figures += r.get('figuresInTsl', 0)
    return dict(
        attempted=len(rows), bridged=len(ok), refused=len(refused),
        refusals=collections.Counter(
            r['refusal'].split(':')[0] for r in refused),
        lessonsWithSemantic=sum(1 for r in ok if r['hasSemantic']),
        lessonsWithTutor=sum(1 for r in ok if r['hasTutor']),
        servedTotal=sum(r['served'] for r in ok),
        withheldTotal=sum(r['withheld'] for r in ok),
        semanticKinds=dict(kinds), semanticRules=dict(rules),
        withheldReasons=dict(reasons.most_common()), blockTypes=dict(types),
        figuresInTsl=figures,
        byBook={k: v for k, v in sorted(by_book.items())},
    )


def render_md(s, rows):
    def pct(n, d):
        return '—' if not d else f'{n / d:.3f}'
    L = ['# Learning View census — what the three views can be built on', '',
         f"- lessons **attempted** {s['attempted']} · **bridged** {s['bridged']} · "
         f"**refused** {s['refused']}",
         f"- served blocks {s['servedTotal']} · withheld {s['withheldTotal']} "
         f"(withheld share {pct(s['withheldTotal'], s['servedTotal'] + s['withheldTotal'])})",
         '',
         '## The number that decides whether ✨ Trực quan has anything to show', '',
         '| | lessons | share of bridged |', '|---|---|---|',
         f"| **yields typed `SemanticData`** | {s['lessonsWithSemantic']} | "
         f"**{pct(s['lessonsWithSemantic'], s['bridged'])}** |",
         f"| yields a tutor script | {s['lessonsWithTutor']} | "
         f"{pct(s['lessonsWithTutor'], s['bridged'])} |",
         '',
         'Denominator = **lessons bridged**, never «lessons that produced something».',
         '']
    if s['refused']:
        L += ['## Refused by the bridge (an answer, not a gap in the census)', '',
              '| refusal | lessons |', '|---|---|']
        L += [f'| `{k}` | {v} |' for k, v in sorted(s['refusals'].items())]
        L += ['']
    L += ['## Semantic kinds actually produced', '', '| kind | instances |', '|---|---|']
    L += [f'| `{k}` | {v} |' for k, v in sorted(s['semanticKinds'].items(),
                                                key=lambda x: -x[1])] or ['| — | 0 |']
    L += ['', '## Derivation rules that produced them', '', '| rule | instances |',
          '|---|---|']
    L += [f'| `{k}` | {v} |' for k, v in sorted(s['semanticRules'].items(),
                                                key=lambda x: -x[1])] or ['| — | 0 |']
    L += ['', '## FORM CENSUS — block types the app receives', '',
          '⚠ The census runs the bridge **without crops**, so `image` blocks are dropped '
          'and this histogram UNDER-REPORTS them. The honest figure count comes from the '
          f"TSLs themselves: **{s['figuresInTsl']} figures**. Never fold it into the "
          'table below — it is a different measurement.', '',
          '| type | blocks |', '|---|---|']
    L += [f'| `{k}` | {v} |' for k, v in sorted(s['blockTypes'].items(),
                                                key=lambda x: -x[1])]
    L += ['', '## Why blocks are withheld', '', '| reason | blocks |', '|---|---|']
    L += [f'| `{k}` | {v} |' for k, v in s['withheldReasons'].items()]
    L += ['', '## Per book', '',
          '| book | lessons | with `SemanticData` | with tutor | served | withheld |',
          '|---|---|---|---|---|---|']
    for b, v in s['byBook'].items():
        L.append(f"| `{b}` | {v['lessons']} | {v['withSemantic']} "
                 f"({pct(v['withSemantic'], v['lessons'])}) | {v['withTutor']} | "
                 f"{v['served']} | {v['withheld']} |")
    L.append('')
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--lessons', default=DEFAULT_LESSONS)
    ap.add_argument('--limit', type=int)
    ap.add_argument('--json', dest='json_out')
    ap.add_argument('--md', dest='md_out')
    a = ap.parse_args(argv)

    paths = tsl_paths(a.lessons)
    if a.limit:
        paths = paths[:a.limit]
    if not paths:
        raise SystemExit(f'no *.tsl.json under {a.lessons}')
    rows = [census_one(p) for p in paths]
    s = summarise(rows)
    md = render_md(s, rows)
    print(md)
    for path, payload in ((a.json_out, dict(summary=s, lessons=rows)),
                          (a.md_out, md)):
        if not path:
            continue
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as fh:
            if isinstance(payload, str):
                fh.write(payload)
            else:
                json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True,
                          default=dict)
                fh.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
