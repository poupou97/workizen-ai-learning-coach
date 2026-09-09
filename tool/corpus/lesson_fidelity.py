#!/usr/bin/env python3
"""WAL-238 — TRUNG THỰC ĐA PHƯƠNG THỨC ĐO THEO **BÀI**, KHÔNG THEO ẢNH.

    python3 tool/corpus/lesson_fidelity.py --n 20 --seed 20260909

⭐ MỘT BÀI KHÔNG TRUNG THỰC CHỈ VÌ MỘT ẢNH ĐÚNG. `FIGURE_CROP_VALID` = 70,8% là
tỉ lệ THEO ẢNH; muốn nói về bài thì phải soi MỌI ảnh trẻ thấy trong bài ấy, và
phải hỏi thêm một câu mà phép đo theo ảnh không hỏi được:

    SÁCH IN «Hình N» MÀ BÀI KHÔNG CÓ ẢNH NÀO ⇒ THIẾU HÌNH BẮT BUỘC.

Đó là bằng chứng in trong sách, không phải phán đoán: chú thích đánh số chứng
minh trang ấy CÓ hình, dù bộ dò có thấy hay không.

Hạng của bài (ghi bằng mắt, không suy từ cổng):

    MULTIMODAL_FAITHFUL   mọi hình bắt buộc đều có, mọi ảnh đều sạch
    PARTIAL               có ảnh đúng, nhưng thiếu hoặc hỏng một phần
    UNFAITHFUL            phần lớn hình sai/thiếu, hoặc có ảnh gây hiểu sai
    NO_REQUIRED_VISUAL    sách không in hình nào cho bài này ⇒ không có gì để sai
    AMBIGUOUS             không đủ căn cứ để xếp
"""
import argparse
import collections
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
PACK = os.path.join(ROOT, 'assets', 'pack')

GRADES = ('MULTIMODAL_FAITHFUL', 'PARTIAL', 'UNFAITHFUL', 'NO_REQUIRED_VISUAL',
          'AMBIGUOUS')

# Nguyên nhân gốc, ghi cho MỌI bài PARTIAL/UNFAITHFUL. Một bài có thể mang
# nhiều họ. `TABLE_DUPLICATION` chỉ đo được sau #167.
CAUSES = ('NOT_A_LEARNING_VISUAL', 'PROSE_CONTAMINATED', 'TRUNCATED',
          'NEIGHBOR_VISUAL_INCLUDED', 'MISSING_REQUIRED_VISUAL',
          'FRAGMENTED_VISUAL', 'IDENTITY_ERROR', 'ORDER_ERROR',
          'TABLE_DUPLICATION', 'OTHER')


def band(g):
    """Bốn dải lớp theo cấp học, không phải ba — Founder chốt ở vòng này."""
    return ('1-3' if g <= 3 else '4-6' if g <= 6 else '7-9' if g <= 9 else '10-12')


def density(n):
    return 'nhiều ảnh' if n >= 6 else ('ít ảnh' if n >= 1 else 'không ảnh')


def src_mix(imgs):
    """Bài này do đường nào cấp hình — để đo lỗi đến từ đâu."""
    s = {i['src'] for i in imgs}
    if not s:
        return 'không ảnh'
    if s == {'docling'}:
        return 'chỉ Docling'
    if s == {'D'}:
        return 'chỉ D'
    return 'cả hai'


def required_visuals(book, pages):
    """Chú thích ĐÁNH SỐ sách in trên các trang của bài — hình BẮT BUỘC phải có.

    Dùng CẢ họ đánh số một cấp («Hình 2»), vì ở đây câu hỏi là «SÁCH ĐÒI HỎI
    hình nào», cần ĐỘ PHỦ của bằng chứng in. Mẫu hai cấp một mình bỏ lọt gần
    hết: trên 21 bài lấy thử, nó chỉ tìm thấy chú thích ở 2 bài.

    Vẫn KHÔNG dùng họ «dấu nguồn» — corpus đã bác bỏ nó (7/7 sai).
    """
    from lesson_reading import page_lines
    import figure_funnel as ff
    out = []
    for p in pages:
        ls = page_lines(book, p) or []
        bl = ff.block_line_counts(ls)
        for a in ff.caption_anchors(ls, extended=True, block_lines=bl):
            out.append(dict(page=p, kind=a['kind'], num=a['num'], text=a['text']))
    return out


def lessons(pack_dir=PACK):
    rows = []
    for g in range(1, 13):
        p = os.path.join(pack_dir, f'lesson-index-g{g}.json')
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8') as fh:
            d = json.load(fh)
        for r in d.get('lessonReadings') or []:
            imgs = [i for i in (r.get('content') or []) if i.get('t') == 'img']
            rows.append(dict(grade=g, band=band(g), book=r.get('book'),
                             lesson=r.get('lesson'), title=r.get('title'),
                             p0=r.get('pagePdfStart'), p1=r.get('pagePdfEnd'),
                             images=[dict(id=i.get('id'), page=i.get('page'),
                                          caption=i.get('caption'),
                                          src='docling' if ':dl' in (i.get('id') or '')
                                              else 'D')
                                     for i in imgs]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=20)
    ap.add_argument('--seed', type=int, default=20260909)
    ap.add_argument('--out', default=os.path.join(ROOT, 'poc-out', 'lesson-fidelity'))
    a = ap.parse_args()
    rows = lessons()
    for r in rows:
        r['density'] = density(len(r['images']))
        r['mix'] = src_mix(r['images'])
    # ⭐ NGẪU NHIÊN TRONG TỪNG TẦNG, KHÔNG CHỌN BÀI VÌ NÓ TRÔNG CÓ VẤN ĐỀ.
    # Tầng = (dải lớp × nguồn cấp hình). Mật độ ảnh và môn được báo cáo lại như
    # thuộc tính của mẫu, không dùng làm tầng nữa — chia quá nhỏ thì mỗi tầng
    # chỉ còn một hai bài và mẫu hết ngẫu nhiên.
    rng = random.Random(a.seed)
    by = collections.defaultdict(list)
    for r in rows:
        by[(r['band'], r['mix'])].append(r)
    keys = sorted(by)
    picked, quota = [], {}
    tot = sum(len(by[k]) for k in keys)
    for k in keys:
        quota[k] = max(1, round(a.n * len(by[k]) / tot))
    while sum(quota.values()) > a.n:
        k = max(keys, key=lambda k: quota[k])
        if quota[k] <= 1:
            break
        quota[k] -= 1
    for k in keys:
        picked += rng.sample(by[k], min(quota[k], len(by[k])))
    for r in picked:
        r['required'] = required_visuals(r['book'], range(r['p0'], r['p1'] + 1))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, 'lessons.json'), 'w', encoding='utf-8') as fh:
        json.dump(dict(seed=a.seed, frame=len(rows), picked=picked), fh,
                  ensure_ascii=False, indent=1)
    print(f'khung {len(rows)} bài · mẫu {len(picked)}')
    for r in picked:
        print(f"  g{r['grade']:>2} {r['book'][:30]:30} Bài {r['lesson']:>3} · "
              f"ảnh {len(r['images']):>2} · «Hình N» sách in {len(r['required']):>2}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
