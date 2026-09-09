#!/usr/bin/env python3
"""`FormulaSourceBlock` — công thức tới với trẻ bằng ẢNH TRANG IN (WAL-239).

Đo được trước khi làm: 88,7% chuỗi OCR ở vùng công thức là HẠI (n=53, Toán
23/23). Nặng nhất không phải chữ vỡ mà là MỆNH ĐỀ SAI ĐỌC TRÔI CHẢY —
«x²/9 + y²/5 = 1» thành «5 = 1.».
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import formula_source as fs  # noqa: E402


def para(box, text='x', seq=0):
    """`page_paragraphs` trả hộp theo GÓC `[x0,y0,x1,y1]`."""
    return dict(box=list(box), text=text, seq=seq, y=box[1])


VUNG = [0.10, 0.20, 0.60, 0.30]          # [x, y, w, h] → góc 0.10..0.70 × 0.20..0.50


class VungAnToan(unittest.TestCase):
    def test_vung_thuong_thi_an_toan(self):
        self.assertTrue(fs.safe_region(VUNG))

    def test_vung_gan_TRON_TRANG_thi_KHONG_an_toan(self):
        """Cắt nó ra là biến cả trang thành ảnh, không phải một khối nội dung."""
        self.assertFalse(fs.safe_region([0.0, 0.0, 1.0, 0.9]))

    def test_vung_TRAN_RA_NGOAI_trang_thi_khong_an_toan(self):
        self.assertFalse(fs.safe_region([0.8, 0.8, 0.5, 0.5]))

    def test_vung_rong_hoac_am_thi_khong_an_toan(self):
        self.assertFalse(fs.safe_region([0.1, 0.1, 0.0, 0.2]))
        self.assertFalse(fs.safe_region([0.1, 0.1, -0.2, 0.2]))
        self.assertFalse(fs.safe_region(None))


class QuyenSoHuu(unittest.TestCase):
    def test_doan_NAM_GON_trong_vung_thi_thuoc_ve_vung(self):
        p = para([0.20, 0.25, 0.50, 0.30])          # gọn bên trong
        self.assertIsNotNone(fs.owned_by_formula(p, [VUNG]))

    def test_doan_NGOAI_vung_thi_GIU_nguyen(self):
        p = para([0.10, 0.60, 0.60, 0.70])
        self.assertIsNone(fs.owned_by_formula(p, [VUNG]))

    def test_doan_chi_CHONG_MOT_PHAN_thi_GIU_nguyen(self):
        """Văn xuôi thò một nửa vào vùng không phải chữ của công thức.
        Founder: «Do NOT suppress surrounding prose.»"""
        p = para([0.10, 0.45, 0.60, 0.75])          # phần lớn nằm dưới vùng
        self.assertIsNone(fs.owned_by_formula(p, [VUNG]))

    def test_KHONG_CO_HOP_BAO_thi_khong_co_bang_chung_nen_GIU(self):
        self.assertIsNone(fs.owned_by_formula(dict(text='x', seq=0), [VUNG]))

    def test_doan_NHO_nam_gon_van_thuoc_ve_vung(self):
        """⚠ Mẫu số phải là diện tích CỦA CHÍNH ĐOẠN. Lấy mẫu số là vùng thì
        đoạn ngắn luôn ra tỉ lệ bé và không bao giờ bị nhận — đúng lỗi đã phải
        sửa ở `table_ownership`."""
        p = para([0.30, 0.30, 0.34, 0.32])
        self.assertIsNotNone(fs.owned_by_formula(p, [VUNG]))


class DanhTinh(unittest.TestCase):
    def test_mot_so_hieu_IN_thi_nhan_lam_danh_tinh(self):
        self.assertEqual(fs.identity(['v = ±ω√(A²−x²)  (3.2)']), '3.2')

    def test_HAI_so_hieu_thi_KHONG_gan_cai_nao(self):
        """Vùng ôm hai công thức được đánh số khác nhau — gán một cái là gán sai."""
        self.assertIsNone(fs.identity(['... (19.5)', '... (19.6)']))

    def test_khong_co_so_hieu_thi_de_trong(self):
        self.assertIsNone(fs.identity(['a) y = x⁴ − 2x² + 3']))
        self.assertIsNone(fs.identity([]))


class DungKhoi(unittest.TestCase):
    def _paras(self):
        return [para([0.20, 0.25, 0.50, 0.30], 'F = ma  (3.2)', seq=7),
                para([0.20, 0.35, 0.50, 0.45], 'v = at', seq=8),
                para([0.10, 0.60, 0.60, 0.75], 'Văn xuôi ngoài vùng', seq=9)]

    def test_dung_khoi_va_CHI_bo_chu_TRONG_vung(self):
        ps = self._paras()
        blk, owned = fs.blocks('b', 21, [VUNG], ps)
        self.assertEqual(len(blk), 1)
        self.assertEqual(blk[0]['t'], 'formula')
        self.assertEqual(blk[0]['ident'], '3.2')
        self.assertEqual(blk[0]['trust'], 'TRUSTED')
        self.assertEqual(blk[0]['seq'], 7, 'neo thứ tự đọc = đoạn đầu tiên nó sở hữu')
        self.assertEqual(blk[0]['src'], dict(book='b', page=21,
                                             region=[0.1, 0.2, 0.6, 0.3]))
        self.assertIn(id(ps[0]), owned)
        self.assertIn(id(ps[1]), owned)
        self.assertNotIn(id(ps[2]), owned, 'văn xuôi ngoài vùng phải được GIỮ')

    def test_vung_KHONG_AN_TOAN_thi_KHONG_dung_khoi_nhung_VAN_giu_lai_chu(self):
        """Founder: không dựng được vùng an toàn ⇒ D — giữ lại chuỗi OCR.
        Thiếu công thức mà nói thật còn hơn một công thức sai mà tự tin."""
        ps = self._paras()
        blk, owned = fs.blocks('b', 21, [[0.0, 0.0, 1.0, 0.95]], ps)
        self.assertEqual(blk, [])
        self.assertTrue(owned, 'chữ trong vùng vẫn phải bị giữ lại')

    def test_vung_co_chu_CHAM_vao_ma_khong_so_huu_thi_KHONG_dung_khoi(self):
        """⛔ Tránh rơi vào C. Không đoạn nào nằm gọn ⇒ không bỏ được chữ sai
        nào ⇒ hiện ảnh lúc này là đặt bản in đúng CẠNH chuỗi OCR sai.
        Đo toàn corpus: 1.388/4.885 = 28,4% vùng rơi vào đây."""
        cham = [para([0.05, 0.15, 0.65, 0.55], 'văn xuôi trùm qua vùng', seq=3)]
        blk, owned = fs.blocks('b', 21, [VUNG], cham)
        self.assertEqual(blk, [], 'không được dựng khối khi không bỏ được chữ')
        self.assertEqual(owned, set())

    def test_doan_DAI_phu_vung_van_lam_no_chot_chong_C(self):
        """⚠ HAI MẪU SỐ KHÁC NHAU. Đoạn dài «T(n) = n2 + 3n - 3 Xác định độ
        phức tạp…» chỉ có 1,5% diện tích CỦA NÓ nằm trong vùng công thức bé,
        nhưng phủ ~80% DIỆN TÍCH VÙNG. Dùng nhầm mẫu số thì chốt không nổ và
        trẻ thấy ảnh đúng cạnh chữ hỏng — đúng C bị cấm. Ca thật ở Tin học 11
        tr.119, lọt qua tới tận vòng soi mẫu bốn bên."""
        nho = [0.30, 0.28, 0.08, 0.03]          # vùng công thức bé
        dai = [para([0.10, 0.20, 0.90, 0.55], 'công thức + cả đoạn văn dài', seq=4)]
        blk, _ = fs.blocks('b', 21, [nho], dai)
        self.assertEqual(blk, [], 'đoạn dài phủ vùng phải chặn được khối')

    def test_vung_SACH_khong_co_chu_nao_thi_VAN_dung_khoi(self):
        """Không có chữ nào để mâu thuẫn ⇒ hiện ảnh là lãi ròng, không phải C."""
        xa = [para([0.10, 0.80, 0.60, 0.90], 'đoạn ở xa', seq=3)]
        blk, _ = fs.blocks('b', 21, [VUNG], xa)
        self.assertEqual(len(blk), 1)

    def test_khong_co_vung_thi_khong_dung_gi_va_khong_bo_gi(self):
        ps = self._paras()
        blk, owned = fs.blocks('b', 21, [], ps)
        self.assertEqual(blk, [])
        self.assertEqual(owned, set())

    def test_khoi_KHONG_phai_hinh_thuong(self):
        """`FIGURE != TABLE != FORMULA != TEXT` — kiểu phải nói đúng nó là gì."""
        blk, _ = fs.blocks('b', 21, [VUNG], self._paras())
        self.assertEqual(blk[0]['t'], 'formula')
        self.assertNotEqual(blk[0]['t'], 'img')


class QuyUocHop(unittest.TestCase):
    """⚠ HAI QUY ƯỚC HỘP CÙNG TỒN TẠI — tôi đã đọc nhầm một lần, mất cả một
    vòng đo. `proposals-w*.jsonl` dùng GÓC; `trusted.jsonl` dùng `[x,y,w,h]`.
    """
    def test_goc_doi_sang_xywh(self):
        self.assertEqual(fs._wh([0.1041, 0.0547, 0.312, 0.118]),
                         [0.1041, 0.0547, 0.312 - 0.1041, 0.118 - 0.0547])

    def test_hop_GOC_hop_le_KHONG_bi_coi_la_tran_bien(self):
        """Hộp góc [0.6, 0.7, 0.9, 0.95] hợp lệ. Đọc nhầm thành x,y,w,h thì
        x+w = 1,5 và nó bị loại oan — chính lỗi đã làm 69,5% vùng bị vứt."""
        self.assertTrue(fs.safe_region(fs._wh([0.6, 0.7, 0.9, 0.95])))

    def test_dien_tich_tinh_tren_be_rong_that(self):
        b = fs._wh([0.2, 0.3, 0.5, 0.34])
        self.assertAlmostEqual(b[2] * b[3], 0.3 * 0.04, places=6)


class CatVuaVan(unittest.TestCase):
    """Nới tới khi MỰC KHÔNG CÒN CHẠM MÉP — không dùng đệm cố định.

    Soi mắt cho thấy một hằng số không đủ: «13/2» cần 0,004 mới đủ mẫu số,
    «mv₁²/2» cần tới 0,008 mới đủ tử số, mà 0,008 ở ca khác đã kéo nửa dòng
    văn xuôi vào. Nên hỏi chính trang in, và nới ĐÚNG cạnh đang bị chạm.
    """
    def _render(self, ink_box):
        """Giả lập trang: chỉ vùng `ink_box` có mực, ngoài ra trắng."""
        def render(box):
            n = 40
            x, y, w, h = box
            out = []
            for j in range(n):
                for i in range(n):
                    px = x + w * (i + 0.5) / n
                    py = y + h * (j + 0.5) / n
                    inside = (ink_box[0] <= px <= ink_box[0] + ink_box[2]
                              and ink_box[1] <= py <= ink_box[1] + ink_box[3])
                    out.append(0 if inside else 255)
            return out, n, n
        return render

    def test_muc_khong_cham_mep_thi_giu_nguyen_khung(self):
        box = [0.20, 0.20, 0.20, 0.10]
        ink = [0.24, 0.23, 0.12, 0.04]        # nằm gọn bên trong
        got, ok = fs.fit_region(None, box, self._render(ink))
        self.assertTrue(ok)
        self.assertEqual(got, box, 'khung đã đủ thì không được nới')

    def test_muc_cham_MEP_TREN_thi_noi_LEN_va_dat(self):
        box = [0.20, 0.20, 0.20, 0.10]
        ink = [0.24, 0.185, 0.12, 0.10]       # tràn lên trên
        got, ok = fs.fit_region(None, box, self._render(ink))
        self.assertTrue(ok)
        self.assertLess(got[1], box[1], 'phải nới lên trên')
        self.assertAlmostEqual(got[0], box[0], places=6,
                               msg='cạnh trái sạch thì KHÔNG được nới')

    def _render_grey(self, ink_box, level):
        """Mực XÁM, không đen tuyệt đối — chữ in quét ra thường là xám."""
        def render(box):
            n = 40
            x, y, w, h = box
            out = []
            for j in range(n):
                for i in range(n):
                    px = x + w * (i + 0.5) / n
                    py = y + h * (j + 0.5) / n
                    inside = (ink_box[0] <= px <= ink_box[0] + ink_box[2]
                              and ink_box[1] <= py <= ink_box[1] + ink_box[3])
                    out.append(level if inside else 255)
            return out, n, n
        return render

    def test_muc_XAM_van_phai_nhan_ra(self):
        """⚠ Mực giả đen tuyệt đối làm mọi ngưỡng đều đúng. Chữ quét thật là
        XÁM — ngưỡng quá chặt thì không thấy mực và khung không bao giờ nới."""
        box = [0.20, 0.20, 0.20, 0.10]
        ink = [0.24, 0.185, 0.12, 0.10]
        got, ok = fs.fit_region(None, box, self._render_grey(ink, 150))
        self.assertTrue(ok)
        self.assertLess(got[1], box[1], 'mực xám chạm mép vẫn phải nới')

    def test_KHONG_noi_qua_han_muc(self):
        """Hạn mức là LUẬT NGHIỆP VỤ: nới quá thì không còn là một công thức.
        Chặn vòng lặp chỉ là lưới an toàn, không thay được luật ấy."""
        box = [0.40, 0.40, 0.05, 0.05]
        got, ok = fs.fit_region(None, box, self._render([0.0, 0.0, 1.0, 1.0]))
        self.assertFalse(ok)
        self.assertLessEqual(got[2] - box[2], fs.GROW_MAX * 2 + 1e-9,
                             'không được nới vượt hạn mức')

    def test_muc_tran_qua_XA_thi_DONG_CHAT(self):
        """Hết hạn mức mà mực vẫn chạm ⇒ không được hiện công thức cắt cụt."""
        box = [0.40, 0.40, 0.05, 0.05]
        ink = [0.0, 0.0, 1.0, 1.0]            # mực khắp trang
        _, ok = fs.fit_region(None, box, self._render(ink))
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()


class DemCat(unittest.TestCase):
    """⚠ ĐỆM LÀ CỦA HÌNH, KHÔNG PHẢI CỦA MỌI THỨ.

    `CROP_PAD = 0,012` sinh ra cho vùng dò bằng MẶT NẠ MỰC, nơi nhãn sơ đồ là
    CHỮ nên nằm NGOÀI khung. Vùng bố cục (công thức) đã ôm sẵn chữ của nó, nên
    nới thêm chỉ kéo vào nửa dòng văn xuôi bên trên/dưới. Soi mắt 5 ca: đệm
    0,012 lần nào cũng dính chữ hàng xóm; đệm 0 sạch và không cắt cụt cái nào.
    """
    def test_crop_jpeg_cho_nguoi_goi_chon_dem(self):
        import inspect
        sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
        from lesson_figures import crop_jpeg
        self.assertIn('pad', inspect.signature(crop_jpeg).parameters,
                      'khối công thức phải cắt được với đệm 0')

    def test_builder_cat_cong_thuc_KHONG_dung_dem_cua_hinh(self):
        """⚠ Bài kiểm bám vào CHUỖI GỌI thì mục ngay khi chữ ký đổi — đã dính
        một lần hôm nay. Bám vào TÍNH CHẤT: đường công thức phải đi qua
        `fit_region` (cắt vừa vặn) và không được dùng đệm mặc định của hình.
        """
        p = os.path.join(HERE, '..', 'ui', 'build_lesson_figures.py')
        with open(p, encoding='utf-8') as fh:
            src = fh.read()
        i = src.index('FML_STATS')
        blk = src[i:src.index('pending.append', i)]
        self.assertIn('fit_region', blk, 'khối công thức phải cắt vừa vặn')
        self.assertIn('pad=0.0', blk, 'không được dùng CROP_PAD của hình')
        self.assertIn('BO_CAT_KHONG_TRON', blk,
                      'cắt không trọn thì phải đóng chặt, có bộ đếm riêng')
