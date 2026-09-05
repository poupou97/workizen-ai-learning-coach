#!/usr/bin/env python3
"""Round 5 · the validator for `vi_text_diacritic`.

The Founder's rule, implemented literally: *a trusted repair must be confirmed by an independent signal or
source*, and *false correction matters most*. So:

* any **objection** from any layer rejects - one `objects` is fatal, whatever else supports;
* the proposal must be **legal Vietnamese** and must be a tone or single-vowel-quality edit of what was
  observed - `edit_kind == 'other'` is rejected outright, so no repair can rewrite a word into a different
  word;
* the proposal must not move a digit or an operator (layer C's fail-closed default);
* **two distinct supporting layers** are required, and for a repair that actually *changes* the text one of
  them must be outside layer A - i.e. the document (D) or the source/layout (B) must agree with the
  lexicon. A change confirmed only by Vietnamese frequency is exactly the failure mode the corpus table is
  vulnerable to («thủỷ» is attested on 743 pages), so frequency alone is never enough to change a word.
* a repair that changes nothing (the arbitration resolved in favour of what was already there) needs the
  same two layers, but layer A may be one of them - it is restoring an *observed* reading, not inventing one.
"""
from __future__ import annotations

from .. import model, registry
from ..repairers.vi_text import FAILURE_CLASS, tokenize
from ..vi import syllable

VALIDATOR_ID = 'vi.independent-signal-v1'


def _edit_kinds(observed, proposed):
    a, b = tokenize(observed), tokenize(proposed)
    if len(a) != len(b):
        return ['other']
    return [syllable.edit_kind(x[0], y[0]) for x, y in zip(a, b) if x[0] != y[0]]


@registry.validator(FAILURE_CLASS, validator_id=VALIDATOR_ID)
def validate(candidate, ctx):
    ev = []
    obj = candidate.objections()
    if obj:
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                      evidence=[dict(kind='objection', signal=s.signal_id,
                                                     detail=dict(s.detail)) for s in obj],
                                      detail=dict(reason='a signal objects'))
    observed = candidate.original_observations[0].value or ''
    proposed = candidate.proposed_value or ''
    changed = bool(candidate.provenance.get('changed'))

    kinds = _edit_kinds(observed, proposed)
    if any(k == 'other' for k in kinds):
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                      evidence=[dict(kind='edit_kind', kinds=kinds)],
                                      detail=dict(reason='a repair may only move diacritics, never rewrite a word'))
    for tok, _s, _e in tokenize(proposed):
        if not syllable.is_legal(tok):
            return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                          evidence=[dict(kind='illegal_syllable', token=tok)],
                                          detail=dict(reason='the proposal is not legal Vietnamese'))

    layers = candidate.independent_support()
    ev.append(dict(kind='supporting_layers', layers=layers, edit_kinds=kinds, changed=changed))
    if len(layers) < 2:
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.INSUFFICIENT, evidence=ev,
                                      detail=dict(reason='fewer than two independent signal layers'))
    if changed and not [x for x in layers if x != 'A']:
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.INSUFFICIENT, evidence=ev,
                                      detail=dict(reason='a text change needs a layer outside the Vietnamese '
                                                         'lexicon (the corpus table shares the OCR\'s own errors)'))
    return model.ValidationResult(VALIDATOR_ID, model.Verdict.VALIDATED, evidence=ev,
                                  detail=dict(layers=layers, changed=changed))
