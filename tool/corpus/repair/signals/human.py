#!/usr/bin/env python3
"""Third signal **layer E** - independent human review.

Layer E is an **output**, never an automatic verdict: the framework cannot manufacture a human, so what it
produces is a *queue* - the blocks where a failure was detected and the machine could not close it, ordered
so that a person's time buys the most accuracy.

Priority, highest first:
1. `agreed_error` on a **trusted** block - the machine believes a served block is wrong. Every one of these
   is a live false-trust claim.
2. `unresolved_disagreement` on a teaching-critical role (question, instruction, rule, answer, objective).
3. `unresolved_disagreement` elsewhere - a withheld block that a human could restore.
4. `low_margin` - a repair that validated on a thin margin and is worth a spot check.

A queue row carries the block id, the page, the role, the observed readings, the candidate the machine
proposed (if any) and the signals for and against, so a reviewer never has to re-derive the machine's case.
It carries **no page image and no verbatim run of SGK text beyond the block itself** - it stays in
`poc-out/`, like every other corpus artefact.
"""
from __future__ import annotations

import json
import os

PRIORITY = {'agreed_error_trusted': 1, 'unresolved_teaching': 2, 'unresolved': 3, 'low_margin': 4}
TEACHING_ROLES = frozenset({'question', 'instruction', 'rule', 'answer', 'model_answer', 'objective',
                            'option', 'activity'})


class ReviewQueue:
    def __init__(self):
        self.rows = []

    def add(self, block_id, kind, page, role, detail, disposition=None):
        self.rows.append(dict(block_id=block_id, kind=kind, priority=PRIORITY.get(kind, 9),
                              book=page.get('book'), page=page.get('page'), role=role,
                              disposition=disposition, detail=detail))

    def classify(self, trusted, role, resolved):
        if not resolved and trusted:
            return 'agreed_error_trusted'
        if not resolved and role in TEACHING_ROLES:
            return 'unresolved_teaching'
        if not resolved:
            return 'unresolved'
        return 'low_margin'

    def sorted_rows(self):
        return sorted(self.rows, key=lambda r: (r['priority'], r['book'] or '', r['page'] or 0, r['block_id']))

    def write(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as fh:
            for r in self.sorted_rows():
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
        return len(self.rows)

    def counts(self):
        from collections import Counter
        return dict(Counter(r['kind'] for r in self.rows))
