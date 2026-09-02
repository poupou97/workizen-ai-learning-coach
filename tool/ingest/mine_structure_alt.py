"""K-12 §VI — structural adapter cho sách KHÔNG dùng «Bài N» trong TOC.

165 sách NO_TOC phần lớn dùng đơn vị khác: «CHỦ ĐỀ N» (âm nhạc, mĩ thuật,
HĐTN, GDCD...), «Unit N» (tiếng Anh), «BÀI N» in hoa. Mine header từ OCR
body (y<0.25, nửa trên trang) → ghi structure thay thế vào
curriculum-structure.json với unitKind ghi rõ (chuDe/unit/bai) — KHÔNG
đổi nghĩa Lesson==Period (§XVI). Idempotent; chỉ đụng doc NO_TOC.
"""
import json, os, re

PATTERNS = [
    (re.compile(r'^CH[ỦU]\s*Đ[ỀE]\s+(\d+)\b', re.I), 'chuDe'),
    (re.compile(r'^Unit\s+(\d+)\b', re.I), 'unit'),
    (re.compile(r'^B[ÀA][IÌ]\s+(\d+)\b'), 'bai'),
    (re.compile(r'^Bài\s+(\d+)\b'), 'bai'),
    (re.compile(r'^TU[ẦA]N\s+(\d+)\b', re.I), 'tuan'),
]

struct = json.load(open('poc-out/graph/curriculum-structure.json'))
changed = 0
for d in struct['documents']:
    if d['structureStatus'] != 'NO_TOC':
        continue
    ocr = f"poc-out/graph/ocr-body/{d['sourceDocumentId']}"
    if not os.path.isdir(ocr):
        continue
    found = {}   # (kind, n) -> first pdf page
    for f in sorted(os.listdir(ocr)):
        try:
            j = json.load(open(f'{ocr}/{f}'))
        except Exception:
            continue
        for l in j['lines'][:8]:
            if l['y'] > 0.3:
                continue
            t = l['text'].strip()
            for pat, kind in PATTERNS:
                m = pat.match(t)
                if m:
                    key = (kind, int(m.group(1)))
                    found.setdefault(key, j['pdf_page'])
    if not found:
        continue
    # chọn kind phổ biến nhất — sách dùng MỘT hệ đơn vị chính
    from collections import Counter
    kind = Counter(k for k, _ in found).most_common(1)[0][0]
    lessons = sorted([{'number': n, 'title': None, 'pageStart': p,
                       'unitKind': kind, 'pageIsPdf': True}
                      for (k, n), p in found.items() if k == kind],
                     key=lambda x: x['number'])
    # loại nhiễu: số đơn vị phải hợp lý và tăng dần theo trang
    if len(lessons) < 3:
        continue
    d['lessons'] = lessons
    d['lessonCount'] = len(lessons)
    d['structureStatus'] = f'OK_ALT_{kind}'
    changed += 1

json.dump(struct, open('poc-out/graph/curriculum-structure.json', 'w'),
          ensure_ascii=False, indent=1)
from collections import Counter
print(f'structural-alt: {changed} sách NO_TOC → có cấu trúc')
print(Counter(d['structureStatus'] for d in struct['documents']))
