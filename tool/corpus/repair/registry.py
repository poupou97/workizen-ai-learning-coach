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
_TOKEN_PROVIDERS = []               # extra per-token signal providers (Lane A4 registers here)
_BLOCK_PROVIDERS = []               # extra per-block signal providers


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


def token_signal_provider(provider_id):
    """**Extension point for another lane (A4).** Register a callable
    `fn(observed, proposed, ctx) -> Signal | [Signal] | None` that is consulted for every token a repairer
    is about to change. Use it to add cross-corpus consistency, an LLM anomaly reading (candidate only,
    never truth) or an external authority - without forking the repairer.

    A provider that returns an `objects` Signal **vetoes** the repair, exactly like a built-in one. There is
    no precedence order between providers and no trust ladder: a signal counts by its layer, its
    independence and its evidence, never by who produced it."""
    def deco(fn):
        fn.provider_id = provider_id
        _TOKEN_PROVIDERS.append((provider_id, fn))
        return fn
    return deco


def block_signal_provider(provider_id):
    """As above, but consulted once per candidate block with `fn(observed_text, proposed_text, ctx)`."""
    def deco(fn):
        fn.provider_id = provider_id
        _BLOCK_PROVIDERS.append((provider_id, fn))
        return fn
    return deco


def _run_providers(providers, *args):
    out = []
    for pid, fn in providers:
        try:
            r = fn(*args)
        except Exception as e:                      # a provider must never take the pipeline down
            out.append(('error', pid, str(e)))
            continue
        if r is None:
            continue
        out.extend(r if isinstance(r, (list, tuple)) else [r])
    return [s for s in out if not isinstance(s, tuple)]


def token_signals(observed, proposed, ctx):
    return _run_providers(_TOKEN_PROVIDERS, observed, proposed, ctx)


def block_signals(observed_text, proposed_text, ctx):
    return _run_providers(_BLOCK_PROVIDERS, observed_text, proposed_text, ctx)


def providers():
    return dict(token=[p for p, _ in _TOKEN_PROVIDERS], block=[p for p, _ in _BLOCK_PROVIDERS])


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
        providers=providers(),
    )


def reset():
    """Tests only: clear the registry so a test can register throwaway plugins."""
    _REPAIRERS.clear()
    _VALIDATORS.clear()
    _SIGNALS.clear()
    _TOKEN_PROVIDERS.clear()
    _BLOCK_PROVIDERS.clear()


def snapshot():
    """Tests only: (repairers, validators, signals) deep copy for save/restore around a test."""
    return ({k: list(v) for k, v in _REPAIRERS.items()},
            {k: list(v) for k, v in _VALIDATORS.items()},
            dict(_SIGNALS), list(_TOKEN_PROVIDERS), list(_BLOCK_PROVIDERS))


def restore(snap):
    r, v, s, tp, bp = snap
    _REPAIRERS.clear(); _REPAIRERS.update({k: list(x) for k, x in r.items()})
    _VALIDATORS.clear(); _VALIDATORS.update({k: list(x) for k, x in v.items()})
    _SIGNALS.clear(); _SIGNALS.update(s)
    _TOKEN_PROVIDERS[:] = tp
    _BLOCK_PROVIDERS[:] = bp
