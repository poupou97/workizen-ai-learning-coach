#!/usr/bin/env python3
"""`tool/corpus/verify` — round 5 · Lane A4 · **MULTI-SIGNAL VERIFICATION**.

    SOURCE → observations → deterministic validation → domain validation → CROSS-CORPUS consistency
           → LLM semantic review → external authoritative check → human correction
           → validated correction → versioned trusted corpus

This package is the *verification* half of that chain. It does **not** own a second repair framework:
Lane A1's `tool/corpus/repair/` owns `Observation`, `Signal`, `RepairCandidate`, `ValidationResult`,
`LedgerEntry` and the plugin registry, and this package **registers into it** (`load_plugins()`).

What A4 adds, and only this:

| module | adds |
|---|---|
| `index` | the cross-corpus index over 62,729 OCR pages / 531 books (read-only) |
| `crosscorpus` | signal `D.cross_corpus` + a repairer + a validator, registered into A1's registry |
| `llm` | signal `G.llm_semantic` — an LLM that may only ever emit an `AnomalySignal` or a `RepairCandidate` |
| `external` | signal `H.external` — bounded authoritative lookup, evidence-only, never auto-applied |
| `trust` | `TrustDecision` — a *projection* over A1's ledger, plus the 3 dispositions A1's set lacks |
| `router` | which verification path a block gets, by content type · risk · disagreement · confidence |
| `human` | the correction-report workflow: schema, validation step, corpus versioning (no production UI) |

**Nothing in this package can write to the trusted corpus, and no signal here is ever truth.** An LLM
answer and a search result are both *observations by another source*, subject to exactly the same
validation as an OCR stack's.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

from . import paths, trust  # noqa: E402,F401

VERIFY_VERSION = 'verify-v1'


def load_plugins(which=('crosscorpus', 'llm', 'external')):
    """Register A4's signals/repairers/validators into Lane A1's registry.

    Importing this package alone registers nothing — a consumer that only wants `TrustDecision` (Lane D
    reading a ledger, Lane B explaining trust to a child) pays no import cost and gets no plugins.
    """
    import importlib
    from repair import registry
    for name in which:
        importlib.import_module(f'{__name__}.{name}')
    return registry.describe()
