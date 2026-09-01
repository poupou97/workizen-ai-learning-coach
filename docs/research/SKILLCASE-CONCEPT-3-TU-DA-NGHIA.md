# SkillCase — khái niệm #3 LIÊN MÔN: `tu-da-nghia` (Tiếng Việt 5) — verdict: **MODIFY (diễn giải)**

**Ngày:** 2026-09-01 · **Nguồn [PRIMARY]:** SGK Tiếng Việt 5 KNTT tập một, Bài 13 tr.65–66
(OCR mới trong phiên: `poc-out/ocr/tv5/`, conf 1.00) + mục lục (Bài 15 "Luyện tập về từ đa
nghĩa" — dạy/luyện tách bài, giống mẫu Toán).
**Phương pháp đúng lệnh Founder §I:** KHÔNG đi tìm SkillCase — hỏi *nguồn tự cấu trúc biến
thể có nghĩa như thế nào*.

## Nguồn tự cấu trúc thế nào (nguyên văn)

Ghi nhớ tr.66: *"Từ đa nghĩa là từ có nhiều nghĩa, trong đó có **một nghĩa gốc** và một hoặc
một số **nghĩa chuyển**. Các nghĩa của một từ đa nghĩa luôn có mối liên hệ với nhau."*

Chuỗi bài tập phân bậc có hệ thống (tr.65–66):
| BT | Yêu cầu | Kỹ năng đòi hỏi |
|---|---|---|
| 1a | tìm nghĩa thích hợp cho từ *mắt* trong ngữ cảnh | **nhận diện nghĩa** |
| 1b, 2, 3 | nghĩa nào là gốc, nghĩa nào là chuyển (*mắt, biển, lưng*) | **phân loại gốc/chuyển** |
| 1c | các nghĩa liên hệ với nhau như thế nào | **giải thích mối liên hệ** |
| 4 | đặt câu để PHÂN BIỆT các nghĩa (*ấm, lạnh*) | **sản sinh** |

## Phát hiện trung tâm: trục biến thể KHÁC CHẤT so với Toán

- Toán (`quy-dong`, `so-sanh-so-thap-phan`): biến thể = **ĐIỀU KIỆN BỀ MẶT của đề** (chia
  hết/không; phần nguyên khác/bằng) → chọn **PHƯƠNG PHÁP khác** → phân ca được bằng hàm
  tất định lúc parse (`analyzeFractionPair`…).
- Tiếng Việt (`tu-da-nghia`): sách KHÔNG chia "trường hợp của đề"; sách chia **BẬC YÊU CẦU
  NHIỆM VỤ** (nhận diện → phân loại → giải thích → sản sinh) trên cùng khái niệm. Một học
  sinh phân loại đúng vẫn có thể không sản sinh được — đúng hiện tượng "mastery từng phần"
  mà SkillCase sinh ra để giữ.

## Verdict: **MODIFY (mở rộng diễn giải, KHÔNG đổi schema)**

1. SkillCase tổng quát hoá thành: *biến thể có-cấu-trúc-theo-nguồn đòi BẰNG CHỨNG RIÊNG* —
   trục biến thể là điều-kiện-đề ở Toán, là bậc-nhiệm-vụ ở Tiếng Việt. Schema hiện tại
   (`id, conceptId, condition, introducedGrade`) CHỨA ĐƯỢC cả hai (condition = lời sách mô
   tả biến thể); ConceptSummary/claim/coverage tái dùng nguyên.
2. **Hệ quả kiến trúc thật (mới):** phân-ca-lúc-parse CHỈ tồn tại ở miền phân tích được
   (số học). Ở miền ngôn ngữ, ca là **thuộc tính lúc SOẠN BÀI** (authoring/Q-matrix gán
   "bài này đo kỹ năng phân-loại"), không suy được từ bề mặt đề bằng hàm tất định.
   Fail-closed giữ nguyên: bài chưa gán ca ⇒ caseUnknown ⇒ Tutor im lặng.
3. Giả thuyết ghi lại [HYP], chưa đủ bằng chứng: trong kỹ năng *phân loại*, nghĩa chuyển
   trừu tượng (lạnh = thái độ) có thể là ca khó riêng so với nghĩa chuyển cụ thể (lưng núi)
   — sách chạm tới (BT4b nghĩa 2) nhưng không đặt tên ca. Chờ dữ liệu học sinh.

## Trạng thái xác minh SkillCase sau 3 khái niệm
| Khái niệm | Môn | Trục biến thể | Phân ca lúc nào | Verdict |
|---|---|---|---|---|
| quy-dong | Toán | điều kiện đề | parse-time (tất định) | KEEP |
| so-sanh-so-thap-phan | Toán | điều kiện đề (kể cả bề mặt) | parse-time | KEEP |
| tu-da-nghia | Tiếng Việt | bậc nhiệm vụ | authoring-time | **MODIFY (diễn giải)** |

Giới hạn: vẫn một bộ sách (KNTT); "bậc nhiệm vụ" mới quan sát ở MỘT bài — cần bài thứ hai
của chính Tiếng Việt (ứng viên: `đại từ` tr.20 + 2 bài luyện tập, đã thấy trong mục lục)
trước khi nâng diễn giải này thành ADR.
