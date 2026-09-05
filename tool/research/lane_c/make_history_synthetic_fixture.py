#!/usr/bin/env python3
"""LANE C (round 4) — FIXTURE MẪU (giả lập) cho lát cắt LS&ĐL 5 Bài 8, để CI/widget test chạy
được ở máy không có corpus. Cùng CHỖ (book + số bài) với fixture thật; mọi câu chữ mở đầu «[MẪU]»;
KHÔNG câu nào là lời sách. Sau khi dựng các block, chính các luật History (history_rules.apply)
chạy lên nó — nên sơ đồ dòng thời gian, nguồn kể chuyện và kịch bản SAM của bản mẫu đi qua đúng
đường mà bản thật đi (trust = fixtureSynthetic ở mọi phần tử).

    python3 tool/research/lane_c/make_history_synthetic_fixture.py [--out assets/fixtures/synthetic]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import history_rules  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
BOOK = '05-sgk-lich-su-va-dia-li-5'
LESSON = 8
TRUST = 'fixtureSynthetic'


def ref(page, printed, bbox, block_id):
    return {'book': BOOK, 'pagePdf': page, 'pagePrinted': printed, 'bbox': bbox, 'blockId': block_id, 'extraction': 'synthetic', 'ocrConf': None}


def blk(i, type_, page, printed, y, **kw):
    bid = f'{BOOK}:p{page:03d}:synthetic:{i:03d}'
    return {'id': bid, 'type': type_, 'sourceRef': ref(page, printed, [0.1, y, 0.8, 0.03], bid), 'trust': TRUST, **kw}


def draw_png(path, text, size=(600, 320), fill=(255, 244, 230)):
    from PIL import Image, ImageDraw
    img = Image.new('RGB', size, fill)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, size[0] - 9, size[1] - 9], outline=(220, 120, 40), width=4)
    d.line([40, 160, 560, 160], fill=(220, 120, 40), width=6)
    for x in (120, 260, 400, 520):
        d.ellipse([x - 10, 150, x + 10, 170], fill=(220, 120, 40))
    d.text((24, 24), 'HÌNH MẪU (giả lập) — không phải hình SGK', fill=(45, 45, 58))
    d.text((24, size[1] - 40), text, fill=(45, 45, 58))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def build(out_dir):
    crops = os.path.join(out_dir, 'crops')
    draw_png(os.path.join(crops, 'synthetic-history-fig-1.png'), 'fig-1: tranh mẫu về một nhân vật')
    draw_png(os.path.join(crops, 'synthetic-history-withheld-1.png'), 'vùng bị giữ lại (mẫu)', size=(600, 80))
    i = iter(range(1, 100))
    hp1 = ['Bài mẫu 8', '1. [MẪU] Một số cuộc đấu tranh mẫu']
    hp2 = ['Bài mẫu 8', 'CHUYỆN MẪU VỀ ÔNG MẪU A']
    blocks = [
        blk(next(i), 'heading', 38, 36, 0.10, text='BÀI MẪU 8: ĐẤU TRANH MẪU THỜI KÌ MẪU (GIẢ LẬP)', level=1, roleConfidence=0.9, sourceRole='heading'),
        blk(next(i), 'heading', 38, 36, 0.20, text='Sau bài học này, em sẽ:', level=2, roleConfidence=0.85, sourceRole='heading'),
        blk(next(i), 'activity', 38, 36, 0.23, kind='objective', text='• [MẪU] Kể được tên và vẽ được trục thời gian mẫu (ví dụ: 101, 205, 450,…).', roleConfidence=0.8, sourceRole='objective'),
        blk(next(i), 'activity', 38, 36, 0.30, kind='stageLabel', text='KHỞI ĐỘNG', roleConfidence=0.95, sourceRole='stage_label'),
        {'id': f'{BOOK}:p038:synthetic:withheld1', 'type': 'withheld', 'sourceRef': ref(38, 36, [0.1, 0.34, 0.8, 0.1], None), 'trust': 'withheld',
         'sourceRole': 'question', 'reason': 'page_feature:color_heavy', 'reasons': ['page_feature:color_heavy'], 'status': 'WITHHELD', 'crop': 'crops/synthetic-history-withheld-1.png'},
        blk(next(i), 'activity', 38, 36, 0.50, kind='stageLabel', text='KHÁM PHÁ', roleConfidence=0.95, sourceRole='stage_label'),
        blk(next(i), 'heading', 38, 36, 0.55, text='1. [MẪU] Một số cuộc đấu tranh mẫu', level=2, roleConfidence=0.85, sourceRole='heading', relations={'headingPath': hp1}),
        blk(next(i), 'question', 38, 36, 0.60, text='[MẪU] Đọc thông tin, em hãy kể tên một số cuộc đấu tranh mẫu.', roleConfidence=0.85, sourceRole='question', relations={'headingPath': hp1}),
        blk(next(i), 'paragraph', 39, 37, 0.07, roleConfidence=0.6, sourceRole='body', relations={'headingPath': hp1},
            text='[MẪU] Ông Mẫu A (101 - 103), Bà Mẫu B (205), Ông Mẫu C - Bà Mẫu D (310 - 320), Ông Mẫu E (398). Chiến thắng mẫu của Ông Mẫu G (450) đã kết thúc thời kì mẫu.'),
        blk(next(i), 'heading', 39, 37, 0.16, text='2. [MẪU] Kể chuyện về nhân vật mẫu', level=2, roleConfidence=0.85, sourceRole='heading'),
        blk(next(i), 'question', 39, 37, 0.23, text='[MẪU] Đọc thông tin và quan sát các hình từ 1 đến 3, em hãy kể câu chuyện mẫu.', roleConfidence=0.85, sourceRole='question'),
        blk(next(i), 'heading', 39, 37, 0.38, text='CHUYỆN MẪU VỀ ÔNG MẪU A', level=3, roleConfidence=0.88, sourceRole='heading', relations={'headingPath': hp2}),
        blk(next(i), 'paragraph', 39, 37, 0.43, text='[MẪU] Thuở xưa, ở một vùng mẫu có Ông Mẫu A. Năm 101, Ông Mẫu A phất cờ khởi nghĩa mẫu.', roleConfidence=0.6, sourceRole='body', relations={'headingPath': hp2}),
        blk(next(i), 'paragraph', 39, 37, 0.53, text='[MẪU] Cuộc khởi nghĩa mẫu đã chứng tỏ tinh thần đấu tranh bất khuất mẫu, tạo tiền đề mẫu cho mai sau.', roleConfidence=0.6, sourceRole='body', relations={'headingPath': hp2}),
        blk(next(i), 'paragraph', 39, 37, 0.69, text='(Theo Tác Giả Mẫu, Sách mẫu về Ông Mẫu A, NXB Mẫu, 2000)', roleConfidence=0.6, sourceRole='body', relations={'headingPath': hp2}),
        {'id': f'{BOOK}:p039:synthetic:fig1', 'type': 'image', 'sourceRef': ref(39, 37, [0.3, 0.74, 0.35, 0.14], None), 'trust': TRUST,
         'crop': 'crops/synthetic-history-fig-1.png', 'captionBlockId': f'{BOOK}:p039:synthetic:016', 'labels': 0, 'aspect': 600 / 320},
        blk(next(i), 'caption', 39, 37, 0.90, text='[MẪU] Hình 1. Tranh mẫu về Ông Mẫu A', refersFigure=True, roleConfidence=0.9, sourceRole='caption'),
        blk(next(i), 'activity', 41, 39, 0.45, kind='stageLabel', text='LUYỆN TẬP', roleConfidence=0.95, sourceRole='stage_label'),
        blk(next(i), 'question', 41, 39, 0.49, text='[MẪU] 1. Hãy vẽ và hoàn thiện trục thời gian (theo gợi ý dưới đây vào vở) thể hiện một số cuộc đấu tranh mẫu.', roleConfidence=0.85, sourceRole='question'),
        blk(next(i), 'question', 41, 39, 0.69, text='[MẪU] 2. Kể lại câu chuyện mẫu mà em sưu tầm được.', roleConfidence=0.85, sourceRole='question'),
        blk(next(i), 'activity', 41, 39, 0.77, kind='stageLabel', text='VẬN DỤNG', roleConfidence=0.95, sourceRole='stage_label'),
        blk(next(i), 'question', 41, 39, 0.80, text='[MẪU] Tìm hiểu và kể tên một số di tích mẫu.', roleConfidence=0.85, sourceRole='question'),
        {'id': f'{BOOK}:b{LESSON}:sourceRef', 'type': 'sourceRef', 'sourceRef': ref(38, 36, [0, 0, 1, 1], None), 'trust': TRUST, 'text': '[MẪU] SGK LS&ĐL 5 · trang 36–39 (giả lập)'},
    ]
    doc = {
        'schema': 'wal-lesson-fixture-v1', 'book': BOOK, 'bookTitle': 'LS&ĐL 5', 'subject': 'LS&ĐL', 'grade': 5, 'lesson': LESSON,
        'title': 'ĐẤU TRANH MẪU THỜI KÌ MẪU (GIẢ LẬP)', 'chapter': None, 'chapters': [],
        'provenance': {'trust': TRUST, 'book': BOOK, 'pagePdfStart': 38, 'pagePdfEnd': 41, 'pagePrintedStart': 36, 'pagePrintedEnd': 39,
                       'generator': 'tool/research/lane_c/make_history_synthetic_fixture.py@v1', 'sourcePipeline': 'synthetic',
                       'distribution': 'synthetic sample — không phải lời sách', 'boundary': {'pageStart': 38, 'pageEnd': 41, 'confidence': 1.0, 'headerFound': True, 'source': 'both'},
                       'auditStatus': 'notAudited', 'answerKeysIncluded': False},
        'evidencePolicy': 'none', 'licence': 'internalResearchOnly', 'blocks': blocks, 'semantic': [],
    }
    out, rep = history_rules.apply(doc, toc_title='Đấu tranh mẫu thời kì mẫu (giả lập)...')
    # mọi phần tử của bản mẫu mang trust fixtureSynthetic (kịch bản SAM là prototype như Bài 17)
    for s in out['semantic']:
        assert s['trust'] == TRUST, s['trust']
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f'lesson-{BOOK}-b{LESSON}.synthetic.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(path, f"events={len(rep['events'])} attributions={len(rep['attributions'])} tutorSteps={len(rep['tutorScript']['steps']) if rep['tutorScript'] else 0}")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'assets', 'fixtures', 'synthetic'))
    a = ap.parse_args()
    build(a.out)


if __name__ == '__main__':
    main()
