#!/usr/bin/env python3
"""TC-v1 — the HARD K-12 SOURCE-FIDELITY GOLD SET: page list (frozen 2026-09-04).

Why these pages: chosen from the layout census strata (tc_gold_select.py,
seed 20260904) plus the 9 WAL-206 gold pages (kept, not discarded) and the
WAL-204 documented failure page. Each page carries at least one hard
feature; families cover Toán, Tiếng Việt/Ngữ văn, Khoa học/KHTN/Vật lí,
LS&ĐL/Địa lí, Tin học, TN&XH, and three SGV pages.

Gold truth itself lives in tool/corpus/tc_gold/<book>-pNNN.json and was
written by reading the rendered page image (tc_render.py --grid), never from
extractor output.
"""
GOLD_PAGES = [
    # (book, pdfPage, why)
    ('07-sgk-khoa-hoc-tu-nhien-7', 20, 'WAL-206 gold: floating boxes, sidebar beside figures, captions'),
    ('07-sgk-khoa-hoc-tu-nhien-7', 21, 'activity box + question boxes + footnote (Bài 3 continues)'),
    ('07-sgk-khoa-hoc-tu-nhien-7', 32, 'WAL-204 documented failure page (column interleave "Trong số 118 nguyên tố…" — located by grep in OCR p032)'),
    ('05-sgk-toan-5-tap-mot', 21, 'WAL-206 gold: math figure-heavy, speech bubbles, worked steps'),
    ('09-sgk-ngu-van-9-tap-mot', 67, 'WAL-206 gold: poem + right sidebar + footnotes (Ngữ văn falsification page)'),
    ('09-sgk-tin-hoc-9', 20, 'WAL-206 gold: two-column bullets + boxes + LUYỆN TẬP/VẬN DỤNG'),
    ('04-sgk-khoa-hoc-4', 30, 'WAL-206 gold: mind-map diagram page'),
    ('05-sgk-lich-su-va-dia-li-5', 41, 'WAL-206 gold: text box beside photo, timeline table'),
    ('10-sgk-dia-li-10', 40, 'WAL-206 gold: body + two Em có biết sidebars'),
    ('10-sgk-vat-li-10', 30, 'WAL-206 gold: worked example, formulas, side-by-side boxes'),
    ('05-sgk-tieng-viet-5-tap-hai', 8, 'WAL-206 gold: image-only chapter opener'),
    ('11-sgk-ngu-van-11-tap-mot', 39, 'two-column literature text, cross-page continuation'),
    ('10-sgk-vat-li-10', 89, 'two-column physics + sidebar + figure'),
    ('07-sgk-lich-su-va-dia-li-7', 94, 'two-column history with figure'),
    ('02-sgk-toan-2-tap-hai', 48, 'grade-2 math two-column exercises, diagrams, boxes'),
    ('03-sgk-toan-3-tap-mot', 32, 'grade-3 math three-column, table, formula, boxes'),
    ('10-sgk-dia-li-10', 115, 'three-column data table (163 OCR lines)'),
    ('06-sgk-tin-hoc-6', 21, 'informatics side-by-side, sidebar, figure, boxes'),
    ('06-sgk-ngu-van-6-tap-mot', 21, 'literature side-by-side box + sidebar'),
    ('07-sgk-toan-7-tap-hai', 41, 'math formulas + sidebar + boxes + continuation'),
    ('04-sgk-khoa-hoc-4', 78, 'science side-by-side, sidebar, diagram'),
    ('08-sgk-lich-su-va-dia-li-8', 71, 'history side-by-side, sidebar, figure, diagram'),
    ('09-sgk-ngu-van-9-tap-mot', 83, 'literature sidebar + coloured boxes'),
    ('12-sgk-toan-12-tap-hai', 20, 'grade-12 math formula + sidebar + figure/diagram'),
    ('09-sgk-khoa-hoc-tu-nhien-9', 46, 'science table + sidebar'),
    ('04-sgk-tieng-viet-4-tap-mot', 28, 'literacy table + sidebar + continuation'),
    ('09-sgk-toan-9-tap-mot', 29, 'grade-9 math formula page'),
    ('11-sgk-vat-li-11', 105, 'physics formulas + sidebar'),
    ('05-sgk-toan-5-tap-mot', 92, 'math diagram + boxes'),
    ('09-sgk-khoa-hoc-tu-nhien-9', 38, 'science diagram page'),
    ('02-sgk-tieng-viet-2-tap-hai', 14, 'grade-2 literacy diagram + boxes'),
    ('01-sgk-tu-nhien-va-xa-hoi-1', 6, 'grade-1 visual page (elementary layout)'),
    ('02-sgk-tieng-viet-2-tap-mot', 103, 'grade-2 literacy cross-page continuation'),
    ('05-sgk-lich-su-va-dia-li-5', 80, 'broken/dense: 109 OCR lines, table, overlap'),
    ('07-sgv-toan-7', 43, 'SGV two-column teacher guide'),
    ('04-sgv-toan-4', 54, 'SGV with diagram + boxes, lesson 11'),
    ('10-sgv-tin-hoc-10', 39, 'SGV plain page with answers, lesson 5'),
    ('08-sgk-ngu-van-8-tap-mot', 38, 'plain single-column control page'),
]

if __name__ == '__main__':
    import json
    print(json.dumps([dict(book=b, page=p, why=w) for b, p, w in GOLD_PAGES], ensure_ascii=False, indent=1))
