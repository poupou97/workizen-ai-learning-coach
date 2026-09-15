# BÀN GIAO — cho Claude ở máy Windows

Viết 2026-09-15, tại `b878068`. Đọc hết trước khi gõ dòng mã đầu tiên.

---

## 1 · Dự án là gì

**«Học cùng SAM»** — gia sư AI cho học sinh phổ thông Việt Nam, dựng trên
**sách giáo khoa thật** (SGK) và **sách giáo viên thật** (SGV). Flutter + công
cụ Python. Jira `WAL`, GitHub `poupou97/workizen-ai-learning-coach`.

Điều làm dự án này khác mọi dự án AI khác bạn từng gặp: **người dùng là trẻ
con, và trẻ con không kiểm chứng được điều máy nói.** Nên luật nền là

> **«KHÔNG BỊA SỰ THẬT CHO TRẺ»**

Không phải khẩu hiệu. Nó là thứ đã khiến hàng chục quyết định kỹ thuật đi
ngược hướng «làm cho con số đẹp hơn».

---

## 2 · Bảy bất biến — thuộc lòng trước khi làm gì

| | nghĩa |
|---|---|
| `OPENED != UNDERSTOOD` | mở được bài không phải là học được |
| `MEASURED != ASSUMED` | đo trước khi ra luật, luôn luôn |
| `CI GREEN != CONTENT CORRECT` | test xanh không chứng minh chữ đúng |
| `PRODUCED != DELIVERED` | có trong pack không phải là trẻ thấy |
| `TEXT MENTION != FIGURE IDENTITY` | nhắc tên hình không phải là hình ấy |
| `TASK EXISTS != TASK IS DOABLE` | có đề bài không phải là làm được |
| `UNKNOWN != VALID` | không biết thì ghi không biết |

Và **`SAI TÊN > THIẾU TÊN`** — thà thiếu còn hơn sai. Mọi luật đều
**fail closed**: thiếu bằng chứng ⇒ giữ nguyên/không phát, không đoán.

---

## 3 · Trạng thái thật hôm nay

`docs/MASTER-TODO.md` là bản nhìn cấp Founder — **đọc nó trước**, và **cập
nhật sau mỗi vòng có ý nghĩa**.

| chỉ số | giá trị | mẫu số |
|---|---|---|
| `OPENABLE_RECORDS` | 2.974 | bản ghi bài mở đọc được |
| `DISTINCT_OPENABLE` | 2.778 | bài duy nhất |
| danh tính HÌNH | 80,2% | 7.120 / 8.876 `NAMED_OWN` |
| cặp SGK↔SGV CONFIDENT | 589 | / 895 cặp bài · 78/220 cuốn |
| `SAM_READY` | **33** | / 2.778 |
| `RUNTIME_GUIDED_READY` | **18** | / 33 |
| `ANSWER_CHECK_READY` | **0** | / 33 |
| `MISCONCEPTION_READY` | **0** | / 33 |

⚠ **Mỗi con số phải đi kèm mẫu số.** Đã có tiền lệ báo sai vì trộn hai mẫu số
(xem `[[learning-coach-denominators]]`).

---

## 4 · Kiến trúc đường dữ liệu

```
PDF sách → OCR (docling+ocrmac) → poc-out/graph
  → lesson_reading → pack canonical (assets/pack/lesson-index-gN.json)
  → client Flutter (lib/features/subjects) → TRẺ ĐỌC

SGK + SGV → ghép CONFIDENT (3 mỏ neo) → pedagogy-contract-v1
  → SourceCurriculum → resolveBinding → TutorScope
  → PedagogyRuntime → màn «Học với SAM»
```

Ba tab học: 📖 Đọc · ✨ Trực quan · 🦉 Học với SAM.

**Ghép SGK↔SGV đòi BA dữ kiện nguồn độc lập** (`tool/pedagogy/sgk_sgv_pairing.py`):
L1 tiêu đề «Bài N» ở đầu trang thân · L2 tiêu đề trùng SGK · L3 ngay sau có mục
mở thân bài. Khớp số bài **một mình không đủ** — đã đo được ca ghép sai thật.

---

## 5 · ⛔ MÁY WINDOWS KHÔNG OCR ĐƯỢC

Kho canonical dựng bằng **`docling-2.126 + ocrmac 1.0.1`** — `ocrmac` bọc
**Apple Vision, chỉ chạy macOS**. **Mọi** con số ở §3 hiệu chỉnh trên đầu ra ấy.

Đổi engine (RapidOCR/PaddleOCR — kho *có* adapter, nhưng đó là ứng viên bakeoff
TC-v1) cho ra **một kho khác**, không phải một bản sao.

**Không chạy lại OCR trên Windows.** Thêm sách mới ⇒ OCR trên máy Mac ⇒ chép
`poc-out/graph` phần mới sang. Chi tiết: `docs/MACHINE-MIGRATION.md`.

---

## 6 · Bộ nhớ làm việc — ĐỌC TRƯỚC KHI LÀM

38 tệp — 37 bài học đã trả giá + MEMORY.md — nằm ở `claude-memory/` trong bản sao lưu di trú. **Khôi
phục vào thư mục memory của bạn trên máy mới.** Vài cái đắt nhất:

- **`copy-verify-or-nothing`** — `rsync` báo exit 0 mà chép 0 byte; `| tail`
  nuốt mã lỗi. «Lệnh báo thành công» không phải bằng chứng.
- **`client-drops-unknown-blocks`** — 2.699 khối công thức vào pack mà client
  bỏ im lặng, mất một ngày mới phát hiện. Thêm loại khối mới ⇒ kiểm ĐỦ CHUỖI
  tới widget.
- **`measurement-window-hides-data`** — bộ lọc dùng để *chọn* dữ liệu lại loại
  đúng thứ đang tìm, và tôi đã dựng cả một «họ lỗi» không có thật.
- **`docling-picture-bbox`** — luật an toàn cho bảng lại nuốt 74% trang khi áp
  cho hình.
- **`comparison-key-collapses`** — khoá `(book, lesson)` gộp mất 12 bản ghi; so
  pack phải theo **vị trí mảng**.
- **`build-flags`** — `FORMULA_SOURCE=1` là cờ bật thủ công; quên thì mảnh OCR
  chảy ngược vào bài mà không lỗi nào báo.
- **`adb-install-not-proof`** — «Success» không chứng minh mã mới lên máy; phải
  **kéo APK về** kiểm.
- **`device-protocol`** — máy là máy **cá nhân của Founder**, có hồ sơ con thật.
  Kiểm foreground **trước** khi bơm input; chụp màn **trước mỗi lần chạm**; đổi
  gì thì **trả lại nguyên trạng**. Đã có một lần bấm Back làm lộ app cá nhân
  đang hiện tên thật của Founder — dừng ngay, bấm HOME, báo cáo.

---

## 7 · Cách Founder làm việc

- Ra lệnh bằng **Master Order** dài, đánh số mục. Đọc **hết** rồi mới làm.
- **Chế độ tự chủ nhanh**: đo/dựng → test → PR → CI xanh → merge main → bằng
  chứng máy thật → sửa tiếp. **Không hỏi từng PR.**
- **Cổng Founder** chỉ còn ở: phát hành store · chi tiền · pháp lý · thay đổi
  dữ liệu không đảo ngược được · đổi hướng kiến trúc lớn.
- **Kiểm-đột-biến là bắt buộc**, không phải tuỳ chọn: sửa xong thì cố ý làm
  hỏng từng chốt, test phải ĐỎ. Đột biến sống sót = bất biến **chưa** được
  chứng minh (trừ khi chứng minh được là tương đương).
- Báo cáo theo mẫu ở cuối `docs/MASTER-TODO.md`: `PROJECT STATUS` → `SAM SCALE`
  → `CURRENT P0` → `P0 PROGRESS` → `NEW EVIDENCE` (tách CENSUS/SAMPLE/DEVICE)
  → `MERGED` → `DEVICE` → `FOUNDER DECISION NEEDED`.
- **Không báo % nếu không có mẫu số tái hiện được.**
- Founder đọc tiếng Việt. Viết tiếng Việt.

### Điều Founder quý nhất

Ông ấy **thưởng cho việc tự bác bỏ mình**. Mấy lần tôi tìm ra lỗi của chính
mình và báo thẳng, ông ấy ghi nhận và dùng nó làm bằng chứng cho vòng sau. Số
liệu đẹp mà không kiểm chứng được thì vô giá trị ở đây.

Giữ lại **kết quả bị bác bỏ**. «Sở hữu hình diện rộng = FALSIFIED» là một tài
sản, không phải một thất bại.

---

## 8 · Đang ĐÓNG BĂNG — không tự mở

Cấu trúc quan hệ **bảng** · OCR **biểu đồ/sơ đồ/ảnh chụp màn hình** · nhiễm
trong khối chú thích bản đồ · **answer ownership** · Formula AVOID-C · Code 541
· TTS · neo vị trí đề bài · hoạt động dây chuyền · **LLM Tutor** (bị cấm từ
2026-09-05) · dọn Jira chung · UI redesign.

Ba giả thuyết **đã bị bác, giữ nguyên, không hồi sinh**: sở hữu hình diện rộng
· «Family B = content loss» · ngưỡng diện tích 5% là luật content-validity.

---

## 9 · Việc tiếp theo

1. **Bootstrap Windows** theo checklist trong `docs/MACHINE-MIGRATION.md`, rồi
   **verify bản khôi phục bằng manifest** — chưa ĐẠT thì chưa được coi là xong.
2. Chờ Founder chọn một trong:
   - **B** — 15/33 bài chưa ràng buộc vì SGK không in khối quy tắc. Thử tìm quy
     tắc trong **SGV** (mục «THÔNG TIN BỔ SUNG»), **không nới luật hiện tại**.
   - **C** — ghép **lớp 1–5**, hiện đóng góp **0 bài**: SGV tiểu học trượt ngay
     cổng SÁCH (lớp 1: 0/10 CONFIDENT). Đây là hướng chính để phá trần 33.

**Không tự chạy.** Founder chọn.

---

## 10 · Tài liệu nên đọc, theo thứ tự

0. `docs/FIRST-PROMPT-WINDOWS.md` — lệnh mở đầu Founder dán cho bạn; nếu bạn
   đọc tài liệu này mà chưa thấy lệnh đó, hãy đọc nó trước

1. `docs/MASTER-TODO.md` — trạng thái cấp Founder
2. `docs/MACHINE-MIGRATION.md` — máy, dữ liệu, bootstrap
3. `docs/SGV-PEDAGOGY-GATE.md` — bốn cổng SGV, đầy đủ số liệu
4. `docs/MAP-LABEL-SUPPRESSION.md` — mẫu một vòng làm việc tốt: **đo → bác bỏ
   giả thuyết rộng → thu hẹp → kiểm-đột-biến → máy thật**
5. `CLAUDE.md` gốc workspace — Canonical Knowledge là bắt buộc đọc trước việc lớn
