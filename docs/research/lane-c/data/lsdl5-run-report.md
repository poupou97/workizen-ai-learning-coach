# LS&ĐL 5 — bounded TC-v2 run report (Lane C, round 4, run `v1`)

Pipeline code unchanged (`tc2-p1`/`sdm-v2` at git `2e42487`; docling 2.126.0, ocrmac 1.0.1); sandbox root `poc-out/round4/lane-c/tc2-lsdl5/v1/root` (inputs symlinked from the main checkout, outputs only there).

**Step 1 — run:** 123 pages, docling ok 123 / error 0, xycut ok 123; docling median 1.686 s, p90 2.139 s, total 227.8 s. Attachment: canonical 28, TOC-ranged 10, headers detected 23 (TOC-confirmed 6, header-only 17), repaired-ranged 27, pages with a lesson 117 / 123. TSL: 23 lessons, learning blocks 1483 = trusted 1263 + withheld 220; figures 387; withheld by reason {'agree_text': 115, 'figure_dependent': 39, 'agree_order': 21, 'low_ocr_conf': 1, 'page_feature:diagram': 12, 'page_feature:color_heavy': 23, 'box_boundary': 19}.

| Bài | PDF pages | n | conf | source | learning | trusted | withheld | figs | title (pipeline) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 7–10 | 4 | 0.95 | both | 50 | 41 | 9 | 12 | QUỐC KÌ, QUỐC HUY, QUỐC CA |
| 2 | 11–21 | 11 | 0.95 | both | 130 | 109 | 21 | 37 | THIÊN NHIÊN VIỆT NAM |
| 4 | 22–27 | 6 | 0.6 | header | 55 | 49 | 6 | 12 | DÂN CƯ VÀ DÂN TỘC Ở VIỆT NAM |
| 5 | 27–30 | 4 | 0.85 | header | 57 | 54 | 3 | 16 | NHÀ NƯỚC VĂN LANG, NHÀ NƯỚC ÂU LẠC |
| 6 | 31–38 | 8 | 0.85 | header | 85 | 77 | 8 | 29 | VƯƠNG QUỐC PHÚ NAM |
| 8 | 38–41 | 4 | 0.95 | both | 51 | 34 | 17 | 14 | THỜI KĨ BẮC THUỘC |
| 9 | 42–45 | 4 | 0.95 | both | 54 | 44 | 10 | 13 | TRIỀU LÝ VÀ VIỆC ĐỊNH ĐÔ Ở THĂNG LONG |
| 10 | 46–52 | 7 | 0.85 | header | 72 | 60 | 12 | 18 | CHỐNG QUÂN MÔNG - NGUYÊN XÂM LƯỢC |
| 12 | 53–62 | 10 | 0.6 | header | 126 | 107 | 19 | 35 | KHỞI NGHĨA LAM SƠN VÀ TRIỀU HẬU LÊ |
| 14 | 63–66 | 4 | 0.6 | header | 48 | 40 | 8 | 14 | CÁCH MẠNG THÁNG TÁM NĂM 1945 |
| 15 | 67–70 | 4 | 0.95 | both | 60 | 50 | 10 | 14 | CHIẾN DỊCH ĐIỆN BIÊN PHỦ NĂM 1954 |
| 16 | 71–73 | 3 | 0.85 | header | 36 | 28 | 8 | 13 | CHIẾN DỊCH HỒ CHÍ MINH NĂM 1975 |
| 17 | 74–78 | 5 | 0.85 | header | 48 | 45 | 3 | 19 | ĐẤT NƯỚC ĐỔI MỚI |
| 18 | 78–83 | 6 | 0.85 | header | 57 | 51 | 6 | 15 | NƯỚC CỘNG HOA NHÂN DÂN TRUNG HOA |
| 19 | 84–87 | 4 | 0.85 | header | 42 | 39 | 3 | 11 | NƯỚC CỘNG HOA DÂN CHỦ NHÂN DÂN LÀO |
| 20 | 88–91 | 4 | 0.85 | header | 51 | 47 | 4 | 12 | VƯƠNG QUỐC CAM-PU-CHIA |
| 21 | 92–95 | 4 | 0.85 | both | 42 | 33 | 9 | 12 | HIỆP HỘI CÁC QUỐC GIA ĐÔNG NAM Á |
| 22 | 95–102 | 8 | 0.85 | header | 134 | 111 | 23 | 32 | CÁC CHÂU LỤC VÀ ĐẠI DƯƠNG TRÊN THỂ GIỚI |
| 24 | 103–106 | 4 | 0.6 | header | 38 | 30 | 8 | 11 | VĂN MINH AI CẬP |
| 25 | 107–111 | 5 | 0.85 | header | 54 | 51 | 3 | 15 | VĂN MINH HY LẠP |
| 26 | 111–113 | 3 | 0.85 | header | 39 | 32 | 7 | 13 | XÂY DỰNG THẾ GIỚI XANH - SẠCH - ĐẸP |
| 27 | 114–117 | 4 | 0.85 | header | 53 | 50 | 3 | 14 | XÂY DỰNG THẾ GIỚI HOA BÌNH |
| 28 | 118–123 | 6 | 0.85 | header | 101 | 81 | 20 | 6 | ÔN TẬP |

**Bài 8 (TSL):** title `THỜI KĨ BẮC THUỘC` · boundary 38–41 conf 0.95 source both header_found True · sourceability PARTIAL · learning 51 = trusted 34 + withheld 17 · withheld by reason {'page_feature:color_heavy': 14, 'agree_text': 3, 'agree_order': 2, 'box_boundary': 1} · roles trusted {'heading': 8, 'stage_label': 5, 'body': 14, 'question': 4, 'caption': 3} · figures 14.

| PDF page | trusted | withheld | trusted roles | withheld reasons |
|---|---|---|---|---|
| 38 | 7 | 14 | {'heading': 4, 'stage_label': 3} | {'page_feature:color_heavy': 14, 'agree_text': 3} |
| 39 | 12 | 2 | {'body': 8, 'heading': 2, 'question': 1, 'caption': 1} | {'agree_order': 2} |
| 40 | 6 | 1 | {'heading': 2, 'body': 3, 'caption': 1} | {'box_boundary': 1} |
| 41 | 9 | 0 | {'body': 3, 'stage_label': 2, 'question': 3, 'caption': 1} | {} |

| block | page | order | role | conf | method | bbox | heading | first words |
|---|---|---|---|---|---|---|---|---|
| p038:tc2-p1:002 | 38 | 2 | heading | 0.97 | lexicon | [0.151, 0.166, 0.08, 0.026] | BÀI 8 | BÀI 8 |
| p038:tc2-p1:003 | 38 | 3 | heading | 0.88 | typography | [0.269, 0.154, 0.415, 0.059] | ĐẦU TRANH GIÀNH ĐỘC LẬP THỜI K | ĐẦU TRANH GIÀNH ĐỘC |
| p038:tc2-p1:004 | 38 | 4 | heading | 0.85 | native | [0.108, 0.237, 0.204, 0.018] | Sau bài học này, em sẽ: | Sau bài học này, |
| p038:tc2-p1:009 | 38 | 9 | stage_label | 0.95 | lexicon | [0.155, 0.349, 0.139, 0.025] | Sau bài học này, em sẽ: | KHỞI ĐỘNG |
| p038:tc2-p1:017 | 38 | 17 | stage_label | 0.95 | lexicon | [0.155, 0.549, 0.135, 0.019] | Sau bài học này, em sẽ: | KHÁM PHÁ |
| p038:tc2-p1:018 | 38 | 18 | heading | 0.85 | native | [0.09, 0.602, 0.647, 0.025] | 1. Một số cuộc đầu tranh tiêu  | 1. Một số cuộc |
| p038:tc2-p1:026 | 38 | 26 | stage_label | 0.95 | lexicon | [0.564, 0.74, 0.124, 0.019] | 1. Một số cuộc đầu tranh tiêu  | Em có biết? |
| p039:tc2-p1:000 | 39 | 0 | body | 0.60 | default | [0.075, 0.068, 0.835, 0.08] | - | Hai Bà Trưng (40 |
| p039:tc2-p1:001 | 39 | 1 | heading | 0.85 | native | [0.075, 0.157, 0.833, 0.044] | 2. Kể chuyện về một số nhân vậ | 2. Kể chuyện về |
| p039:tc2-p1:003 | 39 | 3 | question | 0.85 | lexicon | [0.114, 0.23, 0.5, 0.018] | 2. Kể chuyện về một số nhân vậ | Đọc thông tin và |
| p039:tc2-p1:004 | 39 | 4 | body | 0.60 | default | [0.112, 0.25, 0.753, 0.017] | 2. Kể chuyện về một số nhân vậ | - Kể câu chuyện |
| p039:tc2-p1:005 | 39 | 5 | body | 0.60 | default | [0.112, 0.272, 0.443, 0.016] | 2. Kể chuyện về một số nhân vậ | - Chia sẻ điều |
| p039:tc2-p1:006 | 39 | 6 | body | 0.60 | default | [0.075, 0.308, 0.831, 0.041] | 2. Kể chuyện về một số nhân vậ | Trong cuộc đấu tranh |
| p039:tc2-p1:009 | 39 | 9 | heading | 0.88 | typography | [0.331, 0.382, 0.38, 0.025] | TRƯNG VƯƠNG TRỮ GIẶC HÂN | TRƯNG VƯƠNG TRỮ GIẶC |
| p039:tc2-p1:010 | 39 | 10 | body | 0.60 | default | [0.09, 0.432, 0.804, 0.095] | TRƯNG VƯƠNG TRỮ GIẶC HÂN | Thuở xưa, nước ta |
| p039:tc2-p1:011 | 39 | 11 | body | 0.60 | default | [0.09, 0.532, 0.802, 0.096] | TRƯNG VƯƠNG TRỮ GIẶC HÂN | Cuộc khởi nghĩa được |
| p039:tc2-p1:012 | 39 | 12 | body | 0.60 | default | [0.092, 0.634, 0.8, 0.058] | TRƯNG VƯƠNG TRỮ GIẶC HÂN | Cuộc khởi nghĩa Hai |
| p039:tc2-p1:013 | 39 | 13 | body | 0.60 | default | [0.214, 0.695, 0.678, 0.038] | TRƯNG VƯƠNG TRỮ GIẶC HÂN | (Theo Nguyễn Thi, Thành |
| p039:tc2-p1:015 | 39 | 15 | caption | 0.80 | native | [0.265, 0.897, 0.457, 0.019] | TRƯNG VƯƠNG TRỮ GIẶC HÂN | A Hình 1. Trưng |
| p040:tc2-p1:002 | 40 | 2 | heading | 0.88 | typography | [0.349, 0.074, 0.382, 0.026] | LÝ BĨ VÀ NHÀ NƯỚC VẠN XUÂN | LÝ BĨ VÀ NHÀ |
| p040:tc2-p1:004 | 40 | 4 | body | 0.60 | default | [0.104, 0.283, 0.804, 0.041] | LÝ BĨ VÀ NHÀ NƯỚC VẠN XUÂN | Cuộc khởi nghĩa Lý |
| p040:tc2-p1:005 | 40 | 5 | body | 0.60 | default | [0.412, 0.334, 0.498, 0.039] | LÝ BĨ VÀ NHÀ NƯỚC VẠN XUÂN | (Theo Đinh Xuân Lâm, |
| p040:tc2-p1:007 | 40 | 7 | caption | 0.92 | lexicon | [0.361, 0.664, 0.314, 0.019] | LÝ BĨ VÀ NHÀ NƯỚC VẠN XUÂN | Hình 2. Đền thờ |
| p040:tc2-p1:008 | 40 | 8 | heading | 0.88 | typography | [0.341, 0.74, 0.461, 0.026] | NGÔ QUYỀN ĐẠI PHẢ QUÂN NAM HÃN | NGÔ QUYỀN ĐẠI PHẢ |
| p040:tc2-p1:011 | 40 | 11 | body | 0.60 | default | [0.108, 0.788, 0.804, 0.118] | NGÔ QUYỀN ĐẠI PHẢ QUÂN NAM HÃN | Năm 937, sau khi |
| p041:tc2-p1:000 | 41 | 0 | body | 0.60 | default | [0.092, 0.086, 0.525, 0.156] | - | Nghe tin Hoằng Tháo |
| p041:tc2-p1:001 | 41 | 1 | body | 0.60 | default | [0.094, 0.25, 0.523, 0.076] | - | Chiến thắng Bạch Đằng |
| p041:tc2-p1:002 | 41 | 2 | body | 0.60 | default | [0.137, 0.331, 0.48, 0.055] | - | (Theo Đăng Khoa, Hoài |
| p041:tc2-p1:004 | 41 | 4 | stage_label | 0.95 | lexicon | [0.161, 0.445, 0.137, 0.025] | - | LUYỆN TẬP |
| p041:tc2-p1:005 | 41 | 5 | question | 0.85 | lexicon | [0.094, 0.487, 0.796, 0.039] | - | 1. Hãy vẽ và |
| p041:tc2-p1:006 | 41 | 6 | question | 0.85 | lexicon | [0.092, 0.686, 0.798, 0.04] | - | 2. Kể lại câu |
| p041:tc2-p1:020 | 41 | 20 | stage_label | 0.95 | lexicon | [0.155, 0.767, 0.133, 0.022] | - | VẬN DỤNG |
| p041:tc2-p1:021 | 41 | 21 | question | 0.85 | lexicon | [0.094, 0.804, 0.794, 0.039] | - | Tìm hiếu và kể |
| p041:tc2-p1:023 | 41 | 23 | caption | 0.92 | lexicon | [0.663, 0.324, 0.221, 0.035] | - | Hình 3. Tượng đài |

| withheld | page | order | role | reasons | status | bbox | chars |
|---|---|---|---|---|---|---|---|
| p038:tc2-p1:005 | 38 | 5 | objective | page_feature:color_heavy | WITHHELD | [0.102, 0.26, 0.806, 0.039] | 145 |
| p038:tc2-p1:006 | 38 | 6 | body | page_feature:color_heavy | WITHHELD | [0.104, 0.305, 0.751, 0.019] | 103 |
| p038:tc2-p1:010 | 38 | 10 | question | page_feature:color_heavy | WITHHELD | [0.127, 0.382, 0.641, 0.021] | 68 |
| p038:tc2-p1:011 | 38 | 11 | body | page_feature:color_heavy | WITHHELD | [0.38, 0.407, 0.221, 0.016] | 24 |
| p038:tc2-p1:012 | 38 | 12 | body | page_feature:color_heavy | WITHHELD | [0.335, 0.426, 0.36, 0.022] | 38 |
| p038:tc2-p1:013 | 38 | 13 | body | page_feature:color_heavy | WITHHELD | [0.369, 0.451, 0.265, 0.018] | 27 |
| p038:tc2-p1:014 | 38 | 14 | body | page_feature:color_heavy | WITHHELD | [0.337, 0.471, 0.341, 0.019] | 35 |
| p038:tc2-p1:015 | 38 | 15 | body | page_feature:color_heavy | WITHHELD | [0.298, 0.494, 0.617, 0.018] | 68 |
| p038:tc2-p1:020 | 38 | 20 | body | page_feature:color_heavy | WITHHELD | [0.102, 0.635, 0.239, 0.034] | 24 |
| p038:tc2-p1:021 | 38 | 21 | body | page_feature:color_heavy | WITHHELD | [0.127, 0.674, 0.576, 0.018] | 65 |
| p038:tc2-p1:022 | 38 | 22 | question | page_feature:color_heavy | WITHHELD | [0.129, 0.698, 0.776, 0.019] | 87 |
| p038:tc2-p1:023 | 38 | 23 | body | agree_text,page_feature:color_heavy | WITHHELD | [0.092, 0.737, 0.406, 0.08] | 134 |
| p038:tc2-p1:024 | 38 | 24 | body | agree_text,page_feature:color_heavy | WITHHELD | [0.09, 0.83, 0.41, 0.082] | 147 |
| p038:tc2-p1:027 | 38 | 27 | sidebar | agree_text,page_feature:color_heavy | WITHHELD | [0.539, 0.769, 0.369, 0.147] | 282 |
| p039:tc2-p1:007 | 39 | 7 | body | agree_order | CONFLICT | [0.153, 0.379, 0.092, 0.013] | 10 |
| p039:tc2-p1:008 | 39 | 8 | body | agree_order | CONFLICT | [0.157, 0.394, 0.074, 0.013] | 7 |
| p040:tc2-p1:003 | 40 | 3 | body | box_boundary | WITHHELD | [0.104, 0.134, 0.806, 0.137] | 517 |

| figure | page | bbox | area | caption block | labels |
|---|---|---|---|---|---|
| p041:fig00 | 41 | [0.098, 0.432, 0.197, 0.042] | 0.0082 | — | 0 |
| p041:fig01 | 41 | [0.137, 0.542, 0.724, 0.118] | 0.0856 | — | 5 |
| p041:fig02 | 41 | [0.095, 0.747, 0.19, 0.046] | 0.0087 | — | 0 |
| p041:fig03 | 41 | [0.638, 0.084, 0.25, 0.228] | 0.057 | 023 | 0 |
| p040:fig00 | 40 | [0.079, 0.041, 0.202, 0.077] | 0.0156 | — | 1 |
| p040:fig01 | 40 | [0.187, 0.385, 0.638, 0.271] | 0.1728 | 007 | 0 |
| p040:fig02 | 40 | [0.079, 0.708, 0.206, 0.077] | 0.0159 | 007 | 1 |
| p038:fig00 | 38 | [0.002, 0.001, 0.24, 0.148] | 0.0356 | — | 0 |
| p038:fig01 | 38 | [0.094, 0.338, 0.048, 0.038] | 0.0018 | — | 1 |
| p038:fig02 | 38 | [0.09, 0.527, 0.063, 0.064] | 0.004 | — | 0 |
| p038:fig03 | 38 | [0.101, 0.632, 0.032, 0.023] | 0.0007 | — | 0 |
| p038:fig04 | 38 | [0.523, 0.735, 0.035, 0.027] | 0.001 | — | 0 |
| p039:fig00 | 39 | [0.085, 0.202, 0.033, 0.024] | 0.0008 | — | 0 |
| p039:fig01 | 39 | [0.339, 0.741, 0.307, 0.144] | 0.0443 | 015 | 0 |

**Bridge:** two no-crops runs identical = True (`c7a1a7a992c9…`); with-crops document `6b97c09e5b15…` blocks {'image': 6, 'heading': 8, 'withheld': 17, 'activity': 5, 'paragraph': 14, 'question': 4, 'caption': 3, 'sourceRef': 1} byTrust {'trustedStructuredLesson': 41, 'withheld': 17} semantic [] chapters 0 tutorScript False.

## Step 2 — second review (Lane C reading the renders) vs pipeline, per Bài 8 page

| PDF page | my learning blocks | found by pipeline | role agree | trusted | withheld | anchor verbatim | order inversions / pairs | pipeline learning blocks | pipeline-only | figures mine / pipeline | page features |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 38 | 19 | 19 | 15 | 7 | 12 | 16 | 0 / 136 | 22 | 3 | 0 / 5 | color_heavy, sidebar, figure, side_by_side |
| 39 | 13 | 13 | 9 | 12 | 1 | 9 | 0 / 66 | 14 | 1 | 1 / 2 | figure |
| 40 | 9 | 9 | 8 | 6 | 3 | 6 | 0 / 21 | 7 | 0 | 1 / 3 | figure |
| 41 | 9 | 9 | 8 | 9 | 0 | 8 | 0 / 21 | 9 | 0 | 1 / 4 | diagram, figure |

Totals over the 4 pages: my learning blocks 50, found 50, role agree 40, trusted 34, withheld 16, anchor-verbatim 39, order inversions 0 / 244 pairs, pipeline-only fragments 4.

Role disagreements (my role → pipeline role):

- p38 #6 «Sưu tầm và kể lại được»: objective → body (WITHHELD, page_feature:color_heavy)
- p38 #10 «(Hồ Chí Minh, Lịch sử nước ta,»: attribution → body (WITHHELD, page_feature:color_heavy)
- p38 #13 «Đọc thông tin, em hãy:»: question → body (WITHHELD, page_feature:color_heavy)
- p38 #14 «– Kể tên một số cuộc»: question → body (WITHHELD, page_feature:color_heavy)
- p39 #4 «– Kể câu chuyện về một»: question → body (TRUSTED)
- p39 #5 «– Chia sẻ điều em biết»: question → body (TRUSTED)
- p39 #7 «Câu chuyện Lịch sử»: box_label → body (CONFLICT, agree_order)
- p39 #12 «(Theo Nguyễn Thi, Thành Nam,»: attribution → body (TRUSTED)
- p40 #5 «(Theo Đinh Xuân Lâm, Trương Hữu Quýnh»: attribution → body (TRUSTED)
- p41 #3 «(Theo Đăng Khoa, Hoài Thu,»: attribution → body (TRUSTED)

### Gold pages (second reviewer) — gold vs pipeline vs Lane C

| page | printed | gold lesson | pipeline lesson (method) | Lane C lesson | gold blocks scored | found | role agree | trusted | text blocks | exact | exact (dash-insensitive) | char diffs | order inv / pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 41 | 39 | 9 | 8 (continuation) | 8 | 10 | 10 | 8 | 9 | 9 | 7 | 7 | 7 | 1 / 28 |
| 80 | 78 | 17 | 18 (continuation) | 18 | 7 | 7 | 5 | 5 | 6 | 3 | 3 | 54 | 0 / 10 |
- p41 b03 «(Theo Đăng Khoa, Hoài Thu»: gold attribution → pipeline body (TRUSTED); text exact False, char diff 3
- p41 b07 «Sự kiện»: gold table → pipeline figure_text (WITHHELD); text exact None, char diff None
- p41 b10 «Tìm hiểu và kể tên một số»: gold question → pipeline question (TRUSTED); text exact False, char diff 4
- p80 b01 «Miền Tây gồm các dãy núi cao»: gold body → pipeline body (TRUSTED); text exact False, char diff 3
- p80 b03 «CHÚ GIẢI»: gold table → pipeline figure_text (WITHHELD); text exact None, char diff None
- p80 b04 «Các nước đánh số»: gold table → pipeline figure_text (WITHHELD); text exact False, char diff 49
- p80 b08 «Trung Quốc là một trong những nước»: gold body → pipeline body (TRUSTED); text exact False, char diff 2

Gold agreement (Lane C vs gold annotator): p041 11 / 11 blocks agree, lesson number 9 → 8; p080 9 / 9 blocks agree, lesson number 17 → 18.

## Step 3 — header vs TOC, all 28 lessons

Status counts: {'RESOLVED_HEADER_TOC_AGREE': 6, 'WITHHELD_HEADER_MISSED_BY_REGEX': 5, 'RESOLVED_HEADER_ONLY': 17}; wide-regex probe (adds `Ã/ã` to the pipeline's `B[ÀÁẢẠ]I` header regex) finds 28 / 28 headers; pages attached to the wrong lesson under the pipeline regex: 17 / 123.

| Bài | header PDF (printed) | conf | form | TOC printed → PDF | wide-regex header PDF | status | header title | TOC title |
|---|---|---|---|---|---|---|---|---|
| 1 | 7 (5) | 0.95 | secondary | 5 → 7 | 7 | RESOLVED_HEADER_TOC_AGREE | QUỐC KÌ, QUỐC HUY, QUỐC CA | Vị trí địa lí, lãnh thổ, đơn vị hành chính, Quốc kì, Quốc huy, Quốc ca |
| 2 | 11 (9) | 0.95 | secondary | 9 → 11 | 11 | RESOLVED_HEADER_TOC_AGREE | THIÊN NHIÊN VIỆT NAM | Thiên nhiên Việt Nam.. |
| 3 | — | — | — | 16 → 18 | 18 | WITHHELD_HEADER_MISSED_BY_REGEX | — | Biển, đảo Việt Nam |
| 4 | 22 (20) | 0.6 | secondary | — | 22 | RESOLVED_HEADER_ONLY | DÂN CƯ VÀ DÂN TỘC Ở VIỆT NAM | Dân cư và dân tộc ở Việt Nam... |
| 5 | 27 (25) | 0.85 | secondary | — | 27 | RESOLVED_HEADER_ONLY | NHÀ NƯỚC VĂN LANG, NHÀ NƯỚC ÂU LẠC | Nhà nước Văn Lang, Nhà nước Âu Lạc. |
| 6 | 31 (29) | 0.85 | secondary | — | 31 | RESOLVED_HEADER_ONLY | VƯƠNG QUỐC PHÚ NAM | Vương quốc Phù Nam... |
| 7 | — | — | — | 32 → 34 | 34 | WITHHELD_HEADER_MISSED_BY_REGEX | — | Vương quốc Chăm-pa... |
| 8 | 38 (36) | 0.95 | secondary | 36 → 38 | 38 | RESOLVED_HEADER_TOC_AGREE | THỜI KĨ BẮC THUỘC | Đấu tranh giành độc lập thời kì Bắc thuộc... |
| 9 | 42 (40) | 0.95 | secondary | 40 → 42 | 42 | RESOLVED_HEADER_TOC_AGREE | TRIỀU LÝ VÀ VIỆC ĐỊNH ĐÔ Ở THĂNG LONG | Triều Lý và việc định đô ở Thăng Long .. |
| 10 | 46 (44) | 0.85 | secondary | — | 46 | RESOLVED_HEADER_ONLY | CHỐNG QUÂN MÔNG - NGUYÊN XÂM LƯỢC | Triều Trần xây dựng đất nước và kháng chiến chống quân Mông - Nguyên xâm lược ..... 44 |
| 11 | — | — | — | 50 → 52 | 52 | WITHHELD_HEADER_MISSED_BY_REGEX | — | Ôn tập. |
| 12 | 53 (51) | 0.6 | secondary | — | 53 | RESOLVED_HEADER_ONLY | KHỞI NGHĨA LAM SƠN VÀ TRIỀU HẬU LÊ | Khởi nghĩa Lam Sơn và Triểu Hậu Lê.. |
| 13 | — | — | — | — | 58 | WITHHELD_HEADER_MISSED_BY_REGEX | — | Triều Nguyễn |
| 14 | 63 (61) | 0.6 | secondary | — | 63 | RESOLVED_HEADER_ONLY | CÁCH MẠNG THÁNG TÁM NĂM 1945 | Cách mạng tháng Tám năm 1945 |
| 15 | 67 (65) | 0.95 | secondary | 65 → 67 | 67 | RESOLVED_HEADER_TOC_AGREE | CHIẾN DỊCH ĐIỆN BIÊN PHỦ NĂM 1954 | Chiến dịch Điện Biên Phủ năm 1954 |
| 16 | 71 (69) | 0.85 | secondary | — | 71 | RESOLVED_HEADER_ONLY | CHIẾN DỊCH HỒ CHÍ MINH NĂM 1975 | Chiến dịch Hồ Chí Minh năm 1975.. |
| 17 | 74 (72) | 0.85 | secondary | — | 74 | RESOLVED_HEADER_ONLY | ĐẤT NƯỚC ĐỔI MỚI | Đất nước Đối mới |
| 18 | 78 (76) | 0.85 | secondary | — | 78 | RESOLVED_HEADER_ONLY | NƯỚC CỘNG HOA NHÂN DÂN TRUNG HOA | Nước Cộng hoa Nhân dân Trung Hoa. |
| 19 | 84 (82) | 0.85 | secondary | — | 84 | RESOLVED_HEADER_ONLY | NƯỚC CỘNG HOA DÂN CHỦ NHÂN DÂN LÀO | Nước Cộng hoa Dân chủ Nhân dân Lào |
| 20 | 88 (86) | 0.85 | secondary | — | 88 | RESOLVED_HEADER_ONLY | VƯƠNG QUỐC CAM-PU-CHIA | Vương quôc Cam-pu-chia |
| 21 | 92 (90) | 0.95 | secondary | 90 → 92 | 92 | RESOLVED_HEADER_TOC_AGREE | HIỆP HỘI CÁC QUỐC GIA ĐÔNG NAM Á | Hiệp hội các quốc gia Đông Nam Á |
| 22 | 95 (93) | 0.85 | secondary | — | 95 | RESOLVED_HEADER_ONLY | CÁC CHÂU LỤC VÀ ĐẠI DƯƠNG TRÊN THỂ GIỚI | Các châu lục và đại dương trên thể giới.. |
| 23 | — | — | — | 98 → 100 | 100 | WITHHELD_HEADER_MISSED_BY_REGEX | — | Dân số và các chủng tộc chính trên thế giới |
| 24 | 103 (101) | 0.6 | secondary | — | 103 | RESOLVED_HEADER_ONLY | VĂN MINH AI CẬP | Văn minh Ai Cập.. |
| 25 | 107 (105) | 0.85 | secondary | — | 107 | RESOLVED_HEADER_ONLY | VĂN MINH HY LẠP | Văn minh Hy Lạp. |
| 26 | 111 (109) | 0.85 | secondary | — | 111 | RESOLVED_HEADER_ONLY | XÂY DỰNG THẾ GIỚI XANH - SẠCH - ĐẸP | Xây dựng thế giới xanh - sạch - đẹp ... |
| 27 | 114 (112) | 0.85 | secondary | — | 114 | RESOLVED_HEADER_ONLY | XÂY DỰNG THẾ GIỚI HOA BÌNH | Xây dựng thế giới hoa bình .. |
| 28 | 118 (116) | 0.85 | secondary | — | 118 | RESOLVED_HEADER_ONLY | ÔN TẬP | Ôn tập |

Bài 8: header PDF 38 (TOC printed 36), next header PDF 42, pages [38, 39, 40, 41]; pipeline title `THỜI KĨ BẮC THUỘC` vs TOC title `Đấu tranh giành độc lập thời kì Bắc thuộc...`.

