# 01 — CURRICULUM UX EVIDENCE REPORT (WAL-111 · snapshot K12-2026-09-02)

**Snapshot khoá:** `docs/ingest-manifests/SNAPSHOT-K12.json` @ commit e47277a.
Mọi số dưới đây từ snapshot — không cập nhật ngầm.

## 1. Corpus & coverage (STRUCTURAL ≠ SEMANTIC — báo riêng)

- **531/531 documents SUCCESS** (0 FAILED, 0 PARTIAL ở tầng OCR; 6 duplicate F19 tách) ·
  62.729 trang · 12 lớp · 31 môn · 301 SGK + 220 SGV.
- **STRUCTURAL:** 7.626 lessons; boundary có ở 406 sách (OK 129 + OK_ALT 40 + PARTIAL 237);
  **NO_TOC 125 sách** (chủ yếu ÂN/MT/NN/HĐTN — dùng chủ-đề/unit, cấu trúc alt mới phủ một phần);
  2.219/7.626 tên bài mined (29%) — phần còn lại cần pass title sâu hơn (KHÔNG bịa).
- **SEMANTIC:** 126.552 units generic-GDPT2018 trên 525 docs (tầng KHUNG HOẠT ĐỘNG) +
  2.584 units tầng-sâu Toán/TV qua SCALE GATE 30-check + 569 LearningObjectives (SGV Toán 4-5)
  + 29 methods có trang + Q-matrix 1.109 + **llmInferred = 0**.
  ⚠️ **Semantic SÂU (concept/SkillCase mapping) mới phủ Toán 4-5 + TV5** — mọi kết luận
  môn khác dựa tầng khung, gắn nhãn SOURCE_EVIDENCE(khung)/INFERENCE tương ứng.

## 2. «SGK K-12 thực sự yêu cầu học sinh làm gì?» [SOURCE_EVIDENCE]

**Role theo band** (126.5k units):

| Band | Units | Dài TB | Cấu trúc nổi bật |
|---|---|---|---|
| 1-2 | 9.962 | 604 ký tự | EXERCISE 74% · ACTIVITY 23% · READING 327 |
| 3-5 | 25.000 | 671 | EXERCISE 82% · ACTIVITY 15% · OBSERVATION xuất hiện |
| 6-9 | 38.870 | 737 | + EXAMPLE 916 · EXPERIMENT 100 (KHTN) |
| 10-12 | 52.720 | 808 | Units NHIỀU NHẤT + NOTE 782 (đọc thêm/chuyên sâu) |

**Động từ hành động** (17.6k lệnh match, lexicon VN):

- **1-2: viết·đọc·nói·tìm·chọn·nghe·kể** — ngôn ngữ + ORAL thống trị → voice-heavy cho
  band này giờ là SỐ ĐO, không phải age-theory. MCQ-family (chọn/nối/điền/khoanh) đậm
  nhất ở TN&XH (10% lệnh) ✓ khớp QuizSelect đã build.
- **3-5: đọc·viết·tìm·quan sát·đo·vẽ** — bắt đầu quan sát/đo đạc.
- **6-9: đo·viết·VẼ·đọc·nêu·thực hành** — hands-on vọt lên.
- **10-12: VẼ (884 — số 1!)·đo·viết·nêu·vận dụng·thực hành** — «vẽ sơ đồ/đồ thị/lược đồ»
  là hành động lớn nhất khối cuối ⇒ **Drawing/Diagram surface là BẮT BUỘC band 6-12**,
  không phải nice-to-have. «Tính» (287) THẤP hơn vẽ/đo ở 10-12 [caveat: Toán 4-5 nằm ở
  pipeline sâu riêng, không trong đếm này].

## 3. Đặc thù role theo môn [SOURCE_EVIDENCE]

TV: READING 705 (lớn nhất) · Toán: EXAMPLE 1.305 (worked-example driven!) · KHTN:
EXPERIMENT 100 + OBSERVATION 45 · Sử/LS&ĐL: SOURCE_TEXT 54 + NOTE 395 («Em có biết»
dày đặc — tư liệu đọc thêm là chất liệu môn Sử) · ÂN: hát/nghe/đọc(nhạc) · GDTC/HĐTN:
vận dụng/thảo luận/đánh giá (family G Creative/Performance xác nhận bằng số).

## 4. Gaps ghi thật

Ngoại ngữ (22.9k units — MÔN LỚN NHẤT corpus) chưa có lexicon EN → verb-mining không áp
[UNKNOWN, cần adapter EN] · title coverage 29% · NO_TOC 125 sách cần structural-alt sâu ·
semantic sâu ngoài Toán/TV = việc của các batch adapter kế (không claim trước).

## 5. Cross-grade [SOURCE_EVIDENCE + INFERENCE]

Độ dài unit tăng tuyến tính 604→808; EXERCISE share tăng theo band; ACTIVITY (khung 4
bước GDPT) giữ ~15-23% mọi band — khung Khởi-động/Khám-phá/Luyện-tập/Vận-dụng là bất
biến xuyên cấp [SOURCE], củng cố quyết định shared-core extractor và Learning-Workspace-
nhiều-state (§10 order).
