FOUNDER TASK — VISUAL FIDELITY: MÀU SẮC + FONT + DESIGN TOKENS (mục 8)

Kiểm VISUAL FIDELITY giữa: CONCEPT ĐÃ DUYỆT vs DESIGN SYSTEM HIỆN TẠI vs APP
TRÊN NOKIA. Không chỉ kiểm component — kiểm xem app có còn mang visual language
của concept hay đã lệch dần trong quá trình implement.

8.1 Audit màu từ concept (primary/secondary/accent/background/surface/text/
    border/disabled/success/warning/error/SAM accent/subject/progress/timetable).
    Đặc biệt: PURPLE hiện tại có đúng purple concept không? Kiểm HEX/ARGB,
    opacity, gradient, surface tint, border tint.
8.2 KHÔNG ĐOÁN MÀU BẰNG MẮT. Lấy giá trị thực từ concept. Báo dạng
    CONCEPT → CURRENT TOKEN → CURRENT APP → MATCH/DIFFERENT.
    Không đủ bằng chứng ⇒ ghi UNRESOLVED, không tự phát minh màu.
8.3 Audit typography (family/weight/size/line-height/letter-spacing/hierarchy).
8.4 Font family phải được XÁC MINH, không suy từ hình dáng. Kiểm design source,
    docs, assets, theme, pubspec, font files. Concept dùng font X mà app fallback
    system font ⇒ DESIGN GAP. Kiểm tiếng Việt: ă â ê ô ơ ư đ + 5 dấu.
8.5 Typography hierarchy phải giống concept. Không để mọi thứ BOLD/UPPERCASE/PURPLE.
8.6 Kiểm hard-coded style trong learner-facing screens; đưa về Design Token khi hợp lý.
8.7 Audit shape/spacing: radius, border width, shadow, spacing, icon/mascot size.
8.8 Đối chiếu Home Nokia với concept. Home hiện nhiều PURPLE + BORDER + CARD —
    kiểm xem đó là design language của concept hay do implementation tích luỹ.
8.9 Timetable phải cùng Design Language, không như module ghép vào.
8.10 Subject colors: concept có quy định không? Nếu có phải nhất quán mọi màn.
8.11 VISUAL TOKEN GAP REPORT ngắn: TOKEN/ELEMENT · CONCEPT · CURRENT · VERDICT · ACTION.
8.12 BEFORE/AFTER trên Nokia cùng framing: Home, Timetable, Profile, Lesson Workspace.
8.13 Pipeline: CONCEPT → DESIGN INTENT → DESIGN TOKENS → IMPLEMENTATION → REAL DEVICE.
     Concept khác implementation ⇒ xác định nguyên nhân. Founder đã supersede thì
     ghi rõ; chưa supersede thì ƯU TIÊN BÁM CONCEPT.

FOUNDER VISUAL ACCEPTANCE (kiểm bằng mắt trên Nokia):
1. Màu có giống concept? 2. Font/weight/size có giống tinh thần concept?
3. Home và Timetable cùng Design System? 4. Card/radius/spacing nhất quán?
5. Còn cảm giác nhiều card tím/viền tím do implementation tự phát sinh?
6. Nhìn concept và app có nhận ra cùng một sản phẩm?

Logic đúng nhưng visual lệch ⇒ IMPLEMENTED BUT DESIGN GAP REMAINS. Không gọi UI DONE.
Không mở research UI/UX mới. Tiếp tục PR #123. KHÔNG MERGE. READY FOR FOUNDER REVIEW.
