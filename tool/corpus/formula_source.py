#!/usr/bin/env python3
"""WAL-239 — `FormulaSourceBlock`: công thức tới với trẻ bằng ẢNH TRANG IN.

Founder Gate 2026-09-09 duyệt phương án **B**, dự phòng **D**:

    VÙNG CÔNG THỨC NGUỒN → khối `FormulaSourceBlock` có kiểu riêng
    không dựng được vùng an toàn → GIỮ LẠI chuỗi OCR không an toàn

⛔ KHÔNG chọn C. Đặt bản in đúng cạnh chuỗi OCR sai thì trẻ vẫn đọc bản sai.

── VÌ SAO PHẢI LÀM ─────────────────────────────────────────────────────────

Đo trên 53 ca soi mắt so với bản in (mẫu đóng băng, 35 sách): **88,7% HẠI**,
Toán 23/23. Và loại hại nặng nhất không phải chữ vỡ — chữ vỡ thì trẻ biết là
hỏng. Nặng nhất là MỆNH ĐỀ SAI ĐỌC TRÔI CHẢY dưới danh nghĩa SGK:

    «x²/9 + y²/5 = 1»          → trẻ đọc «5 = 1.»
    «AD/AB = AE/AC = 1/2»      → «AE = AC»
    «1/R = 1/R₁ + 1/R₂»        → «1 = 1, + 1,»
    «1,6·10⁻¹⁹»                → «1,6.10-17»
    «Li⁺»                      → «Lit»

── ĐỘ HẠT: KHỐI, KHÔNG PHẢI HỘP CÔNG THỨC ─────────────────────────────────

Đo rồi mới biết: vùng `formula` của Docling KHÔNG phải hộp công thức chặt.
Trung vị chiếm 29,9% diện tích trang, cao 55% chiều cao trang, 0% vùng nhỏ
hơn 2% trang. Chúng là KHỐI NỘI DUNG TOÁN — chứa nhiều công thức lẫn chữ của
chính bài tập («Giải», «a)», «Luyện tập 3»).

`mathfix` không thay được: nó dò GẠCH PHÂN SỐ, và thưa (1 vùng trên một trang
đầy công thức). Không có bộ dò nào cho vùng công thức chặt ở corpus này.

Nên luật áp ở ĐỘ HẠT KHỐI, và điều đó CHỈ an toàn nhờ một điều: ảnh cắt hiện
ra ĐÚNG những gì bị bỏ. Đây chính là doctrine đã dùng cho bảng (#167) — khối
chữ nằm gọn trong vùng đáng tin thì ảnh đã hiện nó rồi, bỏ đi không mất gì.

Quy mô đã đo: 11.636 khối chữ (4,4% corpus · 1,4% ký tự). Toán 15,6% khối.
907 khối bị bỏ bị `block_kind` gọi là «heading» — soi ra là nhãn bài tập
«a)» «b)» «c)», KHÔNG phải tiêu đề mục của sách.

⛔ KHÔNG BAO GIỜ dựng lại nội dung công thức. Không LaTeX, không LLM, không
sửa thầm. Thiếu công thức mà nói thật còn hơn một công thức sai mà tự tin.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

#: Cùng ngưỡng đã chứng minh ở `table_ownership`: đoạn văn nằm gọn ngần này
#: DIỆN TÍCH CỦA CHÍNH NÓ trong vùng thì vùng ấy sở hữu nó.
INSIDE = 0.80

#: Vùng chiếm gần trọn trang thì không phải một khối nội dung — cắt nó ra là
#: biến cả trang thành ảnh. Đóng chặt: không dựng khối, chỉ giữ lại chữ.
MAX_AREA = 0.85

#: Số hiệu công thức sách IN, «(3.2)», «(19.5)» — danh tính ỔN ĐỊNH khi có.
#: Không có thì để trống; KHÔNG tự đánh số.
EQ_NUM = re.compile(r'\((\d{1,2}\.\d{1,2})\)')


def _wh(box):
    """GÓC `[x0,y0,x1,y1]` → `[x, y, w, h]`.

    ⚠ HAI QUY ƯỚC HỘP CÙNG TỒN TẠI TRONG KHO NÀY, và tôi đã đọc nhầm một lần:
    `proposals-w*.jsonl` (tầng bố cục) dùng **GÓC**; `trusted.jsonl` (sau cổng
    tin cậy) dùng **`[x, y, w, h]`**; `page_paragraphs` dùng **GÓC**.

    Đọc nhầm góc thành x,y,w,h làm mọi phép đo vùng công thức sai theo: diện
    tích trung vị ra 29,9% trang (nghe đã vô lý cho một công thức) và 69,5%
    hộp «tràn ra ngoài trang» tới x+w = 1,79. Đổi đúng quy ước: 0 hộp bất
    thường, trung vị **0,91%** trang, 97,4% dưới 5% — đúng dáng một công thức
    in. Cùng họ lỗi với `aspect()` (pixel vs chuẩn hoá) đã dính trước đây.
    """
    return [box[0], box[1], box[2] - box[0], box[3] - box[1]]


def _inside_frac(inner, outer):
    """Phần diện tích của `inner` nằm trong `outer` — mẫu số là CHÍNH `inner`.

    Lấy mẫu số là `outer` thì một đoạn ngắn luôn ra tỉ lệ bé và không bao giờ
    được coi là thuộc về vùng — đúng lỗi đã phải sửa ở `table_ownership`.
    """
    ix = min(inner[0] + inner[2], outer[0] + outer[2]) - max(inner[0], outer[0])
    iy = min(inner[1] + inner[3], outer[1] + outer[3]) - max(inner[1], outer[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    return (ix * iy) / max(inner[2] * inner[3], 1e-9)


def safe_region(box):
    """Vùng có dựng được một ảnh trung thực không. ĐÓNG CHẶT.

    Không an toàn ⇒ không dựng khối. Chữ mà nó sở hữu vẫn bị giữ lại (D):
    một công thức thiếu còn hơn một công thức sai.
    """
    if not box or len(box) != 4:
        return False
    x, y, w, h = box
    if w <= 0 or h <= 0:
        return False
    if x < 0 or y < 0 or x + w > 1.0001 or y + h > 1.0001:
        return False
    return w * h <= MAX_AREA


def owned_by_formula(para, regions, inside=INSIDE):
    """Đoạn văn này có nằm gọn trong một vùng công thức nào không.

    `para` phải mang hộp bao (`page_paragraphs` có `box`). Không có hộp ⇒
    KHÔNG có bằng chứng sở hữu ⇒ GIỮ chữ. Không đoán.
    """
    b = para.get('box')
    if not b or not regions:
        return None
    pb = _wh(b)
    for r in regions:
        if _inside_frac(pb, r) >= inside:
            return r
    return None


def identity(texts):
    """Số hiệu công thức IN TRONG SÁCH, nếu có. «(3.2)» → `'3.2'`.

    Chỉ nhận khi CHỈ CÓ MỘT số hiệu trong vùng: hai số hiệu nghĩa là vùng ôm
    hai công thức được đánh số khác nhau, và gán một cái là gán sai.
    """
    found = {m.group(1) for t in texts for m in EQ_NUM.finditer(t or '')}
    return found.pop() if len(found) == 1 else None


TOUCH = 0.20              # chữ phủ chừng này DIỆN TÍCH VÙNG thì trong vùng có chữ


def _covers_region(inner, region):
    """Phần diện tích VÙNG bị `inner` phủ — mẫu số là VÙNG, không phải `inner`.

    ⚠ ĐÂY LÀ MỘT MẪU SỐ KHÁC VỚI `_inside_frac`, VÀ CHỌN NHẦM THÌ CHỐT THỦNG.
    `_inside_frac` hỏi «đoạn này có thuộc về vùng không» ⇒ mẫu số là ĐOẠN.
    Ở đây hỏi «trong vùng có chữ không» ⇒ mẫu số là VÙNG.

    Bản đầu tôi dùng nhầm `_inside_frac`: Tin học 11 tr.119, đoạn «T(n) = n2 +
    3n - 3 Xác định độ phức tạp O-lớn của thuật toán…» dài nên chỉ 1,5% diện
    tích CỦA NÓ nằm trong vùng công thức bé — dưới ngưỡng, chốt không nổ, khối
    được dựng và trẻ thấy ẢNH ĐÚNG CẠNH CHỮ HỎNG. Đúng phương án C bị cấm.
    Cùng đoạn ấy phủ ~80% DIỆN TÍCH VÙNG.
    """
    ix = min(inner[0] + inner[2], region[0] + region[2]) - max(inner[0], region[0])
    iy = min(inner[1] + inner[3], region[1] + region[3]) - max(inner[1], region[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    return (ix * iy) / max(region[2] * region[3], 1e-9)


def _touched(region, paragraphs):
    """Trong vùng có chữ OCR mà ta KHÔNG bỏ được không."""
    return any(_covers_region(_wh(p['box']), region) > TOUCH
               for p in paragraphs if p.get('box'))


def blocks(book, page, regions, paragraphs):
    """`(khối FormulaSourceBlock, id đoạn bị vùng sở hữu)` cho MỘT trang.

    Khối mang xuất xứ đầy đủ: sách · trang · vùng nguồn · neo thứ tự đọc ·
    trạng thái tin cậy · danh tính khi sách có in số hiệu.

    ⭐ `FIGURE != TABLE != FORMULA != TEXT`. Khối này KHÔNG phải một hình
    thường: nó nói «đây là công thức của sách, hiện đúng như in», và bước sau
    KHÔNG được suy luận ký hiệu từ nó như thể đã xác minh.
    """
    out, owned = [], []
    for k, r in enumerate(regions):
        mine = [p for p in paragraphs if owned_by_formula(p, [r])]
        if not safe_region(r):
            # ĐÓNG CHẶT: không dựng khối. Chữ vẫn bị giữ lại — xem docstring.
            owned += [id(p) for p in mine]
            continue
        if not mine and _touched(r, paragraphs):
            # ⛔ TRÁNH RƠI VÀO C. Vùng có chữ CHẠM vào nhưng không đoạn nào nằm
            # gọn ⇒ không chứng minh được đoạn nào là chữ của công thức ⇒ không
            # bỏ được cái nào. Hiện ảnh lúc này là đặt bản in đúng CẠNH chuỗi
            # OCR sai — đúng phương án C mà Founder cấm. Nên không dựng khối,
            # ghi thành NỢ ĐO ĐƯỢC. Đo toàn corpus: 1.388/4.885 = 28,4%.
            continue
        anchor = min((p['seq'] for p in mine), default=None)
        out.append(dict(t='formula', id=f'{book}:p{page:03d}:fml{k:02d}',
                        page=page, bbox=list(r), y=round(r[1], 4), seq=anchor,
                        src=dict(book=book, page=page, region=[round(v, 4) for v in r]),
                        trust='TRUSTED', ident=identity(p['text'] for p in mine),
                        owned=len(mine)))
        owned += [id(p) for p in mine]
    return out, set(owned)


def regions_index(path=None):
    """`{(sách, trang): [vùng, ...]}` — vùng `formula` của tầng bố cục.

    Thiếu tệp ⇒ rỗng ⇒ đường dựng chạy y như cũ. Bước tri giác hỏng KHÔNG
    được làm hỏng dữ liệu đang tốt.
    """
    import glob
    out = {}
    pat = path or os.path.join(ROOT, 'poc-out', 'docling', 'proposals-w*.jsonl')
    for p in sorted(glob.glob(pat)):
        with open(p, encoding='utf-8') as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                box = [_wh(it['box']) for it in (r.get('items') or [])
                       if it.get('label') == 'formula']
                if box:
                    out.setdefault((r['book'], r['page']), []).extend(box)
    return out
