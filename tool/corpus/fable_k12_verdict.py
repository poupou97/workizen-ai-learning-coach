#!/usr/bin/env python3
"""Fable 5.1 independent verdict — classify every canonical SGK lesson (3,679) into:

  A_PROVEN            — a shipped Surface + Evidence path exists today (dedicated pipelines).
  B_NEAR_TERM         — clean corpus units whose PRIMARY interaction pattern already has a
                        shipped Surface (Reader/Compose/QuizSelect/Experiment/SourceReader/
                        MapReader) — unlock = generic activity recognition → existing Surface,
                        no new UI. (Toán COMPUTE_SOLVE counted here only where TutorScreen's
                        fraction-domain could host it: NOT assumed — marked NARROW.)
  C_NEW_CAPABILITY    — text-modality pattern with NO Surface yet (short-answer/explain,
                        observe-describe, classify, fill-blank, match, diagram/table, data,
                        prove, code) OR a text subject whose lessons the detector cannot see
                        (detector gap) — both need a reusable capability, not per-lesson work.
  D_MULTIMODAL        — primary pattern needs audio/voice/drawing/movement/group/equipment,
                        or subject is performance/physical, or foreign-language book the
                        extractor cannot parse.
  E_NO_SIGNAL         — no TOC page range, no units from any pipeline, no SGV record: cannot be
                        classified yet (NOT "impossible forever").

Every bucket is MEASURED from existing artifacts; nothing is estimated. Sub-reasons are kept
so "why" is answerable per lesson. Depth signals (SGV pedagogy, answer key, misconception)
are attached as columns, not used as gates.
"""
import csv
import glob
import json
from collections import Counter, defaultdict

EXTERNAL_SUBJECTS = {'GDTC', 'Âm nhạc', 'Mĩ thuật', 'HĐTN', 'HĐTN-HN', 'GDQP'}
FOREIGN_LANG = {'Tiếng Anh', 'Tiếng Trung', 'Tiếng Nhật', 'Tiếng Pháp', 'Tiếng Hàn', 'Tiếng Nga', 'Tiếng Đức'}
SURFACE_EXISTS = {'EXPERIMENT', 'READ_TEXT', 'WRITE_TEXT', 'SOURCE_REASONING', 'MAP_SPATIAL', 'SELECT_MCQ', 'TRUE_FALSE'}
NARROW = {'COMPUTE_SOLVE'}
MULTI = {'DRAW_CREATE', 'ORAL_SHARE', 'ROLEPLAY_GAME', 'AUDIO_PERFORM', 'DICTATION', 'PHYSICAL', 'HANDS_ON_TOOL', 'RESEARCH_PROJECT'}


def main():
    census = json.load(open('poc-out/k12-convergence-census.json'))['rows']
    tax = json.load(open('poc-out/k12-census-exports/fable-taxonomy.json'))
    primary = tax['primary']; labels = tax['labels']
    sgv = json.load(open('poc-out/k12-census-exports/sgk-lessons-with-sgv.json'))
    attach = {r[0]: r for r in json.load(open('poc-out/k12-census-exports/book-attach-coverage.json'))}
    has_file = {fp.split('/')[-1][:-5] for fp in glob.glob('poc-out/units-k12/*-sgk-*.json')}

    out = []
    for r in census:
        key = f"{r['sourceDocumentId']}|{r['lessonNo']}"
        p = primary.get(key)
        sgvrec = sgv.get(key, {})
        subj = r['subject']
        reason = ''
        if r['activityPresent']:
            bucket = 'A_PROVEN'; reason = 'dedicated pipeline activity + shipped Surface'
        elif subj in EXTERNAL_SUBJECTS:
            bucket = 'D_MULTIMODAL'; reason = f'performance/physical subject ({subj})' + (f'; primary={p}' if p else '')
        elif p in MULTI:
            bucket = 'D_MULTIMODAL'; reason = f'primary pattern {p} needs non-text modality'
        elif p in SURFACE_EXISTS:
            bucket = 'B_NEAR_TERM'; reason = f'primary pattern {p} → existing Surface'
        elif p in NARROW:
            bucket = 'B_NEAR_TERM_NARROW'; reason = 'COMPUTE_SOLVE → TutorScreen exists but only fraction domain today'
        elif p:
            bucket = 'C_NEW_CAPABILITY'; reason = f'primary pattern {p} has no Surface (text-modality)'
        elif subj in FOREIGN_LANG:
            bucket = 'D_MULTIMODAL'; reason = 'foreign-language book; extractor parses 0 units; listening/speaking-heavy'
        elif r['sourceDocumentId'] not in has_file:
            bucket = 'C_NEW_CAPABILITY'; reason = 'DETECTOR GAP: book handled by dedicated pipeline, generic extractor never run'
        elif attach.get(r['sourceDocumentId'], [0]*7)[4] == 0:
            bucket = 'C_NEW_CAPABILITY'; reason = 'DETECTOR GAP: extractor parses 0 units for this book layout'
        elif key in labels and not p:
            bucket = 'C_NEW_CAPABILITY'; reason = 'units present but no leading directive recognized'
        elif r['structured'] or attach.get(r['sourceDocumentId'], [0]*7)[4] > 0:
            bucket = 'C_NEW_CAPABILITY'; reason = 'DETECTOR GAP: book partially attached, this lesson missed'
        else:
            bucket = 'E_NO_SIGNAL'; reason = 'no TOC range, no units, no SGV record'
        if bucket == 'E_NO_SIGNAL' and sgvrec:
            bucket = 'C_NEW_CAPABILITY'; reason = 'SGV record exists (pedagogy) but SGK side unparsed → detector gap'
        out.append(dict(r, primary=p or '', labels=';'.join(labels.get(key, [])), bucket=bucket, reason=reason,
                        sgv_objective=int(sgvrec.get('objective', 0) > 0), sgv_sequence=int(sgvrec.get('sequence', 0) > 0),
                        sgv_answer=int(sgvrec.get('answer', 0) > 0), sgv_misconception=int(sgvrec.get('misconception', 0) > 0)))

    json.dump(out, open('poc-out/k12-census-exports/fable-verdict.json', 'w'), ensure_ascii=False)
    n = len(out)
    print(f'TOTAL {n}')
    bc = Counter(o['bucket'] for o in out)
    for b in ['A_PROVEN', 'B_NEAR_TERM', 'B_NEAR_TERM_NARROW', 'C_NEW_CAPABILITY', 'D_MULTIMODAL', 'E_NO_SIGNAL']:
        print(f'  {b:<20}{bc[b]:>6}  {100*bc[b]/n:5.1f}%')
    print('\nC_NEW_CAPABILITY reasons:')
    for k, c in Counter(o['reason'] for o in out if o['bucket'] == 'C_NEW_CAPABILITY').most_common(12):
        print(f'  {c:>5}  {k}')
    print('\nD_MULTIMODAL reasons:')
    for k, c in Counter(o['reason'].split(';')[0] for o in out if o['bucket'] == 'D_MULTIMODAL').most_common(12):
        print(f'  {c:>5}  {k}')
    print('\nSGV depth over all lessons: objective', sum(o['sgv_objective'] for o in out), 'sequence', sum(o['sgv_sequence'] for o in out),
          'answer', sum(o['sgv_answer'] for o in out), 'misconception', sum(o['sgv_misconception'] for o in out))
    print('SGV depth within A+B:', sum(o['sgv_objective'] for o in out if o['bucket'].startswith(('A', 'B'))))

    # grade x subject CSV
    with open('poc-out/k12-census-exports/fable-grade-subject.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['grade', 'subject', 'total', 'A_PROVEN', 'B_NEAR_TERM', 'B_NEAR_TERM_NARROW', 'C_NEW_CAPABILITY', 'D_MULTIMODAL', 'E_NO_SIGNAL', 'sgv_objective', 'sgv_answer'])
        agg = defaultdict(Counter)
        for o in out:
            a = agg[(o['grade'], o['subject'])]; a['total'] += 1; a[o['bucket']] += 1
            a['sgv_objective'] += o['sgv_objective']; a['sgv_answer'] += o['sgv_answer']
        for (g, s), a in sorted(agg.items()):
            w.writerow([g, s, a['total'], a['A_PROVEN'], a['B_NEAR_TERM'], a['B_NEAR_TERM_NARROW'], a['C_NEW_CAPABILITY'], a['D_MULTIMODAL'], a['E_NO_SIGNAL'], a['sgv_objective'], a['sgv_answer']])
    print('\nBY GRADE (A / B+Bn / C / D / E):')
    bg = defaultdict(Counter)
    for o in out: bg[o['grade']][o['bucket']] += 1; bg[o['grade']]['t'] += 1
    for g in sorted(bg):
        c = bg[g]; print(f"  {g:>2}: t={c['t']:>4} A={c['A_PROVEN']:>3} B={c['B_NEAR_TERM']+c['B_NEAR_TERM_NARROW']:>4} C={c['C_NEW_CAPABILITY']:>4} D={c['D_MULTIMODAL']:>4} E={c['E_NO_SIGNAL']:>3}")
    print('\nBY SUBJECT (top 16 by total):')
    bs = defaultdict(Counter)
    for o in out: bs[o['subject']][o['bucket']] += 1; bs[o['subject']]['t'] += 1
    for s in sorted(bs, key=lambda s: -bs[s]['t'])[:16]:
        c = bs[s]; print(f"  {s:<12} t={c['t']:>4} A={c['A_PROVEN']:>3} B={c['B_NEAR_TERM']+c['B_NEAR_TERM_NARROW']:>4} C={c['C_NEW_CAPABILITY']:>4} D={c['D_MULTIMODAL']:>4} E={c['E_NO_SIGNAL']:>3}")


if __name__ == '__main__':
    main()
