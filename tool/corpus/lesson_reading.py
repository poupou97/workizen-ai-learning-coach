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
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import code_source  # noqa: E402  (chỉ dùng khi có `code_regions`; chỉ mục nạp lười)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')

# Dải trên/dưới trang nơi số trang và tiêu đề chạy nằm.
FURNITURE_TOP = 0.055
FURNITURE_BOTTOM = 0.945
LONG_LINE = 0.25      # dòng «dài» = dòng văn thật, không phải ô bảng

#: Tắt hẳn phần giữ dòng cho mã nguồn — để lượt dựng quay về đúng đường cũ mà
#: không phải revert mã. Đặt `WAL_CODE_OFF=1`.
CODE_OFF = os.environ.get('WAL_CODE_OFF') == '1'
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

    ⚠ KHÔNG CÒN LÀ CỔNG. Trước đây trang hai cột bị chặn thẳng vì ghép theo y
    sẽ đan hai cột. Nay `read_order` đọc theo KHỐI nên hai cột được đọc hết cột
    trái rồi tới cột phải — chặn nữa là bỏ đi 802 bài mà không được gì. Giữ hàm
    để census còn đo được bố cục, không dùng để từ chối nội dung.

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


BLOCK_XGAP = 0.04     # chồng x tối thiểu để hai dòng thuộc cùng khối
BLOCK_YGAP = 1.8      # khoảng cách dọc tối đa, tính theo chiều cao dòng
BAND_TOL = 0.01       # sai số khi gộp khối vào cùng một dải ngang


def blocks(lines):
    """Gom dòng thành KHỐI bố cục: dòng mới phải chồng x với MỌI dòng đã có
    trong khối, VÀ liền nhau theo y.

    ⭐⭐ CHỒNG VỚI CẢ KHỐI, KHÔNG PHẢI VỚI DÒNG CUỐI.

    Bản trước chỉ so dòng mới với DÒNG CUỐI, nên khối TRÔI NGANG bắc cầu:
    A(x .09–.50) → B(x .46–.90) → C(x .86–.95) nối được hết dù A và C không hề
    chồng nhau. Đo trên máy: Vật lí 11 trang 21 sinh MỘT khối 23 dòng trải
    `x=0.092..0.900`, nuốt cả cột trái lẫn dải hình. Ranh giới khối là thứ dùng
    để biết CHỖ NÀO LÀ HÌNH và MẢNH KÝ HIỆU THUỘC VỀ ĐÂU — khối trôi thì cả
    hai đều sai.

    Điều kiện ở đây là một BẤT BIẾN CỦA CỘT CHỮ, không phải một con số được
    chỉnh: trong một cột, không tồn tại hai dòng rời hẳn nhau. Giữ giao của mọi
    dòng (`core`) rồi đòi dòng mới chồng giao ấy là cách phát biểu đúng điều đó
    — không có hằng số nào để vặn.

    Chấm trên 12 họ bố cục (một cột · hai cột · công thức · đồ thị · bảng · bài
    tập · âm nhạc · bản đồ · khung phụ · Tiếng Việt · Toán), nhãn đọc từ hình
    học trang + chính tả:

        luật            khối   CẶP DÒNG RỜI   ĐOẠN BỊ CẮT
        dòng-cuối (cũ)   528        121             8
        dải tích luỹ     511         49             1
        thẳng mép        665         56            11
        mép đầu          600         32            11
        trung vị         635         34            10
        GIAO (luật này)  677          0            20

    Đổi 121 khối có dòng rời lấy thêm 12 chỗ đoạn bị cắt: chỗ ghép SAI làm hỏng
    CÂU (đúng họ lỗi #141 — «…tác động KHOẢNG TÁM NGHÌN NĂM xấu của thiên
    nhiên…»), còn chỗ cắt chỉ làm một đoạn hiện thành hai. Sai nội dung nặng
    hơn xấu trình bày.
    """
    ls = sorted([l for l in lines if (l.get('text') or '').strip()],
                key=lambda l: (l['y'], l['x']))
    out, core = [], []
    for l in ls:
        h = l.get('h') or 0.02
        x0, x1 = l['x'], l['x'] + l.get('w', 0)
        for b, c in zip(out, core):
            last = b[-1]
            if not (0 <= l['y'] - last['y'] <= BLOCK_YGAP * max(h, last.get('h') or h)):
                continue
            # Chồng GIAO của khối ⇒ chồng TỪNG dòng của khối (giao nằm trong mọi dòng).
            if min(x1, c[1]) - max(x0, c[0]) > 0:
                b.append(l)
                c[0], c[1] = max(c[0], x0), min(c[1], x1)
                break
        else:
            out.append([l])
            core.append([x0, x1])
    return out


def read_order(lines):
    """⭐ A5 — PAGE → LAYOUT BLOCKS → REGIONS → READING ORDER.

    Ghép dòng theo y là đúng cho trang một luồng, nhưng SAI ngay khi trang có
    khung phụ hay nhãn hình: máy thật (Nokia, Công nghệ 6 Bài 1) cho ra câu
    «…bảo vệ con người trước những tác động KHOẢNG TÁM NGHÌN NĂM xấu của thiên
    nhiên…» — một câu ghép từ thân bài và một khung niên biểu bên phải. Bài 17
    cũng dính nhẹ: nhãn hình «Nước muối», «Đèn cồn» chen vào giữa câu.

    Ngưỡng bề rộng dòng KHÔNG cứu được chuyện này: khung phụ ấy rộng 0,22 —
    hẹp hơn ngưỡng «dòng dài», nên mọi luật dựa trên bề rộng đều bỏ lọt.

    Ở đây: gom khối, gộp khối chồng nhau theo y thành một DẢI, rồi đọc từng dải
    trái→phải. Khung phụ và nhãn hình ra khỏi giữa câu vì chúng là khối riêng.
    """
    bs = blocks(lines)
    bands = []
    for b in sorted(bs, key=lambda b: (min(l['y'] for l in b), min(l['x'] for l in b))):
        y0 = min(l['y'] for l in b)
        y1 = max(l['y'] for l in b)
        for band in bands:
            if not (y1 < band['y0'] - BAND_TOL or y0 > band['y1'] + BAND_TOL):
                band['blocks'].append(b)
                band['y0'] = min(band['y0'], y0)
                band['y1'] = max(band['y1'], y1)
                break
        else:
            bands.append(dict(y0=y0, y1=y1, blocks=[b]))
    seq = []
    for band in sorted(bands, key=lambda z: z['y0']):
        for b in sorted(band['blocks'], key=lambda b: min(l['x'] for l in b)):
            seq += b
    return seq


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


def page_paragraphs(lines, drop=frozenset(), code_regions=()):
    """Từng KHỐI chữ của trang, kèm y — để hình chèn ĐÚNG CHỖ nó thuộc về.

    Gom tất cả xuống cuối bài thì trẻ đọc xong mới thấy hình, và không biết hình
    nào nói về đoạn nào. Giữ y của khối là đủ để đặt hình xen giữa.

    ⚠ PHẢI theo THỨ TỰ DẢI, không phải theo y thuần. Máy thật bắt được: sắp khối
    theo y làm khung phụ chen lại vào giữa câu — đúng lỗi #141 đã sửa cho chuỗi
    chữ phẳng, tái xuất ở dòng nội dung vì đây là một đường đọc thứ hai.
    """
    order = {id(l): i for i, l in enumerate(read_order(lines))}
    out = []
    rest = lines
    if code_regions:
        # ⭐ MÃ NGUỒN TÁCH RA TRƯỚC KHI GOM KHỐI, và tách theo DÒNG.
        #
        # `blocks()` gom theo cột; thụt lề của mã tạo bước nhảy x nên một
        # chương trình bị XÉ ra nhiều khối (60,2% số vùng, tới 14 khối) rồi
        # mỗi mảnh bị HÀN vào văn xuôi quanh nó (88,0%). Lọc theo ĐOẠN không
        # cứu được: đoạn nào cũng chỉ phủ 0,9%–39,7% vào vùng mã.
        #
        # Đây KHÔNG phải giữ xuống dòng của OCR nói chung — chỉ đúng những
        # dòng nằm trong một vùng `code` CÓ dấu vết chương trình in. Văn xuôi
        # không đổi một chữ.
        rest, groups = code_source.owned_lines(lines, code_regions)
        for box, got in groups:
            if not got:
                continue
            seq = min(order.get(id(l), 1 << 30) for l in got)
            q = code_source.code_paragraph(got, box, seq, drop)
            if q is None:
                # Không dựng được thì TRẢ CHỮ VỀ đường cũ, không nuốt mất.
                rest = rest + got
            else:
                out.append(q)
    for b in blocks(rest):
        keep = [l for l in b
                if not is_furniture(l) and (l.get('text') or '').strip()
                and (l.get('text') or '').strip() not in drop]
        if not keep:
            continue
        # ⭐ MANG THEO HỘP BAO, không chỉ `y`. Có hộp thì bước sau mới trả lời
        # được câu «dòng chữ này có nằm TRONG một vùng bảng đáng tin không» —
        # tức là ai SỞ HỮU nó. Không có bằng chứng sở hữu thì không được xoá
        # chữ của sách.
        out.append(dict(y=round(min(l['y'] for l in b), 4),
                        seq=min(order.get(id(l), 1 << 30) for l in keep),
                        box=[round(min(l['x'] for l in keep), 4),
                             round(min(l['y'] for l in keep), 4),
                             round(max(l['x'] + (l.get('w') or 0) for l in keep), 4),
                             round(max(l['y'] + (l.get('h') or 0) for l in keep), 4)],
                        text=' '.join((l.get('text') or '').strip() for l in keep).strip()))
    return sorted(out, key=lambda p: p['seq'])


def page_text(lines, drop=frozenset()):
    return ' '.join((l.get('text') or '').strip()
                    for l in read_order(lines)
                    if not is_furniture(l) and (l.get('text') or '').strip() not in drop).strip()


# ⚠ CỬA SỔ ĐẦU BÀI — ĐO RỒI MỚI ĐỔI, VÀ CỔNG NÀY YẾU HƠN TÊN CỦA NÓ.
#
# Trước đây chỉ soi 400 ký tự đầu. Khi tầng phân khối được sửa (không còn trôi
# ngang), thứ tự đọc mịn hơn nên chữ của tên bài rơi ra NGOÀI 400 ký tự ấy ở 4
# bài — dù 100% từ của tên vẫn nằm TRÊN CHÍNH TRANG đó (Sinh học 11 Bài 11
# 10/10 từ · Hoá học 10 Bài 9 8/8 · Địa lí 12 Bài 27 9/9 · Công nghệ 9 Bài 3
# 11/11). Giữ 400 là bỏ 4 bài vì một chi tiết cài đặt, không phải vì thiếu
# bằng chứng.
#
# Đo trên 1.446 bài lớp 9–12, cửa sổ ⇒ (khớp đúng tên mình · trang khớp tên
# một bài KHÁC cùng sách):
#
#     400 ký tự  98,5%  ·  92,3%
#     600        99,2%  ·  96,6%
#     800        99,5%  ·  97,6%
#     cả trang   99,9%  ·  98,7%
#
# ⭐ Con số thứ hai mới là điều đáng nói: ngay ở 400 ký tự, 92,3% trang đã khớp
# tên của một bài khác. Cổng này GẦN NHƯ KHÔNG phân biệt được gì — nới nó ra
# không đánh đổi mất sức phân biệt, vì sức phân biệt vốn không có. Việc thật
# giữ cho «đúng bài» là `unit_locator` (khớp duy nhất) và luật chương.
#
# Nên soi CẢ TRANG mở đầu: câu hỏi là «trang này có mở bài ấy không», và đơn vị
# của câu hỏi ấy là TRANG.
HEAD_CHARS = None     # None = soi cả trang mở đầu
START_MATCH = 0.5     # tỉ lệ từ của tên bài phải có mặt


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
    h = _norm(head) if HEAD_CHARS is None else _norm(head)[:HEAD_CHARS]
    toks = [w for w in t.split() if len(w) > 2]
    if not toks:                      # tên rất ngắn («Ôn tập») — khớp cả cụm
        return t in h
    return sum(1 for w in toks if w in h) / len(toks) >= START_MATCH


UNIT_START_SLACK = 2      # nới ra ngoài dải attach tối đa ngần này trang


def find_unit_start(book, page_pdf_start, page_pdf_end, title,
                    slack=UNIT_START_SLACK):
    """Trang mà tên đơn vị xuất hiện DUY NHẤT — hoặc `None`.

    Census 270 ca hỏng dải trang cho thấy nguyên nhân chính KHÔNG phải offset
    trang in→PDF (offset thậm chí không ổn định trong cùng một cuốn: 20/44 sách
    có nhiều giá trị khác nhau). Hai họ lớn nhất là:

      · mục lục ghi PHẦN CON của bài, không phải bài (51 ca). Tiếng Việt: mục
        «Luyện từ và câu: Liên kết câu…» là một mục BÊN TRONG «Bài 9», nên dải
        của bài mở ở trang khác với chỗ mục ấy bắt đầu;
      · dải lệch đúng một trang (40 ca).

    Cả hai giải bằng CÙNG một luật: tìm trang mà tên ấy xuất hiện, trước hết
    TRONG dải, rồi nới ±slack. Nhận khi và chỉ khi ĐÚNG MỘT trang khớp.

    ⭐ DUY NHẤT LÀ ĐIỀU KIỆN, KHÔNG PHẢI SỞ THÍCH. Nhiều trang khớp nghĩa là ta
    không biết trang nào là chỗ bắt đầu; chọn trang đầu tiên là đoán, và đoán
    sai thì trẻ đọc nhầm chỗ. Không khớp trang nào cũng vậy. Cả hai ⇒ giữ lại.
    """
    if not title or page_pdf_start is None:
        return None
    inside = [p for p in range(page_pdf_start, (page_pdf_end or page_pdf_start) + 1)
              if _page_opens_unit(book, p, title)]
    if len(inside) == 1:
        return inside[0]
    if inside:
        return None            # nhiều chỗ khớp trong dải ⇒ không quyết được
    near = [p for p in range(page_pdf_start - slack, page_pdf_start + slack + 1)
            if p >= 1 and _page_opens_unit(book, p, title)]
    return near[0] if len(near) == 1 else None


def _page_opens_unit(book, page_pdf, title):
    lines = page_lines(book, page_pdf)
    if lines is None:
        return False
    head = ' '.join((l.get('text') or '').strip()
                    for l in sorted([x for x in lines if (x.get('text') or '').strip()],
                                    key=lambda z: z['y'])[:10])
    return starts_at_lesson(head, title) is True


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
        raw.append((pp, lines))
    if missing:
        return None, 'OCR_MISSING'
    drop = running_headers([l for _, l in raw])
    pages = []
    cregs = {} if CODE_OFF else code_source.regions_index()
    for pp, lines in raw:
        txt = page_text(lines, drop)
        if txt:
            pages.append(dict(pagePdf=pp, text=txt,
                              paragraphs=page_paragraphs(
                                  lines, drop, cregs.get((book, pp)) or ())))
    if not pages:
        return None, 'CONTENT_THIN'
    if title is not None and starts_at_lesson(pages[0]['text'], title) is False:
        # Nội dung không mở đúng bài — thử tìm trang mở THẬT của đơn vị này.
        start = find_unit_start(book, page_pdf_start, page_pdf_end, title)
        if start is None or start == page_pdf_start:
            # `start == page_pdf_start` nghĩa là đầu trang khớp nhưng dòng đọc
            # đầy đủ thì không — đừng lặp lại chính phép vừa trượt.
            return None, 'LESSON_START_UNCONFIRMED'
        # Kiểm LẠI trên dòng đọc đầy đủ, không tin phép dò đầu trang là đủ.
        return lesson_reading(book, start, page_pdf_end,
                              printed_start=printed_start, title=title)
    return dict(book=book, pagePdfStart=page_pdf_start, pagePdfEnd=page_pdf_end,
                pageStart=printed_start, pages=pages,
                extraction='ocr-layout-blocks-v1'), None
