#!/usr/bin/env python3
"""TOC HEALTH — chấm sức khoẻ mục lục của TỪNG cuốn trong corpus.

Vì sao cần: Living Research C-006/C-007/C-008 cho thấy ba triệu chứng khác nhau
(Tiếng Anh mất trang · finding SGV gán sai bài · hoạt động không gắn được vào
bài) đều là MỘT nguyên nhân: quy trình nạp gán sai đơn vị bài. Muốn sửa thì
phải biết CUỐN NÀO hỏng và hỏng KIỂU GÌ — không sửa mò từng cuốn.

Đây là chặng «automated validation» của nhà máy: chạy trên toàn corpus, phân
loại, rồi mới nhắm việc sửa. KHÔNG sửa dữ liệu, chỉ chấm.

Chạy:  python3 tool/corpus/toc_health.py            # bảng tổng hợp
       python3 tool/corpus/toc_health.py --json     # ra JSON để so theo thời gian
       python3 tool/corpus/toc_health.py --doc 05-sgk-khoa-hoc-5
"""
import json
import sys
from collections import Counter

STRUCT = 'poc-out/graph/curriculum-structure.json'
REGISTRY = 'poc-out/registry/source-registry.json'

# Bài trải quá ngần này trang thì chắc chắn là THÙNG CHỨA GOM, không phải bài.
SPREAD_LIMIT = 40


def longest_monotonic_chain(pairs):
    """Chuỗi dài nhất mà số bài tăng ⇒ trang tăng — «xương sống» tự nhất quán.

    Đây là phần mục lục còn tin được của một cuốn, kể cả khi phần còn lại loạn.
    """
    if not pairs:
        return []
    pairs = sorted(pairs)  # theo số bài
    best = []
    # LIS theo trang (n nhỏ, O(n^2) là đủ)
    tails = [[p] for p in pairs]
    for i in range(len(pairs)):
        for j in range(i):
            if pairs[j][1] <= pairs[i][1] and len(tails[j]) + 1 > len(tails[i]):
                tails[i] = tails[j] + [pairs[i]]
        if len(tails[i]) > len(best):
            best = tails[i]
    return best


def classify(doc, page_count):
    lessons = doc.get('lessons', [])
    numbered = [(l['number'], l['pageStart']) for l in lessons
                if l.get('number') is not None and l.get('pageStart') is not None]
    n_total = len(lessons)
    n_paged = len(numbered)

    flags = []
    if n_total == 0:
        return ['NO_TOC'], {}

    if n_paged == 0:
        flags.append('NO_PAGES')

    nums = [n for n, _ in numbered]
    dups = len(nums) - len(set(nums))
    if dups:
        flags.append('DUP_NUMBERS')

    chain = longest_monotonic_chain(numbered)
    # Xương sống phủ được bao nhiêu phần mục lục?
    spine = len(chain) / n_paged if n_paged else 0.0
    if n_paged and spine < 0.8:
        flags.append('NON_MONOTONIC')

    # Mục lục phủ được bao nhiêu phần CUỐN SÁCH? Bài đầu tiên bắt đầu ở đâu?
    coverage = head_gap = None
    if chain and page_count:
        lo, hi = chain[0][1], chain[-1][1]
        coverage = (hi - lo) / page_count
        head_gap = lo / page_count
        if coverage < 0.4:
            flags.append('PARTIAL_COVERAGE')
        # Mục lục bắt đầu quá muộn ⇒ nửa đầu sách KHÔNG bài nào phủ ⇒ hoạt động
        # ở nửa đầu không thể gắn vào bài nào (đúng ca Khoa học 5, C-008).
        if head_gap > 0.25:
            flags.append('HEAD_UNCOVERED')

    return (flags or ['OK']), {
        'lessons': n_total,
        'paged': n_paged,
        'dupNumbers': dups,
        'spineRatio': round(spine, 2),
        'coverage': None if coverage is None else round(coverage, 2),
        'headGap': None if head_gap is None else round(head_gap, 2),
        'pageCount': page_count,
    }


def main():
    docs = json.load(open(STRUCT))['documents']
    pages = {d['sourceDocumentId']: d.get('pageCount')
             for d in json.load(open(REGISTRY))['documents']}

    only = None
    if '--doc' in sys.argv:
        only = sys.argv[sys.argv.index('--doc') + 1]

    rows = []
    for d in docs:
        sid = d['sourceDocumentId']
        if only and sid != only:
            continue
        flags, m = classify(d, pages.get(sid))
        rows.append({'sourceDocumentId': sid, 'grade': d.get('grade'),
                     'subject': d.get('subject'), 'docType': d.get('docType'),
                     'structureStatus': d.get('structureStatus'),
                     'flags': flags, **m})

    if '--json' in sys.argv:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=1)
        return

    tally = Counter(f for r in rows for f in r['flags'])
    print(f'{len(rows)} tài liệu\n')
    print('phân loại (một cuốn có thể mang nhiều cờ):')
    for f, c in tally.most_common():
        print(f'  {f:18s} {c:4d}  ({c * 100 // len(rows)}%)')

    healthy = [r for r in rows if r['flags'] == ['OK']]
    print(f'\nMỤC LỤC DÙNG ĐƯỢC NGAY: {len(healthy)}/{len(rows)} '
          f'({len(healthy) * 100 // len(rows)}%)')

    if only or '--verbose' in sys.argv:
        print()
        for r in rows:
            print(f"{r['sourceDocumentId']:46s} {','.join(r['flags']):34s} "
                  f"bài={r.get('lessons')} cóTrang={r.get('paged')} "
                  f"trùng={r.get('dupNumbers')} xươngSống={r.get('spineRatio')} "
                  f"phủ={r.get('coverage')} hởĐầu={r.get('headGap')}")


if __name__ == '__main__':
    main()
