#!/usr/bin/env python3
"""MẪU ĐỐI CHIẾU BỐN BÊN — NGUỒN · D · DOCLING · CÁI ĐƯỢC CHỌN.

    python3 tool/corpus/selector_review4.py --n 60 --seed 20260912 \
        --decisions /private/tmp/wal-stage-selector/selector-decisions.jsonl

Founder Gate (vòng an toàn cuối): soi bốn khung cạnh nhau, trên mẫu ĐỘC LẬP,
ĐÓNG BĂNG TRƯỚC KHI SOI, và **cố ý lấy cả ca sát ranh giới chốt mới**.

⭐ VÌ SAO PHẢI CÓ KHUNG THỨ TƯ. Ba khung chỉ trả lời «bản nào đẹp hơn». Câu
phải trả lời là «CHÍNH SÁCH có chọn đúng không» — và ở những ca BỊ CHẶN, cái
được chọn là D chứ không phải Docling. Không vẽ khung ấy ra thì mọi ca chặn
sai đều vô hình.

⚠ Cả bốn khung cắt TỪ PDF GỐC. Pack là thứ đang được xét; lấy nó làm thước thì
phép đo tự chứng minh chính nó.
"""
import argparse
import collections
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

VERDICTS = ('DOCLING_BETTER', 'EQUIVALENT', 'D_BETTER', 'BOTH_BAD',
            'IDENTITY_WRONG', 'AMBIGUOUS')
BLOCKED = ('CONTAINS_SEPARATE_CAPTION', 'CONTAINS_OTHER_NAMED_VISUAL',
           'CONTAINS_OTHER_TRUSTED_REGION', 'AMBIGUOUS_CONTAINMENT',
           'PART_OF_NAMED_FIGURE', 'SUBFIGURE_NAME_CLASH')


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


def band(book):
    try:
        g = int(book[:2])
    except ValueError:
        return '?'
    return '1-3' if g <= 3 else ('4-6' if g <= 6 else ('7-9' if g <= 9 else '10-12'))


def stratum(r):
    v = iou(r['d_bbox'], r['dl_bbox'])
    lech = 'khop' if v > 0.7 else ('lech' if v > 0.2 else 'rat-lech')
    if r['decision'] != 'DOCLING_SUPERSEDES_D':
        return ('CHAN', r['decision'], '')     # ca chặn: tầng theo LÝ DO chặn
    return ('THAY', band(r['book']), r.get('kind') or 'picture', lech)


def draw(rows, n, seed, per_book=5, blocked_share=0.30):
    """Rút mẫu, DÀNH SẴN một phần cho ca bị chặn.

    Lấy theo tỉ lệ tự nhiên thì ca chặn (~2%) gần như không lọt vào mẫu, và
    đúng phần chính sách mới nhất lại không ai soi.
    """
    rng = random.Random(seed)
    blk = [dict(r, _i=i) for i, r in enumerate(rows)
           if r['decision'] != 'DOCLING_SUPERSEDES_D']
    sup = [dict(r, _i=i) for i, r in enumerate(rows)
           if r['decision'] == 'DOCLING_SUPERSEDES_D']
    n_blk = min(len(blk), int(round(n * blocked_share)))
    picked = []
    cap = collections.Counter()

    def take(pool, want):
        st = collections.defaultdict(list)
        for r in pool:
            st[stratum(r)].append(r)
        keys = sorted(st)
        got = []
        while len(got) < want and keys:
            for k in list(keys):
                if len(got) >= want:
                    break
                bag = st[k]
                rng.shuffle(bag)
                pick = None
                while bag:
                    c = bag.pop()
                    if cap[c['book']] < per_book:
                        pick = c
                        break
                if pick is None:
                    keys.remove(k)
                    continue
                cap[pick['book']] += 1
                got.append(pick)
        return got

    picked += take(blk, n_blk)
    picked += take(sup, n - len(picked))
    rng.shuffle(picked)
    return picked


def sheets(picked, out_dir, cell=430):
    import fitz
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    docs, made, per = {}, [], 3
    for s in range(0, len(picked), per):
        chunk = picked[s:s + per]
        im = Image.new('RGB', (4 * cell, len(chunk) * (cell + 32)), (255, 255, 255))
        dr = ImageDraw.Draw(im)
        for j, r in enumerate(chunk):
            y = j * (cell + 32)
            sup = r['decision'] == 'DOCLING_SUPERSEDES_D'
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
                sel = r['dl_bbox'] if sup else r['d_bbox']
                panes = (('NGUON', None), ('D', box(r['d_bbox'])),
                         ('DOCLING', box(r['dl_bbox'])),
                         ('ĐƯỢC CHỌN = ' + ('DOCLING' if sup else 'D'), box(sel)))
                for c, (label, clip) in enumerate(panes):
                    px = pg.get_pixmap(dpi=85 if clip is None else 125, clip=clip)
                    c_im = Image.frombytes('RGB', (px.width, px.height), px.samples)
                    c_im.thumbnail((cell - 10, cell - 10))
                    im.paste(c_im, (c * cell + 5, y + 28))
                    dr.text((c * cell + 8, y + 9), label,
                            fill=(20, 120, 40) if c == 3 else (120, 120, 120))
                px = pg.get_pixmap(dpi=85)
                sc = min((cell - 10) / px.width, (cell - 10) / px.height)
                for b, col in ((r['d_bbox'], (200, 40, 40)),
                               (r['dl_bbox'], (30, 120, 220))):
                    dr.rectangle([5 + b[0] * px.width * sc, 28 + b[1] * px.height * sc,
                                  5 + (b[0] + b[2]) * px.width * sc,
                                  28 + (b[1] + b[3]) * px.height * sc],
                                 outline=col, width=3)
            dr.text((8, y + 9),
                    f"#{r['_i']:05d} [{r['decision']}] {r['book']} tr.{r['page']} "
                    f"IoU={iou(r['d_bbox'], r['dl_bbox']):.2f} "
                    f"«{(r.get('caption') or '')[:54]}»", fill=(0, 0, 0))
            dr.line([0, y + cell + 30, 4 * cell, y + cell + 30], fill=(200, 200, 200))
        p = os.path.join(out_dir, f'sheet-{s // per:02d}.png')
        im.save(p)
        made.append(p)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--seed', type=int, default=20260912)
    ap.add_argument('--decisions', required=True)
    ap.add_argument('--out', default=os.path.join(ROOT, 'poc-out', 'selector-review4'))
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.decisions, encoding='utf-8')]
    picked = draw(rows, a.n, a.seed)
    os.makedirs(a.out, exist_ok=True)
    # ĐÓNG BĂNG TRƯỚC: ghi mẫu xong mới dựng ảnh.
    with open(os.path.join(a.out, 'sample.json'), 'w', encoding='utf-8') as fh:
        json.dump(dict(seed=a.seed, frame=len(rows), verdicts=list(VERDICTS),
                       picked=picked), fh, ensure_ascii=False, indent=1)
    made = sheets(picked, a.out)
    st = collections.Counter(r['decision'] for r in picked)
    print(f'khung {len(rows)} quyết định · mẫu {len(picked)} · {len(made)} bảng ảnh → {a.out}')
    for k, v in st.most_common():
        print(f'   {k:32s} {v}')
    print(f'   sách khác nhau: {len({r["book"] for r in picked})}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
