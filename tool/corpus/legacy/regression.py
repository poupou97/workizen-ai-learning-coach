#!/usr/bin/env python3
"""Round 5 · Lane D — the SURVIVING-DEFECT REGRESSION CORPUS (Founder §9 item 3).

Three defects survived BOTH round-4 builds (`legacy-b1` = tc2-p1 and the `tc2-p2` re-run)
and one more was uncovered by the round-4 colour-veto fix. They are named, with block ids,
in `docs/research/legacy-reprocess/PIPELINE-REQUESTS-FROM-LEGACY.md`. This file turns them
into a check that runs against ANY batch output, so "did the round fix them?" is answered
by the build rather than by reading a report.

Each defect is a **deterministic probe over the pipeline's own output** — never a judgement,
never an annotation. A probe returns one of:

    PRESENT   the defect is reproduced exactly as described
    FIXED     the region is no longer served as trusted (withheld, unattached, or absent)
    PARTIAL   the guard fires on some instances of the class and not on others — the defect is
              reduced, not closed
    CHANGED   the region is still served but not with the recorded defect — the probe
              cannot call it fixed and says so rather than guessing
    ABSENT    the lesson/page is not in this batch at all (the probe did not run)

`CHANGED` exists because "the text is different now" is not "the text is right now"; only an
audit can say that, and this file never pretends to.

    python3 tool/corpus/legacy/regression.py check --batch-dir DIR --pipeline ID [--out FILE] [--md FILE]
    python3 tool/corpus/legacy/regression.py check --batch-dir DIR --pipeline ID --compare-to FILE
"""
import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

SCHEMA = 'lane-d-regression-v1'

# ---------------------------------------------------------------------------
# The defect corpus. `where` locates the region; `probe` decides PRESENT/FIXED/CHANGED.
# Every entry cites the round-4 request it comes from and the build it was last seen on.
DEFECTS = [
    dict(
        id='R1-imprint-as-lesson-body',
        title="a book's imprint page is served as the last lesson's body",
        request='R1', priority='P0', last_seen='tc2-p2 (PR #77 @ cb60cde)',
        book='04-sgk-toan-4-tap-hai', lesson=73, page_pdf=121,
        detail="p122 (back cover) was fixed on tc2-p2; p121 (imprint: «Biên tập…», «Trình bày bìa…», "
               "«Cơ sở in:») stayed attached to Bài 73 and served as trusted body/activity.",
        kind='page_attached_and_served',
    ),
    dict(
        id='R2-fraction-fragment-served',
        title="a destroyed fraction is served as content (`b) 10 +` for `b) 3/10 + 5/21`)",
        request='R2', priority='P0', last_seen='tc2-p2 (PR #77 @ cb60cde)',
        book='05-sgk-toan-5-tap-mot', lesson=6, page_pdf=22,
        detail="the number guard does not fire on a bare denominator or on a block ending in a dangling operator.",
        kind='text_pattern',
        # a served block that is a lone integer, or that ends with a dangling arithmetic operator
        patterns=[r'^\s*[a-dà-ỹ]\)\s*\d+\s*[+\-−×÷:x*]\s*$', r'^\s*\d{1,3}\s*$', r'[+\-−×÷]\s*$'],
    ),
    dict(
        id='R3-tone-slip-in-lesson-title',
        title='the lesson title is served with tone slips that turn its key terms into other words',
        request='R3', priority='P0', last_seen='tc2-p2 (PR #77 @ cb60cde)',
        book='05-sgk-toan-5-tap-mot', lesson=6, page_pdf=21,
        detail="«HAI PHÂN» served as «HẠI PHẬN» in an all-caps heading; agree_tones cannot see it because "
               "both extractors agree on the same wrong tones.",
        kind='exact_text',
        # The printed title, and the corrupted form recorded in round 4. Compared on the
        # accent-bearing form: a served heading equal to `corrupt` is the defect reproduced.
        printed='CỘNG, TRỪ HAI PHÂN SỐ KHÁC MẪU SỐ',
        corrupt_tokens=['HẠI PHẬN', 'HẠI PHÂN', 'HAI PHẬN'],
    ),
    dict(
        id='R7c-verse-flattened-to-prose',
        title='verse lines are served joined into a single prose run',
        request='R7c', priority='P0', last_seen='tc2-p2 (PR #77 @ cb60cde) — uncovered by the R7b colour-veto fix',
        book='05-sgk-tieng-viet-5-tap-mot', lesson=25, page_pdf=None,
        detail="the Bài 25 poem came back when the page-level colour veto became block-level, and came back "
               "with its line breaks gone. Lane A's `1960d85 corpus(sdm): withhold verse rather than serve it "
               "joined into prose` claims this; the probe checks the claim on the output.",
        kind='verse_flattened',
    ),
]

VERSE_HINT = re.compile(r'\b(bài thơ|khổ thơ|thơ)\b', re.IGNORECASE)
IMPRINT = ('chịu trách nhiệm xuất bản', 'biên tập', 'trình bày bìa', 'cơ sở in', 'isbn', 'giá:', 'in xong')


def _nfc(s):
    return unicodedata.normalize('NFC', s or '')


def load_tsl(batch_dir, pipeline, book, lesson):
    p = f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{pipeline}/lessons/{book}/bai-{int(lesson):02d}.tsl.json'
    return common.load_json(p), p


# ---------------------------------------------------------------------------- probes
def probe_page_attached_and_served(tsl, d):
    """The defect is the PAGE being attached AND carrying trusted blocks."""
    page = d['page_pdf']
    served = [b for b in tsl.get('blocks', []) if b.get('page') == page]
    withheld = [w for w in tsl.get('withheld', []) if w.get('page') == page]
    pages = (tsl.get('boundary') or {}).get('pages') or []
    attached = page in pages
    imprintish = [b for b in served if any(k in _nfc(b.get('text', '')).lower() for k in IMPRINT)]
    if not attached:
        return 'FIXED', f'pdf page {page} is no longer attached to the lesson (boundary pages {pages[:1]}…{pages[-1:]})', dict(
            attached=False, servedBlocks=0, withheldRegions=len(withheld))
    if not served:
        return 'FIXED', f'pdf page {page} is still attached but serves 0 trusted blocks ({len(withheld)} withheld)', dict(
            attached=True, servedBlocks=0, withheldRegions=len(withheld))
    if imprintish:
        return 'PRESENT', (f'pdf page {page} attached and serving {len(served)} trusted block(s), '
                           f'{len(imprintish)} of them imprint text'), dict(
            attached=True, servedBlocks=len(served), imprintBlocks=len(imprintish),
            ids=[b['id'] for b in imprintish][:6], roles=sorted({b['role']['value'] for b in imprintish}))
    return 'CHANGED', (f'pdf page {page} is still attached and serves {len(served)} trusted block(s), but none '
                       f'matches the recorded imprint phrases — an audit, not this probe, must judge them'), dict(
        attached=True, servedBlocks=len(served), imprintBlocks=0, ids=[b['id'] for b in served][:6])


def probe_text_pattern(tsl, d):
    page = d['page_pdf']
    pats = [re.compile(p) for p in d['patterns']]
    served = [b for b in tsl.get('blocks', []) if b.get('page') == page]
    hits = [b for b in served if any(p.search(_nfc(b.get('text', ''))) for p in pats)]
    if not served:
        return 'FIXED', f'pdf page {page} serves no trusted block at all', dict(servedBlocks=0)
    if hits:
        return 'PRESENT', f'{len(hits)} served block(s) on pdf page {page} match the fragment pattern', dict(
            servedBlocks=len(served), hits=[dict(id=b['id'], role=b['role']['value'], text=_nfc(b['text'])[:40]) for b in hits])
    return 'FIXED', (f'pdf page {page} serves {len(served)} block(s), none of them a bare integer or a block '
                     f'ending in a dangling operator'), dict(servedBlocks=len(served))


def probe_exact_text(tsl, d):
    page = d['page_pdf']
    served = [b for b in tsl.get('blocks', []) if b.get('page') == page]
    headings = [b for b in served if b['role']['value'] in ('heading', 'title')]
    corrupt = [b for b in headings if any(t in _nfc(b.get('text', '')) for t in d['corrupt_tokens'])]
    exact = [b for b in headings if _nfc(b.get('text', '')).strip() == _nfc(d['printed'])]
    if corrupt:
        return 'PRESENT', f'{len(corrupt)} heading(s) on pdf page {page} carry the recorded tone corruption', dict(
            hits=[dict(id=b['id'], text=_nfc(b['text'])[:60], conf=b['role'].get('confidence')) for b in corrupt])
    if exact:
        return 'FIXED', f'the lesson title is served exactly as printed on pdf page {page}', dict(
            ids=[b['id'] for b in exact])
    if not headings:
        return 'FIXED', f'pdf page {page} serves no heading at all ({len(served)} other trusted blocks)', dict(
            servedBlocks=len(served))
    return 'CHANGED', (f'pdf page {page} serves {len(headings)} heading(s), none carrying the recorded corruption '
                       f'and none matching the printed title exactly — an audit must judge them'), dict(
        headings=[dict(id=b['id'], text=_nfc(b['text'])[:60]) for b in headings])


def probe_verse_flattened(tsl, d):
    """A served block is 'verse joined into prose' when it is one long single-line run whose
    source lines were separate. The TSL keeps no line breaks, so the probe uses the pipeline's
    own signal: a poetry lesson serving long multi-clause body blocks with no withheld verse
    region is the shape the defect had. Reported with counts, never as a fidelity verdict."""
    blocks = tsl.get('blocks', [])
    withheld = tsl.get('withheld', [])
    verse_withheld = [w for w in withheld if any('verse' in str(r).lower() or 'line_structure' in str(r).lower()
                                                 for r in (w.get('reasons') or []))]
    long_body = [b for b in blocks
                 if b['role']['value'] in ('body', 'sidebar')
                 and len(_nfc(b.get('text', ''))) >= 120
                 and '\n' not in (b.get('text') or '')]
    if verse_withheld and not long_body:
        return 'FIXED', (f'{len(verse_withheld)} region(s) withheld with a verse / line-structure reason and no '
                         f'long single-run body block served'), dict(
            withheldVerseRegions=len(verse_withheld),
            reasons=sorted({r for w in verse_withheld for r in (w.get('reasons') or [])}),
            longBodyBlocks=0)
    if verse_withheld:
        # The blind restore audit judged `n20260906-0065` — a four-line stanza served as one prose run —
        # WRONG on this very build. A probe that called the class FIXED because *some* verse is withheld
        # would have laundered that away. Some verse withheld and some still joined is PARTIAL.
        return 'PARTIAL', (f'{len(verse_withheld)} region(s) withheld with a verse / line-structure reason, but '
                           f'{len(long_body)} long single-run body block(s) are still served — the guard fires on '
                           f'some verse and not on all of it'), dict(
            withheldVerseRegions=len(verse_withheld),
            reasons=sorted({r for w in verse_withheld for r in (w.get('reasons') or [])}),
            longBodyBlocks=len(long_body))
    if long_body:
        return 'CHANGED', (f'no verse/line-structure withhold, and {len(long_body)} long single-run body block(s) '
                           f'are served — the shape the defect had; only an audit can say whether any is verse'), dict(
            longBodyBlocks=len(long_body), ids=[b['id'] for b in long_body][:6])
    return 'FIXED', 'no verse/line-structure withhold and no long single-run body block', dict(longBodyBlocks=0)


PROBES = {
    'page_attached_and_served': probe_page_attached_and_served,
    'text_pattern': probe_text_pattern,
    'exact_text': probe_exact_text,
    'verse_flattened': probe_verse_flattened,
}


def check(batch_dir, pipeline):
    rows = []
    for d in DEFECTS:
        tsl, path = load_tsl(batch_dir, pipeline, d['book'], d['lesson'])
        if not tsl:
            rows.append(dict(defect=d['id'], request=d['request'], priority=d['priority'], title=d['title'],
                             verdict='ABSENT', evidence=f'no TSL for {d["book"]} Bài {d["lesson"]} in this batch',
                             tslPath=path, detail=d['detail'], lastSeen=d['last_seen'], data={}))
            continue
        verdict, evidence, data = PROBES[d['kind']](tsl, d)
        rows.append(dict(defect=d['id'], request=d['request'], priority=d['priority'], title=d['title'],
                         verdict=verdict, evidence=evidence, tslPath=path, tslSha256=common.sha256_file(path),
                         book=d['book'], lesson=d['lesson'], pagePdf=d.get('page_pdf'),
                         detail=d['detail'], lastSeen=d['last_seen'], data=data))
    return rows


def cmd_tail_scan(a):
    """The R1 CLASS, not the R1 row: on every lesson of a batch, is the book's tail attached?

    R1 is one page of one book. The mechanism behind it — a header-based `continuation` rule with no
    upper bound handing a book's non-lesson tail to its last lesson — is general, so a fix that only
    moves p121 of Toan 4 tap hai is not a fix. This scan asks the same question of every lesson in a
    batch: which attached pages carry NO printed page number (the pipeline's own signal for tail
    matter), and do any of them serve imprint text?
    """
    spec = common.load_json(f'{a.batch_dir}/batch-spec.json', {})
    rows = []
    for L in spec.get('lessons', []):
        tsl, path = load_tsl(a.batch_dir, a.pipeline, L['book'], L['lesson'])
        if not tsl:
            continue
        pages = (tsl.get('boundary') or {}).get('pages') or []
        by_page = {}
        for b in tsl.get('blocks', []):
            by_page.setdefault(b.get('page'), []).append(b)
        unnumbered, imprint_pages = [], []
        for pg in pages:
            blocks = by_page.get(pg, [])
            if blocks and all(b.get('page_printed') is None for b in blocks):
                unnumbered.append(pg)
            if any(k in _nfc(b.get('text', '')).lower() for b in blocks for k in IMPRINT):
                imprint_pages.append(pg)
        rows.append(dict(book=L['book'], lesson=L['lesson'],
                         lastLessonOfBook=bool('last_lesson_of_book' in (L.get('risk') or [])),
                         attachedPages=pages, servedPages=sorted(x for x in by_page if x is not None),
                         attachedPagesWithoutPrintedNumber=unnumbered,
                         attachedPagesServingImprintText=imprint_pages,
                         tailDefect=bool(imprint_pages)))
    out = dict(schema=SCHEMA + '/tail-scan', batchDir=os.path.abspath(a.batch_dir), pipeline=a.pipeline,
               note='an attached page with no printed page number is a candidate tail page; imprint text served '
                    'from one is the R1 class reproduced on a different book',
               lessonsScanned=len(rows), lessonsWithTailDefect=sum(1 for r in rows if r['tailDefect']), rows=rows)
    if a.out:
        common.dump_json(out, a.out)
        print(f'-> {a.out}')
    for r in rows:
        mark = 'X' if r['tailDefect'] else ('?' if r['attachedPagesWithoutPrintedNumber'] else 'o')
        print(f"{mark} {r['book']} Bai {r['lesson']}: attached {r['attachedPages'][:1]}..{r['attachedPages'][-1:]} | "
              f"unnumbered attached {r['attachedPagesWithoutPrintedNumber']} | imprint served {r['attachedPagesServingImprintText']}")
    print(f"  {out['lessonsWithTailDefect']}/{out['lessonsScanned']} lesson(s) serve imprint text from an attached page")
    return 0


def cmd_pack_scan(a):
    """Defect 6 of the 97-row evaluation set, asked of the SHIPPED PACKS rather than of a TSL.

    «imprint / back matter -> lesson heading» is an ATTACHMENT regression, and a pack rebuild is
    exactly where a wrong lesson heading becomes shipped content. The TSL probes above look at the
    research pipeline; this one looks at `assets/pack/lesson-index-g<N>.json`, which is what an APK
    would carry. Two independent signals, both deterministic:

      IMPRINT TEXT   any activity string containing a publishing-credit phrase or a product code
      BEYOND RANGE   an activity whose printed page lies outside its lesson's TOC range for that
                     book, i.e. the pages a header-based `continuation` rule can over-reach into

    A pack is only as good as the last page it will hand a child.
    """
    import glob as _glob
    sys.path.insert(0, os.path.join(common.REPO_ROOT, 'tool', 'corpus', 'legacy'))
    sys.path.insert(0, os.path.join(common.REPO_ROOT, 'tool', 'ui'))
    import packs as _packs
    import lesson_attach as _attach

    docs = (common.load_json(f'{common.MAIN_ROOT}/poc-out/graph/curriculum-structure.json') or {}).get('documents', [])
    # The range half of the scan uses the BUILDER'S OWN attachment rule rather than a second
    # implementation of it. Re-deriving "is this page inside the lesson" here produced 52 flags on the
    # rebuilt packs, 41 of them the known TV5 tap hai TOC offset that `capped-toc-v2` exists to absorb —
    # a defect count that was really a measurement of my own duplicate rule. One rule, one owner.
    reg = _attach.AttachRegistry(docs)
    last_start = {}
    for d in docs:
        starts = [l['pageStart'] for l in (d.get('lessons') or []) if l.get('pageStart') is not None]
        last_start[d['sourceDocumentId']] = max(starts) if starts else None

    TEXT_KEYS = ('expr', 'passage', 'prompt', 'excerpt', 'attribution', 'samGloss', 'title', 'caption',
                 'chuanBi', 'printedCaption', 'lessonTitle')
    IMPRINT_PACK = IMPRINT + ('ma so:', 'nha xuat ban giao duc', 'chiu trach nhiem noi dung', 'ban quyen')
    rows, per_grade = [], {}
    for path in sorted(_glob.glob(os.path.join(a.pack_dir, 'lesson-index-g*.json'))):
        pack = common.load_json(path) or {}
        g = pack.get('grade')
        hits = []
        for fam, spec in _packs.FAMILIES.items():
            blob = pack.get(fam)
            if not blob:
                continue
            items = ([(int(k), e) for k, arr in blob.items() for e in (arr or [])]
                     if spec['shape'] == 'by_lesson' else [(e.get('lesson'), e) for e in blob])
            for lesson, e in items:
                e = e or {}
                book = e.get('book') or e.get('sourceDocumentId') or ''
                strings = []
                for k in TEXT_KEYS:
                    v = e.get(k)
                    if isinstance(v, str):
                        strings.append(v)
                    elif isinstance(v, list):
                        strings += [x for x in v if isinstance(x, str)]
                for q in (e.get('questions') or []):
                    if isinstance(q, dict) and isinstance(q.get('prompt'), str):
                        strings.append(q['prompt'])
                low = _nfc(' '.join(strings)).lower()
                imprint = sorted({k for k in IMPRINT_PACK if k in low})
                page = e.get('page') or e.get('pagePrinted')
                # BACK MATTER: past the last lesson's own start is where a book's tail lives. This is the
                # defect-6 shape, and it is deliberately narrower than "outside my lesson's TOC range".
                ls = last_start.get(book)
                past_last = bool(page is not None and ls is not None and lesson is not None
                                 and page > ls and reg.book(book) and lesson != max(
                                     [n for n in (reg.book(book).canonical or {None})] or [None], default=None))
                reason = None
                if lesson is not None and book:
                    try:
                        _keep, reason = reg.book(book).check_upstream(lesson, page)
                    except Exception:  # noqa: BLE001 - a book with no ranges simply has no verdict
                        reason = 'no_verdict'
                if imprint or past_last:
                    hits.append(dict(grade=g, family=fam, book=book, lesson=lesson, page=page,
                                     attachReason=reason, imprintPhrases=imprint, pastLastLessonStart=past_last))
        per_grade[str(g)] = dict(activities=_packs.pack_metrics(pack)['activitiesTotal'],
                                 flagged=len(hits),
                                 imprint=sum(1 for h in hits if h['imprintPhrases']),
                                 pastLastLessonStart=sum(1 for h in hits if h['pastLastLessonStart']),
                                 packVersion=(pack.get('buildProvenance') or {}).get('packVersion'))
        rows += hits
    total_acts = sum(v['activities'] for v in per_grade.values())
    n_imp = sum(1 for r in rows if r['imprintPhrases'])
    out = dict(schema=SCHEMA + '/pack-scan', packDir=os.path.abspath(a.pack_dir),
               defect='evaluation-set defect 6 - imprint / back matter reaching a lesson, asked of the '
                      'SHIPPED packs rather than of the research pipeline',
               method='imprint phrases in any activity string; and any activity whose printed page lies past '
                      'the LAST lesson start of its book (where a book tail lives). The per-lesson range check '
                      'is delegated to tool/ui/lesson_attach - the builder\'s own rule - and reported as its '
                      'reason code, never re-implemented here.',
               activitiesScanned=total_acts, flagged=len(rows),
               imprintActivities=n_imp,
               pastLastLessonStartActivities=sum(1 for r in rows if r['pastLastLessonStart']),
               verdict=('PRESENT - imprint text is in the shipped packs' if n_imp else
                        'ABSENT - no imprint or back-matter text reaches the shipped packs'),
               perGrade=per_grade, rows=rows)
    if a.out:
        common.dump_json(out, a.out)
        print(f'-> {a.out}')
    for g in sorted(per_grade, key=int):
        v = per_grade[g]
        mark = 'X' if v['imprint'] else ('?' if v['pastLastLessonStart'] else 'o')
        print(f"{mark} g{g}: {v['activities']} activities, flagged {v['flagged']} "
              f"(imprint {v['imprint']}, past last lesson start {v['pastLastLessonStart']})  {v['packVersion']}")
    print(f"  {out['verdict']} - {n_imp} imprint activity(ies) and "
          f"{out['pastLastLessonStartActivities']} past-last-lesson activity(ies) of {total_acts} scanned")
    return 0


def cmd_check(a):
    rows = check(a.batch_dir, a.pipeline)
    prev = common.load_json(a.compare_to) if a.compare_to else None
    prev_by_id = {r['defect']: r['verdict'] for r in (prev or {}).get('defects', [])} if prev else {}
    for r in rows:
        if r['defect'] in prev_by_id:
            r['verdictBefore'] = prev_by_id[r['defect']]
            r['moved'] = prev_by_id[r['defect']] != r['verdict']
    out = dict(schema=SCHEMA, checkedAt=common.load_json.__module__ and __import__('datetime').datetime.now(
        __import__('datetime').timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        batchDir=os.path.abspath(a.batch_dir), pipeline=a.pipeline,
        comparedTo=os.path.abspath(a.compare_to) if a.compare_to else None,
        note='PRESENT / FIXED / CHANGED / ABSENT are probes over the pipeline output. CHANGED means the region '
             'is still served but not with the recorded defect — it is NOT a claim that the block is now correct.',
        counts={v: sum(1 for r in rows if r['verdict'] == v) for v in ('PRESENT', 'PARTIAL', 'FIXED', 'CHANGED', 'ABSENT')},
        defects=rows)
    if a.out:
        common.dump_json(out, a.out)
        print(f'→ {a.out}')
    for r in rows:
        mark = {'PRESENT': '✗', 'PARTIAL': '~', 'FIXED': '✓', 'CHANGED': '?', 'ABSENT': '–'}[r['verdict']]
        was = f"  (was {r['verdictBefore']})" if 'verdictBefore' in r else ''
        print(f"{mark} {r['request']:4s} {r['verdict']:8s} {r['defect']}{was}")
        print(f'       {r["evidence"]}')
    print('  ' + ' · '.join(f'{k} {v}' for k, v in out['counts'].items() if v))
    if a.md:
        L = ['| request | defect | verdict | evidence |', '|---|---|---|---|']
        for r in rows:
            L.append(f'| **{r["request"]}** | {r["title"]} | **{r["verdict"]}** | {r["evidence"]} |')
        os.makedirs(os.path.dirname(os.path.abspath(a.md)), exist_ok=True)
        open(a.md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
        print(f'markdown → {a.md}')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('check')
    s.add_argument('--batch-dir', required=True)
    s.add_argument('--pipeline', required=True)
    s.add_argument('--out', default='')
    s.add_argument('--md', default='')
    s.add_argument('--compare-to', default='')
    s.set_defaults(fn=cmd_check)
    s = sub.add_parser('tail-scan')
    s.add_argument('--batch-dir', required=True)
    s.add_argument('--pipeline', required=True)
    s.add_argument('--out', default='')
    s.set_defaults(fn=cmd_tail_scan)
    s = sub.add_parser('pack-scan')
    s.add_argument('--pack-dir', default=os.path.join(common.REPO_ROOT, 'assets', 'pack'))
    s.add_argument('--out', default='')
    s.set_defaults(fn=cmd_pack_scan)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
