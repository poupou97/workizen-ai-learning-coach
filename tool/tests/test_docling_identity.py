#!/usr/bin/env python3
"""B3 — `REGION_TRUST != IDENTITY_LINK` là BẤT BIẾN, không phải tuỳ chọn.

Nhân chứng thật: Công nghệ 11 (chuyên đề) trang 25 — «Hình 6.1. Một số loại
động vật cảnh phổ biến» là chú thích CHUNG cho ba ảnh, mỗi ảnh có nhãn con in
ngay dưới. Gán cả ba cùng «Hình 6.1» thì không bịa, nhưng mất đúng thứ trẻ cần.

«SAI TÊN > THIẾU TÊN».
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import docling_identity as di  # noqa: E402


def L(x, w, y, text, h=0.02):
    return dict(x=x, w=w, y=y, h=h, text=text)


def cap(num, x, y, w=0.6, h=0.02):
    return dict(kind='hình', num=num, x=x, y=y, w=w, h=h,
                text=f'Hình {num}. Một số loại động vật cảnh phổ biến')


class NhanCon(unittest.TestCase):
    def test_nhan_dong_nhan_con_in_trong_sach(self):
        ls = [L(0.10, 0.25, 0.60, 'a) Chó Bắc Kinh lai Nhật')]
        got = di.sublabels(ls, {id(ls[0]): 1})
        self.assertEqual([(s['letter'], s['text']) for s in got],
                         [('a', 'a) Chó Bắc Kinh lai Nhật')])

    def test_DE_BAI_trong_doan_van_KHONG_phai_nhan_con(self):
        """«b) Vì sao…» trong khối nhiều dòng là ĐỀ BÀI, không phải nhãn ảnh."""
        ls = [L(0.10, 0.75, 0.60, 'b) Vì sao nói Liên Xô trở thành chỗ dựa')]
        self.assertEqual(di.sublabels(ls, {id(ls[0]): 5}), [])

    def test_chu_thich_KHONG_bi_doc_nham_thanh_nhan_con(self):
        ls = [L(0.10, 0.60, 0.60, 'Hình 6.1. Một số loại động vật cảnh')]
        self.assertEqual(di.sublabels(ls, {id(ls[0]): 1}), [])


class NhanConCuaVung(unittest.TestCase):
    def _sub(self, x, y, letter='a'):
        return dict(letter=letter, text=f'{letter}) Chó Bắc Kinh', x=x, y=y,
                    w=0.25, h=0.02)

    def test_lay_nhan_con_ngay_duoi_va_chong_ngang(self):
        got = di.sublabel_for((0.10, 0.30, 0.25, 0.20), [self._sub(0.10, 0.52)])
        self.assertEqual(got['letter'], 'a')

    def test_nhan_con_LECH_COT_thi_khong_tinh(self):
        # Nhãn của ảnh bên cạnh, không phải của ảnh này.
        self.assertIsNone(di.sublabel_for((0.10, 0.30, 0.25, 0.20),
                                          [self._sub(0.70, 0.52)]))

    def test_nhan_con_NAM_DUOI_chu_thich_chung_thi_khong_tinh(self):
        """Nhãn con thuộc về ảnh; thứ nằm dưới chú thích chung là của cụm SAU.

        ⚠ Fixture phải nằm TRONG tầm `SUB_GAP`, nếu không nó bị phép đo khoảng
        cách loại trước và phép kiểm này không hề chạm tới luật đang kiểm —
        đột biến sống sót đúng vì lý do ấy ở lần viết đầu."""
        c = cap('6.1', 0.10, 0.52)
        box, sub = (0.10, 0.30, 0.25, 0.20), self._sub(0.10, 0.54)
        self.assertIsNotNone(di.sublabel_for(box, [sub]))          # trong tầm
        self.assertIsNone(di.sublabel_for(box, [sub], cap=c))      # nhưng dưới chú thích


class NoiDanhTinh(unittest.TestCase):
    def test_chu_thich_RIENG_thi_noi_thang(self):
        st, ident, _ = di.link((0.1, 0.2, 0.4, 0.3), caption=cap('2.1', 0.1, 0.52),
                               shared=1, subs=[])
        self.assertEqual(st, di.RESOLVED)
        self.assertIsNone(ident['sub'])

    def test_chu_thich_CHUNG_co_nhan_con_in_thi_noi_ca_hai(self):
        s = dict(letter='b', text='b) Mèo Anh lông ngắn', x=0.1, y=0.52,
                 w=0.25, h=0.02)
        st, ident, _ = di.link((0.1, 0.2, 0.4, 0.3), caption=cap('6.1', 0.1, 0.56),
                               shared=3, subs=[s])
        self.assertEqual(st, di.RESOLVED)
        self.assertEqual(ident['num'], '6.1')
        self.assertEqual(ident['sub'], 'b) Mèo Anh lông ngắn')

    def test_chu_thich_CHUNG_khong_co_nhan_con_thi_GIU_LAI_danh_tinh(self):
        """⭐ KHÔNG BỊA «Hình 6.1a». Không có nhãn in thì giữ lại danh tính."""
        st, ident, why = di.link((0.1, 0.2, 0.4, 0.3), caption=cap('6.1', 0.1, 0.52),
                                 shared=3, subs=[])
        self.assertEqual(st, di.WITHHELD)
        self.assertIsNone(ident)

    def test_khong_co_chu_thich_thi_GIU_LAI(self):
        st, ident, _ = di.link((0.1, 0.2, 0.4, 0.3), caption=None, shared=0, subs=[])
        self.assertEqual(st, di.WITHHELD)


class HaiPhepDoTachNhau(unittest.TestCase):
    def test_vung_dang_tin_ma_danh_tinh_GIU_LAI_la_trang_thai_HOP_LE(self):
        self.assertFalse(di.readable('TRUSTED', di.WITHHELD, shared=3))

    def test_danh_tinh_KHONG_nang_duoc_vung_chua_dang_tin(self):
        self.assertFalse(di.readable('WITHHELD', di.RESOLVED, shared=1))
        self.assertFalse(di.readable('CONFLICT', di.RESOLVED, shared=1))

    def test_du_ca_hai_thi_vao_dong_doc(self):
        self.assertTrue(di.readable('TRUSTED', di.RESOLVED, shared=1))


if __name__ == '__main__':
    unittest.main()
