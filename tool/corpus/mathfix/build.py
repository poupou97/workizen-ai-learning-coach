#!/usr/bin/env python3
"""From placed observations to an AST — deterministically, or not at all.

This is the step the Founder's §1 chain calls «canonical structured representation». It takes the
atoms the page actually showed — OCR tokens split into enumerators, numbers and operator marks,
plus the `Frac` nodes the raster-validated vinculums licensed — orders them by x, and parses them.

Two properties are the whole point:

  · **A dangling operator cannot parse.** `b) 10 +` ends on an operator, so `parse_item` refuses it.
    That is R2's request (b) — `docs/research/legacy-reprocess/PIPELINE-REQUESTS-FROM-LEGACY.md:71-77`,
    OPEN·P0 since round 4 — met structurally rather than by another regex. The shipped `MATH`
    pattern cannot express it: it needs a digit AFTER the operator, which is exactly what is missing.
  · **An unknown mark fails the whole block closed.** A character this module cannot name is not
    skipped, not guessed and not passed through: it aborts the parse. Prose cannot leak into an
    expression, and a mark the lane has never seen cannot be silently dropped from arithmetic.

Precedence is ordinary school precedence (× ÷ over + −, `=` lowest). It is applied to the printed
order and never re-orders anything.
"""
import re
from dataclasses import dataclass

from . import nodes as A

# An enumerator («a)», «b.», «C]») — a label, never an operand.
ENUMERATOR = re.compile(r'^[a-eA-E]\s*[)\].]')
NUMBER = re.compile(r'^\d+(?:[.,]\d+)?(?:\s\d{3})*')
OPERATOR = re.compile(r'^[+\-–—−×x*÷:=]')
SYMBOL = re.compile(r'^[a-zA-Z](?![a-zA-Z])')
SKIP = re.compile(r'^[\s;,.()\[\]%]')

_PRECEDENCE = {A.EQ: 0, A.ADD: 1, A.SUB: 1, A.MUL: 2, A.DIV: 2}


class Unparseable(Exception):
    """The atoms do not form a printed expression. Always fail closed, always with a reason."""


@dataclass(frozen=True)
class Atom:
    """One printed mark, with where it is on the page.

    `box` is (x0, y0, x1, y1) normalised, interpolated across the OCR token's own box. It is what
    lets `validate.operator_raster_v1` go back to the raster and ask whether the printed glyph is
    really the operator the OCR named — the check that catches a «×» read as «−».
    """
    x: float
    kind: str                # 'enum' | 'num' | 'op' | 'sym' | 'node'
    payload: object
    box: tuple = None


def atoms_of_token(text, x0, x1, y0=None, y1=None):
    """[Atom] for one OCR token, positions interpolated across its own box.

    Raises `Unparseable` on any character this module cannot name — see the module docstring.
    """
    t = text or ''
    n = max(1, len(t))
    out = []
    i = 0

    def box(a, b):
        if y0 is None:
            return None
        return (x0 + (a / n) * (x1 - x0), y0, x0 + (b / n) * (x1 - x0), y1)

    while i < len(t):
        rest = t[i:]
        if SKIP.match(rest):
            i += 1
            continue
        x = x0 + (i / n) * (x1 - x0)
        for pat, kind, pay in ((ENUMERATOR, 'enum', lambda m: m.group(0).strip()),
                               (NUMBER, 'num', lambda m: m.group(0).strip()),
                               (OPERATOR, 'op', lambda m: A.OP_OF_MARK[m.group(0)]),
                               (SYMBOL, 'sym', lambda m: m.group(0))):
            m = pat.match(rest)
            if m:
                out.append(Atom(x, kind, pay(m), box(i, i + m.end())))
                i += m.end()
                break
        else:
            raise Unparseable(f'unknown mark {rest[0]!r} in {t!r}')
    return out


def _pop(ops, out):
    op = ops.pop()
    if len(out) < 2:
        raise Unparseable(f'operator {op} without two operands')
    right = out.pop()
    left = out.pop()
    out.append(A.BinOp(op, left, right))


def parse_item(atoms):
    """Shunting-yard over one item's atoms → a Node. Refuses anything that is not a full expression.

    `atoms` are `Atom`s with kind in {'num', 'sym', 'op', 'node'}; `'node'` carries an already-built
    subtree (a `Frac` from a validated vinculum, a `Quantity`).
    """
    out, ops = [], []
    expect_operand = True
    for a in atoms:
        kind, payload = a.kind, a.payload
        if kind in ('num', 'sym', 'node'):
            if not expect_operand:
                raise Unparseable('two operands with no operator between them')
            out.append(A.Num(payload) if kind == 'num'
                       else A.Sym(payload) if kind == 'sym' else payload)
            expect_operand = False
        elif kind == 'op':
            if expect_operand:
                raise Unparseable(f'operator {payload} with no left operand')
            while ops and _PRECEDENCE[ops[-1]] >= _PRECEDENCE[payload]:
                _pop(ops, out)
            ops.append(payload)
            expect_operand = True
        else:
            raise Unparseable(f'unexpected atom kind {kind!r}')
    if expect_operand:
        raise Unparseable('the expression ends on an operator')      # «b) 10 +»
    while ops:
        _pop(ops, out)
    if len(out) != 1:
        raise Unparseable('the atoms do not form one expression')
    return out[0]


def build_row(atoms):
    """Split an x-ordered atom stream at its enumerators and parse each item.

    Returns a `Row` when the line carries enumerated items, the bare node when it carries one
    unlabelled expression. Raises `Unparseable` if ANY item fails — one destroyed item poisons the
    row, which is the deliberate choice: three correct items beside one destroyed one is the round-3
    failure this lane exists to prevent.
    """
    atoms = sorted(atoms, key=lambda a: a.x)
    items, label, cur = [], None, []
    for a in atoms:
        if a.kind == 'enum':
            if cur:
                items.append((label, cur))
            label, cur = a.payload, []
        else:
            cur.append(a)
    if cur:
        items.append((label, cur))
    if not items:
        raise Unparseable('no atoms')
    built = []
    for lab, group in items:
        node = parse_item(group)
        built.append(A.Seq(lab, node) if lab else node)
    return built[0] if len(built) == 1 else A.Row(tuple(built))
