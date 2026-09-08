/// MẨU TRÍCH CÓ TRỌN NGHĨA KHÔNG?
///
/// Máy thật, thẻ «Bạn có biết?» trên Home:
///
///   «Cô-lôm-bô tìm ra châu Mỹ (1492 - 1502), cuộc thám hiểm của Ph.»
///
/// Câu dừng giữa một cái tên. Trẻ đọc nó như một sự thật đã nói xong.
///
/// Đo trên kho hiện có: 21/38 mẩu (55%) cụt một đầu — body bị cắt ở khoảng 300
/// ký tự lúc trích, nên phần lớn dừng giữa câu hoặc giữa tên.
///
/// ⭐ THÀ BỎ THẺ CÒN HƠN ĐƯA MỘT KHẲNG ĐỊNH DỞ DANG. Đây không phải chuyện đẹp
/// xấu: một nửa câu về lịch sử là một câu SAI về lịch sử.
library;

final _startsMidSentence = RegExp(r'^[,;:)\]…\-–]');
final _endsSentence = RegExp(r'[.!?…"»]\s*$');

/// ⚠ `[A-ZÀ-Ỹ]` KHÔNG phải «chữ hoa tiếng Việt». Đó là dải mã U+00C0–U+1EF8 và
/// nó CHỨA CẢ CHỮ THƯỜNG CÓ DẤU (á, ê, í…). Dùng nó để dò viết tắt thì «…phiêu
/// lưu kí.» cũng bị coi là viết tắt. Phải hỏi thẳng từng ký tự.
bool _isUpper(String c) => c.toUpperCase() == c && c.toLowerCase() != c;

/// Từ CUỐI CÙNG trước dấu chấm hết có phải một chữ viết tắt («… của Ph.»)?
/// Dấu chấm ấy là chấm viết tắt, không phải chấm hết câu.
bool _endsWithAbbrev(String t) {
  final m = RegExp(r'(\S+)\.\s*$').firstMatch(t);
  if (m == null) return false;
  final w = m.group(1)!;
  return w.isNotEmpty && w.length <= 3 && _isUpper(w[0]) &&
      w.substring(1).split('').every((c) => !_isUpper(c));
}

/// `true` khi mẩu này đọc trọn nghĩa cả hai đầu.
///
/// Cụt ĐẦU: bắt đầu bằng chữ thường hoặc dấu câu — phần mở đã mất.
/// Cụt ĐUÔI: không kết bằng dấu câu, hoặc kết bằng một chữ viết tắt ngắn
/// («… của Ph.») — dấu chấm ấy là chấm viết tắt, không phải chấm hết câu.
bool isCompleteSnippet(String? text) {
  final t = (text ?? '').trim();
  if (t.isEmpty) return false;
  final first = t[0];
  if (first.toLowerCase() == first && first.toUpperCase() != first) return false;
  if (_startsMidSentence.hasMatch(t)) return false;
  if (_endsWithAbbrev(t)) return false;
  return _endsSentence.hasMatch(t);
}
