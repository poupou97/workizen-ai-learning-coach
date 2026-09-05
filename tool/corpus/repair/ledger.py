#!/usr/bin/env python3
"""Round 5 · the repair ledger - append-only, one JSON object per line.

Founder order §4/§14: every automatic repair must store the original observations, the repaired value, the
repair rule, the supporting signals, the provenance, the confidence and the validation result; the source
observation is never overwritten and every value is traceable end to end.

The ledger is that store. It is **append-only in code**: `append` refuses an `entry_id` it has already
written, and a value is changed only by writing a NEW entry that names the one it supersedes
(`supersede`). There is no update and no delete. A reader in another lane (D consumes this) needs nothing
but `json.loads` per line.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from . import model


class LedgerConflict(RuntimeError):
    pass


class Ledger:
    """Append-only ledger. `path=None` keeps it in memory (tests, dry runs)."""

    def __init__(self, path=None, run=None):
        self.path = path
        self.run = dict(run or {})
        self.entries = []
        self._ids = set()
        self._fh = None
        if path:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            self._fh = open(path, 'a', encoding='utf-8')

    # ------------------------------------------------------------------ write
    def append(self, entry):
        if not isinstance(entry, model.LedgerEntry):
            raise TypeError('ledger takes LedgerEntry rows only')
        if entry.entry_id in self._ids:
            raise LedgerConflict(f'entry {entry.entry_id} already written - the ledger is append-only; '
                                 f'use supersede() to record a later disposition')
        if not entry.ts:
            entry = model.replace(entry, ts=datetime.now(timezone.utc).isoformat(timespec='seconds'))
        self._ids.add(entry.entry_id)
        self.entries.append(entry)
        if self._fh:
            row = entry.to_json()
            row['run'] = self.run
            self._fh.write(json.dumps(row, ensure_ascii=False) + '\n')
            self._fh.flush()
        return entry

    def supersede(self, prior, **changes):
        """Record a NEW disposition for the block of `prior`, chained to it. `prior` itself stays in the
        ledger untouched - that is the whole point."""
        if prior.entry_id not in self._ids:
            raise LedgerConflict('cannot supersede an entry this ledger never wrote')
        fields = dict(block_id=prior.block_id, failure_class=prior.failure_class,
                      observations=prior.observations, candidate=prior.candidate,
                      validation=prior.validation, final_value=prior.final_value,
                      reasons=prior.reasons, disposition=prior.disposition, stage=prior.stage)
        fields.update(changes)
        fields['prior_entry_id'] = prior.entry_id
        return self.append(model.LedgerEntry(**fields))

    def close(self):
        if self._fh:
            self._fh.close()
            self._fh = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # ------------------------------------------------------------------ read
    def by_block(self, block_id):
        return [e for e in self.entries if e.block_id == block_id]

    def latest(self, block_id):
        """The last entry written for a block - superseded rows are still in `entries`."""
        rows = self.by_block(block_id)
        return rows[-1] if rows else None

    def counts(self):
        from collections import Counter
        return dict(Counter(e.disposition for e in self.entries))

    def false_correction_report(self, truth):
        """**P0 metric, computed from the ledger itself** (Founder ACCURACY RECOVERY addendum).

        `truth(block_id) -> the correct value, or None when unknown`. For every row that reached
        `VALIDATED_REPAIR`, compare what was observed and what was served:

        * `false_correction` — the observation was **already correct** and the repair made it wrong. This is
          the failure mode the Founder named: *«không được biến OCR sai thành AI tự tin sửa sai theo cách
          khác»*. It is counted on its own and never folded into precision.
        * `repaired` — wrong before, right after. `still_wrong` — wrong before, differently wrong after.

        Each row is attributed to **every signal that supported it**, so a false correction can always be
        traced to the signals that proposed it.
        """
        from collections import Counter, defaultdict
        totals = Counter()
        by_signal = defaultdict(Counter)
        rows = []
        for e in self.entries:
            if e.disposition != model.Disposition.VALIDATED_REPAIR or not e.candidate:
                continue
            want = truth(e.block_id)
            if want is None:
                totals['unknown_truth'] += 1
                continue
            was = e.candidate.original_observations[0].value
            now = e.final_value
            if now == was:
                verdict = 'unchanged'
            elif now == want:
                verdict = 'repaired'
            elif was == want:
                verdict = 'false_correction'
            else:
                verdict = 'still_wrong'
            totals[verdict] += 1
            rows.append(dict(block_id=e.block_id, entry_id=e.entry_id, rule_id=e.candidate.rule_id,
                             verdict=verdict,
                             signals=[s.signal_id for s in e.candidate.supporting()]))
            for sig in e.candidate.supporting():
                by_signal[sig.signal_id][verdict] += 1
        changed = totals['repaired'] + totals['false_correction'] + totals['still_wrong']
        return dict(totals=dict(totals), changed=changed,
                    false_correction_rate=(round(totals['false_correction'] / changed, 4) if changed else None),
                    correction_precision=(round(totals['repaired'] / changed, 4) if changed else None),
                    by_signal={k: dict(v) for k, v in sorted(by_signal.items())},
                    rows=rows)

    def to_json(self):
        return [e.to_json() for e in self.entries]


def read(path):
    """Read a ledger file back as raw dicts (the shape another lane consumes)."""
    out = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out
