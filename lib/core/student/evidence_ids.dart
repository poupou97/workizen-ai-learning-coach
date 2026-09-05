/// ⭐ WAL-210 (B-lane, audit check C1) — ĐỊNH DANH SỰ KIỆN DUY NHẤT.
///
/// Trước đây mọi surface sinh `eventId = '$exerciseId#$seq'` với `seq` đếm
/// lại từ 0 mỗi lần mở màn. Mở lại CÙNG một bài ⇒ CÙNG một bộ id
/// (`cur:…:b6#0`, `#1`…). Log append-only hôm nay không khử trùng lặp nên
/// chưa mất gì — nhưng id không còn là ĐỊNH DANH: mọi cơ chế dedupe/audit
/// về sau sẽ nuốt mất lần làm thứ hai một cách im lặng (`replay_audit_test`
/// đã giữ bất biến này cho `attributeEvidence`, chưa giữ cho surface).
///
/// Hợp đồng (PROPOSED — D2, chỉ vừa đủ cho vòng này):
/// - Mỗi PHIÊN mở surface có một [sessionToken] cố định, sinh ĐÚNG MỘT LẦN
///   lúc mở; mọi id trong phiên là hàm tất định của (exerciseId, token, seq).
/// - Token = thời điểm mở (micro-giây, cơ số 36) + số thứ tự trong tiến
///   trình. Thời điểm phân biệt các lần mở QUA khởi động lại; số thứ tự phân
///   biệt hai phiên mở trong cùng một micro-giây (đồng hồ tiêm cố định trong
///   test, hoặc máy có đồng hồ thô).
/// - `exerciseId` trên `LearningEvent` KHÔNG đổi — vẫn là định danh bài; id
///   sự kiện chỉ thêm phần phiên, dữ liệu cũ (`…#0`) vẫn đọc được nguyên vẹn.
library;

int _ordinal = 0;

/// Token phiên — gọi MỘT LẦN khi mở surface, rồi giữ cố định.
String newEvidenceSessionToken(DateTime openedAt) {
  final t = openedAt.microsecondsSinceEpoch.toRadixString(36);
  final n = (_ordinal++).toRadixString(36);
  return '$t-$n';
}

/// `<exerciseId>@<sessionToken>#<seq>` — tất định trong phiên, duy nhất
/// giữa các phiên.
String evidenceEventId({
  required String exerciseId,
  required String sessionToken,
  required int seq,
}) =>
    '$exerciseId@$sessionToken#$seq';
