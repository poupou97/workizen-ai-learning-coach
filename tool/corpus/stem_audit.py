#!/usr/bin/env python3
"""WAL-239 — AUDIT ký hiệu STEM trong chữ mà TRẺ ĐANG ĐỌC.

    python3 tool/corpus/stem_audit.py

⛔ KHÔNG đo được TÍNH ĐÚNG của công thức. PDF là ảnh quét thuần, `conf` của OCR
gần như luôn bằng 1. Không có ground truth thì không được bịa một con số.

── ĐIỀU MODULE NÀY ĐÃ BÁC BỎ (đo trên 260.638 khối chữ của pack) ───────────

Tôi thử bốn tín hiệu HÌNH DẠNG để tìm chữ hỏng, và ba trong bốn là NHIỄU:

  `NGOAC_LECH`  ngoặc không đóng — 6,39% khối chữ. Soi ra thì phần lớn là
      QUY ƯỚC IN CỦA SGK: «a) Tìm số bị chia», «b) Chuyển các hỗn số»,
      «3)», và khoảng nửa mở «[15;16)». Ngoặc lệch KHÔNG phải dấu hiệu hỏng.

  `SO_MU_HONG`  dấu nháy/độ chen giữa chữ và số — 1,91%. Bắt phải dấu nháy
      sở hữu tiếng Anh: «partner's», «He's».

  `KY_TU_LAC`   ký tự lạc giữa hai chữ — 0,06%, quá hiếm để nói lên gì.

  Bản ĐẦU của tôi còn tệ hơn: lớp ký tự viết là `[ºo°'`]`, lọt cả chữ «o»
  thường, nên khớp MỌI từ tiếng Việt có «o» («khoe», «Cholesterol»). Nó cho
  24% và cho MÔN KHÁC (32,9%) CAO HƠN STEM (27,9%) — dấu hiệu rõ ràng rằng
  tín hiệu là nhiễu, nếu tôi chịu đọc con số ấy thay vì mừng vì nó lớn.

Cả ở mức TOKEN cũng vậy: khuôn «có chữ mà thiếu nguyên âm hoặc lẫn chữ với số»
bắt «cm», «kg», «H2O», «SGK», «HTML», «CSS» — chữ IN ĐÚNG của sách — và bắt cả
đại số in đúng «2x-1)(5x+1)», «+3y=-1». Coi cả khuôn là hại thì chặn nhầm
chính nội dung cần dạy.

── ĐIỀU CÒN ĐỨNG ĐƯỢC ──────────────────────────────────────────────────────

Một họ duy nhất là hỏng THẬT và nhận ra được bằng máy:

  `HOA_VAN_NEN`  hoa văn nền của nhà xuất bản lọt vào chữ của bài —
      «Bảng 4.1. Danh sách bộ phận và phụ kiện Số lượng KET NOITRI THUC VỚI
      CUỘ…», và trong công thức Vật lí 11 Bài 5: «- mv? (ẾT NÔ=-m*T HỨC».
      886 khối = 0,34%. Đây KHÔNG phải lỗi công thức — là đồ trang trí của
      trang lọt vào dòng đọc.

⭐ KẾT LUẬN PHƯƠNG PHÁP: hình dạng của CHỮ không tách được hại khỏi lành. Muốn
biết một khối chữ có phải công thức bị OCR phá hay không thì phải hỏi NGUỒN —
trang in có công thức ở CHỖ ẤY không. `tool/corpus/mathfix/detect.py` dò vùng
công thức TỪ ẢNH TRANG (gạch phân số dò bằng vệt mực, có mực trên và dưới,
tách rời) và báo `extractable=False` khi OCR đã phá — đúng dụng cụ cần. Nó
CHƯA được nối vào đường dựng pack. Đó là việc của bước sau, không phải bước
này, và phải qua cổng Founder vì nó đổi kiến trúc dòng đọc.
"""
import collections
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PACK = os.path.join(ROOT, 'assets', 'pack')

#: Hoa văn nền của các bộ sách. Danh sách đóng — đây là chuỗi IN SẴN, không
#: phải khuôn đoán.
WATERMARKS = ('kết nối tri thức', 'với cuộc sống', 'cánh diều',
              'chân trời sáng tạo', 'ket noi tri thuc', 'voi cuoc song')

STEM = ('toan', 'vat-li', 'hoa-hoc', 'tin-hoc', 'khoa-hoc-tu-nhien',
        'sinh-hoc', 'cong-nghe')


def is_stem(book):
    return any(k in book.split('-', 2)[-1] for k in STEM)


def watermark_bleed(text):
    """Hoa văn nền lọt vào chữ của bài.

    Nhận cả bản OCR bỏ dấu («KET NOITRI THUC») vì đó chính là cách nó hiện ra
    khi chữ chìm bị chồng lên chữ thật.
    """
    low = ' '.join((text or '').lower().split())
    return any(w in low for w in WATERMARKS)


def blocks():
    """Mọi khối chữ TRẺ ĐANG ĐỌC, kèm sách và mã bài."""
    out = []
    for g in range(1, 13):
        p = os.path.join(PACK, f'lesson-index-g{g}.json')
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8') as fh:
            idx = json.load(fh)
        for r in idx.get('lessonReadings') or []:
            for e in r.get('content') or []:
                if not isinstance(e, dict) or e.get('t') not in ('text', 'heading'):
                    continue
                v = (e.get('v') or '').strip()
                if v:
                    out.append((r['book'], r.get('lesson'), is_stem(r['book']), v))
    return out


def main():
    rows = blocks()
    hit = [r for r in rows if watermark_bleed(r[3])]
    ns = sum(1 for r in rows if r[2])
    nn = len(rows) - ns
    hs = sum(1 for r in hit if r[2])
    print(f'khối chữ trong pack: {len(rows)}  (STEM {ns} · môn khác {nn})\n')
    print(f'HOA_VAN_NEN — hoa văn nhà xuất bản lọt vào dòng đọc của trẻ')
    print(f'  tổng      {len(hit):5d}  {len(hit) / len(rows):6.2%} số khối chữ')
    print(f'  STEM      {hs:5d}  {hs / ns:6.2%}')
    print(f'  môn khác  {len(hit) - hs:5d}  {(len(hit) - hs) / nn:6.2%}')
    bybook = collections.Counter(r[0] for r in hit)
    print(f'\n  sách dính nhiều nhất:')
    for b, n in bybook.most_common(6):
        print(f'    {b:44s} {n}')
    rng = random.Random(20260913)
    print(f'\n  10 khối ngẫu nhiên (seed 20260913):')
    for b, les, st, t in rng.sample(hit, min(10, len(hit))):
        print(f'    [{"STEM" if st else "khác"}] {b[:26]:26s} «{t[:66]}»')
    print('\n⚠ Đây là ĐỒ TRANG TRÍ LỌT VÀO CHỮ, không phải lỗi công thức.')
    print('  Tính đúng của công thức vẫn KHÔNG đo được — xem docstring.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
