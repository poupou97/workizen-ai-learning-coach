#!/usr/bin/env python3
"""MẪU PHÂN TẦNG để đo `FIGURE_CROP_VALID` — soi bằng MẮT, không suy từ cổng.

    python3 tool/corpus/crop_sample.py --n 120 --seed 20260909

⚠ `UNKNOWN != VALID`. Chưa soi thì KHÔNG được tính là đúng.

⛔ KHÔNG suy `FIGURE_CROP_VALID` từ `REGION_TRUST`, từ chú thích, từ số đề xuất,
hay từ số hình trong pack. Cổng tin cậy trả lời «có bằng chứng in không»; câu
hỏi ở đây khác hẳn: «vùng cắt ấy có phải là hình, trọn vẹn, không nuốt chữ
không». Chín ca soi tay hôm qua không kết luận được gì cho 17.724 hình.

Phân tầng theo thứ tự ảnh hưởng đã đo được: DẢI LỚP × NGUỒN (D / Docling) ×
CÓ CHÚ THÍCH. Họ hình (ảnh chụp, bản đồ, sơ đồ, ký âm, mảng ghép, hình có chữ
bên trong) KHÔNG có nhãn sẵn trong dữ liệu — chúng được ghi lúc soi, không được
đoán trước, nếu không lại là nhãn vòng tròn.
"""
import argparse
import collections
import json
import os
import random
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PACK = os.path.join(ROOT, 'assets', 'pack')
FIG = os.path.join(ROOT, 'poc-out', 'packs', 'figures')

VERDICTS = ('VALID', 'TRUNCATED', 'PROSE_CONTAMINATED', 'NEIGHBOR_VISUAL_INCLUDED',
            'IDENTITY_MISMATCH', 'AMBIGUOUS')


def band(g):
    return '1-3' if g <= 3 else ('4-8' if g <= 8 else '9-12')


def frame():
    """Khung lấy mẫu: mọi hình ĐANG NẰM TRONG DÒNG ĐỌC của trẻ."""
    rows = []
    for g in range(1, 13):
        p = os.path.join(PACK, f'lesson-index-g{g}.json')
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8') as fh:
            d = json.load(fh)
        seen = set()
        for r in d.get('lessonReadings') or []:
            for i in (r.get('content') or []):
                if i.get('t') != 'img' or i.get('id') in seen:
                    continue
                seen.add(i['id'])
                rows.append(dict(id=i['id'], grade=g, band=band(g),
                                 page=i.get('page'), book=r.get('book'),
                                 lesson=r.get('lesson'),
                                 caption=i.get('caption'),
                                 source='docling' if ':dl' in i['id'] else 'D'))
    return rows


def strata(rows):
    out = collections.defaultdict(list)
    for r in rows:
        out[(r['band'], r['source'], bool(r['caption']))].append(r)
    return out


def draw(rows, n, seed):
    """Rút mẫu: mỗi tầng tối thiểu 4 ca, phần còn lại chia theo tỉ lệ."""
    rng = random.Random(seed)
    st = strata(rows)
    keys = sorted(st)
    total = sum(len(v) for v in st.values())
    quota = {}
    for k in keys:
        quota[k] = max(4, round(n * len(st[k]) / total)) if st[k] else 0
    # cắt về đúng n, ưu tiên giữ tầng nhỏ
    while sum(quota.values()) > n:
        k = max(keys, key=lambda k: quota[k])
        if quota[k] <= 4:
            break
        quota[k] -= 1
    picked = []
    for k in keys:
        pool = st[k]
        picked += rng.sample(pool, min(quota[k], len(pool)))
    rng.shuffle(picked)
    return picked


def crop_bytes(fid, grade):
    db = os.path.join(FIG, f'figures-g{grade}.db')
    if not os.path.exists(db):
        return None
    con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    try:
        r = con.execute('SELECT jpeg FROM fig WHERE id=?', (fid,)).fetchone()
        return r[0] if r else None
    finally:
        con.close()


def sheets(picked, out_dir, per=12, cols=4, cell=430):
    """Bảng ảnh để soi hàng loạt. Mỗi ô có SỐ để ghi kết luận theo số."""
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    made = []
    for s in range(0, len(picked), per):
        chunk = picked[s:s + per]
        rowsn = (len(chunk) + cols - 1) // cols
        im = Image.new('RGB', (cols * cell, rowsn * (cell + 26)), (255, 255, 255))
        dr = ImageDraw.Draw(im)
        for j, r in enumerate(chunk):
            x, y = (j % cols) * cell, (j // cols) * (cell + 26)
            raw = crop_bytes(r['id'], r['grade'])
            if raw:
                import io
                c = Image.open(io.BytesIO(raw)).convert('RGB')
                c.thumbnail((cell - 8, cell - 8))
                im.paste(c, (x + 4, y + 22))
            dr.rectangle([x, y, x + cell - 2, y + cell + 22], outline=(200, 200, 200))
            dr.text((x + 6, y + 6),
                    f"#{s + j:03d} g{r['grade']} {r['source']}"
                    f"{' ·cap' if r['caption'] else ''}", fill=(0, 0, 0))
        p = os.path.join(out_dir, f'sheet-{s // per:02d}.png')
        im.save(p)
        made.append(p)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=120)
    ap.add_argument('--seed', type=int, default=20260909)
    ap.add_argument('--out', default=os.path.join(ROOT, 'poc-out', 'crop-sample'))
    a = ap.parse_args()
    rows = frame()
    picked = draw(rows, a.n, a.seed)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, 'sample.json'), 'w', encoding='utf-8') as fh:
        json.dump(dict(seed=a.seed, frame=len(rows), picked=picked), fh,
                  ensure_ascii=False, indent=1)
    made = sheets(picked, a.out)
    st = collections.Counter((r['band'], r['source']) for r in picked)
    print(f'khung {len(rows)} hình · mẫu {len(picked)} · {len(made)} bảng ảnh')
    for k in sorted(st):
        print(f'   {k[0]:>5} {k[1]:>8} {st[k]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
