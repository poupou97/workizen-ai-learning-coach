#!/usr/bin/env python3
"""WAL — MẪU ĐÓNG BĂNG cho luật nhận DANH TÍNH chú thích.

    python3 tool/corpus/caption_probe.py --n 80 --seed 20260911

⛔ ĐÓNG BĂNG TRƯỚC KHI SOI. Tệp mẫu được ghi xong rồi mới đo đặc trưng. Luật
phải được nghĩ ra từ mẫu ĐÃ dán nhãn, không phải nặn cho vừa số.

Mục tiêu KHÔNG phải «lấy được nhiều chú thích hơn». Mục tiêu là DANH TÍNH:

    VẬT THỂ NGUỒN  ↔  CHÚ THÍCH IN  ↔  HÌNH TỚI TAY TRẺ

đủ bằng chứng để nói ba thứ ấy là CÙNG MỘT vật. `SAI TÊN > THIẾU TÊN`.
"""
import argparse
import collections
import glob
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import figure_funnel                      # noqa: E402
from subject import subject               # noqa: E402

OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')


def candidates():
    """Mọi dòng khớp mẫu chú thích ĐÁNH SỐ, kèm chỗ đứng của nó."""
    out = []
    for p in sorted(glob.glob(os.path.join(OCR, '*/p*.json'))):
        bk = p.split('/')[-2]
        pg = int(os.path.basename(p)[1:4])
        try:
            lines = json.load(open(p, encoding='utf-8'))['lines']
        except (OSError, ValueError, KeyError):
            continue
        bl = figure_funnel.block_line_counts(lines)
        for i, l in enumerate(lines):
            t = (l.get('text') or '').strip()
            if not figure_funnel.CAPTION_NUM_ANY.match(t):
                continue
            two = bool(figure_funnel.CAPTION_NUM.match(t))
            n = bl.get(id(l)) or 1
            out.append(dict(book=bk, page=pg, text=t, subject=subject(bk),
                            block_lines=n, two_level=two,
                            nhan_hien_tai=bool(two or n <= 2),
                            x=round(l['x'], 4), y=round(l['y'], 4),
                            w=round(l.get('w') or 0, 4), h=round(l.get('h') or 0, 4)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=80)
    ap.add_argument('--seed', type=int, default=20260911)
    ap.add_argument('--out', default=os.path.join(ROOT, 'poc-out', 'caption-probe'))
    a = ap.parse_args()
    cs = candidates()
    bad = [c for c in cs if not c['nhan_hien_tai']]
    good = [c for c in cs if c['nhan_hien_tai']]
    rng = random.Random(a.seed)
    rng.shuffle(bad); rng.shuffle(good)
    # 3/4 lấy từ nhóm ĐANG BỊ LOẠI — đó là nơi luật phải phân biệt được.
    k = a.n * 3 // 4
    pick = bad[:k] + good[:a.n - k]
    rng.shuffle(pick)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, 'sample.json'), 'w', encoding='utf-8') as fh:
        json.dump(dict(seed=a.seed, khung=len(cs), dang_bi_loai=len(bad),
                       picked=pick), fh, ensure_ascii=False, indent=1)
    print(f'khung {len(cs)} ứng viên · đang bị loại {len(bad)} · mẫu {len(pick)}')
    for k2, v in collections.Counter(c['subject'] for c in pick).most_common():
        print(f'   {k2:12s} {v}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
