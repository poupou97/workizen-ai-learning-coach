#!/usr/bin/env python3
"""WAL-116 — CLASSIFY «vẽ» từ corpus THẬT (rule minh bạch, không LLM tự phán).

Mỗi unit chứa lệnh «vẽ» được gán ĐÚNG MỘT loại theo bộ rule keyword ưu tiên
(rule đầu khớp thắng — in ra để kiểm). UNKNOWN giữ nguyên UNKNOWN (§acceptance).
Distribution 3 chiều: grade × subject × loại.
"""
import json, glob, re, collections

# (loại, regex — ưu tiên theo thứ tự khai báo)
RULES = [
    ('CHART',      r'vẽ\s+(biểu\s*đồ)'),
    ('GRAPH',      r'vẽ\s+(đồ\s*thị)'),
    # «đoạn thắng» = OCR-variant thật của «đoạn thẳng» (đo trong corpus).
    ('GEOMETRY',   r'vẽ\s+(hình|tam giác|đường tròn|đường thẳng|đoạn th[ắẳ]ng|góc|tia|nửa đường tròn|hình chữ nhật|hình vuông|elip|parabol)'),
    ('DIAGRAM',    r'vẽ\s+(sơ\s*đồ|mạch|mô hình|cấu trúc)'),
    ('MAP_SKETCH', r'vẽ\s+(lược\s*đồ|bản\s*đồ)'),
    ('TECHNICAL',  r'(bản\s*vẽ|vẽ\s*kĩ\s*thuật|vẽ\s*kỹ\s*thuật|CAD|hình chiếu)'),
    ('VECTOR',     r'vẽ\s+(vect|véc|lực|từ trường|đường sức)'),
    ('SCIENCE_FIG',r'vẽ\s+(tế bào|cơ quan|vòng đời|chu trình|thí nghiệm)'),
    ('ARTISTIC',   r'vẽ\s+(tranh|con vật|người thân|phong cảnh|trang trí|theo ý thích|bức|chân dung|màu|lớp học|hoặc cắt dán|.{0,24}của em)'),
    ('ANNOTATE',   r'(đánh dấu|khoanh|tô màu|nối|gạch chân)'),
]

def classify(text):
    low = text.lower()
    for name, pat in RULES:
        if re.search(pat, low):
            return name
    return 'UNKNOWN'

# v2: chỉ nhận unit mà «vẽ» là LỆNH (đầu câu lệnh / «hãy vẽ» / «vẽ ... vào»),
# không phải nhắc-tới-vẽ giữa văn bản (nguồn 41.6% UNKNOWN của v1 — đo được).
VE = re.compile(
    r'(^|\n|\.\s|\d\.\s|[a-d]\)\s)(em\s+hãy\s+|hãy\s+)?vẽ\b'
    r'|bản\s*vẽ|vẽ\s*kĩ\s*thuật', re.I)
dist = collections.Counter()
by_gsc = collections.Counter()
samples = collections.defaultdict(list)
total = 0
for f in sorted(glob.glob('poc-out/units-k12/*sgk*.json')):  # SGK — lệnh cho HS
    d = json.load(open(f))
    grade = int(f.split('/')[-1][:2])
    subj = d.get('subject') or '?'
    for u in d.get('units', []):
        t = u.get('text', '')
        if not VE.search(t):
            continue
        total += 1
        k = classify(t)
        dist[k] += 1
        by_gsc[(grade, subj, k)] += 1
        if len(samples[k]) < 2:
            samples[k].append(t[:90])

print(f'TOTAL unit SGK chứa «vẽ»: {total}')
print('\n=== DISTRIBUTION theo loại ===')
for k, n in dist.most_common():
    print(f'{k:12s} {n:5d}  ({n/total*100:4.1f}%)')
print('\n=== TOP (grade, subject, loại) ===')
for (g, s, k), n in by_gsc.most_common(18):
    print(f'  lớp {g:2d} · {s:12s} · {k:12s} {n:4d}')
print('\n=== BAND 10-12 theo loại ===')
band = collections.Counter()
for (g, s, k), n in by_gsc.items():
    if g >= 10:
        band[k] += n
for k, n in band.most_common():
    print(f'{k:12s} {n:5d}')
print('\n=== SAMPLES mỗi loại (kiểm mắt rule) ===')
for k in list(dist):
    for s in samples[k]:
        print(f'[{k}] {s}')
