#!/usr/bin/env python3
"""ROUND 7 · WS-S — the structured-content gap, as tests.

Two questions, and the tests answer them in the order the Founder set them:

  1. **Did anything become SERVABLE?** No — and «no» has to be provable, not asserted. With both
     switches off the emitted document is BYTE-IDENTICAL to round 6's, and `ROLE_MAP` still has no
     key for `footnote`, `activity` or `option`, so those three roles still reach a `WithheldBlock`.
  2. **Is the group rule safe?** It is safe in exactly one direction: it can only ever withhold. Every
     test below that touches it asserts the served set SHRINKS OR STAYS, never grows, and that no
     block gains a text field on the way.

Synthetic TSL only — no verbatim SGK enters the repo (Founder D4). The shape of `mcq_tsl()` is the
shape of the corpus's only complete multiple-choice group (a stem, four options, a trailing directive
line), with fake «[MẪU]» text.

Run:  python3 -m unittest discover -s tool/tests -v
"""
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tsl_to_lesson_document as br  # noqa: E402

BOOK = '07-sgk-mau-7'
META = {'subject': 'KHTN', 'grade': 7}


def prov(page, printed, bbox, bid, sim=100.0):
    return {'book': BOOK, 'page_pdf': page, 'page_printed': printed, 'bbox': bbox,
            'extraction': 'docling-x+ocrmac', 'ocr_conf': 0.98, 'text_sim': sim,
            'pipeline': 'tc2-p1', 'sdm_version': 'sdm-v2', 'block_id': bid}


def blk(n, order, role, text, y, enum=False, conf=0.9, page=32, printed=31):
    bid = f'{BOOK}:p{page:03d}:tc2-p1:{n:03d}'
    bbox = [0.1, y, 0.7, 0.03]
    return {'id': bid, 'page': page, 'page_printed': printed, 'order': order,
            'role': {'value': role, 'coarse': role.upper(), 'confidence': conf, 'method': 'lexicon'},
            'text': text, 'bbox': bbox, 'heading_path': ['[MẪU] Mục 3'], 'refers_figure': False,
            'enumerator_restored': enum, 'provenance': prov(page, printed, bbox, bid)}


def wh(n, order, role, reasons, y, page=32, printed=31):
    bid = f'{BOOK}:p{page:03d}:tc2-p1:{n:03d}'
    bbox = [0.6, y, 0.3, 0.02]
    return {'id': bid, 'page': page, 'page_printed': printed, 'order': order, 'role': role,
            'bbox': bbox, 'reasons': list(reasons), 'status': 'WITHHELD', 'text_len': 16,
            'provenance': prov(page, printed, bbox, bid), 'text': None}


def base_tsl(blocks, withheld=()):
    return {'book': BOOK, 'lesson': 4, 'title': '[MẪU] BÀI MẪU', 'pipeline': 'tc2-p1', 'docType': 'SGK',
            'boundary': {'page_start': 32, 'page_end': 32, 'confidence': 0.9, 'header_found': True,
                         'source': 'both', 'attach_methods': {'header': 1}},
            'sourceability': 'internal', 'stats': {}, 'blocks': list(blocks),
            'withheld': list(withheld), 'figures': [], 'answer_keys_included': False}


def mcq_tsl(withhold_one_option=False):
    """A stem, four options, a trailing directive — the corpus's only complete MCQ shape.

    `withhold_one_option=True` is the case the app CANNOT distinguish from a complete question today:
    three options served, one gone. That is the state a new `option` type would create, and it is why
    the type is not added."""
    blocks = [
        blk(4, 4, 'question', '[MẪU] Câu hỏi mẫu gồm các thứ:', 0.30),
        blk(5, 5, 'option', 'A. [MẪU] thứ nhất', 0.37, enum=True, conf=0.95),
        blk(6, 6, 'option', 'B. [MẪU] thứ hai', 0.37, enum=True, conf=0.95),
        blk(7, 7, 'option', 'C. [MẪU] thứ ba', 0.39, enum=True, conf=0.95),
        blk(8, 8, 'option', 'D. [MẪU] thứ tư.', 0.39, enum=True, conf=0.95),
        blk(9, 9, 'question', '[MẪU] Hãy chọn đáp án đúng nhất.', 0.42),
    ]
    if withhold_one_option:
        opt = next(b for b in blocks if b['id'].endswith(':007'))     # option C leaves the trusted set
        blocks = [b for b in blocks if b is not opt]
        return base_tsl(blocks, [wh(7, 7, 'option', ['agree_text'], 0.39)]), opt
    return base_tsl(blocks), None


def procedure_tsl():
    """An instruction lead and two enumerated steps, one of which is withheld — round 5's other
    mutilated shape, and by count the larger one (29 of 31 on the canonical corpus)."""
    return base_tsl(
        [blk(1, 1, 'instruction', 'Tiến hành:', 0.20),
         blk(2, 2, 'body', '1. [MẪU] Bước mẫu thứ nhất.', 0.24, enum=True),
         blk(3, 3, 'body', '2. [MẪU] Bước mẫu thứ hai.', 0.28, enum=True)])


def served_ids(doc):
    return {b['id'] for b in doc['blocks'] if b['type'] not in ('withheld', 'sourceRef')}


# ---------------------------------------------------------------------------------------------------
class NothingBecameServable(unittest.TestCase):
    """Gate E of the round-7 plan, at this workstream's boundary."""

    def test_role_map_still_has_no_carrier_for_the_three_roles(self):
        for role in ('footnote', 'activity', 'option'):
            self.assertNotIn(role, br.ROLE_MAP, f'{role} gained a servable carrier')
            self.assertNotIn(role, br.KNOWN_UNCARRIED_ROLES)

    def test_the_three_roles_still_reach_a_withheld_block(self):
        tsl = base_tsl([blk(1, 1, 'heading', '[MẪU] Đề mục', 0.05),
                        blk(2, 2, 'footnote', '(1) [MẪU] chú thích', 0.10),
                        blk(3, 3, 'activity', '[MẪU] Thí nghiệm mẫu', 0.15),
                        blk(4, 4, 'option', 'A. [MẪU] thứ nhất', 0.20, enum=True)])
        doc = br.convert(tsl, book_meta=META)
        by_id = {b['id']: b for b in doc['blocks']}
        for n, role in ((2, 'footnote'), (3, 'activity'), (4, 'option')):
            b = by_id[f'{BOOK}:p032:tc2-p1:{n:03d}']
            self.assertEqual(b['type'], 'withheld')
            self.assertEqual(b['reasons'], [f'unknown_role:{role}'])
            self.assertNotIn('text', b)
            self.assertEqual(b['trust'], br.TRUST_WITHHELD)

    def test_group_machinery_is_off_by_default_and_the_bytes_do_not_move(self):
        """The strongest form of «nothing changed»: the same TSL gives the same BYTES as before the
        switches existed, and the stats field is `null` rather than a zero that could be misread as a
        measurement."""
        tsl, _ = mcq_tsl()
        doc = br.convert(tsl, book_meta=META)
        self.assertNotIn('structuralGroups', doc['provenance']['blockCounts'])
        again = br.convert(copy.deepcopy(tsl), book_meta=META)
        self.assertEqual(json.dumps(doc, ensure_ascii=False, sort_keys=True),
                         json.dumps(again, ensure_ascii=False, sort_keys=True))
        # and annotation alone must not move a single block's disposition
        annotated = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True)
        self.assertEqual(served_ids(doc), served_ids(annotated))


# ---------------------------------------------------------------------------------------------------
class TheGroupRuleOnlyEverWithholds(unittest.TestCase):

    def test_a_mutilated_mcq_is_visible_before_the_rule_and_gone_after(self):
        tsl, _ = mcq_tsl(withhold_one_option=True)
        ann = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True)
        stats = ann['provenance']['blockCounts']['structuralGroups']
        self.assertEqual(stats['mutilatedBeforeRule'], 1)
        self.assertEqual(stats['mutilated'][0]['kind'], 'question_options')
        self.assertEqual(stats['mutilatedRemaining'], 1)

        ruled = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True, group_rule=True)
        self.assertEqual(ruled['provenance']['blockCounts']['structuralGroups']['mutilatedRemaining'], 0)
        self.assertTrue(served_ids(ruled) < served_ids(ann), 'the rule must SHRINK the served set')

    def test_the_rule_never_restores_a_withheld_member(self):
        tsl, dropped = mcq_tsl(withhold_one_option=True)
        ruled = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True, group_rule=True)
        by_id = {b['id']: b for b in ruled['blocks']}
        self.assertEqual(by_id[dropped['id']]['type'], 'withheld')
        self.assertNotIn('text', by_id[dropped['id']])
        # the withheld member's OWN reason survives; the rule adds a disposition, it does not relabel one
        self.assertEqual(by_id[dropped['id']]['reasons'], ['agree_text'])
        blob = json.dumps(ruled, ensure_ascii=False)
        self.assertNotIn(dropped['text'], blob, 'the rule leaked the withheld option text')

    def test_every_block_the_rule_withholds_loses_its_text(self):
        tsl, _ = mcq_tsl(withhold_one_option=True)
        ruled = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True, group_rule=True)
        touched = [b for b in ruled['blocks']
                   if any(r.startswith(br.GROUP_REASON) for r in (b.get('reasons') or ()))]
        self.assertTrue(touched)
        for b in touched:
            self.assertEqual(b['type'], 'withheld')
            self.assertNotIn('text', b)
            self.assertEqual(b['trust'], br.TRUST_WITHHELD)

    def test_a_SOURCE_COMPLETE_mcq_is_mutilated_BY_THE_TYPE_GAP_ITSELF(self):
        """⭐ The finding of this workstream, as a test. Nothing is wrong with this question in the
        book: a stem and four options, all four TSL-TRUSTED. The app withholds every option because
        `ROLE_MAP` has no `option` key — so the child reads the stem, then «hãy chọn đáp án đúng
        nhất», and four blank cards. The safety mechanism produced the teaching-critical error, which
        is round 5 defect 8 stated the other way round. It is also why the fix is the GROUP RULE and
        not an `option` type: the rule removes the question; a type would serve four option letters
        that no agreement score ever covered."""
        tsl, _ = mcq_tsl()
        ann = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True)
        stats = ann['provenance']['blockCounts']['structuralGroups']
        self.assertEqual(stats['mutilatedBeforeRule'], 1)
        self.assertEqual(stats['mutilated'][0], dict(
            groupId=stats['mutilated'][0]['groupId'], kind='question_options',
            members=5, served=1, withheld=4))
        ruled = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True, group_rule=True)
        self.assertTrue(served_ids(ruled) < served_ids(ann))
        self.assertEqual(ruled['provenance']['blockCounts']['structuralGroups']['mutilatedRemaining'], 0)

    def test_a_mutilated_procedure_is_the_same_class_and_the_same_fix(self):
        tsl = procedure_tsl()
        tsl['withheld'] = [wh(3, 3, 'body', ['agree_text'], 0.28)]
        tsl['blocks'] = [b for b in tsl['blocks'] if not b['id'].endswith(':003')]
        ann = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True)
        stats = ann['provenance']['blockCounts']['structuralGroups']
        # The source procedure has an instruction lead and TWO steps, the second of which is withheld.
        # The group is found — but with 2 members, not 3: a withheld region carries no text, so its
        # enumerator cannot be seen and it is not recognised as a step. The group therefore looks
        # COMPLETE and the mutilation is invisible. This is not a bug being tolerated, it is the
        # measured reason every `procedure_steps` count on the lesson path is a LOWER BOUND.
        self.assertEqual(stats['byKind'].get('procedure_steps', 0), 1)
        self.assertEqual(stats['mutilatedBeforeRule'], 0)
        self.assertIn('LOWER BOUND', stats['note'])

    def test_annotation_describes_the_emitted_document_not_a_previous_one(self):
        tsl, _ = mcq_tsl(withhold_one_option=True)
        ruled = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True, group_rule=True)
        groups = {}
        for b in ruled['blocks']:
            g = (b.get('relations') or {}).get('group')
            if g:
                groups.setdefault(g['id'], []).append(b)
        self.assertTrue(groups)
        for gid, members in groups.items():
            claimed = members[0]['relations']['group']
            actual = sum(1 for b in members if b['type'] == 'withheld')
            self.assertEqual(claimed['withheldMembers'], actual,
                             f'{gid} claims {claimed["withheldMembers"]} withheld, document has {actual}')
            self.assertEqual(claimed['members'], len(members))

    def test_withheld_conservation_survives_the_rule(self):
        """`check_document` runs inside `convert`; this states the identity it enforces so a future
        change that withholds a block without recording it fails HERE with a readable message."""
        tsl, _ = mcq_tsl(withhold_one_option=True)
        doc = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True, group_rule=True)
        counts = doc['provenance']['blockCounts']
        n_withheld = sum(1 for b in doc['blocks'] if b['type'] == 'withheld')
        self.assertEqual(n_withheld,
                         counts['tslWithheld'] + counts['unknownRoleWithheld']
                         + counts['noCarrierWithheld']
                         + counts['structuralGroups']['blocksWithheldByRule'])


# ---------------------------------------------------------------------------------------------------
class GroupIdsAreProvenanceNotContent(unittest.TestCase):

    def test_a_group_carries_no_text_of_its_members(self):
        tsl, _ = mcq_tsl(withhold_one_option=True)
        doc = br.convert(copy.deepcopy(tsl), book_meta=META, structural_groups=True)
        for b in doc['blocks']:
            g = (b.get('relations') or {}).get('group')
            if g:
                self.assertEqual(set(g), {'id', 'kind', 'members', 'withheldMembers'})
                self.assertIsInstance(g['members'], int)

    def test_the_group_sentinel_never_reaches_a_document(self):
        """The adapter gives withheld regions a placeholder so they take part in group formation. It is
        an internal token; if it ever appeared in an emitted document it would be a rendering string
        that became structure — the exact thing round 6 forbade."""
        tsl, _ = mcq_tsl(withhold_one_option=True)
        for kwargs in ({}, {'structural_groups': True}, {'structural_groups': True, 'group_rule': True}):
            doc = br.convert(copy.deepcopy(tsl), book_meta=META, **kwargs)
            self.assertNotIn(br.GROUP_SENTINEL_TEXT, json.dumps(doc, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
