FOUNDER DECISION — PR #121

APPROVED.

Merge PR #121 vào main.

Sau merge:

1. Verify main:
   - flutter analyze
   - full test suite
   - CI
   - repo clean

2. Không đưa content khác lớp trở lại Home để xử lý empty state.

3. Ghi nhận invariant chính thức:

ACTIVE LEARNER
→ GRADE/CURRICULUM SCOPE
→ HOME ELIGIBLE CONTENT
→ RANKING
→ NEXT ACTION

Content ngoài grade scope không được bước vào Home candidate set.

==================================================
FOLLOW-UP — EMPTY HOME STATE
==================================================

Phát hiện profile Lớp 7 không có SAM-ready lesson
là một PRODUCT GAP hợp lệ, không phải lý do nới grade filter.

Không fake lesson.
Không cross-grade fallback.
Không fake progress.
Không biến sách thành lesson nếu chưa có capability tương ứng.

Mở bounded follow-up trong Round 7:

EMPTY / LOW-COVERAGE LEARNER HOME.

Mục tiêu:

Ngay cả khi learner chưa có SAM-ready lesson,
Home vẫn phải hữu ích và không có cảm giác app bị hỏng.

Ví dụ:

Chào Bi 👋
Lớp 7

HÔM NAY
[ các môn từ thời khóa biểu ]

SAM
"Chưa có bài học SAM chuẩn bị sẵn cho lớp của con."

[ Mở Giá sách ]

hoặc action phù hợp với capability thật hiện có.

Nếu có timetable:

ưu tiên hiển thị:
- môn hôm nay;
- thời khóa biểu;
- sách đúng lớp;
- Learning Map đúng lớp.

Không được nói:
"Không có gì để học."

Không cần biến follow-up này thành workstream lớn.

==================================================
QUAN TRỌNG
==================================================

Sau khi merge #121, quay lại mục tiêu Round 7:

PROFILE
+ TIMETABLE
+ MULTI-SUBJECT HOME
+ GOLDEN JOURNEY
+ UI/UX.

Đặc biệt kiểm tra:

Profile Lớp 5
Profile Lớp 6
Profile Lớp 7 / zero-SAM-ready lesson

để Home có 3 trạng thái:

A. Có nhiều learning threads
B. Có ít learning threads
C. Chưa có SAM-ready lesson

Thiết kế C thành empty state tử tế,
không phá fail-closed.

Tiếp tục UI/UX trên máy thật.

Báo Founder BEFORE / AFTER
của trạng thái C khi xong.
