# PROPOSED APP FLOW — «Học cùng SAM»

## 0. App start (shared device — §26)

```
APP START
  └─ 1 learner duy nhất? → thẳng HOME (nhớ last-active)
  └─ >1 profile        → AI ĐANG HỌC?  [avatar lớn, age-aware]
        ├─ Learner X → HOME (context X: profile+grade+state+agenda)
        └─ Chế độ Phụ huynh → [PIN/biometric] → PARENT HOME
```

## A. First run

```
01 Welcome (Student|Parent)
  Parent nhánh: tạo LearnerProfile hộ con (young — WAL-100)
02 Learner Profile   [TỐI GIẢN: tên + lớp; birthYear/chương-trình = sau, optional]
03 Subject Setup     [grid SINH TỪ REGISTRY theo lớp; default «chọn theo lớp N»]
04 Timetable         [skippable; chụp→OCR→confirm hoặc tay]
→ 05 HOME
```

## B. Home (nền = home1)

```
HOME = Mission Center
  header: [Tên · Lớp ▾] → Đổi người học
  ô hỏi SAM + 5 INTENT CHIPS:
    Học trước · Ôn luyện · Làm bài tập · Học phương pháp · Kiểm tra hiểu bài
  Việc SAM đề xuất (resolveAgenda + reason)   ← WAL-102 ĐÃ BUILD
  Sắp tới (TKB context) · Tiếp tục học · Các môn
```

## C. Core tutor vertical (first slice)

```
HOME/SUBJECT ─┬─ 08 Camera → 09 Confirm(ConfirmedProblem) ─┐
              └─ chọn bài từ Curriculum Browser ───────────┤
                                                           ▼
10 Tutor Start   [provenance card: WHAT/WHERE/METHOD/SOURCE — explainTeaching]
11 Diagnostic    [thử trước / probe WAL-70; KHÔNG điểm số]
12 Workspace     [viết tay/gõ; TutorSession state machine ĐÃ CÓ]
13 Hint          [engine-quyết nấc ±1; nội dung qua output_guard]
14 Your Turn     [independent evidence]
15 Success       [feedbackFor 4 chiều + next action]
16 Why Method / 17 Source   [render TeachingProvenance — sẵn]
18 Review        [reviewStateOf + weak case]
```

Vòng evidence: mọi bước 11-15 phát LearningEvent đúng loại (kernel sẵn) →
recordSession → Agenda ngày mai đổi theo.

## D. Assessment (tách khỏi Quiz — F9)

```
20 Quiz: hint ĐƯỢC, ghi assistance
21a Assessment Start: [xác nhận profile «Đây là bài của Minh Anh?» §26.8]
21b Assessment Mode: hint TẮT (AssistancePolicy.assessment) 
22 Result: independent/assisted tách · claim-gated · remediation
```

## E. Parent flow

```
PARENT MODE (PIN)
  32 Parent Home: TỐI NAY GIÚP GÌ (1 action) + tình hình + lịch
  34 Family Manager: thêm/sửa con · chuyển Learner Mode · consent
  33 Learner Detail: 3-trục claim-gated · KHÔNG ranking
  37 Notifications policy · 38 Family Settings
```

## F. Điều hướng chính (bottom nav — learner)

`Hôm nay (Home) · Môn học · [SAM] · Tiến bộ · Thêm`  — giữ như concept 05;
Voice/Library/Quiz vào ngữ cảnh môn thay vì tab cấp 1 (giảm nav complexity Grade 1-2).
