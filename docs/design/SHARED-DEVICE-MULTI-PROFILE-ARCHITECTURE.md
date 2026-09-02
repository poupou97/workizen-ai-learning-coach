# SHARED DEVICE / MULTI-PROFILE ARCHITECTURE (§26)

## 1. Model

```
Family/Household
 ├─ ParentGuardian (authn optional lúc đầu — local-first §26.10 phương án B→A)
 ├─ LearnerProfile A/B/C   (độc lập: grade, timetable, state, evidence, sessions)
 └─ Device: KHÔNG mang identity — chỉ giữ ACTIVE_PROFILE pointer
```

Bất biến: `DEVICE ≠ USER · ACCOUNT ≠ LEARNER · PARENT ≠ LEARNER ·
ACTIVE PROFILE quyết định toàn bộ learning context.`

## 2. Data ownership matrix

| Phạm vi | Dữ liệu |
|---|---|
| SHARED (immutable) | Knowledge Pack (sam-units.db), Curriculum/Content Graph, Method/SkillCase defs, source metadata, static assets |
| PER FAMILY | consent, subscription, family settings, notification policy, parental controls, Parent PIN |
| PER PARENT | parent prefs, projection views |
| PER LEARNER | LearnerProfile, StudentKnowledgeState, LearningEvidence, LearningSession, transcript, Timetable, ReviewSchedule, Recommendation cache, preferences |
| PER SESSION | InteractionEvents, EvidencePack refs, versions (policy/knowledgeModel) |

Store hiện tại đã thuận: JSONL per-learner (learnerId trong mọi event ✓ —
LearningSession.learnerId bắt buộc từ WAL-95). Pack dùng CHUNG một file —
đã benchmark trên S24, không nhân bản per-learner (§26.9 thoả).

## 3. Isolation — luật + test bắt buộc

- **Evidence:** mọi LearningEvent/Session mang learnerId; recordSession từ chối
  khi activeLearner không xác định (FAIL CLOSED — §26.7). 
- **Falsification test (đưa vào suite):** A học → switch B → B học → switch A ⇒
  state A y hệt (chỉ khác shared content update). 
- **Conversation:** transcript scope theo activeLearnerId; parent xem SUMMARY
  (Parent Projection claim-gated), không merge memory, không đọc mặc định
  toàn bộ chat (§26.15).
- **Camera/Voice:** header phiên hiển thị «SAM đang học cùng Minh Anh — Lớp 4»;
  assessment thêm bước xác nhận profile (§26.8) — correct attribution > surveillance.

## 4. Switcher UX

- Home header `Tên · Lớp ▾` → sheet «Ai đang học?» (avatar lớn, 2-3 chạm, không
  logout). Age-aware: 1-2 avatar to + mascot; 6-12 compact; Parent tile riêng + PIN.
- Switch = load lại LearnerContext + RECOMPUTE agenda (không giữ recommendation cũ
  — §26.12); resolveAgenda thuần + nhanh nên recompute rẻ.

## 5. Account optionality (§26.10)

V1: local-only family (install → tạo bé → chọn lớp → học). Account/cloud-sync là
lớp SAU, tách khỏi core learning; subscription gắn family không gắn learner.

## 6. Falsifications trả lời (F23-F32)

F23 device=learner? **NO** (model trên) · F24 mỗi trẻ 1 account? **NO — local
profiles đủ V1** · F25 nhân bản pack? **NO — đo rồi, shared 1 file** · F26 switch
cosmetic? **NO — swap toàn context + recompute agenda** · F27 parent/learner chung
nav? **NO — 2 mode** · F28 sibling ranking? **REMOVE (concept 34 «So sánh nhanh»
bị thay)** · F29 chat share giữa profile? **NO** · F30 evidence khi learner mù mờ?
**NO — fail closed** · F31 re-login mỗi lần đổi con? **NO (PIN chỉ cho Parent
Mode)** · F32 local-first tốt hơn cho shared-device? **CÓ CƠ SỞ ĐO: pack chung
1.87MB-105MB chạy tốt trên 1 máy; cloud-only sẽ nhân chi phí theo con — vẫn ghi
là evidence-based-lean, không tuyệt đối.**
