#!/usr/bin/env python3
"""Run the trust-gate sensitivity analysis over an evidence file.

    python3 tool/corpus/thresholds/run.py \
        --evidence  poc-out/round5/lane-a3/evidence-gold-tc2-p2.jsonl \
        --scenarios THRESHOLDS.example.json \
        --out-dir   poc-out/round5/lane-a3/gold

Writes: guard-cost.{json,md} · scenarios.{json,md} · sweeps.json · frontier.json ·
curve-coverage-vs-ftr.svg · curve-correct-vs-wrong.svg · summary.md

This tool NEVER writes THRESHOLDS.json and never names a recommended gate. Every scenario
it evaluates is an illustration of a question, not an answer to it.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thresholds import gate as G      # noqa: E402
from thresholds import sweep as S     # noqa: E402

# Guards whose purpose is FIDELITY — "is the served string what the page prints?". Waiving
# one is a real coverage/accuracy trade and belongs on the trade-off curve.
FIDELITY_GUARDS = ['agree_tones', 'agree_text', 'agree_order', 'agree_numbers',
                   'math_guard', 'unit_guard', 'chem_guard', 'low_ocr_conf', 'line_structure']
# Guards whose purpose is POLICY — "may a child be shown this at all?". The gold plane can
# only tell you whether such a block is a faithful copy; it cannot tell you whether serving
# it is allowed. Waiving one is NOT a fidelity trade and the curve must not be read as if it were.
POLICY_GUARDS = ['teacher_text', 'answer_leak', 'figure_text', 'figure_dependent',
                 'page_feature:diagram', 'page_feature:color_heavy', 'box_boundary', 'role_conflict']
# Guards that are structural: waiving them serves nothing (an empty block, a page number).
STRUCTURAL_GUARDS = ['empty_block', 'furniture', 'empty']

HEAD = ('name', 'coverage', 'served', 'served_correct', 'served_wrong', 'ftr',
        'served_teaching_critical', 'withheld', 'withheld_clean', 'restored',
        'restored_clean', 'restore_precision', 'newly_withheld', 'newly_withheld_wrong')


def table(recs):
    L = ['| ' + ' | '.join(h.replace('_', ' ') for h in HEAD) + ' |',
         '|' + '---|' * len(HEAD)]
    for r in recs:
        L.append('| ' + ' | '.join('—' if r.get(h) is None else str(r.get(h)) for h in HEAD) + ' |')
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser(description='trust-gate sensitivity analysis (research only)')
    ap.add_argument('--evidence', required=True)
    ap.add_argument('--scenarios', default=None, help='THRESHOLDS.example.json (illustrations)')
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--plane', default='gold', choices=('gold', 'audit'))
    ap.add_argument('--filter', action='append', default=[],
                    help='FIELD=VALUE — keep only matching rows. Populations are never pooled '
                         'across audits (D5): use --filter audit_source=... per sample.')
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    rows = [json.loads(l) for l in open(a.evidence)]
    rows = [r for r in rows if r.get('plane') == a.plane]
    for f in a.filter:
        k, _, v = f.partition('=')
        rows = [r for r in rows if str(r.get(k)) == v]
    if not rows:
        sys.exit(f'no {a.plane}-plane rows in {a.evidence} matching {a.filter}')

    base = G.evaluate(rows, G.PIPELINE_GATE)
    base['name'] = 'pipeline-today (reference, not a scenario)'

    # ---- what each guard costs on its own
    gc = S.guard_cost(rows)
    json.dump(gc, open(f'{a.out_dir}/guard-cost.json', 'w'), ensure_ascii=False, indent=1)
    gl = ['# What each guard refuses on its own (sole reason for withholding)', '',
          f'Plane `{a.plane}` · {len(rows)} evidence rows. "sole" = this guard fired and no other '
          'denying guard did, so the block is withheld *because of this guard*. "clean" / "wrong" '
          'are measured against the gold, i.e. FIDELITY — a clean block may still be one a child '
          'must not be shown (see the policy guards).', '',
          '| guard | class | fires | sole reason | sole & clean | sole & wrong | clean share |',
          '|---|---|---|---|---|---|---|']
    for k, v in sorted(gc.items(), key=lambda kv: -kv[1]['sole_clean']):
        if not v['fires']:
            continue
        cls = ('fidelity' if k in FIDELITY_GUARDS else
               'policy' if k in POLICY_GUARDS else
               'structural' if k in STRUCTURAL_GUARDS else 'other')
        gl.append(f"| `{k}` | {cls} | {v['fires']} | {v['sole_reason']} | {v['sole_clean']} | "
                  f"{v['sole_wrong']} | {'—' if v['sole_clean_share'] is None else v['sole_clean_share']} |")
    open(f'{a.out_dir}/guard-cost.md', 'w').write('\n'.join(gl) + '\n')

    # ---- named illustrative scenarios
    scen = []
    if a.scenarios and os.path.exists(a.scenarios):
        doc = json.load(open(a.scenarios))
        key = 'scenarios' if a.plane == 'gold' else 'audit_plane_scenarios'
        for s in doc.get(key, []):
            m = G.evaluate(rows, s.get('gate') or {})
            m['name'] = s['name']
            m['illustrates'] = s.get('illustrates')
            m['gate'] = s.get('gate')
            scen.append(m)
    json.dump(dict(baseline=base, scenarios=scen), open(f'{a.out_dir}/scenarios.json', 'w'),
              ensure_ascii=False, indent=1)

    # ---- sweeps
    def _fires_first(names):
        return [n for n in sorted(names, key=lambda k: -gc.get(k, {}).get('sole_clean', 0))
                if gc.get(n, {}).get('fires')]

    fid_order = _fires_first(FIDELITY_GUARDS)
    pol_order = _fires_first(POLICY_GUARDS)
    sweeps = {}
    sweeps['fidelity_waive'] = S.sweep_guards(rows, G.PIPELINE_GATE, fid_order, 'waive fidelity guards')
    sweeps['policy_waive'] = S.sweep_guards(rows, G.PIPELINE_GATE, pol_order, 'waive policy guards')
    sweeps['all_waive'] = S.sweep_guards(rows, G.PIPELINE_GATE, fid_order + pol_order, 'waive fidelity then policy')
    open_gate = dict(G.PIPELINE_GATE, deny_guards=STRUCTURAL_GUARDS)
    sweeps['min_text_sim_on_open'] = S.sweep_axis(rows, open_gate, 'min_text_sim',
                                                  [None, 50, 70, 80, 90, 95, 98, 99, 99.5, 100])
    sweeps['min_text_sim_on_pipeline'] = S.sweep_axis(rows, G.PIPELINE_GATE, 'min_text_sim',
                                                      [None, 50, 70, 80, 90, 95, 98, 99, 99.5, 100])
    sweeps['min_role_confidence'] = S.sweep_axis(rows, G.PIPELINE_GATE, 'min_role_confidence',
                                                 [None, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.93, 0.95, 0.97])
    sweeps['min_ocr_conf'] = S.sweep_axis(rows, G.PIPELINE_GATE, 'min_ocr_conf',
                                          [None, 0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 1.0])
    json.dump(sweeps, open(f'{a.out_dir}/sweeps.json', 'w'), ensure_ascii=False, indent=1)

    allpts = [base] + scen + [p for ps in sweeps.values() for p in ps]
    fr = S.frontier(allpts)
    json.dump(fr, open(f'{a.out_dir}/frontier.json', 'w'), ensure_ascii=False, indent=1)

    # ---- charts
    colours = ['#2f6f9f', '#c2632c', '#4c8a4c', '#8a4c8a', '#a8a02c']
    series = [('waive fidelity guards', sweeps['fidelity_waive'], colours[0]),
              ('waive policy guards', sweeps['policy_waive'], colours[1]),
              ('text-agreement floor, guards off', sweeps['min_text_sim_on_open'], colours[2]),
              ('role-confidence floor, guards on', sweeps['min_role_confidence'], colours[3]),
              ('pipeline today', [base], '#000000')]
    open(f'{a.out_dir}/curve-coverage-vs-ftr.svg', 'w').write(
        S.svg_curve(series, title='Trust-gate trade-off — coverage vs false-trust rate (gold plane, 54 pages / 643 learning blocks)'))
    open(f'{a.out_dir}/curve-correct-vs-wrong.svg', 'w').write(
        S.svg_curve(series, xkey='served_correct', ykey='served_wrong',
                    title='Trust-gate trade-off — correct blocks served vs wrong blocks served',
                    xlabel='correct blocks served', ylabel='wrong blocks served'))

    # ---- summary
    L = ['# Trust-gate sensitivity — computed output (no gate is chosen here)', '',
         f'Evidence: `{os.path.basename(a.evidence)}` · plane `{a.plane}` · {len(rows)} rows'
         + (f" · filter `{'; '.join(a.filter)}`" if a.filter else '') + '.', '',
         '## Reference point — the gate the pipeline implements today', '', table([base]), '',
         '## Named ILLUSTRATIVE scenarios (examples, never recommendations)', '',
         table(scen) if scen else '_no scenario file supplied_', '',
         '## Sweeps', '']
    for k, pts in sweeps.items():
        for p in pts:
            p['name'] = f"{k}={p.get('waived', p.get('value'))}"
        L += [f'### `{k}`', '', table(pts), '']
    L += ['## Pareto frontier (coverage up, wrong-served down)', '', table(fr), '',
          '_A point on this frontier is not a recommendation. It only means no other gate '
          'measured here serves at least as much content with no more wrong blocks._', '']
    open(f'{a.out_dir}/summary.md', 'w').write('\n'.join(L) + '\n')
    print(f'baseline coverage {base["coverage"]} · wrong {base["served_wrong"]} · ftr {base["ftr"]}')
    print(f'{len(scen)} scenarios · {sum(len(v) for v in sweeps.values())} swept gates · '
          f'{len(fr)} on the frontier → {a.out_dir}')


if __name__ == '__main__':
    main()
