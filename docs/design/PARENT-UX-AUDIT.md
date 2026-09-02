# PARENT UX AUDIT (32/33/34/37 + §26)

**Câu hỏi Bắc-đẩu của Parent Home: «Tối nay tôi nên giúp con điều gì?»** — concept 32
đã có mầm đúng (AI Insights + gợi ý); dọn phần giám sát/so sánh.

BỎ (với lý do): % cạnh avatar từng con (sibling ranking ngầm) · «Điểm TB 86%» (false
precision — thay claim-gated: «Vững các dạng đã gặp của quy đồng; còn 2 dạng chưa
thử») · «Xếp hạng lớp 3/28» (dữ liệu không tồn tại + phản triết lý) · achievements
Top-% · khối «So sánh nhanh» của 34 → «Tình hình các con» per-child.

GIỮ/NÂNG: Tối-nay-action (1 việc, 10 phút, từ Agenda + Parent Coach «ĐỪNG làm» —
10 flows đã research WAL-99) · «Cần bạn lưu ý» ✓ · lịch các con ✓ · thành tích CHUNG
gia đình ✓ (hợp tác) · Family Manager (§26.13): thêm/sửa/chuyển mode/consent/offline
data · Notifications: chỉ learning-important, policy theo con · Privacy: parent thấy
INSIGHT không thấy transcript mặc định (§26.15); Parent Detail tabs: Tổng quan
(3-trục) / Bằng chứng (independent vs assisted) / Lịch / Cài đặt con.

Teacher-comment block (33): DEFER — cần TeacherAssignment/authz (WAL-100 staged).
F12 (càng nhiều số càng tốt): NO — mỗi số phải trả lời được «giúp gì tối nay». 
F13 sibling comparison: REMOVE.

## WAL-119 (2026-09-02) — VALUE MATRIX Premium (INSIGHT/COACHING/CONVENIENCE)

Resolver: lib/core/platform/entitlement.dart (entitlement-v1) — ROLE×PIN×TIER,
một chỗ quyết, không rải `if premium`. BASIC = quyền (consent/privacy/safety/
export-delete/basic-status) FREE vô điều kiện.

| Candidate | Loại | Data requirement (đã có?) |
|---|---|---|
| Daily Brief | INSIGHT | LearningSession/ngày (✓ JSONL) + tóm tắt tất định |
| Weekly Insight | INSIGHT | sessions 7 ngày (✓) + trend |
| Independent-vs-assisted | INSIGHT | support/interventionId (✓ WAL-114 lineage) |
| Weakest SkillCase | INSIGHT | ConceptSummary.unobserved/weak (✓) |
| Assessment insight | INSIGHT | SessionMode.assess (✓) — cần WAL-122 mode chạy |
| Multi-week trend | INSIGHT | sessions nhiều tuần (✓ cấu trúc, cần thời gian thật) |
| «Tối nay giúp con gì» | COACHING | parentTonightFor (✓ WAL-53) |
| Parent Coach | COACHING | claim-gated summary (✓ WAL-35) + 10 flows ĐỪNG-làm |
| Review plan | COACHING | ReviewSchedule (✓) |
| Proactive recommendation | COACHING | resolveAgenda (✓) |
| Multi-child overview | CONVENIENCE | multi-profile (✓ WAL-109) |
| Cloud backup/sync | CONVENIENCE | CHƯA có — cần backend (gate spend) |
| Ad-free family | CONVENIENCE | phụ thuộc quyết định ads (WAL-125 gate) |

NEVER-MONETIZE (enforce bằng code — hỏi là ném lỗi): hint · answer ·
assessment · mastery · evidence · child-data · streak · dependence-mechanics.
PAYMENT ≠ LEARNING TRUTH: test quét cấm 'subscription/premium/tier' trong
lib/core/{student,adaptive,curriculum,tutor,pedagogy}.
