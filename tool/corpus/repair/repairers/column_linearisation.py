#!/usr/bin/env python3
"""Round 5 · `column-linearisation-v1` — a second repairer, from Lane C, generalised into the framework.

**The failure it repairs.** `agree_text` withholds a block when the primary's text cannot be aligned into
the verifier's reading-order stream above `TEXT_SIM`. On a two-column page the XY-cut verifier sometimes
*linearises the columns differently* — it reads across a two-column band, or merges two boxes — so the same
words are present on the page but not contiguous in the stream. The guard then reports «the two stacks
disagree about this text» when in fact they agree about every word of it and disagree only about where the
block's boundary is.

**The repair.** Deterministic and evidential, never a threshold change: if every word of the primary block
occurs, **in order and with its diacritics**, somewhere in the verifier's page-level token stream, the
question the guard asked is answered — yes, the verifier read this text. The block is then a
`REPAIRED_CANDIDATE` whose proposed value is *the observed text unchanged*: nothing is rewritten, only the
gate's own reasoning is corrected.

**Why it is still gated.** The two stacks share Apple Vision, so exact agreement is weak evidence of
*correctness* — it is only evidence about the *guard*. Lane A1 measured the naked rule on the dev split at
restore precision **0.762** (16 clean of 21), and with a whole-block Vietnamese legality+attestation sweep
at **0.867** (13 of 15). Neither is good enough to enable by default under «never trade accuracy for
coverage», so this repairer is **registered but off unless `--linearisation` is passed**, and the variant is
measured and reported beside the default so the Founder chooses with numbers rather than adjectives.
"""
from __future__ import annotations

import re
import unicodedata

from .. import model, registry
from ..signals import vi_lexicon
from ..vi import syllable

FAILURE_CLASS = 'text_agreement_segmentation'
RULE = 'column-linearisation-v1'
VALIDATOR_ID = 'linearisation.subsequence-v1'
TOKEN = re.compile(r'[0-9A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+')

ENABLED = False


def enable(on=True):
    global ENABLED
    ENABLED = bool(on)
    return ENABLED


def _place(t):
    import tc_score
    return tc_score.norm_tone_placement(unicodedata.normalize('NFC', t or '')).lower()


def is_subsequence(needle, hay):
    it = iter(hay)
    return all(any(x == n for x in it) for n in needle)


@registry.repairer(FAILURE_CLASS, repairer_id=RULE)
def propose(ctx):
    if not ENABLED:
        return
    if list(ctx.withhold_reasons) != ['agree_text']:
        return                                    # only this reason, and only this reason alone
    stream = (ctx.extra or {}).get('verifier_page_tokens')
    if not stream:
        return
    primary = ctx.primary()
    need = [_place(t) for t in TOKEN.findall(primary.value or '')]
    if len(need) < 2 or not is_subsequence(need, stream):
        return
    yield model.RepairCandidate(
        block_id=ctx.block_id, failure_class=FAILURE_CLASS,
        original_observations=ctx.observations,
        proposed_value=primary.value,             # NOTHING is rewritten
        rule_id=RULE,
        supporting_signals=(
            model.Signal('B.verifier_reading', model.SignalVerdict.SUPPORTS, 0.7,
                         dict(note='every word of the block occurs in order in the verifier\'s page stream; '
                                   'the two stacks disagree about the block boundary, not about the text',
                              tokens=len(need))),
            vi_lexicon.sweep_signal(primary.value, ctx.lexicon, (ctx.page or {}).get('book')),
        ),
        confidence=0.7,
        provenance=dict(covers_reasons=('agree_text',), changed=False,
                        prior_disposition=ctx.disposition, role=ctx.role,
                        book=(ctx.page or {}).get('book'), page=(ctx.page or {}).get('page')),
        detected=dict(kind='verifier column linearisation, not a text disagreement'))


@registry.validator(FAILURE_CLASS, validator_id=VALIDATOR_ID)
def validate(candidate, ctx):
    if candidate.contradicting():
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                      evidence=[dict(kind='objection', signal=s.signal_id) for s in
                                                candidate.contradicting()],
                                      detail=dict(reason='a signal objects - most often the Vietnamese sweep '
                                                         'found a word the corpus has never seen'))
    if candidate.provenance.get('changed'):
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                      detail=dict(reason='this rule never rewrites text'))
    layers = candidate.independent_support()
    if len(layers) < 2:
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.INSUFFICIENT,
                                      evidence=[dict(kind='supporting_layers', layers=layers)],
                                      detail=dict(reason='needs the verifier stream AND a clean Vietnamese sweep'))
    return model.ValidationResult(VALIDATOR_ID, model.Verdict.VALIDATED,
                                  evidence=[dict(kind='supporting_layers', layers=layers),
                                            dict(kind='caveat',
                                                 note='the two stacks share Apple Vision, so this confirms the '
                                                      'GUARD was wrong, not that the text is verbatim')],
                                  detail=dict(layers=layers))
