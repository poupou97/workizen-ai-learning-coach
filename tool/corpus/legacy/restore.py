#!/usr/bin/env python3
"""Round 5 · Lane D — RESTORE PRECISION (Founder §9: "Add RESTORE PRECISION = correctly
restored / all restored. Do not raise coverage with imprecise restores.").

A **restore** is a region one build WITHHELD and a later build SERVES again. Round 5's
restores come from guard improvements, not from a repairer — Lane A1's repair framework and
Lane A2's math repairer had not landed green when this ran — so the REPAIRED stage is empty
and this file measures the only restores that actually happened. It says so in every output;
a restore by a loosened guard and a restore by a validated repair are not the same event and
must never be summed.

The measurement has two halves, and reporting only the first is how coverage gets raised
dishonestly:

    restored                   reviewed withheld regions the new build serves again
    RESTORE PRECISION          correctly restored / all restored — judged BLIND from the page
                               render of what is NOW served, never inherited from the old
                               judgement of what was refused
    falsely-withheld recovered restored ∧ the earlier audit had judged the refusal OVER-withheld
    wrongly restored           restored ∧ the earlier audit had judged the refusal SAFE
                               (the dangerous direction: a region the audit said was rightly
                               refused is being served again)

`falsely-withheld recovered` uses the OLD judgement and answers "did the fix hit the regions
the audit said were wrongly refused?". RESTORE PRECISION uses a NEW judgement and answers
"is what came back correct?". They are different questions and are never merged.

    restore.py rows      --delta FILE --annotated FILE --rerun-dir DIR --pipeline ID --out FILE
    restore.py sheets    --rows FILE --out-dir DIR [--per-sheet 4]
    restore.py precision --rows FILE --answers FILE --out FILE [--md FILE]
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

SCHEMA = 'lane-d-restore-v1'
OVER = 'OVER-withheld'


def _base_verdict(notes):
    """The earlier audit's judgement of the REFUSAL, read off its note. Never a judgement of
    what is served now."""
    n = notes or ''
    if OVER.lower() in n.lower():
        return 'OVER'          # the refusal was over-withholding — clean text wrongly refused
    if 'safe' in n.lower() or 'correct by design' in n.lower():
        return 'SAFE'          # the refusal was right
    return 'UNSURE'


def load_tsl_blocks(rerun_dir, pipeline, book, lesson):
    p = f'{rerun_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{pipeline}/lessons/{book}/bai-{int(lesson):02d}.tsl.json'
    t = common.load_json(p) or {}
    return {b['id']: b for b in t.get('blocks', [])}, p


def cmd_rows(a):
    delta = common.load_json(a.delta) or {}
    annot = {r['sampleId']: r for r in
             (json.loads(l) for l in open(a.annotated, encoding='utf-8') if l.strip())}
    wh = (delta.get('withheld') or {}).get('rows') or []
    rows = []
    for r in wh:
        sid = r.get('sampleId')
        base = annot.get(sid) or {}
        blocks, tsl_path = load_tsl_blocks(a.rerun_dir, a.pipeline, r['book'], r['lesson'])
        nb = r.get('new_block') or {}
        blk = blocks.get(nb.get('id')) if isinstance(nb, dict) else None
        rows.append(dict(
            id=sid, book=r['book'], lesson=r['lesson'], pagePdf=r.get('pagePdf'),
            baseReasons=r.get('base_reasons') or [],
            baseRefusalVerdict=_base_verdict(base.get('notes')),
            baseNotes=(base.get('notes') or '')[:200],
            outcome=r.get('outcome'), coverage=r.get('coverage'),
            restored=(r.get('outcome') == 'now_served'),
            newBlockId=(blk or {}).get('id') or (nb.get('id') if isinstance(nb, dict) else None),
            newRole=((blk or {}).get('role') or {}).get('value'),
            newText=(blk or {}).get('text'),
            newBbox=(blk or {}).get('bbox') or base.get('bbox'),
            newReasons=r.get('new_reasons'),
            tslPath=tsl_path,
        ))
    restored = [r for r in rows if r['restored']]
    by_base = collections.Counter(r['baseRefusalVerdict'] for r in restored)
    over_total = sum(1 for r in rows if r['baseRefusalVerdict'] == 'OVER')
    out = dict(
        schema=SCHEMA + '/rows',
        delta=os.path.abspath(a.delta), annotated=os.path.abspath(a.annotated),
        rerunDir=os.path.abspath(a.rerun_dir), pipeline=a.pipeline,
        restoreMechanism='guard change in the pipeline build — NOT a repair. No REPAIRED stage ran: '
                         'the repair framework and the math repairer had not landed green.',
        reviewedWithheldRegions=len(rows),
        restored=len(restored),
        restoredByBaseRefusalVerdict=dict(by_base),
        falselyWithheldTotal=over_total,
        falselyWithheldRecovered=by_base.get('OVER', 0),
        falselyWithheldRecoveryRate=common.fmt_rate(by_base.get('OVER', 0), over_total) if over_total else '— (n = 0)',
        wronglyRestoredCandidates=by_base.get('SAFE', 0),
        note='restoredByBaseRefusalVerdict uses the EARLIER audit of the refusal. RESTORE PRECISION is a '
             'separate, fresh, blind judgement of what is now served — see `precision`.',
        rows=rows)
    common.dump_json(out, a.out)
    print(f'rows → {a.out}')
    print(f'  reviewed withheld regions {len(rows)} · restored {len(restored)}')
    print(f'  of the restored, the earlier audit had called the refusal: {dict(by_base)}')
    print(f'  falsely-withheld recovered {out["falselyWithheldRecovered"]} of {over_total} '
          f'({out["falselyWithheldRecoveryRate"]})')
    if out['wronglyRestoredCandidates']:
        print(f'  ⚠ {out["wronglyRestoredCandidates"]} restored region(s) the earlier audit called a SAFE refusal '
              f'— these need the fresh judgement most')
    return 0


def cmd_sheets(a):
    """Render each restored region with what is NOW served, for a blind fresh judgement."""
    from PIL import Image, ImageDraw
    import audit as legacy_audit
    d = common.load_json(a.rows) or {}
    rows = [r for r in d['rows'] if r['restored']]
    os.makedirs(a.out_dir, exist_ok=True)
    font, small = legacy_audit._font(19), legacy_audit._font(17)
    panels = []
    for r in rows:
        img = legacy_audit.render_crop(r['book'], r['pagePdf'], r.get('newBbox'), dpi=170)
        if img is None:
            print(f'  no render for {r["id"]}')
            continue
        if img.width > 900:
            img = img.resize((900, int(img.height * 900 / img.width)))
        text = (r.get('newText') or '(no text recorded)')
        wrapped = []
        import textwrap
        for line in text.split('\n'):
            wrapped += textwrap.wrap(line, 58) or ['']
        h = max(img.height, 40 + 22 * (len(wrapped) + 2))
        panel = Image.new('RGB', (img.width + 640, h + 40), (255, 255, 255))
        dr = ImageDraw.Draw(panel)
        dr.text((8, 8), f'{r["id"]}   {r["book"]} Bài {r["lesson"]}   pdf p{r["pagePdf"]}   role {r["newRole"]}',
                fill=(20, 20, 20), font=font)
        panel.paste(img, (0, 40))
        dr.text((img.width + 12, 46), '— text now served —', fill=(90, 90, 90), font=small)
        for i, line in enumerate(wrapped[:40]):
            dr.text((img.width + 12, 70 + 22 * i), line, fill=(20, 20, 20), font=small)
        panels.append((r['id'], panel))
    idx, n = [], 0
    for i in range(0, len(panels), a.per_sheet):
        batch = panels[i:i + a.per_sheet]
        w = max(p.width for _i, p in batch)
        sheet = Image.new('RGB', (w, sum(p.height + 12 for _i, p in batch)), (255, 255, 255))
        y = 0
        for _i, p in batch:
            sheet.paste(p, (0, y)); y += p.height + 12
        out = os.path.join(a.out_dir, f'restore-sheet-{n:02d}.png')
        sheet.save(out)
        idx.append(dict(sheet=os.path.basename(out), ids=[i for i, _p in batch]))
        n += 1
    common.dump_json(dict(schema=SCHEMA + '/sheets', rows=os.path.abspath(a.rows), sheets=idx),
                     os.path.join(a.out_dir, 'INDEX.json'))
    print(f'{n} sheet(s) → {a.out_dir}')
    return 0


def cmd_precision(a):
    d = common.load_json(a.rows) or {}
    ans = common.load_json(a.answers) or {}
    judged = {j['id']: j for j in ans.get('judgements', [])}
    rows, counts = [], collections.Counter()
    for r in d['rows']:
        if not r['restored']:
            continue
        j = judged.get(r['id'])
        if not j:
            counts['not-judged'] += 1
            continue
        v = (j.get('verdict') or '').strip().upper()
        # CORRECT: what is served now matches the page and is servable content.
        # WRONG:   what is served now is damaged, spliced, mis-roled, or is page furniture.
        # UNSURE:  the render cannot settle it — excluded from the precision, counted beside.
        counts[v] += 1
        rows.append(dict(id=r['id'], book=r['book'], lesson=r['lesson'], pagePdf=r['pagePdf'],
                         baseReasons=r['baseReasons'], baseRefusalVerdict=r['baseRefusalVerdict'],
                         newRole=r['newRole'], verdict=v, why=j.get('why', '')))
    k, n = counts['CORRECT'], counts['CORRECT'] + counts['WRONG']
    over_correct = sum(1 for r in rows if r['baseRefusalVerdict'] == 'OVER' and r['verdict'] == 'CORRECT')
    safe_restored = [r for r in rows if r['baseRefusalVerdict'] == 'SAFE']
    out = dict(
        schema=SCHEMA + '/precision',
        rowsFile=os.path.abspath(a.rows), answers=os.path.abspath(a.answers),
        protocol=ans.get('protocol', ''), annotator=ans.get('annotator', ''),
        restoreMechanism=d.get('restoreMechanism'),
        counts=dict(counts),
        restorePrecision=common.fmt_rate(k, n) if n else '— (n = 0)',
        restorePrecisionValue=(k / n) if n else None,
        falselyWithheldRecoveredAndCorrect=over_correct,
        falselyWithheldTotal=d.get('falselyWithheldTotal'),
        restoredThatTheEarlierAuditCalledSafeRefusals=[r['id'] for r in safe_restored],
        note='UNSURE rows are excluded from the precision and counted beside it; a precision computed over '
             'rows the render cannot settle is a precision that was not measured.',
        rows=rows)
    common.dump_json(out, a.out)
    print(f'precision → {a.out}')
    for kk, vv in sorted(counts.items()):
        print(f'  {kk:12s} {vv}')
    print(f'  RESTORE PRECISION {out["restorePrecision"]}')
    print(f'  falsely-withheld recovered AND correct: {over_correct} of {d.get("falselyWithheldTotal")} '
          f'regions the earlier audit called over-withheld')
    if a.md:
        L = ['| id | lesson | pdf page | withheld before, because | earlier audit of the refusal | role now | fresh verdict | why |',
             '|---|---|---|---|---|---|---|---|']
        for r in rows:
            L.append(f'| `{r["id"]}` | {r["book"]} Bài {r["lesson"]} | {r["pagePdf"]} | '
                     f'{", ".join(f"`{x}`" for x in r["baseReasons"])} | {r["baseRefusalVerdict"]} | '
                     f'`{r["newRole"]}` | **{r["verdict"]}** | {r["why"]} |')
        os.makedirs(os.path.dirname(os.path.abspath(a.md)), exist_ok=True)
        open(a.md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
        print(f'markdown → {a.md}')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('rows'); s.add_argument('--delta', required=True); s.add_argument('--annotated', required=True)
    s.add_argument('--rerun-dir', required=True); s.add_argument('--pipeline', required=True); s.add_argument('--out', required=True); s.set_defaults(fn=cmd_rows)
    s = sub.add_parser('sheets'); s.add_argument('--rows', required=True); s.add_argument('--out-dir', required=True)
    s.add_argument('--per-sheet', type=int, default=3); s.set_defaults(fn=cmd_sheets)
    s = sub.add_parser('precision'); s.add_argument('--rows', required=True); s.add_argument('--answers', required=True)
    s.add_argument('--out', required=True); s.add_argument('--md', default=''); s.set_defaults(fn=cmd_precision)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
