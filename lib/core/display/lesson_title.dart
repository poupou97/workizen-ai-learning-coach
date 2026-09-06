/// ROUND 7 · WS-R — CÁCH VIẾT HOA TIÊU ĐỀ BÀI, MỘT LUẬT DUY NHẤT.
///
/// Lỗi máy thật (LS&ĐL 5 Bài 8, vòng 6): fixture mang tiêu đề đúng chính tả
/// **«Đấu tranh giành độc lập thời kì Bắc thuộc»** — lấy nguyên từ mục lục in
/// — nhưng màn hình hiện **«thời kì bắc thuộc»**. Không test nào bắt được;
/// một người cầm máy thật đọc ra.
///
/// NGUYÊN NHÂN GỐC: `LessonDocument.titleCase` `toLowerCase()` TOÀN CHUỖI rồi
/// mới viết hoa lại đầu câu. Phép biến đổi ấy sinh ra cho tiêu đề **mined IN
/// HOA** («HỖN HỢP. TÁCH CHẤT…», Nokia n1 D1), nhưng **điều kiện tiên quyết
/// của nó chưa bao giờ được kiểm**: một tiêu đề đã có chữ thường là tiêu đề
/// ĐÃ ĐÚNG CHÍNH TẢ (từ mục lục in / người soạn), và hạ nó xuống chữ thường
/// là **phá thông tin**, không phải chuẩn hoá nó. Tiếng Việt không suy ra
/// được danh từ riêng từ hình dạng chuỗi: «Bắc thuộc», «Ngô Quyền», «Bạch
/// Đằng» chỉ còn đúng nếu ta **đừng đụng vào**.
///
/// SỬA TIỀN ĐỀ, KHÔNG NỚI CỔNG: luật vẫn viết hoa lại tiêu đề IN HOA y như
/// trước; nó chỉ thôi làm thế với chuỗi **đã mang chữ thường**. Không ký tự
/// nào bị bịa thêm, không danh từ riêng nào được đoán.
///
/// GIỚI HẠN CÒN LẠI, NÓI THẲNG: với tiêu đề **thật sự IN HOA toàn bộ**
/// («THỜI KĨ BẮC THUỘC» — chính là tiêu đề pipeline của bài này trước khi
/// `lesson-title-v1` lấy tên từ mục lục), thông tin hoa/thường **đã mất ở
/// nguồn**. Luật này trả về «Thời kĩ bắc thuộc» và **vẫn sai danh từ riêng**.
/// Không có phép biến đổi hình-dạng-chuỗi nào chữa được; đường chữa duy nhất
/// là lấy tên từ mục lục in (`lesson-title-v1`) hoặc một từ điển danh từ
/// riêng có nguồn — cả hai đều là dữ liệu, không phải hiển thị. Xem
/// `docs/research/ROUND6-DEBT-TRIAGE.md` mục R-3.
library;

/// Ranh giới «đầu chuỗi hoặc sau dấu kết câu» — chỗ duy nhất được viết hoa.
final RegExp _sentenceStart = RegExp(r'(^\s*|[.!?]\s*)(\S)', unicode: true);

/// `true` khi chuỗi KHÔNG mang một chữ cái thường nào — dấu hiệu duy nhất máy
/// đọc được rằng tiêu đề này là chữ IN HOA của sách chứ không phải chính tả
/// của người soạn. Chuỗi rỗng / chỉ có số và dấu cũng thoả, và với chúng phép
/// biến đổi là phép đồng nhất nên không hại gì.
bool isAllUpperCase(String s) => s == s.toUpperCase();

/// Số «từ có chữ cái» — dùng để tách VIẾT TẮT khỏi TIÊU ĐỀ in hoa.
int _letterWords(String s) => s
    .split(RegExp(r'\s+'))
    .where((w) => w.runes.any((r) {
          final c = String.fromCharCode(r);
          return c.toUpperCase() != c.toLowerCase();
        }))
    .length;

/// Tiêu đề bài để HIỂN THỊ.
///
/// - đã có chữ thường ⇒ **giữ nguyên từng ký tự** (chính tả của sách/mục lục);
/// - IN HOA toàn bộ ⇒ hạ xuống chữ thường, viết hoa đầu chuỗi và sau «.!?»
///   (giữ đúng hành vi vòng 3–6 cho «HỖN HỢP. TÁCH CHẤT RA KHỎI HỖN HỢP»).
String displayTitle(String title) {
  if (!isAllUpperCase(title)) return title;
  // MỘT TỪ IN HOA LÀ VIẾT TẮT, không phải tiêu đề bị hét. Đo trên pack đang
  // phát hành: 67 trong 175 tiêu đề in hoa là một từ — «GDTC 5», «GDKT&PL 10»,
  // «TN&XH 1» — và luật cũ biến chúng thành «Gdtc 5». Hạ chữ một viết tắt là
  // làm hỏng một cái tên; để nguyên chỉ là hơi to tiếng. Chọn cái sau.
  if (_letterWords(title) < 2) return title;
  return title.toLowerCase().replaceAllMapped(
        _sentenceStart,
        (m) => '${m[1]}${m[2]!.toUpperCase()}',
      );
}

/// «Bài 8 · Đấu tranh giành độc lập thời kì Bắc thuộc».
String displayLessonLabel(int lessonNo, String title) =>
    'Bài $lessonNo · ${displayTitle(title)}';
