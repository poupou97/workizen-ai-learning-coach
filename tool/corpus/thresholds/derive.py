#!/usr/bin/env python3
"""Derive the candidate trust policies' expected trade-offs from PRE-EXISTING evidence.

    python3 tool/corpus/thresholds/derive.py \
        --gold  poc-out/round5/lane-a3/evidence-gold-tc2-p2.jsonl \
        --audit poc-out/round5/lane-a3/evidence-audit.jsonl \
        --out   poc-out/round7/ws-t/derivation.json

Input is round 5 Lane A3's frozen evidence rows — the same rows that produced the published
trade-off curve, re-decided under trust policies instead of under guard waivers. Nothing new is
extracted, nothing is annotated, no new truth is created.

OUTPUT CARRIES NO LESSON IDENTITY. Every figure is a rate or a count, grouped by subject, role,
grade or plane. `--out` is checked against `policy.identity_leaks` before it is written, and the
writer refuses if a book id or a lesson reference appears anywhere in an admission context.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from thresholds import gate as G          # noqa: E402
from thresholds import policy as P        # noqa: E402
from thresholds import candidates as C    # noqa: E402


def load(path, plane):
    rows = [json.loads(l) for l in open(path, encoding='utf-8')]
    rows = [r for r in rows if r.get('plane') == plane]
    for r in rows:
        # `_served` is the pipeline's own decision, recomputed rather than trusted: on the gold
        # plane by re-running the unchanged gate; on the audit plane it is what actually shipped.
        r['_served'] = (G.decide(r, G.PIPELINE_GATE)[0] if plane == 'gold'
                        else bool(r.get('served_as_trusted')))
    return rows


def harm_split(rows):
    """The three-way split that a single «false trust» number hides."""
    both = sum(1 for r in rows if r.get('truth_wrong_any') and r.get('truth_teaching_critical'))
    ft_only = sum(1 for r in rows if r.get('truth_wrong_any')
                  and not r.get('truth_teaching_critical'))
    tc_only = sum(1 for r in rows if not r.get('truth_wrong_any')
                  and r.get('truth_teaching_critical'))
    return dict(ft_and_tc=both, ft_only=ft_only, tc_only=tc_only, union=both + ft_only + tc_only)


def by_key(rows, key):
    out = {}
    for r in rows:
        k = str(r.get(key))
        d = out.setdefault(k, dict(n=0, ft=0, tc=0))
        d['n'] += 1
        d['ft'] += bool(r.get('truth_wrong_any'))
        d['tc'] += bool(r.get('truth_teaching_critical'))
    for k, d in out.items():
        d['ft_rate'] = round(d['ft'] / d['n'], 4)
        d['tc_rate'] = round(d['tc'] / d['n'], 4)
        d['ft_upper95'] = round(P.wilson_upper(d['ft'], d['n']), 4)
    return dict(sorted(out.items(), key=lambda kv: -kv[1]['n']))


def group_incidence(rows, group_fields):
    """P(a group with >=1 trusted block contains >=1 error) — the child-facing translation.

    On the gold plane the only available grouping is the PAGE; a lesson spans several pages, so
    a page figure is an OPTIMISTIC proxy for a lesson figure.
    """
    groups = collections.defaultdict(lambda: dict(n=0, ft=0, tc=0))
    for r in rows:
        g = groups[tuple(r.get(f) for f in group_fields)]
        g['n'] += 1
        g['ft'] += bool(r.get('truth_wrong_any'))
        g['tc'] += bool(r.get('truth_teaching_critical'))
    tot = len(groups)
    if not tot:
        return None
    with_tc = sum(1 for g in groups.values() if g['tc'])
    with_any = sum(1 for g in groups.values() if g['tc'] or g['ft'])
    sizes = sorted(g['n'] for g in groups.values())
    return dict(groups=tot, median_trusted_blocks_per_group=sizes[len(sizes) // 2],
                mean_trusted_blocks_per_group=round(sum(sizes) / tot, 2),
                groups_with_teaching_critical=with_tc,
                p_group_has_teaching_critical=round(with_tc / tot, 4),
                p_group_has_teaching_critical_upper95=round(P.wilson_upper(with_tc, tot), 4),
                groups_with_any_harm=with_any,
                p_group_has_any_harm=round(with_any / tot, 4))


def main():
    ap = argparse.ArgumentParser(description='derive candidate trust policies (research only)')
    ap.add_argument('--gold', required=True)
    ap.add_argument('--audit', default=None)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    gold = load(a.gold, 'gold')
    served = [r for r in gold if r['_served']]
    doc = dict(
        schema='trust-calibration-derivation-v1',
        _identity_policy='no book id, lesson number or page appears in this document',
        planes={}, candidates={}, guard_free_observations={},
    )

    doc['planes']['gold'] = dict(
        source='round 5 Lane A3 frozen evidence rows, gold plane',
        caveat='54 DELIBERATELY HARD pages, not a sample. No rate here transfers to the corpus.',
        n_rows=len(gold), n_served=len(served),
        coverage=round(len(served) / len(gold), 4),
        harm_split=harm_split(served),
        ft_rate=round(sum(1 for r in served if r.get('truth_wrong_any')) / len(served), 4),
        tc_rate=round(sum(1 for r in served
                          if r.get('truth_teaching_critical')) / len(served), 4),
        by_subject=by_key(served, 'subject'),
        by_role=by_key(served, 'role_value'),
        teaching_critical_mechanisms=dict(collections.Counter(
            ('digit_corruption' if r.get('truth_digits_wrong') else
             'nonquestion_served_as_question' if r.get('truth_as_question') else 'other')
            for r in served if r.get('truth_teaching_critical'))),
    )

    if a.audit:
        for src in ('round3-484', 'legacy-b1-new', 'legacy-b1-old'):
            rows = [r for r in load(a.audit, 'audit') if r.get('audit_source') == src]
            if not rows:
                continue
            srv = [r for r in rows if r['_served']]
            doc['planes'][src] = dict(
                source='round 5 Lane A3 frozen evidence rows, audit plane',
                n_rows=len(rows), n_served=len(srv),
                ft_rate=round(sum(1 for r in srv if r.get('truth_wrong_any')) / len(srv), 4),
                tc_rate=round(sum(1 for r in srv
                                  if r.get('truth_teaching_critical')) / len(srv), 4),
                harm_split=harm_split(srv),
                signals_present={f: sum(1 for r in srv if r.get(f) is not None)
                                 for f in ('role_confidence', 'text_sim', 'layout_family',
                                           'has_math', 'multi_line')},
                note='NOT POOLED with any other plane (D5).')

    for name, pol in C.CANDIDATES.items():
        m = P.evaluate(gold, pol)
        adm = [r for r in served if P.admits(r, pol)[0]]
        m['harm_split'] = harm_split(adm)
        m['by_role'] = by_key(adm, 'role_value')
        m['by_subject'] = by_key(adm, 'subject')
        m['page_incidence'] = group_incidence(adm, ('book', 'page'))
        m['bound'] = pol.get('bound')
        m['evaluated_on'] = 'gold plane (54 hard pages) — NOT a corpus estimate'
        doc['candidates'][name] = m

    doc['guard_free_observations'] = dict(
        role_confidence_floor_is_not_a_safety_dial=(
            'raising the floor to 0.70 lowers false trust 0.0734 -> 0.0593 and RAISES the '
            'teaching-critical rate 0.0339 -> 0.0407, while removing every block of continuous '
            'prose (the `body` role carries the 0.60 «could not tell» confidence).'),
        teaching_critical_is_not_a_subset_of_false_trust=(
            'on the gold plane the two sets overlap but neither contains the other; on the audit '
            'plane teaching-critical is a strict subset. The two planes do not even agree on the '
            'SET RELATION, because they use different definitions of «wrong».'),
        no_single_false_trust_number_exists=(
            'the same quantity measures between 0.073 and 0.727 across the five populations this '
            'repository has annotated. A bound quoted without its plane, pipeline version and '
            'population is not a bound.'),
    )

    leaks = P.identity_leaks(doc)
    if leaks:
        raise SystemExit(f'REFUSING TO WRITE: identity leak in admission context: {leaks[:3]}')
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(doc, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'wrote {a.out}')
    for name, m in doc['candidates'].items():
        print(f"  {name:26s} trusted={m['n_trusted']:4d} "
              f"ft={m['ft_rate']} (<= {m['ft_upper95']})  tc={m['tc_rate']} (<= {m['tc_upper95']})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
