#!/usr/bin/env python3
"""TC-v1 — STRUCTURED DOCUMENT MODEL (SDM) + normalisers for every bake-off candidate.

Why: Markdown is a projection, not a source of truth. Every candidate's raw
output (poc-out/trusted-corpus/<ver>/bakeoff/raw/<cand>/<book>-pNNN.json) is
normalised into ONE page model so that text, block boundaries, reading
order, roles, provenance and trust can be scored with the same code.

SDM page  = {book, page, candidate, seconds, page_size, blocks:[SDM block]}
SDM block = {id, order, role, text, bbox [x, y, w, h] normalised to the page
             (None when the candidate gives no geometry), trusted (True /
             False / None = "no trust concept: implicitly trusted"),
             native_label, column (None if unknown), extraction, confidence}

Coarse roles (shared by gold and candidates):
  HEADING · BODY · QUESTION · OPTION · CAPTION · SIDEBAR · TABLE · FORMULA ·
  FIGURE_TEXT · FOOTNOTE · PAGENUM · UNKNOWN
Gold fine roles map onto these (GOLD_ROLE_MAP); candidate native labels map
onto these (per adapter). A candidate that has no concept of a role (e.g.
Docling has no QUESTION/SIDEBAR) simply never emits it — that is measured,
not excused.
"""
import glob
import json
import os
import re

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
HERE = os.path.dirname(os.path.abspath(__file__))

GOLD_ROLE_MAP = {
    'heading': 'HEADING', 'running_head': 'HEADING',
    'body': 'BODY', 'objective': 'BODY', 'activity': 'BODY', 'rule': 'BODY', 'answer': 'BODY', 'attribution': 'BODY', 'speech_bubble': 'BODY',
    'question': 'QUESTION', 'option': 'OPTION', 'answer_slot': 'OPTION',
    'caption': 'CAPTION', 'sidebar': 'SIDEBAR', 'table': 'TABLE', 'formula': 'FORMULA',
    'figure_label': 'FIGURE_TEXT', 'diagram': 'FIGURE_TEXT', 'footnote': 'FOOTNOTE', 'page_number': 'PAGENUM',
}
# gold blocks whose text a child would be taught from (used for TLSR / false-trust)
LEARNING_ROLES = {'body', 'objective', 'activity', 'rule', 'answer', 'attribution', 'speech_bubble', 'question', 'option', 'heading', 'sidebar', 'caption', 'footnote', 'formula'}
# gold roles that must NEVER be emitted as a learner question
NOT_A_QUESTION = {'heading', 'running_head', 'objective', 'answer', 'rule', 'activity', 'option', 'answer_slot', 'sidebar', 'caption', 'footnote', 'attribution', 'body', 'table', 'figure_label', 'diagram', 'page_number'}

ROLE_CAPABLE = {
    'current-naive': set(), 'current-xycut': {'HEADING', 'BODY', 'QUESTION', 'CAPTION', 'SIDEBAR', 'FOOTNOTE', 'PAGENUM'},
    'docling-ocrmac': {'HEADING', 'BODY', 'CAPTION', 'TABLE', 'FORMULA', 'FOOTNOTE', 'PAGENUM'}, 'docling-rapidocr': {'HEADING', 'BODY', 'CAPTION', 'TABLE', 'FORMULA', 'FOOTNOTE', 'PAGENUM'},
    'pymupdf4llm': {'HEADING', 'BODY'}, 'marker': {'HEADING', 'BODY', 'CAPTION', 'TABLE', 'FORMULA', 'FOOTNOTE', 'PAGENUM'},
    'mineru': {'HEADING', 'BODY', 'CAPTION', 'TABLE', 'FORMULA', 'PAGENUM'}, 'vlm-mlx': {'HEADING', 'BODY', 'QUESTION', 'CAPTION', 'SIDEBAR', 'TABLE', 'FIGURE_TEXT', 'FOOTNOTE', 'PAGENUM'},
}


def _strip_html(h):
    h = re.sub(r'<br\s*/?>', '\n', h or '')
    h = re.sub(r'</(p|li|tr|div|h\d)>', '\n', h)
    h = re.sub(r'<[^>]+>', '', h)
    h = h.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    return re.sub(r'[ \t]+', ' ', h).strip()


def _blk(i, role, text, bbox=None, trusted=None, label=None, column=None, extraction=None, confidence=None):
    return dict(id=f'c{i:03d}', order=i, role=role, text=(text or '').strip(), bbox=bbox, trusted=trusted, native_label=label, column=column, extraction=extraction, confidence=confidence)


# ------------------------------------------------------------------ adapters
def adapt_current_naive(res):
    lines = res['lines']
    out, i = [], 0
    # group consecutive lines into paragraphs on a vertical gap (same rule the generic extractor used: none) —
    # naive = one block per OCR line in file order (this IS the WAL-204 order); we also join runs of lines whose
    # y-gap < 1.6×h so the block texts are comparable with the other candidates.
    cur = None
    for l in lines:
        t = l.get('text', '').strip()
        if not t:
            continue
        if cur and (l['y'] - cur['_y']) < 1.6 * max(cur['_h'], 0.005):
            cur['text'] += ' ' + t; cur['_y'] = l['y']; cur['_h'] = l['h']
            cur['bbox'] = [min(cur['bbox'][0], l['x']), cur['bbox'][1], max(cur['bbox'][0] + cur['bbox'][2], l['x'] + l['w']) - min(cur['bbox'][0], l['x']), l['y'] + l['h'] - cur['bbox'][1]]
        else:
            if cur: out.append(cur)
            cur = _blk(i, 'UNKNOWN', t, [l['x'], l['y'], l['w'], l['h']], None, 'line', None, 'apple-vision-accurate-vi', l.get('conf')); cur['_y'] = l['y']; cur['_h'] = l['h']; i += 1
    if cur: out.append(cur)
    for b in out:
        b.pop('_y', None); b.pop('_h', None)
    return out, None


XY_ROLE = {'heading': 'HEADING', 'body': 'BODY', 'question': 'QUESTION', 'caption': 'CAPTION', 'sidebar': 'SIDEBAR', 'footnote': 'FOOTNOTE', 'pageNumber': 'PAGENUM'}


def adapt_current_xycut(res):
    out = []
    for i, b in enumerate(res['blocks']):
        out.append(_blk(i, XY_ROLE.get(b['role'], 'UNKNOWN'), b['text'], b['bbox'], b.get('trusted'), b['role'], b.get('regionPath'), 'layout-xycut-v1', b.get('ocrConf')))
    return out, dict(page_trusted=res['layout'].get('trusted'), confidence=res['layout'].get('confidence'))


DOCLING_ROLE = {'section_header': 'HEADING', 'title': 'HEADING', 'page_header': 'HEADING', 'page_footer': 'PAGENUM', 'text': 'BODY', 'paragraph': 'BODY', 'list_item': 'BODY',
                'caption': 'CAPTION', 'footnote': 'FOOTNOTE', 'table': 'TABLE', 'formula': 'FORMULA', 'code': 'BODY', 'checkbox_selected': 'BODY', 'checkbox_unselected': 'BODY', 'form': 'BODY', 'key_value_region': 'BODY'}


def adapt_docling(res):
    d = res['docling']
    pg = list(d['pages'].values())[0]; W, H = pg['size']['width'], pg['size']['height']
    out, i = [], 0

    def bbox_of(item):
        if not item.get('prov'):
            return None
        b = item['prov'][0]['bbox']
        # docling bbox: l, t, r, b with origin bottom-left when coord_origin == BOTTOMLEFT
        l, t, r, bt = b['l'], b['t'], b['r'], b['b']
        if b.get('coord_origin', 'BOTTOMLEFT') == 'BOTTOMLEFT':
            y0 = (H - t) / H; y1 = (H - bt) / H
        else:
            y0 = t / H; y1 = bt / H
        return [l / W, y0, (r - l) / W, y1 - y0]

    def rec(node):
        nonlocal i
        for ch in node.get('children', []):
            ref = ch['$ref']; kind, idx = ref.split('/')[1], int(ref.split('/')[2])
            item = d[kind][idx]
            if kind == 'texts':
                out.append(_blk(i, DOCLING_ROLE.get(item.get('label'), 'UNKNOWN'), item.get('text', ''), bbox_of(item), None, item.get('label'), None, 'docling+ocrmac')); i += 1
            elif kind == 'tables':
                cells = item.get('data', {}).get('table_cells', [])
                txt = ' | '.join(c.get('text', '') for c in cells)
                out.append(_blk(i, 'TABLE', txt, bbox_of(item), None, 'table', None, 'docling+ocrmac')); i += 1
            elif kind == 'pictures':
                out.append(_blk(i, 'FIGURE', '', bbox_of(item), None, 'picture', None, 'docling')); i += 1
            rec(item)
    rec(d['body'])
    return out, None


def adapt_pymupdf4llm(res):
    out, i = [], 0
    for c in res['chunks']:
        for para in re.split(r'\n\s*\n', c['text']):
            t = para.strip()
            if not t:
                continue
            role = 'HEADING' if t.startswith('#') else 'BODY'
            t = re.sub(r'^#+\s*', '', t)
            t = re.sub(r'<!--.*?-->', '', t).strip()
            if t:
                out.append(_blk(i, role, t, None, None, 'md', None, 'pymupdf4llm+rapidocr')); i += 1
    return out, None


MARKER_ROLE = {'SectionHeader': 'HEADING', 'PageHeader': 'HEADING', 'PageFooter': 'PAGENUM', 'Text': 'BODY', 'TextInlineMath': 'BODY', 'ListItem': 'BODY', 'ListGroup': 'BODY',
               'Caption': 'CAPTION', 'Footnote': 'FOOTNOTE', 'Table': 'TABLE', 'TableOfContents': 'TABLE', 'Equation': 'FORMULA', 'Code': 'BODY', 'Form': 'BODY', 'Handwriting': 'BODY', 'Figure': 'FIGURE', 'Picture': 'FIGURE'}
MARKER_CONTAINERS = {'FigureGroup', 'PictureGroup', 'TableGroup', 'ListGroup', 'Page', 'Document'}


def adapt_marker(res):
    m = res['marker']
    out, i = [], 0
    pg = m['children'][0]; W, H = pg['bbox'][2], pg['bbox'][3]

    def rec(b):
        nonlocal i
        bt = b.get('block_type')
        kids = b.get('children') or []
        if bt in MARKER_CONTAINERS and kids and bt != 'ListGroup':
            for c in kids:
                rec(c)
            return
        txt = _strip_html(b.get('html'))
        bb = b.get('bbox')
        bbox = [bb[0] / W, bb[1] / H, (bb[2] - bb[0]) / W, (bb[3] - bb[1]) / H] if bb else None
        role = MARKER_ROLE.get(bt, 'UNKNOWN')
        if role == 'FIGURE':
            out.append(_blk(i, 'FIGURE', '', bbox, None, bt, None, 'marker')); i += 1
            return
        if txt or role in ('TABLE',):
            out.append(_blk(i, role, txt, bbox, None, bt, None, 'marker+surya')); i += 1
        if bt == 'ListGroup':
            return
        for c in kids:
            rec(c)
    for c in pg.get('children') or []:
        rec(c)
    return out, None


def adapt_mineru(res):
    mid = res.get('middle')
    out, i = [], 0
    if not mid:
        return out, dict(error=res.get('stderr', '')[-300:])
    pg = mid['pdf_info'][0]; W, H = pg['page_size']
    blocks = pg.get('para_blocks') or pg.get('preproc_blocks') or []

    def text_of(b):
        parts = []
        for ln in b.get('lines', []):
            parts.append(''.join(sp.get('content', '') or sp.get('latex', '') or sp.get('html', '') or '' for sp in ln.get('spans', [])))
        return '\n'.join(p for p in parts if p)

    def emit(b, role, label):
        nonlocal i
        bb = b['bbox']
        out.append(_blk(i, role, text_of(b), [bb[0] / W, bb[1] / H, (bb[2] - bb[0]) / W, (bb[3] - bb[1]) / H], None, label, None, 'mineru-pipeline+paddleocr-latin')); i += 1

    for b in blocks:
        t = b.get('type')
        if t == 'title':
            emit(b, 'HEADING', t)
        elif t in ('text', 'list', 'index'):
            emit(b, 'BODY', t)
        elif t in ('interline_equation',):
            emit(b, 'FORMULA', t)
        elif t == 'table':
            for sb in b.get('blocks', []):
                st = sb.get('type')
                emit(sb, 'TABLE' if st == 'table_body' else 'CAPTION', st)
        elif t in ('image', 'chart'):
            for sb in b.get('blocks', []):
                st = sb.get('type')
                if st in ('image_body', 'chart_body'):
                    bb = sb['bbox']; out.append(_blk(i, 'FIGURE', '', [bb[0] / W, bb[1] / H, (bb[2] - bb[0]) / W, (bb[3] - bb[1]) / H], None, st, None, 'mineru')); i += 1
                else:
                    emit(sb, 'CAPTION', st)
        elif t == 'discarded':
            emit(b, 'PAGENUM' if re.fullmatch(r'\s*\d{1,3}\s*', text_of(b)) else 'UNKNOWN', t)
        else:
            emit(b, 'UNKNOWN', t)
    return out, None


VLM_ROLE = {'heading': 'HEADING', 'body': 'BODY', 'question': 'QUESTION', 'caption': 'CAPTION', 'sidebar': 'SIDEBAR', 'table': 'TABLE', 'figure_label': 'FIGURE_TEXT', 'footnote': 'FOOTNOTE', 'page_number': 'PAGENUM', 'objective': 'BODY'}


def adapt_vlm(res):
    text = res.get('text', '')
    out, i = [], 0
    lines = [l for l in text.split('\n') if l.strip()]
    structured = sum(1 for l in lines if re.match(r'^\s*(heading|body|question|caption|sidebar|table|figure_label|footnote|page_number|objective)\s*\|', l, re.I))
    if structured >= max(2, len(lines) // 2):
        for l in lines:
            m = re.match(r'^\s*(\w+)\s*\|\s*([\d.,\s]+)\|\s*(.*)$', l)
            if not m:
                out.append(_blk(i, 'UNKNOWN', l, None, None, 'vlm-line', None, res.get('model'))); i += 1; continue
            role = VLM_ROLE.get(m.group(1).lower(), 'UNKNOWN')
            nums = [float(v) for v in re.findall(r'[\d.]+', m.group(2))]
            bbox = nums[:4] if len(nums) >= 4 and all(v <= 1.0 for v in nums[:4]) else None
            out.append(_blk(i, role, m.group(3), bbox, None, m.group(1), None, res.get('model'))); i += 1
    else:
        # the model ignored the format: split on ' | ' and treat every piece as a role-less block
        for piece in re.split(r'\s*\|\s*', text):
            p = piece.strip()
            if p and not re.fullmatch(r'[\d.,\s]+', p):
                out.append(_blk(i, 'UNKNOWN', p, None, None, 'vlm-piece', None, res.get('model'))); i += 1
    return out, dict(format_followed=structured >= max(2, len(lines) // 2))


ADAPTERS = {'current-naive': adapt_current_naive, 'current-xycut': adapt_current_xycut, 'docling-ocrmac': adapt_docling, 'docling-rapidocr': adapt_docling,
            'pymupdf4llm': adapt_pymupdf4llm, 'marker': adapt_marker, 'mineru': adapt_mineru, 'vlm-mlx': adapt_vlm}


def load_sdm(candidate, book, page, ver='tc-v1'):
    p = f'{ROOT}/poc-out/trusted-corpus/{ver}/bakeoff/raw/{candidate}/{book}-p{page:03d}.json'
    if not os.path.exists(p):
        return None
    raw = json.load(open(p))
    if raw.get('error') or raw.get('result') is None:
        return dict(book=book, page=page, candidate=candidate, seconds=raw.get('seconds'), error=(raw.get('error') or 'no result')[-300:], blocks=[])
    try:
        blocks, meta = ADAPTERS[candidate](raw['result'])
    except Exception as e:
        import traceback
        return dict(book=book, page=page, candidate=candidate, seconds=raw.get('seconds'), error='adapter: ' + traceback.format_exc()[-400:], blocks=[])
    return dict(book=book, page=page, candidate=candidate, seconds=raw.get('seconds'), meta=meta, blocks=blocks)


def load_gold(book, page):
    p = f'{HERE}/tc_gold/{book}-p{page:03d}.json'
    return json.load(open(p)) if os.path.exists(p) else None


def all_gold():
    return [json.load(open(f)) for f in sorted(glob.glob(f'{HERE}/tc_gold/*.json'))]


if __name__ == '__main__':
    import sys
    cand, book, page = sys.argv[1], sys.argv[2], int(sys.argv[3])
    s = load_sdm(cand, book, page)
    print(json.dumps({k: v for k, v in s.items() if k != 'blocks'}, ensure_ascii=False))
    for b in s['blocks']:
        bb = str([round(v, 2) for v in b['bbox']]) if b['bbox'] else '-'
        print(f"{b['order']:>3} {b['role']:<11} {str(b['trusted']):<5} {bb:<28} {b['text'][:90]!r}")
