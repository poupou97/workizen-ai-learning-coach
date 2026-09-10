#!/usr/bin/env python3
"""Mọi loại khối bộ dựng PHÁT RA đều phải có nhánh đọc ở CLIENT.

⚠ LỖI ĐÃ PHÁT HÀNH VÀ SỐNG MỘT NGÀY. `FormulaSourceBlock` được promote vào
canonical: 2.699 khối `t:"formula"` trong pack, census xanh, bất biến ĐẠT, mẫu
soi mắt 92,7% `SOURCE_FAITHFUL`. Nhưng parser Flutter chỉ có nhánh cho
`text` · `heading` · `img`, nên khối rơi qua cả ba và mất hẳn — trong khi bộ
dựng ĐÃ GỠ chuỗi OCR ở đúng chỗ ấy. Toán 1 tr.61: trẻ mất «60 - 20 = ?» cùng
bốn phép tính và nhận lại con số không.

`sealed class ReadItem` + `switch` vét cạn lẽ ra bắt được. Nó không bắt, vì
khối `formula` chưa bao giờ thành một biến thể của `ReadItem` — nó chết ở tầng
JSON, nơi trình biên dịch không nhìn vào. Test này đứng đúng chỗ ấy.

⛔ Test này đọc CHUỖI trong mã nguồn, nên nó mục được (bài học từ
`test_figures_staging.py`). Vì thế nó tự kiểm chính mình: hai tập phải KHÁC
RỖNG và phải chứa những loại đã biết. Mẫu ngừng khớp ⇒ test đỏ, không xanh giả.
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILDER = os.path.join(ROOT, 'tool/ui/build_lesson_figures.py')
CLIENT = os.path.join(ROOT, 'lib/features/subjects/lesson_index.dart')


def _read(p):
    with open(p, encoding='utf-8') as fh:
        return fh.read()


class LoaiKhoiPhaiToiDuocTre(unittest.TestCase):

    def _phat_ra(self):
        src = _read(BUILDER)
        got = set(re.findall(r"\bdict\(t='([a-z_]+)'", src))
        got |= set(re.findall(r"\bt='([a-z_]+)' if ", src))
        # `block_kind` thì GỌI THẬT, không grep: nó ở module khác và đã một lần
        # làm test này xanh giả vì đọc nhầm tệp.
        import sys
        sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))
        from read_structure import block_kind
        got |= {block_kind(t) for t in
                ('Một đoạn văn bình thường của sách giáo khoa.',
                 '1. Kết quả của mỗi lệnh sau là gì?',
                 'a) Thuật toán duyệt trước.',
                 'I. MỞ ĐẦU', 'II.', 'b)', '')}
        return {t for t in got if t}

    def _doc_duoc(self):
        return set(re.findall(r"it\['t'\] == '([a-z_]+)'", _read(CLIENT)))

    def test_mau_van_con_khop(self):
        """Chốt tự kiểm: mẫu mục thì test phải ĐỎ, không được xanh giả."""
        pr, cl = self._phat_ra(), self._doc_duoc()
        self.assertGreaterEqual(len(pr), 3, f'không đọc được loại khối bộ dựng phát ra: {pr}')
        self.assertGreaterEqual(len(cl), 3, f'không đọc được nhánh của client: {cl}')
        for t in ('text', 'heading', 'img'):
            self.assertIn(t, pr, f'bộ dựng phải phát ra «{t}»')
            self.assertIn(t, cl, f'client phải đọc được «{t}»')

    def test_moi_loai_phat_ra_deu_co_nhanh_o_client(self):
        pr, cl = self._phat_ra(), self._doc_duoc()
        thieu = pr - cl
        self.assertEqual(thieu, set(),
                         f'⛔ bộ dựng phát ra {sorted(thieu)} mà client KHÔNG đọc — '
                         f'khối sẽ rơi im lặng và trẻ mất chữ của sách. '
                         f'client đang đọc: {sorted(cl)}')

    def test_khoi_cong_thuc_nam_trong_ca_hai_phia(self):
        """Chốt riêng cho chính ca đã hỏng, để nó không quay lại."""
        self.assertIn('formula', self._phat_ra())
        self.assertIn('formula', self._doc_duoc())


if __name__ == '__main__':
    unittest.main()
