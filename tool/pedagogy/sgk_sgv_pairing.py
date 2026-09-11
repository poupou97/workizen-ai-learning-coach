#!/usr/bin/env python3
"""SỞ HỮU SGK ↔ SGV — bài nào của sách giáo viên nói về bài nào của sách học sinh.

⛔ KHỚP SỐ BÀI KHÔNG PHẢI LÀ GHÉP ĐÃ CHỨNG MINH. Đo được: ghép theo quy ước
tên tệp HỎNG ở 8/18 cuốn từng khai thác (`01-sgv-toan-1` không có
`01-sgk-toan-1`), và nơi có đôi thì trùng số bài dao động 3/76 → 31/31.

Nên ở đây mỗi cấp đòi **HAI DỮ KIỆN NGUỒN ĐỘC LẬP** cùng nói một điều:

CẤP SÁCH
  B1  SGV TỰ KHAI đi kèm sách nào — «SGK <môn> <lớp>» in trong chính thân sách
  B2  tiêu đề bài trong SGV TRÙNG tiêu đề bài của SGK ở mức đo được
  ⇒ CONFIDENT khi CẢ HAI. Một mình B1 (hay tên tệp) KHÔNG đủ.

CẤP BÀI
  L1  SGV in tiêu đề «Bài N» ở ĐẦU TRANG THÂN (không phải trang mục lục)
  L2  chữ cạnh tiêu đề ấy TRÙNG tiêu đề bài N của SGK
  L3  trang ấy MỞ THÂN BÀI — có «MỤC TIÊU / YÊU CẦU CẦN ĐẠT / MỤC ĐÍCH»
  ⇒ CONFIDENT khi CẢ BA, và chỉ MỘT mục SGV đòi bài ấy.
     AMBIGUOUS khi chỉ một trong hai, hoặc nhiều mục cùng đòi một bài.
     UNKNOWN khi không có mỏ neo nào.

⚠ BẢNG PHÂN BỔ TIẾT CŨNG BỊ LOẠI — và nó KHÔNG phải mục lục. Đo được một ca
ghép sai: `09-sgv-toan-9` tr93 in «Bài 11. Tỉ số lượng giác… 4 tiết · Bài 12…
3 tiết · Luyện tập chung 2 tiết» trong phần giới thiệu sách. Chỉ 3 lần «Bài N»
nên lọt dưới ngưỡng mục lục, mà tiêu đề lại trùng khít SGK. Chốt L3 giết nó
bằng CẤU TRÚC NGUỒN: bảng phân bổ không mở thân bài.

⚠ TRANG MỤC LỤC BỊ LOẠI. Mục lục liệt kê mọi bài nên trang ấy «khớp» với tất
cả — dùng nó làm mỏ neo là tự tạo ra ghép đúng giả. Nhận bằng MẬT ĐỘ: một
trang nhắc ≥`TOC_MIN` lần «Bài N» là mục lục.

⚠ KHÔNG suy từ vị trí gần nhau. Hai bài cạnh nhau trong SGV không chứng minh
gì về SGK; thứ tự có thể lệch vì SGV chèn phần hướng dẫn chung.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')
PACK = os.path.join(ROOT, 'assets/pack')

#: Một trang nhắc ngần này «Bài N» trở lên là MỤC LỤC, không phải thân bài.
TOC_MIN = 4
#: Số dòng đầu trang được coi là vị trí tiêu đề bài.
HEAD_LINES = 6
#: Trùng tiêu đề tính bằng Jaccard trên từ ≥3 ký tự.
TITLE_MIN = 0.34
#: Tỉ lệ tiêu đề bài trùng tối thiểu để công nhận CẶP SÁCH.
BOOK_MIN = 0.25

BAI = re.compile(r'\bB[ÀA]I\s+(\d{1,2})\b', re.IGNORECASE)
HDR = re.compile(r'^\s*B[ÀA]I\s+(\d{1,2})\b\s*[.:·–—-]?\s*(.*)$', re.IGNORECASE)
#: L3 — thân bài SGV luôn mở bằng một trong các mục này (cấu trúc sách tự khai).
#: Dò trên chữ ĐÃ BỎ DẤU: OCR rụng dấu thường xuyên («MỤC ĐICH» ở Tin học 4),
#: mà rụng dấu không làm mục ấy thôi là mục mở thân bài.
OPENER = re.compile(r'(muc tieu|yeu cau can dat|muc dich)')
#: Số dòng sau tiêu đề được soi tìm chốt mở thân bài.
OPEN_WINDOW = 6
SELF = re.compile(
    r'(?:SGK|sách\s+giáo\s+khoa)\s+([^.,;:\n]{2,46}?)\s*(\d{1,2})\b', re.IGNORECASE)


def _fold(s):
    """Bỏ dấu + thường hoá — OCR hay rụng dấu, so dấu là so cái máy đọc sai."""
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.replace('đ', 'd').replace('Đ', 'D').lower()


def toks(s):
    return {w for w in re.findall(r'[a-z0-9]{3,}', _fold(s))}


def title_match(a, b):
    """Jaccard trên từ. Không dùng so khít: OCR sai vài ký tự là trượt hết."""
    A, B = toks(a), toks(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def _pages(book):
    return sorted(glob.glob(os.path.join(OCR, book, 'p*.json')))


def _page_lines(p):
    try:
        return json.load(open(p, encoding='utf-8'))['lines']
    except Exception:
        return []


def sgv_books():
    return sorted(os.path.basename(d) for d in glob.glob(os.path.join(OCR, '*'))
                  if re.search(r'sgv', os.path.basename(d), re.I))


def sgk_lessons():
    """Bài SGK ĐANG PHỤC VỤ — nguồn duy nhất, không dựng lại từ chỗ khác."""
    out = {}
    for p in sorted(glob.glob(os.path.join(PACK, 'lesson-index-g*.json'))):
        for r in json.load(open(p, encoding='utf-8')).get('lessonReadings') or []:
            out.setdefault(r['book'], {}).setdefault(r['lesson'], r.get('title') or '')
    return out


def self_declared(book, scan=25):
    """B1 — SGV tự khai đi kèm SGK nào. Trả (môn thô, lớp) hoặc None."""
    for p in _pages(book)[:scan]:
        t = ' '.join(l.get('text', '') for l in _page_lines(p))
        m = SELF.search(t)
        if m:
            return (m.group(1).strip(), int(m.group(2)))
    return None


def body_headers(book):
    """L1 — tiêu đề «Bài N» ở đầu trang THÂN. Trang mục lục bị loại."""
    out = []
    for p in _pages(book):
        lines = _page_lines(p)
        full = ' '.join(l.get('text', '') for l in lines)
        if len(BAI.findall(full)) >= TOC_MIN:
            continue                        # ⚠ mục lục — khớp với mọi bài
        pg = int(os.path.basename(p)[1:-5])
        for i, l in enumerate(lines[:HEAD_LINES]):
            m = HDR.match((l.get('text') or '').strip())
            if m:
                # ⚠ Chốt mở thân bài phải ĐI NGAY SAU tiêu đề, không phải «có
                # mặt đâu đó trên trang». Bản đầu dò cả trang nên bảng phân bổ
                # tiết của `09-sgv-toan-9` tr93 vẫn qua — trang ấy có chữ
                # «MỤC TIÊU» ở một mục khác hẳn.
                after = ' '.join((x.get('text') or '')
                                 for x in lines[i + 1:i + 1 + OPEN_WINDOW])
                out.append(dict(page=pg, lesson=int(m.group(1)),
                                text=(m.group(2) or '').strip()[:120],
                                opener=bool(OPENER.search(_fold(after)))))
                break
    return out


def pair_book(sgv, sgk_map):
    """CẶP SÁCH — cần CẢ B1 lẫn B2. Trả (sgk_book, b1, b2_rate, status)."""
    decl = self_declared(sgv)
    heads = body_headers(sgv)
    best = (None, 0.0)
    for bk, les in sgk_map.items():
        if not les or not heads:
            continue
        ok = sum(1 for h in heads
                 if h['lesson'] in les
                 and title_match(h['text'], les[h['lesson']]) >= TITLE_MIN)
        rate = ok / len(heads)
        if rate > best[1]:
            best = (bk, rate)
    bk, rate = best
    b1 = False
    if decl and bk:
        sub, grade = decl
        b1 = (toks(sub) & toks(bk)) != set() and str(grade) in bk
    if bk and b1 and rate >= BOOK_MIN:
        st = 'CONFIDENT'
    elif bk and (b1 or rate >= BOOK_MIN):
        st = 'AMBIGUOUS'
    else:
        st = 'UNKNOWN'
    return bk, b1, round(rate, 3), st


def pair_lessons(sgv, sgk_book, sgk_map):
    """CẤP BÀI — leaf record cho từng mục tiêu đề tìm được trong SGV."""
    les = sgk_map.get(sgk_book) or {}
    heads = body_headers(sgv)
    claims = {}
    for h in heads:
        claims.setdefault(h['lesson'], []).append(h)
    rows = []
    for h in heads:
        n = h['lesson']
        sgk_title = les.get(n)
        l1 = sgk_title is not None
        sim = title_match(h['text'], sgk_title or '')
        l2 = sim >= TITLE_MIN
        dup = len(claims.get(n, [])) > 1
        l3 = bool(h.get('opener'))
        if l1 and l2 and l3 and not dup:
            st = 'CONFIDENT'
        elif l1 and l2:
            st = 'AMBIGUOUS'          # thiếu chốt mở thân bài, hoặc bị đòi trùng
        elif l1 or l2:
            st = 'AMBIGUOUS'
        else:
            st = 'UNKNOWN'
        rows.append(dict(sgv=sgv, sgvPage=h['page'], sgvText=h['text'],
                         sgk=sgk_book or '', lesson=n,
                         sgkTitle=(sgk_title or '')[:80],
                         L1_number=int(l1), L2_title=int(l2), L3_opener=int(l3),
                         titleSim=round(sim, 3), duplicate=int(dup),
                         status=st))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='poc-out/pedagogy/sgk-sgv-pairs.csv')
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    sgk_map = sgk_lessons()
    books = sgv_books()
    if a.limit:
        books = books[:a.limit]
    book_rows, leaf = [], []
    for i, b in enumerate(books):
        if i % 20 == 0:
            print(f'  {i}/{len(books)}…', file=sys.stderr, flush=True)
        bk, b1, rate, st = pair_book(b, sgk_map)
        book_rows.append(dict(sgv=b, sgk=bk or '', B1_selfDeclared=int(b1),
                              B2_titleRate=rate, status=st))
        if st == 'CONFIDENT':
            leaf += pair_lessons(b, bk, sgk_map)
    os.makedirs(os.path.dirname(os.path.join(ROOT, a.out)), exist_ok=True)
    bp = os.path.join(ROOT, a.out).replace('.csv', '-books.csv')
    with open(bp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(book_rows[0]))
        w.writeheader(); w.writerows(book_rows)
    if leaf:
        with open(os.path.join(ROOT, a.out), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(leaf[0]))
            w.writeheader(); w.writerows(leaf)
    import collections
    bc = collections.Counter(r['status'] for r in book_rows)
    lc = collections.Counter(r['status'] for r in leaf)
    print(f'\nCẶP SÁCH  (mẫu số {len(book_rows)}): {dict(bc)}')
    print(f'CẶP BÀI   (mẫu số {len(leaf)}): {dict(lc)}')
    print(f'leaf → {a.out}\nbooks → {os.path.basename(bp)}')


if __name__ == '__main__':
    main()


# ─────────────────────────────────────────────────────────────────────────────
# KIỂM ĐỘC LẬP — không dùng lại tiêu đề, vì tiêu đề chính là thứ luật đã dùng.
#
# Dán nhãn tay bằng tiêu đề là VÒNG TRÒN: nó xác nhận lại đúng dữ kiện đã quyết
# định. Nên ở đây so NỘI DUNG: chữ trên trang SGV (và 2 trang kế) phải giống
# THÂN BÀI SGK được ghép hơn là giống một BÀI MỒI NHỬ khác trong cùng cuốn.
#
# Mồi nhử chọn TẤT ĐỊNH (bài xa nhất theo số hiệu) để không ai chọn hộ cho dễ.
# Ghép đúng ⇒ điểm thật > điểm mồi. Ghép sai ⇒ không.
def content_rank(sgv, sgk_book, lesson, page, sgk_bodies, span=3):
    """Bài được ghép xếp hạng MẤY khi so chữ trang SGV với MỌI bài của cuốn SGK.

    ⚠ Bản đầu dùng MỘT bài mồi nhử «xa nhất theo số hiệu» — và nó LỆCH HỆ
    THỐNG: với bài số lớn, mồi luôn rơi vào Bài 1, mà Bài 1 của Tin học là bài
    mở đầu đầy từ vựng chung nên thắng cả ghép đúng. Hai ca «trượt» hoá ra là
    ghép ĐÚNG (trang SGV mở đầu «BÀI 9. HIỆU ỨNG CHUYỂN TRANG»).

    Xếp hạng trên TOÀN BỘ bài thì không còn chỗ cho một mồi nhử may mắn.
    """
    body = []
    for p in _pages(sgv):
        pg = int(os.path.basename(p)[1:-5])
        if page <= pg < page + span:
            body += [l.get('text', '') for l in _page_lines(p)]
    T = toks(' '.join(body))
    les = sgk_bodies.get(sgk_book) or {}
    if not T or lesson not in les:
        return None
    j = lambda A: (len(T & A) / len(T | A)) if (T or A) else 0.0
    scored = sorted(((j(v), k) for k, v in les.items()), reverse=True)
    rank = next(i + 1 for i, (_, k) in enumerate(scored) if k == lesson)
    return dict(rank=rank, of=len(scored), score=round(j(les[lesson]), 4),
                top=scored[0][1], topScore=round(scored[0][0], 4))


def sgk_bodies():
    """Túi từ THÂN BÀI của từng bài SGK — dùng để đối chứng nội dung."""
    out = {}
    for p in sorted(glob.glob(os.path.join(PACK, 'lesson-index-g*.json'))):
        for r in json.load(open(p, encoding='utf-8')).get('lessonReadings') or []:
            txt = ' '.join(e.get('v') or '' for e in (r.get('content') or [])
                           if isinstance(e, dict) and e.get('t') in ('text', 'heading'))
            out.setdefault(r['book'], {})[r['lesson']] = toks(txt)
    return out
