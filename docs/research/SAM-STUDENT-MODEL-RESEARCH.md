# SAM-STUDENT-MODEL-RESEARCH — WS-A + falsify «một xác suất mastery là đủ»

**Ngày:** 2026-09-02 · WAL-99 · Addendum Founder: KHÔNG mặc định scalar đủ; phải falsify.

## 1. FALSIFY «single mastery probability is sufficient» — BỐN PHẢN VÍ DỤ, ba cái ĐÃ ĐO

| # | Phản ví dụ | Bằng chứng | Scalar chết vì |
|---|---|---|---|
| 1 | 2 ca luyện kỹ + 1 ca CHƯA HỎI → min/mean trên observed đều nói «vững» | ADR-003 F1 — test thật, đột biến đỏ | không mang COVERAGE: «phủ hết ca» và «còn ca chưa hỏi» cho cùng một số |
| 2 | Cùng pMastery cao, một stream thuần độc lập vs một stream nặng-hỗ-trợ | **ĐO**: WAL-87 sim + ADR-007 — FALSE TRUSTED 10–19% claims (gate V1) → 0–2% sau pha-loãng | không phân biệt independent vs assisted — đúng bất biến §25.3 |
| 3 | Consistency đo toàn-concept nghiền `caseTransitionGap` | lịch sử golden ③ đỏ khi thử — phải chuyển per-case min | một số che MÂU THUẪN GIỮA CA — tín hiệu chẩn đoán quý nhất |
| 4 | pMastery 0.9 hôm nay = 0.9 sau 6 tháng không chạm | F5/ADR-003 ghi nhận; PSKT xác nhận interval là tín hiệu | không mang TUỔI bằng chứng — recency là trục riêng |

**Steelman cho scalar (phải công bằng):** đơn giản; DKT đạt AUC cao. Nhưng: AUC dự-đoán-câu-sau
≠ trung thực-với-phụ-huynh; DKT không giải thích được (vi phạm provenance doctrine + CV5588
«kiểm chứng»), cần data lớn (EdNet CC-NC cấm sản phẩm), và literature riêng của nó thừa nhận
độ lệch. **Kết luận falsification: scalar CHỈ đủ cho ranking nội bộ** — đúng vai
`estimatedMastery` hiện tại; CLAIM phải đi qua đa trục. Bất biến §25.1/§25.2 **ĐỨNG VỮNG có
bằng chứng**, không phải mặc định.

## 2. Mastery đặt ở TẦNG nào? — test ba phương án

| Phương án | Thử falsify | Kết quả |
|---|---|---|
| Concept-level only | WAL-54: Method↔Case M:N; decimal-comparison 4 ca khác hành vi; TV «liên kết câu» recognize≠apply (test no-collapse) | **BÁC** — một số/concept nuốt khác biệt ca & demand |
| SkillCase-level only | Phụ huynh cần câu trả lời mức khái niệm; curriculum coverage cần biết ca-chưa-quan-sát (danh sách knownCaseIds nằm NGOÀI evidence) | **BÁC ở vai trò duy-nhất** — thiếu view tổng hợp claim-gated |
| ⭐ **Multi-view**: per-SkillCase estimate (BKT) + ConceptSummary 3 trục + claim 6 mức | mọi phản ví dụ trên đều được biểu diễn; chi phí = phức tạp hơn | **SỐNG SÓT** — và ĐÃ LÀ kiến trúc hiện tại (audit CURRENT-TRUTH) |

Trả lời câu hỏi order: **không lưu «điểm môn Toán»** — lưu ở knowledge-component (SkillCase),
tổng hợp lên concept qua 3 trục, môn chỉ là projection nhóm-concept (chưa cần model riêng).

## 3. Node schema đề xuất (conceptual — KHÔNG implement) + phản biện độ phức tạp

Đối chiếu cây order với hiện trạng: mastery/confidence/evidence/attempts/last-practiced/
source-ref ✅ đã có · **thiếu 2**: `commonMistakes` và `forgettingRisk`.

- `commonMistakes` → cần **Misconception model** (MISSING thật). Đề xuất TỐI THIỂU: một
  CATALOG misconception per concept (id, pattern nhận diện tất định, ví dụ corpus, nguồn),
  và evidence chỉ GHI NHẬN match — KHÔNG suy misconception bằng LLM tự do (rủi ro misdiagnosis
  → critical review). Nguồn pattern: lỗi phổ biến từ SGV + bài sai thật khi có WAL-49. KHÔNG
  build trước khi có ≥1 nguồn pattern thật — nếu không là catalog bịa.
- `forgettingRisk` → thuộc REVIEW lane (FSRS-style retrievability), **không đụng pMastery**
  (giữ F5 + §25.10/16). OpenTutor cho mẫu property-tests.
- KT nâng cao (DKT/IRT): **DEFER** — IRT cần calibrate item (chưa có dữ liệu), DKT như trên.
- PSKT gợi ý giữ lại: tách «đang biết» (ks) vs «vừa học» (ka) — WAL đã có dạng thô
  (posterior vs learn-term); ghi làm giả thuyết policy, không đổi model.

**Phản biện «quá phức tạp» (order §14):** phức tạp nằm ĐÚNG chỗ đắt (claim với phụ huynh);
mọi trục đều trả lời một câu hỏi sản phẩm cụ thể và có test giữ. Thứ KHÔNG nên thêm bây giờ:
learning-velocity, transfer-score, affect-state — chưa có consumer lẫn nguồn dữ liệu (YAGNI).
