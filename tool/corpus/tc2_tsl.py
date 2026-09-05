#!/usr/bin/env python3
"""TC-v2 — TRUSTED STRUCTURED LESSON (TSL) builder + Hybrid Smart Book projection (data only, no UI).

One document per attached lesson (book, lesson number), built from the SDM pages (tc2_sdm) and the
header-based attachment (tc2_attach):
  blocks[]      ordered TRUSTED learning blocks: id, page (pdf + printed), order, role {value, confidence,
                method}, text, bbox, heading_path, provenance {book, page, bbox, extraction, ocr_conf,
                agreement.text_sim, pipeline, sdm_version}, refers_figure
  withheld[]    every non-trusted learning block: id, page, bbox, role, reasons[], text_len (NO text of
                answer keys / teacher text is carried — only bbox + reason + provenance)
  figures[]     picture regions with bbox + caption block id
  boundary      {page_start, page_end, pages[], attach_methods{}, confidence = min page confidence,
                header_found, toc_source}
  sourceability FULL (every learning block on the lesson's pages is trusted or furniture/figure) ·
                PARTIAL (≥ 1 trusted learning block) · NONE
  hybridSmartBook  two projections of the same block sequence —
                with_images: withheld region → {kind: source_crop, page, bbox, reason} (a crop the
                             client would render IF page-image delivery is licensed — LEGAL GATE, open)
                no_images:   withheld region → {kind: withheld_ref, reason, page_printed, text:
                             "WITHHELD: <reason> — see SGK page N"} — fully functional without any
                             page image
                + counts per mode (native / crop / withheld_ref)
Invariants: no block with an answer_leak / teacher_text reason is ever serialised with its text; SGV
lessons are written to a separate tree (sgv/) and never merged into an SGK lesson document.

Usage: python3 tool/corpus/tc2_tsl.py --pipeline tc2-p1 <book>…   → poc-out/trusted-corpus/tc-v2/<pipeline>/lessons/<book>/bai-NN.tsl.json
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tc2_attach  # noqa: E402
import tc2_paths  # noqa: E402

ROOT = tc2_paths.ROOT
NEVER_TEXT = {'answer_leak', 'teacher_text'}
FURNITURE = {'page_number', 'running_head', 'figure', 'empty', 'figure_text'}


def out_root(pipeline):
    return tc2_paths.out_root(pipeline)


def build_book(book, pipeline='tc2-p1', write=True):
    att = tc2_attach.load_attach(book, pipeline)
    if att is None:
        att = tc2_attach.attach_book(book, pipeline)
    prec = {r['page']: r for r in att['pages']}
    titles = {l['number']: l.get('title') for l in att['lessons']}
    sdm_files = sorted(glob.glob(f'{out_root(pipeline)}/sdm/{book}/p*.sdm.json'), key=lambda f: int(re.search(r'p(\d+)', f).group(1)))
    lessons = defaultdict(lambda: dict(blocks=[], withheld=[], figures=[], pages=[], methods=Counter(), confs=[], all_learning=0, no_lesson_blocks=0))
    no_lesson_pages = []
    for f in sdm_files:
        s = json.load(open(f))
        page = s['page']; pr = prec.get(page)
        if pr is None or pr.get('lesson') is None and not (pr and pr.get('header')):
            no_lesson_pages.append(page)
        for ob in s['blocks']:
            n, method = tc2_attach.lesson_for_block(pr, ob['bbox'])
            if n is None:
                continue
            L = lessons[n]
            if page not in L['pages']:
                L['pages'].append(page); L['methods'][method] += 1; L['confs'].append(pr.get('confidence', 0) if pr else 0)
            role = ob['role']['value']
            if role in FURNITURE:
                continue
            L['all_learning'] += 1
            prov = dict(book=book, page_pdf=page, page_printed=s.get('printed_page'), bbox=ob['bbox'], extraction=ob['extraction'], ocr_conf=ob['ocr_conf'],
                        text_sim=ob['agreement']['text_sim'], pipeline=pipeline, sdm_version=s.get('sdm_version'), block_id=ob['id'])
            if ob['trust']['status'] == 'TRUSTED':
                L['blocks'].append(dict(id=ob['id'], page=page, page_printed=s.get('printed_page'), order=ob['order'], role=dict(value=role, coarse=ob['role']['coarse'], confidence=ob['role']['confidence'], method=ob['role']['method']),
                                        text=ob['text'], bbox=ob['bbox'], heading_path=ob['heading_path'], refers_figure=ob['refers_figure'], enumerator_restored=ob['enumerator_restored'], provenance=prov))
            else:
                L['withheld'].append(dict(id=ob['id'], page=page, page_printed=s.get('printed_page'), order=ob['order'], role=role, bbox=ob['bbox'], reasons=ob['trust']['reasons'], status=ob['trust']['status'],
                                          text_len=len(ob['text'] or ''), provenance=prov, text=None if (set(ob['trust']['reasons']) & NEVER_TEXT) else None))
        for fg in s.get('figures', []):
            n = pr.get('lesson') if pr else None
            if n is not None:
                lessons[n]['figures'].append(dict(id=fg['id'], page=page, bbox=fg['bbox'], caption=fg['caption'], labels=len(fg['labels'])))
    docs = []
    for n in sorted(lessons):
        L = lessons[n]
        L['blocks'].sort(key=lambda b: (b['page'], b['order'])); L['withheld'].sort(key=lambda b: (b['page'], b['order']))
        trusted_learning = len(L['blocks']); withheld_learning = len(L['withheld'])
        src = 'FULL' if trusted_learning and withheld_learning == 0 else ('PARTIAL' if trusted_learning else 'NONE')
        seq = sorted([dict(kind='native', page=b['page'], order=b['order'], id=b['id']) for b in L['blocks']] + [dict(kind='withheld', page=w['page'], order=w['order'], id=w['id'], bbox=w['bbox'], reasons=w['reasons'], page_printed=w['page_printed']) for w in L['withheld']], key=lambda x: (x['page'], x['order']))
        with_images = [(dict(kind='native', block=x['id']) if x['kind'] == 'native' else dict(kind='source_crop', page=x['page'], bbox=x['bbox'], reason=','.join(x['reasons']), licence_gate='page-image delivery UNRESOLVED (OQ8)')) for x in seq]
        no_images = [(dict(kind='native', block=x['id']) if x['kind'] == 'native' else dict(kind='withheld_ref', reason=','.join(x['reasons']), page_printed=x['page_printed'], page_pdf=x['page'], text=f"WITHHELD: {','.join(x['reasons'])} — see SGK page {x['page_printed'] if x['page_printed'] is not None else '?'}")) for x in seq]
        hsb = dict(with_images=with_images, no_images=no_images,
                   counts=dict(native=sum(1 for x in seq if x['kind'] == 'native'), source_crop=sum(1 for x in seq if x['kind'] != 'native'), withheld_ref=sum(1 for x in seq if x['kind'] != 'native'),
                               crops_by_reason=dict(Counter(','.join(x['reasons']) for x in seq if x['kind'] != 'native'))))
        header_pages = [p for p in L['pages'] if prec.get(p, {}).get('method') == 'header' and prec[p].get('lesson') == n]
        doc = dict(book=book, lesson=n, title=titles.get(n), pipeline=pipeline, docType=att.get('docType'),
                   boundary=dict(page_start=min(L['pages']), page_end=max(L['pages']), pages=sorted(L['pages']), attach_methods=dict(L['methods']), confidence=round(min(L['confs']) if L['confs'] else 0, 2),
                                 header_found=bool(header_pages), header_page=header_pages[0] if header_pages else None, source=next((l['source'] for l in att['lessons'] if l['number'] == n), None)),
                   sourceability=src, stats=dict(learning_blocks=L['all_learning'], trusted=trusted_learning, withheld=withheld_learning, withheld_by_reason=dict(Counter(r for w in L['withheld'] for r in w['reasons'])),
                                                 roles_trusted=dict(Counter(b['role']['value'] for b in L['blocks'])), figures=len(L['figures'])),
                   blocks=L['blocks'], withheld=L['withheld'], figures=L['figures'], hybridSmartBook=hsb, answer_keys_included=False)
        docs.append(doc)
    if write:
        d = f'{out_root(pipeline)}/lessons/{book}'; os.makedirs(d, exist_ok=True)
        for doc in docs:
            json.dump(doc, open(f'{d}/bai-{doc["lesson"]:02d}.tsl.json', 'w'), ensure_ascii=False)
    summary = dict(book=book, lessons=len(docs), FULL=sum(1 for d in docs if d['sourceability'] == 'FULL'), PARTIAL=sum(1 for d in docs if d['sourceability'] == 'PARTIAL'), NONE=sum(1 for d in docs if d['sourceability'] == 'NONE'),
                   header_found=sum(1 for d in docs if d['boundary']['header_found']), pages_no_lesson=len(no_lesson_pages),
                   trusted_blocks=sum(d['stats']['trusted'] for d in docs), withheld_blocks=sum(d['stats']['withheld'] for d in docs),
                   hsb_native=sum(d['hybridSmartBook']['counts']['native'] for d in docs), hsb_crop_or_ref=sum(d['hybridSmartBook']['counts']['source_crop'] for d in docs),
                   withheld_by_reason=dict(sum((Counter(d['stats']['withheld_by_reason']) for d in docs), Counter())))
    return docs, summary


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pipeline', default='tc2-p1'); ap.add_argument('books', nargs='+')
    ap.add_argument('--out', default=None, help='pipeline output root (default poc-out/trusted-corpus/tc-v2/<pipeline>; env TC2_OUT_ROOT)')
    a = ap.parse_args()
    if a.out:
        tc2_paths.set_out_root(a.out)
    for b in a.books:
        _, s = build_book(b, a.pipeline)
        print(json.dumps(s, ensure_ascii=False))


if __name__ == '__main__':
    main()
