#!/usr/bin/env python3
"""BẤT BIẾN PACK — một bước dựng không được âm thầm làm giảm năng lực bước khác.

Lỗi thật đã xảy ra: dựng lại `lesson-index` sinh `content` KHÔNG có mục hình;
hình chỉ quay lại khi ai đó nhớ chạy tiếp `build_lesson_figures`. Lớp 10–12 mất
sạch hình, `L1-M` tụt, KHÔNG một lỗi hay cảnh báo nào.

Ngưỡng phần trăm bị cố ý tránh: «giảm dưới 10% thì cho qua» là một cánh cửa để
mất dữ liệu im lặng.
"""
import json
import os
import sqlite3
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
import build_pack as bp  # noqa: E402


def _index(pack_dir, grade=6, readings=None):
    os.makedirs(pack_dir, exist_ok=True)
    with open(bp.index_path(grade, pack_dir), 'w', encoding='utf-8') as fh:
        json.dump({'grade': grade, 'subjects': {},
                   'lessonReadings': readings if readings is not None else []},
                  fh, ensure_ascii=False)


def _store(fig_dir, grade=6, ids=()):
    os.makedirs(fig_dir, exist_ok=True)
    p = bp.figures_path(grade, fig_dir)
    if os.path.exists(p):
        os.remove(p)
    db = sqlite3.connect(p)
    db.execute('CREATE TABLE fig (id TEXT PRIMARY KEY, book TEXT, lesson INT, '
               'page INT, w INT, h INT, jpeg BLOB)')
    for i in ids:
        db.execute('INSERT INTO fig VALUES (?,?,?,?,?,?,?)', (i, 'b', 1, 1, 10, 10, b''))
    db.commit()
    db.close()


def _reading(lesson=1, imgs=()):
    return dict(book='b', lesson=lesson, pagePdfStart=1, pagePdfEnd=2, text='x',
                content=[{'t': 'text', 'v': 'chữ'}]
                + [{'t': 'img', 'id': i, 'w': 10, 'h': 10} for i in imgs])


class InvariantTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pack = os.path.join(self.tmp.name, 'pack')
        self.figs = os.path.join(self.tmp.name, 'figs')

    def test_index_rebuilt_without_figures_FAILS(self):
        # ĐÚNG ca đã xảy ra: kho còn hình, mục lục không mang mục hình nào.
        _store(self.figs, ids=['f1', 'f2'])
        _index(self.pack, readings=[_reading()])
        problems = bp.verify(6, self.pack, self.figs)
        self.assertTrue(problems)
        self.assertIn('quên hình', problems[0])

    def test_a_healthy_pack_passes(self):
        _store(self.figs, ids=['f1'])
        _index(self.pack, readings=[_reading(imgs=['f1'])])
        self.assertEqual(bp.verify(6, self.pack, self.figs), [])

    def test_dangling_image_reference_FAILS(self):
        # Mục hình trỏ vào thứ kho không có ⇒ ô ảnh vỡ trên máy trẻ.
        _store(self.figs, ids=['f1'])
        _index(self.pack, readings=[_reading(imgs=['f1', 'KHONG-CO'])])
        problems = bp.verify(6, self.pack, self.figs)
        self.assertTrue(any('không có trong kho' in p for p in problems))

    def test_images_without_any_store_FAILS(self):
        _index(self.pack, readings=[_reading(imgs=['f1'])])
        problems = bp.verify(6, self.pack, self.figs)
        self.assertTrue(any('KHÔNG có kho hình' in p for p in problems))

    def test_a_grade_with_no_figure_store_is_VALID(self):
        # Lớp chưa dựng kho hình là hợp lệ — bài vẫn đọc được phần chữ.
        _index(self.pack, readings=[_reading()])
        self.assertEqual(bp.verify(6, self.pack, self.figs), [])

    def test_an_empty_grade_is_valid(self):
        _index(self.pack, readings=[])
        _store(self.figs, ids=['f1'])
        self.assertEqual(bp.verify(6, self.pack, self.figs), [])

    def test_shape_counts_distinct_images_not_entries(self):
        _index(self.pack, readings=[_reading(1, ['f1']), _reading(2, ['f1', 'f2'])])
        s = bp.pack_shape(6, self.pack)
        self.assertEqual(s['openable'], 2)
        self.assertEqual(s['with_images'], 2)
        self.assertEqual(s['images'], 2)


class OrderTests(unittest.TestCase):
    def test_the_build_encodes_index_then_figures(self):
        # Thứ tự là một PHỤ THUỘC, không phải thói quen của người chạy.
        import inspect
        src = inspect.getsource(bp.build)
        self.assertLess(src.index('build_lesson_index'), src.index('build_lesson_figures'))


class PendingFlagTests(unittest.TestCase):
    """Pack tự khai nó chưa xong — không dựa vào việc đếm hình mới phát hiện."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pack = os.path.join(self.tmp.name, 'pack')
        self.figs = os.path.join(self.tmp.name, 'figs')

    def test_a_pack_that_declares_itself_pending_FAILS(self):
        os.makedirs(self.pack, exist_ok=True)
        with open(bp.index_path(6, self.pack), 'w', encoding='utf-8') as fh:
            json.dump({'grade': 6, 'subjects': {}, 'figuresPending': True,
                       'lessonReadings': [_reading(imgs=['f1'])]}, fh, ensure_ascii=False)
        _store(self.figs, ids=['f1'])
        problems = bp.verify(6, self.pack, self.figs)
        self.assertTrue(any('figuresPending' in p for p in problems))

    def test_a_finished_pack_carries_no_pending_flag(self):
        _store(self.figs, ids=['f1'])
        _index(self.pack, readings=[_reading(imgs=['f1'])])
        self.assertFalse(bp.pack_shape(6, self.pack)['pending'])
        self.assertEqual(bp.verify(6, self.pack, self.figs), [])


class ShelfRoutingTests(unittest.TestCase):
    """Cuốn lên giá mà bấm vào ra màn RỖNG — đã xảy ra thật, không lỗi nào báo.

    Máy thật lớp 11: «Tin học 11 · ĐỊNH HƯỚNG KHOA HỌC MÁY TÍNH · 31 bài» trên
    giá; bấm vào ⇒ «SAM chưa có mục lục môn này trên máy». `books[].subject` đã
    được sửa theo lõi định danh, mục lục thì vẫn nằm dưới môn cũ «Khoa học».
    60 bài (lớp 11 + 12) hứa với trẻ rồi dẫn vào ngõ cụt.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pack = os.path.join(self.tmp.name, 'pack')
        self.figs = os.path.join(self.tmp.name, 'figs')
        os.makedirs(self.pack, exist_ok=True)

    def _write(self, books, subjects):
        with open(bp.index_path(11, self.pack), 'w', encoding='utf-8') as fh:
            json.dump({'grade': 11, 'books': books, 'subjects': subjects,
                       'lessonReadings': []}, fh, ensure_ascii=False)

    def test_mon_tren_gia_lech_voi_mon_giu_muc_luc_thi_FAIL(self):
        self._write(
            books=[{'sourceDocumentId': 'b1', 'subject': 'Tin học',
                    'title': 'Tin học 11'}],
            subjects={'Khoa học': [{'sourceDocumentId': 'b1', 'lessons': []}]})
        problems = bp.verify(11, self.pack, self.figs)
        self.assertTrue(any('ra màn rỗng' in p for p in problems), problems)

    def test_khop_mon_thi_dat(self):
        self._write(
            books=[{'sourceDocumentId': 'b1', 'subject': 'Tin học',
                    'title': 'Tin học 11'}],
            subjects={'Tin học': [{'sourceDocumentId': 'b1', 'lessons': []}]})
        self.assertEqual(bp.verify(11, self.pack, self.figs), [])

    def test_sach_khong_co_muc_luc_nao_cung_la_ngo_cut(self):
        self._write(books=[{'sourceDocumentId': 'b1', 'subject': 'Tin học',
                            'title': 'Tin học 11'}],
                    subjects={})
        self.assertTrue(bp.unrouted_books(11, self.pack))

    def test_trung_ten_duoc_DEM_chu_khong_lam_hong_ban_dung(self):
        # 9 cuốn cố ý không có nhãn phân biệt (bìa không xác minh chéo được).
        # Thà để trùng còn hơn dán tên không kiểm được — nhưng phải đếm được.
        self._write(
            books=[{'sourceDocumentId': 'b1', 'subject': 'Công nghệ',
                    'title': 'Công nghệ 9', 'volumeLabel': None,
                    'variantLabel': None},
                   {'sourceDocumentId': 'b2', 'subject': 'Công nghệ',
                    'title': 'Công nghệ 9', 'volumeLabel': None,
                    'variantLabel': None}],
            subjects={'Công nghệ': [{'sourceDocumentId': 'b1', 'lessons': []},
                                    {'sourceDocumentId': 'b2', 'lessons': []}]})
        amb = bp.ambiguous_books(11, self.pack)
        self.assertEqual(len(amb), 1)
        self.assertEqual(sorted(amb[0][1]), ['b1', 'b2'])
        self.assertEqual(bp.verify(11, self.pack, self.figs), [])

    def test_nhan_phan_biet_khac_nhau_thi_khong_bi_tinh_la_trung(self):
        self._write(
            books=[{'sourceDocumentId': 'b1', 'subject': 'Công nghệ',
                    'title': 'Công nghệ 11', 'variantLabel': 'CƠ KHÍ'},
                   {'sourceDocumentId': 'b2', 'subject': 'Công nghệ',
                    'title': 'Công nghệ 11', 'variantLabel': 'CHĂN NUÔI'}],
            subjects={'Công nghệ': [{'sourceDocumentId': 'b1', 'lessons': []},
                                    {'sourceDocumentId': 'b2', 'lessons': []}]})
        self.assertEqual(bp.ambiguous_books(11, self.pack), [])
