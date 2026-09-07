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

ROUND 6 (workstream C) — a VALIDATED REPAIR now crosses this bridge, and does NOT become trusted:
  TSL region with `repair` (disposition `VALIDATED_REPAIR`, written by `repair/tsl_projection.py`) →
  the region stays a `WithheldBlock` with NO text, and gains a `repair` object carrying the trace
  (failure class · method · repair version · validator + version · verdict · supporting layers ·
  whether the value changed · caps). **`repairs[]` — which holds the PROPOSED VALUE — is corpus-side
  and is NEVER copied into the document**; `check_document` asserts no proposed value appears anywhere
  in the emitted JSON. So a validated repair becomes *visible and countable* to the app while remaining
  unreadable by a child. Making one servable is a separate, Founder-gated act; this bridge has no input
  for it and refuses a repair record that claims `TRUSTED`.

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


#: Roles the bridge KNOWS and deliberately has no carrier for. Round 6 (workstream C), obstacle 1:
#: `ROLE_MAP` had no `formula` key, so a formula region fell through to `unknown_role:formula` — a reason
#: code that says «the machine does not know what this is» about a block whose role the machine assigned
#: with confidence 0.95. Round 5 named that exact sin on the other side of the pipeline (`empty_block` on a
#: block reading `7 8 2 8 7 - 2 8 5 8` «misstates what was lost»), so it is not repeated here.
#:
#: `no_carrier:formula` is BEHAVIOUR-NEUTRAL for the app today: `withheld_card.dart` matches
#: `reason.contains('formula')` before it matches `unknown_role`, so the child-facing words are the same
#: ones the formula branch already produced. The set starts and ends at `formula` on purpose — extending
#: it to `footnote` / `activity` / `option` would change what a child reads («máy chưa rõ đoạn này là
#: gì» → the default), and `lib/features/**` is workstream D's. That is a coordination item, not a
#: unilateral one.
#:
#: What a carrier would be is NOT decided here. A servable structured block kind needs BOTH app-side
#: rendering (D) AND a Founder trust decision, and a flattened expression served as a paragraph is the
#: harm round 5 measured — so the honest position today is: withheld region + page crop + the structure
#: countable through its repair record.
KNOWN_UNCARRIED_ROLES = {'formula': 'no_carrier:formula'}

#: ⭐ ROUND 7 (workstream S) — STRUCTURAL GROUPS ON THE LESSON PATH, **BUILT AND NOT SWITCHED ON**.
#:
#: Round 5 defect 8: *withholding one option of a multiple-choice question leaves the SERVED question
#: wrong, not merely smaller.* The Founder's ruling was that for a block with structural siblings the
#: GROUP is the unit of disposition — serve all of it or none of it. `repair/groups.py` implemented
#: that on the GOLD-PAGE path in round 5 (7 mutilated structures → 0). **It was never implemented on
#: the lesson path**, which is the path a child actually reads, and rounds 5 and 6 both recorded the
#: class as still open there.
#:
#: Measured here, over the 238 canonical TSLs (`tool/corpus/structured_gap_census.py`):
#:   **31 mutilated structures are served today** — 29 `procedure_steps` (a LOWER BOUND) and
#:   **2 of 2** `question_options`, i.e. every multiple-choice group in the corpus is mutilated.
#: Enforcing the rule takes that to **0**, and costs **72 blocks** (11 833 → 11 761 served).
#:
#: Both switches default to **False**, and with both off the emitted document is BYTE-IDENTICAL to
#: round 6's — asserted by `test_group_machinery_is_off_by_default`. Withholding 72 blocks a child
#: reads today is a product decision of the same shape as round 6's lost timeline: it is the Founder's,
#: not a lane's. `--group-rule` is the switch; this module will not throw it.
GROUP_REASON = 'structural_group'
GROUP_SENTINEL_TEXT = '\x01withheld\x01'   # never rendered, never emitted; see `structural_groups_of`


def structural_groups_of(tsl):
    """Structural groups for one TSL, from `repair/groups.py` — ONE definition of «a group» for the
    gold path and the lesson path both. Imported lazily so the bridge keeps working in a tree where
    the repair framework is absent.

    A withheld TSL region carries `text: null`, and `groups.structural_groups` drops empty-text blocks;
    without a placeholder every withheld sibling would be invisible to group formation, which is exactly
    why defect 8 could not be seen here. The sentinel restores MEMBERSHIP without inventing text — it is
    not a rendering, it never reaches a document, and `groups.ENUM_STEP` deliberately does not match it.
    Consequence, stated once and carried into every number: `question_options` and `table_rows` are
    decided by ROLE and are complete; `procedure_steps` is decided by an enumerator IN THE TEXT, which a
    withheld region does not have, so a procedure whose missing step is withheld is NOT detected. Every
    `procedure_steps` count is a lower bound, never an over-count."""
    from repair import groups as _groups   # noqa: PLC0415 — optional dependency, see docstring

    by_page, figs = {}, {}
    for b in tsl.get('blocks') or ():
        by_page.setdefault(b['page'], []).append(dict(
            id=b['id'], order=b.get('order') or 0, text=b.get('text') or '',
            role={'value': role_of(b)}))
    for w in tsl.get('withheld') or ():
        by_page.setdefault(w['page'], []).append(dict(
            id=w['id'], order=w.get('order') or 0, text=GROUP_SENTINEL_TEXT,
            role={'value': role_of(w)}))
    for f in tsl.get('figures') or ():
        figs.setdefault(f.get('page'), []).append(f)
    out = []
    for page, blocks in sorted(by_page.items()):
        out.extend(_groups.structural_groups(dict(
            book=tsl['book'], page=page, blocks=blocks, figures=figs.get(page) or [])))
    return out

#: A region-level repair projection may carry NONE of these. They are the ways a proposed value could
#: ride into the document on a block a renderer walks.
REPAIR_FORBIDDEN_KEYS = ('proposedValue', 'text', 'value', 'latex', 'textProjection', 'candidate',
                         'originalObservations', 'structuredValue',
                         # WAL-213. A supersession has TWO values — the destroyed reading and the
                         # replacement — so it opens two more doors of exactly the same shape. The
                         # block carries only `supersedes`, the small projection (a count, an
                         # engine, a coverage class); `supersession` is the full record and stays
                         # corpus-side with the rest of the trace.
                         'supersession', 'supersededValue', 'supersedingValue', 'supersededText',
                         'superseded', 'superseding')
REPAIR_REQUIRED_KEYS = ('repairId', 'disposition', 'failureClass', 'method', 'repairVersion',
                        'validatorId', 'verdict')
DISPOSITION_VALIDATED_REPAIR = 'VALIDATED_REPAIR'

#: WAL-213. Exactly what a block-level supersession projection may hold — an allowlist, not a
#: denylist, because the thing being kept out is «any field that could hold a reading» and only an
#: allowlist closes doors nobody has thought of yet.
SUPERSEDES_ALLOWED_KEYS = frozenset({'supersessionId', 'disposition', 'supersededObservations',
                                     'supersedingEngine', 'coverage', 'agreeingScales', 'stacked',
                                     'resolved', 'changed', 'servable'})
SUPERSEDES_DISPOSITIONS = frozenset({'SUPERSEDED', 'CONFLICT'})


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


def repair_of(x):
    """The region-level repair projection, checked. Returns None when there is none.

    Refuses rather than sanitises: a record that carries a value, or claims a disposition the bridge has
    no Founder decision for, is a bug upstream and papering over it is how an ungated repair reaches a
    child. `tool/corpus/repair/tsl_projection.py` writes exactly the accepted shape.
    """
    r = x.get('repair')
    if r is None:
        return None
    if not isinstance(r, dict):
        raise BridgeRefusal(f'block {x.get("id")} has a non-object `repair`')
    missing = [k for k in REPAIR_REQUIRED_KEYS if not r.get(k)]
    if missing:
        raise BridgeRefusal(f'block {x.get("id")} has a repair record missing {missing} — a repair that '
                            f'cannot name its validator and its version is not a repair')
    present = [k for k in REPAIR_FORBIDDEN_KEYS if k in r]
    if present:
        raise BridgeRefusal(f'block {x.get("id")} carries {present} inline on its repair record — the '
                            f'proposed value stays corpus-side (INTERNAL/RESEARCH), never on a block a '
                            f'renderer walks')
    if r['disposition'] != DISPOSITION_VALIDATED_REPAIR:
        raise BridgeRefusal(f'block {x.get("id")} has a repair with disposition {r["disposition"]!r}. '
                            f'This bridge carries {DISPOSITION_VALIDATED_REPAIR} only: making a repair '
                            f'TRUSTED is a Founder gate and the bridge has no input for it.')
    if r.get('servable'):
        raise BridgeRefusal(f'block {x.get("id")} has a repair record claiming to be servable')
    sup = r.get('supersedes')
    if sup is not None:
        if not isinstance(sup, dict):
            raise BridgeRefusal(f'block {x.get("id")} has a non-object `supersedes`')
        extra = sorted(set(sup) - SUPERSEDES_ALLOWED_KEYS)
        if extra:
            raise BridgeRefusal(
                f'block {x.get("id")} carries {extra} on its supersession projection. The block '
                f'form is a COUNT and a COVERAGE CLASS; the readings on both sides of a '
                f'supersession stay corpus-side (INTERNAL/RESEARCH).')
        if sup.get('servable') or sup.get('disposition') not in SUPERSEDES_DISPOSITIONS:
            raise BridgeRefusal(
                f'block {x.get("id")} has a supersession with disposition '
                f'{sup.get("disposition")!r}; a supersession is SUPERSEDED or CONFLICT and is never '
                f'servable')
    return dict(r)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    with open(path, 'rb') as f:
        return sha256_bytes(f.read())


#: Round 6 (WS-C): the hash method travels WITH every hash this module emits. `shasum -a 256` on the
#: written file does NOT reproduce these numbers, and that is deliberate - canonical JSON survives
#: reformatting and key reordering where a raw byte hash does not. A hash a reader cannot reproduce
#: from the artefact alone does not prove lineage; it looks like tampering.
HASH_METHOD = "sha256(json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False))"


def document_hash(doc):
    """sha256 of the canonical JSON (sorted keys, compact) — the determinism oracle. See `HASH_METHOD`."""
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
    repair_ids = set()
    for r in tsl.get('repairs') or []:
        if not isinstance(r, dict) or not r.get('repairId'):
            raise BridgeRefusal('a `repairs[]` entry has no repairId')
        if r.get('disposition') != DISPOSITION_VALIDATED_REPAIR:
            raise BridgeRefusal(f'repair {r["repairId"]} has disposition {r.get("disposition")!r}; only '
                                f'{DISPOSITION_VALIDATED_REPAIR} crosses this bridge — TRUSTED is a Founder gate')
        if r.get('servable'):
            raise BridgeRefusal(f'repair {r["repairId"]} claims to be servable')
        repair_ids.add(r['repairId'])
    for x in list(tsl['blocks']) + list(tsl.get('withheld') or []):
        rp = repair_of(x)
        if rp and rp['repairId'] not in repair_ids:
            raise BridgeRefusal(f'block {x.get("id")} names repair {rp["repairId"]!r} that is not in '
                                f'`repairs[]` — a trace nobody can follow is not a trace')
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
    if repair_of(b) is not None:
        # `tsl_projection.check_projection` already forbids this; asserted again here because the bridge
        # is the last place before a child, and «a served block carrying an untrusted repair» is the
        # exact shape of an ungated restore.
        raise BridgeRefusal(f'block {b["id"]} is SERVED and carries a repair record — a validated repair '
                            f'is not a trusted one')
    mapped = ROLE_MAP.get(role)
    if role in KNOWN_UNCARRIED_ROLES:
        return withheld_block(book, b, [KNOWN_UNCARRIED_ROLES[role]], status='WITHHELD', source_role=role)
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


def withheld_block(book, w, reasons, status, source_role=None, crop_rel=None, repair=None):
    """WithheldBlock JSON — structurally WITHOUT a text field.

    Round 6: it may now carry `repair` — the trace of a `ValidatedRepair` for this region. The region
    stays withheld and stays text-less; what it gains is that a reader can SEE and COUNT that a
    deterministic validator confirmed a repair here and that nobody has gated serving it."""
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
    if repair:
        blk['repair'] = repair
        blk['disposition'] = repair['disposition']
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
# Round 4 correctness review (F7 + F9), both child-facing:
#   F7  the numeral group had NO trailing boundary, so the roman alternative bit into the next word and
#       invented a chapter out of an ordinary section name: «PHẦN VĂN HỌC» → label «Phần V» + title
#       «ĂN HỌC», «PHẦN XÃ HỘI» → «Phần X»/«Ã HỘI», «CHƯƠNG VIỆT NAM …» → «Chương VI», and «HUÂN CHƯƠNG I»
#       (a medal, in Lịch sử prose and on every back cover) matched as a chapter. The numeral must now be
#       followed by a non-letter/non-digit, and the medal phrase is excluded by name.
#   F9  the tone class did not match the comment above it: «Ề» was listed twice, four of the six Ê-family
#       forms were missing (CHỦ ĐỂ / ĐỄ / ĐỆ / ĐÊ all failed) and «Ù» was missing from the CH class. It is
#       now literally the lesson banner's class — the base vowel plus its five tones — on both syllables.
CHAPTER_HDR = re.compile(r'(?<!HUÂN )(?<!Huân )'
                         r'(?:CH[UÙÚỦŨỤ]\s*Đ[ÊỀẾỂỄỆEÈÉẺẼẸ]\s*(\d{1,2})'
                         r'|CHƯƠNG\s+([IVX]+|\d{1,2})'
                         r'|PHẦN\s+([IVX]+|\d{1,2}))'
                         r'(?![0-9A-Za-zÀ-ỹ\u0300-\u036f])\s*[.\-–:]?\s*')


def chapter_label(m):
    """A GENERATED label (never SGK text): the printed marker normalised, its number kept verbatim."""
    if m.group(1):
        return f'Chủ đề {m.group(1)}'
    if m.group(2):
        return f'Chương {m.group(2)}'
    return f'Phần {m.group(3)}'


def clean_toc_title(raw):
    """TOC titles carry dot leaders and a trailing page number; both are furniture, not title text.

    Round 4 correctness review (F8): the trailing-number strip is written for a LESSON line (title ·
    leader · page number), but this function is applied to CHAPTER titles too, and a chapter title often
    carries no page number at all. The old pattern let the separator run be EMPTY, so it matched the TAIL
    of a longer digit run and a History chapter title lost the last digit of its year
    («… TỪ 1858 ĐẾN NĂM 1945» → «… ĐẾN NĂM 1») — a child-facing wrong title, on exactly the books Lane C's
    Golden Slice #2 uses. The separator is now REQUIRED, so only a digit run standing on its own after a
    leader or a space is read as a page number: a year at the end of a title survives, and
    «… THẾ GIỚI .93» / «… MỘT ..... 5» are still stripped.
    """
    t = re.sub(r'[.\u2026]{2,}', ' ', raw)
    # the leader may be a single dot glued to the page number («… THẾ GIỚI .93»)
    t = re.sub(r'[\s.\u2026]+\d{1,3}\s*$', '', t)
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
def canonical_title(book, grade, lesson):
    """Tên bài theo MỤC LỤC IN của chính cuốn sách, hoặc None.

    ⭐⭐ Tiêu đề trong TSL là một dòng OCR quét được GIỮA TRANG, nên nó dính
    đuôi tiêu đề bài trước. Ca thật, KHTN 6 Bài 16:

        TSL     : «RA KHỎI HỒN HỢP HỖN HỢP CÁC CHẤT»   ← dính đuôi Bài 15/17
        mục lục : «Hỗn hợp các chất»                    ← đúng

    Trẻ đọc tiêu đề ấy trên Home, nên đây là chữ hỏng ĐẾN TAY TRẺ.

    `lib/core/display/lesson_title.dart` đã ghi sẵn cách chữa và ghi rõ nó nằm
    ở đâu: «lấy tên từ mục lục in … nằm TRƯỚC tầng hiển thị». Đây chính là chỗ
    ấy — sửa ở lúc SINH dữ liệu, không phải lúc vẽ.

    Không có pack trên máy ⇒ None ⇒ giữ tên của TSL. Fail open có chủ ý: thà
    một tiêu đề kém còn hơn không dựng được bài.
    """
    import json as _json
    path = f'assets/pack/lesson-index-g{grade}.json'
    if not os.path.exists(path):
        return None
    try:
        idx = _json.load(open(path, encoding='utf-8'))
    except (OSError, ValueError):
        return None
    for books in (idx.get('subjects') or {}).values():
        for b in books:
            if b.get('sourceDocumentId') != book:
                continue
            for l in b.get('lessons') or []:
                if l.get('no') == lesson and (l.get('title') or '').strip():
                    return l['title'].strip()
    return None


def block_key(block_id):
    """`<book>:pNNN:<pipeline>:<order>` → `<book>:pNNN:<order>`.

    Round 4: a TSL block id embeds the PIPELINE NAME, so every id written down by hand (the Bài 17 tutor
    script below) stopped resolving the moment the lesson was rebuilt as `tc2-p2` — the script vanished
    with the message «TSL thiếu block», which blamed withholding for what was really a naming mismatch.
    Keys are compared without the pipeline segment; the id carried in the output is still the real one."""
    parts = (block_id or '').split(':')
    return ':'.join(parts[:2] + parts[3:]) if len(parts) >= 4 else block_id


TUTOR_SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tutor_scripts')


def tutor_script_for(tsl, by_id, script_dir=TUTOR_SCRIPT_DIR):
    """Kịch bản SAM cho bài này, đọc từ DỮ LIỆU. `None` ⇒ bài chưa có kịch bản.

    ⭐⭐ WAL-228 — TRƯỚC ĐÂY ĐÂY LÀ MỘT NHÁNH MÃ CHỈ NHẬN ĐÚNG MỘT BÀI:

        if tsl['book'] != '06-sgk-khoa-hoc-tu-nhien-6' or tsl['lesson'] != 17:
            return None

    …với block id đóng cứng và toàn bộ lời SAM viết thẳng trong Python. Nên
    Đọc và Trực quan chạy được cho mọi bài có TSL, còn «Học với SAM» thì không
    — không phải vì thiếu dữ liệu, mà vì một câu `if`.

    Nay mỗi bài là một tệp `<book>-b<NN>.json`. Trong đó:
      · `blocks`  — vai → KHOÁ block (bền qua các lần chạy lại pipeline)
      · `{block:KEY}` trong bất kỳ chuỗi nào → id THẬT của block ấy
      · `{text:KEY}`  → chữ NGUYÊN VĂN của block ấy
    Nhờ vậy lời sách không bị chép lại lần thứ hai vào kịch bản: nó luôn được
    lấy từ chính block đang được trích, nên không thể lệch với sách.

    ⚠ FAIL CLOSED, giữ nguyên như bản cũ: thiếu bất kỳ block nào ⇒ KHÔNG sinh
    kịch bản. Một kịch bản trỏ vào block đã biến mất là một kịch bản nói về
    thứ không còn trong bài.

    ⚠ VÀ KHÔNG SINH TỰ ĐỘNG. `acceptable` là mẫu khớp, `hints` là thang sư
    phạm, `scaffold` là lời sách — máy tự bịa ba thứ ấy là bịa cách dạy. Tệp
    dữ liệu ở đây để NGƯỜI soạn được, không phải để máy sinh.
    """
    path = os.path.join(script_dir, f"{tsl.get('book')}-b{int(tsl.get('lesson') or 0):02d}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
    except (OSError, ValueError) as e:
        print(f'  ! kịch bản {path} không đọc được ({e}) — không sinh tutorScript', file=sys.stderr)
        return None
    if data.get('book') != tsl.get('book') or data.get('lesson') != tsl.get('lesson'):
        print(f'  ! kịch bản {path} khai bài khác — không sinh tutorScript', file=sys.stderr)
        return None

    by_key = {block_key(k): v for k, v in by_id.items()}
    wanted = data.get('blocks') or {}
    missing = [role for role, key in wanted.items() if key not in by_key]
    if missing:
        print(f'  ! TSL thiếu block cho kịch bản ({", ".join(sorted(missing))}) '
              f'— không sinh tutorScript', file=sys.stderr)
        return None
    real = {role: by_key[key]['id'] for role, key in wanted.items()}

    def fill(v):
        if isinstance(v, dict):
            return {k: fill(x) for k, x in v.items()}
        if isinstance(v, list):
            return [fill(x) for x in v]
        if not isinstance(v, str):
            return v
        for role, rid in real.items():
            v = v.replace('{block:%s}' % role, rid)
            v = v.replace('{text:%s}' % role, by_id[rid]['text'])
        return v

    steps = fill(data.get('steps') or [])
    left = [m for st in steps for m in re.findall(r'\{(?:block|text):[^}]+\}', json.dumps(st, ensure_ascii=False))]
    if left:
        print(f'  ! kịch bản còn chỗ trống chưa điền {sorted(set(left))} — không sinh tutorScript',
              file=sys.stderr)
        return None
    return {
        'samMode': data.get('samMode', 'prototypeScripted'),
        'trust': data.get('trust', TRUST_PROTO),
        'evidencePolicy': data.get('evidencePolicy', 'none'),
        'steps': steps,
    }


# ------------------------------------------------------------------ the pure conversion
def convert(tsl, *, tsl_rel_path=None, tsl_sha256=None, book_meta=None, chapters=None, crops=None,
            audit_status='notAudited', audit_ref=None, include_tutor_script=True,
            structural_groups=False, group_rule=False):
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
    # Round 4 correctness review (F10): `caption_for_picture` deliberately lets ONE caption serve
    # side-by-side pictures, but this map is keyed by caption id, so the LAST figure silently overwrote
    # the first. The figure→caption direction is complete either way (every ImageBlock carries its own
    # `captionBlockId`); the consumer model's `captionOf` is a single id, so it now names the first figure
    # the caption serves, deterministically — and a figure the document DROPS (too small, or no crop) never
    # wins over one it keeps, so `captionOf` cannot point at a block that is not in the document.
    caption_of = {}
    for f in sorted((tsl.get('figures') or []), key=lambda f: not figure_kept(f)):
        if f.get('caption'):
            caption_of.setdefault(f['caption'], f['id'])

    # 1. text blocks in reading order (unknown roles become withheld blocks — never dropped)
    seq = []  # (page, y, x, order, block)
    unknown_role = no_carrier = 0
    for b in blocks_in:
        blk = text_block(book, b, caption_of)
        if blk['type'] == 'withheld':
            # Two different facts, counted separately since round 6: «the consumer model has no type for
            # this role» and «the model knows this role and has no carrier for it». Folding them together
            # is what made a formula region indistinguishable from an unrecognised one.
            if any(r.startswith('no_carrier:') for r in blk['reasons']):
                no_carrier += 1
            else:
                unknown_role += 1
        seq.append((b['page'], b['bbox'][1], b['bbox'][0], b['order'], blk))
    # 2. withheld regions of the TSL — by (page, order), with their crop when rendered
    for w in tsl.get('withheld') or []:
        c = crops.get(w['id']) or {}
        seq.append((w['page'], w['bbox'][1], w['bbox'][0], w['order'],
                    withheld_block(book, w, list(w.get('reasons') or []), status=w.get('status') or 'WITHHELD',
                                   crop_rel=c.get('crop'), repair=repair_of(w))))
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
    # 3b. ROUND 7 (WS-S) — structural groups. Both switches default OFF; with both off this block is a
    #     no-op and the document is byte-identical to round 6's.
    group_stats = None
    if structural_groups or group_rule:
        blocks, group_stats = apply_structural_groups(book, tsl, blocks, enforce=group_rule)
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
    script = tutor_script_for(tsl, by_id) if include_tutor_script else None

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
        'title': canonical_title(book, grade, lesson) or tsl['title'],
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
            'hashMethod': HASH_METHOD,
            'docType': tsl.get('docType'),
            'sourceability': tsl.get('sourceability'),
            'answerKeysIncluded': bool(tsl.get('answer_keys_included', False)),
            'auditStatus': audit_status,
            'auditRef': audit_ref,
            'distribution': DISTRIBUTION,
            'tslStats': tsl.get('stats'),
            'repair': repair_summary(tsl, blocks),
            'blockCounts': {
                'byTrust': counts,
                'tslTrusted': len(blocks_in),
                'tslWithheld': len(tsl.get('withheld') or []),
                'unknownRoleWithheld': unknown_role,
                'noCarrierWithheld': no_carrier,
                'validatedRepairsInTsl': len(tsl.get('repairs') or []),
                'validatedRepairsOnBlocks': sum(1 for b in blocks if b.get('repair')),
                'imagesKept': images_kept,
                'imagesWithoutCrop': images_without_crop,
                'figuresInTsl': len(tsl.get('figures') or []),
                # ROUND 7 (WS-S): the key is ABSENT when the group machinery did not run — not present
                # and null, and never a zero. «0 mutilated structures» is only ever a measurement when
                # this key exists; its absence is the honest way to say the question was not asked. It
                # is also what keeps the default document BYTE-IDENTICAL to round 6's: an added `null`
                # would have been a silent schema change on a path a child reads, and
                # `test_tsl_to_lesson_document` caught exactly that before this comment existed.
                **({'structuralGroups': group_stats} if group_stats is not None else {}),
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


def repair_summary(tsl, blocks):
    """Document-level accounting for validated repairs. Counts only — the values stay corpus-side."""
    reps = tsl.get('repairs') or []
    on_blocks = [b['repair'] for b in blocks if b.get('repair')]
    by_class, by_method, capped = {}, {}, 0
    for r in reps:
        by_class[r.get('failureClass')] = by_class.get(r.get('failureClass'), 0) + 1
        by_method[r.get('repairMethod')] = by_method.get(r.get('repairMethod'), 0) + 1
        if r.get('caps'):
            capped += 1
    return {
        'validatedRepairs': len(reps),
        'onBlocks': len(on_blocks),
        'trusted': 0,                     # invariant, not a measurement: nothing here can be trusted
        'capped': capped,
        'byFailureClass': by_class,
        'byMethod': by_method,
        'projection': (tsl.get('repairProjection') or {}).get('version'),
        'framework': (tsl.get('repairProjection') or {}).get('framework'),
        'productionTrustThreshold': None,
        'note': 'VALIDATED REPAIR != TRUSTED. Every repaired region below is still withheld and still '
                'carries no text; the proposed value never leaves the corpus.',
    }


def apply_structural_groups(book, tsl, blocks, enforce):
    """Annotate every block with its structural group and, when `enforce`, apply «serve the whole group
    or none of it». Returns `(blocks, stats)`.

    The direction is FAIL-CLOSED AND ONE-WAY: a group with a withheld member has its served members
    withheld. Nothing is ever restored — restoring a withheld member needs evidence for that member,
    which is a trust decision and a Founder gate, and this bridge has no input for one. So this function
    can only ever REDUCE what a child reads; there is no argument value that makes it serve more.

    Annotation is provenance, not content: `relations.group` carries the group's id, kind, member count
    and how many members are withheld. A reader (or a guard test) can therefore SEE that a served block
    belongs to a mutilated structure without the app gaining any way to read the missing member."""
    by_id = {b['id']: b for b in blocks}
    tsl_by_id = {b['id']: b for b in tsl.get('blocks') or ()}
    groups = structural_groups_of(tsl)
    mutilated, withheld_by_rule = [], []

    for g in groups:
        members = [m for m in g['members'] if m in by_id]
        if not members:
            continue
        served = [m for m in members if by_id[m]['type'] != 'withheld']
        # `repair.groups.apply_group_rule` ignores a group with fewer than two present members except
        # for `figure_caption`; the same bound is kept here so the two paths cannot disagree.
        if len(members) < 2 and g['kind'] != 'figure_caption':
            continue
        n_withheld = len(members) - len(served)
        if served and n_withheld:
            mutilated.append(dict(groupId=g['group_id'], kind=g['kind'], members=len(members),
                                  served=len(served), withheld=n_withheld))
            if enforce:
                for m in served:
                    src = tsl_by_id.get(m)
                    if src is None:            # a withheld region cannot be in `served`
                        raise BridgeRefusal(f'group member {m} has no TSL record')
                    rel = by_id[m].get('relations')
                    repl = withheld_block(book, src, [f'{GROUP_REASON}:{g["kind"]}'],
                                          status='WITHHELD', source_role=role_of(src))
                    repl['relations'] = rel
                    blocks[blocks.index(by_id[m])] = repl
                    by_id[m] = repl
                    withheld_by_rule.append(m)
        # Annotate LAST, so `withheldMembers` describes the document that is actually emitted rather
        # than the one that existed before the rule ran. A provenance field that reports a state the
        # document no longer has is the shape round 5 caught in serialisation: a record that quietly
        # says the content is better grounded than it is.
        final_withheld = sum(1 for m in members if by_id[m]['type'] == 'withheld')
        for m in members:
            by_id[m].setdefault('relations', {})['group'] = {
                'id': g['group_id'], 'kind': g['kind'],
                'members': len(members), 'withheldMembers': final_withheld}

    stats = {
        'ruleApplied': bool(enforce),
        'groups': len(groups),
        'byKind': {k: sum(1 for g in groups if g['kind'] == k) for k in sorted({g['kind'] for g in groups})},
        # BEFORE the rule — the defect as it stands. With `ruleApplied` true these are the structures the
        # rule resolved, not structures that remain; `mutilatedRemaining` is the number that stays.
        'mutilatedBeforeRule': len(mutilated),
        'mutilated': mutilated,
        'mutilatedRemaining': 0 if enforce else len(mutilated),
        'blocksWithheldByRule': len(withheld_by_rule),
        'note': 'procedure_steps is a LOWER BOUND: a withheld region carries no text, so an enumerated '
                'step that is withheld cannot be recognised as a member. question_options and '
                'table_rows are role-decided and complete.',
    }
    return blocks, stats


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
    counts = doc['provenance']['blockCounts']
    # ROUND 7 (WS-S): the group rule withholds ALREADY-SERVABLE blocks, so the conservation identity
    # gains a fourth term. It is read from the emitted stats, not recomputed, so a rule that withheld a
    # block without recording it fails this assert instead of hiding inside a bigger number.
    by_rule = ((counts.get('structuralGroups') or {}).get('blocksWithheldByRule') or 0)
    assert n_withheld == (len(tsl.get('withheld') or [])
                          + counts['unknownRoleWithheld'] + counts.get('noCarrierWithheld', 0)
                          + by_rule), (
        f'withheld conservation: {n_withheld} != tsl {len(tsl.get("withheld") or [])} + unknownRole '
        f'{counts["unknownRoleWithheld"]} + noCarrier {counts.get("noCarrierWithheld", 0)} + rule {by_rule}')
    assert doc['licence'] == LICENCE and doc['provenance']['trust'] == TRUST_TSL
    assert doc['provenance']['answerKeysIncluded'] is False
    # verbatim: every trusted text block reproduces the TSL text unchanged
    tsl_text = {b['id']: b['text'] for b in tsl['blocks']}
    for b in blocks:
        if b['id'] in tsl_text and b['type'] not in ('withheld', 'table'):
            assert b['text'] == tsl_text[b['id']], f'text altered for {b["id"]}'

    # ---- ROUND 6 (workstream C): a validated repair crosses, its VALUE does not.
    #
    # The weak version of this check reads the fields we chose to emit and finds nothing, because we
    # chose not to emit them. The strong version searches the WHOLE serialised document for each
    # proposed value, so a future field, a nested provenance dict or a careless `**record` cannot open
    # the door quietly. Values equal to the block's own observation are skipped: an unchanged proposal
    # is the text the TSL already carries, and finding it proves nothing.
    blob = json.dumps(doc, ensure_ascii=False)
    for r in tsl.get('repairs') or []:
        proposed = ((r.get('candidate') or {}).get('proposed_value'))
        observed = next((o.get('value') for o in (r.get('originalObservations') or [])), None)
        if not isinstance(proposed, str) or len(proposed) < 8 or proposed == observed:
            continue
        assert proposed not in blob, (
            f'the proposed value of repair {r.get("repairId")} appears in the LessonDocument — a '
            f'repaired value reached the app without a Founder trust decision')
    for b in blocks:
        rp = b.get('repair')
        if not rp:
            continue
        assert b['type'] == 'withheld', f'block {b["id"]} is servable and carries a repair record'
        assert 'text' not in b, f'repaired block {b["id"]} carries text'
        assert rp['disposition'] == DISPOSITION_VALIDATED_REPAIR
        assert b.get('disposition') == DISPOSITION_VALIDATED_REPAIR
    assert doc['provenance']['repair']['trusted'] == 0


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


def crop_neighbours(tsl):
    """{page: [(id, bbox)]} — everything a crop's padding must stop short of.

    Round 4 correctness review (F11): this set was built from `blocks` + `withheld` only, so two adjacent
    FIGURE crops could still bleed into each other by the full pad — the very failure `crop_pads` exists to
    stop, in the one case where the foreign content is another picture. Figures are neighbours too. A
    figure's own caption and its own bbox are excluded by the caller, as before.
    """
    out = {}
    for b in list(tsl.get('blocks') or []) + list(tsl.get('withheld') or []) + list(tsl.get('figures') or []):
        if b.get('bbox'):
            out.setdefault(b['page'], []).append((b.get('id'), b['bbox']))
    return out


def render_crops(tsl, out_dir, dpi=150):
    """Figure + withheld-region crops → {id: {'crop': rel, 'aspect': w/h}}. No PDF ⇒ {} (the document is
    still produced, without images). INTERNAL / RESEARCH ONLY (D4)."""
    book = tsl['book']
    pdf = pdf_path(book)
    if not pdf:
        print(f'  ! không thấy PDF cho {book} — sinh tài liệu KHÔNG crop', file=sys.stderr)
        return {}
    out = {}
    nb_by_page = crop_neighbours(tsl)

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


def build(tsl_path, out_dir, dpi=150, crops=True, audit_status='notAudited', audit_ref=None,
          structural_groups=False, group_rule=False):
    """The ONE path: TSL file → `<out_dir>/lesson-<book>-b<N>.json` (+ crops/). Returns the output path."""
    tsl = json.load(open(tsl_path, encoding='utf-8'))
    validate_tsl(tsl)
    crop_map = render_crops(tsl, out_dir, dpi) if crops else {}
    doc = convert(tsl, tsl_rel_path=os.path.relpath(tsl_path, ROOT), tsl_sha256=sha256_file(tsl_path),
                  book_meta=book_meta_for(tsl['book']), chapters=chapters_from_toc(tsl['book']), crops=crop_map,
                  audit_status=audit_status, audit_ref=audit_ref,
                  structural_groups=structural_groups, group_rule=group_rule)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'lesson-{tsl["book"]}-b{tsl["lesson"]}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    kinds = {}
    for b in doc['blocks']:
        kinds[b['type']] = kinds.get(b['type'], 0) + 1
    print(f'{out_path}\n  hash={document_hash(doc)} ({HASH_METHOD})\n  blocks={len(doc["blocks"])} {kinds}\n  byTrust={doc["provenance"]["blockCounts"]["byTrust"]}'
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
    ap.add_argument('--structural-groups', action='store_true',
                    help='annotate relations.group (provenance only — serves nothing new)')
    ap.add_argument('--group-rule', action='store_true',
                    help='ENFORCE «serve the whole structural group or none of it» (round 5 defect 8). '
                         'WITHHOLDS MORE, never less. Off by default: switching it on removes blocks a '
                         'child reads today, which is a Founder decision, not a lane\'s.')
    a = ap.parse_args(argv)
    try:
        build(a.tsl, a.out, dpi=a.dpi, crops=not a.no_crops, audit_status=a.audit_status,
              audit_ref=a.audit_ref, structural_groups=a.structural_groups, group_rule=a.group_rule)
    except BridgeRefusal as e:
        print(f'REFUSED: {e}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
