# ADR-009 — Surface học tập COMPOSABLE: một SAM, nhiều bề mặt tương tác

**Ngày:** 2026-09-01 · **Trạng thái:** ACCEPTED (L2 — viết KHI BUILD surface đầu tiên,
không viết trước; Founder Task Order §24 «không tạo ADR chỉ vì có nghiên cứu»)
**Bằng chứng:** WAL-97 · corpus 2.202 unit · `learning_activity.dart` + `quiz_select_screen.dart`
· 7 test + 3 đột biến đỏ

## Bối cảnh

Founder bác cả hai cực: «một màn chat + bộ chọn môn» (quá nghèo) và «mỗi môn một app»
(quá tốn). Câu hỏi: kiến trúc ở giữa là gì?

## Quyết định

**Chuỗi bốn tầng, mỗi tầng đổi được mà không đụng tầng trên:**

```
Nguồn/Chương trình (SGK, QĐ 2422)     ← sự thật, KHÔNG chứa quyết định UI
        ↓
LearningActivity (ngữ nghĩa hoạt động) ← bài tập ĐÒI HỎI kiểu trả lời gì
        ↓
resolveSurface()                       ← NƠI DUY NHẤT ánh xạ activity → surface
        ↓
Interaction Surface (Quiz/Problem/Reader/Compose…) ← widget
```

1. **SAM là MỘT persona xuyên mọi surface.** Luật dạy học không nhân bản theo màn: cùng
   `feedbackFor` (WAL-69), cùng ngữ nghĩa hỗ trợ, cùng luật cấm %/điểm/khen-tư-chất.
2. **Surface theo KIỂU TƯƠNG TÁC, không theo môn.** Bằng chứng corpus: động từ mở đầu
   1.706 bài tập cho thấy «Tìm/Chọn» (195 lượt) xuất hiện ở CẢ Toán lẫn Tiếng Việt ⇒ một
   surface Quiz/Select phục vụ cả hai. Test `⭐ F1 bác` chạy cùng màn cho hai môn.
3. **`resolveSurface` là điểm ánh xạ DUY NHẤT** (F8): tri thức không biết gì về widget;
   đổi giao diện sửa một hàm.
4. **Không có surface ⇒ nói KHÔNG HỖ TRỢ**, không ép bài vào màn gần đúng
   (`shortText → unsupported`; đột biến ép-vào-quiz → đỏ).
5. **Taxonomy response = 5 loại ĐO ĐƯỢC** (selectIdentify · numericStep · shortText ·
   compose · readRespond). MCQ-4/MAP/ORAL: **0 xuất hiện trong corpus ⇒ không tạo**.

## Bất biến surface phải giữ (test, không phải lời dặn)

| Luật | Chốt |
|---|---|
| Đúng-sau-gợi-ý ≠ tự làm được | đột biến ghi-công-sai → đỏ |
| Bài chưa biết đáp án ⇒ KHÔNG chấm (UNKNOWN ≠ SAI) | đột biến UNKNOWN→SAI → đỏ |
| Không %, không điểm, không phán xét khi sai | test quét mọi trạng thái màn |
| Provenance hiển thị đúng LOẠI hỗ trợ nguồn | `sourceLineForChild` (ADR-008/Delta) |
| Mọi sự kiện mang lineage (support/policy/prior) | ghi tại `_emit` |

## Hệ quả

- Surface mới = một widget + một nhánh resolver; không đụng kernel, không đụng tri thức.
- Reader/Compose (WAL-98) theo đúng khuôn này; Map/Timeline/Lab **chưa tạo** cho tới khi
  corpus chạm Sử/Địa/Lý-Hoá — gate bằng bằng chứng, không bằng dự đoán.
- Rủi ro ghi nhận: `resolveSurface` có thể phình khi nhiều môn — khi đó tách theo
  subject-family adapter (cùng khuôn với extractor adapter đã falsify ở GĐ2).

## Cập nhật — WAL-98 XONG (2026-09-01)

Reader (`readRespond`) + Compose-lite (`compose`) đã dựng **đúng khuôn**: mỗi surface =
một widget + nhánh resolver đã sẵn, KHÔNG đụng kernel. `LearningActivity` thêm hai trường
CỘNG THÊM (`passage`, `composeChecklist`); ⭐ cố ý **không** có trường giữ «bài văn mẫu».

Hai bất biến fail-closed MỚI, giữ bằng test + mutation (đỏ khi gỡ):
- **READ gate** (Reader): câu hỏi bị khoá tới khi trẻ tự xác nhận đã đọc đoạn văn;
  «đọc xong» KHÔNG phát `LearningEvent` (đọc ≠ mastery). Đoạn văn/câu hỏi thiếu ⇒ nói
  KHÔNG HỖ TRỢ.
- **REVEAL gate** (Compose = «SAM không viết hộ»): nút góp ý + checklist chỉ mở SAU khi
  trẻ nộp nháp; văn KHÔNG chấm đúng/sai (`correct == null`); bằng chứng theo QUÁ TRÌNH —
  nháp = `independentAttempt`, sửa-sau-góp-ý = `guidedAttempt` (có hỗ trợ), tự-soát-rồi-sửa
  = `selfCorrection`.

`shortText` vẫn `unsupported` (chưa đủ căn cứ surface). Map/Timeline/Lab vẫn CHƯA tạo.
Bằng chứng: `reader_screen.dart` + `compose_lite_screen.dart` + 15 test; 233 test toàn suite xanh.
