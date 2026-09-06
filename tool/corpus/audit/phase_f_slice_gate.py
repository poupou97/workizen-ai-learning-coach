#!/usr/bin/env python3
"""PHASE F — the narrow-slice gate. It does not choose a slice; it judges every one of them.

Founder order 47 §PHASE F. The selection rule this implements was committed FIRST, at
`docs/research/PHASE-F-SELECTION-RULE.md` (commit `aadaa13`), before this file existed. Every
definition below is that document's; nothing here may relax one.

    python3 tool/corpus/audit/phase_f_slice_gate.py \
        --out <units.jsonl> --summary <summary.json> [--detail <outside-the-repo.json>]

WHY IT ENUMERATES EVERYTHING
----------------------------
«Không cherry-pick bằng cách biết trước answer rồi điều chỉnh threshold.» The cheapest way to
make cherry-picking impossible is to not pick: every candidate unit on every gold page of both
gold sets is judged by the identical bar and every one is reported, pass and fail alike.

ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION
--------------------------------------------
Four guards, each of which exits non-zero rather than print a clean summary over nothing:

  G1  it enumerated more than zero units
  G2  the population CONTAINS the known failing cases AND the bar FAILS them — the two
      ACTIVITY -> QUESTION rows of the Bai 17 plane and at least one teaching-critical row of
      the 54-page plane. A bar that passes everything is not a bar.
  G3  a unit holding no block a child acts on is NOT-A-LEARNING-SLICE and can never qualify
  G5  --detail carries verbatim strings and must resolve OUTSIDE the repository

D4: `--out` and `--summary` carry ids, roles, booleans and counts only. Readings go to
`--detail` alone, which is refused inside the repository.

NO UNIT CAN BE REPORTED TRUSTED OR CERTIFIED BY THIS SCRIPT, at any measurement. The strongest
verdict it can print is QUALIFIES_GATE_CLOSED, and §S6(b) of the rule says why.
"""
import argparse
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(CORPUS))
sys.path.insert(0, CORPUS)
sys.path.insert(0, os.path.join(CORPUS, 'thresholds'))

import tc_sdm       # noqa: E402
import tc2_sdm      # noqa: E402
import evidence     # noqa: E402
import policy       # noqa: E402

GOLD_54 = os.path.join(CORPUS, 'tc_gold')
GOLD_BAI17 = os.path.join(CORPUS, 'tc_gold_bai17')
FROZEN = os.path.join(CORPUS, 'thresholds', 'frozen', 'TRUST-POLICY-CANDIDATES-v1.json')

#: §2 — furniture is never a member of a unit.
FURNITURE = {'page_number', 'running_head', 'folio'}
#: §G3 — a learning slice must hold at least one block a child ACTS ON.
CHILD_ACTS_ON = {'question', 'activity'}
#: §S6(a) — the pre-registered candidate. The others are reported beside it, never instead.
PREREGISTERED_CANDIDATE = 'C2 · PROSE'

STAGES = ('S1_SOURCE', 'S2_STRUCTURE', 'S3_RECOGNITION', 'S4_ROLE', 'S5_VALIDATION', 'S6a_POLICY')


# ---------------------------------------------------------------------------- population
def gold_pages(gold_dir, plane):
    """The plane is the DIRECTORY, never the `gold_set` field: that field is absent on 38 of the
    54 pages and reads 'tc-v2' on the other 16, so partitioning on it silently drops a third of
    the plane — and with it one of the teaching-critical rows guard G2 exists to see."""
    out = []
    for f in sorted(glob.glob(os.path.join(gold_dir, '*-p[0-9][0-9][0-9].json'))):
        out.append((json.load(open(f)), plane))
    return out


def lesson_spans():
    """(book, lesson_no) -> the pdf pages a TSL claims for the lesson. Used only to enumerate
    the LESSON scope; its emptiness must be MEASURED, not assumed (§2)."""
    spans = {}
    for f in glob.glob(os.path.join(REPO, 'poc-out', 'trusted-corpus', 'tc-v2', 'tc2-p1',
                                    'lessons', '*', '*.tsl.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        b = d.get('boundary') or {}
        if d.get('book') and d.get('lesson') is not None and b.get('pages'):
            spans[(d['book'], d['lesson'])] = sorted(b['pages'])
    return spans


# ---------------------------------------------------------------------------- units
def units_for_page(gold):
    """Every candidate unit on one gold page: one PAGE unit, and one SECTION per heading."""
    blocks = sorted(gold['blocks'], key=lambda b: int(b['order']))
    members = [b for b in blocks if b['role'] not in FURNITURE]
    out = []
    if members:
        out.append(dict(scope='PAGE', anchor=members[0]['id'], members=members))
    cur = None
    for b in members:
        if b['role'] == 'heading':
            if cur:
                out.append(cur)
            cur = dict(scope='SECTION', anchor=b['id'], members=[b])
        elif cur:
            cur['members'].append(b)
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------------------------- the bar
def judge(unit, rows_by_gid, gold, candidates):
    """§3 of the selection rule, stage by stage, on one unit. Returns a D4-free record."""
    ids = [m['id'] for m in unit['members']]
    rows = [rows_by_gid.get(i) for i in ids]
    gmap = {m['id']: m for m in unit['members']}

    no_row = [i for i, r in zip(ids, rows) if r is None]
    no_text = [i for i in ids if not (gmap[i].get('text') or '').strip()]
    present = [(i, r) for i, r in zip(ids, rows) if r is not None]

    # G3 — is this a LEARNING slice at all?
    acts_on = [i for i in ids if gmap[i]['role'] in CHILD_ACTS_ON]

    # S1 SOURCE — every member matched a pipeline block carrying provenance
    s1_unmatched = [i for i, r in present if not r.get('matched')]
    s1 = not no_row and not s1_unmatched

    # S2 STRUCTURE
    bids = [r.get('block_id') for _, r in present if r.get('block_id')]
    s2_many_to_one = sorted({b for b, n in collections.Counter(bids).items() if n > 1})
    s2_figure_dep = [i for i, r in present if r.get('refers_figure')]
    s2_no_text = list(no_text)
    orders = [int(gmap[i]['order']) for i in ids]
    s2_contiguous = orders == sorted(orders)
    s2 = (s2_contiguous and not s2_many_to_one and not s2_figure_dep
          and not s2_no_text and not no_row)

    # S3 RECOGNITION — character-exact, and UNMEASURABLE where gold carries no text
    s3_unmeasurable = bool(no_text) or bool(no_row)
    s3_wrong = [i for i, r in present
                if not (r.get('cer') == 0.0 and (r.get('edits') or 0) == 0)]
    s3 = (not s3_unmeasurable) and not s3_wrong

    # S4 ROLE
    s4_wrong = [i for i, r in present
                if tc_sdm.GOLD_ROLE_MAP.get(gmap[i]['role'], 'UNKNOWN') != r.get('role_coarse')]
    s4_as_question = [i for i, r in present if r.get('truth_as_question')]
    s4 = not no_row and not s4_wrong and not s4_as_question

    # S5 VALIDATION — served by the UNCHANGED pipeline gate, no hole, no wrongness
    s5_withheld = [i for i, r in present if not r.get('pipeline_trusted')]
    s5_guards = sorted({g for _, r in present for g in (r.get('guards') or [])})
    s5_wrong = [i for i, r in present if r.get('truth_wrong')]
    s5_tc = [i for i, r in present if r.get('truth_teaching_critical')]
    s5 = not no_row and not s5_withheld and not s5_guards and not s5_wrong and not s5_tc

    # S6(a) — the frozen candidates. `admits` only ever REFUSES; nothing is activated.
    per_candidate = {}
    for name, pol in candidates.items():
        refusals = collections.Counter()
        admitted = 0
        for _, r in present:
            row = dict(r)
            row['_served'] = bool(r.get('pipeline_trusted'))
            ok, refs = policy.admits(row, pol)
            admitted += 1 if ok else 0
            for x in refs:
                refusals[x] += 1
        per_candidate[name] = dict(all_admitted=bool(present) and admitted == len(present),
                                   admitted=admitted, of=len(present),
                                   refusals=dict(sorted(refusals.items())))
    s6a = per_candidate.get(PREREGISTERED_CANDIDATE, {}).get('all_admitted', False)

    stage = {'S1_SOURCE': s1, 'S2_STRUCTURE': s2, 'S3_RECOGNITION': s3,
             'S4_ROLE': s4, 'S5_VALIDATION': s5, 'S6a_POLICY': s6a}
    first_fail = next((s for s in STAGES if not stage[s]), None)

    if not acts_on:
        verdict = 'NOT_A_LEARNING_SLICE'
    elif s3_unmeasurable:
        verdict = 'UNMEASURABLE'
    elif first_fail:
        verdict = f'FAIL@{first_fail}'
    else:
        verdict = 'QUALIFIES_GATE_CLOSED'

    return dict(
        book=gold['book'], page=gold['page'], printed_page=gold.get('printed_page'),
        gold_set=gold.get('gold_set', 'tc-v1'), subject=gold.get('subject'),
        grade=gold.get('grade'), lesson=(gold.get('lesson') or {}).get('number'),
        scope=unit['scope'], anchor=unit['anchor'], unit_id=f"{gold['book']}#p{gold['page']:03d}#{unit['scope']}#{unit['anchor']}",
        members=len(ids), member_ids=ids, member_roles=[gmap[i]['role'] for i in ids],
        rows=len(present), members_without_row=no_row, members_without_gold_text=no_text,
        acts_on=acts_on,
        stage=stage, first_failing_stage=first_fail, verdict=verdict,
        s1_unmatched=s1_unmatched,
        s2_contiguous=s2_contiguous, s2_many_to_one=s2_many_to_one,
        s2_figure_dependent=s2_figure_dep,
        s3_not_exact=s3_wrong, s3_unmeasurable=s3_unmeasurable,
        s4_role_wrong=s4_wrong, s4_as_question=s4_as_question,
        s5_withheld=s5_withheld, s5_guards=s5_guards, s5_wrong=s5_wrong,
        s5_teaching_critical=s5_tc,
        candidates=per_candidate,
    )


# ---------------------------------------------------------------------------- guards
def adequacy(units, rows_all, expected_pages, built_pages):
    """G1 and G2. Raises SystemExit with UNVERIFIED rather than reporting over nothing."""
    if built_pages < expected_pages:
        raise SystemExit(f'UNVERIFIED: {built_pages} of {expected_pages} gold pages rebuilt. A gate '
                         f'measured over a shrunken plane is a gate measured over the easy half.')
    if not units:
        raise SystemExit('UNVERIFIED (G1): zero candidate units enumerated. A gate over an empty '
                         'population prints a flawless zero.')

    bai17_as_q = [r for r in rows_all
                  if r['_plane'] == 'plane-bai17' and r.get('truth_as_question') and r.get('pipeline_trusted')]
    if len(bai17_as_q) != 2:
        raise SystemExit(f'UNVERIFIED (G2): the Bai 17 plane holds {len(bai17_as_q)} served '
                         'ACTIVITY -> QUESTION rows; Phase B measured 2. The failing case this bar '
                         'must reject is not where it was left.')
    plane54_tc = [r for r in rows_all
                  if r['_plane'] == 'plane-54' and r.get('truth_teaching_critical') and r.get('pipeline_trusted')]
    if not plane54_tc:
        raise SystemExit('UNVERIFIED (G2): the 54-page plane holds no served teaching-critical row. '
                         'A bar never shown a failing case has not been tested.')

    # every failing row must land inside an enumerated unit, and every such unit must NOT qualify
    def units_holding(row):
        return [u for u in units
                if u['book'] == row['book'] and u['page'] == row['page'] and row['gold_id'] in u['member_ids']]

    for r in bai17_as_q + plane54_tc:
        hold = units_holding(r)
        if not hold:
            raise SystemExit(f"UNVERIFIED (G2): failing row {r['book']} p{r['page']:03d} "
                             f"{r['gold_id']} lands in no enumerated unit — the bar never sees it.")
        bad = [u['unit_id'] for u in hold if u['verdict'] == 'QUALIFIES_GATE_CLOSED']
        if bad:
            raise SystemExit(f"UNVERIFIED (G2): a unit holding a known failing row QUALIFIED: {bad}. "
                             'The bar does not reject what it is required to reject.')
    # re-derive the plane totals a SECOND way, from the two underlying flags, and refuse if the
    # two routes disagree. A number of the right type and the wrong quantity passes every check
    # that is not a re-derivation; this guard was added because the first version of this file
    # partitioned on `gold_set` and printed 7 where the plane holds 8.
    p54 = [r for r in rows_all if r['_plane'] == 'plane-54' and r.get('pipeline_trusted')]
    union = sum(1 for r in p54 if r.get('truth_digits_wrong') or r.get('truth_as_question'))
    if union != len(plane54_tc):
        raise SystemExit(f'UNVERIFIED (G4): teaching-critical re-derives to {union} from the two '
                         f'underlying flags but {len(plane54_tc)} from truth_teaching_critical.')
    published = dict(served=356, false_trust=23, teaching_critical=8, digits=6, as_question=2)
    got = dict(served=len(p54),
               false_trust=sum(1 for r in p54 if r.get('truth_wrong_any')),
               teaching_critical=len(plane54_tc),
               digits=sum(1 for r in p54 if r.get('truth_digits_wrong')),
               as_question=sum(1 for r in p54 if r.get('truth_as_question')))
    if got != published:
        raise SystemExit(f'UNVERIFIED (G4): the 54-page plane rebuilds to {got}, not to the arm '
                         f'PHASE-B-QUESTION-VETO §3.1 published for `main` ({published}). The gate '
                         'is being measured on a different population from the one it cites.')
    return dict(bai17_as_question_rows=len(bai17_as_q), plane54_teaching_critical_rows=len(plane54_tc),
                plane54_totals=got, plane54_totals_match_phase_b=True)


def main():
    ap = argparse.ArgumentParser(description='Phase F — judge every candidate slice')
    ap.add_argument('--out', required=True, help='per-unit JSONL (ids/booleans/counts only)')
    ap.add_argument('--summary', required=True, help='aggregate JSON (D4-free)')
    ap.add_argument('--detail', help='verbatim readings; MUST resolve outside the repository')
    ap.add_argument('--min-pages', type=int, default=58,
                    help='declared plane size: 54 tc_gold + 4 tc_gold_bai17')
    ns = ap.parse_args()

    if ns.detail:
        d, r = os.path.realpath(ns.detail), os.path.realpath(REPO)
        if os.path.commonpath([d, r]) == r:
            raise SystemExit('REFUSED (G5): --detail carries D4 readings and must live outside the '
                             'repository.')

    frozen = json.load(open(FROZEN))
    candidates = {c['name']: c for c in frozen['candidates'] if c['clauses']}

    units, rows_all, detail = [], [], []
    built = 0
    gold_by_page = {}
    lesson_pages = collections.defaultdict(set)
    for gold, plane in gold_pages(GOLD_54, 'plane-54') + gold_pages(GOLD_BAI17, 'plane-bai17'):
        sdm = tc2_sdm.build_page(gold['book'], gold['page'], pipeline='tc2-p2')
        rows = evidence.gold_page_rows(gold, sdm)
        built += 1
        by_gid = {r['gold_id']: r for r in rows}
        for r in rows:
            r['_plane'] = plane
        rows_all += rows
        gold_by_page[(gold['book'], gold['page'])] = (gold, by_gid)
        if (gold.get('lesson') or {}).get('number') is not None:
            lesson_pages[(gold['book'], gold['lesson']['number'])].add(gold['page'])
        gtext = {b['id']: (b.get('text') or b.get('anchor') or '') for b in gold['blocks']}
        for u in units_for_page(gold):
            rec = judge(u, by_gid, gold, candidates)
            units.append(rec)
            detail.append(dict(unit_id=rec['unit_id'], verdict=rec['verdict'],
                               members=[dict(gold_id=i, gold_role=role, gold_text=gtext.get(i))
                                        for i, role in zip(rec['member_ids'], rec['member_roles'])]))

    # ---- LESSON scope. §2 of the rule: enumerate it so its emptiness is MEASURED, never assumed.
    spans = lesson_spans()
    lesson_scope = dict(lessons_touched_by_gold=len(lesson_pages), fully_covered=[],
                        partially_covered=0, no_authoritative_span=0)
    for (book, no), pages in sorted(lesson_pages.items()):
        span = spans.get((book, no))
        if not span:
            lesson_scope['no_authoritative_span'] += 1
            continue
        if set(span) <= pages:
            lesson_scope['fully_covered'].append(f'{book}#bai{no}')
            members, gmaps, merged = [], {}, {}
            for pg in span:
                g, by_gid = gold_by_page[(book, pg)]
                for b in sorted(g['blocks'], key=lambda x: int(x['order'])):
                    if b['role'] not in FURNITURE:
                        key = f"p{pg:03d}:{b['id']}"
                        members.append(dict(b, id=key, order=pg * 1000 + int(b['order'])))
                        merged[key] = by_gid.get(b['id'])
            u = dict(scope='LESSON', anchor=f'bai{no}', members=members)
            units.append(judge(u, merged, gold_by_page[(book, span[0])][0], candidates))
        else:
            lesson_scope['partially_covered'] += 1

    checked = adequacy(units, rows_all, ns.min_pages, built)
    checked['lesson_scope'] = lesson_scope

    with open(ns.out, 'w') as fh:
        for u in units:
            fh.write(json.dumps(u, ensure_ascii=False, sort_keys=True) + '\n')
    if ns.detail:
        with open(ns.detail, 'w') as fh:
            json.dump(detail, fh, ensure_ascii=False, indent=1)

    by_verdict = collections.Counter(u['verdict'] for u in units)
    by_scope = collections.Counter(f"{u['scope']}/{u['verdict']}" for u in units)
    first_fail = collections.Counter(u['first_failing_stage'] for u in units
                                     if u['verdict'].startswith('FAIL'))
    # the learning slices only — the population G3 leaves standing
    learn = [u for u in units if u['verdict'] != 'NOT_A_LEARNING_SLICE']
    learn_fail = collections.Counter(u['first_failing_stage'] for u in learn
                                     if u['first_failing_stage'])
    # how far each learning unit got, stage by stage: a monotone survival curve
    survival = {s: sum(1 for u in learn if all(u['stage'][x] for x in STAGES[:i + 1]))
                for i, s in enumerate(STAGES)}
    qual = [u['unit_id'] for u in units if u['verdict'] == 'QUALIFIES_GATE_CLOSED']
    # every unit that cleared S1..S5 but was refused by the pre-registered candidate
    thru_s5 = [u for u in learn if all(u['stage'][s] for s in STAGES[:5])]

    summary = dict(
        schema='phase-f-slice-gate-v1',
        selection_rule='docs/research/PHASE-F-SELECTION-RULE.md @ aadaa13',
        pages_rebuilt=built, gold_rows=len(rows_all), units=len(units),
        by_verdict=dict(sorted(by_verdict.items())), by_scope=dict(sorted(by_scope.items())),
        first_failing_stage_all=dict(sorted(first_fail.items(), key=lambda kv: str(kv[0]))),
        learning_slices=len(learn),
        learning_first_failing_stage=dict(sorted(learn_fail.items(), key=lambda kv: str(kv[0]))),
        learning_survival_by_stage=survival,
        through_S5=[u['unit_id'] for u in thru_s5],
        through_S5_candidate_refusals={
            u['unit_id']: {n: c['refusals'] for n, c in u['candidates'].items()} for u in thru_s5},
        qualifies_gate_closed=qual,
        adequacy=checked, lesson_scope=lesson_scope,
        preregistered_candidate=PREREGISTERED_CANDIDATE,
        note='TRUSTED and CERTIFIED are not available verdicts. See PHASE-F-SELECTION-RULE §S6(b).',
    )
    json.dump(summary, open(ns.summary, 'w'), ensure_ascii=False, indent=1, sort_keys=True)

    print(f'pages={built} gold_rows={len(rows_all)} units={len(units)}')
    for k, v in sorted(by_verdict.items()):
        print(f'  {k:24s} {v}')
    print(f'learning slices (G3 survivors) = {len(learn)}')
    print('  survival:', ' '.join(f'{s}={survival[s]}' for s in STAGES))
    print(f'  through S5: {len(thru_s5)}  ->  QUALIFIES_GATE_CLOSED: {len(qual)}')
    print(f"LESSON scope: touched={lesson_scope['lessons_touched_by_gold']} "
          f"fully_covered={len(lesson_scope['fully_covered'])} "
          f"partial={lesson_scope['partially_covered']} "
          f"no_span={lesson_scope['no_authoritative_span']}")
    print(f'adequacy: {checked}')


if __name__ == '__main__':
    main()
