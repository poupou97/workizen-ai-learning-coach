#!/usr/bin/env python3
"""TRACK B (WAL-210) — sinh FIXTURE bài học cho Lesson Workspace từ MỘT
Trusted Structured Lesson (TSL, `tc2-p1`) + trang PDF SGK.

    python3 tool/fixtures/make_lesson_fixture.py \
        [--tsl poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json] \
        [--out assets/fixtures/real] [--dpi 150] [--no-crops]

Đầu ra (GITIGNORE — chữ SGK nguyên văn + crop trang KHÔNG lên git, WAL-43):
    assets/fixtures/real/lesson-<book>-b<N>.json
    assets/fixtures/real/crops/<book>-p<NNN>-<figure|withheld>-<id>.png

RANH GIỚI (Founder 2026-09-05):
- TSL là NGUỒN DUY NHẤT của chữ. Script không sửa, không "vá" chữ OCR, không
  bịa caption; block bị giữ lại (WITHHELD) đi ra KHÔNG CÓ chữ.
- Crop trang là NỘI BỘ/NGHIÊN CỨU (Founder D4). `distribution` ghi thẳng
  vào provenance để không ai tưởng là tài sản phát hành.
- `trust` của mọi phần tử sinh từ TSL = `fixtureFromTrustedCorpus` (fixture,
  chưa qua cổng cho trẻ). Kịch bản SAM = `prototype` (viết tay, khoá đáp án
  KHÔNG phải SGV). Không phần tử nào mang `trustedCorpus` — app hôm nay chưa
  có TrustedLearningSource.

LUẬT SUY DỮ LIỆU NGỮ NGHĨA (tất định, kiểm lại được, ghi vào `derivation`):
- `tsl-enumerated-steps-v1` (ProcessStep[]): sau mỗi block `instruction`
  (Chuẩn bị…/Tiến hành…) lấy các block `body` cùng trang có
  `enumerator_restored=true`, theo `order`, cho tới block `question` hoặc
  `heading` (trừ heading «Tiến hành:»); block WITHHELD xen giữa thành bước
  «bị giữ lại». Tiêu đề = phần tử cuối `heading_path` của block instruction.
- `tsl-summary-parenthesis-v1` (Comparison): sau `stage_label` «Em đã học»,
  các block `body` có enumerator, khớp `^[·•]\\s*(.+?)\\s*\\((.+)\\)\\.?$`
  → thực thể = nhóm 1, chiều «Dùng để tách» = nhóm 2. Không khớp ⇒ không hàng.
- `toc-ocr-chapters-v1` (ChapterRef[]): MỤC LỤC in (OCR, `units-k12`) tách
  theo «CHƯƠNG <La Mã> - <tên>»; số bài = mọi «Bài N.» trong đoạn. Tên chương
  giữ NGUYÊN OCR (có thể mang lỗi OCR — đó là phát hiện, không sửa tay).
- Hình: figure của TSL có diện tích ≥ 3 % trang, hoặc ≥ 1 % và có caption
  liên kết. Chèn vào thứ tự đọc TRƯỚC block đầu tiên cùng trang có y > tâm y
  của hình (cùng vị trí thì theo x). Caption vẫn là block riêng.
"""
import argparse
import datetime as _dt
import json
import os
import re
import sys

ROOT = os.environ.get('TC_ROOT', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
GENERATOR = 'tool/fixtures/make_lesson_fixture.py@v1'
DISTRIBUTION = 'internal-research-only (Founder D4) — không phân phối, không commit'
TRUST_TSL = 'fixtureFromTrustedCorpus'
TRUST_PROTO = 'prototype'


def pdf_path(book):
    for p in (f'{ROOT}/poc-out/pdf/{book[:2]}/{book}.pdf', f'{ROOT}/poc-out/pdf/{book}.pdf'):
        if os.path.exists(p):
            return p
    return None


def role_of(b):
    r = b.get('role')
    return r.get('value') if isinstance(r, dict) else r


def role_conf(b):
    r = b.get('role')
    return r.get('confidence') if isinstance(r, dict) else None


def source_ref(book, b):
    prov = b.get('provenance') or {}
    return {
        'book': book,
        'pagePdf': b['page'],
        'pagePrinted': b.get('page_printed'),
        'bbox': b['bbox'],
        'blockId': b['id'],
        'extraction': prov.get('extraction'),
        'ocrConf': prov.get('ocr_conf'),
    }


# ------------------------------------------------------------------ chapters
def chapters_from_toc(book):
    """MỤC LỤC in (OCR) → [{label, title, lessonNos}]. Không có ⇒ []."""
    p = f'{ROOT}/poc-out/units-k12/{book}.json'
    if not os.path.exists(p):
        return []
    units = json.load(open(p)).get('units') or []
    toc = next((u.get('text') for u in units if 'MỤC LỤC' in (u.get('text') or '')), None)
    if not toc:
        return []
    start = toc.index('MỤC LỤC')
    end = toc.find('Giải thích một số thuật ngữ', start)
    seg = toc[start:end if end > 0 else None]
    parts = re.split(r'(?=CHƯƠNG\s+[IVX]+\s*[-–])', seg)
    out = []
    for part in parts:
        m = re.match(r'CHƯƠNG\s+([IVX]+)\s*[-–]\s*(.+?)\s+(?=Bài\s+\d+\.)', part, re.S)
        if not m:
            continue
        nos = [int(n) for n in re.findall(r'Bài\s+(\d+)\.', part)]
        if not nos:
            continue
        out.append({
            'label': f'Chương {m.group(1)}',
            'title': re.sub(r'\s+', ' ', m.group(2)).strip(),
            'lessonNos': nos,
            'trust': TRUST_TSL,
            'derivation': 'toc-ocr-chapters-v1',
        })
    return out


# ------------------------------------------------------------------ blocks
def heading_level(b):
    hp = b.get('heading_path') or []
    return max(1, min(3, len(hp)))


def to_block(book, b):
    role = role_of(b)
    base = {
        'id': b['id'],
        'sourceRef': source_ref(book, b),
        'trust': TRUST_TSL,
        'roleConfidence': role_conf(b),
    }
    text = b.get('text')
    if role == 'heading':
        return {**base, 'type': 'heading', 'text': text, 'level': heading_level(b)}
    if role in ('body',):
        return {**base, 'type': 'paragraph', 'text': text}
    if role == 'caption':
        return {**base, 'type': 'caption', 'text': text, 'refersFigure': bool(b.get('refers_figure'))}
    if role == 'question':
        return {**base, 'type': 'question', 'text': text}
    if role in ('objective', 'instruction', 'sidebar', 'stage_label'):
        kind = {'objective': 'objective', 'instruction': 'instruction', 'sidebar': 'sidebar', 'stage_label': 'stageLabel'}[role]
        return {**base, 'type': 'activity', 'kind': kind, 'text': text}
    if role == 'table':
        cells = b.get('cells')
        if isinstance(cells, list) and cells:
            return {**base, 'type': 'table', 'rows': cells, 'safe': False, 'headerRows': 0}
        return None
    # vai trò lạ ⇒ KHÔNG đoán: bỏ, và ghi log để người xem biết
    print(f'  ! bỏ block vai trò lạ {role!r}: {b["id"]}', file=sys.stderr)
    return None


def withheld_block(book, w, crop_rel):
    blk = {
        'id': w['id'],
        'type': 'withheld',
        'sourceRef': {
            'book': book,
            'pagePdf': w['page'],
            'pagePrinted': w.get('page_printed'),
            'bbox': w['bbox'],
            'blockId': w['id'],
            'extraction': (w.get('provenance') or {}).get('extraction'),
        },
        'trust': TRUST_TSL,
        'reason': ','.join(w.get('reasons') or ['unknown']),
    }
    if crop_rel:
        blk['crop'] = crop_rel
    return blk


def figure_kept(f):
    x, y, w, h = f['bbox']
    area = w * h
    return area >= 0.03 or (area >= 0.01 and f.get('caption'))


def image_block(book, f, crop_rel, aspect=None):
    return {
        'aspect': aspect,
        'id': f['id'],
        'type': 'image',
        'sourceRef': {'book': book, 'pagePdf': f['page'], 'pagePrinted': None, 'bbox': f['bbox'], 'blockId': f['id']},
        'trust': TRUST_TSL,
        'crop': crop_rel,
        'captionBlockId': f.get('caption'),
        'labels': f.get('labels') or 0,
    }


# ------------------------------------------------------------------ semantic
def derive_process(tsl):
    """`tsl-enumerated-steps-v1` — xem docstring."""
    blocks = sorted(tsl['blocks'], key=lambda b: (b['page'], b['order']))
    withheld = {(w['page'], w['order']): w for w in tsl.get('withheld') or []}
    out = []
    for i, ins in enumerate(blocks):
        if role_of(ins) != 'instruction':
            continue
        hp = ins.get('heading_path') or []
        title = hp[-1] if hp else 'Quy trình'
        steps = []
        page = ins['page']
        # đi theo `order` trên cùng trang, kể cả các order bị giữ lại
        order = ins['order'] + 1
        by_order = {b['order']: b for b in blocks if b['page'] == page}
        max_order = max(list(by_order) + [o for (p, o) in withheld if p == page])
        while order <= max_order:
            b = by_order.get(order)
            w = withheld.get((page, order))
            if b is not None:
                r = role_of(b)
                if r == 'question' or (r == 'heading' and not re.match(r'^Ti[eề]n h[àa]nh', b.get('text') or '')):
                    break
                if r == 'body' and b.get('enumerator_restored'):
                    steps.append({'order': len(steps) + 1, 'text': b['text'], 'sourceBlockId': b['id']})
            elif w is not None and w.get('role') in ('body', 'sidebar'):
                steps.append({'order': len(steps) + 1, 'withheldReason': ','.join(w.get('reasons') or ['unknown']), 'sourceBlockId': w['id']})
            order += 1
        if steps:
            out.append({
                'type': 'process',
                'id': f'process-{len(out) + 1}',
                'title': title,
                'trust': TRUST_TSL,
                'derivation': 'tsl-enumerated-steps-v1',
                'steps': steps,
            })
    return out


def derive_comparison(tsl):
    """`tsl-summary-parenthesis-v1` — xem docstring."""
    blocks = sorted(tsl['blocks'], key=lambda b: (b['page'], b['order']))
    rows = []
    for i, sl in enumerate(blocks):
        if role_of(sl) != 'stage_label' or not (sl.get('text') or '').strip().lower().startswith('em đã học'):
            continue
        for b in blocks[i + 1:]:
            if b['page'] != sl['page']:
                break
            r = role_of(b)
            if r in ('heading', 'stage_label', 'question'):
                break
            if r == 'body' and b.get('enumerator_restored'):
                m = re.match(r'^[·•]\s*(.+?)\s*\((.+)\)\.?$', b['text'].strip())
                if m:
                    rows.append((m.group(1).strip(), m.group(2).strip(), b['id']))
        break
    if not rows:
        return []
    return [{
        'type': 'comparison',
        'id': 'comparison-1',
        'title': 'Các cách tách chất — sách tóm tắt',
        'trust': TRUST_TSL,
        'derivation': 'tsl-summary-parenthesis-v1',
        'entities': [{'name': e, 'sourceBlockId': src} for e, _, src in rows],
        'dimensions': [{'name': 'Dùng để tách', 'values': [v for _, v, _ in rows]}],
    }]


# ------------------------------------------------------------------ tutor script (PROTOTYPE, chỉ Bài 17)
def tutor_script_bai17(tsl, by_id):
    """Kịch bản VIẾT TAY cho KHTN 6 Bài 17 — `prototype`. Câu hỏi là NGUYÊN
    VĂN block trong TSL (theo id); mọi thứ khác (lời SAM, mẫu chấp nhận,
    gợi ý, scaffold) là của người viết slice, KHÔNG phải SGV, KHÔNG phải
    Pedagogy Runtime. TSL khác ⇒ trả None (không bịa kịch bản)."""
    B = '06-sgk-khoa-hoc-tu-nhien-6:'
    need = {
        'principle': B + 'p061:tc2-p1:016',
        'q_salt': B + 'p063:tc2-p1:011',
        'q_funnel': B + 'p063:tc2-p1:022',
        'q_sand': B + 'p063:tc2-p1:012',
        'summary': B + 'p064:tc2-p1:003',
        'co_can': B + 'p063:tc2-p1:005',
    }
    if tsl.get('book') != '06-sgk-khoa-hoc-tu-nhien-6' or tsl.get('lesson') != 17:
        return None
    if any(k not in by_id for k in need.values()):
        print('  ! TSL thiếu block cho kịch bản Bài 17 — không sinh tutorScript', file=sys.stderr)
        return None
    q = lambda k: by_id[need[k]]['text']
    return {
        'samMode': 'prototypeScripted',
        'trust': TRUST_PROTO,
        'evidencePolicy': 'none',
        'steps': [
            {
                'type': 'explain', 'id': 'e1', 'mascot': 'sam-explain',
                'text': 'Bài này nói về cách tách một chất ra khỏi hỗn hợp. Sách nêu nguyên tắc: '
                        'các chất khác nhau về tính chất, nên mình dựa vào chỗ khác nhau đó để tách. '
                        'Con đọc đoạn sách bên dưới rồi mình thử nhé.',
                'sourceBlockId': need['principle'],
            },
            {
                'type': 'ask', 'id': 'q1',
                'prompt': q('q_salt'), 'promptBlockId': need['q_salt'],
                'options': ['Lọc', 'Cô cạn', 'Chiết', 'Lắng'],
                'acceptable': [r'^cô cạn$', r'cô cạn'],
                'hints': [
                    'Con nghĩ xem: muối ăn không bay hơi, còn nước thì bay hơi được. Cách nào dùng đúng điều đó?',
                    'Sách viết ở mục «2. Cô cạn»: «Phương pháp cô cạn dùng để tách chất tan rắn ra khỏi dung dịch… bằng cách làm cho dung môi bay hơi».',
                ],
                'feedbackMatched': 'Khớp với điều sách viết: làm nước biển bay hơi để thu muối là phương pháp cô cạn. '
                                   'Con đã tự nối được ví dụ với tên phương pháp.',
                'scaffold': 'Chưa khớp, không sao. Sách gọi cách làm muối này là «cô cạn» — mình cùng đọc lại '
                            'đoạn đó, rồi đi tiếp nhé.',
                'keySource': 'prototype — suy từ đoạn ' + need['co_can'] + ' (SGK trang 62); KHÔNG phải SGV',
            },
            {
                'type': 'ask', 'id': 'q2',
                'prompt': q('q_funnel'), 'promptBlockId': need['q_funnel'],
                'options': [],
                'acceptable': [
                    r'dầu.*(lẫn|trộn|chảy|xuống|kịp|theo)',
                    r'(lẫn|trộn).*dầu',
                    r'(kịp|đúng lúc).*(khóa|khoá|vặn)',
                    r'(tách|riêng).*(dầu|nước)',
                ],
                'hints': [
                    'Nhớ lại: trong phễu, nước ở dưới, dầu ở trên. Nếu mở khoá nhanh, điều gì có thể lọt xuống cốc cùng nước?',
                    'Sách dặn: «Khi phần dầu ăn chạm vào bề mặt khoá thì vặn khoá lại» — mở từ từ để kịp làm việc gì?',
                ],
                'feedbackMatched': 'SAM thấy câu trả lời của con có ý «để dầu không chảy lẫn xuống nước» — đúng với điều '
                                   'sách dặn khi làm thí nghiệm. (Đây là kịch bản thử nghiệm; thầy cô mới là người xác nhận.)',
                'scaffold': 'Ý trong sách là: mở từ từ để kịp vặn khoá lại đúng lúc dầu chạm khoá, nhờ vậy dầu không '
                            'chảy lẫn xuống cốc nước. Con ghi lại ý này rồi mình đi tiếp nhé.',
                'keySource': 'prototype — suy từ bước tiến hành ' + B + 'p063:tc2-p1:019 (SGK trang 62); KHÔNG phải SGV',
            },
            {
                'type': 'ask', 'id': 'q3',
                'prompt': q('q_sand'), 'promptBlockId': need['q_sand'],
                'options': [
                    'Hoà tan vào nước → lọc bỏ cát → cô cạn lấy muối',
                    'Chiết bằng phễu chiết',
                    'Để lắng rồi gạn lấy muối',
                ],
                'acceptable': [r'^hoà tan vào nước'],
                'hints': [
                    'Muối tan trong nước, cát thì không. Con dùng điều đó để tách hai thứ ra bằng hai bước nào?',
                    'Sách viết: lọc «tách chất rắn không tan ra khỏi chất lỏng», cô cạn «tách chất khó bay hơi ra khỏi chất dễ bay hơi». Ghép hai bước lại xem.',
                ],
                'feedbackMatched': 'Khớp với hai cách sách đã nêu: lọc bỏ cát (không tan), rồi cô cạn để lấy lại muối. '
                                   'Con đã ghép được hai phương pháp cho một bài toán mới.',
                'scaffold': 'Cách sách gợi: hoà tan mẫu vào nước (muối tan, cát không), lọc bỏ cát, rồi cô cạn để thu muối. '
                            'Mình đọc lại phần «Em đã học» rồi đi tiếp nhé.',
                'keySource': 'prototype — ghép từ ' + need['summary'] + ' và các dòng «Em đã học» (SGK trang 63); KHÔNG phải SGV',
            },
            {
                'type': 'next', 'id': 'n1',
                'label': 'Đọc lại phần «Em đã học» trong sách',
                'target': 'read',
                'anchorBlockId': need['summary'],
            },
        ],
    }


# ------------------------------------------------------------------ crops
def crop_png(pdf, page, bbox, out_path, dpi, pad=0.012):
    import fitz
    doc = fitz.open(pdf)
    pg = doc[page - 1]
    r = pg.rect
    x, y, w, h = bbox
    x0, y0 = max(0.0, x - pad), max(0.0, y - pad)
    x1, y1 = min(1.0, x + w + pad), min(1.0, y + h + pad)
    clip = fitz.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    pm = pg.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False, clip=clip)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pm.save(out_path)
    return pm.width, pm.height


# ------------------------------------------------------------------ main
def build(tsl_path, out_dir, dpi=150, crops=True):
    tsl = json.load(open(tsl_path))
    book, lesson = tsl['book'], tsl['lesson']
    stem = f'lesson-{book}-b{lesson}'
    crop_dir = os.path.join(out_dir, 'crops')
    pdf = pdf_path(book) if crops else None
    if crops and not pdf:
        print(f'  ! không thấy PDF cho {book} — sinh fixture KHÔNG crop', file=sys.stderr)

    cs = next((d for d in json.load(open(f'{ROOT}/poc-out/graph/curriculum-structure.json'))['documents']
               if d['sourceDocumentId'] == book), {})
    subject, grade = cs.get('subject', book), cs.get('grade', int(book[:2]))
    book_title = f'{subject} {grade}'

    blocks_in = sorted(tsl['blocks'], key=lambda b: (b['page'], b['order']))
    by_id = {b['id']: b for b in blocks_in}
    pages = sorted({b['page'] for b in blocks_in})
    printed = sorted({b['page_printed'] for b in blocks_in if b.get('page_printed') is not None})

    # 1. block chữ theo thứ tự đọc
    seq = []  # (page, y, x, order, block)
    for b in blocks_in:
        blk = to_block(book, b)
        if blk:
            seq.append((b['page'], b['bbox'][1], b['bbox'][0], b['order'], blk))
    # 2. withheld — theo (page, order)
    for w in tsl.get('withheld') or []:
        rel = None
        if pdf:
            rel = f'crops/{book}-p{w["page"]:03d}-withheld-{w["order"]:03d}.png'
            crop_png(pdf, w['page'], w['bbox'], os.path.join(out_dir, rel), dpi)
        seq.append((w['page'], w['bbox'][1], w['bbox'][0], w['order'], withheld_block(book, w, rel)))
    seq.sort(key=lambda t: (t[0], t[3]))
    # 3. hình — chèn trước block đầu tiên cùng trang có y > tâm y hình
    figs = [f for f in tsl.get('figures') or [] if figure_kept(f)]
    figs.sort(key=lambda f: (f['page'], f['bbox'][1] + f['bbox'][3] / 2, f['bbox'][0]))
    for f in figs:
        rel = f'crops/{book}-p{f["page"]:03d}-{f["id"].split(":")[-1]}.png'
        aspect = None
        if pdf:
            w, h = crop_png(pdf, f['page'], f['bbox'], os.path.join(out_dir, rel), dpi)
            aspect = round(w / h, 4)
        yc = f['bbox'][1] + f['bbox'][3] / 2
        idx = next((i for i, t in enumerate(seq) if t[0] == f['page'] and t[1] > yc), None)
        if idx is None:
            idx = next((i for i, t in enumerate(seq) if t[0] > f['page']), len(seq))
        seq.insert(idx, (f['page'], yc, f['bbox'][0], -1, image_block(book, f, rel, aspect)))
    blocks = [t[4] for t in seq]
    # 4. dòng nguồn cuối bài
    if printed:
        rng = f'trang {printed[0]}' if printed[0] == printed[-1] else f'trang {printed[0]}–{printed[-1]}'
    else:
        rng = 'chưa dò được trang in'
    blocks.append({
        'id': f'{book}:b{lesson}:sourceRef',
        'type': 'sourceRef',
        'sourceRef': {'book': book, 'pagePdf': pages[0], 'pagePrinted': printed[0] if printed else None,
                      'bbox': [0, 0, 1, 1], 'blockId': None},
        'trust': TRUST_TSL,
        'text': f'SGK {book_title} · {rng} · {tsl.get("pipeline")} / {(blocks_in[0].get("provenance") or {}).get("sdm_version")}',
    })

    chapters = chapters_from_toc(book)
    chapter = next((c for c in chapters if lesson in c['lessonNos']), None)
    semantic = derive_process(tsl) + derive_comparison(tsl)
    script = tutor_script_bai17(tsl, by_id)

    doc = {
        'schema': 'wal-lesson-fixture-v1',
        'book': book,
        'bookTitle': book_title,
        'subject': subject,
        'grade': grade,
        'lesson': lesson,
        'title': tsl['title'],
        'chapter': chapter,
        'chapters': chapters,
        'provenance': {
            'trust': TRUST_TSL,
            'book': book,
            'pagePdfStart': pages[0], 'pagePdfEnd': pages[-1],
            'pagePrintedStart': printed[0] if printed else None,
            'pagePrintedEnd': printed[-1] if printed else None,
            'generator': GENERATOR,
            'sourcePipeline': tsl.get('pipeline'),
            'sdmVersion': (blocks_in[0].get('provenance') or {}).get('sdm_version'),
            'boundaryConfidence': (tsl.get('boundary') or {}).get('confidence'),
            'tslPath': os.path.relpath(tsl_path, ROOT),
            'distribution': DISTRIBUTION,
            'generatedAt': _dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds'),
            'tslStats': tsl.get('stats'),
        },
        'evidencePolicy': 'none',
        'blocks': blocks,
        'semantic': semantic,
    }
    if script:
        doc['tutorScript'] = script
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, stem + '.json')
    json.dump(doc, open(out_path, 'w'), ensure_ascii=False, indent=1)
    kinds = {}
    for b in blocks:
        kinds[b['type']] = kinds.get(b['type'], 0) + 1
    print(f'{out_path}\n  blocks={len(blocks)} {kinds}\n  semantic={[(s["type"], s["title"]) for s in semantic]}'
          f'\n  chapters={len(chapters)} chapter={chapter and chapter["label"]}\n  tutorScript={"có" if script else "không"}')
    return out_path


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tsl', default=f'{ROOT}/poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json')
    ap.add_argument('--out', default=f'{ROOT}/assets/fixtures/real')
    ap.add_argument('--dpi', type=int, default=150)
    ap.add_argument('--no-crops', action='store_true')
    a = ap.parse_args()
    build(a.tsl, a.out, dpi=a.dpi, crops=not a.no_crops)
