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
import unicodedata

import fitz
from PIL import Image

VER = 'cover-v1'

def _slug(t):
    k = unicodedata.normalize('NFD', (t or '').lower())
    k = ''.join(c for c in k if not unicodedata.combining(c)).replace('đ', 'd')
    return '-'.join(''.join(c if c.isalnum() else ' ' for c in k).split())


# Nhiều cuốn dùng CHUNG một `subject`: lớp 10 có 10 cuốn đều mang «Chuyên đề»,
# nên tên hiện ra là «Chuyên đề 10» y hệt nhau và trẻ không phân biệt nổi Hoá
# học với Sinh học (đo trên máy, khung GATE2-n01). Môn thật nằm trong
# `nameExtra` nhưng ở dạng slug KHÔNG DẤU. Thay vì hiện slug cho trẻ đọc, tra
# ngược slug đó về đúng tên môn CÓ DẤU của một cuốn khác trong chính registry —
# vẫn là trường có thật, không OCR bìa, không tự đặt tên.
_SUBJECT_BY_SLUG = {}


def _display_subject(d):
    subj = d.get('subject') or ''
    extra = d.get('nameExtra') or ''
    if not extra:
        return subj
    key = _slug(extra.replace('hoc-tap-', ''))
    for part in (key, key.replace('chuyen-de-', '')):
        for n in range(len(part.split('-')), 0, -1):
            cand = '-'.join(part.split('-')[-n:])
            hit = _SUBJECT_BY_SLUG.get(cand)
            if hit and _slug(hit) != _slug(subj):
                return f'{subj} · {hit}'
    return subj

GRADE = int(sys.argv[1]) if len(sys.argv) > 1 else None
REG = 'poc-out/registry/source-registry.json'
OUT = 'assets/pack/covers'

_reg = json.load(open(REG))
docs = _reg['documents'] if isinstance(_reg, dict) else _reg
_SUBJECT_BY_SLUG.update({_slug(x.get('subject')): x.get('subject')
                         for x in docs if x.get('subject')})

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
    # ⭐ Nhiều cuốn dùng CHUNG một `subject` — lớp 10 có 10 cuốn đều mang
    # subject «Chuyên đề», nên tên hiện ra là «Chuyên đề 10» y hệt nhau và trẻ
    # không phân biệt nổi Hoá học với Sinh học (đo trên máy: khung GATE2-n01).
    # `nameExtra` mang phần còn lại của tên file — dùng nó để tách, vẫn là
    # TRƯỜNG CÓ THẬT trong registry, không OCR bìa.
    title = f"{_display_subject(d)} {d.get('grade')}"
    covers.append(dict(
        sourceDocumentId=d['sourceDocumentId'], subject=d.get('subject'),
        grade=d.get('grade'), volume=vol, title=title,
        volumeLabel=None if vol in (None, '') else f'Tập {vol}',
        cover=f'covers/{name}', pageCount=d.get('pageCount'),
        # ⭐ Bộ sách: registry KHÔNG có trường này (publisher = UNKNOWN). Để
        # null thay vì đoán — chiều dữ liệu giữ chỗ, không bịa giá trị.
        bookSeries=None,
        extraction=VER, legal='localResearchOnly'))

# ⭐ GỘP, không ghi đè: chạy `extract_covers.py 10` mà thay sạch registry thì
# lần dựng pack lớp 5 kế tiếp sẽ ra GIÁ SÁCH RỖNG — hỏng im lặng, đúng loại
# nguy nhất. Giữ bìa của các lớp khác, chỉ thay phần của lớp đang chạy.
_REG = 'poc-out/ui-assets/book-covers.json'
_kept = []
if GRADE is not None and os.path.exists(_REG):
    try:
        _kept = [b for b in json.load(open(_REG)).get('books', [])
                 if b.get('grade') != GRADE]
    except Exception:
        _kept = []
json.dump(dict(version=VER, books=_kept + covers), open(_REG, 'w'),
          ensure_ascii=False, indent=1)
tot = sum(os.path.getsize(f'{OUT}/{c["sourceDocumentId"]}.webp') for c in covers)
print(f'{len(covers)} bìa · {tot/1024:.0f} KB · trung bình {tot/max(len(covers),1)/1024:.1f} KB/bìa')
for s in skipped[:5]:
    print(f'  ⚠️ bỏ {s[0]}: {s[1]}')
if len(skipped) > 5:
    print(f'  … và {len(skipped)-5} cuốn nữa')
