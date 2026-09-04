#!/usr/bin/env python3
"""WAL-206 — layout blocks → learning units (the bridge the pattern router consumes).

Reads poc-out/layout/<book>/pNNN.json (from layout_extract.py) and writes
poc-out/units-layout/<book>.json in the same top-level shape as units-k12
({sourceDocumentId, units:[{id, role, text, pagePdf, ...}]}) so downstream
tooling can switch source without changing its lesson-attachment logic.

Roles emitted (only from TRUSTED blocks; untrusted pages/regions are dropped —
fail closed):
  PASSAGE  — consecutive body blocks in the same region, joined; ≥ 120 chars.
             Never contains sidebar/caption/footnote/heading text: those roles
             are excluded before joining, so a passage cannot splice a box.
  QUESTION — a block the layout labelled `question` (a learner-facing
             directive or a line ending in '?'), text as-is.
  HEADING  — kept for lesson/section attachment; not an activity.
Everything else (sidebar, caption, footnote, pageNumber, untrusted) is kept
only as provenance counts in `dropped`, not as units.
"""
import glob
import json
import os
import re
import sys
from collections import Counter

MIN_PASSAGE = 120


def build_book(book):
    files = sorted(glob.glob(f'poc-out/layout/{book}/p*.json'), key=lambda f: int(re.search(r'p(\d+)', f).group(1)))
    units, dropped = [], Counter()
    for fp in files:
        page = json.load(open(fp))
        pdf = page['pagePdf']
        if page['layout'].get('tableLike'):
            dropped['tableLike_page'] += 1
            continue
        cur = None  # running passage
        def flush():
            nonlocal cur
            if cur and len(cur['text']) >= MIN_PASSAGE:
                units.append(cur)
            elif cur:
                dropped['passage_too_short'] += 1
            cur = None
        for b in page['blocks']:
            if not b.get('trusted', True):
                dropped['untrusted_block'] += 1
                flush(); continue
            r = b['role']
            if r == 'body':
                if cur and cur['regionPath'] == b['regionPath']:
                    cur['text'] += ' ' + b['text']; cur['blockIds'].append(b['id'])
                else:
                    flush()
                    cur = dict(id=f"{b['id']}:passage", role='PASSAGE', text=b['text'], pagePdf=pdf, regionPath=b['regionPath'], blockIds=[b['id']], ocrConf=b['ocrConf'])
            elif r == 'question':
                flush()
                units.append(dict(id=b['id'], role='QUESTION', text=b['text'], pagePdf=pdf, regionPath=b['regionPath'], blockIds=[b['id']], ocrConf=b['ocrConf']))
            elif r == 'heading':
                flush()
                units.append(dict(id=b['id'], role='HEADING', text=b['text'], pagePdf=pdf, regionPath=b['regionPath'], blockIds=[b['id']], ocrConf=b['ocrConf']))
            else:
                dropped[r] += 1
                flush()
        flush()
    out = dict(sourceDocumentId=book, extractor='layout-xycut-v1', units=units, dropped=dict(dropped))
    os.makedirs('poc-out/units-layout', exist_ok=True)
    json.dump(out, open(f'poc-out/units-layout/{book}.json', 'w'), ensure_ascii=False)
    return Counter(u['role'] for u in units), dict(dropped)


if __name__ == '__main__':
    for book in sys.argv[1:]:
        print(book, *build_book(book))
