# UI/UX Pattern Library — 15 họ pattern, MỖI pattern ánh xạ domain state WAL

**Ngày:** 2026-09-01 (WAL-71) · Nguồn: benchmark A (Brilliant/Koji · Khanmigo · Photomath) +
VN-P0 (QANDA · Dicamon) + B/C (IXL · Quizlet · ClassDojo · AutoMath · Duolingo · Prodigy…)
· thang §35: [OFFICIAL-PRODUCT]=trang/app chính thức · [SECONDARY]=báo/review · [WAL]=domain có sẵn
**Luật:** trích pattern TƯƠNG TÁC, không copy hình; pattern không ánh xạ được domain state = không vào thư viện.

## Phát hiện định vị từ VN-P0 (câu hỏi chốt của Founder)

Sản phẩm VN hiểu điều global không làm: **học sinh VN làm việc THEO SÁCH** — Dicamon tổ chức
điều hướng theo đúng SGK/SBT (chọn sách → trang → bài) [OFFICIAL-PRODUCT book.dicamon.vn], và
**luyện đề/kiểm tra là nhu cầu hạng nhất** (giữa kỳ/cuối kỳ/tốt nghiệp). QANDA đi xa hơn
Photomath một bậc: **chụp BÀI LÀM TAY của trẻ để AI sửa** — learner-work-as-input
[OFFICIAL-PRODUCT App Store]. ⇒ WAL bám-SGK-có-provenance không chỉ đúng pháp lý/sư phạm mà
đúng HÀNH VI BẢN ĐỊA; và "sửa bài làm" chính là process-level evidence mà kiến trúc
LearningEvidence sinh ra để chứa. ⚠️ Mặt tối cùng các app này: scan→answer nuôi chép bài —
WAL giữ khác biệt SCAN→HYPOTHESIS→CONFIRM→DIAGNOSE→TEACH.

## 15 họ pattern

| # | Pattern | Học từ | Quyết định tương tác cho WAL | Domain state [WAL] |
|---|---|---|---|---|
| 1 | NEXT_ACTION | IXL diagnostic→action plan; Duolingo path (cấu trúc, KHÔNG nhận engagement-first) | Màn "Hôm nay" mở bằng MỘT hành động + lý do trẻ-đọc-được; không menu | `AdaptiveDecision.action + reason` |
| 2 | CONTEXTUAL_TUTOR | Brilliant/Koji: tutor TRONG bài, thấy thao tác, chỉnh realtime, không đưa đáp án; Khanmigo Socratic | SAM là lớp phủ trên bài đang làm, mở lời bằng câu hỏi về bước hiện tại; không tab chat riêng | TutorScope + LearningStage |
| 3 | CAMERA_CONFIRMATION | (khoảng trống thị trường — QANDA/Photomath/Dicamon đều scan→answer thẳng) | "Tớ đọc được thế này" là BƯỚC BẮT BUỘC: hiển thị biểu thức + CONFIRM/CORRECT/RETAKE | `PerceptionHypothesis→ConfirmedProblem` (WAL-64, type-enforced) |
| 4 | PERCEPTION_CORRECTION | QANDA sửa-bài-làm (input là chữ trẻ) | Trẻ sửa trực tiếp trên hypothesis; mọi sửa được GHI (Student Correction Rate #5) | `ConfirmationKind.corrected` |
| 5 | DIAGNOSTIC_PROBE | Khanmigo "what have you tried?"; IXL diagnostic | Khi bất định: MỘT câu hỏi ngắn trước khi dạy; khung "để hiểu con đang nghĩ gì" | `insufficientEvidence→diagnosePrerequisite`, `isolateSkills` |
| 6 | PROGRESSIVE_HINT | OATutor hint ladder + scaffold-là-câu-hỏi; AutoTutor pump→hint→prompt→assertion | Thang WAL-68 ±1 nấc; mỗi nấc là act có mặt mascot; scaffold sinh evidence | SupportLevel + EvidenceKind |
| 7 | YOUR_TURN | Brilliant learning-by-doing (bài là chuỗi lượt của TRẺ) | Sau mỗi can thiệp, lượt về trẻ là MẶC ĐỊNH; SAM_YOUR_TURN + vùng làm bài sáng lên | fading (WAL-68), `independentAttempt` |
| 8 | STEP_BACK | (không sản phẩm nào làm rõ — khác biệt WAL từ triết lý) | SAM thu nhỏ về góc khi trẻ đang mạch làm; im lặng là feature nhìn thấy được | fading + SAM_STEP_BACK |
| 9 | LEARNING_BY_DOING | Brilliant single-concept + blocked problems; Quizlet phiên ngắn active-recall | Mỗi phiên = 1 concept, chuỗi bài ngắn; không video-lecture | SkillCase + ReviewSchedule |
| 10 | REVIEW_DUE | skillcoco SR-queue ngang hàng nội dung mới; Quizlet progression | Hàng ôn nằm NGAY màn Hôm nay; sắc thái vòng-lặp thân thiện, không đỏ | `ReviewUrgency` |
| 11 | LEARNING_MAP | Khan mastery map; Dicamon bám-cấu-trúc-SGK | Bản đồ theo Concept↦dạng với 3 trạng thái nhìn được: vững/đang học/CHƯA THỬ; điều hướng phụ trợ THEO SÁCH (chương/bài) cho quen thuộc | ConceptSummary (coverage nhìn thấy được) |
| 12 | PARENT_TONIGHT_ACTION | ClassDojo family hierarchy; Khan parent (số-nhiều làm loãng — tránh) | Màn phụ huynh mở bằng MỘT khuyến nghị + CÁCH GIÚP ("Đừng giải ngay — hỏi con vì sao chọn mẫu số đó") | `explainConcept` + citation |
| 13 | UNCERTAINTY | (khoảng trống — không app nào nói "tôi chưa chắc") | SAM_ADMIT_UNCERTAINTY là state thật: caseUnknown/LOW_CONFIDENCE có mặt mascot + câu thoại riêng | fail-closed states (5 chỗ trong domain) |
| 14 | VOICE_HINT | OATutor TTS-per-hint; Khanmigo voice | POC: ĐỌC gợi ý thành lời (một nút loa trên hint) — không voice-chat tự do | hint events (không đổi domain) |
| 15 | MASCOT_PEDAGOGICAL_STATE | Duolingo character-driven (KHÔNG nhận engagement-first); Prodigy (KHÔNG nhận game economy) | 13 state audit MASCOT-STATE-SYSTEM + 2 thiếu; state gắn SỰ KIỆN THẬT của engine, không trang trí | mọi state ↔ domain event (bảng đã có) |

## PRE-CAPTURE (WAL-65 — gate ĐÃ THÀNH MÃ, phần khung hình)
AutoMath/Photomath: khung ngắm + auto-crop + guidance mờ/sáng [SECONDARY]. WAL state machine:
FIT_ONE_PROBLEM · MOVE_CLOSER · MORE_LIGHT · HOLD_STEADY · TOO_BLURRY — mascot CAMERA_SCAN
làm gương mặt của khung ngắm; chặn thượng nguồn rẻ hơn vá hạ nguồn (số WAL-63 làm chuẩn đo).

**Đã ship (`precapture_quality.dart`, 5 test):** `assessFrame(GrayFrame)` → OK ·
TOO_DARK («bật thêm đèn») · TOO_BRIGHT («nghiêng vở cho đỡ bóng») · TOO_BLURRY («giữ máy
yên một nhịp») — sáng kiểm TRƯỚC nét (ảnh tối thì số đo nét vô nghĩa); phương sai Laplacian
ngưỡng 1500 hiệu chỉnh trên trang tổng hợp (nét ≈29.000 vs blur ≈430); lời SAM không đổ lỗi
(test quét). Thiết bị chỉ việc downscale preview → grayscale → gọi hàm.
**Chưa ship (device):** FIT_ONE_PROBLEM/MOVE_CLOSER/REMOVE_HAND cần phát hiện bố cục thật;
hiệu chỉnh ngưỡng trên khung hình thật — WAL-84.

## REJECT ghi sổ
StudyFetch feature-buffet (MVP một vòng lặp làm thật tốt) · Duolingo Max engagement-first ·
Prodigy game-economy · PhotoStudy human-tutor (research-only) · scan→answer làm bề mặt chính.

Sources: [Brilliant](https://brilliant.org/about/) · [Edtech Insiders — Sue Khim/Koji](https://edtechinsiders.buzzsprout.com/1877869/episodes/19457440) · [QANDA App Store VN](https://apps.apple.com/vn/app/id1270676408) · [Dicamon](https://book.dicamon.vn/sach-giao-khoa) · [Dicamon App Store](https://apps.apple.com/us/app/id1529833740) + các nguồn đã dẫn trong EDUCATION-UX-RESEARCH.md
