# HUB → SAM CAPABILITY REUSE MATRIX (§27)

**Audit thật:** `workizen-ai-personal-wallet/mobile/app` — 42 feature modules, deps
xác nhận (ML Kit OCR, cunning_document_scanner, mobile_scanner QR, speech_to_text,
flutter_tts, drift, flutter_secure_storage, RevenueCat, Firebase, BYOK 81 files,
Ollama 10 files). Tổng audit: **31 capability**.

**Đếm quyết định: REUSE AS-IS 6 · REUSE+ADAPTER 13 · EXTRACT SHARED 4 · POC 3 · REJECT 5.**

| Hub capability | Impl thật | SAM use case | Chiến lược | Adapter bắt buộc |
|---|---|---|---|---|
| OCR (ML Kit + Vision) | `google_mlkit_text_recognition`, 64 files | Camera Tutor, TKB scan, worksheet | **REUSE + EDU-SAFETY ADAPTER** | Hypothesis→Confirm bắt buộc (F36: OCR≠evidence — SAM đã có ConfirmedProblem); Apple-Vision pipeline SAM giữ cho corpus build |
| Doc Scanner (edge-detect) | `cunning_document_scanner` | scan nhiều trang, đề kiểm tra | REUSE AS-IS | — |
| Camera capture | feature `camera` | acquisition | REUSE + pre-capture guidance SAM (WAL-65) | activeLearner bind §26.7 |
| QR/Barcode | `mobile_scanner`, `qr_flutter`, feature `qr` | device pairing (WAL-100!), class join, mở bài | **REUSE AS-IS engine** + QRInvitation policy SAM (purpose/nonce/expiry) | SCAN≠AUTHORIZATION |
| STT | `speech_to_text` + `record` (ghi dài) | voice hỏi, oral practice, chính tả nghe-viết | REUSE + CHILD VOICE POLICY | child speech accuracy đo trước; không gửi audio cloud mặc định |
| TTS (My Voice, on-device) | `flutter_tts` MYVOICE-002 | SAM đọc — age-aware, không đọc đoạn dài tự động | **REUSE AS-IS** (on-device ✓ privacy) | speech-rate theo band |
| AI Router + Gateway | features `ai_router`, `ai_gateway` (free/BYOK/Ollama) | generative realization (WAL-30 shadow) | **EXTRACT SHARED + PEDAGOGICAL POLICY** | routing thêm TASK×SAFETY×PRIVACY; fallback KHÔNG đổi constraint (F35: router không quyết pedagogy — cage+guard SAM bọc ngoài) |
| AI Usage/quota | feature `usage` | parent xem usage; trẻ thấy «SAM sẵn sàng» | REUSE + EDU UX | không show token cho trẻ (F40); core learning không khoá vì hết quota (local fallback) |
| Chat/Assistant | features `chat`, `assistant`, `docchat` | — | **REJECT trực tiếp** (F34) | tutor = TutorSession+prompt-cage+guard, không phải chat generic |
| Smart Canvas | feature `canvas` (**11 files, không phải 39** — sửa 2026-09-04 §WAL-185 audit) | Founder mô tả ban đầu (map-annotate/mindmap) **SAI** — thực tế là "Canvas Conversation": nét bút → phân loại ý định bằng vision-LLM (question/spelling/math/diagram/pseudocode), `canvas_conversation_screen.dart`. Không liên quan visual representation | **NOT SUITABLE** cho Learning Visualizer (object-model gắn thẳng `drift` conversation schema của Hub, không tách được) | — |
| Output Engine (summary/infographic/email/mindmap/mermaid/executive_report) | `lib/features/output/` — **52 files, không phải "smart_tools 17 files"** (sửa 2026-09-04 §WAL-185 audit; `smart_tools/` thật là registry gọi-hàm chat: calendar/checklist/email/maps — không liên quan) | tóm tắt bài, sơ đồ tư duy | **REUSE PATTERN, KHÔNG reuse renderer nguyên khối** — xem WAL-185 research note | model `MindmapBody{root,branches}`/`MindNode{label,children,cite}` ĐÃ typed (tốt); nhưng renderer là 1 widget/kind qua `Map<OutputKind,WidgetBuilder>`, KHÔNG có graph-layout chung (mindmap chỉ là Column/Row thụt lề, không phải radial/force-directed dù doc-comment nói vậy) — thêm "Timeline" cần thêm kind+generator+widget mới hoàn toàn, không "cắm vào" renderer có sẵn được. Citation chip (`CiteChip`, `OutputCitation{docId,page,timeMs}`) là pattern ĐÁNG học — chỉ parse từ page-marker đã xác minh, không đoán từ chữ LLM. ~60-70% (spec/body/render model, cố ý không import Flutter/Riverpod) portable; ~30-40% (BM25 retrieval, Riverpod, drift) là Hub-specific, KHÔNG mang sang |
| Document ingestion/PDF | `ingestion`, `pdf`, `docchat` | learner upload phiếu/tài liệu | REUSE + SOURCE-CLASS LABEL | imported ≠ curriculum (F: 5 nhãn nguồn Library) |
| Library | feature `library`, `vault` | Library 5 khu A-E | REUSE ARCHITECTURE, TÁCH ngữ nghĩa (F37) | SAM Knowledge ≠ user files |
| Auth (AppAuth/Google) | `auth`, `flutter_appauth` | parent account optional | REUSE + FAMILY MODEL | account≠learner (F39: model Hub 1-user KHÔNG đủ — thêm LearnerProfile layer local) |
| Backup/restore | 37 files | per-learner state backup | REUSE + SCOPE REDESIGN (F38 audit) | restore không merge learner A/B; version metadata bắt buộc |
| Local DB (drift) | `drift` | SAM đang JSONL — pack SQLite | GIỮ SONG SONG | JSONL evidence (append-only) + sqlite pack đã benchmark |
| Secure storage | `flutter_secure_storage` | Parent PIN, keys | REUSE AS-IS | — |
| Subscription (RevenueCat) | `subscription` | family premium | REUSE AS-IS (P3) | gắn family, không gắn learner |
| Notifications infra | (foreground_task, calendar) | nhắc học | REUSE + LEARNING-ONLY POLICY | không streak-spam |
| Permissions/device abstraction | `permission_handler`, device_info | như Hub | REUSE AS-IS | — |
| Localization/l10n | core/l10n | VI trước | REUSE pattern | — |
| Theme/design tokens | core/theme + AI-first DNA | design system SAM | **EXTRACT SHARED primitives** | semantics màn hình KHÔNG copy (§27.14) |
| Mascot | feature `mascot` | SAM cú tím-vàng | REUSE pattern + asset SAM riêng | age-band prominence |
| Analytics/Firebase | `firebase_core`, `metrics` | ops telemetry | REUSE + CHILD PRIVACY PASS (F42) | không track hành vi trẻ như user thường; tối thiểu hoá + parent consent |
| Deep links/routing | core/navigation | mở bài/QR | REUSE | — |
| Voice UI | `my_voice`, core/voice | SAM Voice surface | REUSE + cage/guard | không bypass TutorScope (F21) |
| Ollama/local AI | 10 files | local fallback cho classification/routing rẻ | POC | đo chất lượng VN trước |
| Leaderboard/Arcade/Growth/Ads | features tương ứng | — | **REJECT** | phản triết lý (so sánh xã hội/engagement/quảng cáo với trẻ) |
| Academy/Journey/Learning_state (Hub) | features cũ | — | REJECT (SAM có student model riêng đã falsify sâu hơn) | tránh 2 nguồn «mastery» |
| Wallet/Portal/TV/News | — | — | REJECT ngoài scope | — |
| Capability explorer | `capability_explorer` | dev tool | REUSE dev-only | — |

## Kiến trúc shared platform (§27.18) — khuyến nghị

**Phương án A (shared Dart packages) cho 4 EXTRACT** (ocr_kit, ai_router, design_tokens,
qr_kit): coupling thấp, release độc lập, API nhỏ. KHÔNG monorepo-hoá vội; KHÔNG để SAM
chờ Hub refactor — bước 1 pragmatic: SAM depend trực tiếp package path-local, Hub
migrate sau (§27.21 «không block SAM vô hạn»). Child-safety isolation: mọi capability
vào SAM qua MỘT lớp `education_safety_adapter` (ALLOW/AGE-GATED/PARENT-GATED/SANITIZE/
DISABLE per capability — bảng trên là input).

## Ước lượng giảm trùng lặp

Slice P0 cần camera+OCR+QR+TTS/STT+storage+auth-optional: **~70-80% infra có sẵn từ
Hub** — SAM chỉ viết adapter giáo dục + surfaces. Rủi ro chính: version drift Flutter
SDK giữa 2 repo (Hub 3.12 vs SAM 3.13-dev) — pin khi extract.
