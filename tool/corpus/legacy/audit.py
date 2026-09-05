#!/usr/bin/env python3
"""Round 4 · Lane D — INDEPENDENT AUDIT tooling (page-render based; the annotator judges from the page, never
from the served text alone). Rows use the round-3 ft_audit schema so ft_audit_score.score_rows (Lane A code)
scores them unchanged; no threshold, no PASS/FAIL.

  sample-second   the ≥ 10 % second annotation of the ORIGINAL round-3 sample (484 rows, seed 20260905) —
                  a different seed, stratified, prioritising Toán · two-column · formula/number rows (pre-check
                  `hasMath`, an annotator-independent flag); annotator #1's verdicts are STRIPPED (blind)
  sample-new      trusted blocks + withheld regions of one batch's NEW Trusted Structured Lessons
  sample-old      OLD served blocks (units + pack activities) of the same lessons, same annotator → OLD vs NEW
  sheets          contact sheets: page crop at 170 dpi (bbox outlined, padded) + served text + mechanical hints
  annotate        merge a judgments JSON {sampleId: {field: value}} into a sample → annotated JSONL (+ append log)
  score           rates per group with Wilson 95 % CIs (ft_audit_score.score_rows) → JSON + md
  kappa           inter-annotator agreement per class (percent agreement + Cohen's κ on OK/WRONG rows)

    python3 tool/corpus/legacy/audit.py sample-second --seed 20260906 --n 54
    .venv-bakeoff/bin/python tool/corpus/legacy/audit.py sheets --sample <jsonl> --out-dir <dir>
    python3 tool/corpus/legacy/audit.py kappa --first poc-out/round3/ft-audit/annotated-20260905.jsonl --second <jsonl>
Outputs live under poc-out/round4/legacy/audit/ (internal, D4). Nothing is overwritten (versioned writes).
"""
import argparse
import collections
import json
import os
import random
import re
import sys
import textwrap
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))
import common  # noqa: E402

os.environ.setdefault('TC_ROOT', common.MAIN_ROOT)
import ft_audit_score as fscore  # noqa: E402  (Lane A-pipeline code, read-only use)

AUDIT_OUT = f'{common.LEGACY_OUT}/audit'
ANNOT_FIELDS = ('display_fidelity', 'teaching_critical_fidelity', 'reading_order', 'role_fidelity', 'lesson_attachment', 'false_trust')
EXTRA_FIELDS = ('notes', 'display_error_class', 'teaching_critical_class', 'reviewer', 'reviewedAt')
VALUES = ('OK', 'WRONG', 'UNSURE', 'NA')
CLASSES = ('display', 'teaching_critical', 'reading_order', 'role', 'attachment', 'false_trust')
CLASS_FIELD = dict(display='display_fidelity', teaching_critical='teaching_critical_fidelity', reading_order='reading_order', role='role_fidelity', attachment='lesson_attachment', false_trust='false_trust')
FONTS = ['/Library/Fonts/Arial Unicode.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf', '/System/Library/Fonts/Supplemental/Tahoma.ttf']
DIGIT_RUN = re.compile(r'(?<!\d)\d{1,3}(?:\s+\d{1,3}){1,}(?!\d)')


def read_jsonl(p):
    with open(p, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl(rows, p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return p


def versioned_jsonl(rows, p):
    if os.path.exists(p):
        base, ext = os.path.splitext(p); n = 2
        while os.path.exists(f'{base}.v{n}{ext}'):
            n += 1
        p = f'{base}.v{n}{ext}'
    return write_jsonl(rows, p)


def subject_group(row):
    s = row.get('subject') or common.subject_of(row.get('book') or '')
    if s == 'Toán':
        return 'Toán'
    if s == 'Tiếng Việt':
        return 'TV'
    if s in ('KHTN', 'Khoa học', 'Hoá học', 'Vật lí'):
        return 'Science'
    return 'Other'


# ---------------------------------------------------------------- sample-second
def second_strata(row):
    if row.get('family') == 'tslBai17':
        return 'TSL'
    g = subject_group(row)
    two = 'two_col' if row.get('layoutFamily') == 'two_col' else 'single'
    math = 'math' if (row.get('precheck') or {}).get('hasMath') else 'text'
    return f'{g}·{two}·{math}'


# priority allocation (rows) — Toán, two-column and math rows first; TSL stratum gets its own line
SECOND_PRIORITY = {'Toán·two_col·math': 12, 'Toán·two_col·text': 6, 'Toán·single·math': 6, 'Toán·single·text': 2,
                   'TV·two_col·text': 8, 'TV·two_col·math': 2, 'TV·single·text': 6, 'TV·single·math': 1,
                   'Science·two_col·text': 4, 'Science·two_col·math': 2, 'Science·single·text': 2, 'Science·single·math': 1,
                   'Other·two_col·text': 1, 'Other·single·text': 1, 'TSL': 4}


def sample_second(rows, seed, n, priority=SECOND_PRIORITY):
    rng = random.Random(seed)
    strata = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: r['sampleId']):
        if r.get('servedAsTrusted', True):
            strata[second_strata(r)].append(r)
    alloc = {}
    for k, rs in strata.items():
        alloc[k] = min(len(rs), priority.get(k, 0))
    # top up to n with the largest strata (deterministic order)
    total = sum(alloc.values())
    for k in sorted(strata, key=lambda k: -len(strata[k])):
        while total < n and alloc[k] < len(strata[k]):
            alloc[k] += 1; total += 1
    picked = []
    for k in sorted(strata):
        rs = list(strata[k]); rng.shuffle(rs)
        picked.extend(rs[:alloc[k]])
    picked.sort(key=lambda r: r['sampleId'])
    blind = []
    for r in picked:
        b = {k: v for k, v in r.items() if k not in ANNOT_FIELDS and k not in EXTRA_FIELDS}
        b['_second'] = dict(stratum=second_strata(r), seed=seed, first_annotated_file=os.path.basename(common.ROUND3_ANNOTATED))
        for f in ANNOT_FIELDS:
            b[f] = ''
        blind.append(b)
    return blind, dict(seed=seed, n=len(blind), requested=n, strata=dict(sorted((k, dict(size=len(v), picked=alloc[k])) for k, v in strata.items())))


# ---------------------------------------------------------------- sample-kind (targeted class sample)
def sample_kind(batch_dir, seed, kinds, per_lesson):
    """A QUOTA sample of one or more roles across a batch — for a class that role-proportional sampling
    under-samples (batch 1 drew 2 caption rows of 74, so the figure/caption class could not be measured).

    These rows are NOT a random sample of what the pipeline serves: they are a census-or-quota of one class,
    and the rate computed from them is the rate WITHIN that class, never a rate over the batch. The sample
    file records that, so it cannot later be pooled with the stratified sample by accident."""
    spec = common.load_json(f'{batch_dir}/batch-spec.json')
    P = spec['pipeline']
    rng = random.Random(seed)
    want = {k.strip() for k in kinds if k.strip()}
    rows = []
    for L in spec['lessons']:
        book, n = L['book'], int(L['lesson'])
        tsl = common.load_json(f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{P}/lessons/{book}/bai-{n:02d}.tsl.json')
        if not tsl:
            continue
        pool = [b for b in tsl['blocks'] if b['role']['value'] in want]
        rng.shuffle(pool)
        for b in sorted(pool[:per_lesson], key=lambda b: (b['page'], b['order'])):
            rows.append(dict(family='legacyNewKind', side='NEW', grade=int(book[:2]), book=book, lesson=n,
                             activityId=f'legacyNew:{P}:{book}:L{n}:p{b["page"]:03d}', kind=b['role']['value'], text=b['text'],
                             pagePdf=b['page'], pagePrinted=b.get('page_printed'), bbox=b['bbox'], tslBlockId=b['id'], tslStatus='TRUSTED',
                             roleConfidence=b['role'].get('confidence'), packVersion=P, servedAsTrusted=True,
                             source=dict(kind='tsl', tslBlockId=b['id'], bbox=b['bbox'], status='TRUSTED', reasons=[]),
                             subject=common.subject_of(book), precheck=dict(hasNumbers=bool(re.search(r'\d', b['text'] or '')), hasMath=False, multiLine=False)))
    for i, r in enumerate(rows):
        r['sampleId'] = f'k{seed}-{i:04d}'
        r['layoutFamily'] = None
        r['_kindSample'] = dict(kinds=sorted(want), seed=seed, per_lesson=per_lesson,
                                warning='quota sample of one class — rates from it are WITHIN-CLASS rates, never rates over the batch; do not pool with the stratified sample')
    return rows


# ---------------------------------------------------------------- sample-new / sample-old
def sample_new(batch_dir, seed, per_lesson, withheld_per_lesson):
    spec = common.load_json(f'{batch_dir}/batch-spec.json')
    P = spec['pipeline']
    rng = random.Random(seed)
    rows = []
    for L in spec['lessons']:
        book, n = L['book'], int(L['lesson'])
        tsl = common.load_json(f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{P}/lessons/{book}/bai-{n:02d}.tsl.json')
        if not tsl:
            continue
        aid = f'legacyNew:{P}:{book}:L{n}'
        by_role = collections.defaultdict(list)
        for b in tsl['blocks']:
            by_role[b['role']['value']].append(b)
        # stratified by role: proportional with floor 1, deterministic
        total = len(tsl['blocks']); take = min(per_lesson, total)
        chosen = []
        alloc = {r: max(1, round(take * len(bs) / max(1, total))) for r, bs in by_role.items()}
        for r in sorted(by_role):
            bs = sorted(by_role[r], key=lambda b: b['id']); rng.shuffle(bs)
            chosen.extend(bs[:alloc[r]])
        chosen = sorted(chosen, key=lambda b: (b['page'], b['order']))[:take + 3]
        # attachment is judged once per activityId (ft_audit_score): for a TSL the unit of attachment is the PAGE
        for b in chosen:
            rows.append(dict(family='legacyNew', side='NEW', grade=int(book[:2]), book=book, lesson=n, activityId=f'{aid}:p{b["page"]:03d}', kind=b['role']['value'], text=b['text'], pagePdf=b['page'], pagePrinted=b.get('page_printed'),
                             bbox=b['bbox'], tslBlockId=b['id'], tslStatus='TRUSTED', roleConfidence=b['role'].get('confidence'), packVersion=P, servedAsTrusted=True,
                             source=dict(kind='tsl', tslBlockId=b['id'], bbox=b['bbox'], status='TRUSTED', reasons=[]), subject=common.subject_of(book),
                             precheck=dict(hasNumbers=bool(re.search(r'\d', b['text'] or '')), hasMath=bool(DIGIT_RUN.search(b['text'] or '') or re.search(r'[+\-×:=]\s*\d|\d\s*[+\-×:=]', b['text'] or '')), multiLine=(b['bbox'][3] > 0.03) if b.get('bbox') else False)))
        ws = sorted(tsl['withheld'], key=lambda w: (w['page'], w['order']))
        rng.shuffle(ws)
        for w in sorted(ws[:withheld_per_lesson], key=lambda w: (w['page'], w['order'])):
            rows.append(dict(family='legacyNew', side='NEW', grade=int(book[:2]), book=book, lesson=n, activityId=f'{aid}:p{w["page"]:03d}', kind=w.get('role'), text=None, pagePdf=w['page'], pagePrinted=w.get('page_printed'),
                             bbox=w['bbox'], tslBlockId=w['id'], tslStatus=w.get('status', 'WITHHELD'), withheldReasons=w.get('reasons', []), packVersion=P, servedAsTrusted=False,
                             source=dict(kind='tsl', tslBlockId=w['id'], bbox=w['bbox'], status=w.get('status', 'WITHHELD'), reasons=w.get('reasons', [])), subject=common.subject_of(book)))
    for i, r in enumerate(rows):
        r['sampleId'] = f'n{seed}-{i:04d}'
        r['layoutFamily'] = None
    return rows


def sample_old(batch_dir, seed, per_lesson, exclude_ids=()):
    import compare  # noqa: E402  (Lane D)
    spec = common.load_json(f'{batch_dir}/batch-spec.json')
    packs = compare.load_packs_main()
    rng = random.Random(seed)
    rows = []
    for L in spec['lessons']:
        book, n = L['book'], int(L['lesson'])
        old = compare.old_blocks_for_lesson(book, n, packs)
        old = [o for o in old if o['id'] not in exclude_ids and o.get('text')]
        by_fam = collections.defaultdict(list)
        for o in old:
            by_fam[o['family']].append(o)
        take = min(per_lesson, len(old))
        chosen = []
        for fam in sorted(by_fam):
            os_ = sorted(by_fam[fam], key=lambda o: o['id']); rng.shuffle(os_)
            chosen.extend(os_[:max(1, round(take * len(os_) / max(1, len(old))))])
        for o in sorted(chosen, key=lambda o: (o.get('page_pdf') or 0, o['id']))[:take + 2]:
            aid = o['id'].rsplit(':', 1)[0] if o['family'] != 'samUnits' else f"samUnits:{o['id']}"
            rows.append(dict(family=o['family'], side='OLD', grade=int(book[:2]), book=book, lesson=n, activityId=aid, kind=(o['kind'] or '').lower(), text=o['text'], pagePdf=o.get('page_pdf'), pagePrinted=o.get('page_printed'),
                             bbox=o.get('bbox'), unitId=o['id'], packVersion='units+packs 20260905T0437Z', servedAsTrusted=True,
                             source=dict(kind='ocr-body', lineIndices=o.get('line_idx'), bbox=o.get('bbox'), coverage=o.get('line_coverage'), extraction=o.get('extraction')), subject=common.subject_of(book),
                             precheck=dict(hasNumbers=bool(re.search(r'\d', o['text'])), hasMath=bool(o.get('digit_run')), multiLine=len(o.get('line_idx') or []) >= 2, orderCrossesColumns=o.get('order_crosses_columns'))))
    for i, r in enumerate(rows):
        r['sampleId'] = f'o{seed}-{i:04d}'
        r['layoutFamily'] = None
    return rows


# ---------------------------------------------------------------- sheets
def _font(size):
    from PIL import ImageFont
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:  # noqa: BLE001
                continue
    return ImageFont.load_default()


def render_crop(book, pdf, bbox, dpi=170, pad_x=0.06, pad_y=0.035, full_page=False):
    import fitz
    from PIL import Image, ImageDraw
    path = common.pdf_path(book)
    if not path or not pdf:
        return None
    doc = fitz.open(path)
    if pdf < 1 or pdf > len(doc):
        return None
    pg = doc[pdf - 1]; r = pg.rect
    if bbox and not full_page:
        x, y, w, h = bbox
        x0, y0 = max(0.0, x - pad_x), max(0.0, y - pad_y); x1, y1 = min(1.0, x + w + pad_x), min(1.0, y + h + pad_y)
        clip = fitz.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)
        pm = pg.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False, clip=clip)
        img = Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
        d = ImageDraw.Draw(img)
        sx = pm.width / clip.width; sy = pm.height / clip.height
        bx0 = (r.x0 + x * r.width - clip.x0) * sx; by0 = (r.y0 + y * r.height - clip.y0) * sy
        d.rectangle([bx0, by0, bx0 + w * r.width * sx, by0 + h * r.height * sy], outline=(220, 0, 0), width=3)
    else:
        pm = pg.get_pixmap(dpi=110, colorspace=fitz.csRGB, alpha=False)
        img = Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
        if bbox:
            d = ImageDraw.Draw(img); x, y, w, h = bbox
            d.rectangle([x * pm.width, y * pm.height, (x + w) * pm.width, (y + h) * pm.height], outline=(220, 0, 0), width=3)
    doc.close()
    return img


def sheet_rows(rows, out_png, max_img_w=900, text_w=640, dpi=170):
    from PIL import Image, ImageDraw
    font = _font(19); small = _font(16); bold = _font(21)
    panels = []
    for r in rows:
        img = render_crop(r['book'], r.get('pagePdf'), (r.get('source') or {}).get('bbox') or r.get('bbox'), dpi=dpi)
        if img is None and r.get('crop') and os.path.exists(f"{common.MAIN_ROOT}/{r['crop']}"):
            img = Image.open(f"{common.MAIN_ROOT}/{r['crop']}").convert('RGB')
        if img is None:
            img = Image.new('RGB', (600, 80), (245, 245, 245))
        if img.width > max_img_w:
            img = img.resize((max_img_w, int(img.height * max_img_w / img.width)), Image.LANCZOS)
        head = f"{r['sampleId']} · {r.get('family')}/{r.get('kind')} · {common.book_label(r['book'])} Bài {r.get('lesson')} · pdf p{r.get('pagePdf')} (in {r.get('pagePrinted')})"
        status = r.get('tslStatus') or ('served' if r.get('servedAsTrusted', True) else 'withheld')
        hints = r.get('precheck') or {}
        hint = f"status {status} · hints: " + ', '.join(f'{k}={v}' for k, v in hints.items() if v not in (None, False, '')) + (f" · withheld reasons {r.get('withheldReasons')}" if r.get('withheldReasons') else '')
        served = r.get('text') if r.get('text') is not None else '(WITHHELD — no text served; judge whether the region is a safe rejection)'
        lines = [head, hint, '— served text —'] + textwrap.wrap(served, 62) or ['']
        text_h = 30 + 24 * len(lines)
        h = max(img.height, text_h) + 20
        panel = Image.new('RGB', (img.width + text_w + 30, h), (255, 255, 255))
        panel.paste(img, (10, 10))
        d = ImageDraw.Draw(panel)
        y = 10
        for i, ln in enumerate(lines):
            f = bold if i == 0 else (small if i in (1, 2) else font)
            d.text((img.width + 20, y), ln, fill=(0, 0, 0) if i not in (1, 2) else (90, 90, 90), font=f)
            y += 24
        panels.append(panel)
    W = max(p.width for p in panels) + 10
    H = sum(p.height + 12 for p in panels) + 10
    canvas = Image.new('RGB', (W, H), (200, 200, 200))
    y = 5
    for p in panels:
        canvas.paste(p, (5, y)); y += p.height + 12
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    canvas.save(out_png)
    return out_png


def make_sheets(rows, out_dir, per_sheet=4, dpi=170):
    index = []
    for i in range(0, len(rows), per_sheet):
        batch = rows[i:i + per_sheet]
        p = f'{out_dir}/sheet-{i // per_sheet:03d}.png'
        sheet_rows(batch, p, dpi=dpi)
        index.append(dict(sheet=os.path.basename(p), sampleIds=[r['sampleId'] for r in batch]))
    common.dump_json(index, f'{out_dir}/sheet-index.json')
    return index


# ---------------------------------------------------------------- annotate / score / kappa
def annotate(rows, judgments, reviewer, log_path=None):
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    out = []
    missing = []
    for r in rows:
        j = judgments.get(r['sampleId'])
        if not j:
            missing.append(r['sampleId']); out.append(r); continue
        r = dict(r)
        for f in ANNOT_FIELDS:
            v = (j.get(f) or '').strip().upper()
            if v and v not in VALUES:
                raise ValueError(f'{r["sampleId"]}: {f}={v!r} not in {VALUES}')
            r[f] = v
        for f in ('notes', 'display_error_class', 'teaching_critical_class'):
            r[f] = j.get(f, '')
        r['reviewer'] = reviewer; r['reviewedAt'] = now
        out.append(r)
        if log_path:
            with open(log_path, 'a', encoding='utf-8') as lf:
                lf.write(json.dumps(dict(sampleId=r['sampleId'], reviewer=reviewer, reviewedAt=now, **{f: r[f] for f in ANNOT_FIELDS}, notes=r['notes']), ensure_ascii=False) + '\n')
    return out, missing


def score(rows, group_key):
    res = fscore.score_rows(rows, group_key=group_key)
    return res


def kappa(first_rows, second_rows):
    """Per class: n both judged (OK/WRONG on both sides), percent agreement, Cohen's κ, confusion, and how often
    one side said NA/UNSURE where the other judged."""
    f = {r['sampleId']: r for r in first_rows}
    out = {}
    for cls, field in CLASS_FIELD.items():
        conf = collections.Counter(); na_mismatch = 0; both = 0; agree = 0
        for s in second_rows:
            a = f.get(s['sampleId'])
            if not a:
                continue
            v1 = (a.get(field) or '').strip().upper(); v2 = (s.get(field) or '').strip().upper()
            if v1 in ('OK', 'WRONG') and v2 in ('OK', 'WRONG'):
                both += 1; conf[(v1, v2)] += 1; agree += (v1 == v2)
            elif (v1 in ('OK', 'WRONG')) != (v2 in ('OK', 'WRONG')) and (v1 or v2):
                na_mismatch += 1
        if both:
            p1w = (conf[('WRONG', 'OK')] + conf[('WRONG', 'WRONG')]) / both; p2w = (conf[('OK', 'WRONG')] + conf[('WRONG', 'WRONG')]) / both
            pe = p1w * p2w + (1 - p1w) * (1 - p2w); po = agree / both
            k = None if pe >= 1.0 else round((po - pe) / (1 - pe), 3)
        else:
            po = None; k = None; p1w = p2w = None
        out[cls] = dict(field=field, n_both_judged=both, agreement=(round(po, 3) if po is not None else None), kappa=k, first_wrong_rate=(round(p1w, 3) if p1w is not None else None),
                        second_wrong_rate=(round(p2w, 3) if p2w is not None else None), confusion={f'{a}/{b}': c for (a, b), c in sorted(conf.items())}, na_or_unsure_mismatch=na_mismatch)
    # derived false trust (5 criteria) on both sides
    fscore.score_rows([dict(r) for r in first_rows]); fscore.score_rows([dict(r) for r in second_rows])
    return out


def kappa_md(k, n_second, seed, first_reviewer, second_reviewer):
    o = [f'# Second annotation — inter-annotator agreement (n = {n_second} rows, seed {seed})\n', f'annotator #1: {first_reviewer} · annotator #2: {second_reviewer} · κ = Cohen\'s kappa on rows both judged OK/WRONG (NA/UNSURE excluded, counted beside)\n',
         '| class | n both judged | agreement | κ | #1 WRONG rate | #2 WRONG rate | confusion (#1/#2) | NA/UNSURE mismatch |', '|---|---|---|---|---|---|---|---|']
    for cls, v in k.items():
        o.append(f"| {cls} | {v['n_both_judged']} | {v['agreement']} | {v['kappa']} | {v['first_wrong_rate']} | {v['second_wrong_rate']} | {v['confusion']} | {v['na_or_unsure_mismatch']} |")
    return '\n'.join(o) + '\n'


def score_md(res, title):
    o = [f'# {title}\n', 'rates = WRONG / (OK + WRONG) judged served rows · Wilson 95 % · unsure / NA beside · no threshold applied\n',
         '| group | blocks (acts) | display | teaching-critical | reading order | role | attachment (act.) | false trust (derived 5) | — teaching-critical FT | — display-only | — other | annotator FT |', '|---|---|---|---|---|---|---|---|---|---|---|---|']

    def f(x):
        return f"{x['wrong']}/{x['judged']} = {x['rate']:.3f} [{x['lo']:.3f}, {x['hi']:.3f}]" if x['judged'] else f"—/{x['judged']}"
    for g, v in res.items():
        if g.startswith('_'):
            continue
        o.append(f"| {g} | {v['blocks']} ({v['activities']}) | {f(v['display_only_fidelity'])} | {f(v['teaching_critical_fidelity'])} (NA {v['teaching_critical_fidelity']['na']}) | {f(v['reading_order'])} | {f(v['role_fidelity'])} | {f(v['lesson_attachment'])} | **{f(v['false_trust_derived'])}** | {f(v['false_trust_teaching_critical'])} | {f(v['false_trust_display_only'])} | {f(v['false_trust_other'])} | {f(v['false_trust_reviewer'])} |")
    o.append(f"\nwithheld rows reviewed: {res.get('_withheld_reviewed')}\n")
    return '\n'.join(o) + '\n'


# ---------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sample-second'); s.add_argument('--seed', type=int, default=20260906); s.add_argument('--n', type=int, default=54); s.add_argument('--first', default=common.ROUND3_ANNOTATED); s.add_argument('--out-dir', default=f'{AUDIT_OUT}/second-annotation')
    s = sub.add_parser('sample-new'); s.add_argument('--batch-dir', default=f'{common.LEGACY_OUT}/batch-1'); s.add_argument('--seed', type=int, default=20260906); s.add_argument('--per-lesson', type=int, default=12); s.add_argument('--withheld-per-lesson', type=int, default=5); s.add_argument('--out-dir', default=None)
    s = sub.add_parser('sample-old'); s.add_argument('--batch-dir', default=f'{common.LEGACY_OUT}/batch-1'); s.add_argument('--seed', type=int, default=20260906); s.add_argument('--per-lesson', type=int, default=10); s.add_argument('--out-dir', default=None)
    s = sub.add_parser('sample-kind'); s.add_argument('--batch-dir', default=f'{common.LEGACY_OUT}/batch-1'); s.add_argument('--seed', type=int, default=20260906); s.add_argument('--kinds', required=True, help='comma list of TSL roles, e.g. caption'); s.add_argument('--per-lesson', type=int, default=8); s.add_argument('--out-dir', default=None)
    s = sub.add_parser('sheets'); s.add_argument('--sample', required=True); s.add_argument('--out-dir', required=True); s.add_argument('--per-sheet', type=int, default=4); s.add_argument('--dpi', type=int, default=170)
    s = sub.add_parser('annotate'); s.add_argument('--sample', required=True); s.add_argument('--judgments', required=True); s.add_argument('--out', required=True); s.add_argument('--reviewer', required=True); s.add_argument('--log', default=None)
    s = sub.add_parser('score'); s.add_argument('--annotated', required=True); s.add_argument('--group', default='lesson', choices=['lesson', 'family', 'side', 'subject', 'kind']); s.add_argument('--out', required=True); s.add_argument('--title', default='audit scores')
    s = sub.add_parser('kappa'); s.add_argument('--first', default=common.ROUND3_ANNOTATED); s.add_argument('--second', required=True); s.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    if a.cmd == 'sample-second':
        rows = read_jsonl(a.first)
        blind, man = sample_second(rows, a.seed, a.n)
        man.update(source=a.first, source_sha256=common.sha256_file(a.first), generated=datetime.now(timezone.utc).isoformat(timespec='seconds'), blind='annotator #1 verdicts stripped from the sample rows')
        p = versioned_jsonl(blind, f'{a.out_dir}/sample-{a.seed}.jsonl'); common.write_new_version(man, f'{a.out_dir}/manifest-{a.seed}.json')
        print(json.dumps(man['strata'], ensure_ascii=False)); print(f'{len(blind)} rows → {p}')
    elif a.cmd == 'sample-new':
        rows = sample_new(a.batch_dir, a.seed, a.per_lesson, a.withheld_per_lesson)
        p = versioned_jsonl(rows, f'{a.out_dir or (a.batch_dir + "/audit")}/new-sample-{a.seed}.jsonl')
        print(f'{len(rows)} rows ({sum(1 for r in rows if r["servedAsTrusted"])} trusted, {sum(1 for r in rows if not r["servedAsTrusted"])} withheld) → {p}')
    elif a.cmd == 'sample-old':
        rows = sample_old(a.batch_dir, a.seed, a.per_lesson)
        p = versioned_jsonl(rows, f'{a.out_dir or (a.batch_dir + "/audit")}/old-sample-{a.seed}.jsonl')
        print(f'{len(rows)} rows → {p}')
    elif a.cmd == 'sample-kind':
        kinds = a.kinds.split(',')
        rows = sample_kind(a.batch_dir, a.seed, kinds, a.per_lesson)
        p = versioned_jsonl(rows, f'{a.out_dir or (a.batch_dir + "/audit")}/kind-sample-{"-".join(sorted(k.strip() for k in kinds))}-{a.seed}.jsonl')
        print(f'{len(rows)} rows of kinds {sorted(k.strip() for k in kinds)} → {p} (WITHIN-CLASS rates only)')
    elif a.cmd == 'sheets':
        rows = read_jsonl(a.sample)
        idx = make_sheets(rows, a.out_dir, a.per_sheet, a.dpi)
        print(f'{len(idx)} sheets → {a.out_dir}')
    elif a.cmd == 'annotate':
        rows = read_jsonl(a.sample); j = common.load_json(a.judgments)
        out, missing = annotate(rows, j, a.reviewer, a.log)
        p = versioned_jsonl(out, a.out)
        print(f'{len(out) - len(missing)} annotated, {len(missing)} missing → {p}')
        if missing:
            print('missing:', missing)
    elif a.cmd == 'score':
        rows = read_jsonl(a.annotated)
        key = {'lesson': lambda r: f"{common.book_label(r['book'])} Bài {r['lesson']}", 'family': lambda r: r.get('family'), 'side': lambda r: r.get('side') or r.get('family'), 'subject': lambda r: r.get('subject'), 'kind': lambda r: f"{r.get('side') or r.get('family')}/{r.get('kind')}"}[a.group]
        res = score(rows, key)
        p = common.write_new_version(dict(title=a.title, source=a.annotated, source_sha256=common.sha256_file(a.annotated), group=a.group, results=res), a.out)
        with open(p.replace('.json', '.md'), 'w', encoding='utf-8') as f:
            f.write(score_md(res, a.title))
        print(score_md(res, a.title))
    elif a.cmd == 'kappa':
        first = read_jsonl(a.first); second = read_jsonl(a.second)
        k = kappa(first, second)
        seed = (second[0].get('_second') or {}).get('seed') if second else None
        p = common.write_new_version(dict(first=a.first, second=a.second, n_second=len(second), seed=seed, per_class=k), a.out)
        md = kappa_md(k, len(second), seed, first[0].get('reviewer') if first else '?', second[0].get('reviewer') if second else '?')
        with open(p.replace('.json', '.md'), 'w', encoding='utf-8') as f:
            f.write(md)
        print(md)
    return 0


if __name__ == '__main__':
    sys.exit(main())
