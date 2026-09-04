#!/usr/bin/env python3
"""WAL-206 — cross-subject layout gold set + scorer.

Gold truth was written by a human reading the rendered page image (PyMuPDF,
80 dpi) — NOT from OCR output — and records the expected READING ORDER as a
list of anchors (the first words of each block, as printed) plus the role
of each anchor. Anchors are matched to extracted blocks by normalized
prefix (case/diacritic-insensitive, OCR-tolerant) so small OCR errors do
not fail the match.

Scores per page:
  order  — pairwise ordering agreement over matched anchors (1.0 = all
           pairs in the right order; a classic two-column interleave scores
           far below 1).
  roles  — share of matched anchors whose extracted role equals the gold
           role (sidebar/footnote/caption/heading/question/body).
  found  — share of gold anchors matched at all.
  fidelity — for anchors marked `contiguous`, whether the gold text
           continues inside ONE extracted block (no foreign text spliced in).

Usage: python3 tool/corpus/layout_gold.py            # score all gold pages
       python3 tool/corpus/layout_gold.py --json     # machine-readable
"""
import json
import re
import sys
import unicodedata

GOLD = [
    # ---- KHTN 7, printed 19: single column + speech-bubble box + sidebar beside figures + captions
    dict(book='07-sgk-khoa-hoc-tu-nhien-7', page=20, family='science, floating boxes', order=[
        ('NGUYÊN TỐ HÓA HỌC', 'heading'),
        ('MỤC TIÊU', 'heading'),
        ('Phát biểu được khái niệm', 'body'),
        ('Viết được kí hiệu', 'body'),
        ('Oxygen, carbon, hydrogen, nitrogen', 'sidebar'),
        ('Vậy nguyên tố hoá học là gì', 'question'),
        ('Nguyên tố hoá học', 'heading'),
        ('Đến nay, người ta đã tìm ra 118', 'body'),
        ('Ở Hy Lạp cổ đại', 'sidebar'),
        ('a) Vàng', 'caption'),
        ('b) Chì', 'caption'),
        ('Hình 3.1', 'caption'),
        ('Các nguyên tử có cùng số proton', 'body'),
        ('Các nguyên tử thuộc cùng một nguyên tố', 'body'),
    ], contiguous=['Đến nay, người ta đã tìm ra 118', 'Các nguyên tử có cùng số proton']),
    # ---- Toán 5 tập một, printed 20: heading, Khám phá, speech bubbles (figure text), worked steps
    dict(book='05-sgk-toan-5-tap-mot', page=21, family='math, figure-heavy', order=[
        ('CỘNG, TRỪ HAI PHÂN SỐ', 'heading'),
        ('Khám phá', 'heading'),
        ('Quy đồng mẫu số', 'body'),
        ('Hai mẫu số 5 và 2 không chia hết', 'body'),
        ('Thực hiện phép cộng', 'body'),
    ], contiguous=['Hai mẫu số 5 và 2 không chia hết']),
    # ---- Ngữ văn 9, printed 66: poem + right sidebar "Theo dõi" + footnotes — the Ngữ văn falsification page
    dict(book='09-sgk-ngu-van-9-tap-mot', page=67, family='literature, sidebar + footnotes', order=[
        ('VĂN BẢN 1', 'heading'),
        ('TRƯỚC KHI ĐỌC', 'heading'),
        ('Hãy giới thiệu một tác phẩm', 'question'),
        ('ĐỌC VĂN BẢN', 'heading'),
        ('Kim – Kiều gặp gỡ', 'heading'),
        ('Nẻo xa mới tỏ mặt người', 'body'),
        ('Theo dõi', 'sidebar'),
        ('Sự xuất hiện của nhân vật Kim Trọng', 'sidebar'),
        ('(1) Nhan đề', 'footnote'),
        ('(8) Nhà trâm anh', 'footnote'),
    ], contiguous=['Nẻo xa mới tỏ mặt người']),
    # ---- Tin học 9, printed 19: two-column bullet continuation + two boxes + LUYỆN TẬP/VẬN DỤNG
    dict(book='09-sgk-tin-hoc-9', page=20, family='informatics, two-column + boxes', order=[
        ('Hành vi vi phạm đến việc bảo đảm', 'body'),
        ('Hành vi tuyên truyền, quảng cáo', 'body'),
        ('mĩ tục, lối sống văn minh', 'body'),
        ('Hành vi xuyên tạc lịch sử', 'body'),
        ('Khi hoạt động trong môi trường số, sử dụng', 'body'),
        ('1. Hành vi nào sau đây', 'question'),
        ('A. Đăng bài', 'body'),
        ('D. Chia sẻ thông tin', 'body'),
        ('2. Minh nhận được một liên kết lạ', 'question'),
        ('LUYỆN TẬP', 'heading'),
        ('1. Em hãy cho biết những cách nào', 'question'),
        ('VẬN DỤNG', 'heading'),
        ('Em hãy tìm hiểu các hành vi bị cấm', 'question'),
    ], contiguous=['1. Hành vi nào sau đây']),
    # ---- Khoa học 4, printed 29: heading, objectives, box question, diagram (mind-map) — diagram text must not become a passage
    dict(book='04-sgk-khoa-hoc-4', page=30, family='science, diagram page', order=[
        ('ÔN TẬP CHỦ ĐỀ CHẤT', 'heading'),
        ('Tóm tắt được những nội dung chính', 'body'),
        ('Em đã được học những gì', 'question'),
        ('1. Đọc thông tin trong hình 1', 'question'),
        ('Hình 1', 'caption'),
    ], contiguous=[]),
    # ---- LS&ĐL 5, printed 39: text box beside a photo + caption, then LUYỆN TẬP with a timeline table, VẬN DỤNG
    dict(book='05-sgk-lich-su-va-dia-li-5', page=41, family='history, box + photo + timeline', order=[
        ('Nghe tin Hoằng Tháo sắp đến', 'body'),
        ('Chiến thắng Bạch Đằng của Ngô Quyền', 'body'),
        ('(Theo Đặng Khoa', 'body'),
        ('Hình 3', 'caption'),
        ('LUYỆN TẬP', 'heading'),
        ('1. Hãy vẽ và hoàn thiện trục thời gian', 'question'),
        ('2. Kể lại câu chuyện', 'question'),
        ('VẬN DỤNG', 'heading'),
        ('Tìm hiểu và kể tên một số di tích', 'question'),
    ], contiguous=['Nghe tin Hoằng Tháo sắp đến']),
    # ---- Địa lí 10, printed 39: body + two "Em có biết?" sidebars beside a figure and beside body text
    dict(book='10-sgk-dia-li-10', page=40, family='geography, body + right sidebars', order=[
        ('c) Nước băng tuyết', 'heading'),
        ('Khi nhiệt độ xuống dưới', 'body'),
        ('Băng tuyết khá phổ biến', 'body'),
        ('Em có biết', 'sidebar'),
        ('Các khối băng lớn thường có màu xanh', 'sidebar'),
        ('Hình 11.2', 'caption'),
        ('Đọc thông tin trong mục c', 'question'),
        ('d) Nước ngầm', 'heading'),
        ('Nước ngầm tồn tại ở dưới bề mặt đất', 'body'),
        ('Mực nước ngầm và lượng nước ngầm', 'body'),
        ('Nơi nước ngầm thoát lên mặt đất', 'sidebar'),
        ('Trong nước ngầm có hàm lượng', 'body'),
    ], contiguous=['Khi nhiệt độ xuống dưới', 'Mực nước ngầm và lượng nước ngầm']),
    # ---- Vật lí 10, printed 29: body + figure/caption right, question box, two side-by-side boxes
    dict(book='10-sgk-vat-li-10', page=30, family='physics, side-by-side boxes', order=[
        ('b) Tổng hợp hai vận tốc', 'heading'),
        ('Bài tập ví dụ', 'body'),
        ('Gọi vận tốc của ca nô', 'body'),
        ('Hình 5.4', 'caption'),
        ('Vì AB = BC', 'body'),
        ('1. Một máy bay đang bay', 'question'),
        ('2. Một người lái máy bay', 'question'),
        ('EM ĐÃ HỌC', 'heading'),
        ('Tốc độ trung bình', 'body'),
        ('EM CÓ THỂ', 'heading'),
        ('1. Tự xác định được tốc độ', 'sidebar'),
    ], contiguous=['Gọi vận tốc của ca nô']),
    # ---- Tiếng Việt 5 tập hai, printed 7: chapter opener — illustration only, one title; must not invent body
    dict(book='05-sgk-tieng-viet-5-tap-hai', page=8, family='literacy, image-only opener', order=[
        ('VẺ ĐẸP CUỘC SỐNG', 'heading'),
    ], contiguous=[]),
]


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def match_anchor(anchor, blocks):
    a = norm(anchor)
    toks = a.split()
    key = ' '.join(toks[:4]) if len(toks) >= 4 else a
    for b in blocks:
        t = norm(b['text'])
        if key and key in t:
            return b
    return None


def score_page(gold):
    path = f"poc-out/layout/{gold['book']}/p{gold['page']:03d}.json"
    try:
        page = json.load(open(path))
    except FileNotFoundError:
        return dict(book=gold['book'], page=gold['page'], error='not extracted')
    blocks = page['blocks']
    matched = []
    role_ok = 0
    for anchor, role in gold['order']:
        b = match_anchor(anchor, blocks)
        if b:
            matched.append((anchor, b['order'], role, b['role']))
            if b['role'] == role:
                role_ok += 1
    pairs = agree = 0
    for i in range(len(matched)):
        for j in range(i + 1, len(matched)):
            pairs += 1
            if matched[i][1] <= matched[j][1]:
                agree += 1
    fid_ok = fid_n = 0
    for anchor in gold.get('contiguous', []):
        b = match_anchor(anchor, blocks)
        if not b:
            continue
        fid_n += 1
        # a block is "clean" if no OTHER gold anchor (of a different role) is spliced into it
        spliced = any(norm(' '.join(norm(o).split()[:4])) in norm(b['text']) for o, r in gold['order'] if o != anchor and r in ('sidebar', 'caption', 'footnote', 'heading'))
        if not spliced:
            fid_ok += 1
    return dict(book=gold['book'], page=gold['page'], family=gold['family'],
                found=round(len(matched) / len(gold['order']), 2),
                order=round(agree / pairs, 2) if pairs else None,
                roles=round(role_ok / len(matched), 2) if matched else None,
                fidelity=round(fid_ok / fid_n, 2) if fid_n else None,
                trusted=page['layout']['trusted'], confidence=page['layout']['confidence'],
                misses=[a for a, _ in gold['order'] if not match_anchor(a, blocks)],
                roleErrors=[(a, g, e) for a, _, g, e in matched if g != e])


if __name__ == '__main__':
    results = [score_page(g) for g in GOLD]
    if '--json' in sys.argv:
        print(json.dumps(results, ensure_ascii=False, indent=1))
        sys.exit(0)
    for r in results:
        if 'error' in r:
            print(r); continue
        print(f"{r['book']:<32} p{r['page']:03d} found={r['found']:.2f} order={r['order']} roles={r['roles']} fidelity={r['fidelity']} trusted={r['trusted']} conf={r['confidence']}")
        if r['misses']: print('   misses:', r['misses'])
        if r['roleErrors']: print('   roleErr:', r['roleErrors'])
    ok = [r for r in results if 'error' not in r]
    def avg(k):
        v = [r[k] for r in ok if r.get(k) is not None]
        return round(sum(v) / len(v), 2) if v else None
    print(f"\nMEAN found={avg('found')} order={avg('order')} roles={avg('roles')} fidelity={avg('fidelity')}")
