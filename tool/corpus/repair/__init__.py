#!/usr/bin/env python3
"""`tool/corpus/repair` - the round-5 data-accuracy framework.

    WRONG -> DETECT -> WITHHOLD -> REPAIR -> VALIDATE -> RESTORE

Public surface (stable; other lanes register against it):

    from repair import model, registry, engine, ledger
    model.Observation / RepairCandidate / ValidationResult / Signal / Disposition / Verdict / SignalVerdict
    registry.repairer(failure_class, repairer_id)     -> decorator
    registry.validator(failure_class, validator_id)   -> decorator
    registry.signal(signal_id)                        -> decorator
    engine.RepairEngine(ledger).run_block(engine.RepairContext(...)) -> engine.Outcome
    ledger.Ledger(path)                               -> append-only JSONL

See `docs/research/DATA-ACCURACY-FRAMEWORK.md` for the contract in prose and a worked plugin.

Importing this package does NOT import the Vietnamese/text plugins - a consumer that only wants the types
(Lane D reading a ledger) pays nothing. Call `load_builtin_plugins()` (or import `repair.repairers.vi_text`)
to register this lane's own repairers.
"""
from . import model, registry, ledger, engine  # noqa: F401
from .model import (Disposition, Observation, RepairCandidate, Signal,  # noqa: F401
                    SignalVerdict, ValidationResult, Verdict, FRAMEWORK_VERSION)

__all__ = ['model', 'registry', 'ledger', 'engine', 'Disposition', 'Observation', 'RepairCandidate',
           'Signal', 'SignalVerdict', 'ValidationResult', 'Verdict', 'FRAMEWORK_VERSION',
           'load_builtin_plugins']


def load_builtin_plugins():
    """Register Lane A1's own plugins (Vietnamese text). Idempotent - a second call is a no-op because the
    modules are already imported. A lane that only reads the ledger never calls this."""
    import importlib
    for mod in ('repair.repairers.vi_text', 'repair.validators.vi_text'):
        try:
            importlib.import_module(mod)
        except ModuleNotFoundError as e:                      # the plugin has not landed yet
            if e.name != mod:
                raise
    return registry.describe()
