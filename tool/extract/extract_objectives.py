"""WAL-76 (GĐ3) — LearningObjective từ SGV: mục MỤC TIÊU per-bài, sourceStated.

Cấu trúc SGV Toán 5 (đo thật): «Bài N …» → «MỤC TIÊU» → «Giúp HS:» →
«Kiến thức, kĩ năng» (bullets '-') → «Phát triển năng lực» (bullets '-')
→ «CHUẨN BỊ». Trích tất định theo cấu trúc đó; concept CHỈ gán khi từ khoá
đặc trưng khớp (như map_rules) — không match ⇒ 'unmapped', không đoán.
"""
import json, os, re, sys, unicodedata

def strip(s):
    s = unicodedata.normalize('NFD', s.lower().replace('đ', 'd').replace('Đ', 'd'))
    return ''.join(c for c in s if not unicodedata.combining(c))

KEYS = [
    ('quy dong mau so', 'quy-dong'),
    ('phan so thap phan', 'phan-so-thap-phan'),
    ('cong, tru hai phan so', 'cong-tru-phan-so'),
    ('phep tinh voi phan so', 'phep-tinh-phan-so'),
    ('hon so', 'hon-so'),
    ('so thap phan', 'so-thap-phan'),
    ('ti so phan tram', 'ti-so-phan-tram'),
    ('the tich cua hinh hop chu nhat', 'the-tich-hinh-hop-chu-nhat'),
    ('the tich cua hinh lap phuong', 'the-tich-hinh-lap-phuong'),
    ('dien tich hinh tam giac', 'dien-tich-tam-giac'),
    ('dien tich hinh thang', 'dien-tich-hinh-thang'),
    ('hinh tron', 'hinh-tron'),
    ('van toc', 'van-toc'),
    ('so tu nhien', 'so-tu-nhien'),
]

BOOK = sys.argv[1] if len(sys.argv) > 1 else '05-sgv-toan-5'
D = f'poc-out/graph/ocr-body/{BOOK}'
LESSON = re.compile(r'^Bài\s+(\d+)\b')
# header thật trong SGV in số La Mã, OCR nhiễu thành 'L'/'I.'/'Ш' — match
# dòng NGẮN kết thúc bằng MỤC TIÊU thay vì đoán đúng tiền tố nhiễu.
MUCTIEU = re.compile(r'^.{0,4}M[ỤU]C TI[ÊE]U\s*$')
ENDBLOCK = re.compile(r'CHU[ẨA]N B[ỊI]|HO[ẠA]T Đ[ỘO]NG D[ẠA]Y')

out, cur_lesson, in_block, mode, cur = [], None, False, None, None
def flush():
    global cur
    if cur and len(cur['text']) >= 10:
        out.append(cur)
    cur = None

for f in sorted(os.listdir(D)):
    j = json.load(open(f'{D}/{f}'))
    for l in j['lines']:
        t = l['text'].strip()
        m = LESSON.match(t)
        if m:
            cur_lesson = int(m.group(1))
        up = t.upper()
        if MUCTIEU.match(up):
            in_block, mode = True, None
            continue
        if in_block and ENDBLOCK.search(up):
            flush(); in_block = False
            continue
        if not in_block:
            continue
        if 'Kiến thức' in t or 'kĩ năng' in t and len(t) < 30:
            flush(); mode = 'knowledge'; continue
        if 'Phát triển năng lực' in t:
            flush(); mode = 'competency'; continue
        if t.startswith('Giúp HS') or t.startswith('Giup HS'):
            continue
        if t.startswith('-'):
            flush()
            cur = {'book': BOOK, 'lesson': cur_lesson, 'pagePdf': j['pdf_page'],
                   'kind': mode or 'knowledge', 'text': t.lstrip('- ').strip(),
                   'origin': 'sourceStated', 'extraction': 'sgv-muctieu-v1'}
        elif cur:
            cur['text'] += ' ' + t

flush()
for i, o in enumerate(out):
    o['id'] = f"{BOOK}:obj:{o['lesson']}:{i:04d}"
    st = strip(o['text'])
    o['conceptId'] = next((c for k, c in KEYS if k in st), 'unmapped')

path = f'poc-out/units/{BOOK}.objectives.json'
json.dump(out, open(path, 'w'), ensure_ascii=False, indent=1)
mapped = sum(1 for o in out if o['conceptId'] != 'unmapped')
lessons = sorted({o['lesson'] for o in out if o['lesson']})
kinds = {}
for o in out: kinds[o['kind']] = kinds.get(o['kind'], 0) + 1
print(f'objectives: {len(out)} · bài phủ: {len(lessons)} ({lessons[0]}-{lessons[-1]})'
      f' · kind: {kinds} · concept mapped: {mapped}/{len(out)}')
no_lesson = [o for o in out if not o['lesson']]
print('objective KHÔNG gán được bài:', len(no_lesson))
