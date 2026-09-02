# 07 — CROSS-SUBJECT ARCHITECTURE VERDICT (WAL-113 B3)

Sau 3 flow chạy thật trên dữ liệu thật — Toán (WAL-108), Tiếng Việt Reader,
Sử SourceReader — trả lời: phần nào SHARED, phần nào SUBJECT-SPECIFIC, phần
nào đang Math-hardcode. Mỗi dòng kèm bằng chứng code. KHÔNG claim
cross-subject chỉ vì interface nhìn generic.

## 1. SHARED THẬT (đã chứng minh bằng 3 môn chạy chung)

| Object | Bằng chứng | Ghi chú |
|---|---|---|
| LearningEvent/EvidenceLog | `lib/core/student/learning_evidence.dart:71` — TV phát `independentAttempt` correct=null, Sử phát cùng kiểu, Toán phát đủ chuỗi | evidence schema KHÔNG đổi một trường nào khi thêm 2 môn |
| recordSession (một chỗ ghi) | `lib/features/shell/session_recorder.dart:25` — Toán gọi từ `slice_flow.dart:289`, TV/Sử gọi từ `subject_home_screen.dart` (_openReading/_openSource) | JSONL trên Nokia: session `tieng-viet` cạnh session Toán, cùng format |
| LessonIndex (mục lục môn×bài) | `lib/features/subjects/lesson_index.dart` — 10 môn từ MỘT parser | v2 mang tvReadings + suSources không phá schema cũ (test real-file) |
| Read-gate pattern | Reader `_markRead` (`reader_screen.dart`) và SourceReader `_markReadSource` (`source_reader.dart`) — cùng họ REVEAL gate của Compose | «đọc xong ≠ bằng chứng» giữ nguyên ở cả hai |
| UNKNOWN ≠ SAI | Reader open-question + SourceReader `_conclude` đều emit `correct: null` — 2 mutation (M1, M4) chứng minh test giữ luật | doctrine xuyên môn, không phải luật Toán |
| SurfaceKind resolver | `learning_activity.dart` `resolveSurface` — readRespond→reader dùng CHUNG cho fixture TV5-t2 và activity mined t1 | một chỗ ánh xạ duy nhất (F8) |

## 2. SUBJECT-SPECIFIC ĐÚNG NGHĨA (không ép chung được — và KHÔNG NÊN ép)

- **Sử cần 3 tầng claim có KIỂU riêng** (`source_reader.dart`: `SourceClaim` /
  `SamInterpretation` / `StudentConclusion`). LearningActivity KHÔNG chứa được
  cấu trúc này — nếu nhét excerpt vào `passage` của Reader thì mất ranh giới
  NGUỒN/DIỄN GIẢI và mất attribution bắt buộc. Falsification đúng như File 04
  dự đoán: **không ép Step Solver/Reader của môn khác vào Sử.**
- **TV recognize ≠ explain ≠ apply**: corpus TV5 tách rõ (b3 «Tìm từ lặp» =
  selectIdentify với đáp án; câu hỏi mở «Vì sao…» = readRespond không đáp án;
  b4 «Viết 2-3 câu» = compose). Ba demand → ba SkillCase — cơ chế đã chứng
  minh ở `cross_activity_case_test.dart` (không collapse-gap).
- **Đáp án**: Toán có đáp án tính được; TV/Sử SGK KHÔNG in đáp án ⇒
  `TvQuestion`/`SuSource` cố ý KHÔNG có trường đáp án — fail-closed theo
  CẤU TRÚC dữ liệu (mutation M5: bỏ guard attribution ⇒ test đỏ).

## 3. MATH-HARDCODE CÒN LẠI (ghi thật, chưa sửa trong WAL-113)

| Chỗ | Bằng chứng | Hệ quả |
|---|---|---|
| `openCanonicalProblem` chỉ nhận CanonicalProblem (expression) | `slice_flow.dart:83` | TV/Sử phải đi entry riêng qua SubjectHome — chấp nhận được ở P0, hợp nhất khi có nhiều surface hơn |
| `toanExercises` là map riêng trong LessonIndex | `lesson_index.dart` | tên trường lộ môn; tvReadings/suSources cũng vậy — TRADE-OFF có chủ đích: schema thật thà theo NGUỒN dữ liệu (qmap vs units vs ocr-body), không giả vờ đồng nhất khi pipeline mining khác nhau |
| TutorSession ±1 ladder + interventionId | `tutor_session.dart` | chỉ có ý nghĩa với bài giải-theo-bước; TV/Sử không dùng — ĐÚNG (không phải nợ) |
| ResponseKind.shortText → unsupported | `learning_activity.dart` resolver | «Nêu…» (37 lượt corpus) chưa có surface — fail closed, log P1 |

## 4. VERDICT

**Kernel evidence/mastery/session: CROSS-SUBJECT THẬT** — 2 môn mới không đổi
một dòng schema nào, chỉ THÊM surface + data model nguồn.
**Surface: PHẢI subject-specific** — Reader/SourceReader/Workspace là ba cách
làm-việc-nhận-thức khác nhau; Surface Resolver hiện tại (ResponseKind→Surface)
đúng cho Toán/TV, còn Sử vào bằng entry riêng vì «đọc tư liệu» không phải một
ResponseKind của bài tập — nó là một LOẠI HOẠT ĐỘNG khác. Không thêm
ResponseKind giả để gom cho đẹp.

## 5. KNOWN DATA ISSUES (đo được trong walk, chưa sửa)

- LS&ĐL curriculum-structure có SỐ BÀI TRÙNG (hai phân môn đánh số riêng,
  title coverage thấp) ⇒ SubjectHome hiện 2 tile «Bài 3» cùng mở 1 tư liệu.
  Cần title-miner pass riêng cho sách 2 phân môn (log vào WAL-144).
- OCR passage TV còn lỗi chính tả nhỏ («suôi», số trang lẫn vào text «8 Bỗng»)
  — verbatim từ nguồn, KHÔNG tự sửa; scoped-enrichment khi cần (direction
  UI-first 2026-09-02).
- Bug máy-trắng: index không nạp lại sau onboarding — đã fix + test hồi quy
  (`onboarding_index_test.dart`), bắt được nhờ walk trên thiết bị chưa có
  hồ sơ (S24 không lộ vì có sẵn hồ sơ).

Evidence: screenshots w1-w5 (S24), n1-n18+ (Nokia 6.1), JSONL on-device
(session tieng-viet + lich-su-va-dia-li), 5 mutations killed, 426 tests.
