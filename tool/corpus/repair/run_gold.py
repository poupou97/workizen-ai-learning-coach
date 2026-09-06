#!/usr/bin/env python3
"""Round 5 · Lane A1 driver: run DETECT/REPAIR/VALIDATE/RESTORE over a set of SDM pages.

What it does, in order:
 1. read a baseline pipeline's SDM pages (default `tc2-p2`, the round-4 result);
 2. build a `RepairContext` per text block - original observations from BOTH stacks, the pipeline's own
    disposition and reasons, the book around it (layer D) and the lexicon (layer A);
 3. run the engine; write every step to an append-only ledger;
 4. emit a NEW pipeline's SDM pages (default `tc2-p3`) in which a validated repair is applied and restored,
    a detected-but-unrepaired failure withholds a previously trusted block, and **`text_original` keeps the
    observation** on every block the repair touched. `tc2-p2` is never written to;
 5. score the token-level repair against the gold text (precision / recall / false-correction rate) and the
    block-level restore against the same gold (restore precision, false withheld);
 6. write the per-signal contribution table and the layer-E human review queue.

Usage
  python3 tool/corpus/repair/run_gold.py --baseline tc2-p2 \
      --baseline-out poc-out/round4/pipeline/tc2-p2 \
      --out poc-out/round5/pipeline/tc2-p3 --split dev
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import os
import shutil
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import tc_sdm            # noqa: E402
import tc2_paths         # noqa: E402
import tc2_sdm           # noqa: E402
import tc_score          # noqa: E402

from repair import context as rctx        # noqa: E402
from repair import groups as rgroups      # noqa: E402
from repair import engine, ledger as ledger_mod, measure, model, registry   # noqa: E402
from repair.repairers import column_linearisation, vi_text      # noqa: E402
from repair.signals import human          # noqa: E402
from repair.validators import vi_text as _validator   # noqa: E402
from repair.vi import lexicon as vi_lexicon           # noqa: E402

ROOT = tc2_paths.ROOT
BAI17 = ('06-sgk-khoa-hoc-tu-nhien-6', (61, 62, 63, 64))

#: Lane A3's finding, adopted here: a block withheld because the SGV text is a teacher's and a child may not
#: read it is **faithful but forbidden**. It is not a fidelity failure and it is not repairable, so it never
#: counts as «false withheld». Fidelity and permission are reported as two different things.
PERMISSION_REASONS = frozenset({'teacher_text', 'answer_leak', 'figure_dependent', 'furniture',
                                'figure_text', 'empty_block', 'empty'})


def is_permission_only(reasons):
    rs = [r for r in reasons or ()]
    if not rs:
        return False
    return all(r in PERMISSION_REASONS or r.startswith('page_feature:') for r in rs)


def gold_pages(split='all', gold_dir=None):
    golds = tc_sdm.all_gold() if not gold_dir else [json.load(open(f)) for f in sorted(glob.glob(f'{gold_dir}/*.json'))]
    if split == 'dev':
        golds = [g for g in golds if not g.get('held_out')]
    elif split == 'heldout':
        golds = [g for g in golds if g.get('held_out')]
    return golds


def run(baseline, baseline_out, out_root, split='all', gold_dir=None, config=None, apply_to=None,
        lexicon_dir=None, quiet=False, group_rule=True, linearisation=False):
    lex = vi_lexicon.VietnameseLexicon.load(lexicon_dir) if lexicon_dir else vi_lexicon.load()
    queue = human.ReviewQueue()
    trace = []
    vi_text.configure(config=config or vi_text.Config(), queue=queue, trace=trace)
    column_linearisation.enable(linearisation)

    os.makedirs(out_root, exist_ok=True)
    lg = ledger_mod.Ledger(f'{out_root}/repair-ledger.jsonl',
                           run=dict(lane='a1', baseline=baseline, pipeline=os.path.basename(out_root),
                                    split=split, framework=model.FRAMEWORK_VERSION,
                                    lexicon=lex.meta, plugins=registry.describe()))
    eng = engine.RepairEngine(lg)
    contrib = engine.SignalContribution()
    score = measure.RepairScore()

    golds = gold_pages(split, gold_dir)
    pages = apply_to or [(g['book'], g['page']) for g in golds]
    gold_by = {(g['book'], g['page']): g for g in golds}

    stats = Counter()
    restored_rows, withheld_rows, census, groups_rows = [], [], [], []
    for book, page in pages:
        tc2_paths.set_out_root(baseline_out)
        sdm = rctx.load_sdm(baseline, book, page)
        if sdm is None:
            stats['no_sdm'] += 1
            continue
        doc = rctx.DocumentContext.for_book(book, page)
        ctxs = rctx.contexts_for_page(sdm, lexicon=lex, document=doc, pipeline=baseline)
        gold = gold_by.get((book, page))
        gold_text = {}
        if gold:
            v1 = tc2_sdm.to_v1_sdm(sdm)
            m = tc_score.match(gold, v1)
            for g in gold['blocks']:
                c = m.get(g['id'])
                if c and g.get('text'):
                    gold_text[c['id']] = g['text']

        out_sdm = copy.deepcopy(sdm)
        by_id = {b['id']: b for b in out_sdm['blocks']}
        sdm_by_id = {b['id']: b for b in sdm['blocks']}
        census_index = {}
        for c in ctxs:
            out = eng.run_block(c)
            blk = by_id.get(c.block_id)
            gt = gold_text.get(c.block_id)
            observed = c.primary().value
            final_text = observed
            after = c.disposition
            for cand in out.candidates:
                validated = out.repaired and cand.candidate_id == (out.entries[-1].candidate.candidate_id
                                                                   if out.entries[-1].candidate else None)
                correct = None
                tc = tr = fc = 0
                if gt is not None and validated:
                    correct = measure.block_clean(gt, cand.proposed_value)
                    one = measure.RepairScore()
                    one.add_block(gt, observed, cand.proposed_value, c.block_id)
                    tc, tr, fc = one.changed, one.changed_right, one.false_correction
                contrib.observe(cand, validated=validated, correct=correct,
                                tokens_changed=tc, tokens_right=tr, false_corrections=fc)
            if not out.entries:
                stats['untouched'] += 1
            elif out.repaired and out.restorable:
                eng.restore(out)
                final_text = out.final_value
                after = model.Disposition.TRUSTED
                stats['restored' if c.disposition == model.Disposition.WITHHELD else 'repaired_in_place'] += 1
                if blk is not None:
                    _apply_repair(blk, out)
                if gt is not None:
                    ok = measure.block_clean(gt, final_text)
                    restored_rows.append(dict(block=c.block_id, book=book, page=page, role=c.role,
                                              was=c.disposition, clean=ok,
                                              changed=bool(out.entries[-1].candidate.provenance.get('changed'))))
            else:
                after = model.Disposition.WITHHELD
                stats['withheld_by_repair' if c.disposition == model.Disposition.TRUSTED
                      else 'stayed_withheld'] += 1
                if blk is not None and c.disposition == model.Disposition.TRUSTED:
                    _apply_withhold(blk, out)
                if gt is not None and c.disposition == model.Disposition.TRUSTED:
                    withheld_rows.append(dict(block=c.block_id, book=book, page=page, role=c.role,
                                              clean=measure.block_clean(gt, observed)))
            if gt is not None:
                # Every gold-text block is measured, repaired or not: recall and the false-correction rate
                # need the whole population as their denominator, not just the blocks the repairer touched.
                score.add_block(gt, observed, final_text, c.block_id)
                census_index[c.block_id] = len(census)
                census.append(dict(block=c.block_id, book=book, page=page, role=c.role,
                                   reasons=list(c.withhold_reasons),
                                   before=c.disposition, after=after,
                                   clean_before=measure.block_clean(gt, observed),
                                   clean_after=measure.block_clean(gt, final_text),
                                   changed=(final_text != observed)))
        # ---- Founder defect 8: the group is the unit of disposition. Count the mutilated structures the
        # baseline would serve, then enforce «serve the whole group or none of it».
        gs = rgroups.structural_groups(out_sdm)
        base_servable = {b['id']: (sdm_by_id[b['id']]['trust']['status'] == 'TRUSTED') for b in out_sdm['blocks']
                         if (b.get('text') or '').strip()}
        mut_before = rgroups.mutilated(gs, dict(base_servable))
        now_servable = {b['id']: (b['trust']['status'] == 'TRUSTED') for b in out_sdm['blocks']
                        if (b.get('text') or '').strip()}
        mut_after_repair = rgroups.mutilated(gs, dict(now_servable))
        reasons_add = {}
        changed_g = rgroups.apply_group_rule(gs, now_servable, reasons_add, ledger=lg,
                                             observations_by_id={c.block_id: c.observations for c in ctxs}) \
            if group_rule else {}
        for b in out_sdm['blocks']:
            if b['id'] in changed_g:
                b['trust'] = dict(status='WITHHELD',
                                  reasons=sorted(set(list(b['trust']['reasons']) + reasons_add.get(b['id'], []))))
                b['group'] = dict(group_id=changed_g[b['id']], disposition=model.Disposition.WITHHELD,
                                  rule='serve the whole group or none of it')
                gi = census_index.get(b['id'])
                if gi is not None:
                    census[gi]['after'] = model.Disposition.WITHHELD
                    census[gi]['group_withheld'] = changed_g[b['id']]
        groups_rows.append(dict(book=book, page=page, groups=len(gs),
                                mutilated_baseline=len(mut_before), mutilated_after_repair=len(mut_after_repair),
                                blocks_withheld_by_group_rule=len(changed_g),
                                detail=mut_before[:8]))
        _write_sdm(out_sdm, out_root, book, page, baseline)
        with open(f'{out_root}/repair-dispositions.jsonl', 'a', encoding='utf-8') as fh:
            for b in out_sdm['blocks']:
                if not (b.get('text') or '').strip():
                    continue
                fh.write(json.dumps(dict(block_id=b['id'], book=book, page=page,
                                         role=b['role']['value'], learning=bool(b.get('learning')),
                                         disposition=b.get('disposition'), servable=b.get('servable'),
                                         trust=b['trust']['status'], reasons=b['trust']['reasons'],
                                         repair=b.get('repair')), ensure_ascii=False) + '\n')
    lg.close()
    return dict(stats=dict(stats), score=score, contrib=contrib, queue=queue, ledger=lg, trace=trace,
                restored=restored_rows, withheld=withheld_rows, census=census, groups=groups_rows,
                lexicon=lex.meta)


def ablation_rule(candidate, layer):
    """Would this repair still validate if the named signal layer had never spoken? Re-runs the REAL
    validator on a copy of the candidate with that layer's signals removed - which is the only honest way
    to answer «what does this signal contribute»."""
    stripped = model.replace(candidate, candidate_id='',
                             supporting_signals=tuple(s for s in candidate.supporting_signals
                                                      if s.layer != layer))
    try:
        return _validator.validate(stripped, None).validated
    except Exception:
        return False


def scoreboard(census):
    """The block-level DATA ACCURACY SCOREBOARD, before -> after, over the gold-text blocks.

    `clean` = the block carries no diacritic error against the human-verified gold text over an aligned
    region covering ≥ 80 % of it (`measure.block_clean`); a block whose alignment is too thin to judge is
    counted as `unknown` and never silently as a success."""
    def side(key_disp, key_clean):
        served = [r for r in census if r[key_disp] == model.Disposition.TRUSTED]
        withheld = [r for r in census if r[key_disp] != model.Disposition.TRUSTED]
        permission = [r for r in withheld if is_permission_only(r.get('reasons'))]
        fidelity = [r for r in withheld if not is_permission_only(r.get('reasons'))]
        return dict(served=len(served),
                    correct_served=sum(1 for r in served if r[key_clean] is True),
                    wrong_served=sum(1 for r in served if r[key_clean] is False),
                    unknown_served=sum(1 for r in served if r[key_clean] is None),
                    withheld=len(withheld),
                    withheld_by_permission=len(permission),
                    withheld_by_fidelity=len(fidelity),
                    false_withheld=sum(1 for r in fidelity if r[key_clean] is True),
                    false_withheld_incl_permission=sum(1 for r in withheld if r[key_clean] is True),
                    withheld_unknown=sum(1 for r in withheld if r[key_clean] is None))
    before = side('before', 'clean_before')
    after = side('after', 'clean_after')
    restored = [r for r in census if r['before'] != model.Disposition.TRUSTED
                and r['after'] == model.Disposition.TRUSTED]
    newly_withheld = [r for r in census if r['before'] == model.Disposition.TRUSTED
                      and r['after'] != model.Disposition.TRUSTED]
    rp_n = sum(1 for r in restored if r['clean_after'] is not None)
    rp_k = sum(1 for r in restored if r['clean_after'] is True)
    tones = [r for r in census if list(r.get('reasons') or ()) == ['agree_tones']]
    pool = dict(agree_tones_sole_withholds=len(tones),
                clean=sum(1 for r in tones if r['clean_before'] is True),
                restored=sum(1 for r in tones if r['after'] == model.Disposition.TRUSTED),
                restored_clean=sum(1 for r in tones if r['after'] == model.Disposition.TRUSTED
                                   and r['clean_after'] is True))
    return dict(blocks=len(census), before=before, after=after, agree_tones_pool=pool,
                restored=len(restored), restored_clean=rp_k, restored_judgeable=rp_n,
                restore_precision=(round(rp_k / rp_n, 4) if rp_n else None),
                restore_precision_ci=measure.wilson(rp_k, rp_n),
                newly_withheld=len(newly_withheld),
                newly_withheld_that_were_clean=sum(1 for r in newly_withheld if r['clean_before'] is True),
                newly_withheld_that_were_wrong=sum(1 for r in newly_withheld if r['clean_before'] is False))


def _apply_repair(blk, out):
    """Apply a VALIDATED REPAIR to the projected block. The observation is preserved in `repair.observed`
    and in the ledger; `text_original` keeps what the pipeline had."""
    cand = out.entries[-1].candidate
    if blk.get('text') != out.final_value:
        blk['text_original'] = blk.get('text')
        blk['text'] = out.final_value
    blk['trust'] = dict(status='TRUSTED', reasons=[])
    blk['repair'] = dict(disposition=model.Disposition.VALIDATED_REPAIR, rule_id=cand.rule_id,
                         candidate_id=cand.candidate_id, confidence=round(cand.confidence, 3),
                         supporting_layers=cand.independent_support(),
                         entry_id=out.entries[-1].entry_id,
                         covers_reasons=list(cand.provenance.get('covers_reasons') or ()),
                         changed=bool(cand.provenance.get('changed')))


def _apply_withhold(blk, out):
    blk['trust'] = dict(status='WITHHELD', reasons=sorted(set(list(blk['trust']['reasons']) + ['vi_repair_unresolved'])))
    blk['repair'] = dict(disposition=out.disposition, reasons=list(out.reasons),
                         entry_id=out.entries[-1].entry_id,
                         contradictory_evidence=[x.to_json() for c in out.candidates for x in c.contradicting()])


def _stamp_dispositions(sdm):
    """Every block of the emitted pipeline carries an explicit disposition (Lane A3's request: a gate must
    be able to key on *validation*, never on the absence of a guard - «waiving a guard is not a repair»).
    A block the framework never touched is an ORIGINAL OBSERVATION that the pipeline trusts or withholds;
    only a block with a validated repair is a VALIDATED REPAIR."""
    for b in sdm['blocks']:
        rep = b.get('repair')
        if rep and rep.get('disposition') == model.Disposition.VALIDATED_REPAIR:
            b['disposition'] = model.Disposition.VALIDATED_REPAIR
            b['servable'] = True
        elif b['trust']['status'] == 'TRUSTED':
            b['disposition'] = model.Disposition.ORIGINAL_OBSERVATION
            b['servable'] = True
        else:
            b['disposition'] = (rep or {}).get('disposition') or model.Disposition.WITHHELD
            b['servable'] = False
    return sdm


def _write_sdm(sdm, out_root, book, page, baseline):
    sdm['pipeline_baseline'] = baseline
    sdm['pipeline'] = os.path.basename(out_root)
    sdm['repair_framework'] = model.FRAMEWORK_VERSION
    _stamp_dispositions(sdm)
    for sub in ('sdm', 'sdm-gold'):
        p = f'{out_root}/{sub}/{book}/p{page:03d}.sdm.json'
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump(sdm, open(p, 'w'), ensure_ascii=False)


def copy_attach(baseline_out, out_root):
    """Attachment is untouched by A1; the new pipeline reuses the baseline's verdicts so the scorer's
    attachment column is comparable rather than empty."""
    src, dst = f'{baseline_out}/attach', f'{out_root}/attach'
    if os.path.isdir(src) and not os.path.isdir(dst):
        shutil.copytree(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', default='tc2-p2')
    ap.add_argument('--baseline-out', default=f'{ROOT}/poc-out/round4/pipeline/tc2-p2')
    ap.add_argument('--out', default=f'{ROOT}/poc-out/round5/pipeline/tc2-p3')
    ap.add_argument('--split', default='all', choices=('all', 'dev', 'heldout'))
    ap.add_argument('--gold-dir', default=None)
    ap.add_argument('--bai17', action='store_true', help='also process the Bài 17 pages (no gold text)')
    ap.add_argument('--json', default=None)
    ap.add_argument('--linearisation', action='store_true',
                    help='also run column-linearisation-v1 (Lane C): restore an `agree_text` withhold whose '
                         'text the verifier does read, in order, elsewhere on the page. OFF by default - '
                         'measured restore precision 0.867 on the dev split, which buys coverage with accuracy')
    ap.add_argument('--no-group-rule', action='store_true',
                    help='do NOT enforce «serve the whole group or none of it» (Founder defect 8); '
                         'produces the coverage-maximal variant for comparison')
    a = ap.parse_args()

    apply_to = None
    if a.bai17:
        apply_to = [(BAI17[0], p) for p in BAI17[1]]
    res = run(a.baseline, a.baseline_out, a.out, split=a.split, gold_dir=a.gold_dir, apply_to=apply_to,
              group_rule=not a.no_group_rule, linearisation=a.linearisation)
    copy_attach(a.baseline_out, a.out)
    n = res['queue'].write(f'{a.out}/human-review-queue.jsonl')
    summary = dict(stats=res['stats'], repair=res['score'].summary(),
                   scoreboard=scoreboard(res['census']),
                   signal_contribution=res['contrib'].table(validator_rule=ablation_rule),
                   signal_contribution_by_signal=res['contrib'].by_signal(),
                   review_queue=dict(rows=n, by_kind=res['queue'].counts()),
                   structural_groups=dict(
                       groups=sum(g['groups'] for g in res['groups']),
                       mutilated_in_baseline=sum(g['mutilated_baseline'] for g in res['groups']),
                       mutilated_after_repair=sum(g['mutilated_after_repair'] for g in res['groups']),
                       blocks_withheld_by_group_rule=sum(g['blocks_withheld_by_group_rule'] for g in res['groups'])),
                   lexicon=res['lexicon'])
    json.dump(dict(summary=summary, restored=res['restored'], withheld=res['withheld'],
                   census=res['census'], groups=res['groups'],
                   repair_rows=res['score'].rows, trace=res['trace'][:4000]),
              open(a.json or f'{a.out}/repair-report.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
