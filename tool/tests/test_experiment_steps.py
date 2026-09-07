#!/usr/bin/env python3
"""Bước thí nghiệm: dấu đầu dòng của KHTN 6-9, và bước xuống dòng giữa câu.

Chạy:  python3 -m unittest discover -s tool/tests -v

Bộ trích viết cho Khoa học 4/5 («- ») rồi mở sang KHTN 6-9 («•») mà không đổi
ký tự. Hậu quả đo được trên KHTN 6: 8/16 khối tìm đủ «Chuẩn bị» + «Tiến hành»
nhưng đọc được 0 bước nên bị bỏ — gồm cả Bài 17, bài đang hiện trên Home.

Chữ trong test lấy nguyên văn từ SGK KHTN 6 tr.61 (Bài 17)."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
from experiment_steps import (  # noqa: E402
    step_body, is_real_step, continues_step, STEP_BULLETS)

# Nguyên văn SGK KHTN 6 tr.61 — bước 1 chạy sang dòng thứ hai.
B17 = [
    '• Lấy một cốc nước, cho 1 thìa đất vào cốc. Khuấy mạnh cho hỗn hợp trong cốc đục',
    'đều lên. Dừng khuấy và quan sát.',
    '• Gấp giấy lọc và đặt vào phễu (Hình 17.3).',
]


class BulletTests(unittest.TestCase):
    def test_khtn_bullet_is_read(self):
        self.assertEqual(step_body('• Gấp giấy lọc và đặt vào phễu.'),
                         'Gấp giấy lọc và đặt vào phễu.')

    def test_primary_school_hyphen_still_works(self):
        # Khoa học 4/5 vẫn dùng «- » — không được làm hỏng lớp 4, 5.
        self.assertEqual(step_body('- Đổ nước vào cốc và quan sát.'),
                         'Đổ nước vào cốc và quan sát.')

    def test_every_declared_bullet_is_recognised(self):
        for b in STEP_BULLETS:
            self.assertIsNotNone(step_body(f'{b}Một bước có nhiều từ.'), b)

    def test_a_plain_line_is_not_a_step(self):
        self.assertIsNone(step_body('Tiến hành:'))
        self.assertIsNone(step_body('Hình 17.3'))

    def test_a_stray_label_is_not_a_real_step(self):
        # Fail closed — «- AgNO3» là nhãn hoá chất, không phải việc phải làm.
        self.assertFalse(is_real_step('AgNO3'))
        self.assertFalse(is_real_step('ngắn'))
        self.assertTrue(is_real_step('Gấp giấy lọc và đặt vào phễu.'))


class ContinuationTests(unittest.TestCase):
    def _parse(self, lines):
        steps = []
        for t in lines:
            body = step_body(t)
            if body is not None:
                if is_real_step(body):
                    steps.append(body)
                continue
            if steps and continues_step(steps[-1], t):
                steps[-1] = f'{steps[-1]} {t.strip()}'
        return steps

    def test_the_real_bai_17_block_reads_as_two_whole_steps(self):
        steps = self._parse(B17)
        self.assertEqual(len(steps), 2)
        self.assertTrue(steps[0].endswith('Dừng khuấy và quan sát.'),
                        f'bước 1 bị cắt giữa câu: {steps[0]!r}')
        self.assertIn('Khuấy mạnh', steps[0])

    def test_a_finished_sentence_is_not_extended(self):
        # Bước đã trọn câu ⇒ dòng sau là văn khác, không được nuốt vào.
        self.assertFalse(continues_step('Gấp giấy lọc và đặt vào phễu.',
                                        'Em hãy quan sát màu sắc'))

    def test_a_label_line_is_not_swallowed_as_continuation(self):
        self.assertFalse(continues_step('Khuấy mạnh cho hỗn hợp đục', 'Chuẩn bị:'))
        self.assertFalse(continues_step('Khuấy mạnh cho hỗn hợp đục', '(b)'))

    def test_nothing_to_continue_when_there_is_no_step_yet(self):
        self.assertFalse(continues_step('', 'đều lên. Dừng khuấy.'))
