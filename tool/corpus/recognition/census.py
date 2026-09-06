#!/usr/bin/env python3
"""FAILURE CENSUS — count the forms before writing any rule.

The standing rule of round 5, established three times over: a rule written from a handful of
examples covers a handful of examples. Lane C found 112 date mentions in 8 forms and could
accept a rule for 1; E1's enumeration rule reached 104 of 224 pages and its date rule exactly 3;
E2's sequence rule fired on 6 of 54 gold pages. So this module does not fix anything. It counts.

Every class below is detected by SHAPE — no world knowledge, no lexicon, no model — and every
count is reported against a **stated denominator**. Three denominators are used and never summed,
because they measure different things:

  LINE     one Apple Vision OCR line, from `poc-out/graph/ocr-body`. The population where a
           character-level failure is observable at all.
  REGION   one printed stacked-fraction region found from the page RASTER by
           `mathfix.detect`, whether or not the OCR read either half. The population where a
           «the digit was never read» failure is observable.
  BLOCK    one SDM block. The population where a ROLE decision is observable.

The classes are the ones round 6 named. A class this module cannot observe deterministically is
reported as NOT MEASURED rather than estimated — an unmeasured class is a known gap; a guessed
count is a false one.
"""
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from mathfix import sci_notation as SN

# ---------------------------------------------------------------- the classes
DIGIT_LOSS = 'DIGIT_LOSS'
OPERATOR_LOSS = 'OPERATOR_LOSS'
FRACTION_STRUCTURE = 'FRACTION_STRUCTURE'
SUPERSCRIPT = 'SUPERSCRIPT'
SUBSCRIPT = 'SUBSCRIPT'
ROMAN_NUMERAL = 'ROMAN_NUMERAL'
DIACRITIC = 'DIACRITIC'
SYMBOL_CONFUSION = 'SYMBOL_CONFUSION'
SEGMENTATION = 'SEGMENTATION'
MATH_REGION = 'MATH_REGION'
FORMULA = 'FORMULA'
TABLE_STRUCTURE = 'TABLE_STRUCTURE'
OTHER = 'OTHER'


@dataclass
class Finding:
    """One observed failure, with enough to find it again on the printed page."""
    cls: str
    rule_id: str
    book: str
    page: int
    text: str
    matched: str = ''
    bbox: tuple = None
    note: str = ''


# ---------------------------------------------------------------- LINE-level detectors
#
# A Roman section number whose second stroke Vision read as a digit. The books number their
# sections «I», «II», «III» and set them at the head of a line followed by a dash or a stop, so
# the shape is tight: Roman strokes, then a digit that cannot be part of a Roman numeral, then a
# separator. `I1 - Định luật khúc xạ ánh sáng` is the Founder's named defect, verbatim.
ROMAN_BROKEN = re.compile(r'^\s*(?P<head>[IVX]{1,3})(?P<digit>[0-9l|])\s*(?P<sep>[-–—.)–])\s')
# The same failure without a separator, where the heading runs straight into its title in caps.
ROMAN_BROKEN_TITLE = re.compile(r'^\s*(?P<head>[IVX]{1,3})(?P<digit>[0-9])\s+(?=[A-ZĐÀ-Ỹ])')

# Ω read as a capital-plus-digit run. Shape only: the ohm sign is the only glyph in these books
# that a recogniser turns into `S2`/`Q2`/`52` inside a unit context, and the context is what the
# rule requires — an equals sign, a number, or an SI prefix immediately before.
#   MEASURED AND CORRECTED. The first version admitted `52` and `92` into the alternation and
#   accepted a bare `=` as the unit context, and the crop probe on its first 60 findings returned
#   `52 - 20 = ?` (Toán 1 tập hai p59), `52 + 3 = 55.` and `520 = 250` — ordinary arithmetic in
#   primary maths books, 60 of 60 with no ohm anywhere. Reported rather than quietly fixed: it is
#   the same failure round 5 named three times, committed here, and caught by the census probe
#   rather than by review.
OHM_LOST = re.compile(r'(?<![A-Za-zÀ-ỹ0-9])[kKMmµ]?[SQ]2(?![A-Za-zÀ-ỹ0-9])')
OHM_CONTEXT = re.compile(r'(?:ôm|[Oo]hm|[Đđ]iện trở|\bM[SQ]\b|\bk[SQ]\b|\bmS\b|vôn kế|ampe)')

# A subscript flattened onto the baseline: an element-shaped letter run glued to a digit. This is
# NOT a chemistry test — `tc2_sdm.CHEM` already fires on this shape and round 5 measured >=40 of
# its 173 matches as non-chemical. It is counted here as what it is: a lost subscript LEVEL, of
# which chemistry is one instance and `I₁`/`R₂`/`U₂` in physics is another.
SUBSCRIPT_FLAT = re.compile(r'(?<![A-Za-zÀ-ỹ0-9])(?P<sym>[A-Z][a-z]?)(?P<idx>[0-9])(?![0-9A-Za-zÀ-ỹ])')
ELEMENTS = frozenset(
    'H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se '
    'Br Kr Rb Sr Y Zr Nb Mo Ag Cd In Sn Sb Te I Xe Cs Ba Pt Au Hg Pb Bi'.split())
PHYSICS_SYMBOLS = frozenset('I R U P Q F E A V W T S N M B D L C G'.split())

# An enumerator, a bare number and an operator fused into one token — the segmentation failure
# that produced `b) 10 +.` where the page prints `b) 3/10 +`. The denominator digit is glued to
# the item letter and the numerator is simply absent.
GLUED_ENUM_MATH = re.compile(r'^\s*[a-eA-E]\s*[)\].]\s*\d{1,4}\s*[+\-–—−×÷:]\s*[.,]?\s*$')

_VOWELS_WITH_TONE = 'aăâeêioôơuưy'


def _strip_diacritics(s):
    """`Cộng hoà` -> `Cong hoa`. Đ/đ handled explicitly; NFD does not decompose them."""
    s = s.replace('Đ', 'D').replace('đ', 'd')
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def line_findings(book, page, text, bbox=None):
    """Every LINE-level failure this module can observe in one OCR line."""
    out = []
    t = text or ''
    for f in SN.find_destroyed_exponents(t):
        out.append(Finding(SUPERSCRIPT, 'destroyed-exponent-v1', book, page, t, f.matched, bbox,
                           note=f'si_expected={f.expected_exponent}'))
    for rx, rule in ((ROMAN_BROKEN, 'roman-broken-v1'), (ROMAN_BROKEN_TITLE, 'roman-broken-title-v1')):
        m = rx.match(t)
        if m:
            out.append(Finding(ROMAN_NUMERAL, rule, book, page, t, m.group(0).strip(), bbox,
                               note=f"reads as {m.group('head')}+{m.group('digit')}"))
            break
    if OHM_CONTEXT.search(t):
        m = OHM_LOST.search(t)
        if m:
            out.append(Finding(SYMBOL_CONFUSION, 'ohm-lost-v1', book, page, t, m.group(0), bbox,
                               note='a unit context with a capital-plus-digit where Ω is printed'))
    for m in SUBSCRIPT_FLAT.finditer(t):
        sym = m.group('sym')
        if sym in ELEMENTS or sym in PHYSICS_SYMBOLS:
            out.append(Finding(SUBSCRIPT, 'subscript-flattened-v1', book, page, t, m.group(0), bbox,
                               note='element' if sym in ELEMENTS else 'physics symbol'))
            break
    if GLUED_ENUM_MATH.match(t):
        out.append(Finding(SEGMENTATION, 'glued-enumerator-math-v1', book, page, t, t.strip(), bbox,
                           note='an item letter, a bare number and an operator in one token'))
    return out


# ---------------------------------------------------------------- DIACRITIC, per book
def diacritic_candidates(counter_by_book, min_total=8, max_share=0.25):
    """Word forms a book writes BOTH with and without their diacritics.

    The evidence is meant to be the book contradicting itself: a press does not set `Cộng hoà`
    350 times and `Cong hoa` twice on purpose.

    **MEASURED AND FALSIFIED at the unigram level — see the census document.** Run over
    2 398 513 OCR lines this returns 26 703 forms in 529 books, and its top rows are `qua`/`quá`,
    `cung`/`cũng`, `nay`/`này`, `thu`/`thủ`. Every one of those bare forms is an ordinary
    Vietnamese word in its own right, so «the book writes both» is not evidence of anything: the
    unigram test cannot separate a lost tone mark from a different word without a lexicon it does
    not have. The function is kept, and its output is reported as a **denominator, not a count**.

    `diacritic_bigram_candidates` is the form that survives, and it survives for a stated reason.

    Returns `{book: [(bare_form, bare_count, dominant_form, dominant_count), ...]}`.
    """
    out = {}
    for book, groups in counter_by_book.items():
        rows = []
        for key, forms in groups.items():
            if len(forms) < 2:
                continue
            total = sum(forms.values())
            if total < min_total:
                continue
            bare = forms.get(key, 0)
            if not bare:
                continue
            dominant, dom_n = max(((f, n) for f, n in forms.items() if f != key), key=lambda kv: kv[1])
            if dominant == key or dom_n <= bare:
                continue
            if bare / total > max_share:
                continue
            rows.append((key, bare, dominant, dom_n))
        if rows:
            out[book] = sorted(rows, key=lambda r: -r[1])
    return out


_WORD = re.compile(r'[A-Za-zÀ-ỹĐđ]{3,}')


def diacritic_index(lines_by_book):
    """Build the `{book: {stripped: Counter(surface)}}` index `diacritic_candidates` consumes."""
    idx = defaultdict(lambda: defaultdict(Counter))
    for book, lines in lines_by_book.items():
        for text in lines:
            for w in _WORD.findall(text or ''):
                low = w.lower()
                stripped = _strip_diacritics(low)
                if stripped == low and not any(c in _VOWELS_WITH_TONE for c in low):
                    continue                       # nothing here could have carried a diacritic
                idx[book][stripped][low] += 1
    return idx


# ---------------------------------------------------------------- REGION-level classification
@dataclass
class RegionCensus:
    """The fraction-region half of the census — the population round 5 could not repair."""
    total: int = 0
    by_class: Counter = field(default_factory=Counter)
    examples: dict = field(default_factory=lambda: defaultdict(list))

    def add(self, cls, key, note=''):
        self.total += 1
        self.by_class[cls] += 1
        if len(self.examples[cls]) < 6:
            self.examples[cls].append((key, note))


def classify_region(region, tokens, mask_height):
    """Why this printed fraction is not readable — and which class the failure belongs to.

    This is the distinction round 5's «274 of 336: the OCR never read the digit» did not draw,
    and it decides what to build: a half with NO overlapping token at all is DIGIT LOSS — nothing
    was recognised there. A half with a token that is not a bare digit run is SEGMENTATION — the
    ink WAS recognised, and glued to something else. The two need different answers.
    """
    if region.extractable:
        return None, ''
    missing = []
    if region.reason in ('numerator_token_missing', 'denominator_token_missing'):
        missing = [region.reason.split('_')[0]]
    elif region.reason in ('numerator_ambiguous', 'denominator_ambiguous'):
        return FRACTION_STRUCTURE, region.reason
    elif region.reason == 'token_shared':
        return FRACTION_STRUCTURE, region.reason
    else:
        return OTHER, region.reason or 'unknown'

    half = missing[0]
    bar = region.bar
    above = half == 'numerator'
    y0, y1 = ((bar.y0 - 0.06, bar.y0) if above else (bar.y1, bar.y1 + 0.06))
    overlapping = [t for t in tokens
                   if t.y1 > y0 and t.y0 < y1
                   and min(bar.x1, t.x1) - max(bar.x0, t.x0) > 0.25 * (t.x1 - t.x0)]
    if not overlapping:
        return DIGIT_LOSS, f'{half}: no OCR token of any kind over the bar'
    return SEGMENTATION, f'{half}: read as {overlapping[0].stripped!r}, not as a digit run'


def diacritic_bigram_candidates(bigrams_by_book, min_total=8, max_share=0.25):
    """The same test on ADJACENT PAIRS of words, which is where it starts to mean something.

    `hoa` alone is a word, so `hóa`/`hoa` proves nothing. `cộng hoà` is a fixed collocation, and a
    book that prints it 350 times and `cộng hoa` twice has not changed its mind about spelling —
    the second reading is a recognition failure. Requiring BOTH words of the pair to match after
    stripping, and at least one of them to differ before stripping, is what removes the ordinary
    homographs the unigram test drowned in.

    Still not a proof: it is a candidate list for a human to confirm, and it is reported as one.
    """
    out = {}
    for book, groups in bigrams_by_book.items():
        rows = []
        for key, forms in groups.items():
            if len(forms) < 2:
                continue
            total = sum(forms.values())
            if total < min_total:
                continue
            bare = forms.get(key, 0)
            if not bare:
                continue
            dominant, dom_n = max(((f, n) for f, n in forms.items() if f != key),
                                  key=lambda kv: kv[1])
            if dom_n <= bare or bare / total > max_share:
                continue
            rows.append((key, bare, dominant, dom_n))
        if rows:
            out[book] = sorted(rows, key=lambda r: -r[1])
    return out


def diacritic_bigram_index(lines_by_book):
    """`{book: {stripped_pair: Counter(surface_pair)}}` for `diacritic_bigram_candidates`."""
    idx = defaultdict(lambda: defaultdict(Counter))
    for book, lines in lines_by_book.items():
        for text in lines:
            ws = [w.lower() for w in _WORD.findall(text or '')]
            for a, b in zip(ws, ws[1:]):
                pair = f'{a} {b}'
                idx[book][_strip_diacritics(pair)][pair] += 1
                #   The bare pair must be indexed too — it IS the group key, and a group that
                #   only ever holds its own key is dropped by `len(forms) < 2` downstream.
    return idx
