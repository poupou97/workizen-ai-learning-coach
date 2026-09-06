#!/usr/bin/env python3
"""Round 5 · Lane A4 — where this lane reads and writes.

Binding from the lane brief: **corpus data only under the main checkout's gitignored `poc-out/`**, and
this lane writes **only** under `poc-out/round5/verify/`. Nothing here ever writes into the corpus, into
another lane's output directory, or into a git-tracked path.
"""
import os

import tc2_paths                      # noqa: E402  (tool/corpus is already on sys.path)

ROOT = tc2_paths.ROOT
OCR_BODY = os.environ.get('A4_OCR_BODY', f'{ROOT}/poc-out/graph/ocr-body')
OUT = os.environ.get('A4_OUT', f'{ROOT}/poc-out/round5/verify')

INDEX = f'{OUT}/xcorpus-index.json'
LLM_CACHE = f'{OUT}/llm-cache'
EXTERNAL_STORE = f'{OUT}/external-evidence.jsonl'
LEDGER = f'{OUT}/verify-ledger.jsonl'


def out(*parts):
    p = os.path.join(OUT, *parts)
    os.makedirs(os.path.dirname(p) if os.path.splitext(p)[1] else p, exist_ok=True)
    return p
