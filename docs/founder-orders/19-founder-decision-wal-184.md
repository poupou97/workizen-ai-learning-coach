FOUNDER DECISION — WAL-184

Chọn hướng:

KEEP SPACED REVIEW POLICY.
CHANGE THE SEMANTICS / WORDING OF THE PROJECTION.

Không xóa lịch ôn chỉ vì learner vừa trả lời đúng một lần.

Nhưng Home không được diễn giải ReviewDue thành:

“Con còn vướng dạng này”

nếu evidence hiện tại không support claim đó.

Phân biệt rõ:

CAPABILITY / MASTERY
= hiện tại evidence cho thấy trẻ làm được gì.

REVIEW URGENCY
= khi nào nên gặp lại kiến thức để kiểm tra retention / củng cố trí nhớ.

REVIEW_DUE != CURRENTLY_STRUGGLING.

Ví dụ sau independent success:

Lesson:
“Con vừa tự làm được dạng này 🚀”

Home:
“Con đã tự làm được dạng này. SAM sẽ nhắc con ôn lại sau vài ngày để nhớ lâu hơn.”

hoặc wording ngắn/tự nhiên hơn theo Design System hiện tại.

Nếu learner thực sự đang có evidence về difficulty thì mới được dùng wording tương đương:

“Con còn vướng...”
“Phần này cần củng cố...”

Do not change D2 spaced-review semantics chỉ để sửa copy.

Do not suppress review scheduling solely because of same-day success unless
existing review algorithm independently determines that from evidence.

Audit các projection khác để đảm bảo không có chỗ nào đang collapse:

REVIEW_DUE
=
WEAK / STRUGGLING.

Fix WAL-184 bằng smallest coherent change.

Add regression test cho scenario:

past difficulty
→ current independent success
→ review remains scheduled
→ capability projection positive
→ review projection says retention/revisit, NOT current difficulty.

Sau đó:
test → Nokia verify nếu user-visible → PR/CI/merge → close WAL-184.

Không cần quay lại Founder duyệt wording chi tiết.
Chọn Vietnamese copy tự nhiên nhất.

Sau WAL-184 tiếp tục autonomous backlog theo dependency.
