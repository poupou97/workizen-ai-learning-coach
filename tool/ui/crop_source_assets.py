#!/usr/bin/env python3
"""WAL-133 — SOURCE_ASSET scoped crop: render trang PDF + cắt bbox TỈ LỆ do
NGƯỜI chấm (human-curation), ghi provenance đầy đủ vào một registry chung.

Thay `crop_map_assets.py` (chỉ bản đồ) — một công cụ, một registry, nhiều môn.
Chấm bbox bằng `tool/ui/preview_page_grid.py` (lưới 0.1 có nhãn) rồi điền vào
CURATED; máy không tự đoán đâu là «hình của bài».

WAL-43: PNG vào assets/pack (GITIGNORED — không commit, không phân phối;
distribution = Founder/Legal Gate). Registry JSON vào poc-out/ui-assets.

    python3 tool/ui/crop_source_assets.py [--check]
"""
import json
import os
import sys

import fitz

VER = 'source-crop-v1'

# (file, subject, kind, pdf, pagePdf, pagePrinted, bboxFrac,
#  printedCaption | None, samGloss | None, lesson | None)
#
# printedCaption CHỈ điền khi sách IN caption đó. Không có thì để None —
# tuyệt đối không tự viết một câu rồi gọi nó là lời sách.
CURATED = [
    ('map-ls-dia-5-p012-tu-nhien-vn.png', 'LS&ĐL', 'MAP',
     'poc-out/pdf/05/05-sgk-lich-su-va-dia-li-5.pdf', 12, 10,
     (0.075, 0.050, 0.935, 0.905),
     'Hình 1. Bản đồ tự nhiên Việt Nam', None, 1),

    ('toan-5-p023-chia-banh-phan-so.png', 'Toán', 'FIGURE',
     'poc-out/pdf/05-sgk-toan-5-tap-mot.pdf', 23, 22,
     (0.185, 0.388, 0.800, 0.556),
     None,  # sách KHÔNG in caption cho hình này
     'Hai cách chia 5 chiếc bánh cho 6 người — phần của mỗi người tô đỏ.', 6),

    ('khoa-5-p017-tach-muoi-hinh5.png', 'Khoa học', 'EXPERIMENT',
     'poc-out/pdf/05/05-sgk-khoa-hoc-5.pdf', 17, 16,
     (0.140, 0.409, 0.930, 0.618),
     'Hình 5', None, None),
]

check = '--check' in sys.argv
os.makedirs('assets/pack', exist_ok=True)
os.makedirs('poc-out/ui-assets', exist_ok=True)
reg, missing = [], []
for (name, subject, kind, pdf, page, printed, bbox,
     caption, gloss, lesson) in CURATED:
    if not os.path.exists(pdf):
        missing.append((name, pdf))
        continue
    x0, y0, x1, y1 = bbox
    assert 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1, f'bbox hỏng: {name}'
    out = f'assets/pack/{name}'
    if not check:
        doc = fitz.open(pdf)
        pg = doc[page - 1]
        r = pg.rect
        clip = fitz.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height,
                         r.x0 + x1 * r.width, r.y0 + y1 * r.height)
        pg.get_pixmap(clip=clip, dpi=200).save(out)
        doc.close()
    reg.append(dict(asset=name, subject=subject, assetType=kind,
                    sourceDocumentId=os.path.basename(pdf)[:-4],
                    pagePdf=page, pagePrinted=printed,
                    bboxFrac=list(bbox), printedCaption=caption,
                    samGloss=gloss, lesson=lesson,
                    extraction=VER, legal='localResearchOnly',
                    association='human-curation'))

path = 'poc-out/ui-assets/source-assets.json'
if not check:
    json.dump(dict(version=VER, assets=reg), open(path, 'w'),
              ensure_ascii=False, indent=1)
for a in reg:
    f = f"assets/pack/{a['asset']}"
    size = os.path.getsize(f) if os.path.exists(f) else 0
    print(f"  {a['subject']:9} {a['assetType']:10} {a['asset']}  "
          f"{size // 1024}KB  caption={'IN' if a['printedCaption'] else 'KHÔNG'}")
for name, pdf in missing:
    print(f'  ⚠️ BỎ {name}: không có {pdf} trên máy này')
print(f'{path}: {len(reg)} asset / {len({a["subject"] for a in reg})} môn')
