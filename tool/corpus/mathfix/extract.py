#!/usr/bin/env python3
"""Assemble a candidate value out of ORIGINAL OBSERVATIONS only.

The rule this module exists to enforce: **no character in a proposed value may be invented.**
Every character traces to an OCR token that was actually read off the page, with one single
exception — the «/» that a raster-validated vinculum licences. `digit_provenance` below is the
check, and it runs on the finished string, so a future change to the assembler cannot quietly
smuggle a character past it.

Two repair rules live here:

  `stacked-fraction-v1`  one printed fraction → «n/d», from the two digit-run tokens the detector
                         attached to the bar.
  `math-line-v1`         one withheld block that is entirely arithmetic → the printed line, with
                         every fraction put back where its bar is. It fails closed on anything it
                         cannot fully account for: a fraction whose halves the OCR lost, a token
                         carrying prose, a block whose tokens sit on more than one baseline. One
                         unreadable item poisons the whole block on purpose — serving three correct
                         items and one destroyed one is exactly the round-3 failure.
"""
import re
from dataclasses import dataclass, field

from .tokens import median_height

# Enumerators («a)», «b)», «1.») and operators are the only non-digit characters a repaired maths
# line may carry. Anything else means the block is prose, and prose is not this lane's to repair.
_MATH_TOKEN = re.compile(r'^[\s0-9a-eA-E)(\].,;:%+\-–—−×÷*=<>≤≥≠]+$')
_LETTERS = re.compile(r'[A-Za-zÀ-ỹ]')
_ENUMERATOR_LETTER = re.compile(r'^[a-eA-E]\s*[)\].]')

MULTI_BASELINE_TOL = 0.75    # a token this far from the block's baseline, in text heights, is another line


@dataclass
class Piece:
    """One ordered fragment of a proposed value, with the observation that produced it."""
    text: str
    x: float
    source: str                    # 'ocr_line' | 'fraction'
    observations: list = field(default_factory=list)


@dataclass
class Candidate:
    """A proposed value plus everything needed to audit it. Never replaces a source observation."""
    rule_id: str
    proposed_value: str
    original_observations: list
    supporting_signals: list
    pieces: list = field(default_factory=list)
    regions: list = field(default_factory=list)
    reason: str = ''               # why no value was proposed, when `proposed_value` is ''


def observation_of_token(t):
    return dict(kind='ocr_line', index=t.index, text=t.text,
                bbox=[round(t.x, 6), round(t.y, 6), round(t.w, 6), round(t.h, 6)],
                conf=t.conf)


def observation_of_bar(bar):
    return dict(kind='raster_bar',
                bbox=[round(bar.x0, 6), round(bar.y0, 6), round(bar.length, 6), round(bar.thickness, 6)])


def fraction_candidate(region):
    """`stacked-fraction-v1` — «n/d» for one detected, extractable region."""
    if not region.extractable:
        return Candidate('stacked-fraction-v1', '', [], [], reason=region.reason or 'not_extractable')
    n, d = region.numerator, region.denominator
    return Candidate(
        rule_id='stacked-fraction-v1',
        proposed_value=f'{n.stripped}/{d.stripped}',
        original_observations=[observation_of_token(n), observation_of_token(d),
                               observation_of_bar(region.bar)],
        supporting_signals=['raster:vinculum', 'ocr:numerator_digit_run', 'ocr:denominator_digit_run'],
        regions=[region])


def _is_math_token(t):
    s = t.stripped
    if not s:
        return False
    if not _MATH_TOKEN.match(s):
        return False
    # a lone letter is only allowed as an enumerator: «a)» yes, «a» no, «cm» no
    for m in _LETTERS.finditer(s):
        tail = s[m.start():]
        if not _ENUMERATOR_LETTER.match(tail):
            return False
    return True


def math_line_candidate(block_tokens, regions, mask):
    """`math-line-v1` — the printed arithmetic line of a block that is arithmetic all the way through.

    `regions` are the fraction regions whose bar falls inside the block. Fails closed, with a named
    reason, on: an unextractable region, a token carrying prose, a token on a second baseline, or a
    block with no fraction at all (there is nothing for this lane to repair there).
    """
    if not regions:
        return Candidate('math-line-v1', '', [], [], reason='no_fraction_region')
    bad = [r for r in regions if not r.extractable]
    if bad:
        return Candidate('math-line-v1', '', [], [], regions=regions,
                         reason=f'region_unextractable:{bad[0].reason or "unknown"}')

    consumed = {t.index for r in regions for t in (r.numerator, r.denominator)}
    rest = [t for t in block_tokens if t.index not in consumed and t.stripped]
    for t in rest:
        if not _is_math_token(t):
            return Candidate('math-line-v1', '', [], [], regions=regions,
                             reason='prose_token_in_block')
    if not rest:
        return Candidate('math-line-v1', '', [], [], regions=regions, reason='no_surviving_token')

    mh = median_height(block_tokens) or 0.018
    cys = sorted(t.cy for t in rest)
    baseline = cys[len(cys) // 2]
    if any(abs(t.cy - baseline) > MULTI_BASELINE_TOL * mh for t in rest):
        return Candidate('math-line-v1', '', [], [], regions=regions, reason='multiple_baselines')

    pieces = [Piece(t.stripped, t.x0, 'ocr_line', [observation_of_token(t)]) for t in rest]
    for r in regions:
        f = fraction_candidate(r)
        pieces.append(Piece(f.proposed_value, r.bar.x0, 'fraction', f.original_observations))
    pieces.sort(key=lambda p: p.x)
    value = ' '.join(p.text for p in pieces)
    return Candidate(
        rule_id='math-line-v1',
        proposed_value=re.sub(r'\s+', ' ', value).strip(),
        original_observations=[o for p in pieces for o in p.observations],
        supporting_signals=['raster:vinculum', 'ocr:token_geometry', 'layout:single_baseline'],
        pieces=pieces, regions=regions)


# ---------------------------------------------------------------- provenance
_SYNTHESISED = set('/ ')


def digit_provenance(candidate):
    """Every character of the value must come from an observation; only «/» and space are synthesised.

    Deliberately a multiset check on characters, not a substring check: a substring check would pass
    a value that reordered or duplicated digits, and «19/33 − 3/5 assembled from two printed items»
    is precisely the round-3 defect this lane exists to prevent.
    """
    have = []
    for o in candidate.original_observations:
        if o['kind'] == 'ocr_line':
            have.extend(c for c in o['text'] if not c.isspace())
    pool = {}
    for c in have:
        pool[c] = pool.get(c, 0) + 1
    missing = []
    for c in candidate.proposed_value:
        if c in _SYNTHESISED:
            continue
        if pool.get(c, 0) <= 0:
            missing.append(c)
        else:
            pool[c] -= 1
    return missing
