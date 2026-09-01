"""WAL-74 batch ③ — extractor RIÊNG cho sách Tiếng Việt (cấu trúc đã đo khác toán).

Đo trước khi viết (2 tập TV5): header «Bài» ĐỨNG LẺ + số ở DÒNG DƯỚI cùng cột
(69 header, ghép số ~91%); section = chữ HOA đứng lẻ (ĐỌC 60, VIẾT 65, NÓI VÀ
NGHE 30, LUYỆN TỪ VÀ CÂU 62, ĐỌC MỞ RỘNG 32); RULE = hộp «Ghi nhớ» (16).
Trang in lấy từ số chân trang (không có TOC dùng được cho sách này ở GĐ1).
Header không ghép được số ⇒ ĐẾM VÀ BÁO, không đoán.
"""
import json, os, re, sys, unicodedata

BOOK = sys.argv[1]
OCR = f'poc-out/graph/ocr-body/{BOOK}'

def strip(s):
    s = unicodedata.normalize('NFD', s.lower().replace('đ', 'd'))
    return ''.join(c for c in s if not unicodedata.combining(c))

SECTION = {'doc': 'READING', 'viet': 'WRITING', 'doc mo rong': 'READING_EXT',
           'noi va nghe': 'SPEAKING', 'luyen tu va cau': 'GRAMMAR'}
EX_STEM = re.compile(r'^(\d{1,2})\s*[.．]?\s+\S')

def main():
    pages = {}
    for f in sorted(os.listdir(OCR)):
        j = json.load(open(f'{OCR}/{f}'))
        pages[j['pdf_page']] = j['lines']

    # trang in từ chân trang: dòng chỉ-số ở y cao nhất
    printed = {}
    for p, lines in pages.items():
        cands = [int(l['text']) for l in lines
                 if l['y'] > 0.88 and l['text'].strip().isdigit()
                 and len(l['text'].strip()) <= 3]
        if cands:
            printed[p] = cands[-1]

    # header «Bài» 2 dòng
    headers, orphan = [], 0
    for p, lines in pages.items():
        for i, l in enumerate(lines):
            if strip(l['text']).strip() == 'bai' and l['y'] < 0.15:
                num = None
                for l2 in lines[i+1:i+4]:
                    if l2['text'].strip().isdigit() and abs(l2['x']-l['x']) < 0.06:
                        num = int(l2['text']); break
                if num is None:
                    orphan += 1
                else:
                    headers.append((p, num))
    headers.sort()
    if not headers:
        sys.exit('⚠️ LỖI TO: không tìm được header bài nào')
    ranges = [(n, p, (headers[i+1][0]-1 if i+1 < len(headers) else max(pages)))
              for i, (p, n) in enumerate(headers)]
    def lesson_of(p):
        for n, a, b in ranges:
            if a <= p <= b: return n
        return None

    units, cur = [], None
    def flush():
        nonlocal cur
        if cur and len(cur['text'].strip()) >= 8:
            cur['text'] = re.sub(r'\s+', ' ', cur['text']).strip()
            units.append(cur)
        cur = None

    def start(role, section, p, text):
        nonlocal cur
        flush()
        cur = {'id': f'{BOOK}:p{p:03d}:{len(units):04d}',
               'role': role, 'section': section,
               'lesson': lesson_of(p), 'pagePdf': p,
               'pagePrinted': printed.get(p), 'text': text,
               'provenance': {'origin': 'textbookVerbatim', 'source': BOOK,
                              'extraction': 'deterministic-marker-tv-v1'}}

    section = None
    for p in sorted(pages):
        if lesson_of(p) is None:
            continue
        for l in pages[p]:
            t = l['text'].strip()
            st = strip(t).strip()
            if st == 'bai' and l['y'] < 0.15:
                flush(); section = None; continue
            if st in SECTION and l['x'] < 0.30:
                flush(); section = SECTION[st]; continue
            if st.startswith('ghi nho'):
                start('RULE', section, p, t[len('Ghi nhớ'):].strip() or t)
                continue
            if EX_STEM.match(t) and l['x'] < 0.25:
                start('EXERCISE', section, p, t); continue
            if cur is None:
                start('SECTION_TEXT', section, p, t)
            else:
                cur['text'] += ' ' + t
    flush()

    from collections import Counter
    roles = Counter(u['role'] for u in units)
    out = {'book': BOOK, 'units': units,
           'stats': {'units': len(units), 'roles': dict(roles),
                     'headers': len(headers), 'headerOrphans': orphan,
                     'pagesNoPrinted': len(pages) - len(printed),
                     'lessons': len({u['lesson'] for u in units})}}
    json.dump(out, open(f'poc-out/units/{BOOK}.json', 'w'),
              ensure_ascii=False, indent=1)
    print(f"units: {len(units)} · roles: {dict(roles)} · header: {len(headers)} "
          f"(mồ côi: {orphan}) · trang thiếu số in: {out['stats']['pagesNoPrinted']}")

if __name__ == '__main__':
    main()
