#!/usr/bin/env python3
"""B3 — CỘNG THÊM, KHÔNG THAY THẾ.

Luật di trú Founder chốt:
`NỘI DUNG D AN TOÀN + VÙNG DOCLING ĐÁNG TIN = NỘI DUNG CANONICAL MỚI`.
Không bao giờ D → Docling thay trọn gói.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import docling_pack as dp  # noqa: E402


def row(book='b', page=3, box=(0.1, 0.2, 0.4, 0.3), readable=True,
        text='Hình 6.1. Một số loại động vật cảnh', sub=None):
    return dict(book=book, page=page, box=list(box), readable=readable,
                region_trust='TRUSTED', identity='RESOLVED',
                ident=dict(kind='hình', num='6.1', text=text, sub=sub))


class ChiMuc(unittest.TestCase):
    def _file(self, rows):
        fh = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False,
                                         encoding='utf-8')
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
        fh.close()
        self.addCleanup(os.remove, fh.name)
        return fh.name

    def test_chi_lay_vung_du_ca_hai_phep_do(self):
        p = self._file([row(), row(page=4, readable=False)])
        got = dp.readable_by_page(p)
        self.assertEqual(list(got), [('b', 3)])

    def test_THIEU_TEP_thi_khong_lam_hong_duong_dung(self):
        """Bước tri giác hỏng KHÔNG được làm hỏng dữ liệu đang tốt."""
        self.assertEqual(dp.readable_by_page('/khong/co/that.jsonl'), {})

    def test_dong_cut_do_sap_giua_chung_khong_lam_vo_ca_tep(self):
        p = self._file([row()])
        with open(p, 'a', encoding='utf-8') as fh:
            fh.write('{"book": "b", "pa')
        self.assertEqual(len(dp.readable_by_page(p)), 1)


class ChuThich(unittest.TestCase):
    def test_uu_tien_NHAN_CON_in_trong_sach(self):
        self.assertEqual(dp.caption_of(row(sub='b) Mèo Anh lông ngắn')),
                         'b) Mèo Anh lông ngắn')

    def test_khong_co_nhan_con_thi_dung_chu_thich_hinh(self):
        self.assertEqual(dp.caption_of(row()), 'Hình 6.1. Một số loại động vật cảnh')


class CongThem(unittest.TestCase):
    def setUp(self):
        self.idx = {('b', 3): [row()]}

    def test_them_vung_D_chua_co(self):
        got = dp.extra_figures('b', [3], existing=[], index=self.idx)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]['source'], 'docling')

    def test_KHONG_them_ban_thu_hai_cua_hinh_D_da_co(self):
        # D đã nhận đúng hình ấy ⇒ thêm nữa là hai ảnh giống nhau trong bài.
        got = dp.extra_figures('b', [3], existing=[[0.1, 0.2, 0.4, 0.3]],
                               index=self.idx)
        self.assertEqual(got, [])

    def test_hai_de_xuat_Docling_chong_nhau_chi_lay_mot(self):
        idx = {('b', 3): [row(), row(box=(0.11, 0.21, 0.4, 0.3))]}
        got = dp.extra_figures('b', [3], existing=[], index=idx)
        self.assertEqual(len(got), 1)

    def test_trang_khong_co_vung_dang_tin_thi_khong_them_gi(self):
        self.assertEqual(dp.extra_figures('b', [9], existing=[], index=self.idx), [])

    def test_dem_cau_noi_di_tru_ngay_luc_dung(self):
        """MOI = chỉ Docling có · CA_HAI = D đã có rồi. Đếm ở đây vì đây là chỗ
        duy nhất biết cả hai phía."""
        import collections
        st = collections.Counter()
        idx = {('b', 3): [row(), row(box=(0.6, 0.6, 0.2, 0.2))]}
        dp.extra_figures('b', [3], existing=[[0.1, 0.2, 0.4, 0.3]], index=idx,
                         stats=st)
        self.assertEqual((st['MOI'], st['CA_HAI']), (1, 1))

    def test_KHONG_dung_toi_hinh_cua_D(self):
        """⭐ Bất biến di trú: danh sách D vào thế nào ra thế ấy."""
        d = [[0.5, 0.5, 0.2, 0.2]]
        before = [list(x) for x in d]
        dp.extra_figures('b', [3], existing=d, index=self.idx)
        self.assertEqual(before, [list(x) for x in d[:len(before)]])


if __name__ == '__main__':
    unittest.main()
