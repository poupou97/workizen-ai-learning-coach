#!/usr/bin/env python3
"""Round 5 · the repair plugin registry.

A **repairer** declares the failure class it handles and returns `RepairCandidate`s.
A **validator** declares the failure class it can rule on and returns a `ValidationResult`.
A **signal** is a third-signal reading a repairer may attach to a candidate; signals are registered too so
that per-signal contribution can be measured without every repairer keeping its own bookkeeping.

Registration is by decorator or by call, so another lane registers against this module without editing it:

    from repair import registry, model

    @registry.repairer('formula_flattened', repairer_id='mathfix.fraction-v1')
    def propose(ctx):
        yield model.RepairCandidate(...)

    @registry.validator('formula_flattened', validator_id='mathfix.deterministic-v1')
    def validate(candidate, ctx):
        return model.ValidationResult('mathfix.deterministic-v1', model.Verdict.VALIDATED, evidence=[...])

`ctx` is a `RepairContext` (see `engine.py`): the block, its observations, the page/document around it and
the signal providers. A plugin never receives a mutable pipeline object and can never write back into one.
"""
from __future__ import annotations

from collections import defaultdict

_REPAIRERS = defaultdict(list)      # failure_class -> [(order, id, fn)]
_VALIDATORS = defaultdict(list)     # failure_class -> [(order, id, fn)]
_SIGNALS = {}                       # signal_id -> fn


class DuplicatePlugin(ValueError):
    pass


def _add(table, failure_class, plugin_id, fn, order):
    if any(pid == plugin_id for _, pid, _ in table[failure_class]):
        raise DuplicatePlugin(f'{plugin_id!r} already registered for failure class {failure_class!r}')
    table[failure_class].append((order, plugin_id, fn))
    table[failure_class].sort(key=lambda t: (t[0], t[1]))
    return fn


def repairer(failure_class, repairer_id, order=100):
    """Register a repairer for `failure_class`. The function takes a context and returns an iterable of
    `RepairCandidate` (possibly empty - a repairer that has nothing to say must return nothing, never a
    low-confidence guess)."""
    def deco(fn):
        fn.repairer_id = repairer_id
        fn.failure_class = failure_class
        return _add(_REPAIRERS, failure_class, repairer_id, fn, order)
    return deco


def validator(failure_class, validator_id, order=100):
    """Register a validator for `failure_class`. Takes (candidate, context) and returns a `ValidationResult`.
    Validators run in registration order; the engine's rule is **unanimity among those that do not abstain**:
    one `rejected` rejects, and a candidate with no `validated` stays a candidate."""
    def deco(fn):
        fn.validator_id = validator_id
        fn.failure_class = failure_class
        return _add(_VALIDATORS, failure_class, validator_id, fn, order)
    return deco


def signal(signal_id):
    """Register a third-signal provider. Takes whatever the signal needs (by convention `(candidate_value,
    ctx)`) and returns a `Signal`. Registered so the engine can enumerate the layers present in a run."""
    def deco(fn):
        if signal_id in _SIGNALS:
            raise DuplicatePlugin(f'signal {signal_id!r} already registered')
        fn.signal_id = signal_id
        _SIGNALS[signal_id] = fn
        return fn
    return deco


def repairers_for(failure_class):
    return [fn for _, _, fn in _REPAIRERS.get(failure_class, ())]


def validators_for(failure_class):
    return [fn for _, _, fn in _VALIDATORS.get(failure_class, ())]


def signals():
    return dict(_SIGNALS)


def failure_classes():
    return sorted(set(_REPAIRERS) | set(_VALIDATORS))


def describe():
    """A JSON-able description of everything registered - printed by `python3 -m repair` and written into
    every measurement run so a scoreboard says which plugins produced it."""
    return dict(
        failure_classes={fc: dict(repairers=[pid for _, pid, _ in _REPAIRERS.get(fc, ())],
                                  validators=[pid for _, pid, _ in _VALIDATORS.get(fc, ())])
                         for fc in failure_classes()},
        signals=sorted(_SIGNALS),
    )


def reset():
    """Tests only: clear the registry so a test can register throwaway plugins."""
    _REPAIRERS.clear()
    _VALIDATORS.clear()
    _SIGNALS.clear()


def snapshot():
    """Tests only: (repairers, validators, signals) deep copy for save/restore around a test."""
    return ({k: list(v) for k, v in _REPAIRERS.items()},
            {k: list(v) for k, v in _VALIDATORS.items()},
            dict(_SIGNALS))


def restore(snap):
    r, v, s = snap
    _REPAIRERS.clear(); _REPAIRERS.update({k: list(x) for k, x in r.items()})
    _VALIDATORS.clear(); _VALIDATORS.update({k: list(x) for k, x in v.items()})
    _SIGNALS.clear(); _SIGNALS.update(s)
