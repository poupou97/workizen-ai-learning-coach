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


def crop_jpeg(pdf_path, page_pdf, bbox, target_w=TARGET_W, quality=JPEG_Q):
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
        x, y, w, h = bbox
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


def lesson_figures(pdf_path, book, page_range, lines_by_page):
    """Hình NỘI DUNG của một bài, kèm chú thích và vị trí để chèn đúng chỗ."""
    out = []
    for pp in page_range:
        lines = lines_by_page.get(pp) or []
        for k, r in enumerate(page_ink_regions(pdf_path, pp, lines)):
            if classify(r) != 'content':
                continue
            out.append(dict(id=f'{book}:p{pp:03d}:img{k:02d}', book=book, page=pp,
                            bbox=r['bbox'], area=r['area'],
                            caption=caption_for(r['bbox'], lines)))
    return out
