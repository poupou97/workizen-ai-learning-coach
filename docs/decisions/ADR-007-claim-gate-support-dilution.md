# ADR-007 — Claim gate pha loãng theo hỗ trợ

**Ngày:** 2026-09-01 · **Trạng thái:** ACCEPTED (L2, agent tự quyết — cơ chế;
hằng số 4 là GIẢ THUYẾT V1 chờ dữ liệu thật) · **Nguồn:** số đo WAL-87

## Vấn đề (đo được, không suy đoán)

Mô phỏng WAL-87 trên kernel thật: stream trộn nhiều luyện-có-hỗ-trợ claim «vững»
trên rất ít mẫu độc lập. Với gate V1 (`minIndependentPerCase = 2` + floor 0.6),
ở học sinh chậm (pLearn 0.05):

| Policy | FALSE TRUSTED (V1) | sau ADR-007 | MISSED (V1) | sau |
|---|---|---|---|---|
| wood-±1 (help-neutral) | **18.8%** số claim | 1.6% | 6% | 16% |
| wood-±1 (zpd) | **10.4%** | 1.3% | 5% | 14% |
| jump-to-full (zpd) | **33.3%** | 0.0% | 91% | 100% |
| never-help (đối chứng, 0 hỗ trợ) | 2.0% | 2.0% (không đổi) | 6% | 6% |

FALSE TRUSTED = tuyên «vững» khi sự thật là CHƯA biết — loại lỗi tệ nhất theo
doctrine (nói với phụ huynh điều không đúng về đứa trẻ).

## Quyết định

`SummaryPolicy.supportDilutionPerCase = 4`: cứ mỗi 4 lần trả-lời-có-hỗ-trợ,
yêu cầu bằng chứng độc lập của ca tăng thêm 1:

```
cần(ca) = minIndependentPerCase + supportedCount ~/ supportDilutionPerCase
volume  = evidenceCount / cần(ca)
```

Lý do cơ chế: trong stream nặng hỗ trợ, vài mẫu độc lập đang cõng toàn bộ kết
luận — phương sai thật của claim cao hơn hẳn con số `evidenceCount` gợi ý.
Knob có tên, có lý do, injectable — đúng luật no-arbitrary-constants (ADR-004).

## Bất biến giữ bằng test (đột biến gỡ dilution → đỏ)

1. Stream thuần độc lập (`supportedCount = 0`): hành vi KHÔNG đổi.
2. 3 độc lập + 16 hỗ trợ ⇒ `insufficientEvidence` (không phải `needsWork` —
   không đủ tin thì không kết luận theo HƯỚNG nào).
3. Rào VƯỢT ĐƯỢC: 6 độc lập + 16 hỗ trợ ⇒ lại `mastered` — không phải án chung
   thân cho trẻ cần nhiều gợi ý.

## Trade-off nói thẳng + residual

- MISSED tăng (5→14% ở wood/zpd): hệ CHỜ LÂU HƠN mới khen «vững». Hướng sai
  an toàn — phụ huynh thấy «đang tiến bộ», không thấy lời khen dối.
- ⚠️ Residual NGOÀI phạm vi ADR này: never-help vẫn FT 12.7% ở zpd/0.05 —
  do `minIndependentPerCase = 2` thấp với chuỗi đoán-may thuần độc lập.
  Đó là knob KHÁC; đụng vào cần bằng chứng riêng, không gộp vào đây.
