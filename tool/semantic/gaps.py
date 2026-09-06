#!/usr/bin/env python3
"""Lane E1 · §17 source-structure gaps and §15 exception clusters.

§17 asks which SOURCE-STRUCTURE losses currently block visualization. This measures them
on the TSL layer rather than arguing from the model: if the structure is not in the
source record, no semantic rule can recover it, and building a graph from flat text where
the structure was already lost is exactly what the brief forbids.

§15 clusters the lessons that cannot be represented, and reports for each cluster how
many lessons ONE grammar extension would unlock — «FIX THE LANGUAGE, NOT 100 INDIVIDUAL
LESSONS».

    python3 tool/semantic/gaps.py
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus_io as cio  # noqa: E402
import corpus_paths as cp  # noqa: E402

# structures the brief names as blocking, and how their loss is DETECTED in a TSL
MCQ_OPTION_RX = re.compile(r'^\s*[A-DĐ]\s*[.)]\s+\S')
FIG_LABEL_RX = re.compile(r'^\s*(?:hình|Hình|HÌNH)\s+\d', re.I)
FRACTION_RX = re.compile(r'\d\s*/\s*\d|\bphân\s+số\b', re.I)
EXPONENT_RX = re.compile(r'\d\s*(?:\^|\*\*)\s*\d|[⁰¹²³⁴⁵⁶⁷⁸⁹]|10\s*[0-9]\s*(?:m/s|N|J)')
VERSE_RX = re.compile(r'(?:khổ\s+thơ|bài\s+thơ|dòng\s+thơ|câu\s+thơ)', re.I)
DIALOG_RX = re.compile(r'^\s*[-–—]\s*\S')
TABLE_WORD_RX = re.compile(r'\bbảng\b', re.I)


def structure_audit():
    """Measure, over every TSL available, what structure the source record does NOT carry."""
    n_lessons = n_blocks = 0
    roles = collections.Counter()
    figs_total = figs_with_caption = figs_with_labels = 0
    tables_total = tables_with_cells = 0
    q_total = q_with_option_sibling = 0
    option_blocks = 0
    mcq_shaped_lines = 0
    frac_blocks = exp_blocks = verse_blocks = dialog_blocks = 0
    table_mentions = 0
    withheld_reasons = collections.Counter()
    lessons_with_any_withheld = 0
    caption_orphan = 0            # "Hình 17.1" alone, with the descriptive text elsewhere

    for les in cio.iter_tsl():
        n_lessons += 1
        blocks = les['blocks']
        n_blocks += len(blocks)
        for b in blocks:
            roles[b['role']] += 1
            t = b['text'] or ''
            if b['role'] == 'option':
                option_blocks += 1
            if MCQ_OPTION_RX.match(t):
                mcq_shaped_lines += 1
            if FRACTION_RX.search(t):
                frac_blocks += 1
            if EXPONENT_RX.search(t):
                exp_blocks += 1
            if VERSE_RX.search(t):
                verse_blocks += 1
            if DIALOG_RX.match(t):
                dialog_blocks += 1
            if TABLE_WORD_RX.search(t):
                table_mentions += 1
            if b['role'] == 'caption' and FIG_LABEL_RX.match(t.strip()) and len(t.strip()) < 20:
                caption_orphan += 1
            if b['role'] == 'table':
                tables_total += 1
                # a TSL table block is TEXT; there is no cells key at all
                if isinstance(b.get('cells'), list):
                    tables_with_cells += 1
            if b['role'] == 'question':
                q_total += 1
        for f in les['figures']:
            figs_total += 1
            if f.get('caption'):
                figs_with_caption += 1
            if f.get('labels'):
                figs_with_labels += 1
        if les['withheld']:
            lessons_with_any_withheld += 1
            for w in les['withheld']:
                for r in (w.get('reasons') or []):
                    withheld_reasons[r] += 1

    return {
        'denominator': {'lessons': n_lessons, 'blocks': n_blocks,
                        'note': 'TSL-backed Science slice; never divide by 3,679'},
        'rolesInSource': dict(roles.most_common()),
        'gaps': {
            'question_stem_plus_options': {
                'questions': q_total,
                'option_role_blocks': option_blocks,
                'lines_that_LOOK_like_an option': mcq_shaped_lines,
                'verdict': 'BLOCKING — the source record has almost no OPTION role, and '
                           'no stem->option link at all. A question is one flat string.',
            },
            'figure_plus_caption': {
                'figures': figs_total,
                'with_caption': figs_with_caption,
                'with_labels': figs_with_labels,
                'orphan_figure_label_blocks': caption_orphan,
                'verdict': 'BLOCKING for LABELED_FIGURE beyond a bare label: the figure '
                           'record carries no caption, and the descriptive caption is a '
                           'SEPARATE block from the "Hình N.M" label.',
            },
            'table_rows_cols': {
                'table_role_blocks': tables_total,
                'with_cells': tables_with_cells,
                'blocks_mentioning_a_table': table_mentions,
                'verdict': 'BLOCKING — table blocks carry no grid.',
            },
            'fraction_exponent_geometry': {
                'blocks_with_fraction_shape': frac_blocks,
                'blocks_with_exponent_shape': exp_blocks,
                'verdict': 'BLOCKING — math is withheld, not modelled; see Lane A2.',
            },
            'poetry_line_stanza': {'blocks': verse_blocks,
                                   'verdict': 'NOT PRESENT in the Science slice — must be '
                                              'measured on Ngữ văn / Tiếng Việt, which '
                                              'has no TSL'},
            'dialogue_speaker_utterance': {'blocks_starting_with_a_dash': dialog_blocks,
                                           'verdict': 'UNMEASURED — a leading dash is also '
                                                      'the bullet enumerator'},
            'procedure_label_plus_steps': {
                'verdict': 'PARTIAL — recoverable, but only via the governing block, and '
                           'a single tone slip («Tiền hành» for «Tiến hành») removes it.',
            },
        },
        'withheldReasons': dict(withheld_reasons.most_common()),
        'lessonsWithAnyWithheld': lessons_with_any_withheld,
    }


CLUSTER_RULES = [
    # (cluster id, predicate over a census row, what one grammar extension would add)
    ('NO_SOURCE_AT_ALL',
     lambda r: not r['unitsBacked'] and not r['tslBacked'],
     'nothing — this is a PIPELINE gap, not a grammar gap'),
    ('NEEDS_MATH_AST',
     lambda r: 'MATH_AST' in r['extensions'] and not r['extractable'],
     'a structured expression node (Lane A2 MathExpression) + a bridge carrier'),
    ('NEEDS_PHYS_QUANTITY',
     lambda r: 'PHYS_QUANTITY' in r['extensions'] and not r['extractable'],
     'Quantity(value, unit, symbol) as a first-class node'),
    ('NEEDS_CHEM_REACTION',
     lambda r: 'CHEM_REACTION' in r['extensions'] and not r['extractable'],
     'Species + Reaction nodes'),
    ('NEEDS_LIT_TEXT',
     lambda r: 'LIT_TEXT' in r['extensions'] and not r['extractable'],
     'Line/Stanza/Character/Attribution — Lane C already has story-attribution-v1'),
    ('CUES_BUT_NO_EXTRACTION',
     lambda r: r['representable'] and not r['extractable'] and r['tslBacked'],
     'an extraction rule for a family that currently has none'),
    ('NO_CUE_AND_NO_EXTRACTION',
     lambda r: not r['representable'] and not r['extractable'] and r['unitsBacked'],
     'unknown — needs a human read; this is the honest E tier'),
]


def exception_clusters(rows):
    out = []
    seen = set()
    for cid, pred, unlock in CLUSTER_RULES:
        members = [r for r in rows
                   if id(r) not in seen and pred(r)]
        for r in members:
            seen.add(id(r))
        by_subject = collections.Counter(r['subject'] for r in members)
        by_grade = collections.Counter(r['grade'] for r in members)
        out.append({
            'cluster': cid,
            'lessons': len(members),
            'pctOfCanonical': round(100.0 * len(members) / max(1, len(rows)), 1),
            'oneExtensionWouldAdd': unlock,
            'topSubjects': by_subject.most_common(6),
            'grades': dict(sorted(by_grade.items())),
        })
    out.sort(key=lambda c: -c['lessons'])
    unclustered = [r for r in rows if id(r) not in seen]
    return out, len(unclustered)


def main():
    out_dir = cp.out_dir()
    struct = structure_audit()
    with open(os.path.join(out_dir, 'census-rows.json'), encoding='utf-8') as fh:
        rows = json.load(fh)
    clusters, unclustered = exception_clusters(rows)
    payload = {'structure': struct, 'exceptionClusters': clusters,
               'unclustered': unclustered, 'canonical': len(rows)}
    with open(os.path.join(out_dir, 'gaps.json'), 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps(struct, ensure_ascii=False, indent=1))
    print('\n--- exception clusters (denominator: %d canonical) ---' % len(rows))
    for c in clusters:
        print('%-26s %5d  %5.1f%%  %s' % (c['cluster'], c['lessons'],
                                          c['pctOfCanonical'],
                                          c['oneExtensionWouldAdd'][:60]))
    print('unclustered (representable AND extractable): %d' % unclustered)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
