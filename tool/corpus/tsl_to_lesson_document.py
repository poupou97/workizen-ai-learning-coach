#!/usr/bin/env python3
"""Round 3 · Lane A-DATA (A1) — THE BRIDGE: Trusted Structured Lesson (TSL, `tc2-p1`) →
LessonDocument JSON (the exact shape `lib/core/lesson_model/` parses).

    python3 tool/corpus/tsl_to_lesson_document.py \
        [--tsl poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json] \
        [--out assets/fixtures/real] [--dpi 150] [--no-crops] \
        [--audit-status notAudited|sampledNoGate] [--audit-ref docs/research/FALSE-TRUST-AUDIT-RESULT-2026-09-05.md]

`tool/fixtures/make_lesson_fixture.py` is a thin wrapper around `build()` — ONE path from TSL to
the document Track B's app loads, not two. Contract: docs/research/TSL-TO-LESSON-DOCUMENT-CONTRACT.md.

WHAT IS PRESERVED, block by block (100 % of TSL blocks, asserted by `check_document`):
  id · book · pdf page · printed page · bbox · role (verbatim, `sourceRole`) · role confidence + method ·
  relations (heading_path, refers_figure, caption_of, order, enumerator_restored) · provenance
  (extraction, ocr_conf, text_sim → agreementScore, pipeline) · trust status · withholding reasons.
Lesson level: book, lesson number, title, boundary (pages, attach methods, confidence, header),
pipeline version, sourceability, answer_keys_included, TSL sha256, stats.

TRUST MAPPING (fail-closed):
  TSL block TRUSTED  → `trustedStructuredLesson`   (NOT production trust: G1 + licence are separate gates;
                                                     the UI keeps a «chưa kiểm định» chip)
  TSL withheld/CONFLICT → `WithheldBlock`, trust `withheld`, NO text field (asserted)
  role the consumer model has no type for → `WithheldBlock`, reason `unknown_role:<role>`
  table without cells → `WithheldBlock`, reason `table_without_cells`
  chapters from the naive-OCR table of contents (outside the TC gate) → `fixtureFromTrustedCorpus`
  tutor script (hand-written, Bài 17 only) → `prototype`
  `licence` = `internalResearchOnly` ALWAYS (Founder D4) — licence is orthogonal to trust.

REFUSALS (raise `BridgeRefusal`, nothing written): docType ≠ SGK; answer_keys_included; a `blocks`
entry without text or with a non-TRUSTED status; a `withheld` entry that carries text; duplicate ids.

DETERMINISM: no timestamps; the same TSL bytes always give the same document bytes
(`document_hash` = sha256 of the canonical JSON) — the tests assert it.

The TSL is READ-ONLY. Nothing here "fixes" OCR text, invents captions, or renames a reason code.
Crops (figures + withheld regions) are INTERNAL / RESEARCH ONLY (D4): never committed, never distributed.

Semantic-data derivation rules (deterministic, recorded in `derivation`; unchanged from the
Track B generator so the device-walked slice keeps its shape):
- `tsl-enumerated-steps-v1` (ProcessStep[]): after each `instruction` block (Chuẩn bị…/Tiến hành…)
  take the same-page `body` blocks with `enumerator_restored=true`, by `order`, until a `question` or
  a `heading` (except «Tiến hành:»); a withheld region in between becomes a withheld step.
- `tsl-summary-parenthesis-v1` (Comparison): after `stage_label` «Em đã học», enumerated `body`
  blocks matching `^[·•]\\s*(.+?)\\s*\\((.+)\\)\\.?$` → entity = group 1, «Dùng để tách» = group 2.
- `toc-ocr-chapters-v1` (ChapterRef[]): printed TOC (naive OCR, `units-k12`) split on
  «CHƯƠNG <Roman> - <name>»; OCR errors kept verbatim (a finding, not fixed by hand).
- Figures: TSL figure with area ≥ 3 % of the page, or ≥ 1 % with a linked caption. Inserted in reading
  order before the first same-page block whose y > the figure's centre y; same row ⇒ left before right.
"""
import argparse
import hashlib
import json
import os
import re
import sys

ROOT = os.environ.get('TC_ROOT', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
GENERATOR = 'tool/corpus/tsl_to_lesson_document.py@v1'
SCHEMA = 'wal-lesson-fixture-v1'
TRUST_TSL = 'trustedStructuredLesson'
TRUST_WITHHELD = 'withheld'
TRUST_PROTO = 'prototype'
TRUST_OUTSIDE_GATE = 'fixtureFromTrustedCorpus'
LICENCE = 'internalResearchOnly'
DISTRIBUTION = 'internal-research-only (Founder D4) — không phân phối, không commit'
AUDIT_STATUSES = ('notAudited', 'sampledNoGate')

# TSL role → (LessonBlock type, ActivityKind). Roles absent here are NOT guessed: they are withheld
# with reason `unknown_role:<role>` (footnote, activity, option … today).
ROLE_MAP = {
    'heading': ('heading', None),
    'body': ('paragraph', None),
    'attribution': ('paragraph', None),   # round 4: same block type, `sourceRole` names it so the UI can say «Kể theo: …»
    'caption': ('caption', None),
    'question': ('question', None),
    'objective': ('activity', 'objective'),
    'instruction': ('activity', 'instruction'),
    'sidebar': ('activity', 'sidebar'),
    'stage_label': ('activity', 'stageLabel'),
    'table': ('table', None),
}


class BridgeRefusal(Exception):
    """The TSL violates a precondition the bridge will not paper over."""


# ------------------------------------------------------------------ small helpers
def role_of(b):
    r = b.get('role')
    return r.get('value') if isinstance(r, dict) else r


def role_conf(b):
    r = b.get('role')
    return r.get('confidence') if isinstance(r, dict) else None


def role_method(b):
    r = b.get('role')
    return r.get('method') if isinstance(r, dict) else None


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    with open(path, 'rb') as f:
        return sha256_bytes(f.read())


def document_hash(doc):
    """sha256 of the canonical JSON (sorted keys, compact) — the determinism oracle."""
    return sha256_bytes(json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))


def pdf_path(book):
    for p in (f'{ROOT}/poc-out/pdf/{book[:2]}/{book}.pdf', f'{ROOT}/poc-out/pdf/{book}.pdf'):
        if os.path.exists(p):
            return p
    return None


# ------------------------------------------------------------------ validation (refusals)
def validate_tsl(tsl):
    if tsl.get('docType') != 'SGK':
        raise BridgeRefusal(f'docType {tsl.get("docType")!r} ≠ SGK — teacher books never reach a learner document')
    if tsl.get('answer_keys_included'):
        raise BridgeRefusal('answer_keys_included is true — refused (SGV answer keys must not reach a learner)')
    for k in ('book', 'lesson', 'title', 'pipeline', 'blocks'):
        if k not in tsl:
            raise BridgeRefusal(f'TSL lacks {k!r}')
    ids = set()
    for b in tsl['blocks']:
        if not isinstance(b.get('text'), str) or not b['text'].strip():
            raise BridgeRefusal(f'block {b.get("id")} in `blocks` has no text — a trusted block must carry its text')
        st = (b.get('trust') or {}).get('status') if isinstance(b.get('trust'), dict) else b.get('status')
        if st not in (None, 'TRUSTED'):
            raise BridgeRefusal(f'block {b.get("id")} in `blocks` has status {st!r} — only TRUSTED blocks may be there')
        if role_of(b) is None:
            raise BridgeRefusal(f'block {b.get("id")} has no role')
        for k in ('id', 'page', 'order', 'bbox'):
            if k not in b:
                raise BridgeRefusal(f'block {b.get("id")} lacks {k!r}')
        if b['id'] in ids:
            raise BridgeRefusal(f'duplicate block id {b["id"]}')
        ids.add(b['id'])
    for w in tsl.get('withheld') or []:
        if w.get('text') not in (None, ''):
            raise BridgeRefusal(f'withheld region {w.get("id")} carries text — the TSL is not fail-closed')
        if not w.get('reasons'):
            raise BridgeRefusal(f'withheld region {w.get("id")} has no reason code')
        if w.get('id') in ids:
            raise BridgeRefusal(f'duplicate block id {w["id"]}')
        ids.add(w.get('id'))


# ------------------------------------------------------------------ per-element mapping
def source_ref(book, b, with_printed=True):
    prov = b.get('provenance') or {}
    ref = {
        'book': book,
        'pagePdf': b['page'],
        'pagePrinted': b.get('page_printed') if with_printed else None,
        'bbox': b['bbox'],
        'blockId': b['id'],
        'extraction': prov.get('extraction'),
        'ocrConf': prov.get('ocr_conf'),
        'pipeline': prov.get('pipeline'),
    }
    sim = prov.get('text_sim')
    ref['agreementScore'] = round(sim / 100.0, 4) if isinstance(sim, (int, float)) else None
    return ref


def relations_of(b, caption_of=None):
    rel = {
        'headingPath': list(b.get('heading_path') or []),
        'refersFigure': bool(b.get('refers_figure')),
        'order': b.get('order'),
        'enumeratorRestored': bool(b.get('enumerator_restored')),
    }
    if caption_of:
        rel['captionOf'] = caption_of
    return rel


def heading_level(b):
    hp = b.get('heading_path') or []
    return max(1, min(3, len(hp)))


def text_block(book, b, caption_of):
    """A TSL TRUSTED block → LessonBlock JSON, or a withheld block when the consumer model has no type
    for its role (never a guess)."""
    role = role_of(b)
    base = {
        'id': b['id'],
        'sourceRef': source_ref(book, b),
        'trust': TRUST_TSL,
        'roleConfidence': role_conf(b),
        'sourceRole': role,
        'roleMethod': role_method(b),
        'relations': relations_of(b, caption_of.get(b['id'])),
    }
    text = b['text']
    mapped = ROLE_MAP.get(role)
    if mapped is None:
        return withheld_block(book, b, [f'unknown_role:{role}'], status='WITHHELD', source_role=role)
    typ, kind = mapped
    if typ == 'heading':
        return {**base, 'type': 'heading', 'text': text, 'level': heading_level(b)}
    if typ == 'paragraph':
        return {**base, 'type': 'paragraph', 'text': text}
    if typ == 'caption':
        return {**base, 'type': 'caption', 'text': text, 'refersFigure': bool(b.get('refers_figure'))}
    if typ == 'question':
        return {**base, 'type': 'question', 'text': text}
    if typ == 'activity':
        return {**base, 'type': 'activity', 'kind': kind, 'text': text}
    if typ == 'table':
        cells = b.get('cells')
        if isinstance(cells, list) and cells and all(isinstance(r, list) for r in cells):
            return {**base, 'type': 'table', 'rows': cells, 'safe': False, 'headerRows': 0}
        return withheld_block(book, b, ['table_without_cells'], status='WITHHELD', source_role=role)
    raise AssertionError(role)  # ROLE_MAP and this chain must agree


def withheld_block(book, w, reasons, status, source_role=None, crop_rel=None):
    """WithheldBlock JSON — structurally WITHOUT a text field."""
    blk = {
        'id': w['id'],
        'type': 'withheld',
        'sourceRef': source_ref(book, w),
        'trust': TRUST_WITHHELD,
        'sourceRole': source_role if source_role is not None else (w.get('role') if isinstance(w.get('role'), str) else role_of(w)),
        'relations': {'order': w.get('order')},
        'reason': ','.join(reasons),
        'reasons': list(reasons),
        'status': status,
    }
    if isinstance(w.get('text_len'), int):
        blk['textLen'] = w['text_len']
    if crop_rel:
        blk['crop'] = crop_rel
    assert 'text' not in blk
    return blk


def figure_kept(f):
    x, y, w, h = f['bbox']
    area = w * h
    return area >= 0.03 or (area >= 0.01 and bool(f.get('caption')))


def image_block(book, f, crop_rel, aspect=None):
    return {
        'aspect': aspect,
        'id': f['id'],
        'type': 'image',
        'sourceRef': {'book': book, 'pagePdf': f['page'], 'pagePrinted': None, 'bbox': f['bbox'], 'blockId': f['id']},
        'trust': TRUST_TSL,
        'sourceRole': 'figure',
        'crop': crop_rel,
        'captionBlockId': f.get('caption'),
        'labels': f.get('labels') or 0,
    }


# ------------------------------------------------------------------ chapters (outside the TC gate)
# Round 4 (Lane C request 6): `toc-ocr-chapters-v1` knew only «CHƯƠNG <roman>», so every «Chủ đề» book
# (LS&ĐL 4/5, Khoa học 4/5, Đạo đức, HĐTN …) reported 0 chapters. The banner font also slips the tone —
# LS&ĐL 5's own TOC prints «CHỦ ĐẾ 6» — so the marker accepts the same tone variants as the lesson banner.
CHAPTER_HDR = re.compile(r'(?:CH(?:Ủ|U|Ú|Ũ|Ụ)\s*Đ(?:Ề|Ế|Ề|È|É|Ẻ|Ẽ|Ẹ|E)\s*(\d{1,2})|CHƯƠNG\s+([IVX]+|\d{1,2})|PHẦN\s+([IVX]+|\d{1,2}))\s*[.\-–:]?\s*')


def chapter_label(m):
    """A GENERATED label (never SGK text): the printed marker normalised, its number kept verbatim."""
    if m.group(1):
        return f'Chủ đề {m.group(1)}'
    if m.group(2):
        return f'Chương {m.group(2)}'
    return f'Phần {m.group(3)}'


def clean_toc_title(raw):
    """TOC titles carry dot leaders and a trailing page number; both are furniture, not title text."""
    t = re.sub(r'[.\u2026]{2,}', ' ', raw)
    # the leader may be a single dot glued to the page number («… THẾ GIỚI .93»)
    t = re.sub(r'[\s.\u2026]*\d{1,3}\s*$', '', t)
    return re.sub(r'\s+', ' ', t).strip(' .\u2026-–:')


def chapters_from_toc(book, units_path=None):
    """Printed TOC (naive OCR) → [{label, title, lessonNos}] with trust `fixtureFromTrustedCorpus`.
    None found ⇒ []. Never edits the OCR text."""
    p = units_path or f'{ROOT}/poc-out/units-k12/{book}.json'
    if not os.path.exists(p):
        # Silent [] used to be indistinguishable from «this book has no chapters». It is usually ROOT:
        # the bridge derives it from __file__, so running from a git worktree finds no poc-out at all.
        print(f'  ! không thấy TOC units cho {book} tại {p} — chapters=[] (đặt TC_ROOT nếu chạy ngoài checkout chính)', file=sys.stderr)
        return []
    units = json.load(open(p)).get('units') or []
    toc = next((u.get('text') for u in units if 'MỤC LỤC' in (u.get('text') or '')), None)
    if not toc:
        return []
    start = toc.index('MỤC LỤC')
    end = toc.find('Giải thích một số thuật ngữ', start)
    seg = toc[start:end if end > 0 else None]
    out = []
    for m in CHAPTER_HDR.finditer(seg):
        nxt = CHAPTER_HDR.search(seg, m.end())
        part = seg[m.end():nxt.start() if nxt else None]
        b = re.search(r'Bài\s+\d+\.', part)
        if not b:
            continue
        nos = [int(n) for n in re.findall(r'Bài\s+(\d+)\.', part)]
        if not nos:
            continue
        out.append({
            'label': chapter_label(m),
            'title': clean_toc_title(part[:b.start()]),
            'lessonNos': nos,
            'trust': TRUST_OUTSIDE_GATE,
            'derivation': 'toc-ocr-chapters-v2',
        })
    return out


# ------------------------------------------------------------------ semantic data (deterministic rules)
def derive_process(tsl):
    """`tsl-enumerated-steps-v1` — see module docstring."""
    blocks = sorted(tsl['blocks'], key=lambda b: (b['page'], b['order']))
    withheld = {(w['page'], w['order']): w for w in tsl.get('withheld') or []}
    out = []
    for ins in blocks:
        if role_of(ins) != 'instruction':
            continue
        hp = ins.get('heading_path') or []
        title = hp[-1] if hp else 'Quy trình'
        steps = []
        page = ins['page']
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
            elif w is not None and (w.get('role') if isinstance(w.get('role'), str) else role_of(w)) in ('body', 'sidebar'):
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
    """`tsl-summary-parenthesis-v1` — see module docstring."""
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


# ------------------------------------------------------------------ tutor script (PROTOTYPE, Bài 17 only)
def block_key(block_id):
    """`<book>:pNNN:<pipeline>:<order>` → `<book>:pNNN:<order>`.

    Round 4: a TSL block id embeds the PIPELINE NAME, so every id written down by hand (the Bài 17 tutor
    script below) stopped resolving the moment the lesson was rebuilt as `tc2-p2` — the script vanished
    with the message «TSL thiếu block», which blamed withholding for what was really a naming mismatch.
    Keys are compared without the pipeline segment; the id carried in the output is still the real one."""
    parts = (block_id or '').split(':')
    return ':'.join(parts[:2] + parts[3:]) if len(parts) >= 4 else block_id


def tutor_script_bai17(tsl, by_id):
    """Hand-written script for KHTN 6 Bài 17 — `prototype`. Prompts are VERBATIM TSL blocks (by id);
    everything else (SAM's words, acceptable patterns, hints, scaffold) is the slice author's, NOT the
    SGV, NOT the Pedagogy Runtime. Any other TSL ⇒ None (no invented script).

    Blocks are looked up pipeline-agnostically (see block_key), so a versioned re-run keeps the script
    when — and only when — every block it quotes is still TRUSTED."""
    B = '06-sgk-khoa-hoc-tu-nhien-6:'
    need = {
        'principle': B + 'p061:016',
        'q_salt': B + 'p063:011',
        'q_funnel': B + 'p063:022',
        'q_sand': B + 'p063:012',
        'summary': B + 'p064:003',
        'co_can': B + 'p063:005',
    }
    if tsl.get('book') != '06-sgk-khoa-hoc-tu-nhien-6' or tsl.get('lesson') != 17:
        return None
    by_key = {block_key(k): v for k, v in by_id.items()}
    missing = [k for k, v in need.items() if v not in by_key]
    if missing:
        print(f'  ! TSL thiếu block cho kịch bản Bài 17 ({", ".join(missing)}) — không sinh tutorScript', file=sys.stderr)
        return None
    need = {k: by_key[v]['id'] for k, v in need.items()}   # back to the REAL ids: they are emitted as provenance
    q = lambda k: by_id[need[k]]['text']  # noqa: E731
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
                    # ROUND 3 (A7 guard, Lane B hand-off): gợi ý chỉ chỗ trong sách, KHÔNG nêu tên phương pháp (dạng đáp án).
                    'Ở trang 62 sách có một mục nói về cách «tách chất tan rắn ra khỏi dung dịch… bằng cách làm cho dung môi bay hơi» — con tìm tên mục đó nhé.',
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


# ------------------------------------------------------------------ the pure conversion
def convert(tsl, *, tsl_rel_path=None, tsl_sha256=None, book_meta=None, chapters=None, crops=None,
            audit_status='notAudited', audit_ref=None, include_tutor_script=True):
    """TSL dict → LessonDocument dict. Pure: no I/O, no clock. `crops` maps a figure/withheld id to
    {'crop': relative path, 'aspect': w/h|None}; absent ⇒ no crop path (figures then carry crop=None and
    are DROPPED, because an ImageBlock without a crop cannot render — counted in `blockCounts`)."""
    validate_tsl(tsl)
    if audit_status not in AUDIT_STATUSES:
        raise BridgeRefusal(f'audit status {audit_status!r} is not one of {AUDIT_STATUSES}')
    crops = crops or {}
    book, lesson = tsl['book'], tsl['lesson']
    meta = book_meta or {}
    subject = meta.get('subject') or book
    grade = meta.get('grade') or int(book[:2])
    book_title = f'{subject} {grade}'

    blocks_in = sorted(tsl['blocks'], key=lambda b: (b['page'], b['order']))
    by_id = {b['id']: b for b in blocks_in}
    pages = sorted({b['page'] for b in blocks_in} | {w['page'] for w in tsl.get('withheld') or []})
    printed = sorted({b['page_printed'] for b in blocks_in if b.get('page_printed') is not None})
    caption_of = {f['caption']: f['id'] for f in tsl.get('figures') or [] if f.get('caption')}

    # 1. text blocks in reading order (unknown roles become withheld blocks — never dropped)
    seq = []  # (page, y, x, order, block)
    unknown_role = 0
    for b in blocks_in:
        blk = text_block(book, b, caption_of)
        if blk['type'] == 'withheld':
            unknown_role += 1
        seq.append((b['page'], b['bbox'][1], b['bbox'][0], b['order'], blk))
    # 2. withheld regions of the TSL — by (page, order), with their crop when rendered
    for w in tsl.get('withheld') or []:
        c = crops.get(w['id']) or {}
        seq.append((w['page'], w['bbox'][1], w['bbox'][0], w['order'],
                    withheld_block(book, w, list(w.get('reasons') or []), status=w.get('status') or 'WITHHELD', crop_rel=c.get('crop'))))
    seq.sort(key=lambda t: (t[0], t[3]))
    # 3. figures — inserted before the first same-page block whose y > the figure's centre y
    figs = [f for f in tsl.get('figures') or [] if figure_kept(f)]
    figs.sort(key=lambda f: (f['page'], round((f['bbox'][1] + f['bbox'][3] / 2) / 0.02), f['bbox'][0]))
    images_kept = images_without_crop = 0
    for f in figs:
        c = crops.get(f['id']) or {}
        if not c.get('crop'):
            images_without_crop += 1
            continue
        images_kept += 1
        yc = f['bbox'][1] + f['bbox'][3] / 2
        idx = next((i for i, t in enumerate(seq) if t[0] == f['page'] and t[1] > yc and t[3] != -1), None)
        if idx is None:
            idx = next((i for i, t in enumerate(seq) if t[0] > f['page']), len(seq))
        seq.insert(idx, (f['page'], yc, f['bbox'][0], -1, image_block(book, f, c['crop'], c.get('aspect'))))
    blocks = [t[4] for t in seq]
    # 4. provenance line at the end of the lesson (generated text, not SGK)
    if printed:
        rng = f'trang {printed[0]}' if printed[0] == printed[-1] else f'trang {printed[0]}–{printed[-1]}'
    else:
        rng = 'chưa dò được trang in'
    sdm_version = (blocks_in[0].get('provenance') or {}).get('sdm_version')
    blocks.append({
        'id': f'{book}:b{lesson}:sourceRef',
        'type': 'sourceRef',
        'sourceRef': {'book': book, 'pagePdf': pages[0], 'pagePrinted': printed[0] if printed else None,
                      'bbox': [0, 0, 1, 1], 'blockId': None, 'pipeline': tsl.get('pipeline')},
        'trust': TRUST_TSL,
        'sourceRole': 'provenance_line',
        'text': f'SGK {book_title} · {rng} · {tsl.get("pipeline")} / {sdm_version}',
    })

    chapters = chapters if chapters is not None else []
    chapter = next((c for c in chapters if lesson in c['lessonNos']), None)
    semantic = derive_process(tsl) + derive_comparison(tsl)
    script = tutor_script_bai17(tsl, by_id) if include_tutor_script else None

    boundary_in = tsl.get('boundary') or {}
    boundary = None
    if boundary_in:
        boundary = {
            'pageStart': boundary_in.get('page_start', pages[0]),
            'pageEnd': boundary_in.get('page_end', pages[-1]),
            'confidence': boundary_in.get('confidence'),
            'headerFound': bool(boundary_in.get('header_found')),
            'source': boundary_in.get('source'),
            'attachMethods': dict(boundary_in.get('attach_methods') or {}),
        }
    counts = {}
    for b in blocks:
        counts[b['trust']] = counts.get(b['trust'], 0) + 1
    doc = {
        'schema': SCHEMA,
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
            'sdmVersion': sdm_version,
            'pipelineVersion': f'{tsl.get("pipeline")}/{sdm_version}',
            'boundaryConfidence': boundary_in.get('confidence'),
            'boundary': boundary,
            'tslPath': tsl_rel_path,
            'sourceHash': tsl_sha256,
            'docType': tsl.get('docType'),
            'sourceability': tsl.get('sourceability'),
            'answerKeysIncluded': bool(tsl.get('answer_keys_included', False)),
            'auditStatus': audit_status,
            'auditRef': audit_ref,
            'distribution': DISTRIBUTION,
            'tslStats': tsl.get('stats'),
            'blockCounts': {
                'byTrust': counts,
                'tslTrusted': len(blocks_in),
                'tslWithheld': len(tsl.get('withheld') or []),
                'unknownRoleWithheld': unknown_role,
                'imagesKept': images_kept,
                'imagesWithoutCrop': images_without_crop,
                'figuresInTsl': len(tsl.get('figures') or []),
            },
        },
        'evidencePolicy': 'none',
        'licence': LICENCE,
        'blocks': blocks,
        'semantic': semantic,
    }
    if script:
        doc['tutorScript'] = script
    check_document(doc, tsl)
    return doc


def check_document(doc, tsl):
    """Post-conditions the bridge guarantees (also exercised by the tests)."""
    blocks = doc['blocks']
    tsl_ids = {b['id'] for b in tsl['blocks']} | {w['id'] for w in tsl.get('withheld') or []}
    doc_ids = [b['id'] for b in blocks]
    assert len(doc_ids) == len(set(doc_ids)), 'duplicate block ids in the document'
    missing = tsl_ids - set(doc_ids)
    assert not missing, f'TSL blocks lost in the bridge: {sorted(missing)[:5]}'
    for b in blocks:
        if b['type'] == 'withheld':
            assert 'text' not in b, f'withheld block {b["id"]} carries text'
            assert b['trust'] == TRUST_WITHHELD, f'withheld block {b["id"]} trust {b["trust"]}'
            assert b['reasons'], f'withheld block {b["id"]} without reasons'
        else:
            assert b['trust'] != TRUST_WITHHELD, f'text block {b["id"]} carries trust withheld'
        assert b['sourceRef']['book'] == doc['book']
        assert isinstance(b['sourceRef']['pagePdf'], int) and len(b['sourceRef']['bbox']) == 4
    n_withheld = sum(1 for b in blocks if b['type'] == 'withheld')
    assert n_withheld == len(tsl.get('withheld') or []) + doc['provenance']['blockCounts']['unknownRoleWithheld']
    assert doc['licence'] == LICENCE and doc['provenance']['trust'] == TRUST_TSL
    assert doc['provenance']['answerKeysIncluded'] is False
    # verbatim: every trusted text block reproduces the TSL text unchanged
    tsl_text = {b['id']: b['text'] for b in tsl['blocks']}
    for b in blocks:
        if b['id'] in tsl_text and b['type'] not in ('withheld', 'table'):
            assert b['text'] == tsl_text[b['id']], f'text altered for {b["id"]}'


# ------------------------------------------------------------------ crops (I/O, internal only)
def crop_pads(bbox, neighbours, pad=0.012, gap=0.003):
    """Round 4 (failure class 5, «crop bbox bleed»): per-side padding for one crop.

    The crop was padded by a fixed `pad` on all four sides. On a dense page that pulls the neighbouring
    paragraph's first line into a figure crop — the child then sees text that is not part of the figure and
    reads it as its caption. Here each side is padded by at most the free distance to the nearest neighbouring
    block on that side, minus `gap`, and never below 0: a crop can lose padding, never gain foreign content.

    `bbox` / `neighbours` are [x, y, w, h] in page fractions. A block counts on a side only when it also
    overlaps the figure on the perpendicular axis (a paragraph in the other column is not "below").
    Returns (left, top, right, bottom)."""
    x, y, w, h = bbox
    x1, y1 = x + w, y + h
    out = []
    for side in ('left', 'top', 'right', 'bottom'):
        free = None
        for nb in neighbours or []:
            nx, ny, nw, nh = nb
            nx1, ny1 = nx + nw, ny + nh
            x_ov = min(x1, nx1) - max(x, nx) > 0
            y_ov = min(y1, ny1) - max(y, ny) > 0
            d = None
            if side == 'left' and y_ov and nx1 <= x:
                d = x - nx1
            elif side == 'right' and y_ov and nx >= x1:
                d = nx - x1
            elif side == 'top' and x_ov and ny1 <= y:
                d = y - ny1
            elif side == 'bottom' and x_ov and ny >= y1:
                d = ny - y1
            if d is not None and (free is None or d < free):
                free = d
        out.append(pad if free is None else max(0.0, min(pad, free - gap)))
    return tuple(out)


def crop_png(pdf, page, bbox, out_path, dpi, pad=0.012, pads=None):
    import fitz
    doc = fitz.open(pdf)
    pg = doc[page - 1]
    r = pg.rect
    x, y, w, h = bbox
    pl, pt, pr, pb = pads if pads is not None else (pad, pad, pad, pad)
    x0, y0 = max(0.0, x - pl), max(0.0, y - pt)
    x1, y1 = min(1.0, x + w + pr), min(1.0, y + h + pb)
    clip = fitz.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    pm = pg.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False, clip=clip)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pm.save(out_path)
    return pm.width, pm.height


def render_crops(tsl, out_dir, dpi=150):
    """Figure + withheld-region crops → {id: {'crop': rel, 'aspect': w/h}}. No PDF ⇒ {} (the document is
    still produced, without images). INTERNAL / RESEARCH ONLY (D4)."""
    book = tsl['book']
    pdf = pdf_path(book)
    if not pdf:
        print(f'  ! không thấy PDF cho {book} — sinh tài liệu KHÔNG crop', file=sys.stderr)
        return {}
    out = {}
    # Round 4: neighbours per page — every TSL block and withheld region that carries a bbox. A crop's padding
    # stops short of them (crop_pads), so a crop cannot bleed into the next paragraph.
    nb_by_page = {}
    for b in list(tsl.get('blocks') or []) + list(tsl.get('withheld') or []):
        if b.get('bbox'):
            nb_by_page.setdefault(b['page'], []).append((b.get('id'), b['bbox']))

    for w in tsl.get('withheld') or []:
        rel = f'crops/{book}-p{w["page"]:03d}-withheld-{w["order"]:03d}.png'
        nbs = [bb for bid, bb in nb_by_page.get(w['page'], []) if bid != w.get('id')]
        crop_png(pdf, w['page'], w['bbox'], os.path.join(out_dir, rel), dpi, pads=crop_pads(w['bbox'], nbs))
        out[w['id']] = {'crop': rel, 'aspect': None}
    for f in tsl.get('figures') or []:
        if not figure_kept(f):
            continue
        rel = f'crops/{book}-p{f["page"]:03d}-{f["id"].split(":")[-1]}.png'
        # a figure's own caption belongs to the figure — it never clips its padding. (The TSL stores
        # `labels` as a COUNT, not a list, so figure labels cannot be excluded by id; they sit inside the
        # picture bbox anyway, which no side test can turn into a neighbour.)
        own = {f.get('caption'), f.get('id')}
        nbs = [bb for bid, bb in nb_by_page.get(f['page'], []) if bid not in own]
        wpx, hpx = crop_png(pdf, f['page'], f['bbox'], os.path.join(out_dir, rel), dpi, pads=crop_pads(f['bbox'], nbs))
        out[f['id']] = {'crop': rel, 'aspect': round(wpx / hpx, 4)}
    return out


def book_meta_for(book):
    p = f'{ROOT}/poc-out/graph/curriculum-structure.json'
    if not os.path.exists(p):
        return {}
    cs = next((d for d in json.load(open(p))['documents'] if d['sourceDocumentId'] == book), {})
    return {'subject': cs.get('subject'), 'grade': cs.get('grade')}


def build(tsl_path, out_dir, dpi=150, crops=True, audit_status='notAudited', audit_ref=None):
    """The ONE path: TSL file → `<out_dir>/lesson-<book>-b<N>.json` (+ crops/). Returns the output path."""
    tsl = json.load(open(tsl_path, encoding='utf-8'))
    validate_tsl(tsl)
    crop_map = render_crops(tsl, out_dir, dpi) if crops else {}
    doc = convert(tsl, tsl_rel_path=os.path.relpath(tsl_path, ROOT), tsl_sha256=sha256_file(tsl_path),
                  book_meta=book_meta_for(tsl['book']), chapters=chapters_from_toc(tsl['book']), crops=crop_map,
                  audit_status=audit_status, audit_ref=audit_ref)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'lesson-{tsl["book"]}-b{tsl["lesson"]}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    kinds = {}
    for b in doc['blocks']:
        kinds[b['type']] = kinds.get(b['type'], 0) + 1
    print(f'{out_path}\n  hash={document_hash(doc)}\n  blocks={len(doc["blocks"])} {kinds}\n  byTrust={doc["provenance"]["blockCounts"]["byTrust"]}'
          f'\n  semantic={[(s["type"], s["title"]) for s in doc["semantic"]]}\n  chapters={len(doc["chapters"])} chapter={doc["chapter"] and doc["chapter"]["label"]}'
          f'\n  tutorScript={"có" if doc.get("tutorScript") else "không"} · auditStatus={audit_status} · licence={LICENCE}')
    return out_path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tsl', default=f'{ROOT}/poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json')
    ap.add_argument('--out', default=f'{ROOT}/assets/fixtures/real')
    ap.add_argument('--dpi', type=int, default=150)
    ap.add_argument('--no-crops', action='store_true')
    ap.add_argument('--audit-status', default='notAudited', choices=AUDIT_STATUSES)
    ap.add_argument('--audit-ref', default=None)
    a = ap.parse_args(argv)
    try:
        build(a.tsl, a.out, dpi=a.dpi, crops=not a.no_crops, audit_status=a.audit_status, audit_ref=a.audit_ref)
    except BridgeRefusal as e:
        print(f'REFUSED: {e}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
