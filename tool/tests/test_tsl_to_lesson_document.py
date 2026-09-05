#!/usr/bin/env python3
"""Round 3 · A1 — tests for the TSL → LessonDocument bridge (tool/corpus/tsl_to_lesson_document.py).

Synthetic TSL only: every text is a clearly fake «[MẪU]» string — no verbatim SGK text enters the repo
(Founder D4). The real Bài 17 conversion is exercised in `test_real_tsl_if_present` which skips on a
clean clone (the corpus never enters git).

Run:  python3 -m unittest discover -s tool/tests -v"""
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tsl_to_lesson_document as br  # noqa: E402

BOOK = '06-sgk-mau-6'


def prov(page, printed, bbox, bid, sim=100.0):
    return {'book': BOOK, 'page_pdf': page, 'page_printed': printed, 'bbox': bbox, 'extraction': 'docling-x+ocrmac',
            'ocr_conf': 0.98, 'text_sim': sim, 'pipeline': 'tc2-p1', 'sdm_version': 'sdm-v2', 'block_id': bid}


def blk(n, page, printed, order, role, text, y, heading_path=(), enum=False, refers=False, method='lexicon', conf=0.9, **extra):
    bid = f'{BOOK}:p{page:03d}:tc2-p1:{n:03d}'
    b = {'id': bid, 'page': page, 'page_printed': printed, 'order': order,
         'role': {'value': role, 'coarse': role.upper(), 'confidence': conf, 'method': method},
         'text': text, 'bbox': [0.1, y, 0.7, 0.03], 'heading_path': list(heading_path), 'refers_figure': refers,
         'enumerator_restored': enum, 'provenance': prov(page, printed, [0.1, y, 0.7, 0.03], bid)}
    b.update(extra)
    return b


def withheld(n, page, printed, order, role, reasons, y, status='WITHHELD'):
    bid = f'{BOOK}:p{page:03d}:tc2-p1:{n:03d}'
    return {'id': bid, 'page': page, 'page_printed': printed, 'order': order, 'role': role, 'bbox': [0.6, y, 0.3, 0.02],
            'reasons': reasons, 'status': status, 'text_len': 16, 'provenance': prov(page, printed, [0.6, y, 0.3, 0.02], bid), 'text': None}


def make_tsl():
    hp = ('Bài 9', '[MẪU] BÀI MẪU')
    blocks = [
        blk(1, 11, 10, 1, 'heading', 'Bài 9', 0.05, ('Bài 9',)),
        blk(2, 11, 10, 2, 'heading', '[MẪU] BÀI MẪU', 0.08, hp),
        blk(3, 11, 10, 3, 'stage_label', 'MỤC TIÊU', 0.12, hp),
        blk(4, 11, 10, 4, 'objective', '· [MẪU] Nêu được một điều mẫu.', 0.15, hp),
        blk(5, 11, 10, 5, 'question', '[MẪU] Câu hỏi mẫu số 1?', 0.20, hp),
        blk(6, 11, 10, 6, 'instruction', 'Tiến hành:', 0.25, hp + ('[MẪU] Thí nghiệm mẫu',)),
        blk(7, 11, 10, 7, 'body', '1. [MẪU] Bước mẫu thứ nhất.', 0.28, hp, enum=True),
        blk(8, 11, 10, 9, 'body', '2. [MẪU] Bước mẫu thứ hai.', 0.34, hp, enum=True),
        blk(9, 11, 10, 10, 'caption', '[MẪU] Chú thích hình mẫu', 0.47, hp, method='native'),   # below the figure (y 0.36–0.46)
        blk(10, 11, 10, 11, 'sidebar', '[MẪU] Ghi chú lề mẫu', 0.50, hp, method='geometry'),
        blk(11, 12, 11, 1, 'footnote', '[MẪU] Chú thích chân trang mẫu', 0.90, hp),           # role the model lacks
        blk(12, 12, 11, 2, 'table', '[MẪU] bảng', 0.50, hp),                                    # table without cells
        blk(13, 12, 11, 3, 'stage_label', 'Em đã học', 0.60, hp),
        blk(14, 12, 11, 4, 'body', '· [MẪU] Cách A (tách mẫu A).', 0.63, hp, enum=True),
        blk(15, 12, 11, 5, 'body', '· [MẪU] Cách B (tách mẫu B).', 0.66, hp, enum=True),
    ]
    wh = [withheld(20, 11, 10, 8, 'body', ['page_feature:diagram'], 0.31),
          withheld(21, 12, 11, 6, 'sidebar', ['math_guard', 'agree_text'], 0.70, status='CONFLICT')]
    figs = [{'id': f'{BOOK}:p011:fig00', 'page': 11, 'bbox': [0.1, 0.36, 0.4, 0.1], 'caption': f'{BOOK}:p011:tc2-p1:009', 'labels': 2},
            {'id': f'{BOOK}:p011:fig01', 'page': 11, 'bbox': [0.5, 0.36, 0.05, 0.05], 'caption': None, 'labels': 0}]   # too small ⇒ dropped
    return {'book': BOOK, 'lesson': 9, 'title': '[MẪU] BÀI MẪU', 'pipeline': 'tc2-p1', 'docType': 'SGK',
            'boundary': {'page_start': 11, 'page_end': 12, 'pages': [11, 12], 'attach_methods': {'header': 1, 'continuation': 1},
                         'confidence': 0.95, 'header_found': True, 'header_page': 11, 'source': 'both'},
            'sourceability': 'PARTIAL', 'answer_keys_included': False,
            'stats': {'learning_blocks': 17, 'trusted': 15, 'withheld': 2},
            'blocks': blocks, 'withheld': wh, 'figures': figs}


CROPS = {f'{BOOK}:p011:fig00': {'crop': 'crops/fig00.png', 'aspect': 1.5},
         f'{BOOK}:p011:tc2-p1:020': {'crop': 'crops/w20.png', 'aspect': None}}


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tsl = make_tsl()
        self.doc = br.convert(self.tsl, tsl_rel_path='x/bai-9.tsl.json', tsl_sha256='ab' * 32, book_meta={'subject': 'KHTN', 'grade': 6},
                              chapters=[{'label': 'Chương II', 'title': '[MẪU]', 'lessonNos': [8, 9], 'trust': br.TRUST_OUTSIDE_GATE, 'derivation': 'toc-ocr-chapters-v1'}],
                              crops=CROPS)

    def by_id(self):
        return {b['id']: b for b in self.doc['blocks']}

    def test_every_tsl_block_survives_with_full_provenance(self):
        ids = self.by_id()
        for b in self.tsl['blocks'] + self.tsl['withheld']:
            self.assertIn(b['id'], ids, b['id'])
            out = ids[b['id']]
            ref = out['sourceRef']
            self.assertEqual((ref['book'], ref['pagePdf'], ref['pagePrinted'], ref['bbox'], ref['blockId']),
                             (BOOK, b['page'], b['page_printed'], b['bbox'], b['id']))
            self.assertEqual((ref['extraction'], ref['ocrConf'], ref['pipeline'], ref['agreementScore']), ('docling-x+ocrmac', 0.98, 'tc2-p1', 1.0))
            self.assertEqual(out['relations']['order'], b['order'])
        # role + relations preserved verbatim on text blocks
        for b in self.tsl['blocks']:
            out = ids[b['id']]
            self.assertEqual(out['sourceRole'], b['role']['value'])
            if out['type'] != 'withheld':
                self.assertEqual(out['relations']['headingPath'], b['heading_path'])
                self.assertEqual(out['relations']['enumeratorRestored'], b['enumerator_restored'])
                self.assertEqual(out['roleMethod'], b['role']['method'])
                self.assertEqual(out['roleConfidence'], b['role']['confidence'])
        self.assertEqual(ids[f'{BOOK}:p011:tc2-p1:009']['relations']['captionOf'], f'{BOOK}:p011:fig00')

    def test_text_is_verbatim_and_trust_mapping(self):
        ids = self.by_id()
        for b in self.tsl['blocks']:
            out = ids[b['id']]
            if out['type'] != 'withheld':
                self.assertEqual(out['text'], b['text'])
                self.assertEqual(out['trust'], 'trustedStructuredLesson')
        types = {out['type'] for out in ids.values()}
        self.assertEqual(types, {'heading', 'activity', 'question', 'paragraph', 'caption', 'withheld', 'image', 'sourceRef'})
        kinds = {ids[f'{BOOK}:p011:tc2-p1:00{n}']['kind'] for n in (3, 4, 6)} | {ids[f'{BOOK}:p011:tc2-p1:010']['kind']}
        self.assertEqual(kinds, {'stageLabel', 'objective', 'instruction', 'sidebar'})

    def test_withheld_is_fail_closed(self):
        ids = self.by_id()
        wh = [b for b in self.doc['blocks'] if b['type'] == 'withheld']
        # 2 TSL withheld + footnote (unknown role) + table without cells
        self.assertEqual(len(wh), len(self.tsl['withheld']) + 2)
        self.assertEqual(self.doc['provenance']['blockCounts']['unknownRoleWithheld'], 2)
        for b in wh:
            self.assertNotIn('text', b)
            self.assertEqual(b['trust'], 'withheld')
            self.assertTrue(b['reasons'])
            self.assertEqual(b['reason'], ','.join(b['reasons']))
        self.assertEqual(ids[f'{BOOK}:p011:tc2-p1:020']['reasons'], ['page_feature:diagram'])
        self.assertEqual(ids[f'{BOOK}:p011:tc2-p1:020']['crop'], 'crops/w20.png')
        self.assertEqual(ids[f'{BOOK}:p012:tc2-p1:021']['status'], 'CONFLICT')
        self.assertEqual(ids[f'{BOOK}:p012:tc2-p1:021']['reasons'], ['math_guard', 'agree_text'])
        self.assertEqual(ids[f'{BOOK}:p012:tc2-p1:011']['reasons'], ['unknown_role:footnote'])
        self.assertEqual(ids[f'{BOOK}:p012:tc2-p1:012']['reasons'], ['table_without_cells'])
        # no withheld text anywhere in the serialised document
        dumped = json.dumps(self.doc, ensure_ascii=False)
        self.assertNotIn('Chú thích chân trang', dumped)
        for b in self.doc['blocks']:
            self.assertEqual(b['type'] == 'withheld', b['trust'] == 'withheld')

    def test_lesson_identity_boundary_licence_and_counts(self):
        d = self.doc
        self.assertEqual((d['book'], d['lesson'], d['title'], d['schema']), (BOOK, 9, '[MẪU] BÀI MẪU', 'wal-lesson-fixture-v1'))
        self.assertEqual(d['licence'], 'internalResearchOnly')
        self.assertEqual(d['evidencePolicy'], 'none')
        p = d['provenance']
        self.assertEqual(p['trust'], 'trustedStructuredLesson')
        self.assertEqual(p['boundary'], {'pageStart': 11, 'pageEnd': 12, 'confidence': 0.95, 'headerFound': True, 'source': 'both',
                                         'attachMethods': {'header': 1, 'continuation': 1}})
        self.assertEqual(p['pipelineVersion'], 'tc2-p1/sdm-v2')
        self.assertEqual(p['auditStatus'], 'notAudited')
        self.assertEqual(p['sourceHash'], 'ab' * 32)
        self.assertFalse(p['answerKeysIncluded'])
        self.assertIn('D4', p['distribution'])
        # 13 text blocks + 1 image + 1 provenance line; 2 TSL withheld + footnote + cell-less table
        self.assertEqual(p['blockCounts']['byTrust'], {'trustedStructuredLesson': 15, 'withheld': 4})
        self.assertEqual(p['blockCounts']['imagesKept'], 1)
        self.assertEqual(d['chapter']['label'], 'Chương II')
        self.assertEqual(d['chapter']['trust'], 'fixtureFromTrustedCorpus')       # naive-OCR TOC is outside the TC gate
        self.assertNotIn('tutorScript', d)                                          # no invented script for another lesson

    def test_semantic_derivation_references_real_blocks(self):
        sem = {s['type']: s for s in self.doc['semantic']}
        self.assertEqual(set(sem), {'process', 'comparison'})
        steps = sem['process']['steps']
        self.assertEqual([s.get('text') for s in steps], ['1. [MẪU] Bước mẫu thứ nhất.', None, '2. [MẪU] Bước mẫu thứ hai.'])
        self.assertEqual(steps[1]['withheldReason'], 'page_feature:diagram')
        ids = self.by_id()
        for s in steps:
            self.assertIn(s['sourceBlockId'], ids)
        self.assertEqual([e['name'] for e in sem['comparison']['entities']], ['[MẪU] Cách A', '[MẪU] Cách B'])
        self.assertEqual(sem['comparison']['dimensions'][0]['values'], ['tách mẫu A', 'tách mẫu B'])
        self.assertEqual(sem['process']['trust'], 'trustedStructuredLesson')

    def test_reading_order_and_figure_placement(self):
        order = [b['id'] for b in self.doc['blocks']]
        fig = order.index(f'{BOOK}:p011:fig00')
        cap = order.index(f'{BOOK}:p011:tc2-p1:009')
        step2 = order.index(f'{BOOK}:p011:tc2-p1:008')
        self.assertLess(step2, fig); self.assertLess(fig, cap)          # figure (y 0.36–0.46, centre 0.41) sits before its caption (y 0.47)
        self.assertNotIn(f'{BOOK}:p011:fig01', order)                     # too small ⇒ not an image block
        self.assertEqual(order[-1], f'{BOOK}:b9:sourceRef')

    def test_deterministic(self):
        again = br.convert(make_tsl(), tsl_rel_path='x/bai-9.tsl.json', tsl_sha256='ab' * 32, book_meta={'subject': 'KHTN', 'grade': 6},
                           chapters=[{'label': 'Chương II', 'title': '[MẪU]', 'lessonNos': [8, 9], 'trust': br.TRUST_OUTSIDE_GATE, 'derivation': 'toc-ocr-chapters-v1'}],
                           crops=CROPS)
        self.assertEqual(json.dumps(self.doc, ensure_ascii=False, indent=1), json.dumps(again, ensure_ascii=False, indent=1))
        self.assertEqual(br.document_hash(self.doc), br.document_hash(again))
        self.assertNotIn('generatedAt', json.dumps(self.doc))

    def test_refusals(self):
        t = make_tsl(); t['docType'] = 'SGV'
        with self.assertRaises(br.BridgeRefusal):
            br.convert(t)
        t = make_tsl(); t['answer_keys_included'] = True
        with self.assertRaises(br.BridgeRefusal):
            br.convert(t)
        t = make_tsl(); t['withheld'][0]['text'] = '[MẪU] chữ lậu'
        with self.assertRaises(br.BridgeRefusal):
            br.convert(t)
        t = make_tsl(); t['blocks'][0]['text'] = None
        with self.assertRaises(br.BridgeRefusal):
            br.convert(t)
        t = make_tsl(); t['blocks'].append(copy.deepcopy(t['blocks'][0]))
        with self.assertRaises(br.BridgeRefusal):
            br.convert(t)
        with self.assertRaises(br.BridgeRefusal):
            br.convert(make_tsl(), audit_status='passed')

    def test_no_crops_means_no_image_blocks_but_all_text_and_withheld_survive(self):
        d = br.convert(make_tsl())
        self.assertEqual(d['provenance']['blockCounts'], {'byTrust': {'trustedStructuredLesson': 14, 'withheld': 4}, 'tslTrusted': 15, 'tslWithheld': 2,
                                                          'unknownRoleWithheld': 2, 'imagesKept': 0, 'imagesWithoutCrop': 1, 'figuresInTsl': 2})
        self.assertIsNone(d['chapter']); self.assertEqual(d['chapters'], [])

    def test_real_tsl_if_present(self):
        p = os.path.join(br.ROOT, 'poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json')
        if not os.path.exists(p):
            self.skipTest('Bài 17 TSL not on this machine (corpus never enters git)')
        tsl = json.load(open(p))
        d = br.convert(tsl, tsl_sha256=br.sha256_file(p), book_meta={'subject': 'KHTN', 'grade': 6})
        self.assertEqual(d['provenance']['blockCounts']['tslWithheld'], 4)
        self.assertEqual(sum(1 for b in d['blocks'] if b['type'] == 'withheld'), 4)
        self.assertEqual(d['provenance']['blockCounts']['unknownRoleWithheld'], 0)
        self.assertIn('tutorScript', d)
        self.assertEqual(br.document_hash(d), br.document_hash(br.convert(tsl, tsl_sha256=br.sha256_file(p), book_meta={'subject': 'KHTN', 'grade': 6})))


if __name__ == '__main__':
    unittest.main()
