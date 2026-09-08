#!/usr/bin/env python3
"""NHÃN PHÂN BIỆT cho những cuốn cùng tên trên giá sách.

Máy thật, lớp 11: TÁM cuốn hiện y hệt «Mĩ thuật 11 · 2 bài». Phân môn (Đồ hoạ,
Hội hoạ, Kiến trúc, Thiết kế thời trang…) chỉ in TRÊN BÌA, không có trong nhãn.
Trẻ nhìn tám ô giống nhau và không biết mở cuốn nào.

Đo được: 65/238 sách (27%) trùng nhãn với ít nhất một cuốn khác — 20 cuốn ở mỗi
lớp 10, 11, 12.

⭐ TÊN PHÂN MÔN KHÔNG CÓ TRONG REGISTRY. Nó chỉ nằm trên trang bìa. Suy từ định
danh (`thiet-ke-thoi-trang` → «Thiết kế thời trang») là BỊA DẤU TIẾNG VIỆT — máy
không biết «hoa» là «hoạ» hay «hoà».

Nên đọc từ bìa, và XÁC MINH CHÉO: dòng bìa được nhận chỉ khi nó chứa ĐỦ các từ
phân biệt trong chính định danh của cuốn sách. Hai nguồn độc lập phải đồng ý —
không có chuyện lấy bừa một dòng to trên bìa làm tên.

Đo được: 56/65 = 86% đọc được theo luật ấy. 9 cuốn còn lại KHÔNG có nhãn phân
biệt — thà để trùng còn hơn dán một cái tên không kiểm được.
"""
import glob
import json
import os
import re
import unicodedata

COVER_PAGES = 3        # tên phân môn nằm ở bìa, không rải trong ruột sách
MIN_WORD = 3           # từ ngắn hơn không phân biệt được gì
MIN_LABEL = 3
MAX_LABEL = 60

BOOK_ID = re.compile(r'^\d{2}-sgk-(.+?)-(\d{1,2})-(.+)$')


def fold(s):
    s = unicodedata.normalize('NFD', (s or '').upper())
    return re.sub(r'[̀-ͯ]', '', s).replace('Đ', 'D')


def distinguishing_words(book_id):
    """Các từ trong định danh nằm SAU «<môn>-<lớp>-» — phần phân biệt cuốn này."""
    m = BOOK_ID.match(book_id)
    if not m:
        return set()
    return {fold(w) for w in m.group(3).split('-') if len(w) >= MIN_WORD}


def variant_label(book_id, ocr_dir):
    """Nhãn phân biệt đọc từ bìa, hoặc `None` khi không xác minh chéo được."""
    words = distinguishing_words(book_id)
    if not words:
        return None
    for p in sorted(glob.glob(os.path.join(ocr_dir, book_id, 'p*.json')))[:COVER_PAGES]:
        try:
            with open(p, encoding='utf-8') as fh:
                lines = json.load(fh)['lines']
        except (OSError, ValueError, KeyError):
            continue
        for l in lines:
            t = (l.get('text') or '').strip()
            if not (MIN_LABEL <= len(t) <= MAX_LABEL):
                continue
            ft = fold(t)
            flat = ft.replace(' ', '')
            # MỌI từ phân biệt phải có mặt: một dòng bìa chỉ khớp một nửa thì
            # không chứng minh được nó là tên của CUỐN NÀY.
            if all(w in ft or w in flat for w in words):
                return t
    return None


def label_variants(books, ocr_dir):
    """`{book_id: nhãn}` cho những cuốn TRÙNG nhãn với cuốn khác.

    Cuốn không trùng thì không cần nhãn phụ — thêm chữ vào chỗ không cần chỉ làm
    giá sách ồn hơn.
    """
    seen = {}
    for b in books:
        key = (b.get('title'), b.get('volumeLabel'))
        seen.setdefault(key, []).append(b)
    out = {}
    for key, group in seen.items():
        if len(group) < 2:
            continue
        for b in group:
            lab = variant_label(b['sourceDocumentId'], ocr_dir)
            if lab:
                out[b['sourceDocumentId']] = lab
    return out
