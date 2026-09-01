# ADR-006 — Local-first K-12 Knowledge: SAM KNOWLEDGE PACK trên thiết bị

**Ngày:** 2026-09-01 · **Trạng thái:** ACCEPTED (L1 — QUYẾT ĐỊNH FOUNDER, không phải agent tự quyết)
**Phạm vi:** ràng buộc kiến trúc cho toàn bộ chương trình E15 (K-12 Ingestion) + E14 (RAG) + mobile app

---

## QUYẾT ĐỊNH

Tri thức giáo dục của «Học cùng SAM» lưu **LOCAL TRÊN THIẾT BỊ** ở mọi chỗ khả thi kỹ thuật.
App lớn / footprint tri thức local lớn là **CHẤP NHẬN ĐƯỢC**. KHÔNG tối ưu kiến trúc quanh
cloud-hosted RAG theo mặc định.

**Nguyên tắc chi phí:** BUILD ONCE → DISTRIBUTE → RETRIEVE LOCALLY MANY TIMES — thay vì trả
tiền remote-retrieval cho MỖI tương tác học.

Động cơ: chi phí CDN/backend lặp lại ≈ 0 cho retrieval thường nhật · học offline · độ trễ
thấp · riêng tư · chi phí vận hành dự đoán được.

## KIẾN TRÚC ĐÍCH

```
RAW CORPUS/PDF  ──chỉ tồn tại trong BUILD PIPELINE──▶  SAM KNOWLEDGE PACK (compiled)
                                                        │ Curriculum Graph · Concept · SkillCase
                                                        │ Method · LearningObjective · ContentUnit
                                                        │ edges · ExerciseSkillMap · provenance
                                                        │ FTS/lexical index · formula index
                                                        │ (embeddings CHỈ khi có benefit đo được)
                                                        ▼
Mobile app tiêu thụ PACK:  query/camera → CanonicalProblem → LOCAL graph lookup
   → LOCAL retrieval → EvidencePack → pedagogical decision → SAM
```
KHÔNG ship PDF thô 20GB chỉ để retrieval. LLM inference có thể remote — ĐỘC LẬP với retrieval.

## RANH GIỚI CLOUD (tách bạch, không always-on)
Cloud CHỈ có thể giữ: LLM inference · sync tài khoản (opt) · backup (opt) · analytics có
kiểm soát riêng tư · PHÂN PHỐI pack update. Không backend RAG thường trực khi chưa có
necessity đo được.

## BẰNG CHỨNG HỘI TỤ (quyết định này KHỚP mọi thứ đã đo)
- Kernel WAL đã 100% local (BKT/replay/summary/diagnosis) [PRIMARY].
- Safety doc: local-first = biện pháp an toàn mạnh nhất; CV 5588: trường không được ép tài
  khoản ⇒ phân phối không-tài-khoản/offline là lợi thế tuân thủ [PRIMARY/OFFICIAL].
- WAL-41: retrieval đúng-sư-phạm cần metadata+graph+BM25 — toàn bộ chạy local được (Hub đã
  ship BM25 local làm tiền lệ [OSS]); skillcoco local-first cùng stack [OSS].

## HỆ QUẢ THI HÀNH (đã vào Jira)
1. GĐ8 (WAL-81) đổi đích: build **artifacts local pack**, không phải service.
2. Nhiệm vụ mới: **Pack compiler + benchmark đóng gói A/B** (FULL K-12 vs MODULAR
   Core+Grade+prerequisite-neighborhood) — KHÔNG mặc định modular thắng, benchmark cả hai.
3. **Storage benchmark** gắn vào WAL-73/74/82: đo bytes từng tầng (PDF→OCR→ContentUnit→
   graph→FTS→provenance→pack) + tỷ số nén + NGOẠI SUY footprint 1–12 từ MẪU ĐO,
   không ước từ cỡ PDF. Storage KHÔNG phải trục tối ưu chính — nhưng phải ĐO.
4. **Mobile POC** (thiết bị thật, 100MB→500MB→1GB→2GB+): size/mở DB/latency graph+FTS/
   memory/update-migration/corruption-recovery/backup behavior.
5. **Update strategy:** delta có ký + versioned (v17 + signed delta → v18) — không bắt tải
   lại nhiều GB cho một sửa nhỏ; provenance phiên bản giữ nguyên vẹn.

## KHÔNG HY SINH
Cấu trúc sư phạm · provenance · offline · độ đúng retrieval — KHÔNG đánh đổi lấy vài trăm MB.
