#!/usr/bin/env python3
"""WAL-150 KS-C — SOURCE_ASSET crop: render trang PDF + crop theo bbox
TỈ-LỆ do NGƯỜI CHẤM (association=human-curation — không mặc định ảnh nào
là chân dung §11). Provenance đầy đủ §10/§12; localResearchOnly (WAL-43):
asset ở poc-out, KHÔNG commit, distribution = Founder/Legal Gate (§29)."""
import json, os
import fitz

VER = 'asset-crop-v1'

# (assetId, pdfPath, pagePdf(1-based), bboxFrac(x0,y0,x1,y1), kind, personId, caption)
CURATED = [
    ('asset:lu-tho-portrait', 'poc-out/pdf/07/07-sgk-lich-su-va-dia-li-7.pdf',
     23, (0.235, 0.425, 0.625, 0.645), 'PORTRAIT', 'p:mác-tin-lu-thơ',
     'Hình 4. Mác-tin Lu-thơ (1483–1546) — SGK LS&ĐL 7, trang PDF 23'),
    ('asset:sac-lo-ma-nho-statue', 'poc-out/pdf/07/07-sgk-lich-su-va-dia-li-7.pdf',
     11, (0.700, 0.360, 0.895, 0.585), 'STATUE_PHOTO', 'p:sác-lơ-ma-nhơ',
     'Hình 1. Tượng Hoàng đế Sác-lơ-ma-nhơ (742–814) ở Hăm-buốc — SGK LS&ĐL 7, trang PDF 11'),
    ('asset:bui-xuan-phai-photo', 'poc-out/pdf/06/06-sgk-mi-thuat-6.pdf',
     14, (0.440, 0.052, 0.910, 0.325), 'HISTORICAL_PHOTO', 'p:bùi-xuân-phái',
     'Hoạ sĩ Bùi Xuân Phái — ảnh: Trần Chính Nghĩa (nguồn in trong sách) — SGK MT 6, trang PDF 14'),
    ('asset:pho-hang-mam-1984', 'poc-out/pdf/06/06-sgk-mi-thuat-6.pdf',
     14, (0.095, 0.498, 0.500, 0.712), 'ARTWORK', 'p:bùi-xuân-phái',
     'Phố Hàng Mắm, 1984, tranh sơn dầu — Bảo tàng Mĩ thuật VN (nguồn in trong sách) — SGK MT 6, trang PDF 14'),
]

def main():
    os.makedirs('poc-out/stories/portraits', exist_ok=True)
    registry = []
    for aid, pdf, page, (x0, y0, x1, y1), kind, pid, caption in CURATED:
        doc = fitz.open(pdf)
        p = doc[page - 1]
        r = p.rect
        clip = fitz.Rect(r.width * x0, r.height * y0,
                         r.width * x1, r.height * y1)
        pix = p.get_pixmap(dpi=150, clip=clip)
        out = f'poc-out/stories/portraits/{aid.split(":")[1]}.png'
        pix.save(out)
        registry.append(dict(
            assetId=aid, type='SOURCE_ASSET', assetKind=kind,
            sourceDocumentId=os.path.basename(pdf)[:-4], pagePdf=page,
            bboxFrac=[x0, y0, x1, y1], personId=pid, caption=caption,
            associationBy='human-curation', extractionVersion=VER,
            file=out, px=[pix.width, pix.height],
            legal='localResearchOnly'))
        print(f'{aid}: {pix.width}x{pix.height} → {out}')
        doc.close()
    json.dump(registry,
              open('poc-out/stories/assets-registry-v0.json', 'w'),
              ensure_ascii=False, indent=1)
    print(f'registry: {len(registry)} SOURCE_ASSET')

if __name__ == '__main__':
    main()
