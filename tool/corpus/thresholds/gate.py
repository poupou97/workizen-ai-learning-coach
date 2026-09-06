#!/usr/bin/env python3
"""A candidate trust gate, and what it would cost — evaluated over evidence rows.

A GATE is a declarative predicate over the signals a block carries. It is deliberately
dumb: it cannot look at the block's text, cannot repair anything and cannot learn. It only
decides SERVE or WITHHOLD, so that the cost of a decision is attributable to the decision
and not to a model.

    gate = {
      "deny_guards":            [...]  # guards that WITHHOLD. Any guard NOT listed is waived.
      "min_text_sim":           float  # agreement.text_sim (0..100); null = no requirement
      "min_ocr_conf":           float  # 0..1
      "min_role_confidence":    float  # 0..1
      "max_tone_disagreements": int
      "allow_roles":            [...]  # null = every role; otherwise a whitelist of fine roles
      "deny_roles":             [...]
      "require_order_ok":       bool   # agreement.order_ok must be true
      "deny_where":             [...]  # generic predicates [{"field","op","value"}] so a gate
                                       # can be expressed over any recorded signal (subject,
                                       # layout family, has_math …) without new code
      "on_missing_signal":      "deny" | "allow"   # fail-closed (default) or fail-open
    }

`evaluate()` reports, for one gate over one plane:

    coverage · correct served · wrong served · teaching-critical served · withheld ·
    false withheld (clean content refused) · safe rejections ·
    and, against the pipeline's own decision as the baseline:
    restored · restore precision · newly withheld (and what it cost / bought).

NOTHING in this module ranks gates, scores them, or picks one. `evaluate` returns numbers.
"""
import math

DEFAULT_GATE = dict(deny_guards=None, min_text_sim=None, min_ocr_conf=None,
                    min_role_confidence=None, max_tone_disagreements=None,
                    allow_roles=None, deny_roles=None, require_order_ok=False,
                    deny_where=None, on_missing_signal='deny')

OPS = {
    'eq': lambda a, b: a == b,
    'ne': lambda a, b: a != b,
    'in': lambda a, b: a in b,
    'not_in': lambda a, b: a not in b,
    'gte': lambda a, b: a is not None and a >= b,
    'lte': lambda a, b: a is not None and a <= b,
    'gt': lambda a, b: a is not None and a > b,
    'lt': lambda a, b: a is not None and a < b,
    'is_true': lambda a, b: bool(a) is True,
    'is_false': lambda a, b: bool(a) is False,
}

# Every guard the round-4/5 pipeline can raise. A gate that lists all of them in
# `deny_guards` and sets no numeric floor reproduces the pipeline's own decision exactly.
ALL_GUARDS = ('agree_text', 'agree_order', 'agree_numbers', 'agree_tones', 'role_conflict',
              'math_guard', 'unit_guard', 'chem_guard', 'empty_block', 'furniture',
              'box_boundary', 'figure_dependent', 'answer_leak', 'teacher_text',
              'page_feature:color_heavy', 'page_feature:diagram', 'figure_text',
              'low_ocr_conf', 'line_structure', 'empty')

PIPELINE_GATE = dict(DEFAULT_GATE, deny_guards=list(ALL_GUARDS))


def normalise(gate):
    g = dict(DEFAULT_GATE)
    g.update(gate or {})
    if g['deny_guards'] is None:
        g['deny_guards'] = list(ALL_GUARDS)
    g['deny_guards'] = set(g['deny_guards'])
    g['allow_roles'] = set(g['allow_roles']) if g['allow_roles'] else None
    g['deny_roles'] = set(g['deny_roles'] or ())
    return g


def _below(value, floor, missing_denies):
    """True when the signal blocks serving."""
    if floor is None:
        return False
    if value is None:
        return missing_denies
    return value < floor


def decide(row, gate):
    """(served: bool, reasons: [str]) — why this gate withholds this block."""
    g = gate if isinstance(gate.get('deny_guards'), set) else normalise(gate)
    miss = g['on_missing_signal'] == 'deny'
    why = []
    if not row.get('matched', True):
        why.append('unmatched')          # no pipeline block exists: nothing can be served
    for x in row.get('guards') or ():
        if x in g['deny_guards']:
            why.append(f'guard:{x}')
    if _below(row.get('text_sim'), g['min_text_sim'], miss):
        why.append('text_sim')
    if _below(row.get('ocr_conf'), g['min_ocr_conf'], miss):
        why.append('ocr_conf')
    if _below(row.get('role_confidence'), g['min_role_confidence'], miss):
        why.append('role_confidence')
    if g['max_tone_disagreements'] is not None:
        td = row.get('tone_disagreements')
        if td is None:
            if miss:
                why.append('tone_disagreements')
        elif td > g['max_tone_disagreements']:
            why.append('tone_disagreements')
    rv = row.get('role_value')
    if g['allow_roles'] is not None and rv not in g['allow_roles']:
        why.append('role_not_allowed')
    if rv in g['deny_roles']:
        why.append('role_denied')
    if g['require_order_ok'] and row.get('order_ok') is False:
        why.append('order_ok')
    for i, p in enumerate(g['deny_where'] or ()):
        op = OPS.get(p.get('op'))
        if op is None:
            raise ValueError(f"unknown deny_where op {p.get('op')!r}")
        if op(row.get(p['field']), p.get('value')):
            why.append(f"where:{p['field']}.{p['op']}")
    return (not why), why


def wilson(k, n, z=1.96):
    if not n:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 4), round((c + h) / d, 4))


def evaluate(rows, gate, baseline='pipeline_trusted'):
    """Counts for one gate over `rows`. `baseline` names the row field holding the
    pipeline's own decision; restored / newly-withheld are measured against it."""
    g = normalise(gate)
    n = len(rows)
    served = wrong = correct = tc = 0
    withheld = withheld_clean = withheld_wrong = 0
    restored = restored_clean = restored_wrong = 0
    new_wh = new_wh_clean = new_wh_wrong = 0
    why_counts = {}
    for r in rows:
        ok, why = decide(r, g)
        base = bool(r.get(baseline))
        bad = bool(r.get('truth_wrong_any'))
        for w in why:
            why_counts[w] = why_counts.get(w, 0) + 1
        if ok:
            served += 1
            if bad:
                wrong += 1
            else:
                correct += 1
            if r.get('truth_teaching_critical'):
                tc += 1
            if not base:
                restored += 1
                if bad:
                    restored_wrong += 1
                else:
                    restored_clean += 1
        else:
            withheld += 1
            if r.get('matched', True):
                if bad:
                    withheld_wrong += 1
                else:
                    withheld_clean += 1
            if base:
                new_wh += 1
                if bad:
                    new_wh_wrong += 1
                else:
                    new_wh_clean += 1
    lo, hi = wilson(wrong, served)
    return dict(
        n=n, served=served, withheld=withheld,
        coverage=round(served / n, 4) if n else None,
        served_correct=correct, served_wrong=wrong,
        ftr=round(wrong / served, 4) if served else None,
        ftr_ci95=[lo, hi],
        served_teaching_critical=tc,
        tc_rate=round(tc / served, 4) if served else None,
        withheld_clean=withheld_clean, withheld_wrong=withheld_wrong,
        over_withhold_rate=round(withheld_clean / (withheld_clean + withheld_wrong), 4)
        if (withheld_clean + withheld_wrong) else None,
        restored=restored, restored_clean=restored_clean, restored_wrong=restored_wrong,
        restore_precision=round(restored_clean / restored, 4) if restored else None,
        newly_withheld=new_wh, newly_withheld_clean=new_wh_clean, newly_withheld_wrong=new_wh_wrong,
        withhold_reasons=dict(sorted(why_counts.items(), key=lambda kv: -kv[1])))
