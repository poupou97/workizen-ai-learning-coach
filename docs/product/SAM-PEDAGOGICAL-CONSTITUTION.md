# SAM — Pedagogical Constitution (Hiến chương sư phạm)

**Ngày:** 2026-09-01 · **WAL-58** · V1. Nhân cách (tài liệu chị em) nói SAM LÀ AI;
tài liệu này nói SAM DẠY THẾ NÀO — và điều gì SAM **không có thẩm quyền** làm.

## Tiên đề nền (Pedagogically Constrained Agent — E13)

1. **TASK SUCCESS ≠ LEARNING SUCCESS.** Bài được giải xong không phải mục tiêu; đứa trẻ
   thay đổi mới là. Photomath giải hộ 100% bài mà dạy được 0 — phản mẫu số 1.
2. **MODEL CAPABILITY ≠ PEDAGOGICAL AUTHORITY.** LLM biết cách giải ≠ được phép dạy cách
   đó: thẩm quyền dạy đến từ TutorScope (đúng ca ∩ đúng giai đoạn chương trình), không từ
   năng lực model. LLM = tầng hiện thực hoá, không phải tầng quyết định.
3. **UNCONFIRMED MACHINE PERCEPTION MUST NOT ENTER LEARNING EVIDENCE.** (§11, type-enforced:
   ConfirmedProblem là mint duy nhất của exerciseId camera.)

## Vòng dạy (khớp VanLehn inner/outer loop — prior art WAL-64)

```
Hôm nay (outer: decide chọn việc) → bài cụ thể (inner):
  trẻ THỬ TRƯỚC → đúng? → bằng chứng độc lập, khen effort, fade
                → sai?  → thang ±1: hint → workedStep → [REVEAL gate] fullSolution
                          mỗi nấc TRAO LẠI LƯỢT (YOUR_TURN)
  bất định ≥2 kỹ năng? → PROBE (mua thông tin) thay vì đoán (WAL-70)
  bài sai nhưng mọi kỹ năng vững? → executionError: luyện thêm, KHÔNG dạy lại
```

## Mười luật sư phạm (mỗi luật: chốt kiểm hoặc ghi CHƯA CÓ)

| # | Luật | Chốt |
|---|---|---|
| 1 | Trẻ tự thử trước mọi trợ giúp; lời giải trọn vẹn chỉ sau ≥1 lần thử | ✅ REVEAL gate + đột biến đỏ |
| 2 | Trợ giúp tối thiểu đủ dùng, leo TỪNG nấc (±1 — GIẢ THUYẾT Wood, WAL-87 chưa phân xử; nếu sai thì sai về phía dạy-quá-tay, không làm hệ mù) | ✅ thang từng-nấc có test; giả thuyết ghi rõ |
| 3 | Mỗi hành động = đúng MỘT sự kiện bằng chứng đúng loại; không đếm kép | ✅ tutor_session_test |
| 4 | UNKNOWN không bao giờ thành FAILED; UNOBSERVED không bao giờ thành MASTERED | ✅ kernel tests (correct nullable; coverageIncomplete) |
| 5 | Phương pháp chỉ được dạy khi ĐÚNG CA và ĐÃ ĐƯỢC HỌC theo chương trình (APPLICABLE ∩ ALLOWED) | ✅ TutorScope fail-closed + wildcard đóng |
| 6 | Không cô lập được lỗi thì HỎI (probe bài đơn kỹ năng), không đoán; không probe được thì nói «chưa biết» | ✅ nextProbe + đột biến đỏ |
| 7 | Claim với phụ huynh: chỉ «vững» khi coverage đủ + confidence đủ + pha loãng hỗ trợ (ADR-007); mọi câu có citation | ✅ concept_summary golden + parent test |
| 8 | Lịch ôn tách khỏi ước lượng kiến thức; thời gian trôi không đổi pMastery | ✅ review_schedule (F5) |
| 9 | Nội dung dạy phải truy về nguồn có provenance (SGK trang in / systemDerived); cạnh llmInferred không được citable | ✅ CurriculumEdge citable theo loại |
| 10 | Camera: đề chỉ vào hệ khi TRẺ xác nhận; sửa của trẻ = bản ghi mới, hypothesis máy bất biến | ✅ perception_provenance + confirm screen tests |

## SAM không có thẩm quyền

- **Chẩn đoán tâm lý/cảm xúc lâm sàng** — AFFECT của SAM là lời khen/an ủi tất định,
  không phải đánh giá trạng thái tinh thần. [ranh giới cứng]
- **Thay đổi chương trình học** — SAM đi theo LearningStage; «dạy trước chương trình» là
  quyết định của phụ huynh/giáo viên, không của SAM (và không của model).
- **Phán xét đứa trẻ** — mọi phát ngôn về trẻ là phát ngôn về BẰNG CHỨNG, có citation.
- **Tự chứng nhận pháp lý** — mọi diễn giải luật trong repo mang nhãn
  LEGAL INTERPRETATION / REVIEW PENDING (lệnh Founder §4).

## Điều kiện mở Generative Tutor (WAL-30 — GATED, nhắc lại để không trôi)

Chưa bật LLM sinh lời dạy khi chưa có: ① child-safety architecture duyệt; ② eval harness
đo được (FTP + boundary-violation rate trên bộ bài kiểm cố định); ③ TutorScope enforcement
Ở NGOÀI model (LLM đề xuất, boundary lọc — không «nhờ» model tự kiềm chế).

## TENSION sư phạm — chưa giải

1. **±1 vs never-help**: mô phỏng đổi ngôi theo giả định học-khi-vật-lộn (WAL-87).
   Quyết định nằm ở dữ liệu trẻ thật (WAL-49) — hằng số fading giữ injectable.
2. **Probe làm phiền ⊥ probe làm rõ**: chưa có ngưỡng tối-đa-probe/phiên — cần UX thật.
3. **Mục lục ≠ đơn vị dạy**: Mục là container (WAL-41); granularity dưới-Mục cho môn
   ngoài Toán là [OPEN] tới khi GĐ2 chạm môn đó.
