#!/usr/bin/env python3
"""WAL-210 item 10a (Founder D3) — FALSE-TRUST AUDIT: reproducible stratified sample of the EXACT
content that ships in the DEFAULT packs, expanded to the source blocks it was built from, with an
annotation sheet for an independent reviewer. Research/tooling only: no threshold is decided here,
and this script never annotates anything.

Population (the "frame"): every block a child would read from `assets/pack/lesson-index-g<N>.json`
(packs must carry a non-experimental `buildProvenance`, else the run refuses): khoaExperiments
(title / Chuẩn bị / each Tiến hành step / Dự đoán / Quan sát), tvReadings (passage + each question),
tvWritings (prompt), suSources (excerpt + attribution — samGloss is SAM's own text, not sampled),
toanExercises (expression), diaMaps (caption + questions), sourceAssets (printed caption), and — as a
separate family with its own denominator — samUnits (`assets/pack/sam-units.db`, the grounding store).
Every block is linked back to its source: OCR-body page + matched line span + bbox
(poc-out/graph/ocr-body), the TC-v2 SDM block on the same page where the six Science books overlap
(poc-out/trusted-corpus/tc-v2/tc2-p1/sdm), and the TV5 unit id for units-derived text.

Mandatory first stratum (Founder addendum 2026-09-05): KHTN 6 Bài 17 «Tách chất khỏi hỗn hợp» —
every shipped default-pack activity of that lesson (measured: none today) PLUS every block of its
TC-v2 Trusted Structured Lesson (read-only, `lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json`),
listed first in the sheet.

Sampling: strata = (family, book); allocation proportional to stratum size with a floor per stratum;
selection by `random.Random(seed)` over a deterministically ordered population, so the same seed
always yields the same sample. Blocks are the sampling unit (the rates are defined on blocks); the
sheet groups them by activity for the reviewer.

Outputs (all under --out, default poc-out/b-lane/ft-audit/ — INTERNAL / RESEARCH ONLY per D4,
verbatim text and page crops never leave poc-out):
  sample-<seed>.jsonl     one row per sampled block, annotation fields empty
  sample-<seed>.md        the readable sheet (Bài 17 first) with crop paths
  manifest-<seed>.json    population per stratum, allocation, pack provenance, seed
  crops/<sampleId>.png    page crop around the block (PyMuPDF), red box = matched region
  pages/<book>-pNNN.png   full page render for context

Annotation fields per block (values OK | WRONG | UNSURE | NA), scored by ft_audit_score.py:
  display_fidelity            the served text matches the page render character-for-character
                              (tone marks, enumerators, no spliced text from another box)
  teaching_critical_fidelity  numbers / formulas / units / terms / negations are correct
  role_fidelity               the block is served in the right role (question vs instruction vs
                              objective vs sidebar vs answer vs body/passage)
  lesson_attachment           the activity is attached to the right lesson (judged once per activity)
  false_trust                 reviewer's overall verdict: served as trusted content but wrong in a
                              way that would mislead a learner (the scorer ALSO derives it from the
                              four criteria; both are reported)

Usage (from the repo root of the main checkout, where poc-out/ and assets/pack/ live):
  python3 tool/corpus/ft_audit_sample.py --seed 20260905 --n 400 [--min-per-stratum 3] [--no-crops]
  python3 tool/corpus/ft_audit_sample.py --frame-only        # population census, no sample
"""
import argparse
import collections
import difflib
import glob
import json
import os
import random
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime, timezone

ROOT = os.environ.get('TC_ROOT', os.getcwd())
PACK_DIR = 'assets/pack'
OCR = 'poc-out/graph/ocr-body'
UNITS = 'poc-out/units'
TC2 = 'poc-out/trusted-corpus/tc-v2/tc2-p1'
PDF = 'poc-out/pdf'
SHOWCASE = dict(book='06-sgk-khoa-hoc-tu-nhien-6', lesson=17, tsl=f'{TC2}/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json', label='KHTN 6 Bài 17 «Tách chất khỏi hỗn hợp»')
FAMILIES = ('khoaExperiments', 'tvReadings', 'tvWritings', 'suSources', 'toanExercises', 'diaMaps', 'sourceAssets', 'samUnits')
ANNOT = ('display_fidelity', 'teaching_critical_fidelity', 'role_fidelity', 'lesson_attachment', 'false_trust')
VALUES = ('OK', 'WRONG', 'UNSURE', 'NA')
SCRIPT_VERSION = 'ft_audit_sample.py@2026-09-05'


# ---------------------------------------------------------------- text helpers
def norm(t):
    t = unicodedata.normalize('NFC', (t or '')).lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', t)).strip()


def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a in b or b in a:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


# ---------------------------------------------------------------- source loaders (cached)
_ocr = {}


def ocr_lines(book, pdf):
    k = (book, pdf)
    if k not in _ocr:
        p = f'{ROOT}/{OCR}/{book}/p{pdf:03d}.json'
        _ocr[k] = json.load(open(p))['lines'] if os.path.exists(p) else []
    return _ocr[k]


_sdm = {}


def sdm_blocks(book, pdf):
    k = (book, pdf)
    if k not in _sdm:
        p = f'{ROOT}/{TC2}/sdm/{book}/p{pdf:03d}.sdm.json'
        _sdm[k] = [b for b in json.load(open(p))['blocks'] if b.get('text')] if os.path.exists(p) else None
    return _sdm[k]


_units = {}


def units_of(book):
    if book not in _units:
        p = f'{ROOT}/{UNITS}/{book}.json'
        _units[book] = json.load(open(p))['units'] if os.path.exists(p) else []
    return _units[book]


def unit_for_text(book, text, printed=None):
    """The TV5 unit whose text equals the served text (exact after normalisation, else best ≥ 0.9)."""
    best, br = None, 0.0
    key = norm(text)
    for u in units_of(book):
        if printed is not None and u.get('pagePrinted') not in (None, printed) and abs((u.get('pagePrinted') or 0) - printed) > 2:
            continue
        r = 1.0 if norm(u['text']) == key else sim(u['text'], text)
        if r > br:
            best, br = u, r
            if r == 1.0:
                break
    return (best, br) if best is not None and br >= 0.9 else (None, br)


# ---------------------------------------------------------------- source linking
def link_lines(book, pdf, text):
    """Matched OCR lines for a served text on a page: line i matches when its normalised text (≥ 4 chars)
    is a substring of the served text, or the served text is a substring of the line. Returns
    (indices, bbox_union, coverage) where coverage = matched chars / served chars (capped at 1)."""
    lines = ocr_lines(book, pdf)
    key = norm(text)
    if not lines or not key:
        return [], None, 0.0
    idx = []
    for i, l in enumerate(lines):
        lk = norm(l.get('text', ''))
        if len(lk) >= 4 and (lk in key or key in lk):
            idx.append(i)
    if not idx and len(key) >= 12:
        # short OCR fragments / tone slips: accept lines whose similarity to a window of the text is high
        for i, l in enumerate(lines):
            lk = norm(l.get('text', ''))
            if len(lk) >= 8 and difflib.SequenceMatcher(None, lk, key[:max(len(lk) * 2, 40)]).ratio() >= 0.85:
                idx.append(i)
    if not idx:
        return [], None, 0.0
    xs0 = min(lines[i]['x'] for i in idx); ys0 = min(lines[i]['y'] for i in idx)
    xs1 = max(lines[i]['x'] + lines[i]['w'] for i in idx); ys1 = max(lines[i]['y'] + lines[i]['h'] for i in idx)
    covered = sum(len(norm(lines[i]['text'])) for i in idx)
    return idx, [round(xs0, 4), round(ys0, 4), round(xs1 - xs0, 4), round(ys1 - ys0, 4)], round(min(1.0, covered / max(1, len(key))), 3)


def link_sdm(book, pdf, text):
    blocks = sdm_blocks(book, pdf)
    if not blocks:
        return None
    best = max(blocks, key=lambda b: sim(text, b['text']))
    r = sim(text, best['text'])
    if r < 0.5:
        return dict(matched=False, ratio=round(r, 2))
    return dict(matched=True, ratio=round(r, 2), id=best['id'], role=best['role']['value'], trust=best['trust']['status'], reasons=best['trust'].get('reasons', []), bbox=best.get('bbox'))


# ---------------------------------------------------------------- population (frame)
def blocks_of_pack(pack, grade):
    """Yield served-block records for one pack."""
    out = []

    def add(family, act_id, kind, text, book, lesson, pdf, printed, extra=None):
        if not text or not str(text).strip():
            return
        out.append(dict(family=family, grade=grade, book=book, lesson=lesson, activityId=act_id, kind=kind, text=str(text).strip(),
                        pagePdf=pdf, pagePrinted=printed, **(extra or {})))

    for i, e in enumerate(pack.get('khoaExperiments', [])):
        aid = f"khoaExperiments:{e['book']}:p{e['pagePdf']:03d}:{i}"
        add('khoaExperiments', aid, 'title', e.get('title'), e['book'], e.get('lesson'), e['pagePdf'], e.get('page'))
        add('khoaExperiments', aid, 'chuanBi', e.get('chuanBi'), e['book'], e.get('lesson'), e['pagePdf'], e.get('page'))
        for j, s in enumerate(e.get('tienHanh') or []):
            add('khoaExperiments', aid, f'step{j + 1}', s, e['book'], e.get('lesson'), e['pagePdf'], e.get('page'))
        add('khoaExperiments', aid, 'duDoan', e.get('duDoan'), e['book'], e.get('lesson'), e['pagePdf'], e.get('page'))
        add('khoaExperiments', aid, 'quanSat', e.get('quanSat'), e['book'], e.get('lesson'), e['pagePdf'], e.get('page'))
    for i, r in enumerate(pack.get('tvReadings', [])):
        if str(r.get('source', '')).startswith('pattern-router'):
            continue
        u, ratio = unit_for_text(r['book'], r['passage'], r.get('page'))
        pdf = u['pagePdf'] if u else None
        aid = f"tvReadings:{r['book']}:L{r['lesson']}:{i}"
        add('tvReadings', aid, 'passage', r['passage'], r['book'], r['lesson'], pdf, r.get('page'), dict(unitId=u['id'] if u else None, unitMatch=round(ratio, 2)))
        for j, q in enumerate(r.get('questions', [])):
            uq, rq = unit_for_text(r['book'], q['prompt'], q.get('page'))
            add('tvReadings', aid, f'question{j + 1}', q['prompt'], r['book'], r['lesson'], uq['pagePdf'] if uq else pdf, q.get('page'), dict(unitId=uq['id'] if uq else None, unitMatch=round(rq, 2)))
    for i, w in enumerate(pack.get('tvWritings', [])):
        if str(w.get('source', '')).startswith('pattern-router'):
            continue
        u, ratio = unit_for_text(w['book'], w['prompt'], w.get('page'))
        add('tvWritings', f"tvWritings:{w['book']}:L{w['lesson']}:{i}", 'prompt', w['prompt'], w['book'], w['lesson'], u['pagePdf'] if u else None, w.get('page'), dict(unitId=u['id'] if u else None, unitMatch=round(ratio, 2)))
    for i, s in enumerate(pack.get('suSources', [])):
        aid = f"suSources:{s['book']}:p{s['pagePdf']:03d}:{i}"
        add('suSources', aid, 'excerpt', s.get('excerpt'), s['book'], s.get('lesson'), s['pagePdf'], s.get('page'))
        add('suSources', aid, 'attribution', s.get('attribution'), s['book'], s.get('lesson'), s['pagePdf'], s.get('page'))
    exmap = []
    p = f'{ROOT}/{UNITS}/exercise-case-map.json'
    if os.path.exists(p):
        e = json.load(open(p)); exmap = e if isinstance(e, list) else e.get('items', [])
    for les, lst in pack.get('toanExercises', {}).items():
        for i, x in enumerate(lst):
            src = next((m for m in exmap if m.get('book') == x.get('book') and m.get('expr') == x.get('expr') and m.get('printed') == x.get('page')), None)
            add('toanExercises', f"toanExercises:{x.get('book')}:L{les}:{i}", 'expr', x.get('expr'), x.get('book'), int(les), src.get('page') if src else None, x.get('page'), dict(skillCaseId=x.get('skillCaseId'), method=src.get('method') if src else None))
    for i, m in enumerate(pack.get('diaMaps', [])):
        aid = f"diaMaps:{m['book']}:{i}"
        add('diaMaps', aid, 'caption', m.get('caption'), m['book'], None, m.get('pagePdf'), m.get('page'), dict(asset=m.get('asset')))
        for j, q in enumerate(m.get('questions', [])):
            add('diaMaps', aid, f'question{j + 1}', q, m['book'], None, m.get('pagePdf'), m.get('page'), dict(asset=m.get('asset')))
    for i, a in enumerate(pack.get('sourceAssets', [])):
        if a.get('printedCaption'):
            add('sourceAssets', f"sourceAssets:{a['asset']}", 'caption', a['printedCaption'], a.get('sourceDocumentId'), a.get('lesson'), a.get('pagePdf'), a.get('pagePrinted'), dict(asset=a['asset']))
    return out


def blocks_of_sam_units():
    p = f'{ROOT}/{PACK_DIR}/sam-units.db'
    if not os.path.exists(p):
        return []
    c = sqlite3.connect(p)
    out = []
    for uid, book, grade, vol, lesson, role, page, text in c.execute('select id, book, grade, vol, lesson, role, page, text from unit order by id'):
        m = re.search(r':p(\d{3}):', uid)
        out.append(dict(family='samUnits', grade=grade, book=book, lesson=lesson, activityId=f'samUnits:{uid}', kind=role.lower(), text=text, pagePdf=int(m.group(1)) if m else None, pagePrinted=page, unitId=uid))
    return out


def blocks_of_showcase():
    """Every block of the KHTN 6 Bài 17 TSL (read-only). Trusted blocks carry text; withheld ones carry
    only their reason (text is fail-closed in the TSL) and are listed for context."""
    p = f'{ROOT}/{SHOWCASE["tsl"]}'
    if not os.path.exists(p):
        return []
    t = json.load(open(p))
    out = []
    for b in t.get('blocks', []):
        out.append(dict(family='tslBai17', grade=6, book=t['book'], lesson=t['lesson'], activityId=f"tsl:{t['book']}:L{t['lesson']}:p{b['page']:03d}", kind=b['role']['value'], text=b.get('text'),
                        pagePdf=b['page'], pagePrinted=b.get('page_printed'), tslBlockId=b['id'], tslStatus='TRUSTED', bbox=b.get('bbox'), roleConfidence=b['role'].get('confidence')))
    for b in t.get('withheld', []):
        out.append(dict(family='tslBai17', grade=6, book=t['book'], lesson=t['lesson'], activityId=f"tsl:{t['book']}:L{t['lesson']}:p{b['page']:03d}", kind=b.get('role'), text=None,
                        pagePdf=b['page'], pagePrinted=b.get('page_printed'), tslBlockId=b['id'], tslStatus=b.get('status', 'WITHHELD'), withheldReasons=b.get('reasons', []), bbox=b.get('bbox')))
    return out


def load_packs(allow_experimental=False):
    packs, prov = {}, {}
    for g in range(1, 13):
        p = f'{ROOT}/{PACK_DIR}/lesson-index-g{g}.json'
        if not os.path.exists(p):
            continue
        pk = json.load(open(p))
        bp = pk.get('buildProvenance')
        if not bp:
            raise SystemExit(f'{p}: no buildProvenance — build the packs with the WAL-210 builder first')
        if bp.get('experimental') and not allow_experimental:
            raise SystemExit(f'{p}: experimental build ({bp.get("packVersion")}) — the audit samples DEFAULT packs only')
        packs[g] = pk; prov[g] = dict(packVersion=bp['packVersion'], contentHash=bp['contentHash'], builderVersion=bp['builderVersion'], gitSha=bp['gitSha'], flags=bp['flags'])
    return packs, prov


# ---------------------------------------------------------------- rendering (internal only, D4)
def pdf_path(book):
    for p in (f'{ROOT}/{PDF}/{book[:2]}/{book}.pdf', f'{ROOT}/{PDF}/{book}.pdf'):
        if os.path.exists(p):
            return p
    return None


_docs = {}


def render_crop(book, pdf, bbox, out_png, dpi=110, pad=0.03):
    import fitz
    path = pdf_path(book)
    if not path:
        return None
    if book not in _docs:
        _docs[book] = fitz.open(path)
    doc = _docs[book]
    if pdf is None or pdf < 1 or pdf > len(doc):
        return None
    pg = doc[pdf - 1]; r = pg.rect
    clip = None
    if bbox:
        x, y, w, h = bbox
        x0, y0 = max(0.0, x - pad), max(0.0, y - pad); x1, y1 = min(1.0, x + w + pad), min(1.0, y + h + pad)
        clip = fitz.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    pm = pg.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False, clip=clip)
    if bbox:
        from PIL import Image, ImageDraw
        img = Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
        d = ImageDraw.Draw(img)
        sx = pm.width / (clip.width); sy = pm.height / (clip.height)
        bx0 = (r.x0 + bbox[0] * r.width - clip.x0) * sx; by0 = (r.y0 + bbox[1] * r.height - clip.y0) * sy
        bx1 = bx0 + bbox[2] * r.width * sx; by1 = by0 + bbox[3] * r.height * sy
        d.rectangle([bx0, by0, bx1, by1], outline=(220, 0, 0), width=3)
        img.save(out_png)
    else:
        pm.save(out_png)
    return out_png


def render_page(book, pdf, out_png, dpi=90):
    return render_crop(book, pdf, None, out_png, dpi=dpi)


# ---------------------------------------------------------------- sampling
def allocate(strata, n, floor):
    """Proportional allocation with a per-stratum floor (capped at stratum size); deterministic."""
    total = sum(strata.values())
    alloc = {}
    for k, size in sorted(strata.items()):
        alloc[k] = min(size, max(floor, round(n * size / max(1, total))))
    return alloc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=20260905)
    ap.add_argument('--n', type=int, default=400, help='target sampled blocks (pack families + samUnits); the showcase stratum is added in full')
    ap.add_argument('--min-per-stratum', type=int, default=3)
    ap.add_argument('--out', default='poc-out/b-lane/ft-audit')
    ap.add_argument('--no-crops', action='store_true')
    ap.add_argument('--no-sam-units', action='store_true')
    ap.add_argument('--frame-only', action='store_true')
    ap.add_argument('--allow-experimental', action='store_true')
    a = ap.parse_args()
    out = f'{ROOT}/{a.out}' if not os.path.isabs(a.out) else a.out
    os.makedirs(out, exist_ok=True)

    packs, prov = load_packs(a.allow_experimental)
    frame = []
    seen_assets = set()
    for g, pk in sorted(packs.items()):
        for b in blocks_of_pack(pk, g):
            if b['family'] == 'sourceAssets':          # the same assets ship in every grade's pack — count each once
                if b['activityId'] in seen_assets:
                    continue
                seen_assets.add(b['activityId'])
            frame.append(b)
    if not a.no_sam_units:
        frame += blocks_of_sam_units()
    showcase_acts = [b for b in frame if b['book'] == SHOWCASE['book'] and b['lesson'] == SHOWCASE['lesson'] and b['family'] != 'samUnits']
    showcase_tsl = blocks_of_showcase()
    frame.sort(key=lambda b: (b['family'], b['book'], b['lesson'] if b['lesson'] is not None else -1, b['pagePdf'] or 0, b['activityId'], b['kind']))
    for i, b in enumerate(frame):
        b['frameIndex'] = i
    strata = collections.Counter((b['family'], b['book']) for b in frame)
    census = dict(blocks=len(frame), activities=len({b['activityId'] for b in frame}), byFamily=dict(collections.Counter(b['family'] for b in frame)),
                  byStratum={f'{f}|{bk}': n for (f, bk), n in sorted(strata.items())},
                  showcase=dict(label=SHOWCASE['label'], shippedActivities=len({b['activityId'] for b in showcase_acts}), shippedBlocks=len(showcase_acts),
                                tslBlocks=len(showcase_tsl), tslTrusted=sum(1 for b in showcase_tsl if b['tslStatus'] == 'TRUSTED'), tslWithheld=sum(1 for b in showcase_tsl if b['tslStatus'] != 'TRUSTED')))
    manifest = dict(script=SCRIPT_VERSION, createdAt=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), seed=a.seed, targetN=a.n, minPerStratum=a.min_per_stratum,
                    packs=prov, population=census, notice='INTERNAL / RESEARCH ONLY (Founder D4): verbatim SGK text and page crops stay in poc-out/; never commit or redistribute.')
    if a.frame_only:
        json.dump(manifest, open(f'{out}/frame-census.json', 'w'), ensure_ascii=False, indent=1)
        print(json.dumps(census, ensure_ascii=False, indent=1))
        return

    rng = random.Random(a.seed)
    alloc = allocate(strata, a.n, a.min_per_stratum)
    by_stratum = collections.defaultdict(list)
    for b in frame:
        by_stratum[(b['family'], b['book'])].append(b)
    sampled = []
    for k in sorted(by_stratum):
        pool = by_stratum[k]
        pick = rng.sample(range(len(pool)), alloc[k])
        sampled += [pool[i] for i in sorted(pick)]
    # mandatory showcase stratum: all shipped Bài 17 activity blocks + all TSL blocks, listed first
    mandatory = [dict(b, mandatory=True) for b in showcase_acts if b not in sampled] + [dict(b, mandatory=True) for b in showcase_tsl]
    rows = mandatory + [dict(b, mandatory=(b['book'] == SHOWCASE['book'] and b['lesson'] == SHOWCASE['lesson'])) for b in sampled]
    manifest['allocation'] = {f'{f}|{bk}': n for (f, bk), n in sorted(alloc.items())}
    manifest['sampled'] = dict(total=len(rows), fromFrame=len(sampled), showcaseActivityBlocks=len(showcase_acts), showcaseTslBlocks=len(showcase_tsl))

    # source linking + crops
    os.makedirs(f'{out}/crops', exist_ok=True); os.makedirs(f'{out}/pages', exist_ok=True)
    pages_done = set()
    for i, r in enumerate(rows):
        r['sampleId'] = f's{a.seed}-{i:04d}'
        r['packVersion'] = prov.get(r['grade'], {}).get('packVersion') if r['family'] != 'tslBai17' else 'tc2-p1'
        r['servedAsTrusted'] = (r.get('tslStatus', 'TRUSTED') == 'TRUSTED')
        if r['family'] == 'tslBai17':
            r['source'] = dict(kind='tsl', tslBlockId=r['tslBlockId'], bbox=r.get('bbox'), status=r['tslStatus'], reasons=r.get('withheldReasons', []))
            bbox = r.get('bbox')
        else:
            idx, bbox, cov = link_lines(r['book'], r['pagePdf'], r['text']) if r['pagePdf'] else ([], None, 0.0)
            r['source'] = dict(kind='ocr-body', page=f"{OCR}/{r['book']}/p{r['pagePdf']:03d}.json" if r['pagePdf'] else None, lineIndices=idx, lineSpan=[min(idx), max(idx)] if idx else None, bbox=bbox, coverage=cov,
                               unitId=r.get('unitId'), sdm=link_sdm(r['book'], r['pagePdf'], r['text']) if r['pagePdf'] else None)
        for k in ANNOT:
            r[k] = ''
        r['reviewer'] = ''; r['reviewedAt'] = ''; r['notes'] = ''
        if not a.no_crops and r['pagePdf']:
            png = f"{out}/crops/{r['sampleId']}.png"
            try:
                r['crop'] = os.path.relpath(render_crop(r['book'], r['pagePdf'], bbox, png) or '', ROOT) or None
            except Exception as e:  # noqa: BLE001 — a missing PDF must not stop the sheet
                r['crop'] = None; r['cropError'] = str(e)[:120]
            key = (r['book'], r['pagePdf'])
            if key not in pages_done:
                try:
                    render_page(r['book'], r['pagePdf'], f"{out}/pages/{r['book']}-p{r['pagePdf']:03d}.png")
                except Exception:  # noqa: BLE001
                    pass
                pages_done.add(key)
            r['pageRender'] = f"{a.out}/pages/{r['book']}-p{r['pagePdf']:03d}.png"
    with open(f'{out}/sample-{a.seed}.jsonl', 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    json.dump(manifest, open(f'{out}/manifest-{a.seed}.json', 'w'), ensure_ascii=False, indent=1)
    write_sheet(rows, manifest, f'{out}/sample-{a.seed}.md')
    linked = sum(1 for r in rows if r['family'] != 'tslBai17' and r['source'].get('lineSpan'))
    sdm_linked = sum(1 for r in rows if r['family'] != 'tslBai17' and (r['source'].get('sdm') or {}).get('matched'))
    print(json.dumps(dict(seed=a.seed, population=census['blocks'], activities=census['activities'], sampled=len(rows), showcaseActivityBlocks=len(showcase_acts), showcaseTslBlocks=len(showcase_tsl),
                          ocrLineLinked=linked, sdmLinked=sdm_linked, out=out), ensure_ascii=False, indent=1))


def write_sheet(rows, manifest, path):
    L = [f"# False-trust audit — annotation sheet (seed {manifest['seed']}) — INTERNAL / RESEARCH ONLY (D4)", '',
         f"Generated {manifest['createdAt']} by {manifest['script']}. Population: {manifest['population']['blocks']} served blocks in {manifest['population']['activities']} activities "
         f"across {len(manifest['population']['byStratum'])} strata (family × book) of the DEFAULT packs ({', '.join(v['packVersion'] for v in manifest['packs'].values())}) + samUnits; "
         f"sampled {manifest['sampled']['total']} rows = {manifest['sampled']['fromFrame']} stratified + the mandatory showcase stratum "
         f"({manifest['sampled']['showcaseActivityBlocks']} shipped Bài 17 activity blocks + {manifest['sampled']['showcaseTslBlocks']} Bài 17 TSL blocks).", '',
         '**How to annotate** — for every row fill the five fields in the JSONL (values `OK` / `WRONG` / `UNSURE` / `NA`), judging from the page crop / full page render, never from the served text alone:',
         '1. `display_fidelity` — served text = page text character-for-character (tone marks, enumerators, nothing spliced from another box). `NA` for withheld TSL rows.',
         '2. `teaching_critical_fidelity` — numbers, formulas, units, terms, negations correct. `NA` when the block has none.',
         '3. `role_fidelity` — served in the right role (question / instruction / objective / sidebar / answer / body-passage / caption). The `kind` column is the role the pack or TSL assigned.',
         '4. `lesson_attachment` — the activity is attached to the right lesson (judge once per `activityId`; copy the value to sibling rows).',
         '5. `false_trust` — your overall verdict: served as trusted but wrong in a way that would mislead a learner.',
         'Then `python3 tool/corpus/ft_audit_score.py <this jsonl>`.', '']
    cur = None
    for r in rows:
        head = f"{r['family']} · {r['book']} · Bài {r['lesson']} · pdf p{r['pagePdf']} (printed {r['pagePrinted']})" + (' · **MANDATORY SHOWCASE STRATUM**' if r.get('mandatory') else '')
        if r['activityId'] != cur:
            cur = r['activityId']
            L += [f"## {head}", f"activity `{r['activityId']}`", '']
        src = r['source']
        if r['family'] == 'tslBai17':
            srcline = f"TSL block `{src['tslBlockId']}` · status {src['status']}" + (f" · withheld: {', '.join(src['reasons'])}" if src.get('reasons') else '') + f" · bbox {src.get('bbox')}"
        else:
            sdm = src.get('sdm') or {}
            srcline = f"OCR lines {src.get('lineSpan')} (coverage {src.get('coverage')}) bbox {src.get('bbox')}" + (f" · unit `{src['unitId']}`" if src.get('unitId') else '') + \
                      (f" · TC-v2 SDM `{sdm.get('id')}` role {sdm.get('role')} **{sdm.get('trust')}** {sdm.get('reasons') or ''}" if sdm.get('matched') else (' · TC-v2 SDM: no match' if sdm else ''))
        L += [f"### {r['sampleId']} — `{r['kind']}`" + ('' if r['servedAsTrusted'] else ' (WITHHELD — not served)'),
              f"crop: `{r.get('crop')}` · page: `{r.get('pageRender')}`", f"source: {srcline}", '',
              '> ' + (r['text'] or '(withheld — no text in the TSL)').replace('\n', ' '), '',
              '| display_fidelity | teaching_critical_fidelity | role_fidelity | lesson_attachment | false_trust | notes |', '|---|---|---|---|---|---|', '|  |  |  |  |  |  |', '']
    open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
