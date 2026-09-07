#!/usr/bin/env python3
"""WAL-228 — kịch bản SAM là DỮ LIỆU, không còn là một nhánh mã.

Chạy:  python3 -m unittest discover -s tool/tests -v

Trước đây `tsl_to_lesson_document.py` mở đầu phần kịch bản bằng

    if tsl['book'] != '06-sgk-khoa-hoc-tu-nhien-6' or tsl['lesson'] != 17:
        return None

nên Đọc và Trực quan chạy cho mọi bài có TSL, còn «Học với SAM» thì không —
không phải vì thiếu dữ liệu, mà vì một câu `if`.

Bốn tính chất phải giữ, mỗi cái một test:
  1. bài có tệp kịch bản ⇒ dựng được; bài không có ⇒ None (không nổ)
  2. chỗ trống được điền bằng ID THẬT và CHỮ NGUYÊN VĂN của block
  3. thiếu block ⇒ KHÔNG sinh (fail closed) — không bịa thay
  4. còn chỗ trống chưa điền ⇒ KHÔNG sinh — thà không có còn hơn lời cụt
"""
import glob
import json
import os
import re
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tsl_to_lesson_document as bridge  # noqa: E402

BOOK = '06-sgk-khoa-hoc-tu-nhien-6'


def _tsl(book=BOOK, lesson=17):
    return {'book': book, 'lesson': lesson, 'blocks': []}


def _by_id():
    return {
        f'{BOOK}:p061:tc2-p1:016': {'id': f'{BOOK}:p061:tc2-p1:016', 'text': 'LỜI NGUYÊN TẮC'},
        f'{BOOK}:p063:tc2-p1:011': {'id': f'{BOOK}:p063:tc2-p1:011', 'text': 'CÂU HỎI MUỐI'},
    }


def _script_dir(data, name=f'{BOOK}-b17.json'):
    d = tempfile.mkdtemp()
    with open(os.path.join(d, name), 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False)
    return d


BASE = {
    'book': BOOK, 'lesson': 17,
    'blocks': {'principle': BOOK + ':p061:016', 'q_salt': BOOK + ':p063:011'},
    'steps': [
        {'type': 'explain', 'id': 'e1', 'text': 'mở bài', 'sourceBlockId': '{block:principle}'},
        {'type': 'ask', 'id': 'q1', 'prompt': '{text:q_salt}',
         'promptBlockId': '{block:q_salt}', 'options': ['A'], 'acceptable': ['^a$'],
         'hints': [], 'feedbackMatched': 'ừ', 'scaffold': 'sách nói',
         'keySource': 'suy từ {block:principle}'},
    ],
}


class LoaderTests(unittest.TestCase):
    def test_the_real_bai17_data_file_ships_and_builds(self):
        # Tệp thật trong repo phải dựng được — nếu không, sản phẩm mất SAM.
        path = os.path.join(HERE, '..', 'corpus', 'tutor_scripts', f'{BOOK}-b17.json')
        self.assertTrue(os.path.exists(path), 'thiếu tệp kịch bản Bài 17')
        data = json.load(open(path, encoding='utf-8'))
        self.assertEqual(data['book'], BOOK)
        self.assertEqual(data['lesson'], 17)
        self.assertEqual([s['type'] for s in data['steps']],
                         ['explain', 'ask', 'ask', 'ask', 'next'])

    def test_a_lesson_without_a_script_file_returns_none(self):
        # 8 bài lớp 6 còn lại đang ở nhánh này — phải im lặng, không nổ.
        self.assertIsNone(
            bridge.tutor_script_for(_tsl(lesson=16), _by_id(), script_dir=_script_dir(BASE)))

    def test_placeholders_become_real_ids_and_verbatim_text(self):
        s = bridge.tutor_script_for(_tsl(), _by_id(), script_dir=_script_dir(BASE))
        self.assertIsNotNone(s)
        self.assertEqual(s['steps'][0]['sourceBlockId'], f'{BOOK}:p061:tc2-p1:016')
        # ⭐ Lời sách KHÔNG chép lại vào kịch bản — luôn lấy từ chính block,
        # nên không thể lệch với sách.
        self.assertEqual(s['steps'][1]['prompt'], 'CÂU HỎI MUỐI')
        self.assertIn(f'{BOOK}:p061:tc2-p1:016', s['steps'][1]['keySource'])

    def test_missing_block_fails_closed(self):
        data = json.loads(json.dumps(BASE))
        data['blocks']['q_salt'] = BOOK + ':p999:001'   # block không có trong TSL
        self.assertIsNone(
            bridge.tutor_script_for(_tsl(), _by_id(), script_dir=_script_dir(data)),
            'kịch bản trỏ vào block đã biến mất là kịch bản nói về thứ không còn trong bài')

    def test_unfilled_placeholder_fails_closed(self):
        data = json.loads(json.dumps(BASE))
        data['steps'][0]['text'] = 'còn {block:khong_khai} chưa điền'
        self.assertIsNone(
            bridge.tutor_script_for(_tsl(), _by_id(), script_dir=_script_dir(data)),
            'thà không có kịch bản còn hơn đưa cho trẻ một câu cụt')

    def test_file_declaring_another_lesson_is_refused(self):
        data = json.loads(json.dumps(BASE))
        data['lesson'] = 99
        self.assertIsNone(
            bridge.tutor_script_for(_tsl(), _by_id(), script_dir=_script_dir(data)))

    def test_broken_json_does_not_crash_the_build(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, f'{BOOK}-b17.json'), 'w', encoding='utf-8') as fh:
            fh.write('{ hỏng')
        self.assertIsNone(bridge.tutor_script_for(_tsl(), _by_id(), script_dir=d))

    def test_every_role_used_in_steps_is_declared(self):
        # Gõ sai một vai (`{block:q_slat}`) không làm gì nổ lúc soạn: cầu chỉ
        # lặng lẽ trả None và bài mất «Học với SAM». CI phải bắt tại chỗ.
        for path in sorted(glob.glob(os.path.join(
                HERE, '..', 'corpus', 'tutor_scripts', '*.json'))):
            data = json.load(open(path, encoding='utf-8'))
            declared = set((data.get('blocks') or {}).keys())
            used = set(re.findall(r'\{(?:block|text):([^}]+)\}',
                                  json.dumps(data.get('steps') or [], ensure_ascii=False)))
            self.assertEqual(used - declared, set(),
                             f'{os.path.basename(path)}: vai dùng trong steps mà không khai')
            self.assertEqual(declared - used, set(),
                             f'{os.path.basename(path)}: khai block thừa, không ai dùng')

    def test_data_file_name_matches_what_it_declares(self):
        # Tệp đặt sai tên ⇒ không bài nào tìm thấy nó; cũng im lặng.
        for path in sorted(glob.glob(os.path.join(
                HERE, '..', 'corpus', 'tutor_scripts', '*.json'))):
            data = json.load(open(path, encoding='utf-8'))
            self.assertEqual(
                os.path.basename(path),
                f"{data['book']}-b{int(data['lesson']):02d}.json")
