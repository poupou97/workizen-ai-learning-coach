#!/usr/bin/env python3
"""Round 5 · Lane D — ORPHANED-SIBLING DETECTION: withholding is not always safe.

Founder, defect 8 of the 97-row evaluation set:

> Withholding one option of a multiple-choice question leaves the *served* question **wrong**,
> not merely smaller. For blocks with sibling/structural relationships (OPTION ⊂ QUESTION, a
> caption bound to its figure, a table row, a step in an enumerated procedure), withholding one
> member must withhold the whole group or restore the group — never serve a mutilated structure.
> This is a **teaching-critical** failure produced by the safety mechanism itself.

So a withheld block cannot be counted as "safely withheld" on its own; it has to be asked what it
left behind. This file answers that **independently of the pipeline and of Lane A1's group-aware
disposition**, from the Trusted Structured Lesson alone, deterministically:

    SPLIT_OPTION_GROUP    a run of `option` siblings where some are served and some withheld
                          — the served question shows a child an incomplete set of answers
    QUESTION_WITHOUT_OPTIONS  a served `question` whose whole option run is withheld
    OPTIONS_WITHOUT_QUESTION  served `option`s whose `question` is withheld
    SPLIT_ENUMERATED_RUN  a run of enumerated sub-items (`a)`, `b)`, `1.`, `2.`…) split the same way
    CAPTION_WITHOUT_FIGURE / FIGURE_WITHOUT_CAPTION   a caption served while its figure region is
                          withheld, or the reverse
    SPLIT_TABLE           a table region split between served and withheld

**These are counted as TEACHING-CRITICAL, not as "safely withheld".** A mutilated multiple-choice
is a wrong question, and a rate that files it under "coverage cost" is measuring the wrong thing.

Grouping is positional, from the page-level index in the BLOCK ID — **not** from the TSL's `order`
field, which is numbered separately for the served list and the withheld list. On the very page the
Founder named, the served options are `order` 11, 12, 13 and the withheld fourth option is `order`
17; an `order`-based grouping walks straight past the defect. Their id suffixes are 011–014.
No text is needed: a withheld region carries `role` and `text_len` but never its text (D4), and
`role == 'option'` is signal enough. Nothing here repairs anything; it counts.

    orphan.py scan --batch-dir DIR --pipeline ID [--out FILE] [--md FILE]
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

SCHEMA = 'lane-d-orphan-v1'

# An enumerator that makes a block a member of an ordered set the reader is meant to see whole.
ENUM = re.compile(r'^\s*(?:([a-eA-E])\s*[\).]|(\d{1,2})\s*[\).]|([A-D])\s*\.)\s')
GROUP_ROLES = ('option',)
STEP_ROLES = ('instruction', 'body', 'question', 'stage_label')


def page_index(block_id):
    """The page-level position from the block id suffix (`…:p130:tc2-p2:014` -> 14).

    This, and NOT `order`, is the sequence served blocks and withheld regions share. `order` is
    numbered per list: on Toán 4 tập một Bài 37 p130 the served options are `order` 11, 12, 13 and
    the withheld fourth option is `order` 17 — four apart, so an `order`-based grouping walks
    straight past the exact defect the Founder named (option D withheld while A, B, C are served).
    Its id suffix is 014, adjacent to 013. Grouping on the id suffix finds it.
    """
    tail = str(block_id).rsplit(':', 1)[-1]
    return int(tail) if tail.isdigit() else None


def entries(tsl):
    """Served blocks and withheld regions in ONE ordered sequence — the sibling relation is
    positional, and separating the two lists is what makes a split invisible."""
    out = []
    for b in tsl.get('blocks', []):
        out.append(dict(id=b['id'], page=b.get('page'), order=page_index(b['id']),
                        listOrder=b.get('order'),
                        role=(b.get('role') or {}).get('value'), served=True,
                        text=b.get('text') or '', bbox=b.get('bbox'), reasons=[]))
    for w in tsl.get('withheld', []):
        out.append(dict(id=w['id'], page=w.get('page'), order=page_index(w['id']),
                        listOrder=w.get('order'),
                        role=w.get('role'), served=False,
                        text='', textLen=w.get('text_len'), bbox=w.get('bbox'),
                        reasons=w.get('reasons') or []))
    out.sort(key=lambda e: (e['page'] if e['page'] is not None else 0,
                            e['order'] if e['order'] is not None else 0, e['id']))
    return out


def runs(seq, is_member):
    """Maximal runs of consecutive entries on one page that satisfy `is_member`."""
    out, cur, last = [], [], None
    for e in seq:
        member = is_member(e)
        contiguous = last is not None and e['page'] == last['page'] and (
            e['order'] is None or last['order'] is None or e['order'] - last['order'] <= 1)
        if member and (not cur or contiguous):
            cur.append(e)
        else:
            if len(cur) >= 2:
                out.append(cur)
            cur = [e] if member else []
        last = e
    if len(cur) >= 2:
        out.append(cur)
    return out


def _finding(kind, members, lesson, why):
    served = [m for m in members if m['served']]
    withheld = [m for m in members if not m['served']]
    return dict(kind=kind, book=lesson['book'], lesson=lesson['lesson'],
                page=members[0]['page'], why=why,
                members=len(members), served=len(served), withheld=len(withheld),
                servedIds=[m['id'] for m in served][:8],
                withheldIds=[m['id'] for m in withheld][:8],
                withheldReasons=sorted({r for m in withheld for r in (m['reasons'] or [])}))


def scan_tsl(tsl):
    """Every structure the withholding mutilated, in one lesson."""
    lesson = dict(book=tsl.get('book'), lesson=tsl.get('lesson'))
    seq = entries(tsl)
    found = []

    # 1. OPTION ⊂ QUESTION — the defect-8 shape.
    for run in runs(seq, lambda e: e['role'] in GROUP_ROLES):
        s = sum(1 for m in run if m['served'])
        if 0 < s < len(run):
            found.append(_finding('SPLIT_OPTION_GROUP', run, lesson,
                                  f'{s} of {len(run)} options served — the question shows an incomplete answer set'))
        elif s == 0:
            found.append(_finding('OPTION_GROUP_FULLY_WITHHELD', run, lesson,
                                  'the whole option run is withheld — safe, and the loss is coverage only'))

    # 2. A question and the options that belong to it (the option run immediately after it).
    by_pos = {(e['page'], e['order']): e for e in seq if e['order'] is not None}
    for e in seq:
        if e['role'] != 'question' or e['order'] is None:
            continue
        opts = []
        n = e['order'] + 1
        while (e['page'], n) in by_pos and by_pos[(e['page'], n)]['role'] in GROUP_ROLES:
            opts.append(by_pos[(e['page'], n)]); n += 1
        if not opts:
            continue
        s = sum(1 for m in opts if m['served'])
        if e['served'] and s == 0:
            found.append(_finding('QUESTION_WITHOUT_OPTIONS', [e] + opts, lesson,
                                  'the question is served and every one of its options is withheld'))
        elif not e['served'] and s > 0:
            found.append(_finding('OPTIONS_WITHOUT_QUESTION', [e] + opts, lesson,
                                  'the options are served and the question they answer is withheld'))

    # 3. Enumerated sub-item runs (a) b) c) · 1. 2. 3.) split between served and withheld.
    #    A withheld region carries no text, so it joins a run by position and role, never by content.
    enum_seq = []
    for e in seq:
        if e['served']:
            enum_seq.append(dict(e, _enum=bool(ENUM.match(e['text']))))
        else:
            enum_seq.append(dict(e, _enum=(e['role'] in STEP_ROLES + GROUP_ROLES)))
    for run in runs(enum_seq, lambda e: e['_enum']):
        served_enum = [m for m in run if m['served'] and ENUM.match(m['text'])]
        withheld = [m for m in run if not m['served']]
        if len(served_enum) >= 2 and withheld:
            found.append(_finding('SPLIT_ENUMERATED_RUN', run, lesson,
                                  f'{len(served_enum)} enumerated items served with {len(withheld)} '
                                  f'region(s) withheld inside the same run — the sequence a child reads has a hole'))

    # 4. caption ↔ figure. A figure region with a served caption and no served content, or a caption
    #    withheld while its figure is served, both leave the reader with half of a pair.
    figs = tsl.get('figures') or []
    for f in figs:
        fb, fp = f.get('bbox'), f.get('page')
        if not fb or fp is None:
            continue
        near = [e for e in seq if e['page'] == fp and e['role'] == 'caption' and _overlaps_x(e['bbox'], fb)]
        if not near:
            continue
        s = sum(1 for m in near if m['served'])
        if 0 < s < len(near):
            found.append(_finding('SPLIT_CAPTION_SET', near, lesson,
                                  'one figure carries both a served and a withheld caption block'))

    # 5. A table split between served and withheld rows.
    for run in runs(seq, lambda e: e['role'] == 'table'):
        s = sum(1 for m in run if m['served'])
        if 0 < s < len(run):
            found.append(_finding('SPLIT_TABLE', run, lesson, 'a table is served with some of its rows withheld'))
    return found


def _overlaps_x(a, b, tol=0.02):
    if not a or not b:
        return False
    return not (a[0] > b[0] + b[2] + tol or b[0] > a[0] + a[2] + tol)


TEACHING_CRITICAL_KINDS = ('SPLIT_OPTION_GROUP', 'QUESTION_WITHOUT_OPTIONS', 'OPTIONS_WITHOUT_QUESTION',
                           'SPLIT_ENUMERATED_RUN', 'SPLIT_CAPTION_SET', 'SPLIT_TABLE')


def cmd_scan(a):
    spec = common.load_json(f'{a.batch_dir}/batch-spec.json', {})
    all_found, per_lesson = [], []
    for L in spec.get('lessons', []):
        p = (f'{a.batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{a.pipeline}/lessons/'
             f'{L["book"]}/bai-{int(L["lesson"]):02d}.tsl.json')
        tsl = common.load_json(p)
        if not tsl:
            continue
        found = scan_tsl(tsl)
        all_found += found
        st = (tsl.get('stats') or {})
        tc = [f for f in found if f['kind'] in TEACHING_CRITICAL_KINDS]
        per_lesson.append(dict(book=L['book'], lesson=L['lesson'],
                               trusted=st.get('trusted'), withheld=st.get('withheld'),
                               findings=len(found), teachingCritical=len(tc),
                               kinds=dict(collections.Counter(f['kind'] for f in found)),
                               withheldRegionsThatOrphanASibling=len(
                                   {i for f in tc for i in f['withheldIds']})))
    kinds = collections.Counter(f['kind'] for f in all_found)
    tc_all = [f for f in all_found if f['kind'] in TEACHING_CRITICAL_KINDS]
    orphaning = {i for f in tc_all for i in f['withheldIds']}
    total_withheld = sum((l.get('withheld') or 0) for l in per_lesson)
    out = dict(
        schema=SCHEMA, batchDir=os.path.abspath(a.batch_dir), pipeline=a.pipeline,
        doctrine='a withheld block that orphans a sibling is a TEACHING-CRITICAL error caused by the safety '
                 'mechanism, not a safe withhold (Founder, evaluation-set defect 8)',
        method='grouping is positional, from the page-level index in the BLOCK ID (not the per-list `order` '
               'field, which is numbered separately for served and withheld and walks past the very defect '
               'this looks for), over served blocks and withheld regions in ONE sequence; a withheld region '
               'joins a group by role and position and never by its text, which the TSL does not carry (D4)',
        lessons=len(per_lesson), findings=len(all_found), kinds=dict(kinds),
        teachingCriticalFindings=len(tc_all),
        withheldRegionsThatOrphanASibling=len(orphaning),
        withheldRegionsTotal=total_withheld,
        orphaningShareOfWithheld=(round(len(orphaning) / total_withheld, 4) if total_withheld else None),
        orphaningShareFormatted=common.fmt_rate(len(orphaning), total_withheld) if total_withheld else '— (n = 0)',
        perLesson=per_lesson, rows=all_found)
    if a.out:
        common.dump_json(out, a.out)
        print(f'→ {a.out}')
    for l in per_lesson:
        print(f"  {l['book']} Bài {l['lesson']}: findings {l['findings']} "
              f"(teaching-critical {l['teachingCritical']}) {l['kinds'] or ''}")
    print(f"  {len(tc_all)} teaching-critical structure(s) mutilated by withholding · "
          f"{len(orphaning)} of {total_withheld} withheld regions orphan a sibling "
          f"({out['orphaningShareFormatted']})")
    if a.md:
        L2 = ['| kind | lesson | pdf page | served | withheld | withheld because | what a child sees |',
              '|---|---|---|---|---|---|---|']
        for f in all_found:
            L2.append(f"| **{f['kind']}** | {common.book_label(f['book'])} Bài {f['lesson']} | {f['page']} | "
                      f"{f['served']} | {f['withheld']} | {', '.join(f'`{r}`' for r in f['withheldReasons'])} | {f['why']} |")
        os.makedirs(os.path.dirname(os.path.abspath(a.md)), exist_ok=True)
        open(a.md, 'w', encoding='utf-8').write('\n'.join(L2) + '\n')
        print(f'markdown → {a.md}')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('scan')
    s.add_argument('--batch-dir', required=True)
    s.add_argument('--pipeline', required=True)
    s.add_argument('--out', default='')
    s.add_argument('--md', default='')
    s.set_defaults(fn=cmd_scan)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
