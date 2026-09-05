# Deliberate falsification of the History rules on the other 27 lessons (Lane C, round 5)

Bounded to LS&ĐL 5, the round-5 run. Every number is measured on the bridged documents of the 28 lessons; nothing here is a coverage claim.

## T1 — does `prose-dated-events-v1` survive a different date style?

The rule extracted **3 events across 28 lessons** (mis-promoted, i.e. a non-date parenthesis turned into an event: 0).

**Date forms the book actually prints (occurrences over the 28 documents):**

| form | occurrences | does the rule accept it? | example (lesson · block) |
|---|---|---|---|
| `narrative-year` | 54 | counted, never promoted (by design) | năm 2025 (1 · p008:tc2-p1:001) |
| `paren-year` | 21 | YES — the only accepted form | (1288) (10 · p050:tc2-p1:009) |
| `century` | 13 | no | thế kỉ XIX (13 · p060:tc2-p1:004) |
| `reign-period` | 12 | no | thời Trần (10 · p046:tc2-p1:017) |
| `decade-range` | 8 | no (outside parentheses) | 1418 - 1427 (12 · p053:tc2-p1:015) |
| `bare-tcn` | 2 | no (only inside parentheses) | 208 TCN (5 · p028:tc2-p1:007) |
| `narrative-year-tcn` | 1 | counted, never promoted | Năm 208 TCN (5 · p028:tc2-p1:007) |
| `century-tcn` | 1 | no | thế kỉ III TCN (5 · p029:tc2-p1:020) |

**Per lesson:**

| Bài | title | rule events | narrative years counted | date forms present |
|---|---|---|---|---|
| 1 | QUỐC KÌ, QUỐC HUY, QUỐC CA | 0 | 0 | narrative-year 3 |
| 10 | CHỐNG QUÂN MÔNG - NGUYÊN XÂM LƯỢC | 1 | 2 | narrative-year 3, paren-year 2, reign-period 2 |
| 11 | ÔN TẬP | 0 | 0 | — |
| 12 | KHỞI NGHĨA LAM SƠN VÀ TRIỀU HẬU LÊ | 1 | 3 | decade-range 3, narrative-year 3, paren-year 3, reign-period 2 |
| 13 | TRIỀU NGUYỄN | 0 | 0 | century 4 |
| 14 | CÁCH MẠNG THÁNG TÁM NĂM 1945 | 0 | 3 | narrative-year 5 |
| 15 | CHIẾN DỊCH ĐIỆN BIÊN PHỦ NĂM 1954 | 0 | 4 | narrative-year 6 |
| 16 | CHIẾN DỊCH HỒ CHÍ MINH NĂM 1975 | 1 | 2 | decade-range 1, narrative-year 4, paren-year 1 |
| 17 | ĐẤT NƯỚC ĐỔI MỚI | 0 | 2 | decade-range 2, narrative-year 2, paren-year 1 |
| 18 | NƯỚC CỘNG HOA NHÂN DÂN TRUNG HOA | 0 | 0 | narrative-year 1 |
| 19 | NƯỚC CỘNG HOA DÂN CHỦ NHÂN DÂN LÀO | 0 | 0 | narrative-year 1 |
| 2 | THIÊN NHIÊN VIỆT NAM | 0 | 0 | — |
| 20 | VƯƠNG QUỐC CAM-PU-CHIA | 0 | 1 | century 2, narrative-year 2 |
| 21 | HIỆP HỘI CÁC QUỐC GIA ĐÔNG NAM Á | 0 | 0 | narrative-year 2 |
| 22 | CÁC CHÂU LỤC VÀ ĐẠI DƯƠNG TRÊN THỂ | 0 | 1 | narrative-year 1 |
| 23 | TRÊN THẾ GIỚI | 0 | 2 | century 1, narrative-year 2 |
| 24 | VĂN MINH AI CẬP | 0 | 0 | — |
| 25 | VĂN MINH HY LẠP | 0 | 0 | — |
| 26 | XÂY DỰNG THẾ GIỚI XANH - SẠCH - ĐẸ | 0 | 0 | — |
| 27 | XÂY DỰNG THẾ GIỚI HOA BÌNH | 0 | 1 | narrative-year 2 |
| 28 | ÔN TẬP | 0 | 2 | decade-range 1, narrative-year 2, paren-year 13, reign-period 3 |
| 3 | BIỂN, ĐẢO VIỆT NAM | 0 | 1 | century 1, narrative-year 1 |
| 4 | DÂN CƯ VÀ DÂN TỘC Ở VIỆT NAM | 0 | 3 | century 1, decade-range 1, narrative-year 8 |
| 5 | NHÀ NƯỚC VĂN LANG, NHÀ NƯỚC ÂU LẠC | 0 | 2 | bare-tcn 1, century 2, century-tcn 1, narrative-year 2, narrative-year-tcn 1, reign-period 2 |
| 6 | VƯƠNG QUỐC PHÚ NAM | 0 | 0 | century 1, reign-period 1 |
| 7 | VƯƠNG QUỐC CHĂM-PA | 0 | 0 | century 1 |
| 8 | THỜI KĨ BẮC THUỘC | 0 | 2 | bare-tcn 1, narrative-year 2, paren-year 1 |
| 9 | TRIỀU LÝ VÀ VIỆC ĐỊNH ĐÔ Ở THĂNG L | 0 | 2 | narrative-year 2, reign-period 2 |

## T2 — does `story-attribution-v1` survive a quoted document instead of a story?

Attributions found: {"story": 30, "quoted-document": 1}. «TƯ LIỆU» boxes the book prints: 1.

| Bài | block | form | closes | story title | story blocks | withheld parts | complete | publisher | year |
|---|---|---|---|---|---|---|---|---|---|
| 10 | p047:tc2-p1:006 | theo | story | — | 4 | 1 | False | NXB Giáo dục | 1997 |
| 10 | p048:tc2-p1:008 | theo | story | TRẠNG NGUYÊN TRẺ TUỔI NHẤT VIỆT NAM | 2 | 2 | False | NXB Giáo dục | 1989 |
| 10 | p048:tc2-p1:016 | theo | story | NGƯỜI THẦY LƯU DANH MUÔN ĐỜI | 0 | 3 | False | None | None |
| 10 | p049:tc2-p1:013 | theo | story | LÁ CỞ THÊU SÂU CHỮ VÀNG | 2 | 0 | True | NXB Kim Đồng | 2017 |
| 10 | p050:tc2-p1:008 | theo | story | — | 1 | 6 | False | None | None |
| 12 | p055:tc2-p1:001 | theo | story | LÊ LAI QUÊN MĨNH CỨU CHÚA | 2 | 2 | False | NXB Giáo dục | 2008 |
| 12 | p055:tc2-p1:033 | theo | story | — | 1 | 1 | False | NXB Văn hóa dân tộc | 1987 |
| 13 | p060:tc2-p1:007 | theo | story | — | 4 | 1 | False | NXB Thuận Hoá | 1993 |
| 13 | p061:tc2-p1:010 | theo | story | — | 3 | 5 | False | NXB Trẻ | 2013 |
| 13 | p062:tc2-p1:010 | theo | story | — | 2 | 4 | False | None | None |
| 14 | p064:tc2-p1:015 | theo | story | THÂNH LẤP ĐỐI VIỆT NAM TUYÊN TRUYỀN GIẢI PHỒNG Q | 1 | 1 | False | NXB Quân đội nhân dân | 2006 |
| 14 | p065:tc2-p1:011 | theo | story | NGƯỜI ĐỘI VIÊN MƯU TRỈ, DŨNG CẮM | 2 | 3 | False | NXB Kim Đồng | 2019 |
| 14 | p066:tc2-p1:010 | theo | quoted-document | — | 1 | 0 | False | NXB Chính trị quốc gia Sự thật | 2018 |
| 15 | p069:tc2-p1:009 | theo | story | CHUYỆN BẮT SỐNG TƯỚNG ĐỜ CA-XTƠ-RI | 2 | 2 | False | NXB Văn nghệ Thành phố Hồ Chí Minh | 2004 |
| 16 | p073:tc2-p1:002 | theo | story | — | 3 | 4 | False | NXB Quân đội nhân dân | 1993 |
| 16 | p073:tc2-p1:011 | theo | story | — | 6 | 7 | False | None | None |
| 17 | p076:tc2-p1:006 | theo | story | XEM TRUYỀN HÌNH THỜI BAO CẤP | 2 | 0 | True | NXB Thông tấn | 2007 |
| 18 | p082:tc2-p1:008 | theo | story | — | 2 | 1 | False | NXB Giáo dục | 2000 |
| 25 | p110:tc2-p1:009 | theo | story | — | 2 | 3 | False | None | None |
| 27 | p115:tc2-p1:006 | theo | story | — | 2 | 2 | False | None | None |
| 4 | p026:tc2-p1:006 | theo | story | ĐOÀN KẾT DÂN TỘC TRONG PHONG TRÀO CẦN VƯƠNG | 5 | 2 | False | NXB Chính trị quốc gia | 2011 |
| 5 | p029:tc2-p1:013 | theo | story | TRUYỀN THUYỀT SƠN TINH, THUỶ TINH | 1 | 2 | False | NXB Giáo dục | 2000 |
| 5 | p030:tc2-p1:006 | theo | story | — | 5 | 1 | False | None | None |
| 7 | p037:tc2-p1:009 | theo | story | THÂP PÔ KLONG GA-RAI | 5 | 6 | False | None | None |
| 8 | p038:tc2-p1:015 | quote | story | — | 4 | 0 | False | NXB Chính trị quốc gia Sự thật | 2018 |
| 8 | p039:tc2-p1:013 | theo | story | — | 7 | 1 | False | NXB Giáo dục Việt Nam | 2017 |
| 8 | p040:tc2-p1:005 | theo | story | LÝ BĨ VÀ NHÀ NƯỚC VẠN XUÂN | 1 | 1 | False | NXB Giáo dục | 2005 |
| 8 | p041:tc2-p1:002 | theo | story | NGÔ QUYỀN ĐẠI PHẢ QUÂN NAM HÃN | 2 | 1 | False | NXB Văn hóa Thông tin | 2014 |
| 9 | p043:tc2-p1:016 | theo | story | VỊ VUA SÁNG LẬP TRIỂU LÝ | 2 | 2 | False | None | None |
| 9 | p044:tc2-p1:014 | theo | story | — | 1 | 3 | False | NXB Giáo dục | 2003 |
| 9 | p045:tc2-p1:011 | theo | story | — | 1 | 6 | False | NXB Thanh niên | 2010 |

**«TƯ LIỆU» boxes:**

| Bài | block | type | first words |
|---|---|---|---|
| 3 | p020:tc2-p1:016 | paragraph | TƯ LIỆU. Năm 1836, vua Minh Mạng cử Phạm Hữu Nhật chỉ huy độ |

## T3 — does lesson identity survive a two-lesson spread?

Pages carrying more than one lesson: **5**.

| PDF page | lessons | blocks each document keeps from that page (trusted / withheld) |
|---|---|---|
| 27 | 4, 5 | Bài 4: 1/0 · Bài 5: 17/0 |
| 38 | 7, 8 | Bài 7: 1/0 · Bài 8: 22/0 |
| 78 | 17, 18 | Bài 17: 1/0 · Bài 18: 15/0 |
| 95 | 21, 22 | Bài 21: 1/0 · Bài 22: 20/0 |
| 111 | 25, 26 | Bài 25: 1/0 · Bài 26: 17/0 |
