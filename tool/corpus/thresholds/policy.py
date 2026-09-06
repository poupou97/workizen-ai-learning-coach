#!/usr/bin/env python3
"""A candidate TRUST policy — and the one thing it is structurally forbidden to do.

Round 7 · WS-T · step A. **This module cannot activate anything.** It describes a candidate
policy, evaluates it over frozen evidence rows, and reports rates. Turning a candidate into
a production trust gate is a Founder act (`apply.py`, which is inert without an approval
artefact naming a frozen policy by hash).

WHY THIS IS NOT `gate.py`
-------------------------
Round 5's `gate.py` parameterises **how much to loosen**: every scenario on Lane A3's curve is
a set of guards *waived*, and its axis is coverage. That is the right instrument for the
question «what does each guard cost?» and the wrong one for «what may be called TRUSTED?».

A trust policy has the opposite shape. Round 6 fixed the vocabulary: `VISIBLE != SERVED`, and
`trusted` is 0 by construction. What a threshold decides is which of the blocks the pipeline
**already serves** may additionally be called trusted. So every policy in this module is

        TRUST  =  SERVED  ∩  admit(...)

with SERVED computed by the *unchanged* pipeline gate (`gate.PIPELINE_GATE`, every guard
denying). Three consequences, all of them load-bearing and all of them enforced in code:

1. **Activation cannot serve one new block.** `trusted ⊆ served`, so round 6's «served set
   byte-identical» invariant survives activation by construction, and Gate E cannot regress.
2. **A waiver can never produce trust.** Waiving a guard validates nothing (A3 §1). There is
   no clause in this module that removes a guard.
3. **A repair is not a trust source.** `REPAIRED != TRUSTED`, `RESTORED != TRUSTED`,
   `VALIDATED REPAIR != TRUSTED`. Clause `no_repair` is mandatory in every candidate.

CLAUSES ARE NECESSARY CONDITIONS, NEVER SUFFICIENT ONES
-------------------------------------------------------
Round 4 falsified `OCR_A == OCR_B => TEXT == TRUE`, and this repo has a measured instance of
the falsification surviving *every* signal a gate can read (see `two_stack_exact` below). So
a clause may only ever REFUSE. Nothing here treats a passed clause as evidence of truth, and
`admits()` returns a refusal list, never a score.
"""
import math
import re
import unicodedata

SCHEMA = 'trust-policy-v1'

#: The base set. A policy may only ever intersect with it.
BASE_SERVED = 'pipeline_served'


# --------------------------------------------------------------------------------------
# Clauses
# --------------------------------------------------------------------------------------
# `available` says whether the machinery a clause needs EXISTS TODAY. A policy that names an
# unavailable clause is legal to write, hash and freeze — and `evaluate()` refuses to report a
# rate for it, because a clause that cannot run has not been measured. This is how a candidate
# records «this bound depends on machinery nobody has built» without pretending otherwise.

def _clause(cid, kind, reason, evidence, predicate, available=True):
    return dict(id=cid, kind=kind, reason=reason, evidence=evidence,
                predicate=predicate, available=available)


def _f(row, key, default=None):
    v = row.get(key)
    return default if v is None else v


CLAUSES = {c['id']: c for c in [
    _clause(
        'served_only', 'structural',
        'trusted ⊆ served. Activation may not serve one block that is withheld today.',
        'ROUND6 §3 «the served set is byte-identical before and after, in every population».',
        lambda r: bool(r.get('_served')),
    ),
    _clause(
        'no_repair', 'doctrine',
        'A repaired, restored or validated-repaired block is never trusted by this policy.',
        'ROUND5 doctrine; ROUND6 §3 — 9 validated repairs crossed the pipeline, trusted: 0.',
        lambda r: (r.get('disposition') or 'ORIGINAL_OBSERVATION') == 'ORIGINAL_OBSERVATION',
    ),
    _clause(
        'two_stack_exact', 'fidelity',
        'Both OCR stacks must agree character-exactly, with no tone disagreement. NECESSARY, '
        'NEVER SUFFICIENT — agreement does not imply truth.',
        'ROUND4 falsified OCR_A==OCR_B => TRUE. A3 §3: adding this floor to today\'s guards '
        'moves 26 wrong served to 22, i.e. it removes some wrong blocks and no more than some.',
        lambda r: _f(r, 'text_sim') == 100.0 and _f(r, 'tone_disagreements', 0) == 0,
    ),
    _clause(
        'role_known', 'role',
        'Refuse a block whose role the role layer could not determine (confidence 0.60 is the '
        '`body` fallback, i.e. «we could not tell»).',
        'A3 §4 «role confidence is a step function, not a dial»; the 0.60→0.70 step removes 84 '
        'served blocks. MEASURED CONSEQUENCE: it removes ALL continuous prose.',
        lambda r: _f(r, 'role_confidence', 0.0) >= 0.70,
    ),
    _clause(
        'role_not_teaching_shaped', 'role',
        'Refuse the roles whose errors are teaching-critical BY CONSTRUCTION: a question '
        '(a non-question served as a question is a teaching error), an option (an incomplete '
        'multiple choice is wrong, not merely smaller), an activity, a caption (bound to a '
        'figure the child is not shown).',
        'ROUND5 97-row defect 8 (sibling withholding is itself teaching-critical); gold plane: '
        '`as_question` is 6 of 26 wrong served blocks and 6 of 12 teaching-critical ones.',
        lambda r: r.get('role_value') not in {'question', 'option', 'activity', 'caption'},
    ),
    _clause(
        'role_not_interactive', 'role',
        'Refuse question/option/activity only — prose and captions stay eligible.',
        'The relaxation of `role_not_teaching_shaped` used by candidate C2.',
        lambda r: r.get('role_value') not in {'question', 'option', 'activity'},
    ),
    _clause(
        'role_is_question_high_confidence', 'role',
        'Admit ONLY blocks the role layer calls a question, at role confidence >= 0.90. This is '
        'a SECOND gate for a question surface, not a stricter setting of the reading gate.',
        'TC-19 #3 requires QUESTION precision >= 0.95 before an auto-labelled question is '
        'graded. A3 measured trusted-QUESTION precision 0.903 at n=72 — the requirement is NOT '
        'MET, and role is the least reproducible class measured (kappa 0.423-0.713).',
        lambda r: r.get('role_value') == 'question' and _f(r, 'role_confidence', 0.0) >= 0.90,
    ),
    _clause(
        'no_figure_dependence', 'policy',
        'Refuse a block whose meaning depends on a figure the product does not render.',
        'A3 §2: `figure_dependent` sole-withholds 13 blocks, clean share 0.615.',
        lambda r: not r.get('refers_figure'),
    ),
    _clause(
        'not_mathematical', 'subject',
        'Refuse mathematics until a structured formula representation exists. Flattened '
        'mathematics is not a fidelity question the gate can answer.',
        'A3 §2: `math_guard` is the only guard whose sole-withheld blocks split evenly (4 clean, '
        '4 wrong) — a detector with no discrimination. Round-3 audit: Toán false trust 0.878. '
        'ROUND6 §7: 41 fabricated Toán expressions removed; the app ships zero Toán exercises.',
        lambda r: r.get('subject') not in {'Toán'} and not r.get('has_math'),
    ),
    _clause(
        'order_ok', 'fidelity',
        'Refuse a block the verifier says moved.',
        'Gold plane: `order_ok=False` carries wrong 2/14 (0.143) vs 24/340 (0.071). WEAK — '
        'reading-order inversion is the LARGEST wrongness class (14 of 26) and this signal '
        'does not see most of it.',
        lambda r: r.get('order_ok') is not False,
    ),
    _clause(
        'sibling_complete', 'structure',
        'Refuse a block if any member of its structural group (OPTION ⊂ QUESTION, a caption '
        'bound to its figure, a table row, a step in a procedure) is withheld. Withholding one '
        'member must withhold the whole group.',
        'ROUND5 97-row defect 8 — a teaching-critical failure produced by the safety mechanism '
        'itself. MACHINERY DOES NOT EXIST: no group key is carried on an evidence row.',
        lambda r: bool(r.get('sibling_group_complete')),
        available=False,
    ),
    _clause(
        'digit_sequence_verified', 'fidelity',
        'If the block contains digits, an INDEPENDENT check must confirm the digit sequence.',
        'Gold plane: 6 of 12 teaching-critical served blocks are digit corruptions, and 3 of '
        'them survive character-exact two-stack agreement — both stacks agreed on the same '
        'wrong digits. No signal a gate can read separates them. MACHINERY DOES NOT EXIST.',
        lambda r: bool(r.get('digit_sequence_verified')),
        available=False,
    ),
]}


# --------------------------------------------------------------------------------------
# Policies
# --------------------------------------------------------------------------------------

def normalise(policy):
    p = dict(schema=SCHEMA, base=BASE_SERVED, clauses=[], bound=None, name=None,
             derived_from=[], notes=None)
    p.update(policy or {})
    if p['base'] != BASE_SERVED:
        raise ValueError(f'a trust policy may only intersect with {BASE_SERVED!r}')
    cl = list(p['clauses'])
    if cl and 'served_only' not in cl:
        cl.insert(0, 'served_only')
    if cl and 'no_repair' not in cl:
        cl.append('no_repair')
    unknown = [c for c in cl if c not in CLAUSES]
    if unknown:
        raise ValueError(f'unknown clause(s): {unknown}')
    p['clauses'] = cl
    return p


def unavailable_clauses(policy):
    return [c for c in normalise(policy)['clauses'] if not CLAUSES[c]['available']]


def admits(row, policy):
    """(admitted, refusals). A clause may only ever REFUSE; nothing here scores a block."""
    p = policy if isinstance(policy.get('clauses'), list) and policy.get('schema') == SCHEMA \
        else normalise(policy)
    refusals = [c for c in p['clauses'] if not CLAUSES[c]['predicate'](row)]
    return (not refusals and bool(p['clauses'])), refusals


def wilson_upper(k, n, z=1.96):
    """Upper 95 % bound on a rate. A point estimate of 0 means nothing at small n; every bound
    in this workstream is stated as an upper confidence bound for that reason."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c + h) / d


def min_n_for_upper_bound(bound, k=0, cap=200000):
    """Smallest audited n whose Wilson upper bound is <= `bound` when `k` errors are observed.
    This is the audit COST of a promise, and it is why a bound is a budget decision."""
    if not 0 < bound < 1:
        raise ValueError('bound must be in (0,1)')
    n = max(k, 1)
    while n <= cap:
        u = wilson_upper(k, n)
        if u is not None and u <= bound:
            return n
        n += 1
    return None


def lesson_clean_probability(block_rate, blocks_per_lesson):
    """P(a lesson's trusted blocks contain no error) under an ASSUMPTION of independence.
    Probably optimistic — but the reference plane has too few events to measure the clustering
    that would make it so, and this workstream corrected itself once for claiming otherwise."""
    return (1.0 - block_rate) ** blocks_per_lesson


def block_rate_for_lesson_promise(promise, blocks_per_lesson):
    """The block-level rate a lesson-level promise implies. This is the direction the arithmetic
    has to run: the product promises something about a LESSON a child opens."""
    return 1.0 - promise ** (1.0 / blocks_per_lesson)


def evaluate(rows, policy, served_key='_served'):
    """Rates for one candidate policy over evidence rows.

    Returns counts and UPPER 95 % bounds for the two harms that are measured separately:
    `ft`  — false trust (the plane's own wrongness definition)
    `tc`  — teaching-critical error
    `harm` — their UNION, which on the gold plane is strictly larger than either.
    """
    p = normalise(policy)
    missing = [c for c in p['clauses'] if not CLAUSES[c]['available']]
    served = [r for r in rows if r.get(served_key)]
    adm = [r for r in served if admits(r, p)[0]]
    n = len(adm)
    ft = sum(1 for r in adm if r.get('truth_wrong_any'))
    tc = sum(1 for r in adm if r.get('truth_teaching_critical'))
    harm = sum(1 for r in adm if r.get('truth_wrong_any') or r.get('truth_teaching_critical'))
    refusal_counts = {}
    for r in served:
        for c in admits(r, p)[1]:
            refusal_counts[c] = refusal_counts.get(c, 0) + 1
    out = dict(
        policy=p['name'], n_rows=len(rows), n_served=len(served), n_trusted=n,
        trusted_share_of_served=round(n / len(served), 4) if served else None,
        ft_k=ft, ft_rate=round(ft / n, 4) if n else None,
        ft_upper95=round(wilson_upper(ft, n), 4) if n else None,
        tc_k=tc, tc_rate=round(tc / n, 4) if n else None,
        tc_upper95=round(wilson_upper(tc, n), 4) if n else None,
        harm_k=harm, harm_rate=round(harm / n, 4) if n else None,
        refused_by=dict(sorted(refusal_counts.items(), key=lambda kv: -kv[1])),
        unavailable_clauses=missing,
    )
    if missing:
        # A clause that cannot run has not been measured. Say so instead of publishing a rate
        # that silently assumes the missing machinery works.
        out['MEASUREMENT_INVALID'] = (
            'this policy names clause(s) whose machinery does not exist: '
            + ', '.join(missing) + '. The rates above were computed with those clauses '
            'REFUSING EVERYTHING, so they are a lower bound on trusted count and say nothing '
            'about what the clause would catch.')
    return out


# --------------------------------------------------------------------------------------
# Canonical form + identity hygiene
# --------------------------------------------------------------------------------------

def canonical(obj):
    """Bytes a hash is taken over. NFC, sorted keys, no ASCII escaping, compact separators —
    so the same policy always hashes the same on any machine."""
    import json

    def norm(o):
        if isinstance(o, str):
            return unicodedata.normalize('NFC', o)
        if isinstance(o, dict):
            return {norm(k): norm(v) for k, v in o.items()}
        if isinstance(o, list):
            return [norm(x) for x in o]
        return o
    return json.dumps(norm(obj), sort_keys=True, ensure_ascii=False,
                      separators=(',', ':')).encode('utf-8')


#: A book id as it appears everywhere in this repo, e.g. `05-sgk-lich-su-va-dia-li-5`.
BOOK_ID_RE = re.compile(r'\b\d{2}-sg[kv]-[a-z0-9-]+\b')
#: `Bài 17`, `Bai 8`, `bài 61` …
LESSON_REF_RE = re.compile(r'\bB[àa]i\s*\d+\b', re.IGNORECASE)
#: Any key that would name what a threshold ADMITS.
ADMITTED_KEY_RE = re.compile(r'admitted|trusted_(?:blocks|lessons|ids)|eligible_lessons',
                             re.IGNORECASE)


def identity_leaks(obj, path='$'):
    """Where a payload names a lesson or book identity in an ADMISSION context.

    The order «policy frozen → population frozen → admitted set» is only provable if no
    artefact produced before an approval shows which lessons a threshold would admit. This is
    the check that makes the claim testable rather than asserted.
    """
    hits = []

    def walk(o, p, in_admit):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f'{p}.{k}', in_admit or bool(ADMITTED_KEY_RE.search(str(k))))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f'{p}[{i}]', in_admit)
        elif isinstance(o, str) and in_admit:
            if BOOK_ID_RE.search(o) or LESSON_REF_RE.search(o):
                hits.append((p, o[:80]))
    walk(obj, path, False)
    return hits
