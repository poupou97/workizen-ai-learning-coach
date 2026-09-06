#!/usr/bin/env python3
"""Round 6 · WS-A — the CONSERVATION LEDGER, and the hard failure that enforces it.

    INPUT SOURCE REGIONS
      = SERVED + WITHHELD + EXCLUDED_WITH_REASON + explicitly defined non-learning regions

INPUT SOURCE REGIONS for a lesson = every SDM block on the lesson's own boundary pages. That is the
population round 5's served share and over-withhold rate were both computed *inside*, after content had
already been dropped from it; this ledger computes it *before* anything is dropped, so the two rates can
be read against the same base.

Every region gets exactly one disposition and one reason. Anything the pipeline cannot name is
UNACCOUNTED, and `audit --strict` (the default) exits non-zero when a single region is UNACCOUNTED.
This is a check that FAILS, not a warning: round 5's silent loss was invisible precisely because nothing
failed.

    ledger.py audit --batch-dir DIR --pipeline ID [--out FILE] [--md FILE] [--historical]

`--historical` reports without failing, which is how a round-5 artefact is measured without pretending
its numbers changed. Counts and reason codes only: block text stays in gitignored `poc-out/`.
"""
import argparse
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dispositions as D  # noqa: E402

SCHEMA = 'ws-a-conservation-ledger-v1'
INVARIANT = ('INPUT SOURCE REGIONS = SERVED + WITHHELD + EXCLUDED_WITH_REASON + '
             'explicitly defined non-learning regions')


def _role(b):
    r = b.get('role')
    return (r.get('value') if isinstance(r, dict) else r) or ''


def _load(path, default=None):
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def tsl_path(batch_dir, pipeline, book, lesson):
    return (f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{pipeline}/lessons/'
            f'{book}/bai-{int(lesson):02d}.tsl.json')


def sdm_files(batch_dir, pipeline, book):
    return sorted(glob.glob(f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{pipeline}/sdm/{book}/*.json'))


def _other_lesson_ids(batch_dir, pipeline, book, lesson):
    """Block ids that a DIFFERENT lesson of the same book already accounts for.

    Two lessons share a page at a mid-page header, so a block on this lesson's boundary page can
    legitimately belong to its neighbour. That is an exclusion with a reason, not a loss — but only
    when the neighbour's own ledger really carries it.
    """
    out = {}
    for p in sorted(glob.glob(f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{pipeline}/lessons/{book}/*.tsl.json')):
        t = _load(p) or {}
        if int(t.get('lesson', -1)) == int(lesson):
            continue
        n = t.get('lesson')
        for b in t.get('blocks', []) + t.get('withheld', []) + t.get('excluded', []):
            out[b['id']] = n
    return out


def block_slot(bid):
    """`book:pNNN:<pipeline>:NNN` → (book, page, native index), the part that is stable across pipelines.

    A downstream stage (WS-C's repair projection) runs on its own generation of the same lesson, so its
    block ids carry a different pipeline segment. The page and the native block index do not change, so
    they are what a cross-generation join may use — never the whole id, and never text.
    """
    parts = (bid or '').split(':')
    return (parts[0], parts[1], parts[-1]) if len(parts) >= 4 else (bid, '', '')


def ledger_lesson(batch_dir, pipeline, book, lesson, demotions=()):
    """The conservation ledger for one lesson. None when the lesson has no TSL in this batch.

    `demotions` are block ids a DOWNSTREAM stage moved out of the served set — WS-C's repair projection
    honouring a fail-closed ledger ruling, for instance. They are applied here and counted separately,
    because two different things can move a served share in one round: an accounting fix that reclassifies
    regions which were never accounted for, and a demotion that withdraws a region that WAS served.
    Folding them into one number would hide both.
    """
    tsl = _load(tsl_path(batch_dir, pipeline, book, lesson))
    if not tsl:
        return None
    demoted_slots = {block_slot(x) for x in (demotions or ())}
    pages = set((tsl.get('boundary') or {}).get('pages') or [])
    served = {b['id'] for b in tsl.get('blocks', [])}
    withheld = {w['id'] for w in tsl.get('withheld', [])}
    demoted = {i for i in served if block_slot(i) in demoted_slots}
    served -= demoted
    withheld |= demoted
    # Present only once the TSL itself conserves (the R13 fix). Absent on round-5 artefacts, which is
    # exactly the defect: the artefact could not say what it had excluded, so the ledger has to derive it.
    excluded_in_tsl = {x['id']: (x.get('reason') or 'excluded') for x in (tsl.get('excluded') or [])}
    neighbours = _other_lesson_ids(batch_dir, pipeline, book, lesson)

    rows, by_disp, by_reason, by_class = [], collections.Counter(), collections.Counter(), collections.Counter()
    for f in sdm_files(batch_dir, pipeline, book):
        page = (_load(f) or {}).get('page')
        if page not in pages:
            continue
        for b in (_load(f) or {}).get('blocks', []):
            bid, role = b['id'], _role(b)
            if bid in served:
                disp, reason = D.SERVED, 'served'
            elif bid in demoted:
                disp, reason = D.WITHHELD, 'withheld:demoted_downstream'
            elif bid in withheld:
                disp, reason = D.WITHHELD, 'withheld'
            elif bid in excluded_in_tsl:
                disp, reason = D.EXCLUDED, excluded_in_tsl[bid]
            elif bid in neighbours:
                disp, reason = D.EXCLUDED, f'other_lesson:{neighbours[bid]}'
            else:
                disp, reason = D.disposition_for_unaccounted_role(role, b.get('text'), D.ocr_line_texts(b))
            cls = (D.classify_unread(b.get('text'), D.ocr_line_texts(b)) if role == 'empty' else None)
            txt = (b.get('text') or '')
            by_disp[disp] += 1
            by_reason[reason] += 1
            if cls:
                by_class[cls] += 1
            rows.append(dict(id=bid, page=page, role=role, disposition=disp, reason=reason,
                             unreadClass=cls, chars=len(txt.strip()),
                             digits=bool(D.DIGIT.search(txt)), expression=bool(D.EXPRESSION.search(txt)),
                             ocrLines=len([x for x in D.ocr_line_texts(b) if (x or '').strip()])))
    inp = len(rows)
    s, w, e, u = by_disp[D.SERVED], by_disp[D.WITHHELD], by_disp[D.EXCLUDED], by_disp[D.UNACCOUNTED]
    # An exclusion is a claim that a region is not learning content. When the excluded region carries an
    # arithmetic expression the claim deserves a second look — it does not fail the invariant (the region
    # IS accounted, with a reason and its evidence), but it is exactly where a diagram-aware recogniser
    # would find printed exercises. Surfaced as a work queue, never as a licence to serve it.
    cbe = [r for r in rows if r['disposition'] == D.EXCLUDED and r['expression']]
    return dict(
        book=book, lesson=int(lesson), pages=sorted(pages),
        inputSourceRegions=inp, served=s, withheld=w, excludedWithReason=e, unaccounted=u,
        demotedDownstream=len(demoted),
        conserves=(s + w + e + u == inp) and u == 0,
        excludedSource=('tsl.excluded' if excluded_in_tsl else 'derived-from-sdm'),
        byReason=dict(by_reason), byUnreadClass=dict(by_class),
        excludedCarryingDigits=sum(1 for r in rows if r['disposition'] == D.EXCLUDED and r['digits']),
        excludedCarryingAnExpression=len(cbe),
        contentBearingExclusionsByReason=dict(collections.Counter(r['reason'] for r in cbe)),
        # Round 5 published `trusted / (trusted + withheld)`. The honest denominator is every region the
        # pipeline extracted that is not a defined non-learning region.
        servedShareAsReported=(round(s / (s + w), 4) if (s + w) else None),
        servedShareOfLearningRegions=(round(s / (s + w + u), 4) if (s + w + u) else None),
        servedShareOfAllInputRegions=(round(s / inp, 4) if inp else None),
        unaccountedIds=[r['id'] for r in rows if r['disposition'] == D.UNACCOUNTED][:12],
        rows=rows)


def ledger_batch(batch_dir, pipeline, demotions=()):
    spec = _load(f'{batch_dir}/batch-spec.json', {}) or {}
    lessons = []
    for L in spec.get('lessons', []):
        r = ledger_lesson(batch_dir, pipeline, L['book'], L['lesson'], demotions)
        if r:
            lessons.append(r)
    tot = {k: sum(l[k] for l in lessons) for k in
           ('inputSourceRegions', 'served', 'withheld', 'excludedWithReason', 'unaccounted',
            'excludedCarryingDigits', 'excludedCarryingAnExpression', 'demotedDownstream')}
    by_reason, by_class, by_cbe = collections.Counter(), collections.Counter(), collections.Counter()
    for l in lessons:
        by_reason.update(l['byReason'])
        by_class.update(l['byUnreadClass'])
        by_cbe.update(l['contentBearingExclusionsByReason'])
    inp, s, w, u = (tot['inputSourceRegions'], tot['served'], tot['withheld'], tot['unaccounted'])
    return dict(
        schema=SCHEMA, invariant=INVARIANT, batchDir=os.path.abspath(batch_dir), pipeline=pipeline,
        lessons=len(lessons),
        conserves=all(l['conserves'] for l in lessons) and u == 0,
        **tot,
        byReason=dict(by_reason), byUnreadClass=dict(by_class),
        contentBearingExclusionsByReason=dict(by_cbe),
        servedShareAsReported=(round(s / (s + w), 4) if (s + w) else None),
        servedShareOfLearningRegions=(round(s / (s + w + u), 4) if (s + w + u) else None),
        servedShareOfAllInputRegions=(round(s / inp, 4) if inp else None),
        perLesson=[{k: v for k, v in l.items() if k != 'rows'} for l in lessons])


def _md(out):
    L = ['| lesson | input regions | SERVED | WITHHELD | EXCLUDED (reason) | **UNACCOUNTED** | served share as reported | served share of learning regions |',
         '|---|---|---|---|---|---|---|---|']
    for r in out['perLesson']:
        L.append(f"| {r['book']} Bài {r['lesson']} | {r['inputSourceRegions']} | {r['served']} | {r['withheld']} | "
                 f"{r['excludedWithReason']} | **{r['unaccounted']}** | {r['servedShareAsReported']} | "
                 f"{r['servedShareOfLearningRegions']} |")
    L.append(f"| **all** | **{out['inputSourceRegions']}** | **{out['served']}** | **{out['withheld']}** | "
             f"**{out['excludedWithReason']}** | **{out['unaccounted']}** | **{out['servedShareAsReported']}** | "
             f"**{out['servedShareOfLearningRegions']}** |")
    if out['byUnreadClass']:
        L += ['', '| unread class | count |', '|---|---|']
        for k, v in sorted(out['byUnreadClass'].items(), key=lambda x: -x[1]):
            L.append(f'| `{k}` | {v} |')
    return '\n'.join(L) + '\n'


def cmd_audit(a):
    dem = []
    if a.demotions:
        d = _load(a.demotions, [])
        dem = d.get('blockIds', []) if isinstance(d, dict) else list(d)
    out = ledger_batch(a.batch_dir, a.pipeline, dem)
    if out['demotedDownstream']:
        print(f"  note: {out['demotedDownstream']} region(s) DEMOTED downstream (served → withheld) — "
              f"reported apart from this workstream's own reclassification, never folded into it")
    for r in out['perLesson']:
        print(f"  {r['book']} Bài {r['lesson']}: input {r['inputSourceRegions']} = served {r['served']} "
              f"+ withheld {r['withheld']} + excluded {r['excludedWithReason']} + UNACCOUNTED {r['unaccounted']}")
    print(f"  TOTAL input {out['inputSourceRegions']} = served {out['served']} + withheld {out['withheld']} "
          f"+ excluded {out['excludedWithReason']} + UNACCOUNTED {out['unaccounted']}")
    if out['byUnreadClass']:
        print('  unread classes: ' + ', '.join(f'{k}={v}' for k, v in sorted(out['byUnreadClass'].items())))
    if out['excludedCarryingAnExpression']:
        print(f"  note: {out['excludedCarryingAnExpression']} excluded region(s) carry an arithmetic "
              f"expression — accounted, but a recognition work queue, not a licence to serve")
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'→ {a.out}')
    if a.md:
        os.makedirs(os.path.dirname(os.path.abspath(a.md)), exist_ok=True)
        open(a.md, 'w', encoding='utf-8').write(_md(out))
        print(f'markdown → {a.md}')
    if out['unaccounted']:
        msg = (f"CONSERVATION FAILURE: {out['unaccounted']} source region(s) carry no disposition. "
               f"{INVARIANT}")
        if a.historical:
            print(f'  [--historical] {msg}')
            return 0
        print(f'  {msg}', file=sys.stderr)
        return 1
    print('  CONSERVATION HOLDS — every input source region carries an explicit disposition.')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('audit')
    s.add_argument('--batch-dir', required=True)
    s.add_argument('--pipeline', required=True)
    s.add_argument('--out', default='')
    s.add_argument('--md', default='')
    s.add_argument('--demotions', default='',
                   help='JSON list (or {"blockIds": [...]}) of block ids a downstream stage moved out of '
                        'the served set; joined on (book, page, native index) so it works across generations')
    s.add_argument('--historical', action='store_true',
                   help='report an UNACCOUNTED count without failing (used to measure a historical artefact)')
    s.set_defaults(fn=cmd_audit)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
