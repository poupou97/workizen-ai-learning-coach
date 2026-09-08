#!/usr/bin/env python3
"""TÌM DẢI TRANG cho đơn vị mà MỤC LỤC KHÔNG GHI TRANG.

Census 107 ca `SOURCE_RANGE`:

    không trang · CÓ tên      59   ← chỉ tập này có bằng chứng để tìm
    không trang · không tên   36   ← không có gì để tìm ⇒ giữ lại
    có trang, attach trượt    12

«Mục lục không ghi trang» KHÔNG đồng nghĩa «sách không có bài ấy». Nhưng tìm nó
phải bằng bằng chứng, và phải chấp nhận rằng phần lớn sẽ KHÔNG tìm được.

HAI BẰNG CHỨNG, KHÔNG PHẢI HAI CƠ HỘI ĐOÁN:
  1. TÊN đơn vị mở đầu trang (nửa trên, ngoài dải đầu/chân trang);
  2. SỐ đơn vị có mặt trên chính trang ấy («Bài 12», «Unit 12», «Chủ đề 12»).

Bằng chứng (2) chỉ dùng để TÁCH khi (1) cho nhiều trang — không bao giờ dùng một
mình. Đo được: tên-duy-nhất 14 ca; thêm số bài tách được thêm 12 ⇒ 26/59.

BỐN THỨ BỊ LOẠI, vì mỗi thứ đều làm một trang «trông như» chỗ mở bài:
  · TRANG MỤC LỤC — nó liệt kê tên bài nhưng không phải chỗ bài bắt đầu. Nhận
    ra bằng chính dữ liệu: trang chứa ≥3 tên bài khác của cùng cuốn.
  · CHÚ THÍCH HÌNH («Hình 3. …») chứa cùng cụm từ.
  · NỬA DƯỚI TRANG — một bài mở ở đầu trang, không ở giữa thân bài.
  · DẢI ĐẦU/CHÂN TRANG — tiêu đề chạy lặp khắp cuốn.

⭐ 0 hoặc >1 ứng viên ⇒ GIỮ LẠI. Không «chọn ứng viên tốt nhất»: khi hai trang
cùng khớp, ta không biết trang nào là chỗ bắt đầu, và đoán sai thì trẻ mở nhầm.

⭐ END KHÔNG SUY BỪA THEO SỐ TRANG. Nó lấy từ ĐƠN VỊ KẾ TIẾP ĐÃ XÁC NHẬN — trang
mở của đơn vị gần nhất phía sau. Không có đơn vị nào phía sau thì hết sách. Suy
«mỗi bài bốn trang» là bịa một cái ranh giới không có trong sách.
"""
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')

HEAD_LINES = 10
TOP_BAND = 0.45        # bài mở ở NỬA TRÊN trang
MARGIN_TOP = 0.05
MARGIN_BOTTOM = 0.95
NAME_MATCH = 0.8
TOC_TITLE_HITS = 3     # trang chứa ngần này tên bài khác ⇒ là trang mục lục
MIN_TOC_TITLE = 12     # tên quá ngắn thì trùng ngẫu nhiên, không tính

CAPTION = re.compile(r'^\s*(hình|bảng|sơ\s*đồ|biểu\s*đồ)\s*[\d IVX]', re.I)


def norm(s):
    s = unicodedata.normalize('NFC', (s or '').lower())
    return re.sub(r'\s+', ' ', re.sub(r'[^0-9a-zà-ỹ\s]', ' ', s)).strip()


def page_head(lines):
    """Dòng ở NỬA TRÊN trang, ngoài dải đầu/chân trang, bỏ chú thích hình."""
    return [l for l in lines
            if (l.get('text') or '').strip()
            and MARGIN_TOP <= (l.get('y') or 0) <= min(TOP_BAND, MARGIN_BOTTOM)
            and not CAPTION.match((l.get('text') or '').strip())]


def is_toc_page(lines, book_titles):
    """Trang MỤC LỤC — liệt kê tên bài nhưng không phải chỗ bài bắt đầu."""
    t = norm(' '.join((l.get('text') or '') for l in lines))
    return sum(1 for x in book_titles
               if len(x) >= MIN_TOC_TITLE and x in t) >= TOC_TITLE_HITS


def opens_with_name(lines, title):
    tk = [w for w in norm(title).split() if len(w) > 2]
    if not tk:
        return False
    h = norm(' '.join((l.get('text') or '') for l in page_head(lines)))
    return sum(1 for w in tk if w in h) / len(tk) >= NAME_MATCH


def carries_number(lines, number):
    """Trang có mang SỐ của chính đơn vị này không? Bằng chứng THỨ HAI."""
    pat = re.compile(rf'\b(b[àa]i|unit|lesson|ch[uủ]\s*[đd][eề]|ph[àầ]n)\s*0?{number}\b',
                     re.I)
    txt = ' '.join((l.get('text') or '') for l in lines
                   if MARGIN_TOP <= (l.get('y') or 0) <= TOP_BAND)
    return bool(pat.search(unicodedata.normalize('NFC', txt)))


def candidate_pages(book, title, number, book_titles, ocr_dir=OCR):
    """Trang có thể là chỗ mở đơn vị — theo TÊN, kèm cờ có/không mang SỐ."""
    out = []
    for p in sorted(glob.glob(os.path.join(ocr_dir, book, 'p*.json'))):
        try:
            page = int(os.path.basename(p)[1:4])
            with open(p, encoding='utf-8') as fh:
                lines = json.load(fh)['lines']
        except (OSError, ValueError, KeyError):
            continue
        if is_toc_page(lines, book_titles):
            continue
        if opens_with_name(lines, title):
            out.append((page, carries_number(lines, number)))
    return out


def locate_start(book, title, number, book_titles, ocr_dir=OCR):
    """Trang mở đơn vị, hoặc `None` khi bằng chứng không quyết được.

    Số đơn vị chỉ dùng để TÁCH khi tên cho nhiều trang — không bao giờ dùng một
    mình, vì «Bài 12» xuất hiện ở mọi trang của bài 12.
    """
    hits = candidate_pages(book, title, number, book_titles, ocr_dir)
    if len(hits) == 1:
        return hits[0][0]
    with_number = [p for p, has in hits if has]
    return with_number[0] if len(with_number) == 1 else None


def locate_end(start, confirmed_starts, last_page):
    """END = ngay trước ĐƠN VỊ KẾ TIẾP ĐÃ XÁC NHẬN.

    `confirmed_starts` là các trang mở đã biết chắc trong cùng cuốn. Không có
    đơn vị nào phía sau ⇒ hết sách. `None` khi không có gì để chốt ranh giới —
    một START đúng không đáng biến thành một dải bịa.
    """
    later = sorted(p for p in confirmed_starts if p > start)
    end = (later[0] - 1) if later else last_page
    return end if end >= start else None
