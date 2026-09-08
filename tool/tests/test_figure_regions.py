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
from lesson_figures import caption_regions, _line_crosses, _iou, _swallows  # noqa: E402


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


class AnchorsMoRong(unittest.TestCase):
    """B2.1 — NỚI MẪU NHẬN BẰNG CHỨNG IN, KHÔNG HẠ CHUẨN BẰNG CHỨNG.

    Census 72 đề xuất bị giữ (diện tích ≥0,02) trên 51 trang: 3 ca là chú thích
    ĐÁNH SỐ MỘT CẤP thật («Hình 2», «Hình 10»), 13 ca là chú thích kết bằng
    CHỈ SỐ NGUỒN («Thêu⁽⁴⁾»). Cả hai vẫn là chữ SÁCH TỰ IN.
    """

    def test_mac_dinh_KHONG_doi_nghia_so_cu(self):
        # Mọi phép đo đã công bố chạy với `extended=False`. Nới mẫu KHÔNG được
        # âm thầm làm số cũ mang nghĩa khác.
        ls = [L(0.1, 0.3, 0.5, 'Hình 2. Cột kinh Phật thời Tiền Lê')]
        self.assertEqual(ff.caption_anchors(ls), [])

    def test_danh_so_MOT_CAP_la_bang_chung_in(self):
        ls = [L(0.1, 0.3, 0.5, 'Hình 2. Cột kinh Phật thời Tiền Lê')]
        got = ff.caption_anchors(ls, extended=True, block_lines={id(ls[0]): 1})
        self.assertEqual([(a['kind'], a['num'], a['family']) for a in got],
                         [('hình', '2', 'NUMBERED')])

    def test_hai_cap_van_doc_ra_hai_cap(self):
        ls = [L(0.1, 0.3, 0.5, 'Hình 5.1. Con lắc đơn')]
        got = ff.caption_anchors(ls, extended=True, block_lines={id(ls[0]): 1})
        self.assertEqual(got[0]['num'], '5.1')

    def test_so_dai_hon_hai_chu_so_KHONG_phai_chu_thich(self):
        # «Hình 123» không phải cách đánh số của SGK; chặn để không nhận bừa.
        ls = [L(0.1, 0.3, 0.5, 'Hình 123 xyz')]
        self.assertEqual(ff.caption_anchors(ls, extended=True,
                                            block_lines={id(ls[0]): 1}), [])

    def test_chu_thich_co_DAU_NGUON_la_bang_chung_in(self):
        ls = [L(0.1, 0.3, 0.5, 'Thực hành tạo dáng chụp ảnh(2)')]
        got = ff.caption_anchors(ls, extended=True, block_lines={id(ls[0]): 1})
        self.assertEqual([(a['family'], a['num']) for a in got], [('FOOTNOTE', None)])

    def test_THAM_CHIEU_trong_doan_van_KHONG_phai_chu_thich(self):
        """⭐ «NEARBY TEXT != CAPTION». Một câu thân bài mở đầu bằng «Hình 2 là
        ví dụ…» nằm trong khối NHIỀU DÒNG — đó là tham chiếu, không phải chú
        thích. Khác biệt này do census tìm ra, không phải ngưỡng ước lệ.

        ⚠ Chỉ ràng buộc HAI HỌ MỚI. Mẫu hai cấp «Hình 16.2» cũ KHÔNG bị chặn ở
        đây — cố tình, để số đã công bố không đổi nghĩa. Câu thân bài mở đầu
        bằng «Hình 16.2 là…» được chặn ở TẦNG KHÁC: quy ước in trong
        `docling_trust.adjacent_captions` (chú thích hình nằm DƯỚI hình).
        """
        ls = [L(0.1, 0.7, 0.5, 'Hình 2 là ví dụ giao diện của phần mềm')]
        self.assertEqual(ff.caption_anchors(ls, extended=True,
                                            block_lines={id(ls[0]): 6}), [])

    def test_mau_HAI_CAP_cu_KHONG_bi_cong_moi_rang_buoc(self):
        ls = [L(0.1, 0.7, 0.5, 'Hình 16.2 là ví dụ giao diện của phần mềm')]
        got = ff.caption_anchors(ls, extended=True, block_lines={id(ls[0]): 6})
        self.assertEqual([a['num'] for a in got], ['16.2'])

    def test_O_BANG_SO_LIEU_khong_phai_chu_thich_co_dau_nguon(self):
        """⭐ TRUSTED SAI thật, cầu nối bóng tìm ra (Toán 11 trang 67): ô đầu cột
        «[160; 165)» của bảng số liệu có ĐÚNG HÌNH DẠNG «…số)» nên được nhận làm
        chú thích, và bảo lãnh cho một con mascot trang trí. Sách không hề nói
        bức ấy tên là gì. Chú thích là một CÁI TÊN — phải mở đầu bằng chữ cái."""
        for t in ('[160; 165)', '[0,5; 10,5)', '110)', ',maxsplit=2)'):
            ls = [L(0.1, 0.2, 0.5, t)]
            self.assertEqual(ff.caption_anchors(ls, extended=True,
                                                block_lines={id(ls[0]): 1}), [], t)

    def test_dau_nguon_trong_doan_van_cung_KHONG_tinh(self):
        ls = [L(0.1, 0.7, 0.5, 'theo số liệu đã nêu ở trên (2)')]
        self.assertEqual(ff.caption_anchors(ls, extended=True,
                                            block_lines={id(ls[0]): 6}), [])

    def test_khong_co_block_lines_thi_coi_nhu_khoi_MOT_dong(self):
        ls = [L(0.1, 0.3, 0.5, 'Hình 2. Cột kinh Phật')]
        self.assertEqual(len(ff.caption_anchors(ls, extended=True)), 1)


class DemDongCuaKhoi(unittest.TestCase):
    def test_dem_theo_KHOI_chu_khong_theo_trang(self):
        ls = [L(0.10, 0.40, 0.30, 'một câu dài của thân bài'),
              L(0.10, 0.40, 0.33, 'câu thứ hai cùng khối'),
              L(0.10, 0.30, 0.70, 'Hình 2. Chú thích đứng riêng')]
        got = ff.block_line_counts(ls)
        self.assertEqual(got[id(ls[0])], 2)
        self.assertEqual(got[id(ls[2])], 1)


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


class WithholdD(unittest.TestCase):
    """⭐ PHƯƠNG ÁN D — không chứng minh được quyền sở hữu thì GIỮ LẠI.

    Bộ kiểm gán tay (#160): với hình học dòng OCR + thành phần mực, KHÔNG luật
    nào vừa nhận đủ chữ-của-hình vừa không nuốt văn xuôi. Tín hiệu sạch duy
    nhất phủ 11%. Nên hợp KHÔNG được nuốt một khối chữ chưa chứng minh được.

    «Thiếu hình» sửa được vòng sau; «hình nuốt mất câu» thì trẻ đọc phải ngay.
    """

    def test_swallows_do_theo_dien_tich_khoi_chu(self):
        self.assertTrue(_swallows([0.1, 0.1, 0.5, 0.5], (0.2, 0.2, 0.3, 0.3)))
        self.assertFalse(_swallows([0.1, 0.1, 0.5, 0.5], (0.9, 0.9, 0.99, 0.99)))

    def test_hop_NUOT_khoi_chu_chua_chung_minh_thi_BO(self):
        # ⚠ Khối chữ ở CỘT KHÁC nên KHÔNG chặn được dải (chặn dải chỉ xét khối
        # cùng cột với chú thích) — nhưng hợp trải ngang vẫn trùm lên nó.
        # Đây đúng là 31/120 ca đo được mà chặn-dải bỏ lọt.
        lines = [L(0.10, 0.22, 0.60, 'Hình 1.1. Sơ đồ mạch điện'),
                 L(0.33, 0.07, 0.42, 'một dòng'), L(0.33, 0.07, 0.45, 'dòng hai')]
        regs = [R(0.12, 0.40, 0.08, 0.10), R(0.41, 0.40, 0.05, 0.10)]
        self.assertEqual(caption_regions(regs, lines), [])

    def test_ca_do_duoc_31_tren_120_la_LOAI_NAY(self):
        """Ghi lại: chặn dải bảo vệ phía TRÊN, cổng nuốt bảo vệ phía TRONG."""
        lines = [L(0.10, 0.22, 0.60, 'Hình 1.1. Sơ đồ mạch điện'),
                 L(0.33, 0.07, 0.42, 'một dòng'), L(0.33, 0.07, 0.45, 'dòng hai')]
        regs = [R(0.12, 0.40, 0.08, 0.10)]        # chỉ một phía ⇒ không trùm
        self.assertEqual(len(caption_regions(regs, lines)), 1)

    def test_khong_co_khoi_chu_nao_bi_nuot_thi_GIU_vung(self):
        lines = [L(0.10, 0.30, 0.60, 'Hình 1.1. Sơ đồ mạch điện'),
                 L(0.70, 0.20, 0.36, 'chữ ở cột khác')]
        regs = [R(0.12, 0.30, 0.10, 0.08), R(0.13, 0.45, 0.12, 0.10)]
        self.assertEqual(len(caption_regions(regs, lines)), 1)


class Dedup(unittest.TestCase):
    def test_iou_nhan_ra_hai_hop_gan_trung(self):
        self.assertGreater(_iou([0.1, 0.1, 0.2, 0.2], [0.11, 0.11, 0.2, 0.2]), 0.5)
        self.assertEqual(_iou([0.1, 0.1, 0.2, 0.2], [0.5, 0.5, 0.2, 0.2]), 0.0)


if __name__ == '__main__':
    unittest.main()
