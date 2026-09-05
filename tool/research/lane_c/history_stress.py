#!/usr/bin/env python3
"""LANE C (round 5, §11 item 3) — DELIBERATE FALSIFICATION of the two PROPOSED History rules and of
lesson identity, on the 27 LS&ĐL 5 lessons that are NOT the golden slice.

Three claims are attacked, each with the counter-example the Founder named:

  T1  «`prose-dated-events-v1` generalises to History» — does it survive a different DATE STYLE?
      The rule only accepts «CapitalisedRun (year[ – year][ TCN])». This test inventories every date form
      the book actually prints — centuries («thế kỉ VI», «thế kỉ III TCN»), reign/period phrases, narrative
      years («năm 544»), TCN mixtures — and reports what the rule sees, misses and (worse) mis-promotes.

  T2  «`story-attribution-v1` generalises to a source» — does it survive a source that is a QUOTED
      DOCUMENT rather than a story («TƯ LIỆU. Trong Chiếu dời đô …»)? The rule walks back to the nearest
      heading; a quoted document sits inside a section, not inside a story box.

  T3  «lesson identity» — does one lesson = one page range survive a TWO-LESSON SPREAD (a page where the
      next lesson's header starts)? Reported from the run's own boundaries, not assumed.

Read-only over the round-5 bounded run's bridged documents. Nothing is written outside `--out`.

    python3 tool/research/lane_c/history_stress.py [--docs DIR] [--out DIR] [--copy-md PATH]
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import history_rules as hr  # noqa: E402

MAIN = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
RUN = f'{MAIN}/poc-out/round5/lane-c/tc2-lsdl5/v1'
DOCS = f'{RUN}/lesson-document-all'
BOOK = '05-sgk-lich-su-va-dia-li-5'

# every way this book writes a date, measured — not a taxonomy copied from Science
FORMS = [
    ('paren-year', re.compile(r'\(\s*\d{1,4}(\s*TCN)?\s*(?:[-–—]\s*\d{1,4})?\s*(TCN)?\s*\)')),
    ('century-tcn', re.compile(r'thế\s+k[ỉiíìỉĩị]\s+[IVXLC]+\s+TCN', re.I)),
    ('century', re.compile(r'thế\s+k[ỉiíìỉĩị]\s+[IVXLC]+', re.I)),
    ('narrative-year', re.compile(r'\b[Nn]ăm\s+\d{3,4}\b')),
    ('narrative-year-tcn', re.compile(r'\b[Nn]ăm\s+\d{1,4}\s+TCN\b')),
    ('bare-tcn', re.compile(r'\b\d{1,4}\s+TCN\b')),
    ('decade-range', re.compile(r'\b\d{4}\s*[-–—]\s*\d{4}\b')),
    ('reign-period', re.compile(r'\b(thời|triều|đời)\s+(vua\s+)?[A-ZĐÂÊÔƠƯÁÀẢÃẠ][^\s,.;]*', re.U)),
]
DOC_SOURCE = re.compile(r'^(TƯ LIỆU|Tư liệu)\b')
QUOTED_DOC = re.compile(r'(Chiếu|Hịch|Bình Ngô|Tuyên ngôn|Nam quốc)', re.U)


def load(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


def docs(d):
    for name in sorted(os.listdir(d)):
        if name.endswith('.json'):
            yield load(f'{d}/{name}')


def text_of(b):
    return b.get('text') or ''


def t1_date_styles(all_docs):
    """What date forms does the book print, and what does the rule see?"""
    per_lesson, totals, examples = [], Counter(), defaultdict(list)
    rule_events_total = mispromoted = 0
    for doc in all_docs:
        counts = Counter()
        for b in doc['blocks']:
            t = text_of(b)
            if not t:
                continue
            for name, rx in FORMS:
                for m in rx.finditer(t):
                    counts[name] += 1
                    if len(examples[name]) < 4:
                        examples[name].append(dict(lesson=doc['lesson'], block=hr._short(b['id']), match=m.group(0)[:40]))
        ev, mentions, _ = hr.derive_events(doc)
        rule_events_total += len(ev)
        # a mis-promotion: the rule made an event out of a parenthesis that is NOT a date
        # (a place gloss «(tỉnh Phú Thọ)» can never match YEARS, but a page/figure number could)
        for e in ev:
            if e['yearStart'] > 2100 or (e['era'] == 'CN' and e['yearStart'] < 30 and e['yearEnd'] < 30):
                mispromoted += 1
        totals.update(counts)
        per_lesson.append(dict(lesson=doc['lesson'], title=doc.get('title'), events=len(ev),
                               narrative=len(mentions), forms=dict(counts)))
    return dict(perLesson=per_lesson, totals=dict(totals.most_common()), examples={k: v for k, v in examples.items()},
                ruleEvents=rule_events_total, misPromoted=mispromoted)


def t2_quoted_documents(all_docs):
    """Attributions the rule finds, split by what they close: a story box, or a quoted document."""
    rows = []
    for doc in all_docs:
        attrs, _ = hr.derive_attributions(doc)
        blocks = {b['id']: b for b in doc['blocks']}
        for a in attrs:
            story_texts = [text_of(blocks[i]) for i in a['storyBlockIds'] if i in blocks]
            title = a.get('title') or ''
            kind = 'quoted-document' if (DOC_SOURCE.match(title) or any(QUOTED_DOC.search(x) for x in story_texts)
                                         or QUOTED_DOC.search(title)) else 'story'
            rows.append(dict(lesson=doc['lesson'], block=hr._short(a['attributionBlockId']), form=a['form'],
                             kind=kind, title=title[:48] or None, storyBlocks=len(a['storyBlockIds']),
                             withheldParts=len(a['withheldPartIds']), complete=a['complete'],
                             publisher=a['publisher'], year=a['year']))
    # the TƯ LIỆU boxes the book prints, whether or not the rule found an attribution for them
    tu_lieu = []
    for doc in all_docs:
        for b in doc['blocks']:
            if DOC_SOURCE.match(text_of(b)):
                tu_lieu.append(dict(lesson=doc['lesson'], block=hr._short(b['id']), type=b['type'],
                                    text=text_of(b)[:60]))
    return dict(rows=rows, tuLieuBoxes=tu_lieu,
                byKind=dict(Counter(r['kind'] for r in rows)))


def t2b_story_title_detector(all_docs):
    """How many story-box titles would an independent in-corpus signal OBJECT to? (a detector, not a truth
    claim — its precision is measured on Bài 8, where the print was read)."""
    import tone_repair_probe as tp
    ev = tp.evidence('book')
    rows = []
    for doc in all_docs:
        attrs, _ = hr.derive_attributions(doc)
        blocks = {b['id']: b for b in doc['blocks']}
        for a in attrs:
            tb = a.get('titleBlockId')
            if not tb or tb not in blocks:
                continue
            title = text_of(blocks[tb])
            cands = tp.candidates(title, ev, 2, 'dominant-majority', 2)
            rows.append(dict(lesson=doc['lesson'], block=hr._short(tb), title=title[:48],
                             objections=[f"{c['observed']}→{c['proposed']}" for c in cands]))
    flagged = [r for r in rows if r['objections']]
    return dict(titles=len(rows), flagged=len(flagged), rows=rows)


def t3_lesson_identity(all_docs):
    """Pages carrying more than one lesson, from the run's own boundaries."""
    page_owner = defaultdict(list)
    spans = []
    for doc in all_docs:
        prov = doc.get('provenance') or {}
        b = prov.get('boundary') or {}
        ps, pe = b.get('pageStart'), b.get('pageEnd')
        pages = b.get('pages') or (list(range(ps, pe + 1)) if ps and pe else [])
        spans.append(dict(lesson=doc['lesson'], pages=pages, confidence=b.get('confidence'),
                          source=b.get('source'), headerFound=b.get('headerFound')))
        for p in pages:
            page_owner[p].append(doc['lesson'])
    shared = {p: ls for p, ls in sorted(page_owner.items()) if len(ls) > 1}
    # the PHYSICAL test the page-range view cannot see: does a lesson's header sit BELOW learning content
    # on its own first page? Then that page is a two-lesson spread and the previous lesson lost its tail.
    spreads = []
    hdr = re.compile(r'^\s*B[ÀÁẢẠÃ]I\s+\d{1,2}\b')
    for doc in all_docs:
        b0 = ((doc.get('provenance') or {}).get('boundary') or {})
        first = b0.get('pageStart')
        if not first:
            continue
        header = next((b for b in doc['blocks']
                       if (b.get('sourceRef') or {}).get('pagePdf') == first and hdr.match(text_of(b))), None)
        if header is None:
            continue
        y = (header['sourceRef']['bbox'] or [0, 0, 0, 0])[1]
        above = [b for b in doc['blocks']
                 if (b.get('sourceRef') or {}).get('pagePdf') == first
                 and (b['sourceRef']['bbox'] or [0, 1, 0, 0])[1] + (b['sourceRef']['bbox'] or [0, 0, 0, 0])[3] < y
                 and b['type'] in ('paragraph', 'question', 'activity', 'heading', 'caption')]
        spreads.append(dict(lesson=doc['lesson'], firstPage=first, headerY=round(y, 3),
                            blocksAboveTheHeader=len(above),
                            anchors=[text_of(b)[:36] for b in above[:3]]))
    # for each shared page: does the document of each owner carry blocks of the OTHER lesson?
    detail = []
    for p, owners in shared.items():
        row = dict(page=p, lessons=owners, blocksPerLesson={})
        for doc in all_docs:
            if doc['lesson'] in owners:
                n = sum(1 for b in doc['blocks'] if (b.get('sourceRef') or {}).get('pagePdf') == p)
                w = sum(1 for b in doc.get('withheld', []) if (b.get('sourceRef') or {}).get('pagePdf') == p)
                row['blocksPerLesson'][str(doc['lesson'])] = dict(trusted=n, withheld=w)
        detail.append(row)
    return dict(spans=spans, sharedPages=detail, sharedPageCount=len(shared), headerSpreads=spreads,
                spreadsWithContentAbove=sum(1 for r in spreads if r['blocksAboveTheHeader']))


def render(rep):
    t1, t2, t3 = rep['t1'], rep['t2'], rep['t3']
    L = ['# Deliberate falsification of the History rules on the other 27 lessons (Lane C, round 5)', '',
         'Bounded to LS&ĐL 5, the round-5 run. Every number is measured on the bridged documents of the 28 '
         'lessons; nothing here is a coverage claim.', '',
         '## T1 — does `prose-dated-events-v1` survive a different date style?', '',
         f"The rule extracted **{t1['ruleEvents']} events across 28 lessons** "
         f"(mis-promoted, i.e. a non-date parenthesis turned into an event: {t1['misPromoted']}).", '',
         '**Date forms the book actually prints (occurrences over the 28 documents):**', '',
         '| form | occurrences | does the rule accept it? | example (lesson · block) |', '|---|---|---|---|']
    accepts = {'paren-year': 'YES — the only accepted form', 'century-tcn': 'no', 'century': 'no',
               'narrative-year': 'counted, never promoted (by design)', 'narrative-year-tcn': 'counted, never promoted',
               'bare-tcn': 'no (only inside parentheses)', 'decade-range': 'no (outside parentheses)',
               'reign-period': 'no'}
    for name, n in t1['totals'].items():
        ex = (t1['examples'].get(name) or [{}])[0]
        L.append(f"| `{name}` | {n} | {accepts.get(name, '?')} | {ex.get('match', '—')} "
                 f"({ex.get('lesson', '—')} · {ex.get('block', '—')}) |")
    L += ['', '**Per lesson:**', '', '| Bài | title | rule events | narrative years counted | date forms present |',
          '|---|---|---|---|---|']
    for r in t1['perLesson']:
        L.append(f"| {r['lesson']} | {(r['title'] or '')[:34]} | {r['events']} | {r['narrative']} | "
                 f"{', '.join(f'{k} {v}' for k, v in sorted(r['forms'].items())) or '—'} |")
    L += ['', '## T2 — does `story-attribution-v1` survive a quoted document instead of a story?', '',
          f"Attributions found: {json.dumps(t2['byKind'])}. «TƯ LIỆU» boxes the book prints: {len(t2['tuLieuBoxes'])}.", '',
          '| Bài | block | form | closes | story title | story blocks | withheld parts | complete | publisher | year |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for r in t2['rows']:
        L.append(f"| {r['lesson']} | {r['block']} | {r['form']} | {r['kind']} | {r['title'] or '—'} | "
                 f"{r['storyBlocks']} | {r['withheldParts']} | {r['complete']} | {r['publisher']} | {r['year']} |")
    if t2['tuLieuBoxes']:
        L += ['', '**«TƯ LIỆU» boxes:**', '', '| Bài | block | type | first words |', '|---|---|---|---|']
        for r in t2['tuLieuBoxes']:
            L.append(f"| {r['lesson']} | {r['block']} | {r['type']} | {r['text']} |")
    L += ['', '## T3 — does lesson identity survive a two-lesson spread?', '',
          f"Pages carrying more than one lesson: **{t3['sharedPageCount']}**.", '',
          '| PDF page | lessons | blocks each document keeps from that page (trusted / withheld) |', '|---|---|---|']
    for r in t3['sharedPages']:
        cells = ' · '.join(f"Bài {k}: {v['trusted']}/{v['withheld']}" for k, v in sorted(r['blocksPerLesson'].items(), key=lambda kv: int(kv[0])))
        L.append(f"| {r['page']} | {', '.join(str(x) for x in r['lessons'])} | {cells} |")
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--docs', default=DOCS)
    ap.add_argument('--out', default=f'{RUN}/report')
    ap.add_argument('--copy-md', default=None)
    a = ap.parse_args()
    all_docs = list(docs(a.docs))
    rep = dict(book=BOOK, lessons=len(all_docs), t1=t1_date_styles(all_docs),
               t2=t2_quoted_documents(all_docs), t2b=t2b_story_title_detector(all_docs),
               t3=t3_lesson_identity(all_docs))
    os.makedirs(a.out, exist_ok=True)
    with open(f'{a.out}/history-stress.json', 'w', encoding='utf-8') as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=2)
    md = render(rep)
    with open(f'{a.out}/history-stress.md', 'w', encoding='utf-8') as fh:
        fh.write(md)
    if a.copy_md:
        with open(a.copy_md, 'w', encoding='utf-8') as fh:
            fh.write(md)
    print(f'{a.out}/history-stress.md')
    print(f"  T1 events {rep['t1']['ruleEvents']} over {rep['lessons']} lessons; forms {rep['t1']['totals']}")
    print(f"  T2 attributions {rep['t2']['byKind']}; TƯ LIỆU boxes {len(rep['t2']['tuLieuBoxes'])}")
    print(f"  T2b story titles {rep['t2b']['titles']}, an independent signal objects to {rep['t2b']['flagged']}")
    print(f"  T3 shared pages {rep['t3']['sharedPageCount']}; header pages with content above the header {rep['t3']['spreadsWithContentAbove']}/{len(rep['t3']['headerSpreads'])}")


if __name__ == '__main__':
    main()
