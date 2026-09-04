#!/usr/bin/env python3
"""WAL-206 — mandatory cascade funnel for the WAL-204 re-run (unique lessons).

BEFORE proven → recovered by layout extraction → correctly attached (TOC
range) → recognized activity pattern → routed → content-valid → device-valid
→ AFTER proven. Founder needs to know WHERE lessons are lost.

Reads: poc-out/layout/, poc-out/units-layout/, assets/pack/lesson-index-g*.json,
poc-out/p0-experiment/{baseline-learnable.json, content-valid-lessons.json,
device-valid-lessons.json (optional, hand-written after the device walk)}.
"""
import glob
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ui'))
sys.path.insert(0, os.path.dirname(__file__))
from pattern_router import printed_to_pdf_offset, toc_ranges, clean  # noqa: E402
from fable_activity_taxonomy import classify  # noqa: E402

BOOKS = ['04-sgk-khoa-hoc-4', '05-sgk-khoa-hoc-5', '06-sgk-khoa-hoc-tu-nhien-6', '07-sgk-khoa-hoc-tu-nhien-7', '08-sgk-khoa-hoc-tu-nhien-8', '09-sgk-khoa-hoc-tu-nhien-9']
SCOPE = {'READ_TEXT', 'SELECT_MCQ', 'WRITE_TEXT'}


def main():
    docs = {d['sourceDocumentId']: d for d in json.load(open('poc-out/graph/curriculum-structure.json'))['documents']}
    before = set(map(tuple, json.load(open('poc-out/p0-experiment/baseline-learnable.json'))))
    fam_before = {k for k in before if k[0] in BOOKS}
    toc_lessons = set(); recovered = set(); attached = set(); patterned = set(); patterned_any = set(); routed = set()
    for book in BOOKS:
        doc = docs[book]; off = printed_to_pdf_offset(book); rng = toc_ranges(doc, off)
        for no, lo, hi in rng: toc_lessons.add((book, no))
        try: units = json.load(open(f'poc-out/units-layout/{book}.json'))['units']
        except FileNotFoundError: units = []
        # recovered: lesson has ≥1 trusted PASSAGE or QUESTION unit anywhere in its range
        for no, lo, hi in rng:
            us = [u for u in units if lo <= u['pagePdf'] < hi and u['role'] in ('PASSAGE', 'QUESTION')]
            if us: recovered.add((book, no)); attached.add((book, no))
            qs = [u for u in us if u['role'] == 'QUESTION']
            labs = set()
            for q in qs:
                t = clean(q['text'])
                if t: labs |= classify(t)
            if labs: patterned_any.add((book, no))
            if labs & SCOPE: patterned.add((book, no))
    for g in range(4, 10):
        p = json.load(open(f'assets/pack/lesson-index-g{g}.json'))
        for r in p['tvReadings'] + p['tvWritings']:
            if r.get('source', '').startswith('pattern-router') and r['book'] in BOOKS:
                routed.add((r['book'], r['lesson']))
    content_valid = set(map(tuple, json.load(open('poc-out/p0-experiment/content-valid-lessons.json')))) if os.path.exists('poc-out/p0-experiment/content-valid-lessons.json') else set()
    device_valid = set(map(tuple, json.load(open('poc-out/p0-experiment/device-valid-lessons.json')))) if os.path.exists('poc-out/p0-experiment/device-valid-lessons.json') else set()
    new_routed = routed - before; new_valid = content_valid - before; new_device = device_valid - before
    print(f'Family: Khoa học/KHTN 4-9 — TOC lessons {len(toc_lessons)}')
    print(f'BEFORE proven (family / all):            {len(fam_before)} / {len(before)}')
    print(f'recovered by layout extraction:          {len(recovered)}  ({100*len(recovered)/len(toc_lessons):.0f}% of TOC lessons)')
    print(f'attached to a lesson (TOC range):        {len(attached)}')
    print(f'with a recognized pattern (any):         {len(patterned_any)}')
    print(f'with a pattern in the re-run scope:      {len(patterned)}   (READ_TEXT / SELECT_MCQ / WRITE_TEXT)')
    print(f'routed to a Surface:                     {len(routed)}   (new vs baseline: {len(new_routed)})')
    print(f'content-valid (automated gate):          {len(content_valid)}   (new: {len(new_valid)})')
    print(f'device-valid (hand-walked):              {len(device_valid)}   (new: {len(new_device)})')
    print(f'AFTER proven (all, if device-valid ship): {len(before | new_device)} / 3679  ({100*len(before | new_device)/3679:.2f}%)')
    print('\nlost at each step (family lessons):')
    print(f'  not recovered (no trusted passage/question): {len(toc_lessons - recovered)}')
    print(f'  recovered but no scope pattern:              {len(recovered - patterned)}   ← largest loss: questions are EXPLAIN/OBSERVE, not READ/MCQ/WRITE')
    print(f'  scope pattern but not routed:                {len(patterned - routed)}')
    print(f'  routed but content-invalid:                  {len(routed - content_valid)}')
    json.dump(dict(toc=len(toc_lessons), recovered=len(recovered), attached=len(attached), patternedAny=len(patterned_any), patternedScope=len(patterned), routed=len(routed), newRouted=len(new_routed), contentValid=len(content_valid), newContentValid=len(new_valid), deviceValid=len(device_valid), newDeviceValid=len(new_device)), open('poc-out/p0-experiment/funnel.json', 'w'))


if __name__ == '__main__':
    main()
