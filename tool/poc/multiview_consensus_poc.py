#!/usr/bin/env python3
"""WAL-62 — Multi-view consensus: đồng thuận đa biến thể có giảm biểu thức bịa?

Giả thuyết (phải falsify): chạy độc lập N biến thể tiền xử lý → OCR → ghép
biểu thức; chỉ NHẬN biểu thức xuất hiện ở ≥2 view ⇒ giảm Fabricated Rate.

⚠️ Giới hạn khai trước: các view ở đây là BIẾN THỂ QUANG HỌC (contrast/denoise/
sharpen) — KHÔNG có sửa phối cảnh thật (cần corner detection). Lỗi GHÉP HÌNH HỌC
(pairing sai theo trục y) có thể TƯƠNG QUAN giữa các view ⇒ POC này đo đúng rủi
ro "đồng thuận giả" mà Founder cảnh báo, không né nó.
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter

def views(im):
    """3 biến thể quang học độc lập + bản gốc."""
    g = im.convert('L')
    return {
        'orig': im,
        'autocontrast': ImageOps.autocontrast(g, cutoff=2).convert('RGB'),
        'denoise-sharpen': g.filter(ImageFilter.MedianFilter(3))
                            .filter(ImageFilter.UnsharpMask(radius=2, percent=150))
                            .convert('RGB'),
        'binarize': g.point(lambda p: 255 if p > 140 else 0).convert('RGB'),
    }

if __name__ == '__main__':
    src_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    for jpg in sorted(src_dir.glob('*-L*.jpg')):
        im = Image.open(jpg)
        for vname, vim in views(im).items():
            d = out_dir / vname
            d.mkdir(parents=True, exist_ok=True)
            vim.save(d / f'{jpg.stem}.png')
    # gói từng (view, level) thành PDF cho ocr_pdf.swift
    for vdir in sorted(out_dir.iterdir()):
        if not vdir.is_dir(): continue
        for lv in ['L1', 'L2', 'L3']:
            pages = [Image.open(f).convert('RGB') for f in sorted(vdir.glob(f'*-{lv}.png'))]
            if pages:
                pages[0].save(vdir / f'{lv}.pdf', save_all=True, append_images=pages[1:])
                print(f'{vdir.name}/{lv}.pdf ← {len(pages)}')
