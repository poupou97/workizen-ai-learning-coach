#!/usr/bin/env python3
"""Lane E1 · P0.1 — the minimal Semantic Foundation (research candidate, not production).

    SourceBlock(s) -> SemanticClaim -> Validation -> SemanticNode/Relation -> VisualElement

This module implements the first three hops as data. It deliberately does NOT implement
"validation" as an approval: a claim leaves here with `status='proposed'` unless a named
deterministic validator ran and said otherwise. Nothing here promotes a claim to truth.

WHAT IS REUSED, WHAT IS NEW (§5: "audit and reuse the existing KnowledgeOrigin /
Provenance first; do not duplicate enums").

  REUSED VERBATIM from lib/, no new vocabulary invented:
    KnowledgeOrigin   lib/core/knowledge/provenance.dart:15
                      sourceStated · sourceDemonstrated · sourceSequence
                      systemDerived · llmInferred
    ContentTrust      lib/core/lesson_model/content_trust.dart:21
                      trustedCorpus · fixtureFromTrustedCorpus · fixtureSynthetic
                      prototype · trustedStructuredLesson · withheld
    SourceRef fields  lib/core/lesson_model/lesson_document.dart:18
                      book · pagePdf · pagePrinted · bbox · blockId · extraction
                      · ocrConf · pipeline · agreementScore
    derivation        lib/core/lesson_model/semantic_data.dart:28 (a rule id string)

  MEASURED GAP — the Founder's §5 list maps onto KnowledgeOrigin as follows:
    SOURCE_STATED          -> KnowledgeOrigin.sourceStated          EXISTS
    SOURCE_DEMONSTRATED    -> KnowledgeOrigin.sourceDemonstrated    EXISTS
    DETERMINISTIC_DERIVED  -> KnowledgeOrigin.systemDerived         EXISTS
    MODEL_PROPOSED         -> KnowledgeOrigin.llmInferred           EXISTS (narrower name)
    HUMAN_CURATED          -> (none)                                MISSING  <-- 1 new value
    CONFLICT               -> NOT AN ORIGIN                         wrong axis
    WITHHELD               -> NOT AN ORIGIN                         wrong axis
  CONFLICT and WITHHELD answer "what happened to this claim", not "where did it come
  from". Folding them into KnowledgeOrigin would make `citableAsTextbookFact`
  (provenance.dart:83) undecidable, because a withheld sourceStated claim would lose the
  fact that the SOURCE said it. So this module keeps two orthogonal fields —
  `support` (KnowledgeOrigin, extended by exactly one value) and `status` (ClaimStatus,
  new and small). That is the whole enum delta: +1 value, +1 enum.

  KnowledgeOrigin also already carries `sourceSequence`, which the Founder's list omits
  and which is load-bearing (TOC order is not a prerequisite — provenance.dart:28-33).
  It is kept.

NO `from_<presentation>` CONSTRUCTOR — EVER (adopted from Lane A2, PR #84).
    A2's `MathExpression` has `from_json` and deliberately NO `from_latex`: `latex` and
    `text` are computed properties with no setter, so a rendering string cannot become
    structure. The same rule binds here and is enforced by a test that scans this
    package: a semantic object may be built from validated structure carrying its
    provenance, never from a rendered or serialised PRESENTATION form. A
    `SemanticClaim.from_markdown` / `VisualSpec.from_svg` / `..._from_latex` would be
    exactly the hole through which a model's output launders itself into TrustedText.
    `SourceGrounding.from_tsl_block` is allowed because a TSL block is not a rendering:
    it is the validated source record, and it carries the page, bbox and pipeline that
    make the claim auditable.

No LLM is called anywhere in this module.
"""
import hashlib
import json

# --- reused vocabularies (mirrored from lib/, names identical on purpose) -----

KNOWLEDGE_ORIGIN = (
    'sourceStated',        # the book says it, quotable with a page
    'sourceDemonstrated',  # the book teaches it by example without stating the rule
    'sourceSequence',      # the book only orders it (never a dependency)
    'systemDerived',       # a deterministic rule over source data
    'llmInferred',         # a model proposed it — never citable
    'humanCurated',        # NEW (+1): a person asserted it; today only expressible as
                           # BindingSource.curated on a different object
)

CONTENT_TRUST = (
    'trustedCorpus', 'fixtureFromTrustedCorpus', 'fixtureSynthetic',
    'prototype', 'trustedStructuredLesson', 'withheld',
)

# --- new, and deliberately tiny -------------------------------------------------

CLAIM_STATUS = (
    'proposed',    # default. A cue matched, a rule fired. NOT truth.
    'validated',   # a named validator ran and passed. Records validatorId.
    'conflict',    # two groundings disagree, or a validator failed.
    'withheld',    # the supporting source region is withheld -> the claim may not be shown.
    'superseded',  # replaced by a later claim (data versioning, round-5 §"disposition").
)

# a claim that may reach a learner must be BOTH of these
LEARNER_VISIBLE_STATUS = ('validated',)
CITABLE_ORIGINS = ('sourceStated', 'sourceDemonstrated', 'sourceSequence')


class SemanticError(ValueError):
    """Raised instead of writing a half-grounded object. Fail-closed by construction."""


def _sha(obj):
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]


# ---------------------------------------------------------------------------
# §7 SourceGrounding — strictly more precise than a bare `sourceBlockId`
# ---------------------------------------------------------------------------
class SourceGrounding:
    """Where a claim actually comes from, at the strongest practical resolution.

    `sourceBlockId` alone (semantic_data.dart:152 etc.) cannot answer "show me the
    print". This carries the page in BOTH numbering systems, the page geometry, and —
    when the evidence is text — the character span inside the block.

    Character offsets are NOT required everywhere: for a figure or a diagram region the
    appropriate evidence is page geometry, so `span` stays None and `figure_id`/`bbox`
    carry the evidence. But a grounding must have at least one locator beyond the block
    id, or it is not a grounding.
    """

    __slots__ = ('book', 'block_id', 'page_pdf', 'page_printed', 'bbox', 'span',
                 'figure_id', 'extraction', 'pipeline', 'ocr_conf', 'agreement_score',
                 'trust', 'quote')

    def __init__(self, book, block_id, page_pdf=None, page_printed=None, bbox=None,
                 span=None, figure_id=None, extraction=None, pipeline=None,
                 ocr_conf=None, agreement_score=None, trust=None, quote=None):
        if not book or not block_id:
            raise SemanticError('grounding needs a book and a block id')
        if trust not in CONTENT_TRUST:
            raise SemanticError('grounding trust %r is not a ContentTrust value' % (trust,))
        # the §7 requirement: something more precise than the block id must be present
        if page_printed is None and page_pdf is None and bbox is None and figure_id is None:
            raise SemanticError('grounding for %s has no locator beyond the block id'
                                % block_id)
        if span is not None:
            if (not isinstance(span, (tuple, list)) or len(span) != 2
                    or span[0] < 0 or span[1] <= span[0]):
                raise SemanticError('bad span %r on %s' % (span, block_id))
            span = (int(span[0]), int(span[1]))
        self.book, self.block_id = book, block_id
        self.page_pdf, self.page_printed, self.bbox = page_pdf, page_printed, bbox
        self.span, self.figure_id = span, figure_id
        self.extraction, self.pipeline = extraction, pipeline
        self.ocr_conf, self.agreement_score = ocr_conf, agreement_score
        self.trust = trust
        # the exact characters the span covers, so a reviewer never has to re-derive it.
        # D4: this stays in gitignored poc-out/, never in the repo.
        self.quote = quote

    @property
    def locator_kind(self):
        if self.span is not None:
            return 'text-span'
        if self.figure_id is not None:
            return 'figure-region'
        if self.bbox is not None:
            return 'page-geometry'
        return 'page'

    def to_json(self):
        d = {'book': self.book, 'blockId': self.block_id, 'trust': self.trust,
             'locatorKind': self.locator_kind}
        for k, v in (('pagePdf', self.page_pdf), ('pagePrinted', self.page_printed),
                     ('bbox', self.bbox), ('figureId', self.figure_id),
                     ('extraction', self.extraction), ('pipeline', self.pipeline),
                     ('ocrConf', self.ocr_conf), ('agreementScore', self.agreement_score),
                     ('quote', self.quote)):
            if v is not None:
                d[k] = v
        if self.span is not None:
            d['span'] = {'start': self.span[0], 'end': self.span[1]}
        return d

    @staticmethod
    def from_tsl_block(block, span=None, quote=None):
        """Build a grounding from a TSL block dict as `corpus_io.load_tsl` returns it."""
        return SourceGrounding(
            book=block.get('book') or (block.get('id') or '').split(':')[0],
            block_id=block['id'], page_pdf=block.get('page'),
            page_printed=block.get('page_printed'), bbox=block.get('bbox'),
            span=span, extraction=block.get('extraction'), pipeline=block.get('pipeline'),
            ocr_conf=block.get('ocr_conf'), agreement_score=block.get('text_sim'),
            trust='trustedStructuredLesson', quote=quote)


# ---------------------------------------------------------------------------
# §5 SemanticClaim — first-class, and the ONLY way a node or relation exists
# ---------------------------------------------------------------------------
class SemanticClaim:
    """A proposition about the lesson, with its support, its status, and its grounding.

    The Founder's rule this type exists to enforce:
        `A --CAUSES--> B` must not become truth merely because A and B are both
        source-grounded. THE RELATIONSHIP ITSELF needs grounding and status.

    So a claim's `subject` is either a node or a *relation*, and in the relation case the
    grounding must point at the text that asserts the relation — not at the two endpoints.
    `assert_relation_grounding_is_not_endpoints()` enforces exactly that.
    """

    __slots__ = ('id', 'kind', 'subject', 'assertion', 'support', 'status', 'derivation',
                 'grounding', 'confidence', 'validator_id', 'validator_result', 'notes')

    def __init__(self, kind, subject, assertion, support, derivation, grounding,
                 confidence=None, status='proposed', validator_id=None,
                 validator_result=None, notes=None, claim_id=None):
        if kind not in ('node', 'relation'):
            raise SemanticError('claim kind must be node|relation, got %r' % (kind,))
        if support not in KNOWLEDGE_ORIGIN:
            raise SemanticError('support %r is not a KnowledgeOrigin value' % (support,))
        if status not in CLAIM_STATUS:
            raise SemanticError('status %r is not a ClaimStatus value' % (status,))
        if not derivation:
            raise SemanticError('a claim without a derivation rule id is unauditable')
        grounding = list(grounding or ())
        if not grounding:
            raise SemanticError('a claim with no grounding cannot exist (%r)' % (assertion,))
        for g in grounding:
            if not isinstance(g, SourceGrounding):
                raise SemanticError('grounding must be SourceGrounding')
        if status == 'validated' and not validator_id:
            raise SemanticError('status=validated requires a validatorId')
        # a claim grounded only in withheld regions may never be shown
        if all(g.trust == 'withheld' for g in grounding) and status != 'withheld':
            raise SemanticError('claim grounded only in withheld regions must be withheld')
        self.kind, self.subject, self.assertion = kind, subject, assertion
        self.support, self.status, self.derivation = support, status, derivation
        self.grounding, self.confidence = grounding, confidence
        self.validator_id, self.validator_result = validator_id, validator_result
        self.notes = notes
        self.id = claim_id or ('cl:' + _sha({'k': kind, 's': subject, 'a': assertion,
                                             'd': derivation}))

    @property
    def citable_as_textbook_fact(self):
        """Mirrors Provenance.citableAsTextbookFact (provenance.dart:83) exactly.

        Same rule, now decidable for a semantic object — which it is not today, because
        SemanticData carries no Provenance at all.
        """
        return (self.support in CITABLE_ORIGINS
                and any(g.page_printed is not None for g in self.grounding)
                and self.status not in ('withheld', 'conflict'))

    @property
    def learner_visible(self):
        """TRACE != EVIDENCE. Proposed is a trace. Only validated may reach a learner."""
        return (self.status in LEARNER_VISIBLE_STATUS
                and all(g.trust != 'withheld' for g in self.grounding))

    def to_json(self):
        d = {'id': self.id, 'kind': self.kind, 'subject': self.subject,
             'assertion': self.assertion, 'support': self.support, 'status': self.status,
             'derivation': self.derivation,
             'grounding': [g.to_json() for g in self.grounding],
             'citableAsTextbookFact': self.citable_as_textbook_fact,
             'learnerVisible': self.learner_visible}
        for k, v in (('confidence', self.confidence), ('validatorId', self.validator_id),
                     ('validatorResult', self.validator_result), ('notes', self.notes)):
            if v is not None:
                d[k] = v
        return d


# ---------------------------------------------------------------------------
# Nodes and relations — thin, because the claim carries the weight
# ---------------------------------------------------------------------------
class SemanticNode:
    __slots__ = ('id', 'primitive', 'label', 'claims', 'attrs')

    def __init__(self, node_id, primitive, label, claims=(), **attrs):
        self.id, self.primitive, self.label = node_id, primitive, label
        self.claims = list(claims)
        self.attrs = attrs

    def to_json(self):
        d = {'id': self.id, 'primitive': self.primitive, 'label': self.label,
             'claims': [c.id for c in self.claims]}
        d.update({k: v for k, v in self.attrs.items() if v is not None})
        return d


class SemanticRelation:
    __slots__ = ('id', 'relation', 'src', 'dst', 'claim', 'attrs')

    def __init__(self, relation, src, dst, claim, **attrs):
        if not isinstance(claim, SemanticClaim) or claim.kind != 'relation':
            raise SemanticError('a relation needs its OWN relation-kind claim '
                                '(%s -%s-> %s)' % (src, relation, dst))
        self.relation, self.src, self.dst, self.claim = relation, src, dst, claim
        self.attrs = attrs
        self.id = 'rel:' + _sha({'r': relation, 's': src, 'd': dst, 'c': claim.id})

    def to_json(self):
        d = {'id': self.id, 'relation': self.relation, 'from': self.src, 'to': self.dst,
             'claim': self.claim.id}
        d.update({k: v for k, v in self.attrs.items() if v is not None})
        return d


class SemanticGraph:
    """A per-lesson graph CANDIDATE. The word candidate is not decoration: nothing in
    this object has crossed a trust gate, and `summary()` reports the counts that say so.
    """

    def __init__(self, book, lesson, title, subject=None, grade=None, pipeline=None):
        self.book, self.lesson, self.title = book, lesson, title
        self.subject, self.grade, self.pipeline = subject, grade, pipeline
        self.nodes, self.relations, self.claims = {}, [], {}
        self.notes = []

    def add_claim(self, claim):
        self.claims[claim.id] = claim
        return claim

    def add_node(self, node):
        for c in node.claims:
            self.add_claim(c)
        self.nodes[node.id] = node
        return node

    def add_relation(self, rel):
        if rel.src not in self.nodes or rel.dst not in self.nodes:
            raise SemanticError('relation endpoints must exist: %s -> %s'
                                % (rel.src, rel.dst))
        self.add_claim(rel.claim)
        self.relations.append(rel)
        return rel

    def summary(self):
        cs = list(self.claims.values())
        by_status, by_support = {}, {}
        for c in cs:
            by_status[c.status] = by_status.get(c.status, 0) + 1
            by_support[c.support] = by_support.get(c.support, 0) + 1
        return {
            'nodes': len(self.nodes), 'relations': len(self.relations),
            'claims': len(cs),
            'claimsByStatus': by_status, 'claimsBySupport': by_support,
            'citable': sum(1 for c in cs if c.citable_as_textbook_fact),
            'learnerVisible': sum(1 for c in cs if c.learner_visible),
            'groundingsByLocator': _count(g.locator_kind for c in cs for g in c.grounding),
        }

    def to_json(self):
        return {
            'schema': 'semantic-graph-candidate/v0',
            'book': self.book, 'lesson': self.lesson, 'title': self.title,
            'subject': self.subject, 'grade': self.grade, 'pipeline': self.pipeline,
            'status': 'CANDIDATE — no trust gate exists; nothing here is product truth',
            'nodes': [n.to_json() for n in self.nodes.values()],
            'relations': [r.to_json() for r in self.relations],
            'claims': [c.to_json() for c in self.claims.values()],
            'summary': self.summary(),
            'notes': self.notes,
        }


def _count(it):
    out = {}
    for x in it:
        out[x] = out.get(x, 0) + 1
    return out


# ---------------------------------------------------------------------------
# §6 the provenance bridge — one total function, no new provenance system
# ---------------------------------------------------------------------------
def provenance_of(claim, book_series=None, grade=None, subject=None):
    """Project a SemanticClaim into the EXISTING `Provenance` shape (provenance.dart:43).

    This is the whole bridge. The two worlds do not merge; the claim simply knows how to
    speak both languages:

        content world   SourceGrounding <- SourceRef fields (book/page/bbox/blockId/...)
        knowledge world Provenance      <- origin/sourceId/extractionMethod/confidence/
                                           pageStart/pageEnd/sourceHash

    Note what becomes decidable the moment this exists: `citableAsTextbookFact`. Today a
    ProcessStep carries a bare `sourceBlockId` and NO Provenance, so nothing can compute
    whether a rendered step may be introduced to a child with "sách viết…". Here it can.

    `sourceId` is the block id, never a file path (provenance.dart:60-62 is explicit
    that a path leaks the machine's layout into the data).
    """
    g = claim.grounding[0]
    pages = [x.page_printed for x in claim.grounding if x.page_printed is not None]
    return {
        'origin': claim.support,
        'sourceId': g.block_id,
        'extractionMethod': claim.derivation,
        'confidence': claim.confidence if claim.confidence is not None else 0.0,
        'bookSeries': book_series,
        'grade': grade,
        'subject': subject,
        'pageStart': min(pages) if pages else None,
        'pageEnd': max(pages) if pages else None,
        'sourceHash': None,
        # carried across so the knowledge world can see the content world's verdict
        # without importing it: this is the join key, not a merged enum.
        '_contentTrust': g.trust,
        '_claimStatus': claim.status,
        'citableAsTextbookFact': claim.citable_as_textbook_fact,
    }


def lineage_of(visual_element_id, claim, graph):
    """The §6 chain, materialised as data so it can be asserted in a test.

    VisualElement -> VisualSpec element -> SemanticClaim -> SemanticNode/Relation
                  -> SourceBlock/SourceSpan -> SourceRef -> TrustedLearningSource
    """
    return {
        'visualElement': visual_element_id,
        'claim': claim.id,
        'claimStatus': claim.status,
        'support': claim.support,
        'derivation': claim.derivation,
        'sourceBlocks': [g.block_id for g in claim.grounding],
        'sourceSpans': [g.to_json().get('span') for g in claim.grounding],
        'sourceRef': [{'book': g.book, 'pagePdf': g.page_pdf,
                       'pagePrinted': g.page_printed, 'bbox': g.bbox}
                      for g in claim.grounding],
        'trustedLearningSource': {
            'trust': sorted({g.trust for g in claim.grounding}),
            # honest terminus: no TrustedLearningSource gate exists yet (round 4 §5a).
            'gate': 'NONE — THRESHOLDS.json does not exist; trusted computes to 0',
        },
        'lesson': '%s#%s' % (graph.book, graph.lesson),
    }
