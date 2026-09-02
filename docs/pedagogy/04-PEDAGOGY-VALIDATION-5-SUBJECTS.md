# 04 — PEDAGOGY VALIDATION · 5 SUBJECT FAMILIES (v0)

> WAL-130 · test: `test/core/pedagogy/subject_validation_test.dart` (29 test pedagogy xanh).
> Learner scenario là MÔ PHỎNG CÓ DÁN NHÃN (`scenario-sim-v1`) — WAL-49: simulation FALSIFY
> được, KHÔNG claim validated-on-real-learners. Mỗi «⚠️ CHARACTERIZATION» là gap ĐƯỢC PHÁT
> HIỆN CHỦ ĐÍCH và ghi thành change-required — đúng mục đích của validation.

## 1. TOÁN (2 case, 2 grade — chống overfit B6)

- **Case 1 — Toán 5 B6** (blueprint `bp:toan5:b6`, nguồn 05-sgv-toan-5 p36): drive TutorSession
  THẬT — 0 vi phạm khi sai→hint→đúng; EVIDENCE_MISSING khi hint-ngay (File 03 §4).
- **Case 2 — Toán 6 b15 số nguyên** (`bp:toan6:b15`, 06-sgv-toan-6 p84 + misconception
  bỏ-ngoặc-dấu-trừ): đúng độc lập tuân thủ; đúng-sau-demonstration trong cap nhưng thiếu
  independentAttempt ⇒ bị đòi evidence — «xem làm mẫu» không phải học xong.
- **Future-knowledge leakage — kernel THẬT chặn**: stage lớp 4 chưa có «mẫu số chung» ⇒
  `TutorScope.forProblem` với catalogue lớp 5 trả RỖNG (test). Chiều ngược có bằng chứng
  corpus: **06-sgk-toan-6-tap-mot p53 b18 Ví dụ 6 dùng BCNN** («Ta có BC…») — BCNN xuất hiện
  Ở LỚP 6, không phải lớp 5 B6; đây chính là ranh giới mà output_guard + TutorScope giữ.
- Demonstration timing + fading: REVEAL gate (tự thử trước) + ±1 ladder đã có test/mutation
  từ WAL-86/87. Transfer: `transferRequired=true` ở B6, cơ chế TransferProbe WAL-103.

## 2. TIẾNG VIỆT (đọc-hiểu — `bp:tv3:doc-hieu`)

Corpus thật: `03-sgk-tieng-viet-3-tap-mot:p027:0126` [READING b3] «ĐỌC… NHẬT KÍ TẬP BƠI» —
đúng dạng đọc-văn-bản→trả-lời. Scenarios: nhận-diện độc lập + giải-thích có scaffold ≤
partialScaffold ⇒ 0 vi phạm; **SAM đọc hộ trọn đáp án (fullSolution) ⇒ ASSISTANCE_OVER_CAP**
— «không đọc hộ» là luật kiểm được, không phải lời dặn. recognize ≠ explain thể hiện ở acts
(diagnosticProbe vs askExplanation); write/revise thuộc Compose (WAL-98, giữ nguyên SAM-không-
viết-hộ). WRITING/REVISION scenario đầy đủ: để PED-E gắn contract (chưa claim ở đây).

## 3. KHTN/KHOA HỌC (`bp:khoa4:quan-sat`)

Corpus thật: `04-sgk-khoa-hoc-4:p007:0018` [OBSERVATION b17] «Quan sát và nhận xét hướng chảy
của nước…». **⚠️ FINDING CHỦ ĐÍCH**: kịch bản «demo TRƯỚC khi trẻ quan sát» — blueprint v0
KHÔNG bắt được (chưa có rule SEQUENCE_ORDER; characterization test giữ chỗ). **Change
required v1**: thêm luật thứ-tự (first-move-must-be-learner khi intent DISCOVER mở đầu).
Tách learner-observation ≠ source-fact ≠ SAM-interpretation: cần object model riêng ở
surface Experiment (WAL-132/113) — evidence log hiện chỉ mang correctness, chưa mang «ai
quan sát». Ghi thành gap cho PED-F.

## 4. LỊCH SỬ (`bp:su10:su-lieu`)

Corpus thật: `10-sgk-lich-su-10:p010:0014` [EXERCISE b1] «Dựa vào Tư liệu 1 (tr. 7), hãy cho
biết…» — bài tập YÊU CẦU khai thác tư liệu, đúng SourceReader. Blueprint Sử là blueprint
NGHIÊM NHẤT: cap strategicHint, KHÔNG act reveal/workedExample (test tĩnh + scenario «làm mẫu
kết luận» ⇒ ASSISTANCE_OVER_CAP ngay). **Gap ghi nhận**: NGUỒN-NÓI-GÌ ≠ SAM-DIỄN-GIẢI ≠
HS-KẾT-LUẬN cần kiểu dữ liệu claim/evidence-use riêng (đã đặt ở WAL-113 B2) — log hiện tại
chưa biểu diễn «trích dẫn tư liệu nào cho claim nào». Không biến Sử thành timeline-only:
blueprint không có act nhớ-sự-kiện nào; goal là lập luận từ evidence.

## 5. NGOẠI NGỮ (`bp:nn3:listening`)

Nguồn pedagogy: SGV GS3 Goal-block (781 skillActivity đo được — LISTENING 385). Corpus SGK
EN qua extractor VN gần rỗng (`03-sgk-tieng-anh-3-tap-1` chỉ SECTION_TEXT/EXERCISE thô) —
xác nhận lại: **semantic adapter EN (WAL-117) là tiền đề** cho validation sâu hơn.
Scenario: nghe-2-lần (hint=replay) rồi đúng độc lập ⇒ 0 vi phạm. **⚠️ FINDING CHỦ ĐÍCH**:
«lộ transcript» và «phát lại chậm» CÙNG map workedStep — v0 không phân biệt được
(characterization test). **Change required**: `interventionKind` (REPLAY/SLOW/TRANSCRIPT/…)
trong evidence contract TRƯỚC khi voice/listening lên production — chuyển WAL-123/131.
Listening ≠ reading-with-audio giữ ở act: không act nào đưa văn bản trong PRACTICE.

## 6. Tổng hợp violations & changes required

| # | Finding | Đích |
|---|---|---|
| 1 | Blueprint v0 thiếu rule SEQUENCE_ORDER (Khoa: demo-trước-quan-sát lọt) | blueprint v1 (WAL-131 harness sẽ đòi) |
| 2 | Evidence thiếu interventionKind (NN: transcript vs replay không phân biệt) | WAL-123 + WAL-131 contract |
| 3 | Sử cần claim/evidence-use model (nguồn ≠ diễn giải ≠ kết luận) | WAL-113 B2 |
| 4 | KHTN cần «ai quan sát» trong evidence (learner vs source) | WAL-132 Experiment surface |
| 5 | EN corpus SGK cần adapter riêng trước khi validate 4 skill đầy đủ | WAL-117 |

## 7. Acceptance §36 điểm 10

5 family đều có: source thật (SGK/SGV id+trang) · SkillCase/activity · goal · blueprint ·
act sequence · learner scenarios · evidence rule · violations found · changes required.
KHÔNG family nào được claim «validated trên học sinh thật» — chỉ falsify được kiến trúc,
và ĐÃ falsify ra 5 changes ở §6.
