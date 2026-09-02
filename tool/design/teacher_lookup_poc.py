#!/usr/bin/env python3
"""WAL-120 — POC MỎNG: teacher lookup «objective + method» cho MỘT bài thật.
Đầu vào: (lớp, bài). Đầu ra: TEACHER BRIEF tất định từ data SGV/SGK đã mined
(569 objectives sourceStated + method-catalogue 29 quy tắc có trang).
KHÔNG LMS, KHÔNG học sinh thật — chỉ chứng minh «chạy được ngay từ SGV data»."""
import json, sys

GRADE = int(sys.argv[1]) if len(sys.argv) > 1 else 5
LESSON = int(sys.argv[2]) if len(sys.argv) > 2 else 6

objs = json.load(open(f'poc-out/units/0{GRADE}-sgv-toan-{GRADE}.objectives.json'))
cat = json.load(open('poc-out/units/method-catalogue.json'))
methods = cat if isinstance(cat, list) else cat.get('methods', [])

my_objs = [o for o in objs if o.get('lesson') == LESSON]
my_methods = [m for m in methods
              if m.get('grade') == GRADE and m.get('lesson') == LESSON]

print(f'=== TEACHER BRIEF · Toán {GRADE} · Bài {LESSON} (tất định, có nguồn) ===')
print(f'\nMỤC TIÊU (SGV nói thẳng — {len(my_objs)} mục):')
for o in my_objs:
    print(f'  [{o["kind"]}] {o["text"]}')
    print(f'      nguồn: {o["book"]} · trang PDF {o["pagePdf"]} · {o["origin"]}')
print(f'\nQUY TẮC/METHOD in trong SGK ({len(my_methods)}):')
for m in my_methods:
    print(f'  «{m["textHead"][:80]}…»')
    print(f'      nguồn: {m["book"]} · Bài {m["lesson"]} · trang in {m["pagePrinted"]}')
if not my_objs and not my_methods:
    print('KHÔNG có dữ liệu cho bài này — nói thật, không bịa (fail closed).')
