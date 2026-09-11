# MASTER TODO — «Học cùng SAM»

**Đây là bản nhìn cấp Founder.** Repo là source of record · Jira là theo dõi thi
hành · tài liệu này là trạng thái dự án.

Cập nhật: **2026-09-11** · main `b7e1bc5` · cây sạch · 1.493 test Python ·
1.477 test Flutter.

> Quy ước: `DONE · DOING · NEXT · WAIT · BLOCKED · FROZEN · DEFER`.
> **NĂNG LỰC TÁCH RIÊNG** (Founder 2026-09-11): `SAM_READY` ≠ `ANSWER_CHECK_READY`
> ≠ `MISCONCEPTION_READY`. Một vòng học KHÔNG CHẤM vẫn là `SAM_READY` nếu nó
> thật và chạy hết đường sản phẩm. Cờ nằm trong DỮ LIỆU, không chỉ trong tài liệu.
>
> **DOING = đang thực sự được thi hành.** Tài sản/mã cũ tồn tại KHÔNG phải DOING.
> Không có % nếu không có mẫu số tái hiện được. Không chắc ⇒ **UNKNOWN**.
> Số cũ đã bị thay ⇒ **SUPERSEDED**. Giả thuyết đã bác ⇒ **FALSIFIED**.

---

## LỘ TRÌNH TỚI SAM SCALE

```
              SAM_READY = 1          ← nguyên mẫu viết tay, trust=prototype
              + 10 bài POC           ← MỘT bộ dựng, KHOÁ chấm điểm (fail-closed)
                    │
   GATE 1 ── ✅ PASS   SGK ↔ SGV: 589 cặp bài CONFIDENT, ghép sai 0/30
                    │
   GATE 2 ── 🟡 PARTIAL  đáp án gắn ĐÚNG VIỆC 81/589 · nhầm-lẫn 61/589
                    │
   GATE 3 ── ⏳ WAIT   Bằng chứng ấy → hợp đồng Pedagogy Runtime
                    │
              SAM 1 → 10            ✅ PASS — 2 máy · 3 môn · back/resume ĐẠT
              SAM → 33              quần thể đáng tin hiện có (trần hôm nay)
                    │
              kiểm chéo lớp · chéo môn · máy thật · ghép SAI · sư phạm SAI
                    │
              SAM 10 → 50           lô
                    │
              SAM 50 → N
```

Kiến trúc nhắm tới — **KHÔNG phải viết tay 2.974 kịch bản**:

```
SGK + SGV + bằng chứng học liệu đáng tin
        ↓  Pedagogy Evidence
        ↓  TutorScope / Pedagogy Runtime
        ↓  hành vi dạy của SAM
```

⛔ **LLM không quyết định sư phạm.**

---

## A · NỀN DỮ LIỆU & GIAO HÀNG (01–08)

| ID | WORKSTREAM | STATUS | EVIDENCE | BLOCKER | NEXT | JIRA |
|---|---|---|---|---|---|---|
| 01 | SGK/SGV ingestion | **DONE** | 531 cuốn có OCR (**220 SGV** + 311 còn lại); 238 tệp attach trong repo | — | — | NONE |
| 02 | Canonical Read | **DONE** | `OPENABLE_RECORDS` **2.974** · `DISTINCT_OPENABLE` **2.778** | — | — | NONE |
| 03 | Figure/Image delivery | **DONE** | **2.671/2.974** bài có ≥1 ảnh giao được; 17.536 khối `img` | — | — | WAL-235 (ACTIVE) |
| 04 | Figure identity/caption | **DONE** | HÌNH `IDENTITY_MATCHED` **7.120/8.876 = 80,2%** · BẢNG **474/599 = 79,1%**; census tái hiện được `figure_identity_census.py` (`a25e6cf`) | — | — | WAL-235 — **STALE** (tiêu đề còn ghi 20,2%) |
| 05 | Formula source-safe | **DONE** | **2.699** khối `formula` trong pack + renderer client + kiểm máy thật | — | — | WAL-239 (PARTIALLY SUPERSEDED) |
| 06 | Program-code preservation | **DONE** | `code_source.py` + 17 test; 21/21 dòng mã tới pack | — | — | WAL-239 |
| 07 | Map evidence / OCR suppression | **DONE** | **2.405** khối gỡ / 10 cuốn; chuỗi NGUỒN→CHẶN→PACK→CLIENT→TRẺ **DEVICE PASS**; `44da1b3` `e52a0e9` `c96d24c` | — | — | WAL-235 |
| 08 | Canonical build safety | **DONE** | `staging.require_promoted` dừng hẳn lượt dựng canonical thiếu năng lực đã promote; 7 test; đã bắn trên lượt dựng thật; `2baa302` | — | — | NONE |

## B · NỢ BẰNG CHỨNG ĐANG ĐÓNG BĂNG (09–10)

| ID | WORKSTREAM | STATUS | EVIDENCE | BLOCKER | NEXT | JIRA |
|---|---|---|---|---|---|---|
| 09 | Table relational structure | **FROZEN** | Ma trận 17 việc: **T1 · T11 · T12** trượt vì ô bảng rời rạc; danh tính bảng đã lên 79,1% nhưng `TABLE IDENTITY RECOVERED != TABLE USABLE` | Founder đóng băng | — | WAL-236 — **PARTIALLY SUPERSEDED** (nửa danh tính xong, nửa cấu trúc còn) |
| 10 | Diagram/chart/screenshot OCR duplication | **FROZEN** | Thấy trên máy thật: trục biểu đồ «100 · 96,5 · 101,3 · 86,0 …» rơi hai lần cạnh ảnh đúng. Giả thuyết **sở hữu hình diện rộng = FALSIFIED** (39.797 đoạn, 1.166 chú thích bị xoá, hộp «Hình 5.4» phình 74% trang) | Cần **bằng chứng điểm ảnh** — kho không có ảnh trang toàn bộ | — | NONE |

> Kèm nhóm này: **nhiễm trong khối chú thích bản đồ** («100 108° Hình 2. Bản đồ…»)
> — chốt fail-closed giữ ĐÚNG luật, lỗi nằm **bên trong đoạn OCR**. FROZEN.

## C · P0 HIỆN TẠI — NGUỒN SƯ PHẠM SGV (11–14)

| ID | WORKSTREAM | STATUS | EVIDENCE | BLOCKER | NEXT | JIRA |
|---|---|---|---|---|---|---|
| 11 | **SGK ↔ SGV lesson pairing** | **DONE · GATE 1 PASS** | 3 mỏ neo nguồn độc lập. Census 220 cuốn: SÁCH CONFIDENT **78**/46/96 · BÀI CONFIDENT **589**/151/155 (mẫu số 895). Mẫu kiểm MỚI chưa nhiễm (20260912, 30 ca, 11 lớp): **ghép sai 0/30** | — | — | WAL-198 |
| 12 | SGV pedagogy evidence extraction | **DONE · GATE 2 PARTIAL** | Trên 589 cặp CONFIDENT: ANSWER 56,9% · ASSESSMENT 77,2% · MISCONCEPTION 10,4%. ⚠ OBJECTIVE 100% là **VÒNG TRÒN** (chốt L3 đã đòi «MỤC TIÊU»); ACTIVITY/HINT ~100% là từ vựng chung | — | — | WAL-198 |
| 13 | Pedagogy evidence trust classification | **DONE** | Hai trục: **A** SOURCE_EXPLICIT/DEMONSTRATED/UNKNOWN · **B** LESSON_OWNED/TASK_LINKED. **ANSWER gắn đúng VIỆC 81/589 = 13,8%** (bản khớp SỐ ra 1,7% — sai phía SGK: «Câu N» chỉ 3,1% bài) | — | — | WAL-198 |
| 14 | **SGV → SAM feasibility gate** | **DONE · PARTIAL** | **79 bài T1** (đáp án gắn đúng việc + hoạt động + hình có danh tính), lớp 6–12, 9 nhóm môn. **Lớp 1–5 = 0 bài** | — | chờ Founder mở 1→10 | WAL-198 |

### Checklist P0 — đã chứng minh vs còn lại

```
[x] Tồn tại nguồn SGV trong kho          220 cuốn đã OCR, phủ lớp 1–12
[x] Bộ khai thác chạy được               sgv-pedagogy-v1, 18 cuốn, 13.634 finding
[x] Đo dấu hiệu MỤC TIÊU (discovery)     186/220 cuốn · 3.809 trang
[x] Đo dấu hiệu ĐÁP ÁN (discovery)       151/220 cuốn
[x] Đo dấu hiệu NHẦM LẪN (discovery)     103/220 cuốn
[x] Bằng chứng ghép theo TÊN là KHÔNG ĐỦ 8/18 cuốn không có SGK đôi
[ ] Định nghĩa ĐƠN VỊ ghép SGK↔SGV
[ ] Đo ghép CHẮC CHẮN
[ ] Đo ghép MƠ HỒ
[ ] Đo UNKNOWN / không ghép được
[ ] Đo bằng chứng OBJECTIVE (đã ghép, không phải đếm xuất hiện)
[ ] Đo bằng chứng ANSWER / EXPECTED RESPONSE
[ ] Đo bằng chứng MISCONCEPTION / COMMON ERROR
[ ] Đo bằng chứng HINT / SCAFFOLD
[ ] Đo bằng chứng ASSESSMENT / RUBRIC
[ ] Đo bằng chứng ACTIVITY GUIDANCE
[ ] Phân xử tin cậy SOURCE_EXPLICIT / SOURCE_DEMONSTRATED / UNKNOWN
[ ] Kiểm mẫu tất định chéo lớp · chéo môn
[ ] Đo GHÉP SAI
[ ] Đo SỞ HỮU BẰNG CHỨNG SAI
[ ] Xác định hành vi SAM mà SGV CHO PHÉP
[ ] Xác định hành vi SAM vẫn phải BỊA
[ ] Cổng cuối: SGV CÓ THỂ NUÔI SAM AN TOÀN KHÔNG — YES / PARTIAL / NO
```

⚠ **Đếm xuất hiện ≠ bằng chứng sư phạm dùng được.** Sáu dòng `[x]` đầu là
*discovery*, không chứng minh ghép đúng, sở hữu đúng, hay SAM dùng được.

## D · SAM (15–20)

| ID | WORKSTREAM | STATUS | EVIDENCE | BLOCKER | NEXT | JIRA |
|---|---|---|---|---|---|---|
| 15 | Pedagogy Runtime | **DONE** | `planForScript` đã tổng quát; `SourceQuoteIndex` đòi mọi trích dẫn nguyên văn nguồn. Chưa nối SGV vì POC KHOÁ chấm điểm. 1.595 dòng ở `lib/core/pedagogy/` (`realization_contract` · `presentation_policy` · `source_misconception` · `source_quote_index`); TutorScope đã có | chưa nối vào nguồn SGV | hợp đồng bằng-chứng→runtime (Gate 3) | NONE |
| 16 | SAM scale POC 1 → 10 | **DONE · PASS** | `SAM_READY` = **1**. Kịch bản duy nhất: `samMode=prototypeScripted` · `trust=prototype` · `evidencePolicy=none` · `keySource` tự khai «KHÔNG phải SGV» | Gate 14 | — | NONE |
| 17 | **SAM SCALE — TRUSTED POPULATION** | **DOING** | quần thể đáng tin hiện có **33 bài**; 33/33 `SAM_READY`. ⚠ `RUNTIME_GUIDED_READY` **0/33** — không tạo `SemanticBinding` vì nguồn không cấp Concept/SkillCase/Method `sourceStated` | Concept/SkillCase chưa có nguồn | device mẫu | NONE |
| 18 | SAM scale 50 → N | **WAIT** | — | 17 | — | NONE |
| 19 | Cross-grade / cross-subject SAM | **WAIT** | 11 fixture hiện chỉ KHTN/Khoa học + 1 LS&ĐL | 16 | — | NONE |
| 20 | Real-device SAM validation | **WAIT** | đường máy thật ĐÃ chứng minh cho Read/Figure (Nokia 6.1, 2026-09-11) | 16 | — | NONE |

## E · ĐANG CHẶN / HOÃN (21–23)

| ID | WORKSTREAM | STATUS | EVIDENCE | BLOCKER | NEXT | JIRA |
|---|---|---|---|---|---|---|
| 21 | Generative / LLM Tutor | **BLOCKED** | «chưa có dòng mã nào»; LLM sinh nội dung học **bị cấm** (Founder 2026-09-05) | quyết định Founder | — | WAL-30 |
| 22 | Nợ LEARNABLE / dữ liệu | **DEFER** | `LEARNABLE_V2` quần thể **37**, lát cắt **6**; WAL-238 mang số **SUPERSEDED** (OPENABLE 2.944, LEARNABLE 0); WAL-194 story mất «Ph»; WAL-214 DIGIT LOSS≠SEGMENTATION; WAL-215 ACTIVITY→QUESTION; WAL-33 ghép biểu thức | — | sửa số WAL-235/238 khi có dịp | WAL-238 · 194 · 214 · 215 · 33 |
| 23 | Nợ UI/UX | **DEFER** | camera polish · dark mode/motion · pack lớn trên máy | — | — | WAL-140 · WAL-50 · WAL-84 |

---

## ĐỐI CHIẾU JIRA

| Jira | Trạng thái đối chiếu | MASTER TODO |
|---|---|---|
| WAL-235 | **STALE** — tiêu đề «recall 20,2%», thực tế 80,2% | 03 · 04 · 07 |
| WAL-236 | **PARTIALLY SUPERSEDED** — danh tính 8/500 → 474/599; cấu trúc còn nợ | 09 |
| WAL-239 | **PARTIALLY SUPERSEDED** — công thức/mã đã giao; `STEM_SAFE` vẫn **UNKNOWN** | 05 · 06 |
| WAL-198 | **ACTIVE — nhà của P0** (dùng nửa SGV pedagogy) | 11 · 12 · 13 · 14 |
| WAL-127 | tiền lệ đã chạy (`sgv-pedagogy-v1`) | 12 |
| WAL-30 | **BLOCKED** — LLM chưa được duyệt | 21 |
| WAL-33 | ACTIVE nhưng không phải P0 | 22 |
| WAL-238 | **STALE** — số từ `05d7139` | 22 |
| WAL-194 · 214 · 215 | ACTIVE, không phải P0 | 22 |
| WAL-197 · 200 · 201 | **DEFERRED** — phụ thuộc 198 | — |
| WAL-196 | quyết định Founder, không phải việc thi hành | — |
| WAL-140 · 84 · 50 | **DEFERRED** | 23 |
| 24 Epic · 33 Ideas | **KHÔNG đụng** theo lệnh Founder | — |

## ĐANG ĐÓNG BĂNG — không khởi động khi chưa có bằng chứng mới

Table relational structure · diagram/chart/screenshot OCR suppression · map
intra-block cleanup · Formula AVOID-C · Code 541 · Formula TTS · positional
prompt anchoring · chained activities · 6→37 LEARNABLE scaling · WAL-30
generative Tutor · WAL-33 mass scaling · UI dark mode/motion · camera polish ·
dọn Jira chung.

## GIẢ THUYẾT ĐÃ BỊ BÁC — giữ nguyên, không hồi sinh

- **Sở hữu hình diện rộng** («mọi vùng hình có danh tính sở hữu chữ bên trong»)
  — **FALSIFIED** 2026-09-11. Không mở lại khi chưa có bằng chứng điểm ảnh.
- **«Family B = content loss»** — **FALSIFIED**; 21/21 dòng mã vẫn tới pack.
- **Ngưỡng diện tích 5% là luật content-validity** — **FALSIFIED** (WAL-232).
