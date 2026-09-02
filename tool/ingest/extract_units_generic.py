"""K-12 §VII — GENERIC ATOMIC EXTRACTOR: shared core + family adapters.

Insight cấu trúc: chương trình GDPT 2018 dùng KHUNG HOẠT ĐỘNG CHUNG mọi
môn (Khởi động / Khám phá / Luyện tập / Vận dụng / Ghi nhớ / Em có biết)
— shared core bám khung đó; adapter theo subject-family chỉ THÊM marker
đặc thù, không thay khung. Không ép taxonomy Toán lên mọi môn (§XV).

Roles generic v1 (audit mở rộng dần theo evidence từng môn):
ACTIVITY · EXERCISE · RULE_CANDIDATE (Ghi nhớ) · NOTE (Em có biết) ·
SECTION_TEXT. assertion: RULE_CANDIDATE=EXPLICIT, còn lại DEMONSTRATED.
Lesson gán từ curriculum-structure (offset hiệu chỉnh bằng header «Bài N»
thật như extract_units); sách NO_TOC ⇒ lesson None — UNKNOWN giữ UNKNOWN.

Output: poc-out/units-k12/<id>.json (KHÔNG đụng poc-out/units cũ — gate
Toán/TV giữ nguyên; gate k12 nằm ở manifest).
"""
import json, os, re, sys, unicodedata

def strip_vn(s):
    s = unicodedata.normalize('NFD', s.lower().replace('đ', 'd'))
    return ''.join(c for c in s if not unicodedata.combining(c))

# khung GDPT 2018 — marker CHUNG (đã strip dấu)
CORE_MARKERS = {
    'khoi dong': 'ACTIVITY', 'kham pha': 'ACTIVITY', 'luyen tap': 'ACTIVITY',
    'van dung': 'ACTIVITY', 'thuc hanh': 'ACTIVITY', 'hoat dong': 'ACTIVITY',
    'ghi nho': 'RULE_CANDIDATE', 'em co biet': 'NOTE',
    'em can biet': 'RULE_CANDIDATE',
}
FAMILY_MARKERS = {
    'Toán': {'vi du': 'EXAMPLE'},
    'Tiếng Việt': {'doc': 'READING', 'viet': 'ACTIVITY', 'noi va nghe': 'ACTIVITY'},
    'Ngữ văn': {'doc hieu': 'READING', 'viet': 'ACTIVITY', 'tri thuc ngu van': 'CONCEPT_EXPLANATION'},
    'KHTN': {'thi nghiem': 'EXPERIMENT', 'quan sat': 'OBSERVATION'},
    'Khoa học': {'thi nghiem': 'EXPERIMENT', 'quan sat': 'OBSERVATION'},
    'Lịch sử': {'tu lieu': 'SOURCE_TEXT'},
    'LS&ĐL': {'tu lieu': 'SOURCE_TEXT'},
    'Địa lí': {'bang so lieu': 'TABLE'},
}
EX_STEM = re.compile(r'^(\d{1,2})\s*[.．]\s+\S')
LESSON_HDR = re.compile(r'^B[ÀA][IÌ]\s+(\d+)\b|^Bài\s+(\d+)\b')

def extract(doc_id):
    ocr = f'poc-out/graph/ocr-body/{doc_id}'
    if not os.path.isdir(ocr):
        return None
    struct = {d['sourceDocumentId']: d for d in json.load(
        open('poc-out/graph/curriculum-structure.json'))['documents']}
    d = struct.get(doc_id, {})
    subject = d.get('subject')
    markers = dict(CORE_MARKERS)
    markers.update(FAMILY_MARKERS.get(subject, {}))

    pages = {}
    for f in sorted(os.listdir(ocr)):
        try:
            j = json.load(open(f'{ocr}/{f}'))
            pages[j['pdf_page']] = j['lines']
        except Exception:
            continue

    # offset in→pdf từ header thật; không hiệu chỉnh được + có TOC ⇒ offset 0
    # nhưng đánh dấu offsetCalibrated=False (PARTIAL, không giấu — §XXII)
    hdr_at = {}
    for p, lines in pages.items():
        for l in lines[:6]:
            m = LESSON_HDR.match(l['text'].strip())
            if m and l['y'] < 0.2:
                hdr_at.setdefault(int(m.group(1) or m.group(2)), p)
    toc = {l['number']: l['pageStart'] for l in d.get('lessons', [])
           if l.get('pageStart')}
    offs = [hdr_at[n] - toc[n] for n in hdr_at if n in toc]
    offset = max(set(offs), key=offs.count) if offs else 0
    calibrated = bool(offs)

    ranges = sorted([(n, p + offset) for n, p in toc.items()],
                    key=lambda x: x[1])
    def lesson_of(pdf_page):
        cur = None
        for n, start in ranges:
            if pdf_page >= start:
                cur = n
            else:
                break
        return cur

    units, cur, mode = [], None, 'SECTION_TEXT'
    def flush():
        nonlocal cur
        if cur and len(cur['text'].strip()) >= 15:
            units.append(cur)
        cur = None
    for p in sorted(pages):
        for l in pages[p]:
            t = l['text'].strip()
            st = strip_vn(t)
            role = None
            for k, r in markers.items():
                if st.startswith(k) and len(st) < len(k) + 25:
                    role = r
                    break
            if role:
                flush(); mode = role
                cur = {'role': role, 'text': t, 'pagePdf': p}
                continue
            if EX_STEM.match(t):
                flush()
                cur = {'role': 'EXERCISE', 'text': t, 'pagePdf': p}
                continue
            if cur is None:
                cur = {'role': mode, 'text': t, 'pagePdf': p}
            else:
                cur['text'] += ' ' + t
    flush()
    for i, u in enumerate(units):
        u['id'] = f'{doc_id}:p{u["pagePdf"]:03d}:{i:04d}'
        u['lesson'] = lesson_of(u['pagePdf'])
        u['provenance'] = {
            'assertion': 'EXPLICIT' if u['role'] == 'RULE_CANDIDATE'
                         else 'DEMONSTRATED',
            'extraction': 'generic-gdpt2018-v1',
        }
    out = {'sourceDocumentId': doc_id, 'subject': subject,
           'extractor': 'generic-gdpt2018-v1',
           'offsetCalibrated': calibrated, 'units': units}
    os.makedirs('poc-out/units-k12', exist_ok=True)
    json.dump(out, open(f'poc-out/units-k12/{doc_id}.json', 'w'),
              ensure_ascii=False, indent=1)
    from collections import Counter
    return {'units': len(units), 'roles': dict(Counter(u['role'] for u in units)),
            'lessonNone': sum(1 for u in units if u['lesson'] is None),
            'calibrated': calibrated}

if __name__ == '__main__':
    for doc in sys.argv[1:]:
        r = extract(doc)
        print(doc, '→', r if r else 'KHÔNG CÓ OCR')
