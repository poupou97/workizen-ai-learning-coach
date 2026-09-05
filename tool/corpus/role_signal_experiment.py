#!/usr/bin/env python3
"""WAL-210 item 10b — ROLE-LAYER SIGNAL EXPERIMENT (bounded research, no LLM, no threshold decision).

Question: can a deterministic ICON / BOX-COLOUR signal read from the page image — the KNTT
conventions the OCR lines never carry (hand icon = activity, "?" bubble = question, tinted box =
question/objective/sidebar block) — lift QUESTION precision toward 0.95 and make ACTIVITY
detectable at all (TC-v2: ACTIVITY P/R 0.00/0.00)?

Method:
  1. For every TC-v2 pipeline block on the gold pages (sdm-gold) compute image features from a
     72-dpi render (PyMuPDF + numpy, deterministic):
       left strip (x − 7.5 % … x − 0.3 % of page width, the block's own line band):
         icon_present  a compact saturated blob 0.5–3 × the line height, aspect 0.35–2.5
         icon_hue      mean hue of that blob (deg) → bucket orange / blue / green / other
       box (bbox grown by 1.2 % / 0.6 %): tint_share = pale-tinted pixel fraction, tint_hue bucket
     Blocks inside the same tinted box (same tint bucket, vertically contiguous) inherit the box's
     top-left icon — the icon marks the box, not each line.
  2. Baseline = the pipeline's own fine role (canonical six-role mapping as tc2_score.py) scored
     against gold with tc_score.match — must reproduce gold-scores.json before anything else.
  3. Signal rules, FROZEN from the KNTT convention + the dev distribution before the held-out set
     is scored (no tuning on held-out):
       R1  pipeline question | instruction | body  +  orange hand icon (own or inherited)  → ACTIVITY
       R2  pipeline body | instruction               +  blue "?" bubble icon                  → QUESTION
       R3  pipeline question with NO icon and NOT in a tinted box, ending without "?"        → BODY
           (bare directive sentences outside any question box are body prose on Science pages)
  4. Score with vs without the signal on dev (38 TC-v1 pages), held-out (16), science (23), all,
     and — Founder addendum — KHTN 6 Bài 17 (pages 61–65) against a separately written gold
     (`--bai17-gold DIR`, anchors + roles + bboxes only), reported apart because it is neither dev
     nor held-out.

Outputs (--out, default poc-out/b-lane/role-signal/): features.jsonl, results.json, results.md,
plus feature-distribution tables per gold role (dev only) that justify the frozen rules.

Usage:
  python3 tool/corpus/role_signal_experiment.py --gold-dir poc-out/b-lane/tc-gold-branch/tool/corpus/tc_gold \
      [--bai17-gold tool/corpus/tc_gold_bai17] [--pipeline tc2-p1] [--dpi 72]
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.environ.get('TC_ROOT', os.getcwd())
import tc_score  # noqa: E402

SIX = ['QUESTION', 'ANSWER', 'ACTIVITY', 'INSTRUCTION', 'OBJECTIVE', 'SIDEBAR']
OTHER = ['HEADING', 'BODY', 'CAPTION', 'OPTION', 'ANSWER_SLOT', 'TABLE', 'FORMULA', 'FOOTNOTE', 'FIGURE_TEXT', 'PAGENUM', 'TEACHER_PROMPT']
GOLD_CANON = {'question': 'QUESTION', 'answer': 'ANSWER', 'activity': 'ACTIVITY', 'instruction': 'INSTRUCTION', 'objective': 'OBJECTIVE', 'sidebar': 'SIDEBAR',
              'heading': 'HEADING', 'running_head': 'HEADING', 'body': 'BODY', 'rule': 'BODY', 'attribution': 'BODY', 'speech_bubble': 'BODY',
              'caption': 'CAPTION', 'option': 'OPTION', 'answer_slot': 'ANSWER_SLOT', 'table': 'TABLE', 'formula': 'FORMULA', 'footnote': 'FOOTNOTE',
              'figure_label': 'FIGURE_TEXT', 'diagram': 'FIGURE_TEXT', 'page_number': 'PAGENUM'}
PIPE_CANON = {'question': 'QUESTION', 'answer': 'ANSWER', 'model_answer': 'ANSWER', 'activity': 'ACTIVITY', 'instruction': 'INSTRUCTION', 'objective': 'OBJECTIVE', 'sidebar': 'SIDEBAR',
              'heading': 'HEADING', 'stage_label': 'HEADING', 'running_head': 'HEADING', 'body': 'BODY', 'teacher_text': 'BODY', 'rule': 'BODY', 'teacher_prompt': 'TEACHER_PROMPT',
              'caption': 'CAPTION', 'option': 'OPTION', 'answer_slot': 'ANSWER_SLOT', 'table': 'TABLE', 'formula': 'FORMULA', 'footnote': 'FOOTNOTE',
              'figure_text': 'FIGURE_TEXT', 'figure': 'FIGURE_TEXT', 'page_number': 'PAGENUM', 'empty': 'EMPTY'}
SCIENCE = {'04-sgk-khoa-hoc-4', '05-sgk-khoa-hoc-5', '06-sgk-khoa-hoc-tu-nhien-6', '07-sgk-khoa-hoc-tu-nhien-7', '08-sgk-khoa-hoc-tu-nhien-8', '09-sgk-khoa-hoc-tu-nhien-9'}
SCIENCE_ALL = SCIENCE | {b.replace('-sgk-', '-sgv-') for b in SCIENCE}
HUE_BUCKETS = (('orange', 10, 50), ('green', 70, 170), ('blue', 185, 250))

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None


# ---------------------------------------------------------------- image features
_docs = {}


def pdf_path(book):
    for p in (f'{ROOT}/poc-out/pdf/{book[:2]}/{book}.pdf', f'{ROOT}/poc-out/pdf/{book}.pdf'):
        if os.path.exists(p):
            return p
    return None


def render(book, page, dpi):
    import fitz
    if book not in _docs:
        p = pdf_path(book)
        _docs[book] = fitz.open(p) if p else None
    doc = _docs[book]
    if doc is None or page < 1 or page > len(doc):
        return None
    pm = doc[page - 1].get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3).astype(np.int16)


def hsv(arr):
    r, g, b = arr[..., 0].astype(float), arr[..., 1].astype(float), arr[..., 2].astype(float)
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn
    sat = np.where(mx > 0, d / np.maximum(mx, 1), 0.0)
    hue = np.zeros_like(mx)
    nz = d > 0
    rm, gm, bm = (mx == r) & nz, (mx == g) & nz & ~(mx == r), (mx == b) & nz & ~(mx == r) & ~(mx == g)
    hue[rm] = (60 * ((g - b) / np.maximum(d, 1e-9)))[rm] % 360
    hue[gm] = (60 * ((b - r) / np.maximum(d, 1e-9)) + 120)[gm]
    hue[bm] = (60 * ((r - g) / np.maximum(d, 1e-9)) + 240)[bm]
    return hue, sat, mx


def bucket(h):
    if h is None:
        return None
    for name, lo, hi in HUE_BUCKETS:
        if lo <= h <= hi:
            return name
    return 'other'


def components(mask):
    """4-connected components of a small boolean array → list of (pixels as (ys, xs) index arrays)."""
    H, W = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    comps = []
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if seen[y0, x0]:
            continue
        stack = [(y0, x0)]; seen[y0, x0] = True; pix = []
        while stack:
            y, x = stack.pop(); pix.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; stack.append((ny, nx))
        comps.append(pix)
    return comps


def block_features(img, hue, sat, mx, bbox, line_h):
    """Icon strip + box tint features for one block (bbox normalised [x, y, w, h])."""
    H, W = mx.shape
    x, y, w, h = bbox
    lh = max(int(line_h * H), 4)
    # --- left strip: the block's own line band, 7.5 % of the page width to the left
    sx0, sx1 = int(max(0, x - 0.075) * W), int(max(0, x - 0.003) * W)
    sy0, sy1 = int(max(0, y - 0.004) * H), int(min(1, y + max(h, 0.018)) * H)
    feat = dict(icon_present=False, icon_hue=None, icon_bucket=None, icon_h_ratio=None, icon_fill=None, strip_colour_frac=0.0, strip_ink_frac=0.0)
    if sx1 > sx0 + 2 and sy1 > sy0 + 2:
        s_sat, s_mx, s_hue = sat[sy0:sy1, sx0:sx1], mx[sy0:sy1, sx0:sx1], hue[sy0:sy1, sx0:sx1]
        colour = (s_sat > 0.30) & (s_mx > 90)
        ink = s_mx < 110
        feat['strip_colour_frac'] = round(float(colour.mean()), 3); feat['strip_ink_frac'] = round(float(ink.mean()), 3)
        best = None
        for pix in components(colour):
            if len(pix) < 6:
                continue
            ys_ = [p[0] for p in pix]; xs_ = [p[1] for p in pix]
            bh, bw = max(ys_) - min(ys_) + 1, max(xs_) - min(xs_) + 1
            ratio = bh / lh; aspect = bw / bh
            if 0.5 <= ratio <= 3.0 and 0.35 <= aspect <= 2.5:
                fill = len(pix) / (bh * bw)
                if best is None or len(pix) > best[0]:
                    hval = float(np.mean([s_hue[p] for p in pix]))
                    best = (len(pix), ratio, fill, hval)
        if best:
            feat.update(icon_present=True, icon_h_ratio=round(best[1], 2), icon_fill=round(best[2], 2), icon_hue=round(best[3], 1), icon_bucket=bucket(best[3]))
    # --- box tint around the block
    bx0, bx1 = int(max(0, x - 0.012) * W), int(min(1, x + w + 0.012) * W)
    by0, by1 = int(max(0, y - 0.006) * H), int(min(1, y + h + 0.006) * H)
    feat.update(tint_share=0.0, tint_hue=None, tint_bucket=None)
    if bx1 > bx0 + 2 and by1 > by0 + 2:
        b_sat, b_mx, b_hue = sat[by0:by1, bx0:bx1], mx[by0:by1, bx0:bx1], hue[by0:by1, bx0:bx1]
        tint = (b_sat > 0.06) & (b_sat < 0.6) & (b_mx > 150)
        feat['tint_share'] = round(float(tint.mean()), 3)
        if tint.sum() >= 20:
            hv = float(np.median(b_hue[tint])); feat['tint_hue'] = round(hv, 1); feat['tint_bucket'] = bucket(hv)
    return feat


def inherit_box_icons(blocks):
    """Blocks in the same tinted box (same tint bucket, tint_share ≥ 0.3, vertically contiguous within
    0.12 page heights, overlapping x) inherit the icon of the box's first (top-most) block."""
    order = sorted([b for b in blocks if b['bbox']], key=lambda b: (b['bbox'][1], b['bbox'][0]))
    for i, b in enumerate(order):
        f = b['features']
        b['icon_eff'] = f['icon_bucket'] if f['icon_present'] else None
        b['icon_source'] = 'own' if f['icon_present'] else None
    for i, b in enumerate(order):
        f = b['features']
        if f['tint_share'] < 0.3 or f['tint_bucket'] is None:
            continue
        for a in order[:i]:
            fa = a['features']
            if fa['tint_share'] >= 0.3 and fa['tint_bucket'] == f['tint_bucket'] and a.get('icon_eff') and 0 <= b['bbox'][1] - a['bbox'][1] <= 0.12 \
                    and min(a['bbox'][0] + a['bbox'][2], b['bbox'][0] + b['bbox'][2]) - max(a['bbox'][0], b['bbox'][0]) > 0.05:
                if not b.get('icon_eff'):
                    b['icon_eff'] = a['icon_eff']; b['icon_source'] = 'box'
                break
    return blocks


# ---------------------------------------------------------------- rules
# v1 = frozen before the held-out set was scored (R1 + R2 + R3).
# v2 = dev-revised: R3 removed after the dev result (22 misses / 2 hits on dev); its held-out numbers
#      are therefore a SECOND look at held-out and are reported as such.
# v3 = post-hoc after the Bài 17 result: an inherited box icon never overrides the INSTRUCTION lexicon
#      (Chuẩn bị / Tiến hành / steps inside a hand-icon box stay instruction). Tuned after seeing
#      Bài 17 — its Bài 17 numbers are in-sample; only dev/held-out/science remain comparable.
RULES = 'v1'


def apply_rules(b):
    role = b['fine_role']; text = b['text'] or ''
    icon = b.get('icon_eff'); tint = b['features']['tint_share'] >= 0.3
    ends_q = text.rstrip().endswith('?')
    r1_roles = ('question', 'body') if RULES == 'v3' else ('question', 'instruction', 'body')
    if role in r1_roles and icon == 'orange':
        return 'activity', 'R1'
    if role in ('body', 'instruction') and icon == 'blue':
        return 'question', 'R2'
    if RULES == 'v1' and role == 'question' and icon is None and not tint and not ends_q:
        return 'body', 'R3'
    return role, None


# ---------------------------------------------------------------- scoring
def canon_gold(g, sgv):
    c = GOLD_CANON.get(g['role'], 'BODY')
    return 'TEACHER_PROMPT' if (sgv and c == 'QUESTION') else c


def score_set(pages, use_signal):
    tp = collections.Counter(); pred = collections.Counter(); gold = collections.Counter(); conf = collections.Counter(); fired = collections.Counter()
    for pg in pages:
        sgv = '-sgv-' in pg['book']
        for gid, (gc, b) in pg['matched'].items():
            fine = b['rule_role'] if use_signal else b['fine_role']
            pc = PIPE_CANON.get(fine, 'BODY')
            gold[gc] += 1; pred[pc] += 1
            if pc == gc:
                tp[pc] += 1
            else:
                conf[f'{gc}->{pc}'] += 1
            if use_signal and b.get('rule'):
                fired[(b['rule'], 'hit' if pc == gc else 'miss')] += 1
    roles = {}
    for k in SIX + OTHER:
        roles[k] = dict(p=round(tp[k] / pred[k], 3) if pred[k] else None, r=round(tp[k] / gold[k], 3) if gold[k] else None, tp=tp[k], pred=pred[k], gold=gold[k])
    return dict(pages=len(pages), roles=roles, confusion=dict(conf.most_common(20)), rules={f'{r}:{o}': n for (r, o), n in sorted(fired.items())})


def load_gold(gold_dir):
    return [json.load(open(f)) for f in sorted(glob.glob(f'{gold_dir}/*.json'))]


def build_page(gold, pipeline, dpi):
    p = f"{ROOT}/poc-out/trusted-corpus/tc-v2/{pipeline}/sdm-gold/{gold['book']}/p{gold['page']:03d}.sdm.json"
    if not os.path.exists(p):
        p = f"{ROOT}/poc-out/trusted-corpus/tc-v2/{pipeline}/sdm/{gold['book']}/p{gold['page']:03d}.sdm.json"
    if not os.path.exists(p):
        return None
    sdm = json.load(open(p))
    img = render(gold['book'], gold['page'], dpi)
    if img is None:
        return None
    hue, sat, mx = hsv(img)
    heights = [b['bbox'][3] for b in sdm['blocks'] if b.get('bbox') and b.get('text') and len(b['text']) < 120]
    line_h = float(np.median(heights)) if heights else 0.015
    blocks = []
    for ob in sdm['blocks']:
        b = dict(id=ob['id'], order=ob['order'], text=ob['text'], bbox=ob['bbox'], fine_role=ob['role']['value'], coarse=ob['role']['coarse'], trusted=ob['trust']['status'] == 'TRUSTED',
                 colour_share=(ob.get('colour') or {}).get('share'))
        b['features'] = block_features(img, hue, sat, mx, ob['bbox'], line_h) if ob.get('bbox') else dict(icon_present=False, icon_bucket=None, tint_share=0.0, tint_bucket=None, icon_hue=None, icon_h_ratio=None, icon_fill=None, strip_colour_frac=0.0, strip_ink_frac=0.0, tint_hue=None)
        blocks.append(b)
    inherit_box_icons(blocks)
    for b in blocks:
        b['rule_role'], b['rule'] = apply_rules(b)
    v1 = dict(book=sdm['book'], page=sdm['page'], candidate='tc2-sdm', blocks=[dict(id=b['id'], order=b['order'], role=b['coarse'], text=b['text'], bbox=b['bbox']) for b in blocks])
    m = tc_score.match(gold, v1)
    by_id = {b['id']: b for b in blocks}
    sgv = '-sgv-' in gold['book']
    matched = {}
    for g in gold['blocks']:
        c = m.get(g['id'])
        if c:
            matched[g['id']] = (canon_gold(g, sgv), by_id[c['id']])
            by_id[c['id']]['gold_role'] = g['role']
    return dict(book=gold['book'], page=gold['page'], held_out=bool(gold.get('held_out')), blocks=blocks, matched=matched)


def feature_table(pages, only_dev=True):
    """Per gold role (dev pages only): how often an icon / tint is present and which bucket."""
    rows = collections.defaultdict(collections.Counter)
    for pg in pages:
        if only_dev and pg['held_out']:
            continue
        for gid, (gc, b) in pg['matched'].items():
            f = b['features']
            rows[gc]['n'] += 1
            rows[gc]['icon_own'] += bool(f['icon_present'])
            rows[gc]['icon_eff'] += bool(b.get('icon_eff'))
            rows[gc][f"icon_{b.get('icon_eff')}"] += bool(b.get('icon_eff'))
            rows[gc]['tinted'] += f['tint_share'] >= 0.3
            rows[gc][f"tint_{f['tint_bucket']}"] += (f['tint_share'] >= 0.3 and f['tint_bucket'] is not None)
    return {k: dict(v) for k, v in rows.items()}


def fmt(x):
    return '—' if x is None else f'{x:.3f}'


def md_roles(title, base, sig):
    L = [f'### {title} ({base["pages"]} pages)', '', '| role | P without | R without | P with signal | R with signal | gold n | pred without → with |', '|---|---|---|---|---|---|---|']
    for k in SIX + ['HEADING', 'BODY', 'CAPTION']:
        b, s = base['roles'][k], sig['roles'][k]
        if b['gold'] == 0 and b['pred'] == 0 and s['pred'] == 0:
            continue
        L.append(f"| {'**' + k + '**' if k in SIX else k} | {fmt(b['p'])} | {fmt(b['r'])} | {fmt(s['p'])} | {fmt(s['r'])} | {b['gold']} | {b['pred']} → {s['pred']} |")
    L += ['', f"rules fired (with signal): {sig['rules']}", f"confusion with signal (gold→pipeline): {sig['confusion']}", '']
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gold-dir', default=os.path.join(HERE, 'tc_gold'))
    ap.add_argument('--bai17-gold', default=None)
    ap.add_argument('--pipeline', default='tc2-p1')
    ap.add_argument('--dpi', type=int, default=72)
    ap.add_argument('--out', default='poc-out/b-lane/role-signal')
    ap.add_argument('--rules', choices=('v1', 'v2', 'v3'), default='v1')
    a = ap.parse_args()
    if np is None:
        raise SystemExit('numpy required')
    global RULES
    RULES = a.rules
    out = a.out if os.path.isabs(a.out) else f'{ROOT}/{a.out}'
    os.makedirs(out, exist_ok=True)
    golds = load_gold(a.gold_dir)
    pages = [p for p in (build_page(g, a.pipeline, a.dpi) for g in golds) if p]
    sets = dict(all=pages, dev=[p for p in pages if not p['held_out']], heldout=[p for p in pages if p['held_out']],
                science=[p for p in pages if p['book'] in SCIENCE_ALL], science_sgk=[p for p in pages if p['book'] in SCIENCE])
    results = {k: dict(without=score_set(v, False), with_signal=score_set(v, True)) for k, v in sets.items()}
    ftab = feature_table(pages, only_dev=True)
    bai17 = None
    if a.bai17_gold and os.path.isdir(a.bai17_gold):
        g17 = load_gold(a.bai17_gold)
        p17 = [p for p in (build_page(g, a.pipeline, a.dpi) for g in g17) if p]
        bai17 = dict(pages=len(p17), without=score_set(p17, False), with_signal=score_set(p17, True), gold_blocks=sum(len(g['blocks']) for g in g17), matched=sum(len(p['matched']) for p in p17))
        pages += p17
    with open(f'{out}/features.jsonl', 'w') as f:
        for pg in pages:
            for b in pg['blocks']:
                f.write(json.dumps(dict(book=pg['book'], page=pg['page'], held_out=pg['held_out'], id=b['id'], fine_role=b['fine_role'], gold_role=b.get('gold_role'), rule_role=b['rule_role'], rule=b['rule'],
                                        icon_eff=b.get('icon_eff'), icon_source=b.get('icon_source'), colour_share=b['colour_share'], **b['features']), ensure_ascii=False) + '\n')
    json.dump(dict(pipeline=a.pipeline, dpi=a.dpi, gold_dir=a.gold_dir, pages=len(pages), sets={k: len(v) for k, v in sets.items()}, results=results, feature_table_dev=ftab, bai17=bai17), open(f'{out}/results.json', 'w'), ensure_ascii=False, indent=1)
    rules_txt = {'v1': 'rules v1 = frozen before held-out scoring (R1 orange-icon→ACTIVITY, R2 blue-icon→QUESTION, R3 bare directive outside any box→BODY)',
                 'v2': 'rules v2 = dev-revised (R1 orange-icon→ACTIVITY, R2 blue-icon→QUESTION; R3 removed after the dev result) — held-out numbers are a SECOND look',
                 'v3': 'rules v3 = post-hoc after Bài 17 (v2 + an inherited icon never overrides the instruction lexicon) — Bài 17 numbers are IN-SAMPLE'}[a.rules]
    L = [f'# Role-layer signal experiment — results (MEASURED, rules {a.rules})', '', f"pipeline {a.pipeline} · render {a.dpi} dpi · gold {a.gold_dir} ({len(golds)} pages, {len(pages) - (bai17['pages'] if bai17 else 0)} scored) · {rules_txt}", '',
         '## Feature distribution per gold role (dev pages only — the evidence the rules were frozen on)', '', '| gold role | n | own icon | effective icon | orange | blue | green | tinted box | tint orange | tint blue | tint green |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for k in SIX + ['HEADING', 'BODY', 'CAPTION']:
        v = ftab.get(k)
        if not v:
            continue
        L.append(f"| {k} | {v['n']} | {v.get('icon_own', 0)} | {v.get('icon_eff', 0)} | {v.get('icon_orange', 0)} | {v.get('icon_blue', 0)} | {v.get('icon_green', 0)} | {v.get('tinted', 0)} | {v.get('tint_orange', 0)} | {v.get('tint_blue', 0)} | {v.get('tint_green', 0)} |")
    L.append('')
    for k in ('dev', 'heldout', 'science', 'science_sgk', 'all'):
        L += md_roles(k, results[k]['without'], results[k]['with_signal'])
    if bai17:
        L += ['## KHTN 6 Bài 17 «Tách chất khỏi hỗn hợp» (Founder addendum — separate gold, neither dev nor held-out)', '', f"gold blocks {bai17['gold_blocks']}, matched {bai17['matched']}", '']
        L += md_roles('bai17', bai17['without'], bai17['with_signal'])
    open(f'{out}/results-{a.rules}.md', 'w').write('\n'.join(L) + '\n')
    os.replace(f'{out}/results.json', f'{out}/results-{a.rules}.json')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
