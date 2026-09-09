#!/usr/bin/env python3
"""MẪU ĐỐI CHIẾU BA BÊN cho bộ chọn hình — NGUỒN · D · DOCLING.

    python3 tool/corpus/selector_review.py --n 60 --seed 20260909

Founder Gate 2026-09-09 buộc: soi CẢ HAI bản cạnh nhau, trên mẫu ĐỘC LẬP,
ĐÓNG BĂNG TRƯỚC KHI SOI. Vì vậy `sample.json` được ghi xong mới dựng ảnh, và
số thứ tự trong bảng ảnh là số trong `sample.json` — đổi mẫu sau khi thấy ảnh
thì lộ ra ngay ở seed.

⚠ Cả ba khung đều cắt TỪ PDF GỐC, không lấy ảnh trong pack. Pack là thứ ĐANG
được xét; lấy nó làm thước thì phép đo tự chứng minh chính nó.

Kết luận ghi tay theo `VERDICTS`. `AMBIGUOUS != EQUIVALENT`: không nhìn ra thì
ghi không nhìn ra.
"""
import argparse
import collections
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PAIRS = os.path.join(ROOT, 'poc-out', 'docling', 'selector-pairs-clean.json')

VERDICTS = ('DOCLING_BETTER', 'EQUIVALENT', 'D_BETTER', 'BOTH_BAD',
            'IDENTITY_WRONG', 'AMBIGUOUS')


def pdf_path(book):
    for p in (f'{ROOT}/poc-out/pdf/{book[:2]}/{book}.pdf',
              f'{ROOT}/poc-out/pdf/{book}.pdf'):
        if os.path.exists(p):
            return p
    return None


def iou(a, b):
    ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    iy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    i = ix * iy
    return i / max(a[2] * a[3] + b[2] * b[3] - i, 1e-9)


def grade_of(book):
    try:
        return int(book[:2])
    except ValueError:
        return 0


def band(g):
    return '1-3' if g <= 3 else ('4-6' if g <= 6 else ('7-9' if g <= 9 else '10-12'))


def subject(book):
    """Môn học suy từ mã sách — chỉ để PHÂN TẦNG, không phải luật nội dung."""
    s = book.split('-', 2)[-1]
    return '-'.join(s.split('-')[:-1]) or s


def stratum(r):
    """DẢI LỚP × LOẠI VÙNG × ĐỘ LỆCH CẮT.

    Độ lệch nằm trong tầng vì đó là chỗ hai bên KHÁC NHAU nhiều nhất. Bỏ nó ra
    thì mẫu toàn ca gần trùng — đẹp mà không nói lên gì.
    """
    v = iou(r['d_bbox'], r['dl_bbox'])
    return (band(grade_of(r['book'])), r.get('kind') or 'picture',
            'khop' if v > 0.7 else ('lech' if v > 0.2 else 'rat-lech'))


def draw(rows, n, seed, per_book=6):
    rng = random.Random(seed)
    st = collections.defaultdict(list)
    for i, r in enumerate(rows):
        st[stratum(r)].append(dict(r, _i=i))
    keys = sorted(st)
    total = len(rows)
    quota = {k: max(3, round(n * len(st[k]) / total)) for k in keys}
    while sum(quota.values()) > n:
        k = max(keys, key=lambda k: quota[k])
        if quota[k] <= 3:
            break
        quota[k] -= 1
    picked, cap = [], collections.Counter()
    for k in keys:
        pool = st[k][:]
        rng.shuffle(pool)
        take = []
        for r in pool:                      # chặn một sách nuốt cả tầng
            if cap[r['book']] >= per_book:
                continue
            take.append(r)
            cap[r['book']] += 1
            if len(take) >= quota[k]:
                break
        picked += take
    rng.shuffle(picked)
    return picked


def sheets(picked, out_dir, cell=460):
    """Mỗi ca MỘT hàng ba khung: NGUỒN (cả trang, khoanh cả hai) · D · DOCLING.

    Xếp theo hàng chứ không theo lưới vì câu hỏi là SO SÁNH TRONG MỘT CA, không
    phải quét nhiều ca. Lưới làm mắt so nhầm ca này với ca kia.
    """
    import fitz
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    docs, made = {}, []
    per = 4
    for s in range(0, len(picked), per):
        chunk = picked[s:s + per]
        im = Image.new('RGB', (3 * cell, len(chunk) * (cell + 30)), (255, 255, 255))
        dr = ImageDraw.Draw(im)
        for j, r in enumerate(chunk):
            y = j * (cell + 30)
            path = pdf_path(r['book'])
            if path and r['book'] not in docs:
                docs[r['book']] = fitz.open(path)
            doc = docs.get(r['book'])
            if doc and 1 <= r['page'] <= len(doc):
                pg = doc[r['page'] - 1]
                W, H = pg.rect.width, pg.rect.height
                def box(b):
                    return fitz.Rect(b[0] * W, b[1] * H,
                                     (b[0] + b[2]) * W, (b[1] + b[3]) * H)
                for c, (label, clip) in enumerate(
                        (('NGUON', None), ('D', box(r['d_bbox'])),
                         ('DOCLING', box(r['dl_bbox'])))):
                    px = pg.get_pixmap(dpi=90 if clip is None else 130, clip=clip)
                    c_im = Image.frombytes('RGB', (px.width, px.height), px.samples)
                    c_im.thumbnail((cell - 10, cell - 10))
                    im.paste(c_im, (c * cell + 5, y + 26))
                    dr.text((c * cell + 8, y + 8), label, fill=(120, 120, 120))
                # khoanh hai hộp trên khung NGUỒN
                px = pg.get_pixmap(dpi=90)
                sc = min((cell - 10) / px.width, (cell - 10) / px.height)
                for b, col in ((r['d_bbox'], (200, 40, 40)),
                               (r['dl_bbox'], (30, 120, 220))):
                    dr.rectangle([5 + b[0] * px.width * sc, 26 + b[1] * px.height * sc,
                                  5 + (b[0] + b[2]) * px.width * sc,
                                  26 + (b[1] + b[3]) * px.height * sc],
                                 outline=col, width=3)
            dr.text((8, y + 8), f"#{r['_i']:04d} {r['book']} tr.{r['page']} "
                                f"IoU={iou(r['d_bbox'], r['dl_bbox']):.2f} "
                                f"«{(r.get('caption') or '')[:60]}»", fill=(0, 0, 0))
            dr.line([0, y + cell + 28, 3 * cell, y + cell + 28], fill=(200, 200, 200))
        p = os.path.join(out_dir, f'sheet-{s // per:02d}.png')
        im.save(p)
        made.append(p)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--seed', type=int, default=20260909)
    ap.add_argument('--pairs', default=PAIRS)
    ap.add_argument('--out', default=os.path.join(ROOT, 'poc-out', 'selector-review'))
    a = ap.parse_args()
    rows = json.load(open(a.pairs, encoding='utf-8'))
    picked = draw(rows, a.n, a.seed)
    os.makedirs(a.out, exist_ok=True)
    # ĐÓNG BĂNG TRƯỚC: ghi mẫu xong mới dựng ảnh.
    with open(os.path.join(a.out, 'sample.json'), 'w', encoding='utf-8') as fh:
        json.dump(dict(seed=a.seed, frame=len(rows), verdicts=list(VERDICTS),
                       picked=picked), fh, ensure_ascii=False, indent=1)
    made = sheets(picked, a.out)
    st = collections.Counter(stratum(r) for r in picked)
    print(f'khung {len(rows)} cặp · mẫu {len(picked)} · {len(made)} bảng ảnh → {a.out}')
    for k in sorted(st):
        print(f'   {k[0]:>5} {k[1]:>8} {k[2]:>8} {st[k]}')
    print(f'   sách khác nhau: {len({r["book"] for r in picked})}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
