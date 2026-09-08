#!/usr/bin/env python3
"""B3 — CHỈ PROMOTE LỚP ĐÃ TRI GIÁC XONG HOÀN TOÀN.

    python3 tool/corpus/docling_promote.py --pages b3-pages.json          # xem
    python3 tool/corpus/docling_promote.py --pages b3-pages.json --build   # dựng

⭐ LUẬT AN TOÀN CỦA FOUNDER, ĐƯỢC MÃ HOÁ CHỨ KHÔNG ĐỂ TÙY PHÁN ĐOÁN:

    KHÔNG promote corpus/pack MỘT PHẦN chỉ vì hết thời gian.

Một lớp chỉ được dựng lại khi MỌI TRANG của MỌI CUỐN thuộc lớp ấy đã có đề xuất
trong khu tạm. Thiếu một trang thì cả lớp giữ nguyên bản cũ đang tốt — vì pack
dựng dở đọc ra vẫn «hợp lệ»: đủ bài, đủ bìa, không lỗi nào, chỉ thiếu hình mà
không ai biết là thiếu.

Đây chính là bài học lớp 3 tụt 232 → 44 bài mà cả ba bất biến đều ĐẠT.
"""
import argparse
import collections
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DL = os.path.join(ROOT, 'poc-out', 'docling')


def perceived(out_dir=DL):
    """`{sách: {trang, ...}}` — trang đã có đề xuất trong khu tạm."""
    done = collections.defaultdict(set)
    for fn in glob.glob(os.path.join(out_dir, 'proposals-w*.jsonl')):
        with open(fn, encoding='utf-8') as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue                  # dòng cụt do sập giữa chừng
                done[d['book']].add(d['page'])
    return done


def coverage(wanted, done, grade_of):
    """`{lớp: (trang đã xong, trang cần, đủ hay chưa)}`."""
    need = collections.defaultdict(set)
    for book, page in wanted:
        need[book].add(page)
    per = collections.defaultdict(lambda: [0, 0, True])
    for book, pages in need.items():
        g = grade_of.get(book, 0)
        got = pages & done.get(book, set())
        per[g][0] += len(got)
        per[g][1] += len(pages)
        if got != pages:
            per[g][2] = False
    return {g: tuple(v) for g, v in sorted(per.items())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pages', required=True)
    ap.add_argument('--build', action='store_true')
    ap.add_argument('--attach', default=None)
    a = ap.parse_args()

    with open(a.pages, encoding='utf-8') as fh:
        wanted = [(b, int(p)) for b, p in json.load(fh)]
    reg = json.load(open(os.path.join(ROOT, 'poc-out', 'registry',
                                      'source-registry.json'), encoding='utf-8'))
    docs = reg['documents'] if isinstance(reg, dict) else reg
    grade_of = {d['sourceDocumentId']: d.get('grade') or 0 for d in docs}

    cov = coverage(wanted, perceived(), grade_of)
    ready = [g for g, (_, _, ok) in cov.items() if ok]
    for g, (got, need, ok) in cov.items():
        print(f'  lớp {g:>2}: {got:>5}/{need:<5} ' +
              ('✅ ĐỦ — được dựng lại' if ok else '⏸ CHƯA ĐỦ — giữ nguyên pack cũ'))
    print(f'\nlớp được promote: {ready or "(chưa lớp nào)"}')
    if not a.build:
        return 0
    for g in ready:
        cmd = [sys.executable, os.path.join(ROOT, 'tool', 'ui', 'build_lesson_figures.py'),
               str(g)]
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode != 0:
            print(f'lớp {g}: dựng THẤT BẠI — dừng, không promote tiếp', file=sys.stderr)
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
