#!/usr/bin/env python3
"""CHƯƠNG / CHỦ ĐỀ của sách, đọc từ chính trang sách.

`(sách, số bài)` KHÔNG đủ làm định danh. Đo trên corpus: 593 bản ghi va chạm
trên 154 khoá ở 45 sách, và `volume` cứu được 0. Số bài reset theo chủ đề —
GDTC có «Bài 1» cho mỗi môn thể thao, Tin học 9 có hai «Bài 9» ở hai chủ đề.
105/154 khoá có tiêu đề GIỐNG HỆT nhau, nên tiêu đề một mình cũng không tách được.

Tín hiệu thật nằm ngay trên trang mở chương:

    CHỦ ĐỀ / ĐỘI HÌNH ĐỘI NGŨ / 1 / BÀI 1 / CÁC TƯ THẾ ĐỨNG NGHIÊM, ĐỨNG NGHỈ
    CHỦ ĐỀ / BÀI TẬP THỂ DỤC  / 2 / BÀI 1 / ĐỘNG TÁC VƯƠN THỞ, ĐỘNG TÁC TAY

Đo được: dựng DÒNG THỜI GIAN chương cho cả cuốn rồi gán bài theo trang thì
88,9% bản ghi mơ hồ có chương, và chương TÁCH HẾT 77/154 khoá (240 bản ghi),
tách một phần thêm 30 khoá nữa.

⚠ CHỮ Đ KHÔNG PHÂN RÃ THEO NFD. «CHỦ ĐỀ» bỏ dấu vẫn còn `Đ` (U+0110), nên một
phép so trên ASCII sẽ trượt — và trượt IM LẶNG. Lần đo đầu của tôi báo 31,9%
thay vì 57,7% đúng vì lỗi này. Phải ánh xạ Đ→D một cách tường minh.
"""
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')

HEAD_LINES = 8          # dấu chương nằm ở đầu trang, không rải giữa bài
MIN_NAME = 6            # tên chương ngắn hơn ngần này thường là số/nhiễu
MARKER = re.compile(r'\b(CHU\s*DE|PHAN|CHUONG)\b')


def fold(s):
    """Bỏ dấu ĐỂ SO SÁNH — kể cả `Đ`, thứ NFD không đụng tới."""
    s = unicodedata.normalize('NFD', (s or '').upper())
    return re.sub(r'[̀-ͯ]', '', s).replace('Đ', 'D')


def chapter_openers(book, ocr_dir=OCR):
    """Các trang MỞ CHƯƠNG của cuốn, theo thứ tự trang PDF: [(page, tên)].

    Tên chương lấy NGUYÊN VĂN dòng dài nhất ở đầu trang không phải chính chữ
    «CHỦ ĐỀ» — chữ của sách, không phải chữ máy đặt.
    """
    out = []
    for p in sorted(glob.glob(os.path.join(ocr_dir, book, 'p*.json'))):
        try:
            page = int(os.path.basename(p)[1:4])
            with open(p, encoding='utf-8') as fh:
                lines = json.load(fh)['lines']
        except (OSError, ValueError, KeyError):
            continue
        top = sorted([l for l in lines if (l.get('text') or '').strip()],
                     key=lambda z: z['y'])[:HEAD_LINES]
        if not MARKER.search(fold(' '.join(l['text'] for l in top))):
            continue
        names = [l['text'].strip() for l in top
                 if len(l['text'].strip()) >= MIN_NAME
                 and not MARKER.search(fold(l['text']))]
        if names:
            out.append((page, names[0]))
    return out


def chapter_at(openers, page_pdf, slack=1):
    """Chương chứa trang này: cái mở gần nhất KHÔNG SAU nó.

    `slack` cho phép trang mở chương và trang mở bài lệch nhau một trang — đo
    được là có thật trong cùng một cuốn. `None` = trang nằm trước mọi chương ⇒
    KHÔNG đoán.
    """
    prev = [c for c in openers if c[0] <= page_pdf + slack]
    return prev[-1][1] if prev else None


def resolve_group(records, openers, offset):
    """Tách một nhóm bài trùng số bằng chương.

    `records`: [{'no', 'pageStart', ...}] cùng `(sách, số bài)`.
    Trả `(resolved, withheld, reason)` — `resolved` là các bản ghi có chương
    RIÊNG, `withheld` là phần không tách được.

    ⭐ SAI BÀI NGUY HIỂM HƠN THIẾU BÀI. Không đủ bằng chứng ⇒ giữ lại, không
    đoán, không fuzzy-match để tăng coverage.
    """
    tagged = []
    for r in records:
        ps = r.get('pageStart')
        ch = chapter_at(openers, ps + offset) if (ps is not None and offset is not None) else None
        tagged.append((ch, r))
    if any(ch is None for ch, _ in tagged):
        return [], records, 'NO_CHAPTER'

    by_chapter = {}
    for ch, r in tagged:
        by_chapter.setdefault(ch, []).append(r)

    resolved, withheld, reason = [], [], None
    for ch, group in by_chapter.items():
        if len(group) == 1:
            resolved.append((ch, group[0]))
            continue
        # Cùng chương VÀ cùng trang mở ⇒ mục lục đọc hai lần một bài: gộp.
        starts = {r.get('pageStart') for r in group}
        if len(starts) == 1:
            resolved.append((ch, group[0]))
            continue
        # Cùng chương, khác trang ⇒ vẫn là hai bài khác nhau mà chương không
        # phân biệt được. Giữ lại cả nhóm.
        withheld.extend(group)
        reason = 'CHAPTER_NOT_DISCRIMINATING'
    return resolved, withheld, reason
