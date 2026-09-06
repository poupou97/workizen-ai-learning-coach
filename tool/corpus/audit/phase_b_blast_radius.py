#!/usr/bin/env python3
"""PHASE B — blast radius of a role-layer change on an UNLABELLED plane.

A rule measured only where truth exists is measured only where it was derived. This rebuilds an
arbitrary SDM plane and writes one record per PIPELINE BLOCK — id, role, coarse role, trust
status — so two checkouts can be diffed and the question "how much does this rule actually
touch, and does it withdraw anything from a learner" is answered on a population far larger than
the gold set. No gold is read and no correctness is claimed: this measures REACH, not accuracy.

D4: ids, roles and statuses only. No served or printed string is written.

ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION: an empty plane, or a plane on which the rule under
test can fire nowhere, is reported as UNVERIFIED and exits non-zero rather than as a clean zero.
"""
import argparse
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HERE)
sys.path.insert(0, CORPUS)

import tc2_sdm  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description='Phase B blast radius (per-block, unlabelled)')
    ap.add_argument('--sdm', help='SDM directory naming the pages to rebuild')
    ap.add_argument('--from-raw', help='raw-candidate directory; every page with a docling-ocrmac raw '
                                       'is rebuilt (a far larger plane than any SDM run)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--label', default='arm')
    ap.add_argument('--min-pages', type=int, default=50)
    ns = ap.parse_args()

    if ns.from_raw:
        pages = []
        for f in sorted(glob.glob(os.path.join(ns.from_raw, 'docling-ocrmac', '*-p[0-9][0-9][0-9].json'))):
            stem = os.path.basename(f)[:-5]
            pages.append((stem[:stem.rindex('-p')], int(stem[stem.rindex('-p') + 2:])))
    elif ns.sdm:
        pages = []
        for f in sorted(glob.glob(os.path.join(ns.sdm, '*', 'p*.sdm.json'))):
            d = json.load(open(f))
            pages.append((d['book'], d['page']))
    else:
        raise SystemExit('UNVERIFIED: give --sdm or --from-raw; there is nothing to measure')
    files = pages
    if len(files) < ns.min_pages:
        raise SystemExit(f'UNVERIFIED: {len(files)} pages under --sdm, fewer than the {ns.min_pages} '
                         f'this measurement declares adequate. A reach measured over a handful of '
                         f'pages cannot show that a rule does not over-fire.')
    T = collections.Counter()
    with open(ns.out, 'w') as fh:
        for book, page in files:
            pg = tc2_sdm.build_page(book, page, pipeline='tc2-p2')
            if not pg or not pg.get('blocks'):
                T['pages_unbuildable'] += 1   # counted, never silently dropped
                continue
            T['pages_built'] += 1
            for b in pg['blocks']:
                r = b['role']
                fh.write(json.dumps(dict(book=book, page=page, id=b['id'],
                                         role=r['value'], coarse=r['coarse'],
                                         status=b['trust']['status']), sort_keys=True) + '\n')
                T['blocks'] += 1
                T[f"role:{r['value']}"] += 1
                T[f"status:{b['trust']['status']}"] += 1
    if T['pages_built'] < ns.min_pages:
        raise SystemExit(f'UNVERIFIED: only {T["pages_built"]} of {len(files)} pages rebuilt '
                         f'({T["pages_unbuildable"]} unbuildable); the plane is not adequate.')
    print(f"[{ns.label}] pages={len(files)} built={T['pages_built']} "
          f"unbuildable={T['pages_unbuildable']} blocks={T['blocks']} "
          f"question={T['role:question']} trusted={T['status:TRUSTED']} withheld={T['status:WITHHELD']}")


if __name__ == '__main__':
    main()
