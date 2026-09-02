"""K-12 §VI bổ khuyết — mine TÊN BÀI từ header trang OCR (tất định).

structure-scan chỉ có (số bài, trang) — 0/7199 title. Title thật nằm ở
header trang mở bài: «Bài N» + dòng TIÊU ĐỀ IN HOA ngay sau (đã thấy ở
Toán/SGV). Luật: tại pageStart (±1 trang, phòng lệch TOC↔pdf), tìm dòng
match 'Bài N' ở nửa trên trang; title = các dòng kế tiếp VIẾT HOA (≥60%
chữ hoa, ≤3 dòng). Không thấy ⇒ title giữ None — không bịa (§XXXIII).
Chạy lại được nhiều lần khi OCR phủ thêm (idempotent — ghi đè file out).
"""
import json, os, re

LESSON = re.compile(r'^Bài\s+(\d+)\b')

def is_title_line(t):
    letters = [c for c in t if c.isalpha()]
    if len(letters) < 3:
        return False
    return sum(1 for c in letters if c.isupper()) / len(letters) >= 0.6

struct = json.load(open('poc-out/graph/curriculum-structure.json'))
docs = struct['documents']
mined = total = have_ocr = 0
for d in docs:
    ocr = f"poc-out/graph/ocr-body/{d['sourceDocumentId']}"
    if not os.path.isdir(ocr):
        continue
    have_ocr += 1
    pages = {}
    for f in os.listdir(ocr):
        try:
            j = json.load(open(f'{ocr}/{f}'))
            pages[j['pdf_page']] = j['lines']
        except Exception:
            continue
    for l in d['lessons']:
        total += 1
        if l['title'] or not l['pageStart']:
            continue
        # TOC ghi trang IN; pdf thường lệch +0..+2 — thử cả ba
        for off in (0, 1, 2):
            lines = pages.get(l['pageStart'] + off)
            if not lines:
                continue
            for i, ln in enumerate(lines[:10]):
                m = LESSON.match(ln['text'].strip())
                if m and int(m.group(1)) == l['number']:
                    parts = []
                    for nxt in lines[i + 1:i + 4]:
                        t = nxt['text'].strip()
                        if is_title_line(t):
                            parts.append(t)
                        elif parts:
                            break
                    if parts:
                        l['title'] = ' '.join(parts)
                        l['titleSource'] = f'ocr-header:p{l["pageStart"]+off}'
                        mined += 1
                    break
            if l.get('title'):
                break

json.dump(struct, open('poc-out/graph/curriculum-structure.json', 'w'),
          ensure_ascii=False, indent=1)
titled = sum(1 for d in docs for l in d['lessons'] if l.get('title'))
print(f'docs có OCR: {have_ocr} · titles mined lần này: {mined} · '
      f'tổng titled: {titled}/{sum(d["lessonCount"] for d in docs)}')
# mẫu kiểm tay
for d in docs:
    if d['sourceDocumentId'] == '05-sgk-toan-5-tap-hai':
        for l in d['lessons'][:5]:
            print(' ', l['number'], '→', (l.get('title') or 'None')[:60])
