# Pedagogically Constrained Agent — nghiên cứu P0 (chưa phải ADR)

**Ngày:** 2026-09-01 · **Trạng thái:** RESEARCH — Founder cấm ra ADR ACCEPTED ở bước này.
**Hai mệnh đề gốc:** TASK SUCCESS ≠ LEARNING SUCCESS · MODEL CAPABILITY ≠ PEDAGOGICAL AUTHORITY.
**Thang bằng chứng (§J):** [ACADEMIC] văn liệu (trích dẫn cần kiểm lại nguyên bản khi soạn ADR) ·
[OSS] mã đã đọc · [WAL] quan sát trong repo này · [PHIL] triết lý Founder · [HYP] giả thuyết.

---

## 1. KNOWN FROM LITERATURE

- **Hai vòng lặp của ITS** [ACADEMIC — VanLehn 2006, *The Behavior of Tutoring Systems*]:
  outer loop chọn BÀI theo student model; inner loop xử lý TỪNG BƯỚC (feedback, hint, cập
  nhật model). Quyền quyết định nằm ở CẤU TRÚC vòng lặp, không nằm ở bộ sinh lời nói.
- **Model tracing ≠ knowledge tracing** [ACADEMIC — Anderson et al., Cognitive Tutors]:
  model tracing theo dõi HÀNH VI từng bước so với mô hình lời giải; knowledge tracing ước
  lượng TRI THỨC qua thời gian. WAL mới có vế sau; vế trước là nền cho diagnostic probe.
- **Taxonomy nước đi hội thoại có sẵn** [ACADEMIC — Graesser et al., AutoTutor]: 12 dialogue
  moves, lõi là chu trình **pump → hint → prompt → assertion** (khơi → gợi → mớm-từ → nói
  thẳng) + 5 mức feedback ngắn tách riêng. ⇒ **TeachingAct KHÔNG phải phát minh mới** —
  prior art trực tiếp, kể cả bản ghép LLM (AutoTutor-LLM "rich pedagogy and guardrails",
  arXiv 2402.09216).
- **Scaffolding & fading** [ACADEMIC — Wood/Bruner/Ross 1976 (contingent tutoring);
  Collins/Brown/Newman (cognitive apprenticeship)]: trợ giúp phải TÙY THUỘC mức vướng và
  PHẢI RÚT DẦN; luật contingency: sai thì tăng một nấc hỗ trợ, đúng thì giảm một nấc.
- **Assistance dilemma** [ACADEMIC — Koedinger & Aleven 2007]: cho thông tin hay bắt tự
  sinh là bài toán đánh đổi CÓ TÊN — không có đáp án phổ quát, phải đo theo miền/giai đoạn.
- **Help-seeking có thể bị lạm dụng** [ACADEMIC — Aleven et al.; Baker et al. ("gaming the
  system", bottom-out hints)]: học sinh câu hint tới đáp án; hệ phải mô hình hoá hành vi
  xin-trợ-giúp, không chỉ nội dung.

## 2. KNOWN FROM OSS (mã đã đọc trong repo research)

- [OSS — OATutor `helpPenaltyMode.js`] ba chế độ phạt hint (`Never/AnswerReveal/OnOpen`),
  mặc định OnOpen: mở hint ⇒ BKT no-credit lần submit sau, **UI vẫn báo đúng** ⇒ tách
  kế-toán-belief khỏi phản-hồi — bản production của mệnh đề TASK ≠ LEARNING.
- [OSS — OATutor `HintSystem.js`] hint "scaffold" = CÂU HỎI CON phải trả lời; sub-hint mở
  khoá tuần tự; TTS per-hint; penalty tách theo nguồn trợ giúp (hint ≠ AI chat).
- [OSS — skillcoco] BKT+SM-2 local-first; review queue là bề mặt hạng nhất.
- [OSS — pyBKT] `forgets`/`multigs`/`multilearn`: tham số hoá theo lớp ngữ cảnh chứ không
  đổi cấu trúc — mẫu tốt cho "policy thay được, cấu trúc đứng yên".

## 3. OBSERVED IN WAL (đã có trong mã, có test)

- Quyền sư phạm ĐÃ nằm ngoài LLM về mặt cấu trúc: `TutorScope` lọc method TRƯỚC khi bất kỳ
  bộ sinh nào chạy (fail-closed, wildcard đóng); `decide()/attributeFailure()` chọn can
  thiệp; `EvidenceWeightingPolicy` quyết cách ghi công — LLM (chưa tích hợp) chỉ có thể là
  **tầng HIỆN THỰC HOÁ lời giảng** trong khung đã chọn. [WAL]
- TASK ≠ LEARNING đã mã hoá: `postHintSuccess` đúng-mà-không-được-ghi-công; 10 đúng-sau-gợi-ý
  = 0 bằng chứng độc lập. [WAL — evidence_replay_test]
- Fading có giá đỡ dữ liệu: thang SupportLevel + log 7 loại sự kiện cho phép ĐO độ sâu trợ
  giúp theo thời gian — chưa có POLICY rút dần. [WAL]

## 4. FOUNDER PHILOSOPHY (ràng buộc thiết kế, không phải kết luận nghiên cứu)

[PHIL] "Lấy tự học làm cốt, do thảo luận và chỉ đạo giúp vào" (HCM 1947 — seed đã ghi nguồn);
SAM không tối ưu phụ thuộc; khen nỗ lực/chiến lược/tự sửa; SAM_YOUR_TURN là trạng thái quan
trọng; lý tưởng = trẻ CÀNG NGÀY CÀNG ÍT CẦN SAM.

## 5. HYPOTHESIS (cần falsify trước khi thành ADR)

- **H1 — TeachingAct là abstraction hạng nhất, TÁCH khỏi Method**: Method = CÁI GÌ của miền
  (lấy tích hai mẫu); TeachingAct = CÁCH SAM can thiệp (ASK/PROBE/HINT/CONTRAST/EXPLAIN/
  DEMONSTRATE/ASK_EXPLANATION/VERIFY/REFLECT/WAIT/STEP_BACK/REVEAL — danh sách ứng viên,
  PHẢI đối chiếu taxonomy AutoTutor + văn liệu tutorial dialogue trước khi chốt).
  Ánh xạ sơ bộ: LearningAction hiện tại (teach/practice/contrastCases/isolateSkills…) là
  lai giữa hai tầng — nếu H1 đúng thì cần tách quyết-định-mục-tiêu khỏi nước-đi-sư-phạm.
- **H2 — Bốn chiều tách biệt** (nâng cấp phát hiện OATutor): TASK CORRECTNESS ·
  ASSISTANCE · MASTERY EVIDENCE · AFFECTIVE FEEDBACK là bốn trục độc lập — trẻ có thể
  đúng-nhờ-trợ-giúp, xứng đáng được khích lệ, và vẫn cho ít bằng chứng độc lập. WAL có
  trục 1–3 (correct/supportedCount/evidenceCount); trục 4 CHƯA có biểu diễn. Khen không
  được nối cứng vào mastery credit.
- **H3 — Diagnostic probe là TeachingAct nhắm vào HỌC SINH, không nhắm vào bài**: chẩn đoán
  bất định → chọn CÂU HỎI vì giá trị thông tin → giảm bất định → mới chọn can thiệp.
  Construct văn liệu gần nhất: model tracing (Anderson), diagnostic assessment/CAT
  (chọn item nhiều thông tin), active learning/information-gain [ACADEMIC]. KHÔNG bịa công
  thức information-gain — `insufficientEvidence → diagnosePrerequisite` hiện tại đã là
  probe thô sơ; nâng cấp cần bằng chứng.
- **H4 — Fading đo được**: policy rút-dần hợp lệ = hàm của (mastery, độ sâu hỗ trợ gần
  đây); metric: tỷ lệ independent-attempt tăng, hint-depth giảm, khoảng cách giữa các lần
  cần SAM tăng. (Trùng anti-goal §8 của Founder.)

## 6. FALSIFIED (tính đến hôm nay)

- ❌ "Mọi bài đa kỹ năng là conjunctive toàn cục" — WAL-54 (phản ví dụ corpus).
- ❌ "eventId không cần thời điểm" — replay audit §G (1 lỗi thật, đã vá).
- ❌ "Engagement tự nó là learning success" [SECONDARY INDUSTRY — Duolingo 2024; đủ cho
  UX doctrine, CHƯA đủ cấp architecture theo thang §J — giữ ở tầng UX].

## 7. OPEN QUESTION

- LLM sinh lời giảng có RÒ quyền không (dạy vượt scope dù bị ràng)? — cần eval harness
  (WAL-59 evaluation tests) TRƯỚC khi tích hợp Generative Tutor; gate thêm: child-safety
  boundary (§L) phải định nghĩa trước.
- Chat tự do có nên chịu penalty như hint (OATutor mặc định Never cho chat)? — cần dữ liệu.
- AFFECTIVE feedback (trục 4 của H2) biểu diễn thế nào mà không thành engagement-first?
- Bao nhiêu bất định thì probe, bao nhiêu thì dạy luôn (ngưỡng của H3)?

## 8. CANDIDATE CONTRIBUTION (nếu sống sót falsification — KHÔNG claim novelty)

Tổ hợp: ranh giới sư phạm fail-closed CÓ KIỂU (TutorScope) + bằng chứng thô replay được +
ba trục claim + TeachingAct tách Method, bám SGK Việt Nam có provenance — từng mảnh đều có
prior art (VanLehn/Anderson/Graesser/OATutor); cái có thể mới là **tổ hợp + tính chất
compile-time-enforced + gắn corpus quốc gia**. Cần khảo thêm trước khi phát biểu.
