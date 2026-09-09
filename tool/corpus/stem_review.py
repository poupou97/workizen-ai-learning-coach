#!/usr/bin/env python3
"""WAL-239 — MẪU ĐỐI CHIẾU: BẢN IN ↔ CHỮ TRẺ ĐANG ĐỌC.

    python3 tool/corpus/stem_review.py --n 60 --seed 20260914

Founder Gate: «Compare learner-visible OCR against the printed source. Measure
learner harm, not strange-character frequency.»

Mỗi ca một hàng: bên trái là VÙNG CÔNG THỨC CẮT TỪ PDF GỐC, bên phải là chuỗi
chữ mà dòng đọc đang hiện ra ở đúng toạ độ ấy. Không có khung thứ ba: câu hỏi
duy nhất là «bản phiên âm này có nói đúng cái sách in không».

Mẫu ĐÓNG BĂNG trước khi soi — `sample.json` ghi xong mới dựng ảnh.

Phân loại (Founder chốt):

    TEXT_CORRECT                 đọc đúng, dùng được
    TEXT_READABLE_BUT_FORMAT_LOST đúng nghĩa, mất định dạng (mũ/chỉ số/phân số)
    SEMANTICALLY_WRONG           nói SAI so với bản in — hại trực tiếp
    SYMBOL_MISSING               thiếu ký hiệu
    SYMBOL_SUBSTITUTED           ký hiệu bị thay bằng ký hiệu khác
    STRUCTURE_LOST               mất cấu trúc (tử/mẫu, hàng/cột, thứ tự)
    SOURCE_IMAGE_REQUIRED        chữ không thể tải nổi nghĩa — phải giữ ảnh in
    AMBIGUOUS                    không kết luận được. `UNKNOWN != VALID`.
"""
import argparse
import collections
import json
import os
import random
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

VERDICTS = ('TEXT_CORRECT', 'TEXT_READABLE_BUT_FORMAT_LOST', 'SEMANTICALLY_WRONG',
            'SYMBOL_MISSING', 'SYMBOL_SUBSTITUTED', 'STRUCTURE_LOST',
            'SOURCE_IMAGE_REQUIRED', 'AMBIGUOUS')


def pdf_path(book):
    for p in (f'{ROOT}/poc-out/pdf/{book[:2]}/{book}.pdf',
              f'{ROOT}/poc-out/pdf/{book}.pdf'):
        if os.path.exists(p):
            return p
    return None


def band(book):
    try:
        g = int(book[:2])
    except ValueError:
        return '?'
    return '1-5' if g <= 5 else ('6-9' if g <= 9 else '10-12')


def draw(rows, n, seed, per_book=4):
    """Phân tầng theo MÔN × DẢI LỚP, chặn một sách nuốt cả tầng."""
    rng = random.Random(seed)
    st = collections.defaultdict(list)
    for i, r in enumerate(rows):
        st[(r['subject'], band(r['book']))].append(dict(r, _i=i))
    keys = sorted(st)
    quota = {k: max(3, round(n * len(st[k]) / len(rows))) for k in keys}
    while sum(quota.values()) > n:
        k = max(keys, key=lambda k: quota[k])
        if quota[k] <= 3:
            break
        quota[k] -= 1
    picked, cap = [], collections.Counter()
    for k in keys:
        bag = st[k][:]
        rng.shuffle(bag)
        got = 0
        for r in bag:
            if got >= quota[k]:
                break
            if cap[r['book']] >= per_book:
                continue
            cap[r['book']] += 1
            picked.append(r)
            got += 1
    rng.shuffle(picked)
    return picked


def sheets(picked, out_dir, cell=520, pad=0.012):
    import fitz
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    docs, made, per = {}, [], 4
    for s in range(0, len(picked), per):
        chunk = picked[s:s + per]
        im = Image.new('RGB', (2 * cell + 480, len(chunk) * (cell // 2 + 46)),
                       (255, 255, 255))
        dr = ImageDraw.Draw(im)
        for j, r in enumerate(chunk):
            y = j * (cell // 2 + 46)
            path = pdf_path(r['book'])
            if path and r['book'] not in docs:
                docs[r['book']] = fitz.open(path)
            doc = docs.get(r['book'])
            if doc and 1 <= r['page'] <= len(doc):
                pg = doc[r['page'] - 1]
                W, H = pg.rect.width, pg.rect.height
                b = r['box']
                clip = fitz.Rect(max(b[0] - pad, 0) * W, max(b[1] - pad, 0) * H,
                                 min(b[0] + b[2] + pad, 1) * W,
                                 min(b[1] + b[3] + pad, 1) * H)
                px = pg.get_pixmap(dpi=190, clip=clip)
                c = Image.frombytes('RGB', (px.width, px.height), px.samples)
                c.thumbnail((cell, cell // 2 - 6))
                im.paste(c, (6, y + 30))
            dr.text((8, y + 10),
                    f"#{r['_i']:05d} [{r['subject']}] {r['book'][:34]} tr.{r['page']}",
                    fill=(0, 0, 0))
            dr.text((cell + 20, y + 10), 'CHỮ TRẺ ĐANG ĐỌC:', fill=(180, 30, 30))
            for k, ln in enumerate(textwrap.wrap(r['text'], 62)[:11]):
                dr.text((cell + 20, y + 30 + k * 17), ln, fill=(0, 0, 0))
            dr.line([0, y + cell // 2 + 42, 2 * cell + 480, y + cell // 2 + 42],
                    fill=(205, 205, 205))
        p = os.path.join(out_dir, f'sheet-{s // per:02d}.png')
        im.save(p)
        made.append(p)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--seed', type=int, default=20260914)
    ap.add_argument('--kind', default='formula')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    src = os.path.join(ROOT, f'poc-out/docling/stem-exposure-{a.kind}.json')
    rows = json.load(open(src, encoding='utf-8'))
    picked = draw(rows, a.n, a.seed)
    out = a.out or os.path.join(ROOT, f'poc-out/stem-review-{a.kind}')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'sample.json'), 'w', encoding='utf-8') as fh:
        json.dump(dict(seed=a.seed, kind=a.kind, frame=len(rows),
                       verdicts=list(VERDICTS), picked=picked), fh,
                  ensure_ascii=False, indent=1)
    made = sheets(picked, out)
    st = collections.Counter((r['subject'], band(r['book'])) for r in picked)
    print(f'khung {len(rows)} vùng · mẫu {len(picked)} · {len(made)} bảng → {out}')
    for k in sorted(st):
        print(f'   {k[0]:12s} {k[1]:6s} {st[k]}')
    print(f'   sách khác nhau: {len({r["book"] for r in picked})}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
