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
  - mọi gắn-bài theo trang dùng tool/ui/lesson_attach (capped-toc-v2: cap 2.5×
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
from experiment_steps import step_body, is_real_step, continues_step
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'corpus'))
from lesson_reading import lesson_reading  # noqa: E402

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
# ---- Founder §3 (2026-09-06): NON-VERBATIM UPSTREAM RECORDS FAIL CLOSED ---------------------
# `poc-out/units/exercise-case-map.json` is written by tool/extract/rebuild_fractions.py, which
# stamps every row `status: INFERRED`, `method: geometric-fraction-rebuild-v1` — «dựng từ hình học
# ⇒ KHÔNG phải nguyên văn». All 41 rows carry it. This builder used to copy only
# expr/skillCaseId/page/book into the pack, so the INFERRED marker and the method were DROPPED and
# 41 expressions rebuilt from geometry shipped as if they were printed in the book — carrying a
# skillCaseId, i.e. feeding the exercise path a child is taught from. It is the same family as the
# `b) 3/10 + 5/21` → `b) 10 +` defect the legacy audit found.
#
# Founder: «Preserve status/provenance or fail closed. Do not silently construct mathematical truth
# from geometry.» The pack schema has no provenance field for an activity and the app has no way to
# show an INFERRED caveat, so FAIL CLOSED is the choice here: a non-verbatim upstream record is not
# emitted at all. Every drop is counted and logged by reason — nothing is deleted upstream, and the
# rows come back the moment provenance can travel with them.
VERBATIM_STATUSES = ('', 'VERBATIM', 'PRINTED', 'ORIGINAL')
_dropped_non_verbatim = []
try:
    ec = json.load(open('poc-out/units/exercise-case-map.json'))
    items = ec if isinstance(ec, list) else ec.get('items', [])
    for e in items:
        if f'0{GRADE}-sgk-toan-{GRADE}' in e.get('book', '') and e.get('lesson') is not None:
            status = (e.get('status') or '').strip().upper()
            if status not in VERBATIM_STATUSES:
                _dropped_non_verbatim.append(dict(
                    book=e.get('book'), lesson=e.get('lesson'), page=e.get('printed'),
                    skillCaseId=e.get('skillCaseId'), conceptId=e.get('conceptId'),
                    status=status, method=e.get('method'),
                    reason='upstream record is not verbatim and the pack carries no provenance field '
                           'for it — fail closed (Founder §3)'))
                continue
            # WAL-210 identity gate: số bài phải có trong mục lục canonical của cuốn đó.
            if not ATT.check_upstream('toanExercises', e['book'], e['lesson'], e.get('printed'), note=e.get('expr')):
                continue
            ex_by_lesson[e['lesson']].append(dict(
                expr=e['expr'], skillCaseId=e.get('skillCaseId'),
                page=e.get('printed'), book=e.get('book')))
except FileNotFoundError:
    pass
if _dropped_non_verbatim:
    _by_lesson = collections.Counter((d['book'], d['lesson']) for d in _dropped_non_verbatim)
    print(f'  ⛔ toanExercises: {len(_dropped_non_verbatim)} non-verbatim upstream record(s) NOT emitted '
          f'(fail closed, Founder §3) across {len(_by_lesson)} lesson(s): '
          + ', '.join(f'{b} B{l}×{n}' for (b, l), n in sorted(_by_lesson.items())))

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
# WAL-210: gắn bài qua ATT.attach (capped-toc-v2) thay cho bảng «pageStart ≤ trang»
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
    # ⛔ GDTC 6 KHÔNG ĐƯỢC THÊM VÀO ĐÂY, dù nó là ứng viên hấp dẫn nhất.
    #
    # Cấu trúc khớp hoàn hảo — «Chuẩn bị:» + «Thực hiện:» trên 44 trang, gấp
    # 2,7 lần toàn bộ KHTN 6 — và bộ trích đọc ra tên trò chơi thật («Tung và
    # bắt bóng», «Ôm bóng chạy tiếp sức»). Nhưng ĐỊNH DANH BÀI thì hỏng:
    #
    #   mục lục GDTC 6 có 24 mục mà chỉ 4 SỐ BÀI — «Bài 1» xuất hiện 7 lần,
    #   «Bài 2» 7 lần, «Bài 3» 7 lần. Mỗi chủ đề đánh số lại từ đầu.
    #
    # App địa chỉ hoá hoạt động bằng `(sách, số bài)`. Thêm GDTC vào đây thì
    # trẻ mở «Bài 1» của chủ đề 1 (trang 8, thể dục) sẽ thấy trò bóng rổ ở
    # trang 93 — NỘI DUNG SAI hiện cho trẻ. Không đánh đổi độ phủ lấy điều đó.
    #
    # Muốn mở GDTC phải đưa CHỦ ĐỀ vào khoá định danh bài — đổi mô hình ở cả
    # pack lẫn Dart lẫn lớp gắn bài. Đó là việc thật, không phải cheap win.
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
# Nay dùng lesson_attach.capped-toc-v2; trang không gắn được ⇒ KHÔNG phát hành.

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
    # Mốc HÀNH ĐỘNG khác nhau theo môn: KHTN «Tiến hành», GDTC «Thực hiện».
    act_key = next((k for k in ('Tiến hành', 'Thực hiện') if k in txt), None)
    if prep_key is None or act_key is None:
        continue
    pdf = int(re.search(r'p(\d+)\.json', f).group(1))
    i_cb = next(i for i, t in enumerate(lines) if prep_key in t)
    i_th = next((i for i, t in enumerate(lines[i_cb:], start=i_cb)
                 if act_key in t), None)
    if i_th is None:
        continue
    # title: KHTN 6-9 tự đặt tên rõ «Thí nghiệm N: ...» ngay sát Chuẩn bị —
    # ưu tiên mốc này (tin cậy hơn) trước khi rơi về mốc «N. ...» cũ của tiểu
    # học, thứ vốn để bắt cả câu hỏi đánh số đứng trước — sai bài Vật lí 9
    # «Trong trường hợp thí nghiệm...» (thật ra là câu hỏi của TN trước) đã
    # lộ ra khi mở rộng sang KHTN 6-9.
    title = None
    for t in reversed(lines[max(0, i_cb - 6):i_cb]):
        # Dấu hai chấm KHÔNG bắt buộc: KHTN 6 viết «Thí nghiệm về sự bảo toàn
        # năng lượng» thành một dòng trần. Nhưng đòi dòng NGẮN và không kết
        # bằng dấu câu, nếu không sẽ vơ luôn thân câu hỏi «Thí nghiệm mô tả ở
        # Hình 42.2 giúp chúng ta khám phá…».
        m = re.match(r'^Thí nghiệm\s*\d*\s*[:.]\s*(\S.*)$', t)
        if m:
            title = m.group(1).strip()
            break
        c = t.strip()
        if (re.match(r'^Thí nghiệm\b', c) and 12 <= len(c) <= 70
                and not c.endswith(('.', '?', '!', ':', ','))):
            title = c
            break
        # ⭐ GDTC đặt tên bằng «Trò chơi …», thường có dấu đầu dòng và một dấu
        # hai chấm trước TÊN THẬT: «- Trò chơi hỗ trợ khởi động: Giành cờ».
        # Lấy phần sau dấu hai chấm — đó mới là tên trẻ đọc.
        m = re.match(r'^[-+•–]?\s*Trò chơi\b[^:]{0,40}:\s*(\S.*)$', c)
        if m and 3 <= len(m.group(1)) <= 60:
            title = m.group(1).strip()
            break
    if title is None:
        # ⚠ Vòng này TRƯỚC ĐÂY quét ngược VÔ HẠN về đầu trang, nên nó lấy được
        # cả «Hoàn thành các câu sau đây» ở dòng 0 làm tên thí nghiệm ở dòng 51.
        # Giới hạn về cùng cửa sổ với các nhánh khác.
        for t in reversed(lines[max(0, i_cb - 14):i_cb]):
            if re.match(r'^\d+\.\s+\S', t):
                c = re.sub(r'^\d+\.\s+', '', t).strip()
                # ⚠ KHÔNG chặn mọi câu hỏi. Khoa học 4 đặt tên bài BẰNG câu
                # hỏi và đó là tên hợp lệ («Không khí có ở đâu?»); thứ phải
                # chặn là ĐỀ BÀI TẬP của KHTN 6 («Nhận xét nào sau đây nói về
                # tính chất hoá học của sắt?»). Phân biệt bằng độ dài + cụm
                # ra-đề, không bằng dấu hỏi — bản trước chặn cả hai và làm
                # lớp 4 mất một thí nghiệm.
                # «hãy» là dấu hiệu CÂU LỆNH cho học sinh, không phải tên thí
                # nghiệm — «Quan sát hình 2, hãy ghi chép sự thay đổi…». Chặn
                # nó ở mọi dạng, không chỉ khi kết bằng dấu hỏi.
                low = c.lower()
                bad_prompt = ('nào sau đây' in low or 'hãy' in low)
                if not bad_prompt and not (c.endswith('?') and len(c) > 40):
                    title = c
                break
    if title is None:
        # ⭐ KHTN 6-9 đặt tên thí nghiệm bằng một dòng TRẦN ngay trên «Chuẩn bị:»
        # — không đánh số, không dấu hai chấm: «Lọc nước từ hỗn hợp nước lẫn
        # đất», «Tìm hiểu một số tính chất của đường và muối ăn». Hai mẫu trên
        # viết cho sách tiểu học nên trượt hết. Đo được 5/16 khối KHTN 6 rớt
        # chỉ vì thiếu tiêu đề, dù dòng tiêu đề nằm ngay đó.
        #
        # Fail closed vẫn giữ: dòng phải TRÔNG NHƯ tiêu đề — không kết câu bằng
        # dấu chấm, không phải câu hỏi, không phải một bước, đủ dài để có nghĩa.
        # ⚠ Bản đầu của tôi chỉ đòi «dài ≥12 và không kết bằng dấu câu» — nó vơ
        # cả dòng GIỮA ĐOẠN: «Thảo luận về những ưu điểm và nhược điểm trong»,
        # «Quả bóng này». Tín hiệu thật của một dòng tiêu đề là nó MỞ ĐẦU một
        # khối: dòng ngay trước nó phải kết thúc trọn câu.
        for k in range(i_cb - 1, max(-1, i_cb - 4), -1):
            c = lines[k].strip()
            prev = lines[k - 1].strip() if k > 0 else ''
            # Mục con «a) b) c)» và chú thích hình cũng MỞ một khối, y như một
            # câu trọn: «c) Trò chơi phát triển sức nhanh» / «Chạy tiếp sức».
            starts_block = (k == 0) or prev.endswith(('.', '?', '!', ':')) \
                or bool(re.match(r'^([a-zđ]\)|\d+\.|Hình\b)', prev))
            if (8 <= len(c) <= 70 and ' ' in c
                    and starts_block
                    and not c.endswith(('.', '?', '!', ':', ','))
                    and not c.startswith(('•', '-', '–', '?', 'Hình', 'Chuẩn bị'))
                    and c[0].isupper()):
                title = c
                break
    # Tiêu đề cũng XUỐNG DÒNG như bước: «Tự làm mô hình tuabin hoạt động bằng
    # nguồn năng / lượng tái tạo». Ghép nốt phần chạy tiếp, cùng nguyên tắc.
    if title is not None:
        try:
            ti = lines.index(title, max(0, i_cb - 6), i_cb)
        except ValueError:
            ti = None
        if ti is not None and ti + 1 < i_cb:
            nxt = lines[ti + 1].strip()
            if (nxt and nxt[0].islower() and len(nxt) <= 40
                    and not nxt.startswith(('•', '-', '–'))):
                title = f'{title} {nxt}'

    steps, du_doan, quan_sat = [], None, None
    # KHTN 6-9: đôi khi bước đầu viết NGAY sau dấu hai chấm cùng dòng
    # («Tiến hành: Dùng panh kẹp...») thay vì xuống dòng rồi mới «- ...».
    # Dòng mốc có thể mang dấu đầu dòng: «- Thực hiện: …», «+ Tiến hành: …».
    inline = re.match(r'^[-+•–]?\s*(?:Tiến hành|Thực hiện)\s*:\s*(\S.*)$',
                      lines[i_th])
    if inline:
        steps.append(inline.group(1).strip())
    # ⭐⭐ SÁCH TIỂU HỌC DÙNG «- », KHTN 6-9 DÙNG «•».
    #
    # Bộ trích này viết cho Khoa học 4/5 rồi mở sang KHTN 6-9 mà không đổi ký
    # tự đầu dòng. Hậu quả đo được: 8/16 khối KHTN 6 tìm thấy đủ «Chuẩn bị» +
    # «Tiến hành» nhưng KHÔNG đọc được bước nào, nên bị bỏ — trong đó có chính
    # Bài 17, bài đang hiện trên Home của trẻ.
    for t in lines[i_th + 1:i_th + 14]:
        body = step_body(t)
        if body is not None:
            if is_real_step(body):
                steps.append(body)
            continue
        if t.startswith('Dự đoán'):
            du_doan = t.strip()
        elif re.match(r'^(Sau .{0,30})?[Qq]uan sát', t):
            quan_sat = t.strip()
        elif t.startswith('?') or t.startswith('Hình') or t.startswith('('):
            break
        elif steps and continues_step(steps[-1], t):
            steps[-1] = f'{steps[-1]} {t.strip()}'
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

# WAL-210 (Dart lane request, PR #63/#64): mọi diaMaps[] mang `lesson` canonical, gắn bằng
# cùng luật capped-toc-v2 + identity như các họ khác — không gắn được ⇒ không phát hành.
dia_maps = ATT.attach_items('diaMaps', dia_maps, page_key='page', pdf_key='pagePdf', note_key='asset')

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

# ---- lessonReadings: TRANG SÁCH CỦA CHÍNH BÀI (họ hoạt động thứ sáu) --------
# Census toàn corpus: 3.142 bài có nội dung đọc được, sản phẩm mở được 117 — vì
# `activitiesFor` không có họ nào là «đọc trang sách». Lớp 1, 2, 3, 11, 12 có
# ĐÚNG 0 bài mở được. Đây là chỗ nối dữ liệu đã có vào sản phẩm.
#
# Nguồn dải trang + tên bài đọc-từ-trang là đầu ra của `tool/corpus/tc2_attach.py`.
# Không có nó ⇒ KHÔNG phát mục nào (pack vẫn dựng được, chỉ là không có họ này) —
# đoán dải trang để bài «mở được» là cho trẻ mở nhầm chỗ.
ATTACH_ROOT = os.environ.get('ATTACH_ROOT', 'poc-out/trusted-corpus/tc-v2/tc2-p1')
lesson_readings = []
_lr_reasons = collections.Counter()
for _subj, _books in subjects.items():
    for _b in _books:
        _bid = _b['sourceDocumentId']
        _ap = os.path.join(ATTACH_ROOT, 'attach', f'{_bid}.json')
        if not os.path.exists(_ap):
            _lr_reasons['NO_ATTACH'] += len(_b['lessons'])
            continue
        _ad = json.load(open(_ap, encoding='utf-8'))
        _npages = len(_ad.get('pages') or [])
        _Ls = sorted([L for L in _ad.get('lessons') or [] if L.get('page_pdf')],
                     key=lambda x: x['page_pdf'])
        _range = {}
        for _i, _L in enumerate(_Ls):
            _s = _L['page_pdf']
            _e = (_Ls[_i + 1]['page_pdf'] - 1) if _i + 1 < len(_Ls) else _npages
            _range[_L['number']] = (_s, max(_s, min(_e, _npages)), _L.get('title'))
        # Bài trùng số trong cùng cuốn: KHÔNG phát. `(book, lessonNo)` không phân
        # biệt được chúng (đo được: 310 bài thật sự khác nhau dùng chung số), nên
        # phát ra sẽ gắn nội dung của bài này vào tên của bài kia.
        _dupes = {n for n, c in collections.Counter(
            l['no'] for l in _b['lessons']).items() if c > 1}
        for _L in _b['lessons']:
            _no = _L['no']
            if _no in _dupes:
                _lr_reasons['AMBIGUOUS_IDENTITY'] += 1
                continue
            if _no not in _range:
                _lr_reasons['SOURCE_RANGE'] += 1
                continue
            _s, _e, _atitle = _range[_no]
            _title = (_L.get('title') or _atitle or '').strip()
            if not _title:
                _lr_reasons['LESSON_IDENTITY_TITLE'] += 1
                continue
            _d, _why = lesson_reading(_bid, _s, _e,
                                      printed_start=_L.get('pageStart'), title=_title)
            if not _d:
                _lr_reasons[_why] += 1
                continue
            lesson_readings.append(dict(
                book=_bid, lesson=_no, title=_title,
                pageStart=_L.get('pageStart'), pagePdfStart=_s, pagePdfEnd=_e,
                text=' '.join(p['text'] for p in _d['pages']),
                extraction=_d['extraction']))
            # Tên đọc-từ-trang bù vào mục lục: chữ của SÁCH, không phải chữ máy đặt.
            if not (_L.get('title') or '').strip():
                _L['title'] = _title

for v in subjects.values():
    v.sort(key=lambda b: (b['volume'] or '9', b['sourceDocumentId']))
out = dict(grade=GRADE, version='lesson-index-v2',
           subjects={k: v for k, v in sorted(subjects.items())},
           toanExercises={str(k): v for k, v in sorted(ex_by_lesson.items())},
           tvReadings=tv_readings,
           tvWritings=tv_writings,
           suSources=su_sources,
           khoaExperiments=khoa_experiments,
           lessonReadings=lesson_readings,
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
                   dropped=ATT.dropped, flagged=ATT.flagged,
                   droppedNonVerbatim=_dropped_non_verbatim),
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
print(f'  lessonReadings: {len(lesson_readings)}/{n_les} bài mở đọc được — '
      f'không phát: {dict(_lr_reasons)}')
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
