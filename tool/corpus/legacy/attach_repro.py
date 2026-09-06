#!/usr/bin/env python3
"""Round 5 · Lane D — DOES THE STORED ATTACH ARTEFACT REPRODUCE FROM ITS OWN CODE?

Lane A1 reported (not fixed) that the stored `tc2-p2` attach files do not reproduce from the code
that claims to produce them — 83 page verdicts differ. This matters to Lane D more than to anyone,
because Lane D's whole method is *snapshot → the OLD baseline stays reproducible → compare*. A
baseline that cannot be regenerated is not a baseline; it is a memory.

This verifies the claim independently, on Lane D's own copies, and answers the question that
actually decides what to do about it:

    of the page verdicts that differ, how many are EXPLAINED by a named rule change,
    and how many are unexplained drift?

An explained difference is a fix landing. Unexplained drift is a provenance failure, and the two
must never be reported as one number.

    attach_repro.py check [--attach-dir DIR] [--pipeline ID] [--out FILE] [--md FILE]

The regenerated attach is written to a scratch root and never overwrites the stored artefact.
"""
import argparse
import collections
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

SCHEMA = 'lane-d-attach-repro-v1'
CORPUS = os.path.abspath(os.path.join(HERE, '..'))
# A difference is EXPLAINED when the re-run lands on one of these end-matter kinds and the stored file
# did not. These are the verdicts the NAMED rules were written to produce: round 4's cover rule
# (`back_cover`) and round 5's imprint rule (`imprint`), plus the generic tail kinds. Everything else —
# above all a page that stays `kind: page` and changes LESSON — is drift, and the two are never summed.
EXPLAINED_NEW_KINDS = ('imprint', 'back_cover', 'back_matter', 'front_matter')


def page_map(doc):
    return {int(p['page']): (p.get('kind'), p.get('lesson'), p.get('method')) for p in doc.get('pages', [])}


def cmd_check(a):
    attach_dir = os.path.abspath(a.attach_dir)
    books = sorted(f[:-5] for f in os.listdir(attach_dir) if f.endswith('.json'))
    if not books:
        print(f'no stored attach files in {attach_dir}', file=sys.stderr)
        return 2

    scratch = tempfile.mkdtemp(prefix='lane-d-attach-repro-')
    out_root = os.path.join(scratch, 'poc-out', 'trusted-corpus', 'tc-v2', a.pipeline)
    os.makedirs(out_root, exist_ok=True)
    env = dict(os.environ, TC_ROOT=common.MAIN_ROOT)
    cmd = [a.python, os.path.join(CORPUS, 'tc2_attach.py'), '--pipeline', a.pipeline,
           '--out', out_root] + books
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:] + '\n' + r.stderr[-3000:], file=sys.stderr)
        shutil.rmtree(scratch, ignore_errors=True)
        return 3

    rows, per_book = [], {}
    n_pages = n_diff = n_expl = 0
    for b in books:
        new_p = os.path.join(out_root, 'attach', f'{b}.json')
        old = common.load_json(os.path.join(attach_dir, f'{b}.json')) or {}
        new = common.load_json(new_p) or {}
        if not new:
            per_book[b] = {'regenerated': False}
            continue
        o, n = page_map(old), page_map(new)
        diffs = []
        for pg in sorted(set(o) | set(n)):
            ov, nv = o.get(pg), n.get(pg)
            if ov == nv:
                continue
            explained = bool(nv and nv[0] in EXPLAINED_NEW_KINDS and (not ov or ov[0] not in EXPLAINED_NEW_KINDS))
            diffs.append(dict(book=b, page=pg,
                              storedKind=(ov or (None,))[0], newKind=(nv or (None,))[0],
                              storedLesson=(ov or (None, None))[1], newLesson=(nv or (None, None))[1],
                              storedMethod=(ov or (None, None, None))[2], newMethod=(nv or (None, None, None))[2],
                              explained=explained))
        n_pages += len(set(o) | set(n))
        n_diff += len(diffs)
        n_expl += sum(1 for d in diffs if d['explained'])
        per_book[b] = dict(regenerated=True, pages=len(set(o) | set(n)), differing=len(diffs),
                           explained=sum(1 for d in diffs if d['explained']),
                           unexplained=sum(1 for d in diffs if not d['explained']))
        rows += diffs

    unexplained = [d for d in rows if not d['explained']]
    transitions = collections.Counter(f"{d['storedKind']} -> {d['newKind']}" for d in unexplained)
    lesson_moves = [d for d in unexplained if d['storedLesson'] != d['newLesson']]
    out = dict(
        schema=SCHEMA,
        question='does the stored attach artefact reproduce from the code that claims to produce it?',
        storedAttachDir=attach_dir, storedPipeline=(common.load_json(os.path.join(attach_dir, f'{books[0]}.json')) or {}).get('pipeline'),
        regeneratedWith=dict(pipeline=a.pipeline, corpus=CORPUS, codeSha=_sha(CORPUS), scratchRoot=out_root),
        books=len(books), pagesCompared=n_pages,
        pagesDiffering=n_diff,
        pagesExplainedByANamedRule=n_expl,
        pagesUnexplained=len(unexplained),
        pagesUnexplainedThatMoveALesson=len(lesson_moves),
        reproducible=(n_diff == 0),
        note='EXPLAINED = the re-run assigns one of ' + ', '.join(EXPLAINED_NEW_KINDS) +
             ' where the stored file did not — the verdicts the named end-matter rules (round 4 cover, '
             'round 5 imprint) were written to produce. Everything else is drift between an artefact and '
             'the code that reads it as current; above all a page that stays kind=page and changes LESSON.',
        unexplainedTransitions=dict(transitions),
        perBook=per_book,
        unexplainedRows=unexplained[:200])
    if a.out:
        common.dump_json(out, a.out)
        print(f'→ {a.out}')
    print(f'  {len(books)} book(s) · {n_pages} page verdicts compared')
    print(f'  differing {n_diff} · explained by a named end-matter rule {n_expl} · '
          f'UNEXPLAINED {len(unexplained)}')
    if unexplained:
        print(f'  unexplained transitions: {dict(transitions)}')
        print(f'  of the unexplained, {len(lesson_moves)} move a page to a different lesson')
    print(f'  stored artefact reproduces from its own code: {"YES" if n_diff == 0 else "NO"}')
    if a.md:
        L = ['| book | pages compared | differing | explained by a named end-matter rule | **unexplained** |',
             '|---|---|---|---|---|']
        for b, v in sorted(per_book.items()):
            if not v.get('regenerated'):
                L.append(f'| `{b}` | — | — | — | not regenerated |')
                continue
            L.append(f"| `{b}` | {v['pages']} | {v['differing']} | {v['explained']} | **{v['unexplained']}** |")
        L.append(f"| **all** | **{n_pages}** | **{n_diff}** | **{n_expl}** | **{len(unexplained)}** |")
        os.makedirs(os.path.dirname(os.path.abspath(a.md)), exist_ok=True)
        open(a.md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
        print(f'markdown → {a.md}')
    shutil.rmtree(scratch, ignore_errors=True)
    return 0


def _sha(cwd):
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd, text=True).strip()
    except Exception:  # noqa: BLE001
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('check')
    s.add_argument('--attach-dir', default=f'{common.MAIN_ROOT}/poc-out/trusted-corpus/tc-v2/tc2-p1/attach')
    s.add_argument('--pipeline', default='repro-check')
    s.add_argument('--python', default=common.BAKEOFF_PYTHON)
    s.add_argument('--out', default='')
    s.add_argument('--md', default='')
    s.set_defaults(fn=cmd_check)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
