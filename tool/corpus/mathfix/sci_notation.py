#!/usr/bin/env python3
"""A destroyed power-of-ten exponent — detection only, never a repair.

The 97-row audit's defect ①: the book prints `3×10⁸ m/s` and the product serves `3×10° m/s`. The
speed of light becomes nonsense, and — unlike the Toán failures — this one is **served TRUSTED**:

  · the error is born in RECOGNITION. Apple Vision reads the superscript ⁸ as a degree sign. No
    later stage rewrites it, so there is nothing to «normalise»;
  · no guard sees it. `MATH` needs a digit after an operator, `UNIT_EXP` covers only m/cm/dm/km/mm
    with exponent 2 or 3, `CHEM` does not match, and `agree_numbers` cannot fire because BOTH OCR
    stacks read the same «°» — round 4's falsified assumption, live;
  · measured: 79 OCR lines across the KHTN / Vật lí / Khoa học books, 7 blocks in the round-4
    tc2-p2 review SDM set, of which **3 are TRUSTED and served today** — the speed of light on two
    pages and «1 Bar = 10° Pa».

So this module DETECTS and reports; the disposition it supports is WITHHOLD. It deliberately does
not repair, because the exponent's value is not in the text: recovering it needs a recogniser on the
printed region, and that recogniser does not exist yet (see `docs/research/MATH-ACCURACY-AUDIT-2026-09-06.md` §7).

`si_expected_exponent` is written as a **validator**, not a generator. Where the page itself states
the prefix relation — «1 kJ = 10ⁿ J», «1 MW = 10ⁿ W» — SI fixes n exactly, and that is an
independent check a future recogniser's reading must pass. It is never used to invent a digit: a
value that came from a table rather than from an observation is a guess with a nice pedigree.
"""
import re
from dataclasses import dataclass

# «10» glued to a degree sign or a prime and followed by a unit letter or a digit: scientific
# notation whose exponent did not survive. Shape only — no world knowledge, no constant table.
#   `(?<!\d)` only: «.» and «,» BEFORE the ten are the mantissa separator of the printed
#   notation itself («3.10⁸», «1,013.10⁵»), so excluding them would have missed the very lines the
#   audit named. A digit before the ten still blocks it — «110°» is an angle, «3105» is a number.
DESTROYED_EXPONENT = re.compile(r"(?<!\d)10\s*[°'′]\s*(?=[A-Za-zΩµμ]|\d)")
# A genuine temperature or angle reading, which this rule must never touch: «20 °C», «góc 30°».
TEMPERATURE = re.compile(r"°\s*[CF]\b")

# SI prefixes, as a validator only. Value = the power of ten the prefix names.
SI_PREFIX = {'Y': 24, 'Z': 21, 'E': 18, 'P': 15, 'T': 12, 'G': 9, 'M': 6, 'k': 3, 'h': 2, 'da': 1,
             'd': -1, 'c': -2, 'm': -3, 'µ': -6, 'μ': -6, 'n': -9, 'p': -12, 'f': -15, 'a': -18}
# Base units whose prefixed forms appear in the K-12 science books.
BASE_UNIT = ('J', 'W', 'V', 'A', 'N', 'Pa', 'Hz', 'Ω', 'C', 'K', 'g', 'm', 's', 'F', 'H', 'T', 'B')

_PREFIXED = re.compile(
    r'^\s*1\s*(da|[YZEPTGMkhdcmµμnpfa])(' + '|'.join(BASE_UNIT) + r')\b\s*=\s*10\s*[°\'′]?\s*(\d*)\s*('
    + '|'.join(BASE_UNIT) + r')\b')


@dataclass(frozen=True)
class ExponentFinding:
    """One place where a power of ten lost its exponent."""
    start: int
    end: int
    matched: str
    expected_exponent: int = None      # from the printed SI prefixes, when the page states them
    evidence: str = ''

    @property
    def rule_id(self):
        return 'destroyed-exponent-v1'


def si_expected_exponent(text):
    """The exponent the page's OWN printed prefixes entail, or None.

    «1 kJ = 10? J» ⇒ 3.  «1 MW = 10? W» ⇒ 6.  «1 GW = 10? W» ⇒ 9.
    Returns None when the two units differ in kind, when no prefix is printed, or when the relation
    is not of this shape — never a default, never a guess.
    """
    m = _PREFIXED.match(text or '')
    if not m:
        return None
    prefix, left_unit, _digits, right_unit = m.groups()
    if left_unit != right_unit:
        return None
    n = SI_PREFIX.get(prefix)
    return n if (n is not None and n > 0) else None


def find_destroyed_exponents(text):
    """Every destroyed power-of-ten exponent in one block's text.

    A temperature or an angle («20 °C», «góc 30°», «cồn 90°») is not one: the rule requires the
    literal «10» before the mark and a unit or digit after it, so an angle can never match.
    """
    t = text or ''
    out = []
    for m in DESTROYED_EXPONENT.finditer(t):
        window = t[max(0, m.start() - 4):m.end() + 4]
        if TEMPERATURE.search(window):
            continue
        out.append(ExponentFinding(
            start=m.start(), end=m.end(), matched=m.group(0),
            expected_exponent=si_expected_exponent(t),
            evidence='a power of ten followed by a degree sign or prime, then a unit or digit'))
    return out


def withholds(text):
    """True when this block must not be served as it stands. Detection only — nothing is repaired."""
    return bool(find_destroyed_exponents(text))
