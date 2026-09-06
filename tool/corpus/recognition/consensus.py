#!/usr/bin/env python3
"""Turn several untrusted readings of one box into one verdict — or into a refusal.

A recogniser that is allowed to answer whenever it feels like it will raise digit recall and
quietly raise the false-recognition rate with it. Round 5's rule applies here without change:

    `false_correction_rate` is the right P0 for a repairer and is BLIND to a detector.
    If you raise recall, report the false-recognition rate beside it, or you will look
    perfect by recognising nothing.

So this module never «picks the best» reading. It accepts a reading only when independent
observations of the same printed box agree, and it refuses — loudly, with a reason — otherwise.
The independent observations are:

  * the same box rendered at several SCALES. Not «higher resolution»: the corpus pages are
    100 ppi scans, so a scale change resamples the same information differently and Vision's
    segmentation lands elsewhere. Measured on Toán 5 tập một p22 region 28, the round-4 defect
    `b) 3/10 + 5/21`: scale 3 reads `-` and `10`, scale 6 reads `3`, `1`, `0`, scale 12 reads
    `10` alone, scale 20 reads `3` then `10`. Agreement across scales is therefore a real
    signal and not a formality — a single scale is not evidence.
  * the numerator box and the denominator box, each asked ALONE;
  * the whole region, asked as one picture, which is the only observation that says the two
    halves STACK. Round 5: completeness and honesty do not prove identity.

Everything here is pure Python over dictionaries. No raster, no subprocess, no dependency.
"""
import re
from collections import Counter
from dataclasses import dataclass, field

DIGIT_RUN = re.compile(r'^\d{1,4}$')

#: at least this many DISTINCT scales must return the same string for a box before it is read.
#: Two is the smallest number that can disagree; one scale is an anecdote, and on the pages
#: measured here a wrong reading has never been reproduced at a second scale.
MIN_AGREEING_SCALES = 2

READ = 'READ'
UNREAD = 'UNREAD'                       # nothing legible came back at any scale
CONFLICT = 'CONFLICT'                   # two scales read two different things — fail closed
INSUFFICIENT = 'INSUFFICIENT_AGREEMENT'  # only one scale read it
AMBIGUOUS = 'AMBIGUOUS'                 # a scale returned more than one legible line in the box


@dataclass
class BoxReading:
    """What the recogniser said about one box, across every scale it was asked at."""
    kind: str
    verdict: str
    value: str = None
    per_scale: dict = field(default_factory=dict)     # scale -> the raw strings returned
    agreeing_scales: tuple = ()
    note: str = ''

    @property
    def ok(self):
        return self.verdict == READ


def _digit_lines(lines):
    """The bare digit runs among a crop's returned lines, in the order they came back."""
    return [ln['text'].strip() for ln in lines if DIGIT_RUN.match((ln.get('text') or '').strip())]


def read_half(per_scale_lines, min_agreeing=MIN_AGREEING_SCALES):
    """One half of a fraction, from `{scale: [line, ...]}`.

    A scale VOTES only when it returns exactly one bare digit run. Two lines in a numerator
    crop means either the neighbouring fraction bled in or the glyph was split, and neither is
    something this module is allowed to repair by joining: joining is reconstruction, and
    reconstruction from fragments is the round-3 failure the whole lane exists to avoid.
    """
    votes, raw = {}, {}
    ambiguous = []
    for scale, lines in sorted(per_scale_lines.items()):
        digits = _digit_lines(lines)
        raw[scale] = [(ln.get('text') or '').strip() for ln in lines]
        if len(digits) == 1:
            votes[scale] = digits[0]
        elif len(digits) > 1:
            ambiguous.append(scale)
    if not votes:
        return BoxReading('half', UNREAD if not ambiguous else AMBIGUOUS, per_scale=raw,
                          note=f'ambiguous at scales {ambiguous}' if ambiguous else '')
    counts = Counter(votes.values())
    if len(counts) > 1:
        return BoxReading('half', CONFLICT, per_scale=raw,
                          note='; '.join(f'{v}x{c}' for v, c in counts.most_common()))
    value = next(iter(counts))
    agreeing = tuple(s for s, v in sorted(votes.items()) if v == value)
    if len(agreeing) < min_agreeing:
        return BoxReading('half', INSUFFICIENT, value=value, per_scale=raw,
                          agreeing_scales=agreeing)
    return BoxReading('half', READ, value=value, per_scale=raw, agreeing_scales=agreeing)


def region_supports(per_scale_lines, numerator, denominator):
    """Does the whole-region picture show those two halves, stacked, at any scale?

    The check is deliberately about ORDER, not about text: a region crop that returns `3` above
    `10` supports `3/10`; one that returns `10` above `3` does not, and one that returns a third
    digit run does not either, because something else is inside the box being read.
    """
    for scale, lines in sorted(per_scale_lines.items()):
        digits = [ln for ln in lines if DIGIT_RUN.match((ln.get('text') or '').strip())]
        if len(digits) != 2:
            continue
        top, bottom = sorted(digits, key=lambda ln: ln.get('y', 0.0))
        if top['text'].strip() == numerator and bottom['text'].strip() == denominator:
            return True, scale
    return False, None


@dataclass
class FractionReading:
    """The verdict for one printed fraction region."""
    region_key: str
    verdict: str
    numerator: BoxReading
    denominator: BoxReading
    value: str = None
    candidate: str = None      # what was refused, kept for the ledger. NEVER a value: a consumer
    #   that reads `value` must never see a string this module declined to accept, and round 5's
    #   two false corrections both looked like perfectly good strings.
    region_agreement_scale: float = None
    reason: str = ''

    @property
    def ok(self):
        return self.verdict == READ


def read_fraction(region_key, num_lines, den_lines, region_lines,
                  min_agreeing=MIN_AGREEING_SCALES, require_region=True):
    """The whole rule, in one place, fail-closed at every step."""
    n = read_half(num_lines, min_agreeing)
    d = read_half(den_lines, min_agreeing)
    if not (n.ok and d.ok):
        bad = n if not n.ok else d
        return FractionReading(region_key, bad.verdict, n, d,
                               reason=f'{"numerator" if not n.ok else "denominator"}:{bad.verdict.lower()}')
    if require_region:
        ok, scale = region_supports(region_lines, n.value, d.value)
        if not ok:
            return FractionReading(region_key, 'REGION_UNCONFIRMED', n, d,
                                   candidate=f'{n.value}/{d.value}',
                                   reason='the two halves were read but never seen stacked')
        return FractionReading(region_key, READ, n, d, value=f'{n.value}/{d.value}',
                               region_agreement_scale=scale)
    return FractionReading(region_key, READ, n, d, value=f'{n.value}/{d.value}')
