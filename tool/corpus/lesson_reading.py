#!/usr/bin/env python3
"""Nội dung ĐỌC của một bài, lấy từ chính trang sách của bài ấy.

Đây là mảnh còn thiếu giữa hai lane. Census đo được: 3.142 bài có nội dung đọc
được, nhưng sản phẩm chỉ mở được 117 — vì `LessonIndex.activitiesFor` chỉ có
năm họ hoạt động (Toán bài tập · TV đọc · TV viết · Sử nguồn · Khoa thí nghiệm)
và KHÔNG có họ «đọc trang sách». Lớp 1, 2, 3, 11, 12 vì thế có ĐÚNG 0 bài mở được.

⭐ CHỈ NHẬN BÀI CHỨNG MINH ĐƯỢC THỨ TỰ ĐỌC.
Apple Vision trả dòng theo thứ tự trên–xuống (đo: nghịch thế trung vị 0%, 98%
trang dưới 2%), nên trang MỘT luồng ghép thẳng là đúng thứ tự đọc. Trang HAI
CỘT thì không: ghép theo y sẽ đan hai cột vào nhau và trẻ đọc một câu vô nghĩa
ghép từ hai câu khác nhau. Bài nào có trang như thế bị GẮN CỜ `READING_ORDER`
và KHÔNG phát nội dung — thà bài chưa mở được còn hơn bài mở ra chữ lộn.
Đo trên corpus: 2.340/3.142 bài an toàn (74,5%), 802 bài phải gắn cờ.

⚠ NGUYÊN VĂN, KHÔNG VIẾT LẠI. Chữ ở đây là chữ trong sách. Máy chỉ được bỏ
phần KHÔNG thuộc dòng chảy bài học (số trang, tiêu đề chạy đầu/cuối trang) và
ghép lại; không tóm tắt, không sửa, không diễn giải.
"""
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')

# Dải trên/dưới trang nơi số trang và tiêu đề chạy nằm.
FURNITURE_TOP = 0.055
FURNITURE_BOTTOM = 0.945
LONG_LINE = 0.25      # dòng «dài» = dòng văn thật, không phải ô bảng
COL_SPLIT = 0.45      # mốc trái/phải khi xét hai luồng
MIN_SPAN = 0.25       # mỗi luồng phải trải ≥ ngần này chiều cao mới coi là cột


def page_lines(book, pdf_page):
    p = os.path.join(OCR, book, f'p{pdf_page:03d}.json')
    try:
        with open(p, encoding='utf-8') as fh:
            return json.load(fh)['lines']
    except (OSError, ValueError, KeyError):
        return None


def is_two_column(lines):
    """Hai LUỒNG VĂN BẢN song song — không phải bảng.

    Chỉ xét dòng DÀI: một bảng gồm nhiều ô ngắn nên không lọt vào phép đo này,
    và ta không muốn xé một bảng ra làm hai cột.
    """
    big = [l for l in lines if (l.get('w') or 0) >= LONG_LINE]
    if len(big) < 6:
        return False
    left = [l for l in big if l['x'] < COL_SPLIT]
    right = [l for l in big if l['x'] >= COL_SPLIT]
    if len(left) < 3 or len(right) < 3:
        return False

    def span(g):
        return max(l['y'] for l in g) - min(l['y'] for l in g)

    return span(left) > MIN_SPAN and span(right) > MIN_SPAN


def is_furniture(line):
    """Số trang / tiêu đề chạy — thuộc về CUỐN SÁCH, không thuộc dòng chảy bài."""
    y = line.get('y') or 0
    if FURNITURE_TOP < y < FURNITURE_BOTTOM:
        return False
    t = (line.get('text') or '').strip()
    if not t:
        return True
    # số trang trần, hoặc dòng rất ngắn ở mép — không phải câu của bài
    return bool(re.fullmatch(r'[\d\W]{0,6}', t)) or len(t) <= 3


def margin_texts(lines):
    """Chữ nằm ở dải mép trên/dưới — ứng viên tiêu đề chạy."""
    return {(l.get('text') or '').strip()
            for l in lines
            if not (FURNITURE_TOP < (l.get('y') or 0) < FURNITURE_BOTTOM)
            and (l.get('text') or '').strip()}


def running_headers(pages_lines):
    """Chữ ở mép LẶP LẠI qua ≥2 trang của bài ⇒ thuộc về cuốn sách, không phải bài.

    Dùng bằng chứng lặp thay vì độ dài. Cắt theo độ dài sẽ xoá cả tên bài:
    «TÁCH CHẤT KHỎI HỖN HỢP» nằm ở y≈0,058 — ngay sát dải mép — và chỉ xuất
    hiện MỘT lần, đúng ở trang mở bài.
    """
    seen = {}
    for lines in pages_lines:
        for t in margin_texts(lines):
            seen[t] = seen.get(t, 0) + 1
    return {t for t, n in seen.items() if n >= 2}


def page_text(lines, drop=frozenset()):
    return ' '.join((l.get('text') or '').strip()
                    for l in lines
                    if not is_furniture(l) and (l.get('text') or '').strip() not in drop).strip()


HEAD_CHARS = 400      # phần đầu bài, nơi tên bài phải xuất hiện
START_MATCH = 0.5     # tỉ lệ từ của tên bài phải có mặt ở phần đầu ấy


def _norm(s):
    s = unicodedata.normalize('NFC', (s or '').lower())
    return re.sub(r'\s+', ' ', re.sub(r'[^0-9a-zà-ỹ\s]', ' ', s)).strip()


def starts_at_lesson(head, title):
    """Nội dung có thật sự MỞ ĐẦU bằng bài này không?

    Dải trang do attach gán có thể bắt đầu trễ một trang: bài vẫn «có nội dung»
    nhưng trẻ mở ra đã ở giữa bài, mất phần mở đầu. Đo được trên corpus: 101 bài
    (4,3% số bài phát được) rơi vào đây. Lùi một trang chỉ cứu 28 bài, nên đây
    là CỔNG, không phải chỗ để đoán.

    `None` = không kiểm được (không có tên) ⇒ người gọi tự quyết, không im lặng.
    """
    t = _norm(title)
    if not t:
        return None
    h = _norm(head)[:HEAD_CHARS]
    toks = [w for w in t.split() if len(w) > 2]
    if not toks:                      # tên rất ngắn («Ôn tập») — khớp cả cụm
        return t in h
    return sum(1 for w in toks if w in h) / len(toks) >= START_MATCH


def lesson_reading(book, page_pdf_start, page_pdf_end, *, printed_start=None, title=None):
    """Nội dung đọc của bài, hoặc `None` kèm lý do nếu KHÔNG chứng minh được.

    Trả `(payload, reason)` — đúng một trong hai khác `None`.
    """
    if page_pdf_start is None or page_pdf_end is None or page_pdf_end < page_pdf_start:
        return None, 'SOURCE_RANGE'
    raw, missing = [], 0
    for pp in range(page_pdf_start, page_pdf_end + 1):
        lines = page_lines(book, pp)
        if lines is None:
            missing += 1
            continue
        if is_two_column(lines):
            return None, 'READING_ORDER'
        raw.append((pp, lines))
    if missing:
        return None, 'OCR_MISSING'
    drop = running_headers([l for _, l in raw])
    pages = []
    for pp, lines in raw:
        txt = page_text(lines, drop)
        if txt:
            pages.append(dict(pagePdf=pp, text=txt))
    if not pages:
        return None, 'CONTENT_THIN'
    if title is not None and starts_at_lesson(pages[0]['text'], title) is False:
        return None, 'LESSON_START_UNCONFIRMED'
    return dict(book=book, pagePdfStart=page_pdf_start, pagePdfEnd=page_pdf_end,
                pageStart=printed_start, pages=pages,
                extraction='ocr-single-flow-v1'), None
