#!/usr/bin/env python3
"""Lane E1 · P0.2 input — VisualSpec, and the compilers that project a graph into one.

§10 HYPOTHESIS UNDER TEST
    ProcessSemantic / ComparisonSemantic / TimelineSemantic are better understood as
    COMPILED VISUAL PROJECTIONS of one semantic graph than as canonical knowledge
    semantics:            SemanticGraph -> compileProcess() -> ProcessVisualSpec

    The falsifiable form: every compiler below reads ONLY `SemanticGraph.nodes`,
    `.relations` and `.claims`. If any compiler needs a field that exists solely for its
    own family, the hypothesis is false and that family is canonical, not projected.
    `compiler_audit()` reports which graph fields each compiler touched, so the claim is
    measured rather than asserted.

WHAT LANE E2 RENDERS. A VisualSpec is declarative and renderer-agnostic: no widget, no
colour, no font, no pixel. It carries, per element, the claim it came from and that
claim's status — so a renderer physically cannot draw an element without knowing whether
it is validated, proposed or withheld.

THE `gap` ELEMENT. Round 5's defect 8: withholding one option of a multiple-choice
question leaves the SERVED question wrong, not merely smaller. So a compiler never
silently drops a withheld member of an ordered structure — it emits a `gap` element that
the renderer must draw. A mutilated structure is a teaching-critical error produced by
the safety mechanism itself; the spec makes it visible instead.

No LLM is called anywhere in this module.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from graph import lineage_of  # noqa: E402

SCHEMA = 'visual-spec/v0'

LAYOUTS = ('sequence', 'grid', 'rail', 'tree', 'hubSpoke', 'figureAnchored', 'cards')

ELEMENT_ROLES = ('node', 'edge', 'cell', 'header', 'label', 'gap')


class VisualElement:
    __slots__ = ('id', 'role', 'text', 'claim_id', 'status', 'slot', 'withheld_reason')

    def __init__(self, el_id, role, text, claim_id, status, slot=None,
                 withheld_reason=None):
        if role not in ELEMENT_ROLES:
            raise ValueError('bad element role %r' % (role,))
        if role != 'gap' and not claim_id:
            raise ValueError('every drawable element must name the claim it came from')
        self.id, self.role, self.text = el_id, role, text
        self.claim_id, self.status = claim_id, status
        self.slot, self.withheld_reason = slot or {}, withheld_reason

    def to_json(self):
        d = {'id': self.id, 'role': self.role, 'status': self.status, 'slot': self.slot}
        if self.text is not None:
            d['text'] = self.text
        if self.claim_id:
            d['claim'] = self.claim_id
        if self.withheld_reason:
            d['withheldReason'] = self.withheld_reason
        return d


class VisualSpec:
    def __init__(self, graph, family, layout, title, compiler):
        if layout not in LAYOUTS:
            raise ValueError('bad layout %r' % (layout,))
        self.graph, self.family, self.layout = graph, family, layout
        self.title, self.compiler = title, compiler
        self.elements = []

    def add(self, el):
        self.elements.append(el)
        return el

    @property
    def drawable(self):
        return [e for e in self.elements if e.role != 'gap']

    def trust_block(self):
        """Every VisualSpec states its own trust, in the app's existing vocabulary."""
        statuses = {e.status for e in self.elements}
        validated = statuses == {'validated'}
        return {
            'chipRequired': True,
            'reason': ('no production trust gate exists (THRESHOLDS.json absent), so '
                       'ContentTrust.trustedCorpus is unreachable by construction'),
            'allElementsValidated': validated,
            'contentTrustCeiling': 'trustedStructuredLesson',
        }

    # ⭐ LESSON IDENTITY DOES NOT CROSS INTO THE SPEC — adopted from Lane E2 (PR #86).
    #
    # The first version carried {book, lesson, title, subject, grade} on the spec. E2 is
    # right that this is not a cosmetic field: it makes `if (lessonId == BAI17)` TYPABLE
    # inside a renderer, and a renderer that can name a lesson is a renderer that can
    # grow 3,679 special cases with no test able to catch it. E2 made the anti-pattern
    # untypable (no book/lessonNo/slotKey on VisualSpec, no LessonDocument on the render
    # context) and guards it with source-scanning tests; the spec must not hand the
    # identity back through another door.
    #
    # Identity is genuinely needed — for provenance, for tap-to-source, for addressing —
    # so it lives on the CLAIM/GROUNDING side, in `lineage_json()`, which is a SEPARATE
    # artefact for the trust layer. The renderer receives `to_json()` and cannot see a
    # lesson at all. `04-BAI17-REPLACEMENT.md` reaches the same conclusion from the
    # other direction, so this is agreement between two lanes, not a concession.

    IDENTITY_KEYS = ('book', 'lesson', 'lessonNo', 'slotKey', 'subject', 'grade',
                     'sourceRef', 'sourceBlocks', 'pagePdf', 'pagePrinted')

    def to_json(self):
        """The renderer-facing spec. Carries NO lesson identity, at any depth."""
        return {
            'schema': SCHEMA,
            'family': self.family,
            'layout': self.layout,
            'title': self.title,
            'compiler': self.compiler,
            'elements': [e.to_json() for e in self.elements],
            'counts': {'elements': len(self.elements),
                       'drawable': len(self.drawable),
                       'gaps': sum(1 for e in self.elements if e.role == 'gap')},
            'trust': self.trust_block(),
        }

    def lineage_json(self):
        """The trust-layer artefact. This is where identity lives, and it is not the
        spec: a renderer is given `to_json()`, never this."""
        return {
            'schema': 'visual-spec-lineage/v0',
            'family': self.family,
            'compiler': self.compiler,
            'lesson': {'book': self.graph.book, 'lesson': self.graph.lesson,
                       'title': self.graph.title, 'subject': self.graph.subject,
                       'grade': self.graph.grade},
            'rows': [lineage_of(e.id, self.graph.claims[e.claim_id], self.graph)
                     for e in self.elements
                     if e.claim_id and e.claim_id in self.graph.claims],
        }


# ---------------------------------------------------------------------------
# the compilers. Each reads ONLY nodes / relations / claims.
# ---------------------------------------------------------------------------
_TOUCHED = {}


def _touch(compiler, field):
    _TOUCHED.setdefault(compiler, set()).add(field)


def compiler_audit():
    """{compilerId: sorted(graph fields it read)} — the §10 hypothesis, measured."""
    return {k: sorted(v) for k, v in _TOUCHED.items()}


def _status_of(graph, claim_id):
    c = graph.claims.get(claim_id)
    return c.status if c else 'proposed'


def compile_process(graph):
    """SemanticGraph -> ProcessVisualSpec. Reads Step nodes and `next` relations.

    A lesson usually prints MORE THAN ONE procedure (Bai 17 ships two process diagrams
    today). So this walks every chain and tags each with a `group`, instead of picking
    the first and silently dropping the rest — dropping them would understate both the
    lesson and the "how many lessons carry multiple visual patterns" census question.
    """
    cid = 'compileProcess@v0'
    _touch(cid, 'nodes'), _touch(cid, 'relations'), _touch(cid, 'claims')
    steps = [n for n in graph.nodes.values() if n.primitive == 'Step']
    if len(steps) < 2:
        return None
    nxt = {r.src: r for r in graph.relations if r.relation == 'next'}
    has_pred = {r.dst for r in graph.relations if r.relation == 'next'}
    starts = [s for s in steps if s.id not in has_pred and s.id in nxt]
    if not starts:
        return None
    spec = VisualSpec(graph, 'PROCESS', 'sequence',
                      'Các bước — theo thứ tự sách in', cid)
    seen = set()
    for group, start in enumerate(starts):
        order, cur = 0, start
        while cur is not None and cur.id not in seen:
            seen.add(cur.id)
            order += 1
            c = cur.claims[0]
            spec.add(VisualElement('%s#n%d' % (cur.id, order), 'node', cur.label, c.id,
                                   c.status, slot={'group': group, 'order': order}))
            rel = nxt.get(cur.id)
            if rel is None:
                break
            spec.add(VisualElement('%s#e%d' % (cur.id, order), 'edge', None,
                                   rel.claim.id, rel.claim.status,
                                   slot={'group': group, 'from': order, 'to': order + 1}))
            cur = graph.nodes.get(rel.dst)
    return spec if len(spec.drawable) >= 2 else None


def compile_timeline(graph):
    """SemanticGraph -> TimelineVisualSpec. Reads Event nodes and their atTime claims."""
    cid = 'compileTimeline@v0'
    _touch(cid, 'nodes'), _touch(cid, 'claims')
    events = [n for n in graph.nodes.values() if n.primitive == 'Event']
    if len(events) < 2:
        return None
    def key(n):
        import re
        m = re.search(r'(\d{3,4})', n.attrs.get('when', '') or '')
        y = int(m.group(1)) if m else 0
        if 'TCN' in (n.attrs.get('when') or '') or 'tcn' in (n.attrs.get('when') or ''):
            y = -y
        return y
    events.sort(key=key)
    spec = VisualSpec(graph, 'TIMELINE', 'rail', 'Dòng thời gian', cid)
    for i, n in enumerate(events):
        c = n.claims[0]
        spec.add(VisualElement('%s#t%d' % (n.id, i), 'node', n.label, c.id, c.status,
                               slot={'order': i + 1, 'when': n.attrs.get('when'),
                                     'year': key(n)}))
    return spec


def compile_hierarchy(graph):
    """SemanticGraph -> HierarchyVisualSpec. Reads Entity nodes and `hasPart`."""
    cid = 'compileHierarchy@v0'
    _touch(cid, 'nodes'), _touch(cid, 'relations'), _touch(cid, 'claims')
    parts = [r for r in graph.relations if r.relation == 'hasPart']
    if len(parts) < 2:
        return None
    spec = VisualSpec(graph, 'HIERARCHY', 'tree', 'Cấu trúc bài — theo đề mục sách in', cid)
    placed = set()
    for r in parts:
        for nid in (r.src, r.dst):
            if nid in placed:
                continue
            n = graph.nodes[nid]
            c = n.claims[0]
            spec.add(VisualElement('%s#h' % nid, 'node', n.label, c.id, c.status,
                                   slot={'depth': n.attrs.get('depth', 0)}))
            placed.add(nid)
        spec.add(VisualElement('%s#edge' % r.id, 'edge', None, r.claim.id, r.claim.status,
                               slot={'from': '%s#h' % r.src, 'to': '%s#h' % r.dst}))
    return spec


def compile_labeled_figure(graph):
    """SemanticGraph -> LabeledFigureVisualSpec. Reads Figure nodes and `depicts`."""
    cid = 'compileLabeledFigure@v0'
    _touch(cid, 'nodes'), _touch(cid, 'relations'), _touch(cid, 'claims')
    figs = [n for n in graph.nodes.values() if n.primitive == 'Figure']
    dep = [r for r in graph.relations if r.relation == 'depicts']
    if not figs or not dep:
        return None
    spec = VisualSpec(graph, 'LABELED_FIGURE', 'figureAnchored',
                      'Hình và câu sách nói về hình', cid)
    for f in figs:
        c = f.claims[0]
        g0 = c.grounding[0]
        # geometry, not identity: the bbox says WHERE ON ITS PAGE the figure sits, which
        # a figure-anchored layout needs. The page NUMBER is identity and stays in the
        # lineage artefact.
        spec.add(VisualElement('%s#f' % f.id, 'node', f.label, c.id, c.status,
                               slot={'figureNumber': f.attrs.get('figureNumber'),
                                     'bbox': g0.bbox}))
    for r in dep:
        src = graph.nodes[r.src]
        spec.add(VisualElement('%s#l' % r.id, 'label', src.label, r.claim.id,
                               r.claim.status, slot={'anchor': '%s#f' % r.dst}))
    return spec


def compile_causal(graph):
    cid = 'compileCausal@v0'
    _touch(cid, 'nodes'), _touch(cid, 'relations'), _touch(cid, 'claims')
    edges = [r for r in graph.relations if r.relation == 'causes']
    if not edges:
        return None
    spec = VisualSpec(graph, 'CAUSAL', 'sequence', 'Nguyên nhân → kết quả', cid)
    for i, r in enumerate(edges):
        for side, nid in (('cause', r.src), ('effect', r.dst)):
            n = graph.nodes[nid]
            c = n.claims[0]
            spec.add(VisualElement('%s#%s' % (r.id, side), 'node', n.label, c.id,
                                   c.status, slot={'pair': i, 'side': side}))
        spec.add(VisualElement('%s#arrow' % r.id, 'edge', None, r.claim.id,
                               r.claim.status, slot={'pair': i}))
    return spec


def compile_definition(graph):
    cid = 'compileDefinition@v0'
    _touch(cid, 'nodes'), _touch(cid, 'relations'), _touch(cid, 'claims')
    edges = [r for r in graph.relations if r.relation == 'hasProperty']
    if not edges:
        return None
    spec = VisualSpec(graph, 'DEFINITION', 'cards', 'Thuật ngữ sách nêu', cid)
    for i, r in enumerate(edges):
        t, d = graph.nodes[r.src], graph.nodes[r.dst]
        spec.add(VisualElement('%s#term' % r.id, 'header', t.label, t.claims[0].id,
                               t.claims[0].status, slot={'card': i}))
        spec.add(VisualElement('%s#defn' % r.id, 'node', d.label, d.claims[0].id,
                               d.claims[0].status, slot={'card': i}))
    return spec


COMPILERS = {
    'PROCESS': compile_process,
    'TIMELINE': compile_timeline,
    'HIERARCHY': compile_hierarchy,
    'LABELED_FIGURE': compile_labeled_figure,
    'CAUSAL': compile_causal,
    'DEFINITION': compile_definition,
}


def compile_all(graph):
    """{family: VisualSpec} for every family this graph actually supports."""
    out = {}
    for fam, fn in COMPILERS.items():
        try:
            spec = fn(graph)
        except Exception:
            spec = None
        if spec is not None and spec.elements:
            out[fam] = spec
    return out
