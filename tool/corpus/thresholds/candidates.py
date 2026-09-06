#!/usr/bin/env python3
"""The candidate trust policies and the bound options — round 7, step A.

Every candidate here was written from PRE-EXISTING evidence: Lane A3's round-5 trade-off curve
(`docs/research/TRUST-GATE-SENSITIVITY.md`), the round-5 97-row evaluation set, the round-3 and
legacy false-trust audits, and round 6's accounting. **No candidate was chosen after looking at
which lessons it admits**, and `freeze.py` refuses to record any artefact that names one.

A BOUND IS A PROMISE ABOUT A LESSON, NOT A NUMBER ABOUT A BLOCK
---------------------------------------------------------------
A block-level rate is not something a parent can be told. What a family experiences is a LESSON,
so the arithmetic runs in that direction: the promise «a lesson a child opens contains no
teaching-critical error, with probability p» fixes the block-level rate, and the block-level rate
fixes the size of the blind audit that could demonstrate it.

    block_rate <= 1 - p**(1/L)                       L = trusted blocks in a lesson
    audit n    >= smallest n with wilson_upper(k, n) <= block_rate

L = 30 is the planning figure, taken from round 6's Golden #1 delivery: one real lesson,
**34 real SGK blocks**. Independence between blocks is ASSUMED. It is probably optimistic — errors
plausibly cluster by page and by book — but that is an assumption, not a measurement: the
reference plane's page-level incidence (0.1026 observed against 0.0975 expected under
independence, 39 pages carrying 4 events) is far too thin to detect clustering either way.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thresholds.policy import (block_rate_for_lesson_promise,      # noqa: E402
                               min_n_for_upper_bound)

#: Trusted blocks in a lesson. ROUND6 §7: Golden #1 replaced 23 placeholder blocks with 34 real
#: SGK blocks. Every lesson-level figure below is computed at this L and is stated with it.
BLOCKS_PER_LESSON = 30


def lesson_bound(bid, promise, ft_upper_max, rationale, prediction):
    r = block_rate_for_lesson_promise(promise, BLOCKS_PER_LESSON)
    return dict(
        id=bid,
        kind='lesson-promise',
        promise=f'P(a lesson\'s trusted blocks contain no teaching-critical error) >= {promise}',
        blocks_per_lesson=BLOCKS_PER_LESSON,
        tc_rate_upper95_max=round(r, 5),
        ft_rate_upper95_max=ft_upper_max,
        min_audited_trusted_blocks_if_zero_observed=min_n_for_upper_bound(r, 0),
        decision_rule=('PASS iff, on the frozen blind population, the Wilson 95 % UPPER bound on '
                       'the teaching-critical rate among admitted blocks is <= '
                       f'{round(r, 5)} AND the upper bound on false trust is <= {ft_upper_max}. '
                       'Otherwise the result is trusted = 0 and a truthful zero is reported.'),
        rationale=rationale,
        prediction_from_pre_existing_evidence=prediction,
    )


BOUNDS = {b['id']: b for b in [
    dict(id='BOUND-0', kind='none',
         promise='nothing is admitted; trusted = 0',
         blocks_per_lesson=BLOCKS_PER_LESSON,
         tc_rate_upper95_max=0.0, ft_rate_upper95_max=0.0,
         min_audited_trusted_blocks_if_zero_observed=0,
         decision_rule='the status quo. No audit, no admission, no claim.',
         rationale='ROUND6 graded Gate D a TRUTHFUL ZERO and the Founder accepted it. Keeping it '
                   'is a legitimate outcome of this calibration, not a failure of it.',
         prediction_from_pre_existing_evidence='holds by construction.'),

    lesson_bound('BOUND-1', 0.95, 0.02,
                 'The strongest promise anyone could state to a parent without qualification: '
                 '19 lessons in 20 carry no teaching-critical error.',
                 'PREDICTED FAIL. The best measured candidate has a teaching-critical rate of '
                 '0.0213 on the gold plane; the expected number of such errors in the required '
                 'audit is ~48, and the rule requires 0.'),

    lesson_bound('BOUND-2', 0.90, 0.05,
                 'Nine lessons in ten clean. Still a promise that survives being said out loud, '
                 'and roughly an order of magnitude better than anything measured.',
                 'PREDICTED FAIL. Expected ~23 teaching-critical errors in the required audit '
                 'against a rule that permits 0.'),

    lesson_bound('BOUND-3', 0.80, 0.08,
                 'The weakest lesson-level promise this workstream is willing to write down: one '
                 'lesson in five carries a teaching-critical error.',
                 'PREDICTED FAIL. Expected ~11 teaching-critical errors against a rule that '
                 'permits 0. Even this is ~3x better than measured.'),

    dict(id='BOUND-4', kind='block-rate',
         promise='block-level teaching-critical rate, upper 95 % bound <= 0.02. NO lesson-level '
                 'promise is implied and none may be quoted.',
         blocks_per_lesson=BLOCKS_PER_LESSON,
         tc_rate_upper95_max=0.02, ft_rate_upper95_max=0.10,
         min_audited_trusted_blocks_if_zero_observed=min_n_for_upper_bound(0.02, 0),
         decision_rule='PASS iff tc_upper95 <= 0.02 and ft_upper95 <= 0.10 on the blind '
                       'population. n = 189 with zero observed, 437 with three observed.',
         rationale='The only bound on this list the pre-existing evidence does not predict will '
                   'fail. It is included so the Founder can see what «achievable» costs.',
         prediction_from_pre_existing_evidence=(
             'BORDERLINE. The measured point estimate is 0.0213 — on the wrong side of the bound '
             'by a hair, well inside sampling noise. CONSEQUENCE, stated because the bound hides '
             'it: at 0.02 and L=30, 45 % of lessons carry at least one teaching-critical error. '
             'This bound is passable and its consequence is not sayable to a parent.')),

    dict(id='BOUND-5', kind='per-lesson-certification',
         promise='a lesson is trusted only when EVERY one of its blocks has been verified '
                 'against the printed page by a human. The bound is per lesson, not per block.',
         blocks_per_lesson=BLOCKS_PER_LESSON,
         tc_rate_upper95_max=None, ft_rate_upper95_max=None,
         min_audited_trusted_blocks_if_zero_observed=BLOCKS_PER_LESSON,
         decision_rule='PASS for a given lesson iff every block in it was verified and none was '
                       'found wrong. There is no sampling and therefore no confidence interval.',
         rationale='NOT A THRESHOLD, and that is precisely why the arithmetic permits it. A '
                   'threshold spends a measured error rate across content nobody looked at; '
                   'certification spends human attention and produces no residual rate to bound. '
                   'ROUND7-PLAN already prefers this shape: «prefer the already-measured Golden '
                   'lessons. Do not scale to the whole corpus.»',
         prediction_from_pre_existing_evidence=(
             'ACHIEVABLE for a bounded slice, at ~30 human verifications per lesson. It does not '
             'generalise, it does not produce a corpus-level claim, and it must never be '
             'described as a trust threshold having been met.')),
]}


def _c(name, headline, clauses, bound, derived_from, notes=None):
    return dict(schema='trust-policy-v1', name=name, base='pipeline_served',
                headline=headline, clauses=clauses, bound=BOUNDS[bound],
                derived_from=derived_from, notes=notes)


CANDIDATES = {c['name']: c for c in [
    _c('C0 · NULL',
       'Admit nothing. The reference point, and a legitimate outcome.',
       [], 'BOUND-0',
       ['ROUND6-CONSOLIDATED-REPORT §1 Gate D — TRUTHFUL ZERO, accepted.']),

    _c('C1 · NAVIGATION-ONLY',
       'Every available signal, stacked as necessary conditions. Admits headings, objectives, '
       'stage labels, sidebars — and no continuous prose at all.',
       ['served_only', 'no_repair', 'two_stack_exact', 'role_known',
        'role_not_teaching_shaped', 'no_figure_dependence', 'not_mathematical', 'order_ok'],
       'BOUND-2',
       ['TRUST-GATE-SENSITIVITY §2 (guard costs), §3 (curve), §4 (role confidence is a step '
        'function, OCR confidence is dead)',
        'ROUND5-AUDIT-97-EVALUATION-SET defect 8 (sibling withholding is teaching-critical)'],
       'The role-confidence floor removes every `body` block, because 0.60 is the fallback '
       'confidence meaning «we could not tell». What survives is the part of a page that teaches '
       'least.'),

    _c('C2 · PROSE',
       'C1 without the role-confidence floor and without the caption exclusion, so continuous '
       'prose is eligible. MEASURED TO DOMINATE C1: more content AND a lower teaching-critical '
       'rate.',
       ['served_only', 'no_repair', 'two_stack_exact', 'role_not_interactive',
        'no_figure_dependence', 'not_mathematical', 'order_ok'],
       'BOUND-2',
       ['TRUST-GATE-SENSITIVITY §4 — role confidence is a step function, not a dial',
        'this workstream\'s own re-decision of the same frozen evidence rows'],
       'The falsification that matters most in this file: tightening role confidence LOWERS false '
       'trust and RAISES the teaching-critical rate. A dial that looks like safety and is not.'),

    _c('C3 · QUESTION SURFACE',
       'A second, separate gate for a surface that asks a child a question. Not a stricter '
       'setting of the reading gate.',
       ['served_only', 'no_repair', 'two_stack_exact', 'role_is_question_high_confidence',
        'no_figure_dependence', 'not_mathematical'],
       'BOUND-1',
       ['TRUST-GATE-SENSITIVITY §7 #2 and THRESHOLDS.example.json scenario F',
        'TC-19 #3 — QUESTION precision >= 0.95 required; A3 measured 0.903 at n = 72'],
       'UNAVAILABLE ON PRE-EXISTING EVIDENCE: the precision requirement this surface already has '
       'is not met, and it was not met before this round started. A question surface is out of '
       'scope for a first trusted slice regardless of what any bound says.'),

    _c('C4 · C1 + THE MACHINERY THAT DOES NOT EXIST',
       'C1 plus structural-sibling completeness and independent digit-sequence verification — '
       'the two clauses that would address the measured teaching-critical mechanisms.',
       ['served_only', 'no_repair', 'two_stack_exact', 'role_known',
        'role_not_teaching_shaped', 'no_figure_dependence', 'not_mathematical', 'order_ok',
        'sibling_complete', 'digit_sequence_verified'],
       'BOUND-2',
       ['gold plane: 6 of 12 teaching-critical served blocks are digit corruptions and 3 of them '
        'survive character-exact two-stack agreement; the other 6 are non-questions served as '
        'questions',
        'ROUND5-AUDIT-97-EVALUATION-SET defect 8'],
       'FROZEN AS A CANDIDATE, NOT AS AN OPTION. Both added clauses have no implementation, so '
       'this policy cannot be evaluated and `policy.evaluate` marks its numbers MEASUREMENT '
       'INVALID. It is here because it names the only work that would move the bound.'),
]}


RECOMMENDATION = dict(
    candidate='C2 · PROSE',
    bound='BOUND-2',
    expected_outcome='TRUTHFUL ZERO',
    statement=(
        'Freeze C2 under BOUND-2 and run the blind evaluation expecting it to fail. C2 because it '
        'is measurably better than C1 on both axes at once; BOUND-2 because it is derived from a '
        'promise about a lesson rather than from what the pipeline happens to achieve, and it is '
        'the weakest such promise that is still worth making. The pre-existing evidence predicts '
        'a truthful zero, and predicting the outcome before measuring it is what distinguishes a '
        'calibration from a selection. If it passes, that is news; if it fails, the round ends '
        'exactly where round 6 ended, with one difference: the zero will have been MEASURED '
        'against a predeclared bound instead of asserted from the absence of a threshold.'),
    what_would_actually_move_it=(
        'Not a threshold. All 12 measured teaching-critical errors in the served set fall into '
        'exactly two mechanisms — digit corruption (6) and a non-question served as a question '
        '(6) — and neither is visible to any signal a gate can read; 3 of the 6 digit corruptions '
        'survive character-exact agreement between two independent OCR stacks. An independent '
        'digit-sequence check and a question/non-question discriminator would each attack half of '
        'the measured harm. A tighter threshold attacks neither.'),
    if_a_non_zero_is_required=(
        'BOUND-5, per-lesson certification of a bounded slice — every block of one lesson '
        'verified against the print by a human, ~30 verifications. It is not a threshold, it '
        'produces no corpus claim, and it must never be reported as one.'),
)
