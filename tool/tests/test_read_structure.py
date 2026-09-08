#!/usr/bin/env python3
"""CẤU TRÚC ĐỌC — phân họ nguyên nhân cho bài quá dài, bằng DẤU HIỆU IN TRONG SÁCH.

Không ngưỡng ước lệ: mỗi họ dựa trên chữ mà sách tự in ra (mốc đơn vị con,
số bài khác, dải trang chồng nhau).
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import read_structure as rs  # noqa: E402


class Subunits(unittest.TestCase):
    def test_moc_don_vi_con_do_chinh_sach_in_ra(self):
        # Ngữ văn 11 Bài 1: 45 trang vì sách gộp «VĂN BẢN 1/2 · ĐỌC · VIẾT ·
        # NÓI VÀ NGHE» vào một «Bài».
        t = 'VĂN BẢN 1 ... ĐỌC ... VĂN BẢN 2 ... VIẾT ... NÓI VÀ NGHE'
        m = rs.subunit_marks(t)
        self.assertEqual(m['VAN_BAN'], 2)
        self.assertEqual(m['NOI_NGHE'], 1)

    def test_khong_bat_chu_nam_trong_tu_khac(self):
        # «ĐỌC» phải là mốc đứng riêng, không phải một phần của chữ khác.
        self.assertNotIn('DOC', rs.subunit_marks('ĐỌCHIỂU văn bản'))


class OtherLessons(unittest.TestCase):
    def test_bo_qua_so_bai_cua_chinh_no(self):
        self.assertEqual(rs.other_lesson_numbers('Bài 5 nói về ...', 5), [])

    def test_bat_duoc_so_bai_la(self):
        self.assertEqual(rs.other_lesson_numbers('Bài 5 ... Bài 6 ... Bài 7', 5),
                         [6, 7])


class Ranges(unittest.TestCase):
    def test_chong_dung_MOT_trang_khong_phai_loi(self):
        # SGK in bài trước kết ở nửa trên, bài sau mở ở nửa dưới CÙNG trang.
        rows = [('b', 1, 5, 10), ('b', 2, 10, 15)]
        self.assertEqual(rs.overlaps(rows), set())

    def test_chong_dung_SAU_la_loi(self):
        rows = [('b', 1, 5, 12), ('b', 2, 10, 15)]
        self.assertEqual(rs.overlaps(rows), {('b', 1), ('b', 2)})

    def test_dai_Y_HET_nhau_chac_chan_sai(self):
        # Tiếng Anh 3 Tập 2: bài 11 và 12 cùng dải (5, 78) — trẻ mở hai bài
        # khác nhau và nhận đúng một bức tường 74 trang y hệt.
        rows = [('b', 11, 5, 78), ('b', 12, 5, 78), ('b', 19, 59, 78)]
        self.assertEqual(rs.identical_ranges(rows), {('b', 11), ('b', 12)})

    def test_sach_khac_nhau_khong_bao_gio_chong_nhau(self):
        rows = [('a', 1, 5, 20), ('b', 1, 5, 20)]
        self.assertEqual(rs.overlaps(rows), set())
        self.assertEqual(rs.identical_ranges(rows), set())


class Classify(unittest.TestCase):
    def test_dai_sai_duoc_noi_TRUOC(self):
        # Dải sai là lỗi nội dung nặng nhất — không được để họ khác che mất.
        self.assertEqual(
            rs.classify(pages=40, text='VĂN BẢN 1 ĐỌC VIẾT', lesson_no=1,
                        overlapping=True), 'C_RANGE_SAI')

    def test_MOT_so_bai_la_KHONG_du_ket_luan_gop(self):
        # 153/197 ca chỉ có đúng một số lạ — thường là câu «xem lại Bài 3».
        self.assertNotEqual(
            rs.classify(pages=4, text='xem lại Bài 3', lesson_no=5,
                        overlapping=False), 'B_GOP_NHIEU_BAI')

    def test_HAI_so_bai_la_tro_len_moi_la_gop(self):
        self.assertEqual(
            rs.classify(pages=4, text='Bài 3 ... Bài 9', lesson_no=5,
                        overlapping=False), 'B_GOP_NHIEU_BAI')

    def test_sach_tu_danh_dau_don_vi_con_thi_la_hat_muc_luc(self):
        self.assertEqual(
            rs.classify(pages=45, text='VĂN BẢN 1 ... VIẾT ... VĂN BẢN 2',
                        lesson_no=1, overlapping=False), 'E_HAT_MUC_LUC_KHAC')

    def test_MOT_moc_le_KHONG_du_ket_luan_hat_muc_luc(self):
        # Một bài Ngữ văn bình thường vẫn có mục «VIẾT» — một mốc lẻ không
        # chứng minh sách đang gộp nhiều đơn vị học vào một «Bài».
        self.assertNotEqual(
            rs.classify(pages=4, text='... phần VIẾT của bài ...', lesson_no=1,
                        overlapping=False), 'E_HAT_MUC_LUC_KHAC')

    def test_nhieu_lan_MOT_LOAI_moc_cung_khong_du(self):
        # «ĐỌC» lặp ba lần vẫn chỉ là một loại mốc — phải có ÍT NHẤT HAI loại
        # thì mới là cấu trúc đơn vị con của sách.
        self.assertNotEqual(
            rs.classify(pages=20, text='ĐỌC ... ĐỌC ... ĐỌC', lesson_no=1,
                        overlapping=False), 'E_HAT_MUC_LUC_KHAC')

    def test_dai_ma_khong_dau_hieu_nao_thi_la_don_vi_dai_that(self):
        self.assertEqual(
            rs.classify(pages=8, text='nội dung bình thường', lesson_no=1,
                        overlapping=False), 'A_DON_VI_DAI_THAT')

    def test_bai_ngan_binh_thuong_khong_bi_gan_ho_nao(self):
        self.assertIsNone(
            rs.classify(pages=3, text='nội dung bình thường', lesson_no=1,
                        overlapping=False))


class Headings(unittest.TestCase):
    def test_tieu_de_muc_cua_sach_duoc_nhan_ra(self):
        # Vật lí 11 Bài 5: nguồn có «III. CƠ NĂNG», «2. Con lắc đơn» thành
        # từng khối riêng — 67 khối, pack ghi ra 1.
        blocks = ['III. CƠ NĂNG Trong dao động', '2. Con lắc đơn - Vị trí',
                  'a) Trường hợp thứ nhất', 'Ớ lớp 10, khi học về chuyển động']
        self.assertEqual(len(rs.heading_blocks(blocks)), 3)


if __name__ == '__main__':
    unittest.main()
