#!/usr/bin/env python3
"""TÊN BÀI — phân loại tín hiệu, KHÔNG sinh tên.

Đã thử ba họ trích tên và bỏ cả ba: mỗi họ đều rò một lỗi mà bằng chứng sẵn có
không chặn được. Test ở đây giữ hai thứ: (1) module KHÔNG bao giờ phát tên,
(2) các chốt lọc vẫn nhận đúng thứ chúng phải loại — vì chúng còn được dùng để
đếm, và một phép đếm sai cũng dẫn tới quyết định sai.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import lesson_title as lt  # noqa: E402


def line(text, x=0.12, y=0.2, w=0.5, h=0.02):
    return {'text': text, 'x': x, 'y': y, 'w': w, 'h': h}


class NoTitleEmission(unittest.TestCase):
    def test_module_exposes_no_title_extractor(self):
        # Nếu ai đó thêm lại hàm sinh tên, test này phải đỏ và buộc đọc lý do.
        self.assertFalse(hasattr(lt, 'title_from_page'),
                         'ba họ trích tên đều đã đo và bỏ — xem docstring module')


class CandidateGuards(unittest.TestCase):
    def test_section_headings_are_not_titles(self):
        for t in ('Mục tiêu', 'YÊU CẦU CẦN ĐẠT', 'Khám phá', 'Luyện tập', 'Vận dụng'):
            self.assertFalse(lt.is_candidate(t), t)

    def test_chapter_names_are_not_lesson_titles(self):
        for t in ('CHỦ ĐỀ 1', 'Chương II', 'PHẦN 3', 'TUẦN 12'):
            self.assertFalse(lt.is_candidate(t), t)

    def test_captions_are_not_titles(self):
        for t in ('Hình 1.2. Cấu tạo chung của nhà ở', 'Bảng 3 Kết quả'):
            self.assertFalse(lt.is_candidate(t), t)

    def test_bullets_are_list_items_not_titles(self):
        for t in ('• Thường thức âm nhạc: Nêu được một số đặc điểm',
                  '- Nghe giới thiệu về hoạt động của các câu lạc bộ'):
            self.assertFalse(lt.is_candidate(t), t)

    def test_a_sentence_is_not_a_title(self):
        self.assertFalse(lt.is_candidate('Nhà ở là công trình được xây dựng để ở.'))

    def test_an_unbalanced_bracket_means_the_text_was_cut(self):
        # «…ĐỘC LẬP DÂN TỘC (TỪ ĐẦU» là một nửa tên; một nửa tên trông như cả tên.
        self.assertFalse(lt.is_candidate('ĐẤU TRANH GIÀNH ĐỘC LẬP DÂN TỘC (TỪ ĐẦU'))
        self.assertTrue(lt.is_candidate('CUỘC KHÁNG CHIẾN CHỐNG THỰC DÂN PHÁP (1945 - 1954)'))

    def test_a_real_title_passes(self):
        for t in ('Em bảo vệ cảnh quan thiên nhiên', 'ĐỒ THỊ QUÃNG ĐƯỜNG - THỜI GIAN'):
            self.assertTrue(lt.is_candidate(t), t)


class ClassifyTests(unittest.TestCase):
    def test_inline_form_is_recognised(self):
        page = [line('Bài 20: Em bảo vệ cảnh quan thiên nhiên', y=0.5)]
        self.assertEqual(lt.classify_page(page, 20), 'inline_title')

    def test_marker_without_a_clear_title(self):
        self.assertEqual(lt.classify_page([line('Bài 7', y=0.2)], 7), 'marker_only')

    def test_a_book_organised_by_topic_has_no_lesson_unit(self):
        # 133/395 bài nằm trong sách mà đơn vị là CHỦ ĐỀ/TUẦN — «Bài N» trong
        # mục lục là suy diễn của bộ đọc mục lục, không phải thứ in trong sách.
        page = [line('CHỦ ĐỀ', y=0.06), line('QUẢN LÍ CHI TIÊU', y=0.11),
                line('TUẦN 13', y=0.37)]
        self.assertEqual(lt.classify_page(page, 13), 'no_lesson_unit')

    def test_a_marker_for_a_DIFFERENT_lesson_does_not_count(self):
        # Tên/dấu của bài kế tiếp không được tính cho bài này.
        self.assertNotEqual(lt.classify_page([line('Bài 21: Giữ gìn môi trường')], 20),
                            'inline_title')

    def test_page_furniture_is_outside_the_body(self):
        self.assertFalse(lt.has_lesson_marker([line('Bài 7', y=0.01)], 7))
        self.assertFalse(lt.has_lesson_marker([line('Bài 7', y=0.99)], 7))


class ContinuationTests(unittest.TestCase):
    def test_a_wrapped_title_is_detected(self):
        head = line('Bài 14: QUYỀN VÀ NGHĨA VỤ', y=0.20, h=0.024)
        cont = line('CỦA CÔNG DÂN VỀ BẦU CỬ', y=0.228, x=0.12, h=0.024)
        body = [(head, head['text']), (cont, cont['text'])]
        self.assertTrue(lt.has_continuation(body, head))

    def test_a_bullet_below_is_not_a_continuation(self):
        head = line('Bài 14: MỘT CÁI TÊN', y=0.20, h=0.024)
        b = line('• một mục tiêu', y=0.228, x=0.12, h=0.024)
        self.assertFalse(lt.has_continuation([(head, head['text']), (b, b['text'])], head))
