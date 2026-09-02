# SOCRATIC-TUTOR-AUDIT — lớp «Socratic tutor» OSS (đại diện: codernoahx/socratiq-ai)

**Verify canonical:** «Socratic Tutor / ai-tutoring» KHÔNG trỏ về một repo canonical nào —
landscape là các prompt collection (mustvlad/ChatGPT-System-Prompts, topics/socratic…).
Audit đại diện: **socratiq-ai** SHA 90333ec · 2025-08-23 · **KHÔNG LICENSE**.
**Chạy được?** `DOCS ONLY` giá trị — Streamlit + Gemini key.

## Claim vs code

| Claimed | Evidence in code | Tests | Works? | SAM relevance |
|---|---|---|---|---|
| «Socratic method of teaching» | `app.py` **10 dòng**; `pages/chat.py` 100 dòng: đọc `model_instructions` từ FILE TEXT → `system_instruction` → gọi model. Toàn bộ «sư phạm» = 1 system prompt | 0 test | chạy như chatbot | trả lời câu order DỨT KHOÁT |
| state handling | `st.session_state` lưu history chat — không student model, không mastery, không diagnosis | 0 | — | — |

## Kết luận — trả lời «real pedagogy architecture hay prompt engineering?»
**Prompt engineering — CONFIRMED bằng code.** Không student model, không strategy selector,
không eval, không provenance. Đây chính là «pedagogy theater» mà critical review phải cảnh báo:
một system prompt tử tế TRÔNG như dạy học trong demo, nhưng không biết học sinh là ai, không
nhớ gì có bằng chứng, không đo được. **`REJECT`** làm kiến trúc; `REFERENCE` duy nhất: đọc
các prompt này để xây NEGATIVE test cho eval (SAM phải hơn mức này một cách ĐO ĐƯỢC).
