"""Round 5 · Lane A3 — re-annotation of the round-4 role sample AGAINST the written spec.

Method (stated in full in ROLE-DEFINITION-SPEC-v1.md §8): the spec is a function from an
OBSERVATION of the printed page to a role verdict. Both round-4 annotators recorded their
observation in free-text notes. This script replays each row's observation through the
spec's decision procedure and records, per row, whether the spec yields a unique verdict.

It does NOT re-judge the page renders — the spec's own claim is that the six disagreements
were about what a role MEANS, not about what is printed, and the notes of the two annotators
describe the same printed content on every one of them. That claim is checked row by row in
`observation_agrees` below, and it is false nowhere in this sample.
"""
import json
import os

OUT = '/Users/alexnguyen/projects/workizen-ai-learning-coach/poc-out/round5/lane-a3'

# rule ids of ROLE-DEFINITION-SPEC-v1.md §7 (judging procedure) / §8
#   R1  judge the region the served block claims, not the whole page
#   R2  one block, one printed role
#   R2c EXTENT: a region spanning two or more different spec roles is a role error,
#       EXCEPT where the roles stand in a declared parent-child relation (OPTION ⊂ QUESTION,
#       ANSWER_SLOT ⊂ QUESTION, CAPTION ⊂ FIGURE)          [Q-ROLE-1 governs the exception-free form]
#   R3  a printed worked example (Mẫu · M: · Ví dụ N with its solution · Thử lại) is ANSWER
#   R4  a parenthesised source line is ATTRIBUTION whatever box it is printed in
#   R5  role is judged from the PRINTED region, never from the served (possibly destroyed) string
#   R6  a bare printed mathematical expression is FORMULA                    [Q-ROLE-2]
#   R7  page furniture and non-lesson pages (covers, ISBN blocks) are never lesson content

ROWS = [
    # --- the six role disagreements of round 4 -------------------------------------------
    dict(id='s20260905-0162', group='disagreement', a1='OK', a2='WRONG',
         served='exercise', printed='ANSWER (the two «Thử lại» check lines of a Mẫu worked example)',
         observation_agrees=True, rules=['R3'], spec='WRONG', status='DECIDED',
         note='Both annotators describe the same box and both call it a worked example. #1 accepted '
              '«exercise» for it; #2 did not. R3 settles it: a printed solution is ANSWER, never a task.'),
    dict(id='s20260905-0329', group='disagreement', a1='OK', a2='WRONG',
         served='exercise', printed='QUESTION + PAGENUM + HEADING + BODY (the next section\'s passage) + FOOTNOTE (glossary)',
         observation_agrees=True, rules=['R2c'], spec='WRONG|OK', status='CONVENTION_DEPENDENT',
         open_question='Q-ROLE-1', spec_if_extent_inclusive='WRONG', spec_if_label_only='OK',
         note='The region carries five different printed roles. Extent-inclusive → WRONG (with #2); '
              'label-only, keyed on the leading unit → OK (with #1). The spec cannot close this without '
              'the Founder answering whether role fidelity judges the LABEL or the EXTENT.'),
    dict(id='s20260905-0380', group='disagreement', a1='OK', a2='WRONG',
         served='section_text', printed='HEADING (chapter banner) + HEADING (lesson banner) + HEADING (stage icon label) + QUESTION (exercise 1 stem) + TABLE (headers)',
         observation_agrees=True, rules=['R2c'], spec='WRONG', status='DECIDED',
         note='Decided under BOTH readings of Q-ROLE-1: extent-inclusive → WRONG; label-only → the '
              'leading printed unit is a HEADING, and the served role is a body role, so still WRONG.'),
    dict(id='s20260905-0391', group='disagreement', a1='OK', a2='WRONG',
         served='exercise', printed='ANSWER («Ví dụ 2» with its worked solution)',
         observation_agrees=True, rules=['R3'], spec='WRONG', status='DECIDED',
         note='Same rule as s…-0162, on a different book and a different worked-example convention.'),
    dict(id='n20260906-0040', group='disagreement', a1='WRONG', a2='OK',
         served='body', printed='FORMULA (printed «b) 3/10 + 5/21», an enumerated exercise item)',
         observation_agrees=True, rules=['R5', 'R6'], spec='WRONG', status='DECIDED',
         note='#2 judged the role acceptable BECAUSE the served string was a bare fragment. R5 forbids '
              'judging the role from the damaged string. Decided under both answers to Q-ROLE-2: the '
              'printed unit is FORMULA or QUESTION, and `body` is neither.'),
    dict(id='n20260906-0071', group='disagreement', a1='OK', a2='WRONG',
         served='sidebar', printed='ATTRIBUTION («(Theo Văn Thành Lê)»)',
         observation_agrees=True, rules=['R4'], spec='WRONG', status='DECIDED',
         note='#1 accepted `sidebar` because the line is printed inside a tinted box. R4: the box is '
              'typography, the source line is an ATTRIBUTION. The pipeline gained this role in round 4.'),

    # --- control: rows both annotators called WRONG --------------------------------------
    dict(id='s20260905-0150', group='control_wrong', a1='WRONG', a2='WRONG', served='exercise',
         printed='non-lesson page (back cover: book list, ISBN, price)', observation_agrees=True,
         rules=['R7'], spec='WRONG', status='DECIDED', note='back cover served as an exercise of Bài 73'),
    dict(id='s20260905-0220', group='control_wrong', a1='WRONG', a2='WRONG', served='exercise',
         printed='TABLE (one timetable cell)', observation_agrees=True,
         rules=['R2'], spec='WRONG', status='DECIDED', note='a table cell fragment served as an exercise'),
    dict(id='s20260905-0262', group='control_wrong', a1='WRONG', a2='WRONG', served='exercise',
         printed='non-lesson page (back-cover book list row)', observation_agrees=True,
         rules=['R7'], spec='WRONG', status='DECIDED', note=''),
    dict(id='s20260905-0404', group='control_wrong', a1='WRONG', a2='WRONG', served='section_text',
         printed='QUESTION ×4 + TABLE + OPTION', observation_agrees=True,
         rules=['R2c'], spec='WRONG', status='DECIDED',
         note='decided under both readings: label-only keys on exercise 1, a QUESTION, not a body role'),
    dict(id='s20260905-0427', group='control_wrong', a1='WRONG', a2='WRONG', served='question2',
         printed='ACTIVITY («Đọc mở rộng» find-and-read task)', observation_agrees=True,
         rules=['R2'], spec='WRONG', status='DECIDED', note='an extension task served as reading question 2'),
    dict(id='s20260905-0450', group='control_wrong', a1='WRONG', a2='WRONG', served='question5',
         printed='ACTIVITY («Đọc mở rộng» find-and-read task)', observation_agrees=True,
         rules=['R2'], spec='WRONG', status='DECIDED', note=''),
    dict(id='n20260906-0023', group='control_wrong', a1='WRONG', a2='WRONG', served='heading',
         printed='non-lesson page (back-cover series banner)', observation_agrees=True,
         rules=['R7'], spec='WRONG', status='DECIDED', note='served as a TRUSTED heading of Bài 73'),

    # --- control: rows both annotators called OK -----------------------------------------
    dict(id='n20260906-0001', group='control_ok', a1='OK', a2='OK', served='heading',
         printed='HEADING (lesson title)', observation_agrees=True, rules=['R2'], spec='OK', status='DECIDED', note=''),
    dict(id='n20260906-0052', group='control_ok', a1='OK', a2='OK', served='body',
         printed='BODY (one verse line)', observation_agrees=True, rules=['R2'], spec='OK', status='DECIDED',
         note='the spec has no VERSE role; verse is BODY carrying a line-structure flag (§6 relationship rules)'),
    dict(id='n20260906-0072', group='control_ok', a1='OK', a2='OK', served='question',
         printed='QUESTION (task 4)', observation_agrees=True, rules=['R2'], spec='OK', status='DECIDED', note=''),
    dict(id='s20260905-0036', group='control_ok', a1='OK', a2='OK', served='heading',
         printed='HEADING («3. Chiết»)', observation_agrees=True, rules=['R2'], spec='OK', status='DECIDED', note=''),
    dict(id='s20260905-0089', group='control_ok', a1='OK', a2='OK', served='duDoan',
         printed='QUESTION (a printed prediction prompt inside a procedure)', observation_agrees=True,
         rules=['R2'], spec='OK', status='DECIDED', note='pack kind `duDoan` is a QUESTION-family kind'),
    dict(id='s20260905-0109', group='control_ok', a1='OK', a2='OK', served='exercise',
         printed='QUESTION (one exercise, truncated in the serving)', observation_agrees=True,
         rules=['R5'], spec='OK', status='DECIDED',
         note='truncation is a display / teaching-critical error; R5 keeps it out of the role class'),
    dict(id='s20260905-0124', group='control_ok', a1='OK', a2='OK', served='exercise',
         printed='QUESTION (MCQ stem) + OPTION ×4', observation_agrees=True, rules=['R2c'], spec='OK',
         status='DECIDED',
         note='THIS ROW CHANGED THE SPEC. Extent-inclusive R2c as first written made it WRONG — an '
              'agreed-OK control broken by the rule. The parent-child exemption (OPTION ⊂ QUESTION) was '
              'added because of it, and only because of it.'),
    dict(id='s20260905-0178', group='control_ok', a1='OK', a2='OK', served='exercise',
         printed='FORMULA ×3 (three bare printed sums) — or QUESTION ×3', observation_agrees=True,
         rules=['R6'], spec='WRONG|OK', status='CONVENTION_DEPENDENT', open_question='Q-ROLE-2',
         spec_if_bare_expression_is_formula='WRONG', spec_if_bare_expression_is_question='OK',
         note='The gold vocabulary calls a bare printed comparison FORMULA (19 such blocks, e.g. Toán 2 '
              'p48 «200 < 300»); the pack vocabulary calls the same shape an `exercise`. Both annotators '
              'accepted the pack reading. The two vocabularies disagree and only the Founder can settle it.'),
    dict(id='s20260905-0222', group='control_ok', a1='OK', a2='OK', served='exercise',
         printed='QUESTION (question 4)', observation_agrees=True, rules=['R2'], spec='OK', status='DECIDED', note=''),
    dict(id='s20260905-0297', group='control_ok', a1='OK', a2='OK', served='exercise',
         printed='QUESTION (question 1)', observation_agrees=True, rules=['R2'], spec='OK', status='DECIDED', note=''),
    dict(id='s20260905-0372', group='control_ok', a1='OK', a2='OK', served='section_text',
         printed='HEADING (lesson title banner) + HEADING (stage icon label)', observation_agrees=True,
         rules=['R2'], spec='WRONG', status='DECIDED',
         note='THE SPEC IS STRICTER THAN BOTH ANNOTATORS HERE. Two HEADING units served under a body '
              'role. Both annotators accepted it; the spec does not. Applying the spec RAISES the '
              'measured role-error rate — it does not flatter the pipeline.'),
    dict(id='s20260905-0409', group='control_ok', a1='OK', a2='OK', served='caption',
         printed='CAPTION («Hình 5»)', observation_agrees=True, rules=['R2'], spec='OK', status='DECIDED', note=''),
    dict(id='s20260905-0481', group='control_ok', a1='OK', a2='OK', served='prompt',
         printed='QUESTION (writing prompt) + TABLE (the reading-record form)', observation_agrees=True,
         rules=['R2c'], spec='WRONG|OK', status='CONVENTION_DEPENDENT', open_question='Q-ROLE-1',
         spec_if_extent_inclusive='WRONG', spec_if_label_only='OK',
         note='A TABLE is not a declared child of a QUESTION, so the parent-child exemption does not '
              'reach it. Same open question as s…-0329.'),
]


def kappa(a, b):
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa = sum(1 for x in a if x == 'WRONG') / n
    pb = sum(1 for x in b if x == 'WRONG') / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return round(po, 4), round((po - pe) / (1 - pe), 4) if pe < 1 else None


def main():
    assert len(ROWS) == 26, len(ROWS)
    assert all(r['observation_agrees'] for r in ROWS)
    a1 = [r['a1'] for r in ROWS]
    a2 = [r['a2'] for r in ROWS]
    po_b, k_b = kappa(a1, a2)

    # after: both annotators put their (identical) observation through the spec.
    # Worst case — a convention-dependent row is scored as if the two annotators kept their
    # original readings of the open question, i.e. it stays a disagreement.
    s1, s2 = [], []
    for r in ROWS:
        if r['status'] == 'DECIDED':
            s1.append(r['spec'])
            s2.append(r['spec'])
        else:
            s1.append(r['a1'] if r['a1'] in ('OK', 'WRONG') else 'OK')
            s2.append(r['a2'])
    po_a, k_a = kappa(s1, s2)

    dec = [r for r in ROWS if r['status'] == 'DECIDED']
    po_d, k_d = kappa([r['spec'] for r in dec], [r['spec'] for r in dec])

    out = dict(
        schema='lane-a3-role-reannotation-v1',
        method='spec adjudication — each annotator\'s recorded OBSERVATION replayed through the '
               'written decision procedure of ROLE-DEFINITION-SPEC-v1.md §7',
        sample=dict(n=len(ROWS), disagreements=sum(1 for r in ROWS if r['group'] == 'disagreement'),
                    control_wrong=sum(1 for r in ROWS if r['group'] == 'control_wrong'),
                    control_ok=sum(1 for r in ROWS if r['group'] == 'control_ok')),
        before=dict(agreement=po_b, kappa=k_b,
                    a1_wrong_rate=round(sum(1 for x in a1 if x == 'WRONG') / len(a1), 4),
                    a2_wrong_rate=round(sum(1 for x in a2 if x == 'WRONG') / len(a2), 4)),
        after_worst_case=dict(agreement=po_a, kappa=k_a,
                              note='the 3 convention-dependent rows are counted as disagreements'),
        after_on_decided_rows=dict(n=len(dec), agreement=po_d, kappa=k_d,
                                   note='κ = 1.000 here is a property of a deterministic spec, NOT '
                                        'evidence that two annotators would agree in the field. The spec '
                                        'was written after these rows were seen: this is in-sample.'),
        decidability=dict(decided=len(dec), convention_dependent=len(ROWS) - len(dec), undecidable=0,
                          rate=round(len(dec) / len(ROWS), 4)),
        open_questions=sorted({r['open_question'] for r in ROWS if r.get('open_question')}),
        verdicts_changed_against_both_annotators=[r['id'] for r in ROWS
                                                  if r['status'] == 'DECIDED' and r['spec'] != r['a1'] and r['spec'] != r['a2']],
        rows=ROWS)
    os.makedirs(OUT, exist_ok=True)
    with open(f'{OUT}/role-reannotation-2026-09-06.json', 'w') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
