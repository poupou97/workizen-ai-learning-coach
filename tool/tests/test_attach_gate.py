#!/usr/bin/env python3
"""CỔNG ATTACH — đầu vào dựng chuẩn phải BỀN, TẤT ĐỊNH, và FAIL CLOSED.

⭐ SỰ CỐ THẬT 2026-09-09. Bộ attach đầy đủ nằm ở `/private/tmp/wal-census/attach`.
Máy khởi động lại ⇒ macOS xoá `/private/tmp` ⇒ bộ ấy bốc hơi; chỗ mặc định
trong repo chỉ còn 39/238 cuốn. Trước bản sửa này, lệnh dựng chuẩn vẫn chạy
trót lọt và sinh ra pack NHỎ HƠN mà không một lỗi nào — bài thiếu attach chỉ
bị cộng vào `NO_ATTACH` rồi bỏ qua trong im lặng.

Cùng họ với vụ lớp 3 tụt 232 → 44 bài trong khi cả ba bất biến đều ĐẠT.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import attach_gate as ag  # noqa: E402


def curriculum(tmp, books):
    """Sổ sách chuẩn tối giản: `books` = [(id, grade, số bài)]."""
    docs = [dict(sourceDocumentId=b, docType='SGK', grade=g,
                 lessons=[dict(number=i + 1) for i in range(n)])
            for b, g, n in books]
    p = os.path.join(tmp, 'curriculum.json')
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump(dict(documents=docs), fh)
    return p


def attach(tmp, book, lessons=3, pages=10, book_field=None, raw=None):
    d = os.path.join(tmp, 'attach')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f'{book}.json')
    with open(p, 'w', encoding='utf-8') as fh:
        if raw is not None:
            fh.write(raw)
        else:
            json.dump(dict(book=book_field or book,
                           pages=[{'page': i + 1} for i in range(pages)],
                           lessons=[dict(number=i + 1, page_pdf=i + 1)
                                    for i in range(lessons)],
                           counts=dict(canonical_lesson_count=lessons)), fh)
    return p


class SuyTuSoSach(unittest.TestCase):
    def test_KHONG_hard_code_238(self):
        """238 là quan sát của hôm nay, không phải hằng số sản phẩm."""
        with tempfile.TemporaryDirectory() as t:
            c = curriculum(t, [('a', 3, 2), ('b', 3, 1), ('c', 4, 1)])
            self.assertEqual(ag.expected_books(curriculum=c), {'a', 'b', 'c'})
            self.assertEqual(ag.expected_books(3, curriculum=c), {'a', 'b'})

    def test_sach_khong_co_bai_danh_so_thi_khong_can_attach(self):
        with tempfile.TemporaryDirectory() as t:
            c = curriculum(t, [('a', 3, 0)])
            self.assertEqual(ag.expected_books(curriculum=c), set())


class SoTapHopChuKhongSoDem(unittest.TestCase):
    def test_DU_SO_LUONG_ma_SAI_CUON_van_KHONG_DAT(self):
        """⭐ «Đếm đủ» là phép kiểm sai: 2 tệp vẫn có thể là 2 cuốn sai."""
        with tempfile.TemporaryDirectory() as t:
            c = curriculum(t, [('a', 3, 2), ('b', 3, 2)])
            attach(t, 'a', lessons=2)
            attach(t, 'z', lessons=2)          # đủ 2 tệp, nhưng thiếu «b»
            self.assertEqual(len(os.listdir(os.path.join(t, 'attach'))), 2)
            self.assertTrue(ag.verify(3, t, c))

    def test_du_dung_tap_hop_thi_DAT(self):
        with tempfile.TemporaryDirectory() as t:
            c = curriculum(t, [('a', 3, 2), ('b', 3, 2)])
            attach(t, 'a', lessons=2); attach(t, 'b', lessons=2)
            self.assertEqual(ag.verify(3, t, c), [])


class BatDauVaoHONG(unittest.TestCase):
    def _one(self, **kw):
        t = tempfile.mkdtemp()
        self.addCleanup(__import__('shutil').rmtree, t, True)
        c = curriculum(t, [('a', 3, 2)])
        attach(t, 'a', **kw)
        return ag.verify(3, t, c)

    def test_THIEU_thi_khong_dat(self):
        with tempfile.TemporaryDirectory() as t:
            c = curriculum(t, [('a', 3, 2)])
            self.assertTrue(ag.verify(3, t, c))

    def test_HONG_khong_doc_duoc_thi_khong_dat(self):
        self.assertTrue(self._one(raw='{ khong phai json'))

    def test_TEP_MANG_TEN_SACH_KHAC_thi_khong_dat(self):
        self.assertTrue(self._one(book_field='cuon-khac'))

    def test_KHONG_CO_TRANG_NAO_thi_khong_dat(self):
        self.assertTrue(self._one(pages=0))

    def test_CU_SO_VOI_SO_SACH_thi_khong_dat(self):
        """Sổ sách nay 2 bài, attach dựng khi sổ có 5 ⇒ CŨ."""
        self.assertTrue(self._one(lessons=5))


class SachDungDuoc(unittest.TestCase):
    """`actual_books` phải đếm sách DÙNG ĐƯỢC, không phải sách CÓ TỆP.

    Nó là thứ `ensure` dựa vào để quyết định sinh lại; đếm cả tệp hỏng thì một
    đầu vào hỏng sẽ không bao giờ được sinh lại."""

    def test_tep_HONG_khong_duoc_tinh_la_dung_duoc(self):
        with tempfile.TemporaryDirectory() as t:
            c = curriculum(t, [('a', 3, 2), ('b', 3, 2)])
            attach(t, 'a', lessons=2)
            attach(t, 'b', raw='{ hong')
            self.assertEqual(ag.actual_books(t, ag.lesson_counts(c)), {'a'})

    def test_tep_CU_so_voi_so_sach_khong_duoc_tinh(self):
        with tempfile.TemporaryDirectory() as t:
            c = curriculum(t, [('a', 3, 2)])
            attach(t, 'a', lessons=9)          # sổ nay 2 bài, attach dựng khi có 9
            self.assertEqual(ag.actual_books(t, ag.lesson_counts(c)), set())


CORPUS = os.path.join(ROOT, 'poc-out', 'graph', 'curriculum-structure.json')


@unittest.skipUnless(os.path.exists(CORPUS),
                     'cần sổ sách chuẩn — corpus KHÔNG vào git (bất biến repo), '
                     'nên phép kiểm này chỉ chạy ở máy có dữ liệu')
class HoiQuySuCoReboot(unittest.TestCase):
    """Tái hiện đúng sự cố: đầu vào bền còn, thư mục attach tạm KHÔNG còn.

    ⚠ Bỏ qua trên CI là ĐÚNG, không phải né tránh: CI cố ý không có corpus, nên
    ở đó bước dựng chết sớm hơn vì thiếu sổ sách — vẫn KHÔNG ghi pack, tính an
    toàn vẫn giữ, chỉ là chết vì lý do khác nên không kiểm được ĐÚNG cổng này.
    """

    def test_dung_pack_voi_attach_RONG_phai_DUNG_LAI_va_KHONG_ghi_pack(self):
        with tempfile.TemporaryDirectory() as empty, \
                tempfile.TemporaryDirectory() as out:
            os.makedirs(os.path.join(empty, 'attach'), exist_ok=True)
            env = dict(os.environ, ATTACH_ROOT=empty, PACK_OUT_DIR=out)
            r = subprocess.run(
                [sys.executable, os.path.join(ROOT, 'tool', 'ui',
                                              'build_lesson_index.py'), '1'],
                cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
            self.assertNotEqual(r.returncode, 0,
                                'attach rỗng mà vẫn dựng xong ⇒ pack nhỏ hơn trong im lặng')
            self.assertIn('CỔNG ATTACH', r.stderr + r.stdout)
            self.assertEqual(os.listdir(out), [],
                             'đã ghi pack DÙ cổng không đạt')


if __name__ == '__main__':
    unittest.main()
