#!/usr/bin/env python3
"""ĐƠN VỊ CẤU TRÚC CỦA SÁCH — corpus tự nói, không áp taxonomy trước.

    python3 tool/corpus/structural_units.py

Giả thuyết cần đo: «BÀI» có phải đơn vị nội dung phổ quát của mọi SGK không?

CÁCH ĐO — không đưa sẵn danh sách từ. Gom mọi «TỪ HOA + SỐ» đứng đầu trang rồi
để bằng chứng tự phân loại, qua BA luật, mỗi luật sinh ra vì một thứ nhiễu ĐO
ĐƯỢC chứ không phải vì linh cảm:

  1. mỗi số chỉ ở ≤2 trang     — loại TIÊU ĐỀ CHẠY. Không có luật này thì
                                 «TOÁN» và «TIẾNG VIỆT» đứng đầu bảng đơn vị:
                                 chúng là tên sách in ở chân mọi trang.
  2. chữ cái đầu viết hoa      — loại CÂU VĂN THƯỜNG («đến 5 giờ»).
  3. số TĂNG DẦN theo trang    — loại DẤU THAM CHIẾU NỘI DUNG. «Bài 1…Bài 17»
                                 đi suốt cuốn theo thứ tự; «Hình 1», «Bảng 2»,
                                 «Bước 3» đánh lại từ đầu ở mỗi bài. Không có
                                 luật này thì HÌNH (19 sách), BƯỚC (12),
                                 BẢNG (7) đứng lẫn trong bảng đơn vị.

⚠ MỘT LỖI ĐO ĐÃ MẮC VÀ ĐÃ SỬA: `[A-ZÀ-Ỹ]` KHÔNG phải «chữ hoa tiếng Việt». Đó
là dải mã U+00C0–U+1EF8 và nó CHỨA CẢ CHỮ THƯỜNG CÓ DẤU (á, ê, í, đ…). Lần đo
đầu dùng nó nên vừa bắt nhầm câu văn thường, vừa báo 159/238 sách «không có đơn
vị» — sai. Số đúng ở dưới.

KẾT QUẢ (238 sách canonical):

    BÀI              77 sách · 1.554 bài
    (không có dấu)   77 sách ·   703 bài
    CHỦ ĐỀ           19 sách ·   345 bài
    TUẦN             10 sách ·   300 bài
    BẢNG              8 sách ·   214 bài   ← còn nhiễu
    HÌNH              9 sách ·   117 bài   ← còn nhiễu
    CHUYÊN ĐỀ         6 sách ·    67 bài
    PHẦN              4 sách ·    93 bài
    BÀI SỐ            4 sách ·    32 bài
    REVIEW            3 sách ·    36 bài

TRẢ LỜI GIẢ THUYẾT: đúng, «BÀI» KHÔNG phổ quát — nó phủ 77/238 sách (42% số
bài). CHỦ ĐỀ và TUẦN là đơn vị thật của 29 sách khác (645 bài).

⛔ NHƯNG ĐÒN BẨY CHỈ MỘT PHẦN — chưa đủ để đổi kiến trúc:
  · TITLE_MISSING 395: 171 (43%) nằm trong sách có đơn vị khác «BÀI»;
  · AMBIGUOUS (census) 80: 53 (66%);
  · Kiểm tận nơi hai họ lớn nhất:
      TUẦN   (81 bài, HĐTN): nhãn «TUẦN N» KHÔNG nằm trên trang mở bài — 0/14.
              Mục lục và cấu trúc tuần của sách không khớp nhau.
      CHỦ ĐỀ (57 bài, phần lớn GDTC): 36/57 = 63% CÓ nhãn trên trang.

Một họ trúng 63%, một họ trúng 0%. Chưa phải một phép sửa generic có đòn bẩy
quyết định, nên KHÔNG cài mô hình LearningUnit trong vòng này — đo trước, ghi
lại, để Founder quyết có đầu tư thay đổi lớn hơn không.

Ngoài lề nhưng đáng ghi: soi họ TUẦN thì thấy mục lục HĐTN có HAI DÃY ĐAN NHAU
(bài 1 ở trang 6 *và* 7; bài 2 ở 9 và 14…) — bảng mục lục hai cột bị đọc thành
một dãy. Toàn corpus: 5 sách, 125 mục. Cũng nhỏ.
"""
import argparse
import collections
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')
PACK = os.path.join(ROOT, 'assets/pack')

HEAD_LINES = 5          # dấu đơn vị ở đầu trang, không rải giữa bài
MIN_UNITS = 3           # dưới ngần này không đủ để gọi là một dãy
MAX_PAGES_PER_UNIT = 2  # một số xuất hiện ở nhiều trang hơn ⇒ tiêu đề chạy
RUNNING_HEADER_SHARE = 0.8
# ⚠ `[A-ZÀ-Ỹ]` KHÔNG phải «chữ hoa tiếng Việt»: đó là dải mã U+00C0–U+1EF8 và
# nó CHỨA CẢ CHỮ THƯỜNG CÓ DẤU (á, ê, í, đ…). Dùng nó thì «đến 5 giờ» cũng
# thành một «đơn vị cấu trúc» tên là DEN. Phải hỏi thẳng từng ký tự.
MARKER = re.compile(r'^(\S[^\d]{0,17}?)\s*(\d{1,2})\b')


def _starts_upper(w):
    """Chữ CÁI ĐẦU viết hoa? Dấu đơn vị luôn mở đầu bằng chữ hoa («Bài 17»,
    «CHỦ ĐỀ 2»); câu văn thường thì không («đến 5 giờ», «ánh sáng 3 màu»)."""
    for c in w:
        if c.isalpha():
            return c.isupper()
    return False


def fold(s):
    s = unicodedata.normalize('NFD', (s or '').upper())
    return re.sub(r'[̀-ͯ]', '', s).replace('Đ', 'D')


def markers_in_book(book, ocr_dir=OCR):
    """`{(từ, số): {trang}}` — mọi «TỪ + SỐ» đứng đầu trang trong cuốn."""
    seen = collections.defaultdict(set)
    for p in sorted(glob.glob(os.path.join(ocr_dir, book, 'p*.json'))):
        try:
            page = int(os.path.basename(p)[1:4])
            with open(p, encoding='utf-8') as fh:
                lines = json.load(fh)['lines']
        except (OSError, ValueError, KeyError):
            continue
        top = sorted([l for l in lines if (l.get('text') or '').strip()],
                     key=lambda z: z['y'])[:HEAD_LINES]
        for l in top:
            m = MARKER.match((l.get('text') or '').strip())
            if not m:
                continue
            raw = m.group(1).strip()
            if not _starts_upper(raw):
                continue          # dấu đơn vị in HOA; câu văn thường thì không
            w = fold(raw).strip()
            if 2 <= len(w) <= 18:
                seen[(w, int(m.group(2)))].add(page)
    return seen


def dominant_unit(book, ocr_dir=OCR):
    """Đơn vị chiếm ưu thế của cuốn, hoặc `(None, 0)`.

    Tiêu đề chạy bị loại bằng BẰNG CHỨNG: cùng một số mà xuất hiện ở nhiều
    trang thì nó không đánh dấu một đơn vị nào cả.
    """
    seen = markers_in_book(book, ocr_dir)
    per_word = collections.defaultdict(list)
    for (w, _), pages in seen.items():
        per_word[w].append(len(pages))
    best = (None, 0)
    for w, counts in per_word.items():
        if len(counts) < MIN_UNITS:
            continue
        share = sum(1 for c in counts if c <= MAX_PAGES_PER_UNIT) / len(counts)
        if share < RUNNING_HEADER_SHARE:
            continue
        if not _ascends_through_book(seen, w):
            continue
        if len(counts) > best[1]:
            best = (w, len(counts))
    return best


def _ascends_through_book(seen, word, min_share=0.8):
    """Số của đơn vị có TĂNG DẦN theo trang suốt cuốn không?

    Đây là chỗ tách ĐƠN VỊ CẤU TRÚC khỏi DẤU THAM CHIẾU NỘI DUNG, bằng bằng
    chứng chứ không bằng danh sách đen. «Bài 1 … Bài 17» đi từ đầu tới cuối
    cuốn theo thứ tự. «Hình 1», «Bảng 2», «Bước 3» thì đánh lại từ đầu ở mỗi
    bài, nên dãy của chúng lên xuống lộn xộn.

    Không có luật này thì HÌNH (19 sách), BƯỚC (12), BẢNG (7), NHỊP (3) đứng
    lẫn trong bảng đơn vị cấu trúc — đo được trên chính corpus.
    """
    pts = sorted((n, min(pages)) for (w, n), pages in seen.items() if w == word)
    if len(pts) < MIN_UNITS:
        return False
    rises = sum(1 for a, b in zip(pts, pts[1:]) if b[1] > a[1])
    return rises / (len(pts) - 1) >= min_share


def interleaved_toc(lessons):
    """Mục lục HAI CỘT bị đọc thành một dãy.

    Dấu hiệu: mỗi số xuất hiện đúng hai lần, và tách được thành hai dãy trang
    ĐỀU TĂNG, dãy sau luôn nằm sau dãy trước ở cùng số.
    """
    by = collections.defaultdict(list)
    for l in lessons:
        if l.get('pageStart') is not None:
            by[l['no']].append(l['pageStart'])
    pairs = sorted((n, sorted(v)) for n, v in by.items() if len(v) == 2)
    if len(pairs) < 4:
        return False
    a = [v[0] for _, v in pairs]
    b = [v[1] for _, v in pairs]
    mono = lambda s: all(x <= y for x, y in zip(s, s[1:]))  # noqa: E731
    return mono(a) and mono(b) and all(x < y for x, y in zip(a, b))


def audit(pack_dir=PACK, ocr_dir=OCR):
    books = {}
    for g in range(1, 13):
        p = os.path.join(pack_dir, f'lesson-index-g{g}.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for subject, bl in (d.get('subjects') or {}).items():
            for b in bl:
                books[b['sourceDocumentId']] = dict(
                    grade=g, subject=subject, lessons=len(b.get('lessons') or []),
                    interleaved_toc=interleaved_toc(b.get('lessons') or []))
    for bid, info in books.items():
        w, n = dominant_unit(bid, ocr_dir)
        info['unit'] = w
        info['units_found'] = n
    return books
