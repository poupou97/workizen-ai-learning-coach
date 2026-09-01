# WAL-44 — Child Safety / Privacy Architecture (TRƯỚC Generative Tutor)

**Ngày:** 2026-09-01 · **Trạng thái:** RESEARCH→DESIGN · đi TRƯỚC mọi tích hợp LLM thật (gate WAL-30)
**Thang nguồn:** [OFFICIAL]=văn bản pháp luật/số hiệu đã xác minh qua nguồn pháp lý VN ·
[PRIMARY]=kiến trúc đã có trong repo · [HYP]=đề xuất thiết kế
**Lưu ý pháp lý:** đây là tài liệu KIẾN TRÚC; cam kết tuân thủ chính thức cần luật sư đọc
nguyên văn (Founder gate §39 — legal/compliance commitment).

## 1. Khung pháp lý VN hiện hành (điểm neo, không phải tư vấn pháp lý)

- [OFFICIAL] **Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15** — hiệu lực **01/01/2026** (đang
  hiệu lực), thay Nghị định 13/2023/NĐ-CP; hướng dẫn: Nghị định 356/2025/NĐ-CP.
- [OFFICIAL] Dữ liệu trẻ em: xử lý phải có **đồng ý của trẻ từ đủ 7 tuổi** VÀ **đồng ý của
  cha mẹ/người giám hộ**; trẻ em thuộc nhóm bảo vệ đặc biệt.
- [OFFICIAL] **Luật Trí tuệ nhân tạo 134/2025/QH15** (viện dẫn trong CV 5588/BGDĐT 19/8/2026,
  bản scan trong repo) — hệ thống AI giáo dục cho trẻ em gần như chắc thuộc diện điều chỉnh;
  đọc nguyên văn khi chạm phát hành (Founder gate).
- [PRIMARY — CV 5588 §3] Trường học "không yêu cầu học sinh phải sử dụng tài khoản cá nhân
  hoặc công cụ chưa được rà soát" ⇒ mô hình phân phối qua trường cần phương án không-tài-khoản
  /local-first — khớp kiến trúc hiện tại.
- Hệ quả sản phẩm: consent KHÔNG phải một checkbox — là **cặp đồng ý** (phụ huynh + trẻ ≥7
  tuổi) và phải thu TRƯỚC khi bất kỳ dữ liệu học tập nào rời máy. Tham chiếu quốc tế khi
  quốc tế hoá: COPPA (Mỹ, <13), GDPR-K (EU) — RESEARCH LATER.

## 2. Nguyên tắc kiến trúc №1: LOCAL-FIRST LÀ BIỆN PHÁP AN TOÀN MẠNH NHẤT [PRIMARY]

Kernel WAL đã chạy 100% local (BKT/replay/summary/diagnosis không cần mạng). **Dữ liệu
không rời máy là dữ liệu không cần bảo vệ trên đường đi.** Mọi quyết định sau đây xếp theo
bậc thang: (a) không thu → (b) thu local → (c) rời máy có consent + tối thiểu hoá.

## 3. Bản đồ dữ liệu × chính sách (theo danh mục §27)

| Dữ liệu | Nhạy cảm | Chính sách đề xuất [HYP trừ khi ghi khác] |
|---|---|---|
| LearningEvidence/mastery | cao | LOCAL mặc định [PRIMARY — đã vậy]; xuất/đồng bộ = opt-in có cặp consent |
| Ảnh camera (bài toán) | **rất cao** (có thể lọt mặt/tên/vở) | xử lý local (Vision local [PRIMARY]); mặc định **XOÁ ảnh gốc sau khi ConfirmedProblem tạo xong** — chỉ giữ `rawImageRef` (hash) + biểu thức đã xác nhận; giữ ảnh để debug = opt-in phụ huynh, TTL ngắn |
| Voice (nếu làm TTS/STT) | cao | TTS (đọc gợi ý) không thu gì — an toàn; STT = RESEARCH LATER, chỉ sau khung consent |
| Chat với SAM | cao | tối thiểu hoá: chỉ lưu local; KHÔNG đưa vào corpus tri thức [PRIMARY — luật Student≠Knowledge store của RAG doc] |
| PII hồ sơ (tên, lớp) | cao | tối thiểu: nickname + khối lớp là đủ cho toàn bộ domain hiện tại — KHÔNG cần tên thật, trường, địa chỉ |

## 4. Ranh giới provider/model (điều kiện tiên quyết của WAL-30 Generative Tutor)

1. **Không gửi PII trong prompt**: EvidencePack (RAG doc §4) là hợp đồng đầu vào LLM —
   thêm luật: pack chỉ chứa `learningContext` ẩn danh (stage/concept/case/summary mức
   claim), KHÔNG chứa tên trẻ, không chat history thô, không ảnh.
2. **Provider phải có chế độ không-train-trên-dữ-liệu** (API business terms) — điều kiện
   chọn provider, ghi vào config từ ngày đầu.
3. **Nội dung không an toàn**: input của trẻ → lọc local trước khi rời máy; output của
   LLM → qua PEDAGOGICAL FILTER (đã có TutorScope) + safety filter; mọi từ chối phải
   fail-closed kiểu SAM ("phần này SAM không giúp được, con hỏi bố mẹ/thầy cô nhé") —
   không giảng giải nội dung nhạy cảm.
4. **Eval harness trước tích hợp** (WAL-59): bộ test đỏ gồm cả unsafe-content probes.

## 5. Quyền của phụ huynh & trẻ [HYP, khớp luật]

- Phụ huynh: xem dữ liệu gì đang lưu (màn hình "dữ liệu của con" — đơn giản, thật) ·
  xuất toàn bộ · **xoá toàn bộ** (một nút, thật sự xoá) · rút consent = dừng mọi xử lý ngoài máy.
- Trẻ ≥7 tuổi: được hỏi đồng ý bằng ngôn ngữ trẻ hiểu; SAM không thu gì "lén" — trùng
  nguyên tắc trung thực của philosophy (E12).
- Visibility: phụ huynh thấy CLAIM + bằng chứng học tập; KHÔNG thấy nội dung chat từng
  dòng của trẻ theo mặc định [HYP — cân bằng giám sát/niềm tin; tension ghi lại cho
  philosophy: quyền phụ huynh vs không gian riêng của trẻ — đưa vào E12 xử lý].

## 6. Age-aware behavior

`LearningStage.grade` đã có [PRIMARY] ⇒ age tier suy được không cần ngày sinh (tối thiểu
hoá!): tier TIỂU-HỌC/THCS đổi: giọng SAM, mật độ mascot (design doc đã có), VÀ chính sách
(THCS có thể tự xem lịch sử của mình nhiều hơn). Không thu ngày sinh chính xác.

## 7. Việc mở ra (Jira khi chạm implement)

Consent flow UI (cặp đồng ý) trước slice camera thật · màn "dữ liệu của con" + xoá/xuất ·
safety filter local cho input trẻ · provider policy check tự động · đọc nguyên văn Luật
91/2025 + NĐ 356/2025 bằng luật sư TRƯỚC phát hành (Founder gate).

**Kết luận gate:** WAL-30 (Generative Tutor) bị chặn cho tới khi: §4.1-4.3 implement +
WAL-59 eval harness có unsafe probes + consent flow tồn tại. Ghi vào WAL-30.
