#!/usr/bin/env python3
"""WAL-117 — EN semantic adapter v1: classify unit Tiếng Anh theo 9 loại
bằng MARKER SET minh bạch (rule đầu khớp thắng; marker phải ở VỊ TRÍ LỆNH —
đầu dòng / sau số thứ tự — như offset-calibration của extractor generic).
UNKNOWN→OTHER giữ nguyên, không ép. In marker-frequency để kiểm mắt.
"""
import json, glob, re, collections

# (loại, marker regex — vị trí lệnh)
# v2 — ĐO ĐƯỢC từ v1: trang EN nhiều cột bị OCR trộn dòng ⇒ marker nằm GIỮA
# text (97.7% OTHER ở v1 là artefact trộn cột, KHÔNG phải thiếu marker).
# Hai tầng: (1) SECTION HEADER của Global Success (cấu trúc sách thật);
# (2) marker-contains theo ưu tiên. Ghi rõ limitation: contains-match có thể
# dính marker của hoạt động bên cạnh trên cùng trang — chấp nhận, in samples.
SECTIONS = [
    ('PRONUNCIATION', r"pronunciation"),
    ('LISTENING',     r"listening|getting started"),
    ('SPEAKING',      r"speaking|communication"),
    ('READING',       r"reading|a closer look 1"),
    ('WRITING',       r"writing|a closer look 2"),
    ('INTERACTION',   r"project|looking back|game"),
]
RULES = [
    ('LISTENING',     r"listen( and (repeat|tick|number|point|circle|match|write|complete|check))?\b|let's listen"),
    ('PRONUNCIATION', r"let's (sing|chant)|sing\b|chant\b|say the sounds?|practise saying|repeat\b"),
    ('SPEAKING',      r"let's talk|point and say|ask and answer|role[- ]?play|interview|make a (conversation|dialogue)|discuss\b"),
    ('INTERACTION',   r"let's play|work in (pairs|groups)|play the game|survey\b|extension activit"),
    ('VOCABULARY',    r"match\b|circle\b|tick\b|number the|label\b|look and (say|write|match)|odd one out|find the words?"),
    ('GRAMMAR',       r"choose the (correct|best)|underline\b|put the verbs?|fill in|correct form of"),
    ('READING',       r"read( the| and)?\b"),
    ('WRITING',       r"write\b|complete the (sentences?|passage|text|email|letter)|make sentences"),
]
def classify(text):
    low = text.lower()
    for name, pat in SECTIONS:
        if re.search(pat, low):
            return name
    for name, pat in RULES:
        if re.search(pat, low):
            return name
    return 'OTHER'

dist = collections.Counter()
by_grade = collections.defaultdict(collections.Counter)
marker_freq = collections.Counter()
samples = collections.defaultdict(list)
total = 0
for f in sorted(glob.glob('poc-out/units-k12/*sgk-tieng-anh*.json')):
    d = json.load(open(f))
    g = int(f.split('/')[-1][:2])
    for u in d.get('units', []):
        t = u.get('text', '')
        total += 1
        k = classify(t)
        dist[k] += 1
        by_grade[g][k] += 1
        if len(samples[k]) < 2:
            samples[k].append(t[:80].replace('\n', ' '))
        for name, pat in RULES:
            m = re.search(pat, t.lower())
            if m:
                marker_freq[m.group(2) if m.lastindex and m.lastindex >= 2 else name] += 1
                break

print(f'TOTAL EN units: {total}')
print('\n=== DISTRIBUTION 9 loại ===')
for k, n in dist.most_common():
    print(f'{k:14s} {n:5d} ({n/total*100:4.1f}%)')
print('\n=== theo GRADE (loại top-3 mỗi lớp) ===')
for g in sorted(by_grade):
    top = by_grade[g].most_common(4)
    print(f'lớp {g:2d}: ' + ' · '.join(f'{k}:{n}' for k, n in top))
print('\n=== SAMPLES ===')
for k in dist:
    for s in samples[k]:
        print(f'[{k}] {s}')
