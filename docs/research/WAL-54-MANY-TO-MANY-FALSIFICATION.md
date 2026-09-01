# WAL-54 — Falsification: Concept ↔ SkillCase ↔ Method có phải many-to-many? Conjunctive có phải luật toàn cục?

**Ngày:** 2026-09-01 · **Phương pháp:** phản ví dụ từ corpus đã OCR + số học chứng minh được
· thang bằng chứng (§J): [PRIMARY] = SGK/số học · [OSS] = mã đã đọc · [HYP] = giả thuyết

## 1. Method ↔ SkillCase — **FALSIFIED một-một** (theo nghĩa applicability)

**Phản ví dụ chứng minh được bằng số học [PRIMARY]:** phương pháp *"lấy tích hai mẫu"*
(sách dạy ở lớp 5 CHO ca không-chia-hết, tr.20) **đúng toán học với MỌI cặp mẫu khác nhau**,
kể cả ca chia-hết: `1/2 + 1/4` quy đồng theo tích → mẫu 8 → `4/8 + 2/8 = 6/8` — đúng
(dù mẫu 4 gọn hơn). Nghĩa là:

- **taught-for** (sách dạy phương pháp này cho ca nào): 1 → 1 ✅ giữ nguyên — đây là điều
  `TeachingMethod.skillCaseId` đang mã hoá, và với TUTOR (chọn cái để DẠY) nó ĐÚNG.
- **mathematically-applicable** (phương pháp chạy đúng trên ca nào): 1 → NHIỀU ⚠️ —
  chưa được mã hoá. Chưa gây lỗi vì WAL chưa có tầng CHẤM BÀI; ngày có trình chấm,
  học sinh dùng phương-pháp-tích trên bài ca-chia-hết KHÔNG được bị đánh sai
  (cùng họ với bài học `productExceedsLcm`: 4,6 quy đồng ra 12 hay 24 đều đúng).

**Kết luận: MODIFY-KHI-CẦN, không đổi schema hôm nay.** Ghi semantic rõ: `skillCaseId`
nghĩa là *taught-for-case*; tầng chấm bài sau này cần bảng applicability riêng (suy được
từ chính domain analysis — `analyzeFractionPair` đã giữ đủ cấu trúc). Test chốt semantic
đã thêm (`many_to_many_semantics_test.dart`).

## 2. Concept ↔ SkillCase — **INSUFFICIENT EVIDENCE để tuyên bố M:N**

Quan sát [PRIMARY]: điều kiện *"hai mẫu số không chia hết cho nhau"* xuất hiện ở ca của
`quy-dong` VÀ mô tả tình huống của `cong-phan-so-khac-mau` — Bài 6 lớp 5 dạy quy đồng
ca mới **BÊN TRONG** bài cộng-trừ phân số (một bài giới thiệu ca của concept A trong khi
danh nghĩa thuộc concept B). Đây là bằng chứng cho **phụ thuộc tuần tự** (quy đồng là
bước con của cộng khác mẫu) chứ CHƯA đủ để nói hai ca là MỘT (kỹ năng khác nhau: biến đổi
mẫu ≠ cộng tử). Giữ hai ca riêng cùng điều-kiện; ghi giả thuyết "case-condition dùng chung"
[HYP] chờ thêm khái niệm.

## 3. Method ↔ Concept — đã M:N sẵn

`TeachingMethod.appliesToConcepts` là `Set<String>` từ đầu — không có gì để falsify.

## 4. Conjunctive AND — **FALSIFIED như luật TOÀN CỤC** (giữ như giả định TỪNG-MAP)

Phản ví dụ từ corpus đã OCR:

| Loại (danh sách Founder) | Ví dụ [PRIMARY] | Hệ quả |
|---|---|---|
| **Skill có mặt nhưng KHÔNG được đánh giá** | Bài 3 tr.39 (chọn cân sai): cần đọc-hiểu-đề + so sánh số thập phân; mục tiêu đánh giá của bài là SO SÁNH | credit conjunctive cho đọc-hiểu-đề mỗi lần đúng = lạm phát bằng chứng cho concept nền — CÙNG HỌ với F3 (bằng chứng yếu chấm như mạnh). OPEN: cần vai trò `required/supporting` khi có tầng authoring; chưa thêm field khi chưa có người ghi nó |
| **Chiến lược thay thế** | Bài 2 tr.39 (sắp xếp 4 số thập phân): làm được bằng so-từng-cặp HOẶC quét-theo-hàng | AND-gate trên tập ca cố định không mô tả được "một trong nhiều đường" — hiện `attributionUnresolved` đã chặn quy lỗi bừa khi sai; quy CÔNG khi đúng vẫn conjunctive = giả định, ghi rõ trong doc `ExerciseSkillMap` |
| **Phụ thuộc tuần tự** | quy đồng là BƯỚC CON của cộng khác mẫu (Bài 6) | thứ tự không được mã hoá; chưa cần cho chẩn đoán hiện tại; [HYP] cần khi làm process-level evidence |

**Quyết định:** conjunctive giữ nguyên như **giả định khai báo theo từng map** (đúng cho
bài toán-nhiều-bước dạng tính), KHÔNG phải luật toàn cục; `attributionUnresolved` là van
an toàn khi sai. Q-matrix STRUCTURE (map nói bài chạm gì) tách khỏi INFERENCE POLICY
(đúng/sai thì credit thế nào) — policy nằm ở `attributeEvidence`/`attributeFailure`, thay
được không cần đổi cấu trúc, đúng tinh thần ADR-004.

## 5. Verdict tổng
| Quan hệ | Kết quả |
|---|---|
| Method↔Case | **M:N về applicability, 1:1 về taught-for** — semantic đã chốt bằng test; schema đổi khi có tầng chấm |
| Concept↔Case | INSUFFICIENT EVIDENCE cho M:N — giữ, theo dõi |
| Method↔Concept | đã M:N |
| Conjunctive | FALSIFIED toàn cục — giữ per-map + van attributionUnresolved |
