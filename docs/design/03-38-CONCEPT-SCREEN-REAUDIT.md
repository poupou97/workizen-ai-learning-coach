# 03 — 38 CONCEPT SCREEN RE-AUDIT (WAL-111 · sau full corpus · snapshot e47277a)

Audit vòng 1 (38-SCREEN-AUDIT.md) đối chiếu lại với evidence 126.5k units.
**Verdict ĐỔI sau corpus: 4 màn** (đánh dấu ▲). Ad Eligibility: NEVER /
POSSIBLE_TRANSITION (PT) / PARENT_PREMIUM (PP) / RESEARCH (R).

| # | Screen | Corpus evidence mới | Verdict | Ads |
|---|---|---|---|---|
| 01 | Onboarding | — | KEEP (sửa §26) | NEVER |
| 02 | Learner Profile | — | MODIFY (tối giản) | NEVER |
| 03 | Subject Setup | registry 31 môn thật/lớp → grid sinh từ data | MODIFY | NEVER |
| 04 | Timetable | — | MODIFY (bỏ auto-gợi-ý) | NEVER |
| 05 | Home | 5 intent = 5 Learning Intent ✓ | MERGE→home1 | PT (transition về Home sau session — R) |
| 06 | Subjects | 31 môn, position từ 7.626 lessons | MODIFY (bỏ %) | PT |
| 07 | Subject Home | worked-example driven Toán (EXAMPLE 1.305) → thêm khối «Ví dụ mẫu» | KEEP-MODIFY | PT |
| 08 | Camera | Mĩ thuật cần artifact-capture → camera thêm use case chụp bài làm sáng tạo ▲mở rộng | KEEP | NEVER |
| 09 | Confirm | — | KEEP | NEVER |
| 10 | Tutor Start | — | MODIFY | NEVER |
| 11 | Diagnostic | — | REPLACE (ErrorHypothesis) | NEVER |
| 12 | Workspace | **▲ NÂNG CẤP verdict: «vẽ» = verb #1 band 10-12 (884) + Toán vẽ 270** → Workspace PHẢI có drawing/diagram mode từ P1 (không đợi P2 Canvas) | KEEP-MODIFY+ | NEVER |
| 13 | Hint | — | MODIFY (engine ladder) | NEVER |
| 14 | Your Turn | — | KEEP | NEVER |
| 15 | Success | — | MODIFY (feedbackFor) | PT (SAU màn success, không trong) |
| 16 | Why Method | 29 methods có trang | KEEP khung/REPLACE nội dung | NEVER |
| 17 | Source | — | REPLACE (SGK/SGV provenance) | NEVER |
| 18 | Review | — | REPLACE (reviewStateOf) | PT |
| 19 | Learning Map | 7.626 lessons + claim | MODIFY | PT |
| 20 | Quiz | MCQ-family cao nhất TN&XH 10% — QuizSelect đúng band 1-3 | KEEP-MODIFY | NEVER (in-quiz) |
| 21 | Assessment | — | SPLIT (mode riêng) | NEVER |
| 22 | Result | — | MODIFY | PT |
| 23 | Vietnamese | READING 705 + viết 1.148 — XÁC NHẬN MẠNH | KEEP | PT |
| 24 | Essay | Ngữ văn viết 836 — Compose full cần sớm hơn (P1) ▲ | MODIFY+ | NEVER |
| 25 | Physics | đúng band 10-12; 6-9 là KHTN | KEEP-MODIFY | NEVER-learning |
| 26 | Chemistry | như trên | KEEP-MODIFY | NEVER-learning |
| 27 | History | SOURCE_TEXT 54 + NOTE 395 = chất liệu source-reading THẬT | MODIFY | PT (browse tư liệu) |
| 28 | Geography | vẽ/sơ đồ 121+438 (LS&ĐL) | KEEP-MODIFY | PT |
| 29 | AI Learning | QĐ2422 đã ingest | REPLACE | NEVER (child) |
| 30 | Sessions | — | KEEP-MODIFY | PP (advanced history = premium R) |
| 31 | Progress | — | REPLACE (edu metrics) | PP (insight sâu) |
| 32 | Parent Home | — | MODIFY | PP (Premium khu vực) |
| 33 | Parent Detail | — | MODIFY sâu | PP |
| 34 | Multi-child | — | MODIFY (Family Manager) | PP |
| 35 | SAM Voice | **▲ NÂNG ưu tiên: Tiếng Anh = môn LỚN NHẤT corpus (22.9k) + band 1-2 oral-heavy** → Voice từ P4 lên P2 | MODIFY+ | NEVER |
| 36 | Library | NOTE 782 (10-12) + 395 (Sử) = «đọc thêm» có chất liệu thật → khu B/D có nội dung ngay ▲ | REPLACE (5 khu, giữ) | PT (browse) — sponsored ≠ recommendation |
| 37 | Notifications | — | MODIFY | NEVER trong notif |
| 38 | Settings | — | MODIFY | NEVER |

## Tổng kết

**KEEP 9 · MODIFY 21 · REPLACE 6 · SPLIT 1 · MERGE 1 · DEFER 0 nguyên màn** (4 verdict
nâng cấp ▲: 12 drawing-mode, 24 compose-sớm, 35 voice-lên-P2, 36 library-có-nội-dung).
**Production: ~24 routes + 16 surfaces** — Workspace/Hint/YourTurn/Success = **1 Learning
Workspace + 4 pedagogical states** (§10); Quiz/Assessment = 1 surface 2 policy-mode.
**Missing concepts (corpus đòi, bộ 38 không có):** Ngoại-ngữ 4-kỹ-năng (môn lớn nhất!) ·
chuyên-đề 10-12 browser · reflection surface (HĐTN) · artifact-capture (Mĩ thuật) ·
teacher-mode (order business đòi Teacher Free).
