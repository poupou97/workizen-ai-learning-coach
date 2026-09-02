#!/usr/bin/env python3
"""WAL-148 KS-A stories-v0 — candidate extractor đa-môn, SOURCE-BOUND (§6).

Mọi item = CANDIDATE (chưa phải curated fact). PRECISION>RECALL: pattern hẹp,
confidence từ chất-lượng-OCR (tỉ lệ dấu tiếng Việt hợp lệ), noise bìa/nghị
định bị loại. KHÔNG LLM. Output: poc-out/stories/candidates-v0.json.
"""
import json, os, re, sys, collections, unicodedata

VER = 'stories-v0'
SAMPLE = [
 '06-sgk-ngu-van-6-tap-mot','10-sgk-ngu-van-10-tap-hai','03-sgk-tieng-viet-3-tap-mot',
 '10-sgk-lich-su-10','04-sgk-lich-su-va-dia-li-4','07-sgk-lich-su-va-dia-li-7',
 '04-sgk-khoa-hoc-4','06-sgk-khoa-hoc-tu-nhien-6','10-sgk-vat-li-10','10-sgk-hoa-hoc-10',
 '10-sgk-sinh-hoc-10','06-sgk-toan-6-tap-mot','10-sgk-tin-hoc-10','06-sgk-cong-nghe-6',
 '04-sgk-dao-duc-4','06-sgk-giao-duc-cong-dan-6','06-sgk-am-nhac-6','06-sgk-mi-thuat-6',
]

NOISE = re.compile(r'NĐ-CP|QĐ-BGDĐT|QĐ-TTg|Bản quyền|NHÀ XUẤT BẢN|ISBN|Tái bản|Chủ biên|Hội đồng|thẩm định', re.I)
NAME = r"[A-ZĐ][a-zà-ỹ]+(?:[\s\-][A-ZĐa-zà-ỹ][a-zà-ỹ\-]*){0,4}"
P_BIRTH = re.compile(r'(' + NAME + r')\s*\(\s*(\d{3,4})\s*[–\-]\s*(\d{3,4})\s*\)')
P_INTRO = re.compile(r'(nhà (?:thơ|văn|bác học|khoa học|toán học|vật lí|hoá học|sử học|giáo dục|soạn nhạc)|nhạc sĩ|hoạ sĩ|họa sĩ|danh nhân|anh hùng)\s+(' + NAME + r')')
P_QUOTE = re.compile(r'"([^"]{15,220})"\s*[\.\s]*\(\s*(' + NAME + r')(?:\s*,\s*([^)]{3,80}))?\)')
P_EVENT = re.compile(r'([Nn]ăm\s+(\d{3,4})|[Nn]gày\s+(\d{1,2})[\-/](\d{1,2})[\-/](\d{4}))[\s,:]([^.]{15,180}\.)')
P_INV = re.compile(r'(' + NAME + r')?[^.]{0,60}(phát minh ra|sáng chế ra|tìm ra|khám phá ra|phát hiện ra)\s+([^.]{5,120}\.)')

def viet_quality(t):
    """Tỉ lệ ký tự chữ hợp lệ + có dấu — thơ OCR vỡ rơi điểm."""
    letters = [c for c in t if c.isalpha()]
    if len(letters) < 10: return 0.0
    good = sum(1 for c in letters if unicodedata.name(c, '').startswith('LATIN'))
    words = t.split()
    diac = sum(1 for w in words if any(0x300 <= ord(unicodedata.normalize('NFD', c)[-1]) <= 0x36F for c in w if c.isalpha()))
    return round(min(1.0, good/len(letters)) * (0.5 + 0.5*min(1.0, diac/max(3,len(words)*0.25))), 2)

def mine(did, reg):
    base = f'poc-out/graph/ocr-body/{did}'
    if not os.path.isdir(base): return None
    r = reg[did]
    out = []
    def add(typ, page, text_ev, **kw):
        conf = viet_quality(text_ev)
        out.append(dict(type=typ, status='CANDIDATE', confidence=conf,
                        source=dict(sourceDocumentId=did, grade=r['grade'],
                                    subject=r['subject'], pagePdf=page,
                                    textEvidence=text_ev[:300],
                                    extractionVersion=VER), **kw))
    for fn in sorted(os.listdir(base)):
        if not fn.endswith('.json'): continue
        page = int(fn[1:4])
        try: d = json.load(open(f'{base}/{fn}'))
        except Exception: continue
        text = ' '.join(l['text'] for l in d.get('lines', []))
        if page <= 3 or NOISE.search(text[:400]):
            continue  # bìa/pháp lý — nguồn nhiễu chính đo được ở probe
        for m in P_BIRTH.finditer(text):
            name, b, dth = m.group(1), int(m.group(2)), int(m.group(3))
            if not (700 <= b <= 2010 and b < dth <= 2026 and dth - b < 110):
                continue  # OCR corruption («7642») ⇒ loại — không REVIEW bừa v0
            add('PERSON', page, text[max(0,m.start()-60):m.end()+120],
                name=name, birthYear=b, deathYear=dth)
        for m in P_INTRO.finditer(text):
            add('PERSON', page, text[max(0,m.start()-40):m.end()+120],
                name=m.group(2), role=m.group(1))
        for m in P_QUOTE.finditer(text):
            add('QUOTE', page, text[max(0,m.start()-40):m.end()+40],
                quote=m.group(1), person=m.group(2), citedSource=m.group(3))
        for m in P_EVENT.finditer(text):
            add('EVENT', page, m.group(0)[:260],
                year=int(m.group(2) or m.group(5)),
                monthDay=(f'{int(m.group(4)):02d}-{int(m.group(3)):02d}'
                          if m.group(3) else None))
        for m in P_INV.finditer(text):
            add('INVENTION_DISCOVERY', page, m.group(0)[:260],
                person=m.group(1), verb=m.group(2), what=m.group(3)[:120])
    return out

def main():
    reg = {d['sourceDocumentId']: d for d in
           json.load(open('poc-out/registry/source-registry.json'))['documents']}
    all_items, missing = [], []
    for did in SAMPLE:
        r = mine(did, reg) if did in reg else None
        if r is None: missing.append(did); continue
        all_items += r
    json.dump(all_items, open('poc-out/stories/candidates-v0.json','w'),
              ensure_ascii=False, indent=1)
    by = collections.Counter((i['type'], i['source']['subject']) for i in all_items)
    byt = collections.Counter(i['type'] for i in all_items)
    print(f'{len(all_items)} candidates | thiếu OCR: {missing}')
    print('theo type:', dict(byt))
    subj = collections.Counter(i['source']['subject'] for i in all_items)
    print('theo môn:', dict(subj.most_common()))
    hi = [i for i in all_items if i['confidence'] >= 0.75]
    print(f'confidence ≥0.75: {len(hi)}')
    print('\n── VÍ DỤ CHẤT LƯỢNG CAO ──')
    seen = set()
    for i in sorted(all_items, key=lambda x: -x['confidence']):
        if i['type'] in seen and len(seen) >= 4: continue
        if list(seen).count(i['type']) : pass
        key = i['type']
        if sum(1 for s in seen if s == key) >= 3: continue
        seen.add(key)
        s = i['source']
        head = {'PERSON': i.get('name'), 'QUOTE': f"{i.get('person')}: «{str(i.get('quote'))[:60]}…»",
                'EVENT': f"{i.get('year')} — {i['source']['textEvidence'][:50]}",
                'INVENTION_DISCOVERY': f"{i.get('person') or '?'} {i.get('verb')} {str(i.get('what'))[:45]}"}[i['type']]
        print(f"  [{i['type'][:6]}|c{i['confidence']}] {s['subject']} {s['grade']} p{s['pagePdf']}: {head}")
        if len(seen) >= 4 and sum(byt[t] > 0 for t in byt) <= len(seen): break
    # đếm ví dụ in tối đa 14 dòng
if __name__ == '__main__':
    main()
