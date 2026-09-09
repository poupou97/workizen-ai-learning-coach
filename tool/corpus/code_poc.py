#!/usr/bin/env python3
"""WAL-239 — POC (KHÔNG canonical): hình học trang có dựng lại được CẤU TRÚC mã?

    python3 tool/corpus/code_poc.py --seed 20260922

⛔ RANH GIỚI TUYỆT ĐỐI, Founder chốt:

    HÌNH HỌC ĐƯỢC PHÉP DỰNG LẠI CẤU TRÚC.
    HÌNH HỌC KHÔNG ĐƯỢC PHÉP BỊA RA NỘI DUNG.

Nếu bước trích nguồn đã mất token / dòng / toán tử / định danh / dấu nháy / số,
thì KHÔNG được dựng lại chúng bằng hiểu biết về ngôn ngữ lập trình. Không LLM,
không đoán cú pháp, không sửa thầm.

Ở đây chỉ dùng đúng ba thứ đo được từ trang in:

    y của mỗi dòng OCR  →  RANH GIỚI DÒNG và THỨ TỰ DÒNG
    x của mỗi dòng OCR  →  MỨC THỤT LỀ
    chính chuỗi ký tự   →  NỘI DUNG (giữ nguyên, không đụng)

⭐ VỚI PYTHON, THỤT LỀ LÀ NGỮ NGHĨA. Một chương trình bị bẹp thành một dòng
KHÔNG phải là «mất định dạng» — nó là một chương trình KHÁC. Vì vậy mất thụt lề
được xếp vào hại, không xếp vào trình bày.

Module này KHÔNG đổi pack. Nó chỉ dựng bằng chứng cho quyết định kiến trúc.
"""
import argparse
import collections
import json
import glob
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from subject import subject  # noqa: E402

OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')

#: Dấu vết mã nguồn IN TRONG SÁCH. Danh sách đóng, dùng để CHỌN MẪU, không
#: dùng để kết luận về nội dung.
PY_MARK = re.compile(r'>>>|\bdef\s|\bprint\(|\bimport\s|\bfor\s.+\sin\s|\bwhile\s|'
                     r'\bif\s.+:|\bint\(|\brange\(|\breturn\b|\blen\(')

#: Họ ký hiệu để phân tầng mẫu đối kháng — nhận bằng CHÍNH chữ in.
FEATURES = (
    ('repl', re.compile(r'>>>|›››')),
    ('ham_nhieu_dong', re.compile(r'\bdef\s')),
    ('long_nhau', re.compile(r':\s*$', re.M)),
    ('if_else', re.compile(r'\belse\b|\belif\b')),
    ('vong_lap', re.compile(r'\bfor\b|\bwhile\b')),
    ('goi_ham', re.compile(r'\w+\(')),
    ('chuoi', re.compile(r'"[^"]*"|\'[^\']*\'')),
    ('toan_tu', re.compile(r'[=+\-*/%<>]=?|\*\*|//')),
    ('ngoac', re.compile(r'[\[\]{}()]')),
    ('so', re.compile(r'\b\d+\b')),
)


def features(text):
    got = [n for n, rx in FEATURES if rx.search(text or '')]
    return got or ['khong_ro']


def _inside(line, box):
    """Dòng OCR có nằm trong vùng không — dùng tâm dòng, đơn giản và đủ."""
    cx = line['x'] + (line.get('w') or 0) / 2
    cy = line['y'] + (line.get('h') or 0) / 2
    return (box[0] <= cx <= box[0] + box[2]) and (box[1] <= cy <= box[1] + box[3])


def reconstruct(lines, box, tol=0.004):
    """Dựng lại DÒNG · THỨ TỰ · THỤT LỀ từ hình học. KHÔNG chạm nội dung.

    Trả `(các dòng, chú thích)`. Mỗi dòng: `{'indent': n, 'text': ...}` với
    `indent` là BẬC thụt lề đếm từ mốc x nhỏ nhất, KHÔNG phải số dấu cách đoán
    ra: các mốc x được gom cụm rồi đánh số theo thứ tự.
    """
    inside = [l for l in lines if _inside(l, box) and (l.get('text') or '').strip()]
    if not inside:
        return [], 'KHONG_CO_DONG_NAO'
    inside.sort(key=lambda l: (round(l['y'], 4), l['x']))
    # Gom dòng theo y: hai mẩu chữ cùng một dòng in thì y gần nhau.
    rows, cur = [], [inside[0]]
    for l in inside[1:]:
        if abs(l['y'] - cur[-1]['y']) <= tol:
            cur.append(l)
        else:
            rows.append(cur)
            cur = [l]
    rows.append(cur)
    # ⭐ CỘT SỐ DÒNG XOÁ MẤT TÍN HIỆU THỤT LỀ. Sách in số dòng ở lề trái, nên
    # `min(x)` của mọi dòng đều bằng nhau và mọi dòng ra bậc 0 — đo được ở
    # Tin học 11 tr.89: cả chương trình 10 dòng ra một bậc. Nhận cột ấy bằng
    # HÌNH HỌC + hình dạng: mọi dòng mở đầu bằng MỘT SỐ NGUYÊN TRẦN tại cùng
    # một mốc x. Nhận ra thì bỏ số dòng khỏi phép tính thụt lề — vẫn giữ
    # nguyên trong nội dung, không xoá chữ của sách.
    def _gutter(rows):
        firsts = [sorted(r, key=lambda l: l['x'])[0] for r in rows]
        if len(firsts) < 3:
            return False
        if not all(re.fullmatch(r'\d{1,3}', (l.get('text') or '').strip())
                   for l in firsts):
            return False
        xs = [l['x'] for l in firsts]
        return max(xs) - min(xs) <= tol * 2

    gut = _gutter(rows)
    if gut:
        rows = [sorted(r, key=lambda l: l['x'])[1:] or r for r in rows]
        rows = [r for r in rows if r]

    # Mốc thụt lề = các giá trị x đầu dòng, gom cụm theo `tol`.
    starts = sorted(min(l['x'] for l in r) for r in rows)
    stops = []
    for x in starts:
        if not stops or x - stops[-1] > tol * 2:
            stops.append(x)
    out = []
    for r in rows:
        x0 = min(l['x'] for l in r)
        lvl = max(i for i, s in enumerate(stops) if x0 >= s - tol)
        txt = ' '.join((l.get('text') or '').strip()
                       for l in sorted(r, key=lambda l: l['x'])).strip()
        out.append(dict(indent=lvl, text=txt))
    return out, ('OK_BO_COT_SO_DONG' if gut else 'OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=20)
    ap.add_argument('--seed', type=int, default=20260922)
    ap.add_argument('--out', default=os.path.join(ROOT, 'poc-out', 'code-poc'))
    a = ap.parse_args()

    regions = []
    for p in glob.glob(os.path.join(ROOT, 'poc-out/docling/proposals-w*.jsonl')):
        with open(p, encoding='utf-8') as fh:
            for line in fh:
                r = json.loads(line)
                for it in r.get('items') or []:
                    if it.get('label') != 'code':
                        continue
                    t = ' '.join((it.get('text') or '').split())
                    if not PY_MARK.search(t):
                        continue
                    x0, y0, x1, y1 = it['box']
                    regions.append(dict(book=r['book'], page=r['page'],
                                        box=[x0, y0, x1 - x0, y1 - y0],
                                        printed=t, subject=subject(r['book']),
                                        fam=features(t)))
    rng = random.Random(a.seed)
    st = collections.defaultdict(list)
    for i, r in enumerate(regions):
        st[r['fam'][0]].append(dict(r, _i=i))
    picked, cap = [], collections.Counter()
    for k in sorted(st):
        bag = st[k][:]
        rng.shuffle(bag)
        got = 0
        for r in bag:
            if got >= max(2, a.n // max(len(st), 1)) or cap[r['book']] >= 4:
                continue
            cap[r['book']] += 1
            picked.append(r)
            got += 1
    rng.shuffle(picked)
    picked = picked[:a.n]

    os.makedirs(a.out, exist_ok=True)
    # ĐÓNG BĂNG TRƯỚC KHI SOI: ghi mẫu xong mới chạy dựng lại.
    with open(os.path.join(a.out, 'sample.json'), 'w', encoding='utf-8') as fh:
        json.dump(dict(seed=a.seed, frame=len(regions), picked=picked), fh,
                  ensure_ascii=False, indent=1)

    out = []
    for r in picked:
        try:
            with open(f"{OCR}/{r['book']}/p{r['page']:03d}.json", encoding='utf-8') as fh:
                lines = json.load(fh)['lines']
        except (OSError, ValueError, KeyError):
            lines = []
        rec, why = reconstruct(lines, r['box'])
        out.append(dict(r, recon=rec, recon_why=why))
    with open(os.path.join(a.out, 'reconstructed.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f'khung {len(regions)} vùng mã nguồn · mẫu {len(picked)} · '
          f'{len({r["book"] for r in picked})} sách → {a.out}')
    for k, v in collections.Counter(r['fam'][0] for r in picked).most_common():
        print(f'   {k:16s} {v}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
