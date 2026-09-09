#!/usr/bin/env python3
"""ĐỒ TRANG TRÍ CỦA TRANG — gỡ nhầm hình thật TỆ HƠN để sót vài dải màu.

Số đo nền: `FIGURE_CROP_VALID` = 70,8% (mẫu 120). 17/35 ca hỏng là đồ trang
trí, và cả 17 đều từ đường D.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import decoration as dec  # noqa: E402


def item(book='b', page=1, h=0xABC, w=640, hh=60, source='D'):
    return dict(book=book, page=page, hash=h, w=w, h=hh, source=source)


class DemLapLai(unittest.TestCase):
    def test_dem_theo_TRANG_phan_biet_khong_theo_ban_ghi(self):
        """Hai bản của cùng một dải TRÊN CÙNG MỘT TRANG không chứng minh nó lặp."""
        r = dec.repeat_index([item(page=1), item(page=1), item(page=1)])
        self.assertEqual(r[('b', 0xABC)], 1)

    def test_khac_cuon_thi_khong_cong_don(self):
        r = dec.repeat_index([item(book='x', page=1), item(book='y', page=2)])
        self.assertEqual(r[('x', 0xABC)], 1)
        self.assertEqual(r[('y', 0xABC)], 1)


class HaiBangChung(unittest.TestCase):
    def _reps(self, n):
        return {('b', 0xABC): n}

    def test_lap_nhieu_VA_rat_det_thi_la_trang_tri(self):
        self.assertTrue(dec.is_page_furniture(item(w=640, hh=60), self._reps(30)))

    def test_lap_nhieu_VA_rat_cao_cung_la_trang_tri(self):
        """Dải DỌC mép trang — họ thứ hai, tìm ra khi soi phía luật giữ lại."""
        self.assertTrue(dec.is_page_furniture(item(w=40, hh=900), self._reps(30)))

    def test_LAP_NHIEU_ma_ti_le_binh_thuong_thi_GIU(self):
        """⭐ Ca thật #067: sơ đồ sân tập GDTC lặp 8 trang vì bài nào cũng dùng
        lại sân ấy. «LẶP LẠI KHÔNG TỰ ĐỘNG LÀ TRANG TRÍ.»"""
        self.assertFalse(dec.is_page_furniture(item(w=640, hh=503), self._reps(8)))

    def test_RAT_DET_ma_khong_lap_thi_GIU(self):
        """⭐ Khuông nhạc rất dẹt nhưng mỗi bài một khác. Đo được: luật hai vế
        gỡ 0/362 hình trong sách Âm nhạc."""
        self.assertFalse(dec.is_page_furniture(item(w=640, hh=60), self._reps(1)))

    def test_vung_DOCLING_khong_bi_luat_nay_dung_toi(self):
        self.assertFalse(dec.is_page_furniture(item(w=640, hh=60, source='docling'),
                                               self._reps(30)))

    def test_khong_co_trong_so_lap_thi_GIU(self):
        self.assertFalse(dec.is_page_furniture(item(), {}))


class NghiNgoThiGiu(unittest.TestCase):
    def test_ngay_o_biên_van_GIU(self):
        """Nghi ngờ thì giữ: đúng ngưỡng chưa đủ để gỡ ở một vế."""
        self.assertFalse(dec.is_page_furniture(item(w=640, hh=60),
                                               {('b', 0xABC): dec.REP_MIN - 1}))
        self.assertFalse(dec.is_page_furniture(item(w=300, hh=299),
                                               {('b', 0xABC): 99}))

    def test_ti_le_do_ca_hai_chieu(self):
        self.assertAlmostEqual(dec.aspect(640, 64), 10.0)
        self.assertAlmostEqual(dec.aspect(64, 640), 10.0)

    def test_HOP_CHUAN_HOA_phai_dung_ham_RIENG(self):
        """⭐ `aspect` chặn dưới ở 1 ĐIỂM ẢNH nên với hộp 0–1 nó trả 1,0 với
        MỌI hộp — luật băng mục từng im lặng không kích hoạt vì lỗi này."""
        self.assertAlmostEqual(dec.aspect(0.84, 0.06), 1.0)
        self.assertAlmostEqual(dec.aspect_norm(0.84, 0.06), 14.0)
        self.assertAlmostEqual(dec.aspect_norm(0.06, 0.84), 14.0)

    def test_kich_thuoc_rong_hoac_cao_bang_khong_khong_lam_vo(self):
        self.assertGreater(dec.aspect(0, 0), 0)


if __name__ == '__main__':
    unittest.main()


def L(x, w, y, text, h=0.02):
    return dict(x=x, w=w, y=y, h=h, text=text)


class BangMucVaDaiTrang(unittest.TestCase):
    """HỌ THỨ HAI — nhận bằng VAI TRÒ TRONG SÁCH, không bằng dáng vẻ.

    Ca đối kháng đắt nhất: 12 hình sách Âm nhạc cùng dải tỉ lệ, soi tận mắt
    thì đúng MỘT NỬA là băng mục, MỘT NỬA là KHUÔNG NHẠC THẬT.
    """

    BAND = (0.08, 0.05, 0.84, 0.06)          # dải ngang, tỉ lệ 14

    def test_bang_muc_mang_NHAN_MUC_lap_nhieu_trang(self):
        lines = [L(0.12, 0.10, 0.07, 'HÁT')]
        self.assertTrue(dec.is_section_furniture(self.BAND, lines, {'HÁT': 10}))

    def test_KHUONG_NHAC_cung_ti_le_ay_thi_GIU(self):
        """⭐ Cùng cuốn, cùng tỉ lệ. Lời hát và ký hiệu nhịp KHÔNG lặp như nhãn mục."""
        lines = [L(0.10, 0.20, 0.07, 'Chậm vừa'), L(0.40, 0.30, 0.07, 'mp')]
        self.assertFalse(dec.is_section_furniture(self.BAND, lines,
                                                  {'CHẬM VỪA': 1, 'MP': 2}))

    def test_dai_trang_mang_CHINH_SO_TRANG_o_mep(self):
        lines = [L(0.90, 0.03, 0.06, '95')]
        self.assertTrue(dec.is_section_furniture(self.BAND, lines, {}))

    def test_so_o_GIUA_trang_khong_phai_so_trang(self):
        band = (0.08, 0.45, 0.84, 0.06)
        lines = [L(0.50, 0.03, 0.47, '95')]
        self.assertFalse(dec.is_section_furniture(band, lines, {}))

    def test_vung_NHIEU_DONG_CHU_thi_GIU(self):
        """Vùng có nhiều dòng là hình CÓ nhãn, không phải bản thân cái nhãn."""
        lines = [L(0.1, 0.2, 0.06, 'HÁT'), L(0.1, 0.2, 0.07, 'a'),
                 L(0.1, 0.2, 0.08, 'b'), L(0.1, 0.2, 0.09, 'c')]
        self.assertFalse(dec.is_section_furniture(self.BAND, lines, {'HÁT': 10}))

    def test_ti_le_BINH_THUONG_thi_khong_dung_toi(self):
        """⭐ Hình học Toán thưa nét nằm ngoài họ này — không được chạm."""
        box = (0.2, 0.3, 0.4, 0.3)
        lines = [L(0.25, 0.10, 0.35, 'HÁT')]
        self.assertFalse(dec.is_section_furniture(box, lines, {'HÁT': 10}))

    def test_khong_co_chu_nao_ben_trong_thi_GIU(self):
        self.assertFalse(dec.is_section_furniture(self.BAND, [], {}))

    def test_khong_co_hop_bao_thi_GIU(self):
        self.assertFalse(dec.is_section_furniture(None, [L(0.1, 0.1, 0.06, 'HÁT')],
                                                  {'HÁT': 10}))


class DemNhanMuc(unittest.TestCase):
    def test_dem_theo_TRANG_va_bo_qua_SO(self):
        pages = {1: [L(0, .1, .05, 'HÁT'), L(0, .1, .9, '12')],
                 2: [L(0, .1, .05, 'hát')],
                 3: [L(0, .1, .9, '13')]}
        r = dec.heading_reps(pages)
        self.assertEqual(r.get('HÁT'), 2)
        self.assertNotIn('12', r)

    def test_dong_qua_dai_khong_phai_nhan_muc(self):
        pages = {1: [L(0, .8, .05, 'Đây là một câu văn dài của thân bài trong sách')]}
        self.assertEqual(dec.heading_reps(pages), {})
