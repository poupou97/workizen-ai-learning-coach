#!/usr/bin/env python3
"""HÌNH TRONG BÀI — dò, phân loại, cắt từ chính trang sách.

Founder dogfood #140 và thấy: bài mở được nhưng CHỈ CÓ CHỮ. Đo lại đường hình,
mất ở tầng ĐẦU TIÊN — DÒ:

    sách canonical                       238
    sách có dữ liệu hình (Docling/SDM)    12   ⇒ 226 sách không có gì để hiển thị
    figure trong pack                      0

Docling là pipeline ML nặng, chạy cho 12 sách. Ở đây dùng tín hiệu TRỰC TIẾP mà
mọi sách đều có: trang SGK là ẢNH QUÉT, nên «có mực mà không phải chữ OCR» chính
là hình/sơ đồ/bảng. Không suy luận, không mô hình.

Đối chiếu với 3.864 figure của Docling trên 12 sách ấy: recall 86%, precision 72%
(vùng «thừa» phần lớn là hình Docling bỏ sót hoặc trang trí, không phải hình sai).

⚠ KHÔNG BỊA. Chỉ CẮT từ đúng trang của đúng bài:
  · không sinh lại hình bằng AI,
  · không đặt chú thích — chú thích chỉ lấy khi sách có dòng «Hình N…»/«Bảng N…»
    nằm ngay dưới hình,
  · vùng không chắc ⇒ BỎ, không gắn bừa vào bài để tăng coverage.
"""
import io
import os
import re

CONTENT_MIN_AREA = 0.05    # < 5% trang: icon, huy hiệu, nét trang trí
DECOR_MAX_AREA = 0.03
FRAME_MIN_FILL = 0.25      # viền hộp: rất rộng/cao mà cực thưa
TEXT_BOX_COVERAGE = 0.10   # chữ phủ hơn ngần này ⇒ hộp chữ có nền, không phải hình
INK_THRESHOLD = 235
TEXT_PAD = 0.006
TARGET_W = 640             # bề rộng hiển thị thật trên điện thoại, không dpi cố định
CROP_PAD = 0.012           # nới biên: nhãn hình nằm NGOÀI khối mực, cắt sát là cụt chữ
JPEG_Q = 72

CAPTION_RE = re.compile(r'^\s*(hình|bảng|sơ\s*đồ|biểu\s*đồ)\s*[\d IVX]', re.IGNORECASE)


def page_ink_regions(pdf_path, page_pdf, lines, dpi=60):
    """Vùng CÓ MỰC trên trang mà không nằm dưới một dòng chữ OCR nào."""
    import numpy as np
    import cv2
    import fitz
    doc = fitz.open(pdf_path)
    try:
        if not (1 <= page_pdf <= doc.page_count):
            return []
        pg = doc[page_pdf - 1]
        pm = pg.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
        img = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    finally:
        doc.close()
    H, W = img.shape
    ink = (img < INK_THRESHOLD).astype('uint8')
    for l in lines:
        if not (l.get('text') or '').strip():
            continue
        x0 = int(max(0, l['x'] - TEXT_PAD) * W)
        y0 = int(max(0, l['y'] - TEXT_PAD) * H)
        x1 = int(min(1, l['x'] + l.get('w', 0) + TEXT_PAD) * W)
        y1 = int(min(1, l['y'] + l.get('h', 0) + TEXT_PAD) * H)
        ink[y0:y1, x0:x1] = 0
    # Khép NHẸ: nối nét đứt trong một hình, không đủ để dính hai hình cạnh nhau.
    ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, np.ones((3, 3), 'uint8'))
    n, _, stats, _ = cv2.connectedComponentsWithStats(ink, 8)
    out = []
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        bw, bh = w / W, h / H
        fill = a / max(w * h, 1)
        if fill < 0.10:
            continue                                  # nhiễu quét
        if fill < FRAME_MIN_FILL and (bw > 0.6 or bh > 0.6):
            continue                                  # viền hộp / đường kẻ
        bbox = [round(x / W, 4), round(y / H, 4), round(bw, 4), round(bh, 4)]
        # ⭐ HỘP CHỮ CÓ NỀN MÀU không phải hình. Nền màu vẫn là «mực» nên lọt qua
        # phép dò; nhìn tận mắt bảng liên hoàn Bài 17 thấy 3/7 vùng là hộp «Em có
        # thể», «Em có biết», hộp thí nghiệm — tức là CHỮ ĐÃ CÓ trong dòng đọc,
        # đưa thêm vào là bắt trẻ đọc lại cùng một đoạn dưới dạng ảnh.
        if text_coverage(bbox, lines) > TEXT_BOX_COVERAGE:
            continue
        out.append(dict(bbox=bbox, area=round(bw * bh, 5), fill=round(fill, 3)))
    return out


def _swallows(bbox, box, frac=0.5):
    """Hộp `bbox` nuốt ít nhất `frac` diện tích khối chữ `box` = (x0,y0,x1,y1)."""
    x, y, w, h = bbox
    ix = min(x + w, box[2]) - max(x, box[0])
    iy = min(y + h, box[3]) - max(y, box[1])
    if ix <= 0 or iy <= 0:
        return False
    return ix * iy >= frac * max((box[2] - box[0]) * (box[3] - box[1]), 1e-9)


def _line_crosses(l, bbox):
    """Dòng CẮT QUA vùng: tâm dọc của dòng nằm trong hộp và có chồng ngang.

    ⚠ Không hỏi «dòng có nằm gọn trong hộp không». Nhìn tận mắt một ca hỏng:
    vùng gom HẸP HƠN dòng văn, nên dòng thò ra hai bên và phép «nằm gọn» cho
    là không dính — trong khi ảnh cắt ra hiện đúng một lát cắt của câu chữ
    («Gọi (P) là mặt phẳng qua E» cụt cả hai đầu). Cắt qua là đủ để hỏng.
    """
    x, y, w, h = bbox
    lx0, lx1 = l['x'], l['x'] + (l.get('w') or 0)
    if min(lx1, x + w) - max(lx0, x) <= 0:
        return False
    cy = l['y'] + (l.get('h') or 0) / 2
    return y <= cy <= y + h


def caption_regions(regions, lines):
    """GOM VÙNG QUANH MỎ NEO CHÚ THÍCH — hình mà sách TỰ NÓI là có.

    Đo phễu dò trên 223 mỏ neo có chú thích số, 5 họ nguồn:

        họ                 n   ĐẠT  VỠ MẢNH  TRANG TRÍ  QUÁ NHỎ  KHÔNG THÀNH  KHÔNG THẤY
        đồ thị nét mảnh   71     5      24        16       18          5          3
        sơ đồ hoá học     36     1      14         3        8          5          5
        sinh học          41    21      17         2        1          0          0
        bản đồ/địa lí     34    11       9         1        1          3          9
        ảnh/minh hoạ      41    21      15         1        2          1          1
        TỔNG             223    59      79        23       30         14         18

    ⭐ VỠ MẢNH là họ lỗi LỚN NHẤT (35,4%): mực có, thành phần liên thông có, HỢP
    của chúng đủ lớn — chỉ thiếu bước GOM. Và lỗi phụ thuộc HỌ NGUỒN: ảnh và
    hình sinh học đạt ~51%, còn đồ thị nét mảnh 7%, sơ đồ hoá học 3%.

    ⇒ `classify()` KHÔNG sai: nó từ chối đúng những mảnh vụn. Hạ ngưỡng diện
    tích sẽ nhận mảnh vụn vào bài đọc. Thứ thiếu là TẦNG GOM VÙNG.

    Chú thích CHỨNG MINH hình tồn tại, KHÔNG cho biết biên của hình. Nên biên ở
    đây là HỢP CỦA MỰC THẬT tìm được trong dải, không phải cái dải.

    Chỉ gom khi CÓ chú thích — nơi nguồn đã khẳng định có hình. Không có chú
    thích thì giữ nguyên luật cũ, để không tự ý dựng hình từ mực vụn.
    """
    from figure_funnel import caption_anchors, neighborhood, in_band, unproven_text_boxes
    from lesson_reading import LONG_LINE
    anchors = caption_anchors(lines)
    unproven = unproven_text_boxes(lines, regions)
    prose = unproven
    out = []
    for a in anchors:
        band = neighborhood(a, anchors, prose=prose)
        xs = (max(0.0, a['x'] - 0.15), min(1.0, a['x'] + a['w'] + 0.15))
        near = [r for r in regions if in_band(r['bbox'], band, xs)]
        if not near:
            continue
        x0 = min(r['bbox'][0] for r in near)
        y0 = min(r['bbox'][1] for r in near)
        x1 = max(r['bbox'][0] + r['bbox'][2] for r in near)
        y1 = max(r['bbox'][1] + r['bbox'][3] for r in near)
        bbox = [round(x0, 4), round(y0, 4), round(x1 - x0, 4), round(y1 - y0, 4)]
        # Hợp mà phủ đầy chữ thì đó là một khối văn bản, không phải hình —
        # cùng luật đã dùng cho hộp chữ có nền.
        if text_coverage(bbox, lines) > TEXT_BOX_COVERAGE:
            continue
        # ⭐ HỢP KHÔNG ĐƯỢC TRÙM DÒNG VĂN THẬT.
        # Nhìn tận mắt một vùng bị đánh dấu: hợp trườn qua hình mascot, HAI DÒNG
        # thân bài («Gọi (P) là mặt phẳng qua E…»), rồi mới tới hình tứ diện thật
        # — đưa cho trẻ ảnh chụp đoạn chữ nó vừa đọc. Chặn bằng khối thân bài
        # không bắt được vì hai dòng ấy chưa đủ thành «khối».
        #
        # Dấu hiệu phân biệt có sẵn và đã được dùng chỗ khác: NHÃN TRONG HÌNH thì
        # ngắn, DÒNG VĂN thì dài. `LONG_LINE` là mốc ấy, không phải hằng số mới.
        if any((l.get('w') or 0) >= LONG_LINE and (l.get('text') or '').strip()
               and _line_crosses(l, bbox) for l in lines):
            continue
        # ⭐ PHƯƠNG ÁN D — HỢP KHÔNG ĐƯỢC NUỐT MỘT KHỐI CHỮ CHƯA CHỨNG MINH.
        #
        # Chặn dải chỉ giới hạn phía TRÊN; một khối chữ nằm GIỮA dải vẫn lọt vào
        # hộp hợp. Đo được: 31/120 vùng nuốt ≥ nửa một khối chữ chưa chứng minh
        # được là chữ của hình. Bộ kiểm gán tay (#160) nói rõ ta KHÔNG có cách
        # nào đáng tin để biết khối ấy thuộc hình hay thuộc bài đọc.
        #
        # «Thiếu hình» sửa được ở vòng sau; «hình nuốt mất câu» thì trẻ đọc phải
        # ngay. Không chứng minh được ⇒ GIỮ LẠI.
        if any(_swallows(bbox, t) for t in unproven):
            continue
        out.append(dict(bbox=bbox, area=round(bbox[2] * bbox[3], 5),
                        parts=len(near), anchor=a['num'], caption=a['text']))
    return out


def text_coverage(bbox, lines):
    """Phần diện tích vùng bị các dòng chữ OCR phủ."""
    x, y, w, h = bbox
    area = max(w * h, 1e-9)
    covered = 0.0
    for l in lines:
        if not (l.get('text') or '').strip():
            continue
        ix = min(x + w, l['x'] + l.get('w', 0)) - max(x, l['x'])
        iy = min(y + h, l['y'] + (l.get('h') or 0)) - max(y, l['y'])
        if ix > 0 and iy > 0:
            covered += ix * iy
    return covered / area


def classify(region):
    """A4 — chỉ ba lớp mà bằng chứng bố cục thật sự chống đỡ được.

    Không dựng classifier: diện tích là tín hiệu tất định duy nhất có sẵn cho
    mọi sách. Vùng ở giữa hai ngưỡng là KHÔNG CHẮC ⇒ bỏ (fail closed), vì gắn
    một huy hiệu trang trí vào bài đọc cũng là nói với trẻ rằng nó có nghĩa.
    """
    a = region['area']
    if a >= CONTENT_MIN_AREA:
        return 'content'
    if a <= DECOR_MAX_AREA:
        return 'decorative'
    return 'uncertain'


def caption_for(bbox, lines, max_gap=0.06):
    """Chú thích = dòng «Hình N…»/«Bảng N…» NGAY DƯỚI hình và chồng ngang với nó.

    Lấy chữ CÓ THẬT trong sách. Hình không có dòng như thế thì không có chú
    thích — máy không đặt tên cho hình của sách giáo khoa.
    """
    x, y, w, h = bbox
    best = None
    for l in lines:
        t = (l.get('text') or '').strip()
        if not t or not CAPTION_RE.match(t):
            continue
        gap = l['y'] - (y + h)
        if not (0 <= gap <= max_gap):
            continue
        ox = min(x + w, l['x'] + l.get('w', 0)) - max(x, l['x'])
        if ox <= 0:
            continue
        if best is None or gap < best[0]:
            best = (gap, t)
    return best[1] if best else None


def crop_jpeg(pdf_path, page_pdf, bbox, target_w=TARGET_W, quality=JPEG_Q,
              pad=None):
    """Cắt đúng vùng ấy từ trang, co về bề rộng hiển thị thật của điện thoại.

    Cắt theo dpi cố định thì hình lớn bị lấy mẫu thừa (đo được: 550 MB cho 12
    lớp); co theo bề rộng hiển thị giữ nét mà không gánh byte vô ích.
    """
    from PIL import Image
    import fitz
    doc = fitz.open(pdf_path)
    try:
        pg = doc[page_pdf - 1]
        r = pg.rect
        # Nới đều bốn phía: nhãn của sơ đồ («Mái nhà», «Tường nhà») là CHỮ nên đã
        # bị xoá khỏi mặt nạ mực, nằm ngoài khung dò. Cắt sát khung là cắt cụt
        # đúng phần nói cho trẻ biết đang nhìn cái gì — máy thật cho thấy điều đó.
        # ⚠ ĐỆM LÀ CỦA HÌNH, KHÔNG PHẢI CỦA MỌI THỨ. `CROP_PAD` sinh ra cho
        # vùng dò bằng MẶT NẠ MỰC, nơi nhãn sơ đồ là CHỮ nên nằm NGOÀI khung.
        # Vùng bố cục (công thức, bảng) đã ôm sẵn cả chữ của nó, nên nới thêm
        # chỉ kéo vào nửa dòng văn xuôi bên trên/dưới — đo bằng mắt trên 5 ca:
        # đệm 0,012 lần nào cũng dính chữ hàng xóm, đệm 0 thì sạch và không
        # cắt cụt công thức nào. Người gọi nói rõ `pad` thì theo người gọi.
        p = CROP_PAD if pad is None else pad
        x = max(0.0, bbox[0] - p)
        y = max(0.0, bbox[1] - p)
        w = min(1.0 - x, bbox[2] + 2 * p)
        h = min(1.0 - y, bbox[3] + 2 * p)
        clip = fitz.Rect(r.x0 + x * r.width, r.y0 + y * r.height,
                         r.x0 + (x + w) * r.width, r.y0 + (y + h) * r.height)
        zoom = max(target_w / max(clip.width, 1), 1.0)
        pm = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB,
                           alpha=False, clip=clip)
        im = Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
    finally:
        doc.close()
    if im.width > target_w:
        im = im.resize((target_w, max(1, round(im.height * target_w / im.width))),
                       Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=quality, optimize=True)
    return buf.getvalue(), im.size


def _iou(a, b):
    ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    iy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    inter = ix * iy
    return inter / (a[2] * a[3] + b[2] * b[3] - inter)


def lesson_figures(pdf_path, book, page_range, lines_by_page):
    """Hình NỘI DUNG của một bài, kèm chú thích và vị trí để chèn đúng chỗ.

    HAI ĐƯỜNG, CỘNG VÀO NHAU:

    1. vùng mực đủ lớn tự nó (luật cũ) — dùng được cả khi sách không in chú thích;
    2. vùng GOM QUANH CHÚ THÍCH (`caption_regions`) — chỗ sách tự nói là có hình.

    Đường (2) không thay đường (1): đo trên 223 mỏ neo có chú thích, phủ đi từ
    23,8% lên 65,0%, và 6 mỏ neo chỉ đường (1) bắt được. Bỏ đường cũ là mất số ấy.
    """
    out = []
    for pp in page_range:
        lines = lines_by_page.get(pp) or []
        regions = page_ink_regions(pdf_path, pp, lines)
        taken = []
        for k, r in enumerate(regions):
            if classify(r) != 'content':
                continue
            out.append(dict(id=f'{book}:p{pp:03d}:img{k:02d}', book=book, page=pp,
                            bbox=r['bbox'], area=r['area'],
                            caption=caption_for(r['bbox'], lines)))
            taken.append(r['bbox'])
        for j, c in enumerate(caption_regions(regions, lines)):
            # Đã có vùng gần trùng ⇒ không thêm bản thứ hai của cùng một hình.
            if any(_iou(c['bbox'], t) > 0.5 for t in taken):
                continue
            out.append(dict(id=f'{book}:p{pp:03d}:cap{j:02d}', book=book, page=pp,
                            bbox=c['bbox'], area=c['area'], caption=c['caption']))
            taken.append(c['bbox'])
    return out
