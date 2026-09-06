#!/usr/bin/env python3
"""Lane E1 · §27 EARLY FOUNDER CHECKPOINT — SOURCE -> SEMANTIC -> VISUAL SPEC, end to end.

Runs the ONE extractor and the SAME compilers over lessons from DIFFERENT SUBJECTS and
writes, per lesson, the graph candidate and every VisualSpec it supports. The point is
not the pictures: it is that no rule and no compiler branched on the subject.

    python3 tool/semantic/run_poc.py                    # the two checkpoint lessons
    python3 tool/semantic/run_poc.py --all-science      # all 238 Science TSLs
    python3 tool/semantic/run_poc.py --all-history      # all LS&DL 5 TSLs

Outputs go to the gitignored poc-out/round5/semantic/ (D4: no verbatim SGK in the repo).
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus_io as cio  # noqa: E402
import corpus_paths as cp  # noqa: E402
import extract as ex  # noqa: E402
import visualspec as vs  # noqa: E402

def _hist(pipeline, root):
    return os.path.join(cp.poc_out(), 'round5' if pipeline == 'tc2-r5' else 'round4',
                        'lane-c', 'tc2-lsdl5', 'v1', 'root', 'poc-out',
                        'trusted-corpus', 'tc-v2', pipeline, 'lessons', root)


HISTORY_TSL = _hist('tc2-r5', '05-sgk-lich-su-va-dia-li-5')
HISTORY_TSL_P1 = _hist('tc2-p1', '05-sgk-lich-su-va-dia-li-5')

CHECKPOINT = [
    # (path, subject, grade) — two subjects, two books, ONE extractor, ZERO branches
    (os.path.join(cp.tsl_dir(), '06-sgk-khoa-hoc-tu-nhien-6', 'bai-17.tsl.json'),
     'KHTN', 6),
    (os.path.join(HISTORY_TSL, 'bai-08.tsl.json'), 'LS&ĐL', 5),
    # the SAME History lesson from the round-4 pipeline build. Kept in the checkpoint on
    # purpose: the two builds differ in whether the block carrying the lesson's dated
    # events survives, so the pair measures how much a visual family depends on the
    # SOURCE pipeline version rather than on the semantic rules. See STRUCTURE-GAPS.
    (os.path.join(HISTORY_TSL_P1, 'bai-08.tsl.json'), 'LS&ĐL (tc2-p1 build)', 5),
]


def run_one(path, subject, grade, out_root, write=True):
    les = cio.load_tsl(path)
    g = ex.extract(les, subject=subject, grade=grade)
    fams, prims, rels = ex.families_present(g)
    specs = vs.compile_all(g)
    rec = {
        'lesson': '%s#%s' % (g.book, g.lesson),
        'subject': subject, 'grade': grade, 'title': g.title,
        'sourceBlocks': len(les['blocks']),
        'withheldRegions': len(les.get('withheld') or []),
        'graph': g.summary(),
        'primitives': prims, 'relations': rels,
        'familiesFromGraph': fams,
        'familiesCompiled': sorted(specs),
        'specElements': {f: len(s.elements) for f, s in specs.items()},
    }
    if write:
        d = os.path.join(out_root, g.book)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'bai-%s.graph.json' % g.lesson), 'w',
                  encoding='utf-8') as fh:
            json.dump(g.to_json(), fh, ensure_ascii=False, indent=1)
        for fam, spec in specs.items():
            with open(os.path.join(d, 'bai-%s.%s.visualspec.json' % (g.lesson, fam.lower())),
                      'w', encoding='utf-8') as fh:
                json.dump(spec.to_json(), fh, ensure_ascii=False, indent=1)
    return rec, g, specs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--all-science', action='store_true')
    ap.add_argument('--all-history', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args(argv)

    out_root = cp.out_dir('poc')
    jobs = list(CHECKPOINT)
    if args.all_science:
        jobs = [(p, 'KHTN/Khoa học', cio.book_grade(p.split('/')[-2]))
                for p in cio.tsl_files()]
    if args.all_history:
        jobs += [(p, 'LS&ĐL', 5) for p in sorted(glob.glob(os.path.join(HISTORY_TSL, '*.tsl.json')))]

    recs = []
    for path, subject, grade in jobs:
        if not os.path.exists(path):
            print('MISSING %s' % path, file=sys.stderr)
            continue
        rec, _, _ = run_one(path, subject, grade, out_root, write=not args.quiet)
        recs.append(rec)
        if len(jobs) <= 6:
            print(json.dumps(rec, ensure_ascii=False, indent=1))

    summary = {
        'lessons': len(recs),
        'compilerAudit': vs.compiler_audit(),
        'familyCounts': _count(f for r in recs for f in r['familiesCompiled']),
        'lessonsWithNoFamily': sum(1 for r in recs if not r['familiesCompiled']),
        'records': recs,
    }
    path = os.path.join(cp.out_dir(), 'poc-summary.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print('\nlessons=%d  families=%s  noFamily=%d  -> %s'
          % (len(recs), summary['familyCounts'], summary['lessonsWithNoFamily'], path))
    print('compiler audit (fields each compiler read):')
    for k, v in sorted(summary['compilerAudit'].items()):
        print('  %-24s %s' % (k, v))
    return 0


def _count(it):
    out = {}
    for x in it:
        out[x] = out.get(x, 0) + 1
    return out


if __name__ == '__main__':
    raise SystemExit(main())
