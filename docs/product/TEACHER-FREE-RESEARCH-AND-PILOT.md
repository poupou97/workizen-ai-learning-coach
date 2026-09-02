# WAL-120 — TEACHER FREE: USE-CASE RESEARCH + PILOT DESIGN (2026-09-02)

Teacher = FREE (Founder direction §14). Teacher→Student→Parent acquisition là
HYPOTHESIS — tài liệu này thiết kế cách falsify nó, KHÔNG go-live (Founder Gate).

## 1. Use-case matrix × capability THẬT

| Use case | Chạy được từ data hiện có? | Nguồn |
|---|---|---|
| Curriculum browser | ✓ NGAY | crossgrade 7.626 lessons + lesson-index |
| Learning-objective lookup | ✓ NGAY | 569 objectives SGV (sourceStated, có trang) |
| Method/quy tắc lookup | ✓ NGAY | method-catalogue 29 quy tắc (trang in) |
| Lesson-prep brief (objective+method 1 bài) | ✓ POC CHẠY RỒI | tool/design/teacher_lookup_poc.py — Toán 5 B6: 3 mục tiêu + trang SGV/SGK |
| Practice generation | PARTIAL | qmap Toán (15 bài B6); môn khác chưa có đáp án |
| Quiz từ pack | PARTIAL | QuizSelect data TV (selectIdentify có đáp án) |
| Worksheet/print | CHƯA | cần layout/print pipeline — không hứa |
| Explanation variants | SHADOW-GATE | generative qua WAL-30/131, không learner-visible |
| Presentation / Mindmap | REUSE+ADAPTER | Hub capability (matrix WAL-110) |
| Scan/OCR bài tập | ✓ | EducationOcrAdapter (hypothesis-only) |
| QR resource sharing | POLICY CÓ SẴN | WAL-100 (SCAN ≠ AUTHORIZATION, purpose/nonce) |
| TeacherIntent → Agenda | ✓ KERNEL CÓ SẴN | WAL-106 (signal 0.6, expiry bắt buộc, không sửa mastery) |
| AI curriculum support | NỀN E16 | QĐ2422/CV5588 doc — chưa cam kết |

## 2. Pilot hypothesis design (THIẾT KẾ — chưa chạy)

- **Hypothesis:** GV dùng lookup/brief hằng tuần và CHIA SẺ resource → kéo
  học sinh/phụ huynh vào (acquisition kênh giáo viên).
- **Cỡ:** 5-10 giáo viên tiểu học (Toán/TV lớp 4-5 — nơi data dày nhất).
- **Thời gian:** 4 tuần.
- **Metrics (đo được, không tự khai):** activation (lần mở đầu tiên hoàn tất
  1 lookup); repeat-use (≥2 phiên/tuần từ tuần 2); use-case thật (log loại
  lookup — không nội dung); resource-share (số QR/worksheet chia sẻ);
  student-acquisition (số học sinh kích hoạt qua mã lớp — nếu có).
- **Consent:** đồng ý bằng văn bản; KHÔNG dữ liệu học sinh thật trong pilot;
  telemetry chỉ đếm sự kiện thô trên máy GV, xuất thủ công (không SDK analytics
  — pubspec-scan vẫn cấm).
- **Điều kiện DỪNG:** (1) GV yêu cầu; (2) phát hiện dữ liệu trẻ em lọt vào
  kênh pilot; (3) >50% GV không quay lại ở tuần 2 (hypothesis yếu — dừng sớm,
  báo thật); (4) Founder yêu cầu.
- **GO-LIVE với GV thật = FOUNDER GATE** — tài liệu này chỉ là thiết kế.

## 3. KHÔNG LÀM (giữ nguyên cấm)

Full LMS · attendance/gradebook/SIS · class management · bất kỳ màn nào cho
học sinh thật trong pilot · claim «validated» khi chưa chạy (WAL-49).
