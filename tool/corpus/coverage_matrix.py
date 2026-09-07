#!/usr/bin/env python3
"""FULL CORPUS COVERAGE MATRIX — sinh từ DỮ LIỆU THẬT, không bảo trì tay.

    python3 tool/corpus/coverage_matrix.py --attach <attach-root> [--json OUT] [--csv OUT]

⭐ MẪU SỐ LÀ MỤC LỤC CANONICAL (`assets/pack/lesson-index-g<N>.json`), không phải
số bài pipeline sinh ra được. Đo pipeline bằng mẫu số của chính pipeline là tự
chấm điểm mình.

⭐ ĐO ĐỘC LẬP TỪNG TẦNG. WAL-137 đã chứng minh `TSL EXISTS != VISUAL AVAILABLE`;
cùng lỗi ấy lặp lại nếu suy «có dải trang ⇒ đọc được» hay «có unit ⇒ có nội dung».
Mỗi tầng dưới đây đọc nguồn của riêng nó:

    định danh   ← mục lục + tiêu đề attach TRÍCH TỪ TRANG SÁCH
    dải trang   ← attach (offset trang in→PDF đã hiệu chỉnh)
    đọc được    ← OCR thật của đúng dải trang ấy
    semantic    ← fixture do cầu TSL sinh
    kịch bản    ← tool/corpus/tutor_scripts/

BA MỨC (lệnh Founder, phase FULL DATA 1–12):
    L1 READABLE     định danh đúng + dải đúng + đủ chữ để đọc
    L2 VISUAL READY L1 + semantic dùng được
    L3 SAM READY    L2 + kịch bản dạy đã soạn

READ-ONLY LÀ TRẠNG THÁI HỢP LỆ. Bài không lên được L2/L3 vẫn là bài trẻ mở được;
nó KHÔNG phải lỗi và không bị trừ khỏi L1.

⚠ KHÔNG DÙNG `(book, lessonNo)` LÀM ĐỊNH DANH. Đo được trên corpus này: 439 bản
ghi va chạm dưới khoá ấy, và `volume` không cứu được bản nào — đánh số reset theo
chủ đề (Tin học 9 có hai «Bài 9»; GDTC có «Bài 1» cho mỗi môn thể thao). Nối nhầm
hai bài để tăng coverage nghĩa là cho trẻ mở nhầm bài. Khoá ở đây là
`(book, no, pageStart)`; phần còn lại được đánh dấu AMBIGUOUS_IDENTITY, KHÔNG bị
im lặng gộp.
"""
import argparse
import collections
import csv
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')
TUTOR_SCRIPTS = os.path.join(ROOT, 'tool/corpus/tutor_scripts')

# Chữ tối thiểu để gọi là ĐỌC ĐƯỢC. Trung vị đo được là ~5.400 ký tự/bài, p10 ~1.280;
# 300 nằm dưới p10 rất xa nên nó loại trang trắng/trang bìa chứ không loại bài thật.
MIN_CHARS = 300

# Họ nguyên nhân — dùng để xếp theo BLAST RADIUS, không phải để dán nhãn cho đẹp.
NO_RANGE = 'SOURCE_RANGE'
NO_TITLE = 'LESSON_IDENTITY_TITLE'
AMBIG = 'LESSON_IDENTITY_AMBIGUOUS'
THIN = 'CONTENT_THIN'
UNCONFIRMED = 'IDENTITY_UNCONFIRMED'


def canonical_lessons():
    """Mẫu số: mọi bài trong mục lục canonical, giữ nguyên bản ghi trùng."""
    out = []
    for g in range(1, 13):
        p = os.path.join(ROOT, f'assets/pack/lesson-index-g{g}.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for subject, books in (d.get('subjects') or {}).items():
            for b in books:
                for L in b.get('lessons') or []:
                    out.append(dict(grade=g, subject=subject, book=b['sourceDocumentId'],
                                    volume=b.get('volume'), no=L.get('no'),
                                    title=(L.get('title') or '').strip(),
                                    page_start=L.get('pageStart')))
    return out


def attach_index(attach_root):
    """Bài attach đã gắn được vào trang, theo (book, no) → bản ghi."""
    idx = {}
    for p in glob.glob(os.path.join(attach_root, 'attach', '*.json')):
        d = json.load(open(p, encoding='utf-8'))
        pages = len(d.get('pages') or [])
        Ls = sorted([L for L in d.get('lessons') or [] if L.get('page_pdf')],
                    key=lambda x: x['page_pdf'])
        for i, L in enumerate(Ls):
            s = L['page_pdf']
            e = (Ls[i + 1]['page_pdf'] - 1) if i + 1 < len(Ls) else pages
            idx[(d['book'], L['number'])] = dict(
                page_pdf=s, page_end=max(s, min(e, pages)),
                title=(L.get('title') or '').strip(),
                source=L.get('source'), confidence=L.get('confidence') or 0.0)
    return idx


_page_cache = {}


def page_chars(book, pdf_page):
    k = (book, pdf_page)
    if k not in _page_cache:
        try:
            lines = json.load(open(f'{OCR}/{book}/p{pdf_page:03d}.json', encoding='utf-8'))['lines']
            _page_cache[k] = sum(len(x.get('text') or '') for x in lines)
        except Exception:
            _page_cache[k] = None
    return _page_cache[k]


def semantic_index(fixture_dirs):
    """Bài có `semantic` KHÔNG RỖNG trong fixture — đọc fixture, không suy từ TSL."""
    have = set()
    for d in fixture_dirs:
        for p in glob.glob(os.path.join(d, '*.json')):
            try:
                f = json.load(open(p, encoding='utf-8'))
            except Exception:
                continue
            if f.get('semantic'):
                have.add((f.get('book'), f.get('lesson')))
    return have


def tutor_index(script_dir=TUTOR_SCRIPTS):
    have = set()
    for p in glob.glob(os.path.join(script_dir, '*.json')):
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception:
            continue
        if d.get('steps'):
            have.add((d.get('book'), d.get('lesson')))
    return have


def build(attach_root, fixture_dirs):
    rows = canonical_lessons()
    att = attach_index(attach_root)
    sem = semantic_index(fixture_dirs)
    tut = tutor_index()

    seen = collections.Counter((r['book'], r['no'], r['page_start']) for r in rows)
    dup_key = {k for k, n in seen.items() if n > 1}

    out = []
    for r in rows:
        a = att.get((r['book'], r['no'])) or {}
        blockers = []
        # Định danh: tên bài — mục lục trước, nếu rỗng thì lấy tên attach ĐỌC TỪ TRANG.
        title = r['title'] or a.get('title') or ''
        title_from = 'index' if r['title'] else ('page' if a.get('title') else None)
        if (r['book'], r['no'], r['page_start']) in dup_key:
            blockers.append(AMBIG)
        if not title:
            blockers.append(NO_TITLE)
        # Dải trang
        if not a.get('page_pdf'):
            blockers.append(NO_RANGE)
            chars = 0
        else:
            chars = 0
            for pp in range(a['page_pdf'], a['page_end'] + 1):
                c = page_chars(r['book'], pp)
                if c:
                    chars += c
            if chars < MIN_CHARS:
                blockers.append(THIN)
        # Định danh chưa được TRANG SÁCH xác nhận: mục lục nói vậy, sách chưa nói vậy.
        if a and a.get('source') not in ('both', 'header'):
            blockers.append(UNCONFIRMED)

        l1 = not [b for b in blockers if b != UNCONFIRMED]
        l1_confirmed = l1 and UNCONFIRMED not in blockers
        key = (r['book'], r['no'])
        l2 = l1 and key in sem
        l3 = l2 and key in tut
        out.append(dict(**r, title_resolved=title, title_from=title_from,
                        page_pdf=a.get('page_pdf'), page_end=a.get('page_end'),
                        attach_source=a.get('source'), chars=chars,
                        blockers=blockers, L1=l1, L1_confirmed=l1_confirmed, L2=l2, L3=l3))
    return out


def summarise(rows):
    n = len(rows)
    s = dict(canonical=n,
             L1=sum(r['L1'] for r in rows),
             L1_confirmed=sum(r['L1_confirmed'] for r in rows),
             L2=sum(r['L2'] for r in rows),
             L3=sum(r['L3'] for r in rows))
    by_grade = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        c = by_grade[r['grade']]
        c['n'] += 1
        for k in ('L1', 'L1_confirmed', 'L2', 'L3'):
            c[k] += bool(r[k])
    blockers = collections.Counter()
    for r in rows:
        if r['L1']:
            continue
        for b in r['blockers']:
            if b != UNCONFIRMED:
                blockers[b] += 1
    return s, by_grade, blockers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--attach', required=True, help='thư mục gốc chứa attach/<book>.json')
    ap.add_argument('--fixtures', nargs='*', default=[os.path.join(ROOT, 'assets/fixtures/real'),
                                                     os.path.join(ROOT, 'assets/fixtures/synthetic')])
    ap.add_argument('--json', default=None)
    ap.add_argument('--csv', default=None)
    a = ap.parse_args()

    rows = build(a.attach, a.fixtures)
    s, by_grade, blockers = summarise(rows)

    print(f"DATA — mẫu số canonical: {s['canonical']:,} bài\n")
    for k, label in (('L1', 'Level 1 READABLE'), ('L1_confirmed', '  ├ trang sách xác nhận'),
                     ('L2', 'Level 2 VISUAL READY'), ('L3', 'Level 3 SAM READY')):
        print(f"  {label:<26} {s[k]:>6,} / {s['canonical']:,} = {s[k]/s['canonical']:6.1%}")
    print(f"\n{'lớp':>4} {'bài':>5} {'L1':>6} {'%':>7} {'xácnhận':>8} {'L2':>5} {'L3':>4}")
    for g in sorted(by_grade):
        c = by_grade[g]
        print(f"{g:>4} {c['n']:>5} {c['L1']:>6} {c['L1']/c['n']:>6.1%} "
              f"{c['L1_confirmed']:>8} {c['L2']:>5} {c['L3']:>4}")
    print('\nTOP BLOCKERS (bài bị chặn khỏi Level 1):')
    for i, (b, cnt) in enumerate(blockers.most_common(), 1):
        print(f'  {i}. {b:<28} → {cnt:,} bài')

    if a.json:
        json.dump(dict(summary=s, by_grade={str(k): dict(v) for k, v in by_grade.items()},
                       blockers=dict(blockers), rows=rows),
                  open(a.json, 'w', encoding='utf-8'), ensure_ascii=False)
        print(f'\n→ {a.json}')
    if a.csv:
        cols = ['grade', 'subject', 'book', 'no', 'title_resolved', 'title_from', 'page_start',
                'page_pdf', 'page_end', 'attach_source', 'chars', 'L1', 'L1_confirmed', 'L2', 'L3']
        with open(a.csv, 'w', encoding='utf-8', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(cols + ['blockers'])
            for r in rows:
                w.writerow([r.get(c) for c in cols] + ['|'.join(r['blockers'])])
        print(f'→ {a.csv}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
