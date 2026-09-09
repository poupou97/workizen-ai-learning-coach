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


class CungMotHinhNguon(unittest.TestCase):
    """⛔ «CÙNG MỘT HÌNH NGUỒN» KHÔNG được định nghĩa bằng CHỒNG HỘP.

    Bằng chứng phải từ nguồn: cùng trang VÀ cùng một dòng chú thích SÁCH IN.
    Hình học chỉ là bằng chứng phụ.
    """

    CAP = 'Hình 6.1. Một số loại động vật cảnh'   # khớp mặc định của `row()`

    def dfig(self, cap=CAP, box=(0.1, 0.2, 0.4, 0.3), page=3):
        return dict(id='d0', book='b', page=page, bbox=list(box), caption=cap,
                    source='D')

    def test_cung_trang_va_cung_CHU_THICH_IN_thi_la_mot(self):
        self.assertTrue(dp.same_source_visual(self.dfig(), row()))

    def test_CHONG_HOP_ma_KHAC_chu_thich_thi_KHONG_phai_mot(self):
        d = self.dfig(cap='Hình 6.2. Một hình khác hẳn')
        self.assertFalse(dp.same_source_visual(d, row()))

    def test_KHAC_TRANG_thi_khong_phai_mot(self):
        self.assertFalse(dp.same_source_visual(self.dfig(page=9), row()))

    def test_D_KHONG_co_chu_thich_thi_KHONG_chung_minh_duoc(self):
        """Thiếu bằng chứng in ⇒ không được thay chỗ."""
        self.assertFalse(dp.same_source_visual(self.dfig(cap=None), row()))

    def test_cung_chu_thich_ma_KHONG_chong_nhau_thi_khong_nhan(self):
        d = self.dfig(box=(0.6, 0.7, 0.2, 0.2))
        self.assertFalse(dp.same_source_visual(d, row()))

    def test_chu_thich_khac_khoang_trang_hoa_thuong_van_la_mot(self):
        d = self.dfig(cap='  hình 6.1.  MỘT SỐ LOẠI ĐỘNG VẬT CẢNH  ')
        r = row(text='Hình 6.1. Một số loại động vật cảnh')
        self.assertTrue(dp.same_source_visual(d, r))


class BoChonHinh(unittest.TestCase):
    def _d(self, cap='Hình 6.1. Một số loại động vật cảnh',
           box=(0.1, 0.2, 0.4, 0.3)):
        return dict(id='d0', book='b', page=3, bbox=list(box), caption=cap,
                    source='D')

    def test_chung_minh_duoc_cung_nguon_thi_DOCLING_THAY_CHO(self):
        st = __import__('collections').Counter()
        out = dp.select([self._d()], 'b', [3], {('b', 3): [row()]}, stats=st)
        self.assertEqual(st['DOCLING_SUPERSEDES_D'], 1)
        self.assertEqual([f['source'] for f in out], ['docling'])

    def test_KHONG_chung_minh_duoc_thi_GIU_D_va_BO_docling(self):
        """Chồng hộp mà khác chú thích ⇒ D là dự phòng, không hiện hai bản."""
        st = __import__('collections').Counter()
        out = dp.select([self._d(cap='Hình 6.2. Khác')], 'b', [3],
                        {('b', 3): [row()]}, stats=st)
        self.assertEqual(st['D_FALLBACK'], 1)
        self.assertEqual([f['source'] for f in out], ['D'])

    def test_cho_D_KHONG_co_gi_thi_THEM_MOI(self):
        st = __import__('collections').Counter()
        out = dp.select([], 'b', [3], {('b', 3): [row()]}, stats=st)
        self.assertEqual(st['DOCLING_NEW'], 1)
        self.assertEqual(len(out), 1)

    def test_CHE_DO_BONG_dem_luat_MOI_nhung_ra_dau_ra_luat_CU(self):
        """⚠ Bóng KHÔNG phải «chỉ giữ D». Bản đầu tôi viết vậy và nó lặng lẽ bỏ
        luôn phần Docling đang có — lớp 6 tụt 913 → 709 hình."""
        st = __import__('collections').Counter()
        out = dp.select([self._d()], 'b', [3], {('b', 3): [row()]},
                        stats=st, shadow=True)
        self.assertEqual(st['DOCLING_SUPERSEDES_D'], 1)
        self.assertEqual([f['source'] for f in out], ['D'])

    def test_CHE_DO_BONG_van_THEM_hinh_o_cho_D_khong_co(self):
        st = __import__('collections').Counter()
        out = dp.select([], 'b', [3], {('b', 3): [row()]}, stats=st, shadow=True)
        self.assertEqual(st['DOCLING_NEW'], 1)
        self.assertEqual(len(out), 1, 'bóng mà bỏ mất hình đang có thì không phải bóng')

    def test_danh_tinh_GIU_LAI_thi_khong_bao_gio_toi_bo_chon(self):
        """`readable_by_page` đã loại vùng chưa nối được danh tính, nên bộ chọn
        không bao giờ thấy chúng — REGION_TRUST != IDENTITY_LINK giữ nguyên."""
        import tempfile, os as _os
        fh = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False,
                                         encoding='utf-8')
        fh.write(json.dumps(row(readable=False), ensure_ascii=False) + '\n')
        fh.close()
        self.addCleanup(_os.remove, fh.name)
        self.assertEqual(dp.readable_by_page(fh.name), {})


if __name__ == '__main__':
    unittest.main()
