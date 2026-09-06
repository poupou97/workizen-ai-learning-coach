#!/usr/bin/env python3
"""LANE C (round 5, §11) — re-run report: what the round-4 pipeline fixes did to LS&ĐL 5 Bài 8.

Read-only. Compares two bounded sandbox runs of the SAME book through the SAME CLIs:

  round 4  poc-out/round4/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/tc2-p1   (sdm-v2)
  round 5  poc-out/round5/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/tc2-r5   (sdm-v3)

Both runs read the SAME raw Docling/XY-cut candidate files (round 4's), so every difference below is
a difference in the SDM / attach / TSL / bridge code, never OCR noise.

It also scores both runs against the round-5 VERBATIM LEDGER (a human read of the printed page —
`docs/research/lane-c/data/lsdl5-bai8-verbatim-ledger.json`), which is the only signal that can
decide false trust and false withhold, because round 4 falsified «two stacks agreeing ⇒ verbatim».

    python3 tool/research/lane_c/round5_rerun.py [--out DIR] [--copy-md PATH]
"""
import argparse
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
BOOK = '05-sgk-lich-su-va-dia-li-5'
LESSON = 8

R4 = f'{MAIN}/poc-out/round4/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/tc2-p1'
R5 = f'{MAIN}/poc-out/round5/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/tc2-r5'
LEDGER = f'{REPO}/docs/research/lane-c/data/lsdl5-bai8-verbatim-ledger.json'

VERBATIM_VERDICTS = ('verbatim', 'verbatim_glyph')


def load(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def tsl(root, lesson=LESSON):
    p = f'{root}/lessons/{BOOK}/bai-{lesson:02d}.tsl.json'
    return load(p) if os.path.exists(p) else None


def short(block_id):
    """`05-…-5:p039:tc2-p1:000` → `p039:tc2-p1:000` (the id the reports and the ledger quote)."""
    parts = block_id.split(':')
    return ':'.join(parts[1:]) if len(parts) >= 4 else block_id


def dispositions(doc):
    """block id → (TRUSTED|WITHHELD, role, reasons)."""
    out = {}
    for b in doc['blocks']:
        out[b['id']] = ('TRUSTED', b['role']['value'], [])
    for b in doc['withheld']:
        out[b['id']] = ('WITHHELD', b.get('role'), sorted(b.get('reasons') or []))
    return out


def book_summary(root):
    """Attachment + TSL totals over every lesson the run produced."""
    d = f'{root}/lessons/{BOOK}'
    lessons, learning, trusted, withheld, reasons = [], 0, 0, 0, Counter()
    for name in sorted(os.listdir(d)):
        if not name.endswith('.tsl.json'):
            continue
        t = load(f'{d}/{name}')
        s = t['stats']
        lessons.append(dict(lesson=t['lesson'], pages=t['boundary']['pages'], conf=t['boundary']['confidence'],
                            source=t['boundary']['source'], learning=s['learning_blocks'], trusted=s['trusted'],
                            withheld=s['withheld'], title=t.get('title')))
        learning += s['learning_blocks']; trusted += s['trusted']; withheld += s['withheld']
        reasons.update(s.get('withheld_by_reason') or {})
    return dict(lessons=lessons, n_lessons=len(lessons), learning=learning, trusted=trusted,
                withheld=withheld, reasons=dict(reasons.most_common()))


def score_verbatim(disp, ledger):
    """The four-cell table the data-accuracy scoreboard needs, judged by the human read."""
    by_block = {e['block']: e for e in ledger['blocks']}
    cells = Counter()
    rows = []
    for bid, (status, role, why) in sorted(disp.items(), key=lambda kv: short(kv[0])):
        entry = by_block.get(short(bid))
        if entry is None:
            cells['unjudged'] += 1
            continue
        verbatim = entry['verdict'] in VERBATIM_VERDICTS
        if status == 'TRUSTED' and verbatim:
            cell = 'correct_served'
        elif status == 'TRUSTED' and not verbatim:
            cell = 'FALSE_TRUST'
        elif status == 'WITHHELD' and verbatim:
            cell = 'FALSE_WITHHELD'
        else:
            cell = 'correct_withheld'
        cells[cell] += 1
        rows.append(dict(block=short(bid), status=status, role=role, reasons=why,
                         verdict=entry['verdict'], cell=cell, anchor=entry.get('anchor'),
                         slips=entry.get('slips') or []))
    return dict(cells=dict(cells), rows=rows)


def md_table(header, rows):
    out = ['| ' + ' | '.join(header) + ' |', '|' + '---|' * len(header)]
    for r in rows:
        out.append('| ' + ' | '.join('' if c is None else str(c) for c in r) + ' |')
    return '\n'.join(out)


def build():
    r4, r5 = tsl(R4), tsl(R5)
    if r4 is None or r5 is None:
        raise SystemExit('both bounded runs must exist (round 4 v1 and round 5 v1)')
    ledger = load(LEDGER)
    d4, d5 = dispositions(r4), dispositions(r5)
    b4, b5 = book_summary(R4), book_summary(R5)
    s4, s5 = score_verbatim(d4, ledger), score_verbatim(d5, ledger)

    gained = sorted([b for b in d5 if d5[b][0] == 'TRUSTED' and d4.get(b, ('?',))[0] != 'TRUSTED'], key=short)
    lost = sorted([b for b in d4 if d4[b][0] == 'TRUSTED' and d5.get(b, ('?',))[0] != 'TRUSTED'], key=short)
    return dict(book=BOOK, lesson=LESSON,
                round4=dict(run=R4, sdm=r4['blocks'][0]['provenance']['sdm_version'], stats=r4['stats'],
                            boundary=r4['boundary'], book=b4, verbatim=s4),
                round5=dict(run=R5, sdm=r5['blocks'][0]['provenance']['sdm_version'], stats=r5['stats'],
                            boundary=r5['boundary'], book=b5, verbatim=s5),
                gained=[dict(block=short(b), role=d5[b][1]) for b in gained],
                lost=[dict(block=short(b), role=d5.get(b, (None, None, None))[1], reasons=d5.get(b, (None, None, []))[2]) for b in lost],
                ledger_meta=dict(reviewer=ledger['reviewer'], date=ledger['date'], blocks=len(ledger['blocks'])))


def render(rep):
    r4, r5 = rep['round4'], rep['round5']
    L = ['# LS&ĐL 5 Bài 8 — round-4 vs round-5 pipeline (Lane C, round 5)', '',
         'Same book, same CLIs, **same raw OCR candidate files** (round 4\'s) — every difference is pipeline code '
         f'({r4["sdm"]} → {r5["sdm"]}). Verbatim verdicts come from a human read of the printed renders '
         f'({rep["ledger_meta"]["blocks"]} blocks, {rep["ledger_meta"]["date"]}), not from stack agreement.', '',
         '## Book (28 lessons of LS&ĐL 5)', '']
    L.append(md_table(['measure', 'round 4', 'round 5'], [
        ['lessons with a TSL', r4['book']['n_lessons'], r5['book']['n_lessons']],
        ['learning blocks', r4['book']['learning'], r5['book']['learning']],
        ['trusted', r4['book']['trusted'], r5['book']['trusted']],
        ['withheld', r4['book']['withheld'], r5['book']['withheld']],
    ]))
    L += ['', '**Withheld by reason (book):**', '']
    keys = sorted(set(r4['book']['reasons']) | set(r5['book']['reasons']))
    L.append(md_table(['reason', 'round 4', 'round 5'],
                      [[k, r4['book']['reasons'].get(k, 0), r5['book']['reasons'].get(k, 0)] for k in keys]))
    L += ['', '## Bài 8', '']
    L.append(md_table(['measure', 'round 4', 'round 5'], [
        ['boundary', f'{r4["boundary"]["page_start"]}–{r4["boundary"]["page_end"]} conf {r4["boundary"]["confidence"]} ({r4["boundary"]["source"]})',
         f'{r5["boundary"]["page_start"]}–{r5["boundary"]["page_end"]} conf {r5["boundary"]["confidence"]} ({r5["boundary"]["source"]})'],
        ['learning blocks', r4['stats']['learning_blocks'], r5['stats']['learning_blocks']],
        ['trusted', r4['stats']['trusted'], r5['stats']['trusted']],
        ['withheld', r4['stats']['withheld'], r5['stats']['withheld']],
        ['roles trusted', json.dumps(r4['stats']['roles_trusted'], ensure_ascii=False),
         json.dumps(r5['stats']['roles_trusted'], ensure_ascii=False)],
        ['withheld by reason', json.dumps(r4['stats']['withheld_by_reason'], ensure_ascii=False),
         json.dumps(r5['stats']['withheld_by_reason'], ensure_ascii=False)],
    ]))
    L += ['', f'### Newly trusted ({len(rep["gained"])})', '']
    L.append(md_table(['block', 'role'], [[g['block'], g['role']] for g in rep['gained']]))
    L += ['', f'### Newly withheld ({len(rep["lost"])})', '']
    L.append(md_table(['block', 'role', 'reasons'], [[g['block'], g['role'], ','.join(g['reasons'])] for g in rep['lost']]))
    L += ['', '## Verbatim scoreboard (denominator: the 51 Bài 8 learning blocks the human read judged)', '']
    cells = ['correct_served', 'FALSE_TRUST', 'FALSE_WITHHELD', 'correct_withheld']
    L.append(md_table(['cell', 'round 4', 'round 5'],
                      [[c, r4['verbatim']['cells'].get(c, 0), r5['verbatim']['cells'].get(c, 0)] for c in cells]))
    L += ['', '### Round 5 — every judged block', '']
    L.append(md_table(['block', 'status', 'role', 'reasons', 'print verdict', 'cell', 'slips'],
                      [[r['block'], r['status'], r['role'], ','.join(r['reasons']), r['verdict'], r['cell'],
                        '; '.join(f'{s["pipeline"]}→{s["printed"]}' for s in r['slips'])]
                       for r in r5['verbatim']['rows']]))
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=f'{MAIN}/poc-out/round5/lane-c/tc2-lsdl5/v1/report')
    ap.add_argument('--copy-md', default=None)
    a = ap.parse_args()
    rep = build()
    os.makedirs(a.out, exist_ok=True)
    with open(f'{a.out}/round5-rerun.json', 'w', encoding='utf-8') as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=2, sort_keys=True)
    md = render(rep)
    with open(f'{a.out}/round5-rerun.md', 'w', encoding='utf-8') as fh:
        fh.write(md)
    if a.copy_md:
        with open(a.copy_md, 'w', encoding='utf-8') as fh:
            fh.write(md)
    r4, r5 = rep['round4'], rep['round5']
    print(f'{a.out}/round5-rerun.md')
    print(f'  Bài 8 trusted {r4["stats"]["trusted"]} → {r5["stats"]["trusted"]}, withheld {r4["stats"]["withheld"]} → {r5["stats"]["withheld"]}')
    print(f'  false trust {r4["verbatim"]["cells"].get("FALSE_TRUST", 0)} → {r5["verbatim"]["cells"].get("FALSE_TRUST", 0)} · '
          f'false withheld {r4["verbatim"]["cells"].get("FALSE_WITHHELD", 0)} → {r5["verbatim"]["cells"].get("FALSE_WITHHELD", 0)}')


if __name__ == '__main__':
    main()
