# OATUTOR-AUDIT — CAHLR/OATutor

**SHA:** 6de5ada3 · last commit 2026-08-28 · LICENSE: có (đọc header bên dưới) · JS/React
**Chạy được?** `NOT WORTH RUNNING` cho mục đích này — là web app CRA; giá trị nằm ở việc ĐỌC model, đã đọc.

## Claim vs code

| Claimed | Evidence in code | Tests | Works? | SAM relevance |
|---|---|---|---|---|
| BKT mastery tracking | `src/models/BKT/BKT-brain.js` — **14 dòng**, update 2 nhánh đúng/sai + transit, pure function `update(model, isCorrect)` | chỉ **1** file `*.test.js` toàn repo — BKT KHÔNG có test riêng | có (toán học đúng chuẩn BKT cổ điển) | CAO — đối chiếu: WAL đã có BKT giàu hơn (likelihood-pair, support-aware, replay) |
| Adaptive problem selection | `Platform.js:634 _nextProblem` → `context.heuristic(problems, completedProbs)` — heuristic INJECTABLE, có `defaultHeuristic`/`experimentalHeuristic` swap theo treatment (A/B) | không | có, dạng đơn giản | TRUNG — pattern «heuristic tách rời + A/B treatment» đáng học |
| Mastery threshold | `config.js:113 MASTERY_THRESHOLD = 0.85` | không | có | trùng đúng 0.85 của WAL (đã cite từ trước) |
| Evaluation | không có harness; logs/ + aws lambda hint-generation | 1 test file | KHÔNG như claim | thấp |

## Kết luận
- **`ADOPT PATTERN`**: (1) BKT update là PURE FUNCTION tách khỏi UI — WAL đã làm đúng hướng này, xác nhận; (2) **heuristic chọn bài injectable + treatment map** — đúng khuôn cho thí nghiệm ±1 vs never-help sau này trên trẻ thật (WAL-49); (3) threshold trong config có tên.
- KHÔNG adopt: content model gắn chặt CRA/Firebase; không forgetting; không per-case semantics.
- Trả lời câu hỏi order: phần reusable = BKT-brain + heuristic seam (~50 dòng ý tưởng); phần còn lại tightly coupled.
