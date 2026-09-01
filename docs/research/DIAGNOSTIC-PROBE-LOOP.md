# WAL-70 — Diagnostic Probe: hỏi-vì-thông-tin, vòng khép kín

**Ngày:** 2026-09-01 · **Maturity:** IMPLEMENTED (luật) + TESTED (5 test, 3 đột biến đỏ)
**Mã:** `lib/core/adaptive/diagnostic_probe.dart` · test `diagnostic_probe_test.dart`

## Vòng

```
attributeFailure ⇒ attributionUnresolved (≥2 nghi phạm)
      │
      ▼
nextProbe ⇒ MỘT bài NGẮN chỉ chạm MỘT ca nghi phạm  ──(không có bài cô lập?)──▶ null
      │                                                  GIỮ bất định — không đoán
      ▼
trẻ trả lời ⇒ bằng chứng vào log ca đó (đường attributeEvidence bình thường)
      │
      ▼
attributeFailure lần nữa ⇒ ① 1 nghi phạm → decide() uỷ quyền (CAN THIỆP)
                           ② vẫn ≥2     → probe kế nhắm ca ÍT bằng chứng nhất
                                          (ca vừa probe đã có bằng chứng ⇒ tự
                                          động xoay sang ca kia — không lặp vô ích)
```

## Đối chiếu construct văn liệu (KHÔNG bịa công thức — đúng AC)

| Construct | Nguồn gốc | Ta lấy gì | Ta KHÔNG lấy gì |
|---|---|---|---|
| CDA / Q-matrix (DINA họ) | diagnostic assessment | item ĐƠN thuộc tính nhận diện thuộc tính tốt nhất ⇒ probe bắt buộc single-requirement | không fit mô hình DINA — chưa có dữ liệu |
| CAT item selection | IRT/maximum information | "hỏi nơi bất định lớn nhất" ⇒ proxy ĐẾM bằng chứng độc lập (ít nhất = bất định nhất) | công thức Fisher information — chưa có tham số item hiệu chuẩn, giả vờ có là bịa |
| Active learning | uncertainty sampling | cùng nguyên tắc trên | acquisition function học được |
| Model tracing | ACT-R tutors | hoà bằng chứng ⇒ kiểm MÓNG trước (introducedGrade thấp trước) | truy vết production rule từng bước |

## Luật «khi nào probe vs dạy luôn» (tất định, có test)

- **1 nghi phạm ⇒ DẠY LUÔN** (`decide` uỷ quyền). Probe từ chối hoạt động —
  probe chỉ để mua thông tin còn thiếu, không phải nghi thức.
- **≥2 nghi phạm ⇒ PROBE**, thứ tự: ít bằng chứng độc lập nhất → introducedGrade
  thấp nhất → id (tất định tuyệt đối, doctrine F4).
- **Không có bài cô lập ⇒ null + GIỮ `attributionUnresolved`.** Quy lỗi sai địa
  chỉ tệ hơn không quy lỗi. UI nói thật «chưa biết con vướng đâu».

## Residual

- Probe UI chưa có (T1 hiện làm bài camera đơn lẻ) — khi có shell điều hướng,
  `isolateSkills` từ E1 sẽ đẩy sang màn probe.
- Chi phí probe chưa mô hình (mỗi probe = thời gian của trẻ); ngưỡng «tối đa
  mấy probe một phiên» chưa đặt — cần bằng chứng UX thật (WAL-49).
- `evidenceOf` quét tuyến tính các concept — đủ cho V0, cần index khi đa khái niệm.
