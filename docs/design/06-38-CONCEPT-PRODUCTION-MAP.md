# 06 — 38-CONCEPT → PRODUCTION MAP (SOURCE OF TRUTH)

> Founder Task Order 2026-09-02 #3 §19. Verdict kế thừa 03-REAUDIT (corpus-grounded, snapshot
> e47277a); Reuse từ HUB-TO-SAM matrix + code ĐÃ CHẠY S24. Jira: Epic **WAL-134**; milestone
> đầu queue **WAL-135 «SAM FIRST REAL LEARNING EXPERIENCE»**. Cập nhật bảng này khi verdict đổi.
> Data: R=READY · RE=READY_WITH_ENRICHMENT (WAL-133) · B=BLOCKED.

| ID | Concept | Type | Verdict | Production target | Reuse | Data | Pri | Jira | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 01 | Onboarding | SCREEN | KEEP | Onboarding 2 câu (đã chạy) | v1 WAL-95 ✓ | R | P1 | WAL-137 | polish wording |
| 02 | Learner Profile | SCREEN | MODIFY | Profile view/edit tối giản | LearnerProfile.withGrade | R | P1 | WAL-137 | grade≠mastery test giữ |
| 03 | Subject Setup | SCREEN | MODIFY | Subjects grid SINH TỪ registry | registry 31 môn/lớp | R | P0 | WAL-136 | không hardcode |
| 04 | Timetable | SCREEN | MODIFY | Nhập tay tối giản | store WAL-96 | R | P1 | WAL-137 | bỏ auto-gợi-ý (F4) |
| 05 | Home | SCREEN | MERGE→home1 | Home 5 intent chips | MissionCenter v1 ✓ | R | P0 | WAL-138 | engine truths giữ |
| 06 | Subjects | SCREEN | MODIFY | Subjects theo grade | tokens+tiles | R | P0 | WAL-136 | bỏ % |
| 07 | Subject Home | SCREEN | KEEP-MODIFY | Lesson list + Ví dụ mẫu | curriculum-structure | R | P0 | WAL-136 | tên bài thật |
| 08 | Camera | SCREEN | KEEP | CaptureScreen (đã chạy S24) | WAL-108 ✓ + assessFrame | R | P1 | WAL-140 | +artifact-capture ▲ |
| 09 | Camera Confirm | SCREEN | KEEP | ConfirmProblem (đã chạy S24) | WAL-52/64 ✓ | R | P1 | WAL-140 | ranh giới giữ nguyên |
| 10 | Tutor Start | STATE | MODIFY | Workspace state:start | TutorScreen ✓ | R | P0 | WAL-139 | provenance chip có sẵn |
| 11 | Diagnostic | STATE | REPLACE | state:diagnostic từ decide/ErrorHypothesis | WAL-24/27 | R | P0 | WAL-139 | không bịa chẩn đoán |
| 12 | Problem Workspace | SURFACE | KEEP-MODIFY+ | Learning Workspace | TutorSession ✓ | R | P0 | WAL-139 | drawing mode chờ WAL-116 |
| 13 | Hint | STATE | MODIFY | state:hint (ladder ±1) | hintTextFor ✓ | R | P0 | WAL-139 | interventionId ✓ |
| 14 | Your Turn | STATE | KEEP | state:your-turn | stepBack act | R | P0 | WAL-139 | — |
| 15 | Success | STATE | MODIFY | state:success 4-chiều | feedbackFor ✓ | R | P0 | WAL-139 | khen≠ghi công |
| 16 | Why This Method | DRILL-DOWN | KEEP khung | Provenance drill-down | explainTeaching ✓ | R | P1 | WAL-141 | 29 methods thật |
| 17 | Source | DRILL-DOWN | REPLACE | Source ref + page (local crop RE) | sourceLineForChild ✓ | RE | P1 | WAL-141 | SOURCE_ASSET WAL-133 |
| 18 | Review | STATE/khu | REPLACE | Khu Ôn lại (Home) + flow | reviewStateOf ✓ | R | P1 | WAL-142 | dịu, không đỏ |
| 19 | Learning Map | SCREEN | MODIFY | Map bài theo môn + claim | 7.626 lessons | R | P1 | WAL-142 | honest per-lesson |
| 20 | Quiz | SURFACE | KEEP-MODIFY | QuizSelect band 1-3 | WAL-97 ✓ | R | P1 | WAL-143 | items từ corpus |
| 21 | Assessment | MODE | SPLIT | Assessment policy trên cùng engine | WAL-104/122 | R | P1 | WAL-143 | profile confirm |
| 22 | Result | SCREEN | MODIFY | Result honest + remediation-sau | 4-chiều | R | P1 | WAL-143 | không điểm hoá bừa |
| 23 | Vietnamese | SURFACE | KEEP | Reader nâng theo blueprint TV | WAL-98 ✓ + bp tv3 | R | P1 | WAL-144 | đồng WAL-113 |
| 24 | Essay | SURFACE | MODIFY+ | Compose 7 bước, không viết hộ | Compose-lite ✓ | R | P1 | WAL-144 | ▲ P1 |
| 25 | Physics | SURFACE | KEEP-MODIFY | Science surface (10-12) | bp khoa4 pattern | RE | P1 | WAL-144 | 6-9 = KHTN |
| 26 | Chemistry | SURFACE | KEEP-MODIFY | Science surface | như trên | RE | P1 | WAL-144 | — |
| 27 | History | SURFACE | MODIFY | SourceReader/Evidence | bp su10 (không reveal) | RE | P1 | WAL-144 | SOURCE_TEXT 54 thật |
| 28 | Geography | SURFACE | KEEP-MODIFY | Map/Chart surface | drawing WAL-116 | RE | P1 | WAL-144 | — |
| 29 | AI Learning | REFERENCE | REPLACE→DEFER | Học-về-AI theo QĐ2422 | WAL-89-93 | B(design) | P2 | WAL-146 | KHÔNG generic chat |
| 30 | History Sessions | DRILL-DOWN | KEEP-MODIFY | Sessions theo ngày/môn | store.sessions ✓ | R | P1 | WAL-142 | projection §5-6 |
| 31 | Progress | SCREEN | REPLACE | Edu metrics (không XP/streak) | ConceptSummary ✓ | R | P1 | WAL-142 | §16 order |
| 32 | Parent Home | SCREEN | MODIFY | Parent overview + 1 khuyến nghị/con | WAL-109 ✓ | R | P1 | WAL-145 | «cần giúp gì?» |
| 33 | Parent Detail | SCREEN | MODIFY | Drill-down claim-gated + citations | explainConcept ✓ | R | P1 | WAL-145 | không spy chat |
| 34 | Multi-child | SCREEN | MODIFY | Family Manager (không ranking) | switcher+PIN ✓ | R | P1 | WAL-145 | §26 giữ |
| 35 | SAM Voice | SURFACE | MODIFY+ | Voice sau EN adapter | Hub STT/TTS + WAL-123 | B(WAL-117) | P2 | WAL-146 | interventionKind sẵn |
| 36 | Library | SCREEN | REPLACE | 5 khu, nhãn nguồn | Hub Library + NOTE 782 | RE | P2 | WAL-146 | sponsored≠rec |
| 37 | Notifications | COMPONENT | MODIFY | Learning-only notif | Hub infra SANITIZE | R | P2 | WAL-146 | không streak-spam |
| 38 | Settings | SCREEN | MODIFY | Settings + consent parent-gated | Hub pattern | R | P2 | WAL-146 | BYOK parent |

**Đếm:** 38/38 có owner. Milestone WAL-135 = #05+#06+#07 (mới) + #08-17 (đã chạy S24). Không orphan.
