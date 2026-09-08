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

/// ⭐ TÊN MÔN VIẾT TẮT TRÊN GIÁ SÁCH — chữ registry, không phải mã môn.
///
/// Máy thật lớp 11: Home ghi «HĐTN-HN», giá sách ghi «GDKT&PL». Đó là tên
/// `subject` của registry, KHÔNG đi qua [subjectDisplayName] (bảng kia tra
/// theo *mã* `khtn`, `dia-li`). Trẻ lớp 6 không giải mã được «TN&XH».
///
/// Tám chữ tắt có trong corpus, mỗi chữ được XÁC MINH CHÉO bằng định danh
/// sách của chính môn ấy — 52/52 cuốn xác nhận (vd «GDKT&PL» ⇔ mọi cuốn đều
/// mang `giao-duc-kinh-te-va-phap-luat`). Hai nguồn độc lập đồng ý thì mới
/// dịch; chữ tắt lạ ⇒ giữ nguyên, không đoán.
const _subjectAbbreviations = <String, String>{
  'GDCD': 'Giáo dục công dân',
  'GDKT&PL': 'Giáo dục kinh tế và pháp luật',
  'GDTC': 'Giáo dục thể chất',
  'HĐTN': 'Hoạt động trải nghiệm',
  'HĐTN-HN': 'Hoạt động trải nghiệm, hướng nghiệp',
  'KHTN': 'Khoa học tự nhiên',
  'LS&ĐL': 'Lịch sử và Địa lí',
  'TN&XH': 'Tự nhiên và Xã hội',
};

/// Tên môn trẻ đọc, từ TÊN môn của mục lục (không phải mã). Không nằm trong
/// bảng ⇒ trả lại nguyên văn: tên đầy đủ đã đọc được thì không cần đụng vào.
String subjectLabel(String subject) =>
    _subjectAbbreviations[subject.trim()] ?? subject;

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

/// Mã sách → tên sách, nạp từ mục lục pack khi app đọc pack (main.dart).
/// Tích luỹ qua các lớp đã mở (tên ổn định theo mã). Không có ⇒ hàm dưới
/// giữ mã.
final Map<String, String> knownBookTitles = <String, String>{};

/// Dòng nguồn của một mẩu «Kho khám phá» (StoryItem chỉ mang trang PDF):
/// «Nguồn: SGK Ngữ văn 6 · Tập 1 · trang PDF 26». Nói «trang PDF» vì đó là
/// điều dữ liệu có — không đội lốt số trang in.
String storySourceLine({
  required String sourceDocumentId,
  required int pagePdf,
  Map<String, String>? bookTitles,
}) {
  final title = (bookTitles ?? knownBookTitles)[sourceDocumentId];
  final book = title == null ? sourceDocumentId : 'SGK $title';
  return 'Nguồn: $book · trang PDF $pagePdf';
}
