#!/usr/bin/env python3
"""B3 — CỘNG THÊM vùng đáng tin của Docling vào hình của D. KHÔNG THAY THẾ.

Luật di trú Founder chốt:

    NỘI DUNG D AN TOÀN  +  VÙNG DOCLING ĐÁNG TIN  =  NỘI DUNG CANONICAL MỚI

Không bao giờ: D → Docling thay trọn gói.

Chỉ vùng đạt CẢ HAI phép đo mới vào dòng đọc của trẻ:
`REGION_TRUST = TRUSTED` VÀ `IDENTITY_LINK = RESOLVED`. Vùng đáng tin mà danh
tính còn giữ lại thì nằm trong corpus canonical, KHÔNG hiện cho trẻ — mất nhãn
con làm ảnh hiện ra sai lệch.

Thiếu tệp `trusted.jsonl` thì hàm này trả về rỗng và đường dựng chạy y như cũ.
Đó là chủ ý: bước tri giác hỏng KHÔNG được làm hỏng dữ liệu đang tốt.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TRUSTED = os.path.join(ROOT, 'poc-out', 'docling', 'trusted.jsonl')
DEDUP_IOU = 0.5           # trùng chừng này với vùng D ⇒ cùng một hình


def _iou(a, b):
    ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    iy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    inter = ix * iy
    return inter / max(a[2] * a[3] + b[2] * b[3] - inter, 1e-9)


def readable_by_page(path=TRUSTED):
    """`{(sách, trang): [vùng, ...]}` — chỉ vùng đủ điều kiện vào dòng đọc."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if not r.get('readable'):
                continue
            out.setdefault((r['book'], r['page']), []).append(r)
    return out


def caption_of(r):
    """Chú thích hiện cho trẻ — CHỮ SÁCH IN, không phải chữ máy đặt.

    Có nhãn con thì nhãn con là thứ nói đúng ảnh NÀY («b) Mèo Anh lông ngắn»);
    không có thì dùng chú thích của hình.
    """
    ident = r.get('ident') or {}
    return ident.get('sub') or ident.get('text') or None


def extra_figures(book, pages, existing, index):
    """Vùng Docling THÊM vào, đã loại những vùng D đã có.

    `existing` = bbox các hình D đã nhận, để không đưa hai bản của cùng một hình.
    """
    out = []
    for pp in pages:
        for k, r in enumerate(index.get((book, pp), [])):
            bbox = r['box']
            if any(_iou(bbox, e) > DEDUP_IOU for e in existing):
                continue
            out.append(dict(id=f'{book}:p{pp:03d}:dl{k:02d}', book=book, page=pp,
                            bbox=bbox, area=round(bbox[2] * bbox[3], 5),
                            caption=caption_of(r), source='docling'))
            existing.append(bbox)
    return out
