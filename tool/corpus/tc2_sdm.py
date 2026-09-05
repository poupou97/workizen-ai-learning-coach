#!/usr/bin/env python3
"""TC-v2 — SDM builder v2: Docling+Apple Vision (primary) ▸ WAL-206 XY-cut (verifier)
→ agreement gate → deterministic guards (reason codes) → deterministic Role Layer → SDM page.

Founder chain validated here: Source → SDM → block trust → Role Layer → guards. Lesson
attachment (tc2_attach.py) and the Trusted Structured Lesson (tc2_tsl.py) read the SDM
written here. Nothing here is an LLM/VLM: every rule is a regex, a geometry test or a
colour measurement, and every withheld block keeps its bbox + reason codes so a Hybrid
Smart Book can point at the source region (with or without a page image).

SDM block (superset of TC-11 §2):
  id, order, native_label, text (enumerator-preserved: Docling `orig`/`marker`, cross-checked
  against the OCR line), text_docling, bbox [x,y,w,h] normalised, column, ocr_conf, colour
  {share, left, right, top, bottom}, extraction, agreement {text_sim, verifier_id,
  verifier_role, order_ok}, role {value, method, confidence, evidence[], verifier_hint,
  conflict}, guards[] (reason codes that fired), trust {status TRUSTED|WITHHELD|CONFLICT,
  reasons[]}, learning (bool), refers_figure, heading_path[], lesson (filled by tc2_attach).

Reason codes (guards): agree_text · agree_order · agree_numbers (round 4: the two OCR stacks read different
digits for the same text) · agree_tones (round 4: same word, different tone marks between the stacks) · role_conflict · math_guard · unit_guard · chem_guard (round 4: flattened unit
exponents / chemical subscripts) · empty_block · furniture (page number / running head) · box_boundary ·
figure_dependent · answer_leak · teacher_text · page_feature:color_heavy · page_feature:diagram ·
figure_text · low_ocr_conf.
Informational (never withhold): enumerator_restored · refers_figure.

Usage (bake-off venv python — rapidfuzz + numpy + pymupdf):
  tc2_sdm.py --pipeline tc2-p1 --pages P.json            # slice pages → sdm/<book>/pNNN.sdm.json
  tc2_sdm.py --pipeline tc2-p1 --gold                    # every gold page → sdm-gold/ (raw from tc-v2 when present, else read-only tc-v1)
  tc2_sdm.py --pipeline tc2-p1 --page <book> <pdfPage>   # print one page
"""
import argparse
import difflib
import glob
import json
import os
import re
import statistics
import sys
import unicodedata
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tc_sdm  # noqa: E402
import tc_score  # noqa: E402
import tc_cascade  # noqa: E402
import layout_extract  # noqa: E402
import tc2_paths  # noqa: E402

ROOT = tc_sdm.ROOT
PDF = f'{ROOT}/poc-out/pdf'
OCR = f'{ROOT}/poc-out/graph/ocr-body'
PIPELINE_ID = 'tc2-p1'
# Round 4 (failure class 3: role classification). The icon / box-tint signal measured in
# docs/research/ROLE-LAYER-SIGNAL-EXPERIMENT-2026-09-05.md is integrated BEHIND A FLAG: None (default) leaves the
# deterministic lexicon/geometry Role Layer unchanged; 'v2' / 'v3' apply the experiment's frozen rules
# (R1 orange icon → ACTIVITY, R2 blue icon → QUESTION; v3 never lets an inherited icon override the instruction
# lexicon). Set with --role-signal on the CLIs or TC2_ROLE_SIGNAL in the environment. No threshold is decided here.
ROLE_SIGNAL = os.environ.get('TC2_ROLE_SIGNAL') or None
SDM_VERSION = 'sdm-v3'   # round 4: LIS order agreement + verifier-aligned re-sequencing (see agreement())
TEXT_SIM = tc_cascade.TEXT_SIM

try:
    from rapidfuzz import fuzz
except Exception:  # pragma: no cover
    fuzz = None
try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None


def out_root(pipeline):
    return tc2_paths.out_root(pipeline)


# ---------------------------------------------------------------- raw loading
def load_raw(cand, book, page, pipeline, allow_v1=True):
    """This run's raw first; then (read-only) the tc2-p1 raw, then the tc-v1 bake-off raw — the raw candidate
    output is deterministic per page and independent of the SDM/role/guard code, so a later pipeline version
    reuses it (tc2_paths.raw_path records which one)."""
    p, src = tc2_paths.raw_path(cand, book, page, pipeline, allow_fallback=allow_v1)
    if p is None:
        return None, None
    r = json.load(open(p))
    if r.get('error') or r.get('result') is None:
        return None, src
    return r, src


def adapt_docling_v2(res):
    """Like tc_sdm.adapt_docling but ENUMERATOR-PRESERVING: Docling strips "1." / "A." from
    list items into `marker`; the raw OCR text survives in `orig`. TC-09 counted 65
    enumerator-dropped events for this; here the marker is restored deterministically."""
    d = res['docling']
    pg = list(d['pages'].values())[0]; W, H = pg['size']['width'], pg['size']['height']
    out, pics, tables, i = [], [], [], 0

    def bbox_of(item):
        if not item.get('prov'):
            return None
        b = item['prov'][0]['bbox']
        l, t, r, bt = b['l'], b['t'], b['r'], b['b']
        if b.get('coord_origin', 'BOTTOMLEFT') == 'BOTTOMLEFT':
            y0 = (H - t) / H; y1 = (H - bt) / H
        else:
            y0 = t / H; y1 = bt / H
        return [round(l / W, 4), round(y0, 4), round((r - l) / W, 4), round(y1 - y0, 4)]

    def rec(node):
        nonlocal i
        for ch in node.get('children', []):
            ref = ch['$ref']; kind, idx = ref.split('/')[1], int(ref.split('/')[2])
            item = d[kind][idx]
            if kind == 'texts':
                txt = item.get('text', '') or ''
                orig = item.get('orig') or ''
                marker = (item.get('marker') or '').strip()
                restored = False
                full = txt
                if marker and not txt.lstrip().startswith(marker):
                    if orig.lstrip().startswith(marker):
                        full = orig; restored = True
                    else:
                        full = f'{marker} {txt}'; restored = True
                b = tc_sdm._blk(i, tc_sdm.DOCLING_ROLE.get(item.get('label'), 'UNKNOWN'), full, bbox_of(item), None, item.get('label'), None, 'docling-2.126+ocrmac')
                b['text_docling'] = txt; b['enumerator_restored'] = restored; b['marker'] = marker or None
                out.append(b); i += 1
            elif kind == 'tables':
                cells = item.get('data', {}).get('table_cells', [])
                txt = ' | '.join(c.get('text', '') for c in cells)
                b = tc_sdm._blk(i, 'TABLE', txt, bbox_of(item), None, 'table', None, 'docling-2.126+ocrmac')
                b['cells'] = [dict(r=c.get('start_row_offset_idx'), c=c.get('start_col_offset_idx'), text=c.get('text', ''), header=bool(c.get('column_header') or c.get('row_header'))) for c in cells]
                out.append(b); tables.append(dict(order=i, bbox=b['bbox'], cells=len(cells))); i += 1
            elif kind == 'pictures':
                bb = bbox_of(item)
                b = tc_sdm._blk(i, 'FIGURE', '', bb, None, 'picture', None, 'docling-2.126')
                out.append(b); pics.append(dict(order=i, bbox=bb)); i += 1
            rec(item)
    rec(d['body'])
    for k in ('furniture',):
        if d.get(k):
            rec(d[k])
    return out, pics, tables


# ---------------------------------------------------------------- page image colour
_doc_cache = {}


def _pdf(book):
    if book not in _doc_cache:
        import fitz
        p = f'{PDF}/{book[:2]}/{book}.pdf'
        if not os.path.exists(p):
            p = f'{PDF}/{book}.pdf'
        _doc_cache[book] = fitz.open(p) if os.path.exists(p) else None
    return _doc_cache[book]


def colour_mask(book, page, dpi=36):
    """Boolean H×W mask of 'on colour' pixels from a low-dpi render — the same signal the TC-03
    census used per line, here measured per block. Calibrated on the 38 TC-v1 gold pages (dev set):
    a PALE threshold (saturation > 0.08, not dark) is what separates a tinted box from white paper
    (EM ĐÃ HỌC box 0.97, blue sidebar 0.61, MỤC TIÊU tint 0.37, white body 0.00); a saturated
    threshold (0.25) misses the tints and fires on coloured step chips."""
    doc = _pdf(book)
    if doc is None or np is None:
        return None
    import fitz
    pm = doc[page - 1].get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
    arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3).astype(np.int16)
    mx = arr.max(axis=2); mn = arr.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)
    return (sat > 0.08) & (mx > 120)


def colour_of(mask, bbox):
    if mask is None or not bbox:
        return None
    Hh, Ww = mask.shape
    x, y, w, h = bbox
    x0, y0 = max(0, int(x * Ww)), max(0, int(y * Hh)); x1, y1 = min(Ww, int((x + w) * Ww) + 1), min(Hh, int((y + h) * Hh) + 1)
    if x1 <= x0 or y1 <= y0:
        return None
    sub = mask[y0:y1, x0:x1]
    def share(s):
        return round(float(s.mean()), 3) if s.size else 0.0
    cw = max(1, (x1 - x0) // 3); ch = max(1, (y1 - y0) // 3)
    return dict(share=share(sub), left=share(sub[:, :cw]), right=share(sub[:, -cw:]), top=share(sub[:ch, :]), bottom=share(sub[-ch:, :]))


# ---------------------------------------------------------------- lexicon (deterministic Role Layer)
STAGE = re.compile(r'^\s*(KHỞI ĐỘNG|KHÁM PHÁ|LUYỆN TẬP|VẬN DỤNG|THỰC HÀNH|MỤC TIÊU|EM ĐÃ HỌC|EM CÓ THỂ|EM CÓ BIẾT|GHI NHỚ|CÂU HỎI VÀ BÀI TẬP|Câu hỏi và bài tập|Khởi động|Khám phá|Luyện tập|Vận dụng|Thực hành|Hoạt động|HOẠT ĐỘNG|Em có biết|Em đã học|Em có thể|Ghi nhớ|Lưu ý|LƯU Ý|Chú ý|CHÚ Ý|Mở rộng|MỞ RỘNG|Kết nối|KẾT NỐI)\b\s*[\d.:]*\s*\??\s*$')
SIDEBAR_LABEL = re.compile(r'^\s*(Em có bi[eê][tít]|EM CÓ BI[EÊ][TÍ]T?|Lưu ý|LƯU Ý|Ghi nhớ|GHI NHỚ|Chú ý|CHÚ Ý|Mở rộng|MỞ RỘNG|Kết nối|KẾT NỐI|Em đã học|EM ĐÃ HỌC|Em có th[eê]|EM CÓ TH[EÊ])\b')
OBJ_BOX = re.compile(r'(MỤC TIÊU|Mục tiêu|Sau bài học này|Học xong bài học này|Học xong bài này|Sau bài này|Sau bài học|em sẽ:?|HS sẽ:?)', re.IGNORECASE)
OBJ_SENT = re.compile(r'^\s*[•·\-–▪■]?\s*(?:\d{1,2}[.)]\s*)?(Nêu|Trình bày|Mô tả|Phân biệt|Đọc|Giải thích|Xác định|Vận dụng|Nhận biết|Kể tên|So sánh|Phát biểu|Viết|Tính|Thực hiện|Sử dụng|Vẽ|Nhận ra|Chỉ ra|Kể|Tìm hiểu|Thu thập|Quan sát|Biết|Liên hệ|Đề xuất|Thiết kế|Lập|Đo|Lấy|Làm|Dự đoán|Tiến hành|Có|Hiểu|Ứng dụng|Tóm tắt|Ghi chú|Nhận thức|Thảo luận|Trình diễn|Chứng minh|Phân tích|Đánh giá|Chọn|Chế tạo|Mắc|Tạo|Hình thành|Nhận xét|Xây dựng|Rèn luyện|Thu thập|Đề ra)\b[^.?!]{0,80}\bđược\b', re.IGNORECASE)
# generic objective shape: "<Capitalised verb> được …" as the first two words (e.g. "Chọn được nấm…", "Mắc được mạch điện…")
OBJ_GENERIC = re.compile(r'^\s*[•·\-–▪■]?\s*(?:\d{1,2}[.)]\s*)?[A-ZÀ-Ỹ][a-zà-ỹ]+\s+được\b')
FLEX_ROLES = {'sidebar', 'caption', 'footnote', 'figure_text', 'stage_label'}
ANSWER = re.compile(r'^\s*(Đáp án|ĐÁP ÁN|Lời giải|LỜI GIẢI|Gợi ý trả lời|Gợi ý|GỢI Ý|Trả lời|TRẢ LỜI|Hướng dẫn giải|Hướng dẫn trả lời|Kết luận:|M:)\b')
ANSWER_INLINE = re.compile(r'\b(Đáp án|đáp án đúng|Lời giải|Gợi ý trả lời)\s*[:：]', re.IGNORECASE)
TEACHER = re.compile(r'^\s*[-–•]?\s*(GV|HS|Giáo viên|Học sinh|GV:|HS:)\b')
INSTRUCTION = re.compile(r'^\s*[•\-–]?\s*(Bước\s*\d|Chuẩn bị\b|Tiến hành\b|Cách tiến hành|Dụng cụ\b|Hoá chất|Hóa chất|Nguyên liệu|Vật liệu|Thí nghiệm\s*\d|Đọc là\b|Lưu ý an toàn|Yêu cầu\b)', re.IGNORECASE)
ACTIVITY = re.compile(r'^\s*(Hoạt động\s*\d*[.:]?|HĐ\s*\d|Thực hành[:.]|Thí nghiệm[:.]|Trò chơi\b|Dự án\b|Thảo luận nhóm|Làm việc nhóm|Chơi trò chơi|Thực hiện thí nghiệm|Tiến hành thí nghiệm|Thiết kế\b|Chế tạo\b)', re.IGNORECASE)
OPTION = re.compile(r'^\s*[A-D][.)]\s+\S')
ENUM = re.compile(r'^\s*(?:(?:HĐ|Bài|Bước|Câu)\s*\d+[.:]?|\d{1,2}[.)]|[a-hA-H][.)])\s*')
QHINT = layout_extract.QUESTION_HINT
DIRECTIVE_ANY = layout_extract.DIRECTIVE_ANY
CAPTION = re.compile(r'^\s*(Hình|Bảng|Sơ đồ|Biểu đồ|Lược đồ|Tranh|Ảnh)\s*\d', re.IGNORECASE)
FOOTNOTE = layout_extract.FOOTNOTE
LESSON_HDR = re.compile(r'^\s*(B[ÀÁẢÃẠ]I|B[àáảãạ]i)\s+(\d{1,2})\b')   # round 4: + Ã (banner OCR «BÃI»), as tc2_attach
THEME_HDR = re.compile(r'^\s*(CHỦ ĐỀ|Chủ đề|CHƯƠNG|Chương)\s+([IVX]+|\d+)\b')
ROMAN_SEC = re.compile(r'^\s*(I|II|III|IV|V|VI|VII|VIII|IX|X)[.)]\s+\S')
NUM_SEC = re.compile(r'^\s*\d{1,2}[.)]\s+\S')
# Round 4 (Lane C request 4): «quan sát các hình từ 1 đến 3 …» carries no «Hình N», so the guard trusted a
# question the child cannot answer from text alone. A look-verb followed within a clause by a figure noun
# is a figure reference even when no number follows it.
FIG_REF = re.compile(r'\b(hình|bảng|sơ đồ|biểu đồ|lược đồ|đồ thị)\s*\d|\b(hình|bảng|sơ đồ)\s+(bên|trên|dưới|sau|dưới đây|sau đây)\b|\btrong (các )?hình\b|\bở hình\b|\b(quan sát|nhìn|xem|dựa vào|căn cứ vào|đọc)\b[^.?!]{0,40}?\b(hình|bảng|sơ đồ|biểu đồ|lược đồ|đồ thị)\b', re.IGNORECASE)
# Round 4 (Lane C request 5): «(Theo …)» / «(…, NXB …, 2017)» closes a story and names its source. tc2-p1 served
# it as body — the child could not tell the SGK's own prose from a quoted source (4 / 4 of Lane C's role
# disagreements on LS&ĐL 5 Bài 8). Fail closed: the marker word OR an explicit publisher is required, so a
# parenthesised proper name alone («(Hồ Chí Minh …)») is still body — a recorded gap, not a guess.
ATTRIBUTION = re.compile(r'^\s*[(\[]\s*(Theo|THEO|Nguồn|NGUỒN|Dẫn theo|DẪN THEO|Trích|TRÍCH|Kể theo|Phỏng theo|Sưu tầm)\b', re.IGNORECASE)
ATTRIBUTION_PUB = re.compile(r'\b(NXB|Nhà xuất bản)\b', re.IGNORECASE)
# Round 4 (Lane C request 5): a «… em hãy:» lead and the dash sub-items under it were served as body.
DASH_LEAD = re.compile(r'^\s*[-–—]\s+(?=\S)')
QUESTION_LEAD = re.compile(r'\b(em hãy|các em hãy|hãy)\s*:\s*$', re.IGNORECASE)
FRONT_MATTER = re.compile(r'^\s*(MỤC LỤC|Mục lục|LỜI NÓI ĐẦU|Lời nói đầu|HƯỚNG DẪN SỬ DỤNG SÁCH|BẢNG TRA CỨU|Bảng tra cứu|GIẢI THÍCH THUẬT NGỮ|PHỤ LỤC|Phụ lục|BẢNG THUẬT NGỮ)')
MATH = tc_cascade.MATH
# Round 4 (failure class 2: formula / number / unit fidelity) — deterministic guards, fail closed, never a guess:
#   UNIT_EXP  a length unit whose exponent every text-line OCR flattens («m2», «cm3», «1 360 m2» → the audit measured
#             «1 360 m²→1 360 m» and «m²→m?/m₴») — a block carrying such a token is withheld unless a parser labelled it
#             FORMULA/TABLE (same rule as the math guard).
#   CHEM      inline chemical formulas whose subscripts are flattened or dropped («AgNO₃»→«AgNO,», «NH₃»→«NH,», «H₂O»→
#             «H,O», «CO2»): an element-symbol run glued to a digit, or followed by a comma before a concentration
#             («AgNO, 1%») or another element symbol («H,O»).
UNIT_EXP = re.compile(r'(?<![A-Za-zÀ-ỹ])(?:m|cm|dm|km|mm)[23](?![\d.,])')
CHEM = re.compile(r'\b(?:[A-Z][a-z]?){1,4}\d(?:[A-Z][a-z]?\d?)*\b|\b(?:[A-Z][a-z]?){1,3},\s*(?=\d+(?:[.,]\d+)?\s*%)|\b[A-Z][a-z]?,[A-Z][a-z]?\b')
DIGIT_RUNS = re.compile(r'\d+')
DIGITS = re.compile(r'^\d{1,3}$')
LETTERS = re.compile(r'[A-Za-zÀ-ỹ]')


def upper_ratio(t):
    letters = [c for c in t if c.isalpha()]
    return (sum(1 for c in letters if c.isupper()) / len(letters)) if letters else 0.0


def ends_sentence(t):
    return bool(re.search(r'[.!?:;…]\s*$', t))


# ---------------------------------------------------------------- role assignment
def assign_role(b, ctx):
    """Deterministic role for one block. Returns (role, method, confidence, evidence[])."""
    t = (b['text'] or '').strip()
    lab = b.get('native_label')
    col = b.get('colour') or {}
    on_colour = (col.get('share') or 0) >= 0.30
    bb = b.get('bbox') or [0, 0, 1, 1]
    narrow_right = bb[2] < 0.45 and bb[0] > 0.45
    prev = ctx.get('prev_role')
    box_ctx = ctx.get('box')  # label of the coloured box this block sits in (objective / sidebar / activity / none)
    sgv = ctx.get('docType') == 'SGV'
    ev = []
    if b['role'] == 'FIGURE':
        return 'figure', 'native', 1.0, ['docling picture']
    if not t or not LETTERS.search(t) and not DIGITS.match(t):
        return 'empty', 'native', 1.0, ['no letters']
    if DIGITS.match(t) and (bb[1] > 0.9 or bb[1] < 0.07) and not ctx.get('big_digit'):
        return 'page_number', 'geometry', 0.95, ['digits in margin']
    if LESSON_HDR.match(t) and len(t) <= 120:
        return 'heading', 'lexicon', 0.97, ['lesson header "Bài N"']
    if ctx.get('big_digit'):
        return 'heading', 'geometry', 0.85, ['large standalone lesson number (elementary banner)']
    if lab == 'page_footer' or (bb[1] > 0.93 and len(t) < 40):
        return 'page_number' if DIGITS.match(t) else 'running_head', 'native', 0.9, ['footer band']
    if lab == 'page_header' or (bb[1] < 0.045 and len(t) < 50):
        return 'running_head', 'native', 0.85, ['header band']
    if b['role'] == 'TABLE':
        return 'table', 'native', 0.95, ['docling table']
    if b['role'] == 'FORMULA':
        return 'formula', 'native', 0.95, ['docling formula']
    if lab == 'footnote' or FOOTNOTE.match(t):
        return 'footnote', 'lexicon', 0.9, ['footnote mark']
    if ctx.get('inside_picture') and not (THEME_HDR.match(t) or (STAGE.match(t) and len(t) <= 45) or SIDEBAR_LABEL.match(t)):
        return 'figure_text', 'geometry', 0.85, ['inside docling picture bbox']
    if THEME_HDR.match(t) and len(t) <= 120:
        return 'heading', 'lexicon', 0.95, ['theme/chapter header']
    if STAGE.match(t) and len(t) <= 45:
        return 'stage_label', 'lexicon', 0.95, ['stage label']
    # Round 4 correctness review (F2): the attribution test must run BEFORE the two `upper_ratio >= 0.7`
    # heading rules. It used to sit after them, so an UPPERCASE «(THEO …)» / «(NGUỒN: …)» could never reach
    # it and became a `heading` — a role that is COLOUR_HEAVY_EXEMPT and that `build_page` then makes the
    # `heading_path` of every following block in the lesson. Only the title-case form ever worked.
    # Fail closed on both sides: a line the extractor itself labelled a caption keeps `caption`, a line that
    # ends in «?» is left to the question rules, and in an SGV it stays `teacher_text` (still withheld by
    # the `teacher_text` guard) exactly as before — only the role NAME changes there.
    if (lab != 'caption' and len(t) <= 220 and not re.search(r'\?\s*$', t)
            and (ATTRIBUTION.match(t) or (re.match(r'^\s*[(\[]', t) and ATTRIBUTION_PUB.search(t)))):
        return ('teacher_text' if sgv else 'attribution'), 'lexicon', 0.9, ['source attribution «(Theo …)» / publisher line']
    # (F2, same finding) a line that OPENS WITH A BRACKET is never a section heading — that is what made an
    # uppercase parenthesised source line a heading, and a heading_path, while its title-case twin stayed body.
    if upper_ratio(t) >= 0.7 and 3 <= len(t) <= 45 and not re.search(r'\?\s*$', t) and not DIGITS.match(t) and not re.match(r'^\s*[(\[]', t):
        return 'heading', 'typography', 0.88, ['short uppercase label']
    if ACTIVITY.match(t) and upper_ratio(ACTIVITY.sub('', t, count=1)) >= 0.7 and len(t) <= 120:
        return 'heading', 'lexicon+typography', 0.9, ['Hoạt động N. + UPPERCASE title']
    if CAPTION.match(t) or lab == 'caption':
        return 'caption', 'lexicon' if CAPTION.match(t) else 'native', 0.92 if CAPTION.match(t) else 0.8, ['caption marker' if CAPTION.match(t) else 'docling caption']
    if sgv and ANSWER.match(t):
        return 'answer', 'lexicon', 0.95, ['answer marker (SGV)']
    if ANSWER.match(t):
        return 'model_answer', 'lexicon', 0.93, ['answer marker']
    if sgv and ctx.get('answer_section'):
        return 'answer', 'context', 0.85, ['inside an SGV Đáp án section']
    if OPTION.match(t):
        return 'option', 'lexicon', 0.95, ['option marker A–D']
    if re.fullmatch(r'\s*\?\s*', t) or re.fullmatch(r'[\s?…._]+', t):
        return 'answer_slot', 'lexicon', 0.9, ['? / blank slot']
    if sgv and TEACHER.match(t):
        return 'teacher_text', 'lexicon', 0.9, ['GV/HS marker']
    if box_ctx == 'objective' and not re.search(r'\?\s*$', t):
        return 'objective', 'context', 0.85 if (OBJ_SENT.match(t) or OBJ_GENERIC.match(t)) else 0.75, ['inside MỤC TIÊU / objectives box'] + (['verb + "được"'] if (OBJ_SENT.match(t) or OBJ_GENERIC.match(t)) else [])
    if (OBJ_SENT.match(t) or OBJ_GENERIC.match(t)) and not re.search(r'\?\s*$', t):
        return 'objective', 'lexicon', 0.85, ['verb + "được"']
    if INSTRUCTION.match(t):
        return 'instruction', 'lexicon', 0.9, ['procedure marker']
    if ACTIVITY.match(t) and len(t) > 45:
        return 'activity', 'lexicon', 0.88, ['activity marker']
    if ACTIVITY.match(t):
        return 'stage_label', 'lexicon', 0.85, ['short activity label']
    if prev == 'instruction' and ENUM.match(t) and not re.search(r'\?\s*$', t) and not QHINT.search(t):
        return 'instruction', 'context', 0.8, ['numbered step after procedure marker']
    if box_ctx == 'activity' and (ENUM.match(t) or DIRECTIVE_ANY.search(t[:80])):
        return 'activity', 'context', 0.8, ['inside activity box']
    if SIDEBAR_LABEL.match(t):
        return 'sidebar', 'lexicon', 0.93, ['sidebar label']
    if box_ctx == 'sidebar':
        return 'sidebar', 'context', 0.85, ['inside labelled side box']
    # heading candidates
    if lab in ('section_header', 'title') and len(t) <= 100 and not re.search(r'\?\s*$', t) and not (ENUM.match(t) and QHINT.search(t)):
        return 'heading', 'native', 0.85, ['docling section_header']
    if upper_ratio(t) >= 0.7 and 3 <= len(t) <= 90 and not re.search(r'\?\s*$', t) and not re.match(r'^\s*[(\[]', t):
        return 'heading', 'typography', 0.85, ['uppercase run']
    if (ROMAN_SEC.match(t) or NUM_SEC.match(t)) and len(t) <= 70 and not ends_sentence(t) and not QHINT.search(ENUM.sub('', t)) and not DIRECTIVE_ANY.search(t) and t[len(ENUM.match(t).group(0)):][:1].isupper():
        return 'heading', 'lexicon', 0.75, ['numbered title-case section']
    # questions
    # A dash sub-item is read WITHOUT its bullet only under a question lead (previous block is a question, or
    # ends with «… hãy:»); everywhere else a leading dash stays part of the text, so dialogue lines in a
    # reading are not promoted to questions.
    dash = DASH_LEAD.match(t)
    lead_ctx = bool(dash) and (prev == 'question' or QUESTION_LEAD.search((ctx.get('prev_text') or '').strip()) is not None)
    core = ENUM.sub('', t[dash.end():] if lead_ctx else t, count=1)
    is_q = re.search(r'\?\s*$', t) is not None
    directive = (QHINT.search(core) is not None or QUESTION_LEAD.search(t) is not None) and len(t) < 400
    num_directive = ENUM.match(t) is not None and DIRECTIVE_ANY.search(core[:120]) is not None and len(t) < 400
    stem = False  # an enumerated line ending with ":" is a question stem ONLY when options follow (post-pass); alone it is a worked-example lead-in (Toán 7 p41)
    if is_q or directive or num_directive or stem:
        if sgv:
            return 'teacher_prompt', 'lexicon', 0.85, ['question form inside SGV → teacher prompt']
        conf = 0.92 if is_q else (0.85 if directive else (0.78 if num_directive else 0.75))
        ev = ['ends with ?'] if is_q else (['leading directive verb'] if directive else (['enumerator + directive verb'] if num_directive else ['enumerated stem ending with ":"']))
        if lead_ctx:
            ev = ev + ['dash sub-item under a question lead']
        if prev in ('activity', 'instruction') and not is_q:
            return 'activity', 'context', 0.7, ev + ['follows activity/instruction']
        return 'question', 'lexicon', conf, ev
    if sgv:
        return 'teacher_text', 'default', 0.7, ['SGV prose']
    if narrow_right and on_colour and len(t) >= 20:
        return 'sidebar', 'geometry', 0.75, ['narrow right box on colour']
    if ctx.get('xy_hint') == 'sidebar' and on_colour:
        return 'sidebar', 'geometry+verifier', 0.8, ['XY-cut sidebar hint + colour']
    if on_colour and prev == 'stage_label' and ctx.get('prev_text') and SIDEBAR_LABEL.match(ctx['prev_text']):
        return 'sidebar', 'context', 0.85, ['after sidebar label, on colour']
    return 'body', 'default', 0.6, ['prose']


def box_pass(blocks, mask):
    """Geometric box context for labels Docling orders AFTER their content (EM CÓ THỂ, Em có biết…):
    every block on colour that sits in the same column band, from just above the label to 0.45 page
    heights below it, becomes 'sidebar' (or 'objective' for MỤC TIÊU-type labels) unless it is a
    heading/caption/table/figure. Deterministic; measured on the dev gold before use."""
    labels = [b for b in blocks if b['role']['value'] in ('stage_label', 'heading') and (SIDEBAR_LABEL.match(b['text']) or re.match(r'^\s*(MỤC TIÊU|Mục tiêu)\s*$', b['text']))]
    for L in labels:
        kind = 'objective' if re.match(r'^\s*(MỤC TIÊU|Mục tiêu)', L['text']) else 'sidebar'
        lb = L['bbox']
        if not lb:
            continue
        for b in blocks:
            bb = b['bbox']
            if b is L or not bb or b['role']['value'] in ('heading', 'stage_label', 'caption', 'table', 'figure', 'figure_text', 'page_number', 'running_head', 'empty', 'footnote', 'option'):
                continue
            col = b.get('colour') or {}
            if (col.get('share') or 0) < 0.30:
                continue
            x_overlap = min(bb[0] + bb[2], lb[0] + lb[2] + 0.35) - max(bb[0], lb[0] - 0.05)
            if x_overlap <= 0.05:
                continue
            if lb[1] - 0.03 <= bb[1] <= lb[1] + 0.45:
                if b['role']['value'] != kind:
                    b['role']['value'] = kind; b['role']['coarse'] = COARSE[kind]; b['role']['method'] = 'geometry+label'
                    b['role']['confidence'] = 0.8; b['role']['evidence'] = b['role'].get('evidence', []) + [f'on colour under label "{L["text"][:20]}"']
    return blocks


def role_signal_pass(book, page, out_blocks, rules):
    """Apply the icon / box-tint rules of role_signal_experiment to the page's blocks (in place). Deterministic image
    features from a 72-dpi render; a block whose role the rules change records method `icon-signal:<rule>` and the
    signal it fired on. Silently a no-op when the PDF or numpy is unavailable (nothing is guessed)."""
    try:
        import role_signal_experiment as rse
    except Exception:  # pragma: no cover
        return 0
    if np is None:
        return 0
    rse.ROOT = ROOT
    img = rse.render(book, page, 72)
    if img is None:
        return 0
    hue, sat, mx = rse.hsv(img)
    heights = [b['bbox'][3] for b in out_blocks if b.get('bbox') and b.get('text') and len(b['text']) < 120]
    line_h = float(np.median(heights)) if heights else 0.015
    empty = dict(icon_present=False, icon_bucket=None, tint_share=0.0, tint_bucket=None, icon_hue=None, icon_h_ratio=None, icon_fill=None, strip_colour_frac=0.0, strip_ink_frac=0.0, tint_hue=None)
    blks = []
    for ob in out_blocks:
        f = rse.block_features(img, hue, sat, mx, ob['bbox'], line_h) if ob.get('bbox') else dict(empty)
        blks.append(dict(id=ob['id'], order=ob['order'], text=ob['text'], bbox=ob['bbox'], fine_role=ob['role']['value'], features=f))
    rse.inherit_box_icons(blks)
    rse.RULES = rules
    changed = 0
    for ob, b in zip(out_blocks, blks):
        new, rule = rse.apply_rules(b)
        ob['role']['signal'] = dict(icon=b.get('icon_eff'), icon_source=b.get('icon_source'), tint=b['features']['tint_share'], tint_bucket=b['features']['tint_bucket'], rules=rules)
        if rule and new != ob['role']['value']:
            ob['role'].update(value=new, coarse=COARSE.get(new, 'UNKNOWN'), method=f'icon-signal:{rule}', confidence=0.8,
                              evidence=ob['role'].get('evidence', []) + [f'{rule}: {b.get("icon_eff")} icon ({b.get("icon_source")})'])
            changed += 1
    return changed


# ---------------------------------------------------------------- figure / caption relation (failure class 5)
CAPTION_LABEL = re.compile(r'^\s*(Hình|Bảng|Sơ đồ|Biểu đồ|Lược đồ|Tranh|Ảnh)\s*\d+(?:[.\-]\d+)*\s*[.:]?\s*$', re.IGNORECASE)


def _cx_overlap(a, b):
    """Horizontal overlap of two [x, y, w, h] boxes (page fractions); ≤ 0 when they do not overlap."""
    return min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])


def caption_for_picture(pic_bbox, captions, med_h):
    """Round 4 (failure class 5) — WHICH caption belongs to this picture, decided by geometry, never by
    reading order.

    tc2-p1 linked a `caption` block to a picture by reading-order distance (`abs(order - rank) <= 2`). On a
    page carrying several pictures, badges and mascots that mislinks: Lane C's O5 (LS&ĐL 5 p039, the Lý Bí
    badge took caption «Hình 2»). A wrong caption is worse than none — the child is told the picture shows
    something it does not.

    A caption qualifies when it overlaps the picture HORIZONTALLY and one of:
      · it sits just BELOW the picture — gap ≤ 2.5 × the page's median line height (the printed convention);
      · it sits INSIDE the picture's lower band — Docling grows a picture box over its own caption
        (Khoa học 4 p30, Vật lí 10 p30, Toán 12 p20);
      · it sits just ABOVE the picture — held much tighter (≤ 1 × median line height), because a caption
        above is rare and a body line above is common.
    The nearest qualifying caption wins (inside first, then the smallest gap, then the largest overlap).
    Returns the caption block id, or None — a picture with no caption is honest.

    `captions` are SDM blocks (dicts with `id`, `bbox` and a `role`); non-caption roles are ignored.
    """
    if not pic_bbox:
        return None
    med_h = med_h or 0.01
    px, py, pw, ph = pic_bbox
    py1 = py + ph
    below_max, above_max = 2.5 * med_h, 1.0 * med_h
    inside_band = max(3.0 * med_h, 0.1 * ph)
    best = None
    for c in captions or []:
        bb = c.get('bbox')
        if not bb or (c.get('role') or {}).get('value') != 'caption':
            continue
        ov = _cx_overlap(pic_bbox, bb)
        if ov <= 0:
            continue
        cy0, cy1 = bb[1], bb[1] + bb[3]
        cyc = bb[1] + bb[3] / 2
        if py <= cyc <= py1:                       # inside the picture box
            if cyc < py1 - inside_band:
                continue                            # a label in the middle of the picture is figure text, not its caption
            key = (0, 0.0, -ov)
        elif cy0 >= py1:                            # below
            gap = cy0 - py1
            if gap > below_max:
                continue
            key = (1, gap, -ov)
        elif cy1 <= py:                             # above
            gap = py - cy1
            if gap > above_max:
                continue
            key = (1, gap, -ov)
        else:
            continue
        if best is None or key < best[0]:
            best = (key, c['id'])
    return best[1] if best else None


def caption_continuation_pass(blocks, med_h):
    """Round 4 (failure class 5) — a caption printed as «Hình 17.1» + its sentence in a SEPARATE block on the
    same printed line. tc2-p1 gave the label `caption` and left the sentence `body`: the audit saw the sentence
    served as lesson prose («caption fragment served as body», 1 of the 2 Bài 17 role errors).

    A block becomes the continuation of a caption label when ALL hold: the label is a bare «Hình/Bảng/… N»
    caption; the candidate starts on the same printed line (centre within ½ a line height); it starts within
    3 line heights to the right of the label; it is short (≤ 90 chars), carries no enumerator, and does not end
    a sentence. Deterministic, geometry + lexicon, no repair of any text. Returns how many blocks moved.
    """
    med_h = med_h or 0.01
    same_line, near_x, moved = 0.5 * med_h, 3.0 * med_h, 0
    labels = [b for b in blocks if b.get('bbox') and (b.get('role') or {}).get('value') == 'caption' and CAPTION_LABEL.match((b.get('text') or '').strip())]
    for lab in labels:
        lx, ly, lw, lh = lab['bbox']
        lyc, lx1 = ly + lh / 2, lx + lw
        for b in blocks:
            if b is lab or not b.get('bbox'):
                continue
            r = b.get('role') or {}
            if r.get('value') not in ('body',) or b.get('continues'):
                continue
            t = (b.get('text') or '').strip()
            if not t or len(t) > 90 or ENUM.match(t) or ends_sentence(t) or CAPTION_LABEL.match(t):
                continue
            bx, by, bw, bh = b['bbox']
            if abs((by + bh / 2) - lyc) > same_line:
                continue
            if not (0 <= bx - lx1 <= near_x):
                continue
            r.update(value='caption', coarse='CAPTION', method='caption-continuation',
                     evidence=list(r.get('evidence') or []) + [f'continues caption label {lab["id"]}'])
            b['continues'] = lab['id']
            moved += 1
    return moved


def question_box_pass(out_blocks, med_h):
    """Round 4 (Bài 17 p61, audit role error «question 2 of a ?-box served as sidebar»): a numbered line («2. …»)
    directly under a QUESTION block, in the same tinted box (both on colour, left edges within 0.03) and within two
    line heights, is the next question of that box — the narrow-right-box-on-colour geometry rule had made it a
    sidebar. Deterministic; the block keeps every guard."""
    seq = sorted([o for o in out_blocks if o['role']['value'] not in ('figure', 'empty', 'figure_text')], key=lambda o: o['order'])
    n = 0
    for prev, ob in zip(seq, seq[1:]):
        if ob['role']['value'] not in ('sidebar', 'body') or prev['role']['value'] != 'question':
            continue
        t = ob['text'] or ''
        if not re.match(r'^\s*\d{1,2}[.)]\s+\S', t):
            continue
        pb, bb = prev.get('bbox'), ob.get('bbox')
        pc, oc = (prev.get('colour') or {}).get('share') or 0, (ob.get('colour') or {}).get('share') or 0
        if not pb or not bb or pc < 0.2 or oc < 0.2 or abs(pb[0] - bb[0]) > 0.03:
            continue
        if bb[1] - (pb[1] + pb[3]) > 2.0 * med_h:
            continue
        ob['role'].update(value='question', coarse='QUESTION', method='context', confidence=0.8, evidence=ob['role'].get('evidence', []) + ['numbered item under a question in the same tinted box'])
        n += 1
    return n


COARSE = {'question': 'QUESTION', 'option': 'OPTION', 'answer_slot': 'OPTION', 'heading': 'HEADING', 'stage_label': 'HEADING', 'running_head': 'HEADING',
          'body': 'BODY', 'objective': 'BODY', 'activity': 'BODY', 'instruction': 'BODY', 'answer': 'BODY', 'model_answer': 'BODY', 'teacher_text': 'BODY', 'teacher_prompt': 'BODY', 'rule': 'BODY',
          'attribution': 'BODY',
          'caption': 'CAPTION', 'sidebar': 'SIDEBAR', 'table': 'TABLE', 'formula': 'FORMULA', 'figure_text': 'FIGURE_TEXT', 'figure': 'FIGURE', 'footnote': 'FOOTNOTE', 'page_number': 'PAGENUM', 'empty': 'UNKNOWN'}
NON_LEARNING = {'page_number', 'running_head', 'figure', 'figure_text', 'empty'}
# tc_layout_census marks a PAGE `color_heavy` at colour share ≥ 0.25; round 4 measures the same share on the
# block's own bbox instead of inheriting the page's verdict. Same constant, smaller measurement window.
COLOUR_HEAVY_SHARE = 0.25
COLOUR_HEAVY_EXEMPT = ('heading', 'stage_label', 'page_number', 'running_head', 'caption', 'figure', 'empty')


def colour_heavy_withholds(page_color_heavy, role, colour):
    """Round 4 (Lane C request 3) — does the colour-heavy guard withhold THIS block?

    `color_heavy` is a PAGE property of the census: ≥ 25 % of the page's pixels are saturated colour
    (tc_layout_census §color_heavy). tc2-p1 applied that page verdict to every block on the page, so a
    theme-opener with a full-bleed photograph withheld the white-column body text printed beside it —
    LS&ĐL 5 Bài 8's header page lost 15 / 15 of its learning-text blocks, and the «Âu Lạc (179 TCN)»
    timeline anchor with them (Lane C, 05-GOLDEN-SLICE-2-GATE §1).

    The page flag still decides WHICH pages are examined at all — no page the census never flagged becomes
    trustable here. Inside such a page the block's OWN measured colour share decides, against the census's
    own 0.25. Fail closed: when there is no colour mask (no PDF, no numpy) the page verdict withholds
    exactly as it did before.
    """
    if not page_color_heavy or role in COLOUR_HEAVY_EXEMPT:
        return False
    if colour is None:
        return True
    return (colour.get('share') or 0) >= COLOUR_HEAVY_SHARE


# ---------------------------------------------------------------- agreement (per block: text as tc_cascade.verify; order by LIS)
def longest_nondecreasing(seq):
    """Indices of one longest non-decreasing subsequence of `seq` (O(n log n); ties keep the earlier element,
    so a stable primary order is preferred). Deterministic."""
    import bisect
    if not seq:
        return set()
    tails, tails_idx, prev = [], [], [-1] * len(seq)
    for i, v in enumerate(seq):
        k = bisect.bisect_right(tails, v)
        if k == len(tails):
            tails.append(v); tails_idx.append(i)
        else:
            tails[k] = v; tails_idx[k] = i
        prev[i] = tails_idx[k - 1] if k > 0 else -1
    out, i = set(), tails_idx[-1]
    while i != -1:
        out.add(i); i = prev[i]
    return out


def _earliest_acceptable(pk, st, base=0):
    """Earliest window of `st` (a stream suffix starting at absolute offset `base`) that aligns with `pk` at
    ≥ TEXT_SIM: the best alignment is found, then the text BEFORE it is searched again for an earlier one, until
    none qualifies. → (score, start, end) with absolute offsets, or (best_score, -1, -1)."""
    best = None
    lo, hi = 0, len(st)
    while hi - lo >= 4:
        al = fuzz.partial_ratio_alignment(pk, st[lo:hi])
        if al is None or al.score < TEXT_SIM:
            if best is None:
                best = (al.score if al else 0.0, -1, -1)
            break
        best = (al.score, base + lo + al.dest_start, base + lo + al.dest_end)
        hi = lo + al.dest_start          # look for an even earlier acceptable window
    return best or (0.0, -1, -1)


def align_in_stream(pk, st, last_pos):
    """Where does primary text `pk` sit in the verifier stream `st`?
    Round 4: (1) prefer the earliest acceptable match AT OR AFTER the previous aligned block (`last_pos`) — a page
    that repeats a label («Cách tiếp cận:» twice on SGV Toán 4 p54, «Tiến hành:» in every experiment box) must
    not send the second occurrence to the first one; (2) only when nothing after `last_pos` reaches TEXT_SIM is
    the whole stream searched (a block Docling displaced to the end of the page really is earlier in the
    verifier — that is the order disagreement the LIS then reports). Short texts (< 12 chars) are located
    verbatim on word boundaries the same way."""
    if len(pk) >= 12:
        if last_pos > 0 and len(st) - last_pos >= 4:
            score, start, end = _earliest_acceptable(pk, st[last_pos:], last_pos)
            if start >= 0:
                return score, start, end
        return _earliest_acceptable(pk, st, 0)
    padded = ' ' + st + ' '
    idx = padded.find(' ' + pk + ' ', max(0, last_pos))
    if idx < 0:
        idx = padded.find(' ' + pk + ' ')
    return (100.0, idx, idx + len(pk)) if idx >= 0 else (0.0, -1, -1)


def agreement(primary_blocks, verifier):
    """Per primary block: text agreement (partial-ratio alignment inside the verifier's reading-order stream,
    ≥ TEXT_SIM) and ORDER agreement.

    Round 4 (failure class: two-column / displaced-box reading order). The tc2-p1 rule compared each block's
    alignment offset with the minimum of the two previous offsets («one-block tolerance»), which (a) never
    flags an adjacent swap and (b) withholds only the FIRST block of a displaced group — Docling moves a whole
    MỤC TIÊU box or a title to the end of the page (KHTN 8 p96, Toán 12 p20) and the gate let the rest of the
    group through, so every block between the group's true and displaced positions was delivered inverted.
    Now the blocks that agree on text are the sequence of their verifier offsets; the longest non-decreasing
    subsequence is the order both stacks share, every block outside it is an order disagreement
    (`agree_order`, fail closed), and `vpos` lets build_page RE-SEQUENCE the page by the verifier's offsets so
    a displaced (withheld) box is at least placed where the geometry saw it instead of dragging its neighbours
    into inversions. Short blocks (< 12 chars) are located at their first occurrence at or after the previous
    aligned block, not the first on the page (repeated labels such as «Tiến hành:»)."""
    st, roles = tc_cascade._stream(verifier)
    vblocks = [v for v in verifier['blocks'] if tc_score.norm_key(v['text'])]
    out = []
    last_pos = 0
    for p in primary_blocks:
        pk = tc_score.norm_key(p['text'])
        a = dict(text_sim=None, verifier_id=None, verifier_role=None, order_ok=None, ok=False, reason=None, vpos=None, vend=None)
        if not pk or p['role'] == 'FIGURE':
            a['reason'] = None if p['role'] == 'FIGURE' else 'empty'; out.append(a); continue
        if fuzz is None or not st:
            a['reason'] = 'agree_text'; out.append(a); continue
        score, start, end = align_in_stream(pk, st, last_pos)
        a['text_sim'] = round(float(score), 1)
        if score < TEXT_SIM:
            a['reason'] = 'agree_text'; out.append(a); continue
        vi = next((k for k, (s0, s1, r) in enumerate(roles) if s0 <= start < s1), None)
        a['verifier_role'] = roles[vi][2] if vi is not None else None
        a['verifier_id'] = vblocks[vi]['id'] if vi is not None and vi < len(vblocks) else None
        a['vpos'] = start; a['vend'] = end; a['vtext'] = st[start:end]
        a['vraw'] = [vblocks[k]['text'] for k, (s0, s1, r) in enumerate(roles) if s0 < end and s1 > start and k < len(vblocks)]
        last_pos = max(last_pos, end)
        out.append(a)
    aligned = [i for i, a in enumerate(out) if a['vpos'] is not None]
    keep = longest_nondecreasing([out[i]['vpos'] for i in aligned])
    for k, i in enumerate(aligned):
        if k in keep:
            out[i]['order_ok'] = True; out[i]['ok'] = True
        else:
            out[i]['order_ok'] = False; out[i]['reason'] = 'agree_order'
    return out


def _x_overlap(a, b):
    if not a or not b:
        return 0.0
    return max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])) / max(1e-6, min(a[2], b[2]))


def _y_overlap(a, b):
    if not a or not b:
        return 0.0
    return max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])) / max(1e-6, min(a[3], b[3]))


def _move_is_geometric(i, seq, agree, bboxes):
    """The verifier's slot for block i is accepted only when it agrees with the page geometry, judged against
    the agreed blocks (LIS) around it in `seq`: (1) column band — a block that x-overlaps i (≥ 0.3 of the
    narrower) and precedes i must lie above i's centre, one that follows must lie below (tolerance half the
    block height); (2) row band — a block that y-overlaps i (≥ 0.5 of the shorter) and precedes i must lie to
    its LEFT, one that follows to its RIGHT (two side-by-side captions read right-to-left by the verifier stay
    where the primary put them). A block with no such neighbour keeps its primary position."""
    bi = bboxes[i]
    if not bi:
        return False
    yc = bi[1] + bi[3] / 2; xc = bi[0] + bi[2] / 2
    tol = max(0.004, bi[3] / 2)
    pos = seq.index(i)
    seen = False
    for k, j in enumerate(seq):
        if j == i or not (agree[j].get('vpos') is not None and agree[j].get('order_ok')):
            continue
        bj = bboxes[j]
        if not bj:
            continue
        if _y_overlap(bi, bj) >= 0.5 and _x_overlap(bi, bj) < 0.3:
            seen = True
            xj = bj[0] + bj[2] / 2
            if (k < pos and xj > xc) or (k > pos and xj < xc):
                return False
            continue
        if _x_overlap(bi, bj) < 0.3:
            continue
        seen = True
        yj = bj[1] + bj[3] / 2
        if k < pos and yj > yc + tol:
            return False
        if k > pos and yj < yc - tol:
            return False
    return seen


TOKEN = re.compile(r'[0-9A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+')


def tone_tokens(text):
    """[(diacritic-stripped key, tone-placement-normalised token)] for the Vietnamese word tokens of `text`."""
    out = []
    for tok in TOKEN.findall(tc_score.nfc(text or '').lower()):
        out.append((tc_score.norm_key(tok), tc_score.norm_tone_placement(tok)))
    return out


def tone_disagreements(primary_text, verifier_texts):
    """Round 4 (cross-lane finding from A-runtime: «vặn khoa lại» served trusted for «vặn khóa lại»). The text-agreement
    gate compares diacritic-STRIPPED strings, so it is blind to tone marks by construction. This compares the two
    stacks token by token WITH diacritics: tokens are matched on their stripped form (difflib, so extra neighbour
    text in the verifier blocks is skipped); a matched token whose tone-placement-normalised forms differ («khoa» vs
    «khóa», «lặng» vs «lăng») is a tone disagreement. → [(primary token, verifier token)] (nothing is repaired)."""
    pt = tone_tokens(primary_text)
    vt = tone_tokens(' '.join(verifier_texts or []))
    if not pt or not vt:
        return []
    sm = difflib.SequenceMatcher(None, [k for k, _ in pt], [k for k, _ in vt], autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal':
            continue
        for k in range(i2 - i1):
            if pt[i1 + k][1] != vt[j1 + k][1]:
                out.append((pt[i1 + k][1], vt[j1 + k][1]))
    return out


def numbers_disagree(primary_text, verifier_window):
    """True when the two OCR stacks read different digit runs for the same aligned text. The verifier window is the
    stream slice the primary text aligned to, so its digit runs must equal the primary's. Only a run that touches
    the window's first or last character may be a neighbour's run cut by the fuzzy alignment — such an edge run
    may be dropped from the comparison; an interior run the primary lacks (a dropped footnote mark, «(2)»→«(<)»)
    or a run the two stacks read differently («(1, 0)»→«(1, O)») is a disagreement."""
    p_full = DIGIT_RUNS.findall(tc_score.norm_key(primary_text or ''))
    p_noenum = DIGIT_RUNS.findall(tc_score.norm_key(ENUM.sub('', primary_text or '', count=1)))   # a leading enumerator («3.», «Bước 5.») is structure, not data: the verifier may hold it in another block
    w = verifier_window or ''
    runs = [(m.start(), m.end(), m.group()) for m in DIGIT_RUNS.finditer(w)]
    v = [r[2] for r in runs]
    first_edge = bool(runs) and runs[0][0] == 0
    last_edge = bool(runs) and runs[-1][1] == len(w)
    cands = [v]
    if first_edge:
        cands.append(v[1:])
    if last_edge:
        cands.append(v[:-1])
    if first_edge and last_edge and len(v) >= 2:
        cands.append(v[1:-1])
    return not any(c == p for c in cands for p in (p_full, p_noenum))


def resequence(agree, bboxes=None):
    """Reading order for the page. Everything the two stacks agree on (the LIS) and everything without verifier
    evidence (figures, empty, text disagreements) keeps the primary (Docling) order; ONLY a block whose position
    the verifier contradicts (`agree_order`, i.e. outside the LIS) is moved — to just after the last agreed
    block whose verifier offset is ≤ its own (to the front when none) — and only when that slot agrees with the
    page geometry (`_move_is_geometric`: vertical order inside the block's own column band). So a MỤC TIÊU box
    Docling appended to the page goes back under the title (geometry confirms: it sits between the title and
    the first paragraph), while a verifier that read two side-by-side captions right-to-left, or two columns as
    one block, cannot drag blocks around. The block stays withheld (`agree_order`) either way — the move only
    decides where its card is shown. Returns the primary indices in reading order (deterministic)."""
    bboxes = bboxes or [None] * len(agree)
    moved = [i for i, a in enumerate(agree) if a.get('vpos') is not None and a.get('order_ok') is False]
    kept = [i for i in range(len(agree)) if i not in set(moved)]
    for i in moved:
        v = agree[i]['vpos']
        anchor = None
        for j in kept:
            if agree[j].get('vpos') is not None and agree[j].get('order_ok') and agree[j]['vpos'] <= v:
                anchor = j
        trial = list(kept)
        at = 0 if anchor is None else trial.index(anchor) + 1
        # a displaced GROUP (title + MỤC TIÊU box …) shares one anchor: keep the group's own verifier order
        while at < len(trial) and agree[trial[at]].get('moved') and agree[trial[at]].get('vpos') is not None and agree[trial[at]]['vpos'] <= v:
            at += 1
        trial.insert(at, i)
        if _move_is_geometric(i, trial, agree, bboxes):
            kept = trial
            agree[i]['moved'] = True
        else:
            # keep the primary slot: insert after the nearest preceding primary index already placed
            prev = [j for j in kept if j < i]
            kept.insert((kept.index(max(prev)) + 1) if prev else 0, i)
            agree[i]['moved'] = False
    return kept


# ---------------------------------------------------------------- census + OCR helpers
_census = {}


def census_row(book, page):
    if not _census:
        p = f'{ROOT}/poc-out/trusted-corpus/tc-v1/census/pages.jsonl'
        if os.path.exists(p):
            for line in open(p):
                j = json.loads(line)
                _census[(j['book'], j['page'])] = j
        _census[('_', 0)] = True
    return _census.get((book, page))


def ocr_lines(book, page):
    p = f'{OCR}/{book}/p{page:03d}.json'
    return json.load(open(p))['lines'] if os.path.exists(p) else []


def inside(bb, box, frac=0.6):
    """share of bb's area inside box ≥ frac"""
    if not bb or not box:
        return False
    ix = max(0, min(bb[0] + bb[2], box[0] + box[2]) - max(bb[0], box[0])); iy = max(0, min(bb[1] + bb[3], box[1] + box[3]) - max(bb[1], box[1]))
    return (ix * iy) >= frac * max(1e-9, bb[2] * bb[3])


# ---------------------------------------------------------------- build one page
def build_page(book, page, pipeline=PIPELINE_ID, docType=None, role_signal=None):
    role_signal = role_signal if role_signal is not None else ROLE_SIGNAL
    rawD, srcD = load_raw('docling-ocrmac', book, page, pipeline)
    rawX, srcX = load_raw('current-xycut', book, page, pipeline)
    if rawD is None or rawX is None:
        return None
    blocks, pics, tables = adapt_docling_v2(rawD['result'])
    X, xmeta = tc_sdm.adapt_current_xycut(rawX['result'])
    verifier = dict(book=book, page=page, candidate='current-xycut', blocks=X, meta=xmeta)
    docType = docType or ('SGV' if '-sgv-' in book else 'SGK')
    cen = census_row(book, page) or {}
    lines = ocr_lines(book, page)
    med_h = statistics.median([l['h'] for l in lines]) if lines else 0.01
    mask = colour_mask(book, page)
    agree = agreement(blocks, verifier)
    order_map = resequence(agree, [b['bbox'] for b in blocks])   # reading order → primary (Docling) index
    xy_by_id = {b['id']: b for b in X}
    # printed page from footer digits
    printed = None
    for l in lines[-4:] + lines[:2]:
        t = l['text'].strip()
        if DIGITS.match(t) and (l['y'] > 0.88 or l['y'] < 0.08):
            printed = int(t)
    front_matter = any(FRONT_MATTER.match(l['text'].strip()) for l in lines[:6])
    # per block
    prev_role = None; prev_text = None; box = None; heading_path = []; answer_section = False
    out_blocks = []
    for rank, pi in enumerate(order_map):
        b, a = blocks[pi], agree[pi]
        bb = b['bbox']
        col = colour_of(mask, bb)
        b['colour'] = col
        # OCR conf + enumerator cross-check from the OCR lines under the bbox
        under = [l for l in lines if bb and (bb[0] - 0.01 <= l['x'] + l['w'] / 2 <= bb[0] + bb[2] + 0.01) and (bb[1] - 0.005 <= l['y'] + l['h'] / 2 <= bb[1] + bb[3] + 0.005)]
        b['ocr_conf'] = round(sum(l.get('conf', 1) for l in under) / len(under), 3) if under else None
        if under and b['text']:
            first = sorted(under, key=lambda l: (l['y'], l['x']))[0]['text'].strip()
            me = ENUM.match(first); mb = ENUM.match(b['text'])
            if me and not mb and tc_score.norm_key(first[len(me.group(0)):])[:12] and tc_score.norm_key(b['text']).startswith(tc_score.norm_key(first[len(me.group(0)):])[:12]):
                b['text'] = me.group(0).strip() + ' ' + b['text']; b['enumerator_restored'] = True
        inside_pic = any(inside(bb, p['bbox'], 0.6) for p in pics) if bb else False
        xy_hint = xy_by_id.get(a.get('verifier_id'), {}).get('native_label') if a.get('verifier_id') else None
        # elementary lesson banner: a standalone 1–2 digit number printed ≥ 1.4× the median line height near the top
        big_digit = bool(DIGITS.match((b['text'] or '').strip())) and bb is not None and bb[1] < 0.3 and any(l['h'] >= 1.4 * med_h and DIGITS.match(l['text'].strip()) for l in under)
        ctx = dict(prev_role=prev_role, prev_text=prev_text, box=box, docType=docType, inside_picture=inside_pic and b['role'] not in ('TABLE',), xy_hint=xy_hint, big_digit=big_digit, answer_section=answer_section)
        role, method, rconf, ev = assign_role(b, ctx)
        # coloured-box context: a stage label / sidebar label / objective marker opens a box until the colour ends
        t = (b['text'] or '').strip()
        if role == 'stage_label' or role == 'heading':
            if re.match(r'^\s*(MỤC TIÊU|Mục tiêu)', t) or (OBJ_BOX.search(t) and len(t) < 80):
                box = 'objective'
            elif SIDEBAR_LABEL.match(t):
                box = 'sidebar'
            elif ACTIVITY.match(t) or re.match(r'^\s*(THỰC HÀNH|Thực hành|HOẠT ĐỘNG|Hoạt động)', t):
                box = 'activity'
            else:
                box = None
            answer_section = bool(re.search(r'(Đáp án|ĐÁP ÁN|Lời giải|LỜI GIẢI|Hướng dẫn giải|Gợi ý trả lời)', t)) if docType == 'SGV' else False
        elif role in ('answer', 'model_answer') and re.match(r'^\s*(Đáp án|ĐÁP ÁN|Lời giải|Hướng dẫn giải)\s*:?\s*$', t):
            answer_section = True
        elif not (col and col.get('share', 0) >= 0.2):
            box = None
        if OBJ_BOX.search(t) and len(t) < 40 and role in ('body', 'teacher_text', 'objective'):
            box = 'objective'  # "Sau bài học, HS sẽ:" / "Sau bài học này, em sẽ:" opens an objectives list
        conflict = False
        if role == 'question' and xy_hint == 'heading':
            conflict = True
        if role == 'sidebar' and xy_hint == 'sidebar':
            rconf = min(0.98, rconf + 0.05); ev = ev + ['XY-cut agrees: sidebar']
        # heading path
        if role == 'heading':
            if LESSON_HDR.match(t):
                heading_path = [t[:80]]
            elif THEME_HDR.match(t):
                heading_path = [t[:80]]
            elif ROMAN_SEC.match(t):
                heading_path = heading_path[:1] + [t[:80]]
            else:
                heading_path = heading_path[:2] + [t[:80]]
        # guards
        guards = []
        learning = role not in NON_LEARNING
        if role == 'empty' or not t:
            guards.append('empty_block')
        if role in ('page_number', 'running_head'):
            guards.append('furniture')
        if role == 'figure_text':
            guards.append('figure_text')
        if not a['ok'] and role not in ('figure', 'empty', 'page_number', 'running_head'):
            if a['reason'] == 'agree_order' and role in FLEX_ROLES:
                ev = ev + ['order_flex: verifier places this flex block elsewhere (not withheld)']
            else:
                guards.append(a['reason'] or 'agree_text')
        if conflict:
            guards.append('role_conflict')
        if role not in ('formula', 'table', 'figure', 'empty') and MATH.search(t):
            guards.append('math_guard')
        if role not in ('formula', 'table', 'figure', 'empty') and UNIT_EXP.search(t):
            guards.append('unit_guard')
        if role not in ('formula', 'table', 'figure', 'empty', 'page_number', 'running_head') and CHEM.search(t):
            guards.append('chem_guard')
        if a.get('ok') and a.get('vtext') is not None and numbers_disagree(t, a['vtext']):
            guards.append('agree_numbers')
        tones = tone_disagreements(t, a.get('vraw')) if a.get('ok') else []
        if tones:
            guards.append('agree_tones')
        if col and bb and bb[3] >= 1.8 * med_h and bb[2] >= 0.15:
            lr = (col['left'], col['right']); tb = (col['top'], col['bottom'])
            if (max(lr) >= 0.5 and min(lr) <= 0.08) or (max(tb) >= 0.5 and min(tb) <= 0.08):
                guards.append('box_boundary')
        refers_fig = bool(FIG_REF.search(t))
        if refers_fig and role in ('question', 'activity', 'instruction', 'teacher_prompt'):
            guards.append('figure_dependent')
        if role in ('answer', 'model_answer') or ANSWER_INLINE.search(t):
            guards.append('answer_leak')
        if role in ('teacher_text', 'teacher_prompt'):
            guards.append('teacher_text')
        if colour_heavy_withholds(cen.get('color_heavy'), role, col):
            guards.append('page_feature:color_heavy')
        if cen.get('diagram') and role in ('body', 'sidebar', 'question', 'activity', 'instruction', 'objective') and (inside_pic or (len(t) < 30 and not ends_sentence(t))):
            guards.append('page_feature:diagram')
        if b['ocr_conf'] is not None and b['ocr_conf'] < 0.6:
            guards.append('low_ocr_conf')
        withhold = [g for g in guards if g not in ('enumerator_restored',)]
        status = 'TRUSTED' if not withhold else ('CONFLICT' if any(g in ('role_conflict', 'agree_order') for g in withhold) and 'agree_text' not in withhold else 'WITHHELD')
        if role in ('figure', 'empty'):
            status = 'WITHHELD'
        sdm_id = f'{book}:p{page:03d}:{pipeline}:{b["order"]:03d}'   # id = the primary's native block index (stable across re-sequencing)
        ob = dict(id=sdm_id, order=rank, native_order=b['order'], native_label=b.get('native_label'), text=b['text'], text_docling=b.get('text_docling'), enumerator_restored=bool(b.get('enumerator_restored')),
                  bbox=bb, column=(1 if bb and bb[0] + bb[2] / 2 < 0.5 else 2) if bb else None, ocr_conf=b['ocr_conf'], colour=col, extraction=b.get('extraction'),
                  agreement=dict(text_sim=a['text_sim'], verifier_id=a['verifier_id'], verifier_role=a['verifier_role'], order_ok=a['order_ok'], verifier_pos=a.get('vpos'), moved=a.get('moved', False), tone_disagreements=tones[:6]),
                  role=dict(value=role, coarse=COARSE.get(role, 'UNKNOWN'), method=method, confidence=round(rconf, 2), evidence=ev, verifier_hint=xy_hint, conflict=conflict),
                  guards=guards, trust=dict(status=status, reasons=withhold), learning=learning, refers_figure=refers_fig, heading_path=list(heading_path),
                  lesson=None, cells=b.get('cells'))
        out_blocks.append(ob)
        prev_role = role; prev_text = t
    # post-passes: (1) box context for labels ordered after their content; (2) MCQ stem = enumerated body followed by an option
    box_pass(out_blocks, mask)
    for i, ob in enumerate(out_blocks):
        nxt = next((o for o in out_blocks[i + 1:] if o['role']['value'] not in ('figure', 'empty', 'figure_text')), None)
        if ob['role']['value'] == 'body' and ENUM.match(ob['text'] or '') and nxt is not None and nxt['role']['value'] == 'option' and docType != 'SGV':
            ob['role'].update(value='question', coarse='QUESTION', method='context', confidence=0.8, evidence=ob['role']['evidence'] + ['enumerated stem followed by options'])
    question_box_pass(out_blocks, med_h)
    caption_continuation_pass(out_blocks, med_h)
    if role_signal:
        role_signal_pass(book, page, out_blocks, role_signal)
    # re-derive trust for blocks whose role changed in the post-passes (guards that depend on the role)
    for ob in out_blocks:
        r = ob['role']['value']
        g = [x for x in ob['guards'] if x not in ('figure_dependent', 'answer_leak', 'teacher_text')]
        if ob['refers_figure'] and r in ('question', 'activity', 'instruction', 'teacher_prompt'):
            g.append('figure_dependent')
        if r in ('answer', 'model_answer') or ANSWER_INLINE.search(ob['text'] or ''):
            g.append('answer_leak')
        if r in ('teacher_text', 'teacher_prompt'):
            g.append('teacher_text')
        ob['guards'] = g
        withhold = [x for x in g if x != 'enumerator_restored']
        ob['trust']['reasons'] = withhold
        ob['trust']['status'] = 'TRUSTED' if not withhold else ('CONFLICT' if any(x in ('role_conflict', 'agree_order') for x in withhold) and 'agree_text' not in withhold else 'WITHHELD')
        if r in ('figure', 'empty'):
            ob['trust']['status'] = 'WITHHELD'
        ob['learning'] = r not in NON_LEARNING
    # figures: pictures + their labels + captions
    figures = []
    rank_of_native = {ob['native_order']: ob['order'] for ob in out_blocks}
    for k, p in enumerate(pics):
        p_rank = rank_of_native.get(p['order'], p['order'])
        labels = [ob['id'] for ob in out_blocks if ob['role']['value'] == 'figure_text' and inside(ob['bbox'], p['bbox'], 0.6)]
        # Round 4 (failure class 5): geometry decides the caption, not reading-order distance. Fail closed —
        # a picture whose caption cannot be placed geometrically carries no caption.
        # One caption may legitimately serve side-by-side pictures, so it is not consumed by the first of them.
        cap = caption_for_picture(p['bbox'], [ob for ob in out_blocks if ob['role']['value'] == 'caption'], med_h)
        figures.append(dict(id=f'{book}:p{page:03d}:fig{k:02d}', bbox=p['bbox'], labels=labels, caption=cap))
    stats = Counter(ob['trust']['status'] for ob in out_blocks if ob['learning'])
    reasons = Counter(r for ob in out_blocks if ob['learning'] for r in ob['trust']['reasons'])
    roles = Counter(ob['role']['value'] for ob in out_blocks)
    return dict(book=book, page=page, printed_page=printed, docType=docType, pipeline=pipeline, sdm_version=SDM_VERSION, role_signal=role_signal or None,
                source=dict(docling_raw=srcD, xycut_raw=srcX, docling_seconds=rawD.get('seconds'), xycut_page_trusted=xmeta.get('page_trusted') if xmeta else None),
                page_size=list(rawD['result']['docling']['pages'].values())[0]['size'], features=dict(diagram=cen.get('diagram'), color_heavy=cen.get('color_heavy'), formula=cen.get('formula'), table=cen.get('table'), sidebar=cen.get('sidebar'), figure=cen.get('figure'), side_by_side=cen.get('side_by_side'), continuation=cen.get('continuation'), front_matter=front_matter),
                blocks=out_blocks, figures=figures, tables=tables, stats=dict(learning=dict(stats), reasons=dict(reasons), roles=dict(roles), blocks=len(out_blocks)))


def sdm_path(pipeline, book, page, gold=False):
    return f'{out_root(pipeline)}/{"sdm-gold" if gold else "sdm"}/{book}/p{page:03d}.sdm.json'


def to_v1_sdm(sdm):
    """Project an SDM-v2 page to the tc-v1 SDM block shape so tc_score.score() measures it unchanged."""
    blocks = []
    for ob in sdm['blocks']:
        blocks.append(dict(id=ob['id'], order=ob['order'], role=ob['role']['coarse'], text=ob['text'], bbox=ob['bbox'],
                           trusted=(ob['trust']['status'] == 'TRUSTED') if ob['role']['value'] != 'figure' else None,
                           native_label=ob['native_label'], column=ob['column'], extraction=ob['extraction'], confidence=ob['ocr_conf'], fine_role=ob['role']['value'], reasons=ob['trust']['reasons']))
    return dict(book=sdm['book'], page=sdm['page'], candidate='tc2-sdm', seconds=sdm['source'].get('docling_seconds'), meta=dict(cascade=True), blocks=blocks)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pipeline', default=PIPELINE_ID); ap.add_argument('--pages', action='append', default=[])
    ap.add_argument('--gold', action='store_true'); ap.add_argument('--page', nargs=2, default=None); ap.add_argument('--force', action='store_true')
    ap.add_argument('--out', default=None, help='pipeline output root (default poc-out/trusted-corpus/tc-v2/<pipeline>; env TC2_OUT_ROOT)')
    ap.add_argument('--role-signal', default=None, choices=('v2', 'v3'), help='apply the icon / box-tint role rules of ROLE-LAYER-SIGNAL-EXPERIMENT (default: off; env TC2_ROLE_SIGNAL)')
    a = ap.parse_args()
    if a.out:
        tc2_paths.set_out_root(a.out)
    if a.role_signal:
        global ROLE_SIGNAL
        ROLE_SIGNAL = a.role_signal
    if a.page:
        s = build_page(a.page[0], int(a.page[1]), a.pipeline)
        if not s:
            raise SystemExit('no raw for that page')
        print(json.dumps({k: v for k, v in s.items() if k != 'blocks'}, ensure_ascii=False))
        for ob in s['blocks']:
            print(f"{ob['order']:>3} {ob['role']['value']:<13} {ob['trust']['status']:<8} {','.join(ob['trust']['reasons']):<28} {str([round(v, 2) for v in ob['bbox']]) if ob['bbox'] else '-':<26} {ob['text'][:80]!r}")
        return
    pages = [p for pf in a.pages for p in json.load(open(pf))]
    if a.gold:
        pages = [dict(book=g['book'], page=g['page']) for g in tc_sdm.all_gold()]
    n = skipped = missing = 0
    for p in pages:
        out = sdm_path(a.pipeline, p['book'], int(p['page']), a.gold)
        if os.path.exists(out) and not a.force:
            skipped += 1; continue
        s = build_page(p['book'], int(p['page']), a.pipeline)
        if s is None:
            missing += 1; continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        json.dump(s, open(out, 'w'), ensure_ascii=False)
        n += 1
    print(f'sdm built={n} skipped={skipped} missing_raw={missing}')


if __name__ == '__main__':
    main()
