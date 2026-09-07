#!/usr/bin/env python3
"""Round 7 · WS-M — run the Metric Definition Registry.

    python3 tool/metrics/cli.py report            # the full registry, one card per metric
    python3 tool/metrics/cli.py verify            # re-derive every metric; non-zero on any mismatch
    python3 tool/metrics/cli.py verify --only ID
    python3 tool/metrics/cli.py deprecated        # what «total activities» actually was
    python3 tool/metrics/cli.py lint              # the container-shape lint over tool/
    python3 tool/metrics/cli.py md                # the registry as markdown

`verify` exits non-zero when a recorded value does not re-derive. An artefact that is not on
this machine reports UNAVAILABLE and does not pass: packs and poc-out/ are gitignored SGK
derivative works, and a missing artefact is never a zero.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import metric_container_lint as container_lint  # noqa: E402
import metric_leaves as L                       # noqa: E402
import metric_registry as R                     # noqa: E402

OK, MISMATCH, UNAVAILABLE, ERROR = 'OK', 'MISMATCH', 'UNAVAILABLE', 'ERROR'
NO_RECORD = 'NO RECORDED VALUE'


def _derive(metric, ctx):
    try:
        return metric.derive(ctx), None
    except L.ArtefactMissing as e:
        return None, f'{UNAVAILABLE}: {e}'
    except Exception as e:                                    # noqa: BLE001
        return None, f'{ERROR}: {type(e).__name__}: {e}'


def cmd_report(args):
    ctx = R.Ctx(args.root)
    print('METRIC DEFINITION REGISTRY — round 7 · WS-M')
    print('NO IMPORTANT DERIVED METRIC IS ACCEPTED UNLESS IT CAN BE RE-DERIVED FROM LEAF RECORDS.\n')
    for m in R.METRICS:
        if args.only and m.id != args.only:
            continue
        value, err = _derive(m, ctx)
        print('=' * 78)
        print(f'{m.id}')
        print('-' * 78)
        print(f'  semantic quantity : {m.semantic_quantity}')
        print(f'  unit              : {m.unit}')
        print(f'  leaf population   : {m.leaf_population}')
        print(f'  grouping key      : {m.grouping_key}')
        print(f'  denominator       : {m.denominator}')
        print(f'  aggregation       : {m.aggregation}')
        print(f'  exclusions        : {m.exclusions}')
        print(f'  source artefact   : {m.source_artefact}')
        print(f'  re-derivation     : {m.rederivation_command}')
        print(f'  recorded ({m.measured_on}): '
              f'{m.recorded_value if m.recorded_value is not None else NO_RECORD}')
        print(f'  re-derived now    : {value if err is None else err}')
        if m.note:
            print(f'  note              : {m.note}')
    return 0


def cmd_verify(args):
    ctx = R.Ctx(args.root)
    # ⭐⭐ WAL-223 S8 — XOÁ MỘT GIÁ TRỊ ĐÃ GHI TỪNG LÀ CÁCH LÀM CỔNG XANH.
    #
    # `NO_RECORD` không được tính vào `bad`, nên một chỉ số bị gỡ giá trị ghi
    # nhận sẽ biến mất khỏi phần «sai» — và tệ hơn, dòng tổng kết còn đếm nó
    # vào «re-derive to their recorded value», một câu không thể đúng khi
    # KHÔNG CÓ giá trị nào được ghi.
    #
    # Đếm riêng: chưa-hỏi khác với đã-hỏi-và-đúng.
    rows, bad, unrecorded = [], 0, 0
    for m in R.METRICS:
        if args.only and m.id != args.only:
            continue
        value, err = _derive(m, ctx)
        if err:
            status = err.split(':')[0]
        elif m.recorded_value is None:
            status = NO_RECORD
        elif value == m.recorded_value:
            status = OK
        else:
            status = MISMATCH
        if status in (MISMATCH, ERROR, UNAVAILABLE):
            bad += 1
        elif status == NO_RECORD:
            unrecorded += 1
        rows.append((m.id, m.recorded_value, value if err is None else '—', m.unit, status, err or ''))

    if not rows:
        print(f'no metric named {args.only!r}', file=sys.stderr)
        return 2

    w = max(len(r[0]) for r in rows)
    print(f'{"metric".ljust(w)}  {"recorded":>9}  {"re-derived":>10}  status')
    for mid, rec, got, _unit, status, err in rows:
        print(f'{mid.ljust(w)}  {str(rec if rec is not None else "—"):>9}  {str(got):>10}  {status}'
              + (f'   {err}' if err else ''))

    shapes = []
    try:
        shapes = L.check_pack_shapes(ctx.packs)
    except L.ArtefactMissing as e:
        print(f'\nschema check: UNAVAILABLE ({e})')
    else:
        print(f'\nschema check: {"OK — every declared shape holds in every pack" if not shapes else shapes}')
    bad += len(shapes)

    verified = len(rows) - bad - unrecorded
    print(f'\n{verified} of {len(rows)} metrics re-derive to their recorded value.')
    if unrecorded:
        # Câu này TỪNG bị nuốt vào con số trên. Một chỉ số không có giá trị ghi
        # nhận thì không «khớp» được với cái gì cả.
        print(f'{unrecorded} metric(s) have NO RECORDED VALUE — not checked, and '
              'not a pass. Deleting a recorded value must not be a way to go green.')
    if bad:
        print('FAIL — a recorded metric did not re-derive, or its artefact is not on this machine.')
    if bad:
        return 1
    if unrecorded and getattr(args, 'require_recorded', False):
        print('--require-recorded: caller claims every metric is verified, but '
              f'{unrecorded} carry no recorded value.')
        return 1
    return 0


def cmd_deprecated(args):
    ctx = R.Ctx(args.root)
    print('DEPRECATED AND SUPERSEDED METRICS — kept, never deleted\n')
    for d in R.DEPRECATED:
        print('=' * 78)
        print(f'{d.id}   [{d.verdict}]   published value: '
              f'{d.published_value if d.published_value is not None else "— (a phrase, not a number)"}')
        print('-' * 78)
        print(f'  published as      : {d.published_as}')
        print(f'  what it really is : {d.what_it_actually_is}')
        print(f'  reason            : {d.reason}')
        print(f'  use instead       : {d.replacement}')
        if d.reconstruction:
            print(f'  reconstruction    : {d.reconstruction}')
        if d.reconstruct is not None:
            try:
                got = d.reconstruct(ctx)
            except L.ArtefactMissing as e:
                print(f'  reconstructed now : UNAVAILABLE ({e})')
            else:
                verdict = 'reproduces' if got == d.published_value else 'DOES NOT REPRODUCE'
                print(f'  reconstructed now : {got} — {verdict} the published {d.published_value}')
    return 0


def cmd_lint(args):
    findings = container_lint.lint_paths(args.root)
    known, repaired = container_lint.KNOWN_FINDINGS, container_lint.REPAIRED_FINDINGS
    live = {f.key for f in findings}
    new = [f for f in findings if f.key not in known]
    print(f'container-shape lint — {len(findings)} finding(s) live, '
          f'{len(known)} baselined, {len(new)} new, {len(repaired)} repaired\n')
    for f in findings:
        tag = 'KNOWN' if f.key in known else '*** NEW ***'
        print(f'[{tag}] {f}')
        if f.key in known:
            print(f'    verdict: {known[f.key]}')
        elif f.key in repaired:
            print('    *** THIS DEFECT WAS REPAIRED AND HAS RETURNED. ***')
            print(f"    was: {repaired[f.key]['defect']}")
        print()
    for key in known:
        if key not in live:
            print(f'[GONE] {key} — baselined but no longer found. If it was fixed, MOVE it to '
                  f'REPAIRED_FINDINGS in the same commit; do not delete it. What a repair means '
                  f'for numbers published from the broken code must not vanish with the code.')
    if repaired:
        print('--- repaired, and what each repair means for numbers published earlier ---\n')
        for key, r in repaired.items():
            print(f'[REPAIRED{" — RETURNED!" if key in live else ""}] {key}')
            print(f"    repaired : {r['repaired']}")
            print(f"    OLD NUMBERS: {r['effect_on_published_numbers']}")
            print(f"    recorded in: {r['correction_recorded_in']}\n")
    return 1 if new else 0


def cmd_md(args):
    ctx = R.Ctx(args.root)
    cols = ('metric', 'unit', 'leaf population', 'grouping key', 'aggregation',
            'denominator', 'exclusions', 'source artefact', 're-derivation', 'value')
    print('| ' + ' | '.join(cols) + ' |')
    print('|' + '|'.join(['---'] * len(cols)) + '|')
    for m in R.METRICS:
        value, err = _derive(m, ctx)
        cells = [f'`{m.id}`', m.unit, m.leaf_population, f'`{m.grouping_key}`', m.aggregation,
                 m.denominator, m.exclusions, m.source_artefact,
                 f'`{m.rederivation_command}`',
                 f'**{value}**' if err is None else 'UNAVAILABLE']
        print('| ' + ' | '.join(c.replace('|', '\\|').replace('\n', ' ') for c in cells) + ' |')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('command', choices=('report', 'verify', 'deprecated', 'lint', 'md'))
    ap.add_argument('--root', default=None, help='repository root (default: autodetected)')
    ap.add_argument('--only', default=None, help='a single metric id')
    ap.add_argument('--require-recorded', action='store_true',
                    help='verify: exit non-zero if any metric carries no recorded '
                         'value (for callers that CLAIM every metric is verified)')
    args = ap.parse_args(argv)
    return {'report': cmd_report, 'verify': cmd_verify, 'deprecated': cmd_deprecated,
            'lint': cmd_lint, 'md': cmd_md}[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
