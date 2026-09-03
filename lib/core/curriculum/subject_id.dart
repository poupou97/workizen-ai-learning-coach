/// Mã môn từ TÊN MÔN, tất định — không bảng tra cứng theo tên.
///
/// Trước đây `subject_home_screen` có một `switch` theo tên môn để đặt
/// `subjectId` khi ghi phiên: `'Vật lí' => 'vat-li'`, `'Hoá học' => 'hoa-hoc'`,
/// còn lại rơi hết về `'khoa-hoc'`. Thêm một môn khoa học nữa (Sinh học chẳng
/// hạn) là bằng chứng của trẻ bị ghi SAI MÔN mà không ai báo — và đó đúng là
/// loại nhánh-theo-tên-môn mà cổng kiến trúc cấm trong runtime dùng chung.
///
/// Nay mã môn suy ra từ chính tên: bỏ dấu, `đ`→`d`, gạch nối. Thêm môn mới
/// không phải sửa một dòng nào.
library;

String subjectIdOf(String subject) {
  const marks = {
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    // ⭐ `đ` KHÔNG phải `d` có dấu — bỏ dấu kiểu nào cũng không ra `d`.
    'đ': 'd',
  };
  final buf = StringBuffer();
  for (final ch in subject.toLowerCase().split('')) {
    final plain = marks[ch] ?? ch;
    if (RegExp(r'[a-z0-9]').hasMatch(plain)) {
      buf.write(plain);
    } else if (buf.isNotEmpty && !buf.toString().endsWith('-')) {
      buf.write('-');
    }
  }
  final s = buf.toString();
  return s.endsWith('-') ? s.substring(0, s.length - 1) : s;
}
