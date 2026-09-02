#!/usr/bin/env python3
"""WAL-144 #28 Địa — SOURCE_ASSET bản đồ: render trang PDF + crop bbox TỈ LỆ
do người chấm (human-curation — mắt xác nhận, không đoán). Provenance đầy đủ;
localResearchOnly (WAL-43): PNG vào assets/pack (GITIGNORED — không commit,
distribution = Founder/Legal Gate), registry JSON vào poc-out/ui-assets."""
import json, os
import fitz

VER = 'map-crop-v1'
# (assetFile, pdfPath, pagePdf 1-based, bboxFrac, caption in trong sách)
CURATED = [
    ('map-ls-dia-5-p012-tu-nhien-vn.png',
     'poc-out/pdf/05/05-sgk-lich-su-va-dia-li-5.pdf', 12,
     (0.075, 0.050, 0.935, 0.905),
     'Hình 1. Bản đồ tự nhiên Việt Nam — SGK LS&ĐL 5, trang in 10'),
]
os.makedirs('assets/pack', exist_ok=True)
os.makedirs('poc-out/ui-assets', exist_ok=True)
reg = []
for name, pdf, page, (x0, y0, x1, y1), caption in CURATED:
    doc = fitz.open(pdf)
    pg = doc[page - 1]
    r = pg.rect
    clip = fitz.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height,
                     r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    pix = pg.get_pixmap(dpi=170, clip=clip)
    out = f'assets/pack/{name}'
    pix.save(out)
    reg.append(dict(asset=name, sourceDocumentId=os.path.basename(pdf)[:-4],
                    pagePdf=page, bboxFrac=[x0, y0, x1, y1], caption=caption,
                    kind='SOURCE_ASSET/MAP', legal='localResearchOnly',
                    extraction=VER, association='human-curation'))
    print(f'{out}: {pix.width}x{pix.height}')
json.dump(dict(version=VER, assets=reg),
          open('poc-out/ui-assets/map-assets.json', 'w'), ensure_ascii=False, indent=1)
print('registry: poc-out/ui-assets/map-assets.json')
