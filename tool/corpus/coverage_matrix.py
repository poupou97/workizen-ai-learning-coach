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

CÁC MỨC (lệnh Founder, phase FULL DATA 1–12 + MULTIMODAL READ):
    L1-T  TEXT READABLE       định danh đúng + dải đúng + đủ chữ để đọc
    L1-M  MULTIMODAL READABLE L1-T + nội dung HÌNH cần thiết cũng tới được trẻ
    OPENABLE                  bài có đường mở THẬT trong app (pack có nội dung đọc)
    L2    VISUAL READY        L1-T + semantic dùng được
    L3    SAM READY           L2 + kịch bản dạy đã soạn

⚠ MỘT CON SỐ «READABLE» LÀ GÂY HIỂU NHẦM. Founder dogfood 2.589 bài «mở được»
và thấy chúng CHỈ CÓ CHỮ — hình, sơ đồ, bảng của sách không tới được trẻ. Bài
đọc được phần chữ mà mất hình thì với môn có hình là mất phần lớn nội dung, nên
L1-T và L1-M phải đứng riêng, không gộp.

Bài mà SÁCH VỐN KHÔNG CÓ hình cần thiết thì text-only vẫn đạt L1-M — thiếu thứ
không tồn tại không phải là thiếu.

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


INDEX_DIR = os.path.join(ROOT, 'assets/pack')


def canonical_lessons(index_dir=INDEX_DIR):
    """Mẫu số: mọi bài trong mục lục canonical, giữ nguyên bản ghi trùng.

    `index_dir` tiêm được: mục lục dựng tại máy và KHÔNG nằm trong git, nên một
    test đọc thẳng nó sẽ xanh ở máy dev và đỏ trên CI — hoặc tệ hơn, xanh RỖNG
    vì không có dữ liệu để khẳng định gì.
    """
    out = []
    for g in range(1, 13):
        p = os.path.join(index_dir, f'lesson-index-g{g}.json')
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


def openable_index(index_dir=INDEX_DIR):
    """Bài có đường mở THẬT trong app: pack mang nội dung đọc của CHÍNH bài ấy.

    ⚠ HAI NGUỒN DẢI TRANG, VÀ ĐÓ LÀ CHỦ Ý. `L1-T` ở đây đo theo dải của ATTACH;
    bộ dựng pack còn tìm thêm dải cho bài mà mục lục không ghi trang
    (`unit_locator`). Nên `OPENABLE` có thể VƯỢT con số suy ra từ `L1-T` — đo
    được: đúng 30 bài. Chênh ấy có giải thích, không phải đếm nống.

    Giữ định nghĩa `L1-T` nguyên như cũ thay vì nới nó theo bộ dựng: một metric
    đổi định nghĩa giữa chừng thì mọi so sánh giữa các vòng thành vô nghĩa.

    ⚠ KHOÁ PHẢI GỒM TRANG MỞ BÀI. Tra bằng `(sách, số bài)` thì MỘT mục pack sẽ
    đánh dấu MỌI bản ghi trùng số là mở được — kể cả bản thuộc chương khác mà
    pack cố ý giữ lại. Đo được: sai lệch nống con số lên 2.961 trong khi pack
    chỉ có 2.858 mục. Đếm nống chính là cách một census tự chấm điểm mình.
    """
    out = {}
    for g in range(1, 13):
        p = os.path.join(index_dir, f'lesson-index-g{g}.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for r in d.get('lessonReadings') or []:
            imgs = [i for i in (r.get('content') or []) if i.get('t') == 'img']
            out[(r.get('book'), r.get('lesson'), r.get('pageStart'))] = \
                dict(packed=len(imgs))
    return out


def source_visuals(book, page_pdf, page_end, pdf_path):
    """Số vùng HÌNH NỘI DUNG mà chính trang sách của bài có.

    Đây là tầng «detected» — đo trên nguồn, KHÔNG suy từ việc pack có gì. Suy
    ngược lại là tự chấm điểm mình: pack rỗng sẽ thành «sách vốn không có hình».
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from lesson_figures import page_ink_regions, classify
    n = 0
    for pp in range(page_pdf, page_end + 1):
        try:
            with open(f'{OCR}/{book}/p{pp:03d}.json', encoding='utf-8') as fh:
                lines = json.load(fh)['lines']
        except (OSError, ValueError, KeyError):
            continue
        try:
            n += sum(1 for r in page_ink_regions(pdf_path, pp, lines)
                     if classify(r) == 'content')
        except Exception:
            return None          # PDF không đọc được ⇒ KHÔNG kết luận «không có hình»
    return n


def pdf_map():
    import glob
    m = {}
    for p in glob.glob(os.path.join(ROOT, 'poc-out/pdf/*/*.pdf')):
        m[os.path.basename(p)[:-4]] = p
    for p in glob.glob(os.path.join(ROOT, 'poc-out/pdf/*.pdf')):
        m.setdefault(os.path.basename(p)[:-4], p)
    return m


def build(attach_root, fixture_dirs, index_dir=INDEX_DIR, with_visuals=False,
          visual_counter=None):
    """`visual_counter(book, start, end, pdf) -> int | None` tiêm được cho test:
    đếm hình thật phải dựng ảnh từng trang, không chạy trong unit test."""
    rows = canonical_lessons(index_dir)
    att = attach_index(attach_root)
    sem = semantic_index(fixture_dirs)
    tut = tutor_index()
    opened = openable_index(index_dir)
    pdfs = pdf_map() if with_visuals else {}

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
        op = opened.get((r['book'], r['no'], r['page_start']))
        packed = op['packed'] if op else 0

        # L1-M: hình CẦN THIẾT của sách có tới được trẻ không.
        detected = None
        if with_visuals and l1 and a.get('page_pdf') and (visual_counter or r['book'] in pdfs):
            detected = (visual_counter or source_visuals)(
                r['book'], a['page_pdf'], a['page_end'], pdfs.get(r['book']))
        # `None` = chưa đo được ⇒ KHÔNG kết luận đạt. Sách vốn không có hình
        # (detected == 0) thì text-only đã là đủ nội dung.
        l1m = bool(l1 and op is not None and detected is not None
                   and packed >= detected)
        out.append(dict(**r, title_resolved=title, title_from=title_from,
                        page_pdf=a.get('page_pdf'), page_end=a.get('page_end'),
                        attach_source=a.get('source'), chars=chars,
                        blockers=blockers, L1=l1, L1_confirmed=l1_confirmed,
                        openable=op is not None, visuals_detected=detected,
                        visuals_packed=packed, L1M=l1m, L2=l2, L3=l3))
    return out


def summarise(rows):
    n = len(rows)
    measured = [r for r in rows if r['visuals_detected'] is not None]
    s = dict(canonical=n,
             L1T=sum(r['L1'] for r in rows),
             L1T_confirmed=sum(r['L1_confirmed'] for r in rows),
             L1M=sum(r['L1M'] for r in rows),
             openable=sum(r['openable'] for r in rows),
             L2=sum(r['L2'] for r in rows),
             L3=sum(r['L3'] for r in rows),
             visual_measured=len(measured),
             lessons_with_source_visuals=sum(1 for r in measured if r['visuals_detected']),
             visuals_detected=sum(r['visuals_detected'] for r in measured),
             visuals_packed=sum(r['visuals_packed'] for r in rows))
    by_grade = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        c = by_grade[r['grade']]
        c['n'] += 1
        for k in ('L1', 'L1_confirmed', 'L1M', 'openable', 'L2', 'L3'):
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
    ap.add_argument('--index-dir', default=INDEX_DIR)
    ap.add_argument('--visuals', action='store_true',
                    help='đo tầng hình (chậm: dựng ảnh từng trang ~0,03s)')
    ap.add_argument('--json', default=None)
    ap.add_argument('--csv', default=None)
    a = ap.parse_args()

    rows = build(a.attach, a.fixtures, a.index_dir, with_visuals=a.visuals)
    s, by_grade, blockers = summarise(rows)

    print(f"DATA — mẫu số canonical: {s['canonical']:,} bài\n")
    for k, label in (('L1T', 'L1-T  TEXT READABLE'),
                     ('L1T_confirmed', '  ├ trang sách xác nhận'),
                     ('L1M', 'L1-M  MULTIMODAL READABLE'),
                     ('openable', 'PRODUCT OPENABLE'),
                     ('L2', 'L2    VISUAL READY'),
                     ('L3', 'L3    SAM READY')):
        print(f"  {label:<28} {s[k]:>6,} / {s['canonical']:,} = {s[k]/s['canonical']:6.1%}")
    if s['visual_measured']:
        print(f"\nMULTIMODAL (đo được trên {s['visual_measured']:,} bài L1-T):")
        print(f"  bài SÁCH CÓ hình         {s['lessons_with_source_visuals']:>6,}")
        print(f"  hình detected            {s['visuals_detected']:>6,}")
        print(f"  hình packed (vào sản phẩm){s['visuals_packed']:>5,}")
    print(f"\n{'lớp':>4} {'bài':>5} {'L1-T':>6} {'%':>7} {'L1-M':>6} {'mở':>6} {'L2':>4} {'L3':>4}")
    for g in sorted(by_grade):
        c = by_grade[g]
        print(f"{g:>4} {c['n']:>5} {c['L1']:>6} {c['L1']/c['n']:>6.1%} "
              f"{c['L1M']:>6} {c['openable']:>6} {c['L2']:>4} {c['L3']:>4}")
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
                'page_pdf', 'page_end', 'attach_source', 'chars', 'L1', 'L1_confirmed',
                'L1M', 'openable', 'visuals_detected', 'visuals_packed', 'L2', 'L3']
        with open(a.csv, 'w', encoding='utf-8', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(cols + ['blockers'])
            for r in rows:
                w.writerow([r.get(c) for c in cols] + ['|'.join(r['blockers'])])
        print(f'→ {a.csv}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
