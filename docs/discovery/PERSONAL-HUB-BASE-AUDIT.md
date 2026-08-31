# Audit AI Personal Hub — tìm phần dùng lại được cho AI Learning Coach

**Ngày:** 2026-08-31 · **Nguồn:** `workizen-ai-personal-wallet` @ `e060e0b`
**Phương pháp:** đọc mã sống, không tin tài liệu cũ. Mọi con số đo bằng công cụ.

> ⚠️ Ba "rủi ro lịch sử" trong work order đã kiểm lại. **Hai trong ba không còn
> đúng như mô tả.** Chi tiết ở §6.

---

## 1. Kiến trúc repo hiện tại

| | |
|---|---|
| Dart package | `wallet` · appId `ai.workizen.wallet` (Android + iOS) |
| Phiên bản | `1.3.2+99` · Dart SDK `^3.12.2` |
| Phụ thuộc | **65** dependencies + 12 dev |
| Mã | **126.204 dòng** Dart — `features/` 96.221 · `data/` 23.352 · `core/` 6.631 |
| Test | **2.493**, analyze sạch |

Ba tầng rõ: `core/` (hạ tầng không biết gì về sản phẩm) · `data/` (Drift + repository)
· `features/` (sản phẩm). Ranh giới này **giữ được** khi tách.

---

## 2. REUSE — lấy gần như nguyên trạng

| Module | Dòng | Vì sao |
|---|---|---|
| `core/theme` | 914 | design tokens + WzScaffold; đổi palette là xong |
| `core/l10n` | 437 | khung i18n; Learning Coach chỉ cần vi (+en) |
| `core/navigation` | 1.005 | app shell, `rootNavigatorKey`, edge-swipe-back, back handler |
| `core/responsive` | 281 | breakpoints |
| `core/widgets` | 1.043 | primitives dùng chung |
| `core/flags` | 1.091 | ⭐ **fail-closed đã đúng** — xem §6② |
| `core/audit` | 62 | `GateAudit`/`QuotaAudit` — nền cho *AI auditability* mà §F đòi |
| `data/services/ocr_processor.dart` | — | ML Kit OCR, **cốt lõi Camera Tutor** |
| `features/ingestion/chunk_retriever.dart` | — | ⭐ BM25 **thuần Dart, tất định** — xem §6③ |
| `features/metrics` | 2.033 | event catalog + on-device metrics |

## 3. REUSE_WITH_REFACTOR

| Module | Dòng | Phải sửa gì |
|---|---|---|
| `features/ingestion` | 3.303 | bỏ phần gắn với Thư viện Hub; giữ pipeline PDF→page→chunk |
| `features/ai_gateway` | 2.872 | ⭐ **đây mới là provider abstraction thật** (không phải `ai_router`) |
| `features/chat` | 3.948 | dùng **dưới hood** cho Tutor Session; KHÔNG làm bề mặt chính |
| `features/auth` | 1.966 | Keycloak; mô hình **parent↔child** chưa có, phải thiết kế mới |
| `features/settings` | 1.554 | giữ khung, thay nội dung |
| `data/` | 23.352 | giữ khung Drift; **schema là của Hub**, không mang sang |
| `features/subscription` | 2.975 | ⚠️ QuotaGuard **fail-open** — xem §6① |
| `features/audio` + `my_voice` | 5.887 | STT/TTS có sẵn; TTS hữu ích cho học sinh tiểu học |

## 4. DROP — không mang sang

`features/arcade` (10.166) · `features/tv` (3.323) · `features/output` Studio (12.378)
· `features/vault` (3.717) · `features/library` (5.061) · `features/canvas` (3.087)
· `features/smart_tools` (2.612) · `features/home` (2.740) · `features/portal` (216)
· `features/ai_router` (24 + shadow) — xem §6③

**Tổng DROP ≈ 43.000 dòng** = 45% của `features/`.

## 5. RESEARCH / BLOCKED

- **Curriculum Graph · Student Knowledge Graph** — Hub **không có gì** tương đương. Xây mới.
- **Mastery / knowledge tracing** — không có. `learning_state` của Academy là thứ khác.
- **Parent↔child identity** — Hub là app một người dùng. Đây là thay đổi kiến trúc thật.
- **BLOCKED: bản quyền SGK** — xem `docs/research/TEXTBOOK-LICENSING-QUESTIONS.md`.

---

## 6. ⚠️ Ba rủi ro lịch sử — kết quả kiểm

### ① QuotaGuard — **VẪN FAIL-OPEN** (còn đúng)

`subscription_ui.dart:33` · `QuotaGuard.check()`:
```dart
} catch (e) {
  // Fail-safe: không đọc được entitlement/usage ⇒ cho qua nhưng có log.
  QuotaAudit.record(QuotaPolicy.error(...));
  return true;
}
```
Đây là lựa chọn **có chủ ý** và có ghi log, không phải bug — với Hub, chặn nhầm một
người lớn đã trả tiền thì tệ hơn cho qua. **Nhưng Learning Coach là app cho trẻ em**:
"cho qua khi không đọc được hạn mức" nghĩa là một đứa trẻ có thể tiêu tiền API của bố
mẹ vô hạn khi entitlement lỗi. **Phải đảo mặc định khi port.**

### ② Feature flags — **ĐÃ FIX, fail-closed** (không còn đúng)

`gate_registry.dart:492` `resolve()`: override → declared default → `failClosedFor(key)`.
Key **chưa khai** trả `false` và ghi `GateOutcome.unknownKeyFailClosed`. Rủi ro lịch sử
này **đã đóng**. → `core/flags` xếp REUSE.

### ③ AI Router — **là shadow-only, đúng nghĩa no-op** (còn đúng, nhưng khác cách hiểu)

`features/ai_router/ai_router.dart` chỉ **24 dòng export**. Comment trong mã:
> *"…only (behind the default-OFF flag `ai_router.shadow`) and **never** influences
> which [provider]"*

⇒ AI Router **không phải** lớp trừu tượng nhà cung cấp đang hoạt động. Nếu port nhầm nó
làm nền cho Learning Coach thì sẽ dựng trên một thứ cố ý không có tác dụng.
**Lớp thật là `features/ai_gateway` (2.872 dòng).**

---

## 7. Rủi ro phụ thuộc

65 dependencies cho một app học tập là **quá nhiều**. Phần lớn phục vụ Arcade/TV/Studio/
Vault — những thứ đã DROP. Bootstrap sạch nên bắt đầu từ **~20** và thêm khi cần, thay vì
kế thừa 65 rồi gỡ dần.

⚠️ **`analyzer: ^12.1.0`** vừa thêm vào Hub (dev) cho chốt kiến trúc AST — mang sang được,
rẻ, và mẫu chốt đó rất hợp với app trẻ em.

## 8. Bảo mật / riêng tư / an toàn trẻ em

| Có sẵn dùng được | Thiếu, phải xây |
|---|---|
| `flutter_secure_storage` (8 tệp) — BYOK key | **parental consent** |
| `core/compliance` (226) — region gate | **child profiles / age-aware UX** |
| `core/audit` — GateAudit/QuotaAudit | **moderation** đầu ra AI |
| cổng đồng ý AI một lần tại choke-point `chat()` | **chặn PII lên model ngoài** |
| Local-first: dữ liệu ở máy, BYOK header trực tiếp | **hint-first tutoring guardrail** |

⭐ Doctrine **Local First / BYOK / Privacy by Default** của Hub *rất* hợp app trẻ em —
đây là tài sản lớn nhất mang sang được, lớn hơn bất kỳ module mã nào.

## 9. Định danh phải thay

`ai.workizen.wallet` → đề xuất **`ai.workizen.learningcoach`** (Android `applicationId`
+ `namespace`, iOS `PRODUCT_BUNDLE_IDENTIFIER` ×2, Dart package `wallet` → `learning_coach`).
⚠️ Quyết định **không đảo ngược được** sau khi lên store.

## 10. Thương hiệu / asset

Toàn bộ `assets/` của Hub là của Hub. Cấu trúc đề xuất cho linh vật CÚ:
```
assets/brand/{logo,wordmark}/  ·  assets/mascot/<state>/   (hello, thinking, hint,
celebrate, retry, confused, mastery, parent_insight, rest, ai_lab, reading, teaching)
assets/illustrations/  ·  assets/icons/
```
`concept/` (3 png Founder đã đặt) → chuyển vào `docs/ux/concepts/`.

## 11. Firebase / config / secret

Hub có Crashlytics + Analytics (bật theo QĐ Founder 7/8) và AdMob App ID **thật** trong
`AndroidManifest.xml`. ⛔ **Không copy `google-services.json`, không copy AdMob ID.**
Learning Coach cần Firebase project riêng. `dev-secrets/` **không** mang sang.

## 12. CI/CD

Hub không ép format trong CI. Đề nghị Learning Coach **ép từ ngày đầu** (`dart format`
+ `flutter analyze` + test) — rẻ lúc repo còn rỗng, đắt sau này.

## 13. Test baseline

Hub 2.493 test. Mẫu đáng mang sang (không phải mã, mà **cách làm**):
- chốt **đo bằng biên dịch** (`dart analyze` trên tệp probe sinh ra rồi xoá)
- chốt **kiến trúc đọc AST** — chặn một API nguy hiểm bị gọi ngoài chỗ được phép
- **bộ đếm hoá đơn LLM** trong test — hỏi "có tiêu tiền không", không hỏi "UI có đúng không"

Ba mẫu này áp thẳng được cho guardrail "AI không được giải hộ" của Tutor.

## 14. Chiến lược đề xuất

→ `docs/architecture/BASE-CLONE-PLAN.md`
