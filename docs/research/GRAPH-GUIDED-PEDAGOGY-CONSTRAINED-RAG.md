# WAL-66 — Graph-guided, Pedagogy-constrained RAG (nghiên cứu, CHƯA implement)

**Ngày:** 2026-09-01 · **Trạng thái:** RESEARCH · thang bằng chứng: [PRIMARY]=đo trong repo/corpus ·
[OSS]=mã đã đọc · [ACADEMIC]=văn liệu (kiểm trích dẫn lại khi soạn ADR) · [HYP]=giả thuyết
**Anti-pattern bị cấm (Founder §16):** PDF → chunk tuỳ tiện → embedding → topK → LLM.

## 0. Vì sao RAG ngây thơ CHẾT với sản phẩm này — từ bằng chứng ĐÃ ĐO

1. [PRIMARY] Thin slice đã chứng minh: biết `grade=5 · concept=quy-dong · case=non-divisible`
   thu tập phương pháp 3→1 **không cần tìm kiếm ngữ nghĩa nào** — lọc cấu trúc mạnh hơn tương
   đồng ngữ nghĩa với dữ liệu này.
2. [PRIMARY] Ranh giới sư phạm là bất biến P0: BCNN xuất hiện 0 lần trong 53 trang Toán 5 —
   một retriever ngữ nghĩa sẽ VUI VẺ kéo đoạn BCNN từ sách lớp 6 về cho câu hỏi quy đồng lớp 5
   (giống nhất về nghĩa!). **RETRIEVED ≠ PEDAGOGICALLY PERMITTED** không phải khẩu hiệu — nó
   là chính TutorScope, và filter phải đứng SAU retrieval, TRƯỚC SAM.
3. [PRIMARY] Chunk theo token xoá đúng thứ đắt nhất: cấu trúc "trường hợp" (SGV ×13),
   vai trò bài (dạy/ôn/dùng — `ExposureRole`), số trang in ≠ số trang PDF.

## 1. SOURCE PLANE (§17)

- `SourceDocument{sourceId, publisher, edition, schoolYear, grade, subject, series,
  licenseStatus, checksum, version}` — mở rộng tự nhiên của `Provenance.sourceId` hiện có
  [PRIMARY: provenance.dart đã cấm đường-dẫn-tệp làm id].
- **Embedding/index KHÔNG BAO GIỜ là nguồn sự thật** — index là dẫn xuất xoá-dựng-lại được
  từ ContentUnit; cùng seam pháp lý `KnowledgeContentProvider` (đổi corpus = đổi một
  implementation). `licenseStatus` kế thừa `ContentLicense` (localResearchOnly…) — Legal Gate
  giữ nguyên, không commit corpus.

## 2. CONTENT PLANE — ContentUnit sư phạm (§18)

- Loại unit ứng viên (đối chiếu corpus thật): `Lesson · Section(mục — ranh giới ca! xem
  concept #2) · Definition · Rule("Ghi nhớ" — TV5 tr.66 có khung Ghi nhớ tường minh) ·
  Example · WorkedExample · Exercise · TeachingNote(SGV "Lưu ý") · Glossary(Toán 9 tr.119) ·
  Figure`. [PRIMARY: tất cả đã gặp trong OCR]
- Giữ: sourceId · trang IN (không phải trang PDF) · bbox · lessonId · loại · conceptIds/
  caseIds nếu đã map · provenance đầy đủ. `KnowledgeChunk` hiện có ~80% khung này
  (id/text/provenance/contentType/conceptIds/methodIds) — thiếu bbox + loại chuẩn hoá + caseIds.
- [HYP] Đơn vị NHỎ NHẤT nên là Section/mục chứ không phải Lesson: bằng chứng concept #2 —
  ranh giới ca nằm giữa các MỤC trong một bài.

## 3. GRAPH FIRST, SEARCH SECOND (§19)

```
Problem Understanding (ConfirmedProblem!) → Concept/SkillCase/LearningStage
  → graph neighborhood (prerequisite xuyên lớp + exposures)
  → CONSTRAINED SCOPE (grade ≤ stage, bài đã dạy, ca đúng)     ← GRAPH quyết ĐÂU
  → hybrid retrieval TRONG scope đó                            ← retrieval quyết GÌ
```
- Stack tìm kiếm phân tầng theo bằng chứng hiện có: ① metadata filter [PRIMARY — đã chứng
  minh mạnh] → ② graph traversal (prerequisite/exposure — đã có CurriculumEdge) → ③ BM25
  [OSS: Hub đã ship BM25-with-citations local] → ④ vector similarity (CHƯA có bằng chứng cần;
  [HYP] với công thức toán, ký hiệu giống nhau nghĩa khác nhau — vector-only đáng ngờ) →
  ⑤ formula/symbol match (dài hạn).
- [ACADEMIC] họ GraphRAG/knowledge-graph-RAG là prior art cho graph-guided — kiểm trích dẫn
  khi ADR; điểm KHÁC của WAL: graph của ta là đồ thị CHƯƠNG TRÌNH có provenance + ranh giới
  sư phạm, không phải đồ thị trích tự động từ văn bản.

## 4. EVIDENCEPACK (§20)

Cấu trúc ứng viên (chỉ field có lý do hôm nay):
`{learningContext(stage, concept, case), retrievedEvidence[](unit + citation trang in),
allowedMethods[] / prohibitedMethods[] (TỪ TutorScope — không phải từ retriever),
retrievalConfidence, unresolvedQuestions[], versions(knowledgeModel, retrievalPolicy, source)}`
— version fields ở đây CÓ lý do (khác perception §12): EvidencePack là đầu vào của LLM,
audit "SAM nói X dựa trên gì" cần đúng phiên bản. [HYP — xác nhận khi làm POC]

## 5. FAIL CLOSED (§21) — ánh xạ thẳng vào khung hiện có

| Trạng thái | Hành vi SAM | Tương đương đã có |
|---|---|---|
| NO_EVIDENCE | "phần này SAM chưa có tài liệu" | remediateKnowledgeMissing |
| LOW_CONFIDENCE | nói "chưa chắc", không suy diễn | diagnosticConfidenceLow |
| SOURCE_CONFLICT | nêu hai nguồn, không tự phân xử | (mới) |
| VERSION_MISMATCH | từ chối trộn phiên bản sách | (mới) |
| FUTURE_KNOWLEDGE_ONLY | "phần này thuộc chương trình lớp N" — KHÔNG dạy trước | TutorScope + RemediationStatus [PRIMARY] |
| INSUFFICIENT_PROVENANCE | không trích như lời sách | citable rules [PRIMARY] |

## 6. STUDENT BOUNDARY (§22)

Knowledge Store (corpus/graph/method — dùng chung mọi học sinh) ≠ Student Store
(EvidenceLog/mastery/summary — của từng em, local-first). **Không embed lịch sử/chat của
trẻ vào corpus nội dung.** Student state chỉ tham gia LẬP KẾ HOẠCH retrieval (chọn scope),
không thành tài liệu. [PRIMARY: kiến trúc hiện tại đã tách đúng như vậy — lib/core/knowledge
vs lib/core/student; ghi thành luật để không ai "tiện tay" gộp khi làm RAG.]

## 7. BENCHMARK GIÁO DỤC (§23) — không chỉ Recall@K

Source Recall · Curriculum Precision (đúng lớp/bộ sách) · SkillCase Precision · Citation
Correctness (đúng trang IN) · Unsupported Claim Rate · **Future-Knowledge Leakage Rate ≈ 0**
· **Method Permission Violation Rate ≈ 0** — hai chỉ số cuối là điều kiện sống, cùng vai với
FTP Rate bên perception (WAL-63). Ground truth khả thi ngay: bộ câu hỏi quy-dong/so-sanh
với nhãn "được phép trả lời bằng gì ở stage nào" — sinh từ chính golden tests.

## 8. KẾT LUẬN & VIỆC MỞ

- WAL-41 (Retrieval POC) = bước POC của epic này: đo ①+②+③ trên corpus đã OCR với benchmark
  §7 TRƯỚC khi thêm vector — nếu metadata+graph+BM25 đã đạt, vector là chi phí không bằng chứng.
- Chưa ADR — sau POC. Không implement gì trong task này (đúng AC).
