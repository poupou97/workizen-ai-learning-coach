# Chiến lược dựng nền cho AI Learning Coach

**Ngày:** 2026-08-31 · Dựa trên `docs/discovery/PERSONAL-HUB-BASE-AUDIT.md` (đo mã thật)

---

## Con số quyết định

| | |
|---|---|
| Hub có | 126.204 dòng Dart · 65 dependencies · 2.493 test |
| DROP thẳng | **≈43.000 dòng** = 45% của `features/` |
| REUSE gần nguyên trạng | **≈6.900 dòng** (`core/` + OCR + BM25 + metrics) |
| REUSE_WITH_REFACTOR | ≈22.500 dòng, mỗi phần đều phải sửa |

⇒ Phần *lấy được mà không sửa* chỉ khoảng **5,5%** khối lượng Hub.

---

## Option A — Clone toàn repo rồi dọn mạnh

Kế thừa 126k dòng, 65 dep, 1.247 commit, lịch sử git 304MB.

❌ **Bác.** Ba lý do đo được, không phải cảm tính:

1. **Tỉ lệ sai.** Xoá 45% rồi sửa 18% để giữ 5,5% — công dọn lớn hơn công dựng.
2. **Có tiền lệ ngay trong Hub.** Tổng Tài từng được bootstrap *bên trong* repo Hub.
   Hôm nay (31/08) tôi vừa gỡ ra: 94 tệp, 33.107 dòng, và **8 ADR kiến trúc của họ
   suýt bị xoá mất vĩnh viễn** vì phép so bằng tên tệp không đủ. Vé WH-291 mở
   **16 ngày**. Đó chính xác là cái giá của "mượn base cho nhanh".
3. **Định danh dính khắp nơi.** `ai.workizen.wallet` nằm ở Android namespace +
   applicationId, iOS bundle ×2, Dart package name, AdMob ID thật, `google-services.json`.
   Sót một chỗ là app trẻ em bắn analytics vào project của Hub.

## Option C — Tách core dùng chung thành package

Đẹp về lý thuyết. ❌ **Chưa phải bây giờ.**

Chỉ có **một** consumer thật (Learning Coach) và nó chưa biết mình cần gì. Rút core ra
package lúc này là đóng băng một API trước khi biết hình dạng đúng — rồi sẽ phải phá.
Cả `core/theme` lẫn `core/navigation` gần như chắc chắn phải đổi cho UX phụ huynh/học sinh.

⭐ **Xem lại Option C sau POC**, khi có consumer thứ hai và API đã ổn định.

## Option B — Scaffold sạch, copy có chọn lọc ✅ **KHUYẾN NGHỊ**

`flutter create` mới, rồi **copy từng tệp có tên trong audit**, mỗi lần copy chạy test.

Vì sao thắng:
- Bắt đầu từ **~20 dependencies** thay vì gỡ dần từ 65.
- Định danh **đúng từ commit đầu**, không có `wallet` nào sót lại.
- Mỗi dòng mã trong repo mới đều có người *chủ động* mang vào — không có "chưa ai dám xoá".
- Doctrine mang sang là **Local First · BYOK · Privacy by Default**, không phải mã.

Đổi lại: chậm hơn A vài ngày. Founder đã chốt *"Clean architecture > Clone nhanh"*.

---

## Thứ tự thực hiện (Phase 3)

```
① flutter create · package `learning_coach` · appId ai.workizen.learningcoach
② core/theme + core/l10n + core/navigation + core/responsive   → chạy được app rỗng
③ core/flags + core/audit                                       → nền auditability
④ data/services/ocr_processor.dart                              → nền Camera Tutor
⑤ features/ingestion/chunk_retriever.dart (BM25 thuần)          → nền retrieval
⑥ features/ai_gateway (KHÔNG phải ai_router)                    → nền BYOK
⑦ mẫu test: probe biên dịch · chốt AST · bộ đếm hoá đơn LLM
```

Sau mỗi bước: `flutter analyze` + `flutter test` phải xanh. Commit nhỏ.

⛔ **Không** copy `google-services.json`, AdMob ID, `dev-secrets/`, `assets/` của Hub.

---

## ⚠️ Ba điểm cần Founder quyết trước khi chạy Phase 3

> **Cập nhật 2026-09-01 — ① và ② ĐÃ ĐÓNG. ③ vẫn mở.**
> Văn bản gốc giữ nguyên bên dưới làm hồ sơ. Đừng đọc chúng như câu hỏi còn mở: doctrine
> hết hạn chặn cứng y hệt một cổng thật, và không test nào bắt được chuyện đó.

**① Tên repo — `workizen-ai-learning-coarch`** · ✅ **ĐÃ CHỐT 2026-09-01**
> Founder xác nhận `coarch` là lỗi gõ. Tên chuẩn **`workizen-ai-learning-coach`**. Thư mục
> local đã đổi tên; branch `master` → `main` theo convention repo sản phẩm mới. Định danh
> package/bundle **không** đổi vì đã đúng dạng sẵn: `learning_coach` ·
> `ai.workizen.learningcoach`.

Nhiều khả năng là lỗi gõ của *coach*. Đổi tên repo GitHub bây giờ tốn 1 phút; sau khi có
CI, submodule, tài liệu trỏ vào thì đắt. **Không tự đổi** — đây là quyết định định danh.

**② Thư mục chưa phải một git repo** · ✅ **KHÔNG CÒN ĐÚNG từ 2026-08-31**
> Nay là repo git riêng: 10 commit, remote `poupou97/workizen-ai-learning-coach` (PRIVATE),
> branch `main` — đúng ADR-059 *một repo mỗi sản phẩm*.

`workizen-ai-learning-coarch/` hiện là thư mục **untracked bên trong** repo cha
`~/projects` (remote `workforceos-project` trên GitHub). Theo ADR-059 *một repo mỗi sản
phẩm* thì nó phải là repo riêng. Tôi chưa `git init` vì việc này gắn với ① .

**③ Bản quyền SGK — có thể là blocker sản phẩm**
9,8GB PDF SGK đang nằm trong thư mục. Chưa có bằng chứng nào về quyền phân phối lại,
huấn luyện, hay RAG thương mại. Xem `docs/research/TEXTBOOK-LICENSING-QUESTIONS.md`.

> ✅ Đã xử lý ngay phần rủi ro kỹ thuật: thêm `.gitignore` chặn `nguon-chi-thuc/`,
> `*.pdf` và `poc-out/`. Đã kiểm: git nay thấy **0** đường dẫn SGK.
>
> ⚠️ **Đính chính cơ chế (đo 2026-09-01).** Câu "một lệnh `git add -A` ở `~/projects` là
> đủ để đẩy 9,8GB lên GitHub" **không đúng** kể từ khi thư mục này thành repo git. Dry-run
> thật ở repo cha chỉ sinh **một** entry gitlink kèm `warning: adding embedded git
> repository` — 0 byte corpus, vì git không đệ quy vào repo lồng. Xem
> `docs/decisions/ADR-002-bao-ve-corpus-nhieu-lop.md` cho ma trận 4 ca đã đo.
