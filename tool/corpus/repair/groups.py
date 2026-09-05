#!/usr/bin/env python3
"""Round 5 · **structural groups** - a disposition that attaches to a group, not only to a block.

Founder defect 8 (97-row audit): *an incomplete multiple-choice question was served because a sibling block
was withheld.* Withholding one option does not make the served question smaller, it makes it **wrong**. So
«withhold» is not a universally safe default, and the safety mechanism itself can create a
teaching-critical error.

The rule this module implements:

> For a block with structural siblings - OPTION ⊂ QUESTION, a caption bound to its figure, a row of a table,
> a step of an enumerated procedure - **the group is the unit of disposition**. Either the whole group is
> servable or none of it is. A group with some members served and some withheld is a *mutilated structure*
> and is a defect in its own right, whichever way it is resolved.

Groups are derived **deterministically** from the SDM's own roles and reading order; nothing here guesses
semantics, and a block that belongs to no group keeps its own disposition exactly as before.
"""
from __future__ import annotations

import re

from . import model

ENUM_STEP = re.compile(r'^\s*(?:[·•▪-]|\(?\d{1,2}[.)]|Bước\s*\d)')
GROUP_KINDS = ('question_options', 'figure_caption', 'table_rows', 'procedure_steps')


def structural_groups(sdm):
    """[{group_id, kind, members: [block_id]}] for one SDM page.

    * `question_options` - a QUESTION (or an enumerated stem) followed, in reading order, by consecutive
      OPTION blocks. The options *are* the question.
    * `figure_caption` - a figure's caption block, bound by `figures[].caption` (the geometric association
      round 4 built); the caption alone is not a teaching object.
    * `table_rows` - consecutive TABLE blocks: half a table is a false table.
    * `procedure_steps` - consecutive enumerated steps under an INSTRUCTION lead («Tiến hành:» then
      «· Lấy một cốc nước…»); a procedure missing a step teaches the wrong procedure.
    """
    blocks = [b for b in sorted(sdm['blocks'], key=lambda b: b['order'])
              if (b.get('text') or '').strip()]
    out = []
    page_key = f"{sdm['book']}:p{sdm['page']:03d}"

    # question ▸ options
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if b['role']['value'] in ('question', 'body') and i + 1 < len(blocks) \
                and blocks[i + 1]['role']['value'] == 'option':
            j = i + 1
            while j < len(blocks) and blocks[j]['role']['value'] == 'option':
                j += 1
            out.append(dict(group_id=f'{page_key}:g-qo-{b["order"]:03d}', kind='question_options',
                            members=[x['id'] for x in blocks[i:j]]))
            i = j
            continue
        i += 1

    # figure ▸ caption
    for fig in sdm.get('figures') or ():
        cap = fig.get('caption')
        if cap:
            out.append(dict(group_id=f'{fig["id"]}:g-fc', kind='figure_caption', members=[cap],
                            figure=fig['id']))

    # consecutive table blocks
    run = []
    for b in blocks + [None]:
        if b is not None and b['role']['value'] == 'table':
            run.append(b)
            continue
        if len(run) > 1:
            out.append(dict(group_id=f'{page_key}:g-tb-{run[0]["order"]:03d}', kind='table_rows',
                            members=[x['id'] for x in run]))
        run = []

    # instruction lead ▸ enumerated steps
    i = 0
    while i < len(blocks):
        if blocks[i]['role']['value'] == 'instruction':
            j = i + 1
            while j < len(blocks) and ENUM_STEP.match(blocks[j].get('text') or '') \
                    and blocks[j]['role']['value'] in ('body', 'instruction', 'activity'):
                j += 1
            if j - i > 1:
                out.append(dict(group_id=f'{page_key}:g-ps-{blocks[i]["order"]:03d}', kind='procedure_steps',
                                members=[x['id'] for x in blocks[i:j]]))
                i = j
                continue
        i += 1
    return out


def mutilated(groups, servable_by_id):
    """Groups that would be served with some members missing - the defect itself, counted before any fix."""
    out = []
    for g in groups:
        states = [servable_by_id.get(m) for m in g['members'] if m in servable_by_id]
        if not states:
            continue
        if any(states) and not all(states):
            out.append(dict(group_id=g['group_id'], kind=g['kind'], members=len(states),
                            served=sum(1 for s in states if s), withheld=sum(1 for s in states if not s)))
    return out


def apply_group_rule(groups, servable_by_id, reasons_by_id=None, ledger=None, observations_by_id=None):
    """Enforce «serve the whole group or none of it». Returns the ids whose disposition changed and, when a
    ledger is given, records one immutable row per group that was resolved.

    The direction is fail-closed: a group with a withheld member is withheld entirely. Restoring the whole
    group instead would require evidence for the withheld member, which is exactly what the repair
    framework produces - so a group becomes servable again only when every member's own repair validated.
    """
    changed = {}
    for g in groups:
        present = [m for m in g['members'] if m in servable_by_id]
        if len(present) < 2 and g['kind'] != 'figure_caption':
            continue
        states = [servable_by_id[m] for m in present]
        if all(states) or not any(states):
            continue
        for m in present:
            if servable_by_id[m]:
                servable_by_id[m] = False
                changed[m] = g['group_id']
                if reasons_by_id is not None:
                    reasons_by_id.setdefault(m, []).append(f'group_incomplete:{g["kind"]}')
        if ledger is not None:
            obs = (observations_by_id or {}).get(present[0]) or ()
            if obs:
                ledger.append(model.LedgerEntry(
                    block_id=g['group_id'], failure_class='structural_group',
                    disposition=model.Disposition.WITHHELD, observations=obs, stage='dispose',
                    reasons=tuple(['mutilated_structure', g['kind']] + present),
                    final_value=None))
    return changed
