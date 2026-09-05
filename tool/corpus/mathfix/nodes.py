#!/usr/bin/env python3
"""The canonical structured representation of a printed STEM expression.

(The module is `nodes`, not `ast`: `tool/corpus` goes on `sys.path`, and a module named `ast` there
shadows the standard library's for every consumer — `inspect` imports `ast`, `dataclasses` imports
`inspect`, and the CLI died on a circular import before a line of it ran. A name collision with the
stdlib is a defect, not a style question.)

Founder order (round 5, STEM P0): *«STOP treating flattened OCR text as the canonical
representation of mathematical/scientific expressions.»* So the canonical object here is the
**AST**, and everything else is a projection of it:

    AST      the machine / pedagogy form.  `ADD(FRACTION(3,10), FRACTION(5,21))`
    LaTeX    the rendering / interchange form, DERIVED from the AST — never parsed back into it
    text     a courtesy projection for logs and diffs; never a source, never re-read

The one-way rule matters. If LaTeX could be parsed back into an AST, a hand-edited or
model-generated LaTeX string would become structure, and a candidate would have laundered itself
into truth. `to_latex()` exists; `from_latex()` does not, and must not.

Nothing in this module recognises anything. Nodes are built by `extract` out of original
observations, and only a validated node reaches `MathExpression(disposition=VALIDATED_REPAIR)`.

Physics (§6) is the same tree with two extra node kinds — `Quantity` and `Unit` — so that
`m/s` and `m/s²` are different objects rather than different strings, and so a destroyed exponent
is a *structural* impossibility rather than a suspicious character: `Power(Num(10), Deg())` cannot
be built at all, because `Deg` is not a node.
"""
from dataclasses import dataclass, field
from fractions import Fraction

# ---------------------------------------------------------------- operators
ADD, SUB, MUL, DIV, EQ = 'ADD', 'SUB', 'MUL', 'DIV', 'EQ'
_OP_LATEX = {ADD: '+', SUB: '-', MUL: r'\times', DIV: r'\div', EQ: '='}
_OP_TEXT = {ADD: '+', SUB: '−', MUL: '×', DIV: ':', EQ: '='}
#: The printed marks this lane accepts as each operator. ASCII '-' is included deliberately —
#: the shipped `MATH` regex omits it, which is one reason a dangling operator was never caught.
OP_OF_MARK = {'+': ADD, '-': SUB, '–': SUB, '—': SUB, '−': SUB,
              '×': MUL, 'x': MUL, '*': MUL, '÷': DIV, ':': DIV, '=': EQ}


class Node:
    """Base. Every node is immutable and knows how to project itself; none can parse."""

    kind = 'node'

    def to_latex(self):
        raise NotImplementedError

    def to_text(self):
        raise NotImplementedError

    def to_json(self):
        raise NotImplementedError

    def value(self):
        """Exact rational value, or None when the node is not numeric (a symbol, a unit)."""
        return None

    def children(self):
        return ()

    def walk(self):
        yield self
        for c in self.children():
            yield from c.walk()


@dataclass(frozen=True)
class Num(Node):
    """A printed numeric literal, kept EXACTLY as the page prints it.

    `literal` is the observation ('3', '0,7', '1 360'); `value()` is its rational reading. The two
    are separate on purpose: Vietnamese decimals use a comma and thousands a space, and normalising
    the literal away would lose the ability to say what the page actually showed.
    """
    literal: str
    kind = 'NUM'

    def to_latex(self):
        return self.literal.replace(',', '{,}').replace(' ', r'\,')

    def to_text(self):
        return self.literal

    def to_json(self):
        return dict(kind=self.kind, literal=self.literal)

    def value(self):
        t = self.literal.replace(' ', '').replace(' ', '').replace(',', '.')
        try:
            return Fraction(t)
        except (ValueError, ZeroDivisionError):
            return None


@dataclass(frozen=True)
class Sym(Node):
    """A printed symbol: `c`, `v`, `r`, `S`. Carries no value."""
    name: str
    kind = 'SYM'

    def to_latex(self):
        return self.name

    def to_text(self):
        return self.name

    def to_json(self):
        return dict(kind=self.kind, name=self.name)


@dataclass(frozen=True)
class Frac(Node):
    """A printed stacked fraction. The vinculum is part of the structure, not a slash in a string."""
    num: Node
    den: Node
    kind = 'FRACTION'

    def children(self):
        return (self.num, self.den)

    def to_latex(self):
        return rf'\frac{{{self.num.to_latex()}}}{{{self.den.to_latex()}}}'

    def to_text(self):
        return f'{self.num.to_text()}/{self.den.to_text()}'

    def to_json(self):
        return dict(kind=self.kind, num=self.num.to_json(), den=self.den.to_json())

    def value(self):
        a, b = self.num.value(), self.den.value()
        return None if (a is None or b is None or b == 0) else a / b


@dataclass(frozen=True)
class Power(Node):
    """A printed superscript. `Power(Num('10'), Num('8'))` is 10⁸.

    A destroyed exponent cannot be represented: there is no node for «°». That is the point —
    §6's «structurally impossible transformation» is impossible in the model, not merely flagged.
    """
    base: Node
    exp: Node
    kind = 'POWER'

    def children(self):
        return (self.base, self.exp)

    def to_latex(self):
        return rf'{{{self.base.to_latex()}}}^{{{self.exp.to_latex()}}}'

    def to_text(self):
        return f'{self.base.to_text()}^{self.exp.to_text()}'

    def to_json(self):
        return dict(kind=self.kind, base=self.base.to_json(), exp=self.exp.to_json())

    def value(self):
        b, e = self.base.value(), self.exp.value()
        if b is None or e is None or e.denominator != 1:
            return None
        return b ** int(e)


@dataclass(frozen=True)
class BinOp(Node):
    """One printed operator and its operands, in printed order."""
    op: str
    left: Node
    right: Node
    kind = 'BINOP'

    def children(self):
        return (self.left, self.right)

    def to_latex(self):
        return f'{self.left.to_latex()} {_OP_LATEX[self.op]} {self.right.to_latex()}'

    def to_text(self):
        return f'{self.left.to_text()} {_OP_TEXT[self.op]} {self.right.to_text()}'

    def to_json(self):
        return dict(kind=self.op, left=self.left.to_json(), right=self.right.to_json())

    def value(self):
        a, b = self.left.value(), self.right.value()
        if a is None or b is None:
            return None
        if self.op == ADD:
            return a + b
        if self.op == SUB:
            return a - b
        if self.op == MUL:
            return a * b
        if self.op == DIV:
            return None if b == 0 else a / b
        return None            # EQ has no value; `holds()` answers it instead

    def holds(self):
        """For an equality: True/False when both sides evaluate, None when they do not."""
        if self.op != EQ:
            return None
        a, b = self.left.value(), self.right.value()
        return None if (a is None or b is None) else (a == b)


@dataclass(frozen=True)
class Unit(Node):
    """A physical unit: a symbol, an integer exponent, and an optional per-unit denominator.

    `m/s²` is `Unit('m', den=Unit('s', exp=2))` — a structure. That is what makes `m/s` and `m/s²`
    different objects rather than two strings that happen to differ by one character, and it is what
    lets a validator ask «is this a speed?» without pattern-matching prose.
    """
    symbol: str
    exp: int = 1
    den: 'Unit' = None
    kind = 'UNIT'

    def children(self):
        return (self.den,) if self.den else ()

    def to_latex(self):
        s = self.symbol if self.exp == 1 else rf'{self.symbol}^{{{self.exp}}}'
        return s if not self.den else rf'{s}/{self.den.to_latex()}'

    def to_text(self):
        sup = {1: '', 2: '²', 3: '³', -1: '⁻¹', -2: '⁻²'}
        s = self.symbol + sup.get(self.exp, f'^{self.exp}')
        return s if not self.den else f'{s}/{self.den.to_text()}'

    def to_json(self):
        d = dict(kind=self.kind, symbol=self.symbol, exp=self.exp)
        if self.den:
            d['den'] = self.den.to_json()
        return d


@dataclass(frozen=True)
class Quantity(Node):
    """A physical quantity: a magnitude and a unit. `PhysicsExpression = MathExpression + Quantity`.

    `Quantity(Power(Num('3'), ...), Unit('m', den=Unit('s')))` — the speed of light is a magnitude
    times a power of ten with a structured unit, and every part of that is separately checkable.
    """
    magnitude: Node
    unit: Unit
    kind = 'QUANTITY'

    def children(self):
        return (self.magnitude, self.unit)

    def to_latex(self):
        return rf'{self.magnitude.to_latex()}\ \mathrm{{{self.unit.to_latex()}}}'

    def to_text(self):
        return f'{self.magnitude.to_text()} {self.unit.to_text()}'

    def to_json(self):
        return dict(kind=self.kind, magnitude=self.magnitude.to_json(), unit=self.unit.to_json())

    def value(self):
        return self.magnitude.value()


@dataclass(frozen=True)
class Seq(Node):
    """An enumerated printed item and its expression: «b)» followed by the arithmetic.

    Kept as structure rather than glued into the expression, so `b) 3/10 + 5/21` never becomes an
    operand and an enumerator can never join the arithmetic.
    """
    label: str
    body: Node
    kind = 'ITEM'

    def children(self):
        return (self.body,)

    def to_latex(self):
        return rf'\text{{{self.label}}}\ {self.body.to_latex()}'

    def to_text(self):
        return f'{self.label} {self.body.to_text()}'

    def to_json(self):
        return dict(kind=self.kind, label=self.label, body=self.body.to_json())

    def value(self):
        return self.body.value()


@dataclass(frozen=True)
class Row(Node):
    """Several printed items on one line — the shape of a Toán exercise row."""
    items: tuple = field(default_factory=tuple)
    kind = 'ROW'

    def children(self):
        return tuple(self.items)

    def to_latex(self):
        return r' \qquad '.join(i.to_latex() for i in self.items)

    def to_text(self):
        return '    '.join(i.to_text() for i in self.items)

    def to_json(self):
        return dict(kind=self.kind, items=[i.to_json() for i in self.items])


# ---------------------------------------------------------------- rehydration
_BY_KIND = {}


def from_json(d):
    """Rebuild a node from its own JSON. NOT a parser: it reads a tree this module wrote.

    The distinction is the doctrine — there is `from_json` and there is no `from_latex`, so a
    string can never become structure.
    """
    k = d['kind']
    if k == 'NUM':
        return Num(d['literal'])
    if k == 'SYM':
        return Sym(d['name'])
    if k == 'FRACTION':
        return Frac(from_json(d['num']), from_json(d['den']))
    if k == 'POWER':
        return Power(from_json(d['base']), from_json(d['exp']))
    if k in (ADD, SUB, MUL, DIV, EQ):
        return BinOp(k, from_json(d['left']), from_json(d['right']))
    if k == 'UNIT':
        return Unit(d['symbol'], d.get('exp', 1), from_json(d['den']) if d.get('den') else None)
    if k == 'QUANTITY':
        return Quantity(from_json(d['magnitude']), from_json(d['unit']))
    if k == 'ITEM':
        return Seq(d['label'], from_json(d['body']))
    if k == 'ROW':
        return Row(tuple(from_json(x) for x in d['items']))
    raise ValueError(f'unknown node kind {k!r}')
