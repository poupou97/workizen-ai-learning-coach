"""LANE C (round 3, WAL-210) — shared read-only helpers.

Every script in this package READS the gitignored corpus outputs of the main
checkout (``--root``) and WRITES only under ``<root>/poc-out/round3/lane-c/``.
Nothing here modifies an older output, builds a pack, or touches ``lib/``.

Label convention used in every emitted table (Founder D5):
  MEASURED   — counted by this script from data on disk
  DOC-CLAIM  — quoted from a research document, not re-measured here
  ESTIMATED  — extrapolated
  HYPOTHESIS — a lexical / structural signal that stands in for a shape
               the pipeline does not yet extract
"""
import glob
import json
import os
import re
from collections import Counter

DEFAULT_ROOT = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
OUT_REL = 'poc-out/round3/lane-c'

# Subject → family. Families are the unit the Founder asked about
# (History/Geography, Math, Vietnamese/Literature, Informatics, English,
# primary grades). Primary is a GRADE cut applied on top of the subject.
FAMILY = {
    'Khoa học': 'science', 'KHTN': 'science', 'Vật lí': 'science', 'Hoá học': 'science',
    'Sinh học': 'science', 'TN&XH': 'science',
    'LS&ĐL': 'history_geo', 'Lịch sử': 'history_geo', 'Địa lí': 'history_geo',
    'Toán': 'math',
    'Tiếng Việt': 'language', 'Ngữ văn': 'language',
    'Tin học': 'informatics',
    'Tiếng Anh': 'english',
}
FAMILY_ORDER = ['science', 'history_geo', 'math', 'language', 'informatics', 'english', 'primary_1_3', 'other']

DIGITS = re.compile(r'^\d{1,3}$')


def root():
    return os.environ.get('TC_ROOT', DEFAULT_ROOT)


def out_dir(r=None):
    d = os.path.join(r or root(), OUT_REL)
    os.makedirs(d, exist_ok=True)
    return d


def load_curriculum(r=None):
    p = os.path.join(r or root(), 'poc-out/graph/curriculum-structure.json')
    cs = json.load(open(p))
    return {d['sourceDocumentId']: d for d in cs['documents']}


def family_of(doc):
    """Family for a curriculum document (SGK); primary grades win."""
    if doc.get('grade') in (1, 2, 3):
        return 'primary_1_3'
    return FAMILY.get(doc.get('subject'), 'other')


def printed_to_pdf_offset(book, r=None):
    """Replica of tool/ui/pattern_router.printed_to_pdf_offset with an absolute
    root: the modal (pdf_page − printed footer number) over the OCR-body
    pages; None when no clear mode (fail closed, as the router does)."""
    diffs = Counter()
    for fp in glob.glob(os.path.join(r or root(), 'poc-out/graph/ocr-body', book, 'p*.json')):
        pdf = int(re.search(r'p(\d+)\.json', fp).group(1))
        try:
            lines = json.load(open(fp))['lines']
        except (OSError, ValueError, KeyError):
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
    return best if n >= 3 else None


def load_census_pages(r=None, books=None):
    """TC-v1 layout census rows (pdf page level). Optionally filtered by book."""
    p = os.path.join(r or root(), 'poc-out/trusted-corpus/tc-v1/census/pages.jsonl')
    rows = []
    with open(p) as fh:
        for line in fh:
            row = json.loads(line)
            if books is None or row['book'] in books:
                rows.append(row)
    return rows


def load_units(book, r=None):
    p = os.path.join(r or root(), 'poc-out/units-k12', book + '.json')
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def load_ocr_page(book, pdf_page, r=None):
    p = os.path.join(r or root(), 'poc-out/graph/ocr-body', book, f'p{pdf_page:03d}.json')
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def load_layout_page(book, pdf_page, r=None):
    """WAL-206 XY-cut page (only 14 books have one)."""
    p = os.path.join(r or root(), 'poc-out/layout', book, f'p{pdf_page:03d}.json')
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def load_pack_index(grade, r=None):
    p = os.path.join(r or root(), 'assets/pack', f'lesson-index-g{grade}.json')
    if not os.path.exists(p):
        return None
    return json.load(open(p))


# ---------------------------------------------------------------- lexical shape markers (HYPOTHESIS)
# These regexes stand in for semantic shapes the pipeline does not extract.
# They are counted, never trusted: a hit says "this unit points at that shape",
# not "that shape is extractable".
SHAPE_MARKERS = {
    'timeline_year': re.compile(r'(?:năm|thế kỉ|thế kỷ|TK)\s+(?:[IVX]+|\d{2,4})|\b(?:1\d{3}|20[0-2]\d)\b'),
    'source_text': re.compile(r'(?:^|\W)(?:Tư liệu|tư liệu|TƯ LIỆU|Nguồn:|\(Theo|Trích)\b'),
    'map_spatial': re.compile(r'(?:lược đồ|bản đồ|Lược đồ|Bản đồ|LƯỢC ĐỒ|BẢN ĐỒ)'),
    'figure_ref': re.compile(r'(?:hình|Hình|HÌNH)\s*\d'),
    'table_ref': re.compile(r'(?:bảng|Bảng|BẢNG)\s*\d|(?:cột A|cột B)'),
    'process_steps': re.compile(r'(?:Bước\s*\d|Tiến hành|Chuẩn bị:|các bước)'),
    'compare': re.compile(r'(?:so sánh|khác nhau|giống nhau|điểm giống|điểm khác)'),
    'cause_why': re.compile(r'(?:vì sao|Vì sao|tại sao|Tại sao|nguyên nhân|hậu quả|ý nghĩa)'),
    'definition': re.compile(r'(?:là gì|khái niệm|được gọi là|Ghi nhớ|GHI NHỚ)'),
    'math_ops': re.compile(r'\d\s*[=+×÷:−-]\s*\d|phân số|số thập phân|chia hết|tính giá trị|biểu thức'),
    'write': re.compile(r'(?:^|\W)(?:viết|Viết)\s+(?:đoạn|bài|câu|một)'),
    'read_aloud': re.compile(r'(?:^|\W)(?:đọc|Đọc)\s+(?:thầm|thành tiếng|bài|đoạn|văn bản|diễn cảm)'),
    'mcq_options': re.compile(r'(?:^|\s)A[\.\)]\s+\S.{2,}?\sB[\.\)]\s+\S', re.DOTALL),
    'blank': re.compile(r'(?:…|\.\.\.\.|_{3,})'),
    'oral': re.compile(r'(?:kể|Kể|trao đổi|Trao đổi|thảo luận|Thảo luận|nói|Nói)\s'),
}


def shape_hits(text):
    return {k for k, rx in SHAPE_MARKERS.items() if rx.search(text or '')}


def pct(n, d):
    return round(100.0 * n / d, 1) if d else None


def dump(obj, name, r=None):
    p = os.path.join(out_dir(r), name)
    with open(p, 'w') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    return p


def write_md(text, name, r=None):
    p = os.path.join(out_dir(r), name)
    with open(p, 'w') as fh:
        fh.write(text)
    return p
