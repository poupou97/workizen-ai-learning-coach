/// ROUND 3 B5 (audit 05 §1 «raw source/document ids in UI») — chữ TRẺ ĐỌC
/// cho hai loại mã nội bộ vẫn đang lọt ra màn:
///
/// - mã môn (`khtn`, `dia-li`) sinh bởi `subjectIdOf` khi ghi phiên;
/// - mã sách (`06-sgk-khoa-hoc-tu-nhien-6`) trên dòng nguồn của hình / tư liệu.
///
/// Luật: chỉ dịch khi CHẮC (bảng tra cố định, hoặc tên sách lấy từ chính mục
/// lục pack đang mở). Không chắc ⇒ trả lại mã gốc — mã thô khó đọc nhưng
/// THẬT; một cái tên đoán mò thì không.
library;

const _subjectNames = <String, String>{
  'toan': 'Toán',
  'tieng-viet': 'Tiếng Việt',
  'ngu-van': 'Ngữ văn',
  'tieng-anh': 'Tiếng Anh',
  'khtn': 'Khoa học tự nhiên',
  'khoa-hoc-tu-nhien': 'Khoa học tự nhiên',
  'khoa-hoc': 'Khoa học',
  'vat-li': 'Vật lí',
  'hoa-hoc': 'Hoá học',
  'sinh-hoc': 'Sinh học',
  'lich-su': 'Lịch sử',
  'dia-li': 'Địa lí',
  'ls-dl': 'Lịch sử và Địa lí',
  'lich-su-va-dia-li': 'Lịch sử và Địa lí',
  'tin-hoc': 'Tin học',
  'cong-nghe': 'Công nghệ',
  'gdcd': 'Giáo dục công dân',
  'giao-duc-cong-dan': 'Giáo dục công dân',
  'am-nhac': 'Âm nhạc',
  'mi-thuat': 'Mĩ thuật',
  'the-duc': 'Giáo dục thể chất',
  'giao-duc-the-chat': 'Giáo dục thể chất',
  'tu-nhien-va-xa-hoi': 'Tự nhiên và Xã hội',
  'dao-duc': 'Đạo đức',
  'hoat-dong-trai-nghiem': 'Hoạt động trải nghiệm',
};

/// Tên môn trẻ đọc từ mã môn; mã lạ ⇒ trả lại mã (không bịa).
String subjectDisplayName(String subjectId) =>
    _subjectNames[subjectId] ?? subjectId;

/// Dòng nguồn trẻ đọc: «SGK `tên sách` · trang N». Tên sách lấy từ
/// [bookTitles] (mã sách → tên trong mục lục pack); không có ⇒ giữ mã sách.
String childSourceLine({
  required String sourceDocumentId,
  required int? pagePrinted,
  Map<String, String> bookTitles = const {},
}) {
  final title = bookTitles[sourceDocumentId];
  final book = title == null ? sourceDocumentId : 'SGK $title';
  return pagePrinted == null ? book : '$book · trang $pagePrinted';
}
