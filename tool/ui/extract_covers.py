#!/usr/bin/env python3
"""WAL-167 — BÌA SÁCH: trang 1 của mỗi PDF, tự động, KHÔNG cần người chấm.

Khác hẳn crop hình trong ruột sách (`crop_source_assets.py` cần người chọn
bbox): bìa LUÔN là trang 1, nên đây là bước duy nhất trong pipeline tài sản
chạy được ở quy mô 531 cuốn mà không tốn công người.

Đo thật: 18,6 KB/bìa · một lớp ~242 KB · toàn bộ 537 cuốn ≈ 9,8 MB.

WAL-43: ảnh vào `assets/pack/covers/` (gitignore), registry vào poc-out.

    python3 tool/ui/extract_covers.py [lớp]        # mặc định: mọi lớp
"""
import json
import os
import sys

import fitz
from PIL import Image

VER = 'cover-v1'
GRADE = int(sys.argv[1]) if len(sys.argv) > 1 else None
REG = 'poc-out/registry/source-registry.json'
OUT = 'assets/pack/covers'

_reg = json.load(open(REG))
docs = _reg['documents'] if isinstance(_reg, dict) else _reg

os.makedirs(OUT, exist_ok=True)
os.makedirs('poc-out/ui-assets', exist_ok=True)
covers, skipped = [], []
for d in docs:
    if d.get('docType') != 'SGK':
        continue
    if GRADE is not None and d.get('grade') != GRADE:
        continue
    path = d.get('path')
    if not path or not os.path.exists(path):
        skipped.append((d.get('sourceDocumentId'), 'thiếu PDF'))
        continue
    name = f"{d['sourceDocumentId']}.webp"
    try:
        doc = fitz.open(path)
        pm = doc[0].get_pixmap(dpi=48)
        im = Image.frombytes('RGB', [pm.width, pm.height], pm.samples)
        im.thumbnail((320, 480))
        im.save(f'{OUT}/{name}', 'WEBP', quality=82)
        doc.close()
    except Exception as e:  # PDF hỏng ⇒ BỎ, không dựng bìa giả
        skipped.append((d['sourceDocumentId'], str(e)[:40]))
        continue
    # Tên hiển thị: dựng từ TRƯỜNG CÓ THẬT trong registry. Không đọc chữ trên
    # bìa (OCR bìa sai một chữ là gọi sai tên sách của trẻ).
    vol = d.get('volume')
    title = f"{d.get('subject')} {d.get('grade')}"
    covers.append(dict(
        sourceDocumentId=d['sourceDocumentId'], subject=d.get('subject'),
        grade=d.get('grade'), volume=vol, title=title,
        volumeLabel=None if vol in (None, '') else f'Tập {vol}',
        cover=f'covers/{name}', pageCount=d.get('pageCount'),
        # ⭐ Bộ sách: registry KHÔNG có trường này (publisher = UNKNOWN). Để
        # null thay vì đoán — chiều dữ liệu giữ chỗ, không bịa giá trị.
        bookSeries=None,
        extraction=VER, legal='localResearchOnly'))

json.dump(dict(version=VER, books=covers),
          open('poc-out/ui-assets/book-covers.json', 'w'),
          ensure_ascii=False, indent=1)
tot = sum(os.path.getsize(f'{OUT}/{c["sourceDocumentId"]}.webp') for c in covers)
print(f'{len(covers)} bìa · {tot/1024:.0f} KB · trung bình {tot/max(len(covers),1)/1024:.1f} KB/bìa')
for s in skipped[:5]:
    print(f'  ⚠️ bỏ {s[0]}: {s[1]}')
if len(skipped) > 5:
    print(f'  … và {len(skipped)-5} cuốn nữa')
