# SAM-LEARNING-SCIENCE-EVIDENCE-MAP — phương pháp × sức bằng chứng × chỗ dùng trong SAM

**Ngày:** 2026-09-02 · WAL-99 · Nguồn ưu tiên: EEF Toolkit (meta-review), Dunlosky et al. 2013
(Psych Sci Public Interest), Rowland 2014 / Schwieren 2017 (meta retrieval), meta expertise-reversal
(176 effect sizes / 60 studies / 5.924 người). KHÔNG câu nào «research proves» thiếu nguồn.

| Method | Sức bằng chứng | Tuổi/môn | Tốt cho | Rủi ro | SAM usage (đối chiếu code) |
|---|---|---|---|---|---|
| **Metacognition/self-regulation** | EEF **+7-8 tháng**, evidence cao (246 papers) | mọi cấp | lập kế hoạch-giám sát-tự đánh giá | dạy trừu tượng suông không gắn môn | `hintRequested` là bằng chứng siêu-nhận-thức (đã code); checklist tự-soát Compose (đã code); probe «tự đặt câu hỏi trước khi dùng» khớp 3.A1.5 QĐ2422 |
| **Feedback** | EEF **+6 tháng** (tiểu học +7), evidence cao; feedback về TASK/CHIẾN LƯỢC > khen | mọi cấp | sửa hướng ngay trong lượt | khen tư chất phản tác dụng | ĐÃ ĐÚNG HƯỚNG: `bannedAbilityPraise` + 4-chiều tách AFFECT khỏi EVIDENCE (WAL-69, có test) |
| **Retrieval practice / practice testing** | Dunlosky HIGH utility; g≈0.50 (Rowland) / 0.56 (Schwieren); transfer nhỏ hơn (Pan&Rickard) | rộng; word-problem toán có nghiên cứu âm tính | giữ lâu, lộ lỗ hổng | thành flashcard-app; đề quá dễ | PARTIAL: review tile + Quiz/Select là retrieval de-facto; THIẾU khái niệm tường minh + cấm-đọc-lại-làm-ôn. Ưu tiên nạp vào Agenda |
| **Distributed/spaced practice** | Dunlosky HIGH utility | mọi cấp | chống quên | lịch cứng nhắc | PARTIAL: SM-2-shape (F5 tách đúng); FSRS là candidate NÂNG CẤP LỊCH, không phải student model (bất biến §25.16) |
| **Worked examples** | mạnh cho NOVICE (Sweller); **expertise reversal**: hại learner khá (meta 176 ES) | novice, môn cấu trúc | giảm tải nhận thức lúc mới học | dùng cho trẻ đã khá → phản tác dụng | `SupportLevel.workedStep` đã là bậc riêng; ⭐ expertise-reversal CHÍNH LÀ evidence văn liệu cho fading ±1 (WAL-87 sim khớp: help-helps cho novice, never-help thắng khi đã vững) |
| **Interleaving** | Dunlosky MODERATE (bằng chứng đang lớn) | toán có kết quả tốt | phân biệt DẠNG bài | quá sớm → quá tải | MISSING; ứng viên tự nhiên: xen ca (divisible/non-divisible/equal) trong Quiz — chờ WAL-49 |
| **Self-explanation** | Dunlosky MODERATE | rộng | hiểu sâu, lộ misconception | tốn thời gian; trẻ nhỏ khó viết | Compose checklist + «giải thích vì sao» trong Parent flow (đã có mẫu); voice = RESEARCH LATER |
| **Elaborative interrogation** | Dunlosky MODERATE | THCS+ tốt hơn | «vì sao đúng?» | với novice thiếu nền → đoán mò | probe/pump đã có khung; nội dung cần corpus |
| **Mastery learning** | EEF **+5 tháng**, evidence LIMITED, low cost | mọi cấp | không để hổng nền | ngưỡng cứng làm chậm trẻ nhanh | ĐÃ LÀ KIẾN TRÚC (BKT + claim gate + coverage); ngưỡng 0.85 = giả thuyết có tên |
| **Parental engagement** | EEF **+4 tháng** (tiểu học +4-5, THCS +2; đọc-viết > toán); ⭐ can thiệp kiểu-giúp-làm-bài-tập KHÔNG tăng attainment; text-nudge rẻ mà có tác dụng | tiểu học mạnh nhất | thói quen, môi trường, đối thoại | cha mẹ thành «giáo viên thứ hai» — CHÍNH EEF bác | Parent Coach đã đúng triết lý («không cần giảng bài — chỉ cần hỏi con giải thích»); weekly-brief kiểu nudge ngắn là hướng ĐÚNG evidence |
| **Formative assessment** | trong Feedback strand EEF | mọi cấp | dạy theo dữ liệu | thành thi liên tục | decide()/probe = formative bẩm sinh; exam-mode tách (F7) |

## Caveat Việt Nam (§12) — không giả định portability
1. Bằng chứng trên chủ yếu US/UK; VN có: sĩ số lớn, học thêm phổ biến, phụ huynh can thiệp SÂU
   (rủi ro «giáo viên thứ hai» CAO HƠN bối cảnh EEF) → Parent Coach càng phải nói «đừng làm gì».
2. Retrieval âm tính ở word-problem: corpus WAL nhiều «bài toán lời văn» → không áp máy móc quiz.
3. Reading level tiểu học: câu Socratic phải ngắn — CV5588 đòi «vừa sức»; đã có luật ±1.
4. Khung pháp lý riêng: QĐ2422 «tổng hợp NHIỀU minh chứng», «không phải thang điểm» — hội tụ.
