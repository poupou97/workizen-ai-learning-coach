"""WAL-74 GĐ2 batch ① — trích ContentUnit ATOMIC từ trang thân bài (Toán 5 t1).

Luật phân vai TẤT ĐỊNH, lexicon ĐÃ KIỂM trên chính corpus (17 «Muốn…»,
34 «Luyện tập», 12 «Khám phá»):
  «Muốn …»                → RULE   (câu phát biểu quy tắc chuẩn của bộ sách)
  «Ví dụ»                 → EXAMPLE
  «Khám phá»              → section EXPLORE
  «Luyện tập»/«Trò chơi»/«Hoạt động» → section PRACTICE/GAME/ACTIVITY
  stem số «N.» đầu dòng trái        → EXERCISE
0 LLM. Đơn vị nào không phân vai được → SECTION_TEXT (không đoán).
Offset trang in ↔ trang PDF được HIỆU CHỈNH bằng header «Bài N» thật,
không giả định. Output ngoài git (ADR-002).
"""
import json, os, re, sys, unicodedata

BOOK = '05-sgk-toan-5-tap-mot'
OCR = f'poc-out/graph/ocr-body/{BOOK}'

def strip(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if not unicodedata.combining(c))

SECTION = {'kham pha': 'EXPLORE', 'luyen tap': 'PRACTICE',
           'tro choi': 'GAME', 'hoat dong': 'ACTIVITY',
           'cuoc song': 'APPLICATION'}
LESSON_HDR = re.compile(r'^Bài\s+(\d+)\b')
EX_STEM = re.compile(r'^(\d{1,2})\s*[.．]?\s+\S')

def main():
    scan = json.load(open('poc-out/graph/structure-scan.json'))
    book = next(b for b in scan['books'] if b['id'] == BOOK)
    toc = {l['n']: l for l in book['lessonTitles'] if l['n'] is not None}

    pages = {}
    for f in sorted(os.listdir(OCR)):
        j = json.load(open(f'{OCR}/{f}'))
        pages[j['pdf_page']] = j['lines']

    # ── hiệu chỉnh offset trang in ↔ pdf bằng header «Bài N» thật ──
    hdr_at = {}
    for p, lines in pages.items():
        for l in lines[:6]:
            m = LESSON_HDR.match(l['text'].strip())
            if m and l['y'] < 0.15:
                hdr_at.setdefault(int(m.group(1)), p)
    offsets = [hdr_at[n] - toc[n]['p'] for n in hdr_at
               if n in toc and toc[n]['p']]
    if not offsets:
        sys.exit('⚠️ LỖI TO: không hiệu chỉnh được offset — dừng, không đoán')
    offset = max(set(offsets), key=offsets.count)
    bad_off = [o for o in offsets if o != offset]
    print(f'offset in→pdf: +{offset} (khớp {len(offsets)-len(bad_off)}/{len(offsets)} header; lệch: {len(bad_off)})')

    # lesson ranges theo pdf page — bài thiếu trang trong TOC bị LOẠI và ĐẾM
    no_page = [n for n in toc if not toc[n]['p']]
    if no_page:
        print(f'⚠️ {len(no_page)} bài TOC thiếu số trang (OCR): {sorted(no_page)} — loại, không đoán')
    toc = {n: v for n, v in toc.items() if v['p']}
    nums = sorted(toc)
    ranges = []
    for i, n in enumerate(nums):
        start = toc[n]['p'] + offset
        end = (toc[nums[i+1]]['p'] + offset - 1) if i+1 < len(nums) else max(pages)
        ranges.append((n, start, end))
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
               'pagePrinted': p - offset, 'text': text,
               'provenance': {'origin': 'textbookVerbatim', 'source': BOOK,
                              'extraction': 'deterministic-marker-v1'}}

    section = None
    for p in sorted(pages):
        if lesson_of(p) is None:
            continue  # ngoài phạm vi bài (bìa, mục lục, ôn tập không số)
        for l in pages[p]:
            t = l['text'].strip()
            st = strip(t)
            if LESSON_HDR.match(t) and l['y'] < 0.15:
                flush(); section = None; continue
            hit = next((v for k, v in SECTION.items() if st.startswith(k)), None)
            if hit:
                flush(); section = hit; continue
            if st.startswith('muon'):
                start('RULE', section, p, t); continue
            if st.startswith('vi du'):
                start('EXAMPLE', section, p, t); continue
            if EX_STEM.match(t) and l['x'] < 0.25:
                start('EXERCISE', section, p, t); continue
            if cur is None:
                start('SECTION_TEXT', section, p, t)
            else:
                cur['text'] += ' ' + t
    flush()

    from collections import Counter
    roles = Counter(u['role'] for u in units)
    frag = sum(1 for u in units if len(u['text']) < 25)
    out = {'book': BOOK, 'offset': offset, 'units': units,
           'stats': {'units': len(units), 'roles': dict(roles),
                     'fragmentsUnder25c': frag,
                     'lessonsCovered': len({u['lesson'] for u in units})}}
    os.makedirs('poc-out/units', exist_ok=True)
    json.dump(out, open(f'poc-out/units/{BOOK}.json', 'w'),
              ensure_ascii=False, indent=1)
    print(f"units: {len(units)} · roles: {dict(roles)} · "
          f"fragment<25c: {frag} · bài phủ: {out['stats']['lessonsCovered']}")

if __name__ == '__main__':
    main()
