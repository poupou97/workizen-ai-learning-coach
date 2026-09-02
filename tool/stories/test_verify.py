#!/usr/bin/env python3
"""WAL-149 — ADVERSARIAL SUITE (§35): 12 ca cố tình bẫy verifier.
Chạy: python3 tool/stories/test_verify.py — exit≠0 nếu ca nào lọt."""
import sys
sys.path.insert(0, 'tool/stories')
from verify_stories import verify

def C(t, subject, ev, **kw):
    return dict(type=t, source=dict(sourceDocumentId='x', grade=5,
                subject=subject, pagePdf=9, textEvidence=ev), **kw)

CASES = [
 # 1. quote không động-từ-nói, attribution chỉ (Tên) sau → REVIEW (ca Ga-li-lê)
 (C('QUOTE','GDCD','ông vẫn nêu: "Dù sao Trái Đất vẫn quay!". (Lê Nguyên Long, Tiếng Việt 4)',
    person='Lê Nguyên Long', quote='Dù sao Trái Đất vẫn quay!'),
  'REVIEW_REQUIRED', 'quote-gán-nhầm-tác-giả-sách'),
 # 2. attribution là TÊN SÁCH → hạ SOURCE_EXCERPT, không thành lời danh nhân
 (C('QUOTE','Lịch sử','nổi dậy "đánh phá các châu, quận" (Giao Châu ngoại vực kí)',
    person='Giao Châu ngoại vực kí', quote='đánh phá các châu, quận'),
  'AUTO_VERIFIED', 'tên-sách→excerpt', 'SOURCE_EXCERPT'),
 # 3. quote CÓ động-từ-nói + người nhắc trước → AUTO
 (C('QUOTE','Lịch sử','Hồ Chí Minh viết: "Dân ta phải biết sử ta" (Hồ Chí Minh)',
    person='Hồ Chí Minh', quote='Dân ta phải biết sử ta'),
  'AUTO_VERIFIED', 'quote-chuẩn'),
 # 4. modal khả-năng → REJECT
 (C('INVENTION_DISCOVERY','Hoá học','Nhà hoá học có thể phát hiện ra tác phẩm giả mạo.',
    verb='phát hiện ra', person=None),
  'REJECTED', 'modal-không-phải-khám-phá'),
 # 5. fiction context môn Văn, không marker người-thật → REVIEW
 (C('INVENTION_DISCOVERY','Ngữ văn','Einstein giở sách, tìm ra phương pháp dạy chim bay.',
    verb='tìm ra', person='Einstein'),
  'REVIEW_REQUIRED', 'fiction-guard'),
 # 6. khám phá có năm thật → AUTO
 (C('INVENTION_DISCOVERY','Lịch sử','Năm 1896, Hen-ri Pho chế tạo, tìm ra cách sản xuất xe hơi.',
    verb='tìm ra', person='Hen-ri Pho'),
  'AUTO_VERIFIED', 'khám-phá-có-năm'),
 # 7. event thống kê hiện đại → REJECT
 (C('EVENT','Sinh học','năm 2020, Việt Nam xếp thứ 91/185 về tỉ lệ mắc mới.', year=2020),
  'REJECTED', 'stats-không-phải-event'),
 # 8. event thiếu động-từ-sự-kiện → REVIEW
 (C('EVENT','Toán','năm 2019, tỉnh Bắc Giang có 1 803 950 người theo bảng.', year=2019),
  'REVIEW_REQUIRED', 'event-thiếu-verb'),
 # 9. event chuẩn có verb → AUTO + todayEligible khi có monthDay
 (C('EVENT','Lịch sử','Ngày 2-9-1945, Hồ Chí Minh đọc bản Tuyên ngôn Độc lập.',
    year=1945, monthDay='09-02'),
  'AUTO_VERIFIED', 'event-chuẩn'),
 # 10. person một-từ → REVIEW (dễ nhầm triều đại/địa danh)
 (C('PERSON','Lịch sử','thời vua Hùng dựng nước', name='Hùng'),
  'REVIEW_REQUIRED', 'person-một-từ'),
 # 11. person prefix địa-danh bị trim, còn tên đủ → AUTO
 (C('PERSON','Vật lí','nhà khoa học Hy Lạp Aristotle bàn về rơi tự do',
    name='Hy Lạp Aristotle', role='nhà khoa học'),
  'AUTO_VERIFIED', 'trim-địa-danh', None, 'Aristotle'),
 # 12. person anchor sinh-mất → AUTO
 (C('PERSON','Ngữ văn','Tô Hoài (1920 - 2014) là nhà văn', name='Tô Hoài',
    birthYear=1920, deathYear=2014),
  'AUTO_VERIFIED', 'anchor-sinh-mất'),
]

fails = 0
for case in CASES:
    item, want_status, label = case[0], case[1], case[2]
    want_type = case[3] if len(case) > 3 and case[3] else None
    want_name = case[4] if len(case) > 4 else None
    st, why = verify(item)
    ok = st == want_status
    if want_type: ok = ok and item['type'] == want_type
    if want_name: ok = ok and item.get('name') == want_name
    mark = '✅' if ok else '❌'
    if not ok: fails += 1
    print(f'{mark} {label}: {st} (muốn {want_status})'
          + (f' type={item["type"]}' if want_type else '')
          + (f' name={item.get("name")!r}' if want_name else ''))
print(f'\n{len(CASES)-fails}/{len(CASES)} adversarial PASS')
sys.exit(1 if fails else 0)
