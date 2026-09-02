# 38-SCREEN AUDIT — concept-ai-first/ (Task Order 2026-09-02)

**Nguồn:** 38 ảnh + `home1.png` (biến thể AI-first của Home). Concept = DESIGN INTENT,
không phải spec. Audit đối chiếu Product Truth thật (kernel 323 test + K-12 registry).

**Đếm verdict: KEEP 10 · MODIFY 20 · REPLACE 6 · SPLIT 1 · MERGE 1 (05→home1) · REMOVE 0 nguyên màn · DEFER: các phần teacher/simulation-nâng-cao/voice-full nằm trong dòng.**

| # | Screen | Learning job | Verdict | Lý do cốt lõi (đối chiếu truth) |
|---|---|---|---|---|
| 01 | Onboarding | định vị SAM + chọn vai | **KEEP** (sửa nhẹ) | Role Student/Parent đúng §26; value prop «ít phụ thuộc hơn» khớp thesis. Sửa: «Đăng nhập» → account-optional (§26.10); thêm đường «máy gia đình nhiều con» |
| 02 | Learner Profile | tạo LearnerProfile | **MODIFY** | Wizard 5 bước quá dài (F13 đã đo: 2 câu đủ để bắt đầu); ngày-sinh đầy đủ + giới tính = thu thừa dữ liệu trẻ (privacy) — birthYear đủ; giữ invariant lớp≠trình độ đã in trên màn ✓; young = parent-owned (WAL-100) |
| 03 | Subject Setup | chọn môn | **MODIFY** | Grid hardcode SAI curriculum: lớp 5 không có «GDCD» (là Đạo đức), «Khoa học» ✓; PHẢI sinh từ registry thật (537 docs đã có môn/lớp); nút «Chọn theo lớp» ✓ giữ làm default |
| 04 | Timetable | context TKB | **MODIFY** | 3 cách nhập → giữ 2 (chụp+confirm, tay); BỎ «Tự động gợi ý» (bịa TKB); skippable ✓; F6 giữ: môn≠bài — preview đang đúng mức môn ✓ |
| 05 | Home | Mission Center | **MERGE → home1** | 05 đẹp nhưng home1 mới đúng AI-first: ô hỏi + **5 intent chips = đúng 5 Learning Intent §XVII Master Order** (Học trước/Ôn/Làm bài/Học phương pháp/Kiểm tra) + QR quick-action (khớp WAL-100). Giữ từ 05: thẻ đề-xuất-có-lý-do («vì hôm qua con cần 2 lần gợi ý» — ĐÚNG resolveAgenda WAL-102 đã build). Bỏ: Xu/XP header. Thêm: header «Tên · Lớp ▾» đổi-người-học (§26.12) |
| 06 | Subjects | danh mục môn | **MODIFY** | «Mức hiểu 72%» = scalar — VI PHẠM ba-trục đã falsify. Thay bằng ConceptClaim ngôn ngữ trẻ («Đang học/Cần ôn/Chưa có dữ liệu») + position; giữ layout |
| 07 | Subject Home | trục môn | **KEEP** (modify) | Position + «SGK Toán 5 Tập 1 Trang 21» ✓ provenance-first; knowledge-map mini có «Chưa học» tách riêng ✓ (unobserved≠failed); sửa: «Hiểu 72%/Chính xác 78%» → claim + observed-count; template này là BASE, subject variant đổi TRỤC (xem SUBJECT-UX) |
| 08 | Camera | acquisition | **KEEP** | Pre-capture tips khớp WAL-65 gate đã build; thu 4 mode → 2 (Bài tập, SGK) cho slice; «Tự động» = pre-capture guidance chạy nhẹ |
| 09 | Camera Confirm | safety boundary | **KEEP** | KHỚP CanonicalProblem/ConfirmedProblem ĐÃ BUILD: ảnh + «SAM nhận diện» + sửa/chụp lại + xác nhận; «SAM xác định môn/lớp/chủ đề/kỹ năng» = attribution hiển thị ✓ |
| 10 | Tutor Start | khởi tạo phiên + provenance | **MODIFY** | Đưa Pedagogical Provenance lên đầu (WHAT/WHERE/METHOD/SOURCE từ TeachingProvenance đã có); BỎ nút «Ẩn đáp án» (REVEAL gate là luật, không phải toggle); «SAM giải thích 3 bước» trước khi trẻ thử → chỉ ở intent «Học trước», còn «Làm bài» phải diagnostic-first |
| 11 | Diagnostic | chẩn đoán | **REPLACE** | «Điểm 72/100» + «Sai do nhầm lẫn (LCM)» trình misconception-as-truth = trái delta C. Thay: attributeFailure/probe (WAL-70 đã build) + ErrorHypothesis («SAM đoán là…, thử 1 bài để chắc») + 3 trục, không điểm |
| 12 | Problem Workspace | làm bài | **KEEP** (modify) | Workspace ≠ chat ✓; viết tay ✓ đáng giữ (evidence quá trình); công cụ hint ladder ✓. PHẢI: mọi «SAM gợi ý» đi qua TutorScope — concept đang dạy **BCNN cho lớp 5 = đúng bug method-permission kernel đã chặn** (bằng chứng sống cho kiến trúc) |
| 13 | Hint | assistance ladder | **MODIFY** | «Mức độ gợi ý Nhẹ/Vừa/Chi tiết» do TRẺ chọn = phá thang ±1 engine-quyết (TutorSession đã đúng); trẻ chỉ được «xin thêm»; nội dung hint từ hintTextFor + output-guard; bỏ BCNN |
| 14 | Your Turn | độc lập hoá | **KEEP** | Đúng thesis; các-bước-đã-làm ✓; bỏ «+10 điểm/chuỗi🔥»; evidence: independent vs postHint đã có trong kernel |
| 15 | Success | kết phiên | **MODIFY** | «Bạn thật giỏi» chứa từ CẤM (bannedAbilityPraise!); XP/coin/sao lấn át; thay bằng feedbackFor 4-chiều ĐÃ BUILD (đúng/mức hỗ trợ/evidence-line/khen-nỗ-lực) + next action từ Agenda |
| 16 | Why This Method | provenance WHY/HOW | **KEEP khung / REPLACE nội dung** | Cấu trúc (ý chính→giải thích→trực quan→ghi nhớ) tốt; nội dung phải render từ explainTeaching(): method tích-hai-mẫu (không BCNN), whyLine + PERMISSION («nằm trong chương trình lớp 5») |
| 17 | Source | provenance SOURCE | **REPLACE** | Concept trỏ VnDoc/Loigiaihay/YouTube = vi phạm provenance nặng nhất bộ. Thay: SGK/SGV trang in + 3 mức tuổi-thích-ứng (📖 Theo sách/🧭 Cách mình đang học/✨ SAM giải thích thêm — đúng sourceLineForChild đã mutation-guard) |
| 18 | Review | ôn tập | **REPLACE** | Concept = bảng điểm+đấu trường+leaderboard. Thay: ReviewSchedule (reviewStateOf) + weak-case + transfer-need; giữ đúng 1 mầm concept có: «Ôn lại vào 22/05» |
| 19 | Learning Map | bản đồ tri thức | **MODIFY** | Path-node ✓ hình thức; thay trạng thái bằng ConceptClaim 6 mức + coverage/confidence; BỎ radar-kỹ-năng (số bịa), XP/level/streak; completion% ≠ mastery |
| 20 | Quiz | luyện có đo | **KEEP** (modify) | Flow chọn→giải thích ngay ✓; «Xem gợi ý» ghi hintRequested ✓ khớp evidence; bỏ XP/xếp hạng/Top%; hint content qua guard |
| 21 | Assessment | đánh giá | **SPLIT** | Ảnh là màn KẾT QUẢ. Thiếu màn LÀM BÀI assessment-mode: hint TẮT, không reveal (AssistancePolicy.assessment + tutoringViolationsInExam đã có). Tách 2 màn; profile-confirm trước bài (§26.8) |
| 22 | Result | sau đánh giá | **MODIFY** | Bỏ «Top 12%» so sánh xã hội; thêm tách independent/assisted + confidence + ErrorHypothesis (nếu đủ evidence) + next action; giữ review-từng-câu |
| 23 | Vietnamese | môn TV | **KEEP** (modify) | Chủ đề khớp corpus TV thật (Chính tả/Từ-câu/Viết/TLV); 5 công cụ ≈ 5 ResponseKind (nghe-viết = surface mới hợp lệ); bỏ %/sao/streak; SkillCase recognize≠apply≠write giữ theo store |
| 24 | Essay | viết-quá-trình | **MODIFY** | Compose-lite ĐÃ BUILD đúng hơn concept: thiếu outline→draft→feedback→revise; rubric 4 tiêu-chí giữ làm FEEDBACK không phải điểm/100 (văn correct=null); bỏ «Gợi ý từ» mặc định (viết hộ mềm); bỏ XP |
| 25 | Physics | môn Lý | **KEEP** (modify) | Simulation slider v-t + graph = interactive có giá trị THẬT (không decorative); cần grade-map (KHTN 6-9, Lý 10-12); bỏ «điểm TB»; formula/diagram/graph = surfaces |
| 26 | Chemistry | môn Hoá | **KEEP** (modify) | Mô phỏng phân tử + bảng tuần hoàn + cân bằng PT ✓ đúng hướng; «Nguyên tố hôm nay» hay; cùng sửa scalar |
| 27 | History | môn Sử | **MODIFY** | Timeline ✓ nhưng thiếu ĐÚNG phần order đòi: source-reading, SOURCE CLAIM vs INTERPRETATION vs LEARNER CONCLUSION; «đã ghi nhớ 18/24 sự kiện» = memorization-mindset; ảnh AI-gen nhân vật thật (VNG…) = rủi ro chính xác/tôn nghiêm → dùng tư liệu thật hoặc không ảnh |
| 28 | Geography | môn Địa | **KEEP** (modify) | Map first-class + layer toggle ✓ đúng; số liệu diện tích/dân số cần provenance nguồn; bỏ thử-thách-quốc-kỳ gamified khỏi trục chính |
| 29 | AI Learning | môn AI | **REPLACE** | SAI QĐ 2422 hoàn toàn: lộ trình ChatGPT→ML→DL→Prompt + leaderboard + tools ChatGPT/Gemini. Thay bằng AiCurriculum ĐÃ SỐ HOÁ (267 YCCĐ, 4 strand A-D, gradeCeiling F8); «không curriculum edge → không claim integration» đã là luật ADR-008 |
| 30 | History Sessions | lịch sử học | **KEEP** (modify) | Model đúng store đã build (one session store + projection ngày/môn); bỏ %-mỗi-phiên; thêm trace assistance/method khi mở chi tiết |
| 31 | Progress | tiến bộ | **REPLACE** | Radar 6 «kỹ năng» = SỐ BỊA từ không-evidence; thay bằng metrics ĐO ĐƯỢC đã có: independence trend (nguyên tắc #15!), hint-depth giảm, self-correction, coverage, confidence, review-due; heatmap lịch ✓ giữ |
| 32 | Parent Home | tối-nay-giúp-gì | **MODIFY** | Trả lời đúng câu hỏi ✓ («AI Insights» + gợi ý); BỎ % cạnh avatar 3 con (sibling comparison ngầm — §26.13); «Điểm TB 86%» → claim-gated statement; achievements «Top Learner» bỏ |
| 33 | Parent Detail | chi tiết 1 con | **MODIFY sâu** | «Xếp hạng lớp 3/28 Top 11%» = dữ liệu KHÔNG TỒN TẠI + phản triết lý → bỏ; %/môn → 3 trục claim-gated (parent_explanation.dart đã có luật); «Nhận xét giáo viên» = DEFER phase teacher; giữ lịch-sắp-tới |
| 34 | Multi-child | quản lý các con | **MODIFY** | BỎ nguyên khối «So sánh nhanh» (chart chồng 3 con) → «Tình hình các con» per-child; GIỮ: «Cần bạn lưu ý» ✓, lịch gộp ✓, thành tích CHUNG «Gia đình học tập» ✓ (hợp tác); nâng thành FAMILY PROFILE MANAGER (§26.13: thêm/sửa/chuyển Learner Mode) |
| 35 | SAM Voice | voice surface | **MODIFY** | Voice = surface DƯỚI cùng constraint (TutorScope/guard/assistance — buildTutorPrompt+output_guard tái dùng); 4 chế độ → map vào Learning Intent; «Giải bài tập» quick-action → «Cùng làm bài» (không làm hộ); transcript ≠ evidence; age: primary voice-heavy ✓ |
| 36 | Library | kho | **REPLACE** | Concept = Google-Drive-của-học-sinh (236 files, quota GB). Thay bằng 5 loại A-E: SAM Curriculum Knowledge (browse từ curriculum-structure.json 7.199 bài!) / OER-teacher / learner-imported / saved artifacts / Offline Pack (đã có sam-units.db); không expose pack như files |
| 37 | Notifications | nhắc học | **MODIFY** | GIỮ: nhắc lịch (TKB context), bài được giao, phản hồi GV, review-due; BỎ: streak-pressure, «Top 10% trong lớp», achievement-spam; parent policy-aware ✓ filter theo con đã có |
| 38 | Settings | cài đặt | **MODIFY** | Khung tốt (Gia đình & Trẻ em ✓, Quyền phụ huynh ✓, Dữ liệu/Xoá ✓, Offline ✓); BỎ XP/level header; THÊM: Parent PIN (§26.3), AI/cloud-inference disclosure, retention/transcript policy; tách Student vs Parent settings theo mode |

## Ba phát hiện xuyên suốt (đưa vào mọi quyết định)

1. **Concept tự chứng minh vì sao cần kernel:** màn 12/13/16/17/20 đều dạy **BCNN cho
   lớp 5** — chính xác lỗi method-permission mà TutorScope/method-catalogue (29 method
   có trang nguồn) được xây để chặn. Concept không sai thẩm mỹ — sai TRI THỨC, và chỉ
   pipeline K-12 đang chạy mới sửa được tận gốc.
2. **Scalar % và gamification tràn mọi màn** (mức hiểu %, điểm chẩn đoán, radar bịa, XP/
   streak/leaderboard/Top%) — trái ba-trục + nguyên tắc #15 + «không tối ưu engagement».
   Một pass «de-gamify» áp toàn bộ: giữ heatmap/tiến-trình-theo-mình, bỏ so sánh xã hội.
3. **Provenance có mặt nhưng sai nguồn** (17 trỏ web ngoài) — trong khi kernel đã có
   TeachingProvenance/sourceLineForChild mutation-guarded. UI chỉ việc RENDER cái đã có.
