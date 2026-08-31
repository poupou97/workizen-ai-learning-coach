# Adaptive Learning Engine — giả thuyết

**Status:** HYPOTHESIS · research only, không implement ở work order này.

Engine trả lời câu số 3: **"học sinh này nên học gì tiếp theo?"**
Đầu ra là **một** `NextBestLearningAction`, kèm **lý do đọc được**.

## Đầu vào

```
ConceptState (mastery + confidence)  ·  Prerequisite Graph  ·  Learning Path hiện tại
Evidence gần đây  ·  Độ khó  ·  Recency/quên  ·  Ràng buộc sư phạm (method của lớp)
```

## Đầu ra

`TEACH · PRACTICE · REVIEW · DIAGNOSE_PREREQUISITE · REMEDIATE · CHALLENGE · ADVANCE · REVISIT · REST`

Mỗi action **bắt buộc** kèm:
```
{ action, concept_id, reason, evidence_ids[], confidence, method_id }
```
`reason` không phải để log — nó là **thứ Parent Coach hiển thị** (§13). Action không giải
thích được thì không dùng được cho sản phẩm này.

## Thuật toán root-gap (§5) — bản làm được ngay

```
Lỗi quan sát → concept mục tiêu
   → nếu tiên quyết đều P cao  ⇒ TARGET failure  → REMEDIATE tại chỗ
   → nếu có tiên quyết P thấp/UNKNOWN ⇒ DIAGNOSE_PREREQUISITE
        → tìm nhị phân trên chuỗi tiên quyết (2–3 câu, xem RESEARCH §CAT)
        → xác định nút gãy → micro-intervention → verify → quay lại bài gốc
```

⚠️ **Ràng buộc từ POC:** với Toán 5 KNTT, chuỗi thật là
`Rút gọn/Tối giản (tr.11) → Quy đồng (ôn, tr.12) → Cộng trừ khác mẫu (tr.20)`.
Nút `Quy đồng` **chỉ được ôn, không được dạy** trong sách lớp 5 — nội dung vá nằm ở lớp 4.

⇒ Engine phải xử lý được ca **"chẩn đoán ra lỗ hổng mà không có nội dung để vá"**. Hành
vi đúng: nói thật với phụ huynh (*"phần này thuộc chương trình lớp 4"*) thay vì bịa một
bài giảng. Đây là ca `LOW_CONFIDENCE` của §13 áp cho nội dung, không chỉ cho phương pháp.

## Ràng buộc sư phạm — điểm khác biệt của Workizen

Engine **không** được chọn method chỉ vì hiệu quả toán học. `method_id` phải đến từ
`(concept, grade, book_series)` của learning path hiện tại.

Ca đã đo: Toán 5 KNTT dạy mẫu số chung = **tích hai mẫu số**; `BCNN` xuất hiện **0 lần**
trong 53 trang. Model tổng quát sẽ chọn BCNN. Engine phải **chặn** điều đó.

⇒ Đây là ràng buộc **kiểm được bằng test**, không phải câu gợi ý trong prompt. Mẫu chốt
mang từ Hub: *bộ đếm hoá đơn* — hỏi "có gọi method ngoài learning path không", không hỏi
"prompt có nhắc không".

## Daily Quest (§12)

Quest = một chuỗi action do engine sinh, không phải "10 bài".
`3′ ôn tiên quyết → 5′ concept mục tiêu → 3′ verify → 2′ challenge`
Mỗi ô là một action kèm `reason`.

## Không làm ở work order này

Không train model · không CAT đầy đủ · không recommendation engine production ·
không Student Profile production.
