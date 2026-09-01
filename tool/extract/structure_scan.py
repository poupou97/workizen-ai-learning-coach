"""WAL-73 GĐ1 — quét CẤU TRÚC toàn bộ SGK 1–12. TẤT ĐỊNH, 0 LLM.

Mỗi cuốn: OCR trang đầu (mục lục) + trang cuối (bảng thuật ngữ) → parse_toc v2.
LUẬT: bố cục lạ / parse hỏng phải LỖI TO trong báo cáo, không giấu (bài học v1).
Toàn bộ output ở poc-out/ (gitignored) — sản phẩm phái sinh KHÔNG vào git (ADR-002).
"""
import json, os, re, subprocess, sys, time, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
from parse_structure import parse_toc, LESSON

OCR = '/tmp/ocr_pdf'
OUT = 'poc-out/graph'
FRONT, BACK = 8, 5  # trang đầu + trang cuối mỗi cuốn

def n(s): return unicodedata.normalize('NFC', s).upper()

def pages_of(pdf):
    r = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True)
    m = re.search(r'Pages:\s+(\d+)', r.stdout)
    return int(m.group(1)) if m else None

def book_meta(fname):
    b = os.path.basename(fname)[:-4]
    m = re.match(r'(\d{2})-(sgk|sgv|sbt|smem|shs)-(.+)', b)
    if not m: return b, None, None
    return b, m.group(2), m.group(3)

def scan_book(pdf, grade):
    bid, kind, subject = book_meta(pdf)
    rec = {'id': bid, 'grade': grade, 'kind': kind, 'subject': subject,
           'pages': None, 'tocPages': [], 'lessons': 0, 'chapters': 0,
           'glossary': False, 'status': 'OK', 'error': None}
    total = pages_of(pdf)
    if not total:
        rec['status'] = 'ERROR'; rec['error'] = 'pdfinfo: không đọc được số trang'
        return rec
    rec['pages'] = total
    odir = f'{OUT}/ocr/{grade:02d}/{bid}'
    os.makedirs(odir, exist_ok=True)
    ranges = [(1, min(FRONT, total))]
    if total > FRONT + BACK: ranges.append((total - BACK + 1, total))
    for a, b in ranges:
        if all(os.path.exists(f'{odir}/p{p:03d}.json') for p in range(a, b + 1)):
            continue  # OCR đã có — idempotent, chạy lại không tốn công
        subprocess.run([OCR, pdf, str(a), str(b), odir],
                       capture_output=True, text=True)
    toc_entries, chapters = [], 0
    for pj in sorted(os.listdir(odir)):
        path = f'{odir}/{pj}'
        try:
            data = json.load(open(path))
        except Exception:
            continue
        text = n(' '.join(l['text'] for l in data['lines']))
        pno = data['pdf_page']
        if 'THUẬT NGỮ' in text or 'BẢNG TRA CỨU' in text:
            rec['glossary'] = True
        is_toc = 'MỤC LỤC' in text or \
            sum(1 for l in data['lines'] if LESSON.match(l['text'].strip())) >= 3
        if is_toc:
            rec['tocPages'].append(pno)
            try:
                parsed = parse_toc(path)
                for ch in parsed['chapters']:
                    if ch.get('title'): chapters += 1
                    toc_entries += ch['lessons']
            except Exception as e:
                rec['status'] = 'PARSE_FAIL'
                rec['error'] = f'parse_toc p{pno}: {type(e).__name__}: {e}'
    rec['lessons'], rec['chapters'] = len(toc_entries), chapters
    rec['lessonTitles'] = [
        {'n': e.get('number'), 't': (e.get('title') or '')[:120],
         'p': e.get('page_start')} for e in toc_entries]
    if not rec['tocPages'] and rec['status'] == 'OK':
        rec['status'] = 'NO_TOC_FOUND'  # LỖI TO, không giấu
    return rec

def main():
    grades = sys.argv[1:] or [str(g) for g in range(1, 13)]
    books, t0 = [], time.time()
    for g in map(int, grades):
        gdir = f'poc-out/pdf/{g:02d}'
        pdfs = sorted(f'{gdir}/{f}' for f in os.listdir(gdir) if f.endswith('.pdf'))
        for pdf in pdfs:
            r = scan_book(pdf, g)
            books.append(r)
            flag = '' if r['status'] == 'OK' else f"  ⚠️ {r['status']}: {r['error'] or ''}"
            print(f"L{g:02d} {r['id']:55s} {r['pages'] or '?':>4} tr · "
                  f"{r['lessons']:>3} bài · toc={r['tocPages']}{flag}", flush=True)
    ok = [b for b in books if b['status'] == 'OK']
    json.dump({'generatedAt': time.strftime('%Y-%m-%dT%H:%M:%S'),
               'books': books}, open(f'{OUT}/structure-scan.json', 'w'),
              ensure_ascii=False, indent=1)
    print(f"\nTỔNG: {len(books)} cuốn · OK {len(ok)} · "
          f"lỗi {len(books) - len(ok)} · "
          f"{sum(b['lessons'] for b in ok)} bài · "
          f"{sum(b['pages'] or 0 for b in books)} trang · "
          f"{time.time() - t0:.0f}s")

if __name__ == '__main__':
    main()
