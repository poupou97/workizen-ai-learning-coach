#!/usr/bin/env python3
"""K-12 layout-aware extraction (WAL-206) — recursive XY-cut over OCR line boxes.

Why: every SGK/SGV in the corpus is a scanned image (no PDF text layer), so
reading order must be recovered from geometry. Apple Vision OCR gives one
box per line (normalized x, y, w, h, conf). The failure that stopped WAL-204
was NOT plain two-column text only: pages mix full-width body with
side-by-side boxes, floating sidebars beside figures, speech bubbles and
captions. A global gutter cannot represent that; recursive XY-cut can.

Algorithm (deterministic, zero dependencies)
  1. page numbers: digit-only lines in the top/bottom margins → pageNumber.
  2. XY-cut: given a set of line boxes, find the widest empty horizontal
     band (y-gap ≥ TY·median line height) and the widest empty vertical band
     (x-gap ≥ TX, spanning the region). Split on the larger-normalized gap;
     y-splits order top→bottom, x-splits order left→right. Recurse until no
     gap. Leaves are REGIONS in reading order (DFS).
  3. blocks: within a region, lines top→bottom; a new block starts on a
     paragraph gap (> 1.5·median h), a numbered item, or a role change.
  4. roles: heading / caption / sidebar / footnote / question / body /
     pageNumber. Geometry adds: a narrow region (< 45% page width) that does
     not start at the body's left margin and sits beside a text-free area
     → sidebar candidate.
  5. trust: page confidence from cut margins (gaps well above threshold) and
     absence of overlapping boxes; `trusted=false` when any cut was marginal
     or > 5% of boxes overlap — downstream must fail closed on such pages.

Provenance per block: book, pagePdf, id, order, regionPath (cut history),
role, bbox, lines, ocrConf.

Output: poc-out/layout/<book>/pNNN.json
Usage: python3 tool/corpus/layout_extract.py <book>...   |   --page <book> <pdfPage>
"""
import glob
import json
import os
import re
import statistics
import sys
from collections import defaultdict

TY = 1.15          # y-gap threshold in median line heights
TX = 0.035         # x-gap threshold in page width
MARGINAL = 1.10    # a cut whose gap < MARGINAL × threshold lowers confidence (calibrated on the gold set: 1.25 flagged pages whose order scored 1.0)
MARGIN = 0.08
MIN_REGION_LINES = 1

DIGITS = re.compile(r'^\d{1,3}$')
CAPTION = re.compile(r'^(Hình|Bảng|Sơ đồ|Biểu đồ|Lược đồ|Tranh)\s*\d|^[a-e]\)\s+\S{1,30}$', re.IGNORECASE)
SIDEBAR_LABEL = re.compile(r'^(Em có biết|EM CÓ BIẾT|Lưu ý|LƯU Ý|Ghi nhớ|GHI NHỚ|Chú ý|CHÚ Ý|Mở rộng|MỞ RỘNG|Kết nối|KẾT NỐI|Theo dõi|THEO DÕI|Dự đoán|DỰ ĐOÁN|Suy luận|Hình dung|Đối chiếu|Liên hệ|Tưởng tượng)\b')
FOOTNOTE = re.compile(r'^\(?[\d\*®]{1,2}\)\s*\S')
NUMBERED = re.compile(r'^\s*(\d{1,2}|[a-eA-E])[\.\)]\s+\S')
LESSON_HDR = re.compile(r'^\s*(BÀI|Bài)\s+\d{1,2}[a-z]?\b')
STAGE_HDR = re.compile(r'^(KHỞI ĐỘNG|KHÁM PHÁ|LUYỆN TẬP|VẬN DỤNG|THỰC HÀNH|MỤC TIÊU|MUC TIÊU|TRƯỚC KHI ĐỌC|ĐỌC VĂN BẢN|SAU KHI ĐỌC|VĂN BẢN \d|Khởi động|Khám phá|Luyện tập|Vận dụng|Thực hành|Hoạt động \d)\b')
DIRECTIVE_ANY = re.compile(r'\b(xác định|tính|hãy|chứng minh|cho biết|nêu|giải thích|so sánh|quan sát|mô tả|trình bày|dự đoán|kể tên|liệt kê|nhận xét|phân loại|sắp xếp|điền|nối|tìm|vẽ|viết|đọc|chọn|thảo luận|em hãy)\b', re.IGNORECASE)
QUESTION_HINT = re.compile(r'\?\s*$|^(Em hãy|Hãy|Nêu|Cho biết|Giải thích|Vì sao|Tại sao|Quan sát|So sánh|Kể|Chọn|Tính|Viết|Đọc|Thảo luận|Trình bày|Mô tả|Xác định|Dự đoán|Kể tên|Liệt kê|Nhận xét|Phân loại|Sắp xếp|Điền|Nối|Tìm)\b', re.IGNORECASE)


def _upper_ratio(t):
    letters = [c for c in t if c.isalpha()]
    return (sum(1 for c in letters if c.isupper()) / len(letters)) if letters else 0.0


WIDE = 0.60        # a line this wide (share of page) is a separator: nothing sits beside it


def _gaps_y(boxes, med_h, body_x0=0.1):
    """Empty horizontal bands inside the boxes' y-extent: list of (gap, ycut).
    A WIDE line also forces a cut at its top and bottom edges (even when the
    gap is small) because nothing can sit beside it — this is what isolates
    a sidebar-beside-figure band from the full-width body below it."""
    ivs = sorted((b['y'], b['y'] + b['h']) for b in boxes)
    out, cur_end = [], ivs[0][1]
    for y0, y1 in ivs[1:]:
        if y0 - cur_end >= TY * med_h:
            out.append((y0 - cur_end, (y0 + cur_end) / 2))
        cur_end = max(cur_end, y1)
    # Separator rule: cut only at the BOUNDARY between a wide (full-width) line
    # and a genuine side element (narrow AND right-shifted, e.g. a sidebar box
    # beside a figure). Cutting at every wide line would shred paragraphs into
    # one-line regions (seen on KHTN 7 p.19 during gold validation).
    ys = sorted(boxes, key=lambda b: b['y'])
    def side(b):
        # a genuine side element is narrow AND not on the body's left margin
        # (a paragraph's short last line is narrow but left-aligned — not a side element)
        return b['w'] < 0.45 and b['x'] > body_x0 + 0.12
    for i, b in enumerate(ys):
        if b['w'] < WIDE:
            continue
        prev = ys[i - 1] if i > 0 else None
        nxt = ys[i + 1] if i + 1 < len(ys) else None
        if prev is not None and side(prev) and prev['y'] + prev['h'] <= b['y'] + 0.002 \
                and all(a['y'] + a['h'] <= b['y'] + 0.002 or a['y'] >= b['y'] - 0.002 for a in boxes):
            out.append((TY * med_h * MARGINAL, b['y'] - 0.001))
        if nxt is not None and side(nxt) and nxt['y'] >= b['y'] + b['h'] - 0.002 \
                and all(a['y'] >= b['y'] + b['h'] - 0.002 or a['y'] + a['h'] <= b['y'] + b['h'] + 0.002 for a in boxes):
            out.append((TY * med_h * MARGINAL, b['y'] + b['h'] + 0.001))
    return out


def _gaps_x(boxes):
    ivs = sorted((b['x'], b['x'] + b['w']) for b in boxes)
    out, cur_end = [], ivs[0][1]
    for x0, x1 in ivs[1:]:
        if x0 - cur_end >= TX:
            out.append((x0 - cur_end, (x0 + cur_end) / 2))
        cur_end = max(cur_end, x1)
    return out


BAND_ROWS = 3      # a side box must span ≥ this many text rows to be split off


def _rows(boxes, med_h):
    """Group boxes into text rows by y (a new row starts when a box begins below
    the current row's bottom minus a third of a line)."""
    rows, cur, cur_end = [], [], None
    for b in sorted(boxes, key=lambda b: b['y']):
        if cur and b['y'] > cur_end - 0.3 * med_h:
            rows.append(cur); cur, cur_end = [], None
        cur.append(b); cur_end = b['y'] + b['h'] if cur_end is None else max(cur_end, b['y'] + b['h'])
    if cur: rows.append(cur)
    return rows


def _side_band(boxes, med_h):
    """Partial-height side box (KHTN 6 p.21: a unit-conversion box beside body
    text, with full-width lines above and below): no whole-region x-gap exists,
    but ≥ BAND_ROWS consecutive rows each contain the SAME x-gap. Returns
    (top, left, right, bottom) box lists or None. Rows above/below stay intact."""
    rows = _rows(boxes, med_h)
    if len(rows) < BAND_ROWS:
        return None
    gaps = []   # per row: (lo, hi) of its widest x-gap, or None
    for r in rows:
        g = _gaps_x(r) if len(r) > 1 else []
        if g:
            best = max(g, key=lambda x: x[0])
            gaps.append((best[1] - best[0] / 2, best[1] + best[0] / 2))
        else:
            gaps.append(None)
    best_run = None
    i = 0
    while i < len(rows):
        if gaps[i] is None:
            i += 1; continue
        lo, hi = gaps[i]; j = i
        while j + 1 < len(rows) and gaps[j + 1] and max(lo, gaps[j + 1][0]) < min(hi, gaps[j + 1][1]) - TX:
            lo, hi = max(lo, gaps[j + 1][0]), min(hi, gaps[j + 1][1]); j += 1
        if j - i + 1 >= BAND_ROWS and (best_run is None or j - i > best_run[1] - best_run[0]):
            best_run = (i, j, (lo + hi) / 2)
        i = j + 1
    if not best_run:
        return None
    i, j, cut = best_run
    band = [b for r in rows[i:j + 1] for b in r]
    left = [b for b in band if b['x'] + b['w'] / 2 < cut]
    right = [b for b in band if b['x'] + b['w'] / 2 >= cut]
    if not left or not right:
        return None
    # Only a genuine ALIGNED BOX qualifies: right lines narrow with a common left edge, left lines
    # starting at the column edge, and a clear gutter. (Without this, KHTN 7 p.20 — the WAL-204 gold
    # page — lost its sidebar/caption roles: fidelity 1.0 → 0.0.)
    gap_lo = max(b['x'] + b['w'] for b in left); gap_hi = min(b['x'] for b in right)
    if gap_hi - gap_lo < 2 * TX:
        return None
    if max(b['w'] for b in right) > 0.30 or (max(b['x'] for b in right) - min(b['x'] for b in right)) > 0.03:
        return None
    lx = min(b['x'] for b in left)
    if any(b['x'] > lx + 0.05 for b in left):
        return None
    top = [b for r in rows[:i] for b in r]
    bot = [b for r in rows[j + 1:] for b in r]
    return top, left, right, bot


def xy_cut(boxes, med_h, path, marginal, body_x0=0.1):
    """Return list of (path, boxes) leaves in reading order."""
    if len(boxes) <= MIN_REGION_LINES:
        return [(path, boxes)]
    gy = _gaps_y(boxes, med_h, body_x0)
    gx = _gaps_x(boxes)
    best_y = max(gy, default=None, key=lambda g: g[0])
    best_x = max(gx, default=None, key=lambda g: g[0])
    ny = (best_y[0] / (TY * med_h)) if best_y else 0
    nx = (best_x[0] / TX) if best_x else 0
    if not best_y and not best_x:
        band = _side_band(boxes, med_h)
        if band:
            top, left, right, bot = band
            out = xy_cut(top, med_h, path + 'T', marginal, body_x0) if top else []
            out += xy_cut(left, med_h, path + 'ML', marginal, body_x0) + xy_cut(right, med_h, path + 'MR', marginal, body_x0)
            out += xy_cut(bot, med_h, path + 'B', marginal, body_x0) if bot else []
            return out
        return [(path, boxes)]
    if ny >= nx:
        if ny < MARGINAL: marginal.append(('y', round(ny, 2), path))
        cut = best_y[1]
        top = [b for b in boxes if b['y'] + b['h'] / 2 < cut]
        bot = [b for b in boxes if b['y'] + b['h'] / 2 >= cut]
        if not top or not bot:
            return [(path, boxes)]
        return xy_cut(top, med_h, path + 'T', marginal, body_x0) + xy_cut(bot, med_h, path + 'B', marginal, body_x0)
    else:
        if nx < MARGINAL: marginal.append(('x', round(nx, 2), path))
        cut = best_x[1]
        left = [b for b in boxes if b['x'] + b['w'] / 2 < cut]
        right = [b for b in boxes if b['x'] + b['w'] / 2 >= cut]
        if not left or not right:
            return [(path, boxes)]
        return xy_cut(left, med_h, path + 'L', marginal, body_x0) + xy_cut(right, med_h, path + 'R', marginal, body_x0)


def _overlap_share(boxes):
    n = 0
    bs = sorted(boxes, key=lambda b: b['y'])
    for i, a in enumerate(bs):
        for b in bs[i + 1:i + 6]:
            if b['y'] > a['y'] + a['h']: break
            ix = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x'])
            iy = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])
            if ix > 0 and iy > 0.5 * min(a['h'], b['h']) and ix > 0.3 * min(a['w'], b['w']):
                n += 1
    return n / max(1, len(boxes))


def role_of(t, line, med_h, region_w, region_x0, body_x0):
    if DIGITS.match(t):
        return 'pageNumber'
    if FOOTNOTE.match(t):
        return 'footnote'
    if CAPTION.match(t):
        return 'caption'
    if SIDEBAR_LABEL.match(t):
        return 'sidebar'
    if LESSON_HDR.match(t) or STAGE_HDR.match(t) or (line['h'] >= 1.5 * med_h and _upper_ratio(t) > 0.6) or (_upper_ratio(t) > 0.85 and 6 <= len(t) <= 60):
        return 'heading'
    if re.match(r'^[a-e]\)\s+\S', t) and len(t) <= 45 and not re.search(r'[\.\?:;,]\s*$', t) and _upper_ratio(t) < 0.85 and t[3:4].isupper():
        return 'heading'
    if (NUMBERED.match(t) and QUESTION_HINT.search(t)) or (QUESTION_HINT.search(t) and len(t) < 220):
        return 'question'
    return 'body'


def extract_page(book, path):
    j = json.load(open(path))
    pdf_page = int(re.search(r'p(\d+)\.json', path).group(1))
    lines = [dict(l) for l in j['lines'] if l.get('w', 0) > 0 and l.get('text', '').strip()]
    if not lines:
        return dict(pagePdf=pdf_page, book=book, layout=dict(regions=0, trusted=False, confidence=0.0, marginalCuts=[]), blocks=[])
    med_h = statistics.median(l['h'] for l in lines) or 0.01
    pagenums = [l for l in lines if DIGITS.match(l['text'].strip()) and (l['y'] < MARGIN or l['y'] > 1 - MARGIN)]
    body = [l for l in lines if l not in pagenums]
    marginal = []
    body_x0 = statistics.median([l['x'] for l in body]) if body else 0.1
    leaves = xy_cut(body, med_h, '', marginal, body_x0) if body else []
    overlap = _overlap_share(body) if body else 0.0
    blocks = []
    order = 0
    for rpath, rboxes in leaves:
        rboxes = sorted(rboxes, key=lambda b: (b['y'], b['x']))
        rx0 = min(b['x'] for b in rboxes); rx1 = max(b['x'] + b['w'] for b in rboxes)
        region_w = rx1 - rx0
        centered = abs((rx0 + rx1) / 2 - 0.5) < 0.08
        narrow_side = region_w < 0.45 and rx0 > body_x0 + 0.15 and not centered
        # Floating diagram labels (KHTN 6 p.35: "Hơi nước", "Nước lỏng", "a) Sự bay hơi" beside a
        # paragraph, 0.02 page-widths from the text — below the x-gap threshold, so no cut isolates
        # them): a very short, narrow line starting well to the right of the region's text edge is a
        # label, never body text.
        wide_x = [b['x'] for b in rboxes if b['w'] >= 0.2]
        dom_x0 = statistics.median(wide_x) if wide_x else None
        cur = None
        floating = []
        for l in rboxes:
            t = l['text'].strip()
            role = role_of(t, l, med_h, region_w, rx0, body_x0)
            if role == 'body' and narrow_side:
                role = 'sidebar'
            if role == 'body' and dom_x0 is not None and l['w'] < 0.12 and len(t.split()) <= 4 \
                    and l['x'] > dom_x0 + 0.25 and not re.search(r'[\.\?!:;,]\s*$', t):
                # keep the paragraph running: the label becomes its own caption block AFTER the region's text
                floating.append(dict(regionPath=rpath or 'ROOT', role='caption', texts=[t], x0=l['x'], y0=l['y'], x1=l['x'] + l['w'], y1=l['y'] + l['h'], confs=[l.get('conf', 1)], _lasty=l['y']))
                continue
            continuation = cur is not None and (l['y'] - cur['_lasty']) <= 1.5 * med_h and cur['role'] not in ('heading', 'caption', 'pageNumber') and (
                t[:1].islower() or (role == 'question' and cur['role'] == 'body' and NUMBERED.match(cur['texts'][0]) is not None and not NUMBERED.match(t)))
            new = (not continuation) and (cur is None or role != cur['role'] or role in ('heading', 'caption', 'pageNumber')
                   or NUMBERED.match(t) is not None or (l['y'] - cur['_lasty']) > 1.5 * med_h)
            if new:
                if cur: blocks.append(cur)
                cur = dict(regionPath=rpath or 'ROOT', role=role, texts=[t], x0=l['x'], y0=l['y'], x1=l['x'] + l['w'], y1=l['y'] + l['h'], confs=[l.get('conf', 1)], _lasty=l['y'])
            else:
                cur['texts'].append(t); cur['x0'] = min(cur['x0'], l['x']); cur['y0'] = min(cur['y0'], l['y'])
                cur['x1'] = max(cur['x1'], l['x'] + l['w']); cur['y1'] = max(cur['y1'], l['y'] + l['h']); cur['confs'].append(l.get('conf', 1)); cur['_lasty'] = l['y']
        if cur: blocks.append(cur)
        blocks.extend(floating)
    for l in sorted(pagenums, key=lambda b: b['y']):
        blocks.append(dict(regionPath='PAGENUM', role='pageNumber', texts=[l['text'].strip()], x0=l['x'], y0=l['y'], x1=l['x'] + l['w'], y1=l['y'] + l['h'], confs=[l.get('conf', 1)]))
    out_blocks = []
    for i, b in enumerate(blocks):
        full = ' '.join(b['texts'])
        # block-level role: a numbered item whose full text ends with '?' or carries a directive is a question
        if b['role'] == 'body' and (full.rstrip().endswith('?') or (NUMBERED.match(full) and (QUESTION_HINT.search(re.sub(r'^\s*(\d{1,2}|[a-eA-E])[\.\)]\s+', '', full)) or DIRECTIVE_ANY.search(full)))):
            b['role'] = 'question'
        out_blocks.append(dict(id=f'{book}:p{pdf_page:03d}:b{i:02d}', order=i, regionPath=b['regionPath'], role=b['role'],
                               text=' '.join(b['texts']), bbox=[round(b['x0'], 3), round(b['y0'], 3), round(b['x1'] - b['x0'], 3), round(b['y1'] - b['y0'], 3)],
                               lines=len(b['texts']), ocrConf=round(sum(b['confs']) / len(b['confs']), 3)))
    # table/figure-dominated page: many digit-only or very short blocks ⇒ no trustworthy prose
    digit_blocks = sum(1 for b in out_blocks if DIGITS.match(b['text'].strip()))
    short_blocks = sum(1 for b in out_blocks if len(b['text']) < 25)
    table_like = len(out_blocks) >= 12 and (digit_blocks / len(out_blocks) > 0.2 or short_blocks / len(out_blocks) > 0.6)
    conf = max(0.0, 1.0 - 0.15 * len(marginal) - 2.0 * overlap - (0.5 if table_like else 0))
    trusted = len(marginal) == 0 and overlap <= 0.05 and not table_like
    marg_paths = [m[2] for m in marginal]
    for b in out_blocks:
        rp = b['regionPath']
        b['trusted'] = (not table_like) and overlap <= 0.05 and not any(rp.startswith(mp) for mp in marg_paths)
    layout = dict(regions=len(leaves), trusted=trusted, tableLike=table_like, confidence=round(conf, 2), marginalCuts=[[m[0], m[1], m[2]] for m in marginal[:6]], overlapShare=round(overlap, 3))
    return dict(pagePdf=pdf_page, book=book, layout=layout, blocks=out_blocks)


def extract_book(book):
    files = sorted(glob.glob(f'poc-out/graph/ocr-body/{book}/p*.json'))
    os.makedirs(f'poc-out/layout/{book}', exist_ok=True)
    stats = defaultdict(int)
    for fp in files:
        try:
            page = extract_page(book, fp)
        except Exception:
            stats['errors'] += 1
            continue
        json.dump(page, open(f"poc-out/layout/{book}/p{page['pagePdf']:03d}.json", 'w'), ensure_ascii=False)
        stats['pages'] += 1
        stats['trusted' if page['layout']['trusted'] else 'untrusted'] += 1
        stats['regions'] += page['layout']['regions']
        for b in page['blocks']:
            stats[f"role_{b['role']}"] += 1
    return dict(stats)


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == '--page':
        page = extract_page(sys.argv[2], f'poc-out/graph/ocr-body/{sys.argv[2]}/p{int(sys.argv[3]):03d}.json')
        print(json.dumps(page['layout'], ensure_ascii=False))
        for b in page['blocks']:
            print(f"{b['order']:>2} {b['regionPath']:<8} {b['role']:<10} {b['text'][:100]}")
        sys.exit(0)
    for book in sys.argv[1:]:
        print(book, extract_book(book))
