#!/usr/bin/env python3
"""Round 6 · WS-A — the disposition vocabulary, and the classifier for the regions that had none.

Round 5 (§8.2, R13) measured a defect that no rate in the repository could see: a block whose role is
`empty` reaches **neither** `blocks` nor `withheld` of the Trusted Structured Lesson. Withholding is a
decision a lesson can be audited for; that is a *disappearance*, and it carries no reason code. It is
invisible to served share (the base already shrank) and invisible to over-withhold rate (which reviews
only regions that WERE withheld).

The invariant this module exists to make checkable:

    INPUT SOURCE REGIONS
      = SERVED + WITHHELD + EXCLUDED_WITH_REASON + explicitly defined non-learning regions

Four dispositions, and nothing else:

  SERVED                  the region reached the child (TSL `blocks[]`)
  WITHHELD                the region was refused, with reasons (TSL `withheld[]`)
  EXCLUDED_WITH_REASON    the region is a *defined* non-learning region, or is accounted in a
                          neighbouring lesson's ledger — always with an explicit reason code
  UNACCOUNTED             none of the above  ⇒  **HARD FAILURE**

`EXCLUDED_WITH_REASON` is deliberately NOT a synonym for `WITHHELD`. Converting every lost region to
`WITHHELD` would trade a silent loss for a mass over-withhold, and round 5 already measured
over-withholding getting worse (0.400 → 0.633). A page number is not withheld teaching content; it is
a region with an evidence-supported reason to be outside the learning surface. A block reading
`7 8 2 8 7 - 2 8 5 8` is neither — it is teaching content the role layer had no vocabulary for, and
`empty_block` / "no letters" misstates what was lost.
"""
import re

SERVED = 'SERVED'
WITHHELD = 'WITHHELD'
EXCLUDED = 'EXCLUDED_WITH_REASON'
UNACCOUNTED = 'UNACCOUNTED'
DISPOSITIONS = (SERVED, WITHHELD, EXCLUDED, UNACCOUNTED)

#: Roles that are *defined* non-learning regions. Each one is a decision the pipeline can defend with
#: evidence about the printed page, not a place to hide content that was not understood.
NON_LEARNING_ROLES = {
    'page_number': 'non_learning:page_number',
    'running_head': 'non_learning:running_head',
    'figure': 'non_learning:figure_region',
    'figure_text': 'non_learning:figure_text',
}

#: The classes the single `empty` bucket was hiding. Only `no_content` is an acceptable exclusion:
#: a region with no block text AND no OCR line under it has nothing that could have been lost. Every
#: other class carries printed content and must end as SERVED or WITHHELD, never as an exclusion.
UNREAD_CLASSES = (
    'no_content',                    # no block text, no OCR line: nothing was lost
    'unreadable_region',             # no block text, but OCR lines under the region carry printed content
    'numeric_expression_inline',     # letterless, one printed line, digits + an arithmetic operator
    'numeric_expression_stacked',    # letterless, ≥ 3 OCR lines: a stacked/fraction expression, flattened
    'numeric_label',                 # letterless digits, no operator (map / table / diagram figures)
    'symbol_fragment',               # letterless, no digits: an operator or rule torn off its expression
)
ACCEPTABLE_UNREAD_EXCLUSIONS = frozenset({'no_content'})

LETTERS = re.compile(r'[A-Za-zÀ-ỹ]')
DIGIT = re.compile(r'\d')
#: An expression-shaped run: two digit groups with an arithmetic operator between them. Deliberately
#: loose, and identical to the round-5 `silent_loss.EXPRESSION` so the two censuses stay comparable.
EXPRESSION = re.compile(r'\d[\d\s]*\s*[+\-−×÷:x*/]\s*[\d\s]*\d')
STACKED_MIN_LINES = 3


def ocr_line_texts(block):
    """The texts of the OCR lines that sit under a block, as the SDM recorded them (may be absent)."""
    g = block.get('geometry') or {}
    return [(l.get('text') or '') for l in (g.get('lines') or [])]


def classify_unread(text, ocr_lines):
    """Which class of region was hiding behind role `empty`?

    `text` is the block's flat text; `ocr_lines` the texts of the OCR lines under its bbox. Pure
    function of what the extractor recorded — no thresholds, no guessing at content.
    """
    t = (text or '').strip()
    lines = [x for x in (ocr_lines or []) if (x or '').strip()]
    if not t:
        return 'no_content' if not lines else 'unreadable_region'
    if EXPRESSION.search(t):
        return 'numeric_expression_stacked' if len(lines) >= STACKED_MIN_LINES else 'numeric_expression_inline'
    if DIGIT.search(t):
        return 'numeric_label'
    return 'symbol_fragment'


def unread_evidence(cls, text, ocr_lines):
    """The truthful evidence string for an `empty`-role block, replacing the blanket "no letters".

    Round 5 §8.2: *«`empty_block` on a block reading `7 8 2 8 7 - 2 8 5 8` also misstates what was
    lost.»* The evidence names the class and the geometry that proves it; it never carries the text.
    """
    n = len([x for x in (ocr_lines or []) if (x or '').strip()])
    chars = len((text or '').strip())
    return {
        'no_content': 'no block text and no OCR line under the region',
        'unreadable_region': f'block text empty but {n} OCR line(s) under the region carry printed content',
        'numeric_expression_inline': f'no letters: an arithmetic expression on {n or 1} printed line ({chars} chars)',
        'numeric_expression_stacked': f'no letters: an arithmetic expression flattened from {n} printed lines',
        'numeric_label': f'no letters: a digit run, no operator ({chars} chars, {n} line(s))',
        'symbol_fragment': f'no letters and no digits: {chars} symbol char(s) on {n} line(s)',
    }[cls]


def unread_guard(cls):
    """The guard reason code for an `empty`-role block. `no_content` keeps the historical
    `empty_block`; every other class gets a code that says what was actually there."""
    return 'empty_block' if cls == 'no_content' else f'unread:{cls}'


def disposition_for_unaccounted_role(role, text, ocr_lines):
    """→ (disposition, reason) for a region that reached neither TSL list, from its role alone."""
    if role in NON_LEARNING_ROLES:
        return EXCLUDED, NON_LEARNING_ROLES[role]
    if role == 'empty':
        cls = classify_unread(text, ocr_lines)
        if cls in ACCEPTABLE_UNREAD_EXCLUSIONS:
            return EXCLUDED, f'non_learning:{cls}'
        return UNACCOUNTED, unread_guard(cls)
    return UNACCOUNTED, f'dropped_with_role:{role}'
