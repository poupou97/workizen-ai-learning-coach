# ADR-010 — Education Safety Boundary + Defer-Extraction (WAL-110, P0-D)

**Trạng thái:** ACCEPTED · 2026-09-02 · Epic WAL-1/WAL-112 (P0-D)

## Bối cảnh

SAM đứng trên nền Workizen Hub (~70-80% infra slice P0 có sẵn). Câu hỏi không
phải «dùng lại được gì» mà «dùng lại QUA CÁI GÌ»: capability người-lớn
(chat generic, analytics, growth) chạm trẻ em là rủi ro cấu trúc, không phải
rủi ro cấu hình. Audit thật 31 capability nằm ở
`docs/design/HUB-TO-SAM-CAPABILITY-REUSE-MATRIX.md` (REUSE 6 / ADAPTER 13 /
EXTRACT 4 / POC 3 / REJECT 5).

## Quyết định

1. **MỘT ranh giới duy nhất, thi hành bằng code**:
   `WORKIZEN SHARED CAPABILITIES → EDUCATION SAFETY ADAPTER → SAM DOMAIN`.
   Hiện thân: `lib/core/platform/education_safety_policy.dart` — 31 capability
   → ALLOW/SANITIZE/AGE_GATED/PARENT_GATED/DISABLE; capability CHƯA audit ⇒
   **DISABLE (fail closed, có test)**. REJECT khoá cứng: chat-generic, ads,
   leaderboard, growth-mechanics, analytics, hub-learning-state (tránh 2 nguồn
   mastery).
2. **5 luật ≠ có chỗ enforce cụ thể** (không phải lời dặn):
   OCR ≠ LearningEvidence (EducationOcrAdapter, type-enforced + mutation) ·
   Chat ≠ Tutor (test cấm feature chat) · Provider ≠ pedagogical authority
   (realization_contract: cage + guard + ACT_OVER_RUNG) · Imported Document ≠
   curriculum truth (ContentLicense bắt buộc khai) · Analytics ≠ child
   telemetry (test quét pubspec cấm ad/analytics SDK — thêm dep là suite đỏ).
3. **DEFER-EXTRACTION có lý do** — không tách shared package khi chưa có
   consumer thứ hai:
   - OCR: extract XONG (adapter WAL-108, cùng version ML Kit với Hub).
   - design-tokens: SAM giữ `wal_tokens` riêng (đo contrast WAL-46); tách
     shared khi Hub refactor cần — tách sớm = maintenance surface không ai dùng.
   - QR / TTS·STT: adapter mở CÙNG feature cần nó (WAL-100 pairing, WAL-123
     voice) — **không viết stub chết**.
4. Pin Flutter SDK giữa 2 repo giữ nguyên như scope gốc.

## Hệ quả

- Mọi capability mới của Hub mặc nhiên KHÔNG chạm SAM cho tới khi được audit
  và phân loại — chi phí là một bước audit; đổi lại không có đường tắt nào
  đưa surface người-lớn tới trẻ.
- Extraction theo nhu-cầu-thật nghĩa là WAL-100/WAL-123 sẽ mang thêm việc
  adapter khi tới lượt — ghi ở ticket đó, không nợ ngầm.
- Ai đảo quyết định này phải sửa test (pubspec-scan, chat-ban, DISABLE-default)
  — tức là phải NHÌN THẤY mình đang đảo nó.
