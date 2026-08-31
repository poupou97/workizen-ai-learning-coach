"""Trích cấu trúc SGK — TẤT ĐỊNH, 0 LLM. Bản v2: tự phát hiện bố cục.

Vì sao có v2: `parse_toc.py` (v1) đóng cứng x của cột theo Toán 5. Toán 9 xếp mục lục
HAI CỘT (x≈0.12 và x≈0.54) ⇒ v1 sẽ trộn hai cột vào nhau và cho thứ tự bài SAI **mà
không báo lỗi**. Đó là loại hỏng tệ nhất: kết quả trông vẫn hợp lý.

v2 tự tìm cột bằng phân cụm toạ độ x, và tự nhận cả hai từ phân cấp:
  Toán 5 → "Chủ đề" (số Ả Rập)      Toán 9 → "Chương" (số La Mã)
"""
import json, re, unicodedata

def _n(s): return unicodedata.normalize('NFC', s).strip()

def detect_columns(lines, gap=0.25):
    """Cụm x của các dòng chữ ⇒ số cột. Không đoán trước."""
    xs = sorted({round(l['x'], 2) for l in lines if len(l['text'].strip()) > 3})
    if not xs: return []
    cols, cur = [], [xs[0]]
    for a, b in zip(xs, xs[1:]):
        (cols.append(cur), cur := [b]) if b - a > gap else cur.append(b)
    cols.append(cur)
    return [min(c) for c in cols]

_FURNITURE = {'MỤC LỤC', 'TRANG', 'MUC LUC'}

LESSON = re.compile(r'B[àa]i\s*(\d+)\s*[.．]\s*(.+)')
CHAPTER = re.compile(r'(?:Chương|Chủ đề)\s+([IVXLC]+|\d+)?\s*[.．]?\s*(.*)', re.I)

def parse_toc(path):
    lines = json.load(open(path))['lines']
    cols = detect_columns(lines)
    # cột số trang = cụm nằm xa nhất bên phải; nội dung là phần còn lại
    pagecols = {c for c in cols if c > 0.80}
    def page_near(y, xmin):
        c = [l for l in lines if abs(l['y'] - y) < 0.013
             and l['text'].strip().isdigit()
             and l['x'] > xmin and any(abs(l['x'] - p) < 0.12 for p in pagecols or {0.85})]
        return int(c[0]['text']) if c else None

    body_cols = [c for c in cols if c not in pagecols]
    out = []
    # ⭐ đọc TỪNG CỘT một, trên→dưới. Đọc theo y toàn trang sẽ đan xen hai cột.
    for ci, cx in enumerate(body_cols):
        nxt = body_cols[ci + 1] if ci + 1 < len(body_cols) else 1.1
        colls = sorted([l for l in lines if cx - 0.03 <= l['x'] < nxt - 0.03],
                       key=lambda l: l['y'])
        cur = None
        for l in colls:
            t = _n(l['text'])
            m = LESSON.match(t)
            if m:
                if cur is None:
                    cur = {'number': None, 'title': None, 'column': ci, 'lessons': []}
                    out.append(cur)
                cur['lessons'].append({'number': int(m.group(1)),
                                       'title': m.group(2).strip(),
                                       'page_start': page_near(l['y'], cx)})
                continue
            c = CHAPTER.match(t)
            named = c and ('Chương' in t or 'Chủ đề' in t)
            # Toán 5 không viết chữ "Chủ đề" trong mục lục — chỉ có số ở cột trái
            # hẹp và TÊN VIẾT HOA ở cột nội dung. Nhận cả hai kiểu.
            bare_caps = (not named and len(t) > 4 and t == t.upper()
                         and not t[0].isdigit()
                         and t not in _FURNITURE)
            # ⭐ Tiêu đề chương TRÀN xuống dòng: dòng VIẾT HOA ngay dưới một chương
            # vừa mở, chưa có bài nào, và bản thân không có số trang. Toán 9:
            # "Chương I. PHƯƠNG TRÌNH VÀ HỆ HAI PHƯƠNG" / "TRÌNH BẬC NHẤT HAI ẨN".
            if bare_caps and out and out[-1]['column'] == ci \
                    and not out[-1]['lessons'] \
                    and page_near(l['y'], cx) is None:
                out[-1]['title'] = _n(f"{out[-1]['title']} {t}")
                continue
            if named or bare_caps:
                num = c.group(1) if named else None
                if num is None:      # tìm số chủ đề ở bên TRÁI cùng hàng
                    left = [x for x in lines
                            if x['x'] < cx - 0.02 and abs(x['y'] - l['y']) < 0.015
                            and x['text'].strip().isdigit()
                            and len(x['text'].strip()) <= 2]
                    if left: num = left[0]['text'].strip()
                cur = {'number': num,
                       'title': _n(c.group(2)) if named and c.group(2) else t,
                       'column': ci, 'lessons': [],
                       'page_start': page_near(l['y'], cx)}
                out.append(cur)
    return {'columns': len(body_cols), 'chapters': out}

TERM_DEF = None
def parse_glossary(path, term_x=None, def_x=None, tol=0.09):
    """Bảng THUẬT NGỮ → GIẢI THÍCH (Toán 9 tr.119). Ghép theo hàng, nối dòng tràn."""
    lines = json.load(open(path))['lines']
    cols = detect_columns(lines, gap=0.15)
    if term_x is None: term_x = cols[0] if cols else 0.07
    if def_x is None:
        cand = [c for c in cols if c > term_x + 0.12]
        def_x = cand[0] if cand else 0.37
    terms = [l for l in lines if abs(l['x'] - term_x) < tol]
    defs = [l for l in lines if abs(l['x'] - def_x) < tol]
    ts = sorted(terms, key=lambda l: l['y'])
    ds = sorted(defs, key=lambda l: l['y'])
    out = []
    for i, t in enumerate(ts):
        y0 = t['y']
        y1 = ts[i + 1]['y'] if i + 1 < len(ts) else 1.0
        body = [d['text'] for d in ds if y0 - 0.008 <= d['y'] < y1 - 0.004]
        # ⭐ Tiếng Việt viết hoa đầu thuật ngữ. Dòng bắt đầu bằng chữ THƯỜNG
        # ("một ẩn") là phần TIẾP của tên mục trước, không phải khái niệm mới.
        # Kiểm "có định nghĩa riêng không" KHÔNG đủ: dòng tràn của định nghĩa
        # nằm cùng hàng nên vẫn trông như có.
        first = _n(t['text'])[:1]
        is_cont = first and first.islower()
        if is_cont and out:
            # ⭐ Tên thuật ngữ TRÀN xuống dòng ("Bất phương trình bậc nhất" /
            # "một ẩn"). Không có định nghĩa riêng ở cùng hàng ⇒ là phần TIẾP của
            # mục trước, không phải mục mới. Bỏ qua kiểm này thì bảng vỡ thành
            # những "khái niệm" vô nghĩa như "một ẩn".
            out[-1]['term'] = _n(out[-1]['term'] + ' ' + t['text'])
            if body:
                out[-1]['definition'] = _n(out[-1]['definition'] + ' ' + ' '.join(body))
            continue
        if body:
            out.append({'term': _n(t['text']), 'definition': _n(' '.join(body))})
    return out
