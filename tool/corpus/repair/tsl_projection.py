#!/usr/bin/env python3
"""Round 6 · Workstream C — the join that makes a validated repair VISIBLE in a product-shaped TSL.

Round 5's repair engine runs on **SDM pages**, where the observations live. The Trusted Structured
Lesson is built from those pages by `tc2_tsl.py`, and it is fail-closed by design: a withheld region
arrives carrying `text: null` and a reason code, and nothing else. The consequence, verified:

    a withheld region in a TSL has NO observation, so the repair path cannot even be asked about it,
    and the repair ledger - which knows the answer - is never joined to the lesson.

This module is that join, written as a **pure TSL -> TSL post-pass**. It reads a TSL and a repair
ledger and returns a new TSL in which each repaired region carries its `ValidatedRepair`. It does not
touch `tc2_sdm.py` (workstream A's role layer) or `tc2_tsl.py`, so it composes with whatever those do.

WHAT IT MAY DO
  * attach a `ValidatedRepair` record to a withheld region, which stays withheld and stays text-less;
  * publish the records under a top-level `repairs[]`, and count them in `stats.repair`;
  * demote a region the laboratory pipeline had already restored, recording WHY it was demoted.

WHAT IT CANNOT DO — by construction, not by configuration
  * make anything TRUSTED. There is no argument, flag, threshold or environment variable in this file
    that promotes a repair. `ValidatedRepair` cannot even hold the value `TRUSTED`, and
    `check_projection()` asserts no record carries it. **CONNECT != TRUST**: connecting the path is a
    workstream's job, setting a production trust threshold is the Founder's, and the two are kept
    apart here by the absence of a mechanism rather than by the discipline of the caller.
  * give a withheld region text. `assert 'text' not in region or region['text'] is None` is checked
    on the way out for every region, whether this pass touched it or not.
  * move a region from `withheld` into `blocks`. The count of served blocks may only go DOWN.

THE LABORATORY-RESTORE CAP, and why it is loud
`run_gold.py` writes a repaired pipeline (`tc2-p3`) in which a validated repair has been RESTORED:
the block's SDM trust status is `TRUSTED`, so `tc2_tsl.py` puts it in `blocks`, with text, and the
bridge would serve it. That is the pipeline trusting a repair with no Founder decision behind it.
So a served block with a repair in the ledger is, by default, a **refusal** (`on_served_repair=
'refuse'`, nothing written); `'withhold'` is offered for research runs and demotes the block to a
withheld region carrying its record. Neither mode can serve a repaired value.

DETECTED-BUT-UNREPAIRED (`SUSPECT` / `CONFLICT`) is *reported*, not acted on, by default. Demoting a
served block on a detection is a false-demotion risk (round 5: demotion precision 0.250 on 4 blocks)
and it changes accounting that workstream A owns. `on_detected_unrepaired='withhold'` exists for a
measured run; the report always names the blocks either way.
"""
from __future__ import annotations

import copy
import json
from collections import Counter, defaultdict

from . import ledger as ledger_mod
from . import model
from .model import Disposition
from .validated import (RepairIntegrityError, TrustEscalation, ValidatedRepair)

PROJECTION_VERSION = 'tsl-repair-projection-v1'

#: the reason string a laboratory restore is capped with. Written onto the record's `caps`, into the
#: region's reasons, and into the report - three places, because a silent cap is a silent loss.
CAP_TRUST_GATE = 'trust_gate:founder_decision_absent'
REASON_NOT_TRUSTED = 'repair_not_trusted'
REASON_DETECTED = 'detected_unrepaired'
REASON_SERVED_UNREPAIRED = 'served_text_has_validated_repair'


class UnTrustedRepairServed(RepairIntegrityError):
    """A TSL served a block the repair ledger says was repaired. Fail-closed: nothing is written."""


def block_key(block_id):
    """`<book>:pNNN:<pipeline>:<order>` -> `<book>:pNNN:<order>`.

    A TSL block id embeds the PIPELINE NAME, and the ledger was written against the *baseline*
    pipeline while the TSL may be built from the repaired one. Joining on the raw id silently matches
    nothing - and «no repairs found» is indistinguishable from «no repairs exist». Same normalisation
    as `tsl_to_lesson_document.block_key`, deliberately: one join rule in the codebase, not two.
    """
    parts = (block_id or '').split(':')
    return ':'.join(parts[:2] + parts[3:]) if len(parts) >= 4 else block_id


def chains(rows):
    """Ledger rows -> {block_key: [row, ...]} in file order. Rows are dicts as written to the JSONL."""
    out = defaultdict(list)
    for r in rows:
        out[block_key(r.get('block_id'))].append(r)
    return dict(out)


def _final_rows(rows):
    """From one block's chain, pick the row that states the outcome, plus whether a RESTORE happened.

    The engine writes `detect` -> `validate` -> `dispose`, and `restore` only when the caller served
    it. The dispose row is the block's outcome; a validate row is used when the caller stopped there.
    """
    restored = any(r.get('stage') == 'restore' or r.get('disposition') == Disposition.TRUSTED
                   for r in rows)
    dispose = [r for r in rows if r.get('stage') == 'dispose']
    validate = [r for r in rows if r.get('stage') == 'validate'
                and r.get('disposition') == Disposition.VALIDATED_REPAIR]
    outcome = dispose[-1] if dispose else (validate[-1] if validate else None)
    if outcome is not None and outcome.get('disposition') == Disposition.TRUSTED and validate:
        # a restore row superseded the dispose row; the *repair* is the validated one underneath it
        outcome = validate[-1]
    return outcome, restored, bool(validate)


def repairs_for_tsl(tsl, rows, *, source_version=None):
    """Build the `ValidatedRepair`s that apply to this lesson, keyed by block key.

    Returns `(by_key, other)` where `other` maps a block key to a non-validated outcome
    (`SUSPECT`, `CONFLICT`, `WITHHELD`) for the report. Ledger rows about blocks that are not in this
    lesson are ignored and counted, never guessed at.
    """
    sv = dict(source_version or {})
    sv.setdefault('pipeline', tsl.get('pipeline'))
    sv.setdefault('book', tsl.get('book'))
    sv.setdefault('lesson', tsl.get('lesson'))
    prov0 = ((tsl.get('blocks') or [{}])[0].get('provenance') or {})
    sv.setdefault('sdm_version', prov0.get('sdm_version'))
    sv.setdefault('projection', PROJECTION_VERSION)

    in_lesson = {block_key(b['id']) for b in tsl.get('blocks') or []}
    in_lesson |= {block_key(w['id']) for w in tsl.get('withheld') or []}

    by_key, other, skipped = {}, {}, 0
    for key, rws in chains(rows).items():
        if key not in in_lesson:
            skipped += 1
            continue
        outcome, restored, has_validated = _final_rows(rws)
        if outcome is None:
            continue
        if outcome.get('disposition') != Disposition.VALIDATED_REPAIR:
            other[key] = dict(disposition=outcome.get('disposition'),
                              failure_class=outcome.get('failure_class'),
                              reasons=list(outcome.get('reasons') or ()),
                              entry_id=outcome.get('entry_id'))
            continue
        caps = [CAP_TRUST_GATE] if restored else []
        entry = ledger_mod.entry_from_json(outcome)
        by_key[key] = ValidatedRepair.from_entry(entry, source_version=sv, caps=caps)
    return by_key, other, skipped


def ledger_run(rows):
    """The `run` block `Ledger` stamps on every JSONL line: which baseline was repaired and which
    pipeline the repaired output was written as. Without it the join cannot tell a TSL built FROM the
    repaired pipeline (where a laboratory restore is live) from one built from the baseline (where the
    ledger is advisory). Absent -> unknown, and the projection stays in its advisory, no-action mode."""
    for r in rows:
        if isinstance(r.get('run'), dict) and r['run']:
            return dict(r['run'])
    return {}


def classify_served(vr, block, *, restored, same_pipeline):
    """What does it MEAN that this block is served while the ledger records a repair for it?

    Four different things, and round 5 shows why conflating them is how a lane fools itself:

    * `repair_served`   - the served text IS the proposal. An ungated repair is on the path to a child.
                          A VIOLATION, whatever pipeline built the TSL.
    * `restore_served`  - the ledger RESTORED a block the guard had withheld, and this TSL was built
                          from that repaired pipeline. Serving it is the trust decision, ungated.
                          A VIOLATION.
    * `served_unrepaired` - the served text is the ORIGINAL OBSERVATION and a validator judged it wrong.
                          Nothing was laundered; the lesson carries pre-existing false trust. A FINDING:
                          acting on it changes served counts that workstream A's accounting owns, and
                          «never weaken a guard for coverage» has a mirror - never tighten one on a
                          cross-pipeline inference either.
    * `join_unverified` - the served text is neither the observation nor the proposal, so this TSL's
                          text is not the text the ledger saw. NO claim is made and NO action is taken.
    """
    served = block.get('text')
    if vr.changed and served == vr.proposed_value:
        return 'repair_served', True
    if served == vr.observed_value:
        if restored and same_pipeline:
            return 'restore_served', True
        return 'served_unrepaired', False
    return 'join_unverified', False


def project(tsl, rows, *, source_version=None, on_served_repair='refuse',
            on_detected_unrepaired='report', on_served_unrepaired='report'):
    """TSL + ledger rows -> (new TSL, report). Pure: the input TSL is never mutated.

    `on_served_repair`: 'refuse' (default) raises `UnTrustedRepairServed` on a VIOLATION; 'withhold'
    demotes the block to a withheld region carrying its record and the reason `repair_not_trusted`.
    `on_served_unrepaired` / `on_detected_unrepaired`: 'report' (default) or 'withhold'.
    """
    for name, v in (('on_served_repair', on_served_repair),
                    ('on_detected_unrepaired', on_detected_unrepaired),
                    ('on_served_unrepaired', on_served_unrepaired)):
        allowed = ('refuse', 'withhold') if name == 'on_served_repair' else ('report', 'withhold')
        if v not in allowed:
            raise ValueError(f'{name} must be one of {allowed} - there is no mode that serves an '
                             f'ungated repair')

    out = copy.deepcopy(tsl)
    run = ledger_run(rows)
    same_pipeline = bool(run.get('pipeline')) and out.get('pipeline') == run.get('pipeline')
    by_key, other, skipped = repairs_for_tsl(out, rows, source_version=source_version)
    restored_keys = {k for k, rws in chains(rows).items()
                     if any(r.get('stage') == 'restore' or r.get('disposition') == Disposition.TRUSTED
                            for r in rws)}

    kept_blocks, demoted = [], []
    counts = Counter()
    violations, findings = [], []

    for b in out.get('blocks') or []:
        key = block_key(b['id'])
        vr = by_key.get(key)
        oth = other.get(key)
        if vr is not None:
            kind, is_violation = classify_served(vr, b, restored=key in restored_keys,
                                                 same_pipeline=same_pipeline)
            row = dict(block_id=b['id'], repair_id=vr.repair_id, kind=kind,
                       failure_class=vr.failure_class, method=vr.repair_method, changed=vr.changed)
            counts['served_' + kind] += 1
            if is_violation:
                violations.append(row)
                if on_served_repair == 'withhold':
                    demoted.append((b, vr, REASON_NOT_TRUSTED))
                    counts['served_repair_demoted'] += 1
                continue                      # 'refuse' raises below; nothing is written either way
            findings.append(row)
            if kind == 'served_unrepaired' and on_served_unrepaired == 'withhold':
                demoted.append((b, vr, REASON_SERVED_UNREPAIRED))
                counts['served_unrepaired_demoted'] += 1
                continue
            kept_blocks.append(b)             # NOT annotated: a served block never carries a repair record
            continue
        if oth is not None and oth['disposition'] in (Disposition.SUSPECT, Disposition.CONFLICT):
            counts['detected_unrepaired_on_served_block'] += 1
            findings.append(dict(block_id=b['id'], kind='detected_unrepaired',
                                 disposition=oth['disposition'], failure_class=oth.get('failure_class')))
            if on_detected_unrepaired == 'withhold':
                demoted.append((b, None, REASON_DETECTED + ':' + (oth.get('failure_class') or 'unknown')))
                counts['detected_unrepaired_demoted'] += 1
                continue
        kept_blocks.append(b)

    if violations and on_served_repair == 'refuse':
        raise UnTrustedRepairServed(
            f'{len(violations)} block(s) of {out.get("book")} bai-{out.get("lesson")} serve a repair the '
            f'ledger never had gated. A validated repair is not a trusted one; serving it is a Founder '
            f'gate. First: {violations[0]}')

    withheld = list(out.get('withheld') or [])
    for b, vr, reason in demoted:
        role = b.get('role')
        region = dict(id=b['id'], page=b['page'], page_printed=b.get('page_printed'), order=b['order'],
                      role=role.get('value') if isinstance(role, dict) else role,
                      bbox=b['bbox'], reasons=[reason], status='WITHHELD',
                      text_len=len(b.get('text') or ''), provenance=dict(b.get('provenance') or {}),
                      text=None)
        if vr is not None:
            region['repair'] = vr.to_block_json()
            region['disposition'] = vr.disposition
        withheld.append(region)

    crossed = 0
    for w in withheld:
        key = block_key(w['id'])
        vr = by_key.get(key)
        if vr is None:
            oth = other.get(key)
            if oth is not None:
                w['disposition'] = oth['disposition']
                counts['unrepaired_' + str(oth['disposition']).lower()] += 1
            continue
        if 'repair' in w:                      # already attached above (a demoted served block)
            crossed += 1
            continue
        w['repair'] = vr.to_block_json()
        w['disposition'] = vr.disposition      # VALIDATED_REPAIR - visible, countable, still withheld
        if CAP_TRUST_GATE in vr.caps and CAP_TRUST_GATE not in (w.get('reasons') or []):
            w['reasons'] = list(w.get('reasons') or []) + [CAP_TRUST_GATE]
        w['text'] = None                       # explicit: a repaired region is still a text-less one
        crossed += 1

    withheld.sort(key=lambda r: (r.get('page') or 0, r.get('order') or 0))
    out['blocks'] = kept_blocks
    out['withheld'] = withheld
    # `repairs[]` carries the PROPOSED VALUE and stays corpus-side: INTERNAL / RESEARCH ONLY (Founder D4).
    # The bridge to the app copies only `to_block_json()`, which has no value in it.
    out['repairs'] = [by_key[k].to_json() for k in sorted(by_key)]
    out['repairProjection'] = dict(
        version=PROJECTION_VERSION, framework=model.FRAMEWORK_VERSION,
        onServedRepair=on_served_repair, onServedUnrepaired=on_served_unrepaired,
        onDetectedUnrepaired=on_detected_unrepaired,
        ledgerRun=run, samePipelineAsLedger=same_pipeline,
        productionTrustThreshold=None,
        findings=findings,
        note='CONNECT != TRUST. No mechanism in this projection produces a TRUSTED disposition; '
             'a validated repair is visible and countable, and is still withheld from a child.')
    stats = dict(out.get('stats') or {})
    stats['repair'] = dict(
        validatedRepairs=len(by_key),
        crossedIntoTsl=crossed,
        trusted=0,
        cappedLaboratoryRestores=sum(1 for v in by_key.values() if CAP_TRUST_GATE in v.caps),
        changedValue=sum(1 for v in by_key.values() if v.changed),
        unchangedValue=sum(1 for v in by_key.values() if not v.changed),
        byFailureClass=dict(Counter(v.failure_class for v in by_key.values())),
        byMethod=dict(Counter(v.repair_method for v in by_key.values())),
        detectedUnrepaired=dict(Counter(o['disposition'] for o in other.values())),
        ledgerRowsForOtherLessons=skipped,
        **{k: v for k, v in counts.items()})
    stats['trusted'] = len(kept_blocks)
    stats['withheld'] = len(withheld)
    out['stats'] = stats
    report = dict(book=out.get('book'), lesson=out.get('lesson'), pipeline=out.get('pipeline'),
                  validated_repairs=len(by_key), crossed=crossed, trusted_repairs=0,
                  same_pipeline_as_ledger=same_pipeline, ledger_run=run,
                  violations=violations, findings=findings, detected_unrepaired=other,
                  capped=[v.repair_id for v in by_key.values() if CAP_TRUST_GATE in v.caps],
                  stats=stats['repair'])
    check_projection(tsl, out)
    return out, report


def check_projection(before, after):
    """Post-conditions. These are the whole safety argument, so they run on every projection.

    They are deliberately about CONSERVATION and NON-ESCALATION, the two ways this pass could do harm:
    a region could disappear (round 5's R13 silent loss, from the other end), or a repair could become
    servable without a decision.
    """
    ids_before = ([b['id'] for b in before.get('blocks') or []]
                  + [w['id'] for w in before.get('withheld') or []])
    ids_after = ([b['id'] for b in after.get('blocks') or []]
                 + [w['id'] for w in after.get('withheld') or []])
    assert len(ids_after) == len(set(ids_after)), 'duplicate ids after projection'
    lost = set(ids_before) - set(ids_after)
    assert not lost, f'projection lost regions (silent loss): {sorted(lost)[:5]}'
    gained = set(ids_after) - set(ids_before)
    assert not gained, f'projection invented regions: {sorted(gained)[:5]}'

    served_before = {b['id'] for b in before.get('blocks') or []}
    served_after = {b['id'] for b in after.get('blocks') or []}
    promoted = served_after - served_before
    assert not promoted, f'projection PROMOTED regions into the served set: {sorted(promoted)[:5]}'

    text_before = {b['id']: b.get('text') for b in before.get('blocks') or []}
    for b in after.get('blocks') or []:
        assert b.get('text') == text_before.get(b['id']), \
            f'projection altered served text of {b["id"]} - the TSL is READ-ONLY for text'

    known = set()
    for r in after.get('repairs') or []:
        assert r.get('disposition') == Disposition.VALIDATED_REPAIR, \
            f'repair record {r.get("repairId")} carries disposition {r.get("disposition")!r}'
        assert r.get('servable') is False, f'repair record {r.get("repairId")} claims to be servable'
        known.add(r.get('repairId'))

    for w in after.get('withheld') or []:
        assert w.get('text') in (None, ''), f'withheld region {w["id"]} carries text after projection'
        assert w.get('reasons'), f'withheld region {w["id"]} has no reason code'
        rep = w.get('repair')
        if rep:
            assert rep.get('repairId') in known, \
                f'region {w["id"]} names repair {rep.get("repairId")!r} that is not in repairs[]'
            assert rep.get('disposition') == Disposition.VALIDATED_REPAIR
            assert 'proposedValue' not in rep and 'text' not in rep, \
                f'region {w["id"]} carries the repaired value inline - a renderer could read it'
    for b in after.get('blocks') or []:
        rep = b.get('repair')
        assert not rep or rep.get('disposition') != Disposition.VALIDATED_REPAIR, \
            f'served block {b["id"]} carries an untrusted repair'
    return True


# ------------------------------------------------------------------ CLI (research runs, no writes by default)
def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description='Join a repair ledger onto a TSL. Never trusts anything.')
    ap.add_argument('--tsl', required=True)
    ap.add_argument('--ledger', required=True, help='repair-ledger.jsonl from run_gold.py')
    ap.add_argument('--out', help='write the projected TSL here (default: report only)')
    ap.add_argument('--on-served-repair', default='refuse', choices=('refuse', 'withhold'))
    ap.add_argument('--on-detected-unrepaired', default='report', choices=('report', 'withhold'))
    ap.add_argument('--on-served-unrepaired', default='report', choices=('report', 'withhold'))
    a = ap.parse_args(argv)
    tsl = json.load(open(a.tsl, encoding='utf-8'))
    rows = ledger_mod.read(a.ledger)
    out, report = project(tsl, rows, on_served_repair=a.on_served_repair,
                          on_detected_unrepaired=a.on_detected_unrepaired,
                          on_served_unrepaired=a.on_served_unrepaired)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as fh:
            json.dump(out, fh, ensure_ascii=False)
        print(f'wrote {a.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
