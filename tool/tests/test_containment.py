#!/usr/bin/env python3
"""VÙNG NUỐT VẬT THỂ KHÁC — hình học đề cử, BẰNG CHỨNG IN phán quyết.

Hai ca thật sinh ra chốt này: khung «Hình 2.3» nuốt trọn «Hình 2.2» (Tin học 6
tr.20), và khung «Hình 5.4» nuốt sơ đồ quy trình + hộp «EM CÓ BIẾT» (Chuyên đề
Hoá 12 tr.25).
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import containment as ct  # noqa: E402

CAP = 'Hình 2.3. Ví dụ cách kết nối 5 máy tính thành một mạng'
KHAC = 'Hình 2.2. Các thiết bị được nối vào mạng'
KHUNG = [0.10, 0.10, 0.80, 0.60]      # khung Docling ứng cử
HINH_D = [0.10, 0.40, 0.80, 0.30]     # hình D nó đòi thay


def line(text, box=(0.20, 0.15, 0.40, 0.03)):
    return dict(text=text, x=box[0], y=box[1], w=box[2], h=box[3])


class NuotVatThe(unittest.TestCase):
    def call(self, **kw):
        kw.setdefault('anchors', ())
        kw.setdefault('d_figs', ())
        kw.setdefault('trusted', ())
        return ct.swallowed(KHUNG, CAP, HINH_D, **kw)

    # ── (1) sách in một TÊN KHÁC bên trong khung ─────────────────────────
    def test_chu_thich_IN_khac_ben_trong_thi_BAT(self):
        lab, why = self.call(anchors=[line(KHAC)])
        self.assertEqual(lab, 'CONTAINS_SEPARATE_CAPTION')
        self.assertEqual(why, KHAC)

    def test_chu_thich_CUA_CHINH_NO_thi_khong_bat(self):
        """Chú thích của chính khung nằm trong khung là chuyện thường."""
        self.assertEqual(self.call(anchors=[line(CAP)])[0], None)

    def test_chu_thich_khac_KHOANG_TRANG_HOA_THUONG_van_la_mot(self):
        self.assertIsNone(self.call(anchors=[line('  hình 2.3.  VÍ DỤ CÁCH KẾT '
                                                  'NỐI 5 MÁY TÍNH THÀNH MỘT MẠNG ')])[0])

    def test_chu_thich_khac_NGOAI_khung_thi_khong_bat(self):
        """Chú thích của hình bên cạnh, nằm ngoài — không phải bị nuốt."""
        self.assertIsNone(self.call(anchors=[line(KHAC, (0.20, 0.85, 0.40, 0.03))])[0])

    # ── (2) hình NGUỒN khác có tên riêng ─────────────────────────────────
    def test_hinh_D_khac_CO_TEN_ben_trong_thi_BAT(self):
        f = dict(bbox=[0.15, 0.15, 0.30, 0.20], caption=KHAC)
        lab, why = self.call(d_figs=[f])
        self.assertEqual(lab, 'CONTAINS_OTHER_NAMED_VISUAL')
        self.assertEqual(why, KHAC)

    def test_hinh_D_khac_KHONG_CO_TEN_thi_khong_bat(self):
        """Không tên thì không chứng minh được là vật thể riêng — có thể là một
        mảnh của chính hình này, hoặc đồ trang trí. Hỏng về phía CHO QUA ở đây
        vì chốt này hỏng về phía GIỮ D ở chỗ khác."""
        f = dict(bbox=[0.15, 0.15, 0.30, 0.20], caption=None)
        self.assertIsNone(self.call(d_figs=[f])[0])

    def test_CHINH_hinh_D_dang_bi_thay_thi_khong_tinh(self):
        f = dict(bbox=list(HINH_D), caption='Tên gì đó khác hẳn')
        self.assertIsNone(self.call(d_figs=[f])[0])

    # ── (3) vùng đáng tin khác đã giải danh tính riêng ───────────────────
    def test_vung_dang_tin_khac_ben_trong_thi_BAT(self):
        r = dict(box=[0.15, 0.15, 0.30, 0.20], ident=dict(text=KHAC))
        self.assertEqual(self.call(trusted=[r])[0], 'CONTAINS_OTHER_TRUSTED_REGION')

    # ── hình học: mẫu số phải là VẬT BỊ NUỐT ─────────────────────────────
    def test_vat_NHO_nam_gon_trong_khung_TO_van_phai_bat(self):
        """⚠ Lấy mẫu số là diện tích KHUNG thì vật nhỏ luôn ra tỉ lệ bé và không
        bao giờ bị bắt — đúng lỗi đã phải sửa ở `table_ownership`."""
        tiny = dict(bbox=[0.20, 0.20, 0.04, 0.03], caption=KHAC)
        self.assertEqual(self.call(d_figs=[tiny])[0], 'CONTAINS_OTHER_NAMED_VISUAL')

    def test_chi_CHONG_MOT_PHAN_thi_khong_phai_bi_nuot(self):
        """Hình bên cạnh thò một góc vào khung không phải là bị nuốt."""
        half = dict(bbox=[0.80, 0.15, 0.30, 0.20], caption=KHAC)
        self.assertIsNone(self.call(d_figs=[half])[0])

    # ── (4) không có gì để tra ───────────────────────────────────────────
    def test_KHONG_co_du_lieu_dong_ma_khung_PHINH_thi_AMBIGUOUS(self):
        lab, _ = ct.swallowed(KHUNG, CAP, [0.10, 0.40, 0.30, 0.20],
                              have_lines=False)
        self.assertEqual(lab, 'AMBIGUOUS_CONTAINMENT')

    def test_KHONG_co_du_lieu_dong_ma_khung_KHONG_phinh_thi_sach(self):
        lab, _ = ct.swallowed(KHUNG, CAP, [0.10, 0.12, 0.78, 0.56],
                              have_lines=False)
        self.assertIsNone(lab)

    def test_CO_du_lieu_dong_ma_khong_thay_gi_thi_SACH(self):
        """Có tra mà không thấy vật thứ hai ⇒ đã giải được, không phải mơ hồ."""
        lab, _ = ct.swallowed(KHUNG, CAP, [0.10, 0.40, 0.30, 0.20],
                              anchors=[line(CAP)], have_lines=True)
        self.assertIsNone(lab)


if __name__ == '__main__':
    unittest.main()
