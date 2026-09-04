"""WAL-204 — Pattern router (P0 falsification experiment).

Source → LearningActivity, generically: for a configured set of books,
  1. TOC-range attachment: assign every generic-extractor unit
     (poc-out/units-k12/<book>.json) to a lesson by its PDF page, using the
     book's TOC page ranges (curriculum-structure.json) and a printed→PDF
     offset derived from footer page digits — NOT the extractor's own in-body
     "Bài N" detection, which OCR mangles on large title typography
     (measured: +497 of 950 previously-unattached lessons recovered).
  2. Activity pattern detection: tool/corpus/fable_activity_taxonomy.classify
     on each clean unit (leading-directive classifier, ≈85% precision).
  3. Routing into EXISTING Surfaces only, by emitting the shapes those
     Surfaces already consume:
       READ_TEXT   → tvReadings  (ReaderScreen, open question, correct=null)
       SELECT_MCQ  → tvReadings with questions[].options, correctOption=null
                     (ReaderScreen ungraded select — LearningActivity.gradable
                     is false without a key ⇒ _pick emits correct=null)
       WRITE_TEXT  → tvWritings  (ComposeLiteScreen)
     Nothing is graded: no SGV answer key is consulted in this experiment.
     EXPERIMENT units are deliberately NOT emitted here — khoaExperiments
     stays on its existing extractor so the 37-lesson regression oracle is
     untouched.

Fail-closed: a unit that cannot yield (prompt ≥ 12 chars) and, for MCQ,
≥ 2 parsed options, or for reading a passage ≥ 120 chars, is dropped. No
LLM, no per-lesson rules, no per-book heuristics beyond the shared offset.
"""
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'corpus'))
from fable_activity_taxonomy import CATALOG, NOISE, STAGE_ONLY, classify  # noqa: E402

DIGITS = re.compile(r'^\d{1,3}$')
# "A. xxx B. yyy C. zzz [D. www]" — options may be inline or newline-separated.
OPT_SPLIT = re.compile(r'(?:(?<=\s)|^)([A-D])[\.\)]\s+')
MIN_PROMPT = 12
MIN_PASSAGE = 120
MAX_PROMPT = 500


# ---- content gate AT SOURCE (WAL-206): the same checks as tool/corpus/content_quality_gate.py,
# applied before emission so packs never carry a known-bad activity (fail closed).
OBJECTIVE_RE = re.compile(r'^\s*(\d{1,2}[\.\)]\s*)?(Giải thích|Nêu|Trình bày|Mô tả|Xác định|Phân biệt|Vận dụng|Nhận biết|Kể tên|So sánh|Phát biểu|Viết|Đọc|Tính|Thực hiện|Sử dụng|Vẽ)\s+được\b', re.IGNORECASE)
FIGURE_RE = re.compile(r'\b(Hình|Bảng|Sơ đồ|Biểu đồ|Lược đồ)\s*\d', re.IGNORECASE)
LABEL_RE = re.compile(r'\b(Em có biết|Lưu ý|Ghi nhớ|Chú ý|Theo dõi)\b')
# WAL-206 device walk (KHTN 6 Bài 2): the "passage" was the MỤC TIÊU bullet list. An objective
# sentence = leading verb + "được" ("Nêu được…", "Phân biệt được…"). A passage whose sentences
# are mostly objectives is a learning-objective box, not learner reading material.
OBJ_SENT_RE = re.compile(r'^\s*(Nêu|Trình bày|Mô tả|Phân biệt|Đọc|Giải thích|Xác định|Vận dụng|Nhận biết|Kể tên|So sánh|Phát biểu|Viết|Tính|Thực hiện|Sử dụng|Vẽ|Nhận ra|Chỉ ra|Kể|Tìm hiểu|Thu thập|Quan sát|Biết|Liên hệ|Đề xuất|Thiết kế|Lập|Đo|Lấy|Làm|Dự đoán|Tiến hành|Có|Hiểu|Ứng dụng|Tóm tắt|Ghi chú)\b.*\bđược\b', re.IGNORECASE)
# "Đọc ý kiến trên … trả lời các câu hỏi sau:" — a lead-in whose real questions follow elsewhere.
LEADIN_RE = re.compile(r'(sau|sau đây|dưới đây)\s*[:：]\s*$')
# Prompt points at something the Surface cannot show (speech-bubble opinions, a figure, a table).
# "Đọc là: iron tác dụng với sulfur…" — a pronunciation/reading instruction, not a question.
PRONOUNCE_RE = re.compile(r'^\s*(\d{1,2}[\.\)]\s*)?Đọc là\b', re.IGNORECASE)
# "quan sát Hình 47.2" — the Reader never shows figures, so an observe-the-figure prompt is
# figure-dependent even when the passage text mentions the figure number.
OBSERVE_FIG_RE = re.compile(r'\b(quan sát|nhìn vào|dựa vào|xem)\b[^.?!]{0,40}\b(hình|bảng|sơ đồ|biểu đồ|lược đồ)\b', re.IGNORECASE)
DEICTIC_RE = re.compile(r'\b(ý kiến|thông tin|hình|bảng|sơ đồ|các bạn|kết quả|thí nghiệm)\s+(trên|dưới đây|sau đây|ở trên|bên)\b|\b(hình bên|bảng bên|trong (các )?hình|ở hình|trên hình|hình trên|hình dưới)\b', re.IGNORECASE)


# "trong các vật sau đây, vật nào là vật sống…" (KHTN 6 Bài 1, device walk): "sau đây/dưới đây"
# with NO inline list after it means the items are in a figure the Reader cannot show.
BARE_DEICTIC_RE = re.compile(r'\b(sau đây|dưới đây|bên dưới)\b', re.IGNORECASE)


def prompt_points_offpage(prompt):
    m = BARE_DEICTIC_RE.search(prompt)
    if not m:
        return False
    tail = prompt[m.end():]
    return not (':' in tail and tail.count(',') + tail.count(';') >= 2)   # an inline list ("…sau đây: a, b, c") is fine


# KHTN 6 Bài 6 (device walk): a unit-conversion side box ("1 gam (g) = 0,001 kg …") beside body
# text was spliced into the passage — a partial-height side box the XY-cut cannot separate when a
# wide line above/below spans both. ≥3 "= digit" fragments is the cheap signature of such a box.
EQ_FRAG_RE = re.compile(r'=\s*\d')


def passage_has_spliced_box(passage):
    return len(EQ_FRAG_RE.findall(passage)) >= 3


def passage_is_objectives(passage):
    parts = [s.strip() for s in re.split(r'\s*[•]\s*|(?<=[.!?])\s+', passage) if s.strip()]
    obj = sum(1 for s in parts if OBJ_SENT_RE.match(s))
    return obj >= 2 or (obj >= 1 and obj >= 0.5 * len(parts))


def reading_ok(prompt, passage):
    words = prompt.split()
    letters = [c for c in prompt if c.isalpha()]
    upper = (sum(1 for c in letters if c.isupper()) / len(letters)) if letters else 0
    if len(words) < 5 or upper > 0.6:
        return 'fragment_or_heading'
    if OBJECTIVE_RE.match(prompt):
        return 'objective_not_question'
    if len(words) >= 8 and len(set(w.lower() for w in words)) < 0.6 * len(words):
        return 'garbled'
    if FIGURE_RE.search(prompt) and not FIGURE_RE.search(passage):
        return 'figure_dependent'
    if LABEL_RE.search(passage) or FIGURE_RE.search(passage[:40]):
        return 'label_in_passage'
    if passage_is_objectives(passage):
        return 'passage_is_objectives'
    if passage_has_spliced_box(passage):
        return 'passage_spliced_box'
    if LEADIN_RE.search(prompt):
        return 'leadin_not_question'
    if DEICTIC_RE.search(prompt) or prompt_points_offpage(prompt):
        return 'deictic_prompt'
    if PRONOUNCE_RE.match(prompt):
        return 'pronunciation_not_question'
    if OBSERVE_FIG_RE.search(prompt):
        return 'observe_figure'
    return None


def printed_to_pdf_offset(book):
    diffs = Counter()
    for fp in glob.glob(f'poc-out/graph/ocr-body/{book}/p*.json'):
        pdf = int(re.search(r'p(\d+)\.json', fp).group(1))
        try:
            lines = json.load(open(fp))['lines']
        except (OSError, ValueError):
            continue
        for l in lines[-3:] + lines[:2]:
            t = l['text'].strip()
            if DIGITS.match(t):
                d = pdf - int(t)
                if -3 <= d <= 15:
                    diffs[d] += 1
    if not diffs:
        return None
    (best, n), = diffs.most_common(1)
    # Require a clear mode — an ambiguous offset would mis-attach silently.
    return best if n >= 3 else None


def toc_ranges(doc, offset):
    ls = sorted((l for l in doc.get('lessons', [])
                 if l.get('number') is not None and l.get('pageStart') is not None),
                key=lambda l: l['pageStart'])
    out = []
    for i, l in enumerate(ls):
        lo = l['pageStart'] + offset
        hi = (ls[i + 1]['pageStart'] + offset) if i + 1 < len(ls) else 10 ** 6
        out.append((l['number'], lo, hi))
    return out


def clean(text):
    t = text.strip()
    if (CATALOG.match(t) and len(t) < 120) or STAGE_ONLY.match(t) or NOISE.search(t):
        return None
    return t


def parse_mcq(text):
    parts = OPT_SPLIT.split(text)
    # parts: [prompt, 'A', optA, 'B', optB, ...]
    if len(parts) < 5:
        return None
    prompt = parts[0].strip()
    letters = parts[1::2]
    bodies = [b.strip() for b in parts[2::2]]
    if letters[:len(bodies)] != list('ABCD')[:len(bodies)]:
        return None
    opts = [re.sub(r'\s+', ' ', b)[:200] for b in bodies if b]
    if len(opts) < 2 or len(prompt) < MIN_PROMPT:
        return None
    return prompt[:MAX_PROMPT], opts


def route_book(doc, subject):
    """UNITS_SOURCE=layout (WAL-206) reads poc-out/units-layout/<book>.json —
    PASSAGE/QUESTION/HEADING units from trusted layout regions — and never
    uses a neighbour block as a question: the QUESTION unit itself is the
    prompt, the nearest preceding PASSAGE in the same lesson is the context.
    Default (legacy) reads units-k12 exactly as in the WAL-204 experiment."""
    book = doc['sourceDocumentId']
    stats = Counter()
    layout_mode = os.environ.get('UNITS_SOURCE') == 'layout'
    src = f'poc-out/units-layout/{book}.json' if layout_mode else f'poc-out/units-k12/{book}.json'
    if not os.path.exists(src):
        stats['no_units_file'] += 1
        return [], [], stats
    offset = printed_to_pdf_offset(book)
    if offset is None:
        stats['no_offset'] += 1
        return [], [], stats
    units = [u for u in json.load(open(src))['units'] if u['role'] != 'SECTION_TEXT']
    by_lesson = defaultdict(list)
    for no, lo, hi in toc_ranges(doc, offset):
        for u in units:
            if lo <= u['pagePdf'] < hi:
                by_lesson[no].append(u)
    readings, writings = [], []
    for no, us in sorted(by_lesson.items()):
        us.sort(key=lambda u: (u['pagePdf'], u['id']))
        last_context = None
        for u in us:
            t = clean(u['text'])
            if t is None:
                continue
            printed = u['pagePdf'] - offset
            if layout_mode:
                if u['role'] == 'PASSAGE':
                    last_context = (t, printed, u['id']); stats['passages'] += 1
                    continue
                if u['role'] != 'QUESTION':
                    continue
            labels = classify(t)
            if not labels:
                if not layout_mode and len(t) >= MIN_PASSAGE:
                    last_context = (t, printed, u['id'])
                continue
            if 'WRITE_TEXT' in labels and len(t) <= 400:
                writings.append(dict(book=book, lesson=no, page=printed, prompt=t, pattern='WRITE_TEXT', subject=subject,
                                     source='pattern-router-v2-layout' if layout_mode else 'pattern-router-v1', unitId=u['id']))
                stats['WRITE_TEXT'] += 1
                continue
            if 'SELECT_MCQ' in labels:
                parsed = parse_mcq(t)
                if parsed and last_context and not reading_ok(parsed[0], last_context[0]):
                    prompt, opts = parsed
                    readings.append(dict(book=book, lesson=no, page=last_context[1], passage=last_context[0],
                                         questions=[dict(prompt=prompt, page=printed, options=opts)],
                                         pattern='SELECT_MCQ', subject=subject, source='pattern-router-v2-layout' if layout_mode else 'pattern-router-v1',
                                         passageUnitId=last_context[2], questionUnitId=u['id']))
                    stats['SELECT_MCQ'] += 1
                else:
                    stats['SELECT_MCQ_dropped'] += 1
                continue
            if layout_mode and os.environ.get('ROUTE_EXPLAIN') == '1' and (labels & {'EXPLAIN_SHORT', 'COMPARE', 'CLASSIFY_SORT'}) and not (labels & {'READ_TEXT', 'SELECT_MCQ', 'WRITE_TEXT'}):
                # MEASUREMENT VARIANT ONLY (P0-NEXT candidate, not the WAL-204 re-run scope):
                # a short-answer learner question + its context passage → ReaderScreen open mode
                # (child answers aloud, self-confirms; correct=null — never graded).
                bad = reading_ok(t, last_context[0]) if last_context else 'no_context'
                if last_context and MIN_PROMPT <= len(t) <= MAX_PROMPT and not bad:
                    readings.append(dict(book=book, lesson=no, page=last_context[1], passage=last_context[0][:4000],
                                         questions=[dict(prompt=t, page=printed)],
                                         pattern='EXPLAIN_SHORT', subject=subject, source='pattern-router-v2-layout',
                                         passageUnitId=last_context[2], questionUnitId=u['id']))
                    stats['EXPLAIN_SHORT'] += 1
                else:
                    stats['EXPLAIN_SHORT_dropped'] += 1; stats[f'gate_{bad}'] += 1
                continue
            if 'READ_TEXT' in labels:
                if layout_mode:
                    # the QUESTION unit is the learner question; the passage is the context it refers to
                    bad = reading_ok(t, last_context[0]) if last_context else 'no_context'
                    if last_context and len(t) >= MIN_PROMPT and not bad:
                        readings.append(dict(book=book, lesson=no, page=last_context[1], passage=last_context[0][:4000],
                                             questions=[dict(prompt=t[:MAX_PROMPT], page=printed)],
                                             pattern='READ_TEXT', subject=subject, source='pattern-router-v2-layout',
                                             passageUnitId=last_context[2], questionUnitId=u['id']))
                        stats['READ_TEXT'] += 1
                    else:
                        stats['READ_TEXT_dropped'] += 1; stats[f'gate_{bad}'] += 1
                    continue
                if u['role'] in ('READING', 'EXERCISE', 'ACTIVITY'):
                    if len(t) < MIN_PASSAGE:
                        stats['READ_TEXT_dropped'] += 1
                        continue
                    q = next((clean(v['text']) for v in us
                              if v['pagePdf'] >= u['pagePdf'] and v['id'] != u['id']
                              and clean(v['text']) and classify(clean(v['text'])) & {'EXPLAIN_SHORT', 'SELECT_MCQ', 'COMPARE', 'CLASSIFY_SORT'}), None)
                    if not q or len(q) < MIN_PROMPT:
                        stats['READ_TEXT_dropped'] += 1
                        continue
                    readings.append(dict(book=book, lesson=no, page=printed, passage=t[:4000],
                                         questions=[dict(prompt=q[:MAX_PROMPT], page=printed)],
                                         pattern='READ_TEXT', subject=subject, source='pattern-router-v1'))
                    stats['READ_TEXT'] += 1
    return readings, writings, stats


def route(grade, books, docs):
    """books: list of (subject, sourceDocumentId). Returns (readings, writings, stats)."""
    by_id = {d['sourceDocumentId']: d for d in docs}
    R, W, S = [], [], Counter()
    for subject, book in books:
        doc = by_id.get(book)
        if not doc:
            S['missing_doc'] += 1
            continue
        r, w, s = route_book(doc, subject)
        R += r
        W += w
        S += s
    return R, W, S
