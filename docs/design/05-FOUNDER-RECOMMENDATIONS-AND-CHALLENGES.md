# 05 — FOUNDER RECOMMENDATIONS & CHALLENGES (WAL-111 · phản biện thẳng)

## A-C. Assumptions

**ĐÚNG (corpus xác nhận):** khung 4-hoạt-động GDPT xuyên cấp (shared extractor ăn 525
docs) · 5 Learning Intent ↔ SGK activity thật · voice-heavy 1-2 (viết/đọc/nói/nghe top
verbs) · KHTN 6-9 integrated · family G Creative/Performance · «SAME CONCEPT ≠ SAME
EVIDENCE» (TV lệnh tách rõ) · Toán worked-example-driven (EXAMPLE 1.305).
**SAI (falsified):** «38 màn = 38 routes» (→ ~24 routes/16 surfaces; Workspace = 1+4
states) · «mọi môn học giống Toán» · «AI Learning = ChatGPT ladder» · «Source = link
web» · «drawing là phụ» (vẽ = verb #1 band 10-12!) · «Voice để sau» (T.Anh môn lớn nhất).
**CHƯA ĐỦ EVIDENCE:** simulation learning-value (F16) · ads-funding đủ COGS (F32) ·
teacher acquisition loop (F38) · child-ads legal VN [cần luật sư — Founder Gate].

## D-K. Sản phẩm

Overfit: Toán-4/5 34/38 màn; band yếu nhất concept = **10-12** (52.7k units — NHIỀU
NHẤT corpus mà ít màn phục vụ nhất: thiếu chuyên-đề, formula-first, drawing). Môn cần
specialized surface: KHTN(experiment) · Sử(source 3-nhãn) · Địa(map) · NN(4-kỹ-năng) ·
ÂN/MT/HĐTN(G). Reuse surface: Tin/CN/GDCD/Khoa-học qua shell+Quiz/Reader. Merge: 12-15
thành Workspace-states; 20/21 thành 1 surface 2 mode. Replace: 11/17/18/29/31/36.
Thiếu: Language 4-kỹ-năng · chuyên-đề browser · reflection · artifact-capture · teacher-mode.

## L-P. Nền tảng

Data gaps: title 29% · NO_TOC 125 · semantic sâu ngoài Toán/TV · lexicon EN. Child-safety
gap: Firebase analytics pass (F42), ads-SDK collection [R]. Hub: reuse 6 as-is/13 adapter/
4 extract/3 POC/5 reject (matrix đã có — corpus mới KHÔNG đổi verdict nào, chỉ NÂNG
voice_kit ưu tiên). Shared-device: giữ nguyên kiến trúc §26 (đã spec). Local-first: pack
34MB-ước-tính cho semantic K-12 đầy đủ [I từ 105MB synthetic benchmark] — khả thi.

## Q-AA. Business (khuyến nghị + phản biện)

- **Q/R:** Student Free = TOÀN BỘ learning loop (không tính năng học nào paywall).
  Bền vững NẾU: deterministic-first (kernel hiện tại 0-LLM cho structured tutor!) +
  local pack + LLM chỉ shadow/realize có guard → COGS/learner thấp. Số shadow: $0.012/
  lượt haiku ⇒ 20 lượt-LLM/ngày ≈ $0.24/learner/ngày NẾU full-LLM — vì thế routing
  local-first là điều kiện sống của Student Free [S: số đo thật].
- **S:** Teacher Free = curriculum browser + practice-builder từ pack (data sẵn!) —
  chi phí biên ~0 vì local. Acquisition loop = hypothesis cần pilot (F38).
- **T/U:** Parent Basic free (consent/privacy/tạo hồ sơ — bắt buộc đạo đức lẫn legal);
  Premium bán INSIGHT (Daily Brief/Coach/independent-insight) — evidence nội bộ: các
  claim-gated statements đã build chính là nguyên liệu Premium.
- **V/W:** Ads: chỉ contextual, chỉ transition/browsing/teacher-utility; **khuyến nghị
  mạnh: band 1-2 KHÔNG ads bất kể vị trí** [I + trách nhiệm]; ad-free-family là perk
  Premium hợp lý [R pricing].
- **X:** Subscription = FAMILY (khớp shared-device §26; RevenueCat Hub sẵn).
- **Y/Z:** COGS model: OCR/STT/TTS on-device (Hub ✓ free) · LLM = số đo shadow làm baseline
  · free-provider Hub (BYOK/Ollama) giảm COGS thêm [F42-đo khi tích hợp].
- **AA. TUYỆT ĐỐI KHÔNG monetize:** hint/answer/reveal (rewarded-ads) · assessment ·
  evidence/mastery (payment≠truth) · dữ liệu hành vi trẻ · streak/dependency mechanics.

## AB-AG. Hành động

**AB experiments:** ①shadow→canary generative (đã KEEP SHADOW) ②teacher-pilot 5 GV
③parent-premium fake-door với Daily Brief mock từ data thật ④contextual-ads UX test
NGOÀI learning loop. **AC risk nếu build 38 concept ngay:** dạy sai method (BCNN!), scalar
% phá trust, ads/gamification phá thesis, 10-12 bị bỏ rơi. **AD priority:** WAL-108 slice
(giữ — xem dưới) → multi-profile → Voice/EN adapter → subject surfaces theo corpus-size.
**AE chưa build:** simulation, teacher-LMS đầy đủ, ads-SDK, cloud-sync. **AF First
Slice: GIỮ WAL-108 (Toán 5 B6) + MỞ RỘNG bắt buộc** thêm 2 bounded checks: TV đọc-hiểu
(Reader — đã build, chi phí ~0) + Sử source-reading mini (SourceReader mộc) để chống
Math-overfit ngay trong slice [§26/§38 order]. **AG Founder cần quyết sau:** ①child-ads
legal/luật sư ②pricing Premium ③teacher pilot scope ④canary generative ⑤ngày bật P0 slice.


## WAL-115 (2026-09-02) — COGS / UNIT ECONOMICS: SỐ ĐO THẬT

Đo (N=50 run LLM thật, haiku qua CLI, usage thật — tool/eval/unit_economics.py):
cost/turn μ=$0.0116 · p95=$0.0201 · out-tokens μ=837 · latency μ=14.0s p95=21.9s.
⚠️ harness CLI mang system prompt ~17k cached ⇒ đây là TRẦN THÔ; API trực tiếp
với cage prompt gọn sẽ thấp hơn — giữ số đo, không tự chiết khấu.

| Mode (LLM turns/phiên — mô hình khai rõ) | nhẹ 1 phiên/ngày | vừa 2 | nặng 4 |
|---|---|---|---|
| A deterministic (0 — CẤU TRÚC, test giữ) | $0.00 | $0.00 | $0.00 |
| B minimal-generative (2 = cap hint ladder) | $0.70 | $1.40 | $2.79 |
| C LLM-heavy (8 ≈ mọi lượt) | $2.79 | $5.59 | $11.17 |

Kết luận đề xuất (quyết định = Founder): **Student Free credible ở MODE A vô
điều kiện** (engine không có đường ra network — unit_economics_test quét import
giữ bằng test, một phiên thật sai→hint→đúng chạy ~µs CPU cục bộ). MODE B chỉ
khả thi khi (1) cage prompt gọn + cache, (2) latency giải quyết — p95 21.9s
hiện KHÔNG đạt cho hint inline ⇒ thêm một lý do KEEP SHADOW (WAL-30). MODE C
không bền cho free tier — củng cố deterministic-first (ADR hiện hành).
OCR/STT/TTS: on-device (Hub, $0). Số liệu này bổ sung §29 AI COST của
Checkpoint (comment trên WAL-112).

## WAL-119 (2026-09-02) — ENTITLEMENT ARCHITECTURE (chưa payment)

ROLE × AGE-POLICY × SUBSCRIPTION × CAPABILITY × SAFETY → ENTITLEMENT, một
resolver (entitlement-v1). Premium = family-unit, bán INSIGHT+COACHING+
CONVENIENCE (matrix: PARENT-UX-AUDIT.md §WAL-119); learning loop FREE bất
biến theo CẤU TRÚC (engine không có chỗ nhận tier — test quét). Consent/
privacy/export-delete không bao giờ paywall. Pricing/thu tiền = Founder Gate.

## WAL-125 (2026-09-02) — ADS/TRẺ EM: research memo đã nộp
Xem docs/safety/ADS-CHILDREN-LEGAL-RESEARCH.md — bảng band×loại (Grade 1-2
NO ADS; personalized FORBIDDEN mọi band; contextual = NEEDS-LEGAL; teacher
surface là ứng viên ít rủi ro nhất) + 5 câu hỏi lawyer. STOP — Founder quyết.
