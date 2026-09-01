# DOCTRINE GOVERNANCE — AI Workforce addendum (EN/VI)
# Binding từ Discovery Freeze 2026-07-20 · Epic WORKIZEN-ALIGNMENT-001

> Addendum này đứng CÙNG các role contracts (`FOUNDER.md`, `PM_AGENT.md`, `DEVELOPER_AGENT.md`, `QA_DEPLOY_AGENT.md`) — không thay thế. Hierarchy: Constitution → Core Charter → **Product Doctrine v1.0** → Positioning → ADR → Epic/Story → Implementation. Đọc `docs/CANONICAL-INDEX.md` trước khi làm bất kỳ việc gì.

## 1 · Default agent mode (EN) / Chế độ mặc định

**From now the default is: Build · Review · Measure · Refactor · Operate.**
**No longer default: Discover · Invent vision · Create new architecture · Expand product scope · Research competitors.**

Competitor research CHỈ được phép khi có đủ 4 điều: Founder yêu cầu trực tiếp · issue rõ ràng · câu hỏi quyết định cụ thể · giới hạn thời gian + output.

## 2 · Pre-task checklist (MỌI agent, TRƯỚC khi đề xuất/nhận task)

```
[ ] 1. Task phục vụ Doctrine Article nào? (không trả lời được → không làm)
[ ] 2. Task tác động metric nào? (M1-M4 hoặc "none — vì sao vẫn đáng làm?")
[ ] 3. Owner repository là đâu? (Hub/Compute/TổngTài/Portal/Runtime/Router)
[ ] 4. Capability đã tồn tại trong registry chưa? (id + status)
[ ] 5. Có duplication không? (check registry + audit report)
[ ] 6. Có vượt Product Boundary không? (docs/product/doctrine/product-boundaries.md)
[ ] 7. Có cần Founder approval không? (L1/L2/L3 — D-118)
```

## 3 · Epic template (bắt buộc mọi Epic mới — Jira description)

```
## Doctrine Article: <Article + số Principle>
## Product Principle: <#>
## Capability Owner: <registry id + repo>
## Target Experience: <experience-architecture.md row>
## Target User: <primary/secondary/future — customer-definition.md>
## Expected metric impact: <M1-M4 + hướng>
## Evidence or hypothesis: <VERIFIED evidence hoặc HYPOTHESIS ghi rõ>
## Non-goals: <danh sách>
## Boundary check: <đã đối chiếu product-boundaries.md — kết quả>
## Human approval level: <L1/L2/L3>
```

**Story/Task:** phải trace được về Epic (và qua Epic về Article). Không trace được → **KHÔNG tự động chạy** → chuyển trạng thái/label `needs-product-alignment` → KHÔNG xoá issue.

**ADR mới:** bắt buộc mục "Doctrine Article affected" + backward-compatibility + migration impact. **UX proposal:** bắt buộc Target Experience + A3 check (không lộ API key/BYOK/provider/model/local-runtime cho primary path).

## 4 · Labels (Jira — tái sử dụng, không đẻ thêm)

`doctrine-aligned` · `doctrine-review` · `doctrine-conflict` · `insufficient-evidence` · `historical` · `retire-candidate` · `needs-product-alignment` · marker chống chạy lại: **`doctrine-audit-completed`**.

**Re-audit CHỈ khi:** doctrine version đổi · code/scope đổi đáng kể · Founder yêu cầu · evidence mới. Task đã mang `doctrine-audit-completed` thì agent KHÔNG audit lại — chống vòng lặp vô hạn.

## 5 · Non-blocking sponsor rule (giữ nguyên, nhắc lại)

Task cần Founder quyết → chuyển **Waiting** + ghi đầy đủ context/options/recommendation/risk → agent tiếp tục task độc lập khác → KHÔNG suy đoán quyết định chiến lược thay Founder.

## 6 · Ràng buộc tự động hoá (từ Epic ALIGNMENT-001, Part 13)

Agent ĐƯỢC tự động: docs merge/index/status/metadata · evidence collection · audit reports · Jira issue · label/template update không phá workflow · archive marking · agent-instruction update · low-risk doc corrections khớp live reality.
Agent KHÔNG ĐƯỢC tự động: đổi vision · thêm product/architecture layer · merge repository · xoá feature · tắt production capability · đổi subscription/customer segment · đổi ADR accepted · telemetry nhạy cảm · refactor lớn · merge production code cần Founder approval.
