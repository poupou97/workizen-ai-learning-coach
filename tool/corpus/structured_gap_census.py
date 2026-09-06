#!/usr/bin/env python3
"""ROUND 7 · WS-S — STRUCTURED CONTENT GAP: what are the 118 blocks the app has no type for?

Round 6 (`ROUND6-WS-D-LEARNING-VIEW-CENSUS.md`) measured **118 blocks withheld with reason
`unknown_role:*`** over the 238 canonical TSLs — `footnote` 64 · `activity` 50 · `option` 4 —
and called it «a model gap, not a data gap, and the cheapest win on the board».

This census does NOT accept that framing on trust. It re-derives the 118 from the leaf records
and then asks the three questions that decide whether a type may be added:

  1. **STRUCTURE.** Does the block belong to a structural group (round 5 defect 8: OPTION ⊂ QUESTION,
     caption ⊂ figure, table rows, procedure steps)? If it does, its own disposition is not the
     unit of safety — the group's is. A group served with a member missing is a **mutilated
     structure**, and that is a teaching-critical error *produced by the safety mechanism*.
  2. **ANCHOR.** For a `footnote`: is there a served block carrying its referent marker? A note
     numbered «(1)» served with no «(1)» anywhere on the page is a dangling cross-reference —
     mutilation of a different shape.
  3. **CONTENT.** Is the block actually what its role says? The `activity` bucket is checked for
     round-5 **defect 6** (imprint / back matter leaking into a lesson).

NOTHING HERE CHANGES WHAT IS SERVED. It runs `tsl_to_lesson_document.convert()` read-only, exactly
as the product does, counts what comes out, and computes COUNTERFACTUALS («what would the mutilated-
structure count be if role X were mapped?») without ever writing a document. The counterfactual is
arithmetic on a disposition table; it is not a code path a child can reach.

    python3 tool/corpus/structured_gap_census.py \\
        [--lessons poc-out/trusted-corpus/tc-v2/tc2-p1/lessons] [--json OUT] [--md OUT] [--detail]

Group derivation reuses `tool/corpus/repair/groups.py` — the module written for defect 8 on the
GOLD-PAGE path — through a documented adapter, so the lesson path and the gold path cannot drift
apart on what «a group» means. The adapter's one honest limitation is recorded in
`groups_for_lesson()` and in the report: a withheld TSL region has **no text**, so
`procedure_steps`, which is detected from an enumerator in the text, cannot see a withheld step.
Withheld-member detection is therefore complete for `question_options` and `table_rows` (role-based)
and INCOMPLETE for `procedure_steps` — an under-count, never an over-count.

Standard library only. Read-only on every input.
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))
import tsl_to_lesson_document as bridge  # noqa: E402
from repair import groups as repair_groups  # noqa: E402

DEFAULT_LESSONS = os.path.join(ROOT, 'poc-out', 'trusted-corpus', 'tc-v2', 'tc2-p1', 'lessons')

#: Round-5 defect 6 (imprint / back matter leaking into a lesson), as a text test on the leaf record.
#: Deliberately literal: this is a detector for reporting, not a filter anything depends on.
IMPRINT_LEAD = re.compile(r'^\s*(Trình bày bìa|Chịu trách nhiệm|Biên tập viên|Thiết kế sách|'
                          r'In\s+\d|Số ĐKXB|Mã số:)', re.IGNORECASE)

SUPERSCRIPT = {'1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
               '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '0': '⁰'}
#: A well-formed footnote mark: «(1)», «(12)», «(*)». Everything else that OPENS like a mark but does
#: not close as one — «("», «(i)», «®)», «()» — is MANGLED, and that distinction is the whole point:
#: a note whose own mark the pipeline could not read cannot be anchored to anything.
FOOTNOTE_MARKER = re.compile(r"^\s*\(\s*([0-9]{1,2}|\*{1,2})\s*\)")
FOOTNOTE_MARK_LIKE = re.compile(r"^\s*[(\[®©]")


def role_of(b):
    r = b.get('role')
    return r.get('value') if isinstance(r, dict) else r


def tsl_paths(root):
    out = []
    for dirpath, _dirs, files in os.walk(root):
        for f in sorted(files):
            if f.endswith('.tsl.json'):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


# ----------------------------------------------------------------- group formation on the lesson path
def groups_for_lesson(tsl):
    """Delegates to `tsl_to_lesson_document.structural_groups_of` — ONE definition of «a group» for the
    census, the bridge and the gold path. The adapter and its one honest limitation (a withheld region
    has no text, so `procedure_steps` under-counts) live there."""
    return bridge.structural_groups_of(tsl)


def mutilated(groups, servable_by_id):
    """Groups that WOULD be served with members missing. Same definition as `repair.groups.mutilated`."""
    return repair_groups.mutilated(groups, servable_by_id)


# ----------------------------------------------------------------- per-lesson census
def census_one(path):
    rel = os.path.relpath(path, ROOT)
    with open(path, encoding='utf-8') as fh:
        tsl = json.load(fh)
    try:
        doc = bridge.convert(tsl, tsl_rel_path=rel, tsl_sha256=None,
                             book_meta=bridge.book_meta_for(tsl.get('book')),
                             chapters=None, crops=None)
    except Exception as e:  # a refusal is an answer, not a crash
        return dict(ok=False, rel=rel, refusal=f'{e.__class__.__name__}: {e}'[:200])

    blocks = doc.get('blocks') or []
    # The disposition the PRODUCT actually produces today, keyed by block id.
    servable = {}
    reasons_by_id = {}
    for b in blocks:
        if b.get('type') == 'withheld':
            servable[b['id']] = False
            reasons_by_id[b['id']] = list(b.get('reasons') or [])
        elif b.get('type') != 'sourceRef':
            servable[b['id']] = True
    # withheld[] entries the bridge emits verbatim are already in `blocks`; TSL regions the bridge
    # drops (there are none by contract) would be missing — assert that, do not paper over it.
    tsl_ids = {b['id'] for b in (tsl.get('blocks') or ())} | {w['id'] for w in (tsl.get('withheld') or ())}
    missing = sorted(tsl_ids - set(servable))
    groups = groups_for_lesson(tsl)

    # roles that reach `unknown_role:*` / `no_carrier:*` today
    gap_ids = collections.defaultdict(list)
    for b in blocks:
        if b.get('type') != 'withheld':
            continue
        for r in (b.get('reasons') or ()):
            if r.startswith('unknown_role:') or r.startswith('no_carrier:'):
                gap_ids[r.split(':', 1)[1]].append(b['id'])

    return dict(ok=True, rel=rel, book=doc.get('book'), lesson=doc.get('lesson'),
                servable=servable, reasons=reasons_by_id, groups=groups,
                gapIds=dict(gap_ids), missingFromDoc=missing, tsl=tsl)


# ----------------------------------------------------------------- footnote anchors
def footnote_anchor_rows(tsl, servable):
    """Per `footnote` block: its marker, and whether a SERVED block carries the referent."""
    rows = []
    # A footnote is never its own referent, and never ANOTHER footnote's: a run of «(1)…(6)» blocks
    # that all carry the role would otherwise anchor each other and report a resolved reference that
    # does not exist. Round 5's rule — re-derive a number a second way before recording it — caught
    # exactly this: without the exclusion the count is 22, with it 10, and 10 is the true one.
    served_blocks = [b for b in (tsl.get('blocks') or ())
                     if servable.get(b['id']) and role_of(b) != 'footnote']
    for b in tsl.get('blocks') or ():
        if role_of(b) != 'footnote':
            continue
        text = b.get('text') or ''
        m = FOOTNOTE_MARKER.match(text)
        raw = m.group(1) if m else None
        if m is None:
            cls = 'mark_mangled' if FOOTNOTE_MARK_LIKE.match(text) else 'no_mark_at_all'
        elif raw.startswith('*'):
            cls = 'marker_star'
        else:
            cls = 'marker_numeric'
        anchor = scope = None
        if cls == 'marker_numeric':
            sup = SUPERSCRIPT.get(raw, '')
            alt = r'\(\s*' + re.escape(raw) + r'\s*\)'
            pat = re.compile(alt + ('|' + re.escape(sup) if sup else ''))
            for other in served_blocks:
                if other['id'] == b['id'] or other['page'] != b['page']:
                    continue
                if pat.search(other.get('text') or ''):
                    anchor, scope = other['id'], 'same_page'
                    break
            if anchor is None:
                for other in served_blocks:
                    if other['id'] == b['id']:
                        continue
                    if pat.search(other.get('text') or ''):
                        anchor, scope = other['id'], 'other_page_same_lesson'
                        break
        rows.append(dict(id=b['id'], page=b['page'], marker=raw, markerClass=cls,
                         anchor=anchor, anchorScope=scope, textLen=len(text),
                         context=footnote_context(tsl, b)))
    return rows


#: A `footnote` block that sits under an `instruction` lead («Tiến hành:», «Dụng cụ:») with nothing but
#: same-role siblings in between is a PROCEDURE STEP the role lexicon read as a note; one that sits
#: immediately after a `caption` or a figure-bearing block is a FIGURE CALLOUT. Both are role errors,
#: and a role error is the one thing a new block type cannot fix — it renders the mistake more
#: confidently. Deliberately conservative: it reports only what the same page's own roles support.
def footnote_context(tsl, fn):
    page = [b for b in (tsl.get('blocks') or ()) if b['page'] == fn['page']]
    page.sort(key=lambda b: b.get('order') or 0)
    idx = next((i for i, b in enumerate(page) if b['id'] == fn['id']), None)
    if idx is None:
        return 'unknown'
    for j in range(idx - 1, -1, -1):
        r = role_of(page[j])
        if r == 'footnote':
            continue
        if r == 'instruction':
            return 'under_instruction_lead'
        if r == 'caption':
            return 'after_caption'
        return f'after_{r}'
    return 'page_start'


# ----------------------------------------------------------------- counterfactuals
def counterfactual(rows, add_roles, group_rule=False):
    """Mutilated-structure count if `add_roles` were mapped to app types (and, optionally, if the
    all-or-nothing group rule were enforced). ARITHMETIC ON A DISPOSITION TABLE — no document is
    produced, nothing is written, no code path a child can reach is taken."""
    total_mut = collections.Counter()
    total_served = 0
    changed = 0
    for r in rows:
        if not r['ok']:
            continue
        servable = dict(r['servable'])
        for role, ids in r['gapIds'].items():
            if role in add_roles:
                for i in ids:
                    servable[i] = True
                    changed += 1
        if group_rule:
            for g in r['groups']:
                present = [m for m in g['members'] if m in servable]
                if len(present) < 2 and g['kind'] != 'figure_caption':
                    continue
                if not all(servable[m] for m in present):
                    for m in present:
                        servable[m] = False
        for g in mutilated(r['groups'], servable):
            total_mut[g['kind']] += 1
        total_served += sum(1 for v in servable.values() if v)
    return dict(mutilated=dict(total_mut), mutilatedTotal=sum(total_mut.values()),
                served=total_served, unwithheld=changed)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--lessons', default=DEFAULT_LESSONS)
    ap.add_argument('--json', dest='json_out')
    ap.add_argument('--md', dest='md_out')
    ap.add_argument('--detail', action='store_true', help='print every gap block and every mutilated group')
    a = ap.parse_args(argv)

    paths = tsl_paths(a.lessons)
    if not paths:
        print(f'no TSL under {a.lessons}', file=sys.stderr)
        return 2
    rows = [census_one(p) for p in paths]
    ok = [r for r in rows if r['ok']]

    gap = collections.Counter()
    for r in ok:
        for role, ids in r['gapIds'].items():
            gap[role] += len(ids)

    base = counterfactual(ok, set())
    variants = {
        'TODAY': base,
        '+option': counterfactual(ok, {'option'}),
        '+activity': counterfactual(ok, {'activity'}),
        '+footnote': counterfactual(ok, {'footnote'}),
        '+all three': counterfactual(ok, {'option', 'activity', 'footnote'}),
        'TODAY + group rule': counterfactual(ok, set(), group_rule=True),
        '+all three + group rule': counterfactual(ok, {'option', 'activity', 'footnote'}, group_rule=True),
    }

    anchors = []
    for r in ok:
        anchors.extend(footnote_anchor_rows(r['tsl'], r['servable']))
    anchor_class = collections.Counter(x['markerClass'] for x in anchors)
    numeric = [x for x in anchors if x['markerClass'] == 'marker_numeric']
    anchored = [x for x in numeric if x['anchor']]

    imprint = []
    for r in ok:
        for b in r['tsl'].get('blocks') or ():
            if IMPRINT_LEAD.match(b.get('text') or ''):
                imprint.append(dict(id=b['id'], role=role_of(b), servedToday=r['servable'].get(b['id']),
                                    text=(b.get('text') or '')[:60]))
    imprint_by_role = collections.Counter(x['role'] for x in imprint)
    imprint_served = collections.Counter(x['role'] for x in imprint if x['servedToday'])

    # every group that contains at least one gap block, by kind and by which role is missing
    gap_in_group = collections.Counter()
    gap_group_rows = []
    for r in ok:
        gapset = {i: role for role, ids in r['gapIds'].items() for i in ids}
        for g in r['groups']:
            hits = [m for m in g['members'] if m in gapset]
            if hits:
                gap_in_group[(g['kind'], gapset[hits[0]])] += 1
                gap_group_rows.append(dict(lesson=r['rel'], group=g['group_id'], kind=g['kind'],
                                           members=g['members'],
                                           gapMembers=hits,
                                           servedMembers=[m for m in g['members'] if r['servable'].get(m)]))

    mut_rows = []
    for r in ok:
        for g in mutilated(r['groups'], r['servable']):
            mut_rows.append(dict(lesson=r['rel'], **g))

    out = dict(
        lessons=dict(attempted=len(rows), bridged=len(ok), refused=len(rows) - len(ok)),
        gapBlocksByRole=dict(gap), gapBlocksTotal=sum(gap.values()),
        groupsTotal=sum(len(r['groups']) for r in ok),
        groupsByKind=dict(collections.Counter(g['kind'] for r in ok for g in r['groups'])),
        mutilatedToday=dict(collections.Counter(x['kind'] for x in mut_rows)),
        mutilatedTodayTotal=len(mut_rows),
        variants=variants,
        footnoteMarkers=dict(anchor_class),
        footnoteContext=dict(collections.Counter(x['context'] for x in anchors)),
        footnoteContextUnderInstructionOrCaption=sum(
            1 for x in anchors if x['context'] in ('under_instruction_lead', 'after_caption')),
        footnoteNumeric=len(numeric), footnoteAnchored=len(anchored),
        footnoteAnchorScope=dict(collections.Counter(x['anchorScope'] for x in anchored)),
        imprintByRole=dict(imprint_by_role), imprintServedToday=dict(imprint_served),
        gapBlocksInsideGroups=dict(collections.Counter(
            f'{k}/{role}' for (k, role), n in gap_in_group.items() for _ in range(n))),
        missingFromDoc=sum(len(r['missingFromDoc']) for r in ok),
    )

    print(json.dumps(out, ensure_ascii=False, indent=1))
    if a.detail:
        print('\n=== mutilated structures TODAY ===')
        for x in mut_rows:
            print(' ', json.dumps(x, ensure_ascii=False))
        print('\n=== groups containing a gap block ===')
        for x in gap_group_rows:
            print(' ', json.dumps(x, ensure_ascii=False))
        print('\n=== imprint / back-matter blocks ===')
        for x in imprint:
            print(' ', json.dumps(x, ensure_ascii=False))
        print('\n=== footnotes with no resolvable anchor ===')
        for x in anchors:
            if x['markerClass'] != 'marker_numeric' or not x['anchor']:
                print(' ', json.dumps(x, ensure_ascii=False))
    if a.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.json_out)), exist_ok=True)
        with open(a.json_out, 'w', encoding='utf-8') as fh:
            json.dump(dict(summary=out, mutilatedToday=mut_rows, gapGroups=gap_group_rows,
                           footnotes=anchors, imprint=imprint), fh, ensure_ascii=False, indent=1)
        print(f'\nwrote {a.json_out}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
