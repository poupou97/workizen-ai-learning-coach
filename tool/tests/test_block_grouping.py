#!/usr/bin/env python3
"""GOM KHỐI — chống TRÔI NGANG BẮC CẦU.

Luật cũ chỉ so dòng mới với DÒNG CUỐI của khối, nên A → B → C nối được hết dù
A và C không hề chồng nhau. Máy thật: Vật lí 11 trang 21 sinh một khối 23 dòng
trải `x=0.092..0.900`, nuốt cả cột trái lẫn dải hình.

Bất biến của một CỘT CHỮ: không tồn tại hai dòng rời hẳn nhau trong cùng khối.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
from lesson_reading import blocks, read_order  # noqa: E402
import block_grouping as bg  # noqa: E402


def L(x, w, y, text='x', h=0.02):
    return dict(x=x, w=w, y=y, h=h, text=text)


def _texts(bs):
    return [' '.join(l['text'] for l in b) for b in bs]


class NoTransitiveDrift(unittest.TestCase):

    def test_A_B_C_khong_duoc_noi_thanh_MOT_khoi(self):
        # A(.09–.50) chồng B(.46–.90); B chồng C(.86–.95); A và C RỜI HẲN.
        ls = [L(0.09, 0.41, 0.10, 'A'), L(0.46, 0.44, 0.12, 'B'), L(0.86, 0.09, 0.14, 'C')]
        bs = blocks(ls)
        for b in bs:
            self.assertNotIn('A', [l['text'] for l in b] and
                             ([l['text'] for l in b] if 'C' in [l['text'] for l in b] else []))
        self.assertEqual(bg.disjoint_pairs(bs), 0)

    def test_cot_chu_that_van_lien_mot_khoi(self):
        ls = [L(0.10, 0.40, 0.10, 'dòng một'), L(0.10, 0.40, 0.13, 'dòng hai'),
              L(0.10, 0.25, 0.16, 'dòng ba')]
        self.assertEqual(len(blocks(ls)), 1)

    def test_hai_cot_song_song_KHONG_bi_dan_vao_nhau(self):
        ls = [L(0.08, 0.35, 0.10, 'trái1'), L(0.55, 0.35, 0.10, 'phải1'),
              L(0.08, 0.35, 0.13, 'trái2'), L(0.55, 0.35, 0.13, 'phải2')]
        bs = blocks(ls)
        self.assertEqual(len(bs), 2)
        self.assertEqual(bg.disjoint_pairs(bs), 0)

    def test_khung_phu_ben_le_la_KHOI_RIENG(self):
        # ⭐ Lỗi #141: khung niên biểu bên phải chen vào giữa câu thân bài.
        ls = [L(0.08, 0.45, 0.10, 'bảo vệ con người trước những tác động'),
              L(0.70, 0.22, 0.11, 'KHOẢNG TÁM NGHÌN NĂM'),
              L(0.08, 0.45, 0.13, 'xấu của thiên nhiên')]
        bs = blocks(ls)
        self.assertEqual(len(bs), 2)
        body = [t for t in _texts(bs) if 'bảo vệ' in t][0]
        self.assertNotIn('TÁM NGHÌN NĂM', body)

    def test_thu_tu_doc_van_la_than_bai_TRUOC_khung_phu(self):
        ls = [L(0.08, 0.45, 0.10, 'thân1'), L(0.70, 0.22, 0.11, 'KHUNG'),
              L(0.08, 0.45, 0.13, 'thân2')]
        self.assertEqual([l['text'] for l in read_order(ls)],
                         ['thân1', 'thân2', 'KHUNG'])


class Invariant(unittest.TestCase):

    def test_bat_bien_khong_co_hai_dong_roi_han_trong_mot_khoi(self):
        ls = [L(0.09, 0.41, 0.10), L(0.46, 0.44, 0.12), L(0.86, 0.09, 0.14),
              L(0.10, 0.40, 0.16), L(0.60, 0.30, 0.18)]
        self.assertEqual(bg.disjoint_pairs(blocks(ls)), 0)

    def test_nhan_CAP_DONG_ROI_bat_duoc_kieu_hong_ma_nhan_cum_bo_lot(self):
        # Nhãn cũ (≥2 CỤM rời, mỗi cụm ≥2 dòng) bỏ lọt khối rộng nuốt dòng hẹp.
        wide = [L(0.05, 0.90, 0.10), L(0.05, 0.90, 0.13), L(0.80, 0.05, 0.16),
                L(0.06, 0.04, 0.19)]
        self.assertEqual(bg.false_merges([wide]), 0)      # nhãn cũ: không thấy gì
        self.assertEqual(bg.disjoint_pairs([wide]), 1)    # nhãn mới: bắt được

    def test_khoi_mot_dong_khong_bao_gio_vi_pham(self):
        self.assertEqual(bg.disjoint_pairs([[L(0.1, 0.2, 0.1)]]), 0)


if __name__ == '__main__':
    unittest.main()
