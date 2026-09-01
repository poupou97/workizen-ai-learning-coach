# BÁO CÁO ĐÊM — 2026-08-31 → 09-01

## Executive Summary

Kiến trúc **đã đổi**, và đổi vì bằng chứng chứ không vì ý thích. Ba thay đổi lớn:

**① `SkillCase` được BẢO VỆ bởi bằng chứng nguồn, không phải bởi tôi.** Sách giáo viên
Toán 4 dùng đúng chữ *"trường hợp"* để giới hạn phạm vi bài học — và dùng **13 lần trên
35 trang, trải ≥5 chủ đề**. Tôi không phát minh abstraction; tôi tìm lại cấu trúc mà tác
giả chương trình đang dùng. **KEEP.**

**② Mastery phải chuyển từ Concept xuống SkillCase — vì mã cũ TỰ MÂU THUẪN.** BKT giữ
một trạng thái ẩn cho mỗi skill. Đặt skill = Concept thì không có chỗ chứa *"vững ca này,
chưa vững ca kia"* — mà đó chính là `caseTransitionGap` tôi đã dựng chốt vàng cho hôm
qua. Một chẩn đoán mà mô hình không thể sinh bằng chứng để kết luận. → **ADR-001.**

**③ Misconception KHÔNG lấy được từ sách.** Giả thuyết của tôi ("SGV là nguồn tốt nhất
cho lỗi thường gặp") **sai**. 52 đoạn `Lưu ý` trong 35 trang gần như toàn bộ là chỉ dẫn
tổ chức lớp. Misconception là bài toán **học từ dữ liệu học sinh lúc chạy**, không phải
trích xuất corpus. Ngày ra mắt sẽ có tập rỗng — thiết kế phải chạy được với nó.

## Repository Truth

`workizen-ai-learning-coarch` · **9 commit** · 39 test · analyze sạch · working tree sạch
· **0 PDF/SGK trong toàn bộ lịch sử git** · 0 dấu vết secret · `.git` 9,9MB.

## Experiments Run

| # | Thí nghiệm | Kết quả |
|---|---|---|
| 1 | OCR local Apple Vision, Toán 5 | 0,37 s/trang · 0 đ · văn xuôi ~100% |
| 2 | Render 3× vs 6× | **Y HỆT** — nguồn 100 ppi, độ phân giải không phải cần gạt |
| 3 | Dựng lại phân số bằng hình học | 8/15 (53%) |
| 4 | Trích cấu trúc từ mục lục | Toán 5: 3 chủ đề/18 bài, 1 trang, 0,4 s |
| 5 | Trích tối thiểu Toán 4 | tìm ra Bài 57 — nơi **DẠY** quy đồng |
| 6 | SGV Toán 4, 35 trang mẫu | *"trường hợp"* ×13 / ≥5 chủ đề |
| 7 | Toán 9 mục lục | **kết quả âm tính** — không có phân số |
| 8 | Đọc 4 repo OSS | mâu thuẫn kiến trúc → ADR-001 |
| 9 | Thin slice end-to-end | **nối được** |

## Evidence / Findings

**Hai lớp dạy hai phương pháp cho CÙNG khái niệm** *(mới, quan trọng nhất về sản phẩm)*
- lớp 4 Bài 57 tr.62: mẫu này **chia hết** cho mẫu kia → lấy mẫu lớn
- lớp 5 Bài 6 tr.20: **không chia hết** → lấy **tích** hai mẫu
- lớp 5 mở đầu bằng *"không chia hết cho nhau"* — **sách tự tham chiếu ca lớp 4**

⇒ Học sinh lớp 5 sai `3/4 + 2/5` **có thể không hề hổng quy đồng**. Em ấy vững ca lớp 4
và bối rối vì **luật đổi**. Can thiệp đúng là **đối chiếu hai ca**, không dạy lại.

**Toán 5 chỉ ÔN quy đồng, không DẠY.** Trang 12 là bài luyện tập; Bài 3 tên là *"Ôn tập
phân số"*. Nội dung vá lỗ nằm ở **lớp 4** ⇒ prerequisite graph bắt buộc xuyên lớp.

## Architecture Changes

| | |
|---|---|
| `KnowledgeOrigin` | 3 → **4 mức**: `sourceStated` / `sourceSequence` / `systemDerived` / `llmInferred` |
| `CurriculumEdge.citable` | phụ thuộc **loại khẳng định**, không chỉ xuất xứ |
| `SkillCase` | tầng mới Concept → Case → Method |
| `TeachingMethod` | thêm `skillCaseId` — gate theo **ca**, không chỉ theo lớp |
| `TutorScope.forProblem` | `APPLICABLE ∩ ALLOWED`, **fail closed** |
| `DiagnosticOutcome` | 7 mức, có `caseTransitionGap` |
| `Concept` | `exposures` theo lớp + `ExposureRole` |
| `RemediationStatus` | 3 mức, có `remediateKnowledgeMissing` |
| **`CaseMastery`** | **ADR-001** — BKT 14 dòng, mastery theo ca |
| `AdaptiveEngine` | luật, kèm `reason` hiển thị được cho phụ huynh |

## Architecture Hypotheses Rejected

- ❌ *"SGV là nguồn misconception"* — sai, đo được
- ❌ *"Mastery đặt ở Concept là đủ"* — mâu thuẫn với `caseTransitionGap`
- ❌ *"Toán 9 cho phép so cùng khái niệm ở lớp cao hơn"* — lớp 9 không có phân số
- ❌ *"Độ phân giải cao hơn cứu được OCR toán"* — 6× cho kết quả y hệt
- ❌ *"parse_toc v1 dùng được cho mọi sách"* — Toán 9 hai cột, v1 sai **im lặng**

## SkillCase Verdict — **KEEP** *(và nâng lên đơn vị mastery)*

Bằng chứng ủng hộ: SGV dùng *"trường hợp"* 13 lần trên ≥5 chủ đề khác nhau. Không phải
riêng phân số. Đây là cấu trúc sư phạm tái diễn, `SOURCE_STATED`.

⚠️ Vẫn còn mỏng: mới **một** khái niệm được xác minh sâu (`quy-dong`). Chưa đo ở môn khác.

## Toán 9 Findings

Không có phân số trong tập một. Chương I–V: phương trình/hệ · bất phương trình · căn bậc
hai-ba · hệ thức lượng tam giác vuông · đường tròn. ⇒ **khái niệm có VÒNG ĐỜI**; không
phải khái niệm nào cũng trải mọi lớp.

⭐ Toán 9 có **BẢNG GIẢI THÍCH THUẬT NGỮ** (tr.119) — khái niệm **kèm định nghĩa**, tốt
hơn hẳn bảng thuật ngữ Toán 5 (chỉ có số trang). Trích được **26 mục**. Chất lượng nguồn
khác nhau theo lớp.

## Retrieval Results

**Chưa chạy POC riêng.** Nhưng lọc metadata trước đã chứng minh trong thin slice: biết
`grade=5 · concept=quy-dong · case=non-divisible` thì tập phương pháp thu từ 3 xuống 1
mà không cần tìm kiếm ngữ nghĩa nào. Với dữ liệu đang có, **lọc cấu trúc mạnh hơn tương
đồng ngữ nghĩa** — nhưng đây chưa phải benchmark, đừng trích dẫn như benchmark.

## Camera Tutor OCR Results

**Chưa đo trên ảnh chụp điện thoại.** Biết từ bản quét: công thức toán 53%. Kiến trúc đã
sẵn sàng cho ca xấu — `caseUnknown` ⇒ Tutor nhận **tập rỗng**, có test.

## Adaptive Learning Readiness

| | |
|---|---|
| Concept graph | 🟢 khung tất định từ mục lục, 2 sách |
| Prerequisite graph | 🟡 chuỗi xuyên lớp có, cạnh vẫn `llmInferred` |
| Exercise → Concept | 🔴 chặn ở OCR công thức 53% |
| Misconception | 🔴 không có nguồn văn bản — phải học lúc chạy |
| Mastery evidence | 🟢 **BKT 14 dòng, chạy, có test** |
| Root-gap | 🟢 luật chạy, phân biệt được 4 ca chẩn đoán |
| Next Best Action | 🟢 chạy, kèm lý do đọc được |
| V1 algorithm | 🟢 **Mastery Learning + BKT + rule engine**, không DKT |

## End-to-End Thin Slice — ✅ NỐI ĐƯỢC

6 test: chuỗi trọn vẹn · cùng học sinh ca khác ⇒ chẩn đoán khác · OCR hỏng ⇒ fail closed
· học sinh mới ⇒ không kết luận · vòng lặp khép kín (bằng chứng mới đổi kết luận).

## Quality

**tests** 39 · **analyze** sạch · **mutation** 7 phép, 6 bắt được ngay, 1 lộ **chốt thừa**
(hai lớp chắn độc lập cho cùng kết quả) → đã siết test, nay bắt được ·
**git** 9 commit, tree sạch, 0 PDF trong lịch sử.

## Corpus Used

Toán 5 tập một (53 tr.) · Toán 4 tập một+hai (mục lục + Bài 57) · SGV Toán 4 (35 tr.) ·
Toán 9 tập một (mục lục + 2 tr. thuật ngữ). **Không** ingest lớp nào khác.

## Token / Cost / Runtime

**LLM calls cho toàn bộ trích xuất: 0.** OCR local 0,37 s/trang, 0 đ.
Ước lượng scale: mục lục + thuật ngữ cho 444 cuốn ≈ 1.332 trang ≈ **8 phút, 0 đ**.

## Legal / Source Safety

`TECHNICAL_POC_ALLOWED_BY_FOUNDER` / `COMMERCIAL_USE_LEGAL_REVIEW_PENDING` — **không đổi**.
0 PDF trong lịch sử git. 4 repo OSS đều **MIT**; license mã **không** phủ dataset.

## Founder Decisions Required

**~~FOUNDER_DECISION_REQUIRED~~ — 1. Tên repo `coarch`** · ✅ **ĐÃ CHỐT 2026-09-01**
> Founder: `coarch` là lỗi gõ. Repo nay là `workizen-ai-learning-coach`, branch `main`,
> remote `poupou97/workizen-ai-learning-coach` (PRIVATE).

Gần như chắc là lỗi gõ của *coach*. Nay đã có 9 commit và một repo git thật. Đổi bây giờ
vẫn rẻ; sau khi có CI/remote thì đắt. *Không tự đổi — quyết định định danh.*

**FOUNDER_DECISION_REQUIRED — 2. Luật tổng hợp case → concept**
ADR-001 chọn `min` vì *"vững nhất ở mức ca yếu nhất"* an toàn cho trẻ. **Chưa có dữ liệu
thực nghiệm.** Lựa chọn khác: `mean` (dịu hơn, nhưng giấu ca hỏng), có trọng số theo số
bằng chứng. Hệ quả: ảnh hưởng trực tiếp tần suất Parent Coach báo động.

## Recommended Next

1. **Camera Tutor OCR trên ảnh điện thoại** — ô đỏ duy nhất chặn cả Exercise→Concept lẫn
   Camera Tutor. Nếu ảnh điện thoại vượt được rào 53% thì cục diện đổi hẳn.
2. **SkillCase ở môn/khái niệm thứ hai** — mẫu hiện tại là một khái niệm; cần ca thứ hai
   trước khi tin abstraction ở quy mô.
3. **P1 repos** — KT-PSP (process-level knowledge tracing) liên quan trực tiếp Camera
   Tutor: chấm *cách làm*, không chỉ *đáp số*.
