#!/usr/bin/env python3
"""Round 5 · Lane A4 — idempotent registration that survives `registry.reset()`.

## The bug this exists to remove

A4's plugins used to register by **module-import side effect**: decorators at module level, and
`load_plugins()` calling `importlib.import_module(...)`. That is a reasonable shape and it is silently
wrong, because a module is imported **once**. Lane A2's tests legitimately call `repair.registry.reset()`
— that is what `reset()` is for — and after a reset the modules are still in `sys.modules`, so
re-importing them does nothing and their registrations are never replayed. `load_plugins()` then returned
a **partial registry and reported success**: one signal of three, with `H.external` gone too.

Reproduced by the coordinator as `python3 -m unittest test_mathfix_plugin test_verify_signals`, where the
only reason `G.llm_semantic` survived is that `verify.llm` happened to be first imported *after* the reset.

## Why this matters more than the test

A router configured for six signals could run with one and **still report success**. That is the same
failure family as this round's other two worst findings — Lane D's R13, where a block disappears with no
reason code, and a grounding step that strengthened itself through a file write. A component that quietly
delivers less than it was asked for, with no error, is exactly what a Trusted Corpus cannot be built on,
and it is what this lane's own discipline is against.

## The two changes

1. **`register()` is an explicit, idempotent function**, not an import side effect. Every helper here
   checks the registry's *current* state before adding, so calling it twice is a no-op and calling it
   after a reset restores everything.
2. **`load_plugins()` verifies and fails loudly.** It compares what each module says it registered against
   `registry.describe()` afterwards and raises `RegistrationIncomplete` if anything is missing — a silent
   degradation becomes an error, which is the only version of this that can be relied on.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

from repair import registry  # noqa: E402


class RegistrationIncomplete(RuntimeError):
    """Raised when the registry does not contain everything a plugin module said it registered."""


def apply(signals=None, token_providers=None, block_providers=None, repairers=None, validators=None):
    """Register what is missing and return a manifest of everything this module owns.

    Idempotent by construction: each helper reads the registry's live state first, so a second call adds
    nothing and a call after `registry.reset()` restores everything. The registry's own decorators are
    used to do the adding, so plugins keep the attributes (`signal_id`, `repairer_id`, …) the engine and
    the contribution accounting read.
    """
    manifest = dict(signals=[], token_providers=[], block_providers=[], repairers=[], validators=[])

    have_signals = set(registry.signals())
    for sid, fn in (signals or {}).items():
        if sid not in have_signals:
            registry.signal(sid)(fn)
        manifest['signals'].append(sid)

    have = registry.providers()
    for pid, fn in (token_providers or {}).items():
        if pid not in have['token']:
            registry.token_signal_provider(pid)(fn)
        manifest['token_providers'].append(pid)
    for pid, fn in (block_providers or {}).items():
        if pid not in have['block']:
            registry.block_signal_provider(pid)(fn)
        manifest['block_providers'].append(pid)

    described = registry.describe()['failure_classes']
    for (fc, rid), fn in (repairers or {}).items():
        if rid not in (described.get(fc) or {}).get('repairers', ()):
            registry.repairer(fc, rid)(fn)
        manifest['repairers'].append([fc, rid])
    described = registry.describe()['failure_classes']
    for (fc, vid), fn in (validators or {}).items():
        if vid not in (described.get(fc) or {}).get('validators', ()):
            registry.validator(fc, vid)(fn)
        manifest['validators'].append([fc, vid])

    return manifest


def verify(manifests):
    """Check the registry really contains everything the manifests claim. → the registry description.

    This is the half that turns the bug into an error. `load_plugins()` used to return
    `registry.describe()` without ever asking whether the description contained what was requested.
    """
    d = registry.describe()
    have_signals = set(d['signals'])
    have = d['providers']
    missing = []
    for name, m in manifests.items():
        for sid in m['signals']:
            if sid not in have_signals:
                missing.append(f'{name}: signal {sid}')
        for pid in m['token_providers']:
            if pid not in have['token']:
                missing.append(f'{name}: token provider {pid}')
        for pid in m['block_providers']:
            if pid not in have['block']:
                missing.append(f'{name}: block provider {pid}')
        for fc, rid in m['repairers']:
            if rid not in (d['failure_classes'].get(fc) or {}).get('repairers', ()):
                missing.append(f'{name}: repairer {fc}/{rid}')
        for fc, vid in m['validators']:
            if vid not in (d['failure_classes'].get(fc) or {}).get('validators', ()):
                missing.append(f'{name}: validator {fc}/{vid}')
    if missing:
        raise RegistrationIncomplete(
            'the repair registry is missing plugins A4 registered — a partial signal set must never be '
            'reported as success:\n  ' + '\n  '.join(missing) +
            f'\nregistry now holds: signals={sorted(have_signals)} providers={have}')
    return d
