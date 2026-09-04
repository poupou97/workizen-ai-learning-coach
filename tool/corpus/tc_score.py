#!/usr/bin/env python3
"""TC-v1 — SOURCE-FIDELITY SCORER: gold pages × candidates, every metric kept separate.

Per (page, candidate) it measures — never collapsed into one number:
  found          share of gold blocks (with an anchor) matched in the candidate output
  order          pairwise reading-order agreement over matched gold blocks in the MAIN
                 FLOW (pairs involving a flex-group block are skipped unless both blocks
                 are in the same group)
  order_meaning  number of inverted pairs between two learning blocks of the same
                 column (a "meaning-changing" inversion)
  text_cer       character error rate on gold blocks that carry full text
                 (NFC, whitespace-collapsed) — with diacritics, without tone marks,
                 and without any diacritics (đ→d) — so OCR diacritic loss is visible
  fidelity       share of gold `contiguous` blocks delivered in ONE candidate block
                 with NO foreign gold anchor spliced in
  splice         count of candidate blocks containing anchors of ≥ 2 gold blocks
                 from different columns / flex groups (cross-column contamination)
  role P/R       per coarse role over matched blocks (+ question P/R separately)
  caption_assoc  share of gold captions matched with role CAPTION and adjacent
                 (order distance ≤ 2) to a FIGURE block or its figure text
  table/formula  gold TABLE/FORMULA blocks matched with the right role
  provenance     share of matched candidate blocks carrying a bbox
  digits_ok      share of full-text gold blocks whose digit/operator sequence
                 survives exactly (math/science data integrity)
  TRUST          trusted = candidate says trusted, or has no trust concept
                 (implicit). A matched learning block is WRONG when: CER(diacritics)
                 > 0.10, or spliced, or emitted as QUESTION while gold says it is not
                 a question, or inverted with a same-column neighbour.
    TLSR         gold learning blocks delivered correctly AND trusted / gold learning blocks
    FTR          wrong AND trusted / trusted (false trust rate)
    safe_reject  gold learning blocks matched but marked untrusted (safe failure)
  CTE            critical-teaching-error events by class:
                 heading_as_question · nonquestion_as_question · cross_column_contamination ·
                 order_changes_meaning · corrupted_data · figure_text_as_prose ·
                 attribution_detached · lesson_attach_wrong (page-level, TOC range vs gold)

Usage: python3 tool/corpus/tc_score.py [--ver tc-v1] [--cands a,b,c] [--json out.json] [--md out.md]
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tc_sdm  # noqa: E402

ROOT = tc_sdm.ROOT
CANDS = ['current-naive', 'current-xycut', 'docling-ocrmac', 'mineru', 'marker', 'vlm-mlx', 'pymupdf4llm']


# ---------------------------------------------------------------- text utils
def nfc(s):
    s = unicodedata.normalize('NFC', s or '')
    s = s.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'").replace('–', '-').replace('—', '-').replace('…', '...')
    return re.sub(r'\s+', ' ', s).strip()


def strip_tones(s):
    """Remove Vietnamese TONE marks only (keep â ê ô ơ ư ă đ)."""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if c not in '̣̀́̃̉')
    return unicodedata.normalize('NFC', s)


def strip_all(s):
    s = unicodedata.normalize('NFD', s.replace('đ', 'd').replace('Đ', 'D'))
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def norm_key(s):
    return re.sub(r'[^a-z0-9]+', ' ', strip_all(nfc(s)).lower()).strip()


try:  # fast C++ Levenshtein when available (pip install rapidfuzz in the bake-off venv); pure-python fallback otherwise
    from rapidfuzz.distance import Levenshtein as _RL

    def lev(a, b):
        return _RL.distance(a, b)
except Exception:  # pragma: no cover
    def lev(a, b):
        if a == b:
            return 0
        if not a:
            return len(b)
        if not b:
            return len(a)
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            for j, cb in enumerate(b, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            prev = cur
        return prev[-1]


_TONE_PLACE = re.compile(r'([oOuU])([aeyAEY])([̣̀́̃̉])')


def norm_tone_placement(s):
    """Map old-style tone placement (hoá, thuỷ) to modern (hóa, thủy) so the two valid
    Vietnamese orthographies are not counted as OCR errors; real tone errors still count."""
    d = unicodedata.normalize('NFD', s)
    d = _TONE_PLACE.sub(lambda m: m.group(1) + m.group(3) + m.group(2), d)
    return unicodedata.normalize('NFC', d)


def cer(gold, cand):
    """Character error rate of the gold text against the best-aligned substring of the
    candidate text (the candidate block may legitimately contain neighbouring blocks)."""
    g, c = nfc(gold), nfc(cand)
    if not g:
        return None
    if len(c) > 1.15 * len(g) + 6:
        try:
            from rapidfuzz import fuzz
            al = fuzz.partial_ratio_alignment(g, c)
            if al is not None:
                sub = c[al.dest_start:al.dest_end]
                return min(1.0, lev(g, sub) / len(g))
        except Exception:
            pass
        best = None
        toks = c.split(' ')
        starts = [0]
        for t in toks[:-1]:
            starts.append(starts[-1] + len(t) + 1)
        starts = [s for s in starts if s <= len(c) - len(g) * 0.5]
        step = max(1, len(starts) // 40)
        for st in starts[::step]:
            for f in (0.95, 1.05, 1.15):
                w = c[st:st + int(f * len(g)) + 4]
                d = lev(g, w)
                if best is None or d < best:
                    best = d
        return min(1.0, best / len(g))
    return min(1.0, lev(g, c) / len(g))


def digits_seq(s):
    """Digits and math operators only; a dash counts only when glued to a digit (−2, 1873–1909), never as a bullet."""
    return re.findall(r'\d+|[=<>≠≤≥×÷+/√²³°%]|(?<=\d)\s?-(?=\s?\d)|-(?=\d)', nfc(s))


def key4(anchor):
    toks = norm_key(anchor).split()
    return ' '.join(toks[:4]) if len(toks) >= 4 else ' '.join(toks)


def iou(a, b):
    if not a or not b:
        return 0.0
    ax0, ay0, aw, ah = a; bx0, by0, bw, bh = b
    ix = max(0, min(ax0 + aw, bx0 + bw) - max(ax0, bx0)); iy = max(0, min(ay0 + ah, by0 + bh) - max(ay0, by0))
    inter = ix * iy; u = aw * ah + bw * bh - inter
    return inter / u if u > 0 else 0.0


# ---------------------------------------------------------------- matching
def _contains(text_key, key):
    return (' ' + key + ' ') in (' ' + text_key + ' ')


def match(gold, sdm):
    """gold block id → candidate block: longest anchor prefix (7…3 tokens) found on token boundaries;
    fallback bbox IoU for anchor-less blocks (figures)."""
    m = {}
    cands = sdm['blocks']
    ckeys = [(c, norm_key(c['text'])) for c in cands]
    last_order = -1  # duplicate texts on a page (e.g. two "1. Khám phá" headings): prefer the next occurrence after the previous match
    for g in gold['blocks']:
        src = g.get('text') or g.get('anchor')
        hit = None
        if src:
            toks = norm_key(src.split('\n')[0]).split()
            if not toks and g.get('anchor'):
                toks = norm_key(g['anchor']).split()
            levels = [n for n in (7, 6, 5, 4, 3) if len(toks) >= n] or ([len(toks)] if 1 <= len(toks) < 3 else [])
            for n in levels:
                k = ' '.join(toks[:n])
                found = [c for c, ck in ckeys if _contains(ck, k)]
                if found:
                    later = [c for c in found if c['order'] > last_order]
                    hit = (later or found)[0]
                    break
        if not hit and g.get('bbox'):
            best = (0.25, None)
            for c in cands:
                v = iou(g['bbox'], c['bbox'])
                if v > best[0] and (c['text'] or c['role'] == 'FIGURE'):
                    best = (v, c)
            hit = best[1]
        if hit:
            m[g['id']] = hit
            if hit['order'] > last_order:
                last_order = hit['order']
    return m


def group_of(gold):
    gid = {}
    for gi, grp in enumerate(gold.get('flex_groups', [])):
        for b in grp:
            gid[b] = gi
    return gid


def lesson_from_toc(book, page):
    docs = lesson_from_toc._docs
    if docs is None:
        docs = {x['sourceDocumentId']: x for x in json.load(open(f'{ROOT}/poc-out/graph/curriculum-structure.json'))['documents']}
        lesson_from_toc._docs = docs
    m = docs.get(book)
    if not m:
        return None
    ls = sorted([l for l in m.get('lessons', []) if l.get('pageStart')], key=lambda l: l['pageStart'])
    cur = None
    for l in ls:
        if l['pageStart'] <= page:
            cur = l
        else:
            break
    return cur['number'] if cur else None


lesson_from_toc._docs = None


# ---------------------------------------------------------------- scoring
def score(gold, sdm):
    r = dict(book=gold['book'], page=gold['page'], candidate=sdm['candidate'], seconds=sdm.get('seconds'), error=sdm.get('error'))
    if sdm.get('error') or not sdm['blocks']:
        r.update(found=0.0, note='no output'); return r
    m = match(gold, sdm)
    gid = group_of(gold)
    gb = {g['id']: g for g in gold['blocks']}
    anchored = [g for g in gold['blocks'] if g.get('anchor')]
    r['gold_blocks'] = len(gold['blocks']); r['found'] = round(sum(1 for g in anchored if g['id'] in m) / max(1, len(anchored)), 3)
    r['misses'] = [g['id'] for g in anchored if g['id'] not in m]
    # reading order (main flow)
    matched = [g for g in gold['blocks'] if g['id'] in m]
    pairs = agree = 0; meaning_inv = 0
    for i in range(len(matched)):
        for j in range(i + 1, len(matched)):
            a, b = matched[i], matched[j]
            ga, gbb = gid.get(a['id']), gid.get(b['id'])
            if (ga is not None or gbb is not None) and ga != gbb:
                continue
            if m[a['id']]['order'] == m[b['id']]['order']:
                continue  # same candidate block: order undefined
            pairs += 1
            ok = m[a['id']]['order'] < m[b['id']]['order']
            agree += ok
            if not ok and a['role'] in tc_sdm.LEARNING_ROLES and b['role'] in tc_sdm.LEARNING_ROLES and a.get('column') == b.get('column'):
                meaning_inv += 1
    r['order'] = round(agree / pairs, 3) if pairs else None; r['order_pairs'] = pairs; r['order_meaning_inversions'] = meaning_inv
    # roles
    role_tp = Counter(); role_gold = Counter(); role_pred = Counter()
    q_tp = q_pred = q_gold = 0
    cte = Counter(); cte_examples = []
    for g in matched:
        gr = tc_sdm.GOLD_ROLE_MAP.get(g['role'], 'UNKNOWN'); cr = m[g['id']]['role']
        role_gold[gr] += 1; role_pred[cr] += 1
        if gr == cr: role_tp[gr] += 1
        if gr == 'QUESTION': q_gold += 1
        if cr == 'QUESTION':
            q_pred += 1
            if gr == 'QUESTION': q_tp += 1
            elif g['role'] in ('heading', 'running_head'):
                cte['heading_as_question'] += 1; cte_examples.append(('heading_as_question', g['id'], m[g['id']]['text'][:70]))
            elif g['role'] in tc_sdm.NOT_A_QUESTION:
                cte['nonquestion_as_question'] += 1; cte_examples.append(('nonquestion_as_question', g['id'], m[g['id']]['text'][:70]))
    r['role_acc'] = round(sum(role_tp.values()) / max(1, len(matched)), 3)
    r['role_pr'] = {k: dict(p=round(role_tp[k] / role_pred[k], 2) if role_pred[k] else None, r=round(role_tp[k] / role_gold[k], 2) if role_gold[k] else None, gold=role_gold[k], pred=role_pred[k]) for k in set(role_gold) | set(role_pred)}
    r['question_p'] = round(q_tp / q_pred, 3) if q_pred else None; r['question_r'] = round(q_tp / q_gold, 3) if q_gold else None
    r['question_gold'] = q_gold; r['question_pred'] = q_pred
    # text accuracy
    cers, cers_t, cers_a, dig_ok, dig_n = [], [], [], 0, 0
    for g in matched:
        if not g.get('text'):
            continue
        ct = m[g['id']]['text']
        # extend with following candidate blocks if the gold text is much longer
        if len(nfc(ct)) < 0.7 * len(nfc(g['text'])):
            o = m[g['id']]['order']
            for c in sdm['blocks']:
                if o < c['order'] <= o + 8 and c['text']:
                    ct += ' ' + c['text']
                    if len(nfc(ct)) >= len(nfc(g['text'])): break
        c1 = cer(norm_tone_placement(g['text']), norm_tone_placement(ct)); c2 = cer(strip_tones(g['text']), strip_tones(ct)); c3 = cer(strip_all(g['text']), strip_all(ct))
        cers.append(c1); cers_t.append(c2); cers_a.append(c3)
        g['_cer_notone'] = c2
        # enumerators ("1.", "a)", "HĐ1", "2. ") are structure, not data: compare them separately
        enum_re = re.compile(r'^\s*(?:(?:HĐ|Bài|Bước)\s*\d+[.:]?|\d{1,2}[.)]|[a-dA-D][.)])\s*')
        g_core = enum_re.sub('', nfc(g['text']), count=1); c_core = enum_re.sub('', nfc(ct), count=1)
        ds = digits_seq(g_core)
        if ds:
            dig_n += 1
            dc = digits_seq(c_core)
            if ds == dc[:len(ds)] or all(d in dc for d in ds):
                dig_ok += 1
            else:
                if g['role'] in tc_sdm.LEARNING_ROLES:
                    cte['corrupted_data'] += 1; cte_examples.append(('corrupted_data', g['id'], ' '.join(ds)[:40] + ' ≠ ' + ' '.join(dc)[:40]))
        ge = enum_re.match(nfc(g['text']))
        if ge and ge.group(0).strip() and g['role'] in ('question', 'option'):
            core3 = ' '.join(norm_key(g_core).split()[:3]); with_enum = norm_key(ge.group(0) + ' ' + ' '.join(g_core.split()[:3]))
            ctk = norm_key(ct)
            if core3 and _contains(ctk, core3) and not _contains(ctk, with_enum):
                cte['enumerator_dropped'] += 1
        g['_cer'] = c1; g['_edits'] = c1 * len(nfc(g['text']))
    r['text_blocks'] = len(cers)
    r['cer'] = round(sum(cers) / len(cers), 4) if cers else None
    r['cer_notone'] = round(sum(cers_t) / len(cers_t), 4) if cers_t else None
    r['cer_nodiacritic'] = round(sum(cers_a) / len(cers_a), 4) if cers_a else None
    r['text_acc'] = round(1 - r['cer'], 4) if cers else None
    r['digits_ok'] = round(dig_ok / dig_n, 3) if dig_n else None
    # fidelity / splice
    anchor_keys = {g['id']: ' '.join(norm_key((g.get('text') or g['anchor']).split('\n')[0]).split()[:6]) for g in gold['blocks'] if g.get('anchor')}
    anchor_keys = {k: v for k, v in anchor_keys.items() if len(v.split()) >= 5}  # short keys ("Bảng nhân 7") occur inside other blocks legitimately
    def foreign_in(cblock, gself):
        t = norm_key(cblock['text'])
        out = []
        for gidd, k in anchor_keys.items():
            if gidd == gself['id']: continue
            og = gb[gidd]
            if _contains(t, k) and (og.get('column') != gself.get('column') or gid.get(gidd) != gid.get(gself['id']) or og['role'] in ('sidebar', 'caption', 'footnote', 'figure_label', 'speech_bubble')):
                out.append(gidd)
        return out
    fid_n = fid_ok = 0
    for g in matched:
        if not g.get('contiguous'):
            continue
        fid_n += 1
        if not foreign_in(m[g['id']], g):
            fid_ok += 1
    r['fidelity'] = round(fid_ok / fid_n, 3) if fid_n else None
    splices = 0
    seen = set()
    for c in sdm['blocks']:
        if c['order'] in seen or not c['text']: continue
        t = norm_key(c['text'])
        ins = [gidd for gidd, k in anchor_keys.items() if _contains(t, k)]
        cols = {(gb[x].get('column'), gid.get(x), gb[x]['role'] in ('sidebar', 'caption', 'footnote', 'figure_label', 'speech_bubble')) for x in ins}
        if len(ins) >= 2 and len(cols) >= 2:
            splices += 1; seen.add(c['order'])
            cte['cross_column_contamination'] += 1; cte_examples.append(('cross_column_contamination', ','.join(ins), c['text'][:80]))
    r['splices'] = splices
    if meaning_inv:
        cte['order_changes_meaning'] += meaning_inv
    # caption association
    caps = [g for g in matched if g['role'] == 'caption']
    cap_ok = 0
    figs = [c for c in sdm['blocks'] if c['role'] in ('FIGURE', 'FIGURE_TEXT')]
    for g in caps:
        c = m[g['id']]
        if c['role'] == 'CAPTION' and (not figs or any(abs(f['order'] - c['order']) <= 2 for f in figs)):
            cap_ok += 1
    r['caption_assoc'] = round(cap_ok / len(caps), 3) if caps else None
    # table / formula
    tabs = [g for g in matched if g['role'] == 'table']; forms = [g for g in matched if g['role'] == 'formula']
    r['table_role'] = round(sum(1 for g in tabs if m[g['id']]['role'] == 'TABLE') / len(tabs), 2) if tabs else None
    r['formula_role'] = round(sum(1 for g in forms if m[g['id']]['role'] == 'FORMULA') / len(forms), 2) if forms else None
    # figure text as prose: candidate BODY blocks overlapping a gold figure_label/diagram bbox (≥ 0.3 of the candidate box) and not matching any gold non-figure block
    fig_prose = 0
    for c in sdm['blocks']:
        if c['role'] not in ('BODY', 'UNKNOWN') or not c['bbox'] or len(c['text']) < 12: continue
        if any(v > 0.3 for v in [iou(c['bbox'], g['bbox']) for g in gold['blocks'] if g['role'] in ('figure_label', 'diagram')] ) and c['order'] not in {m[x]['order'] for x in m if gb[x]['role'] not in ('figure_label', 'diagram')}:
            fig_prose += 1
    if fig_prose:
        cte['figure_text_as_prose'] += fig_prose
    # attribution
    for g in matched:
        if g['role'] != 'attribution': continue
        prev = [x for x in gold['blocks'] if x['order'] < g['order'] and x['role'] == 'body' and x['id'] in m]
        if prev and abs(m[g['id']]['order'] - m[prev[-1]['id']]['order']) > 2:
            cte['attribution_detached'] += 1
    # provenance
    r['provenance_bbox'] = round(sum(1 for g in matched if m[g['id']]['bbox']) / max(1, len(matched)), 3)
    # trust / TLSR / FTR
    learning = [g for g in gold['blocks'] if g['role'] in tc_sdm.LEARNING_ROLES and g.get('anchor')]
    has_trust = any(c['trusted'] is not None for c in sdm['blocks'])
    trusted_n = wrong_trusted = delivered_ok = safe_reject = 0
    wrong_list = []
    for g in learning:
        if g['id'] not in m:
            continue
        c = m[g['id']]
        trusted = c['trusted'] if has_trust else True
        if has_trust and sdm.get('meta') and sdm['meta'].get('page_trusted') is False:
            trusted = False
        wrong = []
        # _cer is tone-placement-normalised (hoá/hóa are not errors; real tone errors are); a block is WRONG when > 10 % of
        # its characters are wrong AND at least 3 characters are wrong (one slipped tone mark in a 9-char heading is not a teaching error)
        if g.get('_cer') is not None and g['_cer'] > 0.10 and g.get('_edits', 0) >= 3: wrong.append('cer')
        if g.get('contiguous') and foreign_in(c, g): wrong.append('splice')
        if c['role'] == 'QUESTION' and g['role'] in tc_sdm.NOT_A_QUESTION: wrong.append('as_question')
        # same-column inversion involving this block
        for h in learning:
            if h['id'] in m and h is not g and h.get('column') == g.get('column') and gid.get(h['id']) == gid.get(g['id']) and m[h['id']]['order'] != c['order']:
                if (h['order'] < g['order']) != (m[h['id']]['order'] < c['order']):
                    wrong.append('order'); break
        if trusted:
            trusted_n += 1
            if wrong: wrong_trusted += 1; wrong_list.append((g['id'], wrong))
            else: delivered_ok += 1
        else:
            safe_reject += 1
    r['learning_blocks'] = len(learning); r['trusted_blocks'] = trusted_n
    r['tlsr'] = round(delivered_ok / max(1, len(learning)), 3)
    r['ftr'] = round(wrong_trusted / trusted_n, 3) if trusted_n else None
    r['false_trusted'] = wrong_trusted; r['safe_rejected'] = safe_reject; r['wrong_examples'] = wrong_list[:6]
    r['has_trust_concept'] = has_trust
    # lesson attachment (pipeline-level, independent of parser)
    # curriculum-structure stores PRINTED page numbers; the router calibrates printed→PDF from footer digits, so compare on printed pages
    toc = lesson_from_toc(gold['book'], gold.get('printed_page') or gold['page']); gl = gold.get('lesson', {}).get('number')
    r['lesson_toc'] = toc; r['lesson_gold'] = gl
    if gl is None:
        r['lesson_attach'] = 'gold=none' + (' (TOC attaches %s → WRONG)' % toc if toc is not None else ' (TOC attaches none → OK)')
        if toc is not None: cte['lesson_attach_wrong'] += 1
    else:
        r['lesson_attach'] = 'OK' if toc == gl else f'WRONG (toc={toc}, gold={gl})'
        if toc != gl: cte['lesson_attach_wrong'] += 1
    r['cte'] = dict(cte); r['cte_total'] = sum(cte.values()); r['cte_examples'] = cte_examples[:8]
    return r


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ver', default='tc-v1'); ap.add_argument('--cands', default=','.join(CANDS))
    ap.add_argument('--json', default=None); ap.add_argument('--md', default=None); a = ap.parse_args()
    cands = a.cands.split(',')
    golds = tc_sdm.all_gold()
    rows = []
    for g in golds:
        for c in cands:
            s = tc_sdm.load_sdm(c, g['book'], g['page'], a.ver)
            if s is None:
                rows.append(dict(book=g['book'], page=g['page'], candidate=c, error='not run')); continue
            rows.append(score(g, s))
    out = dict(pages=len(golds), candidates=cands, rows=rows)
    # aggregate
    agg = {}
    for c in cands:
        rs = [r for r in rows if r['candidate'] == c and not r.get('error') and 'tlsr' in r]
        def mean(k):
            v = [r[k] for r in rs if r.get(k) is not None]
            return round(sum(v) / len(v), 3) if v else None
        cte = Counter()
        for r in rs: cte.update(r.get('cte', {}))
        agg[c] = dict(pages=len(rs), ran=sum(1 for r in rows if r['candidate'] == c and r.get('error') != 'not run'), errors=sum(1 for r in rows if r['candidate'] == c and r.get('error') and r.get('error') != 'not run'),
                      found=mean('found'), order=mean('order'), meaning_inversions=sum(r['order_meaning_inversions'] for r in rs), text_acc=mean('text_acc'), cer=mean('cer'), cer_notone=mean('cer_notone'), cer_nodiacritic=mean('cer_nodiacritic'),
                      fidelity=mean('fidelity'), splices=sum(r['splices'] for r in rs), role_acc=mean('role_acc'), question_p=mean('question_p'), question_r=mean('question_r'), caption_assoc=mean('caption_assoc'),
                      table_role=mean('table_role'), formula_role=mean('formula_role'), digits_ok=mean('digits_ok'), provenance=mean('provenance_bbox'),
                      learning_blocks=sum(r['learning_blocks'] for r in rs), tlsr=round(sum(r['tlsr'] * r['learning_blocks'] for r in rs) / max(1, sum(r['learning_blocks'] for r in rs)), 3),
                      trusted_blocks=sum(r['trusted_blocks'] for r in rs), false_trusted=sum(r['false_trusted'] for r in rs), ftr=round(sum(r['false_trusted'] for r in rs) / max(1, sum(r['trusted_blocks'] for r in rs)), 4),
                      safe_rejected=sum(r['safe_rejected'] for r in rs), cte=dict(cte), cte_total=sum(cte.values()), cte_pages=sum(1 for r in rs if r['cte_total']),
                      sec_per_page=mean('seconds'), sec_median=(lambda v: (v[len(v) // 2] if v else None))(sorted(r['seconds'] for r in rs if r.get('seconds') is not None)))
    out['aggregate'] = agg
    if a.json:
        json.dump(out, open(a.json, 'w'), ensure_ascii=False, indent=1)
    # markdown summary
    L = [f'# TC-v1 parser bake-off — {len(golds)} gold pages (MEASURED)', '', '| candidate | pages | found | order | meaning-inv | text acc (diacritics) | CER no-tone | CER no-diacritic | fidelity | splices | role acc | Q prec | Q rec | caption | table | formula | digits ok | provenance | TLSR | trusted blk | false trusted | FTR | safe rej | CTE total | CTE pages | s/page (median) |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for c, v in agg.items():
        f = lambda x: '—' if x is None else (f'{x:.3f}' if isinstance(x, float) else str(x))
        L.append(f"| {c} | {v['pages']} | {f(v['found'])} | {f(v['order'])} | {v['meaning_inversions']} | {f(v['text_acc'])} | {f(v['cer_notone'])} | {f(v['cer_nodiacritic'])} | {f(v['fidelity'])} | {v['splices']} | {f(v['role_acc'])} | {f(v['question_p'])} | {f(v['question_r'])} | {f(v['caption_assoc'])} | {f(v['table_role'])} | {f(v['formula_role'])} | {f(v['digits_ok'])} | {f(v['provenance'])} | {f(v['tlsr'])} | {v['trusted_blocks']} | {v['false_trusted']} | {f(v['ftr'])} | {v['safe_rejected']} | {v['cte_total']} | {v['cte_pages']} | {f(v['sec_median'])} |")
    L += ['', '## Critical teaching errors by class', '', '| candidate | ' + ' | '.join(sorted({k for v in agg.values() for k in v['cte']})) + ' |']
    keys = sorted({k for v in agg.values() for k in v['cte']})
    L.append('|---|' + '---|' * len(keys))
    for c, v in agg.items():
        L.append(f'| {c} | ' + ' | '.join(str(v['cte'].get(k, 0)) for k in keys) + ' |')
    L += ['', '## Per page', '', '| page | candidate | found | order | text acc | fidelity | splices | Q p/r | TLSR | FTR | CTE | lesson |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        if r.get('error'):
            L.append(f"| {r['book']} p{r['page']:03d} | {r['candidate']} | ERROR {str(r['error'])[:40]} | | | | | | | | | |"); continue
        f = lambda x: '—' if x is None else (f'{x:.2f}' if isinstance(x, float) else str(x))
        L.append(f"| {r['book']} p{r['page']:03d} | {r['candidate']} | {f(r['found'])} | {f(r['order'])} | {f(r['text_acc'])} | {f(r['fidelity'])} | {r['splices']} | {f(r['question_p'])}/{f(r['question_r'])} | {f(r['tlsr'])} | {f(r['ftr'])} | {r['cte_total']} {r['cte'] if r['cte'] else ''} | {r['lesson_attach']} |")
    md = '\n'.join(L) + '\n'
    if a.md:
        open(a.md, 'w').write(md)
    print('\n'.join(L[:12]))


if __name__ == '__main__':
    main()
