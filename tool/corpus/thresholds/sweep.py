#!/usr/bin/env python3
"""Sweep candidate gates into a TRADE-OFF CURVE.

The Founder asked for a curve, not a number. This module produces the curve three ways and
never marks a point on it:

  · `sweep_axis`    — move ONE numeric knob (text agreement, OCR confidence, role
                      confidence) and watch coverage and wrong-served move together.
  · `sweep_guards`  — waive guards one at a time, cumulatively, in a stated order. This is
                      the axis that actually moves on today's pipeline, because the pipeline
                      has no numeric threshold at all: its gate IS its guard set.
  · `frontier`      — the Pareto-optimal points of any set of evaluated gates, on
                      (coverage up, wrong-served down). A gate off the frontier is dominated:
                      some other gate serves at least as much and is wrong no more often.

`guard_cost` reports, per guard, what that guard alone is refusing — how many clean blocks
and how many genuinely wrong ones. It is the honest input to any waiving decision, and it is
descriptive: it says what a guard costs, never whether the cost is worth paying.
"""
from . import gate as G


def guard_cost(rows, baseline_gate=None):
    """Per guard: how many blocks does it withhold *on its own* (no other deny-guard fires),
    and of those how many are clean (the price) vs wrong (the protection)."""
    base = G.normalise(baseline_gate or G.PIPELINE_GATE)
    out = {}
    for guard in sorted(base['deny_guards']):
        alone = clean = bad = 0
        for r in rows:
            gs = set(r.get('guards') or ())
            if guard not in gs:
                continue
            if gs & (base['deny_guards'] - {guard}):
                continue          # some other denying guard also fires: not this guard's doing
            if not r.get('matched', True):
                continue
            alone += 1
            if r.get('truth_wrong_any'):
                bad += 1
            else:
                clean += 1
        total = sum(1 for r in rows if guard in set(r.get('guards') or ()))
        out[guard] = dict(fires=total, sole_reason=alone, sole_clean=clean, sole_wrong=bad,
                          sole_clean_share=round(clean / alone, 4) if alone else None)
    return out


def sweep_axis(rows, base_gate, key, values, label=None):
    pts = []
    for v in values:
        g = dict(base_gate)
        g[key] = v
        m = G.evaluate(rows, g)
        m['axis'] = label or key
        m['value'] = v
        m['gate'] = {k: (sorted(x) if isinstance(x, (set,)) else x) for k, x in g.items()}
        pts.append(m)
    return pts


def sweep_guards(rows, base_gate, order, label='waive_guards'):
    """Cumulatively waive guards in `order`, starting from `base_gate`'s deny set."""
    g0 = G.normalise(base_gate)
    deny = set(g0['deny_guards'])
    pts = []
    waived = []
    for step in [None] + list(order):
        if step is not None:
            deny.discard(step)
            waived.append(step)
        g = dict(base_gate)
        g['deny_guards'] = sorted(deny)
        m = G.evaluate(rows, g)
        m['axis'] = label
        m['value'] = len(waived)
        m['waived'] = list(waived)
        m['gate'] = dict(g)
        pts.append(m)
    return pts


def frontier(points):
    """Pareto-optimal points on (coverage MAX, served_wrong MIN)."""
    out = []
    for p in points:
        dominated = any(q is not p and q['coverage'] >= p['coverage'] and q['served_wrong'] <= p['served_wrong']
                        and (q['coverage'] > p['coverage'] or q['served_wrong'] < p['served_wrong'])
                        for q in points)
        if not dominated:
            out.append(p)
    return sorted(out, key=lambda p: p['coverage'])


# ------------------------------------------------------------------ rendering
def svg_curve(series, width=760, height=440, title='trade-off curve',
              xkey='coverage', ykey='ftr', xlabel='coverage (served / learning blocks)',
              ylabel='false-trust rate among served'):
    """A small dependency-free SVG scatter/line chart. Deliberately plain: this is evidence,
    not a dashboard. `series` = [(name, [points], colour), ...]."""
    pad_l, pad_r, pad_t, pad_b = 66, 190, 34, 52
    xs = [p[xkey] for _, ps, _ in series for p in ps if p.get(xkey) is not None]
    ys = [p[ykey] for _, ps, _ in series for p in ps if p.get(ykey) is not None]
    if not xs or not ys:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"></svg>'
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    x0, x1 = (x0 - 0.02, x1 + 0.02)
    span = (y1 - y0) or 1.0
    y0, y1 = (max(0.0, y0 - 0.06 * span), y1 + 0.06 * span)

    def px(v):
        return pad_l + (v - x0) / ((x1 - x0) or 1) * (width - pad_l - pad_r)

    def py(v):
        return height - pad_b - (v - y0) / ((y1 - y0) or 1) * (height - pad_t - pad_b)

    L = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
         f'viewBox="0 0 {width} {height}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11">',
         f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
         f'<text x="{pad_l}" y="20" font-size="13" font-weight="600" fill="#111">{title}</text>']
    for i in range(5):
        v = y0 + (y1 - y0) * i / 4
        y = py(v)
        L.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width-pad_r}" y2="{y:.1f}" stroke="#e6e6e6"/>')
        L.append(f'<text x="{pad_l-8}" y="{y+3:.1f}" text-anchor="end" fill="#555">{v:.3f}</text>')
    for i in range(5):
        v = x0 + (x1 - x0) * i / 4
        x = px(v)
        L.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{height-pad_b}" stroke="#f2f2f2"/>')
        L.append(f'<text x="{x:.1f}" y="{height-pad_b+16}" text-anchor="middle" fill="#555">{v:.3f}</text>')
    L.append(f'<text x="{(pad_l+width-pad_r)/2:.0f}" y="{height-12}" text-anchor="middle" fill="#333">{xlabel}</text>')
    L.append(f'<text x="16" y="{(pad_t+height-pad_b)/2:.0f}" text-anchor="middle" fill="#333" '
             f'transform="rotate(-90 16 {(pad_t+height-pad_b)/2:.0f})">{ylabel}</text>')
    ly = pad_t + 6
    for name, ps, colour in series:
        ps = [p for p in ps if p.get(xkey) is not None and p.get(ykey) is not None]
        ps = sorted(ps, key=lambda p: p[xkey])
        if len(ps) > 1:
            d = ' '.join(f'{"M" if i == 0 else "L"}{px(p[xkey]):.1f},{py(p[ykey]):.1f}' for i, p in enumerate(ps))
            L.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="1.6" opacity="0.85"/>')
        for p in ps:
            L.append(f'<circle cx="{px(p[xkey]):.1f}" cy="{py(p[ykey]):.1f}" r="3.2" fill="{colour}" opacity="0.9"/>')
        L.append(f'<rect x="{width-pad_r+8}" y="{ly-8}" width="10" height="10" fill="{colour}"/>')
        L.append(f'<text x="{width-pad_r+24}" y="{ly+1}" fill="#333">{name}</text>')
        ly += 18
    L.append('</svg>')
    return '\n'.join(L)
