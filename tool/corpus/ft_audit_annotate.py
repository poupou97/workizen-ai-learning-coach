#!/usr/bin/env python3
"""Round 3 · A2 — ANNOTATION LOG for the false-trust audit. Records are appended to an append-only
JSONL log (one line per (sampleId, pass)); `merge` folds the LAST record per sampleId into the
pre-checked sample and writes the annotated JSONL the scorer reads. Nothing here decides a rate.

Record fields (protocol §3 + Round-3 extensions):
  d    display_fidelity            OK | WRONG | UNSURE | NA
  tc   teaching_critical_fidelity  OK | WRONG | UNSURE | NA
  role role_fidelity               OK | WRONG | UNSURE | NA
  att  lesson_attachment           OK | WRONG | UNSURE | NA   (judged per activity; copied to siblings)
  ft   false_trust                 OK | WRONG | UNSURE | NA   (annotator's overall verdict)
  ro   reading_order               OK | WRONG | UNSURE | NA   (NA when the row is a single line)
  cls  display_error_class         tone_mark | ocr_char | enumerator_dropped | bullet_dropped | splice |
                                   truncated | extra_text | math_flattened | table_flattened | figure_text |
                                   layout_merge | '' (free text allowed, comma-separated)
  tcc  teaching_critical_class     number | fraction | formula | unit | term | negation | sequence | ''
  n    notes

Usage:
  python3 tool/corpus/ft_audit_annotate.py add  --log <log.jsonl> --reviewer "<name>" --json '{"s…-0001": {"d":"OK",…}, …}'
  python3 tool/corpus/ft_audit_annotate.py add  --log <log.jsonl> --reviewer "<name>" --file records.json
  python3 tool/corpus/ft_audit_annotate.py merge --log <log.jsonl> --sample <precheck.jsonl> --out <annotated.jsonl>
  python3 tool/corpus/ft_audit_annotate.py status --log <log.jsonl> --sample <precheck.jsonl>
"""
import argparse
import collections
import json
import os
import sys
from datetime import datetime, timezone

VALUES = ('OK', 'WRONG', 'UNSURE', 'NA')
FIELDS = {'d': 'display_fidelity', 'tc': 'teaching_critical_fidelity', 'role': 'role_fidelity', 'att': 'lesson_attachment',
          'ft': 'false_trust', 'ro': 'reading_order'}
EXTRA = {'cls': 'display_error_class', 'tcc': 'teaching_critical_class', 'n': 'notes'}


def validate(sid, rec):
    for k in FIELDS:
        v = (rec.get(k) or '').strip().upper()
        if v and v not in VALUES:
            raise SystemExit(f'{sid}: {k}={rec.get(k)!r} not in {VALUES}')
    if rec.get('ft', '').strip().upper() == 'WRONG' and not any((rec.get(k) or '').strip().upper() == 'WRONG' for k in ('d', 'tc', 'role', 'att')):
        # a false-trust verdict without a named cause is allowed but must say why
        if not (rec.get('n') or '').strip():
            raise SystemExit(f'{sid}: ft=WRONG with no criterion WRONG and no note')


def cmd_add(a):
    recs = json.loads(open(a.file, encoding='utf-8').read()) if a.file else json.loads(a.json)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(a.log, 'a', encoding='utf-8') as f:
        for sid, rec in recs.items():
            validate(sid, rec)
            f.write(json.dumps(dict(sampleId=sid, reviewer=a.reviewer, reviewedAt=now, **{k: rec.get(k, '') for k in list(FIELDS) + list(EXTRA)}), ensure_ascii=False) + '\n')
    print(f'{len(recs)} records appended → {a.log}')


def load_log(path):
    last = {}
    if os.path.exists(path):
        for l in open(path, encoding='utf-8'):
            if l.strip():
                r = json.loads(l); last[r['sampleId']] = r
    return last


def cmd_merge(a):
    rows = [json.loads(l) for l in open(a.sample, encoding='utf-8') if l.strip()]
    last = load_log(a.log)
    # lesson attachment is judged once per activity: propagate the first explicit value to siblings
    att_by_act = {}
    for r in rows:
        rec = last.get(r['sampleId'])
        v = (rec or {}).get('att', '').strip().upper()
        if v and r.get('activityId') not in att_by_act:
            att_by_act[r['activityId']] = v
    n = 0
    with open(a.out, 'w', encoding='utf-8') as f:
        for r in rows:
            rec = last.get(r['sampleId'])
            if rec:
                n += 1
                for k, field in FIELDS.items():
                    r[field] = (rec.get(k) or '').strip().upper()
                for k, field in EXTRA.items():
                    r[field] = rec.get(k, '') or ''
                r['reviewer'] = rec.get('reviewer', ''); r['reviewedAt'] = rec.get('reviewedAt', '')
            if not (r.get('lesson_attachment') or '').strip() and att_by_act.get(r.get('activityId')):
                r['lesson_attachment'] = att_by_act[r['activityId']]
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'{n} / {len(rows)} rows annotated → {a.out}')


def cmd_status(a):
    rows = [json.loads(l) for l in open(a.sample, encoding='utf-8') if l.strip()]
    last = load_log(a.log)
    done = [r for r in rows if r['sampleId'] in last]
    todo = [r['sampleId'] for r in rows if r['sampleId'] not in last]
    c = collections.Counter()
    for r in done:
        rec = last[r['sampleId']]
        for k in FIELDS:
            c[f'{k}={rec.get(k, "").strip().upper() or "-"}'] += 1
    print(json.dumps(dict(annotated=len(done), remaining=len(todo), nextIds=todo[:12], counts=dict(sorted(c.items()))), ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('add'); p.add_argument('--log', required=True); p.add_argument('--reviewer', required=True); p.add_argument('--json'); p.add_argument('--file')
    p = sub.add_parser('merge'); p.add_argument('--log', required=True); p.add_argument('--sample', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('status'); p.add_argument('--log', required=True); p.add_argument('--sample', required=True)
    a = ap.parse_args()
    {'add': cmd_add, 'merge': cmd_merge, 'status': cmd_status}[a.cmd](a)
    return 0


if __name__ == '__main__':
    sys.exit(main())
