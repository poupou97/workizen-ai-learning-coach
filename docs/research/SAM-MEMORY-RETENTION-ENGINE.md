# SAM-MEMORY-RETENTION-ENGINE — WS-D: quên, ôn, và Learning Agenda

**Ngày:** 2026-09-02 · WAL-99 · Bất biến §25.10/14/16 falsify tại chỗ.

## 1. Falsify «review scheduling = knowledge mastery» (§25.10) — GIỮ TÁCH, có bằng chứng

Thử gộp (memory strength LÀ mastery): FSRS retrievability giảm theo thời gian ⇒ nếu gộp,
pMastery tự tụt khi trẻ nghỉ hè ⇒ tháng 9 hệ nói «con quên quy đồng» KHÔNG CÓ bằng chứng mới
— vi phạm evidence-first (§25.8) và tạo claim sai cho phụ huynh. Chiều ngược (chỉ mastery,
không memory): bỏ lỡ đúng lúc cần ôn — F5 ghi nhận từ ADR-003. **Kết: hai đại lượng, hai
vòng đời**: mastery đổi KHI CÓ EVIDENCE; retrievability đổi THEO THỜI GIAN và chỉ lái LỊCH.
FSRS đúng vai «candidate cho scheduling» (§25.16) — OpenTutor minh hoạ đúng cách đặt:
fsrs fields TRÊN learning-progress, property-tests, không đụng knowledge model.

## 2. Nâng cấp lịch: SM-2-shape hiện tại → FSRS-style retrievability

Hiện tại: interval cố định ×2 cap 112d — không cá nhân hoá, không risk số. Đề xuất
(KHÔNG implement): thêm `forgettingRisk = f(stability, elapsed)` per-case, chỉ tiêu thụ bởi
Agenda; stability tăng theo lần ôn ĐỘC LẬP thành công (dùng lineage sẵn có — assisted không
tăng stability, cùng luật khen≠ghi-công). Property-tests kiểu OpenTutor làm chốt.

## 3. Learning Agenda Engine — «hôm nay học mới hay ôn?»

Pattern ADOPT từ OpenTutor: **signals → resolve_next_action (tín hiệu mạnh nhất) + dedup +
cooldown**; map vào WAL: decide() hiện tại đã là resolver một-concept; Agenda = tầng trên
gom NHIỀU nguồn tín hiệu:

| Input (order) | Nguồn WAL có sẵn |
|---|---|
| curriculum position | LearnerProfile.grade + LearningStage |
| mastery/prerequisite | ConceptSummary + caseBreakdown + cross-grade edges |
| recent mistakes | LearningSession projection (store đã có) |
| review due | ReviewSchedule (+ forgettingRisk tương lai) |
| timetable | prioritiseByTimetable — CHỈ xếp lại (§25.14 đã enforce bằng API, test giữ) |
| study time / fatigue | ❌ chưa có — fatigue proxy V1: số phút phiên + giờ trong ngày; KHÔNG đo sinh trắc |

Output đúng order: learn/practice/review/retrieve/explain/**stop-rest**. `stop-rest` là
output HẠNG NHẤT (OpenTutor: no-signals→submit; SAM: không tín hiệu đủ mạnh → «hôm nay đủ
rồi» — chống engagement-optimization, khớp §25.11).

## 4. Anti-goals
Không thành flashcard app (đơn vị = bài/ca trong curriculum, không phải thẻ) · không «streak
đóng băng» thao túng · lịch là GỢI Ý cho Mission, trẻ/phụ huynh ghi đè được — autonomy theo tuổi.
