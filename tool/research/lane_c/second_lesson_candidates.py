#!/usr/bin/env python3
"""LANE C — census of the SECOND GOLDEN LESSON candidates (no pack, no fixture).

For every candidate (book, lesson number) this script MEASURES from data on disk:
  - lesson identity: TOC `pageStart` (printed) → PDF range via the router's
    printed→PDF offset rule; the printed «Bài N» header actually found on the
    OCR lines inside/around that range (tc2_attach-style, lite) so the TOC
    counter can be checked against the book;
  - layout hard features per page (TC-v1 census) and, where WAL-206 ran, the
    XY-cut page gate verdict (poc-out/layout);
  - the old-extractor units attached to the lesson (units-k12): roles,
    27-pattern labels (fable classify), lexical SHAPE markers (HYPOTHESIS);
  - SGV: units-k12 SGV units whose `lesson` equals the candidate's number, and
    the answer-key / objective lexicon hits among them (marker counts only —
    D4: no SGV text is copied out);
  - pack wiring for (book, lesson) in assets/pack;
  - gold pages (TC-v1/v2) inside the PDF range.

Read-only. Writes poc-out/round3/lane-c/second-lesson-candidates.{json,md}.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'corpus'))
from common import dump, load_census_pages, load_curriculum, load_layout_page, load_ocr_page, load_pack_index, load_units, pct, printed_to_pdf_offset, root, shape_hits, write_md  # noqa: E402
from fable_activity_taxonomy import CATALOG, NOISE, STAGE_ONLY, classify  # noqa: E402

# (book, lesson number as in curriculum-structure, modality label, why it is on the list)
CANDIDATES = [
    ('05-sgk-lich-su-va-dia-li-5', 8, 'History · timeline + source reasoning', 'four dated uprisings (40 → 938) + «Tư liệu»; SourceReader family'),
    ('05-sgk-lich-su-va-dia-li-5', 9, 'History · source reasoning (Chiếu dời đô)', 'suSources already wired for this lesson; dates 1009/1010'),
    ('05-sgk-lich-su-va-dia-li-5', 15, 'History · campaign timeline + map', 'Điện Biên Phủ 1954: three dated phases + lược đồ'),
    ('06-sgk-toan-6-tap-mot', 9, 'Math · rule + deterministic validator', 'Dấu hiệu chia hết — integer-only rules; same learner persona (Lớp 6)'),
    ('05-sgk-toan-5-tap-mot', 25, 'Math · formula + method', 'Diện tích hình tam giác — formula (math_guard) + figure; Deep path already covers Bài 6 fractions'),
    ('05-sgk-tieng-viet-5-tap-hai', 3, 'Language · reading (poem) + comprehension', 'Đọc: Hạt gạo làng ta — ReaderScreen family; TV5 SGV tập hai exists'),
    ('05-sgk-tieng-viet-5-tap-hai', 18, 'Language · writing (argument paragraph)', 'Viết: Tìm ý cho đoạn văn nêu ý kiến tán thành — ComposeLite family'),
    ('06-sgk-tin-hoc-6', 1, 'Informatics · match / MCQ + SGV answer key', 'Thông tin và dữ liệu — MATCH (cột A/B), SELECT_MCQ; WAL-192 answer-key convention (grade 6)'),
]
SGV_ANSWER = re.compile(r'(Đáp án|ĐÁP ÁN|Gợi ý trả lời|Gợi ý:|Trả lời:|Câu trả lời|Dự kiến|Kết quả:)')
SGV_OBJECTIVE = re.compile(r'(MỤC TIÊU|Mục tiêu|Yêu cầu cần đạt|YÊU CẦU CẦN ĐẠT)')
BAI_HEADER = re.compile(r'^\s*(?:BÀI|Bài)\s+(\d{1,2})\b')
FEATURES = ['formula', 'table', 'diagram', 'sidebar', 'side_by_side', 'color_heavy', 'figure', 'colored_box', 'two_col', 'continuation']
YEAR = re.compile(r'\b(?:năm\s+)?(\d{3,4})\b')


def lesson_meta(docs, book, no):
    d = docs[book]
    ls = sorted((l for l in d['lessons'] if l.get('pageStart') is not None), key=lambda l: l['pageStart'])
    this = next((l for l in d['lessons'] if l.get('number') == no), None)
    nxt = None
    if this and this.get('pageStart') is not None:
        after = [l for l in ls if l['pageStart'] > this['pageStart']]
        nxt = after[0] if after else None
    return d, this, nxt


def printed_headers(book, pdf_pages, r):
    """«Bài N» lines in the top 20 % of each page — the header signal tc2_attach uses."""
    found = {}
    for p in pdf_pages:
        page = load_ocr_page(book, p, r)
        if not page:
            continue
        for l in page['lines']:
            if l.get('y', 1) < 0.2:
                m = BAI_HEADER.match(l['text'])
                if m:
                    found[p] = int(m.group(1))
                    break
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=root())
    a = ap.parse_args()
    R = a.root
    docs = load_curriculum(R)
    census = {}
    for row in load_census_pages(R, books={c[0] for c in CANDIDATES}):
        census[(row['book'], row['page'])] = row
    with_sgv = json.load(open(os.path.join(R, 'poc-out/k12-census-exports/sgk-lessons-with-sgv.json')))
    gold_pages = set()
    for name in os.listdir(os.path.join(R, 'poc-out/trusted-corpus/tc-v2/tc2-p1/sdm-gold')):
        m = re.match(r'(.+)-p(\d{3})\.json$', name)
        if m:
            gold_pages.add((m.group(1), int(m.group(2))))
    packs = {g: load_pack_index(g, R) for g in (5, 6)}

    out = []
    for book, no, modality, why in CANDIDATES:
        d, this, nxt = lesson_meta(docs, book, no)
        off = printed_to_pdf_offset(book, R)
        rec = {'book': book, 'lesson': no, 'modality': modality, 'why': why, 'subject': d['subject'], 'grade': d['grade'],
               'title': (this or {}).get('title'), 'toc_status': d.get('structureStatus'), 'book_lessons_missing_pageStart': d.get('lessonsMissingPage'),
               'printed_start': (this or {}).get('pageStart'), 'next_printed_start': (nxt or {}).get('pageStart'), 'next_lesson_no': (nxt or {}).get('number'),
               'printed_to_pdf_offset': off}
        pdf_pages = []
        if this and this.get('pageStart') is not None and off is not None:
            lo = this['pageStart'] + off
            hi = (nxt['pageStart'] + off) if nxt else lo + 8
            pdf_pages = list(range(lo, hi))
        rec['pdf_pages'] = pdf_pages
        rec['range_is_open_ended(next lesson has no pageStart)'] = bool(nxt and nxt.get('number') != no + 1)
        # printed headers in and just before the range
        probe = list(range((pdf_pages[0] - 2) if pdf_pages else 1, (pdf_pages[-1] + 3) if pdf_pages else 1))
        hdr = printed_headers(book, probe, R)
        rec['printed_bai_headers_near_range'] = {str(k): v for k, v in sorted(hdr.items())}
        rec['toc_counter_matches_printed_header'] = any(v == no for v in hdr.values())
        # layout features
        feats = Counter()
        gate = Counter()
        for p in pdf_pages:
            c = census.get((book, p))
            if c:
                feats['pages_in_census'] += 1
                for f in FEATURES:
                    if c.get(f):
                        feats[f] += 1
                if not any(c.get(x) for x in ('formula', 'table', 'diagram', 'color_heavy', 'three_col')):
                    feats['no_unhandled_feature'] += 1
            lp = load_layout_page(book, p, R)
            if lp:
                gate['pages_with_xycut'] += 1
                if (lp.get('layout') or {}).get('trusted'):
                    gate['xycut_trusted_pages'] += 1
                for b in lp.get('blocks') or []:
                    gate['xycut_role_' + str(b.get('role'))] += 1
        rec['layout_features_pages'] = dict(feats)
        rec['xycut_gate'] = dict(gate)
        rec['gold_pages_in_range'] = [f'p{p:03d}' for p in pdf_pages if (book, p) in gold_pages]
        # units (old extractor)
        uj = load_units(book, R)
        units_by_lesson = [u for u in (uj or {}).get('units', []) if u.get('lesson') == no and u.get('role') != 'SECTION_TEXT']
        units_by_page = [u for u in (uj or {}).get('units', []) if u.get('pagePdf') in pdf_pages and u.get('role') != 'SECTION_TEXT']
        labels = Counter()
        shapes = Counter()
        years = set()
        clean_units = 0
        for u in units_by_lesson:
            t = (u.get('text') or '').strip()
            if (CATALOG.match(t) and len(t) < 120) or STAGE_ONLY.match(t) or NOISE.search(t):
                continue
            clean_units += 1
            for l in classify(t):
                labels[l] += 1
            for s in shape_hits(t):
                shapes[s] += 1
            for y in YEAR.findall(t):
                yi = int(y)
                if 40 <= yi <= 2030:
                    years.add(yi)
        rec['units_extractor'] = (uj or {}).get('extractor')
        rec['units_attached_to_lesson'] = len(units_by_lesson)
        rec['units_in_pdf_range'] = len(units_by_page)
        rec['units_roles'] = dict(Counter(u.get('role') for u in units_by_lesson))
        rec['units_clean'] = clean_units
        rec['pattern_labels'] = dict(labels.most_common())
        rec['shape_markers'] = dict(shapes.most_common())
        rec['distinct_years_mentioned'] = sorted(years)[:20]
        # SGV
        sgv_book = book.replace('-sgk-', '-sgv-')
        sj = load_units(sgv_book, R)
        if sj is None:
            base = sgv_book.split('-tap-')[0]
            for cand in sorted(os.listdir(os.path.join(R, 'poc-out/units-k12'))):
                if cand.startswith(base) and cand.endswith('.json'):
                    sgv_book = cand[:-5]
                    sj = load_units(sgv_book, R)
                    break
        sgv_units = [u for u in (sj or {}).get('units', []) if u.get('lesson') == no]
        rec['sgv_units_file'] = sgv_book if sj else None
        rec['sgv_units_for_lesson_no'] = len(sgv_units)
        rec['sgv_answer_lexicon_hits'] = sum(1 for u in sgv_units if SGV_ANSWER.search(u.get('text') or ''))
        rec['sgv_objective_lexicon_hits'] = sum(1 for u in sgv_units if SGV_OBJECTIVE.search(u.get('text') or ''))
        rec['sgv_markers_census(sgk-lessons-with-sgv)'] = with_sgv.get(f'{book}|{no}')
        # pack wiring
        wiring = Counter()
        pk = packs.get(d['grade'])
        if pk:
            for key in ('toanExercises', 'tvReadings', 'tvWritings', 'suSources', 'khoaExperiments', 'diaMaps'):
                xs = pk.get(key) or []
                if isinstance(xs, dict):
                    xs = list(xs.values())
                for e in xs:
                    if isinstance(e, dict) and (e.get('book') or e.get('sourceDocumentId')) == book and (e.get('lesson') or e.get('lessonNo')) == no:
                        wiring[key] += 1
        rec['pack_wiring'] = dict(wiring)
        out.append(rec)

    dump(out, 'second-lesson-candidates.json', R)
    md = ['# Second golden lesson — candidate census (MEASURED; shape markers HYPOTHESIS)', '',
          'Page ranges: TOC `pageStart` (printed) + the router\'s printed→PDF offset; the range ends at the next lesson with a `pageStart` (open-ended ranges are flagged). «Printed header» = a «Bài N» line in the top 20 % of a page near the range — the signal TC-v2 attaches by.', '',
          '| # | book · Bài | modality | title | TOC status (book missing pageStart) | printed → PDF range | printed «Bài N» headers near range | TOC no. = printed no.? | census pages · formula · table · diagram · colour-heavy · no-unhandled | XY-cut pages trusted | gold pages | units (lesson / range) | top pattern labels | shape markers | years | SGV units (answer hits / objective hits) | SGV marker census | pack wiring |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for i, r in enumerate(out, 1):
        f = r['layout_features_pages']
        g = r['xycut_gate']
        pages = r['pdf_pages']
        rng = f'{r["printed_start"]}→{r["next_printed_start"]} · PDF {pages[0]}–{pages[-1]} ({len(pages)} p)' if pages else f'{r["printed_start"]} → offset {r["printed_to_pdf_offset"]} (no range)'
        feats = f'{f.get("pages_in_census", 0)} · {f.get("formula", 0)} · {f.get("table", 0)} · {f.get("diagram", 0)} · {f.get("color_heavy", 0)} · {f.get("no_unhandled_feature", 0)}'
        xy = f'{g.get("xycut_trusted_pages", 0)} / {g.get("pages_with_xycut", 0)}' if g else '— (no WAL-206 run)'
        labs = ', '.join(f'{k} {v}' for k, v in list(r['pattern_labels'].items())[:5]) or '—'
        shp = ', '.join(f'{k} {v}' for k, v in list(r['shape_markers'].items())[:6]) or '—'
        yrs = ', '.join(str(y) for y in r['distinct_years_mentioned'][:8]) or '—'
        sgv = f'{r["sgv_units_for_lesson_no"]} ({r["sgv_answer_lexicon_hits"]} / {r["sgv_objective_lexicon_hits"]})' if r['sgv_units_file'] else 'no SGV units file'
        mk = r['sgv_markers_census(sgk-lessons-with-sgv)']
        mk = ', '.join(f'{k} {v}' for k, v in mk.items()) if mk else '—'
        wiring = ', '.join(f'{k} {v}' for k, v in r['pack_wiring'].items()) or '—'
        md.append(f'| {i} | {r["book"]} · Bài {r["lesson"]} | {r["modality"]} | {r["title"]} | {r["toc_status"]} ({r["book_lessons_missing_pageStart"]}) | {rng}{" · OPEN-ENDED" if r["range_is_open_ended(next lesson has no pageStart)"] else ""} | {r["printed_bai_headers_near_range"]} | {r["toc_counter_matches_printed_header"]} | {feats} | {xy} | {", ".join(r["gold_pages_in_range"]) or "—"} | {r["units_attached_to_lesson"]} / {r["units_in_pdf_range"]} | {labs} | {shp} | {yrs} | {sgv} | {mk} | {wiring} |')
    md.append('')
    p = write_md('\n'.join(md), 'second-lesson-candidates.md', R)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print('wrote', p)


if __name__ == '__main__':
    main()
