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
kh_book = f'0{GRADE}-sgk-khoa-hoc-{GRADE}'
kh_lessons = []
for d in docs:
    if d['sourceDocumentId'] == kh_book:
        kh_lessons = sorted(
            [(l['pageStart'], l['number'], l.get('title'))
             for l in d.get('lessons', [])
             if l.get('pageStart') is not None and l.get('number') is not None])

def kh_lesson_for(printed):
    hit = None
    for ps, no, title in kh_lessons:
        if ps <= printed:
            hit = (no, title)
    return hit

khoa_experiments = []
for f in sorted(glob.glob(f'poc-out/graph/ocr-body/{kh_book}/p*.json')):
    j = json.load(open(f))
    lines = [l['text'] for l in j['lines']]
    txt = '\n'.join(lines)
    if 'Chuẩn bị:' not in txt or 'Tiến hành:' not in txt:
        continue
    pdf = int(re.search(r'p(\d+)\.json', f).group(1))
    # OCR có thể dính «Chuẩn bị:» giữa dòng — dò bằng chứa, không startswith.
    i_cb = next(i for i, t in enumerate(lines) if 'Chuẩn bị:' in t)
    i_th = next(i for i, t in enumerate(lines) if 'Tiến hành' in t)
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
    les = kh_lesson_for(printed)
    khoa_experiments.append(dict(
        book=kh_book, page=printed, pagePdf=pdf,
        lesson=les[0] if les else None,
        lessonTitle=(les[1] or None) if les else None,
        title=title,
        chuanBi=' '.join(x.strip() for x in lines[i_cb:i_th]).replace('Chuẩn bị:', '', 1).strip(),
        tienHanh=steps,
        duDoan=du_doan,
        quanSat=quan_sat))

for v in subjects.values():
    v.sort(key=lambda b: (b['volume'] or '9', b['sourceDocumentId']))
out = dict(grade=GRADE, version='lesson-index-v2',
           subjects={k: v for k, v in sorted(subjects.items())},
           toanExercises={str(k): v for k, v in sorted(ex_by_lesson.items())},
           tvReadings=tv_readings,
           tvWritings=tv_writings,
           suSources=su_sources,
           khoaExperiments=khoa_experiments)
os.makedirs('assets/pack', exist_ok=True)
path = f'assets/pack/lesson-index-g{GRADE}.json'
json.dump(out, open(path, 'w'), ensure_ascii=False)
n_les = sum(len(l['lessons']) for v in subjects.values() for l in v)
print(f'{path}: {len(subjects)} môn, {n_les} bài, exToán '
      f'{sum(len(v) for v in ex_by_lesson.values())}, '
      f'tvReadings {len(tv_readings)}, tvWritings {len(tv_writings)}, '
      f'suSources {len(su_sources)}, khoaExperiments {len(khoa_experiments)}')
for r in tv_readings[:3]:
    print('  TV:', r['book'][-7:], 'L', r['lesson'], 'p', r['page'],
          len(r['questions']), 'câu hỏi —', r['passage'][:50])
for s in su_sources:
    print('  SỬ: bài', s['lesson'], repr((s['lessonTitle'] or '')[:30]),
          'tr.', s['page'], '—', s['excerpt'][:50], '| gloss:', bool(s['samGloss']))
