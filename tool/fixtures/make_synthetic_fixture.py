#!/usr/bin/env python3
"""TRACK B (WAL-210) — sinh FIXTURE MẪU (giả lập) cho CI/widget test.

    python3 tool/fixtures/make_synthetic_fixture.py [--out assets/fixtures/synthetic]

Khác với `make_lesson_fixture.py`, script này KHÔNG đọc SGK, KHÔNG đọc TSL.
Mọi câu chữ là văn bản viết lại rõ ràng là mẫu (mỗi đoạn mở đầu bằng
«[MẪU]»), mọi hình là PNG tự vẽ có chữ «HÌNH MẪU». Mục đích: một bản clone
sạch (không có corpus) vẫn dựng được đủ 9 loại block, 2 hình dạng ngữ nghĩa
và 1 kịch bản SAM để test và để màn không rỗng — với `trust =
fixtureSynthetic` ở mọi phần tử (chip «nội dung mẫu (giả lập)» bắt buộc).

Cùng CHỖ (book + số bài) với fixture thật để catalog thay thế được; cùng
schema `wal-lesson-fixture-v1`. Không có gì ở đây là lời sách.
"""
import argparse
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BOOK = '06-sgk-khoa-hoc-tu-nhien-6'
LESSON = 17
TRUST = 'fixtureSynthetic'
PROTO = 'prototype'


def ref(page, printed, bbox, block_id):
    return {'book': BOOK, 'pagePdf': page, 'pagePrinted': printed, 'bbox': bbox, 'blockId': block_id,
            'extraction': 'synthetic', 'ocrConf': None}


def blk(i, type_, page, printed, y, **kw):
    bid = f'{BOOK}:p{page:03d}:synthetic:{i:03d}'
    return {'id': bid, 'type': type_, 'sourceRef': ref(page, printed, [0.1, y, 0.8, 0.03], bid), 'trust': TRUST, **kw}


def draw_png(path, text, size=(600, 320), fill=(243, 238, 255)):
    from PIL import Image, ImageDraw
    img = Image.new('RGB', size, fill)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, size[0] - 9, size[1] - 9], outline=(124, 77, 255), width=4)
    d.line([40, 250, 200, 90, 360, 250, 540, 90], fill=(124, 77, 255), width=6)
    d.text((24, 24), 'HÌNH MẪU (giả lập) — không phải hình SGK', fill=(45, 45, 58))
    d.text((24, size[1] - 40), text, fill=(45, 45, 58))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def build(out_dir):
    crops = os.path.join(out_dir, 'crops')
    draw_png(os.path.join(crops, 'synthetic-fig-1.png'), 'fig-1: hai cốc nước, một đục một trong')
    draw_png(os.path.join(crops, 'synthetic-fig-2.png'), 'fig-2: phễu và giấy lọc')
    draw_png(os.path.join(crops, 'synthetic-withheld-1.png'), 'vùng bị giữ lại (mẫu)', size=(600, 80))

    i = iter(range(1, 100))
    blocks = [
        blk(next(i), 'heading', 61, 60, 0.07, text='BÀI MẪU: TÁCH CHẤT KHỎI HỖN HỢP (GIẢ LẬP)', level=1, roleConfidence=0.9),
        blk(next(i), 'activity', 61, 60, 0.15, kind='stageLabel', text='MỤC TIÊU', roleConfidence=0.9),
        blk(next(i), 'activity', 61, 60, 0.17, kind='objective', text='· [MẪU] Kể được vài cách đơn giản để tách chất ra khỏi hỗn hợp.', roleConfidence=0.8),
        blk(next(i), 'question', 61, 60, 0.28, text='[MẪU] Người ta tách hạt cát ra khỏi nước như thế nào?', roleConfidence=0.9),
        blk(next(i), 'heading', 61, 60, 0.32, text='· Nguyên tắc (mẫu)', level=2, roleConfidence=0.85),
        blk(next(i), 'paragraph', 61, 60, 0.35, text='[MẪU] Các chất trong một hỗn hợp có tính chất khác nhau, nên có thể dựa vào chỗ khác nhau đó để tách chúng ra. Đây là văn bản giả lập để kiểm thử, không phải lời sách.', roleConfidence=0.6),
        {'id': f'{BOOK}:p061:synthetic:fig1', 'type': 'image', 'sourceRef': ref(61, 60, [0.1, 0.4, 0.4, 0.3], None), 'trust': TRUST,
         'crop': 'crops/synthetic-fig-1.png', 'captionBlockId': f'{BOOK}:p061:synthetic:007', 'labels': 0},
        blk(next(i), 'caption', 61, 60, 0.7, text='[MẪU] Hình 1. Nước đục để yên thì hạt nặng lắng xuống', refersFigure=True, roleConfidence=0.9),
        blk(next(i), 'question', 61, 60, 0.78, text='[MẪU] 1. Vì sao hạt cát lắng xuống đáy cốc?', roleConfidence=0.9),
        blk(next(i), 'activity', 61, 60, 0.86, kind='sidebar', text='[MẪU] 2. Kể một ví dụ tách chất mà em gặp ở nhà.', roleConfidence=0.8),
        blk(next(i), 'heading', 62, 61, 0.07, text='I Một số cách tách chất (mẫu)', level=1, roleConfidence=0.85),
        blk(next(i), 'heading', 62, 61, 0.10, text='1. Lắng, gạn và lọc (mẫu)', level=2, roleConfidence=0.85),
        blk(next(i), 'paragraph', 62, 61, 0.12, text='[MẪU] Khi hạt rắn không tan mà lơ lửng, ta lọc để giữ chúng lại trên giấy lọc. Văn bản giả lập.', roleConfidence=0.6),
        blk(next(i), 'heading', 62, 61, 0.47, text='Lọc nước đục (thí nghiệm mẫu)', level=3, roleConfidence=0.85),
        blk(next(i), 'activity', 62, 61, 0.50, kind='instruction', text='[MẪU] Chuẩn bị: nước, cốc, đất, phễu, giấy lọc. Tiến hành:', roleConfidence=0.9),
        blk(next(i), 'paragraph', 62, 61, 0.55, text='· [MẪU] Bước một: khuấy đất vào cốc nước rồi để yên.', roleConfidence=0.6),
        blk(next(i), 'paragraph', 62, 61, 0.59, text='· [MẪU] Bước hai: gấp giấy lọc, đặt vào phễu.', roleConfidence=0.6),
        blk(next(i), 'paragraph', 62, 61, 0.62, text='· [MẪU] Bước ba: rót từ từ phần nước phía trên vào phễu, hứng nước lọc.', roleConfidence=0.6),
        {'id': f'{BOOK}:p062:synthetic:fig2', 'type': 'image', 'sourceRef': ref(62, 61, [0.2, 0.68, 0.3, 0.17], None), 'trust': TRUST,
         'crop': 'crops/synthetic-fig-2.png', 'captionBlockId': None, 'labels': 0},
        blk(next(i), 'caption', 62, 61, 0.88, text='[MẪU] Hình 2. Bộ lọc đơn giản', refersFigure=True, roleConfidence=0.9),
        {'id': f'{BOOK}:p062:synthetic:withheld1', 'type': 'withheld', 'sourceRef': ref(62, 61, [0.1, 0.9, 0.5, 0.03], None), 'trust': TRUST,
         'reason': 'math_guard', 'crop': 'crops/synthetic-withheld-1.png'},
        blk(next(i), 'table', 63, 62, 0.20, rows=[['Cách', 'Dùng khi'], ['Lọc (mẫu)', 'hạt rắn không tan'], ['Cô cạn (mẫu)', 'chất rắn đã tan']], safe=True, headerRows=1, roleConfidence=0.7),
        blk(next(i), 'question', 63, 62, 0.33, text='[MẪU] Làm muối từ nước biển dùng cách tách chất nào?', roleConfidence=0.9),
        blk(next(i), 'activity', 64, 63, 0.17, kind='stageLabel', text='Em đã học (mẫu)', roleConfidence=0.9),
        blk(next(i), 'paragraph', 64, 63, 0.24, text='· [MẪU] Lọc (tách hạt rắn không tan ra khỏi chất lỏng).', roleConfidence=0.6),
        blk(next(i), 'paragraph', 64, 63, 0.26, text='· [MẪU] Cô cạn (tách chất rắn đã tan bằng cách làm bay hơi chất lỏng).', roleConfidence=0.6),
        {'id': f'{BOOK}:b{LESSON}:sourceRef', 'type': 'sourceRef', 'sourceRef': ref(61, 60, [0, 0, 1, 1], None), 'trust': TRUST,
         'text': 'SGK KHTN 6 · trang 60–63 · FIXTURE MẪU (giả lập) — không phải nội dung sách'},
    ]
    ids = [b['id'] for b in blocks]
    step_ids = [b['id'] for b in blocks if b['type'] == 'paragraph' and b['text'].startswith('· [MẪU] Bước')]
    summary_ids = [b['id'] for b in blocks if b['type'] == 'paragraph' and b['sourceRef']['pagePdf'] == 64]
    q_salt = next(b['id'] for b in blocks if b['type'] == 'question' and 'muối' in b['text'])
    q_sand = next(b['id'] for b in blocks if b['type'] == 'question' and 'cát lắng' in b['text'])
    principle = next(b['id'] for b in blocks if b['type'] == 'paragraph' and 'Nguyên tắc' not in b['text'] and b['sourceRef']['pagePdf'] == 61)
    doc = {
        'schema': 'wal-lesson-fixture-v1',
        'book': BOOK, 'bookTitle': 'KHTN 6', 'subject': 'KHTN', 'grade': 6, 'lesson': LESSON,
        'title': 'TÁCH CHẤT KHỎI HỖN HỢP (BẢN MẪU)',
        'chapter': {'label': 'Chương IV', 'title': 'HỖN HỢP. TÁCH CHẤT RA KHỎI HỖN HỢP (mẫu)', 'lessonNos': [16, 17], 'trust': TRUST, 'derivation': 'synthetic'},
        'chapters': [
            {'label': 'Chương I', 'title': 'MỞ ĐẦU (mẫu)', 'lessonNos': list(range(1, 9)), 'trust': TRUST, 'derivation': 'synthetic'},
            {'label': 'Chương II', 'title': 'CHẤT QUANH TA (mẫu)', 'lessonNos': [9, 10, 11], 'trust': TRUST, 'derivation': 'synthetic'},
            {'label': 'Chương III', 'title': 'VẬT LIỆU, NHIÊN LIỆU, THỰC PHẨM (mẫu)', 'lessonNos': [12, 13, 14, 15], 'trust': TRUST, 'derivation': 'synthetic'},
            {'label': 'Chương IV', 'title': 'HỖN HỢP. TÁCH CHẤT RA KHỎI HỖN HỢP (mẫu)', 'lessonNos': [16, 17], 'trust': TRUST, 'derivation': 'synthetic'},
            {'label': 'Chương V', 'title': 'TẾ BÀO (mẫu)', 'lessonNos': [18, 19, 20, 21], 'trust': TRUST, 'derivation': 'synthetic'},
        ],
        'provenance': {
            'trust': TRUST, 'book': BOOK, 'pagePdfStart': 61, 'pagePdfEnd': 64, 'pagePrintedStart': 60, 'pagePrintedEnd': 63,
            'generator': 'tool/fixtures/make_synthetic_fixture.py@v1', 'sourcePipeline': 'synthetic', 'sdmVersion': None,
            'boundaryConfidence': None, 'tslPath': None,
            'distribution': 'synthetic — committed; contains no SGK text or images',
        },
        'evidencePolicy': 'none',
        'blocks': blocks,
        'semantic': [
            {'type': 'process', 'id': 'process-1', 'title': 'Lọc nước đục (thí nghiệm mẫu)', 'trust': TRUST, 'derivation': 'synthetic',
             'steps': [
                 {'order': 1, 'text': '· [MẪU] Bước một: khuấy đất vào cốc nước rồi để yên.', 'sourceBlockId': step_ids[0]},
                 {'order': 2, 'text': '· [MẪU] Bước hai: gấp giấy lọc, đặt vào phễu.', 'sourceBlockId': step_ids[1]},
                 {'order': 3, 'withheldReason': 'math_guard', 'sourceBlockId': f'{BOOK}:p062:synthetic:withheld1'},
                 {'order': 4, 'text': '· [MẪU] Bước ba: rót từ từ phần nước phía trên vào phễu, hứng nước lọc.', 'sourceBlockId': step_ids[2]},
             ]},
            {'type': 'comparison', 'id': 'comparison-1', 'title': 'Các cách tách chất (mẫu)', 'trust': TRUST, 'derivation': 'synthetic',
             'entities': [{'name': 'Lọc (mẫu)', 'sourceBlockId': summary_ids[0]}, {'name': 'Cô cạn (mẫu)', 'sourceBlockId': summary_ids[1]}],
             'dimensions': [{'name': 'Dùng để tách', 'values': ['tách hạt rắn không tan ra khỏi chất lỏng', 'tách chất rắn đã tan bằng cách làm bay hơi chất lỏng']}]},
        ],
        'tutorScript': {
            'samMode': 'prototypeScripted', 'trust': PROTO, 'evidencePolicy': 'none',
            'steps': [
                {'type': 'explain', 'id': 'e1', 'mascot': 'sam-explain', 'sourceBlockId': principle,
                 'text': '[MẪU] Bài này nói về cách tách một chất ra khỏi hỗn hợp. Con đọc đoạn mẫu bên dưới rồi mình thử nhé.'},
                {'type': 'ask', 'id': 'q1', 'prompt': '[MẪU] Làm muối từ nước biển dùng cách tách chất nào?', 'promptBlockId': q_salt,
                 'options': ['Lọc', 'Cô cạn', 'Chiết'], 'acceptable': [r'^cô cạn$'],
                 'hints': ['[MẪU] Gợi ý 1: muối không bay hơi, nước thì có.', '[MẪU] Gợi ý 2: xem dòng «Cô cạn» trong bảng.'],
                 'feedbackMatched': '[MẪU] Khớp với bảng mẫu: đó là cô cạn.',
                 'scaffold': '[MẪU] Chưa khớp, không sao — bảng mẫu gọi cách này là cô cạn. Mình đi tiếp nhé.',
                 'keySource': 'synthetic prototype key — không phải SGV'},
                {'type': 'ask', 'id': 'q2', 'prompt': '[MẪU] 1. Vì sao hạt cát lắng xuống đáy cốc?', 'promptBlockId': q_sand,
                 'options': [], 'acceptable': [r'nặng', r'nặng hơn'],
                 'hints': ['[MẪU] Gợi ý 1: so cân nặng của hạt cát và nước.', '[MẪU] Gợi ý 2: hạt nặng hơn thì đi về đâu?'],
                 'feedbackMatched': '[MẪU] SAM thấy câu trả lời có ý «nặng hơn» — khớp ý mẫu.',
                 'scaffold': '[MẪU] Ý mẫu: hạt cát nặng hơn nước nên lắng xuống. Mình đi tiếp nhé.',
                 'keySource': 'synthetic prototype key — không phải SGV'},
                {'type': 'next', 'id': 'n1', 'label': '[MẪU] Đọc lại phần «Em đã học»', 'target': 'read', 'anchorBlockId': summary_ids[0]},
            ],
        },
    }
    assert len(set(ids)) == len(ids), 'id trùng'
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f'lesson-{BOOK}-b{LESSON}.synthetic.json')
    json.dump(doc, open(path, 'w'), ensure_ascii=False, indent=1)
    print(path, 'blocks', len(blocks))
    return path


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=f'{ROOT}/assets/fixtures/synthetic')
    build(ap.parse_args().out)
