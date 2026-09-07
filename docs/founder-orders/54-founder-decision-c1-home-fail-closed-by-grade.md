FOUNDER DECISION — C-1

Chốt C-1:

HOME PHẢI FAIL-CLOSED THEO LEARNER PROFILE.

Với profile hiện tại:

Home chỉ được hiển thị learning content thuộc grade/curriculum scope của learner đó.

Ví dụ:
- Na — Lớp 6 → Home không hiển thị bài Lớp 5.
- Minh — Lớp 5 → Home không hiển thị bài Lớp 6.

Không dùng cách:
"vẫn hiện bài khác lớp + gắn nhãn không phải sách lớp con".

Bài ngoài lớp vẫn có thể tồn tại trong:
- Library / Learning Map
- Search
- chế độ khám phá chủ động trong tương lai

nhưng KHÔNG được tham gia mặc định vào:

Home
Smart Learning Cards
Continue Learning
Next Action
Recommended Lesson
Timetable recommendation.

Nguyên tắc:

ACTIVE LEARNER
→ Grade
→ Subjects
→ Books/Curriculum Scope
→ Eligible Home Content
→ Recommendation / Next Action.

Grade filtering phải xảy ra TRƯỚC ranking/recommendation,
không phải ranking xong rồi mới gắn nhãn cảnh báo.

Bổ sung regression tests tối thiểu:

1. Lớp 5 không nhận Home card Lớp 6.
2. Lớp 6 không nhận Home card Lớp 5.
3. Continue Learning không cross-grade.
4. Next Action không cross-grade.
5. Switch profile làm Home recompute theo learner mới.
6. Không reuse WorkspaceTrace/session state của learner trước.
7. Timetable chỉ tạo recommendation từ grade/books của learner hiện tại.

Sau khi sửa:
- flutter analyze
- full tests
- test Na Lớp 6 ↔ Minh Lớp 5 trên Nokia nếu thiết bị sẵn sàng
- screenshot Home của cả hai profile.

Nếu xanh:
tạo PR và báo READY FOR FOUNDER REVIEW.
KHÔNG tự merge nếu chưa có lệnh merge mới.
