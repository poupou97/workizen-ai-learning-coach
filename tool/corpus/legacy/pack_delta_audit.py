#!/usr/bin/env python3
"""Round 5 · Lane D — BLIND AUDIT OF THE PACK-REBUILD DELTA (Founder §13:
"if the content delta is large, audit a representative delta before treating
the pack as usable").

The measured content delta of the round-5 rebuild is **empty**: all 12 packs
are byte-identical once `buildProvenance` is removed. There is therefore no
served block to audit — but there *is* a delta, and refusing to look at it
because it did not reach the served surface would be the papering-over the
order forbids.

What actually moved is the **attachment diagnosis**. `capped-toc-v2` adds a
systematic (header − TOC) offset; on the default packs it fires on exactly one
book (`05-sgk-tieng-viet-5-tap-hai`, offset −2) and reclassifies rows between
`range_ok` and `range_mismatch`. Those codes are counted, never dropped, for
families whose lesson comes from an upstream extractor — which is *why* the
served content did not move. So this tool audits the claim the new rule makes:

    for each reclassified row, does the lesson printed on the page
    actually equal the lesson the activity carries?

Method: render the top strip of the printed page (where the lesson badge sits),
judge the printed lesson number from the render **without** seeing the claimed
lesson, then join. `verdicts` reports, per direction:

    restored-correct       mismatch → ok  and the page really is that lesson
    restored-wrong         mismatch → ok  but the page is a different lesson
    flagged-correct        ok → mismatch  and the page really is a different lesson
    flagged-wrong          ok → mismatch  but the page really is that lesson
    no-badge-unjudgeable   the page prints no lesson badge at all

which is the same restored / falsely-restored shape as the legacy scoreboard's
RESTORE PRECISION, applied to a flag rather than to a block.

**The protocol's limit, stated where it cannot be missed.** A page in the MIDDLE of a
lesson prints no badge, so "no badge" does not mean "a different lesson". Such rows are
`no-badge-unjudgeable` and are excluded from both precisions rather than scored as
disagreements — a precision computed over rows the method cannot see is a precision
that was never measured. `restorePrecisionWorstCase` reports the harshest alternative
(every unjudgeable row counted against the change) beside the headline, never instead.

    pack_delta_audit.py rows   --old DIR --new DIR --out FILE
    pack_delta_audit.py sheets --sample FILE --out-dir DIR [--per-sheet 5]
    pack_delta_audit.py verdicts --sample FILE --answers FILE --out FILE [--md FILE]
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

FLAG_CODES = ('range_mismatch', 'unranged_lesson', 'not_canonical', 'page_unknown')


def _rows(path):
    d = json.load(open(path, encoding='utf-8'))
    out = {}
    for kind in ('dropped', 'flagged'):
        for r in d.get(kind, []):
            k = (r.get('family'), r.get('book'), r.get('lesson'), r.get('page'), r.get('note'))
            out[k] = dict(r, kind=kind)
    return out, d.get('summary', {})


def cmd_rows(a):
    """Every row whose attachment verdict changed between two builds."""
    rows, per_grade = [], {}
    for g in range(1, 13):
        f = f'lesson-index-g{g}.attach-log.json'
        po, pn = os.path.join(a.old, f), os.path.join(a.new, f)
        if not (os.path.exists(po) and os.path.exists(pn)):
            per_grade[str(g)] = {'missing': True}
            continue
        o, so = _rows(po)
        n, sn = _rows(pn)
        changed = []
        for k in set(o) | set(n):
            ro, rn = o.get(k), n.get(k)
            if (ro or {}).get('reason') == (rn or {}).get('reason'):
                continue
            fam, book, lesson, page, note = k
            before = (ro or {}).get('reason') or 'range_ok'
            after = (rn or {}).get('reason') or 'range_ok'
            changed.append(dict(
                id=f'pd{g:02d}-{len(changed):04d}', grade=g, family=fam, book=book,
                lesson=lesson, page=page, note=note,
                pagePdf=_pdf_page(note),
                reasonBefore=before, reasonAfter=after,
                direction=('restored' if before in FLAG_CODES and after == 'range_ok'
                           else 'newly-flagged' if before == 'range_ok' and after in FLAG_CODES
                           else 'other'),
            ))
        rows += changed
        per_grade[str(g)] = {
            'changed': len(changed),
            'ruleBefore': so.get('rule'), 'ruleAfter': sn.get('rule'),
            'tocOffsetsAfter': {b: v.get('toc_offset') for b, v in (sn.get('books') or {}).items() if v.get('toc_offset')},
            'flaggedBefore': so.get('flagged'), 'flaggedAfter': sn.get('flagged'),
            'droppedBefore': so.get('dropped'), 'droppedAfter': sn.get('dropped'),
        }
    out = {
        'schema': 'lane-d-pack-delta-audit-v1/rows',
        'oldAttachLogDir': os.path.abspath(a.old), 'newAttachLogDir': os.path.abspath(a.new),
        'totals': dict(collections.Counter(r['direction'] for r in rows)),
        'byBook': {b: dict(c) for b, c in sorted(
            ((b, collections.Counter(r['direction'] for r in rows if r['book'] == b))
             for b in sorted({r['book'] for r in rows})))},
        'perGrade': per_grade,
        'rows': sorted(rows, key=lambda r: (r['grade'], r['family'], r['page'] or 0)),
    }
    common.dump_json(out, a.out)
    print(f'rows → {a.out}')
    print(f'  {len(rows)} changed row(s): ' + ', '.join(f'{k} {v}' for k, v in sorted(out['totals'].items())))
    for b, c in out['byBook'].items():
        print(f'  {b}: {dict(c)}')
    return 0


def _pdf_page(note):
    """The unit id embeds its own pdf page: <book>:p0NN:… ."""
    if not note:
        return None
    for part in str(note).split(':'):
        if part.startswith('p') and part[1:].isdigit():
            return int(part[1:])
    return None


HEADER_STRIP = 0.22   # the top of a printed page: where the lesson badge sits


def cmd_sheets(a):
    """Contact sheets of the page TOP for each row — no claimed lesson shown (blind)."""
    from PIL import Image, ImageDraw
    import audit as legacy_audit
    sample = json.load(open(a.sample, encoding='utf-8'))
    rows = sample['rows']
    os.makedirs(a.out_dir, exist_ok=True)
    font = legacy_audit._font(20)
    idx, panels = [], []
    for r in rows:
        img = legacy_audit.render_crop(r['book'], r['pagePdf'], (0.0, 0.0, 1.0, HEADER_STRIP), dpi=150)
        if img is None:
            print(f'  no render for {r["id"]} ({r["book"]} pdf p{r["pagePdf"]})')
            continue
        if img.width > 1000:
            img = img.resize((1000, int(img.height * 1000 / img.width)))
        head = Image.new('RGB', (img.width, 34), (245, 245, 245))
        ImageDraw.Draw(head).text((8, 7), f'{r["id"]}   {r["book"]}   printed page {r["page"]}   (pdf p{r["pagePdf"]})',
                                  fill=(20, 20, 20), font=font)
        panel = Image.new('RGB', (img.width, img.height + 34), (255, 255, 255))
        panel.paste(head, (0, 0)); panel.paste(img, (0, 34))
        panels.append((r['id'], panel))
    n = 0
    for i in range(0, len(panels), a.per_sheet):
        batch = panels[i:i + a.per_sheet]
        w = max(p.width for _i, p in batch)
        h = sum(p.height + 10 for _i, p in batch)
        sheet = Image.new('RGB', (w, h), (255, 255, 255))
        y = 0
        for _i, p in batch:
            sheet.paste(p, (0, y)); y += p.height + 10
        out = os.path.join(a.out_dir, f'delta-sheet-{n:02d}.png')
        sheet.save(out)
        idx.append({'sheet': os.path.basename(out), 'ids': [i for i, _p in batch]})
        n += 1
    common.dump_json({'schema': 'lane-d-pack-delta-audit-v1/sheets', 'sample': os.path.abspath(a.sample),
                      'headerStrip': HEADER_STRIP, 'sheets': idx}, os.path.join(a.out_dir, 'INDEX.json'))
    print(f'{n} sheet(s) → {a.out_dir}')
    return 0


def cmd_verdicts(a):
    """Join the blind readings to the claimed lessons and score the delta."""
    sample = json.load(open(a.sample, encoding='utf-8'))
    answers = json.load(open(a.answers, encoding='utf-8'))
    read = {r['id']: r for r in answers['readings']}
    rows, counts = [], collections.Counter()
    for r in sample['rows']:
        rd = read.get(r['id'])
        if not rd:
            counts['not-judged'] += 1
            continue
        printed = rd.get('printedLesson')
        agrees = (printed is not None and printed == r['lesson'])
        if rd.get('unreadable'):
            verdict = 'unreadable'
        elif printed is None:
            # A page in the MIDDLE of a lesson prints no badge. "No badge" therefore does not
            # mean "a different lesson" — the protocol simply cannot judge this row, and scoring
            # it either way would invent a precision that was never measured.
            verdict = 'no-badge-unjudgeable'
        elif r['direction'] == 'restored':
            verdict = 'restored-correct' if agrees else 'restored-wrong'
        elif r['direction'] == 'newly-flagged':
            verdict = 'flagged-correct' if not agrees else 'flagged-wrong'
        else:
            verdict = 'other'
        counts[verdict] += 1
        rows.append(dict(id=r['id'], family=r['family'], book=r['book'], page=r['page'],
                         claimedLesson=r['lesson'], printedLesson=printed,
                         direction=r['direction'], verdict=verdict, note=rd.get('note', '')))
    n_rest = counts['restored-correct'] + counts['restored-wrong']
    n_flag = counts['flagged-correct'] + counts['flagged-wrong']
    # Sensitivity: the harshest reading, where an unbadged page counts against the change that
    # touched it. Reported beside the headline, never in place of it.
    unj = collections.Counter(r['direction'] for r in rows if r['verdict'] == 'no-badge-unjudgeable')
    s_rest_n = n_rest + unj['restored']
    s_flag_n = n_flag + unj['newly-flagged']
    out = {
        'schema': 'lane-d-pack-delta-audit-v1/verdicts',
        'sample': os.path.abspath(a.sample), 'answers': os.path.abspath(a.answers),
        'protocol': answers.get('protocol', ''),
        'protocolLimit': 'a page in the middle of a lesson prints no lesson badge, so a row whose page '
                         'shows none is UNJUDGEABLE by this protocol — it is excluded from both precisions '
                         'and counted as no-badge-unjudgeable, never scored as a disagreement',
        'counts': dict(counts),
        'unjudgeableByDirection': dict(unj),
        'restorePrecision': common.fmt_rate(counts['restored-correct'], n_rest) if n_rest else '— (n = 0)',
        'restorePrecisionValue': (counts['restored-correct'] / n_rest) if n_rest else None,
        'newFlagPrecision': common.fmt_rate(counts['flagged-correct'], n_flag) if n_flag else '— (n = 0)',
        'newFlagPrecisionValue': (counts['flagged-correct'] / n_flag) if n_flag else None,
        'restorePrecisionWorstCase': common.fmt_rate(counts['restored-correct'], s_rest_n) if s_rest_n else '— (n = 0)',
        'newFlagPrecisionWorstCase': common.fmt_rate(counts['flagged-correct'], s_flag_n) if s_flag_n else '— (n = 0)',
        'rows': rows,
    }
    common.dump_json(out, a.out)
    print(f'verdicts → {a.out}')
    for k, v in sorted(counts.items()):
        print(f'  {k:18s} {v}')
    print(f'  restore precision (flag level): {out["restorePrecision"]}   worst case {out["restorePrecisionWorstCase"]}')
    print(f'  new-flag precision:             {out["newFlagPrecision"]}   worst case {out["newFlagPrecisionWorstCase"]}')
    if unj:
        print(f'  unjudgeable (page prints no lesson badge): {dict(unj)} — excluded from both, never scored as a disagreement')
    if a.md:
        L = ['| id | family | printed page | lesson claimed | lesson printed | direction | verdict |', '|---|---|---|---|---|---|---|']
        for r in rows:
            L.append(f'| `{r["id"]}` | `{r["family"]}` | {r["page"]} | {r["claimedLesson"]} | '
                     f'{r["printedLesson"] if r["printedLesson"] is not None else "—"} | {r["direction"]} | **{r["verdict"]}** |')
        os.makedirs(os.path.dirname(os.path.abspath(a.md)), exist_ok=True)
        open(a.md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
        print(f'markdown → {a.md}')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('rows'); s.add_argument('--old', required=True); s.add_argument('--new', required=True); s.add_argument('--out', required=True); s.set_defaults(fn=cmd_rows)
    s = sub.add_parser('sheets'); s.add_argument('--sample', required=True); s.add_argument('--out-dir', required=True); s.add_argument('--per-sheet', type=int, default=5); s.set_defaults(fn=cmd_sheets)
    s = sub.add_parser('verdicts'); s.add_argument('--sample', required=True); s.add_argument('--answers', required=True); s.add_argument('--out', required=True); s.add_argument('--md', default=''); s.set_defaults(fn=cmd_verdicts)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
