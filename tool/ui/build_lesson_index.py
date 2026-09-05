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
localResearchOnly; build local vào APK dev).

WAL-210 (pre-autonomy audit gates G2/G3/G5):
  - mọi gắn-bài theo trang dùng tool/ui/lesson_attach (capped-toc-v1: cap 2.5×
    median, min 8; successor-unranged guard; TC-v2 header cross-check khi có
    dữ liệu) — trang ngoài phạm vi ⇒ KHÔNG gắn, KHÔNG phát hành (fail closed);
  - mọi hoạt động chỉ được mang số bài CÓ trong danh sách bài canonical của
    chính cuốn đó (identity gate) — sai ⇒ bỏ + đếm theo mã lý do;
  - pack mang `buildProvenance` (tool/ui/pack_provenance): builder version,
    git sha, cờ build, experimental, contentHash — `pack_provenance.py verify`
    là test «bản build mặc định» phía Python.
Log lý do: poc-out/b-lane/attach-log/lesson-index-g<N>.attach-log.json
(đổi thư mục bằng ATTACH_LOG_DIR)."""
import glob
import json, os, re, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lesson_attach import AttachRegistry  # noqa: E402
import pack_provenance  # noqa: E402

GRADE = int(sys.argv[1]) if len(sys.argv) > 1 else 5
ATTACH_LOG_DIR = os.environ.get('ATTACH_LOG_DIR', 'poc-out/b-lane/attach-log')

docs = json.load(open('poc-out/graph/curriculum-structure.json'))['documents']
# WAL-210: một sổ gắn-bài chung cho mọi họ hoạt động — mỗi quyết định có mã lý do.
ATT = AttachRegistry(docs)

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
            # WAL-210 identity gate: số bài phải có trong mục lục canonical của cuốn đó.
            if not ATT.check_upstream('toanExercises', e['book'], e['lesson'], e.get('printed'), note=e.get('expr')):
                continue
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
            # WAL-210 identity gate (TV5: 2 bài không có trong mục lục canonical ⇒ bỏ + đếm).
            if not ATT.check_upstream('tvReadings', book, lesson, p.get('pagePrinted'), note=p['id']):
                continue
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
            if not ATT.check_upstream('tvWritings', data['book'], u['lesson'], u.get('pagePrinted'), note=u['id']):
                continue
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
# WAL-210: gắn bài qua ATT.attach (capped-toc-v1) thay cho bảng «pageStart ≤ trang»
# không chặn trên; khối không gắn được ⇒ KHÔNG phát hành.

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
        les = ATT.attach('suSources', su_book, printed, pdf, note=' '.join(excerpt)[:60])
        if les['lesson'] is None:
            break                 # fail closed: không gắn được bài ⇒ không phát hành khối này
        su_sources.append(dict(
            book=su_book, page=printed, pagePdf=pdf,
            lesson=les['lesson'],
            lessonTitle=les['title'] or None,
            excerpt=re.sub(r'^TƯ LIỆU\.?\s*', '', ' '.join(excerpt)).strip(),
            attribution=' '.join(attrib).strip(),
            samGloss=SAM_GLOSS.get(pdf)))
        break                 # một khối mỗi trang là đủ cho slice

# ---- khoaExperiments (WAL-144 #KHTN): khối THÍ NGHIỆM thật từ Khoa học 5 ----
# Trang có cả «Chuẩn bị:» và «Tiến hành:» = một khối thí nghiệm SGK.
# Giữ VERBATIM (kể cả lỗi OCR nhỏ) — không viết lại lời sách.
EXPERIMENT_BOOKS = {  # môn × sách theo lớp — khối «Chuẩn bị/Dụng cụ + Tiến hành»
    4: [('Khoa học', '04-sgk-khoa-hoc-4')],
    5: [('Khoa học', '05-sgk-khoa-hoc-5')],
    6: [('KHTN', '06-sgk-khoa-hoc-tu-nhien-6')],
    7: [('KHTN', '07-sgk-khoa-hoc-tu-nhien-7')],
    8: [('KHTN', '08-sgk-khoa-hoc-tu-nhien-8')],
    9: [('KHTN', '09-sgk-khoa-hoc-tu-nhien-9')],
    10: [('Vật lí', '10-sgk-vat-li-10'), ('Hoá học', '10-sgk-hoa-hoc-10')],
}
# WAL-172: gắn khối thí nghiệm về bài bằng TRANG IN của CHÍNH CUỐN chứa nó.
# Bản trước dựng bảng trang→bài từ một cuốn Khoa học đóng cứng theo tên, nên
# Vật lí 10 và Hoá học 10 không bao giờ gắn được — cùng họ lỗi «hỏi tên môn»
# đã bỏ ở WAL-166. Nay mỗi cuốn tự có bảng của nó.
# WAL-210 (audit G2): bảng «pageStart ≤ trang» KHÔNG có chặn trên nên KHTN 8
# «Bài 22» (mục lục dừng ở bài 22/47) nuốt thí nghiệm của bài 24 và 28, và bài
# không có pageStart (Khoa học 4 Bài 2, Khoa học 5 Bài 4) bị bài trước nuốt.
# Nay dùng lesson_attach.capped-toc-v1; trang không gắn được ⇒ KHÔNG phát hành.

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
    # title: KHTN 6-9 tự đặt tên rõ «Thí nghiệm N: ...» ngay sát Chuẩn bị —
    # ưu tiên mốc này (tin cậy hơn) trước khi rơi về mốc «N. ...» cũ của tiểu
    # học, thứ vốn để bắt cả câu hỏi đánh số đứng trước — sai bài Vật lí 9
    # «Trong trường hợp thí nghiệm...» (thật ra là câu hỏi của TN trước) đã
    # lộ ra khi mở rộng sang KHTN 6-9.
    title = None
    for t in reversed(lines[max(0, i_cb - 6):i_cb]):
        m = re.match(r'^Thí nghiệm\s*\d*\s*[:.]\s*(\S.*)$', t)
        if m:
            title = m.group(1).strip()
            break
    if title is None:
        for t in reversed(lines[:i_cb]):
            if re.match(r'^\d+\.\s+\S', t):
                title = re.sub(r'^\d+\.\s+', '', t).strip()
                break
    steps, du_doan, quan_sat = [], None, None
    # KHTN 6-9: đôi khi bước đầu viết NGAY sau dấu hai chấm cùng dòng
    # («Tiến hành: Dùng panh kẹp...») thay vì xuống dòng rồi mới «- ...».
    inline = re.match(r'^Tiến hành\s*:\s*(\S.*)$', lines[i_th])
    if inline:
        steps.append(inline.group(1).strip())
    for t in lines[i_th + 1:i_th + 12]:
        # Fail closed: một nhãn hình/ký hiệu lạc trong vùng bước («- AgNO3»)
        # không phải một bước thật — bước thật luôn là một câu, nhiều từ.
        if t.startswith('- ') and len(t[2:].strip()) >= 10 and ' ' in t[2:].strip():
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
    les = ATT.attach('khoaExperiments', bk, printed, pdf, note=title[:60])
    if les['lesson'] is None:
        continue  # fail closed: trang ngoài phạm vi bài / bài mơ hồ ⇒ không phát hành
    khoa_experiments.append(dict(
        subject=subj,
        book=bk, page=printed, pagePdf=pdf,
        lesson=les['lesson'],
        lessonTitle=les['title'] or None,
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
    # WAL-210 identity gate: asset gắn bài thì bài phải có trong mục lục canonical.
    if a.get('lesson') is not None and a.get('sourceDocumentId') and not ATT.check_upstream(
            'sourceAssets', a['sourceDocumentId'], a['lesson'], a.get('pagePrinted'), note=a['asset']):
        print(f"  ⚠️ BỎ asset {a.get('asset')}: bài {a.get('lesson')} không có trong mục lục {a.get('sourceDocumentId')}")
        continue
    source_assets.append(dict(
        asset=a['asset'], subject=a['subject'],
        assetType=a.get('assetType', 'FIGURE'),
        sourceDocumentId=a.get('sourceDocumentId', ''),
        pagePdf=a['pagePdf'], pagePrinted=a.get('pagePrinted'),
        bboxFrac=a['bboxFrac'], extractionVersion=a['extraction'],
        printedCaption=a.get('printedCaption'), samGloss=a.get('samGloss'),
        lesson=a.get('lesson')))

# ---- WAL-204 pattern router (P0 falsification): Khoa học/KHTN 4-9 only ------
# Source → LearningActivity generically (TOC-range attach → directive pattern →
# route into EXISTING Surface shapes). Appends to tvReadings/tvWritings; never
# touches khoaExperiments (the 37-lesson regression oracle).
PATTERN_BOOKS = {
    4: [('Khoa học', '04-sgk-khoa-hoc-4')],
    5: [('Khoa học', '05-sgk-khoa-hoc-5')],
    6: [('KHTN', '06-sgk-khoa-hoc-tu-nhien-6')],
    7: [('KHTN', '07-sgk-khoa-hoc-tu-nhien-7')],
    8: [('KHTN', '08-sgk-khoa-hoc-tu-nhien-8')],
    9: [('KHTN', '09-sgk-khoa-hoc-tu-nhien-9')],
}
# Gated OFF by default after the WAL-204 device check: routed READ_TEXT passages
# from the generic extractor are column-scrambled on multi-column pages
# (unreadable). Enable only for experiments: PATTERN_ROUTER=1.
if PATTERN_BOOKS.get(GRADE) and os.environ.get('PATTERN_ROUTER') == '1':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pattern_router import route as _route_patterns
    _pr, _pw, _ps = _route_patterns(GRADE, PATTERN_BOOKS[GRADE], docs)
    tv_readings += _pr
    tv_writings += _pw
    print(f'  pattern-router: +{len(_pr)} readings, +{len(_pw)} writings — {dict(_ps)}')

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
# ---- WAL-210: provenance (audit G5) + reason-coded attachment log (G2/G3) --------
_flags = pack_provenance.read_flags()
out = pack_provenance.stamp(out, GRADE, _flags, __file__)
os.makedirs('assets/pack', exist_ok=True)
path = f'assets/pack/lesson-index-g{GRADE}.json'
json.dump(out, open(path, 'w'), ensure_ascii=False)
_att = ATT.summary()
try:
    os.makedirs(ATTACH_LOG_DIR, exist_ok=True)
    json.dump(dict(grade=GRADE, packVersion=out['buildProvenance']['packVersion'],
                   contentHash=out['buildProvenance']['contentHash'], summary=_att,
                   dropped=ATT.dropped, flagged=ATT.flagged),
              open(f'{ATTACH_LOG_DIR}/lesson-index-g{GRADE}.attach-log.json', 'w'),
              ensure_ascii=False, indent=1)
except OSError as e:
    print(f'  ⚠️ không ghi được attach-log ({e})')
_prov = out['buildProvenance']
print(f"  provenance: {_prov['packVersion']} {_prov['builderVersion']} flags={_prov['flags']} "
      f"experimental={_prov['experimental']} hash={_prov['contentHash'][:12]}…")
print(f"  attach ({_att['rule']}): dropped {_att['dropped']}, flagged {_att['flagged']} — "
      + '; '.join(f'{fam}: {reasons}' for fam, reasons in _att['counts'].items()))
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
