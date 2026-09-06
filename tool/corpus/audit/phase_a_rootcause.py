#!/usr/bin/env python3
"""PHASE A — bounded root-cause audit of the teaching-critical errors in the SERVED set.

Founder order 47 §PHASE A. For every block the round-5/round-7 evidence plane marks
`pipeline_trusted AND truth_teaching_critical`, walk the whole chain

    source -> geometry -> SDM block -> recognition -> repair -> role -> serving

and record, at each stage, a MEASUREMENT that discriminates between the six root-cause
classes. The classification is never read off the final string: a wrong character in the
served text is born either at recognition or at a boundary that split a token, and those
are different classes with different fixes.

The probes, and what each one settles
-------------------------------------
MATCH INTEGRITY   Did the *evaluation* match this gold block to the block the pipeline
                  actually produced for it? `tc_score.match` is not injective and falls back
                  to a 1-token containment test, so a short gold anchor can be attached to an
                  unrelated block. A row whose match has IoU 0 while a much better candidate
                  exists is a measurement artefact, not a pipeline error, and must be reported
                  as one rather than classified.

GEOMETRY          How many SDM blocks have their centre inside the gold block's box? >1 means
                  the printed block was split, and the split is a candidate cause for anything
                  missing from the tail of the served text.

RECOGNITION       Three independent layers hold a reading of the page: the OCR line layer
                  (`poc-out/graph/ocr-body`), Docling+ocrmac (the text the pipeline serves)
                  and the XY-cut verifier. For every glyph the served text lost, ask each
                  layer whether it read it. Present in a layer -> the glyph was recognised and
                  something downstream lost it (boundary / composition / ordering). Present in
                  none -> recognition.

ROLE COUNTERFACTUAL
                  Re-run `tc2_sdm.assign_role` on the same block with (a) the gold text, i.e.
                  perfect recognition, and (b) the concatenated text of every SDM block inside
                  the gold box, i.e. perfect segmentation. A role that is still wrong under
                  both is a role-layer defect and nothing upstream explains it. This is the
                  probe that stops a role error being blamed on a split that happens to be
                  next to it.

D4: this script READS the corpus and prints values only to `--detail`, which must stay out of
git. The `--out` census carries counts, classes and booleans and no book content.

ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION: with no corpus the script exits non-zero and
says UNVERIFIED. It never prints a clean summary over an empty population.
"""
import argparse
import copy
import difflib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HERE)
sys.path.insert(0, CORPUS)

import tc_score   # noqa: E402
import tc_sdm     # noqa: E402
import tc2_sdm    # noqa: E402

ENUM_RE = re.compile(r'^\s*(?:(?:HĐ|Bài|Bước)\s*\d+[.:]?|\d{1,2}[.)]|[a-dA-D][.)])\s*')
#: A match with no geometric overlap at all, made on a key this short, is the matcher's
#: 1-token fallback rather than an identification of the block.
ARTEFACT_MAX_LEVEL = 2


def centre_in(bb, box, pad=0.005):
    if not bb or not box:
        return False
    cx, cy = bb[0] + bb[2] / 2, bb[1] + bb[3] / 2
    return (box[0] - pad <= cx <= box[0] + box[2] + pad
            and box[1] - pad <= cy <= box[1] + box[3] + pad)


def match_trace(gold, v1, g):
    """Reproduce `tc_score.match`'s decision for ONE gold block and report how it was made."""
    src = g.get('text') or g.get('anchor') or ''
    toks = tc_score.norm_key(src.split('\n')[0]).split()
    if not toks and g.get('anchor'):
        toks = tc_score.norm_key(g['anchor']).split()
    levels = [n for n in (7, 6, 5, 4, 3) if len(toks) >= n] or ([len(toks)] if 1 <= len(toks) < 3 else [])
    ckeys = [(x, tc_score.norm_key(x['text'])) for x in v1['blocks']]
    for n in levels:
        k = ' '.join(toks[:n])
        found = [x for x, ck in ckeys if tc_score._contains(ck, k)]
        if found:
            return len(toks), n, len(found)
    return len(toks), None, None


def layers_reading(book, page, gold_bbox):
    """The three recognition layers, restricted to the gold block's box."""
    lines = tc2_sdm.ocr_lines(book, page)
    ocr = [l for l in lines if centre_in([l['x'], l['y'], l['w'], l['h']], gold_bbox)]
    rawD, _ = tc2_sdm.load_raw('docling-ocrmac', book, page, 'tc2-p2')
    rawX, _ = tc2_sdm.load_raw('current-xycut', book, page, 'tc2-p2')
    docling = []
    if rawD:
        blocks, _, _ = tc2_sdm.adapt_docling_v2(rawD['result'])
        docling = [b for b in blocks if centre_in(b.get('bbox'), gold_bbox)]
    xycut = []
    if rawX:
        X, _ = tc_sdm.adapt_current_xycut(rawX['result'])
        xycut = [b for b in X if centre_in(b.get('bbox'), gold_bbox)]
    return dict(ocr_line=[l['text'] for l in ocr],
                docling=[b['text'] for b in docling],
                xycut=[(b.get('text') or '') for b in xycut])


def role_counterfactual(book, page, rank, gold_text, merged_text):
    """assign_role on the SAME block with perfect recognition / perfect segmentation."""
    cap = []
    orig = tc2_sdm.assign_role

    def patched(b, ctx):
        r = orig(b, ctx)
        cap.append((copy.deepcopy(b), copy.deepcopy(ctx), r))
        return r

    tc2_sdm.assign_role = patched
    try:
        tc2_sdm.build_page(book, page, pipeline='tc2-p2')
    finally:
        tc2_sdm.assign_role = orig
    if rank >= len(cap):
        return None
    b, ctx, actual = cap[rank]
    out = dict(actual=actual[0], actual_evidence=actual[3])
    for key, txt in (('gold_text', gold_text), ('merged_text', merged_text)):
        if not txt:
            out[key] = None
            continue
        b2 = copy.deepcopy(b)
        b2['text'] = txt.replace('\n', ' ')
        out[key] = tc2_sdm.assign_role(b2, ctx)[0]
    return out


def audit(evidence_path, sdm_dir, gold_dir):
    rows = [json.loads(l) for l in open(evidence_path)]
    served = [r for r in rows if r['pipeline_trusted']]
    pop = [r for r in served if r['truth_teaching_critical']]
    # ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION.
    if not rows:
        raise SystemExit('UNVERIFIED: the evidence file is empty')
    if not served:
        raise SystemExit('UNVERIFIED: no served rows — the population this audit is about is absent')
    if not pop:
        raise SystemExit('UNVERIFIED: no teaching-critical row in the served set; '
                         'this audit has no subject and MUST NOT report a clean result')
    cases = []
    for r in sorted(pop, key=lambda r: (r['book'], r['page'], r['gold_id'])):
        book, page, gid = r['book'], r['page'], r['gold_id']
        sdm = json.load(open(f'{sdm_dir}/{book}/p{page:03d}.sdm.json'))
        gold = json.load(open(f'{gold_dir}/{book}-p{page:03d}.json'))
        v1 = tc2_sdm.to_v1_sdm(sdm)
        tc_score.score(gold, v1)          # populates _cer / _edits
        m = tc_score.match(gold, v1)
        g = [x for x in gold['blocks'] if x['id'] == gid][0]
        c = m[gid]
        ob = [b for b in sdm['blocks'] if b['id'] == c['id']][0]
        rank = int(ob['id'].rsplit(':', 1)[1])
        gbb, cbb = g.get('bbox'), ob['bbox']
        ntoks, lvl, ncand = match_trace(gold, v1, g)
        alts = sorted(((tc_score.iou(gbb, b['bbox']), b) for b in sdm['blocks'] if b['bbox']),
                      key=lambda t: -t[0]) if gbb else []
        best_alt = alts[0] if alts else (0.0, None)
        sharing = sorted(k for k, v in m.items() if v is c)
        inside = [b for b in sdm['blocks'] if b['bbox'] and centre_in(b['bbox'], gbb)] if gbb else []
        gt = g.get('text') or ''
        ct = ob['text']
        ext = []
        if gt and len(tc_score.nfc(ct)) < 0.7 * len(tc_score.nfc(gt)):
            for c2 in v1['blocks']:
                if c['order'] < c2['order'] <= c['order'] + 8 and c2['text']:
                    ct += ' ' + c2['text']
                    ext.append(c2['id'].rsplit(':', 1)[1])
                    if len(tc_score.nfc(ct)) >= len(tc_score.nfc(gt)):
                        break
        gd = tc_score.digits_seq(ENUM_RE.sub('', tc_score.nfc(gt), count=1)) if gt else []
        cd = tc_score.digits_seq(ENUM_RE.sub('', tc_score.nfc(ct), count=1)) if gt else []
        ops = []
        if gt:
            sm = difflib.SequenceMatcher(None, tc_score.nfc(gt), tc_score.nfc(ct), autojunk=False)
            ops = [dict(tag=t, gold=tc_score.nfc(gt)[i1:i2], cand=tc_score.nfc(ct)[j1:j2], at=i1)
                   for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']
        merged = ' '.join(b['text'] for b in inside if b['text'])
        cases.append(dict(
            book=book, page=page, gold_id=gid, block_id=ob['id'],
            gold_role=g['role'], served_role=ob['role']['value'], served_coarse=ob['role']['coarse'],
            role_method=ob['role']['method'], role_confidence=ob['role']['confidence'],
            role_evidence=ob['role']['evidence'], verifier_role=(ob.get('agreement') or {}).get('verifier_role'),
            native_label=ob.get('native_label'), trust=ob['trust']['status'], guards=ob['guards'],
            trigger_digits=bool(r['truth_digits_wrong']), trigger_as_question=bool(r['truth_as_question']),
            cer=r['cer'], edits=r['edits'], text_sim=r['text_sim'],
            match=dict(anchor_tokens=ntoks, level=lvl, candidates_with_key=ncand,
                       iou=round(tc_score.iou(gbb, cbb), 4) if gbb else None,
                       best_alternative_iou=round(best_alt[0], 4),
                       best_alternative_block=best_alt[1]['id'] if best_alt[1] else None,
                       best_alternative_role=best_alt[1]['role']['value'] if best_alt[1] else None,
                       gold_blocks_sharing_candidate=sharing),
            geometry=dict(sdm_blocks_in_gold_bbox=[b['id'].rsplit(':', 1)[1] for b in inside],
                          gold_text_len=len(gt), served_text_len=len(ob['text']),
                          extended_over=ext),
            digits=dict(gold_tokens=len(gd), served_tokens=len(cd),
                        missing=len([d for d in gd if d not in cd]),
                        diff_ops=[dict(tag=o['tag'], gold_len=len(o['gold']), cand_len=len(o['cand']),
                                       at=o['at'], gold_has_digit=bool(re.search(r'\d', o['gold'])))
                                  for o in ops]),
            _detail=dict(gold_text=gt, served_text=ob['text'], extended_text=ct,
                         gold_digits=gd, served_digits=cd, ops=ops,
                         layers=layers_reading(book, page, gbb) if gbb else None,
                         merged_text=merged),
            role_cf=role_counterfactual(book, page, rank, gt, merged),
        ))
    return dict(evidence=os.path.basename(evidence_path),
                rows=len(rows), served=len(served), teaching_critical=len(pop),
                distinct_served_blocks=len({c['block_id'] for c in cases}),
                cases=cases)


def main():
    ap = argparse.ArgumentParser(description='Phase A root-cause audit (research only)')
    ap.add_argument('--evidence', required=True)
    ap.add_argument('--sdm', required=True)
    ap.add_argument('--gold-dir', default=os.path.join(CORPUS, 'tc_gold'))
    ap.add_argument('--out', required=True, help='D4-safe census (no book content)')
    ap.add_argument('--detail', help='local-only dump WITH readings; never commit it')
    ns = ap.parse_args()
    for p in (ns.evidence, ns.sdm, ns.gold_dir):
        if not os.path.exists(p):
            raise SystemExit(f'UNVERIFIED: {p} is absent — this audit cannot run without the corpus')
    res = audit(ns.evidence, ns.sdm, ns.gold_dir)
    if ns.detail:
        with open(ns.detail, 'w') as fh:
            json.dump(res, fh, ensure_ascii=False, indent=1)
    safe = copy.deepcopy(res)
    for c in safe['cases']:
        c.pop('_detail', None)
    os.makedirs(os.path.dirname(os.path.abspath(ns.out)) or '.', exist_ok=True)
    with open(ns.out, 'w') as fh:
        json.dump(safe, fh, ensure_ascii=False, indent=1)
    print(f"{res['teaching_critical']} teaching-critical rows over {res['served']} served "
          f"({res['distinct_served_blocks']} distinct served blocks) → {ns.out}")


if __name__ == '__main__':
    main()
