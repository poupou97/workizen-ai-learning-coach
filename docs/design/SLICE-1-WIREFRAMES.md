# SLICE 1 — Wireframes: Mission → Camera → Xác nhận → Probe → Tutor → Evidence → Next

**Ngày:** 2026-09-01 (WAL-48) · **MATURITY: DESIGNED** — mọi màn CHỈ dùng dữ liệu domain ĐANG CÓ
· Vòng lặp §M: SAM hỏi → trẻ thử → SAM quan sát → probe nếu cần → can thiệp TỐI THIỂU ĐỦ →
YOUR_TURN → evidence → fade/next — KHÔNG phải "student asks → chatbot answers".
· Lát domain: `quy-dong` (đầy đủ case/method/summary/review). Copy = tiếng Việt thật, sửa khi user-test.

## Flow tổng
```
[M1 Hôm nay] ─chọn nhiệm vụ─▶ [C1 Camera] ─chụp─▶ [C2 "Tớ đọc được thế này"] ─CONFIRM─▶
   ▲                                                   │CORRECT (sửa tại chỗ) │RETAKE→C1
   │                                              [T0 Probe? nếu bất định]
   │                                                   ▼
   └──────────[E1 Evidence + Next] ◀─── [T1 Tutor: trẻ thử → thang hint → YOUR_TURN]
```

## M1 — HÔM NAY (Mission Center) · pattern NEXT_ACTION + REVIEW_DUE
```
┌────────────────────────────────────┐
│ [SAM HELLO nhỏ]  Chào Minh!        │  mascot: HELLO (thu về góc sau 2s — STEP_BACK)
│                                    │
│ ┌────────────────────────────────┐ │  ← THẺ DUY NHẤT, to nhất
│ │ ▶ Hôm nay mình luyện dạng      │ │  nguồn: AdaptiveDecision.action + reason
│ │   "hai mẫu số không chia hết"  │ │  copy lý do = decision.reason (trẻ-đọc-được)
│ │   Vì con đã vững dạng chia hết │ │
│ │   — giờ thử luật mới nhé  [Bắt │ │
│ │   đầu]                         │ │
│ └────────────────────────────────┘ │
│ Ôn lại (2)  ⟳                      │  nguồn: ReviewUrgency.reviewDue/overdue
│  · So sánh số thập phân  ⟳ tới hạn │  KHÔNG đỏ, không đếm ngược hối thúc
│ Thử dạng mới (1)  ✦                │  nguồn: ConceptSummary.unobservedCases
│  · "Hai mẫu bằng nhau" — chưa thử  │  (thử-thách-phủ: tăng coverage)
│                                    │
│ [📷 Chụp bài tập]      [Bản đồ ▸]  │
└────────────────────────────────────┘
CẤM: %, điểm số, streak-đếm-ngày. Trống review ⇒ ẩn mục, không placeholder buồn.
```

## C1 — CAMERA + pre-capture (WAL-65) · mascot CAMERA_SCAN*
```
┌────────────────────────────────────┐
│  ┌──────── khung ngắm ─────────┐   │  guidance state machine (một dòng, đổi theo ảnh):
│  │                             │   │  FIT_ONE_PROBLEM "Đưa MỘT bài vào khung nhé"
│  │      [vùng bài toán]        │   │  MORE_LIGHT "Tối quá — bật thêm đèn?"
│  │                             │   │  HOLD_STEADY "Giữ yên máy chút xíu…"
│  └─────────────────────────────┘   │  TOO_BLURRY "Chưa nét — lại gần hơn"
│  [SAM CURIOUS*] "Đưa MỘT bài vào   │  *CAMERA_SCAN sprite chưa có (WAL-47) —
│   khung nhé"            [⭕ Chụp]  │   tạm dùng CURIOUS, ghi chú asset
└────────────────────────────────────┘
```

## C2 — "TỚ ĐỌC ĐƯỢC THẾ NÀY" · RANH GIỚI AN TOÀN (WAL-64 — bắt buộc, không đường tắt)
```
┌────────────────────────────────────┐
│ [SAM THINK→neutral]                │  nguồn: PerceptionHypothesis.expression
│  Tớ đọc được thế này:              │
│  ┌──────────────┐                  │
│  │  3/4 + 2/5   │ ✏️ sửa          │  chạm ✏️ → sửa inline từng số
│  └──────────────┘                  │  (mọi sửa → ConfirmationKind.corrected,
│  Đúng đề bài của con chưa?         │   hypothesis GIỮ NGUYÊN — đo #5 WAL-63)
│  [✓ Đúng rồi]  [✏️ Sửa]  [📷 Chụp lại] │
└────────────────────────────────────┘
Nếu không ghép được biểu thức (caseUnknown): [SAM ADMIT_UNCERTAINTY]
"Tớ chưa chắc mình đọc đúng đề — con chụp gần hơn giúp tớ nhé?" [Chụp lại] [Gõ đề ✎→man:]
KHÔNG BAO GIỜ đoán. Evidence chỉ sinh sau CONFIRM (exerciseId = cp:… — type-enforced).
```

## T0 — DIAGNOSTIC PROBE (chỉ khi bất định) · pattern DIAGNOSTIC_PROBE
```
Điều kiện vào: decide() = insufficientEvidence HOẶC attributeFailure = attributionUnresolved
┌────────────────────────────────────┐
│ [SAM PROBE/THINK_WITH_YOU]         │  attributionUnresolved.implicatedCases →
│  Để hiểu con đang nghĩ gì, thử     │  MỘT câu hỏi ngắn cô lập MỘT thành phần
│  câu nhanh này nhé (không tính     │  (isolateSkills — log ghi như bài thường,
│  điểm đâu):                        │   độc lập → independentAttempt)
│  "2/4 và 1/4 — mẫu số nào chung?"  │
└────────────────────────────────────┘
Copy KHÔNG mang giọng kiểm tra; tối đa 1–2 probe rồi phải sang can thiệp.
```

## T1 — TUTOR · trẻ-thử-trước + thang WAL-68 + YOUR_TURN
```
┌────────────────────────────────────┐
│  Bài: 3/4 + 2/5                    │
│  [vùng làm bài của con — to nhất]  │  ⭐ lượt của TRẺ là mặc định
│  [SAM YOUR_TURN thu nhỏ ở góc]     │  "Con thử bước đầu tiên trước nhé"
│  ────────────────────────────────  │
│  [💡 Gợi ý]                        │  thang ±1 nấc (WAL-68), mức khởi đầu theo
└────────────────────────────────────┘  CaseMastery; mỗi nấc = 1 event (F3)
Nấc 1 PROMPT: "Hai mẫu số 4 và 5 có chia hết cho nhau không?"      (hintShown)
Nấc 2 SMALL_HINT (scaffold-câu-hỏi): "Mẫu chung tìm từ 4 và 5 thế nào nhỉ?" (guidedAttempt)
Nấc 3 DEMONSTRATE_STEP: SAM làm mẫu BƯỚC quy đồng, con làm tiếp    (workedStep)
Nấc 4 REVEAL: chỉ sau ≥1 lần tự thử + đã qua nấc 3                 (fullSolution — no credit)
caseTransitionGap ⇒ CONTRAST_CASES: "Con đã giỏi dạng chia hết. Dạng này KHÁC ở chỗ…"
Sai lần đầu ⇒ [SAM TRY_AGAIN] "Không sao! Dạng này MỚI với con mà" — không đỏ, không trừ điểm.
```

## E1 — EVIDENCE + NEXT · tách 4 chiều (H2/WAL-69)
```
┌────────────────────────────────────┐
│ [SAM CELEBRATE nếu độc lập /       │  AFFECT: khen theo HÀNH VI, không theo IQ:
│  khích lệ ấm nếu sau gợi ý]        │  độc lập: "Lần này con KHÔNG cần gợi ý!"
│  Con làm đúng!                     │  sau hint: "Con làm được rồi — lần sau
│                                    │   mình thử không cần gợi ý nhé"  ← UI vẫn
│  Dạng "không chia hết": con vừa    │   khen; model KHÔNG ghi công (OnOpen)
│  có thêm 1 lần tự làm ✓            │  nguồn: EvidenceKind vừa ghi
│  [Bài nữa dạng này] [Về Hôm nay]  │  next: AdaptiveDecision mới (fade: nếu đủ
└────────────────────────────────────┘  vững → đề xuất dạng khác/ôn — SAM lùi)
CẤM: "Thiên tài!", %, so sánh với bạn khác.
```

## Đối chiếu 7 nguyên tắc (UX-PRINCIPLES-AND-IA)
1 hành-động-kế-tiếp ✓(M1) · 2 không-số-giả-chính-xác ✓(mọi màn) · 3 thất-bại-là-dạng-mới
✓(T1) · 4 hint-sinh-bằng-chứng ✓(T1 thang) · 5 AI-trong-ngữ-cảnh ✓(T0/T1) ·
6 fail-closed-tử-tế ✓(C2) · 7 vùng-cấm-mascot ✓(không mascot ở màn dữ liệu/consent).

## Dữ liệu domain tiêu thụ (chốt AC: không màn nào cần dữ liệu CHƯA tồn tại)
AdaptiveDecision(.action/.reason) · ReviewState/ReviewUrgency · ConceptSummary(.unobservedCases
/.claim/.observedCaseFacts) · PerceptionHypothesis/ConfirmedProblem · analyzeFractionPair ·
decide()/attributeFailure(.implicatedCases) · SupportLevel/EvidenceKind · contrastCaseFor.
Thiếu DUY NHẤT (đã có ticket): sprite CAMERA_SCAN/REVIEW_DUE (WAL-47) · token màu (WAL-46) ·
TeachingAct POC cho thang chính thức (E13 — thang tạm dùng SupportLevel 4 nấc đã ship).
