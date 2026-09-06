#!/usr/bin/env python3
"""Round 7 · WS-M — the CONTAINER-SHAPE LINT.

Finds the defect family that produced round 6's «10 toanExercises» against a true 41, and
round 3's identical mistake before it: **a count or an iteration taken over a keyed
container instead of over its leaf records.**

Two shapes are flagged, both high-precision:

  A · `len(X['toanExercises'])` / `len(X.get('toanExercises'))`
      len() on a by-lesson container returns KEYS. Round 6 published that number as an
      expression count.

  B · `for e in X['toanExercises']` / `for e in X.get('toanExercises') or []`
      Iterating a dict yields its KEYS — strings, not leaf records. The loop body then
      quietly discards every one of them, and the count is silently zero.

The family key may be a literal, or a loop variable drawn from a list/tuple literal of
family names (module-level or inline) — which is how the two live occurrences in
tool/research/lane_c/ are written, and why a literal-only lint would have missed both.

Not a type checker and not trying to be: it knows one schema, `ACTIVITY_SHAPES`, and it is
silent about everything else. A narrow lint that is never wrong is worth more than a broad
one nobody believes.

    python3 tool/metrics/cli.py lint [--root DIR]
"""
import ast
import os

import leaves as L

BY_LESSON_FAMILIES = frozenset(k for k, v in L.ACTIVITY_SHAPES.items() if v == 'by_lesson')

# Directories walked by the lint. `tool/metrics` itself is included: this file's own
# helpers must obey the rule they enforce.
DEFAULT_DIRS = ('tool',)
SKIP_DIRS = {'__pycache__', '.git', 'build', '.dart_tool', 'poc-out', 'node_modules'}


class Finding:
    def __init__(self, path, line, rule, snippet, family_expr):
        self.path, self.line, self.rule = path, line, rule
        self.snippet, self.family_expr = snippet, family_expr

    @property
    def key(self):
        """Baseline identity. Deliberately NOT the line number: an unrelated edit above a
        finding must not silently retire its entry, and a change to the flagged line itself
        SHOULD force a re-triage."""
        return f'{self.path} :: {self.rule} :: {self.snippet}'

    def __str__(self):
        return (f'{self.path}:{self.line}  [{self.rule}]  {self.snippet}\n'
                f'    family key: {self.family_expr}')


def _str_seq(node):
    """The set of string constants in a list/tuple/set literal, else None."""
    if not isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return None
    out = set()
    for elt in node.elts:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            out.add(elt.value)
        else:
            return None
    return out


class _Visitor(ast.NodeVisitor):
    """Collects findings for one module."""

    def __init__(self, path, source):
        self.path = path
        self.lines = source.splitlines()
        self.findings = []
        # names bound (module-wide, conservatively) to a literal sequence of strings
        self.seq_names = {}
        # loop variables currently known to range over family names
        self.family_vars = set()
        # local names currently holding a by-lesson container (its lineage, not its type)
        self.alias = {}

    # -------------------------------------------------- name binding
    def visit_Assign(self, node):
        seq = _str_seq(node.value)
        if seq is not None:
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    self.seq_names[tgt.id] = seq

        # alias lineage: `xs = pack.get(key)` makes `xs` the container.
        # A reassignment that still mentions the alias (`xs = list(xs.values())`) does NOT
        # clear it — that is the one-level-short flatten, and the lineage survives it.
        # A reassignment through a real flatten (a nested comprehension, or
        # flatten_by_lesson) does clear it.
        fam = self._family_access(node.value)
        for tgt in node.targets:
            if not isinstance(tgt, ast.Name):
                continue
            if fam:
                self.alias[tgt.id] = fam
            elif tgt.id in self.alias:
                if self._is_real_flatten(node.value) or not self._mentions(node.value, tgt.id):
                    self.alias.pop(tgt.id, None)
        self.generic_visit(node)

    @staticmethod
    def _mentions(node, name):
        return any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(node))

    @staticmethod
    def _is_real_flatten(node):
        for n in ast.walk(node):
            if isinstance(n, (ast.ListComp, ast.SetComp, ast.GeneratorExp)) and len(n.generators) >= 2:
                return True
            if isinstance(n, ast.Name) and n.id == 'flatten_by_lesson':
                return True
            if isinstance(n, ast.Attribute) and n.attr == 'flatten_by_lesson':
                return True
        return False

    # -------------------------------------------------- the two rules
    def visit_For(self, node):
        # `for key in <seq of family names>:` binds a family variable for the body
        added = None
        seq = _str_seq(node.iter)
        if seq is None and isinstance(node.iter, ast.Name):
            seq = self.seq_names.get(node.iter.id)
        if seq and (seq & BY_LESSON_FAMILIES) and isinstance(node.target, ast.Name):
            added = node.target.id
            self.family_vars.add(added)

        fam = self._container_expr(node.iter)
        if fam:
            self._add(node, 'B-iterate-container', fam,
                      'iterating a by-lesson container yields its KEYS, not leaf records')
        self.generic_visit(node)
        if added:
            self.family_vars.discard(added)

    def visit_FunctionDef(self, node):
        saved = dict(self.alias)
        self.alias.clear()
        self.generic_visit(node)
        self.alias = saved

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        if (isinstance(node.func, ast.Name) and node.func.id == 'len'
                and len(node.args) == 1):
            fam = self._family_access(node.args[0])
            if fam:
                self._add(node, 'A-len-on-container', fam,
                          'len() on a by-lesson container counts KEYS, not leaf records')
        self.generic_visit(node)

    # -------------------------------------------------- recognisers
    def _family_access(self, node):
        """Return the family key expression if `node` reads a by-lesson family, else None.

        Sees through `X or []`, `X or {}` and `list(X)`.
        """
        while True:
            if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or) and node.values:
                node = node.values[0]
                continue
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in ('list', 'sorted') and node.args):
                node = node.args[0]
                continue
            break

        key = None
        if isinstance(node, ast.Subscript):
            key = node.slice
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
              and node.func.attr == 'get' and node.func.value is not None and node.args):
            key = node.args[0]
        if key is None:
            return None

        if isinstance(key, ast.Constant) and key.value in BY_LESSON_FAMILIES:
            return repr(key.value)
        if isinstance(key, ast.Name) and key.id in self.family_vars:
            return f'{key.id} (a family-name loop variable covering {sorted(BY_LESSON_FAMILIES)})'
        return None

    def _container_expr(self, node):
        """`_family_access`, plus names that hold a by-lesson container by lineage."""
        fam = self._family_access(node)
        if fam:
            return fam
        while isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or) and node.values:
            node = node.values[0]
        if isinstance(node, ast.Name) and node.id in self.alias:
            return f'{node.id} (bound from {self.alias[node.id]})'
        return None

    def _add(self, node, rule, fam, _why):
        line = node.lineno
        snippet = self.lines[line - 1].strip() if 0 < line <= len(self.lines) else ''
        self.findings.append(Finding(self.path, line, rule, snippet, fam))


def lint_source(source, path='<string>'):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    v = _Visitor(path, source)
    # two passes: module-level sequence names may be defined after their use
    v.visit(tree)
    v.findings = []
    v.visit(tree)
    return v.findings


def lint_paths(root=None, dirs=DEFAULT_DIRS):
    root = root or L.repo_root()
    out = []
    for d in dirs:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, d)):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in sorted(filenames):
                if not fn.endswith('.py'):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root)
                with open(full, encoding='utf-8') as fh:
                    out.extend(lint_source(fh.read(), rel))
    return sorted(out, key=lambda f: (f.path, f.line))


# --------------------------------------------------------------------------- baseline
# Every occurrence known to WS-M on 2026-09-06, with a verdict. A finding NOT in this map
# is a new one and fails the test in tool/tests/test_metric_registry.py.
#
# These are round-3-era research scripts, not the shipped pack path. They are recorded as
# HISTORICAL CORRECTION TO ROUND 3 rather than silently repaired: the census outputs they
# produced were published, and rewriting the code now would change what a reader finds
# without changing what was published. WS-M does not own those scripts' outputs.
KNOWN_FINDINGS = {
    'tool/research/lane_c/subject_family_census.py :: B-iterate-container :: '
    'for e in p.get(key) or []:':
        'DEFECT, round 3. `for e in p.get(key) or []` with key ranging over PACK_KEYS, which '
        'includes toanExercises. Iterating that dict yields lesson-number STRINGS; the very next '
        'line files each one under `_non_dict_entries` with the comment «some packs carry bare '
        'ids», which is a misdiagnosis of this bug. Effect: the pack-wiring census counted 0 '
        'toanExercises for every family and recorded 10 phantom `_non_dict_entries`, against a '
        'true 41 leaves in 10 lessons. Same defect family as the round-6 incident, two rounds '
        'earlier and still live.',
    'tool/research/lane_c/second_lesson_candidates.py :: B-iterate-container :: '
    'for e in xs:':
        'DEFECT, round 3. `xs = pk.get(key) or []` then `if isinstance(xs, dict): xs = '
        'list(xs.values())` — the shape check is present but the flatten is one level short: '
        '.values() yields LISTS of exercises, and the following `isinstance(e, dict)` rejects '
        'every one. Effect: `pack_wiring[toanExercises]` is 0 for every candidate lesson in the '
        'second-golden-lesson census. A shape check that stops one level early is worse than none, '
        'because it reads as if the shape had been handled.',
}
