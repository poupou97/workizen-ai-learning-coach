#!/usr/bin/env python3
"""Lane E1 — COUNT THE FORMS BEFORE ANYONE PROPOSES A RULE.

Three lanes independently measured that a grammar validated on one lesson does not
generalise (see 09-E2-RECONCILIATION §3). Lane C found the sharpest version: LS&DL 5
prints 112 date mentions in EIGHT surface forms, its rule accepts ONE, and it extracts
3 events across 28 lessons. E1's census reached the same 3 from the corpus side.

The lesson is procedural, not descriptive: before writing an extraction rule, count how
many distinct SURFACE FORMS the thing actually takes, per subject. A rule that covers
one form of eight is not a grammar, however well it does on the lesson it was written
against — and the count is cheap to get, which is what makes not getting it inexcusable.

This measures the forms. It does not propose rules.

    python3 tool/semantic/forms.py date
    python3 tool/semantic/forms.py enum
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus_io as cio  # noqa: E402
import corpus_paths as cp  # noqa: E402

# Surface forms of a DATE, each named. The point is the partition, not any one member.
DATE_FORMS = [
    ('paren_range',   re.compile(r'\(\s*\d{1,4}\s*[-–—]\s*\d{1,4}\s*\)')),
    ('paren_single',  re.compile(r'\(\s*\d{2,4}\s*\)')),
    ('paren_tcn',     re.compile(r'\(\s*\d{1,4}\s*(?:TCN|tcn)\s*\)')),
    ('nam_year',      re.compile(r'(?<![\wÀ-ỹ])năm\s+\d{3,4}')),
    ('nam_tcn',       re.compile(r'(?<![\wÀ-ỹ])năm\s+\d{1,4}\s*(?:TCN|tcn)')),
    ('the_ki_roman',  re.compile(r'thế\s+k[ỉỷyi]\s+[IVXivx]+')),
    ('the_ki_arabic', re.compile(r'thế\s+k[ỉỷyi]\s+\d{1,2}')),
    ('ngay_thang',    re.compile(r'ngày\s+\d{1,2}\s*(?:tháng|[-/])\s*\d{1,2}')),
    ('dmy_slash',     re.compile(r'\d{1,2}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{2,4}')),
    ('year_range',    re.compile(r'(?<![\d(])\d{3,4}\s*[-–—]\s*\d{3,4}(?![\d)])')),
    ('bare_year',     re.compile(r'(?<![\wÀ-ỹ\d(])(?:1[0-9]{3}|20[0-2][0-9])(?![\d)])')),
    ('giai_doan',     re.compile(r'(?:giai\s+đoạn|thời\s+k[ìỳyi])\s+[^.;,]{2,40}')),
]

# Surface forms of an ENUMERATION — the input to every PROCESS rule.
ENUM_FORMS = [
    ('num_dot',    re.compile(r'^\s*\d{1,2}\s*\.\s+\S')),
    ('num_paren',  re.compile(r'^\s*\d{1,2}\s*\)\s+\S')),
    ('alpha_paren', re.compile(r'^\s*[a-hA-H]\s*\)\s+\S')),
    ('alpha_dot',  re.compile(r'^\s*[a-hA-H]\s*\.\s+\S')),
    ('buoc_n',     re.compile(r'^\s*[Bb][ưươ][ớờ]c\s+\d')),
    ('bullet_mid', re.compile(r'^\s*[·•▪]\s+\S')),
    ('bullet_dash', re.compile(r'^\s*[–—-]\s+\S')),
    ('roman',      re.compile(r'^\s*[IVX]{1,4}\s*[.)]\s+\S')),
    ('plus',       re.compile(r'^\s*\+\s+\S')),
    ('star',       re.compile(r'^\s*[*✦❖]\s+\S')),
]

FORMS = {'date': DATE_FORMS, 'enum': ENUM_FORMS}
# The forms E1's current rules actually accept, so "covered" is measured, not claimed.
COVERED = {
    'date': {'paren_range', 'paren_single', 'paren_tcn'},   # e1-prose-dated-events-v1
    'enum': {'num_dot', 'num_paren', 'alpha_paren', 'alpha_dot', 'buoc_n',
             'bullet_mid', 'bullet_dash'},                   # e1-ordered-steps-v1
}


def _stream(layer):
    """(subject, lesson_key, [texts]) for one corpus layer.

    ⭐ THE LAYER CHANGES THE ANSWER, and for enumerations it changes it completely. The
    units layer (`poc-out/units-k12/`) is produced by a line extractor that keeps the
    number prefix and DROPS the bullet glyph, so an enum census run there reports
    `num_dot` at 100 % and finds no bullets at all — a fact about the extractor, not
    about the books. The TSL layer keeps «·» because it keeps the block text verbatim.
    Run enum on `tsl`; run date on either (dates survive both).
    """
    if layer == 'units':
        for book, subject, lesson, units in cio.iter_units_lessons():
            yield (subject or '?'), cio.lesson_key(book, lesson), [u['text'] for u in units]
    else:
        for les in cio.iter_tsl():
            yield les['book'], cio.lesson_key(les['book'], les['lesson']), \
                [b['text'] for b in les['blocks']]


def census(kind, layer='units'):
    forms = FORMS[kind]
    per_subject = collections.defaultdict(collections.Counter)
    lessons_with_form = collections.defaultdict(set)
    subj_lessons = collections.Counter()
    total = collections.Counter()
    for subject, key, texts in _stream(layer):
        subj_lessons[subject] += 1
        for t in texts:
            t = t or ''
            for name, rx in forms:
                hits = len(rx.findall(t)) if kind == 'date' else (1 if rx.match(t) else 0)
                if hits:
                    per_subject[subject][name] += hits
                    total[name] += hits
                    lessons_with_form[name].add(key)
    covered = COVERED[kind]
    covered_hits = sum(v for k, v in total.items() if k in covered)
    all_hits = sum(total.values())
    rows = []
    for subject, cnt in sorted(per_subject.items(),
                              key=lambda kv: -sum(kv[1].values())):
        distinct = len([k for k, v in cnt.items() if v])
        cov = sum(v for k, v in cnt.items() if k in covered)
        tot = sum(cnt.values())
        rows.append({
            'subject': subject, 'lessons': subj_lessons[subject],
            'mentions': tot, 'distinctForms': distinct,
            'coveredMentions': cov,
            'coverage': round(cov / tot, 3) if tot else None,
            'topForms': cnt.most_common(5),
        })
    return {
        'kind': kind,
        'formsDeclared': len(forms),
        'formsAcceptedByCurrentRules': sorted(covered),
        'totalMentions': all_hits,
        'coveredMentions': covered_hits,
        'overallFormCoverage': round(covered_hits / all_hits, 3) if all_hits else None,
        'byForm': {k: {'mentions': v, 'lessons': len(lessons_with_form[k]),
                       'acceptedByCurrentRules': k in covered}
                   for k, v in total.most_common()},
        'bySubject': rows,
        'layer': layer,
        'denominator': ('units-backed SGK lessons (poc-out/units-k12), line-level text'
                        if layer == 'units' else
                        'TSL-backed lessons (trusted-corpus/tc-v2), verbatim block text'),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('kind', choices=sorted(FORMS))
    ap.add_argument('--layer', choices=['units', 'tsl'], default='units')
    args = ap.parse_args(argv)
    res = census(args.kind, layer=args.layer)
    path = os.path.join(cp.out_dir(), 'forms-%s-%s.json' % (args.kind, args.layer))
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    print('%s on %s — %d forms declared, %d accepted by current rules, coverage %.3f'
          % (args.kind, args.layer, res['formsDeclared'],
             len(res['formsAcceptedByCurrentRules']), res['overallFormCoverage'] or 0))
    print('\nform                 mentions  lessons  accepted')
    for k, v in res['byForm'].items():
        print('%-20s %8d %8d  %s' % (k, v['mentions'], v['lessons'],
                                     'yes' if v['acceptedByCurrentRules'] else 'NO'))
    print('\nsubject           lessons  mentions  forms  coverage')
    for r in res['bySubject'][:14]:
        print('%-17s %7d %9d %6d  %s' % (r['subject'][:17], r['lessons'], r['mentions'],
                                         r['distinctForms'], r['coverage']))
    print('\n-> %s' % path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
