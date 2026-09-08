#!/usr/bin/env python3
"""GOM VÙNG QUANH CHÚ THÍCH — hình mà SÁCH TỰ NÓI là có.

Phễu dò trên 223 mỏ neo có chú thích số, 5 họ nguồn:

    ĐẠT 59 · VỠ MẢNH 79 · TRANG TRÍ 23 · QUÁ NHỎ 30 · KHÔNG THÀNH 14 · KHÔNG THẤY 18

VỠ MẢNH là họ lớn nhất (35,4%): mực có, thành phần có, HỢP của chúng đủ lớn —
chỉ thiếu bước GOM. Nên `classify()` KHÔNG sai; hạ ngưỡng diện tích sẽ nhận
mảnh vụn vào bài đọc.

Chú thích chứng minh hình TỒN TẠI, không cho biết BIÊN. Biên là hợp của mực
thật; dải tìm bị chặn trên bởi chú thích khác và bởi khối thân bài.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import figure_funnel as ff  # noqa: E402
from lesson_figures import caption_regions, _line_crosses, _iou  # noqa: E402


def L(x, w, y, text, h=0.02):
    return dict(x=x, w=w, y=y, h=h, text=text)


def R(x, y, w, h):
    return dict(bbox=[x, y, w, h], area=round(w * h, 5), fill=0.5)


class Anchors(unittest.TestCase):
    def test_chi_nhan_chu_thich_CO_SO_HIEU(self):
        ls = [L(0.1, 0.3, 0.5, 'Hình 5.1. Con lắc đơn'), L(0.1, 0.3, 0.6, 'Hình dưới đây'),
              L(0.1, 0.3, 0.7, 'Bảng 2.3. Số liệu')]
        got = [(a['kind'], a['num']) for a in ff.caption_anchors(ls)]
        self.assertEqual(got, [('hình', '5.1'), ('bảng', '2.3')])


class Neighborhood(unittest.TestCase):
    def test_dung_o_chu_thich_khac_phia_tren(self):
        a1 = dict(x=0.6, y=0.60, w=0.3, h=0.02, num='5.1')
        a2 = dict(x=0.6, y=0.82, w=0.3, h=0.02, num='5.2')
        top, _ = ff.neighborhood(a2, [a1, a2])
        self.assertAlmostEqual(top, 0.62, places=3)   # đáy chú thích trên

    def test_khong_co_gi_phia_tren_thi_bi_CHAN_BOI_BAND_UP(self):
        a = dict(x=0.6, y=0.82, w=0.3, h=0.02, num='5.2')
        top, _ = ff.neighborhood(a, [a])
        self.assertAlmostEqual(top, 0.82 - ff.BAND_UP, places=3)

    def test_dung_o_KHOI_THAN_BAI_phia_tren(self):
        # ⭐ Không có chặn này, hợp trườn qua cả đoạn văn phía trên.
        a = dict(x=0.1, y=0.60, w=0.3, h=0.02, num='1.1')
        top, _ = ff.neighborhood(a, [a], prose=[(0.08, 0.20, 0.50, 0.40)])
        self.assertAlmostEqual(top, 0.40, places=3)

    def test_khoi_than_bai_KHAC_COT_thi_khong_chan(self):
        a = dict(x=0.60, y=0.60, w=0.3, h=0.02, num='1.1')
        top, _ = ff.neighborhood(a, [a], prose=[(0.05, 0.20, 0.40, 0.40)])
        self.assertAlmostEqual(top, 0.25, places=3)


class CrossingGuard(unittest.TestCase):
    def test_dong_van_THO_RA_HAI_BEN_van_bi_tinh_la_cat_qua(self):
        # Ca hỏng nhìn tận mắt: vùng HẸP HƠN dòng văn nên phép «nằm gọn» bỏ lọt,
        # ảnh cắt ra hiện một lát cắt của câu chữ.
        self.assertTrue(_line_crosses(L(0.05, 0.90, 0.50, 'một câu dài'), [0.3, 0.45, 0.2, 0.15]))

    def test_dong_ngoai_hop_thi_khong_tinh(self):
        self.assertFalse(_line_crosses(L(0.05, 0.90, 0.90, 'x'), [0.3, 0.45, 0.2, 0.15]))


class Regions(unittest.TestCase):
    def _lines(self):
        return [L(0.10, 0.30, 0.60, 'Hình 1.1. Sơ đồ mạch điện')]

    def test_gom_nhieu_manh_thanh_MOT_vung(self):
        regs = [R(0.12, 0.40, 0.10, 0.05), R(0.24, 0.42, 0.08, 0.06), R(0.15, 0.50, 0.12, 0.04)]
        out = caption_regions(regs, self._lines())
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['parts'], 3)
        self.assertEqual(out[0]['anchor'], '1.1')

    def test_KHONG_CO_manh_nao_thi_KHONG_dung_vung(self):
        # Chú thích chứng minh hình tồn tại, nhưng không có mực thì không bịa hộp.
        self.assertEqual(caption_regions([], self._lines()), [])

    def test_hop_CAT_QUA_dong_van_bi_bo(self):
        # ⚠ Hợp phải ĐỦ LỚN để `text_coverage` KHÔNG loại nó — nếu không, test
        # này xanh nhờ một cổng khác và cổng «cắt qua dòng văn» không được kiểm.
        # (Đột biến bỏ cổng ấy từng SỐNG SÓT vì đúng lỗi này.)
        lines = self._lines() + [L(0.05, 0.90, 0.45, 'một dòng thân bài rất dài')]
        regs = [R(0.12, 0.27, 0.10, 0.14), R(0.24, 0.30, 0.08, 0.25)]
        union_cover = 0.90 * 0.02 * 0.0    # dòng chỉ chiếm một lát mỏng
        self.assertEqual(union_cover, 0.0)
        self.assertEqual(caption_regions(regs, lines), [])

    def test_hop_KHONG_cat_dong_van_nao_thi_GIU(self):
        lines = self._lines() + [L(0.05, 0.90, 0.10, 'dòng thân bài ở tận trên')]
        regs = [R(0.12, 0.27, 0.10, 0.14), R(0.24, 0.30, 0.08, 0.25)]
        self.assertEqual(len(caption_regions(regs, lines)), 1)

    def test_khong_chu_thich_thi_khong_gom_gi(self):
        self.assertEqual(caption_regions([R(0.1, 0.4, 0.2, 0.2)], [L(0.1, 0.3, 0.6, 'chữ thường')]), [])


class Dedup(unittest.TestCase):
    def test_iou_nhan_ra_hai_hop_gan_trung(self):
        self.assertGreater(_iou([0.1, 0.1, 0.2, 0.2], [0.11, 0.11, 0.2, 0.2]), 0.5)
        self.assertEqual(_iou([0.1, 0.1, 0.2, 0.2], [0.5, 0.5, 0.2, 0.2]), 0.0)


if __name__ == '__main__':
    unittest.main()
