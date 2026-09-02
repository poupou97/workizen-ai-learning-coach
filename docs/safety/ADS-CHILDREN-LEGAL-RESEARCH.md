# WAL-125 — ADS FOR CHILDREN: LEGAL/COMPLIANCE RESEARCH (2026-09-02)

**RESEARCH-ONLY. KHÔNG production approval. Mọi cam kết compliance = Founder
+ lawyer.** Baseline hypothesis giữ nguyên: contextual + non-personalized;
Grade 1-2 = NO ADS; không ads trong learning loop; không rewarded-ads.

## 1. Việt Nam

- **NĐ 13/2023/NĐ-CP (bảo vệ dữ liệu cá nhân, hiệu lực 01/07/2023):** xử lý
  dữ liệu cá nhân TRẺ EM cần đồng ý của cha mẹ/người giám hộ, và của chính
  trẻ nếu ≥7 tuổi; dùng dữ liệu khách hàng cho marketing/quảng cáo phải có
  đồng ý trên cơ sở hiểu rõ nội dung/hình thức/tần suất. ⇒ personalized ads
  trên dữ liệu trẻ = rủi ro pháp lý cao nhất — khớp CẤM TUYỆT ĐỐI của ticket.
- **Luật Quảng cáo (VBHN 88/VBHN-VPQH 2025; Luật 75/2025/QH15 sửa đổi; NĐ
  342/2025/NĐ-CP hướng dẫn):** danh mục cấm quảng cáo (sữa thay thế sữa mẹ
  <24 tháng, dinh dưỡng bổ sung <6 tháng, bình bú/vú ngậm…) + hành vi cấm
  (kỳ thị, định kiến giới…); quảng cáo NHẮM TRẺ EM có danh mục nội dung
  không được thể hiện (điều khoản bảo vệ trẻ em — cần lawyer trích đúng điều
  số trong VBHN 2025). ⇒ mọi ad creative hướng trẻ cần human review theo
  danh mục cấm VN, không chỉ theo policy store.

## 2. Google Play — Families Policy

- App target trẻ em: CHỈ dùng **Families self-certified ads SDK**; mixed
  audience: bắt buộc **neutral age screen**, trẻ chỉ thấy non-personalized.
- Child-directed treatment: TẮT personalized/interest-based/remarketing.
- ⚠️ SAM hiện CẤM ad/analytics SDK bằng test pubspec-scan — nếu Founder
  ngày nào bật ads, chỉ SDK trong danh sách self-certified và phải sửa test
  một cách CÓ CHỦ ĐÍCH (đảo quyết định = thấy mình đảo).

## 3. Apple — Kids Category

- Mặc định KHÔNG third-party ads/analytics. Ngoại lệ hẹp: contextual ads với
  practices công bố công khai + HUMAN REVIEW ad creatives cho phù hợp tuổi;
  analytics không được thu IDFA/định danh/vị trí/thiết bị.

## 4. Bảng age-band × ads-type (đề xuất — Founder quyết)

| Band | Personalized | Contextual non-personalized | Rewarded | Trong learning loop |
|---|---|---|---|---|
| 1-2 (6-8t) | **FORBIDDEN** (NĐ13 + policy + doctrine) | **NO ADS** (hypothesis giữ) | FORBIDDEN | FORBIDDEN |
| 3-5 | FORBIDDEN | NEEDS-LEGAL (điều khoản QC trẻ em VN + Families SDK) | FORBIDDEN | FORBIDDEN |
| 6-9 | FORBIDDEN | NEEDS-LEGAL | FORBIDDEN | FORBIDDEN |
| 10-12 | FORBIDDEN (dưới 18 — dữ liệu cá nhân nhạy) | NEEDS-LEGAL | FORBIDDEN | FORBIDDEN |
| Teacher/Parent surface | NEEDS-LEGAL (người lớn — consent NĐ13) | ALLOWED-candidate (sau-session/library/utility) | FORBIDDEN | FORBIDDEN |

## 5. Câu hỏi cụ thể cho LAWYER

1. Điều khoản chính xác nào của Luật QC (VBHN 2025) liệt kê nội dung «không
   được thể hiện» trong quảng cáo nhắm trẻ em — áp cho app học tập thế nào?
2. NĐ13: cơ chế đồng ý «cha mẹ + trẻ ≥7 tuổi» — với ad CONTEXTUAL không thu
   dữ liệu cá nhân, có cần consent riêng không?
3. «Non-personalized» theo chuẩn Play/Apple có thỏa định nghĩa «không xử lý
   dữ liệu cá nhân» của NĐ13 không (IP/device-id kỹ thuật)?
4. NĐ 342/2025 có yêu cầu thủ tục nào cho quảng cáo trên «mạng» áp dụng cho
   app giáo dục không (nhãn, tần suất, thời điểm)?
5. Nếu chỉ đặt ads ở TEACHER surface (người lớn), nghĩa vụ nào còn lại?

## 6. STOP

Research dừng ở đây. Không chọn network, không implement, không cam kết.
Trình Founder + lawyer quyết.

Nguồn: support.google.com/googleplay/android-developer/answer/9893335 ·
answer/9900633 (self-certified SDK) · developer.apple.com App Review
Guidelines (Kids) · thuvienphapluat.vn (NĐ13/2023; Luật 75/2025/QH15;
VBHN 88/2025; QC nhắm trẻ em) · NĐ 342/2025/NĐ-CP.
