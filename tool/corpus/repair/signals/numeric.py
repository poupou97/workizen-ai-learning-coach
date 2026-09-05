#!/usr/bin/env python3
"""Third signal **layer C** - deterministic number / unit / formula checks. **This is Lane A2's slot.**

A1 owns the *interface* and a fail-closed default; A2 owns the knowledge and registers a real provider from
`tool/corpus/mathfix/` without editing this file:

    from repair.signals import numeric
    numeric.register_provider(my_provider)     # my_provider(text_before, text_after, ctx) -> Signal | None

The default provider below never invents a number. It says only what is deterministically true of two
strings: it **objects** to any proposal that changes the digit/operator sequence of the observed text. That
is the fail-closed default a text lane needs - a Vietnamese diacritic repair must never move a digit - and
it is exactly the constraint A2 will refine when it can prove a digit repair.
"""
from __future__ import annotations

import re

from .. import model, registry

DIGIT_RUN = re.compile(r'\d+')
OPERATORS = re.compile(r'[=<>≤≥≠+×÷/%°]')

_provider = None


def register_provider(fn):
    """Lane A2 installs its deterministic checker here. It receives (observed_text, proposed_text, ctx)
    and returns a `Signal` (or None to fall through to the default)."""
    global _provider
    _provider = fn
    return fn


def digits_and_operators(text):
    return (DIGIT_RUN.findall(text or ''), OPERATORS.findall(text or ''))


@registry.signal('C.numeric')
def numeric_signal(observed_text, proposed_text, ctx=None):
    if _provider is not None:
        s = _provider(observed_text, proposed_text, ctx)
        if s is not None:
            return s
    od, oo = digits_and_operators(observed_text)
    pd, po = digits_and_operators(proposed_text)
    if od != pd or oo != po:
        return model.Signal('C.numeric', model.SignalVerdict.OBJECTS, 1.0,
                            dict(observed_digits=od, proposed_digits=pd,
                                 observed_operators=oo, proposed_operators=po,
                                 note='a text repair may not change a digit or an operator; '
                                      'layer C is Lane A2\'s to refine'))
    return model.Signal('C.numeric', model.SignalVerdict.ABSTAINS, 0.0,
                        dict(digits_unchanged=True, note='default provider: no positive numeric evidence, '
                                                         'only the guarantee that nothing numeric moved'))
