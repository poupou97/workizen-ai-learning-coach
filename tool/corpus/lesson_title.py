#!/usr/bin/env python3
"""TÊN BÀI — phân loại tín hiệu nguồn. KẾT QUẢ: KHÔNG KHÔI PHỤC ĐƯỢC AN TOÀN.

395 bài không có tên trong mục lục, và tên là điều kiện để bài xuất hiện cho
trẻ. Đo tín hiệu trên trang mở bài của cả 395:

    A  «Bài N: Tên» trên MỘT dòng                       17
    B  «Bài N» + tên cùng hàng bên phải                 59
    C  «Bài N» + dòng ngay dưới                          2
    E  KHÔNG có dấu «Bài» nào                          317
         · 133 sách tổ chức theo CHỦ ĐỀ/TUẦN — đơn vị của sách KHÔNG phải «bài»
         · 148 không có dấu nào trên trang
         ·  36 không có dải trang

⛔ ĐÃ THỬ VÀ ĐÃ BỎ. Mọi họ đều rò lỗi mà bằng chứng sẵn có không chặn được:

  C  bắt «YÊU CẦU CẦN ĐẠT» — tiêu đề MỤC, không phải tên bài.
  B  59 ca; siết hết mức vẫn còn 2/9 ghép SAI THỨ TỰ:
       «TRONG HÔN NHÂN VÀ GIA ĐÌNH QUYỀN VÀ NGHĨA VỤ CỦA CÔNG DÂN»
          (đúng: «QUYỀN VÀ NGHĨA VỤ CỦA CÔNG DÂN TRONG HÔN NHÂN VÀ GIA ĐÌNH»)
     OCR trả các mảnh của một tên xuống dòng như thể cùng một hàng, và thứ tự x
     không dựng lại được thứ tự đọc.
  A  sau khi thêm chốt xuống-dòng và chốt trùng-tên còn 7 ca; ca cuối cùng kiểm
     tay thì phát hiện dải trang của nó BẮT ĐẦU GIỮA BÀI, nên cái tên đọc được
     là tên của BÀI KẾ TIẾP.

⭐ SAI TÊN NGUY HIỂM HƠN THIẾU TÊN. Tên sai không im lặng như một bài vắng mặt:
nó nằm trên giá sách, trẻ mở đúng cái mình tưởng và đọc phải bài khác. 7 cái tên
không đáng đổi lấy rủi ro ấy, nên module này KHÔNG phát tên nào.

Cái nó còn làm: phân loại để census đo được họ này, và ghi lại kết quả âm để
không ai thử lại ba lần nữa. Đường đi đúng cho 133 sách kia không phải «đọc tên
bài» mà là nhận ra đơn vị của chúng là CHỦ ĐỀ/TUẦN — một câu hỏi cấu trúc khác.
"""

import re
import unicodedata

MARGIN_TOP = 0.05
MARGIN_BOTTOM = 0.95
ROW_TOL = 0.02          # cùng «hàng ngang» khi tâm y lệch dưới ngần này
MIN_LEN = 4
MAX_LEN = 120           # dài hơn nữa là câu văn, không phải tên bài

INLINE = re.compile(r'^\s*B[àa]i\s*(\d+)\s*[:.]\s*(\S.*)$', re.I)
NUM_ONLY = re.compile(r'^\s*B[àa]i\s*(\d+)\s*[.:]?\s*$', re.I)
CAPTION = re.compile(r'^\s*(hình|bảng|sơ\s*đồ|biểu\s*đồ)\s*[\d IVX]', re.I)

# Tiêu đề MỤC in sẵn trong mọi bài — không phải tên riêng của bài nào.
SECTION_WORDS = {
    'MUC TIEU', 'YEU CAU CAN DAT', 'KHAM PHA', 'LUYEN TAP', 'VAN DUNG',
    'THUC HANH', 'MO DAU', 'KHOI DONG', 'GHI NHO', 'EM CO BIET', 'EM CO THE',
    'HOAT DONG', 'KIEN THUC MOI', 'TU DANH GIA', 'CHUAN BI', 'TIEN HANH',
}
TOPIC = re.compile(r'\b(CHU\s*DE|PHAN|CHUONG|TUAN)\b')


def fold(s):
    """Bỏ dấu để so sánh — kể cả `Đ`, thứ NFD không đụng tới."""
    s = unicodedata.normalize('NFD', (s or '').upper())
    return re.sub(r'[̀-ͯ]', '', s).replace('Đ', 'D')


BULLET = re.compile(r'^\s*[•·▪◦*+\-–—]\s')


def _balanced(t):
    """Ngoặc mở mà không đóng ⇒ tên bị CẮT giữa chừng.

    «ĐẤU TRANH GIÀNH ĐỘC LẬP DÂN TỘC (TỪ ĐẦU» là một nửa tên, và một nửa tên
    trên giá sách còn tệ hơn không có tên: trẻ tưởng đó là cả tên.
    """
    return t.count('(') == t.count(')') and t.count('«') == t.count('»')


def is_candidate(text):
    """Chuỗi này có thể là TÊN BÀI không? Loại thẳng mọi thứ đã biết là không."""
    t = (text or '').strip()
    if not (MIN_LEN <= len(t) <= MAX_LEN):
        return False
    if CAPTION.match(t):
        return False
    # Gạch đầu dòng ⇒ một mục trong danh sách (mục tiêu, yêu cầu), không phải tên.
    if BULLET.match(t):
        return False
    if not _balanced(t):
        return False
    f = fold(t).strip()
    if TOPIC.search(f):
        return False
    if f.rstrip('.:') in SECTION_WORDS:
        return False
    # Câu văn kết bằng dấu câu — thân bài, không phải tên.
    if t[-1] in '.,;?!':
        return False
    # Phải có chữ cái, không phải chuỗi số/ký hiệu.
    return any(c.isalpha() for c in t)


def _in_body(line):
    y = line.get('y') or 0
    return MARGIN_TOP <= y <= MARGIN_BOTTOM


def has_lesson_marker(lines, lesson_no):
    """Trang có «Bài N» đúng số này không? PHÂN LOẠI, không đặt tên."""
    for l in lines:
        t = (l.get('text') or '').strip()
        m = NUM_ONLY.match(t) or INLINE.match(t)
        if m and int(m.group(1)) == lesson_no and _in_body(l):
            return True
    return False





def classify_page(lines, lesson_no):
    """Họ tín hiệu của trang này — để census ĐẾM, không để sinh tên.

    `no_lesson_unit` là phát hiện đáng giá nhất: 133 bài nằm trong sách mà đơn
    vị tổ chức là CHỦ ĐỀ/TUẦN chứ không phải «bài», nên «Bài N» trong mục lục là
    một suy diễn của bộ đọc mục lục, không phải thứ in trong sách.
    """
    body = [(l, (l.get('text') or '').strip()) for l in lines
            if (l.get('text') or '').strip() and _in_body(l)]
    if has_lesson_marker(lines, lesson_no):
        for l, t in body:
            m = INLINE.match(t)
            if m and int(m.group(1)) == lesson_no:
                return 'inline_title'
        return 'marker_only'
    head = ' '.join(t for _, t in sorted(body, key=lambda z: z[0]['y'])[:6])
    if TOPIC.search(fold(head)):
        return 'no_lesson_unit'
    return 'no_marker"'.rstrip('"')


def has_continuation(body, head, gap=2.2, xtol=0.06):
    """Có dòng NỐI TIẾP ngay dưới — cùng cột, cùng cỡ chữ, không phải gạch đầu
    dòng hay chú thích?

    Có ⇒ cái tên trải nhiều dòng. Bằng chứng có sẵn không dựng lại đúng thứ tự
    được (đã thử và ghép sai), nên bỏ chứ không đoán.
    """
    h = head.get('h') or 0.02
    for o, t in body:
        dy = o['y'] - head['y']
        if not (0 < dy <= gap * h):
            continue
        if abs(o['x'] - head['x']) > xtol:
            continue
        if abs((o.get('h') or 0) - h) > h * 0.45:
            continue
        if BULLET.match(t) or CAPTION.match(t) or not is_candidate(t):
            continue
        return True
    return False
