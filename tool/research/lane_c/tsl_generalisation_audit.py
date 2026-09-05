#!/usr/bin/env python3
"""LANE C — generalisation audit of the Bài 17 abstractions over the 238 TSLs.

Question: if the Track B fixture generator (tool/fixtures/make_lesson_fixture.py)
were pointed at every Trusted Structured Lesson of the tc-v2 Science slice,
how much of KHTN 6 Bài 17's model would carry over UNCHANGED?

For each TSL under poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/ we MEASURE:
  - block-kind mapping: TSL roles → LessonBlock kinds (the generator's
    `to_block`), and which trusted blocks would be DROPPED as "vai trò lạ";
  - SemanticData derivation: `derive_process` (tsl-enumerated-steps-v1) and
    `derive_comparison` (tsl-summary-parenthesis-v1) imported from the
    generator itself — how many lessons yield a Process / a Comparison;
  - withheld reasons: whether "withheld = diagram / math" holds;
  - question shape: enumerated? ends with "?"? figure-dependent? MCQ options?
  - figures: caption linkage and the ≥3 % / caption keep rule;
  - boundary: header vs TOC, confidence;
  - Next-Action rule reachability (rule 1 needs a Process; rule 3 needs a
    tutor script — which exists for exactly one lesson).

Read-only. Writes poc-out/round3/lane-c/tsl-generalisation.{json,md}.
Usage: python3 tool/research/lane_c/tsl_generalisation_audit.py [--root R]
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'fixtures'))
from common import dump, pct, root, write_md  # noqa: E402

os.environ.setdefault('TC_ROOT', root())
import make_lesson_fixture as gen  # noqa: E402  (read-only import of the Track B generator)

MAPPED_ROLES = {'heading', 'body', 'caption', 'question', 'objective', 'instruction', 'sidebar', 'stage_label', 'table'}
ENUM = re.compile(r'^\s*(?:\d{1,2}|[a-e])[\.\)]\s')
MCQ = re.compile(r'(?:^|\s)A[\.\)]\s+\S.{2,}?\sB[\.\)]\s+\S', re.DOTALL)
FIG = re.compile(r'(?:hình|Hình|HÌNH)\s*\d')
QUAN_SAT = re.compile(r'(?:quan sát|Quan sát|QUAN SÁT)')
VISUAL_REASONS = {'page_feature:diagram', 'math_guard', 'page_feature:color_heavy', 'figure_dependent'}


def audit_one(path):
    tsl = json.load(open(path))
    blocks = tsl['blocks']
    roles = Counter(gen.role_of(b) for b in blocks)
    unmapped = Counter(gen.role_of(b) for b in blocks if gen.role_of(b) not in MAPPED_ROLES)
    tables = [b for b in blocks if gen.role_of(b) == 'table']
    tables_with_cells = sum(1 for b in tables if isinstance(b.get('cells'), list) and b['cells'])
    withheld = tsl.get('withheld') or []
    wr = Counter()
    for w in withheld:
        for r in (w.get('reasons') or ['unknown']):
            wr[r] += 1
    w_q = [w for w in withheld if w.get('role') == 'question']
    w_q_fig = sum(1 for w in w_q if 'figure_dependent' in (w.get('reasons') or []))
    w_table = sum(1 for w in withheld if w.get('role') == 'table')
    w_answer = sum(1 for w in withheld if w.get('role') in ('model_answer', 'answer'))
    qs = [b for b in blocks if gen.role_of(b) == 'question']
    q_enum = sum(1 for b in qs if ENUM.match(b.get('text') or '') or b.get('enumerator_restored'))
    q_qmark = sum(1 for b in qs if (b.get('text') or '').rstrip().endswith('?'))
    # `refers_figure` is never set on a trusted question (0 / 1,642 measured) and no
    # trusted question contains «hình N»: the figure_dependent guard withholds them
    # BEFORE the TSL. So the figure-dependent question class is measured from the
    # withheld list, not from the trusted blocks.
    q_fig = sum(1 for b in qs if FIG.search(b.get('text') or ''))
    q_quan_sat = sum(1 for b in qs if QUAN_SAT.search(b.get('text') or ''))
    q_mcq = sum(1 for b in qs if MCQ.search(b.get('text') or ''))
    figs = tsl.get('figures') or []
    figs_cap = sum(1 for f in figs if f.get('caption'))
    figs_kept = sum(1 for f in figs if gen.figure_kept(f))
    procs = gen.derive_process(tsl)
    comps = gen.derive_comparison(tsl)
    stage = [(b.get('text') or '').strip().lower() for b in blocks if gen.role_of(b) == 'stage_label']
    has_em_da_hoc = any(s.startswith('em đã học') for s in stage)
    bnd = tsl.get('boundary') or {}
    return {
        'book': tsl['book'], 'lesson': tsl['lesson'], 'title': (tsl.get('title') or '')[:60],
        'sourceability': tsl.get('sourceability'),
        'blocks_trusted': len(blocks), 'withheld': len(withheld),
        'roles': dict(roles), 'unmapped_roles': dict(unmapped), 'unmapped_blocks': sum(unmapped.values()),
        'tables': len(tables), 'tables_with_cells': tables_with_cells,
        'withheld_reasons': dict(wr),
        'withheld_visual_or_math': sum(n for r, n in wr.items() if r in VISUAL_REASONS),
        'withheld_other': sum(n for r, n in wr.items() if r not in VISUAL_REASONS),
        'questions': len(qs), 'q_enumerated': q_enum, 'q_question_mark': q_qmark, 'q_refers_figure': q_fig, 'q_quan_sat': q_quan_sat, 'q_mcq_shaped': q_mcq,
        'withheld_questions': len(w_q), 'withheld_questions_figure_dependent': w_q_fig,
        'withheld_tables': w_table, 'withheld_answers': w_answer,
        'figures': len(figs), 'figures_with_caption': figs_cap, 'figures_kept_rule': figs_kept,
        'processes': len(procs), 'process_steps': [len(p['steps']) for p in procs],
        'process_withheld_steps': sum(1 for p in procs for s in p['steps'] if 'withheldReason' in s),
        'process_titles': [p['title'][:40] for p in procs],
        'comparison_rows': sum(len(c['entities']) for c in comps),
        'has_em_da_hoc_stage': has_em_da_hoc,
        'instruction_blocks': roles.get('instruction', 0),
        'boundary_source': bnd.get('source'), 'boundary_confidence': bnd.get('confidence'),
        'header_found': bnd.get('header_found'), 'pages': len(bnd.get('pages') or []),
        'max_heading_depth': max((len(b.get('heading_path') or []) for b in blocks), default=0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=root())
    a = ap.parse_args()
    paths = sorted(glob.glob(os.path.join(a.root, 'poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/*/bai-*.tsl.json')))
    rows = [audit_one(p) for p in paths]
    n = len(rows)
    by_book = defaultdict(list)
    for r in rows:
        by_book[r['book']].append(r)

    def cnt(pred):
        return sum(1 for r in rows if pred(r))

    tot_blocks = sum(r['blocks_trusted'] for r in rows)
    tot_unmapped = sum(r['unmapped_blocks'] for r in rows)
    unmapped_roles = Counter()
    for r in rows:
        unmapped_roles.update(r['unmapped_roles'])
    wr_all = Counter()
    for r in rows:
        wr_all.update(r['withheld_reasons'])
    tot_withheld = sum(wr_all.values())
    vis = sum(n_ for k, n_ in wr_all.items() if k in VISUAL_REASONS)
    tot_q = sum(r['questions'] for r in rows)
    tot_figs = sum(r['figures'] for r in rows)
    steps_hist = Counter()
    for r in rows:
        for s in r['process_steps']:
            steps_hist[min(s, 6)] += 1

    agg = {
        'denominator': f'{n} / 238 repaired-ranged lessons, six Science books · TC-v2 tc2-p1 · subset: TSLs on disk',
        'lessons': n,
        'blocks_trusted': tot_blocks,
        'block_kinds': {
            'lessons_with_unmapped_block': cnt(lambda r: r['unmapped_blocks'] > 0),
            'unmapped_blocks': tot_unmapped, 'unmapped_share_pct': pct(tot_unmapped, tot_blocks),
            'unmapped_by_role': dict(unmapped_roles),
            'lessons_with_table': cnt(lambda r: r['tables'] > 0),
            'table_blocks': sum(r['tables'] for r in rows), 'table_blocks_with_cells': sum(r['tables_with_cells'] for r in rows),
            'lessons_with_all_bai17_kinds': cnt(lambda r: all(r['roles'].get(k, 0) > 0 for k in ('heading', 'body', 'question', 'caption', 'instruction', 'objective', 'sidebar', 'stage_label'))),
            'lessons_with_instruction': cnt(lambda r: r['instruction_blocks'] > 0),
            'lessons_with_objective': cnt(lambda r: r['roles'].get('objective', 0) > 0),
            'lessons_with_stage_label': cnt(lambda r: r['roles'].get('stage_label', 0) > 0),
            'lessons_with_sidebar': cnt(lambda r: r['roles'].get('sidebar', 0) > 0),
            'lessons_with_caption': cnt(lambda r: r['roles'].get('caption', 0) > 0),
            'lessons_with_question': cnt(lambda r: r['questions'] > 0),
        },
        'semantic_process': {
            'lessons_with_process': cnt(lambda r: r['processes'] > 0),
            'lessons_with_process_ge2_steps': cnt(lambda r: any(s >= 2 for s in r['process_steps'])),
            'lessons_with_instruction_but_no_process': cnt(lambda r: r['instruction_blocks'] > 0 and r['processes'] == 0),
            'processes_total': sum(r['processes'] for r in rows),
            'steps_histogram(capped_at_6)': dict(sorted(steps_hist.items())),
            'processes_with_withheld_step': sum(1 for r in rows if r['process_withheld_steps'] > 0),
        },
        'semantic_comparison': {
            'lessons_with_em_da_hoc_stage': cnt(lambda r: r['has_em_da_hoc_stage']),
            'lessons_with_comparison_rows': cnt(lambda r: r['comparison_rows'] > 0),
            'comparison_rows_total': sum(r['comparison_rows'] for r in rows),
            'note': 'derive_comparison hard-codes the title «Các cách tách chất — sách tóm tắt» and the dimension «Dùng để tách» — lesson-specific strings',
        },
        'withheld': {
            'lessons_with_any_withheld': cnt(lambda r: r['withheld'] > 0),
            'withheld_total': tot_withheld, 'by_reason': dict(wr_all.most_common()),
            'visual_or_math_share_pct': pct(vis, tot_withheld),
            'lessons_where_all_withheld_are_visual_or_math': cnt(lambda r: r['withheld'] > 0 and r['withheld_other'] == 0),
            'lessons_with_agree_text_or_order_withheld': cnt(lambda r: any(k in r['withheld_reasons'] for k in ('agree_text', 'agree_order'))),
        },
        'questions': {
            'total_trusted': tot_q,
            'total_withheld': sum(r['withheld_questions'] for r in rows),
            'withheld_figure_dependent': sum(r['withheld_questions_figure_dependent'] for r in rows),
            'withheld_share_of_all_questions_pct': pct(sum(r['withheld_questions'] for r in rows), tot_q + sum(r['withheld_questions'] for r in rows)),
            'lessons_with_ge1_figure_dependent_withheld_question': cnt(lambda r: r['withheld_questions_figure_dependent'] > 0),
            'enumerated_pct': pct(sum(r['q_enumerated'] for r in rows), tot_q),
            'ends_with_question_mark_pct': pct(sum(r['q_question_mark'] for r in rows), tot_q),
            'trusted_mentioning_hinh_N_pct': pct(sum(r['q_refers_figure'] for r in rows), tot_q),
            'trusted_with_quan_sat_pct': pct(sum(r['q_quan_sat'] for r in rows), tot_q),
            'mcq_shaped_pct': pct(sum(r['q_mcq_shaped'] for r in rows), tot_q),
            'lessons_with_ge1_trusted_question': cnt(lambda r: r['questions'] > 0),
            'withheld_tables': sum(r['withheld_tables'] for r in rows),
            'withheld_model_answers': sum(r['withheld_answers'] for r in rows),
        },
        'figures': {
            'total': tot_figs,
            'with_caption_pct': pct(sum(r['figures_with_caption'] for r in rows), tot_figs),
            'kept_by_rule_pct': pct(sum(r['figures_kept_rule'] for r in rows), tot_figs),
            'lessons_with_zero_kept_figures': cnt(lambda r: r['figures_kept_rule'] == 0),
        },
        'boundary': {
            'header_found': cnt(lambda r: r['header_found']),
            'source': dict(Counter(r['boundary_source'] for r in rows)),
            'confidence': dict(Counter(str(r['boundary_confidence']) for r in rows)),
            'pages_histogram': dict(sorted(Counter(min(r['pages'], 9) for r in rows).items())),
            'sourceability': dict(Counter(r['sourceability'] for r in rows)),
        },
        'next_action': {
            'rule1_visual_reachable(lessons_with_process)': cnt(lambda r: r['processes'] > 0),
            'rule3_tutor_reachable(lessons_with_script)': 1,
            'rule3_note': 'tutor_script_bai17() returns None for every TSL except KHTN 6 Bài 17 (MEASURED in the generator source)',
        },
        'per_book': {b: {
            'lessons': len(rs),
            'with_process': sum(1 for r in rs if r['processes'] > 0),
            'with_comparison': sum(1 for r in rs if r['comparison_rows'] > 0),
            'with_unmapped': sum(1 for r in rs if r['unmapped_blocks'] > 0),
            'with_table': sum(1 for r in rs if r['tables'] > 0),
            'all_withheld_visual_or_math': sum(1 for r in rs if r['withheld'] > 0 and r['withheld_other'] == 0),
        } for b, rs in sorted(by_book.items())},
    }
    dump({'aggregate': agg, 'lessons': rows}, 'tsl-generalisation.json', a.root)

    md = ['# TSL generalisation audit — Bài 17 abstractions × 238 Science TSLs (MEASURED)', '',
          f'Denominator: {agg["denominator"]}. Generator rules imported from `tool/fixtures/make_lesson_fixture.py` unchanged.', '',
          '| question | value |', '|---|---|']
    bk, sp, sc, wh, qq, fg, bd = (agg['block_kinds'], agg['semantic_process'], agg['semantic_comparison'], agg['withheld'], agg['questions'], agg['figures'], agg['boundary'])
    md += [
        f'| lessons whose trusted blocks ALL map onto Bài 17 block kinds | {n - bk["lessons_with_unmapped_block"]} / {n} |',
        f'| trusted blocks the generator would drop as «vai trò lạ» | {bk["unmapped_blocks"]} / {agg["blocks_trusted"]} ({bk["unmapped_share_pct"]} %) — by role {bk["unmapped_by_role"]} |',
        f'| lessons with a `table` role block · table blocks carrying `cells` | {bk["lessons_with_table"]} · {bk["table_blocks_with_cells"]} / {bk["table_blocks"]} |',
        f'| lessons showing every Bài 17 kind (heading, body, question, caption, instruction, objective, sidebar, stage label) | {bk["lessons_with_all_bai17_kinds"]} / {n} |',
        f'| lessons with ≥1 instruction block (Process precondition) | {bk["lessons_with_instruction"]} / {n} |',
        f'| lessons where `tsl-enumerated-steps-v1` yields ≥1 Process · with ≥2 steps | {sp["lessons_with_process"]} · {sp["lessons_with_process_ge2_steps"]} / {n} |',
        f'| lessons with an instruction block but NO derivable Process | {sp["lessons_with_instruction_but_no_process"]} |',
        f'| process step-count histogram (steps → processes; 6 = ≥6) | {sp["steps_histogram(capped_at_6)"]} |',
        f'| processes containing a withheld step | {sp["processes_with_withheld_step"]} / {sp["processes_total"]} |',
        f'| lessons with an «Em đã học» stage label · where `tsl-summary-parenthesis-v1` yields ≥1 row | {sc["lessons_with_em_da_hoc_stage"]} · {sc["lessons_with_comparison_rows"]} / {n} |',
        f'| withheld regions by reason | {wh["by_reason"]} |',
        f'| withheld that are diagram / math / colour / figure-dependent | {wh["visual_or_math_share_pct"]} % of {wh["withheld_total"]} |',
        f'| lessons whose withheld regions are ONLY visual/math (the Bài 17 case) | {wh["lessons_where_all_withheld_are_visual_or_math"]} / {wh["lessons_with_any_withheld"]} with any withheld |',
        f'| lessons with an `agree_text` / `agree_order` withheld region (a text disagreement, not a diagram) | {wh["lessons_with_agree_text_or_order_withheld"]} / {n} |',
        f'| trusted question blocks | {qq["total_trusted"]} — enumerated {qq["enumerated_pct"]} % · ends with «?» {qq["ends_with_question_mark_pct"]} % · mentions «hình N» {qq["trusted_mentioning_hinh_N_pct"]} % · «quan sát» {qq["trusted_with_quan_sat_pct"]} % · MCQ-shaped {qq["mcq_shaped_pct"]} % |',
        f'| WITHHELD question regions · of which `figure_dependent` | {qq["total_withheld"]} · {qq["withheld_figure_dependent"]} — {qq["withheld_share_of_all_questions_pct"]} % of all question regions never reach the TSL text; lessons with ≥1 such question: {qq["lessons_with_ge1_figure_dependent_withheld_question"]} / {n} |',
        f'| withheld table regions · withheld model-answer regions | {qq["withheld_tables"]} · {qq["withheld_model_answers"]} |',
        f'| figures · with a caption link · kept by the ≥3 % / caption rule | {fg["total"]} · {fg["with_caption_pct"]} % · {fg["kept_by_rule_pct"]} % (lessons with 0 kept figures: {fg["lessons_with_zero_kept_figures"]}) |',
        f'| boundary from a printed header · source · confidence | {bd["header_found"]} / {n} · {bd["source"]} · {bd["confidence"]} |',
        f'| pages per lesson (9 = ≥9) · sourceability | {bd["pages_histogram"]} · {bd["sourceability"]} |',
        f'| Next-Action rule 1 (Trực quan first) reachable | {agg["next_action"]["rule1_visual_reachable(lessons_with_process)"]} / {n} lessons |',
        f'| Next-Action rule 3 (Học với SAM) reachable | 1 / {n} — {agg["next_action"]["rule3_note"]} |',
        '', '## Per book', '', '| book | lessons | Process | Comparison | unmapped block | table | withheld only visual/math |', '|---|---|---|---|---|---|---|']
    for b, v in agg['per_book'].items():
        md.append(f'| {b} | {v["lessons"]} | {v["with_process"]} | {v["with_comparison"]} | {v["with_unmapped"]} | {v["with_table"]} | {v["all_withheld_visual_or_math"]} |')
    md += ['', 'Reading rules: a lesson «has a Process» when the generator rule returns ≥1 process with ≥1 step; «unmapped» blocks are trusted blocks with a role outside the generator\'s `to_block` mapping (they would vanish from the Smart Book silently — the generator only logs them).', '']
    p = write_md('\n'.join(md), 'tsl-generalisation.md', a.root)
    print(json.dumps(agg, ensure_ascii=False, indent=1))
    print('wrote', p)


if __name__ == '__main__':
    main()
