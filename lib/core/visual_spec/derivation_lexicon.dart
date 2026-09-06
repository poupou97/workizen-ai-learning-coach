/// ⭐ LANE E2 (round 5) — «VÌ SAO SAM VẼ THẾ NÀY» nói theo LUẬT SINH, không
/// theo kiểu Dart.
///
/// LỖI ĐANG CÓ trong `visual_view.dart` (`_why`): câu giải thích được chọn
/// bằng `switch (s) { ProcessSemantic() => … }`, tức theo KIỂU, nên MỌI
/// `ProcessSemantic` — dù sinh bởi luật nào, môn nào — đều nói câu tả đúng
/// luật của Bài 17: «các bước đánh dấu «·» theo thứ tự». Với một quy trình
/// Tin học đánh số 1./2./3. câu đó SAI, mà không test nào bắt được: kiểu vẫn
/// đúng, chữ vẫn hiện.
///
/// Ở đây câu giải thích tra theo `derivationRule`. Luật LẠ ⇒ câu TỔNG QUÁT
/// KHÔNG khẳng định gì về cách sách trình bày (fail-closed về mặt chữ nghĩa),
/// chứ không mượn tạm câu của luật khác.
library;

/// Tra câu giải thích cho một luật sinh. `null` ⇒ chưa có mục từ.
String? childExplanationForRule(String rule) => _lexicon[rule];

/// Câu dùng khi luật chưa có mục từ — KHÔNG mô tả cách sách trình bày, chỉ
/// nói đúng thứ SAM chắc chắn làm.
const String genericRuleExplanation =
    'SAM xếp lại các ý sách viết trong bài này, giữ nguyên lời sách và không '
    'thêm ý nào. Con chạm vào từng ô để xem đúng chỗ sách viết nhé.';

/// Câu giải thích trẻ đọc cho một hình, dựng từ TẤT CẢ luật đã tham gia.
/// Nhiều luật ⇒ nối các câu đã biết; không luật nào biết ⇒ câu tổng quát.
String childExplanationForRules(Iterable<String> rules) {
  final seen = <String>[];
  for (final r in rules) {
    final line = childExplanationForRule(r);
    if (line != null && !seen.contains(line)) seen.add(line);
  }
  return seen.isEmpty ? genericRuleExplanation : seen.join(' ');
}

/// Mục từ — mỗi dòng gắn với MỘT luật có thật trong kho, viết bằng lời trẻ và
/// KHÔNG mang mã máy (test «không mã máy trên màn trẻ» quét chuỗi này).
const Map<String, String> _lexicon = {
  'tsl-enumerated-steps-v1':
      'Sách viết hoạt động này thành từng bước có dấu đầu dòng theo thứ tự — '
          'SAM xếp đúng thứ tự sách, giữ nguyên lời sách, không thêm bước nào.',
  'tsl-summary-methods-v1':
      'Phần tóm tắt cuối bài liệt kê từng cách kèm chú thích — SAM xếp thành '
          'bảng để con so sánh, chữ vẫn là chữ sách.',
  'prose-dated-events-v1':
      'Sách viết các mốc kèm năm trong ngoặc — SAM lấy đúng những mốc đó và '
          'xếp theo năm sách nêu, không đoán thêm năm nào.',
  'story-attribution-v1':
      'Cuối mỗi câu chuyện sách ghi «Theo …» — SAM chép lại đúng dòng đó để '
          'con biết chuyện lấy từ đâu.',
  'synthetic':
      'Đây là bài MẪU để thử máy — các câu trong hình không phải lời sách '
          'thật, con đừng học thuộc nhé.',
};

/// Các luật đã có mục từ — cho test và cho báo cáo phủ.
Set<String> get knownDerivationRules => _lexicon.keys.toSet();
