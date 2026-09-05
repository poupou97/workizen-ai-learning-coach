#!/usr/bin/env python3
"""WAL-210 item 10a (Founder D3) — FALSE-TRUST AUDIT SCORER. Reads the annotated sheet written by
ft_audit_sample.py and reports the FIVE rates SEPARATELY, each with a Wilson 95 % interval and the
denominators the D5 convention requires. Decides nothing: acceptance thresholds are proposed in
docs/research/FALSE-TRUST-AUDIT-PROTOCOL.md and set by the Founder.

Rates (a rate = WRONG / (OK + WRONG) over judged rows; UNSURE and NA are reported beside it, never
folded into either side):
  display-only source fidelity     per served block  — served text ≠ page text
  teaching-critical fidelity       per served block  — numbers / formulas / terms / negations wrong
  role fidelity                    per served block  — served in the wrong role
  lesson attachment                per ACTIVITY      — attached to the wrong lesson
  false trust (derived)            per served block  — any of the four above WRONG (attachment via the
                                                       block's activity); OK only when every judged
                                                       criterion is OK and at least one was judged
  false trust (reviewer)           per served block  — the reviewer's explicit verdict, reported beside
                                                       the derived one

Withheld rows (TSL blocks with status ≠ TRUSTED) are never in a served denominator; they are counted
as "withheld, reviewed" so a reviewer's `notes` on them can be read as safe-rejection audits.

Sample size for a "< 1 % false trust" claim — the formula the protocol uses:
  Wilson upper bound  U(k, n) = (p̂ + z²/2n + z·sqrt(p̂(1−p̂)/n + z²/4n²)) / (1 + z²/n),  p̂ = k/n, z = 1.96
  with k = 0 observed false-trusted blocks:  U(0, n) = z²/(n + z²) < 0.01  ⇔  n > 99·z² = 380.3  ⇒  n ≥ 381
  exact (Clopper–Pearson) with k = 0:        (1 − 0.01)^n ≤ 0.05  ⇒  n ≥ ln 0.05 / ln 0.99 = 298.1  ⇒  n ≥ 299
  the table printed below gives the smallest n for k = 0 … 5 under both bounds.

Usage:
  python3 tool/corpus/ft_audit_score.py poc-out/b-lane/ft-audit/sample-20260905.jsonl [--md out.md] [--json out.json]
  python3 tool/corpus/ft_audit_score.py --from-gold [--gold-dir tool/corpus/tc_gold] [--pipeline tc2-p1]
      validation mode: builds rows from tc_score.score() on the TC-v2 gold pages (page-level trusted /
      false-trusted counts, block ids from wrong_examples where listed) and must reproduce
      poc-out/trusted-corpus/tc-v2/tc2-p1/metrics/gold-scores.json (all 50/439 = 0.1139, science 19/190).
"""
import argparse
import collections
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('TC_ROOT', os.getcwd())
Z = 1.959963984540054
BLOCK_CRITERIA = ('display_fidelity', 'teaching_critical_fidelity', 'role_fidelity')
SCIENCE = {'04-sgk-khoa-hoc-4', '05-sgk-khoa-hoc-5', '06-sgk-khoa-hoc-tu-nhien-6', '07-sgk-khoa-hoc-tu-nhien-7', '08-sgk-khoa-hoc-tu-nhien-8', '09-sgk-khoa-hoc-tu-nhien-9'}
SCIENCE_ALL = SCIENCE | {b.replace('-sgk-', '-sgv-') for b in SCIENCE}


# ---------------------------------------------------------------- statistics
def wilson(k, n, z=Z):
    if n <= 0:
        return None, None, None
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return p, max(0.0, (centre - half) / denom), min(1.0, (centre + half) / denom)


def _binom_cdf(k, n, p):
    """P[X ≤ k] for X ~ Bin(n, p), log-space, no scipy."""
    if p <= 0:
        return 1.0
    if p >= 1:
        return 0.0 if k < n else 1.0
    total = 0.0
    lp, lq = math.log(p), math.log(1 - p)
    for i in range(0, k + 1):
        total += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq)
    return min(1.0, total)


def clopper_pearson_upper(k, n, alpha=0.05):
    """One-sided exact upper bound: smallest p with P[X ≤ k | p] ≤ alpha (bisection)."""
    if n <= 0:
        return None
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _binom_cdf(k, n, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


def n_for_upper(k, target=0.01, method='wilson', n_max=20000):
    f = (lambda n: wilson(k, n)[2]) if method == 'wilson' else (lambda n: clopper_pearson_upper(k, n))
    n = max(k + 1, 1)
    while n <= n_max:
        u = f(n)
        if u is not None and u < target:
            return n
        n += 1
    return None


def sample_size_table(target=0.01):
    rows = []
    for k in range(0, 6):
        rows.append(dict(k=k, wilson=n_for_upper(k, target, 'wilson'), exact=n_for_upper(k, target, 'exact')))
    return rows


# ---------------------------------------------------------------- rates
def _rate(rows, field):
    c = collections.Counter((r.get(field) or '').strip().upper() or 'UNJUDGED' for r in rows)
    k, ok = c.get('WRONG', 0), c.get('OK', 0)
    n = k + ok
    p, lo, hi = wilson(k, n) if n else (None, None, None)
    return dict(wrong=k, ok=ok, judged=n, unsure=c.get('UNSURE', 0), na=c.get('NA', 0), unjudged=c.get('UNJUDGED', 0), rate=p, lo=lo, hi=hi, sampled=len(rows))


def derived_false_trust(row, attach_by_activity, criteria=BLOCK_CRITERIA):
    vals = [(row.get(f) or '').strip().upper() for f in criteria]
    att = (attach_by_activity.get(row.get('activityId')) or '').strip().upper()
    if 'WRONG' in vals or att == 'WRONG':
        return 'WRONG'
    judged = [v for v in vals + [att] if v in ('OK', 'WRONG')]
    if not judged:
        return ''
    if any(v == 'UNSURE' for v in vals + [att]):
        return 'UNSURE'
    return 'OK'


# Round 3 (A2): reading order is a fifth block criterion (CTE class «order changes meaning»); the
# derived false trust INCLUDES it. The protocol's original four-criterion derivation is reported
# beside it as `false_trust_derived4` for comparability.
BLOCK_CRITERIA_R3 = BLOCK_CRITERIA + ('reading_order',)


def _partition(row):
    """Split a derived-WRONG row into ONE class: teaching-critical › display-only › other (role /
    attachment / order). Returns '' when the row is not derived-WRONG."""
    if row.get('_false_trust_derived') != 'WRONG':
        return ''
    if (row.get('teaching_critical_fidelity') or '').strip().upper() == 'WRONG':
        return 'teaching_critical'
    d = (row.get('display_fidelity') or '').strip().upper()
    others = [(row.get(f) or '').strip().upper() for f in ('role_fidelity', 'reading_order')] + [row.get('_att', '')]
    if d == 'WRONG' and all(v in ('OK', 'NA', '') for v in others):
        return 'display_only'
    return 'other'


def _rate_from(rows, pred_wrong, judged_pred):
    """Rate whose numerator is `pred_wrong(row)` over rows where `judged_pred(row)` holds."""
    judged = [r for r in rows if judged_pred(r)]
    k = sum(1 for r in judged if pred_wrong(r))
    n = len(judged)
    p, lo, hi = wilson(k, n) if n else (None, None, None)
    return dict(wrong=k, ok=n - k, judged=n, unsure=sum(1 for r in rows if r.get('_false_trust_derived') == 'UNSURE'),
                na=0, unjudged=len(rows) - n - sum(1 for r in rows if r.get('_false_trust_derived') == 'UNSURE'), rate=p, lo=lo, hi=hi, sampled=len(rows))


def score_rows(rows, group_key=lambda r: r.get('family')):
    served = [r for r in rows if r.get('servedAsTrusted', True)]
    withheld = [r for r in rows if not r.get('servedAsTrusted', True)]
    attach_by_activity = {}
    for r in rows:
        v = (r.get('lesson_attachment') or '').strip().upper()
        if v and r.get('activityId') not in attach_by_activity:
            attach_by_activity[r['activityId']] = v
    for r in served:
        r['_att'] = attach_by_activity.get(r.get('activityId'), '')
        r['_false_trust_derived4'] = derived_false_trust(r, attach_by_activity)
        r['_false_trust_derived'] = derived_false_trust(r, attach_by_activity, BLOCK_CRITERIA_R3)
        r['_class'] = _partition(r)
    groups = collections.OrderedDict()
    groups['ALL'] = served
    for r in served:
        groups.setdefault(group_key(r), []).append(r)
    out = collections.OrderedDict()
    judged = lambda r: r.get('_false_trust_derived') in ('OK', 'WRONG')  # noqa: E731
    for g, rs in groups.items():
        acts = {}
        for r in rs:
            acts.setdefault(r.get('activityId'), dict(activityId=r.get('activityId'), lesson_attachment=attach_by_activity.get(r.get('activityId'), '')))
        out[g] = dict(blocks=len(rs), activities=len(acts),
                      display_only_fidelity=_rate(rs, 'display_fidelity'),
                      teaching_critical_fidelity=_rate(rs, 'teaching_critical_fidelity'),
                      reading_order=_rate(rs, 'reading_order'),
                      role_fidelity=_rate(rs, 'role_fidelity'),
                      lesson_attachment=_rate(list(acts.values()), 'lesson_attachment'),
                      false_trust_derived=_rate(rs, '_false_trust_derived'),
                      false_trust_derived4=_rate(rs, '_false_trust_derived4'),
                      false_trust_teaching_critical=_rate_from(rs, lambda r: r['_class'] == 'teaching_critical', judged),
                      false_trust_display_only=_rate_from(rs, lambda r: r['_class'] == 'display_only', judged),
                      false_trust_other=_rate_from(rs, lambda r: r['_class'] == 'other', judged),
                      false_trust_reviewer=_rate(rs, 'false_trust'),
                      error_classes=dict(collections.Counter(c.strip() for r in rs for c in (r.get('display_error_class') or '').split(',') if c.strip())),
                      teaching_critical_classes=dict(collections.Counter(c.strip() for r in rs for c in (r.get('teaching_critical_class') or '').split(',') if c.strip())))
    out['_withheld_reviewed'] = dict(rows=len(withheld), with_notes=sum(1 for r in withheld if (r.get('notes') or '').strip()))
    return out


def worst_examples(rows, limit=40):
    """Derived-WRONG served rows, teaching-critical first, with block ids and a SHORT quote only."""
    bad = [r for r in rows if r.get('servedAsTrusted', True) and r.get('_false_trust_derived') == 'WRONG']
    order = {'teaching_critical': 0, 'other': 1, 'display_only': 2}
    bad.sort(key=lambda r: (order.get(r.get('_class'), 9), r.get('family'), r.get('sampleId')))
    out = []
    for r in bad[:limit]:
        src = r.get('source') or {}
        out.append(dict(sampleId=r.get('sampleId'), cls=r.get('_class'), family=r.get('family'), book=r.get('book'), lesson=r.get('lesson'),
                        pagePdf=r.get('pagePdf'), kind=r.get('kind'), blockId=r.get('tslBlockId') or (src.get('sdm') or {}).get('id') or r.get('unitId') or r.get('activityId'),
                        display_error_class=r.get('display_error_class', ''), teaching_critical_class=r.get('teaching_critical_class', ''),
                        quote=(r.get('text') or '')[:60], notes=(r.get('notes') or '')[:160]))
    return out


def fmt_rate(x):
    if x['judged'] == 0:
        return f"— (0 judged / {x['sampled']} sampled; unsure {x['unsure']}, NA {x['na']}, unjudged {x['unjudged']})"
    return f"**{x['rate']:.4f}** [{x['lo']:.4f}, {x['hi']:.4f}] = {x['wrong']} / {x['judged']} judged (of {x['sampled']} sampled; unsure {x['unsure']}, NA {x['na']}, unjudged {x['unjudged']})"


RATE_COLS = [('display_only_fidelity', 'display fidelity error'), ('teaching_critical_fidelity', 'teaching-critical fidelity error'),
             ('reading_order', 'reading-order error'), ('role_fidelity', 'role error'), ('lesson_attachment', 'lesson-attachment error (per activity)'),
             ('false_trust_derived', 'false trust (derived, 5 criteria)'), ('false_trust_teaching_critical', 'teaching-critical false trust'),
             ('false_trust_display_only', 'display-only false trust'), ('false_trust_other', 'other false trust (role / attachment / order)'),
             ('false_trust_derived4', 'false trust (protocol 4 criteria)'), ('false_trust_reviewer', 'false trust (annotator verdict)')]


def render_md(results, meta, title):
    L = [f'# {title}', '', meta, '']
    for key, label in RATE_COLS:
        L += [f'### {label}', '', '| group | blocks | activities | rate [Wilson 95 %] = k / n judged (of m sampled; unsure, NA, unjudged) |', '|---|---|---|---|']
        for g, v in results.items():
            if g.startswith('_') or key not in v:
                continue
            L.append(f"| {g} | {v['blocks']} | {v['activities']} | {fmt_rate(v[key])} |")
        L.append('')
    L += ['### Error classes (display) and teaching-critical classes, per group', '', '| group | display error classes | teaching-critical classes |', '|---|---|---|']
    for g, v in results.items():
        if g.startswith('_'):
            continue
        L.append(f"| {g} | {json.dumps(v.get('error_classes', {}), ensure_ascii=False)} | {json.dumps(v.get('teaching_critical_classes', {}), ensure_ascii=False)} |")
    w = results.get('_withheld_reviewed', {})
    L += ['', f"Withheld rows reviewed (never in a served denominator): {w.get('rows', 0)} ({w.get('with_notes', 0)} with reviewer notes).", '',
          '## Sample size for a "< 1 % false trust" claim', '',
          'Wilson upper bound U(k, n) = (p̂ + z²/2n + z·sqrt(p̂(1−p̂)/n + z²/4n²)) / (1 + z²/n), z = 1.96; exact = Clopper–Pearson one-sided 95 %. Smallest n with U < 0.01 given k observed false-trusted blocks:', '',
          '| k false-trusted | n (Wilson) | n (exact) |', '|---|---|---|']
    for r in sample_size_table():
        L.append(f"| {r['k']} | {r['wilson']} | {r['exact']} |")
    L += ['', 'Reading: with 0 failures the Wilson bound needs 381 judged served blocks (exact: 299); every observed failure raises the requirement by roughly 130–160 blocks. Blocks from the same activity are not independent — treat the block-level interval as optimistic and report the activity-level count beside it.']
    return '\n'.join(L) + '\n'


def n_needed_at_observed_rate(k, n, target=0.01, n_max=200000):
    """Smallest N such that, at the OBSERVED proportion k/n, the Wilson upper bound is < target — i.e. how
    large a sample would have to be for a < 1 % claim if the rate stayed what it is (None ⇒ impossible: the
    observed rate itself is ≥ target)."""
    if n <= 0:
        return None
    p = k / n
    if p >= target:
        return None
    # exact scan (the bound is not strictly monotone because k is rounded), then coarse steps
    N = n
    while N <= n_max:
        if wilson(round(p * N), N)[2] < target:
            return N
        N += 1 if N < 20000 else max(1, N // 50)
    return None


# ---------------------------------------------------------------- validation on the TC-v2 gold
def rows_from_gold(gold_dir, pipeline):
    sys.path.insert(0, HERE)
    import tc_sdm  # noqa: E402
    import tc_score  # noqa: E402
    rows, pages = [], []
    for f in sorted(glob.glob(f'{gold_dir}/*.json')):
        gold = json.load(open(f))
        p = f"{ROOT}/poc-out/trusted-corpus/tc-v2/{pipeline}/sdm-gold/{gold['book']}/p{gold['page']:03d}.sdm.json"
        if not os.path.exists(p):
            continue
        sdm = json.load(open(p))
        v1 = dict(book=sdm['book'], page=sdm['page'], candidate='tc2-sdm', seconds=None, meta=dict(cascade=True),
                  blocks=[dict(id=ob['id'], order=ob['order'], role=ob['role']['coarse'], text=ob['text'], bbox=ob['bbox'],
                               trusted=(ob['trust']['status'] == 'TRUSTED') if ob['role']['value'] != 'figure' else None,
                               native_label=ob['native_label'], column=ob['column'], extraction=ob['extraction'], confidence=ob['ocr_conf'], fine_role=ob['role']['value'], reasons=ob['trust']['reasons'])
                          for ob in sdm['blocks']])
        r = tc_score.score(gold, v1)
        if r.get('error') or 'trusted_blocks' not in r:
            continue
        sets = ['all', 'heldout' if gold.get('held_out') else 'dev']
        if gold['book'] in SCIENCE_ALL:
            sets.append('science')
        wrong_ids = [w[0] for w in r.get('wrong_examples', [])]
        n_wrong, n_trusted = r['false_trusted'], r['trusted_blocks']
        for i in range(n_trusted):
            wrong = i < n_wrong
            bid = wrong_ids[i] if wrong and i < len(wrong_ids) else f"{gold['book']}:p{gold['page']:03d}:{'wrong' if wrong else 'ok'}{i}"
            rows.append(dict(sampleId=bid, family='gold:' + '+'.join(sets), sets=sets, book=gold['book'], pagePdf=gold['page'], activityId=f"{gold['book']}:p{gold['page']:03d}",
                             servedAsTrusted=True, display_fidelity='WRONG' if wrong else 'OK', teaching_critical_fidelity='NA', role_fidelity='NA',
                             lesson_attachment='OK' if r.get('lesson_attach', '').startswith('OK') else ('WRONG' if r.get('lesson_attach', '').startswith('WRONG') else 'NA'),
                             false_trust='WRONG' if wrong else 'OK'))
        pages.append(dict(book=gold['book'], page=gold['page'], trusted=n_trusted, false_trusted=n_wrong, sets=sets))
    return rows, pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jsonl', nargs='*')
    ap.add_argument('--md', default=None); ap.add_argument('--json', default=None)
    ap.add_argument('--from-gold', action='store_true'); ap.add_argument('--gold-dir', default=os.path.join(HERE, 'tc_gold')); ap.add_argument('--pipeline', default='tc2-p1')
    a = ap.parse_args()
    if a.from_gold:
        rows, pages = rows_from_gold(a.gold_dir, a.pipeline)
        res = collections.OrderedDict()
        for s in ('all', 'dev', 'heldout', 'science'):
            rs = [r for r in rows if s in r['sets']]
            k = sum(1 for r in rs if r['false_trust'] == 'WRONG'); n = len(rs)
            p, lo, hi = wilson(k, n) if n else (None, None, None)
            res[s] = dict(pages=sum(1 for p_ in pages if s in p_['sets']), trusted=n, false_trusted=k, ftr=p, lo=lo, hi=hi)
        ref_path = f"{ROOT}/poc-out/trusted-corpus/tc-v2/{a.pipeline}/metrics/gold-scores.json"
        ref = json.load(open(ref_path))['aggregate'] if os.path.exists(ref_path) else {}
        print('| set | pages | trusted | false-trusted | FTR (scorer) | Wilson 95 % | FTR (gold-scores.json) |')
        print('|---|---|---|---|---|---|---|')
        for s, v in res.items():
            rr = ref.get(s, {})
            print(f"| {s} | {v['pages']} | {v['trusted']} | {v['false_trusted']} | {v['ftr']:.4f} | [{v['lo']:.4f}, {v['hi']:.4f}] | {rr.get('ftr', '—')} ({rr.get('false_trusted', '—')}/{rr.get('trusted', '—')}) |")
        print()
        print('| k | n (Wilson) | n (exact) |'); print('|---|---|---|')
        for r in sample_size_table():
            print(f"| {r['k']} | {r['wilson']} | {r['exact']} |")
        if a.json:
            json.dump(dict(validation=res, pages=pages, sampleSize=sample_size_table()), open(a.json, 'w'), ensure_ascii=False, indent=1)
        return 0
    rows = []
    for p in a.jsonl:
        rows += [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
    if not rows:
        print('no rows'); return 2
    results = score_rows(rows)
    by_book = score_rows(rows, group_key=lambda r: f"{r.get('family')}|{r.get('book')}")
    by_subject = score_rows(rows, group_key=lambda r: f"subject={r.get('subject')}")
    by_layout = score_rows(rows, group_key=lambda r: f"layout={r.get('layoutFamily')}")
    by_kind = score_rows(rows, group_key=lambda r: f"{r.get('family')}/{r.get('kind')}")
    # the shipped-content view: pack families + samUnits, WITHOUT the mandatory Bài 17 TSL stratum
    shipped = [r for r in rows if r.get('family') != 'tslBai17']
    results_shipped = score_rows(shipped)
    worst = worst_examples(rows)
    pv = sorted({r.get('packVersion') for r in rows if r.get('packVersion')})
    reviewers = sorted({r.get('reviewer') for r in rows if (r.get('reviewer') or '').strip()})
    meta = (f"Rows {len(rows)} ({sum(1 for r in rows if r.get('servedAsTrusted', True))} served, {sum(1 for r in rows if not r.get('servedAsTrusted', True))} withheld) from {', '.join(a.jsonl)} · packs {', '.join(pv)} · "
            f"annotator(s): {', '.join(reviewers) or 'none'} · "
            'Denominators per D5: rates are over JUDGED served blocks of the SAMPLE; the population is the frame census in manifest-<seed>.json; nothing here is divided by 3,679. '
            'No threshold is applied here; PASS/FAIL is a Founder decision.')
    md = render_md(results, meta, 'False-trust audit — scores (rates reported separately, Wilson 95 %)')
    md += '\n## Shipped content only (pack families + samUnits; Bài 17 TSL stratum excluded)\n\n' + render_md(results_shipped, '', 'shipped').split('\n', 2)[2]
    md += '\n## By family × book\n\n' + render_md(by_book, '', 'per stratum').split('\n', 2)[2]
    md += '\n## By subject\n\n' + render_md(by_subject, '', 'per subject').split('\n', 2)[2]
    md += '\n## By layout family (K-12 census page class)\n\n' + render_md(by_layout, '', 'per layout').split('\n', 2)[2]
    md += '\n## By family / kind (served role)\n\n' + render_md(by_kind, '', 'per kind').split('\n', 2)[2]
    k = results_shipped['ALL']['false_trust_derived']['wrong']; n = results_shipped['ALL']['false_trust_derived']['judged']
    need = n_needed_at_observed_rate(k, n)
    md += ('\n## Sample size at the OBSERVED shipped rate\n\n'
           f"Observed derived false trust on shipped content: {k} / {n}. A «< 1 %» claim at this observed rate would need "
           f"{'n ≥ ' + str(need) + ' judged blocks (Wilson)' if need else 'an observed rate below 1 % — it is not, so no sample size makes the claim; the failing classes must be fixed and re-sampled with a new seed'}.\n")
    md += '\n## Worst examples (derived WRONG; teaching-critical first; short quotes only)\n\n| sampleId | class | family | book | lesson | pdf p | kind | block / unit | display class | tc class | quote | notes |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n'
    for w in worst:
        md += f"| {w['sampleId']} | {w['cls']} | {w['family']} | {w['book']} | {w['lesson']} | {w['pagePdf']} | {w['kind']} | `{w['blockId']}` | {w['display_error_class']} | {w['teaching_critical_class']} | {w['quote'].replace('|', '¦')} | {w['notes'].replace('|', '¦')} |\n"
    print(md)
    if a.md:
        open(a.md, 'w', encoding='utf-8').write(md)
    if a.json:
        json.dump(dict(results=results, shipped=results_shipped, byStratum=by_book, bySubject=by_subject, byLayout=by_layout, byKind=by_kind,
                       worst=worst, sampleSize=sample_size_table(), sampleSizeAtObservedShippedRate=dict(k=k, n=n, nNeeded=need), annotators=reviewers),
                  open(a.json, 'w'), ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
