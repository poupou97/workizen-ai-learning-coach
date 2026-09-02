# Danh tính theo tuổi + QR autonomy (WAL-100, Founder delta M)

**Trạng thái:** research→design, không implement (teacher/QR infra vẫn thuộc
«KHÔNG build bây giờ» của SAM-MULTI-ROLE §6). Bổ sung cho doc multi-role:
Option C KHÔNG phải universal flow — nó là flow cho MỘT ĐOẠN TUỔI.

## 1. Nguyên tắc: autonomy tăng theo tuổi (Constitution #13)

Quan hệ guardian↔learner không phải hằng số — nó là HÀM của tuổi. Một mô
hình đóng đinh «trẻ = sub-profile của cha mẹ» đúng ở lớp 1 và SAI ở lớp 11:
THCS/THPT mà vĩnh viễn là sub-profile là phủ nhận chủ thể học tập — và về
pháp lý VN, dữ liệu cá nhân của người 16+ không còn mặc định do cha mẹ
định đoạt (xem §5).

## 2. Hai mô hình sở hữu + một transition

| | TIỂU HỌC (young) | THCS/THPT (older) |
|---|---|---|
| Ai tạo profile | **Parent tạo** (Option C — đã thắng falsification F3) | **Học sinh tự sở hữu** UserAccount + LearnerProfile |
| Ghép nối | Parent phát QR pairing cho THIẾT BỊ của con | **Học sinh phát invite** — parent scan → đề nghị GuardianRelationship, học sinh (hoặc luật authority) xác nhận |
| Recovery | qua guardian (đã giải trong multi-role F3/F13) | qua chính account học sinh; guardian là kênh PHỤ có điều kiện |
| Mặc định chia sẻ | guardian thấy claim-gated view đầy đủ | minimum-necessary; mở rộng cần consent của học sinh |

**Transition (điểm mới của delta M):** khi trẻ lên THCS (ngưỡng đề xuất:
theo CẤP HỌC, không theo sinh nhật — khớp đời sống trường lớp VN):
1. Hệ đề nghị chuyển: LearnerProfile parent-owned → student-owned account;
   evidence/JSONL GIỮ NGUYÊN — đổi CHỦ THỂ SỞ HỮU, không đổi Learning Truth
   (cùng bất biến «withGrade không đụng evidence»).
2. GuardianRelationship KHÔNG bị xoá — hạ authority: owner→guardian-viewer
   (claim-gated, minimum-necessary dần theo tuổi).
3. Không tự động: transition là NGHI THỨC có confirm của cả hai phía —
   không âm thầm đổi quyền của ai (SCAN≠AUTHORIZATION mở rộng thành
   AGE≠AUTO-TRANSFER).

## 3. QR theo tuổi — cùng một QRInvitation, khác issuer

Cấu trúc QRInvitation {purpose, issuerId, nonce, expiresAt, maxUses,
revoked} (multi-role §3) KHÔNG đổi. Tuổi chỉ đổi **ai được là issuer của
purpose nào**: young — parent issue device-pairing, teacher issue
class-invite (parent scan/confirm enrollment); older — học sinh issue
guardian-invite; học sinh tự scan class-invite và tự confirm. Bảng
issuer×purpose×age là POLICY đọc được, không phải code rẽ nhánh rải rác.

## 4. Device-loss / multi-guardian (kế thừa, không mở lại)

Device-loss: young — parent re-pair thiết bị mới, thiết bị cũ revoke;
older — đăng nhập lại account, guardian không cần can thiệp. Multi-guardian:
GuardianRelationship n-n + authority (multi-role F14) — không đổi; chỉ thêm:
với older, thêm guardian mới cần consent của HỌC SINH, không chỉ của
guardian hiện có.

## 5. Pháp lý VN — REVIEW PENDING (Founder Gate, không tự kết luận)

Điểm neo cần luật sư xác nhận, KHÔNG code trước: Luật Trẻ em 2016 (dưới 16
= trẻ em); Nghị định 13/2023 về bảo vệ dữ liệu cá nhân (xử lý dữ liệu trẻ
em cần đồng ý của cha mẹ/người giám hộ — ranh giới tuổi và hình thức đồng
ý cho «học sinh tự sở hữu account» ở THCS cần rà); Luật Bảo vệ dữ liệu cá
nhân mới (hiệu lực 2026) có thể siết thêm. Ngưỡng chuyển-cấp đề xuất ở §2
là NGỮ NGHĨA SẢN PHẨM; ngưỡng PHÁP LÝ do review quyết — hai ngưỡng có thể
khác nhau và model phải chứa được cả hai (authority per-relationship).

## 6. Điều KHÔNG đổi

MVP vẫn Student+Parent (young flow trước — đúng đối tượng tiểu học hiện
tại của corpus); teacher/authz/QR infra vẫn chưa build; mọi kết luận
multi-role §2 (18 câu F) giữ nguyên hiệu lực.
