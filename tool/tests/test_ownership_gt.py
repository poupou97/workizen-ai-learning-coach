#!/usr/bin/env python3
"""QUYỀN SỞ HỮU CHỮ — kết luận ĐO ĐƯỢC, ghim lại để vòng sau không lật ngầm.

Bộ kiểm gán BẰNG MẮT trên 5 trang nguồn (88 khối, 77 khối có nhãn PROSE/VISUAL),
phủ: đồ thị nét mảnh + công thức · bảng + ảnh chú thích · bảng trong khung hoạt
động · ảnh + khung phụ (họ lỗi #141) · hình học.

⛔ Nhãn KHÔNG được suy từ bề rộng, số dòng, detector hay prose-bound — nếu suy
thì phép chấm chỉ soi gương chính nó. Ba vòng liền tôi đã dính đúng bẫy ấy:
  · #158 nhãn «≥2 cụm rời» bỏ lọt khối rộng nuốt dòng hẹp;
  · vòng ownership lần 1 định nghĩa PROSE có kèm «dòng ≥ LONG_LINE» rồi chấm
    luật theo bề rộng — 0 dương-tính-giả là do ĐỊNH NGHĨA;
  · lần 2 định nghĩa PROSE = «≥3 dòng» rồi chấm luật «≤2 dòng» — cũng vòng quanh.
Trang Sinh học 11 chứng minh cả hai định nghĩa ấy sai: MỘT khối 22 dòng là toàn
bộ ruột BẢNG, không phải văn xuôi.

Kết luận ghim ở đây: với biểu diễn tri giác hiện có (hình học dòng OCR + thành
phần mực), quyền sở hữu chữ KHÔNG khôi phục được đáng tin.
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'data', 'ownership-gt.json')


def load():
    with open(GT, encoding='utf-8') as fh:
        return json.load(fh)


def score(rows, rule):
    V = [r for r in rows if r['lab'] == 'VISUAL']
    P = [r for r in rows if r['lab'] == 'PROSE']
    tp = sum(1 for r in V if rule(r))
    fp = sum(1 for r in P if rule(r))
    return tp, len(V), fp, len(P)


class GroundTruth(unittest.TestCase):

    def test_bo_kiem_co_du_hai_phia_va_du_ho(self):
        d = load()
        self.assertGreaterEqual(len(d['pages']), 5)
        labs = [r['lab'] for r in d['blocks']]
        self.assertGreaterEqual(labs.count('VISUAL'), 30)
        self.assertGreaterEqual(labs.count('PROSE'), 30)

    def test_co_ca_ca_KHUNG_PHU_hep_nhieu_dong_ma_van_la_chu_doc(self):
        """⭐ Ca phản chứng của mọi luật «hẹp ⇒ chữ của hình»."""
        d = load()
        cn = [r for r in d['blocks'] if r['page'] == 'cn9']
        narrow_prose = [r for r in cn
                        if r['lab'] == 'PROSE' and r['wmax'] < 0.25 and r['nlines'] >= 3]
        self.assertTrue(narrow_prose, 'thiếu ca khung phụ — bộ kiểm mất sức phản chứng')


class Conclusions(unittest.TestCase):
    """Hai kết luận này là LÝ DO không ship luật ownership nào."""

    def setUp(self):
        d = load()
        self.dev = [r for r in d['blocks'] if r['split'] == 'dev']

    def test_luat_theo_BE_RONG_pha_van_xuoi(self):
        # Recall cao nhưng nuốt hơn một phần tư khối chữ đọc ⇒ crop ăn vào câu.
        tp, nv, fp, np_ = score(self.dev, lambda r: r['wmax'] < 0.25)
        self.assertGreater(tp / nv, 0.9)
        self.assertGreater(fp / np_, 0.25)

    def test_luat_NAM_TRONG_MUC_HINH_chinh_xac_nhung_phu_qua_thap(self):
        # Tín hiệu DUY NHẤT không phá văn xuôi — nhưng chỉ thấy được chữ của
        # những hình mà bộ dò ĐÃ tìm ra, nên phủ rất thấp.
        tp, nv, fp, np_ = score(self.dev, lambda r: r['inink'])
        self.assertEqual(fp, 0)
        self.assertLess(tp / nv, 0.20)

    def test_khong_luat_nao_vua_phu_cao_vua_khong_pha_van_xuoi(self):
        rules = [
            lambda r: r['wmax'] < 0.25,
            lambda r: r['wmax'] < 0.15,
            lambda r: r['inink'],
            lambda r: r['incap'],
            lambda r: r['wmax'] < 0.25 and r['incap'],
            lambda r: r['inink'] or (r['wmax'] < 0.15 and r['incap']),
        ]
        for f in rules:
            tp, nv, fp, np_ = score(self.dev, f)
            good = tp / nv >= 0.7 and fp / np_ <= 0.05
            self.assertFalse(good, 'có luật đạt cả hai — cập nhật lại kết luận')


if __name__ == '__main__':
    unittest.main()
