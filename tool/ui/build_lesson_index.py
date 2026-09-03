#!/usr/bin/env python3
"""WAL-136 + WAL-113 — lesson index cho UI từ DỮ LIỆU THẬT.
v2 (WAL-113 cross-subject): thêm
  - tvReadings: bài đọc-hiểu TV5 = SECTION_TEXT dài (đoạn văn thật) + các
    EXERCISE cùng bài ngay sau đó (câu hỏi mở, KHÔNG có đáp án trong SGK ⇒
    UI không được chấm — UNKNOWN ≠ SAI).
  - suSources: khối «TƯ LIỆU.» mined từ ocr-body Sử-Địa 5 — trích NGUYÊN VĂN
    + attribution in trong sách; samGloss là DIỄN GIẢI CỦA SAM (CURATED tay,
    không bao giờ trình bày như lời nguồn).
Output: assets/pack/lesson-index-g<N>.json — pack policy (gitignored,
localResearchOnly; build local vào APK dev)."""
import glob
import json, os, re, sys, collections

GRADE = int(sys.argv[1]) if len(sys.argv) > 1 else 5

docs = json.load(open('poc-out/graph/curriculum-structure.json'))['documents']

subjects = collections.defaultdict(list)
for d in docs:
    if d['docType'] != 'SGK' or d['grade'] != GRADE:
        continue
    lessons = [dict(no=les['number'], title=les.get('title'),
                    pageStart=les.get('pageStart'))
               for les in d.get('lessons', []) if les.get('number') is not None]
    if lessons:
        subjects[d['subject']].append(dict(
            sourceDocumentId=d['sourceDocumentId'],
            volume=d.get('volume'),
            lessons=sorted(lessons, key=lambda x: x['no'])))

ex_by_lesson = collections.defaultdict(list)
try:
    ec = json.load(open('poc-out/units/exercise-case-map.json'))
    items = ec if isinstance(ec, list) else ec.get('items', [])
    for e in items:
        if f'0{GRADE}-sgk-toan-{GRADE}' in e.get('book', '') and e.get('lesson') is not None:
            ex_by_lesson[e['lesson']].append(dict(
                expr=e['expr'], skillCaseId=e.get('skillCaseId'),
                page=e.get('printed'), book=e.get('book')))
except FileNotFoundError:
    pass

# ---- tvReadings (WAL-113 B1): đoạn văn + câu hỏi THẬT từ units TV ----------
MIN_PASSAGE = 400          # SECTION_TEXT ngắn = tiêu đề/lệnh, không phải bài đọc
Q_RE = re.compile(r'^\d+\.\s')
tv_readings = []
for path in sorted(glob.glob(f'poc-out/units/0{GRADE}-sgk-tieng-viet-{GRADE}-*.json')):
    data = json.load(open(path))
    book = data['book']
    units = data['units']
    by_lesson = collections.defaultdict(list)
    for u in units:
        if u.get('lesson') is not None:
            by_lesson[u['lesson']].append(u)
    for lesson, us in sorted(by_lesson.items()):
        passages = [u for u in us if u['role'] == 'SECTION_TEXT'
                    and len(u['text']) >= MIN_PASSAGE]
        for p in passages:
            qs = [dict(prompt=u['text'].strip(), page=u.get('pagePrinted'))
                  for u in us
                  if u['role'] == 'EXERCISE' and Q_RE.match(u['text'])
                  and p['pagePdf'] <= u['pagePdf'] <= p['pagePdf'] + 2
                  and len(u['text']) <= 300][:6]
            if not qs:
                continue          # đoạn văn không có câu hỏi đi kèm ⇒ bỏ, không bịa
            tv_readings.append(dict(
                book=book, lesson=lesson, page=p.get('pagePrinted'),
                passage=p['text'].strip(), questions=qs))

# ---- tvWritings (WAL-144 Essay): bài «Viết…» thật — đề + trang, KHÔNG mẫu ---
W_RE = re.compile(r'^\s*\d*\.?\s*(Viết|Dựa vào[^.]{0,80}viết)', re.U)
tv_writings = []
for path in sorted(glob.glob(f'poc-out/units/0{GRADE}-sgk-tieng-viet-{GRADE}-*.json')):
    data = json.load(open(path))
    for u in data['units']:
        if (u['role'] == 'EXERCISE' and u.get('lesson') is not None
                and W_RE.match(u['text']) and len(u['text']) <= 400):
            tv_writings.append(dict(
                book=data['book'], lesson=u['lesson'],
                page=u.get('pagePrinted'), prompt=u['text'].strip()))

# ---- suSources (WAL-113 B2): khối «TƯ LIỆU.» nguyên văn từ ocr-body Sử ------
# samGloss = DIỄN GIẢI CỦA SAM (curated tay, systemDerived) — UI phải dán nhãn
# «SAM diễn giải», KHÔNG BAO GIỜ render như lời của nguồn.
SAM_GLOSS = {
    20: 'Nguồn này cho biết: năm 1836, vua Minh Mạng cử Phạm Hữu Nhật ra quần '
        'đảo Hoàng Sa cắm cột mốc khắc rõ năm và tên người vâng mệnh — tức là '
        'triều Nguyễn đã thực thi chủ quyền ở Hoàng Sa từ thời đó.',
    43: 'Nguồn này cho thấy vua Lý Thái Tổ chọn thành Đại La vì thế đất rộng, '
        'cao, ở giữa bốn phương, thuận cho con cháu lâu dài — việc dời đô là '
        'một quyết định có tính toán, không phải ngẫu nhiên.',
}
su_book = f'0{GRADE}-sgk-lich-su-va-dia-li-{GRADE}'
su_lessons = []
for d in docs:
    if d['sourceDocumentId'] == su_book:
        su_lessons = sorted(
            [(l['pageStart'], l['number'], l.get('title'))
             for l in d.get('lessons', [])
             if l.get('pageStart') is not None and l.get('number') is not None])

def su_lesson_for(printed):
    hit = None
    for ps, no, title in su_lessons:
        if ps <= printed:
            hit = (no, title)
    return hit

su_sources = []
for f in sorted(glob.glob(f'poc-out/graph/ocr-body/{su_book}/p*.json')):
    j = json.load(open(f))
    lines = [l['text'] for l in j['lines']]
    pdf = int(re.search(r'p(\d+)\.json', f).group(1))
    for i, t in enumerate(lines):
        if not t.startswith('TƯ LIỆU'):
            continue
        excerpt, attrib, in_attrib = [], [], False
        for k in range(i, min(i + 15, len(lines))):
            ln = lines[k]
            if not in_attrib and ln.startswith('('):
                in_attrib = True
            if in_attrib:
                attrib.append(ln)
                if ln.rstrip().endswith(')'):
                    break
            else:
                excerpt.append(ln)
        else:
            if not in_attrib:
                continue      # không thấy attribution ⇒ fail closed, bỏ khối
        if not attrib or not attrib[-1].rstrip().endswith(')'):
            continue
        printed = int(lines[-1]) if lines[-1].strip().isdigit() else pdf - 2
        les = su_lesson_for(printed)
        su_sources.append(dict(
            book=su_book, page=printed, pagePdf=pdf,
            lesson=les[0] if les else None,
            lessonTitle=(les[1] or None) if les else None,
            excerpt=re.sub(r'^TƯ LIỆU\.?\s*', '', ' '.join(excerpt)).strip(),
            attribution=' '.join(attrib).strip(),
            samGloss=SAM_GLOSS.get(pdf)))
        break                 # một khối mỗi trang là đủ cho slice

# ---- khoaExperiments (WAL-144 #KHTN): khối THÍ NGHIỆM thật từ Khoa học 5 ----
# Trang có cả «Chuẩn bị:» và «Tiến hành:» = một khối thí nghiệm SGK.
# Giữ VERBATIM (kể cả lỗi OCR nhỏ) — không viết lại lời sách.
EXPERIMENT_BOOKS = {  # môn × sách theo lớp — khối «Chuẩn bị/Dụng cụ + Tiến hành»
    5: [('Khoa học', '05-sgk-khoa-hoc-5')],
    10: [('Vật lí', '10-sgk-vat-li-10'), ('Hoá học', '10-sgk-hoa-hoc-10')],
}
# WAL-172: gắn khối thí nghiệm về bài bằng TRANG IN của CHÍNH CUỐN chứa nó.
# Bản trước dựng bảng trang→bài từ một cuốn Khoa học đóng cứng theo tên, nên
# Vật lí 10 và Hoá học 10 không bao giờ gắn được — cùng họ lỗi «hỏi tên môn»
# đã bỏ ở WAL-166. Nay mỗi cuốn tự có bảng của nó.
_lesson_pages = {}
for d in docs:
    ls = sorted([(l['pageStart'], l['number'], l.get('title'))
                 for l in d.get('lessons', [])
                 if l.get('pageStart') is not None and l.get('number') is not None])
    if ls:
        _lesson_pages[d['sourceDocumentId']] = ls


def lesson_for(book, printed):
    """Bài chứa trang in này trong cuốn `book`. Không có bảng ⇒ None (fail
    closed): thà không gắn còn hơn gắn vào bài của cuốn khác."""
    hit = None
    for ps, no, title in _lesson_pages.get(book, ()):
        if ps <= printed:
            hit = (no, title)
    return hit

khoa_experiments = []
_exp_sources = []
for subj, bk in EXPERIMENT_BOOKS.get(GRADE, []):
    for f in sorted(glob.glob(f'poc-out/graph/ocr-body/{bk}/p*.json')):
        _exp_sources.append((subj, bk, f))
for subj, bk, f in _exp_sources:
    j = json.load(open(f))
    lines = [l['text'] for l in j['lines']]
    txt = '\n'.join(lines)
    # tiểu học: «Chuẩn bị:»; lớp 10: «Dụng cụ» — cùng vai trò chuẩn-bị.
    prep_key = 'Chuẩn bị:' if 'Chuẩn bị:' in txt else (
        'Dụng cụ' if 'Dụng cụ' in txt else None)
    if prep_key is None or 'Tiến hành' not in txt:
        continue
    pdf = int(re.search(r'p(\d+)\.json', f).group(1))
    i_cb = next(i for i, t in enumerate(lines) if prep_key in t)
    i_th = next((i for i, t in enumerate(lines[i_cb:], start=i_cb)
                 if 'Tiến hành' in t), None)
    if i_th is None:
        continue
    # title: dòng đánh-số gần nhất phía trên «Chuẩn bị:»
    title = None
    for t in reversed(lines[:i_cb]):
        if re.match(r'^\d+\.\s+\S', t):
            title = re.sub(r'^\d+\.\s+', '', t).strip()
            break
    steps, du_doan, quan_sat = [], None, None
    for t in lines[i_th + 1:i_th + 12]:
        if t.startswith('- '):
            steps.append(t[2:].strip())
        elif t.startswith('Dự đoán'):
            du_doan = t.strip()
        elif re.match(r'^(Sau .{0,30})?[Qq]uan sát', t):
            quan_sat = t.strip()
        elif t.startswith('?') or t.startswith('Hình'):
            break
    if not steps or title is None:
        continue  # khối không đọc được cấu trúc ⇒ bỏ, không bịa
    printed = int(lines[-1]) if lines[-1].strip().isdigit() else pdf - 1
    les = lesson_for(bk, printed) if printed is not None else None
    khoa_experiments.append(dict(
        subject=subj,
        book=bk, page=printed, pagePdf=pdf,
        lesson=les[0] if les else None,
        lessonTitle=(les[1] or None) if les else None,
        title=title,
        chuanBi=' '.join(x.strip() for x in lines[i_cb:i_th])
            .replace('Chuẩn bị:', '', 1).strip(),
        tienHanh=steps,
        duDoan=du_doan,
        quanSat=quan_sat))

# ---- diaMaps (WAL-144 #28 Địa): bản đồ SGK đã crop (human-curation) --------
# Câu hỏi VERBATIM từ trang khai thác hình (p013 trang in 11).
DIA_MAPS = [
    dict(subject='LS&ĐL', book='05-sgk-lich-su-va-dia-li-5', page=10,
         asset='map-ls-dia-5-p012-tu-nhien-vn.png',
         caption='Hình 1. Bản đồ tự nhiên Việt Nam',
         questions=[
             'Kể tên và xác định trên bản đồ một số khoáng sản ở nước ta.',
             'Nêu vai trò của tài nguyên khoáng sản đối với sự phát triển kinh tế.',
         ])
] if GRADE == 5 else []
# WAL-133: bản đồ chỉ được coi là SOURCE_ASSET khi CHỨNG MINH ĐƯỢC cách cắt.
# Registry crop giữ pagePdf/bboxFrac/extraction; thiếu bất kỳ thứ nào ⇒ BỎ bài
# đó, vì lúc ấy ta không còn cắt lại/kiểm chứng được và không được quyền nói
# với trẻ rằng «đây là hình trong sách».
_REG = 'poc-out/ui-assets/source-assets.json'  # WAL-133: registry CHUNG mọi môn
_reg = {}
if os.path.exists(_REG):
    for a in json.load(open(_REG)).get('assets', []):
        _reg[a.get('asset')] = a
dia_maps = []
for m in DIA_MAPS:
    if not os.path.exists(f"assets/pack/{m['asset']}"):
        continue  # asset chưa crop trên máy này
    r = _reg.get(m['asset'])
    if not r or not r.get('extraction') or r.get('pagePdf') is None \
            or len(r.get('bboxFrac') or []) != 4:
        print(f"  ⚠️ BỎ {m['asset']}: registry thiếu provenance crop")
        continue
    dia_maps.append(dict(m, pagePdf=r['pagePdf'], bboxFrac=r['bboxFrac'],
                         extractionVersion=r['extraction']))

# ---- books (WAL-167): manifest sách + bìa thật, để trẻ nhận ra cuốn sách ----
# Chỉ nhận sách CÓ bìa trên máy này VÀ có bài trong mục lục — sách không mở ra
# được cái gì thì không lên giá.
_COVERS = 'poc-out/ui-assets/book-covers.json'
_cov = {}
if os.path.exists(_COVERS):
    for b in json.load(open(_COVERS)).get('books', []):
        _cov[b.get('sourceDocumentId')] = b
_lessons_by_book = {}
for subj, blist in subjects.items():
    for b in blist:
        _lessons_by_book[b['sourceDocumentId']] = (subj, len(b['lessons']))
books = []
for sid, (subj, n) in sorted(_lessons_by_book.items()):
    c = _cov.get(sid)
    if not c or not os.path.exists(f"assets/pack/{c['cover']}"):
        print(f'  ⚠️ {sid}: chưa có bìa trên máy này ⇒ không lên giá sách')
        continue
    books.append(dict(sourceDocumentId=sid, subject=subj, grade=GRADE,
                      volume=c.get('volume'), title=c.get('title'),
                      volumeLabel=c.get('volumeLabel'), cover=c['cover'],
                      bookSeries=c.get('bookSeries'), lessonCount=n,
                      pageCount=c.get('pageCount')))

# ---- sourceAssets (WAL-133): hình SGK đã crop, provenance đầy đủ ----------
# Chỉ nhận asset CÓ MẶT trên máy này và ĐỦ provenance; thiếu ⇒ bỏ, không để UI
# hứa một hình không dựng lại được.
source_assets = []
for a in _reg.values():
    if not os.path.exists(f"assets/pack/{a.get('asset','')}"):
        continue
    if a.get('pagePdf') is None or len(a.get('bboxFrac') or []) != 4 \
            or not a.get('extraction') or not a.get('subject'):
        print(f"  ⚠️ BỎ asset {a.get('asset')}: thiếu provenance")
        continue
    source_assets.append(dict(
        asset=a['asset'], subject=a['subject'],
        assetType=a.get('assetType', 'FIGURE'),
        sourceDocumentId=a.get('sourceDocumentId', ''),
        pagePdf=a['pagePdf'], pagePrinted=a.get('pagePrinted'),
        bboxFrac=a['bboxFrac'], extractionVersion=a['extraction'],
        printedCaption=a.get('printedCaption'), samGloss=a.get('samGloss'),
        lesson=a.get('lesson')))

for v in subjects.values():
    v.sort(key=lambda b: (b['volume'] or '9', b['sourceDocumentId']))
out = dict(grade=GRADE, version='lesson-index-v2',
           subjects={k: v for k, v in sorted(subjects.items())},
           toanExercises={str(k): v for k, v in sorted(ex_by_lesson.items())},
           tvReadings=tv_readings,
           tvWritings=tv_writings,
           suSources=su_sources,
           khoaExperiments=khoa_experiments,
           diaMaps=dia_maps,
           sourceAssets=source_assets,
           books=books)
os.makedirs('assets/pack', exist_ok=True)
path = f'assets/pack/lesson-index-g{GRADE}.json'
json.dump(out, open(path, 'w'), ensure_ascii=False)
n_les = sum(len(l['lessons']) for v in subjects.values() for l in v)
print(f'{path}: {len(subjects)} môn, {n_les} bài, exToán '
      f'{sum(len(v) for v in ex_by_lesson.values())}, '
      f'tvReadings {len(tv_readings)}, tvWritings {len(tv_writings)}, '
      f'suSources {len(su_sources)}, khoaExperiments {len(khoa_experiments)}, '
      f'diaMaps {len(dia_maps)}, '
      f'books {len(books)}, '
      f'sourceAssets {len(source_assets)} '
      f'({len({a["subject"] for a in source_assets})} môn)')
for r in tv_readings[:3]:
    print('  TV:', r['book'][-7:], 'L', r['lesson'], 'p', r['page'],
          len(r['questions']), 'câu hỏi —', r['passage'][:50])
for s in su_sources:
    print('  SỬ: bài', s['lesson'], repr((s['lessonTitle'] or '')[:30]),
          'tr.', s['page'], '—', s['excerpt'][:50], '| gloss:', bool(s['samGloss']))
