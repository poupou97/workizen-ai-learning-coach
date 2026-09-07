#!/usr/bin/env python3
"""WAL-194 — cửa sổ bằng chứng của story phải cắt ở RANH GIỚI TỪ.

Chạy:  python3 -m unittest discover -s tool/tests -v

Vì sao có tệp này: màn chuyện dán nhãn khối văn bản là «TRÍCH NGUYÊN VĂN TỪ
NGUỒN». Cửa sổ cắt theo offset ký tự cố định (`m.start()-60`) rơi vào giữa từ
bất cứ khi nào nó rơi vào giữa từ, nên trẻ đọc được «ương pháp nhuộm Gram…» —
một mảnh cụt, không phải nguyên văn.

Đo trên pack trước bản vá: 8/38 cụt đầu, 15/38 cụt đuôi. Ticket báo 1 ca.
Không dựa vào kho chuyện thật (gitignore) — test này kiểm thẳng hàm cắt."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'stories'))
import mine_stories as ms  # noqa: E402

# Chính câu đã hỏng trên máy thật.
PAGE = ('Bước 3: Quan sát. Phương pháp nhuộm Gram được phát minh bởi nhà khoa '
        'học Hen Krit-chừn Gioa-chim G-ram (Hans Christian Joachim Gram) năm '
        '1884 và vẫn dùng đến nay.')


class SnapTests(unittest.TestCase):
    def test_the_real_regression_reads_whole_words(self):
        start = PAGE.index('ương pháp')          # cố tình rơi vào giữa «Phương»
        got = ms.snap(PAGE, start, start + 30)
        self.assertTrue(got.startswith('Phương pháp'),
                        f'vẫn cụt đầu: {got[:20]!r}')

    def test_never_starts_or_ends_mid_word(self):
        # Quét MỌI cửa sổ có thể — lỗi này sinh ra từ một offset vô tình, nên
        # kiểm một ca thì chưa đủ.
        for start in range(len(PAGE)):
            for width in (10, 40, 90):
                got = ms.snap(PAGE, start, start + width)
                if not got:
                    continue
                i = PAGE.index(got)
                if i > 0:
                    self.assertFalse(
                        ms._WORDCH.match(PAGE[i - 1]) and ms._WORDCH.match(got[0]),
                        f'cụt đầu tại start={start} width={width}: {got[:15]!r}')
                e = i + len(got)
                if e < len(PAGE):
                    self.assertFalse(
                        ms._WORDCH.match(PAGE[e]) and ms._WORDCH.match(got[-1]),
                        f'cụt đuôi tại start={start} width={width}: {got[-15:]!r}')

    def test_only_widens_never_narrows(self):
        # Bước curate khớp bằng «mảnh bắt buộc có trong evidence». Nếu snap có
        # thể THU HẸP cửa sổ thì một lần dựng lại pack có thể đánh rơi mục đã
        # được người chấm duyệt — nên tính chất này phải được khoá.
        for start in range(0, len(PAGE), 3):
            for width in (10, 40, 90):
                a, b = start, min(len(PAGE), start + width)
                got = ms.snap(PAGE, a, b)
                self.assertIn(PAGE[a:b], got,
                              'snap đã cắt mất chữ vốn nằm trong cửa sổ gốc')

    def test_snap_clamps_out_of_range(self):
        self.assertEqual(ms.snap(PAGE, -50, 10**6), PAGE)

    def test_clip_backs_off_to_a_word_boundary(self):
        t = 'Phương pháp nhuộm Gram được phát minh'
        got = ms.clip(t, 20)
        self.assertLessEqual(len(got), 20)
        self.assertTrue(t.startswith(got))
        # cap không được tái tạo đúng lỗi mà snap vừa sửa
        self.assertFalse(ms._WORDCH.match(t[len(got.rstrip())]) and got.rstrip()
                         and ms._WORDCH.match(got.rstrip()[-1]),
                         f'clip cắt giữa từ: {got!r}')

    def test_clip_leaves_short_text_alone(self):
        self.assertEqual(ms.clip('ngắn', 300), 'ngắn')
