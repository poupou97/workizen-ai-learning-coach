#!/usr/bin/env python3
"""Build the per-block EVIDENCE rows the trust-gate simulator runs on.

An evidence row is a frozen fact sheet about one block: what the pipeline could observe
about it (agreement, OCR confidence, role, guards, colour, geometry) and what is actually
true of it (measured against gold, or judged by an annotator against the page render).
The simulator never looks at the pipeline again — it only re-decides these rows.

GOLD PLANE (`build_gold`)
  Input : a directory of SDM pages (`.../sdm-gold/<book>/pNNN.sdm.json`) written by
          `tc2_sdm.py`, plus the gold directory (`tool/corpus/tc_gold`).
  Rows  : every gold LEARNING block that carries an anchor — matched or not. An unmatched
          gold block can never be served, so it is a permanent coverage loss and is kept
          in the denominator (this is exactly how `tc_score` computes coverage/TLSR).
  Truth : `tc_score.score`'s own wrongness definition — cer > 0.10 with >= 3 edits, splice,
          non-question served as QUESTION, same-column order inversion. The four are
          reproduced here block by block and then ASSERTED equal, per page, to the
          aggregates `tc_score.score` returns. If the two ever drift the extractor raises;
          the numbers in the report cannot silently stop matching the published scoreboard.

AUDIT PLANE (`build_audit`)
  Input : the annotated JSONL files of the false-trust audits.
  Truth : the annotator's per-class verdicts (display / teaching-critical / reading order /
          role / attachment / false trust). Signals are only what the audit row recorded.

Usage
  python3 tool/corpus/thresholds/evidence.py gold  --sdm <dir> --gold-dir <dir> --out <jsonl>
  python3 tool/corpus/thresholds/evidence.py audit --annotated <jsonl> [--annotated ...] --out <jsonl>
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HERE)
sys.path.insert(0, CORPUS)

import tc_sdm      # noqa: E402
import tc_score    # noqa: E402
import tc2_sdm     # noqa: E402

ROOT = tc_sdm.ROOT
EVIDENCE_SCHEMA = 'lane-a3-evidence-v1'

# Teaching-critical, on the gold plane, is defined ONLY from the pipeline's own critical
# teaching-error classes so the number is auditable against `cte` in the gold scoreboard:
#   · `corrupted_data`          — the gold digit sequence is not delivered
#   · `nonquestion_as_question` / `heading_as_question` — a non-question asked as a question
# It is deliberately NARROWER than the audit protocol's teaching-critical class (which also
# counts truncation, contamination and term-level tone slips). The two planes are not summed.


def _wrongness(gold, v1, m, gid, gb):
    """Per-block wrongness, replicating `tc_score.score`'s trust loop exactly.

    Returns {gold_id: dict(wrong=[...], digits_wrong=bool|None, as_question=bool)}.
    """
    anchor_keys = {g['id']: ' '.join(tc_score.norm_key((g.get('text') or g['anchor']).split('\n')[0]).split()[:6])
                   for g in gold['blocks'] if g.get('anchor')}
    anchor_keys = {k: v for k, v in anchor_keys.items() if len(v.split()) >= 5}
    self_keys = {g['id']: tc_score.norm_key(g.get('text') or g.get('anchor') or '') for g in gold['blocks']}

    def foreign_in(cblock, gself):
        t = tc_score.norm_key(cblock['text'])
        out = []
        for gidd, k in anchor_keys.items():
            if gidd == gself['id']:
                continue
            og = gb[gidd]
            if tc_score._contains(self_keys.get(gself['id'], ''), k):
                continue
            if tc_score._contains(t, k) and (og.get('column') != gself.get('column')
                                             or gid.get(gidd) != gid.get(gself['id'])
                                             or og['role'] in ('sidebar', 'caption', 'footnote', 'figure_label', 'speech_bubble')):
                out.append(gidd)
        return out

    enum_re = tc_score.re.compile(r'^\s*(?:(?:HĐ|Bài|Bước)\s*\d+[.:]?|\d{1,2}[.)]|[a-dA-D][.)])\s*')
    learning = [g for g in gold['blocks'] if g['role'] in tc_sdm.LEARNING_ROLES and g.get('anchor')]
    out = {}
    for g in learning:
        c = m.get(g['id'])
        if not c:
            out[g['id']] = dict(wrong=[], digits_wrong=None, as_question=False, matched=False)
            continue
        wrong = []
        if g.get('_cer') is not None and g['_cer'] > 0.10 and g.get('_edits', 0) >= 3:
            wrong.append('cer')
        if g.get('contiguous') and foreign_in(c, g):
            wrong.append('splice')
        as_q = c['role'] == 'QUESTION' and g['role'] in tc_sdm.NOT_A_QUESTION
        if as_q:
            wrong.append('as_question')
        for h in learning:
            if h['id'] in m and h is not g and h.get('column') == g.get('column') \
                    and gid.get(h['id']) == gid.get(g['id']) and m[h['id']]['order'] != c['order']:
                if (h['order'] < g['order']) != (m[h['id']]['order'] < c['order']):
                    wrong.append('order')
                    break
        # digits: the `corrupted_data` critical-teaching class, computed on the same
        # extension rule the scorer uses for a gold block spanning several pipeline blocks
        digits_wrong = None
        if g.get('text'):
            ct = c['text']
            if len(tc_score.nfc(ct)) < 0.7 * len(tc_score.nfc(g['text'])):
                for c2 in v1['blocks']:
                    if c['order'] < c2['order'] <= c['order'] + 8 and c2['text']:
                        ct += ' ' + c2['text']
                        if len(tc_score.nfc(ct)) >= len(tc_score.nfc(g['text'])):
                            break
            gd = tc_score.digits_seq(enum_re.sub('', tc_score.nfc(g['text']), count=1))
            if gd:
                cd = tc_score.digits_seq(enum_re.sub('', tc_score.nfc(ct), count=1))
                digits_wrong = not (gd == cd[:len(gd)] or all(d in cd for d in gd))
        out[g['id']] = dict(wrong=wrong, digits_wrong=digits_wrong, as_question=as_q, matched=True)
    return out


def gold_page_rows(gold, sdm):
    """Evidence rows for one gold page. Raises AssertionError if the per-block truth does
    not reproduce `tc_score.score`'s page aggregates."""
    v1 = tc2_sdm.to_v1_sdm(sdm)
    r = tc_score.score(gold, v1)          # populates g['_cer'] / g['_edits'] on gold blocks
    m = tc_score.match(gold, v1)
    gid = tc_score.group_of(gold)
    gb = {g['id']: g for g in gold['blocks']}
    by_id = {b['id']: b for b in sdm['blocks']}
    truth = _wrongness(gold, v1, m, gid, gb)
    feats = sdm.get('features') or {}
    rows = []
    trusted_n = wrong_trusted = safe_reject = 0
    for g in [g for g in gold['blocks'] if g['role'] in tc_sdm.LEARNING_ROLES and g.get('anchor')]:
        t = truth[g['id']]
        c = m.get(g['id'])
        row = dict(
            schema=EVIDENCE_SCHEMA, plane='gold',
            book=gold['book'], page=gold['page'], printed_page=gold.get('printed_page'),
            doc_type=gold.get('docType') or ('SGV' if '-sgv-' in gold['book'] else 'SGK'),
            gold_set=gold.get('gold_set', 'tc-v1'), held_out=bool(gold.get('held_out')),
            subject=gold.get('subject'), grade=gold.get('grade'),
            gold_id=g['id'], gold_role=g['role'], gold_has_text=bool(g.get('text')),
            matched=t['matched'],
            truth_wrong=t['wrong'], truth_wrong_any=bool(t['wrong']),
            truth_digits_wrong=t['digits_wrong'], truth_as_question=t['as_question'],
            truth_teaching_critical=bool(t['digits_wrong']) or t['as_question'],
            cer=g.get('_cer'), cer_notone=g.get('_cer_notone'), edits=g.get('_edits'),
            page_color_heavy=bool(feats.get('color_heavy')), page_diagram=bool(feats.get('diagram')),
        )
        if c is None:
            row.update(block_id=None, pipeline_trusted=False, pipeline_status='UNMATCHED',
                       guards=[], role_value=None, role_coarse=None, role_confidence=None,
                       role_method=None, role_conflict=None, text_sim=None, order_ok=None,
                       tone_disagreements=None, ocr_conf=None, colour_share=None,
                       refers_figure=None, learning=None, text_len=0)
        else:
            ob = by_id.get(c['id'], {})
            ag = ob.get('agreement') or {}
            ro = ob.get('role') or {}
            col = ob.get('colour') or {}
            trusted = c['trusted'] is True
            row.update(
                block_id=c['id'], pipeline_trusted=trusted,
                pipeline_status=(ob.get('trust') or {}).get('status'),
                guards=sorted(x for x in (c.get('reasons') or []) if x != 'enumerator_restored'),
                role_value=ro.get('value'), role_coarse=ro.get('coarse'),
                role_confidence=ro.get('confidence'), role_method=ro.get('method'),
                role_conflict=bool(ro.get('conflict')),
                text_sim=ag.get('text_sim'), order_ok=ag.get('order_ok'),
                tone_disagreements=len(ag.get('tone_disagreements') or []),
                ocr_conf=ob.get('ocr_conf'), colour_share=col.get('share'),
                refers_figure=bool(ob.get('refers_figure')), learning=bool(ob.get('learning')),
                text_len=len(ob.get('text') or ''))
            if trusted:
                trusted_n += 1
                if t['wrong']:
                    wrong_trusted += 1
            else:
                safe_reject += 1
        rows.append(row)
    assert r['learning_blocks'] == len(rows), f"{gold['book']} p{gold['page']}: learning {r['learning_blocks']} != rows {len(rows)}"
    assert r['trusted_blocks'] == trusted_n, f"{gold['book']} p{gold['page']}: trusted {r['trusted_blocks']} != {trusted_n}"
    assert r['false_trusted'] == wrong_trusted, f"{gold['book']} p{gold['page']}: false_trusted {r['false_trusted']} != {wrong_trusted}"
    assert r['safe_rejected'] == safe_reject, f"{gold['book']} p{gold['page']}: safe_rejected {r['safe_rejected']} != {safe_reject}"
    return rows


def build_gold(sdm_dir, gold_dir):
    rows = []
    pages = 0
    for f in sorted(glob.glob(os.path.join(sdm_dir, '*', 'p*.sdm.json'))):
        sdm = json.load(open(f))
        gp = os.path.join(gold_dir, f"{sdm['book']}-p{sdm['page']:03d}.json")
        if not os.path.exists(gp):
            continue
        rows += gold_page_rows(json.load(open(gp)), sdm)
        pages += 1
    return rows, pages


# ------------------------------------------------------------------ audit plane
AUDIT_CLASSES = ('display_fidelity', 'teaching_critical_fidelity', 'reading_order',
                 'role_fidelity', 'lesson_attachment', 'false_trust')


def audit_rows(path, source_name):
    rows = []
    with open(path) as fh:
        lines = fh.readlines()
    for line in lines:
        a = json.loads(line)
        pre = a.get('precheck') or {}
        src = a.get('source') or {}
        verdicts = {k: a.get(k) for k in AUDIT_CLASSES}
        derived = any(verdicts.get(k) == 'WRONG'
                      for k in ('display_fidelity', 'teaching_critical_fidelity', 'reading_order',
                                'role_fidelity', 'lesson_attachment'))
        rows.append(dict(
            schema=EVIDENCE_SCHEMA, plane='audit', audit_source=source_name,
            sample_id=a.get('sampleId'), family=a.get('family'), book=a.get('book'),
            grade=a.get('grade'), lesson=a.get('lesson'), subject=a.get('subject'),
            page_pdf=a.get('pagePdf'), kind=a.get('kind'), pack_version=a.get('packVersion'),
            layout_family=a.get('layoutFamily'),
            served_as_trusted=bool(a.get('servedAsTrusted')),
            pipeline_trusted=bool(a.get('servedAsTrusted')),
            guards=sorted(src.get('reasons') or []),
            pipeline_status=src.get('status'),
            role_confidence=a.get('roleConfidence'),
            text_sim=pre.get('ocrSim'), tone_only=pre.get('toneOnly'),
            enumerator_dropped=bool(pre.get('enumeratorDropped')),
            has_math=bool(pre.get('hasMath')), has_numbers=bool(pre.get('hasNumbers')),
            multi_line=bool(pre.get('multiLine')),
            page_in_lesson_range=pre.get('pageInLessonRange'),
            sdm_status=pre.get('sdmStatus'), sdm_role=pre.get('sdmRole'),
            text_len=len(a.get('text') or ''),
            **{f'verdict_{k}': verdicts[k] for k in AUDIT_CLASSES},
            truth_wrong_any=derived,
            truth_teaching_critical=(verdicts.get('teaching_critical_fidelity') == 'WRONG'),
            annotator=a.get('reviewer')))
    return rows


def main():
    ap = argparse.ArgumentParser(description='build trust-gate evidence rows (research only)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('gold')
    g.add_argument('--sdm', required=True, help='sdm-gold directory of a pipeline run')
    g.add_argument('--gold-dir', default=os.path.join(CORPUS, 'tc_gold'))
    g.add_argument('--out', required=True)
    a = sub.add_parser('audit')
    a.add_argument('--annotated', action='append', required=True,
                   help='NAME=PATH of an annotated audit JSONL (repeatable)')
    a.add_argument('--out', required=True)
    ns = ap.parse_args()
    if ns.cmd == 'gold':
        rows, pages = build_gold(ns.sdm, ns.gold_dir)
        note = f'{pages} gold pages'
    else:
        rows = []
        for spec in ns.annotated:
            name, _, path = spec.partition('=')
            rows += audit_rows(path or name, name if path else os.path.basename(name))
        note = f'{len(set(r["audit_source"] for r in rows))} audit files'
    os.makedirs(os.path.dirname(os.path.abspath(ns.out)), exist_ok=True)
    with open(ns.out, 'w') as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'{len(rows)} evidence rows ({note}) → {ns.out}')


if __name__ == '__main__':
    main()
