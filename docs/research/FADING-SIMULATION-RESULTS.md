# WAL-87 — Fading simulation: ±1 (Wood) vs 4 policy đối chứng

**Ngày:** 2026-09-01 · **Maturity:** SIMULATED (không phải bằng chứng trẻ thật)
**Chạy trên kernel THẬT:** sự kiện = `LearningEvent` đúng taxonomy 7 loại; ước lượng =
`replayMastery` + `ConservativeBktPolicy`. Mã: `tool/sim/fading_sim.dart` ·
số liệu đầy đủ: `poc-out/sim/fading-sim.json` (gitignored — chạy lại 1 lệnh, seeded).

## Câu hỏi

Founder checkpoint §3: *«±1 fading là GIẢ THUYẾT»*. Mô phỏng 800 học sinh/ô ×
4 kịch bản học × 3 tốc độ học × 5 policy, budget 20 lần thử:

| Policy | Là gì |
|---|---|
| `wood-±1` | **giả thuyết**: sai → +1 nấc hỗ trợ, đúng → −1 (fade) |
| `jump-to-full` | phản mẫu Photomath: sai một lần → xem trọn lời giải |
| `never-help` | không bao giờ gợi ý |
| `fixed-hint` | luôn treo gợi ý nấc 1 |
| `random` | nấc ngẫu nhiên mỗi lượt |

**GIẢ ĐỊNH KHAI BÁO** (không phải sự thật đo được): ảnh hưởng của hỗ trợ lên
P(học) — 4 kịch bản `help-helps` / `help-neutral` / `zpd-flail-futile` (vật lộn
không dẫn dắt dạy rất ít — kịch bản mà giả thuyết Wood thực sự sống trong đó) /
`full-hurts`; và P(đúng | chưa biết, mức hỗ trợ) = 0.10/0.25/0.50/**0.95** (chép).

## Kết quả — cái gì BẤT BIẾN qua mọi kịch bản (đây mới là kiến thức)

**① `jump-to-full` bị nghiền ở MỌI ô.** Độc lập 0–3%, bằng chứng độc lập 6–7%,
hệ MÙ 96–99% (trẻ biết mà hệ không bao giờ thấy); ở `full-hurts` còn giảm nửa
việc học thật (35% vs 70%). Phản mẫu Photomath giờ có số, không chỉ có lập luận.

**② Hỗ trợ mà KHÔNG fade về độc lập = hệ mù vĩnh viễn.** `fixed-hint` dạy được
(học-được cao nhất bảng ở vài ô!) nhưng MISSED **100% ở mọi ô**: không một mảnh
bằng chứng độc lập nào ⇒ không bao giờ được claim ⇒ phụ huynh không bao giờ được
báo. **Nửa FADE (YOUR_TURN) không phải trang trí sư phạm — nó là CẢM BIẾN của
toàn hệ đo.** Đây là số liệu trực tiếp bảo vệ `SAM_YOUR_TURN` và luật trẻ-thử-trước.

**③ Claim gate V1 của kernel (≥2 độc lập/ca) yếu với học sinh chậm.** Đo với
gate V1 thật: FALSE TRUSTED lên 10–19% số claim ở wood-±1, **33–40%** ở
jump-to-full (pLearn 0.05). ⇒ ĐÃ SỬA: **ADR-007** — yêu cầu độc lập tăng theo
supportedCount (`+1 mỗi 4 lần có-hỗ-trợ`). Đo lại: FT về 0–2% mọi policy hỗ
trợ; CHI PHÍ nói thẳng: MISSED tăng 5→14% (hệ chờ lâu hơn mới khen — hướng sai
an toàn). Đối chứng never-help không đổi (0 hỗ trợ ⇒ dilution không chạm).

## Kết quả — cái gì KHÔNG phân xử được (nói thẳng)

`wood-±1` vs `never-help` **đổi ngôi theo kịch bản**: ở `zpd-flail-futile`
wood thắng áp đảo (77%/62% vs 21%/20% ở pLearn 0.05); ở `help-neutral` và
`full-hurts` never-help ngang hoặc nhỉnh hơn về độc lập và luôn hơn về độ giàu
bằng chứng (100% độc lập theo định nghĩa). Mô phỏng KHÔNG thể nói kịch bản nào
đúng với trẻ thật — đó là câu hỏi thực nghiệm (WAL-49), không phải câu hỏi mã.
**±1 GIỮ NGUYÊN trạng thái GIẢ THUYẾT.** Điều mô phỏng thêm được: nếu ±1 sai,
nó sai về phía dạy-quá-tay, không sai về phía làm hệ mù — trần MISSED của wood
≤8% ở mọi ô, so với 96–100% của hai policy hỗ-trợ-nặng.

## Giới hạn (đọc trước khi trích dẫn)

Không mô hình cảm xúc/bỏ cuộc (trẻ thật flail 20 lần sẽ bỏ — thiên vị
`never-help`); policy do HỆ chủ động (`hintShown`) trong khi UI WAL-86 là trẻ
chủ động xin (`hintRequested`) — chưa mô phỏng tác tử trẻ; budget 20; một ca
kỹ năng đơn lẻ; P(đúng|chép lời giải)=0.95 là giả định mạnh.
