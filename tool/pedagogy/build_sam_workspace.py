#!/usr/bin/env python3
"""MỘT bộ dựng cho MỌI bài — không phải 10 kịch bản viết tay.

Đầu vào cho từng bài: (a) dòng đọc canonical (`lesson_reading`, cùng đường mà
pack đang dùng), (b) hợp đồng sư phạm suy từ SGV đã ghép CHỨNG MINH. Đầu ra:
`LessonDocument` đúng lược đồ `wal-lesson-fixture-v1` mà client đã đọc được.

⛔ DỮ LIỆU RIÊNG TỪNG BÀI thì được; LOGIC RIÊNG TỪNG BÀI thì không. Tệp này
không có một nhánh `if book == …` nào. Bài khác nhau chỉ khác ở BẰNG CHỨNG.

⚠ KHOÁ CHẤM ĐIỂM — quyết định fail-closed của vòng POC. Đo được: trong 589 bài
ghép CONFIDENT chỉ 46 bài có VIỆC của trẻ chứng minh được, và chỉ **6 việc /
3 bài** có đáp án gắn theo danh sách đánh số — soi tay thì quá nửa số ấy VẪN
là đáp án của câu khác («Trong khí quyển, khí nitrogen phổ biến thứ mấy?» nhận
đáp án «Hợp chất của nitrogen có ý nghĩa quan trọng…»). Không đủ để nói với
một đứa trẻ rằng em sai. Nên `evidencePolicy = none`, `answerKeysIncluded =
false`, và `check_answer` nằm trong `forbiddenTutorActions` của MỌI bài.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))

from lesson_reading import lesson_reading  # noqa: E402
from subject import subject as subject_of  # noqa: E402

SCHEMA = 'wal-lesson-fixture-v1'
GEN = 'tool/pedagogy/build_sam_workspace.py@v1'


def _pack_lesson(book, lesson, cache={}):
    if not cache:
        import glob
        for p in sorted(glob.glob(os.path.join(ROOT, 'assets/pack',
                                               'lesson-index-g*.json'))):
            g = json.load(open(p, encoding='utf-8'))
            for r in g.get('lessonReadings') or []:
                cache[(r['book'], r['lesson'])] = (r, g.get('grade'))
    return cache.get((book, lesson), (None, None))


def _role(text):
    """Vai trò đọc được từ CHÍNH chữ — không suy diễn ngoài nguồn."""
    t = (text or '').strip()
    if t.endswith('?'):
        return 'question', 'question'
    if t.isupper() and len(t) < 90:
        return 'heading', 'heading'
    return 'body', 'paragraph'


def build(book, lesson, contract, out_dir):
    rec, grade = _pack_lesson(book, lesson)
    if rec is None:
        return None, 'KHÔNG CÓ TRONG PACK'
    doc, _ = lesson_reading(book, rec['pagePdfStart'], rec['pagePdfEnd'],
                            printed_start=rec.get('pageStart'),
                            title=rec.get('title'))
    if not doc:
        return None, 'KHÔNG DỰNG ĐƯỢC DÒNG ĐỌC'
    blocks = []
    for pg in doc['pages']:
        for q in sorted(pg.get('paragraphs') or [], key=lambda x: x['seq']):
            b = q.get('box')
            if not b or not (q.get('text') or '').strip():
                continue
            role, btype = _role(q['text'])
            bid = f"{book}:p{pg['pagePdf']:03d}:sam:{len(blocks):03d}"
            blocks.append({
                'id': bid, 'type': btype, 'trust': 'trustedStructuredLesson',
                'sourceRole': role, 'text': q['text'],
                'sourceRef': {
                    'book': book, 'pagePdf': pg['pagePdf'],
                    'pagePrinted': pg.get('pagePrinted'),
                    'bbox': [round(b[0], 4), round(b[1], 4),
                             round(b[2] - b[0], 4), round(b[3] - b[1], 4)],
                    'blockId': bid, 'extraction': 'lesson-reading-canonical',
                    'pipeline': 'pack-canonical'},
            })
    if not blocks:
        return None, 'KHÔNG CÓ KHỐI CHỮ'
    d = {
        'schema': SCHEMA, 'book': book,
        'bookTitle': (rec.get('bookTitle') or book), 'subject': subject_of(book),
        'grade': grade, 'lesson': lesson, 'title': rec.get('title') or '',
        'evidencePolicy': 'none', 'licence': 'internalResearchOnly',
        'provenance': {
            'trust': 'trustedStructuredLesson', 'book': book,
            'pagePdfStart': rec['pagePdfStart'], 'pagePdfEnd': rec['pagePdfEnd'],
            'generator': GEN, 'sourcePipeline': 'pack-canonical',
            'pipelineVersion': 'pack-canonical/pedagogy-contract-v1',
            'docType': 'SGK', 'sourceability': 'PARTIAL',
            # ⭐ KHOÁ CỨNG: mọi tài liệu của vòng này KHÔNG mang khoá chấm.
            'answerKeysIncluded': False,
            'auditStatus': 'notAudited', 'auditRef': None,
            'distribution': 'internal-research-only',
            'pedagogySource': {
                'sgvBook': contract['sgvBook'], 'sgvPages': contract['sgvPages'],
                'pairing': contract['provenance']['pairing'],
                'tasksOwned': len(contract['tasks']),
                'answerWithheld': True,
                'withholdReason': 'TASK_ANSWER_OWNERSHIP_UNPROVEN'},
        },
        'blocks': blocks,
    }
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, f'lesson-{book}-b{lesson}.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return p, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--picks', default='poc-out/pedagogy/poc10.json')
    ap.add_argument('--contracts', default='poc-out/pedagogy/contracts')
    ap.add_argument('--out', default='assets/fixtures/real')
    a = ap.parse_args()
    picks = json.load(open(os.path.join(ROOT, a.picks), encoding='utf-8'))
    ok = 0
    for book, lesson in picks:
        cp = os.path.join(ROOT, a.contracts, f'{book}-b{lesson}.json')
        if not os.path.exists(cp):
            print(f'  ⛔ {book} B{lesson}: KHÔNG CÓ HỢP ĐỒNG')
            continue
        contract = json.load(open(cp, encoding='utf-8'))
        dest = os.path.join(ROOT, a.out, f'lesson-{book}-b{lesson}.json')
        # ⚠ KHÔNG GHI ĐÈ TÀI LIỆU ĐÃ CÓ. Lượt đầu của tôi đè mất hai fixture
        # dựng từ TSL (KHTN 6 Bài 9 và 10) — chúng mang `semantic` cho tab
        # Trực quan mà bộ dựng này không sinh ra. Đè = mất năng lực đang chạy.
        if os.path.exists(dest):
            print(f'  = {book[:38]:38s} B{lesson:<3d} GIỮ tài liệu đã có')
            ok += 1
            continue
        p, err = build(book, lesson, contract, os.path.join(ROOT, a.out))
        print(f"  {'✓' if p else '⛔'} {book[:38]:38s} B{lesson:<3d} "
              f"{os.path.basename(p) if p else err}")
        ok += bool(p)
    print(f'\n{ok}/{len(picks)} tài liệu dựng được bằng MỘT bộ dựng')


if __name__ == '__main__':
    main()
