#!/usr/bin/env python3
"""B3 — CỔNG CHẠY TRÊN CẢ TRANG, không xét từng hộp rời.

Vì sao phải xét cả trang: «chú thích này đang được MẤY vùng viện dẫn» là dấu
hiệu duy nhất cho biết đây là CỤM HÌNH CON. Xét lẻ từng hộp thì không thấy —
và ba ảnh chó/mèo/gà sẽ lặng lẽ cùng mang một danh tính «Hình 6.1».
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import docling_gate as dg      # noqa: E402
import docling_identity as di  # noqa: E402


def L(x, w, y, text, h=0.015):
    return dict(x=x, w=w, y=y, h=h, text=text)


def pic(x0, y0, x1, y1):
    return dict(label='picture', box=[x0, y0, x1, y1], text='')


class CumHinhCon(unittest.TestCase):
    """Ba ảnh xếp hàng ngang, mỗi ảnh một nhãn con, một chú thích chung."""

    ROW = [pic(0.10, 0.30, 0.35, 0.60),
           pic(0.38, 0.30, 0.63, 0.60),
           pic(0.66, 0.30, 0.91, 0.60)]

    def _lines(self, subs=True):
        ls = [L(0.10, 0.60, 0.10, 'Các loại động vật cảnh được nuôi nhiều hiện nay')]
        if subs:
            ls += [L(0.10, 0.24, 0.62, 'a) Chó Bắc Kinh lai Nhật'),
                   L(0.38, 0.24, 0.62, 'b) Mèo Anh lông ngắn'),
                   L(0.66, 0.24, 0.62, 'c) Gà tre Tân Châu')]
        # ⚠ 0,64 chứ không phải 0,66: đáy ảnh 0,60 + `CAPTION_GAP` 0,06 rơi
        # đúng biên, và 0,66-0,60 trong dấu phẩy động lớn hơn 0,06 một chút
        # ⇒ fixture bị phép đo khoảng cách loại trước khi chạm luật đang kiểm.
        ls.append(L(0.22, 0.56, 0.64, 'Hình 6.1. Một số loại động vật cảnh phổ biến'))
        return ls

    def _run(self, subs):
        rec = dict(book='b', page=25, items=list(self.ROW))
        return dg.judge_page(rec, self._lines(subs))

    def test_co_nhan_con_in_thi_moi_anh_mot_danh_tinh_rieng(self):
        got = self._run(True)
        self.assertEqual([r['region_trust'] for r in got], ['TRUSTED'] * 3)
        self.assertEqual([r['identity'] for r in got], [di.RESOLVED] * 3)
        self.assertEqual([r['ident']['sub'] for r in got],
                         ['a) Chó Bắc Kinh lai Nhật', 'b) Mèo Anh lông ngắn',
                          'c) Gà tre Tân Châu'])
        self.assertTrue(all(r['readable'] for r in got))

    def test_KHONG_co_nhan_con_thi_vung_van_tin_nhung_danh_tinh_GIU_LAI(self):
        """⭐ Trạng thái hợp lệ: REGION_TRUST = TRUSTED, IDENTITY_LINK = WITHHELD.

        Và vì không nói được đây là mảnh nào của cụm, ảnh KHÔNG vào dòng đọc."""
        got = self._run(False)
        self.assertEqual([r['region_trust'] for r in got], ['TRUSTED'] * 3)
        self.assertEqual([r['identity'] for r in got], [di.WITHHELD] * 3)
        self.assertEqual([r['shared'] for r in got], [3, 3, 3])
        self.assertFalse(any(r['readable'] for r in got))

    def test_mot_anh_mot_chu_thich_thi_noi_thang_khong_can_nhan_con(self):
        rec = dict(book='b', page=25, items=[pic(0.10, 0.30, 0.91, 0.60)])
        ls = [L(0.22, 0.56, 0.62, 'Hình 6.1. Một số loại động vật cảnh phổ biến')]
        got = dg.judge_page(rec, ls)
        self.assertEqual(got[0]['identity'], di.RESOLVED)
        self.assertEqual(got[0]['shared'], 1)
        self.assertTrue(got[0]['readable'])


class ChiXetHinhVaBang(unittest.TestCase):
    def test_bo_qua_moi_nhan_khac(self):
        rec = dict(book='b', page=1, items=[
            dict(label='text', box=[0.1, 0.1, 0.9, 0.2], text='x'),
            dict(label='section_header', box=[0.1, 0.3, 0.9, 0.4], text='y')])
        self.assertEqual(dg.judge_page(rec, []), [])


if __name__ == '__main__':
    unittest.main()
