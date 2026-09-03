#!/usr/bin/env python3
"""WAL-133 — xem một trang PDF kèm LƯỚI TỈ LỆ để CHẤM bbox bằng mắt.

Curation là việc của người: máy không biết đâu là «hình của bài» và đâu là
trang trí. Công cụ này chỉ làm cho việc chấm chính xác lặp lại được — lưới
0.1 có nhãn, nên bbox đọc thẳng ra chứ không ước lượng.

    python3 tool/ui/preview_page_grid.py <pdf> <trang 1-based> <ra.png> [dpi]
"""
import sys
import fitz
from PIL import Image, ImageDraw

pdf, page, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 110
pm = fitz.open(pdf)[page - 1].get_pixmap(dpi=dpi)
im = Image.frombytes('RGB', [pm.width, pm.height], pm.samples).convert('RGB')
dr = ImageDraw.Draw(im)
W, H = im.size
for i in range(1, 10):
    x, y = W * i / 10, H * i / 10
    dr.line([(x, 0), (x, H)], fill=(255, 0, 0), width=1)
    dr.line([(0, y), (W, y)], fill=(0, 90, 255), width=1)
    dr.text((x + 2, 2), f'{i/10:.1f}', fill=(255, 0, 0))
    dr.text((2, y + 2), f'{i/10:.1f}', fill=(0, 90, 255))
im.save(out)
print(f'{out}  {W}x{H}  (đỏ = x, xanh = y, theo tỉ lệ)')
