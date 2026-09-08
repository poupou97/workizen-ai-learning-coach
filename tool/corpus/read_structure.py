#!/usr/bin/env python3
"""CẤU TRÚC ĐỌC — bài mở được có đọc ra một BÀI HỌC không, hay một bức tường chữ.

Máy thật, Vật lí 11 Bài 5: 4.980 ký tự trong MỘT khối. Đọc lại từ nguồn thì
trang sách có **67 khối** — mục «III. CƠ NĂNG», «2. Con lắc đơn», từng công
thức một. Cấu trúc CÓ SẴN và bị vứt đi ở bước ghi pack (`text=' '.join(...)`).

Đo được, 2.944/2.944 bài: số khối chữ trong pack ≤ số ảnh + 1, KHÔNG một ngoại
lệ. Nghĩa là dòng đọc chưa bao giờ được ngắt theo đoạn — nó chỉ bị cắt ở chỗ
chèn ảnh. «708 bài một khối» ở vòng trước là cách nói sai: đúng ra là **0%
bài có cấu trúc đoạn**, và 708 chỉ là những bài không có ảnh nào để cắt.

Cỡ đơn vị là một chuyện KHÁC, không chữa được bằng ngắt đoạn. Ngữ văn 11 Bài 1
dài 45 trang vì chính SÁCH gộp: bên trong nó có «VĂN BẢN 1», «VĂN BẢN 2»,
«ĐỌC», «VIẾT», «NÓI VÀ NGHE» — đó mới là đơn vị học. Nên phân họ:

  A  đơn vị nguồn dài thật     — dài, nhưng sách không đánh dấu đơn vị con
  B  nhiều bài bị gộp          — trong ruột có «Bài N» của bài KHÁC
  C  dải trang sai             — chồng lấn dải của bài khác
  E  mục lục khác hạt sản phẩm — sách tự đánh dấu ≥2 đơn vị con
  D  OCR/layout mất cấu trúc   — KHÔNG phải một họ: đúng với 100% bài

Không đặt ngưỡng ước lệ: mọi họ đều dựa trên DẤU HIỆU IN TRONG SÁCH.
"""
import re
import unicodedata

# Mốc đơn vị con do CHÍNH SÁCH in ra. Không suy diễn: mỗi mẫu ở đây đều đọc
# được nguyên văn trên trang (đã kiểm trên Ngữ văn 11 Bài 1).
SUBUNIT = [
    ('VAN_BAN', re.compile(r'\bVĂN BẢN\s*\d+')),
    ('DOC', re.compile(r'(?<![A-ZÀ-Ỹa-zà-ỹ])ĐỌC(?![A-ZÀ-Ỹa-zà-ỹ])')),
    ('VIET', re.compile(r'(?<![A-ZÀ-Ỹa-zà-ỹ])VIẾT(?![A-ZÀ-Ỹa-zà-ỹ])')),
    ('NOI_NGHE', re.compile(r'\bNÓI VÀ NGHE\b')),
    ('THUC_HANH_TV', re.compile(r'\bTHỰC HÀNH TIẾNG VIỆT\b')),
    ('TIET', re.compile(r'\bTIẾT\s+\d+')),
    ('HOAT_DONG', re.compile(r'\bHOẠT ĐỘNG\s+\d+')),
]

# Tiêu đề mục bên trong bài — chữ của sách, dùng để biết cấu trúc CÓ sẵn.
HEADING = re.compile(r'^\s*(?:[IVX]+\s*[.)]|\d{1,2}\s*[.)]|[a-đ]\s*\))\s*\S')
OTHER_LESSON = re.compile(r'\bB[àa]i\s+(\d{1,2})\b')
FIG_REF = re.compile(r'\bH[ìi]nh\s+(\d{1,2}[.,]\d{1,2})')
TAB_REF = re.compile(r'\bB[ảa]ng\s+(\d{1,2}[.,]\d{1,2})')


def fold(s):
    s = unicodedata.normalize('NFD', (s or '').upper())
    return re.sub(r'[̀-ͯ]', '', s).replace('Đ', 'D')


def subunit_marks(text):
    """`{tên mốc: số lần}` cho những mốc đơn vị con sách tự in."""
    return {name: len(p.findall(text or '')) for name, p in SUBUNIT
            if p.search(text or '')}


def other_lesson_numbers(text, lesson_no):
    """Số bài KHÁC xuất hiện trong ruột — dấu hiệu nhiều bài bị gộp."""
    return sorted({int(n) for n in OTHER_LESSON.findall(text or '')
                   if int(n) != lesson_no})


def heading_blocks(blocks):
    """Khối chữ mở đầu bằng đánh số mục — cấu trúc sách CÓ, pack đang mất."""
    return [b for b in blocks if HEADING.match(b)]


# Hai bài in trên CÙNG MỘT TRANG là chuyện thường của SGK: bài trước kết ở
# nửa trên, bài sau mở ở nửa dưới. Chồng đúng một trang KHÔNG phải lỗi.
# Chồng sâu thì có: đo được Tiếng Anh 3 Tập 2 có bài 11 và 12 CÙNG dải (5, 78)
# — trẻ mở hai bài khác nhau và nhận đúng một bức tường 74 trang y hệt.
SHARED_PAGE_OK = 1


def overlaps(ranges, *, deep_only=True):
    """`{(book, lesson)}` có dải trang chồng lấn SÂU với một bài khác cùng sách."""
    bad = set()
    by_book = {}
    for book, no, s, e in ranges:
        by_book.setdefault(book, []).append((s, e, no))
    for book, rs in by_book.items():
        rs.sort()
        for i in range(len(rs) - 1):
            a, b = rs[i], rs[i + 1]
            shared = a[1] - b[0] + 1
            if shared <= 0:
                continue
            if deep_only and shared <= SHARED_PAGE_OK:
                continue
            bad.add((book, a[2]))
            bad.add((book, b[2]))
    return bad


def identical_ranges(ranges):
    """`{(book, lesson)}` dùng CHUNG y hệt một dải với bài khác — chắc chắn sai."""
    bad, seen = set(), {}
    for book, no, s, e in ranges:
        seen.setdefault((book, s, e), []).append(no)
    for (book, s, e), nos in seen.items():
        if len(nos) > 1:
            bad |= {(book, n) for n in nos}
    return bad


def classify(*, pages, text, lesson_no, overlapping):
    """Họ nguyên nhân cho một bài. `None` = không có dấu hiệu bất thường.

    Thứ tự có chủ ý: dải sai là lỗi nội dung nặng nhất, phải nói trước.
    """
    if overlapping:
        return 'C_RANGE_SAI'
    # MỘT số bài lạ thường chỉ là câu dẫn «xem lại Bài 3» — đo được 153/197 ca
    # chỉ có đúng một số lạ. Gộp thật thì trong ruột có NHIỀU đầu bài khác.
    if len(other_lesson_numbers(text, lesson_no)) >= 2:
        return 'B_GOP_NHIEU_BAI'
    marks = subunit_marks(text)
    if sum(marks.values()) >= 2 and len(marks) >= 2:
        return 'E_HAT_MUC_LUC_KHAC'
    if pages >= 6:
        return 'A_DON_VI_DAI_THAT'
    return None
