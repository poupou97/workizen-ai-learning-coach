# OPENTUTOR-AUDIT — zijinz456/OpenTutor

**SHA:** 7dffe36 · last commit 2026-09-01 (RẤT active) · LICENSE: có · Python FastAPI + web
**Chạy được?** `PARTIAL` — API+DB stack; phần giá trị (FSRS/agenda) đọc được từ code+tests.

## Claim vs code

| Claimed | Evidence in code | Tests | Works? | SAM relevance |
|---|---|---|---|---|
| FSRS spaced repetition | migration `…_fsrs_fields_on_learning_progress.py`; `routers/flashcards.py`, `progress_knowledge.py` | ⭐ `test_fsrs_bkt_properties.py` — **property-based**: stability>0, difficulty bounded, retrievability∈[0,1], giảm theo thời gian, rating cao→stability cao | CÓ, nghiêm túc | RẤT CAO |
| Forgetting forecast | `test_forgetting_forecast.py`: zero-elapsed→1, large-elapsed→thấp, bounded | có | có | CAO — đúng «forgettingRisk» mà WAL đang MISSING |
| ⭐ Agenda engine | `services/agent/agenda.py`: `resolve_next_action`, `run_agenda_tick`; models `AgendaRun/AgentTask/StudyGoal`; router `agenda.py` «observe and trigger the agent's decision loop» | `test_agenda_tick.py`: no-signals→submit, **picks highest signal**, dedup window, cooldown | có | RẤT CAO — đây là «Learning Agenda Engine» WS-D bằng xương thịt |
| Adaptive learning workspace | block-based UI apps/web | e2e ít | một phần | thấp (flashcard-centric) |

## Kết luận
**`ADOPT PATTERN`:**
1. **Property-based tests cho công thức trí nhớ** — đúng phong cách chốt-đột-biến của WAL; nếu WAL thêm retrievability thì test kiểu này, không golden-số.
2. **Agenda = signals → resolve_next_action (chọn tín hiệu mạnh nhất) + dedup + cooldown** — map thẳng vào decide() mở rộng: review-due/weak-case/new-lesson là signals; «không tín hiệu → nghỉ» = đúng output `stop/rest` order muốn.
3. FSRS fields nằm TRÊN learning-progress (không thay mastery) — khớp quyết định F5 tách của Founder.

KHÔNG adopt: flashcard làm đơn vị học (SAM là tutor theo bài/ca, không phải Anki — đúng cảnh báo order).
