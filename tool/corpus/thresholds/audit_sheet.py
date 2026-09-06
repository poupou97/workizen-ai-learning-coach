#!/usr/bin/env python3
"""STEP D — the blind audit worklist, and the sealed key that makes it blind.

Round 7 builds this and does not run it on real content.

WHAT THE ANNOTATOR MUST NOT SEE
-------------------------------
Whether a row was admitted. If the sheet says «this one is trusted», every subsequent judgement
is anchored, and the false-trust rate measures the anchor. Round 3's audit already learned the
weaker version of this lesson — its OCR-similarity pre-check was «shown as a hint, never as a
verdict» — and round 6 learned the stronger one, when WS-D's keyword canary fired on legitimate
book text and taught the reader that red is normal.

So the worklist carries the served text, the page reference and nothing else; the admission
status goes to a SEALED KEY written to a separate file. `measure.py` joins them afterwards. The
worklist is shuffled with a recorded seed so that admitted and withheld rows are interleaved and
neither position nor order leaks the gate.

BOTH SIDES ARE AUDITED
----------------------
Admitted rows measure false trust and teaching-critical error. Withheld rows measure
OVER-withholding — which round 5's 97-row audit found to be the LARGER pool (19 of 30 withheld
rows were refused wrongly) and which round 5's defect 8 proved is not a safe default: withholding
one option of a multiple choice leaves the served question wrong, not merely smaller. A protocol
that audits only what a threshold admits cannot see the harm the threshold causes by refusing.

The six verdict fields are the round-3 false-trust audit protocol's, unchanged, so the numbers
this produces are comparable with the audits already published rather than a new scale.
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

#: `FALSE-TRUST-AUDIT-PROTOCOL.md`, reproduced field for field.
VERDICTS = ('display_fidelity', 'teaching_critical_fidelity', 'reading_order', 'role_fidelity',
            'lesson_attachment', 'false_trust')
VALUES = ('OK', 'WRONG', 'UNSURE', 'NA')

#: Fields the annotator may see. Everything else — guards, agreement, role confidence, and above
#: all the admission decision — is withheld, because each of them is an invitation to agree with
#: the machine instead of with the page.
VISIBLE = ('row_id', 'sourceDocumentId', 'lessonNo', 'page_pdf', 'printed_page', 'text',
           'crop_path')


def build(rows, admitted_ids, seed):
    """(worklist, sealed_key). `rows` are the population's evidence rows; `admitted_ids` the
    row ids a policy admitted — which is exactly what the worklist must not reveal."""
    rng = random.Random(seed)
    order = list(rows)
    rng.shuffle(order)
    worklist, key = [], {}
    for i, r in enumerate(order):
        rid = r.get('row_id') or hashlib.sha256(
            json.dumps([r.get('sourceDocumentId'), r.get('lessonNo'), r.get('block_id')],
                       sort_keys=True).encode()).hexdigest()[:16]
        item = {k: r.get(k) for k in VISIBLE if k != 'row_id'}
        item['row_id'] = rid
        item['sheet_position'] = i + 1
        for v in VERDICTS:
            item[v] = None
        item['display_error_class'] = None
        item['teaching_critical_class'] = None
        item['annotator'] = None
        worklist.append(item)
        key[rid] = dict(admitted=rid in admitted_ids, served=bool(r.get('_served')),
                        lessonNo=r.get('lessonNo'),
                        sourceDocumentId=r.get('sourceDocumentId'))
    return worklist, dict(schema='blind-audit-sealed-key-v1', seed=seed,
                          n=len(worklist), key=key)


def main():
    ap = argparse.ArgumentParser(description='STEP D — blind audit worklist + sealed key')
    ap.add_argument('--evidence', required=True)
    ap.add_argument('--admitted', required=True,
                    help='admitted.jsonl from apply.py; its row ids become the sealed key')
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--out-dir', required=True)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.evidence, encoding='utf-8')]
    adm = {json.loads(l).get('row_id') for l in open(a.admitted, encoding='utf-8')}
    worklist, key = build(rows, adm, a.seed)
    os.makedirs(a.out_dir, exist_ok=True)
    wl = os.path.join(a.out_dir, 'worklist.jsonl')
    with open(wl, 'w', encoding='utf-8') as fh:
        for w in worklist:
            fh.write(json.dumps(w, ensure_ascii=False) + '\n')
    kp = os.path.join(a.out_dir, 'SEALED-KEY.json')
    json.dump(key, open(kp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # A worklist that leaks the answer is worse than no worklist. Check, do not assume.
    leaked = [k for w in worklist for k in w
              if k in ('admitted', 'trusted', '_served', 'guards', 'role_confidence')]
    assert not leaked, f'worklist leaks the gate: {sorted(set(leaked))}'
    print(f'{len(worklist)} rows -> {wl}\nsealed key -> {kp} '
          f'({sum(1 for v in key["key"].values() if v["admitted"])} admitted, hidden)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
