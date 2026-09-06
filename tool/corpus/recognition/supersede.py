#!/usr/bin/env python3
"""WAL-213 · the recogniser side of the supersession contract.

`study.block_projection` measures the round-7 defect exactly:

    aug_tokens = list(tokens) + list(recovered)

It **ADDS**. The destroyed whole-page observation stays, so a block holds two overlapping
expressions and `math_line_candidate` glues both into one line — the measured
`0) 1 3 8/14 2/7` on Toán 4 Bài 61 p83, which is why `10 -> 10, delta 0`.

This module turns each recovered region into a `repair.supersession.Supersession`: the destroyed
page-pass observations it covers, the recovered observation that replaces them, the engine, the
scales that agreed, and the region/stacking evidence. `resolve_tokens()` then produces the token
list a validator may read — page tokens **minus** the ones that were superseded, **plus** the
recovered ones — or refuses, per block, when any region is unresolved.

**Nothing here decides trust and nothing here writes into a pipeline output.** It is a projection,
like round 6's, so the round-7 «before» numbers stay reproducible: `study.py` is untouched.

Two facts about the real population that this module exists to express rather than hide, both
measured on Bài 61 p081-083 at the frozen 4-scale ladder:

  * **4 of 17** recovered regions replace a page token that lies wholly inside the crop the
    recogniser read. Those resolve.
  * **13 of 17** replace a token that carries OTHER PRINTED CONTENT too — an item letter `0)`, an
    operator, a neighbouring fraction's digit. Trimming such a token to fit would be **overwriting
    a source observation**. They are `CONFLICT`, and the block that holds one is refused.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recognition import boxes as B                                  # noqa: E402
from repair import model                                            # noqa: E402
from repair import supersession as SUP                              # noqa: E402

#: The whole-page pass — `mathfix.tokens.Token.engine`'s default, reused verbatim.
PAGE_ENGINE = 'apple-vision-page-v1'
#: The targeted re-crop — the name `study.py` already stamps on a recovered token.
CROP_ENGINE = 'apple-vision-crop-v1'

RULE_ID = 'recognition.recrop-supersede-v1'

#: The signal letter this evidence belongs to in the Founder's priority order: layout/geometry.
REGION_SIGNAL = 'B.region_stacking'
SCALE_SIGNAL = 'F.scale_agreement'


def token_bbox4(t):
    """A `mathfix.tokens.Token` box as `(x0, y0, x1, y1)`.

    The corpus writes token geometry as `(x, y, w, h)` and crop geometry as `(x0, y0, x1, y1)`.
    Mixing the two silently is how a coverage test passes for the wrong reason, so the conversion
    happens exactly here and the contract only ever sees corner form.
    """
    return (float(t.x), float(t.y), float(t.x) + float(t.w), float(t.y) + float(t.h))


def page_observation(block_id, t, *, book=None, page=None, pipeline=None):
    """One whole-page OCR line, as a round-5 `Observation`. Immutable, and never edited."""
    prov = dict(bbox=token_bbox4(t), engine=getattr(t, 'engine', PAGE_ENGINE),
                conf=getattr(t, 'conf', None), token_index=getattr(t, 'index', None))
    if book:
        prov['book'] = book
    if page is not None:
        prov['page'] = page
    if pipeline:
        prov['pipeline'] = pipeline
    return model.Observation(block_id=block_id, source=getattr(t, 'engine', PAGE_ENGINE),
                             value=t.text, provenance=prov)


def recovered_observation(block_id, region_key, value, bbox4, *, book=None, page=None,
                          engine=CROP_ENGINE, agreeing_scales=None, stacking_scale=None):
    """The reading the re-crop produced, as an `Observation` of a DIFFERENT source.

    It is an `ORIGINAL_OBSERVATION` in its own right — it is what a source actually produced — and
    it becomes a replacement only through the relation, never by being written over anything.
    """
    prov = dict(bbox=tuple(float(v) for v in bbox4), engine=engine, region_key=region_key,
                agreeing_scales={k: list(v) for k, v in dict(agreeing_scales or {}).items()},
                stacking_scale=stacking_scale)
    if book:
        prov['book'] = book
    if page is not None:
        prov['page'] = page
    return model.Observation(block_id=block_id, source=engine, value=value, provenance=prov)


def region_evidence(row, text_height):
    """`RegionEvidence` from one `study.py` region row — the boxes the recogniser actually asked
    about, the scales that agreed on each half, and the scale at which the whole-region crop showed
    them stacked."""
    bxs = {b.kind: b.bbox for b in B.fraction_boxes(row['bar'], text_height)}
    scales = {}
    if row.get('numerator_scales'):
        scales['numerator'] = tuple(row['numerator_scales'])
    if row.get('denominator_scales'):
        scales['denominator'] = tuple(row['denominator_scales'])
    return SUP.RegionEvidence(region_key=row['key'],
                              boxes={k: v for k, v in bxs.items() if k != 'region'},
                              agreeing_scales=scales,
                              stacking_scale=row.get('region_scale'),
                              detector='mathfix.detect.find_fraction_regions',
                              bar=tuple(row['bar']))


def covered_tokens(evidence, tokens, *, touch=SUP.TOUCH_COVERAGE):
    """The page tokens this region touches at all — the candidates for supersession.

    Uses the union of the crop boxes the recogniser read (`envelope`), and the token's own box.
    A token grazing the padded crop by less than `touch` is not in this region; anything above it
    is, and whether the replacement may STAND ALONE is then decided by coverage, not here.
    """
    out = []
    for t in tokens:
        f = evidence.covers(token_bbox4(t))
        if f > touch:
            out.append((t, f))
    return out


def supersession_for_row(row, tokens, text_height, block_id, *, book=None, page=None,
                         pipeline=None, validation=None):
    """One recovered region -> a `Supersession`, or `(None, reason)` when it is not one.

    Returns `(supersession, reason)`. `supersession` is None when the region recovered a reading
    with **nothing to replace** — an ADDITION. That is deliberately not expressible as a
    supersession: a value with no superseded observation behind it has not replaced anything, and
    letting it borrow the authority of a replacement is the exact laundering this contract forbids.
    """
    if not row.get('value'):
        return None, 'region was refused by consensus; there is no reading to carry'
    ev = region_evidence(row, text_height)
    hits = covered_tokens(ev, tokens)
    if not hits:
        return None, ('ADDITION: no whole-page observation exists over this region, so nothing is '
                      'superseded. A recovered value with no destroyed observation behind it is an '
                      'addition and is recorded as one.')
    superseded = tuple(page_observation(block_id, t, book=book, page=page, pipeline=pipeline)
                       for t, _ in hits)
    new = recovered_observation(block_id, row['key'], row['value'], ev.envelope, book=book,
                                page=page, agreeing_scales=ev.agreeing_scales,
                                stacking_scale=ev.stacking_scale)
    signals = [
        model.Signal(REGION_SIGNAL,
                     model.SignalVerdict.SUPPORTS if ev.stacked else model.SignalVerdict.ABSTAINS,
                     strength=1.0 if ev.stacked else 0.0,
                     detail=dict(stacking_scale=ev.stacking_scale, region_key=ev.region_key)),
        model.Signal(SCALE_SIGNAL,
                     model.SignalVerdict.SUPPORTS if ev.min_agreeing >= 2 else model.SignalVerdict.ABSTAINS,
                     strength=min(1.0, ev.min_agreeing / 4.0),
                     detail={k: list(v) for k, v in ev.agreeing_scales.items()}),
    ]
    cand = model.RepairCandidate(
        block_id=block_id, failure_class=row.get('failure_class') or 'RECOGNITION',
        original_observations=superseded, proposed_value=row['value'], rule_id=RULE_ID,
        supporting_signals=tuple(signals), confidence=0.0,
        provenance=dict(book=book, page=page, region_key=row['key'], bbox=ev.envelope,
                        engine=CROP_ENGINE, pipeline=pipeline),
        detected=dict(baseline_reason=row.get('baseline_reason'),
                      failure_note=row.get('failure_note'),
                      baseline_value=row.get('baseline_value')))
    s = SUP.Supersession(block_id=block_id, superseded=superseded, superseding=new,
                         engine=CROP_ENGINE, region=ev, candidate=cand,
                         failure_class=row.get('failure_class') or 'RECOGNITION',
                         reason=f'targeted re-crop read {row["key"]} where the page pass could not',
                         validation=validation)
    SUP.assert_not_trusted(s)
    return s, ''


def resolve_tokens(tokens, supersessions, recovered_tokens_by_region):
    """The token list a validator may read, after supersession.

    Page tokens **minus** every one that a FULL supersession replaced, **plus** the recovered
    tokens of the regions that resolved. Regions that did not resolve contribute NOTHING — neither
    the destroyed reading nor the replacement — and their observations are returned separately so
    the caller can fail the whole block closed.

    Returns `(current_tokens, refused_region_keys, audit)`.
    """
    resolved, refused = [], []
    for s in supersessions:
        (resolved if s.resolved else refused).append(s)
    superseded_boxes = {tuple(round(v, 6) for v in dict(o.provenance)['bbox'])
                        for s in resolved for o in s.superseded}
    conflicted_boxes = {tuple(round(v, 6) for v in dict(o.provenance)['bbox'])
                        for s in refused for o in s.superseded}
    current = [t for t in tokens
               if tuple(round(v, 6) for v in token_bbox4(t)) not in superseded_boxes
               and tuple(round(v, 6) for v in token_bbox4(t)) not in conflicted_boxes]
    for s in resolved:
        current.extend(recovered_tokens_by_region.get(s.region.region_key) or ())
    audit = dict(resolved=[s.supersession_id for s in resolved],
                 refused=[s.supersession_id for s in refused],
                 superseded_observations=sum(len(s.superseded) for s in resolved),
                 conflicted_observations=sum(len(s.superseded) for s in refused))
    return current, [s.region.region_key for s in refused], audit


def observation_set(block_id, tokens, supersessions, *, book=None, page=None, pipeline=None):
    """An `ObservationSet` for one block: every page observation it holds, plus the relations.

    Built so `resolve()` and `assert_conserved()` can be run on the real population rather than on
    a fixture — the whole point of WAL-213's population rule.
    """
    obs = [page_observation(block_id, t, book=book, page=page, pipeline=pipeline) for t in tokens]
    by_id = {}
    for o in obs:
        by_id.setdefault(o.observation_id, o)
    seen = set()
    rels = []
    for s in supersessions:
        missing = [o.observation_id for o in s.superseded if o.observation_id not in by_id]
        if missing:
            # The relation names an observation this block does not hold: keep it out rather than
            # inventing the observation, and let the caller see the drop.
            continue
        if s.supersession_id in seen:
            continue
        seen.add(s.supersession_id)
        rels.append(s)
    st = SUP.ObservationSet(block_id, tuple(by_id.values()))
    for s in rels:
        st = st.with_supersession(s)
    return st
