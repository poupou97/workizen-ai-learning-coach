# SAM-PEDAGOGY-CRITICAL-REVIEW — cố giết ý tưởng (§18)

**Ngày:** 2026-09-02 · WAL-99 · 14 failure mode, mỗi cái Risk→Why→Detection→Mitigation→Kill.

| # | Risk | Why | Detection | Mitigation (hiện trạng) | Kill condition |
|---|---|---|---|---|---|
| 1 | **False mastery inference** | ít mẫu + đoán may + stream hỗ trợ | FALSE-TRUSTED rate (ĐÃ ĐO: 10–19% gate V1) | claim-gate 3 trục + ADR-007 (→0–2%) + coverage | FT >5% trên trẻ thật sau chỉnh |
| 2 | **LLM misdiagnosis** (misconception bịa) | LLM tự do gán nhãn lỗi nghe-có-lý | so nhãn LLM vs luật tất định vs giáo viên | catalog tất định trước, LLM chỉ đề xuất PENDING | disagreement với giáo viên >30% |
| 3 | **Over-scaffolding** | «giúp» dễ nghiện — dạy-quá-tay | hint-strength + independence-trend (tầng-1 eval) | ±1 + REVEAL gate + fading; WAL-87: sai về phía này ít nguy hiểm cho ĐO nhưng hại HỌC | independence-trend giảm 4 tuần liên tiếp |
| 4 | **Trẻ gaming tutor** (bấm bừa lấy hint/đáp án) | mọi hệ hint đều game được | pattern: sai-nhanh-liên-tục + hintRequested dồn (timeSpent có sẵn) | guessing-detector (scenario #8) + không bao giờ full trước attempt | >X% phiên có pattern gaming |
| 5 | **Dependency on AI** | tutor tiện → không tự học | tỷ lệ bài làm KHÔNG cần SAM theo thời gian | §25.11 là mục tiêu tối ưu tường minh; stop-rest hạng nhất | trẻ từ chối làm bài không có SAM (WAL-49 quan sát) |
| 6 | **Parent surveillance** | dashboard hoá là quán tính sản phẩm | review UI: đếm metric-gây-áp-lực xuất hiện | claim-gate + MỘT-khuyến-nghị + cấm transcript-dump (test giữ một phần) | phụ huynh dùng SAM để phạt con (WAL-49 phỏng vấn) |
| 7 | **Curriculum mismatch** | dạy đúng toán nhưng sai sách/lớp | boundary-violation rate (eval tầng 1) | TutorScope + stage + corpus-derived methods; F2 test | vi phạm >0 ở chế độ production |
| 8 | **Wrong age adaptation** | câu lớp 5 cho trẻ lớp 2 | reading-level check trong scenario bank | băng tuổi (WAL-50) + luật câu-ngắn | trẻ không hiểu SAM nói gì (WAL-49) |
| 9 | **Pedagogy theater** | prompt tử tế TRÔNG như dạy (socratiq-ai audit) | đòi bằng chứng CẤU TRÚC: gate/state/eval — không tin demo | mọi luật = kiểu dữ liệu + test + đột biến (chuẩn repo) | tính năng dạy mới nào ship không kèm chốt đo |
| 10 | **Excessive complexity** | mô hình đẹp nhưng không ai bảo trì | LOC/khái niệm mới trên mỗi giá trị người dùng | §25.18: không abstraction mới nếu model cũ giải quyết (đã bác TeachingStrategy-enum) | tính năng học >2 tuần không chạm được trẻ thật |
| 11 | **Analytics without evidence** | «learning insights» từ số không có nghĩa | mọi claim UI phải truy về evidence (citation) | claim-gate + provenance bắt buộc | một claim không truy vết được lọt UI |
| 12 | **Cognitive overload** | nhiều surface/gợi ý = nhiễu | thời gian-tới-hành-động-đầu của trẻ | MỘT hành động/màn (Mission) + tối giản taxonomy | trẻ lạc trong app (WAL-49) |
| 13 | **Privacy/child data** | ảnh bài + giọng + log là dữ liệu trẻ em | audit retention từng loại | bậc thang retention + local-first + luật 91/2025 (REVIEW PENDING) | bất kỳ dữ liệu trẻ nào lên cloud không rõ căn cứ |
| 14 | **Reward distortion** | gamification lệch mục tiêu (điểm > hiểu) | đo hành vi săn-thưởng | cấm điểm/streak/leaderboard (test) | trẻ hỏi «làm bài này được mấy sao?» thành phổ biến |

Bổ sung 2 rủi ro NGHIÊN CỨU (meta): (15) **benchmark tự-đạt** — tự viết eval tự pass; thuốc:
judge calibrate với giáo viên + κ công bố; (16) **nguỵ chứng cứ văn liệu** — trích meta-analysis
ngoài ngữ cảnh (VD retrieval âm tính word-problem đã ghi); thuốc: cột caveat bắt buộc trong evidence map.
