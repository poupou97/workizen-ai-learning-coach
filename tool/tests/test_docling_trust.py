#!/usr/bin/env python3
"""CỔNG TIN CẬY cho đề xuất Docling (B2, chế độ bóng).

Kiến trúc Founder chốt: model nói CHỖ NÀO, sách nói ĐÓ LÀ GÌ. Cổng này chỉ
TIN khi có bằng chứng IN TRONG SÁCH; không đủ thì GIỮ LẠI.

⛔ Không tái dùng cổng của D: đo được, áp thẳng cổng D lên hộp Docling chặn
6/9 hộp có hại nhưng chặn NHẦM 30/93 hộp lành, vì hộp Docling đúng thì đương
nhiên chứa chữ (ô bảng, nhãn sơ đồ, lời bài hát).
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import docling_trust as dt  # noqa: E402


def cap(num, x, y, w=0.30, h=0.02, kind='hình'):
    return dict(kind=kind, num=num, x=x, y=y, w=w, h=h, text=f'Hình {num}. ...')


def item(box, label='text'):
    return dict(label=label, box=list(box), text='x')


class Adjacency(unittest.TestCase):
    def test_chu_thich_ngay_DUOI_vung(self):
        got = dt.adjacent_captions([0.1, 0.2, 0.4, 0.3], [cap('5.1', 0.15, 0.52)])
        self.assertEqual([a['num'] for a in got], ['5.1'])

    def test_chu_thich_ngay_TREN_vung(self):
        # Bảng SGK thường in «Bảng N.M» PHÍA TRÊN — chỉ nhận khi xét như BẢNG.
        got = dt.adjacent_captions([0.1, 0.3, 0.4, 0.3],
                                   [cap('2.1', 0.15, 0.26, kind='bảng')], kind='table')
        self.assertEqual([a['num'] for a in got], ['2.1'])

    def test_chu_thich_HINH_o_phia_TREN_thi_KHONG_tinh(self):
        """⭐ QUY ƯỚC IN CỦA SGK, KHÔNG PHẢI THẨM MỸ.

        Ca thật, nhìn tận mắt (Công nghệ 10 trang 95): câu thân bài «Hình 16.2.
        là ví dụ giao diện của phần mềm AutoCAD.» đứng TRÊN ảnh; chú thích thật
        «Hình 16.2. Giao diện của phần mềm AutoCAD 2021» nằm DƯỚI. Nhận cả phía
        trên thì cổng trích dẫn CÂU THÂN BÀI làm bằng chứng — lần ấy kết luận
        vẫn đúng nhờ có chú thích thật ở dưới, nhưng ở trang khác đó là một
        TRUSTED SAI.
        """
        got = dt.adjacent_captions([0.1, 0.3, 0.4, 0.3], [cap('16.2', 0.15, 0.26)])
        self.assertEqual(got, [])

    def test_BANG_thi_van_nhan_chu_thich_phia_tren(self):
        # Bảng in chú thích TRÊN; chặn cả hai phía là mất toàn bộ bảng.
        got = dt.adjacent_captions([0.1, 0.3, 0.4, 0.3],
                                   [cap('41.1', 0.15, 0.26, kind='bảng')], kind='table')
        self.assertEqual([a['num'] for a in got], ['41.1'])

    def test_chu_thich_XA_thi_khong_tinh(self):
        self.assertEqual(dt.adjacent_captions([0.1, 0.2, 0.4, 0.3], [cap('5.1', 0.15, 0.80)]), [])

    def test_chu_thich_khac_cot_thi_khong_tinh(self):
        self.assertEqual(dt.adjacent_captions([0.1, 0.2, 0.2, 0.3], [cap('5.1', 0.70, 0.52)]), [])


class Judge(unittest.TestCase):
    def test_co_chu_thich_ke_ben_thi_TIN(self):
        st, why, c = dt.judge([0.1, 0.2, 0.4, 0.3], anchors=[cap('5.1', 0.15, 0.52)])
        self.assertEqual(st, 'TRUSTED')
        self.assertEqual(c['num'], '5.1')

    def test_KHONG_co_bang_chung_thi_GIU_LAI(self):
        st, why, _ = dt.judge([0.1, 0.2, 0.4, 0.3], anchors=[])
        self.assertEqual(st, 'WITHHELD')

    def test_om_HAI_chu_thich_la_CONFLICT(self):
        # Vùng nuốt cả hình của người khác — đã gặp thật (LS&ĐL 6: Hình 5 + Hình 6).
        st, why, _ = dt.judge([0.1, 0.1, 0.8, 0.8],
                              anchors=[cap('5', 0.15, 0.40), cap('6', 0.15, 0.70)])
        self.assertEqual(st, 'CONFLICT')

    def test_chua_phan_tu_cau_truc_khac_la_CONFLICT(self):
        st, why, _ = dt.judge([0.05, 0.05, 0.9, 0.9], anchors=[],
                              items=[item((0.2, 0.2, 0.6, 0.3), 'section_header')])
        self.assertEqual(st, 'CONFLICT')

    def test_CHINH_NO_khong_tinh_la_chua_phan_tu_khac(self):
        # ⚠ Không loại chính nó thì MỌI hộp bảng tự-mâu-thuẫn: đo được 7/7 bảng
        # bị chặn oan trước khi sửa.
        box = [0.1, 0.2, 0.4, 0.3]
        st, why, _ = dt.judge(box, anchors=[cap('2.1', 0.15, 0.16, kind='bảng')],
                              items=[item((0.1, 0.2, 0.5, 0.5), 'table')],
                              kind='table')
        self.assertEqual(st, 'TRUSTED')

    def test_hop_rong_thi_GIU_LAI(self):
        self.assertEqual(dt.judge([0.1, 0.2, 0, 0.3], anchors=[])[0], 'WITHHELD')


class Doctrine(unittest.TestCase):
    def test_CHU_TRONG_VUNG_KHONG_bi_coi_la_lan_chu(self):
        """Ô bảng, nhãn trục, lời bài hát là chữ CỦA hình — cổng không được
        phạt vì có chữ bên trong."""
        st, _, _ = dt.judge([0.1, 0.2, 0.6, 0.4], anchors=[cap('9.6', 0.2, 0.62)],
                            items=[])
        self.assertEqual(st, 'TRUSTED')


if __name__ == '__main__':
    unittest.main()
