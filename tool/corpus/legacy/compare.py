#!/usr/bin/env python3
"""Round 4 · Lane D — OLD vs NEW compare for one legacy batch (mechanical alignment; the judged rates come
from audit.py — this file never decides trust).

    python3 tool/corpus/legacy/compare.py --batch-dir poc-out/round4/legacy/batch-1
        → <batch-dir>/compare/compare.json + compare.md (internal: verbatim text allowed, D4)

OLD side = what the product served for the lesson: every unit of poc-out/units/<book>.json with that lesson
number (= the sam-units.db rows, same ids) + the default-pack activities (toanExercises expressions, tvReadings
passage/questions, tvWritings prompts, khoaExperiments strings, suSources). Each OLD block is linked to the OCR
lines it was cut from (ft_audit_sample.link_lines, Lane A code called as-is) → page + bbox.
NEW side = the batch's Trusted Structured Lesson (tc2_tsl, pipeline <id>): TRUSTED blocks with text + WITHHELD
regions (bbox + reasons, no text) + SDM figure regions + the header-based page attachment.

Alignment is geometric (page + bbox overlap): every OLD block is classified as
  now_trusted          ≥ 50 % of its region under TRUSTED new blocks and text similarity ≥ 0.80
  now_trusted_changed  … under TRUSTED new blocks but the text differs (one side is wrong — the audit says which)
  now_withheld         ≥ 50 % under WITHHELD / figure regions (the pipeline refuses what OLD served)
  now_mixed            partly trusted, partly withheld
  now_absent           nothing in the new output covers the region (not extracted at all)
  now_other_lesson     the new header-based attachment puts the page in another lesson / no lesson
plus MECHANICAL per-class signals (labelled mechanical, never a judged rate): attachment (OLD lesson vs NEW
page attachment), reading order (OLD line spans that cross the column gap), formula/number/unit (fraction-like
digit runs in OLD text · math_guard withholds in NEW · residual digit runs in NEW trusted text), figure/caption
(OLD spans inside NEW figure regions · figure_text withheld in NEW), role (OLD role vs NEW role of the matched
block). Hashes/versions for both sides; nothing overwritten (versioned write).
"""
import argparse
import collections
import difflib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))
import common  # noqa: E402

os.environ.setdefault('TC_ROOT', common.MAIN_ROOT)
import ft_audit_sample as fas  # noqa: E402  (Lane A-pipeline code, read-only use)

fas.ROOT = common.MAIN_ROOT
COMPARE_VERSION = 'legacy-compare-v1'
DIGIT_RUN = re.compile(r'(?<!\d)\d{1,3}(?:\s+\d{1,3}){1,}(?!\d)')     # "1 2 3 4" — a flattened fraction / stacked digits
FRACTION = re.compile(r'\b\d{1,3}\s*/\s*\d{1,3}\b')
OPERATOR_FRAGMENT = re.compile(r'(^|\s)[+\-×x:=]\s*$|(^|\s)[+\-×:]\s+[+\-×:]')
ROLE_MAP = {  # OLD unit role → set of NEW roles that mean the same thing
    'EXERCISE': {'question', 'option', 'instruction', 'activity', 'body'},
    'SECTION_TEXT': {'body', 'heading', 'objective', 'stage_label', 'caption', 'sidebar', 'footnote'},
    'RULE': {'rule', 'body', 'sidebar'},
    'EXAMPLE': {'body', 'question'},
    'RULE_CANDIDATE': {'rule', 'body', 'sidebar'},
    'expr': {'formula', 'body', 'question'},
    'passage': {'body', 'heading'}, 'question': {'question'}, 'prompt': {'question', 'instruction', 'body'},
    'title': {'heading', 'question', 'body'}, 'chuanBi': {'body', 'instruction'}, 'step': {'instruction', 'body'}, 'duDoan': {'question', 'body'}, 'quanSat': {'question', 'body'},
    'excerpt': {'body', 'sidebar'}, 'attribution': {'attribution', 'footnote', 'body', 'caption'},
}


# ---------------------------------------------------------------- geometry
def overlap_frac(a, b):
    """share of bbox a's area that lies inside bbox b ([x, y, w, h] normalised)."""
    if not a or not b or a[2] <= 0 or a[3] <= 0:
        return 0.0
    ix = max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
    return (ix * iy) / (a[2] * a[3])


def text_sim(a, b):
    a, b = common.norm(a), common.norm(b)
    if not a or not b:
        return 0.0
    return round(difflib.SequenceMatcher(None, a, b).ratio(), 3)


def crosses_column_gap(lines, idx, gap_x=None):
    """Mechanical reading-order signal: the OLD unit's lines alternate between the left and right half of the
    page (centre crosses the gap ≥ 2 times) — the WAL-204 column-interleave mechanism."""
    if len(idx) < 3:
        return False
    gx = gap_x if gap_x is not None else 0.5
    sides = []
    for i in idx:
        l = lines[i]
        cx = l['x'] + l['w'] / 2
        w = l['w']
        if w > 0.55:            # a full-width line belongs to no column
            sides.append(None); continue
        sides.append('L' if cx < gx else 'R')
    sides = [s for s in sides if s]
    flips = sum(1 for a, b in zip(sides, sides[1:]) if a != b)
    return flips >= 2


# ---------------------------------------------------------------- OLD side
def old_blocks_for_lesson(book, lesson, packs=None, units_dir=common.UNITS, printed_offset=1):
    """OLD served blocks of one lesson: units (= sam-units rows) + pack activities, each linked to OCR lines.
    `printed_offset` = pdf page − printed page for pack entries that carry only the printed page."""
    out = []
    j = common.load_json(f'{units_dir}/{book}.json') or {}

    def to_pdf(e):
        if e.get('pagePdf'):
            return int(e['pagePdf'])
        try:
            return int(e.get('page')) + printed_offset
        except (TypeError, ValueError):
            return None
    for u in j.get('units', []):
        if u.get('lesson') != lesson:
            continue
        out.append(dict(family='samUnits', id=u['id'], kind=u.get('role'), page_pdf=u.get('pagePdf'), page_printed=u.get('pagePrinted'), text=u.get('text') or '', old_lesson=lesson,
                        extraction=(u.get('provenance') or {}).get('extraction')))
    packs = packs if packs is not None else load_packs_main()
    for g, pk in packs.items():
        for fam, val in pk.items():
            if fam in ('grade', 'version', 'subjects', 'books', 'buildProvenance'):
                continue
            entries = []
            if isinstance(val, dict):
                for k, es in val.items():
                    for e in (es if isinstance(es, list) else [es]):
                        try:
                            n = int(e.get('lesson', k))
                        except (TypeError, ValueError):
                            continue
                        entries.append((n, e))
            elif isinstance(val, list):
                entries = [(int(e['lesson']), e) for e in val if e.get('lesson') is not None]
            for n, e in entries:
                if e.get('book') != book or n != lesson:
                    continue
                aid = f'{fam}:{book}:L{lesson}:p{e.get("pagePdf") or e.get("page")}'
                if fam == 'toanExercises':
                    pp = to_pdf(e)                        # exercise-case-map page is PRINTED; pdf = printed + offset (1 in Toán 4–5)
                    out.append(dict(family=fam, id=f'{aid}:{e.get("expr")}', kind='expr', page_pdf=pp, page_printed=e.get('page'), text=e.get('expr') or '', old_lesson=lesson, extraction='geometric-fraction-rebuild-v1'))
                elif fam == 'tvReadings':
                    pp = to_pdf(e)
                    out.append(dict(family=fam, id=f'{aid}:passage', kind='passage', page_pdf=pp, page_printed=e.get('page'), text=e.get('passage') or '', old_lesson=lesson, extraction='units-tv-v1'))
                    for i, q in enumerate(e.get('questions') or [], 1):
                        qt = q if isinstance(q, str) else (q.get('prompt') or q.get('text') or '')
                        qp = (q.get('page') if isinstance(q, dict) else None)
                        out.append(dict(family=fam, id=f'{aid}:question{i}', kind='question', page_pdf=(int(qp) + printed_offset) if qp else pp, page_printed=qp or e.get('page'), text=qt, old_lesson=lesson, extraction='units-tv-v1'))
                elif fam == 'tvWritings':
                    out.append(dict(family=fam, id=f'{aid}:prompt', kind='prompt', page_pdf=to_pdf(e), page_printed=e.get('page'), text=e.get('prompt') or '', old_lesson=lesson, extraction='units-tv-v1'))
                elif fam == 'khoaExperiments':
                    pp = e.get('pagePdf')
                    for kind in ('title', 'chuanBi', 'duDoan', 'quanSat'):
                        if e.get(kind):
                            out.append(dict(family=fam, id=f'{aid}:{kind}', kind=kind, page_pdf=pp, page_printed=e.get('page'), text=e[kind], old_lesson=lesson, extraction='ocr-body-naive-lines'))
                    for i, s in enumerate(e.get('tienHanh') or [], 1):
                        out.append(dict(family=fam, id=f'{aid}:step{i}', kind='step', page_pdf=pp, page_printed=e.get('page'), text=s, old_lesson=lesson, extraction='ocr-body-naive-lines'))
                elif fam == 'suSources':
                    for kind in ('excerpt', 'attribution'):
                        if e.get(kind):
                            out.append(dict(family=fam, id=f'{aid}:{kind}', kind=kind, page_pdf=e.get('pagePdf'), page_printed=e.get('page'), text=e[kind], old_lesson=lesson, extraction='ocr-body-naive-lines'))
    for b in out:
        b['sha256'] = common.sha256_text(b['text'])
        b['page_pdf'] = int(b['page_pdf']) if b.get('page_pdf') else None
        if b['page_pdf'] and b['text'] and b['kind'] != 'expr':
            idx, bbox, cov = fas.link_lines(book, b['page_pdf'], b['text'])
            b.update(line_idx=idx, bbox=bbox, line_coverage=cov)
            lines = fas.ocr_lines(book, b['page_pdf'])
            b['order_crosses_columns'] = crosses_column_gap(lines, idx) if idx else False
        else:
            b.update(line_idx=[], bbox=None, line_coverage=0.0, order_crosses_columns=False)
        b['digit_run'] = bool(DIGIT_RUN.search(b['text'])) or bool(FRACTION.search(b['text']))
    return out


def load_packs_main():
    packs = {}
    for g in range(1, 13):
        j = common.load_json(f'{common.PACK_DIR}/lesson-index-g{g}.json')
        if j:
            packs[g] = j
    return packs


# ---------------------------------------------------------------- NEW side
def new_side(batch_dir, pipeline, book, lesson):
    root = f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{pipeline}'
    tsl_path = f'{root}/lessons/{book}/bai-{lesson:02d}.tsl.json'
    tsl = common.load_json(tsl_path)
    att = common.load_json(f'{root}/attach/{book}.json') or {}
    pages = {p['page']: p for p in att.get('pages', [])}
    figures = collections.defaultdict(list)
    sdm_pages = {}
    if tsl:
        for p in tsl['boundary']['pages']:
            s = common.load_json(f'{root}/sdm/{book}/p{p:03d}.sdm.json')
            if s:
                sdm_pages[p] = s
                for fg in s.get('figures', []):
                    figures[p].append(fg['bbox'])
    ld_path = f'{batch_dir}/lesson-documents/lesson-{book}-b{lesson}.json'
    ld = common.load_json(ld_path)
    return dict(tsl=tsl, tsl_path=tsl_path, tsl_sha256=(common.sha256_file(tsl_path) if tsl else None), attach_pages=pages, figures=figures, sdm_pages=sdm_pages,
                printed_offset=(att.get('counts') or {}).get('printed_offset'),
                lesson_document_path=ld_path if ld else None, lesson_document_sha256=(common.sha256_file(ld_path) if ld else None),
                document_source_hash=((ld or {}).get('provenance') or {}).get('sourceHash'), document_pipeline=((ld or {}).get('provenance') or {}).get('pipelineVersion'))


# ---------------------------------------------------------------- alignment
def align_block(ob, new, lesson):
    """Classify one OLD block against the NEW lesson output on its page."""
    tsl = new['tsl']
    page = ob.get('page_pdf')
    att = new['attach_pages'].get(page) if page else None
    new_lesson = att.get('lesson') if att else None
    res = dict(old_id=ob['id'], family=ob['family'], kind=ob['kind'], page_pdf=page, old_bbox=ob.get('bbox'), new_page_lesson=new_lesson, new_attach_method=att.get('method') if att else None,
               new_page_kind=att.get('kind') if att else None, attachment_differs=(new_lesson != lesson), matched_trusted=[], matched_withheld=[], cover_trusted=0.0, cover_withheld=0.0, cover_figure=0.0,
               text_sim=None, new_text_len=0, role_new=None, role_compatible=None, withheld_reasons=[], status=None)
    if tsl is None:
        res['status'] = 'now_absent'; res['note'] = 'no TSL for this lesson (pipeline produced nothing → WITHHELD, nothing guessed)'
        return res
    if new_lesson != lesson:
        res['status'] = 'now_other_lesson'
    bb = ob.get('bbox')
    if not bb:
        # geometry-rebuilt Toán expressions and unlinked strings: page-level only
        page_trusted = [b for b in tsl['blocks'] if b['page'] == page]
        best = max(page_trusted, key=lambda b: text_sim(ob['text'], b['text']), default=None)
        if best is not None and ob['kind'] == 'expr':
            # an expression counts as present only if the exact normalised expr string occurs in a trusted block
            key = re.sub(r'\s+', '', ob['text'])
            hit = [b for b in page_trusted if key in re.sub(r'\s+', '', b['text'])]
            res['matched_trusted'] = [b['id'] for b in hit]
            res['text_sim'] = 1.0 if hit else 0.0
            if res['status'] is None:
                res['status'] = 'now_trusted' if hit else ('now_withheld' if any(w['page'] == page for w in tsl['withheld']) else 'now_absent')
            res['note'] = 'expression rebuilt from geometry (no OCR line span): matched by exact string against trusted blocks of the page'
        elif res['status'] is None:
            res['status'] = 'now_absent'; res['note'] = 'OLD text could not be linked to OCR lines on its page'
        return res
    for b in tsl['blocks']:
        if b['page'] != page:
            continue
        f = overlap_frac(bb, b['bbox'])
        g = overlap_frac(b['bbox'], bb)
        if f >= 0.05 or g >= 0.5:
            res['matched_trusted'].append(b['id'])
            res['cover_trusted'] += min(f, 1.0)
    for w in tsl['withheld']:
        if w['page'] != page:
            continue
        f = overlap_frac(bb, w['bbox'])
        g = overlap_frac(w['bbox'], bb)
        if f >= 0.05 or g >= 0.5:
            res['matched_withheld'].append(w['id'])
            res['cover_withheld'] += min(f, 1.0)
            res['withheld_reasons'].extend(w.get('reasons') or [])
    for fg in new['figures'].get(page, []):
        res['cover_figure'] += min(overlap_frac(bb, fg), 1.0)
    res['cover_trusted'] = round(min(res['cover_trusted'], 1.0), 3); res['cover_withheld'] = round(min(res['cover_withheld'], 1.0), 3); res['cover_figure'] = round(min(res['cover_figure'], 1.0), 3)
    res['withheld_reasons'] = sorted(set(res['withheld_reasons']))
    if res['matched_trusted']:
        by_id = {b['id']: b for b in tsl['blocks']}
        texts = [by_id[i]['text'] for i in res['matched_trusted']]
        res['text_sim'] = text_sim(ob['text'], ' '.join(texts))
        res['new_text_len'] = sum(len(t) for t in texts)
        roles = [by_id[i]['role']['value'] for i in res['matched_trusted']]
        res['role_new'] = roles[0] if len(set(roles)) == 1 else '+'.join(sorted(set(roles)))
        ok = ROLE_MAP.get(ob['kind'], set())
        res['role_compatible'] = any(r in ok for r in roles) if ok else None
        res['new_digit_run'] = any(DIGIT_RUN.search(t) or OPERATOR_FRAGMENT.search(t) for t in texts)
    if res['status'] is not None:
        return res
    ct, cw, cf = res['cover_trusted'], res['cover_withheld'], res['cover_figure']
    if ct >= 0.5 and cw < 0.25:
        res['status'] = 'now_trusted' if (res['text_sim'] or 0) >= 0.8 else 'now_trusted_changed'
    elif (cw + cf) >= 0.5 and ct < 0.25:
        res['status'] = 'now_withheld'
    elif ct >= 0.25 or cw >= 0.25:
        res['status'] = 'now_mixed'
    else:
        res['status'] = 'now_absent'
    return res


def lesson_compare(batch_dir, pipeline, L, packs):
    book, lesson = L['book'], int(L['lesson'])
    new = new_side(batch_dir, pipeline, book, lesson)
    old = old_blocks_for_lesson(book, lesson, packs, printed_offset=new.get('printed_offset') or 1)
    grade = int(book[:2])
    grade_pack = (packs.get(grade) or {}).get('buildProvenance') or {}
    aligned = [align_block(ob, new, lesson) for ob in old]
    tsl = new['tsl']
    status = collections.Counter(a['status'] for a in aligned)
    by_family = collections.defaultdict(collections.Counter)
    for a in aligned:
        by_family[a['family']][a['status']] += 1
    old_pages = sorted(set(ob['page_pdf'] for ob in old if ob.get('page_pdf')))
    new_pages = tsl['boundary']['pages'] if tsl else []
    att_pages = {p: new['attach_pages'].get(p, {}) for p in sorted(set(old_pages) | set(new_pages) | set(L.get('pages_pdf', [])))}
    trusted_blocks = tsl['blocks'] if tsl else []
    withheld = tsl['withheld'] if tsl else []
    mech = dict(
        attachment=dict(old_pages_now_other_lesson=[p for p in old_pages if (att_pages.get(p) or {}).get('lesson') != lesson],
                        new_pages_with_no_printed_number=[p for p, s in new['sdm_pages'].items() if s.get('printed_page') is None],
                        new_pages_kind=dict(collections.Counter((att_pages.get(p) or {}).get('kind') or 'unknown' for p in new_pages)),
                        old_blocks_other_lesson=status.get('now_other_lesson', 0)),
        reading_order=dict(old_blocks_crossing_columns=sum(1 for ob in old if ob.get('order_crosses_columns')), old_blocks_multi_line=sum(1 for ob in old if len(ob.get('line_idx') or []) >= 2),
                           new_withheld_agree_order=sum(1 for w in withheld if 'agree_order' in (w.get('reasons') or [])), new_trusted_single_column=sum(1 for b in trusted_blocks)),
        formula_number_unit=dict(old_blocks_with_digit_runs=sum(1 for ob in old if ob.get('digit_run')), old_geometry_rebuilt_exprs=sum(1 for ob in old if ob['kind'] == 'expr'),
                                 old_exprs_present_verbatim_in_new=sum(1 for a in aligned if a['kind'] == 'expr' and a['status'] == 'now_trusted'),
                                 new_withheld_math_guard=sum(1 for w in withheld if 'math_guard' in (w.get('reasons') or [])),
                                 new_trusted_with_digit_runs=sum(1 for b in trusted_blocks if DIGIT_RUN.search(b['text'] or '') or OPERATOR_FRAGMENT.search(b['text'] or '')),
                                 new_trusted_formula_role=sum(1 for b in trusted_blocks if b['role']['value'] == 'formula')),
        figure_caption=dict(old_blocks_inside_figure=sum(1 for a in aligned if a['cover_figure'] >= 0.5), new_withheld_figure_text=sum(1 for w in withheld if 'figure_text' in (w.get('reasons') or [])),
                            new_withheld_figure_dependent=sum(1 for w in withheld if 'figure_dependent' in (w.get('reasons') or [])), new_trusted_captions=sum(1 for b in trusted_blocks if b['role']['value'] == 'caption'),
                            new_figures=len(tsl['figures']) if tsl else 0),
        role=dict(old_roles=dict(collections.Counter(ob['kind'] for ob in old)), new_roles_trusted=dict(collections.Counter(b['role']['value'] for b in trusted_blocks)),
                  matched_role_compatible=sum(1 for a in aligned if a['role_compatible'] is True), matched_role_incompatible=sum(1 for a in aligned if a['role_compatible'] is False)),
        display=dict(text_sim_mean=round(sum(a['text_sim'] for a in aligned if a['text_sim'] is not None) / max(1, sum(1 for a in aligned if a['text_sim'] is not None)), 3),
                     text_sim_lt_0_8=sum(1 for a in aligned if a['text_sim'] is not None and a['text_sim'] < 0.8)),
    )
    # short diff samples — the largest changes among blocks that are now trusted-but-changed / withheld
    samples = []
    by_id = {b['id']: b for b in trusted_blocks}
    for a in sorted(aligned, key=lambda a: (a['status'] != 'now_trusted_changed', a['text_sim'] if a['text_sim'] is not None else 1.0))[:6]:
        ob = next(o for o in old if o['id'] == a['old_id'])
        samples.append(dict(old_id=a['old_id'], status=a['status'], old=ob['text'][:80], new=' '.join(by_id[i]['text'] for i in a['matched_trusted'])[:80] if a['matched_trusted'] else None,
                            withheld_reasons=a['withheld_reasons'], text_sim=a['text_sim']))
    if tsl is None:
        new_class, reasons = 'withheld', ['no TSL produced (pipeline could not process the lesson pages)']
    elif tsl['stats']['trusted'] == 0:
        new_class, reasons = 'withheld', ['0 trusted blocks']
    elif mech['attachment']['new_pages_with_no_printed_number'] or any(k in ('back_matter', 'front_matter') for k in mech['attachment']['new_pages_kind']):
        new_class, reasons = 'partial', [f"sourceability {tsl['sourceability']}", 'pages without a printed page number attached to the lesson (attachment suspect — audit decides)']
    else:
        new_class, reasons = ('partial' if tsl['sourceability'] == 'PARTIAL' else 'full_candidate'), [f"sourceability {tsl['sourceability']}", f"withheld {tsl['stats']['withheld']} of {tsl['stats']['learning_blocks']} learning blocks"]
    return dict(book=book, lesson=lesson, title=L.get('title'), label=common.book_label(book), risk=L.get('risk'), why=L.get('why'),
                old=dict(blocks=len(old), by_family=dict(collections.Counter(ob['family'] for ob in old)), pages_pdf=old_pages, units_file=f'{common.UNITS}/{book}.json',
                         units_file_sha256=common.sha256_file(f'{common.UNITS}/{book}.json') if os.path.exists(f'{common.UNITS}/{book}.json') else None,
                         sam_units_db_sha256=common.sha256_file(common.SAM_UNITS_DB) if os.path.exists(common.SAM_UNITS_DB) else None,
                         pack_version=grade_pack.get('packVersion'), pack_content_hash=grade_pack.get('contentHash'), pack_builder=grade_pack.get('builderVersion'),
                         extractors=sorted(set(ob.get('extraction') or '?' for ob in old)), blocks_sha256=common.sha256_json([ob['sha256'] for ob in old])),
                new=dict(pipeline=pipeline, tsl_path=os.path.relpath(new['tsl_path'], common.MAIN_ROOT), tsl_sha256=new['tsl_sha256'], lesson_document=new['lesson_document_path'] and os.path.relpath(new['lesson_document_path'], common.MAIN_ROOT),
                         lesson_document_sha256=new['lesson_document_sha256'], document_source_hash=new['document_source_hash'], document_pipeline=new['document_pipeline'], sourceability=tsl['sourceability'] if tsl else None,
                         boundary=tsl['boundary'] if tsl else None, stats=tsl['stats'] if tsl else None, pages_processed=new_pages),
                attach_by_page={str(p): dict(lesson=(a or {}).get('lesson'), method=(a or {}).get('method'), kind=(a or {}).get('kind'), printed=(a or {}).get('printed')) for p, a in att_pages.items()},
                old_block_status=dict(status), old_block_status_by_family={k: dict(v) for k, v in by_family.items()}, mechanical=mech,
                new_version_class=new_class, new_version_class_reasons=reasons, new_version_class_note='mechanical, pre-audit: partial = trusted blocks + withheld regions; full_candidate = no withheld region; withheld = nothing trusted. REPROCESSED ≠ TRUSTED — the scoreboard overlays the independent audit (rejected when a trusted block carries a teaching-critical error or non-lesson content).',
                diff_samples=samples, aligned=aligned)


def render_md(cmp_):
    o = []
    o.append(f"# OLD vs NEW compare — {cmp_['batch']} (pipeline {cmp_['pipeline']}) · {COMPARE_VERSION} · INTERNAL (D4)\n")
    o.append(f"code {cmp_['pipeline_code_sha']} · generated {cmp_['generated']} · mechanical alignment only — judged rates are in the audit files.\n")
    o.append('| lesson | OLD blocks (family) | OLD pages | NEW pages processed | NEW trusted / withheld (reasons) | OLD → now_trusted / changed / withheld / mixed / absent / other-lesson | new class (pre-audit) |')
    o.append('|---|---|---|---|---|---|---|')
    for L in cmp_['lessons']:
        s = L['old_block_status']; st = L['new']['stats'] or {}
        o.append(f"| {L['label']} Bài {L['lesson']} | {L['old']['blocks']} {L['old']['by_family']} | {L['old']['pages_pdf']} | {L['new']['pages_processed']} | {st.get('trusted')} / {st.get('withheld')} {st.get('withheld_by_reason')} | "
                 f"{s.get('now_trusted', 0)} / {s.get('now_trusted_changed', 0)} / {s.get('now_withheld', 0)} / {s.get('now_mixed', 0)} / {s.get('now_absent', 0)} / {s.get('now_other_lesson', 0)} | **{L['new_version_class']}** — {'; '.join(L['new_version_class_reasons'])} |")
    o.append('\n## Mechanical signals per failure class (OLD served blocks vs NEW output — counts, not judged rates)\n')
    for L in cmp_['lessons']:
        m = L['mechanical']
        o.append(f"### {L['label']} Bài {L['lesson']} — {L['title']}")
        o.append(f"- attachment: OLD pages now attached elsewhere {m['attachment']['old_pages_now_other_lesson']}; NEW pages without a printed number {m['attachment']['new_pages_with_no_printed_number']}; NEW page kinds {m['attachment']['new_pages_kind']}")
        o.append(f"- reading order: OLD blocks whose lines cross the column gap {m['reading_order']['old_blocks_crossing_columns']} / {m['reading_order']['old_blocks_multi_line']} multi-line; NEW withheld by agree_order {m['reading_order']['new_withheld_agree_order']} (every trusted NEW block is one column, order verified by two stacks)")
        o.append(f"- formula/number/unit: OLD blocks with flattened digit runs {m['formula_number_unit']['old_blocks_with_digit_runs']}; geometry-rebuilt exprs {m['formula_number_unit']['old_geometry_rebuilt_exprs']} (present verbatim in NEW trusted text: {m['formula_number_unit']['old_exprs_present_verbatim_in_new']}); NEW math_guard withheld {m['formula_number_unit']['new_withheld_math_guard']}; **NEW trusted blocks still carrying digit runs / operator fragments {m['formula_number_unit']['new_trusted_with_digit_runs']}** (residual risk → audit)")
        o.append(f"- figure/caption: OLD blocks inside a NEW figure region {m['figure_caption']['old_blocks_inside_figure']}; NEW figure_text withheld {m['figure_caption']['new_withheld_figure_text']}, figure_dependent {m['figure_caption']['new_withheld_figure_dependent']}, trusted captions {m['figure_caption']['new_trusted_captions']}, figures {m['figure_caption']['new_figures']}")
        o.append(f"- role: OLD {m['role']['old_roles']} → NEW trusted {m['role']['new_roles_trusted']}; matched compatible {m['role']['matched_role_compatible']} / incompatible {m['role']['matched_role_incompatible']}")
        o.append(f"- display: mean text similarity of matched blocks {m['display']['text_sim_mean']}; matched with sim < 0.8: {m['display']['text_sim_lt_0_8']}")
        o.append(f"- hashes: OLD units {L['old']['units_file_sha256'] and L['old']['units_file_sha256'][:12]} · sam-units.db {L['old']['sam_units_db_sha256'] and L['old']['sam_units_db_sha256'][:12]} · pack {L['old']['pack_version']} ({L['old']['pack_content_hash'] and L['old']['pack_content_hash'][:12]}) | NEW TSL {L['new']['tsl_sha256'] and L['new']['tsl_sha256'][:12]} · LessonDocument {L['new']['lesson_document_sha256'] and L['new']['lesson_document_sha256'][:12]} · sourceHash(TSL) {L['new']['document_source_hash'] and L['new']['document_source_hash'][:12]} · {L['new']['document_pipeline']}")
        o.append('- diff samples (≤ 80 chars, internal):')
        for smp in L['diff_samples']:
            o.append(f"  - `{smp['old_id']}` {smp['status']} sim={smp['text_sim']} — OLD «{smp['old']}» → NEW «{smp['new']}» {smp['withheld_reasons'] or ''}")
        o.append('')
    return '\n'.join(o) + '\n'


def run(batch_dir, pipeline=None, out_dir=None):
    spec = common.load_json(f'{batch_dir}/batch-spec.json')
    man = common.load_json(f'{batch_dir}/run-manifest.json', {})
    pipeline = pipeline or spec['pipeline']
    packs = load_packs_main()
    lessons = [lesson_compare(batch_dir, pipeline, L, packs) for L in spec['lessons']]
    from datetime import datetime, timezone
    cmp_ = dict(version=COMPARE_VERSION, batch=spec['batch'], pipeline=pipeline, pipeline_code_sha=man.get('pipeline_code_sha'), tool_versions=man.get('versions'),
                generated=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                totals=dict(lessons=len(lessons), old_blocks=sum(L['old']['blocks'] for L in lessons), old_block_status=dict(sum((collections.Counter(L['old_block_status']) for L in lessons), collections.Counter())),
                            new_trusted=sum((L['new']['stats'] or {}).get('trusted', 0) for L in lessons), new_withheld=sum((L['new']['stats'] or {}).get('withheld', 0) for L in lessons),
                            new_version_class=dict(collections.Counter(L['new_version_class'] for L in lessons))),
                lessons=lessons)
    out_dir = out_dir or f'{batch_dir}/compare'
    pj = common.write_new_version(cmp_, f'{out_dir}/compare.json')
    pm = pj.replace('.json', '.md')
    with open(pm, 'w', encoding='utf-8') as f:
        f.write(render_md(cmp_))
    return cmp_, pj, pm


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--batch-dir', default=f'{common.LEGACY_OUT}/batch-1')
    ap.add_argument('--pipeline', default=None)
    a = ap.parse_args(argv)
    cmp_, pj, pm = run(a.batch_dir, a.pipeline)
    print(cmp_['totals']); print('→', pj, pm)
    return 0


if __name__ == '__main__':
    sys.exit(main())
