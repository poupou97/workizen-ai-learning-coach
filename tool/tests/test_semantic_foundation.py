#!/usr/bin/env python3
"""Lane E1 — tests for the semantic foundation (no corpus needed).

Run:  python3 -m unittest discover -s tool/tests -v
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'semantic'))

import extract as ex  # noqa: E402
import ontology as onto  # noqa: E402
import visualspec as vs  # noqa: E402
from graph import (CLAIM_STATUS, KNOWLEDGE_ORIGIN, SemanticClaim,  # noqa: E402
                   SemanticError, SemanticGraph, SemanticNode, SemanticRelation,
                   SourceGrounding, lineage_of, provenance_of)


def g(block_id='b:p001:001', trust='trustedStructuredLesson', **kw):
    kw.setdefault('page_printed', 12)
    return SourceGrounding(book='b', block_id=block_id, trust=trust, **kw)


def claim(kind='node', subject='n1', support='sourceStated', status='proposed',
          grounding=None, **kw):
    return SemanticClaim(kind=kind, subject=subject, assertion='a', support=support,
                         derivation='r-v1', grounding=grounding or [g()], status=status,
                         **kw)


class SourceGroundingTests(unittest.TestCase):
    def test_a_block_id_alone_is_not_a_grounding(self):
        # §7: sourceBlockId is what exists today and it is not enough.
        with self.assertRaises(SemanticError):
            SourceGrounding(book='b', block_id='x', trust='trustedStructuredLesson')

    def test_locator_kind_names_the_strongest_evidence_present(self):
        self.assertEqual(g().locator_kind, 'page')
        self.assertEqual(g(bbox=[0, 0, 1, 1]).locator_kind, 'page-geometry')
        self.assertEqual(g(figure_id='f1').locator_kind, 'figure-region')
        self.assertEqual(g(span=(3, 9)).locator_kind, 'text-span')

    def test_trust_must_be_a_real_ContentTrust_value(self):
        with self.assertRaises(SemanticError):
            SourceGrounding(book='b', block_id='x', page_printed=1, trust='probably-fine')

    def test_bad_spans_are_refused_not_clamped(self):
        for bad in ((5, 5), (-1, 4), (7, 3), 'nope'):
            with self.assertRaises(SemanticError):
                g(span=bad)


class SemanticClaimTests(unittest.TestCase):
    def test_a_claim_cannot_exist_without_grounding(self):
        with self.assertRaises(SemanticError):
            SemanticClaim('node', 'n', 'a', 'sourceStated', 'r-v1', grounding=[])

    def test_a_claim_cannot_exist_without_a_derivation_rule(self):
        with self.assertRaises(SemanticError):
            SemanticClaim('node', 'n', 'a', 'sourceStated', '', grounding=[g()])

    def test_support_and_status_are_separate_axes(self):
        # the §5 finding: CONFLICT / WITHHELD are statuses, not origins. If they had
        # been folded into KnowledgeOrigin this assertion could not hold.
        self.assertNotIn('conflict', KNOWLEDGE_ORIGIN)
        self.assertNotIn('withheld', KNOWLEDGE_ORIGIN)
        self.assertIn('conflict', CLAIM_STATUS)
        self.assertIn('withheld', CLAIM_STATUS)

    def test_knowledge_origin_is_reused_not_replaced(self):
        # every value lib/core/knowledge/provenance.dart:15 declares must survive here
        for v in ('sourceStated', 'sourceDemonstrated', 'sourceSequence',
                  'systemDerived', 'llmInferred'):
            self.assertIn(v, KNOWLEDGE_ORIGIN)
        # exactly one value was added
        self.assertEqual(len(KNOWLEDGE_ORIGIN), 6)
        self.assertIn('humanCurated', KNOWLEDGE_ORIGIN)

    def test_validated_requires_a_named_validator(self):
        with self.assertRaises(SemanticError):
            claim(status='validated')
        c = claim(status='validated', validator_id='timeline-order-v1')
        self.assertTrue(c.learner_visible)

    def test_a_withheld_grounded_claim_cannot_pretend_to_be_proposed(self):
        with self.assertRaises(SemanticError):
            claim(grounding=[g(trust='withheld')])
        ok = claim(grounding=[g(trust='withheld')], status='withheld')
        self.assertFalse(ok.learner_visible)

    def test_trace_is_not_evidence(self):
        # a proposed claim is a TRACE. It never reaches a learner.
        self.assertFalse(claim().learner_visible)

    def test_citable_mirrors_the_dart_rule(self):
        # provenance.dart:83 — origin in {stated, demonstrated, sequence} AND a page
        self.assertTrue(claim(support='sourceStated').citable_as_textbook_fact)
        self.assertTrue(claim(support='sourceSequence').citable_as_textbook_fact)
        self.assertFalse(claim(support='llmInferred').citable_as_textbook_fact)
        self.assertFalse(claim(support='systemDerived').citable_as_textbook_fact)
        no_page = SourceGrounding(book='b', block_id='x', bbox=[0, 0, 1, 1],
                                  trust='trustedStructuredLesson')
        self.assertFalse(claim(grounding=[no_page]).citable_as_textbook_fact)

    def test_llm_output_can_never_be_citable_whatever_its_confidence(self):
        c = claim(support='llmInferred', confidence=0.999)
        self.assertFalse(c.citable_as_textbook_fact)


class RelationGroundingTests(unittest.TestCase):
    """The heart of §5: a relation needs its own grounded claim."""

    def setUp(self):
        self.gr = SemanticGraph('b', 1, 't')
        for nid in ('a', 'b'):
            self.gr.add_node(SemanticNode(nid, 'Statement', nid,
                                          claims=[claim(subject=nid)]))

    def test_two_grounded_endpoints_do_not_make_a_grounded_edge(self):
        node_claim = claim(kind='node', subject='a')
        with self.assertRaises(SemanticError):
            SemanticRelation('causes', 'a', 'b', node_claim)

    def test_a_relation_claim_is_accepted(self):
        rc = claim(kind='relation', subject={'from': 'a', 'rel': 'causes', 'to': 'b'})
        rel = self.gr.add_relation(SemanticRelation('causes', 'a', 'b', rc))
        self.assertEqual(rel.relation, 'causes')
        self.assertIn(rc.id, self.gr.claims)

    def test_endpoints_must_exist(self):
        rc = claim(kind='relation', subject={'from': 'a', 'rel': 'causes', 'to': 'zz'})
        with self.assertRaises(SemanticError):
            self.gr.add_relation(SemanticRelation('causes', 'a', 'zz', rc))


class ProvenanceBridgeTests(unittest.TestCase):
    def test_bridge_projects_into_the_existing_provenance_shape(self):
        p = provenance_of(claim(confidence=0.8), book_series='kntt', grade=6,
                          subject='KHTN')
        for k in ('origin', 'sourceId', 'extractionMethod', 'confidence', 'bookSeries',
                  'grade', 'subject', 'pageStart', 'pageEnd', 'sourceHash'):
            self.assertIn(k, p)          # every Provenance field is filled or null
        self.assertEqual(p['sourceId'], 'b:p001:001')   # a block id, never a file path
        self.assertEqual(p['extractionMethod'], 'r-v1')
        self.assertTrue(p['citableAsTextbookFact'])

    def test_bridge_carries_both_worlds_verdicts_without_merging_them(self):
        p = provenance_of(claim())
        self.assertEqual(p['_contentTrust'], 'trustedStructuredLesson')
        self.assertEqual(p['_claimStatus'], 'proposed')

    def test_page_range_spans_every_grounding(self):
        c = claim(grounding=[g('b1', page_printed=61), g('b2', page_printed=64)])
        p = provenance_of(c)
        self.assertEqual((p['pageStart'], p['pageEnd']), (61, 64))

    def test_lineage_chain_reaches_the_source_and_says_no_gate_exists(self):
        gr = SemanticGraph('b', 17, 't')
        c = claim(span=(0, 4)) if False else claim()
        gr.add_claim(c)
        ln = lineage_of('vis#1', c, gr)
        for k in ('visualElement', 'claim', 'sourceBlocks', 'sourceRef',
                  'trustedLearningSource'):
            self.assertIn(k, ln)
        self.assertIn('THRESHOLDS.json does not exist',
                      ln['trustedLearningSource']['gate'])


class OntologyTests(unittest.TestCase):
    def test_every_family_names_only_declared_primitives_and_relations(self):
        for fam, spec in onto.FAMILIES.items():
            for p in spec['primitives']:
                self.assertIn(p, onto.PRIMITIVES, '%s -> %s' % (fam, p))
            for r in spec['relations']:
                self.assertIn(r, onto.RELATIONS, '%s -> %s' % (fam, r))

    def test_composed_things_are_not_also_primitives(self):
        for name in onto.COMPOSED_NOT_PRIMITIVE:
            self.assertNotIn(name, onto.PRIMITIVES)

    def test_bare_nam_is_not_a_timeline_cue(self):
        # "năm" also means "five"; only a year counts. This was a real false friend.
        hits = onto.cue_hits(' có năm loại chất khác nhau ', 'TIMELINE')
        self.assertEqual(hits, [])
        self.assertTrue(onto.cue_hits(' năm 1945 ', 'TIMELINE'))

    def test_cues_are_word_bounded(self):
        # "gồm" must not fire inside a longer word
        self.assertTrue(onto.cue_hits('cơ thể gồm ba phần', 'HIERARCHY'))
        self.assertEqual(onto.cue_hits('gồmgồmgồm', 'HIERARCHY'), [])

    def test_concept_map_has_no_cue_of_its_own_by_design(self):
        self.assertEqual(onto.CUES['CONCEPT_MAP'], [])


def _tsl_block(bid, role, text, page=61, order=1):
    return {'id': bid, 'page': page, 'page_printed': page - 1, 'order': order,
            'role': role, 'coarse': role.upper(), 'role_conf': 0.9, 'text': text,
            'heading_path': [], 'refers_figure': False, 'bbox': [0, 0, 1, 0.1]}


def _lesson(blocks, book='06-sgk-khoa-hoc-tu-nhien-6', lesson=17):
    return {'book': book, 'lesson': lesson, 'title': 'T', 'sourceability': 'PARTIAL',
            'blocks': blocks, 'figures': [], 'withheld': [], 'stats': {}, 'path': '-'}


class ExtractorTests(unittest.TestCase):
    def test_ordered_steps_ground_the_edge_in_the_enumerator(self):
        les = _lesson([_tsl_block('x:1', 'body', '1. Gấp giấy lọc', order=1),
                       _tsl_block('x:2', 'body', '2. Đặt phễu lên giá', order=2),
                       _tsl_block('x:3', 'body', '3. Rót từ từ hỗn hợp', order=3)])
        gr = ex.extract(les)
        nexts = [r for r in gr.relations if r.relation == 'next']
        self.assertEqual(len(nexts), 2)
        for r in nexts:
            gnd = r.claim.grounding[0]
            self.assertEqual(gnd.locator_kind, 'text-span')   # the enumerator itself
            self.assertEqual(r.claim.support, 'systemDerived')

    def test_causal_edge_is_grounded_in_the_connective_not_the_clauses(self):
        les = _lesson([_tsl_block('x:1', 'body',
                                  'Vì hạt bụi nặng hơn không khí nên chúng lắng xuống đáy')])
        gr = ex.extract(les)
        causes = [r for r in gr.relations if r.relation == 'causes']
        self.assertEqual(len(causes), 1)
        q = causes[0].claim.grounding[0].quote
        self.assertIn('nên', q)

    def test_no_causal_edge_without_a_connective(self):
        les = _lesson([_tsl_block('x:1', 'body', 'Hạt bụi nặng hơn không khí.'),
                       _tsl_block('x:2', 'body', 'Chúng lắng xuống đáy.', order=2)])
        gr = ex.extract(les)
        self.assertEqual([r for r in gr.relations if r.relation == 'causes'], [])

    def test_dated_events_handle_a_bare_year_and_a_hyphenated_name(self):
        # regression: the first version missed "(248)" and "Lý Bí - Triệu Quang Phục",
        # found by comparing against Lane C's hand-checked 7/7 on LS&DL 5 Bai 8.
        les = _lesson([_tsl_block('h:1', 'body',
                                  'Hai Bà Trưng (40 - 43), Bà Triệu (248), '
                                  'Lý Bí - Triệu Quang Phục (542 - 602).')],
                      book='05-sgk-lich-su-va-dia-li-5', lesson=8)
        gr = ex.extract(les)
        events = [n for n in gr.nodes.values() if n.primitive == 'Event']
        self.assertGreaterEqual(len(events), 3)
        for e in events:
            self.assertEqual(e.claims[0].grounding[0].locator_kind, 'text-span')

    def test_event_titles_never_start_mid_word(self):
        # regression, Vietnamese-specific: `[A-ZÀ-Ỹ]` is a RANGE covering the lowercase
        # accented letters too, so the first version emitted 'ăm' (from "năm") and
        # 'ủa Ngô Quyền' (from "của") as event names. They read like real names.
        les = _lesson([_tsl_block('h:1', 'body',
                                  'Diễn ra năm 938. Chiến thắng của Ngô Quyền (938) '
                                  'đã kết thúc thời kì Bắc thuộc.')],
                      book='05-sgk-lich-su-va-dia-li-5', lesson=8)
        titles = [n.label for n in ex.extract(les).nodes.values()
                  if n.primitive == 'Event']
        self.assertEqual(titles, ['Ngô Quyền'])
        for t in titles:
            self.assertTrue(t[0].isupper(), t)

    def test_upper_class_excludes_lowercase_vietnamese(self):
        for lower in 'ăâđêôơưáàảãạủứựỳ':
            self.assertNotIn(lower, ex.UPPER)
        for upper in 'ĂÂĐÊÔƠƯÁÀẢÃẠỦỨỰỲ':
            self.assertIn(upper, ex.UPPER)

    def test_a_parenthesis_that_is_not_a_date_is_not_an_event(self):
        les = _lesson([_tsl_block('h:1', 'body',
                                  'Quan sát Hình 2 (trang 41) rồi trả lời.')])
        self.assertEqual([n for n in ex.extract(les).nodes.values()
                          if n.primitive == 'Event'], [])

    def test_extractor_never_branches_on_subject(self):
        with open(os.path.join(HERE, '..', 'semantic', 'extract.py'),
                  encoding='utf-8') as fh:
            src = fh.read()
        for banned in ('subject ==', "subject in (", 'if book ==', 'khtn', 'lich_su'):
            self.assertNotIn(banned, src.lower().replace('subject=subject', ''))

    def test_a_failing_rule_does_not_take_the_lesson_down(self):
        les = _lesson([_tsl_block('x:1', 'body', None)])   # text is None
        gr = ex.extract(les)                               # must not raise
        self.assertIsInstance(gr.summary()['nodes'], int)


class VisualSpecTests(unittest.TestCase):
    def _process_graph(self):
        les = _lesson([_tsl_block('x:%d' % i, 'body', '%d. bước %d' % (i, i), order=i)
                       for i in (1, 2, 3)])
        return ex.extract(les)

    def test_every_drawable_element_names_its_claim(self):
        spec = vs.compile_process(self._process_graph())
        self.assertIsNotNone(spec)
        for el in spec.drawable:
            self.assertTrue(el.claim_id)
            self.assertIn(el.claim_id, spec.graph.claims)

    def test_a_spec_always_declares_the_experimental_chip(self):
        spec = vs.compile_process(self._process_graph())
        t = spec.trust_block()
        self.assertTrue(t['chipRequired'])
        self.assertEqual(t['contentTrustCeiling'], 'trustedStructuredLesson')
        self.assertFalse(t['allElementsValidated'])

    def test_lineage_is_emitted_for_every_element(self):
        spec = vs.compile_process(self._process_graph())
        j = spec.to_json()
        self.assertEqual(len(j['lineage']), len(spec.elements))
        self.assertTrue(all(l['sourceBlocks'] for l in j['lineage']))

    def test_compilers_read_only_graph_fields(self):
        # §10: if a compiler needed a family-specific field, the "compiled projection"
        # hypothesis would be false. This asserts the measurement, not the prose.
        gr = self._process_graph()
        vs.compile_all(gr)
        allowed = {'nodes', 'relations', 'claims'}
        for compiler, fields in vs.compiler_audit().items():
            self.assertTrue(set(fields) <= allowed, '%s read %s' % (compiler, fields))

    def test_multiple_procedures_are_kept_as_groups_not_dropped(self):
        les = _lesson([_tsl_block('x:1', 'body', '1. a', order=1),
                       _tsl_block('x:2', 'body', '2. b', order=2),
                       _tsl_block('x:h', 'heading', 'II Phần hai', order=3),
                       _tsl_block('x:3', 'body', '1. c', order=4),
                       _tsl_block('x:4', 'body', '2. d', order=5)])
        spec = vs.compile_process(ex.extract(les))
        groups = {el.slot.get('group') for el in spec.drawable}
        self.assertGreaterEqual(len(groups), 2)

    def test_a_bad_element_role_is_refused(self):
        with self.assertRaises(ValueError):
            vs.VisualElement('e', 'sparkle', 't', 'c', 'proposed')

    def test_only_a_gap_may_omit_its_claim(self):
        with self.assertRaises(ValueError):
            vs.VisualElement('e', 'node', 't', None, 'proposed')
        vs.VisualElement('e', 'gap', None, None, 'withheld')   # allowed


if __name__ == '__main__':
    unittest.main()
